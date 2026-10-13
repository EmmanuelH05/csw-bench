from __future__ import annotations

import json
from pathlib import Path

import pytest

from csw_bench.accounting import PricePerMTok
from csw_bench.cache import ResponseCache
from csw_bench.loader import ItemSet
from csw_bench.providers import REQUEST_TIMEOUT_SECONDS, ProviderError
from csw_bench.results import load_run
from csw_bench.runner import RetentionError, RunConfig, RunRecord, run, run_id
from csw_bench.taxonomy import ViolationType
from tests.conftest import (
    FakeProvider,
    continuation_item,
    identification_item,
    judgment_item,
    parse,
    repair_item,
)

_CONFIG = RunConfig(
    provider_family="fake",
    model="fake-1",
    template_id="a",
    seed=7,
    minimality_threshold=0.6,
    zero_retention=True,
)


def _reply(prompt: str) -> str:
    if "Matrix Language" in prompt:
        return "Spanish sets the frame: verb inflection and determiner agreement are Spanish."
    if "Complete this" in prompt:
        return "Ayer compré los libros for my class."
    return "Compré los libros ayer."


def _item_set() -> ItemSet:
    return ItemSet(
        parse(builder(f"csw-es-en-{n:04d}", ViolationType.EL_SYSTEM_MORPHEME))
        for n, builder in enumerate(
            (judgment_item, continuation_item, identification_item, repair_item), start=1
        )
    )


def test_run_scores_every_item_and_persists_artifacts(tmp_path: Path) -> None:
    result = run(
        _item_set(), FakeProvider(_reply), _CONFIG, ResponseCache(tmp_path / "cache"), tmp_path
    )

    assert len(result.records) == 4
    assert all(r.points == r.max_points for r in result.records), [
        (r.item_id, r.reason) for r in result.records
    ]
    assert (tmp_path / "run.json").is_file()
    assert (tmp_path / "records.jsonl").is_file()


def test_rerun_from_cache_reproduces_identical_scores_without_billing(tmp_path: Path) -> None:
    """Phase 3 completion condition: a rerun must reproduce the exact result with zero
    provider calls.
    """
    cache = ResponseCache(tmp_path / "cache")
    first = run(_item_set(), FakeProvider(_reply), _CONFIG, cache, tmp_path / "run1")

    second_provider = FakeProvider(_reply)
    second = run(_item_set(), second_provider, _CONFIG, cache, tmp_path / "run2")

    def scores(records: tuple[RunRecord, ...]) -> list[tuple[str, str, int, int, str]]:
        return [(r.item_id, r.response_text, r.points, r.max_points, r.reason) for r in records]

    assert second_provider.calls == 0
    assert scores(second.records) == scores(first.records)
    assert all(r.cached for r in second.records)
    assert second.accounting.cache_hits == 4
    assert second.accounting.provider_calls == 0
    assert second.accounting.billed_input_tokens == 0
    assert second.accounting.billed_output_tokens == 0


def test_template_change_misses_the_cache(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path / "cache")
    run(_item_set(), FakeProvider(_reply), _CONFIG, cache, tmp_path / "run1")

    other_template = FakeProvider(_reply)
    run(
        _item_set(),
        other_template,
        _CONFIG.model_copy(update={"template_id": "b"}),
        cache,
        tmp_path / "run2",
    )

    assert other_template.calls == 4


def test_attested_items_refuse_to_run_without_zero_retention(tmp_path: Path) -> None:
    """TalkBank's terms forbid sending corpus material to providers that retain it. A
    default-configured API key must fail before the first request, not after.
    """
    attested = parse(
        judgment_item(
            "csw-es-en-0001",
            ViolationType.EL_SYSTEM_MORPHEME,
            provenance={
                "source": "attested",
                "license": "CC-BY-NC-SA-3.0",
                "citation_key": "fixture2024",
                "corpus_ref": "fixture.cha:1",
            },
        )
    )
    provider = FakeProvider(_reply)

    with pytest.raises(RetentionError, match="zero retention"):
        run(
            ItemSet([attested]),
            provider,
            _CONFIG.model_copy(update={"zero_retention": False}),
            ResponseCache(tmp_path / "cache"),
            tmp_path,
        )
    assert provider.calls == 0


def test_constructed_items_may_run_without_zero_retention(tmp_path: Path) -> None:
    result = run(
        _item_set(),
        FakeProvider(_reply),
        _CONFIG.model_copy(update={"zero_retention": False}),
        ResponseCache(tmp_path / "cache"),
        tmp_path,
    )

    assert len(result.records) == 4


def test_cost_is_computed_only_from_billed_tokens(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path / "cache")
    prices = PricePerMTok(input=3.0, output=15.0)
    first = run(_item_set(), FakeProvider(_reply), _CONFIG, cache, tmp_path / "run1", prices=prices)

    accounting = first.accounting
    expected = (
        accounting.billed_input_tokens * 3.0 + accounting.billed_output_tokens * 15.0
    ) / 1_000_000
    assert accounting.cost_usd == pytest.approx(expected)

    rerun = run(_item_set(), FakeProvider(_reply), _CONFIG, cache, tmp_path / "run2", prices=prices)
    assert rerun.accounting.cost_usd == 0.0


def test_cost_is_absent_without_supplied_prices(tmp_path: Path) -> None:
    result = run(
        _item_set(), FakeProvider(_reply), _CONFIG, ResponseCache(tmp_path / "cache"), tmp_path
    )

    assert result.accounting.cost_usd is None


def test_run_artifacts_round_trip_through_load_run(tmp_path: Path) -> None:
    """Multiline prompts and responses must survive the JSONL encoding, and the loaded
    result must equal the in-memory one exactly -- hash, accounting, and all.
    """
    multiline = FakeProvider(lambda prompt: "line one\nCompré los libros ayer.\nline three")
    result = run(
        _item_set(), multiline, _CONFIG, ResponseCache(tmp_path / "cache"), tmp_path / "run"
    )

    assert load_run(tmp_path / "run") == result


def test_a_provider_error_on_one_item_does_not_abort_the_run(tmp_path: Path) -> None:
    """One pathological item (e.g. a reasoning model exhausting its token budget on a
    single prompt) must not lose the other three items' scores -- discovered running the
    real Phase 3 pilot against gpt-oss:20b, which did exactly this.
    """

    def flaky_reply(prompt: str) -> str:
        if "Matrix Language" in prompt:
            raise ProviderError("ollama exhausted its output budget")
        return _reply(prompt)

    result = run(
        _item_set(), FakeProvider(flaky_reply), _CONFIG, ResponseCache(tmp_path / "cache"), tmp_path
    )

    assert len(result.records) == 4
    errored = [r for r in result.records if r.errored]
    ok = [r for r in result.records if not r.errored]
    assert len(errored) == 1
    assert errored[0].task_type.value == "ml_identification"
    assert errored[0].points == 0
    assert errored[0].response_text == ""
    assert "provider error" in errored[0].reason
    assert len(ok) == 3
    assert all(r.points == r.max_points for r in ok)
    assert result.accounting.provider_errors == 1
    assert result.accounting.provider_calls == 4


def test_an_errored_item_is_not_cached_so_a_rerun_retries_the_provider(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path / "cache")
    calls = {"n": 0}

    def flaky_once(prompt: str) -> str:
        if "Matrix Language" in prompt and calls["n"] == 0:
            calls["n"] += 1
            raise ProviderError("transient failure")
        return _reply(prompt)

    first = run(_item_set(), FakeProvider(flaky_once), _CONFIG, cache, tmp_path / "run1")
    assert any(r.errored for r in first.records)

    second = run(_item_set(), FakeProvider(_reply), _CONFIG, cache, tmp_path / "run2")
    assert not any(r.errored for r in second.records)
    assert all(r.points == r.max_points for r in second.records)


def test_unknown_template_id_is_rejected_at_config_time() -> None:
    with pytest.raises(ValueError, match="unknown template id"):
        RunConfig(
            provider_family="fake",
            model="fake-1",
            template_id="z",
            seed=7,
            minimality_threshold=0.6,
            zero_retention=True,
        )


def test_a_run_written_before_the_timeout_field_loads_with_the_value_it_used(
    tmp_path: Path,
) -> None:
    """Every committed run under runs/ predates `request_timeout_seconds` and ran at the
    300 s constant, so the default must be that constant and an old run.json must load.
    """
    result = run(
        _item_set(), FakeProvider(_reply), _CONFIG, ResponseCache(tmp_path / "cache"), tmp_path
    )
    header = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
    del header["config"]["request_timeout_seconds"]
    (tmp_path / "run.json").write_text(json.dumps(header), encoding="utf-8")

    loaded = load_run(tmp_path)
    assert loaded.config.request_timeout_seconds == REQUEST_TIMEOUT_SECONDS == 300.0
    assert loaded == result


def test_run_id_is_deterministic_and_config_sensitive() -> None:
    item_set_hash = _item_set().hash()

    assert run_id(item_set_hash, _CONFIG) == run_id(item_set_hash, _CONFIG)
    assert run_id(item_set_hash, _CONFIG) != run_id(
        item_set_hash, _CONFIG.model_copy(update={"seed": 8})
    )


def test_on_record_reports_each_persisted_record_with_a_running_index(tmp_path: Path) -> None:
    seen: list[tuple[str, int, int]] = []

    run(
        _item_set(),
        FakeProvider(_reply),
        _CONFIG,
        ResponseCache(tmp_path / "cache"),
        tmp_path,
        on_record=lambda record, index, total: seen.append((record.item_id, index, total)),
    )

    assert seen == [(f"csw-es-en-{n:04d}", n, 4) for n in range(1, 5)]
