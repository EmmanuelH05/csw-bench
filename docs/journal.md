# Journal

Per `docs/charter.md`: each phase ends with a commit and an entry here recording **what was
tried, what broke, and what changed in our thinking**. Negative results and reversals
belong here. Suppressing them is the exact failure mode this project exists to avoid.

---

## Phase 0 — repo skeleton

**Date:** 2026-08-15

**What was tried.** Scaffolded the repo: `uv` project, `src/csw_bench` package layout,
`docs/` skeletons, `data/` tree split by language pair, test directory, license,
`ERRATA.md` created empty per the Phase 5 requirement (created now so there is never a
moment where a post-freeze issue has nowhere to go).

**Decisions made and why.**

- **Python over TypeScript.** Overrides the global standing preference for TypeScript.
  Reasons: `matriz` fine-tunes models and is necessarily Python, so a TS benchmark puts
  a serialization seam between the two halves of the experiment; the field's eval
  harnesses (lm-eval-harness, HELM, LinCE) are Python, which makes the repo legible to
  its actual audience; and Phase 4 requires bootstrap confidence intervals on every
  number, which is a scipy call in Python and hand-rolled resampling code we would have
  to separately defend in TS. Approved explicitly by the principal.

- **Hindi/English as the second pair, provisionally.** _Superseded same day — see Phase
  0a below. Retained because the reasoning is what the reversal had to answer._
  The tempting choice was
  Swahili/English, since MLF was developed on it. Rejected: evaluating a theory on the
  data the theory was derived from is testing on train. Hindi/English is genuinely
  out-of-sample for MLF, is typologically distant on criteria that yield crisp
  system-morpheme diagnostics (postpositions, split ergativity, light verbs), has real
  digitized corpora, and — a practical constraint that turned out to be decisive — has a
  recruitable bilingual population for the Phase 2 human validation and Phase 4 human
  ceiling. Swahili/English fails that last test badly enough to stall Phase 2.
  **Provisional pending corpus verification in Phase 1 Track A.**

- **No taxonomy enum in code yet.** Tempting to write `ViolationType` during scaffold.
  Deliberately not done: `docs/charter.md` puts the taxonomy in Phase 1 and forbids opening a
  phase with a prior checkbox open. Encoding five guessed types now would let the code
  silently become the source of truth ahead of the document. `docs/taxonomy.md` ratifies
  first; the enum is generated against it afterward.

- **Skipped `gsd-new-project`.** `docs/charter.md` already is the roadmap and phase
  breakdown. Running project-init would have produced a lower-fidelity duplicate.

**What broke.** Nothing yet — no code with behavior to break.

**What changed in our thinking.** One thing, and it is load-bearing: the second-pair
choice started as a logistics question (which has better corpora) and ended as a
construct-validity argument (which pair is out-of-sample for MLF). That reframing is
worth more to the project's central claim than the corpus counts were, and it should
appear in `design.md` as the primary justification with corpus availability secondary.

---

## Phase 0a — narrowed to a single language pair

**Date:** 2026-08-15

**What changed.** Dropped Hindi/English. The benchmark is Spanish/English only.

**Why.** Principal's call, and defensible on its own terms. The binding constraints on
this project are item count and second-pass review effort, not ambition. Two pairs at
~200 items each gives roughly ten items per violation-type × task-type cell; holding out
an entire violation type downstream would then leave `matriz` with too little to train on.
One pair at ~400 doubles cell density. The item target deliberately did *not* halve with
the pair count — that is the whole content of the decision.

Spanish/English is also the pair where the provenance rules are actually satisfiable.
Bangor Miami, Spanish in Texas, and LinCE mean attested items with real citations exist in
quantity, which was never as certain for the distant pair. And the human-dependent gates —
three bilinguals scoring above 90% in Phase 2, a human ceiling in Phase 4 — are reachable
for Spanish/English at UCLA in a way they would not have been otherwise.

**What this costs.** Real, and now written into `limitations.md` as a first-class threat
rather than a caveat. Spanish and English share SVO order, Latin script, and heavy
cognate vocabulary, so a model may score well by riding that overlap rather than by
representing an MLF constraint. The typologically distant pair existed precisely to
supply the contrast case that would separate those two explanations. Without it we cannot
fully separate them. The partial mitigation is a subset of items where MLF prediction and
the shared-order heuristic dissent, scored separately.

**What changed in our thinking.** The previous entry recorded a reframing — that pair
choice was a construct-validity question, not a logistics one. That reframing survives the
narrowing and now cuts against us, which is the useful part. Going single-pair does not
make the validity problem disappear; it makes it *undiagnosable within the benchmark*.
Naming it that bluntly is better than the alternative, and the dissent-subset is a real
if partial answer. Interview question 6 — what this does not measure — now has a sharp
answer instead of a vague one.

## Phase 1 — design and taxonomy (in progress)

**Date:** 2026-08-15

**What was written.** `design.md` sections 1–6 and a five-type draft in `taxonomy.md`.
Three of four Phase 1 completion conditions now close; the fourth is blocked on taxonomy
ratification.

**Decisions.**

- **T1 and T4 split along the 4-M early/outsider line**, rather than being one
  "EL system morpheme" type. This is the most load-bearing decision in the taxonomy: the
  early-versus-outsider distinction is what makes MLF's predictions graded instead of
  binary, so collapsing it would cost real theoretical resolution.

- **Adjective placement rejected as a T2 probe.** Spanish licenses both prenominal and
  postnominal adjectives with a meaning difference, so an English-looking order may be
  independently grammatical — it fails the diagnostic's third question. Clitic placement
  is used instead, where preverbal position with finite verbs is obligatory.

- **Anti-hedging is three rules, not one.** Non-commitment scores zero; monolingual
  output scores zero on generation tasks; correct label with lexical-counting evidence
  earns the label point only. The monolingual rule closes what would otherwise be the
  largest hole in the design — without it a model dodges every continuation item by
  answering in one language.

- **No cross-task averaging.** Task types have different point scales and different
  chance floors, so a single headline number would be meaningless. Reported as a vector
  normalized against per-task chance.

**What broke.** **T4 may not be populable.** English inflectional morphology is
impoverished — subject-verb agreement reduces to third-person singular *-s*, structural
case surfaces only on pronouns — and English-EL-into-Spanish-ML is the more common
direction in the corpora. That leaves few probes for an EL-sourced late outsider system
morpheme. The fallback is to fold T4 into T1 and ship four types, which still clears the
minimum. Recorded now, unresolved, rather than discovered at item 200.

**What changed in our thinking.** Two things.

Writing the null-result section forced a distinction that was not obvious going in: a
null downstream result is *publishable*, but a **ceiling effect is not**. If frontier
models score above ~90% on the pilot, the benchmark cannot discriminate and the
downstream experiment has no headroom — that is a design failure, not a finding. Phase 2's
pilot now has a second job beyond validating items: detecting ceiling early enough to
raise difficulty rather than discovering it after 400 items exist.

Second, threat 5.2 (surface frequency) is more dangerous than 5.3 (contested ML
assignment), which is not where the emphasis sat at the start. Contested ML assignment
weakens the theoretical framing; surface frequency offers a *complete alternative
explanation* for a good score. The dissent subsets — items where MLF disagrees with
corpus frequency, and where MLF disagrees with translation fidelity — moved from a nice
idea to the load-bearing mitigation for the benchmark's central claim.

## Phase 1 — Track A corpus recon and the ordering stress test

**Date:** 2026-08-15

Two blockers cleared, and both changed the design rather than confirming it.

### Corpus licensing is more restrictive than assumed

Bangor Miami is **CC BY-NC-SA 3.0**, not permissive. TalkBank states the license
"precludes the incorporation of the data in commercial products, including systems such
as large language models," and that "the data themselves cannot be included in models."

Three consequences, all recorded in `corpora.md`:

- **The repo is now dual licensed.** MIT for code, per-item licenses for items. The old
  `LICENSE` note waved at "source corpora licenses" without naming one, which was fine
  when we did not know and negligent once we did. Fixed, and surfaced in `README.md`
  rather than buried — a user who builds on this and later commercializes has a problem
  we could have warned them about in one sentence.
- **The schema needs a per-item `license` field, and the loader must filter on it.** A
  Phase 3 API requirement discovered in Phase 1, which is exactly what Track A was for.
- **`matriz` has genuine non-commercial exposure and it is unresolved.** The favorable
  reading is that the LLM restriction addresses commercial enterprises and academic
  fine-tuning is squarely permitted; the unfavorable reading is that "cannot be included
  in models" is stated flatly. Recommendation is to email the depositors for written
  clarification while proceeding on the non-commercial reading. **Not resolvable by
  assumption — flagged for decision.**

Also established: LinCE supplies candidate utterances but never gold MLF labels, since
its tasks are LID, NER, POS, and sentiment. Treating its annotations as labels would
import answers to a different question. Spanish in Texas terms remain unread.

### The ordering stress test found two real defects

Ten constructed ambiguous cases against the T3→T2→T4→T1→T5 ordering. Six clean, two
contested, **two failures**.

**T2 admitted monolingual errors.** Case C4 — a postverbal clitic in otherwise
all-Spanish text — satisfied every T2 question while containing no EL material at all.
That is a Spanish grammar error, not a code-switching violation. The diagnostic now asks
whether the constituent contains EL material before anything else. This is the most
valuable thing the exercise produced: unpatched, it would have quietly contaminated the
item set with items that measure the wrong construct, and the contamination would have
been invisible at review because each item is individually well-formed.

**T4 is dead.** Case C10 could not produce a clean constructed case — \*`camina-s` is
incoherent rather than code-switched. Combined with the populability argument from
English's impoverished inflection, that is two independent reasons. **T4 folds into T1;
the taxonomy ships four types.** The alternative, keeping it small and documenting the
low count, was rejected: a type `matriz` cannot meaningfully hold out is not a type.

Four types across four task types gives sixteen cells at ~25 items each — better density
than the five-type design's twenty cells at ~20.

### What changed in our thinking

The stress test was written expecting to validate the ordering. It broke it twice
instead, and the T2 hole is the kind of error that survives review precisely because
every individual item looks fine — only the aggregate is wrong. **A stress test that
finds nothing is evidence the cases were too easy, not that the design is sound.**
Expanding to twenty before ratification, and treating a clean run as a red flag.

Second: cutting T4 shows the taxonomy is doing real work rather than being decorative.
Five types was the number that felt right when the theory was the only input; four is
what the language pair actually supports. The gap between those two numbers is the
project's whole thesis in miniature — theoretical elegance is not the same as a construct
you can measure.

## Phase 1 — parallel pass: stress test to 20, council, corpus spike

**Date:** 2026-08-15

Four workstreams run in parallel. Three reported; the licensing recon is still out. The
headline is that **the taxonomy failed much harder under adversarial testing than under
its first ten cases**, and that is the useful result.

### The stress test broke four of five diagnostics

Twenty cases: eight clean, five contested, seven failures. Five of the seven failures came
from the second ten, which were built to attack the ordering rather than exercise it.

The first round's six-clean result should be read as evidence those cases were too easy,
not as validation. That reframing is the methodological lesson and it now sits in the file
itself.

Defects found and fixed:

- **T1 fired on both presence and absence of the same morpheme.** `los books` (EL plural
  present) and \*`los book` (EL plural absent) both returned T1, which is incoherent — the
  System Morpheme Principle is about the *source* of a morpheme that surfaces. T1 now
  requires the morpheme be present. This reassigns C8 to T5 on the diagnostic's own terms.
- **T2 had no EL-island exclusion** while T5 did, so licensed multiword EL nominals like
  `la movie theater` were flagged. Highest-yield fix in the round; multiword EL nominals
  are common enough to have contaminated T2 at scale.
- **T2's "licensed ML alternative" test was silently variety-relative** — wh-non-inversion
  violates standard Spanish but is native to Caribbean Spanish. Probes are now restricted
  to constructions obligatory across all major varieties, which shrinks an already thin
  type.
- **T3 was unreachable on internally ill-formed EL with no ML intrusion**, so \*`book the`
  fell through every type to no assignment — the C4 hole again, in the other language. T3
  gains an out-of-scope terminator, and a contiguity requirement that stops it capturing
  scattered EL material just because an island reading is available.
- **T5 question 3 now reads "morphology on the EL element itself"**, since Spanish gender
  is realised on the determiner rather than affixally, and the old wording flagged licensed
  `la table`.

Two coverage gaps are now documented rather than left implicit: agreement-*value* failure
on EL nouns is out of scope (MLF predicts morpheme source, not agreement correctness), and
segmentation is an unstated input, so contested segmentation becomes its own recorded,
separately scored annotation.

### The council resolved both contested cases and found a bigger hole

C8 → T5 and C9 → T2, both with losing arguments recorded verbatim and explicit flip
conditions in `council-c8-c9.md`. C8's verdict was reached independently by the stress
test and the council, which is the closest thing to corroboration available here.

More importantly, the council found a **structural gap that neither case was about**.
Folding T4 removed the outsider type, bridge was never covered, and T1 admitted only early
morphemes — so the shipped taxonomy had **no type for any EL-sourced late system
morpheme**. C9 concealed it because its bridge morpheme drags word order along and T2
catches the result. Strip that coincidence and \*`el libro of Juan` fires nothing: not T3,
not T2, not T1, not T5. A violation MLF is explicitly committed to predicting went
unclassified.

**Fix: T1 is widened from "EL early system morpheme" to "EL system morpheme."** The 4-M
class survives as a per-item metadata field rather than as a type, so the early/outsider
gradation remains analysable downstream without being a held-out split too sparse to
matter.

This is better than it first looks. The taxonomy is now a clean **system/content** split —
T1 for system morphemes, T5 for content morphemes — which is MLF's own primary division,
and it recovers most of what cutting T4 cost. The earlier limitation entry stands but is
narrower than written.

Consequence: **C9 must be re-adjudicated.** Under the narrow T1 it was never admissible
and the ordering was not load-bearing; under the widened T1 it becomes a genuine T1/T2
overlap that the ordering decides.

### The corpus is gated, and the terms reach further than expected

Bangor Miami **could not be downloaded**. Both documented URLs fail — one 404s, the other
returns HTTP 200 with 319 bytes of HTML auth modal, which a naive `curl -o Miami.zip`
writes to disk looking like success. Worth knowing before someone "successfully" downloads
a corpus that is actually a login page.

The gate is site-wide rather than corpus-specific: an openly-licensed CHILDES corpus
returns the identical modal. So this reads as a **free-account requirement, not a
permission denial** — resolvable by registering, not by negotiating.

Everything downstream of the download remains genuinely unknown: whether token-level
language ID exists, whether `%mor` morphological tiers exist, whether timestamps do.
`corpora.md` asserts token-level language ID; that is now marked unconfirmed. **The `%mor`
question is the one that matters** — the system/content distinction the entire taxonomy
rests on depends on it. If the tiers are absent, item construction becomes an annotation
project rather than a parsing job, and Phase 2's cost estimate is wrong.

Separately: TalkBank forbids uploading their data to third-party LLM systems unless
non-retention is explicitly selected. That binds **Phase 3 evaluation**, not just `matriz`
fine-tuning, which is where the earlier analysis had filed it. Every provider account used
in a run needs zero retention enabled, and the setting becomes a recorded run detail.
Now in `design.md` §5.7. A default-configured API key silently violates the corpus terms.

### What changed in our thinking

Running four workstreams in parallel produced something sequential work would not have:
the stress test and the council reached the same verdict on C8 by different routes, and
the council found a structural gap precisely *because* it was forced to argue a case it
had been told was about something else. The instruction that produced the most value was
"try to break this," not "check this."

Second, and less comfortable: the diagnostics were substantially worse than they looked
after one review pass. Four of five had defects that only adversarial cases exposed, and
every one would have produced items that individually pass review while collectively
measuring the wrong thing. **The revised diagnostics have not themselves been stress
tested** — that is now a ratification blocker, because fixes written in response to
specific failures are exactly the kind that overfit to those failures.

## Phase 1 — Track A complete: three corpora became one

**Date:** 2026-08-15

The licensing recon finished last and produced the largest single change to the project's
risk profile so far. **We planned around three corpora and have one.**

**Spanish in Texas is CC BY-NC-ND 4.0**, verified at the Texas Data Repository deposit that
holds the cited DOI. ND forbids redistributing adapted material, and a benchmark item built
from a transcript — retokenized, minimally paired, relabelled — is an adaptation. The
corpus can be read and studied; derived items cannot be published. That makes it unusable
as an item source without written permission from the depositors.

Notably, `spintx.org` states CC BY-NC-**SA** 3.0 while the deposit states CC BY-NC-**ND**
4.0. These are incompatible, not merely different. We operate on the deposit, because it is
the distribution channel and carries the required citation DOI. This is the second time in
one day a secondary source contradicted a primary one on licensing — the first was a search
summary claiming Bangor Miami was BY-SA when TalkBank's own rules say BY-NC-SA. **Licensing
claims get verified at the distribution point or they do not get used.**

**LinCE is blocked**, and for a more interesting reason than expected. No license is stated
anywhere — not the datasets page, not the LREC paper, not the HuggingFace card. An absent
license is not a permissive one. Three of its four Spanish/English constituents are Twitter
data distributed as IDs rather than text, which carries its own redistribution bar. And the
fourth, the POS split, **is Bangor Miami** — so routing through LinCE would have re-imported
the CC BY-NC-SA obligation while adding a layer of indirection. It launders nothing.

**The two licenses cannot be combined.** SA requires adaptations be shared alike; ND forbids
adaptations. There is no merged "csw-bench corpus," only single-sourced items with per-item
licenses. This is the second independent argument for the per-item `license` field already
in the schema, which is now doing more work than when it was added.

### What changed in our thinking

The single-corpus outcome is worse than a licensing inconvenience and it took a while to see
why. Bangor Miami is 84 bilinguals in Miami, 2008–2011, informal conversation only. Miami
Spanish is heavily Caribbean-influenced — and the stress test had *already* found that T2's
diagnostic is variety-sensitive, with Caribbean Spanish licensing wh-non-inversion that
standard Spanish forbids. Those two findings arrived from different workstreams and only
collide when read together: **our sole attested source is drawn from a variety that may
license the very constructions one of our violation types depends on.**

That is not a reason to stop. It is a reason to check T2's probes against Caribbean Spanish
specifically before building items, and it moves the speaker-population narrowness from a
generic limitations-section caveat to a live threat against a specific type. Added to
`limitations.md` as its own entry.

Second: Phase 2's plan assumed corpus abundance. It should now assume scarcity — which
argues for building constructed items to a higher proportion than originally intended, and
for being explicit in results about how much of the benchmark is attested versus derived
from documented predictions.

## Phase 1 — round 2: the fixes broke things, and T2 may not survive

**Date:** 2026-08-15

Two adversarial passes. Both found more than the first round did, and one of them
invalidated a claim recorded earlier the same day.

### The round-1 fixes overfit to the failures that motivated them

Exactly the risk flagged when they were written. Eleven of twenty cases changed type, and
**one previously-working case broke outright**.

**T3's contiguity requirement contradicted T3's own third question.** q1 demanded the EL
stretch be unbroken; q3 demanded ML material inside it; ML material inside a stretch breaks
contiguity. Both could not hold. C3 — round 1's flagship clean case, described in this
journal as "the case the ordering exists for" — returned no type at all, and **T3's own
canonical example in `taxonomy.md` failed its own first question.** T3 was close to empty
and nobody noticed, because round 1 never re-ran the old cases against the new rules.

Replaced with constituenthood-modulo-intrusion, which still rejects C13's phantom island
without excluding the intrusion that defines the type.

**T1 had no island exclusion.** T2 and T5 both did. Under the narrow T1 this was harmless,
because early system morphemes attach to their own EL hosts — but bridge morphemes attach
*outward* by definition, so widening T1 made it fire on licensed EL islands (C22). The leak
was manufactured by the widening, not inherited from it.

**Two correct fixes combined into a hole.** T1 requires the morpheme be present (fixes
C17); T5 requires missing morphology be on the EL element itself (fixes C11). A *missing,
free-standing ML system morpheme* — \*`Vi la teacher` without the personal *a* — satisfies
neither escape and falls through the whole taxonomy. Neither fix is wrong; their
conjunction removed coverage nobody voted on. C8 escapes only by accident, because Spanish
plural happens to be an affix.

**A retraction.** This journal recorded that widening T1 "recovers most of what T4's
removal cost." **That is false.** Widening closes the late *bridge* hole — its one
unambiguous win — but recovers no late *outsider* coverage, for exactly the reasons T4 died:
EL affix on ML stem is unattestable, EL affix on EL stem is excluded by q4, fused case is
unsegmentable. `system_morpheme_class` will contain no outsider values. Corrected in
`taxonomy.md` and `limitations.md`.

Also: the phrase "attaches to ML material" was undefined and silently decided seven of
twenty-six cases. Now specified.

### T2 may not be viable, and the two analyses disagree

The variety check found T2's probe inventory nearly empty. Wh-inversion is dead on variety
grounds, subject expression is dead and actively generates false positives, clitic climbing
is optional in the standard itself, negation is low-yield.

Worst: **preverbal clitic placement — T2's headline probe — fails structurally, not
dialectally.** Proclisis is genuinely categorical in Caribbean Spanish; the problem is that
the clitic and the finite verb are both ML by construction, so the constituent has nowhere
to put EL material. The taxonomy's own example, \*`Yo veo lo en la tienda`, is entirely
Spanish and is terminated by the C4 exclusion this project added a few hours earlier. We
shipped a headline example that our own diagnostic rejects.

That leaves nominal possessor order as the only strong survivor — which is C9. And the two
round-2 workstreams reach **opposite verdicts on C9**: the variety check wants it in T2
(keeping four types), the diagnostic re-run argues it is T1 (dropping the taxonomy to
three, below the `docs/charter.md` minimum).

### What changed in our thinking

Three things, and the second is uncomfortable.

**Fixes need adversarial re-testing as much as designs do.** Round 1 wrote five diagnostic
fixes and did not re-run the twenty cases against them. That single omission hid a broken
T3, a manufactured island leak, and a coverage hole created by two individually-correct
fixes interacting. The rule now: any diagnostic change re-runs the full case set.

**We were about to reason backwards from a quota.** The tempting move is to assign C9 to T2
because T2 needs items. That is deriving a linguistic judgment from a logistical need, and
it is precisely the failure mode this benchmark exists to detect in others. Written into
`taxonomy.md` explicitly so the temptation is on the record rather than acted on quietly.

**The premise underneath the whole T2 crisis is unverified.** Nobody has checked Bangor
Miami's speaker national-origin breakdown. "Caribbean-influenced" was inferred from the
recording location. Two documents now argue from that inference, and one of them may force
a three-type taxonomy. The corpus metadata can settle it in an afternoon and must, before
any decision. A benchmark about construct validity nearly made a structural decision on an
uncounted population.

---

## Phase 3 — harness built ahead of sequence

**Date:** 2026-08-16

**What was tried.** Built the model-agnostic evaluation harness that `csw-bench run` and
`csw-bench report` depend on, ahead of Phase 1 closing and with zero pilot items on disk:
`prompts.py` (two paraphrased templates per task type, deterministic presentation order
for judgment pairs so a position-biased model cannot beat the 50% floor), `providers.py`
(Anthropic/OpenAI/Google adapters behind one `ModelProvider` protocol, SDK imports
deferred to construction so `matriz` never pays for them), `cache.py` (response cache
keyed by a hash of the full `CompletionRequest`, so any settings change misses and a
rerun under identical settings never re-bills), `accounting.py` (token totals split into
billed vs. cached columns; cost computed only from prices supplied at run time, never a
hardcoded table), `runner.py` (the run loop, plus a `RetentionError` guard that refuses
to send an attested item to a provider unless `zero_retention=True` — the TalkBank terms
obligation from `docs/corpora.md`), and `results.py`/`stats.py` (pure-Python percentile
bootstrap, per-task above-chance rescaling, and the `compare()` prompt-sensitivity
delta). `cli.py` gained `run` and `report` subcommands.

**This is a deliberate sequence violation, not an oversight.** `docs/charter.md` says no phase
opens with a prior checkbox open, and Phase 1's own checklist (line 127 onward) is still
unchecked — T2/C9 are unresolved and the Bangor Miami speaker-metadata premise is
unverified, both noted above. The harness was built anyway on explicit instruction to
maximize code completion in one sitting. Recorded here per the standing rule: **follow
the instruction, but the departure from the phase gate goes on the record.** Phase 3's
actual completion conditions (line 153 onward — full pilot runs against three model
families, a reproduced cached rerun, a reported prompt-sensitivity delta, tested filter
disjointness) cannot be checked off yet, because they require real items and Phase 2 has
none. What exists is infrastructure verified against synthetic fixtures, not a completed
phase.

**Verification.** 127 tests (up from 54), `ruff check`, `ruff format --check`, and
`mypy --strict` all pass. Ran a four-dimension adversarial multi-agent review
(correctness, spec compliance, the code-quality bar, third-party SDK correctness against
the installed `anthropic`/`openai`/`google-genai` package sources) with an independent
skeptic verifying every raw finding. One confirmed, low severity: `ModelProvider` and its
three implementations carried a `family: str` class attribute nothing read — dead code
under the project's own bar. Deleted from the protocol and all four provider classes
(three real, one test fixture). Every other raised finding was refuted with an empirical
check rather than argument (e.g. deleting the attribute and re-running `mypy`/`pytest` to
prove it was unread; a claimed unreachable rubric tier turned out to be pre-existing at
`HEAD`, not introduced by this change). Seven of sixteen review sub-agents hit a session
limit mid-run, so the review is solid on what it covered but not exhaustive — it did not
finish auditing repair-minimality semantics, cached-rerun idempotency into a fixed output
directory, or CLI-level provider-exception handling.

**What changed in our thinking.** Nothing about the taxonomy or the corpus questions —
those remain exactly as open as Phase 1 round 2 left them. What changed is procedural:
building downstream infrastructure before an upstream phase gate closes is now a named,
recorded exception rather than something that could happen silently. The harness is
real and tested, but "the code runs" is not the same claim as "the phase is done," and
this entry exists so the two are never conflated later.

127 tests, 0 items, disagreement rate n/a.

## Phase 1 — closed: three types ship, not four; two licensing findings still open

**Date:** 2026-08-16

**What was tried.** Closed out the two ratification blockers Phase 1 round 2 left open —
T2's viability and the C9 type assignment — plus the corpus-licensing and citation loose
ends the harness-ahead-of-sequence entry above flagged as still owed.

**T2/C9, decided.** Three independent lines of evidence converged: `t2-variety-check.md`'s
dialect-level probe survey (most candidates dead — several on dialect grounds as
false-positive generators, one on optionality, the taxonomy's own headline probe on a
structural defect independent of dialect — one low-yield, only nominal possessor
order — C9 — surviving as a strong probe); `ordering-stress-test-v2.md`'s diagnostic-level
re-run, which found C9's order deviation is the obligatory linearization of one imported
morpheme (English `'s`) rather than evidence of general EL-frame pressure, and that
tightening T2's question 5 to say so — independently required to fix a parallel false
positive at C19 — removes C9 from T2 regardless of the type-count question; and a further
targeted search this session for heritage/contact-Spanish-specific probes the first two
passes might have missed (differential object marking, subject-verb order, DP-internal
order), which came back negative and, more specifically, found the contact-linguistics
literature reports *convergence* toward English-compatible order in exactly the domains
that would serve as T2 probes — the opposite of what a violation type needs. **T2 is
dropped. C9 resolves to T1 (late bridge). The taxonomy ships three types: T1, T3, T5.**
Full reasoning in `taxonomy.md` § "T2 dropped." `docs/charter.md`'s four-type floor is amended
to three, with the reasoning recorded there rather than silently relaxed, and Phase 4's
item-density arithmetic recalculated (twelve cells, not sixteen — cell density went *up*).

The premise check `taxonomy.md` previously said must happen before deciding — Bangor
Miami's speaker national-origin breakdown — was **not** fully clearable this session
(see below), and the decision proceeds without it. That is a deliberate call, not an
oversight: two of the three converging lines of evidence do not depend on Miami's specific
population, so an unbounded wait on population data that may never arrive was judged worse
than a documented, reversible decision. If the data later shows the population is less
Caribbean-influenced than assumed, the dialect-level leg of the argument weakens but the
diagnostic-level and convergence-literature legs do not, and T2 can be reopened the same
way T4's fold was documented rather than deleted.

**A real primary-source find: Bangor Miami's license is contested, not settled.** Session
had, for the first time, actual network access to attempt the Phase 1 blockers previously
left as `[VERIFY]`. `Miami_doc.pdf` — the corpus's own documentation file, written by the
depositor (Margaret Deuchar) and hosted at the canonical TalkBank access URL — states the
corpus is licensed **GNU GPL v3**, not CC BY-NC-SA 3.0. That directly conflicts with the
CC BY-NC-SA reading `corpora.md`, `LICENSE`, and `README.md` were already built on, which
came from a different TalkBank page (the access/terms page, not the depositor's own
documentation) and from TalkBank's site-wide data-sharing policy. **Not resolved.** Two
live readings — both terms apply, stacked (access terms plus depositor's own license), or
the depositor's license controls and TalkBank's page is an error or simplification — and
picking one would mean rewriting a licensing conclusion already load-bearing elsewhere.
Flagged prominently in `corpora.md` §1 for the principal to resolve by asking the
depositor directly, alongside the pre-existing `matriz` non-commercial question — both are
the same email. Also downloaded and read the documentation itself: it confirms corpus size
(242,475 words, 84 speakers, 35:11:04) but does not give speaker national origin, which is
"available to researchers on request" — meaning the T2 premise-check needs a direct
request to the Bangor team, not merely a TalkBank account, correcting an earlier
assumption in this journal.

**Citation verification, partial.** All five theoretical citations
(@myersscotton1993duelling, @myersscotton2002contact, @myersscotton2000fourm,
@macswan1999minimalist, @poplack1980sometimes) checked at the work level (year, venue,
volume, pages) against publisher/journal records — all confirmed. One real error found and
fixed: `references.bib`'s Bangor Miami entry cited a different, real paper (Deuchar et al.
2014, "Building Bilingual Corpora") instead of the citation TalkBank's own page requires
(Deuchar & Parafita Couto 2011, with DOI) — using the wrong one would not have satisfied
the corpus's own mandatory-attribution term. Page-level verification of the SMP's exact
wording and the 4-M classification of bridge morphemes remains blocked — both source books
are login-gated (Internet Archive controlled lending) or paywalled, and no PDF exists
locally. A secondary-source finding surfaced during the attempt and is recorded, not
acted on: two independent secondary sources quote the SMP as constraining only morphemes
with grammatical relations *external to their head constituent* — the 4-M model's own
definition of *outsider*, not early or bridge. If that reading holds on a direct read of
the primary text, T1's citation is only fully licensed for the outsider cases this
taxonomy cannot populate, and the early/bridge violations that make up nearly all of T1's
actual item pool would need a different citation. Flagged as the single highest-priority
`[VERIFY: page]` item, ranked above the C8/C9 checks that depend on it.

**C25 (missing free-standing ML system morpheme) decided: out of scope.** Consistent with
the existing C12 precedent — the SMP constrains morpheme *source*, not *presence* — and
chosen over building a fifth type, which would have required the same blocked SMP page
check. Reversible if that check later shows the SMP does constrain absence.

**Other decisions closed.** Spanish in Texas dropped as an item source (ND license forbids
derived items; Bangor Miami is the better corpus regardless). `matriz` non-commercial
question: operating on the non-commercial reading as a provisional default, with the
stronger fix (emailing the depositor) explicitly left for the principal to send — not
decided or executed in this session, since it is an external communication on the
project's behalf. `LICENSE`/`README.md` dual-licensing language: found already correct
from earlier work, not something this session had to do — though now provisionally
correct pending the GPL conflict above, not fully settled.

**A process note.** This session ran concurrently with another working session
open on the same repo, discovered mid-session when both were found editing
the same files. No work was lost or silently overwritten — caught early, coordinated by
message, confirmed uncontested before either side's edits landed — but it is recorded here
as a real, if narrowly avoided, risk: nothing in this project's process currently detects
two concurrent editors of the same doc, and next time it might not resolve as cleanly.

**What changed in our thinking.** The T2 crisis this journal has tracked across several
entries as "the largest open question in the project" turned out to have a cleaner answer
than its length suggested: once the diagnostic fix motivated by a *different* case (C19)
was actually applied to C9, the type-count question mostly answered itself, and the
population-verification premise this document insisted on turned out to be
non-load-bearing for two of the three convergent arguments. The harder-won lesson is the
licensing one: a conclusion built on one authoritative-seeming page (`corpora.md`'s
CC BY-NC-SA finding, cited and re-cited across four documents and never re-checked) turned
out to have a second, contradicting authoritative-seeming page nobody had read. This is
the same failure shape Track A already flagged once — "licensing claims get verified at
the distribution point or they do not get used" — except this time the distribution point
itself was internally inconsistent. The fix is not "read more carefully next time"; it is
that a single-source citation, even a primary one, is not verification until a second
independent statement from the same authority is checked to agree with it.

128 tests, 0 items, disagreement rate n/a.

## Phase 1 → Phase 2 transition — scope narrowed: no external or human-dependent steps

**Date:** 2026-08-16

**What was decided.** The principal declined to pursue any of the external/human-dependent
steps the entry above left open: no email to the Bangor Miami depositor, no recruiting
bilingual human raters, no TalkBank account creation. Rather than block on these or quietly
drop the rigor they existed to provide, each is replaced with a documented, named
substitute — the same discipline this project has applied to every other departure so far
(T4's fold, T2's drop, the four-type floor amendment).

**Licensing, decided permanently rather than left pending.** The GPL v3 / CC BY-NC-SA 3.0
conflict and the `matriz` NC question both get a final answer instead of "pending email":
this project operates under the **union of both readings' obligations** — attribution,
non-commercial use only, share-alike/no-relicensing for adaptations — since compliance
with the stricter combined reading satisfies either individual reading regardless of which
authority (TalkBank's access page or the depositor's own documentation) is actually
correct. The one question this doesn't resolve — whether a model fine-tuned on these items
is a GPL "derivative work" — is accepted as open risk and named in `corpora.md` §1 and
`LICENSE`, not chased down. `LICENSE` and `README.md` rewritten to disclose the conflict
explicitly rather than assert CC BY-NC-SA 3.0 as settled fact.

**Corpus access, confirmed blocked and not pursued.** Tried the transcript browser
directly this session (`sla.talkbank.org/TBB/biling/Bangor/Miami`) rather than assume the
prior "319-byte auth modal" finding still held after `Miami_doc.pdf` turned out to be
unexpectedly reachable. It does still hold — a 469-byte JS app shell containing a
client-side `authModals` object, a genuine login gate. **No attested items will be built
from raw Bangor Miami transcripts.** This does not mean no attested items at all:
`docs/charter.md`'s provenance rules name "published corpora **and the code-switching
literature**" as primary sources together, so genuinely attested examples quoted and
cited from published papers (Poplack, Toribio, Zentella, and others already surfaced
during Track A and the T2 research) remain in scope. Phase 2 will lean more heavily on
constructed items than the original design assumed, and that shift is named here rather
than discovered by a reader counting citation types in Phase 4's results table.

**Phase 2/4 validation, restructured — see the amendment recorded directly in
`docs/charter.md`.** Three bilingual humans scoring the pilot blind, and a human ceiling in
Phase 4, are both replaced with independent *blind* AI review — a reviewer that never
sees the gold label, run as a genuinely separate pass from the one that built the item.
`docs/charter.md` carries the full reasoning and the honest statement of what is lost: a human
catches blind spots a model of any family may share, which is exactly the risk this gate
existed to catch, and substituting AI review is weakest precisely where the benchmark's
central claim is strongest. This is recorded as a real degradation of construct validity,
not a relabeling, and `limitations.md` will carry it as a first-class threat once Phase 2
produces something to evaluate against it.

**What changed in our thinking.** Every departure recorded in this journal up to this
point was a response to what the *evidence* forced (T2's populability, the licensing
conflict). This one is different in kind: it is a response to what *resources* allow, not
what the theory or the data required. The discipline that kept the earlier departures
honest — name the cost, don't quietly relax the bar, record what would change the decision
back — applies exactly the same way here, and is the reason this entry is as long as the
ones that record an actual research finding. A scope-narrowing decision that isn't written
down with the same rigor as a research finding is how a project quietly stops being the
thing its own documentation claims it is.

0 items, disagreement rate n/a.

## Phase 2 — pilot set built and blind-reviewed

**Date:** 2026-08-16

**What was tried.** Built the 30-item pilot set: 10 items per violation type (T1, T3, T5),
distributed 9/7/7/7 across the four task types (grammaticality judgment, constrained
continuation, ML identification, repair). All items are `source: constructed` — the
corpus-access finding above means no item cites a raw Bangor Miami transcript this pass;
a literature-sourced attested subset remains future work, not attempted here. Built via
`scripts/build_pilot_items.py`, which computes `violation_span` from the real tokenizer
rather than hand-counting, so indices can't drift from what the schema and scorer
actually see. `csw-bench validate`: 30/30 pass.

Design choices, briefly: T1 items probe determiner/demonstrative intrusion (the
taxonomy's own productive T1 probe). T3 items follow the taxonomy's canonical example
structure exactly — an EL-internal article plus an ML article intruding immediately
after it ("a el book"), not a substitution, since an earlier draft that substituted the
EL article for an ML one turned out to be diagnostically ambiguous (arguably just a
licensed mixed NP, not an island violation) and was caught and corrected before
construction, not after. T5 items use the taxonomy's own documented contrast: a
morphologically-integrated EL verb root (parquear, printeó, chatear, texteo, clickea —
established, frequently-cited integration patterns in the Spanish-English contact
literature, not invented) versus the same root surfacing bare.

**Blind review, executed as specified in the `docs/charter.md` amendment.** Rendered every item
through the actual `prompts.py` templates (template "a") — the same rendering path
Phase 3's harness uses — and dispatched all 30 rendered prompts to a fresh, independent
subagent with zero access to this conversation, the taxonomy, gold labels, or
justifications. It answered each blind, as a fluent bilingual would, per that item's own
instructions.

**Result: 29/30 (96.7%) construct-validity agreement, clears the amended 90% bar.**
Judgment (9/9) and repair (9/9) items: the reviewer selected exactly the gold-licensed
member, or produced exactly the gold repair, on every single item. ML identification
(7/7): the reviewer named Spanish as the Matrix Language, with sound morphosyntactic
reasoning, on every item. Constrained continuation (6/7 clean, 1/7 logged disagreement):
the reviewer's free completions didn't match the single recorded example for six items,
but on inspection all six are genuinely well-formed, licensed alternatives — "mis keys
ahorita" (Spanish possessive + English noun, same licensed pattern as the gold example),
"a beautiful sunset ayer" (an intact English island, same pattern), and so on. These were
verified against the item's own diagnostic and added to `licensed_continuations` as
validated second examples, not just noted — the second independent pass improving the
gold label is exactly what this process is for.

**The one genuine, unresolved disagreement: csw-es-en-0024.** Prompted with "Todos los
días yo", the reviewer completed "...check my email antes de salir." Whether "check my
email" is a bare EL verb phrase requiring Spanish inflection (this item's intended T5
violation) or a clause-level switch to a full English constituent (a different,
arguably-licensed phenomenon this taxonomy doesn't have a clean answer for) is genuinely
unclear on inspection. Not force-resolved. Logged verbatim in the item's own
`provenance.review_disagreement`, per the disagreement-reporting rule already in place —
this is the actual, honest 1/30 the disagreement-rate statistic reports.

**A separate, real finding: the ML-identification scorer needs the Phase 3 work its own
docstring already asks for.** The literal automated scorer (`score_ml_identification`)
reports only 42/58 (72.4%) points earned, not 96.7%. Every point of that gap traces to one
mechanism: the evidence sub-score requires the reviewer's free-text answer to contain
`item.required_evidence` strings verbatim as substrings, and a fluent independent
reviewer's own phrasing — correct, specific, morphosyntactic — never happens to match
mine word-for-word. `scoring.py`'s own docstring already names this exact failure mode
("brittle against free prose... needs a response-extraction step") as a known Phase 3 gap.
This session's blind review is the first time that gap produced a concrete, measured
number against real items rather than a documented worry. Not fixed here — fixing it by
rephrasing `required_evidence` to match one reviewer's specific wording would be
overfitting to that reviewer, not a real fix, and the real fix (an extraction step ahead
of the literal match) is already correctly scoped to Phase 3.

**What changed in our thinking.** The AI-substitute validation gate amended into
`docs/charter.md` two entries ago was written defensively, expecting it to be a weaker signal
than human review and hoping it would at least clear the bar. It did clear the bar, at
96.7% — but the more useful thing it produced wasn't the pass/fail number, it was six
items whose answer keys were quietly too narrow and one item whose intended violation
turns out to be genuinely ambiguous. A validation pass that only confirms items are fine
is doing less work than one that finds something to fix, and this one found real things
on both a "the item was under-specified" axis and a "the scorer, not the item, is the
problem" axis — which is exactly the distinction a validation pass needs to draw rather
than collapse into one pass/fail number.

30 items, disagreement rate 1/30 (3.3%).

## Phase 2 — second review

**Date:** 2026-08-16

**What was tried.** Round 1's blind review checked construct validity — does an
independent reviewer, seeing only the rendered prompt, reach the gold answer. It was
never designed to catch problems that don't show up in that narrow lens: a bug in how an
item was *constructed*, not in whether its answer is fluent. So a second, differently
scoped independent review followed — this reviewer was handed the taxonomy, the schema,
the scorer, and all 30 items together, and asked to audit for construction problems the
blind method structurally can't see.

**What it found, and what got fixed rather than patched around, in `scripts/
build_pilot_items.py` revision 2:**
- T3's `"a el X"` intrusion pattern collides with two things at once: Spanish's
  obligatory `a + el → al` contraction, and the homograph between English's indefinite
  article "a" and the Spanish preposition "a". Both create a spurious second reading.
  Replaced with `"the el X"` throughout, which has no Spanish-preposition reading.
- Several `ml_identification` items cited word order (adverb-PP order, SVO order) as
  Matrix Language evidence. Spanish and English share both orders — this is exactly the
  confound `docs/limitations.md` already names as a threat, and citing it as *evidence*
  inside an item directly contradicted that threat. Replaced with genuinely discriminating
  evidence: finite Spanish verb morphology, null-subject licensing, Spanish-sourced
  function words.
- Three T3 `ml_identification` items cited the island-internal intrusion itself as
  Matrix-Language evidence — circular, since the intrusion is the thing being tested, not
  proof of the frame around it.
- The T3 double-article construction admits two independently grammatical minimal
  repairs (delete either article), which a single `gold_repair` string can't express.
  Rather than force one arbitrary answer, added `RepairItem.alternate_repairs`
  (`schema.py`) and its own validator (alternates must be distinct from each other and
  from `violating`).
- Two items' gold repairs picked one tense/demonstrative variant among several
  equally-valid ones with nothing in the sentence to disambiguate which. Fixed by adding
  disambiguating context (a temporal adverb forcing tense; possessives in place of a
  demonstrative that had a second valid Spanish translation) rather than picking a
  winner arbitrarily.
- Two of round 1's six validated continuation widenings were reverted: on closer
  inspection they license the sentence through a different mechanism than the one under
  test (a bare noun with no determiner at all; an English adverb with no EL verb at all)
  — genuinely grammatical, but not evidence for or against the construct being measured.
- Vocabulary was templated too repetitively — the same violating string reused across
  three or four items under different task types. That doesn't just look repetitive, it
  means round 1's 96.7% blind-review figure was measured against items that were less
  mutually independent than a flat "29/30, 96.7%" implies. Diversified nouns and verbs
  across the set; some intentional reuse remains where a repair item legitimately shares
  its stimulus with the judgment item it repairs, which is not the same problem.
- The reviewer also surfaced the T3 diagnostic-question confound recorded separately in
  `docs/taxonomy.md` (a literal reading of T3's q1/q2/q3 diagnostic can fire on plain
  T1/T5 items) — flagged there as unresolved, not fixed here, since fixing a shipped
  diagnostic requires the full case-set re-run `taxonomy.md`'s own house rule demands.

**What it confirmed.** In the reviewer's own words: "All 30 items carry exactly one
primary violation from the shipped taxonomy... No item's violating string is accidentally
grammatical, and no item's licensed string is ungrammatical." The fixes above are
construction-quality corrections on top of that base, not a discovery that items were
wrong at the level round 1 already checked.

**What changed in our thinking.** Two independent review passes with different scopes
caught different classes of problem — round 1 (blind, narrow) caught answer-key gaps;
round 2 (informed, broad) caught construction bugs a blind pass can't see because it
never looks at the taxonomy or the generator logic at all. Neither pass alone would have
been sufficient. The vocabulary-repetition finding is the one that most directly qualifies
the headline number: 96.7% construct-validity agreement is real, but it was measured
against a less mutually-independent item set than the number alone suggests, and that
qualification belongs next to the number, not buried in a script docstring. This entry
exists because `scripts/build_pilot_items.py` cited it by name before it was written —
closing that gap here rather than leaving code pointing at a journal section that doesn't
exist.

30 items, disagreement rate 1/30 (3.3%).

## Phase 3 pivot: local models

**Date:** 2026-08-17

**What was decided.** `providers.py` shipped with three cloud vendors (Anthropic, OpenAI,
Google) and nothing in `docs/`, `docs/charter.md`, or this journal ever recorded a decision to
use them specifically — they were just the default someone reaches for when a design says
"model providers." Asked directly, the principal's intent was local inference throughout,
not cloud APIs. Rather than treat this as a footnote, it is recorded as a real pivot with
real consequences, the same discipline applied to every other departure in this file.

**What changed.** `AnthropicProvider`, `OpenAIProvider`, and `GoogleProvider` are removed
outright, not kept dormant — per `docs/charter.md`'s own no-dead-code rule, provider code the
project has decided not to use is dead code regardless of whether it's reachable.
Replaced with a single `OllamaProvider` talking to a local Ollama server
(`http://localhost:11434` by default), using the official `ollama` PyPI package in place
of `anthropic`/`openai`/`google-genai` in `pyproject.toml`'s optional `runners` extra.

**What "three model families" means now.** The original design's three-vendor
requirement existed to avoid a benchmark result that's really just "one company's
post-training happens to agree with these labels." That reasoning doesn't disappear
locally — it just moves down a level: `PROVIDER_FAMILIES` collapses to `("ollama",)`
because there is only one local transport, but `RunConfig.model` still picks a specific
pulled tag, exactly the way `OpenAIProvider` used to serve many model ids under one
family. Three *model families* now means three distinct model lineages/training
organizations run through that one transport, not three API vendors. Candidate trio,
chosen from what is already pulled on this machine (`ollama list`) rather than picked
abstractly: **`qwen3:30b`** (Alibaba/Qwen), **`deepseek-r1:32b`** (DeepSeek), **`gpt-oss:
20b`** (OpenAI's open-weight release) — three genuinely different organizations and
training lineages, which is the property the original design was actually protecting.
`kimi-k2.6:cloud` also appears in `ollama list` but is excluded from this trio: the
`:cloud` tag routes through Moonshot's hosted API rather than running on-device, which
would silently reintroduce the exact cloud dependency this pivot removes.

**What this resolves and what it doesn't.** No API keys, no per-token cost in practice
(see `PricePerMTok` note below) — the Phase 3 blocker reported to the principal in the
prior session (three-vendor API spend) is gone. It does **not** unblock "full pilot runs
end to end against three models" by itself: that completion condition also needs the
repair-minimality edit-distance threshold, which `docs/design.md` already flags as open
and uncalibrated, and calibrating it against an uncommitted, arbitrary value would
produce a run that looks complete but isn't backed by a real threshold. That calibration
is separate work, not done here.

**`PricePerMTok`, kept and not deleted.** `accounting.PricePerMTok`, the CLI's
`--price-input`/`--price-output` flags, and `RunAccounting.cost_usd` all describe a
provider that bills per token, which `OllamaProvider` never does — `cli.py`'s `run`
command simply passes `prices=None` when the flags are omitted, and every run so far has
omitted them. This is the same "kept, not deleted" call `docs/design.md` §5.7 made for
`zero_retention`, for the same reason: `accounting.py`'s own docstring already treats
provider pricing as caller-supplied, not hardcoded, so nothing about it assumes a cloud
vendor, and a future cloud-provider comparison (`docs/design.md` §5.7 names this as the
scenario that would make the retention reasoning load-bearing again) would need this
exact mechanism back immediately. Unlike `AnthropicProvider`/`OpenAIProvider`/
`GoogleProvider`, this isn't cloud-specific code sitting unused — it's provider-agnostic
accounting infrastructure that a local-only run legitimately exercises with `prices=None`.

**Self-review before commit found real gaps in the pivot itself, fixed before
committing.** A `pr-review-toolkit` pass (required by `docs/charter.md`'s own "review before
done on multi-file work" rule once a change touches more than three files) found that the
"local-only" claim this entry makes above was not actually enforced by the code as first
written:
- `OllamaProvider.__init__` called bare `ollama.Client()`, which resolves its host from
  `OLLAMA_HOST` and attaches `OLLAMA_API_KEY` as a bearer token if either is set in the
  environment — meaning a stray env var, not anything in this repo, decided whether a
  "local" run actually stayed local. Confirmed against the installed package's source
  (`ollama._client.BaseClient.__init__`), not just the docs. Fixed: the provider now pins
  `host=LOCAL_OLLAMA_HOST` explicitly, and that resolved host is recorded on
  `RunConfig.provider_host` so the claim is auditable from `run.json` rather than trusted
  from whatever `providers.py` happens to do at the time.
- `:cloud`-tagged Ollama models (like `kimi-k2.6:cloud`, visible in local `ollama list`)
  proxy to a hosted API despite looking local, and nothing rejected `--model
  kimi-k2.6:cloud`. Fixed: `OllamaProvider.complete` now rejects any `:cloud`-suffixed
  model before it ever calls the client.
- `docs/design.md` §5.7's amendment had said the retention constraint "cannot be
  violated... regardless" — false given the two gaps above. Corrected to describe what
  the code actually enforces, not what local inference merely tends to do.
- A truncated reasoning-model response (chain-of-thought alone can exceed the default
  1024-token `num_predict` budget, which the pivot's own candidate trio includes
  `deepseek-r1:32b` for) produced an unhelpful "no text content" error indistinguishable
  from an actual empty response. Fixed: branch on `ChatResponse.done_reason == "length"`
  for a distinct, correctly-attributed error. Whether to raise the default `max_tokens`
  or pass `think=False` for reasoning models is a calibration decision, written down here
  rather than defaulted into: not decided yet, and needed before the real three-model
  pilot run.
- The original tests asserted `seed_applied is True` against a hardcoded literal — a
  tautology that couldn't fail even if the `options` mapping to Ollama's `chat()` call
  were wrong. Fixed: tests now assert the exact call `OllamaProvider` makes against the
  client mock, plus dedicated cases for the `:cloud` rejection, the truncation error, and
  both halves of the missing-usage-accounting guard (parametrized; only one half was
  covered before).
- `docs/corpus-parse-spike.md` §3, the source document §5.7 was derived from, still
  asserted the original "every provider account... zero retention" framing untouched.
  Given the host-pinning gap above, its own amendment note is narrower than §5.7's: the
  constraint stops binding only for runs that are actually local, which is now an
  enforced and recorded property, not an assumed one.

30 items, disagreement rate unchanged at 1/30 (3.3%).

## Repair-minimality threshold calibrated; think=False wired in

**Date:** 2026-08-24

**What was tried.** The two open items blocking a real Phase 3 pilot run —
`docs/design.md`'s uncalibrated repair-minimality threshold and the undecided
`think=False`/`max_tokens` question from the Ollama pivot — were both closed before
running anything against the three local models.

**Threshold.** Computed `SequenceMatcher(None, tokenize(violating),
tokenize(gold_repair)).ratio()` for all 7 pilot repair items: real minimal single-token
gold repairs range 0.75-0.909. Simulated non-minimal repairs (gold fix plus one token
changed outside the violation site) on the same items range 0.5-0.6. The two ranges don't
overlap; fixed the threshold at **0.7**, inside the gap. Full reasoning, including a real
length-sensitivity limitation this calibration doesn't surface (the pilot's repair items
are all 4-6 tokens) and Phase 4's resulting constraint on repair-item length, is in
`docs/design.md` §4.

**A more consequential finding surfaced while calibrating, not looked for.** Re-reading
`score_repair` to pick the threshold showed the minimality branch it gates is currently
*unreachable*: the function requires an exact token-sequence match against
`[gold_repair, *alternate_repairs]` before it ever computes a ratio, and every string in
that list is minimal by construction (`alternate_repairs`' own docstring says so). So the
ratio computed after the gate is a constant determined by which item it is, never by
which response the model gave — the "1 point, edits exceeded the violation site" branch
cannot fire for any item in the current pilot set, at any threshold. This doesn't
invalidate the calibration (a principled value is still needed for the day
`alternate_repairs` gets a genuinely non-minimal entry, or span-constrained scoring
replaces the exact-match gate), but it does mean the upcoming pilot run's repair scores
will show only 0 or `maximum`, never 1 — reported as an observed property of the scorer,
not smoothed over. Full detail in `design.md` §4.

**think=False.** `OllamaProvider.complete` now passes `think=False` on every call.
Resolves the calibration decision the Phase 3 pivot entry above left open. Every prompt
template asks for the target utterance verbatim and nothing else, so chain-of-thought
was pure downside: it could exhaust `num_predict` before any content emerged (the
truncation case already tested), and even when it didn't, it would pollute
`response.message.content` with reasoning prose that the exact-match scorers count
against the model. A no-op for non-reasoning models, a real fix for `deepseek-r1:32b`.

30 items, disagreement rate unchanged at 1/30 (3.3%).

## Phase 4: 30 -> 402 items

**Date:** 2026-08-24

**What was built.** `scripts/build_phase4_items.py` generates 372 new items
(csw-es-en-0031 through csw-es-en-0402), 31 per (violation type x task type) cell across
all 12 cells, on top of the 30-item pilot. Same construction discipline as Phase 2:
constructed provenance, a recorded derivation per item, hand-curated vocabulary. 402
items total, balanced 134/134/134 across T1/T3/T5.

**Real bugs found during construction, fixed before committing:**

1. **`str.capitalize()` silently lowercases embedded proper nouns** --
   `"Vi el carro de Juan hoy.".capitalize()` produces `"...de juan hoy."`. Every
   sentence-level capitalize call (25 of them) replaced with a `cap()` helper that
   touches only the first character.
2. **Gender-agreement bug invisible at pilot scale.** The pilot's possessive items only
   ever used a feminine noun, so a hardcoded feminine adjective ("nueva") never surfaced
   as wrong. Crossing possessives against the full noun list produced "su carro nueva"
   instead of "su carro nuevo" -- an error the narrower pilot vocabulary structurally
   could not expose. Fixed with a `nuevo(gender)` helper.
3. **Semantically anomalous verb-object pairings.** T5's 20 loanverbs crossed
   combinatorially against a shared object list produced "Necesito chatear el archivo"
   (chatear takes an interlocutor, not a document) and "Text la ventana". Fixed with a
   `VERB_OBJECTS` mapping, one real-world-plausible complement per verb. T3's
   `ISLAND_CARRIER_VERBS` had the same defect ("leer"/"romper" crossed against every
   island produced "leyo the red car"); dropped both in favor of general-purpose
   possession/handling verbs.
4. **A combinatorial periodicity bug.** When one vocabulary cycle's period evenly
   divides another's (a 4-item prompt cycle against the 20-item verb-root cycle), the
   *pair* they produce repeats exactly every `lcm` of the two -- 20, not the 51+ items
   requested. Fixed at the root (a 3-prompt cycle, coprime with 20) rather than by
   hand-tuning offsets against each collision found, which broke again the moment a
   vocabulary table changed shape. General backstop added regardless: the assembly stage
   over-generates a buffer per cell and drops any candidate that exactly duplicates
   something already accepted (pilot or earlier in the same run); IDs are assigned after
   filtering so dropped duplicates leave no numbering gaps.

Zero duplicate sentence pairs, zero gender mismatches, zero mis-capitalized proper nouns
-- checked programmatically across all 402 items, not spot-checked.

## Phase 4 blind review: a sample, and a real finding about the continuation task

**Date:** 2026-08-24

**Sampling, and why it's a sample and not the full 372.** `docs/charter.md` says every item
gets a second-pass review. At 372 new items, genuinely independent review of every one
exceeds what's feasible here. 120 items were sampled (10 per cell, stratified across all
12 violation x task-type cells) and reviewed blind by 10 independent fresh agents -- no
gold label, no taxonomy, no mention of MLF, only the rendered prompt -- the same
methodology Phase 2 used, just sampled rather than exhaustive. Named as a real
degradation from the stated rule, the same way the human-validation substitution already
is, not quietly treated as equivalent.

**Raw agreement by task type**, scored against gold with `scripts/score_phase4_review.py`:

| Task type | Agreement |
|---|---|
| grammaticality_judgment | 30/30 (100%) |
| ml_identification | 30/30 (100%) |
| repair | 26/30 (86.7%) raw |
| constrained_continuation | 0/30 (0%) raw |

**Repair's 4 "failures" are not failures.** All four are attested alternate integration
spellings of the same loanword the gold answer already used correctly (taguear/taggear,
chequear/checkear, escanear/scanear, taipear/typear) -- the reviewer localized and fixed
the right thing, just spelled the integrated verb differently. Added as `alternate_repairs`
to the four affected items (csw-es-en-0377, -0379, -0401, -0402), the same precedent
already set for cliquea/clickea in the pilot. Construct-validity agreement for repair is
effectively 30/30 once credited correctly, not 26/30.

**Constrained continuation's 0/30 is not 30 item defects -- it's one task-design finding,
and it's the real unexpected finding this phase produced.** Every one of the 30
disagreements was inspected by hand. Not one reproduced the item's actual
`violating_continuations` string -- checked programmatically, zero matches. What
reviewers did instead falls into two patterns:

- **18/30**: after the Spanish frame-establishing prompt, the reviewer completes the
  rest of the sentence entirely in English ("Compre a new laptop.", "Todos los dias yo
  work out.") -- no further code-switching at all.
- **12/30**: the reviewer keeps switching in Spanish elsewhere in the sentence (temporal
  adverbials, additional clauses) but still produces a *fully English* object NP with
  its own English determiner ("Busque flights para el fin de semana.", "Vi the new
  Marvel movie ayer.") rather than the single-morpheme-mixed NP the item is built to
  probe.

Both patterns are well-formed EL islands under MLF's own licensing -- a complete,
internally well-formed English constituent is a legitimate switch point, structurally
distinct from the partial, single-morpheme-mixed constituent (an EL-sourced determiner
attached to an ML-sourced noun) that T1's and T3's continuation items are specifically
built to force. `design.md`'s existing anti-hedging rule already closes the *monolingual
output* hole ("Monolingual output scores zero on generation tasks"); it does not close
this one, because the reviewers' answers are not monolingual and not ungrammatical --
they are genuinely code-switched, MLF-licensed sentences that simply resolve to a
*different*, always-available construction instead of the one under test. An open-ended
"complete this utterance" prompt does not force the narrow contrast; a fully-formed EL
island is a standing escape hatch, and independent bilingual-competent responders reached
for it as their *default* strategy, not a rare edge case.

**Why this matters beyond the review sample.** `score_constrained_continuation` checks a
response's normalized text against exactly two recorded strings (licensed, violating) and
returns 0 -- "matched no recorded licensed form" -- for anything else. A real model that
competently produces a licensed EL-island continuation instead of the specific recorded
one would be scored identically to a model that failed outright. Phase 4's upcoming
results need this named as a live confound for every T1/T3 continuation cell, not
discovered after the fact when continuation scores come back surprisingly low. Logged
here and flagged for `design.md` §5 and `limitations.md`; not fixed by rewriting all 93
continuation items in this pass -- that scope is out of what Phase 4 can absorb right
now, and is recorded as a real, open cost rather than silently deferred.

402 items, sample-review disagreement rate: judgment 0/30, ml_id 0/30, repair 0/30
(post-credit), continuation 0/30 genuine violations reproduced / 30/30 resolved via an
unmodeled licensed alternative -- reported as a task-design finding, not an item defect.

## A hung request, not just a failed one

**Date:** 2026-08-24

The per-item `ProviderError` isolation fixed earlier in Phase 3 was tested for real
running the actual pilot against `gpt-oss:20b`, and it wasn't enough. Item
`csw-es-en-0011` — a plain grammaticality-judgment prompt that should take single-digit
seconds — never returned. The run sat with no progress for over 20 minutes before it was
killed and investigated directly (`ollama ps` showed the model idle-ish, not actively
generating; the harness's own Python process showed near-zero CPU, consistent with
blocking forever on a synchronous HTTP call).

Root cause: `ollama.Client()` forwards its kwargs straight to `httpx.Client`, whose
default is `timeout=None`. No timeout was ever set anywhere in `providers.py`. A request
that never raises — because it never returns — can't be caught by the `ProviderError`
isolation added earlier, no matter how correct that isolation is; that fix handles a
provider that answers badly, not one that doesn't answer.

Fixed by constructing the client with an explicit 300s timeout and catching
`httpx.TimeoutException`, re-raised as `ProviderError` so the existing per-item isolation
picks it up from there. 300s is generous headroom over every real generation timing
observed so far (worst case ~35s), while still bounding a hang to minutes instead of an
indefinite wait. Full detail in the commit. This is the second reliability gap the real
pilot run has surfaced that no amount of code review would have found — both were only
visible by actually running the harness against a real local model, which is the entire
reason Phase 3's "full pilot run" gate exists rather than being satisfiable by unit tests
alone.

**Correction, filed once more evidence came in.** The specific item 0011 stall above was
re-diagnosed after the timeout fix landed: an isolated single-item run through the actual
`run()` code path (not a synthetic test) completed normally in 11.9 seconds — the same
item, the same model, no code difference from the run that appeared to hang. The
apparent multi-hour stall coincides with the host machine's clock jumping forward three
days between checks, which is consistent with the machine going to sleep mid-run rather
than gpt-oss looping. The timeout and flush fixes above are real, independently-justified
improvements regardless (a request timeout is correct engineering with or without this
explanation, and per-write flushing is what made the discrepancy checkable at all) — but
the root cause of *this specific* stall is filed as "the machine slept," not "gpt-oss
hung," and subsequent long runs are launched under `caffeinate -i` to prevent a recurrence.
Noted here rather than left as an unresolved contradiction with the 11.9s re-run.

## Phase 3 gate, model 1 of 3: gpt-oss:20b

**Date:** 2026-08-27

Full 30-item pilot run completed end to end, then rescored twice as the two real ml_
identification scoring fixes landed (`scripts/rescore_run.py`; 3/30 then 2/30 records'
scores changed, respectively — see the two fix commits below). Final results
(`runs/pilot-gpt-oss-20b-a/`), reported via `csw-bench report`:

| Task | Score | Errored |
|---|---|---|
| grammaticality_judgment | 100% (9/9) | 0 |
| repair | 66.7% | 1/9 |
| ml_identification | 26.7% | 2/7 |
| constrained_continuation | 0% | 4/7 |

**Two things worth separating.** The continuation-task confound this journal already
documents (the EL-island escape hatch) means the 0% there cannot be read as "gpt-oss
doesn't represent the T1/T3 constraints" — but 4 of its 7 continuation attempts didn't
even reach a scoreable response, hitting the reasoning-budget provider error
(`docs/journal.md`, "A hung request, not just a failed one") even at `max_tokens=8192`.
That's a genuine reliability finding about this model on this task, independent of the
scoring confound: gpt-oss:20b's harmony-format reasoning channel burns through a large
token budget disproportionately on continuation prompts specifically (judgment and
repair prompts, structurally similar in length, essentially never hit this). 7/30 = 23%
overall provider-error rate for this model.

The 26.7% ml_identification score, post-fix, is a real (if middling) number rather than
a scoring artifact — worth flagging explicitly since two separate fixes landed mid-run
and each could be mistaken for having inflated the score. Both were verified against
concrete reproductions before being trusted (see the anchored-claim fix commit), not
just assumed correct because the number moved in the expected direction.

Two models remaining: qwen3:30b (running now) and deepseek-r1:32b.

## Phase 3 gate, model 2 of 3: qwen3:30b

**Date:** 2026-08-27

Full 30-item pilot run completed end to end, 0 provider errors (vs gpt-oss:20b's 7/30).
Rescored with all three scoring fixes applied (`extract_final_answer`, both
`ml_identification` fixes) — 17/30 records changed score, which is itself informative:
this confirms the `<think>` leakage and anchored-claim fixes were catching real,
substantive scoring corruption on this model, not edge cases. `runs/pilot-qwen3-30b-a/`.

| Task | Score | Errored |
|---|---|---|
| grammaticality_judgment | 88.9% | 0/9 |
| repair | 42.9% | 0/7 |
| ml_identification | 33.3% (consistent across T1/T3/T5, label credit only) | 0/7 |
| constrained_continuation | 0% | 0/7 |

The T5 repair native-word-substitution finding (`docs/findings.md`) came from this run:
three of qwen3's T5 repairs scored 0 because they replaced the bare EL verb with a
different, correct native Spanish verb instead of the loanword's morphologically
integrated form — a real, grammatical sentence that nonetheless doesn't exercise the
constraint T5 targets. Flagged as an item-design gap, not scored as a model error.

One model remaining: deepseek-r1:32b.

## Phase 3 gate, model 3 of 3: deepseek-r1:32b

**Date:** 2026-08-27

Full 30-item pilot run completed end to end, this time under `caffeinate -i` throughout
(the sleep-related false "hang" diagnosis above was from an earlier attempt at this same
model). One resource-contention self-inflicted mistake mid-run: a competing verification
request to `gpt-oss:20b` evicted deepseek-r1:32b from Ollama's memory (only 24GB RAM),
producing one extra timeout (csw-es-en-0008) attributable to the mistake, not the model.
Killed the competing request via `TaskStop` on noticing the latency spike; the harness
process itself survived and resumed normally. `runs/pilot-deepseek-r1-32b-a/`. Rescored
with all current fixes: 0/30 records changed (deepseek's completed responses didn't
happen to hit either bug class this pilot exercised).

| Task | Score | Errored |
|---|---|---|
| grammaticality_judgment | 100% | 0/9 |
| repair | 42.9% | 0/7 |
| ml_identification | — | 7/7 (100%, all timeouts) |
| constrained_continuation | 0% | 0/7 |

**The headline finding for this model**: all 7 of 7 `ml_identification` items timed out
at the full 300s budget, while every item of every other task type completed normally.
That is not a general reasoning-budget problem (`grammaticality_judgment` and `repair`
prompts are structurally comparable in length and completed fine) — it is isolated to
the one task that asks the model to *analyze and justify* rather than select or
reproduce a target string, and it is 100%, not a tendency. Full writeup with the
realness checks in `docs/findings.md`.

**Phase 3's cross-model gate is now satisfied**: full pilot runs completed end to end
against three distinct local model families (gpt-oss:20b, qwen3:30b, deepseek-r1:32b),
each rescoreable from cached responses without re-billing. Remaining Phase 3 items: the
cache-rerun reproducibility check and the prompt-sensitivity (template b) check.

## Cache-rerun reproducibility, verified and one honest caveat

**Date:** 2026-08-27

Verified the Phase 3 gate "a rerun from cache reproduces identical scores" directly
against `runs/pilot-deepseek-r1-32b-a`, whose cache was still warm and uncontended: for
every one of its 23 non-errored records, reconstructed the exact `CompletionRequest`
(prompt, model, seed, temperature, max_tokens from `run.json`), looked it up against
`runs/cache/` with zero provider calls, and confirmed both the raw response text and the
rescored `Score` match the committed record exactly — 23/23. (A live CLI rerun was tried
first and confirmed the same thing for its first 6 items before being stopped: it also
correctly *fell through to a live provider call*, not a false cache hit, for the one
previously-errored item it reached next — expected, since `runner.py` never caches an
errored response. Full CLI reruns were not needed to demonstrate this once the direct
cache-lookup script gave a cleaner, faster answer.)

**The honest caveat.** The same check run against `runs/pilot-gpt-oss-20b-a` found only
3/23 entries still in the cache — not a mechanism failure, but the documented
resource-contention workaround earlier in this file (`rm -rf runs/cache` run before each
new model's pilot, to guarantee a clean memory state) also destroyed gpt-oss's and
qwen3's *raw response caches* specifically, since the cache is shared and keyed
model-agnostically rather than partitioned per run. This does not threaten score
reproducibility for either model — `records.jsonl` persists each response's full text
independently of the cache, which is exactly what let `rescore_run.py` recompute scores
for all three models' runs multiple times without a single provider call — but it does
mean a *cold-cache CLI rerun* of gpt-oss or qwen3 today would re-bill 20/23 items rather
than hitting cache, contrary to the "rerunnable from cache without re-billing"
requirement for those two specific runs. Named here rather than silently only testing the
one model whose cache happened to survive.

## Phase 4/5 infrastructure built without a single model run; three item-set findings

**Date:** 2026-09-01

**Constraint on this session, stated up front.** No inference was run. The principal
called that after a machine memory incident mid-session (unrelated to this repo's
processes, which were reading files at the time; recorded here only because it is why
the plan changed). Everything that does not need a model was built instead, so that the
remaining work is literally `scripts/run_phase4.sh` plus transcribing its numbers. Every
checkbox that needs a run stays open in `docs/charter.md`, annotated with what closes it.

**The dangling `runs/pilot-qwen3-30b-b/`, investigated and removed.** Fourteen records,
no `run.json`. Items 0001 and 0002 were served from cache (an even earlier attempt);
items 0003 through 0014 are twelve consecutive 300 s timeouts, one hour of wall-clock,
starting at 09:48 on 2026-08-27 -- ten minutes after `runs/pilot-deepseek-r1-32b-a/`
began on the same 24 GB machine. Two 18-19 GB models cannot coexist in Ollama's memory,
so every qwen3 request waited behind an eviction and timed out. That is the
resource-contention episode the deepseek entry above already records from the other
side, not a template-b finding. Nothing in it is worth folding into the journal beyond
this paragraph, and a partial run without a manifest cannot be loaded by `load_run`
anyway. Deleted; the runbook recreates the directory properly as its first stage.

**What was built.**

- `csw-bench table RUN_DIR...`: the Phase 4 results table as markdown, one column per
  run, one row per task and per task x violation cell, each cell carrying the raw mean,
  the above-chance mean with its bootstrap CI, the scored n, and any errored count. It
  refuses runs over different item sets. `docs/results.md` is its output; the README's
  headline table is a copy of the pooled rows, so "every number reproducible from
  committed code and data" is one command.
- `compare()` is now paired by item and reports a percentile-bootstrap CI on the delta,
  so the Phase 3 prompt-sensitivity number will not be a bare point estimate. An item
  errored in either run leaves the pair rather than counting as a zero on one side.
- `run()` takes an `on_record` observer; the CLI prints a timestamped line per item to
  stderr, so a multi-hour background run is followable from a log.
- `scripts/run_phase4.sh`: template b on the pilot against qwen3:30b, then the three
  full-set runs in sequence, each stage skipped when its `run.json` exists, under
  `caffeinate -i`, with the operator notes the pilot taught (one model at a time, expect
  a day and a half, the deepseek ml_identification timeouts alone are eight hours).
- `scripts/continuation_escape_hatch.py`: buckets every continuation response by what it
  did instead of a recorded string, and computes the one continuation statistic the
  escape hatch cannot distort, the violation-production rate. See finding 3 below for
  what it showed on the pilot runs already on disk.
- `tests/test_shipped_set.py`: the v1.0 hash in `docs/versions.md` must equal the items
  on disk, and the ml_identification chance floor must equal the best constant-label
  strategy's score on the shipped set. Both are contracts between committed data and
  code that fixtures cannot check.

**Three findings about the item set, logged rather than fixed.** All three were found by
reading the data the tooling above needed, not by running anything.

1. **Every one of the 402 items has Spanish as its Matrix Language**, including all 100
   `ml_identification` items. A model that answers "Spanish" to every prompt earns the
   label point (1 of 3) on every item with no analysis. `CHANCE_FLOOR` had 0 for this
   task; it is now 1/3, the score of that constant strategy, derived from the shipped
   distribution and pinned by test. Effect on the pilot numbers already published: raw
   means are unchanged; the above-chance column moves. qwen3:30b's 0.333 (label credit
   only, every item) is exactly the floor and now reads +0.00; gpt-oss:20b's 0.267 reads
   -0.10, below the floor, because it named the wrong language on some items. The label
   component has no discriminative power on this set; only the evidence points do. The
   imbalance itself is a consequence of the design (items restricted to cases where the
   literature converges on the ML, and Spanish-frame/English-content is the convergent
   direction for this pair), so it is reported as a property, not repaired by inventing
   English-ML items nobody has reviewed.

2. **The 372 Phase 4 items carry no Spanish diacritics at all**: 0/372 contain any
   accented character, against 18/30 in the pilot. "Compre el libro ayer", "Perdi el
   documento", "esta manana". `scripts/build_phase4_items.py`'s vocabulary tables are
   ASCII. Scoring is unaffected -- `textnorm.normalize` strips diacritics before every
   comparison, so a model that answers with correct accents still matches -- but the
   stimulus is not: "compre" is the present subjunctive, not the preterite "compré", and
   "manana" is not a word. A model reading the prompt as written sees non-standard
   Spanish, which is a confound on every Phase 4 item and an inconsistency against the
   accented pilot items in the same set. **Not fixed**, on the principal's standing
   instruction and for a reason that holds independently: the 120-item blind-review
   sample and its 100%/100%/100%/0% agreement were measured against exactly these
   strings, and regenerating 372 items with accents would ship an item set nobody has
   reviewed. Carried into v1.0 as a named defect (`docs/limitations.md`, "Known item-set
   defects at v1.0"); a v1.1 that regenerates with accents and re-reviews is the honest
   fix.

3. **Exact-string continuation scoring zeroes the very construction it exists to
   detect.** Running the new classifier over the three pilot runs already on disk: on
   T1 items, qwen3:30b completed "Ayer compré" with "un coffee" and "Tengo" with "mi
   phone" -- a Spanish determiner attached to an English noun, precisely the licensed
   pattern the T1 items are built around -- and scored 0, "matched no recorded licensed
   form", because the gold string fixes the *noun* ("las revistas para la clase"), not
   the construction. deepseek-r1:32b completed all 7 of 7 continuation items in
   monolingual Spanish ("el libro", "me levanto temprano"), also 0, which is the rubric's
   intended outcome for monolingual output but reached by accident of no-match rather
   than by the rule `design.md` §4 states. And the rule and the gold labels contradict
   each other: all 34 T1 licensed continuations are themselves monolingual Spanish
   strings, so a literal implementation of "monolingual scores zero" would zero the gold
   answers. The escape-hatch finding of 2026-08-24 stands and is now the narrower case
   of a broader one: as scored, `constrained_continuation` measures whether a response
   coincides with one of two strings, and its cells should be read for the
   violation-production rate (did the model produce the recorded MLF violation) rather
   than the score, as a lower bound -- the same exact match misses a violation built on
   a different word (qwen3's "work late" for "Todos los días yo", a bare EL verb in a
   Spanish 1sg frame, counted as neither). Violation rate on the pilot: 0/17 scored
   continuations across all three models. Not fixed in the scorer: crediting any "det + noun" match means
   re-specifying what every T1/T3/T5 continuation item licenses, which is item design,
   not a scoring patch.

**A fourth finding, about process.** `scripts/compute_ceiling.py` and
`scripts/score_phase4_review.py` read the blind-review sample from `/tmp`, which is
gone. The construction-time ceiling (judgment 100%, repair 100%, ml_identification 33%,
continuation 0%) and the Phase 4 agreement rates are therefore historical figures,
citable from this journal and not reproducible from the repository. Both scripts now
read `data/review/phase4-blind-sample/` and fail loudly with the explanation; the
directory holds a README specifying the layout so a re-collected pass lands in git.
Phase 5's "every number reproducible" condition cannot be checked for the ceiling until
that happens, and `docs/charter.md` says so next to the box.

**What changed in our thinking.** The tooling was supposed to be plumbing for numbers
that do not exist yet; instead, building it forced three reads of the item set that
review had not: the label distribution (the floor test), the vocabulary tables (the
diacritics audit), and the continuation gold strings next to real model output (the
classifier). Each turned up something the blind reviewers structurally could not see,
because a reviewer answering one prompt at a time never sees that every ML is Spanish,
never compares a Phase 4 string against a pilot string, and never sees a model's
"un coffee" beside the gold "las revistas". Finding 3 also reframes the 2026-08-24
escape-hatch entry: the reviewers' island completions were the visible symptom, but the
mechanism is exact-string matching against a noun the prompt does not constrain, and a
model producing the target construction with a different noun is the cleaner
demonstration. The construct-validity claim for continuation now rests on the violation
rate, a number the runbook computes, rather than on the cell score.

402 items, hash baf85c44 (candidate v1.0), disagreement rate unchanged (pilot 1/30;
Phase 4 sample as reported on 2026-08-24, now historical). 164 tests. 0 runs this
session.

## The post-run path automated; mypy extended past src/; one README overclaim found

**Date:** 2026-09-02

**Constraint on this session, stated up front.** No inference again, by instruction: the
goal was every remaining piece of *code* finished, so that what is left is the runs and
the prose they feed. Nothing here required a model, and none was called.

**The gate was already green, and that is the honest headline.** `ruff check .`,
`ruff format --check .`, `mypy src`, `pytest` (164 passed, 96% statement coverage), and
`csw-bench validate` (402 items) all passed before a line was touched. The library —
loader, schema, prompts, providers, cache, runner, scorer, results, stats, CLI — is
finished. The work below is not repair of that; it is the part of the project that sat
*after* the runs and would otherwise have been done by hand.

**What was built.**

- `scripts/finalize_phase4.py`. Writes `docs/results.md`, rewrites the README's headline
  block in place between HTML-comment markers from the same `Report` objects, and prints
  the digest of every number the PENDING RUNS sections of `findings.md` and
  `limitations.md` ask for: per task, which models sit above chance with an interval
  excluding zero; per task, the spread of above-chance means across T1/T3/T5 (the
  clustering-vs-scatter question those sections are actually about); and per model and
  task, the provider-error rate. It refuses to write under any item-set hash
  `docs/versions.md` does not name as v1.0, reading that hash from the same row
  `tests/test_shipped_set.py` pins the items on disk to.
- `run_phase4.sh` calls it, and its closing checklist went from seven manual steps —
  three of them transcribing figures between files — to bookkeeping plus prose, with
  every number named and sourced to a log file. The inline heredoc that built
  `docs/results.md` is gone with it; that construction truncated a committed document
  before running the command that filled it, so a failure at the end of a day and a half
  of inference left a stub behind.

**A flag written and then removed.** The first version took `--sensitivity RUN_B RUN_A`
and printed the prompt-sensitivity delta alongside the rest, which is a nicer single
digest and also a second bootstrap over a number `csw-bench report --compare` already
owns and `run_phase4.sh` already writes to `runs/logs/prompt-sensitivity.txt`. Removed:
the digest now points at that file and at `runs/logs/escape-hatch.txt` for the
violation-production rate, on the same one-owner-per-job rule that keeps the escape-hatch
classifier out of this script.

**Type checking extended past `src/`.** `mypy src` was the enforced command, so
`scripts/` — 2,300 lines, including the tools that run *after* the inference — was never
checked. It had 100 errors. `mypy src scripts` is now the command in CI, `docs/charter.md`, and
the runbook, and it passes. Two of the three offending files are the item builders, and
they are excluded in `pyproject.toml` rather than fixed, with the reason written at the
exclusion: the item set is frozen and hash-pinned, so those 1,700 lines must never run
again, and annotating them would be churn against a released artifact. Every script that
can still legitimately run is checked.

The third, `scripts/score_phase4_review.py`, was fixed rather than excluded, because it
runs the moment a blind-review pass is re-collected. It dispatched on
`item.task_type.value` string equality and then read fields that only exist on the
matching subclass, which is why mypy could not narrow it — and which means a disagreement
between an item's `task_type` and its actual class would have silently taken the wrong
branch and scored the review against the wrong criterion. Now it matches on the item
class, the same way `scoring.score` does, so that disagreement is a type error. It also
divided by zero when the sample directory held files but no id in the sample had an
answer; that now exits with the reason.

**One overclaim found by reading the docs against each other.** `README.md` told a
linguist that `docs/taxonomy.md` carries "the attested and constructed examples." It
carries the constructed ones. Every shipping type's *attested* example is still
`[PENDING]`, all 402 items are `constructed`, and the taxonomy's own ratification
checklist has that box open — so the README was the only document in the repo claiming
otherwise, in the section written specifically for the reader most likely to check.
Corrected, and the checklist line sharpened while there: it said attested examples were
"pending corpus access," which reads as queued work, when the 2026-08-16 entry above
records that the login gate was tried, confirmed, and deliberately not pursued. What is
actually open is the other route the provenance rules allow — an example quoted and cited
from a published paper — and none has been collected.

**What changed in our thinking.** The previous entry closed by saying the tooling was
plumbing for numbers that do not exist yet, and that building it forced three reads of the
item set that review had not. The same thing happened one level up. Automating the
transcription step meant writing down exactly which number lands in which sentence of
which document, and that made the README's attested-examples claim visible — not by
auditing the README, but by asking what `finalize_phase4.py` was and was not allowed to
assert. A step that a person does by hand is a step nobody has had to specify; specifying
it is what exposes the claims that were never checked. The residue is that the last
manual work in this project is now genuinely interpretive — what the error pattern means
— rather than clerical, which is the only kind of manual step worth defending.

402 items, hash baf85c44 (candidate v1.0), disagreement rate unchanged (pilot 1/30;
Phase 4 sample as reported on 2026-08-24, historical). 164 tests. 0 runs this session.

## Phase 3 gate closed: prompt sensitivity, and the delta is mostly the scorer's

**Date:** 2026-09-08

**What was run.** `scripts/run_phase4.sh`, stage one: template b against the 30-item
pilot on qwen3:30b, the model with the cleanest template-a pilot (0 provider errors).
16.5 minutes, 28 provider calls, 2 cache hits, 0 provider errors, 51,845 output tokens.
`runs/pilot-qwen3-30b-b/`. Compared item-paired against `runs/pilot-qwen3-30b-a/` with
`csw-bench report --compare` (percentile bootstrap over per-item differences, 10,000
resamples, seed 0):

| Task | template a | template b | delta (a - b) | 95% CI | n |
|---|---|---|---|---|---|
| grammaticality_judgment | +0.778 | +0.778 | 0.000 | [-0.667, +0.667] | 9 |
| constrained_continuation | +0.000 | +0.000 | 0.000 | [+0.000, +0.000] | 7 |
| ml_identification | +0.000 | -0.286 | +0.286 | [+0.071, +0.429] | 7 |
| repair | +0.429 | +0.286 | +0.143 | [+0.000, +0.429] | 7 |

Above-chance units. Three tasks show no template effect the interval can distinguish from
zero. ML identification shows one: template a scores 0.286 higher, interval excluding
zero. Per `design.md` §5.5 a large delta is a finding, so it was checked for what it
actually measures before being reported as prompt sensitivity.

**It is mostly the scorer's sensitivity, not the model's.** Every one of the seven
template-b responses was read against the scorer's two mechanisms:

1. Template b never uses the phrase "Matrix Language" (it says "sets the grammatical
   frame"), so no response contains it, `_claimed_matrix_language` finds no anchor on
   any of the seven, and the scorer falls back to its whole-text last-mention heuristic.
   Three of the four responses scored "wrong or unclear Matrix Language" conclude, in
   their own final sentences, that Spanish is the frame -- csw-es-en-0008 ("all
   grammatical elements ... are Spanish"), -0026 ("confirms Spanish as the frame, not
   English"), -0027 ("making Spanish the frame") -- and are zeroed only because the word
   "English" occurs later in the text than the word "Spanish". The fourth, csw-es-en-0018
   ("Vio the el big house ayer en la calle", T3), ends "**Final Answer**: English" and is
   genuinely wrong.
2. Template b's instruction "not from how many words each language contributes" is
   paraphrased back by the model in all seven responses ("not just the number of words",
   "not just word count"), and `_LEXICAL_EVIDENCE` matches the paraphrase. Every
   template-b response is therefore capped at the 1-point "lexical-frequency reasoning"
   tier -- including csw-es-en-0017, whose actual argument is "the Spanish verb *leyó*
   alone is sufficient evidence". Point-neutral on this pilot only because the
   substring evidence matcher recognised 0 of 2 `required_evidence` strings on every
   response under both templates, so nothing had evidence points to lose.

Decomposed: three artifact zeros are 3 x (1/3) / 7 = 0.143 raw, 0.214 above-chance; the
one genuine wrong label is 0.071. The model's prompt sensitivity on this task is about
0.07; the other 0.21 is the scorer being tuned to template a's vocabulary. The other
three tasks, whose scorers match strings rather than prose, show none.

**Not patched mid-run.** Widening the anchor to "grammatical frame" and making the
lexical regex negation-aware are both real improvements, and both are exactly the kind
of fix the Phase 1 stress test warned about: written against the seven responses that
motivated them. The full-set runs are in progress under the current scorer; every raw
response is persisted, so a scorer revision can be applied to all runs at once with
`scripts/rescore_run.py` and recorded as one change, rather than landing between the
qwen3 and gpt-oss stages of a single results table. Decision deferred to Phase 5 close
and named in `docs/findings.md`; template a remains the headline template, so the
results table is unaffected either way.

**What changed in our thinking.** The prompt-sensitivity check was designed to measure
the model. On the one task where it found something, it measured the scorer: the
anchoring fix of 2026-08-27, built from template-a responses, encoded template a's
vocabulary as the definition of "made a claim". A paraphrased template is a test of the
scorer's paraphrase tolerance before it is a test of the model's, and the two cannot be
separated by the delta alone -- only by reading the responses, which is the third time
in this project that reading real model output has overturned what the number said.

402 items, hash baf85c44 (candidate v1.0), disagreement rate unchanged (pilot 1/30).
Phase 4 full-set runs in progress under `scripts/run_phase4.sh` with `scripts/watchdog.sh`.

## A cache hit that should not have happened: continuation stimuli are not distinct

**Date:** 2026-09-08

**What was seen.** Item 86 of the full qwen3:30b run came back `(cached)`. No Phase 4
item had ever been run, so the only way its request could be in the cache is that an
earlier item rendered to the byte-identical prompt. Counted across the item set:

| Task | Items | Distinct rendered prompts |
|---|---|---|
| grammaticality_judgment | 102 | 102 |
| constrained_continuation | 100 | **24** |
| ml_identification | 100 | 100 |
| repair | 100 | 100 |

By violation type, continuation has 11 distinct prompts over 34 T1 items, 14 over 33
T3 items, and **4 over 33 T5 items** ("Ella siempre" x 11, "Todos los dias yo" x 11,
"Cada manana yo" x 10). The pilot's own continuation prompts are all distinct; the
duplication is the Phase 4 generator's. Its 2026-08-24 periodicity fix made the
(prompt, gold) *pair* unique per item and stopped there, which is correct for every
other task, where the gold string is inside the stimulus. For continuation the stimulus
is the prompt alone, and the item's identity lives entirely in a gold string the model
never sees.

**What it means for the results.** At temperature 0 with a fixed seed, one prompt gets
one response, and the cache serves that response to every sibling. The 100 continuation
records in each full run are 24 model responses. A response can match at most one
sibling's gold string, so even a model that produced the licensed construction every time
could score at most 24/100 on this task, and the table's continuation n counts records,
not independent observations -- a four-to-one overstatement in the CI's effective sample.
The violation-production rate from `scripts/continuation_escape_hatch.py` is over 24
distinct responses per run, not 100. This compounds the exact-string finding of
2026-09-01 rather than replacing it: continuation was already measuring string
coincidence, and it now does so over a quarter of the stimuli it appears to.

**Not fixed, for the same reason as the other three defects.** The full runs are in
progress against this set under its recorded hash, and regenerating 100 items would
ship them unreviewed. Instead `scripts/finalize_phase4.py` now prints a stimulus-
multiplicity block directly under the results table naming every affected cell, computed
from the item set rather than typed, so the n column is read correctly where it is read.
The escape-hatch classifier states the distinct-stimulus counts above its buckets. A v1.1
continuation task needs a distinct prompt per item, and probably a prompt long enough to
close the island escape hatch at the same time.

**What changed in our thinking.** The cache was built so a rerun never re-bills. It
turned out to be a duplicate-stimulus detector: a cache hit on a never-run item is a
proof, not a warning, that two items are the same experiment. Nothing in validation
checks that rendered prompts are unique across items, and it should -- but adding that
check now would fail against the shipped set, so it is recorded here as a v1.1 gate
rather than added as a test the current data cannot pass.

402 items, hash baf85c44 (candidate v1.0), disagreement rate unchanged (pilot 1/30).
Full-set runs in progress.

## The first full-set run died at item 377: a GPU out-of-memory the harness did not isolate

**Date:** 2026-09-09

**What happened.** `runs/full-qwen3-30b-a`, 01:31, item 377 of 402 (a T5 repair
prompt, nothing unusual about it): Ollama's Metal runner failed with
`Insufficient Memory (kIOGPUCommandBufferCallbackErrorOutOfMemory)`, then
`GGML_ASSERT([rsets->data count] == 0) failed`, and the server logged
`llama runner terminated, exit status 2` and answered the request with HTTP 500. The
Python SDK raised `ollama.ResponseError`. `OllamaProvider.complete` catches
`httpx.TimeoutException` and nothing else, so the exception went straight through
`runner.py`'s per-item isolation, the CLI, and `set -e` in the runbook. The stage ended
with 376 records and no `run.json`; the watchdog noticed the runbook gone and exited
cleanly. The kernel's memory-pressure level never left "warning" (6-13% free): the GPU
command-buffer allocator runs out before the kernel does, and the watchdog cannot see
it.

**The harness gap, fixed.** This is the same class of failure as the 2026-08-24 hang
and the earlier per-item isolation: a provider that answers badly rather than not at
all. `complete` now maps `httpx.HTTPError` and `ollama.ResponseError` to
`ProviderError`, so a runner crash records one errored item (the next request reloads
the runner) and the stage continues. Two tests pin it, one on the exact `ResponseError`
observed. No scoring code changed.

**Cost.** None to the data: every one of the 376 completed responses is in the cache,
and the relaunched stage served them back without a model call before continuing at
item 377. The 376 records were re-scored from identical responses, which is the
cache-rerun reproducibility gate exercised at full scale for free.

402 items, hash baf85c44 (candidate v1.0), disagreement rate unchanged (pilot 1/30).
Full-set runs resumed.

## Phase 4 runs: two of three models complete; the third paused at 270 of 402

**Date:** 2026-09-10

**What ran.** `scripts/run_phase4.sh` under `scripts/watchdog.sh`, 2026-09-08 22:07 to
2026-09-09 23:28, relaunched five times. `runs/full-qwen3-30b-a` and
`runs/full-gpt-oss-20b-a` are complete (402 records each, `run.json` written) and
committed with this entry. `runs/full-deepseek-r1-32b-a` reached item 368 of 402 before
the machine rebooted; 270 of its responses are in the cache, 98 errored records are
retried on resume (97 `ml_identification` timeouts at 300 s each and one runner crash),
and the stage was stopped at the principal's request at 23:28 with 15 records replayed.
It resumes from `scripts/run_phase4.sh` and costs about nine hours, almost all of them
the timeouts; the 300 s limit is a protocol setting and was not shortened to save them.

**What broke, in order.**

1. *GPU out-of-memory at item 377* (previous entry): the one harness gap, fixed.
2. *ComfyUI.* The relaunched qwen3 stage timed out on items 377-382 in a row at exactly
   300 s each, then crashed the Ollama runner again. The machine was carrying ComfyUI
   (about 18 GB) and 22 GB of swap alongside the 18 GB model: the video pipeline's launch
   agent (`com.mannie.videogen`) restarts ComfyUI every 60 s on AC power, and had been
   doing so under every run since the pilot. Killing ComfyUI by hand lasted a minute.
   With the principal's approval the agent was unloaded (`launchctl bootout`) for the
   duration; the runbook now refuses to start while ComfyUI is up and its header carries
   the unload and reload commands. The runner crashed eight times in total under the
   collision, seven in the qwen3 stage and once in deepseek's (item 130); every crash cost
   one errored record and nothing else, which is the 2026-09-09 fix doing its job.
3. *A reboot at about 22:15 on 2026-09-09*, cause unrecorded (no panic report), at
   deepseek item 368. It reloaded the launch agent, which relaunched ComfyUI.
4. *The watchdog killed the relaunch in preflight*: it measured "no progress" from the
   stage log's mtime, which predated the reboot by 40 minutes. It now measures from its
   own start (commit a8381de). The next relaunch ran clean.

**qwen3:30b on its final pass: 402/402, 0 errors.** The 25 errored items from the
contended passes were retried on a clean machine (377 cache hits, 25 model calls, 23
minutes). Every one of the 25 had been a 300 s timeout or a runner crash, and every one
answered at normal speed once the model had the machine to itself: the "degenerate
generation loop" the timeout message suggests was, on this machine, another process's
memory.

**gpt-oss:20b: 402/402, 77 errored.** 75 are the model exhausting its 8192-token output
budget before emitting any content, 1 an empty response, 1 a response with no usage
accounting; by task, judgment 10, continuation 19, `ml_identification` 42, repair 6.
Not retried: the stage closed with `run.json`, budget exhaustion at temperature 0
reproduces, and raising the budget mid-table would change the protocol for one model.
Recorded as the provider-error rate the table carries beside every cell, and in
`docs/limitations.md` as a selection effect on that model's scored cells.

**deepseek-r1:32b, partial.** 97 of the 97 `ml_identification` items it reached timed
out; the pilot's 100% pattern holds through item 368. Every other item it reached
completed, the one runner crash aside. The 300 s timeout and gpt-oss:20b's 8192-token
budget are the same failure seen from two sides: a reasoning model that spends its whole
budget thinking is indistinguishable from a hung one, and the harness records both as
provider errors rather than as answers.

**What the two finished runs say** is written in `docs/findings.md` ("Headline result",
"Error patterns by violation type") from `scripts/finalize_phase4.py --check` over the
two runs; the digest is regenerated, not retyped, when the third run lands. The short
version: both models above chance on judgment and repair, at zero on continuation,
below the constant-label floor on `ml_identification`; errors cluster on T5 in every
task that has them, in both models, and every T5 `ml_identification` failure reads the
bare English verb as the frame-setter.

**What changed in our thinking.** The dominant failure source across a day and a half of
inference was the machine, not the models or the harness: every crash and every qwen3
timeout traced to a process that was not this project's. The watchdog was built to
catch the model misbehaving and caught none of this, because memory pressure from a
foreign process reads as "warning" right up until the GPU allocator fails. A run's
operational log is data about the numbers it produced: the 25 qwen3 retries would have
been reported as model errors if the cache had not made retrying them free.

402 items, hash baf85c44 (candidate v1.0), disagreement rate unchanged (pilot 1/30).
Two full runs committed; deepseek-r1:32b resumable.

## The claim anchor revised, every committed run rescored, 20 records moved

**Date:** 2026-09-10

**What was tried.** Writing up the `ml_identification` row from the two finished runs,
both models sat below the constant-label floor (qwen3:30b -0.150, gpt-oss:20b -0.164).
Before reporting that as a model result, every zero-scored response in both runs (49)
was read. Twelve of qwen3:30b's thirty conclude Spanish, explicitly and repeatedly, in
the sentence the scorer zeroed them on: "a classic case of Spanish as the Matrix
Language with English lexical items inserted". The 2026-08-27 anchor takes the language
name nearest the last "matrix language" mention; "English" six characters after the
phrase beat "Spanish" eight characters before it. One credited response failed the other
way: csw-es-en-0354 says "English is the Matrix Language" eleven times and was credited
because its closing table row reads "English matrix language | Spanish embedded
content". gpt-oss:20b had three of the first shape ("Matrix Language: Spanish. Why
Spanish is the matrix language ...").

**The decision deferred on 2026-09-08 is made: the fix lands now, once.** The grounds
then were that a scorer change should not fall between stages of one table and that a
rule written against seven responses is suspect. Both still hold and both are met: no
run is scored under two scorers (every committed run was rescored from its persisted
responses in one pass, and the third run will be scored live under the same code), and
the rule was written after reading forty-nine zero-scored responses across two model
families plus every template-b response, then checked by diffing every record of every
run.

**The rule.** `_claimed_matrix_language` now collects explicit claims ("X is / as / sets
/ supplies the Matrix Language", "the Matrix Language (in the utterance ...) is X", "the
grammatical frame is (set by) X", the heading "Matrix Language: X") and takes the last
one; the nearest-name heuristic is the fallback when a response phrases no claim, and
whole-text last mention the fallback after that. "Grammatical frame" is template b's
wording, so the same change closes the half of the 2026-09-08 fix that was about
vocabulary. Negations match nothing by construction: the verb and the name must be
adjacent to the phrase. A heading match sitting inside a phrased claim ("English as the
Matrix Language | Spanish provides ...") is discarded, which a constructed test case was
needed to find.

**What moved**, `scripts/rescore_run.py` over every committed run, diffed record by
record against a snapshot:

| Run | Records moved | Direction |
|---|---|---|
| full-qwen3-30b-a | 13/402 | 12 up (0 to 1), 1 down (csw-es-en-0354) |
| full-gpt-oss-20b-a | 3/402 | 3 up |
| pilot-qwen3-30b-b | 3/30 | 3 up (0008, 0026, 0027: the three artifact zeros of 2026-09-08) |
| pilot-gpt-oss-20b-a | 1/30 | 1 up (0007) |
| pilot-qwen3-30b-a, pilot-deepseek-r1-32b-a | 0/30 | |

Every moved record is one that was read and classified before the rule existed; nothing
moved that was not on that list. Response text, cache flags and errored flags are
byte-identical before and after.

**What changed in the numbers.** `ml_identification` above-chance: qwen3:30b -0.150 to
-0.095 [-0.135, -0.060]; gpt-oss:20b -0.164 to -0.138 [-0.198, -0.086]; pilot
gpt-oss:20b -0.10 to 0.00. Prompt-sensitivity delta on `ml_identification`: 0.286
[+0.071, +0.429] to 0.071 [+0.000, +0.214], which is the single genuine wrong answer
(csw-es-en-0018) the 2026-09-08 decomposition predicted. `docs/results-pilot.md`, the
README's pilot row and `runs/logs/prompt-sensitivity.txt` are regenerated from the
rescored runs. Continuation, judgment and repair scores are untouched by construction.

**Not changed, and counted.** The lexical-frequency detector's negation blindness ("not
from how many words each language contributes", template b) caps three template-b
records at the label point they earn anyway, and fires once in the headline runs on "the
order is mostly Spanish" (csw-es-en-0102). The hedge detector fires once inside a
reasoning preamble that then commits ("or it depends on the speaker", csw-es-en-0242).
One record each; both left as named instances rather than rules written against one
response. The evidence matcher credited 0 of 158 scored responses in the two full runs.
That one is not a fix for v1.0 at all: it is the matcher the construction-time ceiling
and the pilot were scored with, the evidence strings are part of the frozen items, and
widening it after reading model output is the circularity `docs/design.md` §5 names. Its
consequence is stated where the number is read: under the v1.0 scorer no model can score
above the `ml_identification` floor, and the row is the wrong-label rate.

**What changed in our thinking.** Each anchor was the fix for the previous anchor's
failure, and each encoded the phrasing that motivated it: first mention, then last
mention, then nearest name, now explicit claim. The sequence is not converging on a
parser; it is enumerating the shapes two model families produce under two templates. The
honest description of `score_ml_identification`'s label check is a string matcher whose
recall has been verified on that output and no other, and its docstring now says so. The
artifact this time ran in a model's favour for the first time, which is the argument for
reading the credited responses as well as the zeros whenever a number is surprising.

402 items, hash baf85c44 (candidate v1.0), disagreement rate unchanged (pilot 1/30).

## Phase 4 closed and v1.0 tagged: the third run, and what three models say

**Date:** 2026-09-11

**What ran.** `runs/full-deepseek-r1-32b-a`, resumed from cache under
`scripts/run_phase4.sh` and `scripts/watchdog.sh`. A first resume on 2026-09-10 (12:16
to 18:00) reached item 246 and was stopped at the principal's request; the second
(23:53 to 09:05, 9 h 12 min) ran to 402/402 with no crash, no watchdog action, and the
launch agent unloaded throughout. 131 provider calls, 271 cache hits, 100 provider
errors: every `ml_identification` item timed out at 300 s, on both attempts, and nothing
else errored. The runbook then ran `scripts/continuation_escape_hatch.py` and
`scripts/finalize_phase4.py`, which wrote `docs/results.md` and the README headline block
from the three runs; no figure in either was typed.

**The third model.** Judgment +0.980 [+0.941, +1.000], 101 of 102 pairs, the one miss on
T5. Continuation 0.000, and all 100 continuations are monolingual Spanish ("un libro
interesante en la libreria"): the abandon-switching escape the 2026-08-24 review sample
showed in 18 of 30, now at 100 of 100 for one model. ML identification: no scored items.
Repair +0.310 [+0.220, +0.400], with T1 +0.758 against T3 +0.091 and T5 +0.088.

**The repair row was read before it was reported.** The zero-scored T3 answers are
translations: "Compró el regalo ayer" for "Compró the el gift ayer" (gold "Compró the
gift ayer"), 30 of 33 dropping the English island entirely. The T5 answers substitute a
native verb ("imprimió" for "print"), the escape already logged for qwen3:30b on
2026-08-27. The T1 score is not the exception it looks like: deleting every English word
coincides with the minimal repair when the only English word is the article, so 25 of 33
reach the gold by a strategy that never located anything. The same two escapes exist in
the other models at lower rates, island-dropping T3 repairs 30/33, 18/33, 6/33 and
loanword-avoiding T5 repairs 20/34, 19/34, 15/31 for deepseek-r1:32b, qwen3:30b,
gpt-oss:20b. Counted with a token heuristic over the extracted answers, not a parse;
the samples read the same way the counts do.

**What three models say**, `docs/findings.md` "Headline result" and "Error patterns by
violation type": all three above chance on judgment; none distinguishable from chance on
continuation, with 0 of 281 scored continuations reproducing a recorded violation; the
two that answered ML identification sit below the constant-label floor, and the evidence
matcher credited 0 of 158 responses; all three above chance on repair, in a spread from
+0.787 to +0.310. Errors cluster by violation type in every model and T5 is in the
cluster every time. qwen3:30b and gpt-oss:20b show the 4-M split in their error profile
(system-morpheme and island violations handled, bare content morphemes not).
deepseek-r1:32b is a third profile, recognition at ceiling and production that retreats
to Spanish, which is the failure mode the README's first paragraph names and which the
judgment task alone cannot see.

**Phase 5 closed.** README banner, `docs/findings.md`, `docs/limitations.md` ("Numbers
from the full runs", the section the runbook calls PENDING RUNS), `docs/charter.md` Phase 4 and
Phase 5 boxes, `docs/versions.md` v1.0 date. Tag `v1.0` on this commit. Two Phase 5
boxes stay open because no one on this project can close them: a reader with no
linguistics stating what is measured from the README, and a linguist finding the
grounding in a minute. The README sections built for each exist; the readers do not yet.

**What changed in our thinking.** The project now has three documented escape hatches,
one per production task: a licensed island in continuation, a native verb in T5 repair,
a whole-utterance translation in T3 repair. Each satisfies the surface requirement
(produce a licensed sentence) without engaging the constraint under test, and each was
found by reading zero-scored output, never by the score. A per-cell number can be
reached by a strategy that never touches the construct (deepseek-r1:32b's T1 repair),
and a model can be first on one task and last on another for the same underlying
behaviour (recognition intact, production normalising). The benchmark's value is the
four-task design plus the reading, not the table; the table on its own would have ranked
the model that abandons code-switching as the best judge of it, which is true and
useless.

402 items, hash baf85c44, tagged v1.0, disagreement rate 1/30 (pilot, unchanged).

**Addendum, same day.** The vault sync's read of the repo caught three things the close
missed: `pyproject.toml`, `__version__`, and `CITATION.cff` still said 0.1.0;
`ERRATA.md` still said the set was unreleased; the README's license section described
the corpus-derived rule without saying that all 402 shipped items are constructed and
MIT. Fixed in the next commit and the `v1.0` tag moved onto it before any push (the tag
had never left this machine). The item-set hash is unchanged.
