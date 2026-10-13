from __future__ import annotations

from enum import StrEnum
from typing import NamedTuple


class ViolationType(StrEnum):
    """Identifiers are stable and gap-tolerant.

    T2 (ML constituent order violated) and T4 (EL late outsider system morpheme) were
    both cut in Phase 1 and their identifiers are retired, not reused. `matriz` records
    these strings against a hashed item set, so renumbering T5 to T2 or T4 would silently
    change the meaning of an already-published label.
    """

    EL_SYSTEM_MORPHEME = "T1"
    ILL_FORMED_EL_ISLAND = "T3"
    CONGRUENCE_FAILURE = "T5"


class SystemMorphemeClass(StrEnum):
    """4-M classes, recorded per item rather than indexed as separate violation types.

    T1 admits all three. Keeping the class as metadata preserves the early/outsider
    gradation for analysis while avoiding a type too sparse for `matriz` to hold out.
    """

    EARLY = "early"
    LATE_BRIDGE = "late_bridge"
    LATE_OUTSIDER = "late_outsider"


class TaskType(StrEnum):
    GRAMMATICALITY_JUDGMENT = "grammaticality_judgment"
    CONSTRAINED_CONTINUATION = "constrained_continuation"
    ML_IDENTIFICATION = "ml_identification"
    REPAIR = "repair"


class Language(StrEnum):
    SPANISH = "es"
    ENGLISH = "en"


class ViolationSpec(NamedTuple):
    prediction: str
    citation_key: str
    diagnostic: str


VIOLATION_SPECS: dict[ViolationType, ViolationSpec] = {
    ViolationType.EL_SYSTEM_MORPHEME: ViolationSpec(
        prediction="System Morpheme Principle",
        citation_key="myersscotton1993duelling",
        diagnostic="An EL-sourced system morpheme of any 4-M class is present in an "
        "ML-framed constituent and attaches to ML material.",
    ),
    ViolationType.ILL_FORMED_EL_ISLAND: ViolationSpec(
        prediction="EL Island Trigger Hypothesis",
        citation_key="myersscotton1993duelling",
        diagnostic="ML material intrudes into EL-framed material, or an island boundary "
        "cuts a constituent EL grammar requires be complete.",
    ),
    ViolationType.CONGRUENCE_FAILURE: ViolationSpec(
        prediction="Blocking Hypothesis",
        citation_key="myersscotton1993duelling",
        diagnostic="An EL content morpheme outside any EL island surfaces without "
        "morphology the ML obligatorily supplies.",
    ),
}

RESOLUTION_ORDER: tuple[ViolationType, ...] = (
    ViolationType.ILL_FORMED_EL_ISLAND,
    ViolationType.EL_SYSTEM_MORPHEME,
    ViolationType.CONGRUENCE_FAILURE,
)
