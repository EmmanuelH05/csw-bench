from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from pydantic import ValidationError

from csw_bench import __version__
from csw_bench.accounting import PricePerMTok
from csw_bench.cache import CacheError, ResponseCache
from csw_bench.export import export_hf
from csw_bench.loader import ItemLoadError, load_item, load_items
from csw_bench.prompts import TEMPLATE_IDS
from csw_bench.providers import (
    PROVIDER_FAMILIES,
    REQUEST_TIMEOUT_SECONDS,
    ProviderError,
    create_provider,
)
from csw_bench.results import (
    compare,
    format_comparison,
    format_markdown_table,
    format_report,
    load_run,
    summarize,
)
from csw_bench.runner import RetentionError, RunConfig, RunRecord, RunResult, run, run_id
from csw_bench.taxonomy import ViolationType

ITEMS_ROOT = Path(__file__).resolve().parents[2] / "data" / "items"
RUNS_ROOT = Path("runs")

_LOAD_FAILURES = (OSError, ValidationError, json.JSONDecodeError)


def validate(items_root: Path) -> int:
    if not items_root.is_dir():
        print(f"No item directory at {items_root}")
        return 1

    paths = sorted(items_root.rglob("*.json"))
    if not paths:
        print(f"0 items under {items_root}. Nothing to validate.")
        return 0

    failures: list[str] = []
    for path in paths:
        try:
            load_item(path)
        except ItemLoadError as exc:
            failures.append(str(exc))

    for failure in failures:
        print(f"FAIL {failure}", file=sys.stderr)

    if failures:
        print(f"\n{len(failures)} of {len(paths)} items failed validation.", file=sys.stderr)
        return 1

    print(f"{len(paths)} items validated.")
    return 0


def stats(items_root: Path) -> int:
    try:
        item_set = load_items(items_root)
    except ItemLoadError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1

    if not len(item_set):
        print("0 items.")
        return 0

    print(f"{len(item_set)} items")
    print(f"hash {item_set.hash()}")
    print("\nby primary violation type:")
    for violation, count in item_set.counts_by_violation_type().items():
        print(f"  {violation.value} {violation.name:<24} {count}")

    print("\nby license:")
    for license_id, count in sorted(item_set.counts_by_license().items()):
        print(f"  {license_id:<28} {count}")

    attested = sum(1 for i in item_set if i.provenance.source == "attested")
    synthetic = sum(1 for i in item_set if i.provenance.source == "synthetic")
    print(f"\nattested {attested}, synthetic {synthetic} (excluded from headline results)")
    return 0


def export_command(args: argparse.Namespace) -> int:
    try:
        item_set = load_items(args.items_root)
    except ItemLoadError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1

    counts = export_hf(item_set, args.out_dir)
    for task, count in counts.items():
        print(f"{count:>4}  {args.out_dir / f'{task.value}.jsonl'}")
    print(f"{len(item_set)} items, hash {item_set.hash()}")
    return 0


def _progress(record: RunRecord, index: int, total: int) -> None:
    outcome = "ERROR" if record.errored else f"{record.points}/{record.max_points}"
    cached = " (cached)" if record.cached else ""
    print(
        f"{time.strftime('%H:%M:%S')} [{index}/{total}] {record.item_id} "
        f"{record.task_type.value} {outcome}{cached} -- {record.reason}",
        file=sys.stderr,
        flush=True,
    )


def run_command(args: argparse.Namespace) -> int:
    try:
        item_set = load_items(args.items_root)
    except ItemLoadError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    if not len(item_set):
        print("0 items; nothing to run.", file=sys.stderr)
        return 1

    config = RunConfig(
        provider_family=args.provider,
        model=args.model,
        template_id=args.template,
        seed=args.seed,
        minimality_threshold=args.minimality_threshold,
        zero_retention=args.retention == "zero",
        max_tokens=args.max_tokens,
        request_timeout_seconds=args.timeout,
    )
    prices = None
    if args.price_input is not None:
        prices = PricePerMTok(input=args.price_input, output=args.price_output)

    out_dir: Path = (
        args.out if args.out is not None else RUNS_ROOT / run_id(item_set.hash(), config)
    )
    try:
        result = run(
            item_set,
            create_provider(args.provider, timeout_seconds=config.request_timeout_seconds),
            config,
            ResponseCache(args.cache_dir),
            out_dir,
            prices=prices,
            on_record=_progress,
        )
    except (RetentionError, ProviderError, CacheError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1

    accounting = result.accounting
    print(f"{len(result.records)} items -> {out_dir}")
    print(
        f"provider calls {accounting.provider_calls}, cache hits {accounting.cache_hits}, "
        f"provider errors {accounting.provider_errors}"
    )
    print(
        f"billed tokens {accounting.billed_input_tokens} in / {accounting.billed_output_tokens} out"
    )
    if accounting.cost_usd is not None:
        print(f"cost ${accounting.cost_usd:.4f}")
    return 0


def report_command(args: argparse.Namespace) -> int:
    try:
        result = load_run(args.run_dir)
    except _LOAD_FAILURES as exc:
        print(f"FAIL {args.run_dir}: {exc}", file=sys.stderr)
        return 1

    print(
        f"model {result.config.model}, template {result.config.template_id}, "
        f"item set {result.item_set_hash[:12]}\n"
    )
    print(format_report(summarize(result.records, resamples=args.resamples, seed=args.ci_seed)))

    if args.compare is not None:
        try:
            other = load_run(args.compare)
            deltas = compare(result, other, resamples=args.resamples, seed=args.ci_seed)
        except (*_LOAD_FAILURES, ValueError) as exc:
            print(f"FAIL {args.compare}: {exc}", file=sys.stderr)
            return 1
        print(f"\n{format_comparison(deltas, args.run_dir.name, args.compare.name)}")
    return 0


def _column_labels(results: list[RunResult], run_dirs: list[Path]) -> list[str] | None:
    """Model ids, unless two runs share one (templates a and b of the same model), then
    directory names, then full paths; None only if the same directory was passed twice.
    """
    for labels in (
        [r.config.model for r in results],
        [run_dir.name for run_dir in run_dirs],
        [str(run_dir) for run_dir in run_dirs],
    ):
        if len(set(labels)) == len(labels):
            return labels
    return None


def table_command(args: argparse.Namespace) -> int:
    try:
        results = [load_run(run_dir) for run_dir in args.run_dirs]
    except _LOAD_FAILURES as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1

    hashes = {r.item_set_hash for r in results}
    if len(hashes) != 1:
        print(
            "FAIL runs evaluated different item sets "
            f"({', '.join(sorted(h[:12] for h in hashes))}); their scores are not comparable",
            file=sys.stderr,
        )
        return 1

    labels = _column_labels(results, args.run_dirs)
    if labels is None:
        print("FAIL run directories must be distinct", file=sys.stderr)
        return 1
    reports = [
        (label, summarize(r.records, resamples=args.resamples, seed=args.ci_seed))
        for label, r in zip(labels, results, strict=True)
    ]

    print(
        f"Item set `{hashes.pop()}`; runs: "
        f"{', '.join(f'`{run_dir.name}`' for run_dir in args.run_dirs)}.\n"
    )
    print(format_markdown_table(reports))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="csw-bench",
        description="Matrix Language Frame benchmark for intrasentential code-switching.",
    )
    parser.add_argument("--version", action="version", version=f"csw-bench {__version__}")
    parser.add_argument("--items-root", type=Path, default=ITEMS_ROOT)

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("validate", help="Schema-check every item on disk.")
    subparsers.add_parser("stats", help="Item counts, hash, and provenance breakdown.")
    subparsers.add_parser("taxonomy", help="List the violation types.")

    run_parser = subparsers.add_parser("run", help="Evaluate a model over the item set.")
    run_parser.add_argument("--provider", required=True, choices=PROVIDER_FAMILIES)
    run_parser.add_argument("--model", required=True)
    run_parser.add_argument("--template", required=True, choices=TEMPLATE_IDS)
    run_parser.add_argument("--seed", type=int, required=True)
    run_parser.add_argument(
        "--minimality-threshold",
        type=float,
        required=True,
        help="Repair minimality cutoff, calibrated in Phase 3. Required: no default.",
    )
    run_parser.add_argument(
        "--retention",
        required=True,
        choices=("zero", "default"),
        help="Provider account data-retention setting; recorded with the run. Attested "
        "items refuse to run without 'zero'.",
    )
    run_parser.add_argument("--max-tokens", type=int, default=1024)
    run_parser.add_argument(
        "--timeout",
        type=float,
        default=REQUEST_TIMEOUT_SECONDS,
        metavar="SECONDS",
        help="Wall-clock budget per model call; an item that exceeds it is recorded as "
        "errored, not scored. Recorded in run.json. Set it above max_tokens divided by "
        "your machine's tokens-per-second, or long answers error on the clock before "
        "the token budget binds.",
    )
    run_parser.add_argument("--cache-dir", type=Path, default=RUNS_ROOT / "cache")
    run_parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Run directory; defaults to a content-derived name under runs/.",
    )
    run_parser.add_argument(
        "--price-input",
        type=float,
        default=None,
        help="USD per million input tokens, as billed. Both prices or neither.",
    )
    run_parser.add_argument("--price-output", type=float, default=None)

    report_parser = subparsers.add_parser("report", help="Aggregate a run into result tables.")
    report_parser.add_argument("run_dir", type=Path)
    report_parser.add_argument(
        "--compare",
        type=Path,
        default=None,
        help="Second run directory; prints the per-task prompt-sensitivity delta.",
    )
    report_parser.add_argument("--resamples", type=int, default=10_000)
    report_parser.add_argument("--ci-seed", type=int, default=0)

    table_parser = subparsers.add_parser(
        "table", help="Markdown results table across runs of the same item set."
    )
    table_parser.add_argument("run_dirs", type=Path, nargs="+")
    table_parser.add_argument("--resamples", type=int, default=10_000)
    table_parser.add_argument("--ci-seed", type=int, default=0)

    export_parser = subparsers.add_parser(
        "export-hf",
        help="Write the item set as one JSONL file per task type, the layout the Hugging "
        "Face dataset card in data/hf/ declares.",
    )
    export_parser.add_argument("out_dir", type=Path, nargs="?", default=Path("data/hf"))

    args = parser.parse_args(argv)

    if args.command == "validate":
        return validate(args.items_root)
    if args.command == "stats":
        return stats(args.items_root)
    if args.command == "taxonomy":
        for violation in ViolationType:
            print(f"{violation.value}  {violation.name}")
        return 0
    if args.command == "run":
        if (args.price_input is None) != (args.price_output is None):
            parser.error("--price-input and --price-output must be given together")
        return run_command(args)
    if args.command == "report":
        return report_command(args)
    if args.command == "table":
        return table_command(args)
    if args.command == "export-hf":
        return export_command(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
