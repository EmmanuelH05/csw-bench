from __future__ import annotations

import json
from pathlib import Path

import pytest

from csw_bench.cli import main
from csw_bench.export import export_hf, export_rows
from csw_bench.loader import ItemSet
from csw_bench.taxonomy import TaskType, ViolationType
from tests.conftest import (
    continuation_item,
    identification_item,
    judgment_item,
    parse,
    repair_item,
)


def _item_set() -> ItemSet:
    # Deliberately out of id order, and two items in one task, so sorting is tested.
    return ItemSet(
        [
            parse(repair_item("csw-es-en-0004", ViolationType.CONGRUENCE_FAILURE)),
            parse(judgment_item("csw-es-en-0002", ViolationType.EL_SYSTEM_MORPHEME)),
            parse(continuation_item("csw-es-en-0003", ViolationType.ILL_FORMED_EL_ISLAND)),
            parse(identification_item("csw-es-en-0005", ViolationType.EL_SYSTEM_MORPHEME)),
            parse(judgment_item("csw-es-en-0001", ViolationType.ILL_FORMED_EL_ISLAND)),
        ]
    )


def test_export_writes_one_file_per_task_with_items_sorted_by_id(tmp_path: Path) -> None:
    counts = export_hf(_item_set(), tmp_path)

    assert counts == {
        TaskType.GRAMMATICALITY_JUDGMENT: 2,
        TaskType.CONSTRAINED_CONTINUATION: 1,
        TaskType.ML_IDENTIFICATION: 1,
        TaskType.REPAIR: 1,
    }
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(
        f"{task.value}.jsonl" for task in TaskType
    )
    judgment = (tmp_path / "grammaticality_judgment.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in judgment.splitlines()]
    assert [row["id"] for row in rows] == ["csw-es-en-0001", "csw-es-en-0002"]
    assert rows[0]["task_type"] == "grammaticality_judgment"
    assert rows[0]["provenance"]["derivation"] == "System Morpheme Principle"


def test_every_row_carries_every_field_so_a_file_has_one_schema() -> None:
    """The dataset viewer infers one schema per file; a key present on some rows and
    absent on others reads as a schema conflict. Defaults are serialized, not dropped.
    """
    rows = export_rows(_item_set())
    repair = json.loads(rows[TaskType.REPAIR][0])

    assert repair["alternate_repairs"] == []
    assert repair["secondary_violations"] == []
    assert repair["system_morpheme_class"] is None
    assert repair["provenance"]["review_disagreement"] is None
    assert repair["violation_span"] == [1, 2]


def test_export_is_byte_identical_across_calls(tmp_path: Path) -> None:
    export_hf(_item_set(), tmp_path / "one")
    export_hf(_item_set(), tmp_path / "two")

    for task in TaskType:
        name = f"{task.value}.jsonl"
        assert (tmp_path / "one" / name).read_bytes() == (tmp_path / "two" / name).read_bytes()


def test_export_hf_command_reports_counts_and_hash(
    write_item, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write_item(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    out = tmp_path / "hf"

    assert main(["--items-root", str(tmp_path), "export-hf", str(out)]) == 0

    captured = capsys.readouterr().out
    assert f"   1  {out / 'grammaticality_judgment.jsonl'}" in captured
    assert f"   0  {out / 'repair.jsonl'}" in captured
    assert "1 items, hash " in captured
    assert (out / "repair.jsonl").read_text(encoding="utf-8") == ""


def test_export_hf_command_fails_cleanly_on_a_bad_item(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "csw-es-en-0001.json").write_text("{not json", encoding="utf-8")

    assert main(["--items-root", str(tmp_path), "export-hf", str(tmp_path / "hf")]) == 1
    assert "FAIL" in capsys.readouterr().err
