"""The lm-evaluation-harness task under integrations/la-leaderboard/ carries a copy of
the repair scorer, because the harness cannot import csw-bench. These tests hold the copy
to the original over every repair item on disk, with the response shapes the rubric
distinguishes: the gold repair, an alternate, the violating string echoed back, a hedge,
a wholesale rewrite, and a leaked reasoning preamble.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

from csw_bench.loader import load_items
from csw_bench.schema import RepairItem
from csw_bench.scoring import score
from csw_bench.taxonomy import TaskType
from csw_bench.textnorm import normalize

REPO = Path(__file__).resolve().parents[1]
PORT = REPO / "integrations" / "la-leaderboard" / "csw_bench" / "utils.py"


def _load_port() -> ModuleType:
    spec = importlib.util.spec_from_file_location("la_leaderboard_csw_bench_utils", PORT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


port = _load_port()
REPAIR_ITEMS = [
    item
    for item in load_items(REPO / "data" / "items").filter_by_task_type(TaskType.REPAIR)
    if isinstance(item, RepairItem)
]


def _responses(item: RepairItem) -> list[str]:
    return [
        item.gold_repair,
        f'"{item.gold_repair}"',
        f"<think>\nthe article is wrong\n</think>\n{item.gold_repair}",
        *item.alternate_repairs,
        item.violating,
        f"It depends: {item.gold_repair}",
        f"{item.gold_repair} Y luego fuimos a casa a descansar un rato.",
        "",
    ]


def test_the_shipped_set_has_repair_items_to_check_against() -> None:
    assert len(REPAIR_ITEMS) == 100


@pytest.mark.parametrize("item", REPAIR_ITEMS, ids=lambda item: item.id)
def test_port_agrees_with_the_canonical_repair_scorer(item: RepairItem) -> None:
    doc = item.model_dump(mode="json")
    for response in _responses(item):
        # score(), not score_repair(): the runner's entry point, which strips a leaked
        # reasoning preamble before the repair rubric sees the response.
        expected = score(item, response, port.MINIMALITY_THRESHOLD).points
        assert port.repair_points(doc, response) == expected, (item.id, response)


def test_process_results_reports_the_harness_metrics(tmp_path: Path) -> None:
    item = REPAIR_ITEMS[0]
    doc = item.model_dump(mode="json")

    assert port.process_results_repair(doc, [item.gold_repair]) == {
        "repair_score": 1.0,
        "repair_minimal": 1.0,
    }
    assert port.process_results_repair(doc, [item.violating]) == {
        "repair_score": 0.0,
        "repair_minimal": 0.0,
    }


def test_port_normalization_matches_textnorm() -> None:
    for text in ("Compré the libros ayer.", "  MAÑANA, vamos!!  ", "Ñandú: ¿qué?"):
        assert port.normalize(text) == normalize(text)
