# Versions

The item set is versioned and hash-stamped. `matriz` records the hash it evaluated
against; a silent edit after that point invalidates the downstream experiment.

## How the hash is computed

`ItemSet.hash()` (`csw_bench.loader.ItemSet`) — SHA-256 over the canonical serialization
of every item, sorted by item ID, with volatile fields (file mtime, load order) excluded.
The exact procedure is fixed once and never changed without a version bump, because a
change to the hashing procedure is indistinguishable from a change to the data.

`uv run csw-bench stats` prints the hash of the items on disk. `tests/test_shipped_set.py`
asserts that it equals the v1.0 row below, so editing any item fails the test suite
instead of drifting silently past the recorded hash.

## Released versions

| Version | Date | Item count | Pairs | Item-set SHA-256 | Notes |
|---|---|---|---|---|---|
| v1.0 | 2026-09-11 | 402 | es-en | baf85c444ea741fd812f8f09eeafe9048db617b7383025c5b353a7c66fab069c | Item set final as of 2026-09-01; git tag `v1.0` applied 2026-09-11 after the Phase 4 results table (`docs/results.md`, three full runs). Known defects carried into the release, deliberately not fixed: `docs/limitations.md` § "Known item-set defects at v1.0". |
| pilot | 2026-08-16 | 30 | es-en | 73a3116e87b0110e271d11443574a89bbd00875f050893b8ca48b726dfbd09b7 | `data/items-pilot/`, the first 30 items of v1.0 byte-for-byte. Recorded because every `runs/pilot-*` run carries it in `run.json`. Not a release. |

## Freeze policy

Once `matriz` begins training against a released hash, this repo **freezes**. Flaws
found after that point are documented in `ERRATA.md` and reported alongside results.
They are not quietly fixed. A repaired benchmark mid-experiment is worse than a flawed
one, because the flaw is at least disclosable.

Defects known *before* the tag are not errata. They are listed in `docs/limitations.md`
and shipped as-is, because the blind-review sample and the pilot runs were measured
against exactly these items; changing them now would silently disconnect those numbers
from the data they describe.
