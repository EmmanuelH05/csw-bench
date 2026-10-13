# Design

> **Status, 2026-08-16: Phase 1 type structure finalized; Phase 2 pilot built.**
> Phase 2 opened with one "Blocking before Phase 2" item still unchecked — the
> repair-minimality edit-distance threshold — a recorded exception, same precedent as the
> Phase 3 harness-ahead-of-sequence entry in `docs/journal.md`: it does not block item
> *construction*, only the eventual repair-task *scoring calibration*, so it was not
> allowed to block writing the pilot. Citations marked `[VERIFY: page]` remain
> page-unchecked (login-gated/paywalled sources) — no item may cite a page nobody has
> read, and none currently does; the open citations are theoretical-prediction citations
> in `taxonomy.md`, not item-level ones.

## 1. Which MLF predictions are operationalized

Each prediction below is falsifiable about a given code-switched clause, which is what
makes it gradeable. Keys refer to `references.bib`.

| Prediction | Source | Falsifiable claim |
|---|---|---|
| **Morpheme Order Principle** | @myersscotton1993duelling `[VERIFY: page]` | Surface morpheme order in a mixed constituent follows the ML. |
| **System Morpheme Principle** | @myersscotton1993duelling `[VERIFY: page]` | Syntactically relevant system morphemes in a mixed constituent come from the ML. |
| **Blocking Hypothesis** | @myersscotton1993duelling `[VERIFY: page]` | EL content morphemes not congruent with the ML are blocked from mixed constituents. |
| **EL Island Trigger Hypothesis** | @myersscotton1993duelling `[VERIFY: page]` | An EL morpheme not licensed in a mixed constituent forces completion as a well-formed EL island. |
| **4-M model** | @myersscotton2000fourm `[VERIFY: page]` | Late *outsider* system morphemes — those depending on information outside their head constituent — come from the ML. |

Later restatements in @myersscotton2002contact are consulted where the 1993 formulation
is ambiguous, but the 1993 principles are the operative ones, because they are the
formulations the critical literature responds to.

**The 4-M model is consulted but not separately operationalized.** It originally grounded
a fifth violation type (EL late outsider system morpheme), which was cut during Phase 1 —
English inflectional morphology is too impoverished to supply the probes, and no clean
case could be constructed. The 4-M content/system distinction still does work inside the
T1 and T5 diagnostics; it just no longer indexes a type of its own. Four predictions are
operationalized as types; the fifth informs how the others are applied. See
`taxonomy.md` and `ordering-stress-test.md`.

## 2. Mapping from prediction to task type

Each task type is a different *cognitive demand* on the same underlying constraint. That
is the design's leverage: a model can pattern-match its way through recognition while
failing at generation, and the gap between the two is itself a finding.

| Task type | Prediction operationalized | What it demands | Failure signature |
|---|---|---|---|
| **Grammaticality judgment** | All five, via minimal pairs | Recognition | Constraint is not represented at all — model cannot distinguish a violating string from its licensed twin. |
| **Constrained continuation** | Morpheme Order, System Morpheme, Blocking | Generation under constraint | Constraint is represented passively but does not govern production. Model recognizes violations it will nonetheless commit. |
| **ML identification** | ML criteria (morpheme order + system morphemes) | Analysis | Model reaches the right label by counting words rather than by morphosyntax — detectable because the rubric scores label and evidence separately. |
| **Repair** | All five | Localization | Model detects that something is wrong but cannot say *where*, revealed by wholesale rewrites that fix the string without isolating the violation. |

Note the deliberate asymmetry: grammaticality judgment covers all five predictions
because minimal pairs can isolate any of them, while constrained continuation covers
three, since island triggering and outsider morphology are hard to force in a
continuation without telegraphing the answer.

## 2a. The task types are not redundant

An objection worth pre-empting, because a reviewer will raise it: if grammaticality
judgment already covers all five predictions, why the other three?

Because they dissociate. A model scoring high on judgment and low on continuation has a
represented constraint that does not govern production — a specific, reportable claim
about its representations. Collapsing to one task type would make that claim
unavailable. The four-way design exists to produce dissociations, not coverage.

## 3. Language pair — Spanish/English

Single pair, by decision rather than by attrition.

**Why Spanish/English.** It is the most densely documented pair in the code-switching
literature, which is what makes the provenance rules satisfiable: attested items with real
citations exist in quantity.

**Corpus reality after Track A — this is now a one-source project.** The plan assumed three
usable corpora. Licensing recon left one:

| Source | Status |
|---|---|
| Bangor Miami | **The only viable source.** CC BY-NC-SA 3.0. Download is auth-gated; `%mor` tier presence unconfirmed. |
| Spanish in Texas | **Unusable as an item source.** CC BY-NC-**ND** 4.0 — derived items may not be redistributed, and a benchmark item is an adaptation. |
| LinCE | **Blocked.** No license stated anywhere; site unreachable; and its Spanish/English POS split is Bangor Miami anyway, so it launders nothing. |

The two corpora are also mutually unpoolable: SA requires adaptations be shared alike, ND
forbids adaptations at all. There is no merged corpus — only per-item licenses and a
loader that filters on them.

Concentrating on one corpus is a real risk and is recorded as such in `limitations.md`.
Details and the options for reopening Spanish in Texas are in `corpora.md`.

It is also the pair where Matrix Language assignment is *contested in interesting ways* —
close enough typologically that the ML criteria have to do real work, which is where the
gradeable violations live.

**Why only one pair.** Item count and second-pass-review effort are the binding
constraints, not enthusiasm. Two pairs at 200 items each yields roughly ten items per
violation-type × task-type cell, which is too thin for the downstream held-out split to
leave usable training data. One pair at 400 doubles the density per cell. Depth is the
choice that makes `matriz` possible.

**What this costs, stated plainly.** Spanish and English share SVO constituent order, a
Latin script, and substantial cognate vocabulary. A model could therefore score well by
exploiting that overlap rather than by representing an MLF constraint, and a single pair
gives us no contrast case to rule that out. A typologically distant pair would have
provided exactly that contrast. We do not have it. See `limitations.md` §
"Single-pair design", which treats this as a first-class threat, not a caveat.

**Partial mitigation within the pair.** Items can still be built where MLF prediction and
Spanish/English surface overlap *dissent* — cases where the shared-order heuristic gives
the wrong answer. Those items are the closest thing to a contrast case available here, and
their score should be reported separately from the aggregate.

## 4. Scoring rubric

### The anti-hedging rule

Partial credit is available *within* a committed answer, never for declining to commit.
Three consequences, applied uniformly:

1. **Non-commitment scores zero.** "It depends," "both are acceptable in some
   varieties," and refusals score 0, not partial. They are not treated as a separate
   response category, because a benchmark that lets models opt out measures willingness,
   not competence.
2. **Monolingual output scores zero on generation tasks.** Without this, a model dodges
   every continuation item by answering in one language. This is the single largest
   hedging hole in the design and it is closed explicitly.
3. **Right answer, wrong reasoning earns the label credit only.** The rubric separates
   *what* from *why* so that pattern-matching to a correct label is visible rather than
   indistinguishable from analysis.

### Per task type

**Grammaticality judgment** — 2AFC. Both members of the minimal pair are presented; the
model names the licensed one. Score 1 or 0, no partial credit, chance is 50%.
Forced-choice rather than a rating scale precisely because a scale invites hedging toward
the midpoint. Reported against the 50% floor, never as a bare accuracy.

**ML identification** — 3 points, two components:

| Component | Points | Awarded for |
|---|---|---|
| Label | 1 | Correct Matrix Language named |
| Evidence | 2 | Cites morpheme order and/or system-morpheme distribution |
| Evidence | 1 | Cites relevant morphosyntax imprecisely |
| Evidence | 0 | Cites lexical counts ("more Spanish words"), or no evidence |

Lexical-frequency reasoning scores 0 on evidence *even when the label is correct*, since
word-counting reaches the right answer for the wrong reason and the whole point of this
task is to catch that. "Both languages equally" or "no single Matrix Language" scores 0
on both components.

**Constrained continuation** — 2 points:

| Points | Criterion |
|---|---|
| 2 | Continuation is code-switched and MLF-licensed |
| 1 | Code-switched and licensed but degraded (dispreferred though not violating) |
| 0 | Violates MLF, is monolingual, or declines |

> **Observed 2026-09-01, against the scorer and the shipped items, not the rubric.** Row
> 3's "is monolingual" clause is not implemented as a rule: `score_constrained_continuation`
> credits an exact match to a recorded licensed string and scores everything else 0, so
> monolingual output reaches 0 only by failing to match. It could not be implemented
> literally, because all 34 T1 licensed continuations are themselves monolingual Spanish
> strings ("las revistas para la clase") -- the rubric row and the gold labels contradict
> each other. Row 2 (1 point, degraded) is unreachable for the same reason: nothing in
> the scorer distinguishes degraded from unlisted. And the exact match fixes the noun, so
> a response that produces the licensed *construction* with a different noun ("un
> coffee" for "Ayer compré", qwen3:30b, pilot) scores 0. As scored, this task measures
> coincidence with one of two strings; read its cells for the violation-production rate
> (`scripts/continuation_escape_hatch.py`) rather than the score. `docs/findings.md`
> carries the evidence; `docs/limitations.md` carries it as a v1.0 defect.

**Repair** — 2 points:

| Points | Criterion |
|---|---|
| 2 | Violation corrected, edits confined to the violation site |
| 1 | Violation corrected, but with edits beyond the site |
| 0 | Not corrected, or "corrected" by rewriting the utterance wholesale or rendering it monolingual |

Minimality is operationalized as token-level edit distance against the gold repair, with
the threshold fixed in Phase 3 and frozen thereafter. A wholesale rewrite scores 0 even
when the output is perfectly grammatical, because the task tests *localization* — a model
that cannot find the violation has failed even if it can produce a clean sentence.

### Known weaknesses in the implementation

`csw_bench.scoring` implements this rubric and is honest about being a first pass:

- **Pattern matching is brittle against free prose.** A correct answer in an
  unanticipated phrasing can score zero, and that failure looks identical to incompetence
  — which biases scores *downward* in a way that could be mistaken for a finding.

  > **Partially addressed, 2026-08-27, against two concrete instances found running real
  > models.** `scoring.extract_final_answer` strips a leaked `<think>...</think>`
  > reasoning preamble before judgment/continuation/repair scoring — found running the
  > real pilot against `qwen3:30b`: despite `think=False`, Ollama's chat template
  > stripped the opening `<think>` tag but not the closing one, so a fully correct answer
  > that reasoned through both members of a minimal pair before committing scored 0 under
  > "no unambiguous selection." Separately, `score_ml_identification`'s label check is
  > now anchored to the response's actual "matrix language" claim rather than raw
  > first/last mention position, after a first attempt at fixing this (comparing last
  > mention) was itself falsified by a real, correctly-reasoned `qwen3:30b` response.
  > Revised again 2026-09-10 at full scale: the check now reads an explicit claim ("X is
  > the Matrix Language", "the grammatical frame is X") before falling back to mention
  > position, after the nearest-name rule zeroed twelve correct qwen3:30b answers and
  > credited one wrong one; every committed run was rescored in one pass
  > (`docs/journal.md`, 2026-09-10).
  > Neither fix closes the underlying brittleness class — a model phrasing its answer in
  > some third unanticipated way can still score 0 — only the two specific instances of
  > it that real models actually produced. Full detail in `docs/journal.md`.
- **Agreement with human scoring is unmeasured.** Until a sample is double-scored by
  hand, the automatic scores have no validated relationship to the rubric they implement.
  This is a Phase 3 blocker, not a nicety.
- **Hedge detection is English-only.** A Spanish-language hedge currently passes.
- **The repair minimality threshold is uncalibrated**, so `score_repair` requires it as
  an explicit argument rather than defaulting — no run can silently use a made-up value.

  > **Calibrated 2026-08-24 — threshold fixed at 0.7.** Computed empirically from the
  > pilot's own 7 repair items rather than picked: `SequenceMatcher(None,
  > tokenize(violating), tokenize(gold_repair)).ratio()` for every real minimal,
  > single-token-substitution gold repair in the pilot ranges 0.75-0.909 (min at
  > `csw-es-en-0009`/`0010`, both 4-token sentences with one token swapped). A simulated
  > *non-minimal* repair — the correct fix plus one additional token changed outside the
  > violation site — was computed for the same items and ranges 0.5-0.6 (max at the two
  > 5-token items). The two ranges do not overlap; 0.7 sits inside the gap, closer to the
  > minimal floor (0.05 below it) than the non-minimal ceiling (0.10 above it), which
  > matches the rubric's asymmetry: a genuinely minimal repair should never be
  > misclassified as non-minimal, and 0.7 keeps a small buffer against tokenization noise
  > on the minimal side while still safely excluding every observed non-minimal case.
  >
  > **A real limitation of this calibration, named rather than hidden.** The ratio is not
  > length-invariant: a single-token substitution's ratio is algebraically ~(N-1)/N for an
  > N-token sentence, so a 3-token sentence's minimal repair (~0.67) would fall *below*
  > 0.7 and misscore as non-minimal, while on an 8+ token sentence a genuine two-token
  > drift (~0.75) could clear 0.7 and misscore as minimal. The pilot's repair items are
  > all 4-6 tokens, which is why the calibration data doesn't surface this. The 400-item
  > set (Phase 4) keeps repair items in the same 4-7 token range for this reason — a
  > documented constraint on item construction, not an incidental one. `RepairItem`
  > already carries `violation_span`, unused by the scorer per its own docstring; the
  > durable fix is span-constrained scoring rather than whole-string ratio, tracked as
  > existing Phase 3+ follow-up work, not done here.
  >
  > **A second, more consequential finding from re-reading `score_repair` while
  > calibrating this: the minimality branch is currently unreachable in practice.** The
  > function's first gate requires `tokenize(response) == tokenize(a)` for `a` in
  > `[gold_repair, *alternate_repairs]` — an *exact* token-sequence match against a small,
  > fixed, pre-approved list. Every string in that list is itself minimal by construction
  > (the docstring on `alternate_repairs` says so explicitly). So for a given item, once a
  > response clears the exact-match gate at all, it clears it by being byte-for-byte one
  > of those pre-approved minimal strings — the similarity ratio computed afterward is
  > therefore a **constant determined by the item**, never by which response was
  > produced. The 1-point "edits exceeded the violation site" branch cannot fire for any
  > item in the current pilot set, regardless of model or threshold value, because no
  > accepted answer is non-minimal. This does not invalidate the calibration above — the
  > threshold still needs a principled value for whenever a non-minimal accepted answer
  > *does* get added, and for the day span-constrained scoring replaces the exact-match
  > gate — but it does mean Phase 3's real pilot run will show every repair response as
  > either 0 (didn't reach a listed answer, including free-prose wrapping around an
  > otherwise-correct repair) or `maximum` (matched one), never 1. That is reported
  > plainly as an observed property of the current scorer, not smoothed into "1 point"
  > results that don't actually occur.

Treat current scores as a lower bound.

### Aggregation

Task types are reported separately and never averaged into a single headline number.
Averaging across tasks with different point scales and different chance floors would
manufacture a score that means nothing. Where a summary is needed, each task is
normalized against its own chance floor and reported as a vector, not a scalar.

The floors are the score of the best analysis-free strategy on the shipped set, not an
abstract guessing rate: 0.5 for judgment (balanced presentation order, so always picking
one position scores 0.5), and **1/3 for ML identification**, because every shipped item
has Spanish as its Matrix Language and the constant answer "Spanish" earns the label
point on all of them (found 2026-09-01; pinned to the label distribution by
`tests/test_shipped_set.py`). Continuation and repair have no analysis-free strategy
that scores above 0. `csw-bench table` reports each cell as raw mean, above-chance mean
with a bootstrap interval, and scored n, with errored counts alongside.

## 5. Threats to validity

Seven, ordered by how much damage they do if real. Two cannot be fully mitigated and are
marked.

### 5.1 Translation-ability confound

A model might score well by translating internally rather than by representing a
switching constraint. **Mitigation:** include items where the MLF-licensed option is the
*worse* translation — where fidelity and licensing dissent. If scores hold on that subset,
translation is not doing the work.

### 5.2 Surface-frequency confound

In a minimal pair, the violating member may simply be rarer in training text, so a plain
language model picks correctly without representing anything. This is the most serious
threat to the central claim, because it offers a complete alternative explanation for a
good score. **Mitigation:** frequency-match pair members where possible, and build a
subset where MLF and corpus frequency dissent. Report that subset separately.

### 5.3 ML assignment is contested within the theory — **UNMITIGABLE**

The Matrix Language is identified by the morpheme-order and system-morpheme criteria, and
@macswan1999minimalist argues that identification is circular: the criteria defining the
ML are the same ones used to detect violations of it. We cannot settle a live theoretical
dispute inside a benchmark. **Bound, not fixed:** restrict items to cases where the
literature converges on the ML, exclude contested cases, and report the size of the
excluded set. A reader who rejects MLF's ML criterion should read this benchmark as
measuring consistency with a specific theory rather than with code-switching competence
as such — and that framing is stated in `README.md` rather than buried here.

### 5.4 Single-pair design — **UNMITIGABLE**

Spanish and English share SVO order, Latin script, and heavy cognate vocabulary, so
surface overlap is an alternative explanation for good scores and there is no
typologically distant contrast case to rule it out. **Bound:** the dissent subset in §5.2.
Full treatment in `limitations.md`.

### 5.5 Prompt sensitivity

Scores may reflect prompt phrasing rather than competence. **Mitigation:** Phase 3
requires two paraphrased templates per task with the delta reported. A large delta is
itself a finding and gets reported as one rather than smoothed away by picking the better
template.

### 5.6 Annotator pool is not naive

Whoever builds items knows the theory, so gold labels may encode theoretical commitment
rather than speaker intuition. **Original mitigation:** Phase 2 human validators, briefed
on nothing beyond the raw sentences. Not done — no human validators were recruited (see
`docs/journal.md`, "no external/human-dependent steps"). **Actual mitigation, weaker:**
the Phase 2 blind-review pass gave an independent AI reviewer only the bare prompts, with
no mention of MLF, the taxonomy, or the intended violation type, and it reached 96.7%
agreement with the gold labels on that basis alone — evidence the labels are not purely
an artifact of the item-builder's own framing, since a reviewer told nothing about the
framing still converged on them. This is not what the original mitigation would have
shown (an unbriefed *human's* language intuition, independent of any model's), so treat
it as suggestive, not as closing the threat. See `docs/limitations.md`.

### 5.7 Provider data retention — an operational constraint, not a threat

Recorded here because it binds Phase 3 and is easy to violate by default.

TalkBank's terms forbid uploading their data to third-party LLM systems unless
non-retention is explicitly selected. Attested items quote corpus material, and the
harness sends items to model providers. **Therefore every provider account used for a run
must have zero data retention enabled, and which setting was active becomes a recorded
run detail** alongside cost and token counts.

This lands on *evaluation*, not only on `matriz`'s fine-tuning, which is where the earlier
analysis had put it. A default-configured API key silently violates the corpus terms.

> **Amended 2026-08-17 — moot for a run that is actually local, which is now enforced and
> recorded rather than assumed.** Phase 3 runs exclusively against a local Ollama server
> (`docs/journal.md`, "Phase 3 pivot: local models"). The first version of this amendment
> claimed item text "cannot" reach a third party "regardless" of settings; that was wrong
> and a self-review caught it before commit — bare `ollama.Client()` resolves its host
> from an `OLLAMA_HOST` environment variable and would attach `OLLAMA_API_KEY` if set, and
> Ollama's own `:cloud`-tagged models (e.g. `kimi-k2.6:cloud`) proxy to a hosted API
> despite appearing in a local `ollama list`. `OllamaProvider` now pins its host
> explicitly and rejects `:cloud` model tags, and the resolved host is recorded on
> `RunConfig.provider_host` — so "this run stayed local" is an enforced, auditable
> property of the run, not an assumption about the caller's environment. The reasoning
> stays here rather than getting deleted for two further reasons: `RunConfig.zero_retention`
> and its `_guard_retention` check in `runner.py` still exist and still gate attested items
> (there are none in the pilot yet, so the guard has never actually fired), and a future
> reintroduction of a cloud provider — for comparison, say — would make this section
> load-bearing again immediately. Treat "local-only" as the current, enforced operating
> mode, not a permanent deletion of the cloud-provider code path's constraints.

### 5.8 Constructed-item circularity

Items constructed *from* MLF predictions, then used to test conformity *to* MLF, risk
circularity. This is weaker than it first appears — the predictions are independently
motivated by corpus data that long predates this benchmark — but it is why attested items
are primary, constructed items require a recorded derivation, and headline results are
reported with the attested-only subset alongside.

### 5.9 The EL-island escape hatch confounds `constrained_continuation` for T1/T3

Found during Phase 4's blind-review sample (`docs/journal.md`, "Phase 4 blind review"),
not anticipated when the task type was designed. `score_constrained_continuation`
compares a response against exactly two recorded strings — the intended licensed
continuation and the intended violating one — and scores 0, "matched no recorded
licensed form," for anything else. But a T1 or T3 continuation item's *specific* licensed
form is only one of several MLF-licensed ways to continue the prompt: a fully-formed EL
island (a complete, internally well-formed English constituent, itself licensed under the
EL Island Trigger Hypothesis) is *also* available at exactly the point these items probe,
and it is a structurally different construction from the single-morpheme-mixed NP (an
EL-sourced determiner attached to an ML-sourced noun) the item is built to force.

The blind-review sample shows this is not a rare edge case. All 30 of the sample's
`constrained_continuation` disagreements were inspected by hand; zero reproduced the
item's actual violating string, and all 30 resolved into either (a) abandoning further
code-switching entirely after the prompt, or (b) continuing to switch elsewhere in the
sentence while still producing a fully English, fully-islanded object NP. Independent
bilingual-competent responders reached for the island escape as their *default*
completion strategy, not an occasional dodge.

This is distinct from the already-closed monolingual-output hole (§4's anti-hedging rule
2): these responses are genuinely code-switched and genuinely MLF-licensed, just via a
different mechanism than the one under test. A real model that competently produces a
licensed island continuation would score identically to one that failed outright —
meaning a low `constrained_continuation` score for T1/T3 cells cannot currently
distinguish "the model doesn't represent the constraint" from "the model represents it
fine and chose the other licensed option." **Not mitigated in the Phase 4 item set as
shipped** — closing it means either constraining the prompt further (supplying enough of
the sentence that an island continuation is no longer syntactically available) or scoring
a detected island continuation as a distinct third outcome rather than folding it into
"0, no match." Both are real engineering, out of scope for what Phase 4 could absorb in
this pass. Treat every T1/T3 `constrained_continuation` score in the results table as
read through this confound until it's closed. `limitations.md` carries this as a
first-class threat, not a footnote.

## 6. What a null result looks like downstream, and why it is still publishable

Written now, before any data exists, so it cannot be retrofitted to whatever we find.

**The downstream experiment.** `matriz` fine-tunes on some violation types and holds
others out, then evaluates here. The hypothesis is that MLF constraints are learnable as
*constraints* — that training on, e.g., T1 and T3 improves held-out T5. (Originally framed
against four types, T1–T3 training against held-out T5; the taxonomy shipped three types,
T1/T3/T5, after T2 was dropped in Phase 1 — see `taxonomy.md` § "T2 dropped." The
experimental logic is unchanged, just over a smaller type set.)

**The null result.** No transfer. Held-out violation types show no improvement while
trained types improve substantially.

**Why that is publishable.** It is a clean negative answer to a sharp question: the
models learned the items, not the constraint. That is a specific claim about
representation, not a failed experiment, and it is only available because the taxonomy is
mutually exclusive and the held-out split is principled. A fuzzy taxonomy would have made
the same result uninterpretable — you could not tell whether transfer failed or the split
leaked. The rigor in Phase 1 is what converts a null result from an embarrassment into a
finding.

**The genuinely bad outcome** is neither of those. It is **ceiling effects**: if frontier
models score above roughly 90% on the pilot, the benchmark cannot discriminate and the
downstream experiment has no headroom to measure. That is a design failure rather than a
finding, and Phase 2's pilot exists partly to detect it early. If it happens, the response
is to raise item difficulty — not to publish a benchmark everything passes.
## Phase 1 completion conditions

- [x] Every task type traces to a named MLF prediction with a citation — §2
- [x] The rubric assigns partial credit without rewarding hedging — §4, three-part
      anti-hedging rule
- [x] At least three threats to validity named, including one that cannot be fully
      mitigated — §5, seven named, two unmitigable
- [x] Taxonomy has at least three mutually exclusive types, each with a stated diagnostic
      — three types (T1, T3, T5), ordering stress-tested across twenty-six cases in two
      rounds. **`docs/charter.md`'s four-type floor amended, 2026-08-16** — see `journal.md` for
      the reasoning; T2 and T4 both considered and dropped/folded on populability grounds,
      not four types trimmed for convenience. C8 and C9 resolved (C8 → T5, C9 → T1).

### Blocking before Phase 2

- [ ] Page-verify every `[VERIFY: page]` citation against the physical source — work-level
      verification done for all five theoretical citations (2026-08-16); page-level
      access to @myersscotton1993duelling and @myersscotton2002contact remains blocked
      (login-gated / paywalled). Top-priority open item: whether the SMP as literally
      worded covers early/bridge system morphemes or only outsiders — see `taxonomy.md`.
- [x] Resolve T4 — folded into T1
- [x] Resolve T2 — dropped; MOP survives only as an ML-identification criterion, not a
      held-out violation type; taxonomy ships three types (T1, T3, T5)
- [x] Test the first-match ordering against ten ambiguous cases —
      `ordering-stress-test.md`; found and fixed a T2 scope hole
- [x] Expand the stress test to twenty cases; resolve C8 and C9 at reasoning council —
      `ordering-stress-test.md`, `council-c8-c9.md`; C9's council verdict was later
      superseded once T1 widened, see `ordering-stress-test-v2.md` and `taxonomy.md`
- [x] Add stress cases for late bridge/outsider morphemes and re-run all cases —
      `ordering-stress-test-v2.md`, 26 cases, C21–C26 added
- [x] **Verify corpus licensing — contested, resolved by policy rather than by asking.**
      `corpora.md`; Bangor Miami's license is contested between two TalkBank pages
      (CC BY-NC-SA 3.0 vs. GPL v3). No depositor contact is being pursued for this
      project (`journal.md`); operating permanently under the union of both readings'
      obligations. Spanish in Texas read (CC BY-NC-ND 4.0, dropped as an item source);
      LinCE checked (no license stated anywhere, blocked).
- [x] **Decide the `matriz` non-commercial question** (`corpora.md` §4.3) — decided
      permanently: non-commercial reading, no depositor email pending
- [x] Update `LICENSE` and `README.md` for dual licensing — both disclose the license
      conflict and the union-compliance policy explicitly
- [x] **Confirm Bangor Miami transcript access — confirmed blocked, not pursued.**
      Genuine login gate (`sla.talkbank.org` browser requires an account); no attested
      items will be built from raw transcripts. Attested items instead drawn from the
      code-switching literature per `docs/charter.md`'s provenance rules, which name both
      sources as primary; see `limitations.md` for the resulting provenance-mix cost.
- [x] **Phase 2/4 human-validation gates — replaced with documented AI-substitute
      validation.** No human raters recruited; see the amendment recorded directly in
      `docs/charter.md` and the first-class threat recorded in `limitations.md`.
- [x] Fix the edit-distance threshold for repair minimality — 0.7, calibrated 2026-08-24
      from the pilot's own repair items; see §4 "Known weaknesses" above for the method,
      the length-sensitivity limitation, and the unreachable-minimality-branch finding
