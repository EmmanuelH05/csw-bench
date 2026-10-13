# Findings

> **Status: v1.0, 2026-09-11.** Every finding below is backed by committed data or by a
> check recorded in `docs/journal.md`. The headline and error-pattern sections are read
> from `docs/results.md`, generated from the three full runs under `runs/full-*-a`.

What the observed error patterns suggest about model representations of code-switching.

## Headline result

Three models, 402 items, template a, scored by the v1.0 scorer after the 2026-09-10
claim-anchor revision (below). Pooled per-task rows of `docs/results.md`, which
`scripts/finalize_phase4.py` generates as `uv run csw-bench table runs/full-qwen3-30b-a
runs/full-gpt-oss-20b-a runs/full-deepseek-r1-32b-a`; above-chance units with 95%
percentile-bootstrap intervals. Pilot scale (30 items) is in `docs/results-pilot.md` and
is not the headline.

- **Grammaticality judgment: all three above chance.** gpt-oss:20b +1.000
  [+1.000, +1.000] (n=92, 10 errored): every scored minimal pair resolved to the licensed
  member. deepseek-r1:32b +0.980 [+0.941, +1.000] (n=102), 101 of 102. qwen3:30b +0.686
  [+0.549, +0.824] (n=102).
- **Constrained continuation: none distinguishable from chance**, +0.000 for all three
  (n=100, 81, 100). Read this row through the escape hatch, not the score: no model
  produced a single recorded violation string either (next section).
- **ML identification: the two models that answered sit below the constant-label floor;
  the third has no scored items.** qwen3:30b -0.095 [-0.135, -0.060] (n=100); gpt-oss:20b
  -0.138 [-0.198, -0.086] (n=58, 42 errored); deepseek-r1:32b timed out on 100 of 100 at
  300 s, the pilot's pattern at full scale. Below zero here means the model named English
  as the Matrix Language, and nothing else: the evidence matcher credited 0 of the 158
  scored responses (`docs/limitations.md`, "Numbers from the full runs"), so under the
  v1.0 scorer the row cannot be positive for any model and measures the wrong-label rate.
- **Repair: all three above chance, in a wide spread.** gpt-oss:20b +0.787
  [+0.702, +0.872] (n=94); qwen3:30b +0.630 [+0.540, +0.720] (n=100); deepseek-r1:32b
  +0.310 [+0.220, +0.400] (n=100), almost all of it on T1 (next section).

gpt-oss:20b's intervals are over the items it answered. 77 of its 402 records are
provider errors (output budget exhausted before any content), concentrated in
`ml_identification` (42/100) and `constrained_continuation` (19/100), so its cells are
not the same sample as the other two models', and budget exhaustion selects the items
it reasoned longest about. deepseek-r1:32b's 100 errors are all `ml_identification`
timeouts; its other 302 records are clean.

## Error patterns by violation type

Per-violation above-chance means from the same three runs; the intervals are the
per-violation rows of `docs/results.md`.

**Errors cluster by violation type in every model, and T5 is in the cluster every time.**
T5 is the congruence-failure / bare-form type: an English content morpheme, here a bare
verb ("park el carro todos los dias en la oficina"), sitting in a Spanish frame without
the inflection the frame obligatorily supplies.

- Judgment: qwen3:30b T1 +1.000, T3 +0.706, T5 +0.353. deepseek-r1:32b T1 +1.000, T3
  +1.000, T5 +0.941 (its one miss is a T5 pair). gpt-oss:20b is at ceiling on all three.
- Repair: qwen3:30b T1 +0.879, T3 +0.788, T5 +0.235; gpt-oss:20b T1 +0.967, T3 +1.000,
  T5 +0.387; deepseek-r1:32b T1 +0.758, T3 +0.091, T5 +0.088. The first two models
  locate and minimally fix an intruding English article or a cut island far more often
  than they inflect a bare English verb. deepseek-r1:32b's T3 and T5 rows are a different
  failure, found by reading its zero-scored answers: 30 of its 33 T3 repairs drop the
  English island and translate ("Compró el regalo ayer" for "Compró the el gift ayer",
  gold "Compró the gift ayer"), and its T5 repairs substitute a native verb ("imprimió"
  for "print"). It reaches the gold on T1 (25/33) because deleting every English word
  coincides with the minimal repair when the only English word is the article. Its
  repair row therefore measures a normalisation strategy, not violation location. The
  same two escapes exist in the other models at lower rates: T3 repairs that drop the
  island, 30/33, 18/33, 6/33 for deepseek-r1:32b, qwen3:30b, gpt-oss:20b; T5 repairs
  that avoid the integrated loanword (the native-word substitution under "Items that
  turned out to be wrong", scored 0 by design), 20/34, 19/34, 15/31.
- ML identification: the wrong-label rate is 2/33, 3/34, 11/33 (T1, T3, T5) for
  qwen3:30b and 2/22, 4/15, 10/21 for gpt-oss:20b; deepseek-r1:32b has no scored items.
  All 21 T5 wrong-label responses cite the verb: the model reads the bare English verb as
  the head of the clause and concludes that English supplies the frame, against the
  Spanish articles, preposition, and constituent order it lists in the same answer. That
  is the specific MLF error the task exists to catch (the frame is set by system
  morphemes and order, not by the language of a content morpheme), and it is the same
  item type both models repair worst.
- Continuation: nothing to cluster. 0 of 281 scored continuations reproduced a recorded
  violation string in any model (violation-production rate 0.00,
  `scripts/continuation_escape_hatch.py`), and 0 reproduced the recorded licensed
  string. The unmatched mass is islands and monolingual completions, as the escape-hatch
  finding predicted; counts are under that finding below. deepseek-r1:32b's 100
  continuations are all monolingual Spanish. Items sharing a prompt share one response
  (`docs/limitations.md`), so those counts are over records, not independent responses.

**What the pattern implies.** A model pattern-matching surface Spanglish would fail
uniformly or at random across types. qwen3:30b and gpt-oss:20b are above chance on T1
and T3 in judgment and repair, where the violation is a misplaced *system* morpheme or a
broken island. On T5, where the violation is a *content* morpheme lacking ML inflection,
qwen3:30b drops in judgment and both drop in repair and ML identification. gpt-oss:20b
still judges T5 pairs at ceiling: it recognises the bare form as wrong when the licensed
member is beside it, yet reads the same bare verb as the frame-setter when asked to
analyse the utterance alone. The most economical reading is that both models represent
"English function words do not go in Spanish slots" and neither reliably represents
"English content words in a Spanish frame take Spanish inflection": the 4-M split the
taxonomy is built on (`docs/taxonomy.md`) is visible in the error profile.

deepseek-r1:32b is a third profile: judgment at ceiling on every type, and then, in
every production task, a retreat to monolingual Spanish (100 of 100 continuations, 30 of
33 T3 repairs). That is the behaviour the README's first paragraph names, treating mixed
input as degraded Spanish to be normalised, and it is invisible to the judgment task and
to any aggregate score. A benchmark with only the judgment task would rank it first. The
alternative reading of T5, that the bare-verb construction is common enough in bilingual
speech for a model to treat it as acceptable, is a question about the T5 items rather
than the models, and three model families do not settle it.

## Unexpected findings

`docs/charter.md` Phase 4 requires at least one finding that was not expected, reported as
found. Recorded here with the date noticed and how it was checked for realness —
including any check that killed a candidate finding.

### The EL-island escape hatch (2026-08-24)

**What was expected.** The Phase 4 blind-review sample (120 of 372 new items,
`docs/journal.md`) was built to measure whether the new items' gold labels hold up under
independent judgment, the same check Phase 2 ran on the pilot. The expectation, based on
Phase 2's 96.7% construct-validity agreement, was a similarly high number across all four
task types.

**What was found instead.** `grammaticality_judgment` and `ml_identification` held at
100% (30/30 each). `repair` was 26/30 raw, but all four "failures" were attested
alternate spellings of the same correct loanword (chequear/checkear, and similar) — 30/30
once credited. `constrained_continuation` was 0/30 by exact string match, and that number
looked at first like a serious item-quality problem in the new T1/T3/T5 continuation
cells specifically.

**How it was checked for realness, rather than accepted at face value.** A 0% score is
exactly the kind of number a project with this one's stated priors should be suspicious
of — it is either a real, severe defect, or a measurement artifact, and the difference
matters. Two checks, in order:

1. **Did any of the 30 disagreements reproduce the item's actual violating string?**
   Checked programmatically against every item's `violating_continuations` field: zero
   matches. If reviewers had been reconstructing the intended ungrammatical form as
   natural, that would mean the gold labels were backwards or the construct itself
   doesn't hold — a genuine crisis. They were not doing that.
2. **What were they doing instead?** Read by hand, all 30. Two patterns, both already
   named in `docs/design.md` §5.9: abandoning further code-switching entirely after the
   Spanish-framing prompt (18/30), or continuing to switch elsewhere in the sentence
   while still producing a fully English, fully-islanded object NP (12/30). Both are
   well-formed EL islands under MLF's own licensing — a legitimate, always-available
   alternative to the single-morpheme-mixed construction the item targets, not an error.

**The actual finding.** Not "the new items are broken" (the candidate finding this check
killed) but **the `constrained_continuation` task design has an unmodeled escape hatch**:
an open-ended "complete this utterance" prompt does not force the narrow contrast T1/T3
items are built to test, because a fully-formed EL island is always a licensed
alternative completion, and independent bilingual-competent responders reached for it as
their *default* strategy rather than an occasional dodge. `score_constrained_continuation`
cannot currently tell "produced a licensed island instead" apart from "failed outright" —
both score 0. This means every T1/T3 `constrained_continuation` cell in the results table
below should be read as a lower bound confounded by this effect, not a clean measure of
whether the model represents the constraint. Full mechanism in `docs/design.md` §5.9 and
`docs/limitations.md`.

**Why this is worth reporting as a finding rather than quietly noted as a limitation.**
It is falsifiable and it changes what a low continuation score means for the headline
claim: a model that scores near-zero on T1/T3 continuation could be failing to represent
the Morpheme Order/System Morpheme constraints, *or* could be a fluent enough
code-switcher to reliably reach for the licensed alternative — two very different
findings about model competence that the current scorer cannot distinguish. Closing it
(constraining the prompt further, or scoring a detected island as a distinct third
outcome) is real engineering, out of scope for this pass, and named as open work rather
than silently deferred.

**At full scale (2026-09-10, third run 2026-09-11).** The full runs behave as the review
sample did. `scripts/continuation_escape_hatch.py` over the three `runs/full-*-a`: 0 of
281 scored continuations reproduce a recorded violation and 0 reproduce a recorded
licensed string. The rest, qwen3:30b, gpt-oss:20b, then deepseek-r1:32b, are
English-only islands (24, 38, 0), mixed islands (10, 10, 0), completions with no
English function word (25, 17, 100), other unmatched (29, 16, 0), and declines
(12, 0, 0). Read samples: "the new iphone", "the check por favor", "un coffee", "work
late", "me levanto early y me preparo para el dia"; deepseek-r1:32b's hundred are all
monolingual Spanish ("un libro interesante en la libreria", "me levanto temprano"), the
abandon-switching pattern the review sample showed in 18 of 30. Every one is licensed
under MLF and none is the construction the item probes. The 0.00 violation-production
rate is a lower bound, since a violation built on a different word lands in an unmatched
bucket, but the samples read as islands and monolingual retreats, not as disguised
violations.

### The ML-identification scorer penalized a natural opening sentence (2026-08-27)

**What was expected.** Running the Phase 3 pilot against `gpt-oss:20b` (the first real
model, not a synthetic fixture, to exercise `score_ml_identification` at scale) was
expected to surface prompt-sensitivity or verbosity issues, not a scorer defect — the
scorer had passing unit tests and had already scored the Phase 2 pilot and the Phase 4
ceiling sample without incident.

**What was found instead.** A code-review pass run in parallel with the pilot (prompted
to look for exactly this kind of thing before Phase 4 results were computed at scale)
found that `score_ml_identification` compared the *first* occurrence of each language
name in the raw response text. A response opening with a natural framing sentence —
"This utterance mixes English and Spanish elements. The Matrix Language is Spanish
because..." — names "English" before "Spanish" purely as an artifact of that framing,
and scored 0 despite citing the correct label and both required-evidence strings
verbatim.

**How it was checked for realness.** Reproduced directly against the real scorer
(`Score(points=0, reason='wrong or unclear Matrix Language')` for the exact sentence
above, before the fix) rather than trusted from the review agent's description alone.
Confirmed the fix doesn't just paper over the false negative by checking the genuine
wrong-answer case still scores 0: "Some say Spanish, but I think English is the Matrix
Language" (mentions the correct language, then commits to the wrong one) correctly stays
at 0 points after the fix, which compares each name's *last* mention rather than its
first.

**Why this matters beyond one scorer function.** This is the second time in Phase
3/4 that actually running the harness against real model output — not just unit tests
against hand-picked fixtures — surfaced a defect that would have silently corrupted
results (the first was the request-hang and provider-error-isolation gaps, `docs/journal.md`).
Both were invisible to code review of the scorer/runner in isolation and only became
visible against real, unscripted text. Any future scoring change should be spot-checked
against real model output before being trusted, not just against the existing fixture
suite — the fixtures themselves can share the same blind spot as the code they're
testing (both were written by the same process, at the same time, with the same
assumption about what "the answer" looks like in text).

### deepseek-r1:32b fails every ml_identification prompt specifically (2026-08-27)

**What was expected.** Having already run `gpt-oss:20b` (23% overall provider-error
rate, concentrated in `constrained_continuation`) and `qwen3:30b` (0% provider errors),
the expectation for the third model was some baseline error rate from reasoning-budget
exhaustion, not a pattern isolated to one specific task type.

**What was found instead.** All 7 of 7 `ml_identification` items in the pilot set
(csw-es-en-0007, -0008, -0016, -0017, -0018, -0026, -0027 — 2 T1, 3 T3, 2 T5) timed out
at the full 300s request budget (`providers.py`'s `REQUEST_TIMEOUT_SECONDS`), recorded as
provider errors rather than scores: a 100% failure rate for the task type, confirmed only
once the run finished completely. Every `grammaticality_judgment` (9/9), every
`constrained_continuation` (7/7), and every `repair` (7/7) item completed normally with a
real score, most in under 90 seconds.

**How it was checked for realness.** One of the seven (csw-es-en-0008) coincided with a
self-inflicted resource-contention mistake this session (a competing request to
`gpt-oss:20b` evicted `deepseek-r1:32b` from memory mid-run, `docs/journal.md`), so that
one specific timeout is attributable to the mistake, not the model. The other six
(-0007, -0016, -0017, -0018, -0026, -0027) occurred with no competing request running and
no memory pressure — checked directly via `ps` at the time, and confirmed after the fact
by `csw-bench report` showing 0 completed and 7 errored for the task with no other task
type affected — and span all three violation types (T1, T3, T5), ruling out an
item-specific or violation-type-specific artifact. A 100% failure rate isolated to
exactly one task type, persisting across unrelated items, a model reload, and every
violation type, is a real pattern rather than noise.

**The likely mechanism, stated as a hypothesis, not confirmed.** `ml_identification`'s
prompt (`prompts.py`) is structurally different from the other three task types: it asks
the model to *analyze and justify*, not just select or reproduce a target string. For a
reasoning model, "which language, and why" is exactly the kind of open-ended analytical
question that can trigger unbounded chain-of-thought — the same class of problem
`docs/journal.md`'s "Phase 3 pivot" and "A hung request" entries already document for
other reasoning models on other tasks, but concentrated here with unusual severity. This
is a hypothesis about *why*, offered for a future investigation — not verified by
inspecting the model's actual (absent) output, since a timeout produces no output to
inspect.

**Why this is reportable rather than just an error count.** A model that cannot complete
morphosyntactic-analysis prompts within a generous budget is exhibiting a real, specific
limitation distinct from "doesn't know Spanish/English code-switching" — it is a
task-format brittleness that this benchmark's four-task design is well-positioned to
isolate, precisely because the other three tasks on the same model, over the same
violation types, complete normally. Reported as a model-specific reliability finding,
not folded silently into an aggregate error rate.

**Held at full scale (2026-09-11).** `runs/full-deepseek-r1-32b-a`: 100 of 100
`ml_identification` items timed out at 300 s, across two attempts on separate days, on a
machine with nothing else loaded; 0 errors on the other 302 records. The cell is empty,
not low, and `docs/results.md` shows it as a dash. gpt-oss:20b's 42 budget-exhaustion
errors on the same task are the same failure measured in tokens rather than seconds: a
reasoning model that spends its whole budget thinking is indistinguishable from a hung
one, and the harness records both as provider errors rather than as answers. The
hypothesis above stands unverified for the same reason it did: a timeout leaves nothing
to read.

### The ML-identification label point is free on this item set (2026-09-01)

**What was expected.** `CHANCE_FLOOR` treated ML identification as floorless: a model
with no analysis earns nothing.

**What was found instead.** Every one of the 402 items, including all 100
`ml_identification` items, has Spanish as its Matrix Language. The constant answer
"Spanish" earns the label point (1 of 3) on every item. Found while writing the
shipped-set contract tests, by counting, not by running anything.

**How it was checked for realness.** Against the committed pilot runs: qwen3:30b's
`ml_identification` mean of exactly 0.333 with a degenerate [0.333, 0.333] interval is
seven items at label-only credit, i.e. seven answers that were "Spanish" plus evidence the
substring matcher did not recognise; that is the floor, and it now reads +0.00 above
chance. gpt-oss:20b's 0.267 now reads -0.10, below the floor, because it named the wrong
language on at least one item. The floor is set to 1/3 and pinned to the shipped label
distribution by `tests/test_shipped_set.py`.

**Why this matters.** The label component carries no information on this set; the two
evidence points carry the whole construct, and they are the part the scorer is weakest
at (substring matching of `required_evidence`). Any `ml_identification` number in the
results table is, in effect, an evidence-citation score with a constant added.

### Exact-string continuation scoring zeroes the construction it exists to detect (2026-09-01)

**What was expected.** The EL-island escape hatch above: responders reaching for a fully
English island instead of the single-morpheme-mixed NP the item probes.

**What was found instead.** `scripts/continuation_escape_hatch.py`, run over the three
pilot runs already on disk, buckets every continuation by what it did. On T1 items,
qwen3:30b completed "Ayer compré" with **"un coffee"** and "Tengo" with **"mi phone"**:
a Spanish determiner attached to an English noun, which is precisely the licensed
pattern T1 items are built around, and scored 0, "matched no recorded licensed form",
because the gold string is "las revistas para la clase" -- it fixes the noun, not the
construction. deepseek-r1:32b completed 7 of 7 continuation items in monolingual Spanish
("el libro", "me levanto temprano"), also 0. gpt-oss:20b's three scored continuations were two
English islands and one Spanish clause closed by an English discourse tag ("...que me
ayude con esto, you know?"). Across the three models, 0 of 17 scored continuations
reproduced the item's recorded violation.

**How it was checked for realness.** By reading the records, not the scores: the
classifier prints the text after the model's last echo of the prompt, and the strings
above are verbatim from `runs/pilot-qwen3-30b-a/records.jsonl` and
`runs/pilot-deepseek-r1-32b-a/records.jsonl`. The rubric contradiction is checked
against the items: all 34 T1 `licensed_continuations` are monolingual Spanish, so the
rubric row "monolingual scores zero" (`design.md` §4) cannot be implemented without
zeroing the gold answers, and it is not implemented -- monolingual output scores 0 only
by failing to match.

**The actual finding.** As scored, `constrained_continuation` measures coincidence with
one of two strings. The escape hatch is the visible symptom; a model producing the
target construction with a different noun is the cleaner demonstration, because it
cannot be read as the model dodging anything. The number to read from continuation cells
is the **violation-production rate**: how often the model produced the recorded MLF
violation. It is a lower bound, for the same reason in mirror image: the exact match
also misses a violation built on a different lexical item. qwen3:30b's "work late" for
"Todos los días yo" (csw-es-en-0024) is a bare English verb in a Spanish first-person
frame -- the T5 construction, with a different verb from the recorded "text a mis
amigos" -- and counts as neither licensed nor violating; it is also exactly the
construction that item's logged pilot disagreement is about. A low score with a zero
violation rate is consistent with full competence; a nonzero violation rate is the only
continuation evidence of an unrepresented constraint, and reading the unmatched
samples by hand is the only way to find the violations the string match missed.
Not fixed in the scorer: crediting any determiner-plus-noun match means re-specifying
what every continuation item licenses, which is item design for v1.1, not a scoring
patch for v1.0.

### The prompt-sensitivity check measured the scorer, not the model (2026-09-08)

**What was expected.** `design.md` §5.5: a large score delta between the two paraphrased
templates means the benchmark measures phrasing rather than competence, and gets
reported as such.

**What was found instead.** Template b against the pilot on qwen3:30b, paired by item:
no distinguishable delta on judgment, continuation, or repair; a 0.286 above-chance drop
on `ml_identification` with a 95% interval of [+0.071, +0.429]. Read response by
response, three of the four template-b answers scored as naming the wrong Matrix Language
conclude that Spanish is the frame (csw-es-en-0008, -0026, -0027). They are zeroed
because template b never says "Matrix Language", so the scorer's claim anchor finds
nothing and falls back to whichever language name occurs last. All seven template-b
answers also paraphrase the prompt's "not from how many words each language contributes",
which the lexical-frequency regex matches, capping every one at the label point --
point-neutral here only because the evidence matcher credited nothing under either
template. One item, csw-es-en-0018, is a genuine wrong answer ("Final Answer: English").

**How it was checked for realness.** Each of the seven responses' final sentences was
read and each scorer mechanism was evaluated on it directly (`docs/journal.md`,
2026-09-08). The decomposition is arithmetic: 0.214 of the 0.286 is the three artifact
zeros; 0.071 is the one wrong label.

**The actual finding.** The 2026-08-27 anchoring fix encoded template a's vocabulary as
the definition of "the model made a claim", so the sensitivity check compares the
scorer's tolerance of paraphrase at least as much as the model's. Template a stays the
headline template and every full-set run uses it, so the results table is not affected.
**Resolved 2026-09-10.** The claim anchor now reads an explicit claim ("Spanish sets the
grammatical frame", "the Matrix Language is Spanish") before falling back to mention
position, and every committed run was rescored in one pass with `scripts/rescore_run.py`
(next section). The three artifact zeros are credited; csw-es-en-0018 stays 0; the
delta is now 0.071 [+0.000, +0.214], the one wrong answer. The negated-lexical-mention
half of the deferred fix was not made: it affects only template b's paraphrase of the
prompt, caps a response at the label point it earns anyway on this item set, and touches
no headline run.

### The claim anchor failed in both directions at full scale (2026-09-10)

**What was expected.** The 2026-08-27 anchor (the language name nearest the last "matrix
language" mention) had survived the pilot under template a and been falsified only under
template b's different vocabulary. The full runs use template a, so the ML-identification
row was expected to need no scorer attention beyond the known evidence-matcher gap.

**What was found instead.** Reading the 30 zero-scored qwen3:30b responses before
writing them up: 12 conclude Spanish, explicitly and repeatedly, in the sentence the
scorer zeroed them on. Its shape is "a classic case of Spanish as the Matrix Language
with English lexical items inserted", and the incidental "English" six characters after
the phrase beats the claimed "Spanish" eight characters before it. One record failed the
other way: csw-es-en-0354 says "English is the Matrix Language" eleven times and was
credited, because its closing table row reads "English matrix language | Spanish
embedded content" and "Spanish" is nearer. gpt-oss:20b showed the first shape three
times ("Matrix Language: Spanish. Why Spanish is the matrix language ...").

**How it was checked for realness.** Every record the revised rule moves was read in
full before the rule was written; the rule was then run over every committed run and
diffed record by record against the pre-revision scores: 13/402 qwen3:30b (12 up, 1
down), 3/402 gpt-oss:20b, 3/30 pilot template b, 1/30 pilot gpt-oss:20b, 0 elsewhere.
The moved set is exactly the hand-read set. Constructed sentences of both polarities,
including negations ("does not make English the Matrix Language") and the heading shape
that produced the false credit, are pinned in `tests/test_scoring.py`.

**The actual finding.** The revised rule reads the response's explicit claim first ("X
is / as / sets / supplies the Matrix Language", "the Matrix Language (in the utterance
...) is X", "the grammatical frame is X", a heading "Matrix Language: X") and takes the
last such claim; only a response that phrases no claim falls back to the nearest-name
heuristic, then to whole-text last mention. Effect on the headline row: qwen3:30b -0.150
to -0.095, gpt-oss:20b -0.164 to -0.138, both still below the floor, now for a reason
the responses support (the T5 English-verb error above). Two smaller artifacts were
counted and left: the hedge detector fires on "or it depends on the speaker" inside a
reasoning preamble that then commits to Spanish (csw-es-en-0242), and the
lexical-frequency detector fires on "the order is mostly Spanish" (csw-es-en-0102). Each
moves one record by one point and neither generalises to a rule worth writing against
one response.

**Why this is reported as a finding.** It is the fourth time reading real output has
overturned what the number said, and the first time a scorer artifact ran in a model's
favour. The nearest-name heuristic was itself the fix for the previous artifact, and each
fix encoded the phrasing that motivated it. The explicit-claim rule is more specific, not
more general, and a fifth phrasing will find its edge. Treat every `ml_identification`
number as the output of a string matcher whose recall has been checked on two models'
full output and no further.

### The blind-review sample was lost before it was committed (2026-09-01)

A process finding, reported because it changes what the ceiling numbers are. The 120
review answers behind the Phase 4 agreement rates and the construction-time ceiling were
written to `/tmp` by the scripts that scored them and never copied into the repository.
Both scripts now read `data/review/phase4-blind-sample/` and refuse to run while it is
empty. The figures quoted in `docs/journal.md` (2026-08-24) stand as recorded; they are
not reproducible from this repository, and `docs/limitations.md` says so where a reader
would look for the ceiling.

## Items that turned out to be wrong

Per the working-style rule: when a model's answer looks wrong but is arguably licensed,
that is a finding about the item, not the model. Those go here, flagged, rather than
being scored as model errors.

### T5 repair: native-word substitution as an escape from loanword integration (2026-08-27)

**What was found.** All three of `qwen3:30b`'s T5 repair attempts in the pilot
(csw-es-en-0028, -0029, -0030) scored 0 ("did not reach the gold repair"), but not
because the repairs were wrong — they replaced the bare EL verb with a *different,
grammatically correct native Spanish verb* instead of the loanword's morphologically
integrated form: "park" → "aparcar" (not "parquear"), "print" → "imprimió" (not
"printeó"), "chat" → "charlar" (not "chateó"). Every one of these is a real, standard
Spanish word, correctly conjugated, and produces a perfectly grammatical sentence.

**Is this a model error or an item-design gap?** Genuinely arguable, flagged rather than
silently scored. The repair task's construct is specifically whether a model can locate
*and minimally fix* a congruence-failure violation — docs/charter.md's own framing is
"repair... tests whether the model can locate the violation." Substituting a native verb
does locate and eliminate the violation, but it does so by avoiding the EL-sourced
lexical item entirely rather than by supplying the ML morphology the Blocking Hypothesis
predicts should attach to it. That's a different repair *strategy* than the one T5 is
built to probe — structurally analogous to the EL-island escape hatch already documented
for `constrained_continuation` above: an always-available alternative that satisfies the
surface requirement (produce a licensed sentence) without engaging the specific
constraint under test.

**Why not add these as `alternate_repairs`, matching the attested-spelling-variant
precedent (csw-es-en-0377 etc., `docs/journal.md`)?** Those variants were different
spellings of the *same* morphological strategy (loanword integration). "Aparcar" is a
different strategy entirely — crediting it would mean the item no longer tests loanword
integration at all, just "produced any grammatical repair," which isn't what T5 is
designed to measure. Left unscored rather than credited, and named here instead, so a
future reader doesn't mistake three genuinely well-formed Spanish sentences for three
outright failures.

### Continuation items share stimuli: 100 items, 24 distinct prompts (2026-09-08)

**What was found.** A `(cached)` result on item 86 of the first full-set run, an item
that had never been run. Two items with identical rendered prompts produce identical
cache keys. Counted: judgment, ML identification, and repair have one distinct prompt
per item; continuation has 24 distinct prompts across 100 items, 4 of them covering all
33 T5 items.

**Effect.** At temperature 0 each full run's 100 continuation records are 24 model
responses; a response can match at most one sibling's gold string; the task's ceiling is
24/100 for any model; the table's continuation n overstates independent observations
about four to one. The violation-production rate is over 24 responses per run.

**Why it is not fixed.** Same reason as the defects above, plus the runs against this
exact set are in progress. `scripts/finalize_phase4.py` states the affected cells under
the results table from the item data. A v1.1 needs a distinct prompt per continuation
item and a validation check that rendered prompts are unique, which the current set
cannot pass.

### 372 Phase 4 items carry no Spanish diacritics (2026-09-01)

**What was found.** 0 of the 372 items added in Phase 4 contain any accented character,
against 18 of the 30 pilot items. "Compre el libro ayer" for "Compré", "Perdi" for
"Perdí", "esta manana" for "esta mañana", across 166 items by a conservative word list
and, by construction, every item whose vocabulary table entry should carry an accent.
`scripts/build_phase4_items.py`'s tables are ASCII.

**Effect.** None on scoring: `textnorm.normalize` strips diacritics before every
comparison, so a model answering with correct orthography still matches. Real on the
stimulus: "compre" is a different verb form from "compré", "manana" is not a word, and a
model was shown standard Spanish on the pilot items and non-standard Spanish on the rest
of the same set. Which cells this touches is not knowable from the scores -- a model
whose parse is disturbed by the orthography fails indistinguishably from one that
misrepresents the MLF constraint.

**Why it is not fixed.** The blind-review sample was measured against these exact
strings, and regenerating the items with accents would ship 372 items that no reviewer
has seen. Carried into v1.0 as a named defect (`docs/limitations.md`) with a v1.1 fix:
regenerate with accented tables, re-review, re-run.
