from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import ollama
import pytest

from csw_bench.providers import (
    LOCAL_OLLAMA_HOST,
    PROVIDER_FAMILIES,
    REQUEST_TIMEOUT_SECONDS,
    CompletionRequest,
    OllamaProvider,
    ProviderError,
    create_provider,
)

REQUEST = CompletionRequest(
    prompt="hola", model="qwen3:30b", seed=0, temperature=0.0, max_tokens=10
)


def test_local_provider_family_is_supported() -> None:
    assert PROVIDER_FAMILIES == ("ollama",)


def test_unknown_family_is_rejected_with_the_valid_choices() -> None:
    with pytest.raises(ValueError, match="ollama"):
        create_provider("anthropic")


def test_create_provider_builds_an_ollama_provider_pinned_to_localhost() -> None:
    with patch("ollama.Client") as client_cls:
        provider = create_provider("ollama")

    assert isinstance(provider, OllamaProvider)
    client_cls.assert_called_once_with(host=LOCAL_OLLAMA_HOST, timeout=REQUEST_TIMEOUT_SECONDS)


def test_request_rejects_unknown_fields() -> None:
    """The cache key hashes exactly the request fields, so an unnoticed extra field
    would mean responses cached under conditions the key does not record.
    """
    with pytest.raises(ValueError):
        CompletionRequest.model_validate(
            {
                "prompt": "p",
                "model": "m",
                "seed": 0,
                "temperature": 0.0,
                "max_tokens": 10,
                "top_p": 0.9,
            }
        )


def _fake_client(response: ollama.ChatResponse) -> MagicMock:
    client = MagicMock()
    client.chat.return_value = response
    return client


def test_ollama_maps_a_successful_response() -> None:
    response = ollama.ChatResponse(
        message=ollama.Message(role="assistant", content="hola"),
        prompt_eval_count=12,
        eval_count=3,
    )
    client = _fake_client(response)
    with patch("ollama.Client", return_value=client):
        result = OllamaProvider().complete(REQUEST)

    assert result.text == "hola"
    assert result.input_tokens == 12
    assert result.output_tokens == 3
    assert result.seed_applied is True
    client.chat.assert_called_once_with(
        model="qwen3:30b",
        messages=[{"role": "user", "content": "hola"}],
        think=False,
        options={"temperature": 0.0, "seed": 0, "num_predict": 10},
    )


def test_ollama_rejects_empty_text() -> None:
    response = ollama.ChatResponse(
        message=ollama.Message(role="assistant", content=""),
        done_reason="stop",
        prompt_eval_count=12,
        eval_count=0,
    )
    with (
        patch("ollama.Client", return_value=_fake_client(response)),
        pytest.raises(ProviderError, match="no text content"),
    ):
        OllamaProvider().complete(REQUEST)


def test_ollama_reports_a_truncated_reasoning_budget_distinctly() -> None:
    """Reasoning models can spend the whole num_predict budget on chain-of-thought and
    emit no content -- worth a distinct error from "no text content" so it isn't
    mistaken for the model refusing or misbehaving.
    """
    response = ollama.ChatResponse(
        message=ollama.Message(role="assistant", content=""),
        done_reason="length",
        prompt_eval_count=12,
        eval_count=10,
    )
    with (
        patch("ollama.Client", return_value=_fake_client(response)),
        pytest.raises(ProviderError, match="exhausted its output budget"),
    ):
        OllamaProvider().complete(REQUEST)


def test_a_custom_timeout_is_passed_to_the_client_and_named_in_the_error() -> None:
    client = MagicMock()
    client.chat.side_effect = httpx.ReadTimeout("timed out")
    with patch("ollama.Client", return_value=client) as client_cls:
        provider = create_provider("ollama", timeout_seconds=1800.0)
        client_cls.assert_called_once_with(host=LOCAL_OLLAMA_HOST, timeout=1800.0)
        with pytest.raises(ProviderError, match="did not respond within 1800s"):
            provider.complete(REQUEST)


def test_a_hung_generation_times_out_as_a_provider_error() -> None:
    """`ollama.Client()` inherits httpx's default of no timeout at all -- discovered
    running the real Phase 3 pilot, where a single item that should take single-digit
    seconds instead never returned and hung the whole run. The client must be
    constructed with a timeout, and a timeout must surface as ProviderError so
    runner.py's per-item isolation can act on it rather than the run hanging forever.
    """
    client = MagicMock()
    client.chat.side_effect = httpx.ReadTimeout("timed out")
    with (
        patch("ollama.Client", return_value=client),
        pytest.raises(ProviderError, match=r"did not respond within \d+s"),
    ):
        OllamaProvider().complete(REQUEST)


def test_ollama_rejects_cloud_routed_model_tags() -> None:
    with pytest.raises(ProviderError, match="hosted API"):
        OllamaProvider().complete(
            CompletionRequest(
                prompt="hola", model="kimi-k2.6:cloud", seed=0, temperature=0.0, max_tokens=10
            )
        )


@pytest.mark.parametrize("missing_field", ["prompt_eval_count", "eval_count"])
def test_ollama_rejects_missing_usage_accounting(missing_field: str) -> None:
    counts = {"prompt_eval_count": 12, "eval_count": 3}
    counts[missing_field] = None
    response = ollama.ChatResponse(
        message=ollama.Message(role="assistant", content="hola"),
        done_reason="stop",
        **counts,
    )
    with (
        patch("ollama.Client", return_value=_fake_client(response)),
        pytest.raises(ProviderError, match="no usage accounting"),
    ):
        OllamaProvider().complete(REQUEST)


def test_a_runner_crash_is_a_provider_error_not_a_run_abort() -> None:
    """Item 377 of the first full-set run: Ollama's Metal runner ran out of GPU memory,
    the server answered HTTP 500, the SDK raised ResponseError, and nothing caught it --
    the whole stage died with 376 items done. Every server-side failure must reach
    runner.py's per-item isolation as a ProviderError.
    """
    client = MagicMock()
    client.chat.side_effect = ollama.ResponseError(
        "an error was encountered while running the model: GGML_ASSERT(...) failed", 500
    )
    with (
        patch("ollama.Client", return_value=client),
        pytest.raises(ProviderError, match=r"failed to serve model 'qwen3:30b'.*GGML_ASSERT"),
    ):
        OllamaProvider().complete(REQUEST)


@pytest.mark.parametrize(
    "failure",
    [httpx.RemoteProtocolError("peer closed connection"), httpx.ConnectError("refused")],
    ids=["protocol", "connect"],
)
def test_transport_failures_are_provider_errors(failure: httpx.HTTPError) -> None:
    client = MagicMock()
    client.chat.side_effect = failure
    with (
        patch("ollama.Client", return_value=client),
        pytest.raises(ProviderError, match="failed to serve"),
    ):
        OllamaProvider().complete(REQUEST)
