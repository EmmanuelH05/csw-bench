"""Contracts between the committed item set and the code that reports on it. Checked
against fixtures these would pass vacuously; they only mean something against the items
actually on disk.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pytest

from csw_bench.export import export_rows
from csw_bench.loader import load_items
from csw_bench.scoring import CHANCE_FLOOR, MAX_POINTS
from csw_bench.taxonomy import TaskType

REPO = Path(__file__).resolve().parents[1]
VERSIONS = REPO / "docs" / "versions.md"
ITEMS_ROOT = REPO / "data" / "items"
HF_EXPORT = REPO / "data" / "hf"


def test_committed_hf_export_matches_the_items_on_disk() -> None:
    """data/hf/ is what gets uploaded to Hugging Face. It is derived from data/items/
    and must never be edited by hand; regenerate with `uv run csw-bench export-hf`.
    """
    expected = export_rows(load_items(ITEMS_ROOT))
    for task, lines in expected.items():
        path = HF_EXPORT / f"{task.value}.jsonl"
        assert path.is_file(), f"{path} missing; run `uv run csw-bench export-hf`"
        assert path.read_text(encoding="utf-8").splitlines() == lines, (
            f"{path} differs from the items on disk; run `uv run csw-bench export-hf`"
        )
    assert sum(len(lines) for lines in expected.values()) == 402


def test_recorded_v1_hash_matches_the_items_on_disk() -> None:
    """The freeze is only real if editing an item fails a test. docs/versions.md carries
    the hash `matriz` records against; this pins the files on disk to it, so a changed
    item forces a deliberate version-table edit rather than a silent drift.
    """
    rows = [
        line
        for line in VERSIONS.read_text(encoding="utf-8").splitlines()
        if line.startswith("| v1.0 ")
    ]
    assert len(rows) == 1, "docs/versions.md must carry exactly one v1.0 row"
    recorded = re.search(r"\b[0-9a-f]{64}\b", rows[0])
    assert recorded is not None, "the v1.0 row carries no SHA-256"

    assert load_items(ITEMS_ROOT).hash() == recorded.group()


def test_ml_identification_floor_is_the_best_constant_label_strategy_on_disk() -> None:
    """If the Matrix Language distribution of the shipped ml_identification items ever
    changes, the floor must be re-derived with it rather than left at a stale constant.
    """
    items = load_items(ITEMS_ROOT).filter_by_task_type(TaskType.ML_IDENTIFICATION)
    assert items

    majority = max(Counter(item.matrix_language for item in items).values())
    label_point = 1 / MAX_POINTS[TaskType.ML_IDENTIFICATION]

    assert CHANCE_FLOOR[TaskType.ML_IDENTIFICATION] == pytest.approx(
        majority / len(items) * label_point
    )
