# Phase 4 blind-review sample

Expected contents, read by `scripts/compute_ceiling.py` and `scripts/score_phase4_review.py`:

- `review_sample_ids.txt` — one item id per line, the stratified sample (10 per
  violation x task-type cell, 120 total in the original pass)
- `review_answers_*.json` — one file per review batch, a JSON list of
  `{"id": "<item id>", "answer": "<the reviewer's verbatim answer>"}`

**Currently empty.** The pass recorded in `docs/journal.md` ("Phase 4 blind review",
2026-08-24) wrote these files to `/tmp`, which was cleared before they were committed.
The agreement rates and construction-time ceiling quoted in `docs/` are therefore
historical figures, not reproducible from this repository until a new blind pass is
collected into this directory. `docs/limitations.md` carries this as a named gap.
