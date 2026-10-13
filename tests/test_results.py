from __future__ import annotations

import pytest

from csw_bench.accounting import RunAccounting
from csw_bench.results import (
    above_chance,
    compare,
    format_comparison,
    format_markdown_table,
    format_report,
    summarize,
)
from csw_bench.runner import RunConfig, RunRecord, RunResult
from csw_bench.taxonomy import TaskType, ViolationType

_CONFIG = RunConfig(
    provider_family="fake",
    model="fake-1",
    template_id="a",
    seed=7,
    minimality_threshold=0.6,
    zero_retention=True,
)

_ACCOUNTING = RunAccounting(
    billed_input_tokens=0,
    billed_output_tokens=0,
    cached_input_tokens=0,
    cached_output_tokens=0,
    provider_calls=0,
    cache_hits=0,
    provider_errors=0,
    cost_usd=None,
)


def _record(
    item_id: str,
    task: TaskType,
    violation: ViolationType,
    points: int,
    max_points: int,
    *,
    errored: bool = False,
) -> RunRecord:
    return RunRecord(
        item_id=item_id,
        task_type=task,
        primary_violation=violation,
        prompt="prompt",
        response_text="response",
        cached=False,
        points=points,
        max_points=max_points,
        reason="fixture",
        errored=errored,
    )


def _judgment_records(*points: int) -> list[RunRecord]:
    return [
        _record(
            f"csw-es-en-{n:04d}",
            TaskType.GRAMMATICALITY_JUDGMENT,
            ViolationType.ILL_FORMED_EL_ISLAND,
            p,
            1,
        )
        for n, p in enumerate(points, start=1)
    ]


def _result(records: list[RunRecord], item_set_hash: str = "abc123") -> RunResult:
    return RunResult(
        config=_CONFIG,
        item_set_hash=item_set_hash,
        prices=None,
        accounting=_ACCOUNTING,
        records=tuple(records),
    )


def test_above_chance_rescales_the_judgment_floor() -> None:
    task = TaskType.GRAMMATICALITY_JUDGMENT

    assert above_chance(1.0, task) == 1.0
    assert above_chance(0.75, task) == pytest.approx(0.5)
    assert above_chance(0.5, task) == 0.0


def test_below_chance_goes_negative_rather_than_clamping() -> None:
    """Below chance is a finding, not noise to round up to zero."""
    assert above_chance(0.25, TaskType.GRAMMATICALITY_JUDGMENT) == pytest.approx(-0.5)


def test_floorless_tasks_pass_through_unchanged() -> None:
    assert above_chance(0.75, TaskType.REPAIR) == 0.75


def test_ml_identification_floor_is_the_constant_label_strategy() -> None:
    """Every shipped item has Spanish as its Matrix Language, so always answering
    "Spanish" earns the 1-of-3 label point on every item. That, not 0, is chance.
    """
    assert above_chance(1 / 3, TaskType.ML_IDENTIFICATION) == pytest.approx(0.0)
    assert above_chance(1.0, TaskType.ML_IDENTIFICATION) == pytest.approx(1.0)
    assert above_chance(0.0, TaskType.ML_IDENTIFICATION) == pytest.approx(-0.5)


def test_summarize_produces_task_rows_and_violation_cells() -> None:
    records = _judgment_records(1, 1, 0, 0)
    records.append(
        _record("csw-es-en-0005", TaskType.REPAIR, ViolationType.EL_SYSTEM_MORPHEME, 2, 2)
    )

    report = summarize(records, resamples=200, seed=0)

    task_row = next(
        c
        for c in report.cells
        if c.task_type is TaskType.GRAMMATICALITY_JUDGMENT and c.violation is None
    )
    assert task_row.n == 4
    assert task_row.mean_normalized == pytest.approx(0.5)
    assert task_row.mean_above_chance == pytest.approx(0.0)

    cell = next(
        c
        for c in report.cells
        if c.task_type is TaskType.GRAMMATICALITY_JUDGMENT
        and c.violation is ViolationType.ILL_FORMED_EL_ISLAND
    )
    assert cell.n == 4
    assert len(report.task_rows()) == 2


def test_summarize_excludes_errored_records_from_the_score_but_counts_them() -> None:
    """A provider infrastructure failure is not the model answering wrong -- it must not
    pull the mean down, but it also must not vanish silently from the report.
    """
    records = _judgment_records(1, 1, 1)
    records.append(
        _record(
            "csw-es-en-0009",
            TaskType.GRAMMATICALITY_JUDGMENT,
            ViolationType.ILL_FORMED_EL_ISLAND,
            0,
            1,
            errored=True,
        )
    )

    report = summarize(records, resamples=200, seed=0)

    task_row = next(
        c
        for c in report.cells
        if c.task_type is TaskType.GRAMMATICALITY_JUDGMENT and c.violation is None
    )
    assert task_row.n == 3
    assert task_row.mean_normalized == pytest.approx(1.0)
    assert task_row.errored == 1


def test_summarize_handles_a_cell_that_is_entirely_errored() -> None:
    records = [
        _record(
            "csw-es-en-0001",
            TaskType.GRAMMATICALITY_JUDGMENT,
            ViolationType.ILL_FORMED_EL_ISLAND,
            0,
            1,
            errored=True,
        )
    ]

    report = summarize(records, resamples=200, seed=0)

    task_row = next(
        c
        for c in report.cells
        if c.task_type is TaskType.GRAMMATICALITY_JUDGMENT and c.violation is None
    )
    assert task_row.n == 0
    assert task_row.errored == 1
    assert task_row.mean_normalized == 0.0


def test_compare_excludes_errored_records() -> None:
    a = _result(_judgment_records(1, 1), item_set_hash="x")
    b_records = _judgment_records(0, 0)
    b_records.append(
        _record(
            "csw-es-en-0009",
            TaskType.GRAMMATICALITY_JUDGMENT,
            ViolationType.ILL_FORMED_EL_ISLAND,
            1,
            1,
            errored=True,
        )
    )
    b = _result(b_records, item_set_hash="x")

    deltas = compare(a, b)

    assert len(deltas) == 1
    assert deltas[0].mean_b == pytest.approx(-1.0)


def test_summarize_is_deterministic_under_a_fixed_seed() -> None:
    records = _judgment_records(1, 0, 1, 0, 1)

    assert summarize(records, resamples=500, seed=3) == summarize(records, resamples=500, seed=3)


def test_ci_brackets_the_cell_mean() -> None:
    records = _judgment_records(1, 1, 1, 0, 0, 1, 0, 1)

    report = summarize(records, resamples=2000, seed=0)

    for cell in report.cells:
        assert cell.ci_low <= cell.mean_above_chance <= cell.ci_high


def test_compare_reports_per_task_deltas() -> None:
    a = _result(_judgment_records(1, 1, 0, 0))
    b = _result(_judgment_records(1, 1, 1, 0))

    (delta,) = compare(a, b)

    assert delta.task_type is TaskType.GRAMMATICALITY_JUDGMENT
    assert delta.n == 4
    assert delta.mean_a == pytest.approx(0.0)
    assert delta.mean_b == pytest.approx(0.5)
    assert delta.delta == pytest.approx(0.5)
    assert delta.ci_low <= delta.delta <= delta.ci_high


def test_compare_pairs_by_item_and_drops_an_item_errored_in_either_run() -> None:
    """A provider failure on one side is not a template effect; the pair leaves both
    columns rather than counting as a zero on one of them.
    """
    a = _result(_judgment_records(1, 1, 0))
    b_records = _judgment_records(1, 0)
    b_records.append(
        _record(
            "csw-es-en-0003",
            TaskType.GRAMMATICALITY_JUDGMENT,
            ViolationType.ILL_FORMED_EL_ISLAND,
            1,
            1,
            errored=True,
        )
    )
    b = _result(b_records)

    (delta,) = compare(a, b, resamples=200, seed=0)

    assert delta.n == 2
    assert delta.mean_a == pytest.approx(1.0)
    assert delta.mean_b == pytest.approx(0.0)
    assert delta.ci_low <= delta.delta <= delta.ci_high


def test_compare_refuses_runs_over_different_item_sets() -> None:
    a = _result(_judgment_records(1))
    b = _result(_judgment_records(1), item_set_hash="different")

    with pytest.raises(ValueError, match="different item sets"):
        compare(a, b)


def test_format_report_states_that_tasks_are_never_averaged() -> None:
    report = summarize(_judgment_records(1, 0), resamples=100, seed=0)

    rendered = format_report(report)

    assert "grammaticality_judgment" in rendered
    assert "never averaged" in rendered


def test_format_comparison_shows_the_delta() -> None:
    deltas = compare(_result(_judgment_records(1, 1, 0, 0)), _result(_judgment_records(1, 1, 1, 0)))

    rendered = format_comparison(deltas, "run-a", "run-b")

    assert "run-a" in rendered
    assert "+0.500" in rendered


def test_format_comparison_reports_the_paired_n_and_interval() -> None:
    deltas = compare(
        _result(_judgment_records(1, 1, 0, 0)),
        _result(_judgment_records(1, 1, 1, 0)),
        resamples=200,
        seed=0,
    )

    rendered = format_comparison(deltas, "run-a", "run-b")

    assert "delta CI" in rendered
    assert "paired by item" in rendered
    assert rendered.splitlines()[1].split()[-1] == "4"


def test_format_markdown_table_has_one_column_per_run_and_keeps_errored_counts_visible() -> None:
    clean = summarize(_judgment_records(1, 1, 1, 0), resamples=100, seed=0)
    records = _judgment_records(1, 1)
    records.append(
        _record(
            "csw-es-en-0003",
            TaskType.GRAMMATICALITY_JUDGMENT,
            ViolationType.ILL_FORMED_EL_ISLAND,
            0,
            1,
            errored=True,
        )
    )
    flaky = summarize(records, resamples=100, seed=0)

    rendered = format_markdown_table([("model-x", clean), ("model-y", flaky)])

    assert "| task | violation | model-x | model-y |" in rendered
    assert "| grammaticality_judgment | all |" in rendered
    assert "| grammaticality_judgment | T3 |" in rendered
    assert "n=4" in rendered
    assert "n=2 (1 errored)" in rendered
    assert "never averaged" in rendered


def test_format_markdown_table_shows_a_fully_errored_cell_as_absent_not_zero() -> None:
    records = [
        _record(
            "csw-es-en-0001",
            TaskType.GRAMMATICALITY_JUDGMENT,
            ViolationType.ILL_FORMED_EL_ISLAND,
            0,
            1,
            errored=True,
        )
    ]

    rendered = format_markdown_table([("model-x", summarize(records, resamples=100, seed=0))])

    assert "| grammaticality_judgment | all | — (1 errored) |" in rendered


def test_format_markdown_table_refuses_reports_bootstrapped_differently() -> None:
    a = summarize(_judgment_records(1, 0), resamples=100, seed=0)
    b = summarize(_judgment_records(1, 0), resamples=200, seed=0)

    with pytest.raises(ValueError, match="different settings"):
        format_markdown_table([("a", a), ("b", b)])
