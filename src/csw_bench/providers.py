"""Model-agnostic provider adapter, local-only.

The `ollama` SDK import is deferred to construction so that `matriz`, which needs only
the loader and scorer, never pays for the provider dependency. Local inference is meant
to keep item text off the network -- see docs/journal.md, "Phase 3 pivot: local models"
for why this replaced the original three-cloud-vendor design -- but `ollama.Client()`
resolves its host from `OLLAMA_HOST`/`OLLAMA_API_KEY` if left unpinned, and Ollama's own
`:cloud`-tagged models proxy to a hosted API despite appearing in a local `ollama list`.
`OllamaProvider` pins the host explicitly and rejects `:cloud` tags so "local" is an
enforced property of a run, not an assumption about the caller's environment. Determinism
is best-effort and recorded, not assumed: `ModelResponse.seed_applied` records whether a
seed was passed, not whether the backend actually honored it.
"""

from __future__ import annotations

from typing import Final, Protocol

from pydantic import BaseModel, ConfigDict, Field

LOCAL_OLLAMA_HOST: Final[str] = "http://localhost:11434"

REQUEST_TIMEOUT_SECONDS: Final[float] = 300.0
"""Default wall-clock budget per request; `csw-bench run --timeout` overrides it and the
value used is recorded in `run.json` (`RunConfig.request_timeout_seconds`).

`ollama.Client()` passes its kwargs straight through to `httpx.Client`, whose own
default is `timeout=None` -- no timeout at all. A single item that makes the model loop
(observed running the real Phase 3 pilot: a plain grammaticality-judgment prompt that
should take single-digit seconds instead never returned) would otherwise hang the whole
run indefinitely, and `runner.py`'s per-item `ProviderError` isolation can't help with a
request that never raises because it never returns. 300s was generous headroom over
every generation observed in the pilot (worst case ~35s) while still bounding a hang to
minutes rather than forever.

It is not headroom for every legitimate answer. The committed full runs use an
8192-token output budget, and a 32B reasoning model on a 24 GB machine generates a few
tokens per second, so an `ml_identification` answer that runs long is cut off by the
clock long before the token budget binds: that is how `runs/full-deepseek-r1-32b-a` lost
all 100 of its `ml_identification` items (`docs/findings.md`). A timeout shorter than
`max_tokens / tokens-per-second` turns the protocol's token budget into a wall-clock one
that depends on the machine, which is why the value is now a recorded run setting rather
than a constant.
"""


class ProviderError(Exception):
    pass


class CompletionRequest(BaseModel):
    """The full set of response-determining inputs. The cache key is a hash of exactly
    this model, so adding a field here silently invalidates every existing cache entry
    -- which is correct, since a new field means the old entries were produced under
    different (unrecorded) conditions.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    prompt: str
    model: str
    seed: int
    temperature: float = Field(ge=0.0)
    max_tokens: int = Field(gt=0)


class ModelResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    seed_applied: bool


class ModelProvider(Protocol):
    def complete(self, request: CompletionRequest) -> ModelResponse: ...


class OllamaProvider:
    """Talks to a local Ollama server, always at `LOCAL_OLLAMA_HOST` -- pinned rather
    than left to `ollama.Client()`'s default `OLLAMA_HOST`/`OLLAMA_API_KEY` resolution,
    so a stray environment variable can't silently redirect a "local" run off-machine.
    One provider class serves every local model -- `request.model` picks the pulled tag
    (e.g. "qwen3:30b"), the same way OpenAIProvider used to serve many model ids under
    one family. Model-family diversity (the original "three vendors" requirement) is now
    "three distinct local model lineages", enforced by which model ids a run picks, not
    by which provider class runs them.

    `think=False` is passed on every call, resolving the calibration decision
    docs/journal.md's "Phase 3 pivot: local models" entry left open. Every prompt in
    prompts.py asks for the target utterance verbatim and nothing else -- chain-of-thought
    both risks exhausting `num_predict` before any content is emitted (see
    test_ollama_reports_a_truncated_reasoning_budget_distinctly) and, when it doesn't,
    still pollutes `response.message.content` with reasoning prose that the exact-match
    scorers in scoring.py would count against the model. Disabling it is a no-op for
    non-reasoning models and removes the failure mode for reasoning ones.
    """

    def __init__(self, timeout_seconds: float = REQUEST_TIMEOUT_SECONDS) -> None:
        import ollama

        self._timeout_seconds = timeout_seconds
        self._client = ollama.Client(host=LOCAL_OLLAMA_HOST, timeout=timeout_seconds)

    def complete(self, request: CompletionRequest) -> ModelResponse:
        import httpx
        import ollama

        if request.model.endswith(":cloud"):
            raise ProviderError(
                f"model {request.model!r} is routed through a hosted API by Ollama's "
                "cloud proxy, not run on-device; local-only runs must use a pulled, "
                "on-device model"
            )
        try:
            response = self._client.chat(
                model=request.model,
                messages=[{"role": "user", "content": request.prompt}],
                think=False,
                options={
                    "temperature": request.temperature,
                    "seed": request.seed,
                    "num_predict": request.max_tokens,
                },
            )
        except httpx.TimeoutException as exc:
            # Three causes look identical from here: a hung generation, another process
            # holding the memory the model needs (docs/journal.md, 2026-09-10), or an
            # answer that is simply longer than the clock allows at this machine's
            # tokens-per-second. Only the first is the model's fault.
            raise ProviderError(
                f"ollama did not respond within {self._timeout_seconds:.0f}s for model "
                f"{request.model!r} -- a hang, memory contention from another process, or "
                "a generation longer than the timeout allows; raise --timeout to tell them "
                "apart"
            ) from exc
        except (httpx.HTTPError, ollama.ResponseError) as exc:
            # A server-side failure, not a slow one: item 377 of the first full-set run
            # ended with Ollama's Metal runner out of GPU memory and an HTTP 500, which
            # nothing caught, so the stage died with 376 items done. The next request
            # reloads the runner; this item just records the failure.
            raise ProviderError(f"ollama failed to serve model {request.model!r}: {exc}") from exc
        text = response.message.content
        if not text:
            if response.done_reason == "length":
                raise ProviderError(
                    f"ollama exhausted its output budget (num_predict={request.max_tokens}) "
                    f"for model {request.model!r} before producing any content -- likely "
                    "spent on chain-of-thought for a reasoning model; raise max_tokens or "
                    "pass think=False for this model family"
                )
            raise ProviderError(f"ollama returned no text content for model {request.model}")
        if response.prompt_eval_count is None or response.eval_count is None:
            raise ProviderError(f"ollama returned no usage accounting for model {request.model}")
        return ModelResponse(
            text=text,
            input_tokens=response.prompt_eval_count,
            output_tokens=response.eval_count,
            seed_applied=True,
        )


PROVIDER_FAMILIES: tuple[str, ...] = ("ollama",)


def create_provider(
    family: str, *, timeout_seconds: float = REQUEST_TIMEOUT_SECONDS
) -> ModelProvider:
    match family:
        case "ollama":
            return OllamaProvider(timeout_seconds=timeout_seconds)
    raise ValueError(f"unknown provider family {family!r}; expected one of {PROVIDER_FAMILIES}")
