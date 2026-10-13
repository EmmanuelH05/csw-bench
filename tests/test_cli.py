from __future__ import annotations

import json
from pathlib import Path

import pytest

from csw_bench import __version__
from csw_bench.cli import main, stats, validate
from csw_bench.providers import REQUEST_TIMEOUT_SECONDS
from csw_bench.taxonomy import ViolationType
from tests.conftest import FakeProvider, judgment_item


def test_version_is_exposed() -> None:
    assert __version__ == "1.0.0"


def test_validate_fails_when_item_dir_is_missing(tmp_path: Path) -> None:
    assert validate(tmp_path / "nope") == 1


def test_validate_succeeds_on_empty_item_set(tmp_path: Path) -> None:
    assert validate(tmp_path) == 0


def test_validate_accepts_a_wellformed_item(write_item, tmp_path: Path) -> None:
    write_item(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))

    assert validate(tmp_path) == 0


def test_validate_rejects_a_malformed_item(tmp_path: Path) -> None:
    (tmp_path / "bad.json").write_text(json.dumps({"id": "csw-es-en-0001"}), encoding="utf-8")

    assert validate(tmp_path) == 1


def test_validate_reports_every_failure_not_just_the_first(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    for name in ("a", "b"):
        (tmp_path / f"{name}.json").write_text("{not json", encoding="utf-8")

    assert validate(tmp_path) == 1
    assert capsys.readouterr().err.count("FAIL") == 2


def test_stats_prints_hash_and_counts(
    write_item, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write_item(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))

    assert stats(tmp_path) == 0
    out = capsys.readouterr().out
    assert "1 items" in out
    assert "hash " in out


def test_taxonomy_command_lists_three_types(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["taxonomy"]) == 0
    out = capsys.readouterr().out

    assert out.count("\n") == 3
    assert "T2" not in out
    assert "T4" not in out


def test_version_flag_exits_zero() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])

    assert exc.value.code == 0


def test_bare_invocation_prints_help_and_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0

    assert "csw-bench" in capsys.readouterr().out


def _run_args(tmp_path: Path, *extra: str) -> list[str]:
    return [
        "--items-root",
        str(tmp_path),
        "run",
        "--provider",
        "ollama",
        "--model",
        "fake-1",
        "--template",
        "a",
        "--seed",
        "7",
        "--minimality-threshold",
        "0.6",
        "--retention",
        "zero",
        "--cache-dir",
        str(tmp_path / "artifacts" / "cache"),
        "--out",
        str(tmp_path / "artifacts" / "run"),
        *extra,
    ]


def test_run_and_report_end_to_end(
    write_item,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    write_item(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    monkeypatch.setattr(
        "csw_bench.cli.create_provider",
        lambda family, timeout_seconds: FakeProvider(lambda prompt: "Compré los libros ayer."),
    )

    assert main(_run_args(tmp_path)) == 0
    captured = capsys.readouterr()
    assert "1 items" in captured.out
    assert "provider calls 1" in captured.out
    assert "[1/1] csw-es-en-0001 grammaticality_judgment 1/1" in captured.err

    assert main(["report", str(tmp_path / "artifacts" / "run"), "--resamples", "100"]) == 0
    assert "grammaticality_judgment" in capsys.readouterr().out


def test_run_timeout_reaches_the_provider_and_is_recorded_with_the_run(
    write_item, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The deepseek-r1:32b full run lost 100 ml_identification items to the 300 s
    default; the rerun that recovers them differs only in this setting, so it has to be
    both honoured by the provider and auditable from run.json.
    """
    write_item(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    seen: list[float] = []

    def fake_create(family: str, *, timeout_seconds: float) -> FakeProvider:
        seen.append(timeout_seconds)
        return FakeProvider(lambda prompt: "Compré los libros ayer.")

    monkeypatch.setattr("csw_bench.cli.create_provider", fake_create)

    assert main(_run_args(tmp_path, "--timeout", "1800")) == 0
    assert seen == [1800.0]
    header = json.loads((tmp_path / "artifacts" / "run" / "run.json").read_text())
    assert header["config"]["request_timeout_seconds"] == 1800.0


def test_run_timeout_defaults_to_the_provider_constant(
    write_item, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_item(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME))
    seen: list[float] = []

    def fake_create(family: str, *, timeout_seconds: float) -> FakeProvider:
        seen.append(timeout_seconds)
        return FakeProvider(lambda prompt: "Compré los libros ayer.")

    monkeypatch.setattr("csw_bench.cli.create_provider", fake_create)

    assert main(_run_args(tmp_path)) == 0
    assert seen == [REQUEST_TIMEOUT_SECONDS]


def test_run_requires_both_prices_or_neither(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        main(_run_args(tmp_path, "--price-input", "3.0"))

    assert exc.value.code == 2


def test_run_refuses_attested_items_without_zero_retention(
    write_item,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    write_item(
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
    provider = FakeProvider(lambda prompt: "Compré los libros ayer.")
    monkeypatch.setattr("csw_bench.cli.create_provider", lambda family, timeout_seconds: provider)
    args = _run_args(tmp_path)
    args[args.index("zero")] = "default"

    assert main(args) == 1
    assert "FAIL" in capsys.readouterr().err
    assert provider.calls == 0


def test_report_fails_cleanly_on_a_missing_run_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["report", str(tmp_path / "nope")]) == 1

    assert "FAIL" in capsys.readouterr().err


def _run_into(items_root: Path, out: Path, reply: str, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(
        "csw_bench.cli.create_provider",
        lambda family, timeout_seconds: FakeProvider(lambda prompt: reply),
    )
    args = _run_args(items_root)
    args[args.index("--out") + 1] = str(out)
    args[args.index("--cache-dir") + 1] = str(out / "cache")
    assert main(args) == 0
    return out


def test_table_renders_one_markdown_column_per_run(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two runs of the same model id fall back to directory names as column heads."""
    items = tmp_path / "items"
    items.mkdir()
    (items / "item.json").write_text(
        json.dumps(judgment_item("csw-es-en-0001", ViolationType.EL_SYSTEM_MORPHEME)),
        encoding="utf-8",
    )
    right = _run_into(items, tmp_path / "right", "Compré los libros ayer.", monkeypatch)
    wrong = _run_into(items, tmp_path / "wrong", "Compré the libros ayer.", monkeypatch)
    capsys.readouterr()

    assert main(["table", str(right), str(wrong), "--resamples", "50"]) == 0
    out = capsys.readouterr().out

    assert "| task | violation | right | wrong |" in out
    assert "| grammaticality_judgment | all |" in out
    assert "| grammaticality_judgment | T1 |" in out
    assert "1.00 · +1.00 [+1.00, +1.00] · n=1" in out
    assert "0.00 · -1.00 [-1.00, -1.00] · n=1" in out


def test_table_refuses_runs_over_different_item_sets(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    outs = []
    for n in (1, 2):
        root = tmp_path / f"set{n}"
        root.mkdir()
        (root / "item.json").write_text(
            json.dumps(judgment_item(f"csw-es-en-{n:04d}", ViolationType.EL_SYSTEM_MORPHEME)),
            encoding="utf-8",
        )
        outs.append(_run_into(root, root / "run", "Compré los libros ayer.", monkeypatch))
    capsys.readouterr()

    assert main(["table", str(outs[0]), str(outs[1]), "--resamples", "50"]) == 1
    assert "different item sets" in capsys.readouterr().err


def test_table_fails_cleanly_on_a_missing_run_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["table", str(tmp_path / "nope")]) == 1

    assert "FAIL" in capsys.readouterr().err
