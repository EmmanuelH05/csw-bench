from __future__ import annotations

from typing import Any

import pytest

from csw_bench.scoring import CHANCE_FLOOR, extract_final_answer, is_non_committal, score
from csw_bench.taxonomy import TaskType, ViolationType
from tests.conftest import judgment_item, parse, repair_item

_PROVENANCE = {
    "source": "constructed",
    "license": "MIT",
    "derivation": "System Morpheme Principle",
}


def _item(task_type: TaskType, **fields: Any) -> Any:
    payload: dict[str, Any] = {
        "id": "csw-es-en-0001",
        "task_type": task_type.value,
        "matrix_language": "es",
        "primary_violation": ViolationType.EL_SYSTEM_MORPHEME.value,
        "difficulty": "medium",
        "justification": "Constructed fixture.",
        "provenance": _PROVENANCE,
    }
    payload.update(fields)
    return parse(payload)


@pytest.mark.parametrize(
    "response",
    [
        "It depends on the variety.",
        "Both are acceptable in some dialects.",
        "I cannot determine which is correct.",
        "The two are equally grammatical.",
    ],
)
def test_hedging_is_detected(response: str) -> None:
    assert is_non_committal(response)


def test_judgment_hedging_scores_zero_not_partial() -> None:
    item = judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME)
    result = score(parse(item), "It depends on the speaker.")

    assert result.points == 0


def test_judgment_correct_choice_scores_full() -> None:
    item = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))

    assert score(item, "Compré los libros ayer.").points == 1


def test_judgment_naming_both_members_scores_zero() -> None:
    """Quoting the whole prompt back is not a selection."""
    item = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))

    result = score(item, "Compré los libros ayer. Compré the libros ayer.")

    assert result.points == 0


def test_extract_final_answer_keeps_only_text_after_the_last_think_tag() -> None:
    """qwen3:30b leaks its reasoning into content despite think=False -- the closing
    </think> tag (and everything before it) survives even though the opening <think>
    tag is stripped by Ollama's chat template. Found running the real Phase 3 pilot.
    """
    leaked = (
        "We are given two sentences... Sentence (1) is correct, sentence (2) uses "
        "English 'the'...\n</think>\n\nCompré los libros ayer."
    )

    assert extract_final_answer(leaked) == "Compré los libros ayer."


def test_extract_final_answer_is_a_noop_without_a_think_tag() -> None:
    assert extract_final_answer("Compré los libros ayer.") == "Compré los libros ayer."


def test_judgment_scores_correctly_despite_a_leaked_reasoning_preamble_naming_both_members() -> (
    None
):
    """The exact failure mode found in the real qwen3:30b pilot run: a response that
    quotes both members while reasoning about them, decided correctly, but would have
    hit test_judgment_naming_both_members_scores_zero's rule without extraction.
    """
    item = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    leaked = (
        'Sentence (1): "Compré los libros ayer." This is standard Spanish.\n'
        'Sentence (2): "Compré the libros ayer." This uses the English word "the".\n'
        "Therefore the acceptable sentence is (1).\n"
        "</think>\n\nCompré los libros ayer."
    )

    assert score(item, leaked).points == 1


def test_repair_exact_match_gate_survives_a_leaked_reasoning_preamble() -> None:
    """The exact-match gate in score_repair is the task type most vulnerable to this --
    any leaked text before the real answer means the response can never equal the gold
    string exactly.
    """
    item = parse(repair_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    leaked = "The error is 'the' where Spanish 'los' belongs.\n</think>\n\nCompré los libros ayer."

    assert score(item, leaked, minimality_threshold=0.7).points == 2


def test_judgment_chance_floor_is_reported_as_half() -> None:
    assert CHANCE_FLOOR[TaskType.GRAMMATICALITY_JUDGMENT] == 0.5


def _deletion_pair() -> Any:
    """T5-style pair where the violating member is a prefix of the licensed one, so a
    verbatim echo of the licensed member contains both.
    """
    return parse(
        judgment_item(
            "csw-es-en-0001",
            ViolationType.CONGRUENCE_FAILURE,
            licensed="Compré los libros ayer",
            violating="Compré los libros",
        )
    )


def test_judgment_echoing_the_longer_member_of_a_deletion_pair_counts_as_its_selection() -> None:
    assert score(_deletion_pair(), "Compré los libros ayer").points == 1


def test_judgment_echoing_the_shorter_member_of_a_deletion_pair_selects_it() -> None:
    result = score(_deletion_pair(), "Compré los libros")

    assert result.points == 0
    assert result.reason == "selected the violating member"


def test_judgment_echoing_both_members_of_a_deletion_pair_stays_ambiguous() -> None:
    result = score(_deletion_pair(), "Compré los libros ayer. Compré los libros.")

    assert result.points == 0
    assert result.reason == "no unambiguous selection"


def _ml_item() -> Any:
    return _item(
        TaskType.ML_IDENTIFICATION,
        utterance="Compré the libros ayer.",
        required_evidence=["preverbal clitic", "verbal inflection"],
    )


def test_ml_lexical_counting_earns_the_label_point_only() -> None:
    """Right answer by word-counting is the failure this task exists to expose."""
    result = score(_ml_item(), "Spanish, because most of the words are Spanish.")

    assert result.points == 1


def test_ml_morphosyntactic_evidence_earns_full() -> None:
    result = score(
        _ml_item(),
        "Spanish. The preverbal clitic and the verbal inflection both come from Spanish.",
    )

    assert result.points == 3


def test_ml_no_single_matrix_language_scores_zero() -> None:
    result = score(_ml_item(), "There is no single Matrix Language here.")

    assert result.points == 0


def test_ml_wrong_label_scores_zero_even_with_good_evidence() -> None:
    result = score(_ml_item(), "English, based on the preverbal clitic.")

    assert result.points == 0


def test_ml_naming_the_other_language_in_an_incidental_framing_clause_still_earns_credit() -> None:
    """A response can mention both language names without hedging -- 'this utterance
    mixes English and Spanish' is a natural way to open an answer that still commits to
    the correct label afterward. Scoring by which name appears *first* in the raw text
    rejected this exact shape (found reviewing a real model response); the fix compares
    each name's *last* mention, since that's the response's actual final commitment.
    """
    result = score(
        _ml_item(),
        "This utterance mixes English and Spanish elements. The Matrix Language is "
        "Spanish: the preverbal clitic and the verbal inflection both come from Spanish.",
    )

    assert result.points == 3


@pytest.mark.parametrize(
    "response",
    [
        # The shape that zeroed 11 of qwen3:30b's 100 full-set answers: the incidental
        # "English" after the phrase sits nearer than the claimed "Spanish" before it.
        "This is a classic case of Spanish as the Matrix Language with English lexical "
        "items inserted into its grammatical structure.",
        "The Matrix Language in the utterance 'Compré the libros ayer' is Spanish. The "
        "English article 'the' is a single inserted item.",
        "The English 'the' does not make English the Matrix Language; the Matrix "
        "Language is Spanish.",
        "Spanish, not English, is the Matrix Language.",
        "The question is whether English is the Matrix Language; it is not. Spanish is "
        "the Matrix Language: the verb carries Spanish inflection.",
        # Template b never says "matrix language".
        "Spanish sets the grammatical frame: the verb inflection is Spanish and the "
        "English 'the' is one inserted word.",
        "The grammatical frame of the sentence is set by Spanish; English contributes "
        "only vocabulary.",
    ],
)
def test_ml_explicit_claim_of_the_right_language_earns_the_label(response: str) -> None:
    assert score(_ml_item(), response).points == 1


@pytest.mark.parametrize(
    "response",
    [
        "Matrix Language: English. Morphosyntactic evidence: the verb is an English "
        "imperative; the Spanish articles are embedded material.",
        # The nearest name to the last "matrix language" mention is Spanish; the
        # claim is not.
        "The clause is governed by English as the Matrix Language; Spanish provides the "
        "lexical content within that frame.",
        "The grammatical frame is English because the noun phrase follows English order. "
        "Spanish contributes vocabulary.",
    ],
)
def test_ml_explicit_claim_of_the_wrong_language_scores_zero(response: str) -> None:
    assert score(_ml_item(), response).points == 0


def test_ml_committing_to_the_wrong_language_after_mentioning_the_right_one_scores_zero() -> None:
    """The inverse of the case above: mentioning the correct language first does not
    earn credit if the response's final commitment is the wrong one.
    """
    result = score(_ml_item(), "Some say Spanish, but I think English is the Matrix Language.")

    assert result.points == 0


def test_ml_a_correct_answer_that_names_the_other_language_afterward_as_contrast_earns_credit() -> (
    None
):
    """The case that broke the first fix's 'compare last mention of each name'
    heuristic: a real qwen3:30b response opened '...the Matrix Language ... is
    Spanish' and then, evidencing it, closed with '...overriding the English lexical
    item "the"' -- 'English' being the textually last language name in the whole
    response scored a correct, well-evidenced answer 0. The fix anchors to the
    language name nearest the actual "matrix language" claim instead of comparing raw
    last-mention position across the whole text.
    """
    result = score(
        _ml_item(),
        "The Matrix Language is Spanish, evidenced by the preverbal clitic and the "
        "verbal inflection, both overriding the English lexical item used in the "
        "mixed constituent.",
    )

    assert result.points == 3


def _continuation_item() -> Any:
    return _item(
        TaskType.CONSTRAINED_CONTINUATION,
        prompt="Ayer compré",
        licensed_continuations=["los libros"],
        violating_continuations=["the libros"],
    )


def test_continuation_monolingual_dodge_scores_zero() -> None:
    """The largest hedging hole in the design: without this a model answers every
    continuation item in one language and never risks a violation.
    """
    result = score(_continuation_item(), "yesterday I bought some books")

    assert result.points == 0


def test_continuation_licensed_form_scores_full() -> None:
    assert score(_continuation_item(), "los libros").points == 2


def test_continuation_violating_form_scores_zero() -> None:
    assert score(_continuation_item(), "the libros").points == 0


def _repair_item() -> Any:
    return _item(
        TaskType.REPAIR,
        violating="Compré the libros ayer.",
        gold_repair="Compré los libros ayer.",
        violation_span=(1, 2),
    )


def test_repair_requires_an_explicit_threshold() -> None:
    """No run may silently use an uncalibrated minimality threshold."""
    with pytest.raises(ValueError, match="explicit minimality_threshold"):
        score(_repair_item(), "Compré los libros ayer.")


def test_repair_minimal_edit_scores_full() -> None:
    result = score(_repair_item(), "Compré los libros ayer.", minimality_threshold=0.5)

    assert result.points == 2


def test_repair_failing_to_reach_gold_scores_zero() -> None:
    result = score(_repair_item(), "Compré unos libros ayer.", minimality_threshold=0.5)

    assert result.points == 0


def test_repair_matching_an_alternate_scores_full() -> None:
    """Some violations admit more than one equally minimal fix; the scorer must accept
    any of them, not just whichever one was recorded as `gold_repair`.
    """
    item = _item(
        TaskType.REPAIR,
        violating="Compró a el gift ayer.",
        gold_repair="Compró a gift ayer.",
        alternate_repairs=["Compró el gift ayer."],
        violation_span=(2, 3),
    )

    result = score(item, "Compró el gift ayer.", minimality_threshold=0.5)

    assert result.points == 2


def test_repair_hedging_scores_zero() -> None:
    result = score(_repair_item(), "It depends what you meant.", minimality_threshold=0.5)

    assert result.points == 0


def test_score_normalizes_against_its_own_maximum() -> None:
    result = score(_ml_item(), "Spanish, because most of the words are Spanish.")

    assert result.normalized == pytest.approx(1 / 3)
