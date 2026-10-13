from __future__ import annotations

import pytest

from csw_bench.prompts import TEMPLATE_IDS, judgment_member_order, render
from csw_bench.schema import GrammaticalityJudgmentItem
from csw_bench.taxonomy import ViolationType
from tests.conftest import (
    continuation_item,
    identification_item,
    judgment_item,
    parse,
    repair_item,
)

_BUILDERS = (judgment_item, continuation_item, identification_item, repair_item)


@pytest.mark.parametrize("builder", _BUILDERS)
@pytest.mark.parametrize("template_id", TEMPLATE_IDS)
def test_every_task_type_renders_under_every_template(builder, template_id: str) -> None:
    item = parse(builder("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))

    assert render(item, template_id)


@pytest.mark.parametrize("builder", _BUILDERS)
def test_templates_are_actual_paraphrases_not_copies(builder) -> None:
    item = parse(builder("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))

    assert render(item, "a") != render(item, "b")


def test_unknown_template_id_is_rejected() -> None:
    item = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))

    with pytest.raises(ValueError, match="unknown template id"):
        render(item, "c")


def test_judgment_prompt_presents_both_members() -> None:
    item = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    assert isinstance(item, GrammaticalityJudgmentItem)

    prompt = render(item, "a")

    assert item.licensed in prompt
    assert item.violating in prompt


def test_member_order_is_deterministic() -> None:
    item = parse(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    assert isinstance(item, GrammaticalityJudgmentItem)

    assert judgment_member_order(item) == judgment_member_order(item)


def test_member_order_varies_across_items() -> None:
    """A position-biased model must not beat the 50% floor, so both presentation orders
    have to occur across the id space.
    """
    orders = set()
    for n in range(1, 21):
        item = parse(judgment_item(f"csw-es-en-{n:04d}", ViolationType.EL_SYSTEM_MORPHEME))
        assert isinstance(item, GrammaticalityJudgmentItem)
        orders.add(judgment_member_order(item)[0] == item.licensed)

    assert orders == {True, False}
