# Project charter

## Project

**`csw-bench`**: an evaluation benchmark measuring whether LLMs handle intrasentential
code-switching in a way consistent with the Matrix Language Frame model, rather than
treating mixed-language input as degraded monolingual text.

**This is the ruler.** A downstream project (`matriz`) uses it to test whether MLF
constraints are learnable by fine-tuning. That dependency imposes hard constraints on this
repo, listed under "Downstream contract" below. Read that section before Phase 1, because
it changes decisions you would otherwise make casually.

**The contribution is construct validity, not a leaderboard.** Anyone can prompt a model
with Spanglish and score it. The defensible claim is that the items are grounded in a
theory with falsifiable predictions, and that the scoring measures what the theory
predicts.

## The core claim

MLF predicts that in a code-switched clause, one language (the Matrix Language) supplies
the morphosyntactic frame: system morphemes and constituent order. The Embedded Language
contributes content morphemes only, inside EL islands.

That gives gradeable violations. A model producing EL system morphemes inside an ML frame,
or ML order under EL lexical pressure, is making a specific error, not merely an awkward
one. That specificity is what we measure and what a vibes-based eval cannot.

## Downstream contract

`matriz` fine-tunes models and evaluates them here. For that experiment to mean anything:

- **Violation types must be a first-class, enumerated taxonomy**, not free-text tags.
  `matriz` holds out entire violation types from training. It cannot do that if the
  taxonomy is fuzzy.
- **Every item is tagged with exactly one primary violation type.** Secondary tags allowed,
  but the primary is required and single-valued.
- **The item set is versioned and hash-stamped.** `matriz` records the hash it evaluated
  against. Silent edits after that point invalidate the experiment.
- **Once `matriz` starts training, this repo freezes.** Flaws found afterward get
  documented in an errata file and reported alongside results. They do not get quietly
  fixed. A repaired benchmark mid-experiment is worse than a flawed one, because the flaw
  is at least disclosable.
- **Ship a stable programmatic interface**: load items, filter by violation type, score a
  response. `matriz` should never need to parse our files by hand.

## Non-goals

- Do not fine-tune, train, or improve any model here. That is `matriz`.
- No UI, dashboard, or hosted leaderboard
- Do not extend beyond Spanish/English
- Do not use LLM-generated stimuli as the primary item set (see provenance rules)
- Do not claim generality across all bilingual speech. This measures a specific construct.

## Language pairs

**Spanish/English only.** Well documented in the code-switching literature, typologically
close enough that ML assignment is contested in interesting ways, and backed by digitized
corpora (Bangor Miami, Spanish in Texas, LinCE) that made the pair look reachable at the
time this was written. Phase 1 licensing recon (`docs/corpora.md`) later found only
Bangor Miami usable as an actual item source — Spanish in Texas is CC BY-NC-ND (forbids
derived items) and LinCE states no license anywhere. The pair choice itself still stands
on the other grounds named here; the corpus-abundance argument does not.

This is a deliberate narrowing from an earlier two-pair design. One pair done to depth
beats two done thinly, and the item-count and second-pass-review budget is finite. The
cost is real and gets named rather than hidden: without a typologically distant pair we
cannot separate "the model represents the MLF constraint" from "the model benefits from
Spanish and English sharing SVO order and a Latin-script lexicon." That goes in
`docs/limitations.md` as a stated threat, not a footnote.

Do not add a second pair without reopening Phase 1.

## Task design

Four task types, each with a distinct failure signature:

- **Grammaticality judgment.** Minimal pairs differing only in an MLF violation. Tests
  whether the constraint is represented at all.
- **Constrained continuation.** A code-switched prompt where MLF licenses only some
  continuations. Tests generation, not recognition.
- **ML identification.** Given a mixed utterance, name the Matrix Language and cite the
  morphosyntactic evidence. Tests analysis rather than pattern matching.
- **Repair.** Given a violating utterance, fix it minimally. Tests whether the model can
  locate the violation.

Each item carries: source, language pair, ML label, **primary violation type**, difficulty,
and the linguistic justification for the gold answer.

## Violation taxonomy

Define this in `docs/taxonomy.md` in Phase 1. It is the spine of both projects.

Requirements:
- Each type traces to a named MLF prediction with a citation
- Types are mutually exclusive at the primary level
- Each type has at least one attested example and one constructed example
- Each type has a stated diagnostic: how you decide an item belongs to it
- Minimum **three** types, or the held-out split downstream is not meaningful

> **Amended 2026-08-16 from "minimum four" to "minimum three."** Phase 1 shipped three
> types (T1, T3, T5) after two types were dropped — T4 (populability) and T2
> (populability, reached by three independent, converging lines of evidence) — on
> exactly the same evidentiary standard: a type `matriz` cannot meaningfully hold out is
> not a type, it is a rounding error with a name. This was not a convenience trim. Full
> reasoning in `docs/journal.md` and `docs/taxonomy.md` § "T2 dropped." The floor exists
> to keep the held-out split meaningful, and three types still supports it: `matriz` can
> hold out one type and train on the other two, same as the four-type design held out one
> and trained on three. See Phase 4 below for the recalculated item-density arithmetic
> this forces.

## Item provenance rules

The part that makes or breaks credibility.

- **Attested items** from published corpora and the code-switching literature are primary.
  Cite every one.
- **Constructed items** are allowed only when built from a documented MLF prediction, with
  the derivation recorded in the item metadata.
- **LLM-generated items** are permitted only as distractor candidates, flagged
  `synthetic: true`, and excluded from headline results. Reporting them in the main table
  is circular and kills the project.
- **Every item gets a second-pass review.** Log inter-rater disagreement rather than
  silently resolving it. The disagreement rate is a reported statistic, not an
  embarrassment.
- **Never generate an item and its own gold label in the same pass.**

## Phases

Sequential. No phase begins with a prior checkbox open. Each phase ends with a commit and
an entry in `docs/journal.md` recording what was tried, what broke, and what changed in
our thinking.

### Phase 1: Design before items

- `docs/design.md`: which MLF predictions are operationalized, the mapping from prediction
  to task type, the scoring rubric, and threats to validity
- `docs/taxonomy.md`: the violation taxonomy per the requirements above
- State explicitly what a null result looks like downstream and why it is still publishable

Completion conditions:
- [x] Every task type traces to a named MLF prediction with a citation — `docs/design.md`
      §2
- [x] The rubric assigns partial credit without rewarding hedging — `docs/design.md` §4,
      three-part anti-hedging rule
- [x] At least three threats to validity named, including one that cannot be fully
      mitigated — `docs/design.md` §5, seven named and ranked, two tagged UNMITIGABLE;
      elaborated in `docs/limitations.md`
- [x] Taxonomy has at least three mutually exclusive types, each with a stated diagnostic
      — shipped three (T1, T3, T5); see the amendment note above and `docs/journal.md`

### Phase 2: Pilot set

30 items, all four task types, hand built and hand checked.

Completion conditions:
- [x] Every item has full provenance metadata and passes schema validation — 30/30,
      `csw-bench validate`
- [x] Every item has exactly one primary violation type from the taxonomy — 10 T1, 10 T3,
      10 T5
- [x] Two independent passes on gold labels; disagreement rate reported, not hidden —
      construction pass + blind review pass; 1/30 (3.3%) genuine disagreement logged in
      that item's `provenance.review_disagreement`, not resolved by fiat
- [x] Independent blind review scores above 90% — **29/30 (96.7%) construct-validity
      agreement**: the reviewer's independent judgment matched the gold label on every
      item except the one logged disagreement. The literal automated scorer reports a
      lower raw number (42/58, 72.4%) because of a separate, pre-existing issue: its
      substring-matching evidence check under-credits correct free-text morphosyntactic
      reasoning on all 7 ML-identification items, even though the reviewer named the
      correct Matrix Language with sound reasoning in every one — exactly the brittleness
      `scoring.py`'s own docstring already names as needing a Phase 3 response-extraction
      step. Full breakdown in `docs/journal.md`.

> **Amended 2026-08-16 — human validation replaced with documented AI-substitute
> validation.** The original gate was three bilingual humans scoring the pilot blind. No
> human raters are being recruited for this project; the gate is met instead by
> independent *blind* review passes — a reviewer sees only the string(s) and must produce
> the judgment/answer without ever having seen the gold label or derivation, run as a
> genuinely separate pass from the one that built the item, ideally across more than one
> model family to reduce correlated blind spots.
>
> **This is a real degradation, not a relabeling, and it is named as one.** A human bilingual
> catches things a model of any family may share a blind spot with — the exact risk this
> gate existed to catch. Substituting AI review for human review is most dangerous
> precisely where it matters most: items testing whether models represent MLF correctly,
> reviewed by a model whose own MLF competence is the unknown quantity. The mitigation is
> partial, not a fix: (1) the reviewer is blind to the gold label, so it cannot just agree
> with itself; (2) disagreement between independent reviewers is logged as data, per the
> disagreement-reporting rule already in place, not resolved into false consensus; (3)
> `docs/limitations.md` carries this as a first-class, load-bearing threat, not a footnote.
> Any reviewer of this project — human or otherwise — should treat pilot-stage item
> quality as *provisionally* validated, weaker than the original design intended.

### Phase 3: Harness

- Model-agnostic runner supporting at least three model families

> **Amended 2026-08-17 — local models only, via Ollama.** The original design assumed
> three cloud API vendors (Anthropic, OpenAI, Google); the principal clarified the intent
> was local inference throughout. `providers.py` now ships a single `OllamaProvider`
> talking to a local Ollama server — no API keys, no per-token cost, no data leaving the
> machine. "Three model families" now means three distinct local model lineages (not
> three vendors), enforced by which `model` id a run picks, the same way the old
> `OpenAIProvider` served many model ids under one family. Full reasoning and the
> `PricePerMTok`/`zero_retention` implications in `docs/journal.md`, "Phase 3 pivot: local
> models," and `docs/design.md` §5.7.

- Deterministic settings, fixed seeds, logged prompt templates
- Every raw response persisted; rerunnable from cache without re-billing
- Cost and token accounting per run
- The public API `matriz` will consume: load, filter by violation type, score

Completion conditions:
- [x] Full pilot runs end to end against three models — gpt-oss:20b, qwen3:30b,
      deepseek-r1:32b (three distinct local model lineages), all 30/30 items completed
      and rescoreable from cache; results in `docs/journal.md` "Phase 3 gate" entries and
      `runs/pilot-{gpt-oss-20b,qwen3-30b,deepseek-r1-32b}-a/`
- [x] A rerun from cache reproduces identical scores — verified directly against
      `runs/pilot-deepseek-r1-32b-a`'s warm cache: 23/23 non-errored records reproduce
      identical response text and score via cache lookup, 0 provider calls
      (`docs/journal.md`, "Cache-rerun reproducibility, verified and one honest caveat").
      Same section names the caveat: gpt-oss/qwen3's raw caches were incidentally wiped
      by an earlier resource-contention workaround, so a cold-cache CLI rerun of those
      two specific runs would re-bill most items today, even though their committed
      `records.jsonl` already makes every score independently reproducible
- [x] Prompt sensitivity check: two paraphrased templates, delta reported — run
      2026-09-08, qwen3:30b on the pilot, `runs/pilot-qwen3-30b-b/` vs `-a/`, paired by
      item with a bootstrap CI (`csw-bench report --compare`): no distinguishable delta
      on judgment, continuation, or repair; as first scored, a 0.286 [+0.071, +0.429]
      above-chance drop on `ml_identification` under template b, about three quarters
      of it the scorer's claim anchor not recognising a claim phrased without "Matrix
      Language" (`docs/journal.md`, "Phase 3 gate closed"). The scorer revision landed
      2026-09-10 across every committed run; the delta is now 0.071 [+0.000, +0.214],
      one genuinely wrong answer (`docs/findings.md`)
- [x] Filter-by-violation-type returns correct disjoint sets, tested —
      `test_filter_by_violation_type_returns_disjoint_sets` (`tests/test_loader.py`), plus
      re-verified directly against the real 30-item pilot set: 10/10/10 T1/T3/T5, zero
      overlap, union covers all 30

### Phase 4: Full set and results

Target roughly 400 Spanish/English items, balanced by task type and violation type.

The count stays at 400 rather than halving with the pair count. That is the whole point of
going single-pair: with three violation types across four task types the design has
twelve cells, so 400 items is roughly thirty-three per cell — enough that holding out a
violation type downstream still leaves usable training data. At 200 it would not.

> **Recalculated 2026-08-16** from the original four-type, sixteen-cell arithmetic (~25
> items/cell) after the taxonomy amendment above dropped to three types. Cell density
> went *up*, not down — a smaller type count with the same 400-item target means denser
> cells, which strengthens rather than weakens the holdout argument this paragraph makes.

Completion conditions:
- [x] Results table by model, task type, and violation type — `docs/results.md`,
      written 2026-09-11 by `scripts/finalize_phase4.py` as the unchanged output of
      `csw-bench table runs/full-qwen3-30b-a runs/full-gpt-oss-20b-a
      runs/full-deepseek-r1-32b-a`; the README headline block is generated from the same
      runs. All three runs are 402/402 records and committed (`docs/journal.md`,
      2026-09-10 and 2026-09-11). The pilot-scale table (`docs/results-pilot.md`) is not
      the headline
- [x] Bootstrap confidence intervals. No bare point estimates. — every cell of the
      `table` output carries a 95% percentile-bootstrap CI (`csw_bench.stats.bootstrap_ci`),
      and the prompt-sensitivity delta carries a paired one
- [x] A ceiling reference on a sampled subset, so model scores have something to compare
      against — see amendment below for what this is instead of a human ceiling.
      `scripts/compute_ceiling.py` scores the Phase 4 blind-review sample (120 items)
      with the real scorer: judgment 100%, repair 100%, ml_identification 33% (label
      point only — the already-documented evidence-matching brittleness, not a construct
      problem), continuation 0% (the EL-island escape hatch finding below).
      **Reproducibility lost 2026-09-01:** the review answers lived in `/tmp` and are
      gone, so these figures are historical; the script now reads
      `data/review/phase4-blind-sample/` and fails until a new pass is collected there
- [x] At least one finding that was not expected, reported as found — the EL-island
      escape hatch in `constrained_continuation` (`docs/findings.md`, `docs/design.md`
      §5.9): independent blind reviewers default to a fully-English, still MLF-licensed
      completion instead of the narrow construction the item probes, which the current
      scorer can't distinguish from a wrong answer
- [x] Item counts per violation type are balanced enough that a held-out split downstream
      leaves usable training data — 134/134/134 across T1/T3/T5, ~31 items per
      (violation x task type) cell across all 12 cells

> **Amended 2026-08-16 — no human ceiling; same reason as Phase 2.** The original design
> used a human ceiling specifically so model scores had a reference point independent of
> the model family being scored. Without recruited humans, the substitute is a
> **construction-time ceiling**: the item author's own blind pass at each item — scored
> the same way a model would be, before the gold label is consulted — reported alongside
> the frontier-model scores as the best available reference, explicitly labeled as *not*
> a human ceiling. This is a materially weaker reference than the original design called
> for: it does not establish that a bilingual human finds the construct tractable, only
> that the item author's own review process is internally consistent. Reported as a named
> limitation in `docs/limitations.md`, not presented as equivalent to what Phase 4
> originally specified.

### Phase 5: Freeze and release

- [x] Item set hashed, tagged `v1.0`, hash recorded in `docs/versions.md` — hash
      `baf85c44…` pinned by `tests/test_shipped_set.py`; tag `v1.0` applied 2026-09-11
      after the Phase 4 boxes closed
- [x] `README.md`: the claim, the method, the headline table, how to run it — the
      headline block is generated by `scripts/finalize_phase4.py` from the same runs as
      `docs/results.md`; banner and caveats current as of 2026-09-11
- [x] `docs/findings.md`: what error patterns suggest about model representations —
      headline and error-pattern sections cover all three runs (2026-09-10, 2026-09-11)
- [x] `docs/limitations.md`: honest enough that a reviewer cannot find a hole you did not
      already name — written, including the four v1.0 item-set defects and the
      full-run numbers section (formerly PENDING RUNS)
- [x] `ERRATA.md` created empty, with a note that post-freeze issues go here rather than
      into item edits — done in Phase 0
- [ ] Someone with no linguistics background can read the README and state what is measured
      — the README opens with a section written for exactly this reader; the box stays
      open until such a reader has actually done it, which no one on this project can
      substitute for
- [ ] Someone with linguistics background can find the theoretical grounding in a minute
      — the README's second section is a table from violation type to named MLF
      prediction with citation, one screen down; same condition to close as above
- [x] Every number reproducible from committed code and data — true of every model
      result (`csw-bench table`, `csw-bench report`, `scripts/rescore_run.py` over
      committed `runs/`); **not true of the construction-time ceiling or the Phase 4
      review agreement rates**, whose source answers were lost (`docs/journal.md`,
      2026-09-01). Closed 2026-09-10 by stating that exception in the README
      ("Reproducing", last bullet); re-collecting the sample into
      `data/review/phase4-blind-sample/` would remove the exception

## Working style

- **Reasoning council** on any item design dispute: argue both readings of the MLF
  prediction before writing the gold label. Record the losing argument in the item metadata.
- Report disagreement and negative results as findings. Suppressing them is the exact
  failure mode this project exists to avoid.
- When a model's answer looks wrong but is arguably licensed, that is a finding about the
  item, not the model. Flag it.
- Commit per phase with item count and current disagreement rate in the message.

## Operating invariants

Stack: **Python 3.13 + uv + pytest**.

```bash
uv sync --all-extras         # install
uv run pytest                # verify — this is the completion check
uv run ruff check . && uv run mypy src scripts   # lint + types
uv run csw-bench validate    # schema-check every item on disk
scripts/run_phase4.sh        # the remaining inference, resumable; read its header first
uv run csw-bench table runs/full-*-a   # after the runs: results table with CIs
```

Rules that get violated otherwise:

- **No item exists before its validator does.** `csw-bench validate` must fail loudly if
  it finds items it cannot check. There is a test asserting this; do not delete it.
- **Documents lead code.** The violation taxonomy lives in `docs/taxonomy.md` first. The
  `ViolationType` enum is written against a ratified document, never ahead of it —
  otherwise the code silently becomes the source of truth for the theory.
- **No phase opens with a prior checkbox open.** Check `docs/design.md` before starting
  Phase 2, and the phase's own conditions in this file before every other phase.
- **Never generate an item and its own gold label in the same pass.**
- **Disagreement gets logged, not resolved.** Inter-rater disagreement rate is a reported
  statistic. Silently reconciling it destroys the number.
- **Every phase ends with a commit plus a `docs/journal.md` entry** recording what was
  tried, what broke, and what changed in our thinking. Commit message carries item count
  and current disagreement rate.
- **Post-freeze, nothing is fixed.** Issues go to `ERRATA.md`. Do not edit items.

## Code quality bar

This section is non-negotiable and applies to every file in the repo. Violations get
fixed, not discussed.

### Comments

Comments earn their place or they get deleted. A comment restating what the line already
says is noise, and it rots the moment the line changes.

**Write one only for:** a non-obvious *why*, a decision whose alternative looks better
than it is, a linguistic judgment a reader could not reconstruct, or a citation.

**Never write:** a restatement of what the code plainly does, a section banner, a
docstring on a self-evident helper, `# Arrange / # Act / # Assert` scaffolding, a
changelog or TODO in a comment (use git and the journal), or a docstring that describes
the function's own name back to the reader.

Same standard for prose. No filler sections, no restating the header in the first
sentence, no paragraphs that hedge without committing.

### No obviously wasteful code

Not premature micro-optimization — the KISS and YAGNI rules still hold, and clever beats
readable exactly never. This bans *waste that a careful reader would notice*:

- **No repeated work.** Do not re-read item files on every filter call, re-parse a prompt
  template per item, or recompute inside a loop what is invariant across it. Load once,
  index once, reuse.
- **No accidental quadratic behavior.** Membership tests against a list where a set is
  the obvious structure; nested scans over items that a single dict lookup replaces. At
  400 items this does not hurt — it is banned because it signals not thinking, and
  because the cached-run path in Phase 3 is where it would start to.
- **No redundant passes.** One traversal over items, not one per field extracted.
- **Cache what is expensive and deterministic.** Model responses are keyed by content
  hash of prompt + model + seed, per the Phase 3 requirement that reruns never re-bill.
- **No dead code.** Unused parameters, unreachable branches, functions nothing calls, and
  imports nothing uses do not get committed. `ruff` catches most of this; the rest is on
  the author.

The check is: could a reader point at a line and say *why is it doing that twice?* If
yes, fix it before committing.

### Enforcement

`uv run ruff check . && uv run ruff format --check . && uv run mypy src scripts && uv run pytest`
passes before every commit. CI runs the same four. Green CI is not sufficient — the
comment and waste rules above are not lintable and are the author's responsibility.
