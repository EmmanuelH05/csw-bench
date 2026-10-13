"""Scores the Phase 4 blind-review sample (data/review/phase4-blind-sample/) against gold
labels, using the same construct-validity-agreement judgment Phase 2 used rather than
the raw automated scorer -- docs/design.md already documents why the automated scorer
under-credits correct free-text answers (ml_identification especially), so grading the
review sample against it would reproduce that same known artifact rather than measure
review agreement.

Prints a table of (id, task_type, agree/disagree, note) and the aggregate rate. Not part
of the package -- one-shot, run after all review-batch agents finish.
"""

from __future__ import annotations

import json
from pathlib import Path

from csw_bench.loader import load_item
from csw_bench.schema import (
    ConstrainedContinuationItem,
    GrammaticalityJudgmentItem,
    Item,
    MlIdentificationItem,
    RepairItem,
)
from csw_bench.taxonomy import Language
from csw_bench.textnorm import normalize


def judge(item: Item, answer: str) -> tuple[bool, str]:
    """Construct-validity agreement, dispatched on the item class rather than on
    `task_type`'s string value: the class is what carries the fields each branch reads,
    so a mismatch between the two becomes a type error here instead of a silently wrong
    branch.
    """
    norm_answer = normalize(answer)
    match item:
        case GrammaticalityJudgmentItem():
            agree = (
                normalize(item.licensed) in norm_answer
                and normalize(item.violating) not in norm_answer
            )
            return agree, "picked licensed" if agree else f"answer={answer!r}"
        case ConstrainedContinuationItem():
            agree = any(
                normalize(c) in norm_answer for c in item.licensed_continuations
            ) and not any(normalize(c) in norm_answer for c in item.violating_continuations)
            return agree, "picked licensed" if agree else f"answer={answer!r}"
        case MlIdentificationItem():
            expected = "spanish" if item.matrix_language is Language.SPANISH else "english"
            other = "english" if expected == "spanish" else "spanish"
            agree = expected in norm_answer and other not in norm_answer.split(expected)[0]
            return agree, f"named {expected}" if agree else f"answer={answer!r}"
        case RepairItem():
            accepted = [item.gold_repair, *item.alternate_repairs]
            agree = any(
                normalize(a) in norm_answer or norm_answer in normalize(a) for a in accepted
            )
            if agree:
                return True, "reached gold"
            return False, f"answer={answer!r} gold={item.gold_repair!r}"


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

print(f"loaded {len(answers)} answers")

ids = [line.strip() for line in ids_path.read_text(encoding="utf-8").splitlines() if line.strip()]
missing = [i for i in ids if i not in answers]
if missing:
    print(f"MISSING answers for: {missing}")

rows = []
for item_id in ids:
    if item_id not in answers:
        continue
    item = load_item(Path(f"data/items/es-en/{item_id}.json"))
    agree, note = judge(item, answers[item_id])
    rows.append((item_id, item.task_type.value, item.primary_violation.value, agree, note))

if not rows:
    raise SystemExit(
        f"none of the {len(ids)} sampled ids has an answer in {REVIEW_DIR}; there is "
        "nothing to score"
    )

print(f"\n{'id':<20} {'task':<26} {'viol':<5} {'agree':<7} note")
for item_id, task, viol, agree, note in rows:
    print(f"{item_id:<20} {task:<26} {viol:<5} {agree!s:<7} {note[:80]}")

n_agree = sum(1 for r in rows if r[3])
print(f"\n{n_agree}/{len(rows)} agreement ({100 * n_agree / len(rows):.1f}%)")

disagreements = [r for r in rows if not r[3]]
print(f"\n{len(disagreements)} disagreements:")
for item_id, task, viol, _, note in disagreements:
    print(f"  {item_id} [{viol} {task}]: {note}")
