"""Computes the Phase 4 construction-time ceiling from the blind-review sample in
data/review/phase4-blind-sample/ (see docs/journal.md, "Phase 4 blind review").

Per docs/charter.md's Phase 4 amendment: no human ceiling (no raters recruited), so the
reference point is "the item author's own blind pass at each item -- scored the same way
a model would be, before the gold label is consulted." The blind-review agents already
did exactly this: answered each rendered prompt with no visibility into the gold label,
in the same format a model's response would take. This script scores those same answers
with the real `csw_bench.scoring.score` function (not the looser construct-validity
check `score_phase4_review.py` uses) and aggregates them through the real
`csw_bench.results.summarize` pipeline, so the ceiling is reported in the same units as
the eventual model results table -- directly comparable, not a separate approximation.

Not part of the package -- one-shot, run after the review-answer files exist.
"""

from __future__ import annotations

import json
from pathlib import Path

from csw_bench.loader import load_item
from csw_bench.results import format_report, summarize
from csw_bench.runner import RunRecord
from csw_bench.scoring import MAX_POINTS, score

MINIMALITY_THRESHOLD = 0.7

REVIEW_DIR = Path("data/review/phase4-blind-sample")

answer_paths = sorted(REVIEW_DIR.glob("review_answers_*.json"))
ids_path = REVIEW_DIR / "review_sample_ids.txt"
if not answer_paths or not ids_path.is_file():
    raise SystemExit(
        f"{REVIEW_DIR} holds no blind-review sample (see its README.md). The original "
        "Phase 4 pass lived in /tmp and was lost before it was committed; the figures in "
        "docs/ are historical until a new blind pass is collected into that directory."
    )

answers: dict[str, str] = {}
for path in answer_paths:
    for row in json.loads(path.read_text(encoding="utf-8")):
        answers[row["id"]] = row["answer"]

ids = [line.strip() for line in ids_path.read_text(encoding="utf-8").splitlines() if line.strip()]

records: list[RunRecord] = []
for item_id in ids:
    if item_id not in answers:
        continue
    item = load_item(Path(f"data/items/es-en/{item_id}.json"))
    response_text = answers[item_id]
    item_score = score(item, response_text, MINIMALITY_THRESHOLD)
    records.append(
        RunRecord(
            item_id=item.id,
            task_type=item.task_type,
            primary_violation=item.primary_violation,
            prompt="",
            response_text=response_text,
            cached=False,
            points=item_score.points,
            max_points=item_score.max_points,
            reason=item_score.reason,
        )
    )

print(
    f"{len(records)} sampled items scored with the real scorer (threshold={MINIMALITY_THRESHOLD})\n"
)
print(format_report(summarize(records, resamples=10_000, seed=0)))
print(f"\nfor reference, MAX_POINTS per task: { {k.value: v for k, v in MAX_POINTS.items()} }")
