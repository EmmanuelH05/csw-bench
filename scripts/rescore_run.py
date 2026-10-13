"""Recomputes scores for an existing run from its persisted raw responses, without
re-invoking the provider.

Exists because a scoring bug fix (or a minimality-threshold recalibration) shouldn't
require re-running -- and re-billing -- every model. `runner.run()` already keeps every
raw response for exactly this reason ("rerunnable from cache without re-billing" is a
Phase 3 requirement); this is the other half of that promise: rerunning the *scorer*,
not just the provider, against material already collected.

Usage: uv run python scripts/rescore_run.py <run_dir> [--minimality-threshold 0.7]
Overwrites records.jsonl and run.json in place. The original item_set_hash and
accounting are preserved -- only points/max_points/reason (and errored's exemption from
them) can change.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from csw_bench.loader import load_items
from csw_bench.results import load_run
from csw_bench.runner import RunRecord, RunResult
from csw_bench.scoring import score


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--items-root", type=Path, default=Path("data/items"))
    parser.add_argument("--minimality-threshold", type=float, default=None)
    args = parser.parse_args()

    result = load_run(args.run_dir)
    item_set = load_items(args.items_root)
    if item_set.hash() != result.item_set_hash:
        print(
            f"WARNING: {args.items_root} hash {item_set.hash()[:12]} does not match "
            f"the run's recorded hash {result.item_set_hash[:12]} -- rescoring against "
            "a different item set than the run actually saw."
        )
    by_id = {item.id: item for item in item_set}

    threshold = (
        args.minimality_threshold
        if args.minimality_threshold is not None
        else result.config.minimality_threshold
    )

    new_records: list[RunRecord] = []
    changed = 0
    for record in result.records:
        if record.errored or record.item_id not in by_id:
            new_records.append(record)
            continue
        item = by_id[record.item_id]
        new_score = score(item, record.response_text, threshold)
        if (new_score.points, new_score.reason) != (record.points, record.reason):
            changed += 1
        new_records.append(
            record.model_copy(
                update={
                    "points": new_score.points,
                    "max_points": new_score.max_points,
                    "reason": new_score.reason,
                }
            )
        )

    new_config = result.config.model_copy(update={"minimality_threshold": threshold})
    new_result = RunResult(
        config=new_config,
        item_set_hash=result.item_set_hash,
        prices=result.prices,
        accounting=result.accounting,
        records=tuple(new_records),
    )

    (args.run_dir / "run.json").write_text(
        new_result.model_dump_json(indent=2, exclude={"records"}), encoding="utf-8"
    )
    with (args.run_dir / "records.jsonl").open("w", encoding="utf-8") as sink:
        for record in new_records:
            sink.write(record.model_dump_json() + "\n")

    print(f"{changed}/{len(new_records)} records changed score, threshold={threshold}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
