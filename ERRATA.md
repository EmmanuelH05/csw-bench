# Errata

**This file is intentionally empty of entries.**

Once `matriz` begins training against a released item-set hash, this repo freezes.
Problems discovered after that point are recorded here and reported alongside results.
They are **not** fixed by editing items.

The reasoning: a benchmark repaired mid-experiment is worse than a flawed one, because
the flaw is at least disclosable. An item silently corrected after a model was evaluated
against it makes every downstream number unreproducible and unfalsifiable.

## Format

Each entry records:

- **Date noticed** and by whom
- **Affected item IDs**
- **What is wrong** — the specific defect, not a vague concern
- **Suspected effect on results** — which cells of which tables are implicated
- **Why it was not fixed** — normally "post-freeze", but state it explicitly

## Entries

_None as of v1.0 (tagged 2026-09-11, item set `baf85c44…`). The freeze begins when
`matriz` starts training against that hash. Defects known before the tag are not errata;
they are listed in `docs/limitations.md`, "Known item-set defects at v1.0", and shipped
as-is._
