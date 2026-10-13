"""Prompt templates, two deliberately paraphrased variants per task type.

Phase 3 reports the score delta between templates "a" and "b": a large delta means the
benchmark measures prompt phrasing rather than competence. The templates are fixed
strings versioned with the code -- editing one after results exist invalidates the
comparison, so treat them like items, not like copy.

Every template instructs the model to answer with the target utterance verbatim, because
the scorer matches normalized substrings and free prose around the answer is the one
noise source it tolerates.
"""

from __future__ import annotations

import hashlib

from csw_bench.schema import (
    ConstrainedContinuationItem,
    GrammaticalityJudgmentItem,
    Item,
    MlIdentificationItem,
    RepairItem,
)

TEMPLATE_IDS: tuple[str, ...] = ("a", "b")


def judgment_member_order(item: GrammaticalityJudgmentItem) -> tuple[str, str]:
    """Presentation order is derived from the item id: deterministic across runs, with no
    RNG state to carry, and balanced across the set so a model cannot beat the 50% floor
    by always picking the same position.
    """
    if hashlib.sha256(item.id.encode()).digest()[0] % 2 == 0:
        return item.licensed, item.violating
    return item.violating, item.licensed


_JUDGMENT = {
    "a": (
        "Below are two Spanish/English code-switched sentences. Exactly one is "
        "acceptable to a fluent bilingual speaker.\n\n"
        "(1) {first}\n"
        "(2) {second}\n\n"
        "Reply with the acceptable sentence copied verbatim, and nothing else."
    ),
    "b": (
        "You will see two mixed Spanish-English utterances. One violates the grammar of "
        "bilingual code-switching; the other does not.\n\n"
        "A. {first}\n"
        "B. {second}\n\n"
        "Answer by repeating, word for word, only the utterance that does not violate it."
    ),
}

_IDENTIFICATION = {
    "a": (
        "Consider this code-switched utterance:\n\n"
        '"{utterance}"\n\n'
        "Which language is the Matrix Language -- the one supplying the morphosyntactic "
        "frame? Name it, then cite the morphosyntactic evidence: which system morphemes "
        "and whose constituent order govern the clause."
    ),
    "b": (
        "Here is an utterance mixing Spanish and English:\n\n"
        '"{utterance}"\n\n'
        "One of the two languages sets the grammatical frame of the sentence. Say which, "
        "and justify it from the morphosyntax -- inflections, function words, word order "
        "-- not from how many words each language contributes."
    ),
}

_CONTINUATION = {
    "a": (
        "Complete this code-switched utterance the way a fluent Spanish-English "
        "bilingual would:\n\n"
        '"{prompt}"\n\n'
        "Reply with the completed utterance only."
    ),
    "b": (
        "A Spanish-English bilingual breaks off mid-sentence:\n\n"
        '"{prompt}"\n\n'
        "Finish the sentence naturally, keeping the mix of both languages. Give only the "
        "finished sentence."
    ),
}

_REPAIR = {
    "a": (
        "The following code-switched utterance contains exactly one grammatical error in "
        "how the two languages combine:\n\n"
        '"{violating}"\n\n'
        "Rewrite it with the smallest change that fixes the error. Reply with the "
        "corrected utterance only."
    ),
    "b": (
        "This mixed Spanish-English sentence is ill-formed:\n\n"
        '"{violating}"\n\n'
        "Correct it, changing as little as possible. Your entire reply must be the "
        "repaired sentence."
    ),
}


def render(item: Item, template_id: str) -> str:
    if template_id not in TEMPLATE_IDS:
        raise ValueError(f"unknown template id {template_id!r}; expected one of {TEMPLATE_IDS}")
    match item:
        case GrammaticalityJudgmentItem():
            first, second = judgment_member_order(item)
            return _JUDGMENT[template_id].format(first=first, second=second)
        case MlIdentificationItem():
            return _IDENTIFICATION[template_id].format(utterance=item.utterance)
        case ConstrainedContinuationItem():
            return _CONTINUATION[template_id].format(prompt=item.prompt)
        case RepairItem():
            return _REPAIR[template_id].format(violating=item.violating)
