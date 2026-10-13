"""Buckets every constrained_continuation response in one or more runs by what the
model did instead of reproducing a recorded string: the full-scale check on the
EL-island escape hatch (docs/findings.md), and the source of the one continuation number
the hatch cannot distort -- the violation-production rate.

`score_constrained_continuation` recognizes exactly two strings per item; everything
else scores 0 as "matched no recorded licensed form", which folds a fluent licensed
island, a monolingual dodge, and a genuine failure into one number. The buckets here are
a lexical heuristic (English determiners, Spanish and English function words) over the
text after the prompt, not a parse. They say roughly how the unmatched mass splits and
pull samples for hand inspection; they rescore nothing.

Usage: uv run python scripts/continuation_escape_hatch.py <run_dir> [<run_dir> ...]
           [--items-root data/items] [--samples 3]
"""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path

from csw_bench.loader import load_items
from csw_bench.results import load_run
from csw_bench.runner import RunRecord
from csw_bench.schema import ConstrainedContinuationItem
from csw_bench.scoring import extract_final_answer
from csw_bench.taxonomy import TaskType, ViolationType
from csw_bench.textnorm import normalize

# No "a": it is also the Spanish preposition and personal a, among the most frequent
# tokens in any Spanish continuation, and would route Spanish text into the island
# buckets. Likewise "no" belongs to both languages and sits in neither lexicon.
EN_DETERMINERS = frozenset(
    {"the", "an", "my", "your", "his", "her", "our", "their", "this", "that", "these", "those"}
)
EN_FUNCTION = EN_DETERMINERS | {
    *("i", "you", "we", "they", "it", "and", "or", "but", "for", "with", "to", "of"),
    *("in", "on", "at", "is", "are", "was", "were"),
}
ES_FUNCTION = frozenset(
    {
        *("el", "la", "los", "las", "un", "una", "unos", "unas"),
        *("mi", "mis", "tu", "tus", "su", "sus", "nuestro", "nuestra"),
        *("de", "del", "al", "que", "para", "por", "con", "en", "y", "o"),
        *("es", "esta", "estan", "son", "ayer", "hoy", "manana", "ahorita"),
        *("siempre", "todos", "cada", "muy", "mas"),
    }
)

SCORED = {
    "produced a violating continuation": "violating",
    "produced a licensed continuation": "licensed_exact",
    "declined to continue": "declined",
}
BUCKETS = (
    "violating",
    "licensed_exact",
    "island_english_only",
    "island_mixed",
    "no_english_function_words",
    "other_unmatched",
    "declined",
)


def continuation_after_prompt(item: ConstrainedContinuationItem, response: str) -> str:
    """Text after the model's last echo of the prompt, matched at word boundaries so a
    short prompt ("Vio") is not found inside a longer word ("avion")."""
    answer = normalize(extract_final_answer(response))
    echoes = list(re.finditer(rf"\b{re.escape(normalize(item.prompt))}\b", answer))
    return answer[echoes[-1].end() :].strip() if echoes else answer


def bucket(item: ConstrainedContinuationItem, record: RunRecord) -> tuple[str, str]:
    if record.reason in SCORED:
        return SCORED[record.reason], ""
    continuation = continuation_after_prompt(item, record.response_text)
    tokens = set(continuation.split())
    if tokens & EN_DETERMINERS:
        return ("island_mixed" if tokens & ES_FUNCTION else "island_english_only"), continuation
    if not tokens & EN_FUNCTION:
        return "no_english_function_words", continuation
    return "other_unmatched", continuation


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("run_dirs", type=Path, nargs="+")
    parser.add_argument("--items-root", type=Path, default=Path("data/items"))
    parser.add_argument("--samples", type=int, default=3)
    args = parser.parse_args()

    item_set = load_items(args.items_root)
    items = {i.id: i for i in item_set if isinstance(i, ConstrainedContinuationItem)}
    stimuli = ", ".join(
        f"{v.value} {sum(1 for i in items.values() if i.primary_violation is v)} items / "
        f"{len({i.prompt for i in items.values() if i.primary_violation is v})} distinct prompts"
        for v in ViolationType
    )
    print(
        f"continuation stimuli: {stimuli}. Items sharing a prompt share one response at "
        "temperature 0; every count below is over records, not independent responses.\n"
    )

    for run_dir in args.run_dirs:
        result = load_run(run_dir)
        if result.item_set_hash != item_set.hash():
            raise SystemExit(
                f"{run_dir} was run over item set {result.item_set_hash[:12]}, not the "
                f"{item_set.hash()[:12]} under {args.items_root}; a prompt from a different "
                "item version would be stripped wrongly, so pass the matching --items-root"
            )
        config = result.config
        print(f"## {run_dir.name}  (model {config.model}, template {config.template_id})")

        counts: dict[ViolationType | None, Counter[str]] = defaultdict(Counter)
        errored: Counter[ViolationType | None] = Counter()
        samples: dict[tuple[ViolationType, str], list[tuple[str, str]]] = defaultdict(list)
        for record in result.records:
            if record.task_type is not TaskType.CONSTRAINED_CONTINUATION:
                continue
            if record.errored:
                errored[record.primary_violation] += 1
                errored[None] += 1
                continue
            name, text = bucket(items[record.item_id], record)
            counts[record.primary_violation][name] += 1
            counts[None][name] += 1
            cell = samples[(record.primary_violation, name)]
            if name not in SCORED.values() and len(cell) < args.samples:
                cell.append((record.item_id, text))

        head = f"{'violation':<10} {'scored':>6} {'errored':>7} " + " ".join(
            f"{b:>{max(len(b), 6)}}" for b in BUCKETS
        )
        print(head + f" {'viol. rate':>10}")
        for violation in (*ViolationType, None):
            tally = counts[violation]
            scored = sum(tally.values())
            rate = f"{tally['violating'] / scored:.2f}" if scored else "-"
            label = violation.value if violation else "all"
            row = f"{label:<10} {scored:>6} {errored[violation]:>7} "
            row += " ".join(f"{tally[b]:>{max(len(b), 6)}}" for b in BUCKETS)
            print(row + f" {rate:>10}")
        print(
            "\nviol. rate = violating / scored: the share of continuations that reproduce the "
            "item's recorded MLF violation string. A lower bound: a violation built on a "
            "different word lands in an unmatched bucket. Buckets other than "
            "violating/licensed_exact/declined are a lexical heuristic, not a parse; read the "
            "samples."
        )

        print(f"\nsamples ({args.samples} per cell, text after the prompt):")
        for (violation, name), cell in sorted(samples.items()):
            for item_id, text in cell:
                print(f"  [{violation.value} {name}] {item_id}: {text[:120]!r}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
