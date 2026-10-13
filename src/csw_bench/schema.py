from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from csw_bench.taxonomy import Language, SystemMorphemeClass, TaskType, ViolationType
from csw_bench.textnorm import normalize, tokenize

ITEM_ID_PATTERN = r"^csw-es-en-\d{4}$"


class Provenance(BaseModel):
    """Attested items cite a corpus; constructed items record a derivation. Enforcing
    that split in the type system is what keeps synthetic material out of headline
    results by accident rather than by vigilance.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: Literal["attested", "constructed", "synthetic"]
    license: str = Field(
        description="SPDX identifier or corpus license. Inherited from the source, not "
        "from the repository."
    )
    citation_key: str | None = Field(
        default=None, description="Key in docs/references.bib. Required for attested items."
    )
    corpus_ref: str | None = Field(
        default=None, description="Corpus file and token span the item derives from."
    )
    derivation: str | None = Field(
        default=None,
        description="The MLF prediction this item was built from. Required for constructed items.",
    )
    reviewed_by: list[str] = Field(default_factory=list)
    review_disagreement: str | None = Field(
        default=None,
        description="The losing argument, recorded rather than discarded. Its presence "
        "means reviewers disagreed; the item is still usable.",
    )

    @model_validator(mode="after")
    def _require_source_specific_fields(self) -> Provenance:
        if self.source == "attested" and not (self.citation_key and self.corpus_ref):
            raise ValueError("attested items require both citation_key and corpus_ref")
        if self.source == "constructed" and not self.derivation:
            raise ValueError("constructed items require a derivation")
        return self


class _BaseItem(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(pattern=ITEM_ID_PATTERN)
    matrix_language: Language
    primary_violation: ViolationType
    secondary_violations: list[ViolationType] = Field(default_factory=list)
    difficulty: Literal["easy", "medium", "hard"]
    justification: str = Field(min_length=1, description="Why the gold answer is correct.")
    system_morpheme_class: SystemMorphemeClass | None = Field(
        default=None,
        description="4-M class of the offending morpheme. Metadata, not a type: T1 was "
        "widened to admit all three classes, and recording which one preserves the "
        "early/outsider gradation for analysis without making it a held-out split.",
    )
    contested_segmentation: bool = Field(
        default=False,
        description="Constituent segmentation is a contested input to the type "
        "assignment. Reported, not resolved.",
    )
    provenance: Provenance

    @model_validator(mode="after")
    def _primary_not_repeated_in_secondary(self) -> _BaseItem:
        if self.primary_violation in self.secondary_violations:
            raise ValueError("primary_violation must not also appear in secondary_violations")
        return self

    @model_validator(mode="after")
    def _morpheme_class_only_on_system_morpheme_violations(self) -> _BaseItem:
        if (
            self.system_morpheme_class is not None
            and self.primary_violation is not ViolationType.EL_SYSTEM_MORPHEME
        ):
            raise ValueError("system_morpheme_class applies only to T1 items")
        return self


class GrammaticalityJudgmentItem(_BaseItem):
    """The item is the minimal pair, not one string.

    `primary_violation` stays single-valued and required because it names what
    distinguishes the two members -- which is the only thing the pair tests.
    """

    task_type: Literal[TaskType.GRAMMATICALITY_JUDGMENT]
    licensed: str = Field(min_length=1)
    violating: str = Field(min_length=1)

    @model_validator(mode="after")
    def _members_must_differ(self) -> GrammaticalityJudgmentItem:
        # The scorer compares normalized forms, so a pair distinguished only by casing,
        # punctuation, or diacritics would be well-formed here and unscoreable there.
        if normalize(self.licensed) == normalize(self.violating):
            raise ValueError("minimal pair members must differ beyond casing and diacritics")
        return self


class ConstrainedContinuationItem(_BaseItem):
    task_type: Literal[TaskType.CONSTRAINED_CONTINUATION]
    prompt: str = Field(min_length=1)
    licensed_continuations: list[str] = Field(min_length=1)
    violating_continuations: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def _violating_never_inside_licensed(self) -> ConstrainedContinuationItem:
        # The scorer checks violating matches first, so a violating string occurring
        # inside a licensed continuation would score the licensed answer zero.
        normalized_licensed = [normalize(c) for c in self.licensed_continuations]
        for violating in self.violating_continuations:
            norm_violating = normalize(violating)
            for licensed, norm in zip(
                self.licensed_continuations, normalized_licensed, strict=True
            ):
                if norm_violating in norm:
                    raise ValueError(
                        f"violating continuation {violating!r} occurs inside licensed "
                        f"continuation {licensed!r}; the item cannot be scored"
                    )
        return self


class MlIdentificationItem(_BaseItem):
    task_type: Literal[TaskType.ML_IDENTIFICATION]
    utterance: str = Field(min_length=1)
    required_evidence: list[str] = Field(
        min_length=1,
        description="Morphosyntactic evidence that earns the evidence points. Lexical "
        "frequency reasoning never appears here.",
    )


class RepairItem(_BaseItem):
    task_type: Literal[TaskType.REPAIR]
    violating: str = Field(min_length=1)
    gold_repair: str = Field(min_length=1)
    alternate_repairs: list[str] = Field(
        default_factory=list,
        description="Other minimal repairs that are equally correct. Some violation "
        "constructions (e.g. a double-article intrusion) admit more than one "
        "single-token fix; recording the alternates here, rather than picking one "
        "arbitrarily as the sole gold answer, keeps the scorer from marking a fluent "
        "speaker's equally valid repair wrong.",
    )
    violation_span: tuple[int, int] = Field(
        description="Token index range of the violation in `violating`, for human/model "
        "reference. Not currently consumed by the scorer, which compares whole "
        "token sequences (see scoring.score_repair) -- wiring span-constrained "
        "scoring in is tracked as open Phase 3 work, same as the minimality "
        "threshold it would need to be calibrated against."
    )

    @model_validator(mode="after")
    def _span_is_ordered(self) -> RepairItem:
        start, end = self.violation_span
        if start < 0 or end <= start:
            raise ValueError("violation_span must be a non-empty ordered range")
        return self

    @model_validator(mode="after")
    def _repair_changes_something(self) -> RepairItem:
        # The scorer compares token sequences, so a repair differing only in punctuation
        # or diacritics is indistinguishable from no repair at all.
        if tokenize(self.gold_repair) == tokenize(self.violating):
            raise ValueError(
                "gold_repair must differ from the violating utterance in token content"
            )
        return self

    @model_validator(mode="after")
    def _alternates_are_real_alternates(self) -> RepairItem:
        violating_tokens = tuple(tokenize(self.violating))
        seen = {tuple(tokenize(self.gold_repair))}
        for alt in self.alternate_repairs:
            alt_tokens = tuple(tokenize(alt))
            if alt_tokens == violating_tokens:
                raise ValueError("alternate_repairs must differ from the violating utterance")
            if alt_tokens in seen:
                raise ValueError("alternate_repairs must be distinct from each other and gold")
            seen.add(alt_tokens)
        return self


Item = Annotated[
    GrammaticalityJudgmentItem | ConstrainedContinuationItem | MlIdentificationItem | RepairItem,
    Field(discriminator="task_type"),
]
