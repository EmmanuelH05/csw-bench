from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from pydantic import TypeAdapter

from csw_bench.providers import CompletionRequest, ModelResponse
from csw_bench.schema import Item
from csw_bench.taxonomy import TaskType, ViolationType

_ADAPTER: TypeAdapter[Item] = TypeAdapter(Item)


def parse(payload: dict[str, Any]) -> Item:
    return _ADAPTER.validate_python(payload)


def _base(item_id: str, violation: ViolationType) -> dict[str, Any]:
    return {
        "id": item_id,
        "matrix_language": "es",
        "primary_violation": violation.value,
        "difficulty": "medium",
        "justification": "Constructed fixture.",
        "provenance": {
            "source": "constructed",
            "license": "MIT",
            "derivation": "System Morpheme Principle",
        },
    }


def judgment_item(item_id: str, violation: ViolationType, **overrides: Any) -> dict[str, Any]:
    item = _base(item_id, violation) | {
        "task_type": TaskType.GRAMMATICALITY_JUDGMENT.value,
        "licensed": "Compré los libros ayer.",
        "violating": "Compré the libros ayer.",
    }
    item.update(overrides)
    return item


def continuation_item(item_id: str, violation: ViolationType, **overrides: Any) -> dict[str, Any]:
    item = _base(item_id, violation) | {
        "task_type": TaskType.CONSTRAINED_CONTINUATION.value,
        "prompt": "Ayer compré",
        "licensed_continuations": ["los libros for my class"],
        "violating_continuations": ["the libros para mi clase"],
    }
    item.update(overrides)
    return item


def identification_item(item_id: str, violation: ViolationType, **overrides: Any) -> dict[str, Any]:
    item = _base(item_id, violation) | {
        "task_type": TaskType.ML_IDENTIFICATION.value,
        "utterance": "Compré the books ayer en la tienda.",
        "required_evidence": ["verb inflection", "determiner agreement"],
    }
    item.update(overrides)
    return item


def repair_item(item_id: str, violation: ViolationType, **overrides: Any) -> dict[str, Any]:
    item = _base(item_id, violation) | {
        "task_type": TaskType.REPAIR.value,
        "violating": "Compré the libros ayer.",
        "gold_repair": "Compré los libros ayer.",
        "violation_span": [1, 2],
    }
    item.update(overrides)
    return item


class FakeProvider:
    """Deterministic in-memory provider. The reply is a function of the prompt so a test
    can steer scores, and `calls` makes 'a rerun from cache makes no provider calls'
    directly assertable.
    """

    def __init__(self, reply: Callable[[str], str]) -> None:
        self.calls = 0
        self._reply = reply

    def complete(self, request: CompletionRequest) -> ModelResponse:
        self.calls += 1
        text = self._reply(request.prompt)
        return ModelResponse(
            text=text,
            input_tokens=len(request.prompt.split()),
            output_tokens=len(text.split()),
            seed_applied=True,
        )


@pytest.fixture
def write_item(tmp_path: Path):
    def _write(payload: dict[str, Any], name: str | None = None) -> Path:
        path = tmp_path / f"{name or payload['id']}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    return _write
