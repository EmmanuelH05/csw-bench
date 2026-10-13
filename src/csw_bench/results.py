"""Aggregation of run records into the reportable result vector.

Scores are reported per task type and per task x violation cell, rescaled against each
task's chance floor. Nothing here averages across task types: the tasks have different
scales and different floors, and a single blended number would erase exactly the
dissociations (high judgment, low continuation) the benchmark exists to surface.
"""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean

from csw_bench.runner import RunRecord, RunResult
from csw_bench.scoring import CHANCE_FLOOR
from csw_bench.stats import bootstrap_ci
from csw_bench.taxonomy import TaskType, ViolationType


def load_run(run_dir: Path) -> RunResult:
    header = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    with (run_dir / "records.jsonl").open(encoding="utf-8") as fh:
        records = [RunRecord.model_validate_json(line) for line in fh if line.strip()]
    return RunResult.model_validate({**header, "records": records})


def above_chance(value: float, task: TaskType) -> float:
    """Rescales a normalized score so 0 is chance and 1 is ceiling. Judgment has a 50%
    guessing floor and ML identification a constant-label floor; the other tasks have
    none. Below-chance results go negative rather than being clamped, because below
    chance is a finding.
    """
    floor = CHANCE_FLOOR[task]
    return (value - floor) / (1.0 - floor)


def _rescaled(record: RunRecord) -> float:
    return above_chance(record.points / record.max_points, record.task_type)


@dataclass(frozen=True)
class Cell:
    task_type: TaskType
    violation: ViolationType | None
    n: int
    mean_normalized: float
    mean_above_chance: float
    ci_low: float
    ci_high: float
    errored: int = 0


@dataclass(frozen=True)
class Report:
    cells: tuple[Cell, ...]
    resamples: int
    seed: int
    confidence: float

    def task_rows(self) -> tuple[Cell, ...]:
        return tuple(c for c in self.cells if c.violation is None)


def _cell(
    task: TaskType,
    violation: ViolationType | None,
    records: Sequence[RunRecord],
    *,
    resamples: int,
    seed: int,
    confidence: float,
) -> Cell:
    """`records` may include errored ones (provider infrastructure failures, not model
    answers) -- they're excluded from the score itself so a model's failure-to-serve
    isn't silently absorbed into its competence score, but counted and reported via
    `Cell.errored` so the exclusion is visible rather than a silent drop in `n`.
    """
    errored = sum(1 for r in records if r.errored)
    scored = [r for r in records if not r.errored]
    if not scored:
        return Cell(
            task_type=task,
            violation=violation,
            n=0,
            mean_normalized=0.0,
            mean_above_chance=0.0,
            ci_low=0.0,
            ci_high=0.0,
            errored=errored,
        )
    normalized = [r.points / r.max_points for r in scored]
    rescaled = [above_chance(v, task) for v in normalized]
    low, high = bootstrap_ci(rescaled, resamples=resamples, seed=seed, confidence=confidence)
    return Cell(
        task_type=task,
        violation=violation,
        n=len(scored),
        mean_normalized=fmean(normalized),
        mean_above_chance=fmean(rescaled),
        ci_low=low,
        ci_high=high,
        errored=errored,
    )


def summarize(
    records: Iterable[RunRecord],
    *,
    resamples: int = 10_000,
    seed: int = 0,
    confidence: float = 0.95,
) -> Report:
    by_task: dict[TaskType, list[RunRecord]] = defaultdict(list)
    by_cell: dict[tuple[TaskType, ViolationType], list[RunRecord]] = defaultdict(list)
    for record in records:
        by_task[record.task_type].append(record)
        by_cell[(record.task_type, record.primary_violation)].append(record)

    cells: list[Cell] = []
    for task in TaskType:
        if task not in by_task:
            continue
        cells.append(
            _cell(task, None, by_task[task], resamples=resamples, seed=seed, confidence=confidence)
        )
        for violation in ViolationType:
            group = by_cell.get((task, violation))
            if group:
                cells.append(
                    _cell(
                        task,
                        violation,
                        group,
                        resamples=resamples,
                        seed=seed,
                        confidence=confidence,
                    )
                )
    return Report(cells=tuple(cells), resamples=resamples, seed=seed, confidence=confidence)


@dataclass(frozen=True)
class TaskDelta:
    task_type: TaskType
    n: int
    mean_a: float
    mean_b: float
    ci_low: float
    ci_high: float

    @property
    def delta(self) -> float:
        return self.mean_b - self.mean_a


def compare(
    a: RunResult,
    b: RunResult,
    *,
    resamples: int = 10_000,
    seed: int = 0,
    confidence: float = 0.95,
) -> tuple[TaskDelta, ...]:
    """Per-task delta between two runs over the same item set, paired by item -- the
    Phase 3 prompt-sensitivity check when the runs differ only in template. The interval
    is a percentile bootstrap over per-item differences, so it bounds the noise in the
    delta itself rather than in either mean. An item errored in either run leaves the
    pair entirely: counting a provider failure as a zero on one side would manufacture a
    template effect out of an infrastructure one.
    """
    if a.item_set_hash != b.item_set_hash:
        raise ValueError(
            "runs evaluated different item sets "
            f"({a.item_set_hash[:12]} vs {b.item_set_hash[:12]}); their scores are not comparable"
        )

    scored_b = {r.item_id: r for r in b.records if not r.errored}
    pairs: dict[TaskType, list[tuple[float, float]]] = defaultdict(list)
    for record in a.records:
        other = scored_b.get(record.item_id)
        if record.errored or other is None:
            continue
        pairs[record.task_type].append((_rescaled(record), _rescaled(other)))

    deltas: list[TaskDelta] = []
    for task in TaskType:
        group = pairs.get(task)
        if not group:
            continue
        low, high = bootstrap_ci(
            [vb - va for va, vb in group], resamples=resamples, seed=seed, confidence=confidence
        )
        deltas.append(
            TaskDelta(
                task_type=task,
                n=len(group),
                mean_a=fmean(va for va, _ in group),
                mean_b=fmean(vb for _, vb in group),
                ci_low=low,
                ci_high=high,
            )
        )
    return tuple(deltas)


def format_report(report: Report) -> str:
    pct = int(report.confidence * 100)
    lines = [
        f"{'task':<26} {'violation':<10} {'n':>4} {'mean':>6} {'>chance':>8} {f'{pct}% CI':>18}"
    ]
    for cell in report.cells:
        violation = cell.violation.value if cell.violation else "all"
        ci = f"[{cell.ci_low:+.3f}, {cell.ci_high:+.3f}]"
        errored = f"  ({cell.errored} errored, excluded)" if cell.errored else ""
        lines.append(
            f"{cell.task_type.value:<26} {violation:<10} {cell.n:>4} "
            f"{cell.mean_normalized:>6.3f} {cell.mean_above_chance:>+8.3f} {ci:>18}{errored}"
        )
    lines.append(
        f"\nabove-chance rescales each task against its own floor; tasks are never averaged. "
        f"bootstrap: {report.resamples} resamples, seed {report.seed}."
    )
    return "\n".join(lines)


def format_comparison(deltas: Sequence[TaskDelta], label_a: str, label_b: str) -> str:
    lines = [f"{'task':<26} {label_a:>10} {label_b:>10} {'delta':>8} {'delta CI':>18} {'n':>4}"]
    for d in deltas:
        ci = f"[{d.ci_low:+.3f}, {d.ci_high:+.3f}]"
        lines.append(
            f"{d.task_type.value:<26} {d.mean_a:>+10.3f} {d.mean_b:>+10.3f} {d.delta:>+8.3f} "
            f"{ci:>18} {d.n:>4}"
        )
    lines.append("\npaired by item; an item errored in either run is excluded from both columns.")
    return "\n".join(lines)


def format_markdown_table(reports: Sequence[tuple[str, Report]]) -> str:
    """One row per task (pooled) and per task x violation cell, one column per run. A
    cell shows the raw normalized mean, the above-chance mean with its interval, and the
    scored n; errored counts stay visible so a clean-looking mean over a mostly-errored
    cell cannot pass as a clean result.
    """
    if not reports:
        raise ValueError("no reports to tabulate")
    settings = {(r.resamples, r.seed, r.confidence) for _, r in reports}
    if len(settings) != 1:
        raise ValueError(
            "reports were bootstrapped under different settings; their intervals are not "
            "comparable side by side"
        )
    resamples, seed, confidence = settings.pop()

    by_run = [{(c.task_type, c.violation): c for c in report.cells} for _, report in reports]
    lines = [
        "| task | violation | " + " | ".join(label for label, _ in reports) + " |",
        "|---|---|" + "---|" * len(reports),
    ]
    for task in TaskType:
        for violation in (None, *ViolationType):
            key = (task, violation)
            if not any(key in cells for cells in by_run):
                continue
            cells = " | ".join(_markdown_cell(run.get(key)) for run in by_run)
            lines.append(f"| {task.value} | {violation.value if violation else 'all'} | {cells} |")
    lines.append("")
    lines.append(
        f"Each cell: raw mean · above-chance mean [{int(confidence * 100)}% CI] · scored n. "
        "Above-chance rescales each task against its own floor; tasks are never averaged. "
        "Errored records (provider failures, not model answers) are excluded from the score "
        f"and counted. Bootstrap: {resamples} resamples, seed {seed}."
    )
    return "\n".join(lines)


def _markdown_cell(cell: Cell | None) -> str:
    if cell is None:
        return "—"
    errored = f" ({cell.errored} errored)" if cell.errored else ""
    if cell.n == 0:
        return f"—{errored}"
    return (
        f"{cell.mean_normalized:.2f} · {cell.mean_above_chance:+.2f} "
        f"[{cell.ci_low:+.2f}, {cell.ci_high:+.2f}] · n={cell.n}{errored}"
    )
