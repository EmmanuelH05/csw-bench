# Limitations

> **Status: v1.0, 2026-09-11.** The bar from `docs/charter.md`: honest enough that a reviewer
> cannot find a hole you did not already name. Written to be read adversarially. The
> last section carries the numbers from the three full runs; nothing in this file waits
> on a run.

## What this does not measure

**Not code-switching competence in general — consistency with one specific theory of
it.** A model that scores well here represents MLF's predictions about Spanish/English
intrasentential switching. A model that scores poorly might fail to represent *any*
switching constraint, or might represent a *different*, equally defensible theory of
switching that happens to make different predictions on these items (§5.3's ML-assignment
dispute is exactly this kind of disagreement). Scoring low is evidence against
MLF-consistency, not evidence of "can't code-switch."

**Not translation ability, and not fluency in either language alone.** No item can be
solved by translating well or by being a strong monolingual Spanish or English model —
every item requires reasoning about the mixed-language boundary itself. But this repo has
not run the dedicated translation-confound check design.md §5.1 calls for (items where
the MLF-licensed answer is deliberately the *worse* translation), so this claim is a
design intention, not yet a verified property of the shipped item set.

**Not generation-time preference under natural sampling.** Every item uses `temperature=0`
and a fixed seed (`docs/design.md`, Phase 3). Whether a model's *typical* sampled output at
realistic decoding settings matches its zero-temperature best guess is a different,
unasked question.

**Not whether a model can produce fluent, natural-sounding code-switched text.** The
rubric scores whether an answer is MLF-licensed, not whether it reads naturally to a
bilingual speaker beyond that. A stilted but MLF-compliant answer and a natural,
MLF-compliant answer score identically.

**Not multi-clause or discourse-level switching.** Every item is a single clause. MLF
itself, and code-switching more broadly, has things to say about switching at the
clause boundary and across turns; none of that is in scope here.

**Not any language pair besides Spanish/English**, and not (per §"Single-pair design"
below) cleanly separable from the specific typological overlap between these two
languages. A model's score here says nothing calibrated about its behavior on, say,
Mandarin/English or Arabic/French switching.

**Not whether the *taxonomy's coverage* is complete.** Three violation types are tested
(T1, T3, T5); at least two real, frequently-discussed contact phenomena are explicitly
out of scope by the taxonomy's own design (missing free-standing ML system morphemes,
agreement-value failure on an EL noun — `taxonomy.md`, "Documented out-of-scope cases").
A model could produce either of those failure modes constantly and this benchmark would
never detect it.

**Not construct-validity beyond the pilot's independent-review sample.** 96.7% agreement
was measured on 30 hand-built items and 100%/100%/100%/0% (raw) on a 120-item stratified
sample of the 372 items added in Phase 4 — not on all 402. See "No human validation"
below and `docs/journal.md`, "Phase 4 blind review," for exactly what was and wasn't
covered.

## Known item-set defects at v1.0

Found 2026-09-01 while building the results tooling, after the blind-review sample and
the pilot runs had already been measured against these items. Deliberately shipped as-is
rather than fixed: repairing them now would disconnect every committed number from the
data it describes and would ship an item set nobody has reviewed. Each is a v1.1
candidate. Full account in `docs/journal.md`, 2026-09-01.

**The 372 Phase 4 items carry no Spanish diacritics.** 0/372 contain any accented
character, against 18/30 pilot items: "Compre el libro ayer", "Perdi el documento",
"esta manana". The generator's vocabulary tables are ASCII. Scoring is unaffected
because `textnorm.normalize` strips diacritics before every comparison, so a model that
answers with correct accents still matches. The stimulus is affected: "compre" is a
present subjunctive, not the preterite "compré", and "manana" is not a word. A model was
shown non-standard Spanish on every Phase 4 item and standard Spanish on every pilot
item, which is both a confound and an inconsistency inside one item set. A model that
"corrects" the orthography in its answer is not penalized; a model whose parse of the
frame is disturbed by it is, indistinguishably from a real MLF error.

**Every item has Spanish as its Matrix Language.** All 402, including all 100
`ml_identification` items. The label point of that task (1 of 3) is earned by the
constant answer "Spanish"; it has no discriminative power on this set, and only the two
evidence points do. Reported through the chance floor (1/3 for this task, `docs/design.md`
§4) so the above-chance column says so, rather than by adding English-ML items that have
been through no review. The imbalance follows from restricting items to cases where the
literature converges on the ML, and Spanish-frame/English-content is the convergent
direction for this pair -- see "ML assignment is contested" below.

**The 100 `constrained_continuation` items render to 24 distinct prompts.** 11 over
34 T1 items, 14 over 33 T3, 4 over 33 T5. The stimulus for this task is the prompt
alone, and the Phase 4 generator cycled a short prompt list against a long gold-string
list, so an item's identity lives in a gold string the model never sees. At temperature 0
one prompt gets one response, served from cache to every sibling: each full run's 100
continuation records are 24 responses, a response can match at most one sibling's gold
string, and the best possible score on this task is 24/100. The results table's n for
continuation cells counts records, not independent observations; `docs/results.md`
lists the affected cells under the table. Found 2026-09-08 from a cache hit on a
never-run item (`docs/journal.md`).

**`constrained_continuation` is scored as exact-string coincidence.** The scorer credits
one of two recorded strings per item and scores everything else 0. The gold string fixes
the noun, so a response producing the licensed construction with a different noun ("un
coffee", "mi phone" from qwen3:30b on pilot T1 items) scores the same as a failure. The
rubric's "monolingual scores zero" rule is not implemented and cannot be implemented
literally, since all 34 T1 licensed continuations are monolingual Spanish. The EL-island
escape hatch (§ below) is the visible symptom of this; the mechanism is broader. The one
continuation number that survives it is the violation-production rate -- how often the
model produced the recorded MLF violation -- which `scripts/continuation_escape_hatch.py`
computes and the results entry reports alongside the cells.

## Threats to validity we could not fully mitigate

### No human validation — AI blind review substitutes for it, and that is a real degradation

The original design gated the pilot set on three bilingual humans scoring blind above
90%, and gated the full results on a human ceiling for model scores to be measured
against. Neither was done. Both gates were replaced with independent *blind* AI review —
a reviewer that never sees the gold label, run as a separate pass from item construction —
documented as a scope decision in `docs/journal.md` and amended directly into `docs/charter.md`.

This is not a like-for-like substitution and should not be read as one. The entire reason
a human gate existed is that a bilingual speaker catches errors a model might not, *because
their competence with the construct is not the thing being measured downstream* — a model
reviewer's blind spots are not independent of the blind spots the benchmark exists to
detect in the first place. An item that passes AI blind review because the reviewing model
shares a misconception with the models it will later score is a false positive this
project's original design was specifically built to catch, and cannot catch anymore.

The partial mitigations — blindness to the gold label, disagreement between independent
review passes logged rather than resolved into consensus, cross-model review where
feasible — bound the risk. They do not close it. Every quality claim this benchmark makes
about its own items should be read as "passed independent AI review," not "validated by
fluent bilingual judgment," and the difference between those two claims is exactly the gap
this section exists to name rather than blur.

**Phase 2 result, 2026-08-16.** The pilot's 30 items cleared the blind-review gate at
96.7% (29/30) construct-validity agreement — one genuine disagreement, logged in that
item's own `provenance.review_disagreement` rather than resolved by fiat (see
`docs/journal.md`). That number is real, but it is a measurement of whether one
independent AI reviewer's judgment matches the item author's, not of whether either
judgment matches a fluent human's. The review also surfaced a separate, useful fact: the
automated `score_ml_identification` scorer under-credits genuinely correct free-text
morphosyntactic reasoning because it matches evidence strings literally — already named
in `scoring.py`'s own docstring as a Phase 3 gap, now confirmed against real items rather
than only anticipated. That gap is about scoring precision, not item validity, and the
two should not be conflated when reading Phase 3+ results.

**The Phase 4 sample and the construction-time ceiling are no longer reproducible
(2026-09-01).** The 120-item blind-review answers were written to `/tmp` and were lost
before being committed. The agreement rates (judgment 30/30, ml_identification 30/30,
repair 30/30 after crediting spelling variants, continuation 0/30) and the ceiling
computed from the same answers (judgment 100%, repair 100%, ml_identification 33%,
continuation 0%) are historical figures citable from `docs/journal.md`, not numbers this
repository can regenerate. `scripts/compute_ceiling.py` and `scripts/score_phase4_review.py`
now read `data/review/phase4-blind-sample/` and fail loudly while it is empty. Until a
new blind pass is collected there, Phase 5's "every number reproducible from committed
code and data" holds for every model result and for nothing about the review sample.
The ceiling was already a weaker reference than the human ceiling the design called for
(see `docs/charter.md`, Phase 4 amendment); it is now also an unreproducible one.

A second, differently-scoped review pass (informed, not blind — given the taxonomy,
schema, and generator logic, not just the rendered prompt) found that the 96.7% figure
should be read with one more qualification: several items reused the same violating
string across task types, which makes the item set less mutually independent than a flat
pass-rate implies. Diversified in the version that shipped, but the original 96.7% was
measured before that fix, against a less independent set — see `docs/journal.md`, "Phase
2 — second review," for the full account, including the construction bugs (a
Spanish-preposition homograph collision in the T3 pattern, circular and
non-discriminating evidence citations in several `ml_identification` items) that pass
also caught and fixed.

### Item provenance skews constructed, not attested, more than the original design assumed

`docs/charter.md` names attested items — from corpora or the code-switching literature — as
primary, constructed items as secondary. Raw corpus access (Bangor Miami's `.cha`
transcripts) turned out to require an account this project did not create (see
`docs/journal.md`), so items attested against actual corpus tokens are not available; only
examples quoted and cited from published literature are. The practical effect is a higher
proportion of constructed items than the original design planned for, which sharpens the
existing circularity caveat in the provenance rules — constructed items are built *from*
MLF predictions and then used to test conformity *to* MLF — since there is less
attested-item counterweight than intended. Reported per-item in the `source` provenance
field regardless, so the actual attested/constructed ratio is always checkable rather than
asserted.

### ML assignment is contested within the theory itself

The Matrix Language is identified by the Morpheme Order and System Morpheme criteria —
and critics (notably MacSwan) argue that identification is circular, since the criteria
that define the ML are the same ones used to detect violations of it. We cannot resolve
a live theoretical dispute inside a benchmark. What we can do is bound it: restrict
items to cases where the code-switching literature converges on the ML, and report the
size of the excluded contested set as a statistic rather than hiding it.

At v1.0 that restriction is total: every item has a Spanish frame with English content,
the direction the Spanish/English literature converges on, and no item probes an
English-ML clause or a contested-ML clause. The "excluded contested set" is therefore
not a subset with a count; it is the entire other half of the design space. Two
consequences. A model's score here says nothing about whether it identifies an English
Matrix Language when Spanish is embedded, which is a live phenomenon in the same
communities. And the ML-identification task's label component is a constant on this
set (see "Known item-set defects"), so the task's evidence points carry the whole
construct.

### Single-pair design

The benchmark tests Spanish/English only. Those languages share SVO constituent order, a
Latin script, and a large cognate vocabulary, so a model can plausibly score well by
exploiting that overlap rather than by representing the Matrix Language Frame constraint.
A typologically distant second pair would have supplied the contrast case that separates
those two explanations. It is not here.

This is not fully mitigable within the design. The partial measure is a subset of items
where the MLF prediction and the shared-order heuristic dissent, scored and reported
separately — if a model's advantage evaporates on that subset, the overlap explanation is
doing the work. That subset is smaller than the main set and correspondingly noisier, so
it bounds the concern without closing it.

### Every attested item comes from one corpus

Licensing recon left exactly one usable source: the Bangor Miami Corpus. Spanish in Texas
is CC BY-NC-ND, which forbids redistributing derived items; LinCE states no license at all
and its Spanish/English POS split is Bangor Miami regardless.

The consequences are not merely logistical:

- **Speaker-population narrowness.** Bangor Miami is 84 bilinguals recorded in Miami
  between 2008 and 2011. Findings generalize to that community and that period. Miami
  Spanish is heavily Caribbean-influenced, and this variety-sensitivity is exactly what
  killed T2 as a violation type (see "The Morpheme Order Principle is not independently
  tested," below) — a construction obligatory in the standard grammar may be optional, or
  even reversed, for this specific population, which cuts directly against building an
  order-violation type on it. The exact national-origin composition of the 84 speakers
  remains unverified as of this Phase 1 pass (public corpus documentation gives age, sex,
  and recording length but not origin; available "on request" from the research team).
- **Register narrowness.** Informal recorded conversation only. No written, formal, or
  elicited registers.
- **Single point of failure.** If the corpus turns out to lack `%mor` morphological tiers,
  the system-versus-content distinction the entire taxonomy rests on has to be annotated by
  hand, and there is no second corpus to fall back to.

A benchmark whose attested items all derive from one community's speech should not be
described as measuring Spanish/English code-switching in general, and this document is
where that is said rather than left for a reviewer to notice.

### The 4-M outsider distinction is not tested

**Widening T1 did not fix this.** An earlier draft claimed it recovered most of the lost
coverage; that claim was retracted after round 2. Widening closes the late *bridge* gap
only. Late outsider morphemes remain untestable for the same reasons the dedicated type was
cut: an EL affix on an ML stem is unattestable, an EL affix on an EL stem is excluded by
T1's own diagnostic, and fused case forms are unsegmentable. The `system_morpheme_class`
field will contain no `late_outsider` values.

The taxonomy tests early and bridge system morphemes. It does not test outsider ones.

The cut type — EL late outsider system morphemes — was dropped in Phase 1 because English
inflectional morphology is too impoverished to supply probes: subject-verb agreement
reduces to third-person singular *-s*, structural case surfaces only on pronouns, and no
clean case could be constructed even hypothetically.

The cost is specific. The 4-M model's early-versus-outsider split is what makes MLF's
system-morpheme prediction *graded* rather than binary, and this benchmark does not test
that gradation. A model could in principle respect the early/outsider asymmetry, or
violate it, and csw-bench would not detect either. A language pair with richer agreement
morphology would test it; Spanish/English cannot.

### The Morpheme Order Principle is not independently tested

**T2 (ML constituent order violated) was dropped in Phase 1**, not merely narrowed. Two
independent surveys (`t2-variety-check.md`, a dialect-level probe inventory check;
`ordering-stress-test-v2.md`, a diagnostic-level re-run) and a further targeted search for
missed heritage/contact-specific probes all converged on the same result: no populable,
non-redundant class of EL-frame-order violations exists for this language pair and corpus.
Full reasoning in `taxonomy.md` § "T2 dropped."

The Morpheme Order Principle survives elsewhere in the design — it remains one of the two
criteria used to *identify* the Matrix Language before any violation type is applied — but
it is no longer an independently held-out violation type. `matriz` holds out from three
types (T1, T3, T5), not four. A model that has fully represented the MOP as a generative
constraint and one that has only memorized surface Spanish/English collocations cannot be
distinguished by this benchmark the way they could have been if a populable T2 had shipped.

This is a language-pair-specific finding, not a claim about MLF generally. Two of the
three convergent lines of evidence (the diagnostic re-run, and the broader heritage-syntax
convergence literature) are not specific to Bangor Miami's population, but the third
(the dialect-level survey) is calibrated to a Caribbean-influenced Miami sample whose
exact national-origin composition remains unverified — see `taxonomy.md` for what was and
was not checked before this decision was made.

### Missing ML system morphemes are not tested

The taxonomy catches an EL system morpheme intruding into an ML frame (T1) and an EL
content morpheme surfacing bare where the ML requires morphology on it (T5). It does not
catch the third case: an obligatory ML system morpheme that is simply **absent** —
omitted personal *a* (\*`Vi la teacher en la tienda`), an omitted obligatory preposition,
an omitted complementizer *que*. These are frequently discussed in the Spanish/English
contact literature, so this is not a rare edge case being defined away.

The gap is principled, not accidental: the System Morpheme Principle is a claim about
where a system morpheme is *sourced from*, and a morpheme that never surfaced has no
source to evaluate. Building a type to catch omission would test a different claim than
the one this benchmark is designed around. The alternative considered and rejected —
widening T5's morphology requirement — was rejected because it reopens a previously-fixed
false positive (`la table`, licensed). See `taxonomy.md` § "Resolved gap" for the full
reasoning.

A model that never omits obligatory ML morphemes and a model that omits them constantly
would score identically on this benchmark. That is a real detection gap, not a
theoretical one.

### The EL-island escape hatch confounds `constrained_continuation` for T1/T3

`constrained_continuation` items for T1 and T3 are built to force a narrow,
single-morpheme-mixed continuation — an EL-sourced determiner attached to an ML-sourced
noun, e.g. "the libros" instead of "los libros". But a fully-formed EL island (a
complete, internally well-formed English constituent — "a new laptop", with its own
English determiner) is *also* MLF-licensed at exactly the point these items probe, and it
is a structurally different construction from the one under test. `score_
constrained_continuation` only recognizes two recorded strings per item (the intended
licensed and violating forms) and scores everything else 0.

This was found, not assumed: in Phase 4's blind-review sample, all 30 sampled
`constrained_continuation` disagreements were inspected by hand, and every one resolved
into a fully-islanded or fully-monolingual continuation rather than a reproduction of the
item's actual violation. Independent bilingual-competent responders reached for the
island escape as their default completion strategy. A model that competently produces a
licensed island continuation instead of the specific recorded one scores identically to a
model that failed outright — so a low T1/T3 continuation score cannot currently
distinguish "doesn't represent the constraint" from "represents it fine, chose the other
licensed option." Full detail and the two response patterns found are in `docs/design.md`
§5.9 and `docs/journal.md`, "Phase 4 blind review." Not mitigated in the item set as
shipped; every T1/T3 continuation number in the results table should be read through this
confound.

### Others

None currently identified beyond the threats named above. This section stays open
rather than being deleted, so a future finding has a place to go without restructuring
the document.

## Construct-validity caveats

**Translation-ability and surface-frequency confounds are named, not closed.**
`docs/design.md` §5.1 and §5.2 identify both as live threats and specify a mitigation —
a subset of items where the MLF-licensed answer is deliberately the worse translation, or
where MLF and corpus frequency dissent — but that subset has not been built or run
separately from the main item set. Until it is, a model's score on any individual item
cannot be attributed with confidence to "represents the MLF constraint" versus "picked
the more fluent-sounding option" or "picked the higher-frequency option." The aggregate
score across 400+ items is a weaker but still meaningful signal (an MLF-blind strategy has
no reason to systematically track MLF-licensed forms across three structurally different
violation types), but the item-level attribution the dissent subset would have provided is
missing from this release.

**The EL-island escape hatch (§"The EL-island escape hatch" above) is a construct-validity
caveat specifically for `constrained_continuation`** on T1/T3 cells: a low score there
cannot currently be attributed to "doesn't represent the constraint" versus "represents it
fine, chose the other licensed construction." Repeated here because it is the single
largest known caveat on any individual task type's numbers.

## Statistical limitations

**Cell sizes.** 402 items across 3 violation types × 4 task types gives ~31-34 items per
cell (`csw-bench stats`) — enough for a bootstrap confidence interval to be meaningfully
narrower than the full [-1, +1] above-chance range, not enough to detect small
between-model differences within a single cell with tight confidence. Aggregating to the
task-type level (n≈100-134 per task, pooling across violation types) narrows intervals
further and is the more reliable comparison; per-cell numbers should be read as directional,
not decisive.

**No paired significance test between models.** `csw-bench report --compare` computes a
per-task point delta between two runs (built for the prompt-sensitivity check, §5.5), but
nothing in this repo tests whether a delta between two *different models'* scores is
larger than bootstrap noise would produce. A results table showing model A above model B
on some task is a descriptive ranking, not a tested claim of superiority, until that
comparison exists.

**The chance floors are set by the shipped set, not by the task in the abstract.** The
ML-identification floor is 1/3 because every shipped item's Matrix Language is Spanish;
on a balanced set it would be 1/6, and the above-chance numbers in `docs/results.md` are
not comparable to a future release that rebalances the labels without re-deriving the
floor (`tests/test_shipped_set.py` forces that re-derivation).

**Continuation cells have a quarter of the independent observations they show.** See
"Known item-set defects": 100 records, 24 distinct stimuli, one response per stimulus.
The bootstrap resamples records, so those intervals are narrower than the true
uncertainty by roughly a factor of two.

**Bootstrap CIs assume item-level independence.** Items sharing a template pattern
(`scripts/build_phase4_items.py`'s combinatorial generation) are not fully independent
draws — a model's tendency to succeed or fail on one instance of a pattern is correlated
with its tendency on other instances of the same pattern. The bootstrap resamples items,
not patterns, so reported CIs are likely somewhat narrower than the true uncertainty.

## Generality

This measures a specific construct against a specific theory on one language pair. It
does not license claims about bilingual speech in general, nor about any pair other than
Spanish/English — and given how typologically close that pair is, it especially does not
license claims about switching between structurally divergent languages.

## Numbers from the full runs

The section `docs/charter.md` and `scripts/finalize_phase4.py` call PENDING RUNS, filled from
`docs/results.md`, `runs/logs/prompt-sensitivity.txt`, and `runs/logs/escape-hatch.txt`
over the three `runs/full-*-a`.

- **Prompt sensitivity (2026-09-08, rescored 2026-09-10).** Template a vs b on the
  pilot, qwen3:30b, paired by item: no distinguishable delta on judgment (0.000
  [-0.667, +0.667]), continuation (0.000), or repair (+0.143 [+0.000, +0.429]);
  `ml_identification` 0.071 [+0.000, +0.214] lower under template b, one genuinely wrong
  answer. As first scored the drop was 0.286 [+0.071, +0.429], three quarters of it the
  scorer's claim anchor not recognising a claim phrased without "Matrix Language"
  (`docs/findings.md`); the anchor was revised and every run rescored. The headline runs
  use template a. A third template would find the next phrasing the anchor does not know.
- **Provider-error rates, full set.** qwen3:30b 0/402 on its final pass; the earlier
  passes' 25 errors were machine contention (`docs/journal.md`, 2026-09-10) and were
  retried from cache. gpt-oss:20b 77/402: judgment 10/102, continuation 19/100,
  `ml_identification` 42/100, repair 6/100; 75 are the 8192-token output budget exhausted
  before any content, 2 are an empty or unaccounted response. Excluded from every score,
  and not random: budget exhaustion selects the items the model reasoned longest about,
  so gpt-oss:20b's scored cells lean toward the items it found easy and its intervals
  are over that subset. deepseek-r1:32b 100/402: `ml_identification` 100/100 timed out
  at 300 s, the pilot's 100% pattern at full scale; 0 errors on the other three tasks.
  Its `ml_identification` cell is empty, not low, and the table shows it as a dash.
- **Violation-production rate.** 0.00 for all three models (0 of 281 scored
  continuations reproduce a recorded violation string); a lower bound, read with the
  samples in `docs/findings.md`. deepseek-r1:32b's 100 continuations are monolingual
  Spanish.
- **Evidence citation is never credited.** 0 of 158 scored `ml_identification` responses
  across the three full runs (deepseek-r1:32b scored none) matched a recorded evidence
  string, so under the v1.0 scorer the task's above-chance value cannot exceed zero for
  any model, and a negative value is the wrong-label rate and nothing more. Not a v1.0
  fix: the matcher is what the
  construction-time ceiling and the pilot were scored with, the evidence strings are part
  of the frozen items, and widening the matcher after reading two models' output is the
  circularity `docs/design.md` §5 names. The v1.1 shape is a claim-and-evidence extractor
  validated on held-out responses, not a wider regex.
