"""Token and cost accounting per run.

There is no built-in pricing table. Provider prices move, and a stale constant would
misreport cost with full confidence; a run that wants a dollar figure supplies the
prices it is actually billed at, and they are recorded with the run artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from csw_bench.providers import ModelResponse


class PricePerMTok(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    input: float = Field(ge=0.0, description="USD per million input tokens.")
    output: float = Field(ge=0.0, description="USD per million output tokens.")


@dataclass
class UsageTotals:
    """Billed and cached traffic are separate columns: 'rerun from cache costs nothing'
    is only checkable if cached tokens never fold into the billed count. Mutable as a
    run-local accumulator; it is frozen into `RunAccounting` before leaving the runner.
    """

    billed_input_tokens: int = 0
    billed_output_tokens: int = 0
    cached_input_tokens: int = 0
    cached_output_tokens: int = 0
    provider_calls: int = 0
    cache_hits: int = 0
    provider_errors: int = 0

    def record(self, response: ModelResponse, *, cached: bool) -> None:
        if cached:
            self.cache_hits += 1
            self.cached_input_tokens += response.input_tokens
            self.cached_output_tokens += response.output_tokens
        else:
            self.provider_calls += 1
            self.billed_input_tokens += response.input_tokens
            self.billed_output_tokens += response.output_tokens

    def record_error(self) -> None:
        """A provider call that raised rather than returned. Counted separately from a
        billed call: it consumed no tokens on our side of the accounting (the provider
        may have burned its own generation budget, but returned nothing to bill), and
        conflating it with a real response would misreport both cost and cache-hit rate.
        """
        self.provider_calls += 1
        self.provider_errors += 1


class RunAccounting(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    billed_input_tokens: int
    billed_output_tokens: int
    cached_input_tokens: int
    cached_output_tokens: int
    provider_calls: int
    cache_hits: int
    provider_errors: int
    cost_usd: float | None


def finalize(totals: UsageTotals, prices: PricePerMTok | None) -> RunAccounting:
    cost = None
    if prices is not None:
        cost = (
            totals.billed_input_tokens * prices.input + totals.billed_output_tokens * prices.output
        ) / 1_000_000
    return RunAccounting(
        billed_input_tokens=totals.billed_input_tokens,
        billed_output_tokens=totals.billed_output_tokens,
        cached_input_tokens=totals.cached_input_tokens,
        cached_output_tokens=totals.cached_output_tokens,
        provider_calls=totals.provider_calls,
        cache_hits=totals.cache_hits,
        provider_errors=totals.provider_errors,
        cost_usd=cost,
    )
