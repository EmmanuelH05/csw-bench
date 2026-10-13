"""Model-agnostic run loop: items -> prompts -> provider or cache -> scored records.

A run directory holds `run.json` (config, item-set hash, accounting) and
`records.jsonl` (one scored record per item, with the full rendered prompt and raw
response text). Together with the response cache they make every score reproducible
without a provider call.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from csw_bench.accounting import PricePerMTok, RunAccounting, UsageTotals, finalize
from csw_bench.cache import ResponseCache
from csw_bench.loader import ItemSet
from csw_bench.prompts import TEMPLATE_IDS, render
from csw_bench.providers import (
    LOCAL_OLLAMA_HOST,
    REQUEST_TIMEOUT_SECONDS,
    CompletionRequest,
    ModelProvider,
    ProviderError,
)
from csw_bench.schema import Item
from csw_bench.scoring import MAX_POINTS, score
from csw_bench.taxonomy import TaskType, ViolationType


class RetentionError(Exception):
    pass


class RunConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    provider_family: str
    provider_host: str = Field(
        default=LOCAL_OLLAMA_HOST,
        description="Resolved host the provider talked to, recorded so 'this run stayed "
        "local' is auditable from run.json rather than trusted from the provider code's "
        "current behavior.",
    )
    model: str
    template_id: str
    seed: int
    minimality_threshold: float = Field(
        ge=0.0,
        le=1.0,
        description="Repair minimality cutoff, calibrated in Phase 3 and frozen. "
        "Required so no run silently scores repairs against an uncalibrated value.",
    )
    zero_retention: bool = Field(
        description="Whether the provider account had zero data retention enabled. "
        "TalkBank's terms forbid sending Bangor Miami material to providers that retain "
        "it, so the setting is a recorded run detail and attested items refuse to run "
        "without it."
    )
    temperature: float = Field(default=0.0, ge=0.0)
    max_tokens: int = Field(default=1024, gt=0)
    request_timeout_seconds: float = Field(
        default=REQUEST_TIMEOUT_SECONDS,
        gt=0.0,
        description="Wall-clock budget per provider call. Deliberately not part of the "
        "cache key: a response that arrived is the same response whatever the clock "
        "allowed, so a rerun at a longer timeout still serves every finished item from "
        "cache. It is recorded because it decides which items error -- the committed "
        "full runs lost 100 ml_identification items to the 300 s default and were rerun "
        "with a longer budget, and this field is the only difference between those runs. "
        "Runs written before the field existed load with the default, which is the value "
        "they all used.",
    )

    @model_validator(mode="after")
    def _template_exists(self) -> RunConfig:
        if self.template_id not in TEMPLATE_IDS:
            raise ValueError(
                f"unknown template id {self.template_id!r}; expected one of {TEMPLATE_IDS}"
            )
        return self


class RunRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    item_id: str
    task_type: TaskType
    primary_violation: ViolationType
    prompt: str
    response_text: str
    cached: bool
    points: int
    max_points: int
    reason: str
    errored: bool = Field(
        default=False,
        description="The provider call raised rather than returned -- an infrastructure "
        "failure, not the model declining or answering wrong. Excluded from scored "
        "aggregates (results.summarize) so a model's failure-to-serve doesn't get "
        "silently absorbed into its competence score; the count is reported alongside "
        "it instead.",
    )


class RunResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    config: RunConfig
    item_set_hash: str
    prices: PricePerMTok | None
    accounting: RunAccounting
    records: tuple[RunRecord, ...]


RecordObserver = Callable[[RunRecord, int, int], None]


def run_id(item_set_hash: str, config: RunConfig) -> str:
    """Content-derived, so the same evaluation lands in the same directory and a repeat
    invocation is a cache exercise rather than a second billing event.
    """
    digest = hashlib.sha256(f"{item_set_hash}:{config.model_dump_json()}".encode()).hexdigest()
    safe_model = re.sub(r"[^\w.-]", "-", config.model)
    return f"{safe_model}-t{config.template_id}-s{config.seed}-{digest[:8]}"


def _guard_retention(item_set: ItemSet, config: RunConfig) -> None:
    if config.zero_retention:
        return
    attested = sorted(i.id for i in item_set if i.provenance.source == "attested")
    if attested:
        raise RetentionError(
            f"{len(attested)} attested items (first: {attested[0]}) quote corpus material "
            "whose license forbids retention by model providers. Enable zero retention on "
            "the provider account and pass zero_retention=True, or exclude attested items."
        )


def _evaluate(
    item: Item,
    config: RunConfig,
    provider: ModelProvider,
    cache: ResponseCache,
    totals: UsageTotals,
) -> RunRecord:
    prompt = render(item, config.template_id)
    request = CompletionRequest(
        prompt=prompt,
        model=config.model,
        seed=config.seed,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )
    response = cache.get(request)
    cached = response is not None
    if response is None:
        try:
            response = provider.complete(request)
        except ProviderError as exc:
            totals.record_error()
            return RunRecord(
                item_id=item.id,
                task_type=item.task_type,
                primary_violation=item.primary_violation,
                prompt=prompt,
                response_text="",
                cached=False,
                points=0,
                max_points=MAX_POINTS[item.task_type],
                reason=f"provider error: {exc}",
                errored=True,
            )
        cache.put(request, response)
    totals.record(response, cached=cached)

    item_score = score(item, response.text, config.minimality_threshold)
    return RunRecord(
        item_id=item.id,
        task_type=item.task_type,
        primary_violation=item.primary_violation,
        prompt=prompt,
        response_text=response.text,
        cached=cached,
        points=item_score.points,
        max_points=item_score.max_points,
        reason=item_score.reason,
    )


def run(
    item_set: ItemSet,
    provider: ModelProvider,
    config: RunConfig,
    cache: ResponseCache,
    out_dir: Path,
    *,
    prices: PricePerMTok | None = None,
    on_record: RecordObserver | None = None,
) -> RunResult:
    """`on_record` fires after each record is persisted, with (record, index, total), so
    a multi-hour background run can be followed from a log rather than by polling
    records.jsonl.
    """
    _guard_retention(item_set, config)

    totals = UsageTotals()
    records: list[RunRecord] = []
    total = len(item_set)
    out_dir.mkdir(parents=True, exist_ok=True)

    with (out_dir / "records.jsonl").open("w", encoding="utf-8") as sink:
        for index, item in enumerate(item_set, start=1):
            record = _evaluate(item, config, provider, cache, totals)
            records.append(record)
            sink.write(record.model_dump_json() + "\n")
            sink.flush()
            if on_record is not None:
                on_record(record, index, total)

    result = RunResult(
        config=config,
        item_set_hash=item_set.hash(),
        prices=prices,
        accounting=finalize(totals, prices),
        records=tuple(records),
    )
    (out_dir / "run.json").write_text(
        result.model_dump_json(indent=2, exclude={"records"}), encoding="utf-8"
    )
    return result
