"""Scoring for `csw_bench_repair`, ported from `csw_bench.scoring.score_repair` and
`csw_bench.textnorm` so the task runs inside lm-evaluation-harness without csw-bench
installed. `tests/test_la_leaderboard_port.py` checks this file against the canonical
scorer over every repair item on disk; change both or neither.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

MINIMALITY_THRESHOLD = 0.7
"""Frozen in csw-bench Phase 3 (docs/design.md section 4); every committed run used it."""

_NON_COMMITTAL = re.compile(
    r"\b(it depends|both are|either could|cannot determine|can't determine|"
    r"no single|equally|ambiguous|unclear|as an ai|i cannot|i can't)\b",
    re.IGNORECASE,
)


def normalize(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text.casefold())
    stripped = "".join(c for c in folded if not unicodedata.combining(c))
    despaced = re.sub(r"[^\w\s]", " ", stripped)
    return re.sub(r"\s+", " ", despaced).strip()


def tokenize(text: str) -> list[str]:
    return normalize(text).split()


def extract_final_answer(response: str) -> str:
    marker = "</think>"
    idx = response.rfind(marker)
    if idx == -1:
        return response
    return response[idx + len(marker) :].strip()


def repair_points(doc: dict[str, Any], response: str) -> int:
    """0: no repair, hedge, or a wrong one. 1: reached a gold repair by rewriting more
    than the violation site. 2: reached it minimally.
    """
    answer = extract_final_answer(response)
    if _NON_COMMITTAL.search(answer):
        return 0
    produced = tokenize(answer)
    if not produced:
        return 0
    accepted = [doc["gold_repair"], *doc["alternate_repairs"]]
    if not any(produced == tokenize(a) for a in accepted):
        return 0
    similarity = SequenceMatcher(None, tokenize(doc["violating"]), produced).ratio()
    return 2 if similarity >= MINIMALITY_THRESHOLD else 1


def process_results_repair(doc: dict[str, Any], results: list[str]) -> dict[str, float]:
    points = repair_points(doc, results[0])
    return {"repair_score": points / 2, "repair_minimal": float(points == 2)}
