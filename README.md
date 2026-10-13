# csw-bench

A benchmark that checks whether a language model handles Spanish/English
**code-switching** (mixing both languages inside one clause) the way bilingual grammar
does, instead of treating the mixed sentence as broken Spanish or broken English. The
yardstick is the Matrix Language Frame (MLF) model from linguistics, which makes
specific, testable predictions about which mixes are fine and which are not.

402 items, four task types, three violation types, three local models run through
Ollama. Code and data are MIT. Every number in this repository regenerates from
committed files without a model call.

> **Status: v1.0**, tagged 2026-09-11. Item set hash `baf85c44…` (`docs/versions.md`).
> Three full-set runs are committed under `runs/full-*-a`. The item set ships with four
> known defects, listed under "Read the numbers through these" and in
> `docs/limitations.md`. One results hole is being closed: deepseek-r1:32b's
> ML-identification row was empty because all 100 of its answers hit the 300 s request
> timeout, and a rerun with a longer timeout is recorded in `ERRATA.md`.

## Quick start

```bash
uv sync --all-extras          # install: Python 3.13 + uv; pulls the Ollama SDK and the dev tools

uv run csw-bench run --provider ollama --model qwen3:30b --template a --seed 42 \
  --minimality-threshold 0.7 --retention zero --max-tokens 8192      # run: the protocol every committed run used

uv run csw-bench report runs/<run-dir>        # scores per task with 95% bootstrap intervals
```

You need a local [Ollama](https://ollama.com) server with the model pulled
(`ollama pull qwen3:30b`). No API keys, nothing leaves the machine. The run writes
`runs/<run-dir>/records.jsonl` (every prompt and raw response, scored) and `run.json`
(settings, item-set hash, token accounting); the raw responses also go to a content-hash
cache under `runs/cache/`, which is why a rerun with the same settings costs zero model
calls.

Two flags worth knowing. `--timeout SECONDS` (default 300) is the wall-clock budget per
model call; a reasoning model that writes long analyses needs it above
`max_tokens / your tokens-per-second`, or the clock cuts off answers the token budget
would have allowed (that is exactly what happened to deepseek-r1:32b, `ERRATA.md`).
`--out runs/<name>` names the run directory; without it the name is derived from the
settings.

Everything else:

```bash
uv run csw-bench validate                     # schema-check every item
uv run csw-bench stats                        # counts, hash, licenses
uv run csw-bench table runs/<a> runs/<b> ...  # one markdown table across runs of the same item set
uv run csw-bench report runs/<a> --compare runs/<b>   # item-paired delta, for prompt-sensitivity checks
uv run csw-bench export-hf                    # regenerate data/hf/ (the Hugging Face dataset)
uv run pytest                                 # the test suite, with coverage
```

## The idea in plain words

Bilingual speakers mix languages mid-sentence all the time, by rules nobody taught them.
"Compré los libros ayer" and "Compré the books ayer" both sound fine to a
Spanish/English bilingual. "Compré the libros ayer" does not. The difference: in the
third sentence an English grammatical word ("the") has been put where Spanish grammar is
in charge.

The Matrix Language Frame model (Myers-Scotton 1993) says that in any mixed clause one
language is the **Matrix Language**: it supplies the grammatical frame, meaning the
function words, the inflections, and the word order. The other language, the **Embedded
Language**, can contribute content words, or whole chunks ("islands") that are well
formed in their own grammar. Break that division and the sentence stops sounding right
to bilinguals.

That gives something gradeable. A model that puts an English article inside a Spanish
frame, or leaves an English verb without the Spanish ending the frame demands, is making
a specific error, not just an awkward one. The three violation types are three of MLF's
named predictions:

| Type | Prediction | What the violation looks like |
|---|---|---|
| T1 | System Morpheme Principle | an English grammatical word or ending inside a Spanish-framed constituent ("Compré **the** libros") |
| T3 | EL Island Trigger Hypothesis | Spanish material intruding into, or cutting, an English island ("Compró **the el** gift ayer") |
| T5 | Blocking Hypothesis | a bare English content word missing the ending Spanish requires ("**park** el carro todos los dias") |

`docs/taxonomy.md` has the full diagnostics and the two types that were cut and why;
`docs/design.md` maps each prediction to a task; `docs/references.bib` has the citations.

## The four tasks

Each task has a different failure signature, and they are never averaged.

| Task | Items | The model is asked to | A good score shows | Scoring |
|---|---|---|---|---|
| Grammaticality judgment | 102 | pick the acceptable sentence of a minimal pair | the constraint is represented at all | 0 or 1, floor 0.5 |
| Constrained continuation | 100 | finish a code-switched sentence like a bilingual would | the model can produce licensed mixing, not only recognize it | 0 to 2, floor 0 |
| ML identification | 100 | name the Matrix Language and cite the grammatical evidence | the model can analyze the frame, not just pattern-match | 1 point label + 2 evidence, floor 1/3 |
| Repair | 100 | fix a violating sentence with the smallest possible change | the model can locate the violation | 0 to 2, floor 0; a non-minimal fix earns 1 |

Scores are reported two ways: a raw mean, and an **above-chance** mean that rescales
against the task's own floor (0.5 for a two-way choice; 1/3 for ML identification
because every item's Matrix Language is Spanish and the constant answer "Spanish" earns
the label point). Hedging ("it depends", "both are acceptable") scores zero everywhere;
a benchmark that lets a model opt out measures willingness, not competence. Full rubric:
`docs/design.md` section 4.

**Items.** 402, constructed from documented MLF predictions with the derivation recorded
on each item, balanced 134/134/134 across T1/T3/T5 and about 31 per (violation x task)
cell. No corpus-derived items shipped (licensing and access, `docs/corpora.md`). Every
item carries its source, license, Matrix Language, exactly one primary violation type,
a difficulty rating and the linguistic justification of its gold answer.

**Models and settings.** Local inference only, via Ollama: `qwen3:30b`, `gpt-oss:20b`,
`deepseek-r1:32b`, three distinct model lineages. Temperature 0, seed 42, 8192-token
output budget, thinking disabled, prompt template `a` (a paraphrased template `b` exists
for the prompt-sensitivity check). Every raw response is persisted; every score is
recomputable with no model call.

**Validation.** No human raters. Items were blind-reviewed by independent model
reviewers that never saw the gold label (pilot: 29/30 agreement, the one disagreement
logged in the item; the later 372 items on a 120-item stratified sample). This is a
named weakness, not a substitute for bilingual humans: `docs/limitations.md`, "No human
validation".

## Results

<!-- headline-table:start -->
**Headline table (402 items, 3 models).** The pooled per-task rows of `docs/results.md`; the per-violation rows are in that file. Regenerate with `uv run csw-bench table runs/full-qwen3-30b-a runs/full-gpt-oss-20b-a runs/full-deepseek-r1-32b-a`.

| task | violation | qwen3:30b | gpt-oss:20b | deepseek-r1:32b |
|---|---|---|---|---|
| grammaticality_judgment | all | 0.84 · +0.69 [+0.55, +0.82] · n=102 | 1.00 · +1.00 [+1.00, +1.00] · n=92 (10 errored) | 0.99 · +0.98 [+0.94, +1.00] · n=102 |
| constrained_continuation | all | 0.00 · +0.00 [+0.00, +0.00] · n=100 | 0.00 · +0.00 [+0.00, +0.00] · n=81 (19 errored) | 0.00 · +0.00 [+0.00, +0.00] · n=100 |
| ml_identification | all | 0.27 · -0.09 [-0.13, -0.06] · n=100 | 0.24 · -0.14 [-0.20, -0.09] · n=58 (42 errored) | — (100 errored) |
| repair | all | 0.63 · +0.63 [+0.54, +0.72] · n=100 | 0.79 · +0.79 [+0.70, +0.87] · n=94 (6 errored) | 0.31 · +0.31 [+0.22, +0.40] · n=100 |

Each cell: raw mean · above-chance mean [95% CI] · scored n. Above-chance rescales each task against its own floor; tasks are never averaged. Errored records (provider failures, not model answers) are excluded from the score and counted. Bootstrap: 10000 resamples, seed 0.
<!-- headline-table:end -->

The per-violation rows (T1/T3/T5 for every task and model) are in `docs/results.md`,
and `docs/findings.md` reads them. The short version: all three models are above chance
at telling licensed from violating sentences; none produce licensed mixing on demand;
the two that answered ML identification sit below the constant-label floor; all three
can repair, in a wide spread, and in two of them (qwen3:30b and gpt-oss:20b) repair
collapses on T5, the bare-English-verb type, while holding up on T1 and T3.
deepseek-r1:32b has a different shape: 0.76 on T1 and 0.09 on both T3 and T5, which
`docs/findings.md` traces to the model dropping the English and translating. The
pilot-scale table (30 items) is in `docs/results-pilot.md` and is not the headline.

### Read the numbers through these

1. **Errored is not wrong.** An errored record is a provider failure (timeout, output
   budget exhausted before any text, a crashed runner), excluded from the score and
   counted beside it. gpt-oss:20b has 77 across all four tasks (judgment 10,
   continuation 19, ML identification 42, repair 6), 75 of them the 8192-token budget
   spent before any content, which selects the items it reasoned longest about; its
   cells are over the items it answered. deepseek-r1:32b's 100 errors are all one task,
   ML identification, every one a 300 s timeout; its other 302 records are clean, and a
   rerun with a longer timeout is in `ERRATA.md`.
2. **ML identification's evidence points were never earned.** The label point is free
   (every item's Matrix Language is Spanish) and the evidence check is a substring
   match against recorded evidence strings, which credited none of the 158 scored
   responses. A negative above-chance value means the model named English; under the
   v1.0 scorer the row cannot be positive for any model.
3. **Constrained continuation is scored as exact-string coincidence.** A response that
   produces the licensed construction with a different noun scores 0, the same as a
   failure. Read that row for the violation-production rate
   (`scripts/continuation_escape_hatch.py`: 0 of 281 scored continuations reproduced a
   recorded violation), not the score.
4. **The 372 post-pilot items carry no Spanish diacritics** ("Compre", "manana").
   Scoring strips diacritics, answers are unaffected, but the stimulus the model saw is
   non-standard Spanish.
5. **Continuation items share stimuli.** The 100 items render to 24 distinct prompts, one
   response each at temperature 0; the task's best possible score is 24/100 and its n
   overstates independent observations. `docs/results.md` names the cells.
6. **The construction-time ceiling is historical.** The blind-review answers behind it
   were lost before being committed, and the figures in `docs/journal.md` cannot be
   regenerated from this repository. This is the one exception to "every number
   reproducible".

## What this does not show

- **Not code-switching competence in general.** It measures consistency with one theory
  (MLF) on one language pair. A low score is evidence against MLF-consistency, not proof
  a model "cannot code-switch"; a model could follow a different, defensible theory.
- **One pair, and a close one.** Spanish and English share SVO order and the Latin
  script. Nothing here separates "the model represents the MLF constraint" from "the
  model benefits from the overlap". A typologically distant pair would; none is included.
- **Single clauses only.** Nothing about switching at clause boundaries or across turns.
- **Temperature 0 only.** Whether a model's typical sampled output behaves the same is a
  different question.
- **Constructed items only.** No attested corpus examples shipped, and the two
  reviewers were models, not bilingual humans.
- **Three violation types.** Two real contact phenomena (a missing Spanish function
  word, agreement failure on an English noun) are out of scope by design and would go
  undetected.
- **Two of the four scorers are brittle** in the specific ways listed above (ML
  identification evidence, continuation exact match). Treat those rows as lower bounds
  and read `docs/findings.md`, which found three "escape hatches": models reaching a
  licensed sentence without engaging the constraint under test.

`docs/limitations.md` has every threat a reviewer would otherwise have to find,
including the ones that cannot be mitigated.

## Reproducing every number

- Any table or interval: `uv run csw-bench table` or `report` over the committed `runs/`
  directories, read-only; the bootstrap seed defaults to 0 and is printed with the table.
  `docs/results.md` and the headline block above are written by
  `scripts/finalize_phase4.py` from those same runs, never retyped, and that script
  refuses to write under any item-set hash `docs/versions.md` does not name as v1.0.
- Any score after a scorer change: `uv run python scripts/rescore_run.py runs/<run-dir>
  --items-root <the set that run saw>` recomputes every record from its persisted
  response text. It rewrites the run directory in place; the pilot runs were over
  `data/items-pilot`.
- The item-set hash: `uv run csw-bench stats`; `tests/test_shipped_set.py` fails if it
  drifts from `docs/versions.md`, and fails if `data/hf/` drifts from `data/items/`.
- Not reproducible: the Phase 4 blind-review agreement rates and the construction-time
  ceiling (caveat 6).

The programmatic API, used by the downstream project `matriz`:

```python
from pathlib import Path
from csw_bench.loader import load_items
from csw_bench.scoring import score
from csw_bench.taxonomy import TaskType, ViolationType

item_set = load_items(Path("data/items"))
t1_items = item_set.filter_by_violation_type(ViolationType.EL_SYSTEM_MORPHEME)  # a held-out split
repair_items = item_set.filter_by_task_type(TaskType.REPAIR)
result = score(item, model_response_text, minimality_threshold=0.7)
```

## The data

`data/items/es-en/` holds the 402 items as one JSON file each, the form the hash is
computed over. `data/hf/` is the same items as one JSONL file per task type with a
Hugging Face dataset card (`data/hf/README.md`), regenerated by
`uv run csw-bench export-hf` and pinned to the items by a test. `data/items-pilot/` is
the first 30 items, byte for byte, kept because every `runs/pilot-*` run records its
hash.

**License, read before building on it.** Code is MIT. Each item carries its own
`provenance.license`, and at v1.0 all 402 are MIT (`uv run csw-bench stats`). The
per-item field exists because a corpus-derived item would inherit its corpus's license;
the Bangor Miami corpus, the one usable source found, is read as CC BY-NC-SA 3.0, whose
non-commercial clause would propagate to anything built on such items, fine-tuned models
included. No such item shipped. Filter on the field rather than assuming.

**Provenance rules** that make or break credibility: attested items are cited; constructed
items are built from a documented MLF prediction with the derivation recorded;
LLM-generated items are allowed only as distractors flagged `synthetic: true` and excluded
from headline results (none shipped); every item gets a second, blind review pass, and
disagreement is logged in the item rather than resolved; an item and its own gold label
are never produced in the same pass.

## Beyond this repository

- `integrations/la-leaderboard/` is an lm-evaluation-harness task for the two tasks that
  port cleanly (judgment and repair), in the format La Leaderboard uses, with a README on
  how it would be submitted. Not submitted.
- A separate project, `matriz`, fine-tunes models and evaluates them here to test
  whether MLF constraints are learnable. That dependency is why the taxonomy is an
  enumerated type, every item has exactly one primary violation, the set is
  hash-stamped, and the repo freezes once training begins (`docs/charter.md`, "Downstream
  contract"). Post-freeze issues go to `ERRATA.md`, never into item edits.

## Repository layout

```
data/items/        the 402 items, under es-en/;  data/items-pilot/ the first 30
data/hf/           the Hugging Face export (JSONL per task) and its dataset card
docs/              design.md, taxonomy.md, journal.md, versions.md, findings.md,
                   limitations.md, charter.md, results.md (generated),
                   results-pilot.md (generated)
src/csw_bench/     schema, loader, prompts, providers, cache, runner, scoring,
                   results, stats, export, cli
scripts/           run_phase4.sh (the original runbook), finalize_phase4.py,
                   rescore_run.py, continuation_escape_hatch.py, compute_ceiling.py,
                   watchdog.sh, item builders (frozen)
runs/              run.json + records.jsonl per run, committed; the raw response
                   cache under runs/cache/ and runs/logs/ are gitignored
integrations/      la-leaderboard/ (lm-evaluation-harness task)
tests/
```

## Citing

`CITATION.cff` has the metadata. Please record the item-set hash you evaluated against
alongside any number you report.
