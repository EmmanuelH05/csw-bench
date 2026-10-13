from __future__ import annotations

from pathlib import Path

import pytest

from csw_bench.loader import ItemLoadError, ItemSet, load_item, load_items
from csw_bench.taxonomy import ViolationType
from tests.conftest import judgment_item, parse


def test_loads_a_valid_item(write_item) -> None:
    path = write_item(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))

    assert load_item(path).id == "csw-es-en-0001"


def test_rejects_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(ItemLoadError, match="invalid JSON"):
        load_item(path)


def test_rejects_unknown_field(write_item) -> None:
    path = write_item(
        judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME, unexpected="x")
    )

    with pytest.raises(ItemLoadError, match="schema violation"):
        load_item(path)


def test_rejects_malformed_item_id(write_item) -> None:
    path = write_item(judgment_item("item-1", ViolationType.EL_SYSTEM_MORPHEME), name="bad-id")

    with pytest.raises(ItemLoadError, match="schema violation"):
        load_item(path)


def test_rejects_duplicate_ids(write_item, tmp_path: Path) -> None:
    write_item(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME), name="a")
    write_item(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME), name="b")

    with pytest.raises(ValueError, match="duplicate item ids"):
        load_items(tmp_path)


def test_filter_by_violation_type_returns_disjoint_sets() -> None:
    """Phase 3 completion condition. Every item has exactly one primary violation, so
    filtering distinct types must never return an overlapping item.
    """
    items = [
        parse(judgment_item(f"csw-es-en-{n:04d}", violation))
        for n, violation in enumerate(
            [
                ViolationType.EL_SYSTEM_MORPHEME,
                ViolationType.ILL_FORMED_EL_ISLAND,
                ViolationType.CONGRUENCE_FAILURE,
                ViolationType.EL_SYSTEM_MORPHEME,
            ],
            start=1,
        )
    ]
    item_set = ItemSet(items)

    seen: set[str] = set()
    total = 0
    for violation in ViolationType:
        selected = item_set.filter_by_violation_type(violation)
        ids = {i.id for i in selected}
        assert not (ids & seen), f"{violation} overlaps a previous type"
        seen |= ids
        total += len(selected)

    assert total == len(item_set)
    assert seen == {i.id for i in item_set}


def test_filter_accepts_multiple_types_without_duplicating() -> None:
    items = [
        parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME)),
        parse(judgment_item("csw-es-en-0002", ViolationType.EL_SYSTEM_MORPHEME)),
    ]
    item_set = ItemSet(items)

    both = item_set.filter_by_violation_type(
        ViolationType.EL_SYSTEM_MORPHEME, ViolationType.EL_SYSTEM_MORPHEME
    )

    assert len(both) == 2


def test_filter_with_no_arguments_returns_empty() -> None:
    item_set = ItemSet([parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))])

    assert item_set.filter_by_violation_type() == ()


def test_hash_is_order_independent() -> None:
    a = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    b = parse(judgment_item("csw-es-en-0002", ViolationType.CONGRUENCE_FAILURE))

    assert ItemSet([a, b]).hash() == ItemSet([b, a]).hash()


def test_hash_changes_when_content_changes() -> None:
    a = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    b = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME, difficulty="hard"))

    assert ItemSet([a]).hash() != ItemSet([b]).hash()


def test_filter_by_license_selects_compatible_subsets() -> None:
    """SA requires share-alike and ND forbids adaptation, so a consumer must be able to
    select a license-compatible subset instead of pooling everything.
    """
    mit = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    sa = parse(
        judgment_item(
            "csw-es-en-0002",
            ViolationType.EL_SYSTEM_MORPHEME,
            provenance={
                "source": "attested",
                "license": "CC-BY-NC-SA-3.0",
                "citation_key": "fixture2024",
                "corpus_ref": "fixture.cha:1",
            },
        )
    )
    item_set = ItemSet([mit, sa])

    assert [i.id for i in item_set.filter_by_license("CC-BY-NC-SA-3.0")] == ["csw-es-en-0002"]
    assert item_set.filter_by_license("CC-BY-NC-ND-4.0") == ()
    assert item_set.counts_by_license() == {"MIT": 1, "CC-BY-NC-SA-3.0": 1}


def test_exclude_synthetic_drops_synthetic_items() -> None:
    real = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    fake = parse(
        judgment_item(
            "csw-es-en-0002",
            ViolationType.EL_SYSTEM_MORPHEME,
            provenance={
                "source": "synthetic",
                "license": "MIT",
                "derivation": "System Morpheme Principle",
            },
        )
    )

    assert len(ItemSet([real, fake]).exclude_synthetic()) == 1
