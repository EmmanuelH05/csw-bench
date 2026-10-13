"""Rubric implementation for docs/design.md §4.

Scoring is substring- and pattern-based, which is adequate for constrained responses and
brittle against free prose: a model that answers correctly in an unanticipated phrasing
can still score zero, indistinguishable from incompetence. `extract_final_answer` strips
a leaked `<think>...</think>` reasoning preamble ahead of judgment/continuation/repair
scoring, and `score_ml_identification`'s label check reads the response's explicit claim
("X is the Matrix Language", "the grammatical frame is X") before falling back to mention
position -- both implemented and verified against real model output (`docs/journal.md`,
Phase 3 pilot and Phase 4 full runs), not merely planned. Neither closes the underlying
brittleness class, only the concrete instances found running real models so far; treat
scores as a lower bound.

The hedging patterns are English-only, so a Spanish-language hedge currently slips
through. Both gaps are recorded in docs/design.md §4.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from csw_bench.schema import (
    ConstrainedContinuationItem,
    GrammaticalityJudgmentItem,
    Item,
    MlIdentificationItem,
    RepairItem,
)
from csw_bench.taxonomy import Language, TaskType
from csw_bench.textnorm import normalize, tokenize

MAX_POINTS: dict[TaskType, int] = {
    TaskType.GRAMMATICALITY_JUDGMENT: 1,
    TaskType.ML_IDENTIFICATION: 3,
    TaskType.CONSTRAINED_CONTINUATION: 2,
    TaskType.REPAIR: 2,
}

CHANCE_FLOOR: dict[TaskType, float] = {
    TaskType.GRAMMATICALITY_JUDGMENT: 0.5,
    # Every shipped ml_identification item has Spanish as its Matrix Language, so the
    # constant answer "Spanish" earns the label point (1 of 3) on every item with no
    # analysis at all. Chance for this task is that strategy's score, not 0; only the
    # evidence points discriminate on this item set (docs/limitations.md). Pinned to the
    # shipped label distribution by tests/test_shipped_set.py.
    TaskType.ML_IDENTIFICATION: 1 / 3,
    TaskType.CONSTRAINED_CONTINUATION: 0.0,
    TaskType.REPAIR: 0.0,
}

_NON_COMMITTAL = re.compile(
    r"\b(it depends|both are|either could|cannot determine|can't determine|"
    r"no single|equally|ambiguous|unclear|as an ai|i cannot|i can't)\b",
    re.IGNORECASE,
)

_LEXICAL_EVIDENCE = re.compile(
    r"\b(more (spanish|english) words|mostly (spanish|english)|majority of the words|"
    r"word count|number of words|most of the (words|vocabulary)|lexical frequency)\b",
    re.IGNORECASE,
)


def extract_final_answer(response: str) -> str:
    """Strips a leaked reasoning preamble, keeping only what follows the last `</think>`.

    Found running the real Phase 3 pilot against qwen3:30b: despite `think=False`
    (providers.py), the model's opening `<think>` tag is stripped by Ollama's chat
    template but the closing `</think>` -- and every token of reasoning before it --
    leaks into `response.message.content` anyway. Every judgment/continuation/repair
    prompt asks for the target utterance "and nothing else"; a response that quotes both
    the licensed and violating members while explaining its reasoning, then gives the
    real answer after `</think>`, is not an ambiguous or incorrect answer -- it's a
    correct answer wrapped in exactly the free prose docs/design.md already names as
    "Phase 3 needs a response-extraction step ahead of scoring." A no-op for any response
    without a literal `</think>` (e.g. gpt-oss, which separates reasoning into its own
    field rather than leaking it into content).

    Deliberately NOT applied to ml_identification: that task explicitly asks the model to
    cite morphosyntactic evidence, and a model that reasons its way to the right evidence
    inside a leaked preamble should still get credit for having cited it -- stripping the
    preamble there would remove evidence rather than noise.
    """
    marker = "</think>"
    idx = response.rfind(marker)
    if idx == -1:
        return response
    return response[idx + len(marker) :].strip()


@dataclass(frozen=True)
class Score:
    points: int
    max_points: int
    reason: str

    @property
    def normalized(self) -> float:
        return self.points / self.max_points if self.max_points else 0.0


def is_non_committal(response: str) -> bool:
    """Hedging scores zero rather than partial. A benchmark that lets models opt out
    measures willingness, not competence.
    """
    return bool(_NON_COMMITTAL.search(response))


def score_grammaticality_judgment(item: GrammaticalityJudgmentItem, response: str) -> Score:
    """Forced 2AFC against a 50% floor. No partial credit -- a rating scale would invite
    hedging toward the midpoint, which is exactly what the rubric forbids.
    """
    maximum = MAX_POINTS[TaskType.GRAMMATICALITY_JUDGMENT]
    if is_non_committal(response):
        return Score(0, maximum, "declined to commit")

    normalized = normalize(response)
    norm_licensed = normalize(item.licensed)
    norm_violating = normalize(item.violating)
    picked_licensed = norm_licensed in normalized
    picked_violating = norm_violating in normalized

    if picked_licensed and picked_violating:
        # Deletion-based pairs (T5 bare forms) can make one member a substring of the
        # other, so echoing the longer member matches both. When every occurrence of the
        # shorter member falls inside an occurrence of the longer, the response echoed
        # only the longer member, and that is the selection.
        shorter, longer = sorted((norm_licensed, norm_violating), key=len)
        if shorter in longer and normalized.count(shorter) == normalized.count(
            longer
        ) * longer.count(shorter):
            picked_licensed = longer == norm_licensed
            picked_violating = longer == norm_violating

    if picked_licensed and not picked_violating:
        return Score(maximum, maximum, "selected the licensed member")
    if picked_violating and not picked_licensed:
        return Score(0, maximum, "selected the violating member")
    return Score(0, maximum, "no unambiguous selection")


_MATRIX_LANGUAGE_PHRASE = re.compile(r"matrix language")
_LANGUAGE_NAME = re.compile(r"spanish|english")
_CLAIM_WINDOW = 200
"""Characters searched on either side of a "matrix language" mention for the nearest
language name. Generous enough to span a quoted utterance sitting between the phrase and
the verb ("The Matrix Language in the utterance "..." is Spanish"), the exact gap in the
qwen3:30b response that motivated this design -- see score_ml_identification's docstring.
"""

_LANG = r"(spanish|english)"
# "grammatical frame" is template b's wording; a response that never says "matrix
# language" is answering the question it was asked, not dodging it (Phase 3 gate).
_FRAME = r"(?:matrix language|(?:grammatical|morphosyntactic) frame(?:work)?)"
_COPULA = r"(?:is|remains|must be|should be|would be|appears to be)"
_QUALIFIER = r"(?:clearly |therefore |thus |unambiguously |definitively |the )?"
_BY = r"(?:(?:set|supplied|provided|established|determined|governed) by )?"
_DEICTIC = (
    r"(?:ml |here |identified |"
    r"(?:in|of|for) this (?:code switched |mixed )?(?:utterance|sentence|clause) )?"
)
_QUOTED = (
    r"(?:in|of|for) (?:the|this) (?:code switched |mixed )?(?:utterance|sentence|clause) "
    r"(?:(?:(?!spanish|english|frame|matrix language).){0,120}? )?"
)
# "Spanish, not English, is the Matrix Language"; "whether English is the Matrix
# Language". Adjacency is not polarity: a marker not listed here still reads as a claim.
_NOT_PRECEDED = r"(?<!not )(?<!no )(?<!neither )(?<!nor )(?<!whether )(?<!if )(?<!than )"
_EXPLICIT_CLAIMS = tuple(
    re.compile(pattern)
    for pattern in (
        # "Spanish is / as / sets / supplies the Matrix Language"; "Spanish, not English,
        # is the Matrix Language"
        rf"{_NOT_PRECEDED}\b{_LANG}(?: not (?:spanish|english))? (?:is|as|sets|supplies|"
        rf"provides|establishes|determines|serves as|functions as|acts as|remains|must be|"
        rf"should be) the {_FRAME}\b",
        # "the Matrix Language (here / in this utterance) is (set by) Spanish"
        rf"\b{_FRAME} {_DEICTIC}{_COPULA} {_QUALIFIER}{_BY}{_LANG}\b",
        # "the Matrix Language in the utterance '...' is Spanish"
        rf"\b{_FRAME} {_QUOTED}{_COPULA} {_QUALIFIER}{_BY}{_LANG}\b",
    )
)
# "Matrix Language: Spanish. Why Spanish is ..." -- a heading, its colon lost to
# normalization, recognised only when what follows reads like the answer's body.
_HEADING_CLAIM = re.compile(
    rf"\b{_FRAME} (?:identification )?(?:ml )?{_LANG}(?: (?=morphosyntactic|evidence|why|"
    r"justification|because|governing|supplies|dictates|provides|sets|the |1 |feature|"
    r"conclusion|reason)|$)"
)
"""The claim shapes read off real responses, 2026-08-27 through 2026-09-10. "is not
English" and "does not make English the Matrix Language" match nothing because the verb
must sit between the name and the phrase; a negation or hypothetical marker in front of
the name is excluded by `_NOT_PRECEDED`, and only the markers it lists. A shape not
listed here falls through to the nearest-name heuristic below.
"""


def _explicit_claims(normalized: str) -> list[tuple[int, int, str]]:
    claims = [
        (match.start(), match.end(), match.group(1))
        for pattern in _EXPLICIT_CLAIMS
        for match in pattern.finditer(normalized)
    ]
    # A heading-shaped match whose frame phrase is the tail of a phrased claim ("English
    # as the Matrix Language; Spanish provides the lexical content") is not a claim.
    claims.extend(
        (match.start(), match.end(), match.group(1))
        for match in _HEADING_CLAIM.finditer(normalized)
        if not any(start <= match.start() < end for start, end, _ in claims)
    )
    return claims


def _claimed_matrix_language(normalized: str) -> str | None:
    """The language the response claims as the frame: the *last* explicit claim if it
    makes one, else the language name nearest its last "matrix language" mention. None
    when neither is available, so the caller can fall back to whole-text last mention.

    The nearest-name rule was the whole test until 2026-09-10. At full scale it zeroed
    11 of qwen3:30b's 100 answers, every one concluding "Spanish as the Matrix Language
    with English lexical items inserted" -- the incidental "English" six characters after
    the phrase beat the claimed "Spanish" eight characters before it -- and credited one
    answer that said "English is the Matrix Language" a dozen times because its final
    table row read "English matrix language | Spanish embedded". Read before written:
    every record the explicit rule moves was checked by hand (docs/journal.md).
    """
    claims = _explicit_claims(normalized)
    if claims:
        return max(claims, key=lambda claim: claim[0])[2]

    phrase_spans = list(_MATRIX_LANGUAGE_PHRASE.finditer(normalized))
    if not phrase_spans:
        return None
    phrase = phrase_spans[-1]
    window = normalized[max(0, phrase.start() - _CLAIM_WINDOW) : phrase.end() + _CLAIM_WINDOW]
    anchor = phrase.start() - max(0, phrase.start() - _CLAIM_WINDOW)

    closest: str | None = None
    closest_distance = None
    for match in _LANGUAGE_NAME.finditer(window):
        distance = min(
            abs(match.start() - anchor), abs(match.end() - (anchor + len(phrase.group())))
        )
        if closest_distance is None or distance < closest_distance:
            closest, closest_distance = match.group(), distance
    return closest


def score_ml_identification(item: MlIdentificationItem, response: str) -> Score:
    """Label and evidence are scored separately so that reaching a correct label by
    counting words stays visible instead of being indistinguishable from analysis.
    """
    maximum = MAX_POINTS[TaskType.ML_IDENTIFICATION]
    if is_non_committal(response):
        return Score(0, maximum, "declined to commit or named no single ML")

    normalized = normalize(response)
    expected = "spanish" if item.matrix_language is Language.SPANISH else "english"
    other = "english" if expected == "spanish" else "spanish"

    # A correct, well-evidenced answer mentions BOTH language names many times, so raw
    # mention position (first or last) is not the claim -- found on the Phase 3 pilot,
    # whose qwen3:30b answer opened "The Matrix Language ... is Spanish" and closed
    # "...overriding the English lexical item 'the'". Whole-text last mention is the
    # fallback only when the response never phrases a claim at all.
    claimed = _claimed_matrix_language(normalized)
    if claimed is not None:
        if claimed != expected:
            return Score(0, maximum, "wrong or unclear Matrix Language")
    else:
        names_expected = expected in normalized
        names_other = other in normalized
        if not names_expected or (
            names_other and normalized.rindex(other) > normalized.rindex(expected)
        ):
            return Score(0, maximum, "wrong or unclear Matrix Language")

    if _LEXICAL_EVIDENCE.search(response):
        return Score(1, maximum, "correct label, lexical-frequency reasoning")

    matched = sum(1 for evidence in item.required_evidence if normalize(evidence) in normalized)
    if matched >= 2:
        return Score(3, maximum, "correct label, morphosyntactic evidence")
    if matched == 1:
        return Score(2, maximum, "correct label, partial morphosyntactic evidence")
    return Score(1, maximum, "correct label, no evidence cited")


def score_constrained_continuation(item: ConstrainedContinuationItem, response: str) -> Score:
    """Monolingual output scores zero. Without that rule a model dodges every item in
    this task by answering in one language.
    """
    maximum = MAX_POINTS[TaskType.CONSTRAINED_CONTINUATION]
    if is_non_committal(response):
        return Score(0, maximum, "declined to continue")

    normalized = normalize(response)
    if any(normalize(v) in normalized for v in item.violating_continuations):
        return Score(0, maximum, "produced a violating continuation")
    if any(normalize(candidate) in normalized for candidate in item.licensed_continuations):
        return Score(maximum, maximum, "produced a licensed continuation")
    return Score(0, maximum, "continuation matched no recorded licensed form")


def score_repair(item: RepairItem, response: str, minimality_threshold: float) -> Score:
    """Wholesale rewrites score zero even when grammatical: the task tests whether the
    model can locate the violation, not whether it can produce a clean sentence.

    `minimality_threshold` is fixed in Phase 3 against real repairs and frozen. It is a
    required argument rather than a default so that no run can silently use an
    uncalibrated value.
    """
    maximum = MAX_POINTS[TaskType.REPAIR]
    if is_non_committal(response):
        return Score(0, maximum, "declined to repair")

    produced = tokenize(response)
    if not produced:
        return Score(0, maximum, "empty response")

    accepted = [item.gold_repair, *item.alternate_repairs]
    if not any(produced == tokenize(a) for a in accepted):
        return Score(0, maximum, "did not reach the gold repair")

    original = tokenize(item.violating)
    similarity = SequenceMatcher(None, original, produced).ratio()
    if similarity >= minimality_threshold:
        return Score(maximum, maximum, "repaired minimally")
    return Score(1, maximum, "repaired, but edits exceeded the violation site")


def score(item: Item, response: str, minimality_threshold: float | None = None) -> Score:
    match item:
        case GrammaticalityJudgmentItem():
            return score_grammaticality_judgment(item, extract_final_answer(response))
        case MlIdentificationItem():
            return score_ml_identification(item, response)
        case ConstrainedContinuationItem():
            return score_constrained_continuation(item, extract_final_answer(response))
        case RepairItem():
            if minimality_threshold is None:
                raise ValueError("repair items require an explicit minimality_threshold")
            return score_repair(item, extract_final_answer(response), minimality_threshold)
