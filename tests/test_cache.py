from __future__ import annotations

from pathlib import Path

import pytest

from csw_bench.cache import CacheError, ResponseCache
from csw_bench.providers import CompletionRequest, ModelResponse


def _request(**overrides: object) -> CompletionRequest:
    fields: dict[str, object] = {
        "prompt": "Which sentence is acceptable?",
        "model": "fake-1",
        "seed": 7,
        "temperature": 0.0,
        "max_tokens": 256,
    }
    fields.update(overrides)
    return CompletionRequest.model_validate(fields)


_RESPONSE = ModelResponse(text="ok", input_tokens=5, output_tokens=1, seed_applied=True)


def test_miss_returns_none(tmp_path: Path) -> None:
    assert ResponseCache(tmp_path).get(_request()) is None


def test_roundtrip_returns_the_stored_response(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path)
    cache.put(_request(), _RESPONSE)

    assert cache.get(_request()) == _RESPONSE


def test_key_is_stable_for_equal_requests() -> None:
    assert ResponseCache.key(_request()) == ResponseCache.key(_request())


@pytest.mark.parametrize(
    "overrides",
    [
        {"prompt": "different"},
        {"model": "fake-2"},
        {"seed": 8},
        {"temperature": 0.5},
        {"max_tokens": 512},
    ],
)
def test_any_setting_change_misses(tmp_path: Path, overrides: dict[str, object]) -> None:
    """Rerun-from-cache is only trustworthy if every response-determining input is in
    the key; a hit across changed settings would silently serve a stale answer.
    """
    cache = ResponseCache(tmp_path)
    cache.put(_request(), _RESPONSE)

    assert cache.get(_request(**overrides)) is None


def test_corrupt_entry_fails_loudly(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path)
    cache.put(_request(), _RESPONSE)
    key = ResponseCache.key(_request())
    (tmp_path / key[:2] / f"{key}.json").write_text("{not json", encoding="utf-8")

    with pytest.raises(CacheError, match="corrupt"):
        cache.get(_request())


def test_entries_persist_as_files_on_disk(tmp_path: Path) -> None:
    ResponseCache(tmp_path).put(_request(), _RESPONSE)
    key = ResponseCache.key(_request())

    assert (tmp_path / key[:2] / f"{key}.json").is_file()
