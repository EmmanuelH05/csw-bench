"""The frozen item set as one JSONL file per task type: the layout the Hugging Face
dataset card (`data/hf/README.md`) declares as its configs, and the only copy of the
data that lives anywhere other than `data/items/`.

Derived, never edited. `csw-bench export-hf` regenerates it, and
`tests/test_shipped_set.py` fails when the committed export drifts from the items on
disk, the same way it fails when the items drift from the recorded hash.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from csw_bench.loader import ItemSet
from csw_bench.taxonomy import TaskType


def export_rows(item_set: ItemSet) -> dict[TaskType, list[str]]:
    """One JSON line per item, items sorted by id and keys sorted, with every field
    present (defaults included) so each file has one schema for the dataset viewer to
    infer. Byte-identical across runs, which is what lets the committed copy be checked
    rather than trusted. Same payload `ItemSet.hash` digests.
    """
    rows: dict[TaskType, list[str]] = defaultdict(list)
    for item in sorted(item_set, key=lambda i: i.id):
        payload = item.model_dump(mode="json")
        rows[item.task_type].append(json.dumps(payload, sort_keys=True, ensure_ascii=False))
    return {task: rows[task] for task in TaskType}


def export_hf(item_set: ItemSet, out_dir: Path) -> dict[TaskType, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[TaskType, int] = {}
    for task, lines in export_rows(item_set).items():
        path = out_dir / f"{task.value}.jsonl"
        path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
        counts[task] = len(lines)
    return counts
