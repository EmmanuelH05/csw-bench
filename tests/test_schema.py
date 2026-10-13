from __future__ import annotations

import pytest
from pydantic import ValidationError

from csw_bench.taxonomy import (
    RESOLUTION_ORDER,
    VIOLATION_SPECS,
    SystemMorphemeClass,
    TaskType,
    ViolationType,
)
from tests.conftest import continuation_item, judgment_item, parse, repair_item


def test_every_violation_type_has_a_spec() -> None:
    assert set(VIOLATION_SPECS) == set(ViolationType)


def test_resolution_order_covers_every_type_exactly_once() -> None:
    assert sorted(RESOLUTION_ORDER, key=str) == sorted(ViolationType, key=str)


def test_t4_identifier_is_retired_not_reused() -> None:
    """T4 was cut in Phase 1. `matriz` records these strings against a hashed item set,
    so reusing the identifier would silently change the meaning of a published label.
    """
    assert "T4" not in {v.value for v in ViolationType}
    assert ViolationType.CONGRUENCE_FAILURE.value == "T5"


def test_t2_identifier_is_retired_not_reused() -> None:
    """T2 was dropped later in Phase 1 (populability, resolved by three converging
    lines of evidence) for the same reason T4 was: a type `matriz` cannot meaningfully
    hold out is not a type. See `docs/taxonomy.md` and `docs/journal.md`.

    Also pins T3 and T5's identifiers, since T2's now-vacant slot is exactly the kind of
    gap a well-meaning future edit might "close" by renumbering — which would silently
    change the meaning of an already-published label.
    """
    assert "T2" not in {v.value for v in ViolationType}
    assert ViolationType.ILL_FORMED_EL_ISLAND.value == "T3"
    assert ViolationType.CONGRUENCE_FAILURE.value == "T5"


def test_attested_item_requires_citation_and_corpus_ref() -> None:
    with pytest.raises(ValidationError, match="citation_key and corpus_ref"):
        parse(
            judgment_item(
                "csw-es-en-0001",
                ViolationType.EL_SYSTEM_MORPHEME,
                provenance={"source": "attested", "license": "CC-BY-NC-SA-3.0"},
            )
        )


def test_constructed_item_requires_a_derivation() -> None:
    with pytest.raises(ValidationError, match="derivation"):
        parse(
            judgment_item(
                "csw-es-en-0001",
                ViolationType.EL_SYSTEM_MORPHEME,
                provenance={"source": "constructed", "license": "MIT"},
            )
        )


def test_primary_violation_cannot_repeat_in_secondary() -> None:
    with pytest.raises(ValidationError, match="must not also appear"):
        parse(
            judgment_item(
                "csw-es-en-0001",
                ViolationType.EL_SYSTEM_MORPHEME,
                secondary_violations=[ViolationType.EL_SYSTEM_MORPHEME.value],
            )
        )


def test_minimal_pair_members_must_differ() -> None:
    with pytest.raises(ValidationError, match="must differ"):
        parse(
            judgment_item(
                "csw-es-en-0001",
                ViolationType.EL_SYSTEM_MORPHEME,
                licensed="Compré los libros.",
                violating="Compré los libros.",
            )
        )


def test_minimal_pair_members_differing_only_in_diacritics_are_rejected() -> None:
    """The scorer compares normalized forms; such a pair would validate and then be
    permanently unscoreable.
    """
    with pytest.raises(ValidationError, match="casing and diacritics"):
        parse(
            judgment_item(
                "csw-es-en-0001",
                ViolationType.EL_SYSTEM_MORPHEME,
                licensed="Compré los libros.",
                violating="compre los libros",
            )
        )


def test_continuation_rejects_violating_string_inside_a_licensed_one() -> None:
    with pytest.raises(ValidationError, match="occurs inside"):
        parse(
            continuation_item(
                "csw-es-en-0001",
                ViolationType.EL_SYSTEM_MORPHEME,
                licensed_continuations=["los libros for my class"],
                violating_continuations=["libros for my class"],
            )
        )


def test_repair_rejects_a_gold_repair_identical_to_the_violation() -> None:
    with pytest.raises(ValidationError, match="must differ from the violating"):
        parse(
            repair_item(
                "csw-es-en-0001",
                ViolationType.EL_SYSTEM_MORPHEME,
                gold_repair="Compré the libros ayer!",
            )
        )


def test_repair_accepts_a_distinct_alternate() -> None:
    item = parse(
        repair_item(
            "csw-es-en-0001",
            ViolationType.EL_SYSTEM_MORPHEME,
            alternate_repairs=["Compré unos libros ayer."],
        )
    )

    assert list(item.alternate_repairs) == ["Compré unos libros ayer."]


def test_repair_rejects_an_alternate_identical_to_the_violation() -> None:
    with pytest.raises(ValidationError, match="differ from the violating"):
        parse(
            repair_item(
                "csw-es-en-0001",
                ViolationType.EL_SYSTEM_MORPHEME,
                alternate_repairs=["Compré the libros ayer."],
            )
        )


def test_repair_rejects_an_alternate_duplicating_gold() -> None:
    with pytest.raises(ValidationError, match="distinct from each other and gold"):
        parse(
            repair_item(
                "csw-es-en-0001",
                ViolationType.EL_SYSTEM_MORPHEME,
                alternate_repairs=["Compré los libros ayer."],
            )
        )


def test_repair_item_rejects_inverted_span() -> None:
    with pytest.raises(ValidationError, match="ordered range"):
        parse(
            {
                "id": "csw-es-en-0001",
                "task_type": TaskType.REPAIR.value,
                "matrix_language": "es",
                "primary_violation": ViolationType.EL_SYSTEM_MORPHEME.value,
                "difficulty": "easy",
                "justification": "Constructed fixture.",
                "violating": "Compré the libros ayer.",
                "gold_repair": "Compré los libros ayer.",
                "violation_span": [3, 1],
                "provenance": {
                    "source": "constructed",
                    "license": "MIT",
                    "derivation": "System Morpheme Principle",
                },
            }
        )


def test_system_morpheme_class_is_rejected_on_non_t1_items() -> None:
    """T1 was widened to admit all three 4-M classes; the class is metadata on T1 only.
    Attaching it elsewhere would imply a distinction the taxonomy does not make.
    """
    with pytest.raises(ValidationError, match="only to T1"):
        parse(
            judgment_item(
                "csw-es-en-0001",
                ViolationType.CONGRUENCE_FAILURE,
                system_morpheme_class=SystemMorphemeClass.EARLY.value,
            )
        )


def test_t1_item_accepts_every_4m_class() -> None:
    for morpheme_class in SystemMorphemeClass:
        item = parse(
            judgment_item(
                "csw-es-en-0001",
                ViolationType.EL_SYSTEM_MORPHEME,
                system_morpheme_class=morpheme_class.value,
            )
        )

        assert item.system_morpheme_class is morpheme_class


def test_contested_segmentation_defaults_off_and_is_recordable() -> None:
    plain = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    flagged = parse(
        judgment_item(
            "csw-es-en-0002", ViolationType.EL_SYSTEM_MORPHEME, contested_segmentation=True
        )
    )

    assert not plain.contested_segmentation
    assert flagged.contested_segmentation


def test_items_are_frozen() -> None:
    item = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))

    with pytest.raises(ValidationError):
        item.difficulty = "hard"  # type: ignore[misc]


def test_disagreement_is_recordable_without_invalidating_the_item() -> None:
    """The project logs inter-rater disagreement rather than resolving it, so an item
    carrying a recorded losing argument must still validate.
    """
    item = parse(
        judgment_item(
            "csw-es-en-0001",
            ViolationType.EL_SYSTEM_MORPHEME,
            provenance={
                "source": "constructed",
                "license": "MIT",
                "derivation": "System Morpheme Principle",
                "reviewed_by": ["a", "b"],
                "review_disagreement": "Reviewer B read this as T5.",
            },
        )
    )

    assert item.provenance.review_disagreement
