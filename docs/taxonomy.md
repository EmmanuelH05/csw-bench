# Violation taxonomy

> **Status, 2026-08-16: type structure finalized (T1, T3, T5); full ratification still
> open.** The `docs/charter.md` Phase 1 bar — at least three mutually exclusive types, each with
> a citation and a stated diagnostic — is met, and the type *count and membership* are not
> expected to change again. The stricter internal ratification checklist below (page-level
> citation checks, attested examples, per-type populability at the new item target) is not
> yet complete and blocks Phase 2, per `design.md`'s "Blocking before Phase 2" list. The
> `ViolationType` enum was updated to match the finalized type structure this session —
> code follows a settled type-structure decision here, not a theory decision the code
> made first.

## What this file is for

`matriz` holds out **entire violation types** from training and tests whether the
constraint transfers. That only means something if the types are principled, mutually
exclusive, and each populated densely enough to leave usable training data when one is
removed. So this taxonomy is designed against three pressures at once: theoretical
grounding, decidability by a human annotator, and populability from Spanish/English
corpora.

A type that fails any of the three does not ship.

## Citation practice

Citations here are to work and named principle. Page-level citations are marked
`[VERIFY: page]` and must be checked against the physical source before Phase 2 opens —
no item may cite a page number that has not been read. Keys refer to `references.bib`.

**Work-level verification, 2026-08-16.** All five theoretical citations
(@myersscotton1993duelling, @myersscotton2002contact, @myersscotton2000fourm,
@macswan1999minimalist, @poplack1980sometimes) checked against publisher/journal records
for correct year, venue, volume, and pages. All confirmed. One real error was found and
fixed: the Bangor Miami corpus citation in `references.bib` did not match the citation
TalkBank's own access page requires (wrong year, wrong author list, no DOI) — corrected,
since using the wrong citation would not have satisfied the corpus's own mandatory-
attribution license term.

**Page-level `[VERIFY: page]` items remain unresolved.** @myersscotton1993duelling and
@myersscotton2002contact are not available online — both are login-gated (Internet
Archive controlled lending) or paywalled, and no PDF exists in this repo or environment.
This blocks the SMP-wording check that decides C8 and the coordinator/preposition 4-M
classification that decides C21/C26. One partial, secondhand [S] finding survives the
attempt and is recorded for whoever does the page check: Myers-Scotton's own published
short-summary page states Spanish complementizer *que* is classified as a late bridge
system morpheme — corroborating, not proving, the bridge classification this taxonomy
already assumes for *of* and coordinators by analogy. It also states explicitly that
prepositions are *not* uniformly system morphemes ("some prepositions are content
morphemes... others are SMs"), which means the bridge classification assumed for *of*
throughout `ordering-stress-test-v2.md` is a weaker inference than the parallel
complementizer case and should get first priority when page access is available.

## Identifying the Matrix Language

Every type below presupposes an ML assignment, so the procedure is fixed here rather than
left to each annotator.

The ML is identified by the two criteria in @myersscotton1993duelling:

1. **Morpheme order.** Surface morpheme order in mixed constituents follows the ML.
2. **Syntactically relevant system morphemes.** These come from the ML.

Where the two criteria conflict, or where an utterance is too short to establish a frame,
the item is **excluded** rather than adjudicated. The size of the excluded set is a
reported statistic (see `design.md` § threats) because it bounds how much of the
benchmark rests on contested ML assignment — the unmitigable threat named in
`limitations.md`.

## The 4-M distinction this taxonomy leans on

@myersscotton2000fourm splits morphemes four ways, and two of the splits do real work here:

| Morpheme type | Property | Used by |
|---|---|---|
| Content | Assigns or receives thematic roles | T5 |
| Early system | Conceptually activated with its head; indirectly elected | T1 |
| Late bridge system | Structurally assigned within a maximal projection | T1 |
| Late outsider system | Depends on information *outside* its head constituent | T1 (theoretical only — see below) |

> **Stale as originally written, corrected 2026-08-16.** This table and the paragraph
> below it predate two later changes and are updated to match the taxonomy's final state,
> not its Phase 1 starting point. Originally: T1 took only early system morphemes, and a
> now-dropped T4 took late outsider ones, with the early/outsider split between them
> called "the single most load-bearing decision in this document." T4 was folded into T1
> for populability (below); T1 was subsequently widened to admit *any* EL system
> morpheme — early, bridge, or outsider. In practice only early and bridge morphemes
> populate T1; no attestable Spanish/English configuration reaches outsider (see T1's
> widening note below and `limitations.md` § "The 4-M outsider distinction is not
> tested"). The early/outsider *gradation* the original split preserved is lost — that
> cost is real and is where it is actually recorded now.

---

## T1 — EL system morpheme in ML frame

> **Widened during Phase 1 from "early system morpheme" to *any* EL system morpheme.**
>
> The narrow version left a hole. Cutting T4 removed the outsider type, bridge was never
> covered, and T1 admitted only early morphemes — so no type caught an EL-sourced late
> system morpheme. `*el libro **of** Juan` fires nothing: not T3 (no island), not T2
> (N+PP is Spanish order), not T1 (*of* is not early), not T5 (not a content morpheme).
> A violation MLF is explicitly committed to predicting went unclassified.
>
> T1 now covers all three system-morpheme classes on paper. The 4-M class is recorded as
> a per-item metadata field (`system_morpheme_class`).
>
> **Correction, round 2.** An earlier version of this note claimed the widening "recovers
> most of what T4's removal cost." **That is false and is retracted.** Widening closes the
> late *bridge* hole (C21, `el libro of Juan`) — that is its one unambiguous win. It does
> **not** recover late *outsider* coverage, for the same reason T4 died: an EL affix on an
> ML stem is unattestable (C10), an EL affix on an EL stem is excluded by question 4, and
> fused case forms are unsegmentable (C24). In practice `system_morpheme_class` will
> contain no `late_outsider` values.
>
> The honest statement is that the taxonomy tests early and bridge system morphemes and
> does not test outsider ones. `limitations.md` says so.
>
> Net effect: the taxonomy is now a clean **system/content** split — T1 for system
> morphemes, T5 for content morphemes — which is MLF's own primary division.

**Prediction.** System Morpheme Principle, @myersscotton1993duelling. `[VERIFY: page —
the SMP's exact wording decides C8 and blocks ratification]`

> ⚠ **New finding, secondhand only — the SMP may not cover early or bridge morphemes at
> all.** Two independent secondary sources (an honors thesis and a 2019 *Open Linguistics*
> paper on Myers-Scotton's model, both found via search, neither read directly — WebFetch
> was blocked on both by 403s from ResearchGate/academia.edu/Oberlin/De Gruyter) quote the
> SMP as: *"In ML+EL constituents, all system morphemes which have grammatical relations
> external to their head constituent will come from the ML"* (@myersscotton1993duelling,
> p.83; restated @myersscotton2002contact, p.59). One source glosses this directly:
> "outsider late morphemes are the only system morphemes which have grammatical relations
> external to their head, and therefore will come from the ML."
>
> Taken at face value, that wording constrains only morphemes with grammatical relations
> *external to their head constituent* — which is the 4-M model's own definition of
> **late outsider**, not early or bridge. Early system morphemes are conceptually
> activated *with* their head (internal); late bridge morphemes are structurally assigned
> *within* a maximal projection (also internal, by the table above). If this reading
> holds, **T1's citation is only fully licensed for the outsider cases this taxonomy
> cannot populate (C10, C23, C24)**, and the early/bridge violations that make up nearly
> all of T1's actual item pool (determiners, plural marking, `of`, `'s`) would need a
> *different* citation — plausibly the frame-building mechanism itself (Matrix Language
> Principle / Uniform Structure Principle) rather than the SMP by name — or the secondary
> sources' gloss is incomplete and a fuller reading of the primary text resolves it.
>
> **This is not decided here and the taxonomy is not changed on the strength of a search
> summary.** It is the single highest-priority `[VERIFY: page]` item in the document,
> ranked above the C8/C9 page checks that cite it, because it bears on T1's grounding as a
> whole rather than one contested case. Needs the physical or library-access text of
> @myersscotton1993duelling p.83 and @myersscotton2000fourm, read directly, not summarized.

**Claim.** In a mixed constituent framed by the ML, system morphemes come from the ML.
A system morpheme sourced from the EL is a violation.

**Diagnostic.** Four questions. All four must be yes.

1. Is an ML frame established for the constituent by the ML criteria above?
2. Is the morpheme in question a system morpheme by the 4-M test (early, late bridge, or
   late outsider)? Record which — it is a metadata field, not a type.
3. **Is the morpheme actually present in the string?** T1 fires on the *presence* of a
   foreign system morpheme, never on the *absence* of a native one. A missing ML morpheme
   is not an imported EL one.
4. Is it sourced from the EL, and does it **attach to ML material** — meaning its host,
   or the constituent it takes scope over, is ML-sourced? (Added round 2: this phrase was
   undefined and silently decided seven of twenty-six cases.)
5. **Is the constituent an EL island?** If yes, T1 does not apply.

   > **Added round 2.** T2 and T5 both had island exclusions; T1 did not. Under the
   > narrow T1 that was harmless, because early system morphemes attach to their own EL
   > hosts. Widening T1 to admit bridge morphemes broke it — bridge morphemes attach
   > *outward* by definition, so T1 began firing on licensed EL islands such as
   > `Fui a la casa of my friend` (C22). The leak was created by the widening, not
   > inherited.

Question 3 was added after the stress test found T1 firing on both `los books` (EL plural
present) and \*`los book` (EL plural absent) — incoherent, since the SMP is about the
source of a morpheme that surfaces. This is what reassigns C8 to T5, on the diagnostic's
own terms rather than by vote.

Determiners and plural marking are the productive probes for Spanish/English.

**Constructed example.** Spanish ML, English EL:

> \*Compré **the** libros ayer.

The determiner is an early system morpheme and comes from the EL, inside a
Spanish-framed NP. Contrast the licensed *Compré los libros ayer* and the licensed EL
island *Compré the books yesterday*.

**Attested example.** `[PENDING: Bangor Miami — the sole item source, per corpora.md §4.5
— must be a real corpus token with a citation, not a constructed sentence relabelled]`

**Populability.** Good. Determiner-noun switching is among the most frequently discussed
phenomena in the Spanish/English literature, which means attested tokens are findable.

---

## T2 — ML constituent order violated

> **RESOLVED, 2026-08-16 — T2 does not ship.** Kept as a documented section, like T4
> below, so the reasoning survives for anyone who asks why a four-type taxonomy became
> three. Full argument in "⚠ T2 dropped" below; this section is retained as the historical
> diagnostic, not an active type.

**Prediction.** Morpheme Order Principle, @myersscotton1993duelling. `[VERIFY: page]`. The
MOP remains load-bearing elsewhere in this document — it is one of the two criteria used
to **identify the Matrix Language** in the first place (see above). Dropping T2 removes it
as an independently held-out *violation type*; it does not remove it from the taxonomy's
foundations.

**Claim.** Surface morpheme order in a mixed constituent follows the ML. Order imposed by
the EL is a violation.

**Diagnostic, final form (never shipped as an active type).**

1. Is an ML frame established?
2. **Does the constituent contain EL material at all?** If no, out of scope — a
   monolingual word-order error (C4).
3. **Is the constituent an EL island?** If yes, T2 does not apply (C19).
4. Does the surface order match what the ML requires?
5. **Is the deviation attributable to EL *frame* order — as opposed to being the
   obligatory linearization of an individual EL morpheme present in the string, or of
   EL-internal compounding?** If the latter, T2 does not apply.

   > **Tightened, round 2** (`ordering-stress-test-v2.md` Part 2). The original q5 —
   > "attributable to EL order rather than a licensed ML alternative" — offered a false
   > dichotomy. It does not distinguish general EL frame pressure (a real T2 case, e.g.
   > C5) from the linearization forced by one lexical item's own requirements (C9's
   > possessive `'s`, which is prenominal in English by lexical entry, not by any general
   > frame effect) or from EL-internal compound order surfacing inside a non-island
   > constituent (C19, `movie theater`). Under the untightened q5, C9 and C22 — the same
   > bridge-morpheme class, one with an order side-effect and one without — landed in
   > *different* held-out types for no principled reason. The tightening fixes both C9 and
   > C19 by the same clause, independently of which way the C9 type debate went, which is
   > why it is applied here regardless of the type-count outcome.

Under the tightened diagnostic, **C9 fails q5 and resolves to T1** (late bridge system
morpheme), not T2. See "⚠ T2 dropped" for what that leaves T2 to test.

**Constructed example (retained for the record; no longer licensed).** \*`Yo veo lo en la
tienda` — this was T2's own headline example and **fails question 2**: it contains no EL
material at all and is a monolingual Spanish clitic-placement error (the C4 exclusion,
added earlier in Phase 1, retroactively invalidated this example without anyone noticing
until the variety check). A type whose canonical example fails its own diagnostic was
never on solid ground.

Adjective placement was rejected earlier for a different reason: prenominal and
postnominal adjectives are both licensed in Spanish with a meaning difference.

---

## T3 — Ill-formed EL island

**Prediction.** EL Island Trigger Hypothesis, @myersscotton1993duelling. `[VERIFY: page]`

**Claim.** When an EL morpheme is not licensed in a mixed constituent, the constituent
must be completed as a well-formed EL island — internally EL, structurally complete.

**Diagnostic.**

1. Is there a stretch of EL material forming a constituent **when any intruding ML
   material is set aside** (constituenthood modulo intrusion)?

   > **Corrected after round 2.** This question originally demanded *contiguity*, which
   > contradicted question 3: q1 required the EL stretch be unbroken, q3 required ML
   > material inside it, and ML material inside a stretch breaks contiguity. The two
   > questions could not both be satisfied. T3 was effectively empty — **its own
   > canonical example failed its own first question**, and C3, round 1's flagship clean
   > case, returned no type at all.
   >
   > Constituenthood-modulo-intrusion does the job contiguity was added for (it still
   > rejects C13's phantom island, where scattered EL material is not a constituent under
   > any grouping) without excluding the intrusion that defines the type.
2. Is it internally well formed *by EL grammar*? **If no, and no ML material intrudes,
   the item is out of scope** — internally broken EL with no ML involvement is an English
   grammar error, not a code-switching violation. Without this terminator, C16
   (\*`book the`) falls through every type and receives no assignment at all. Same defect
   as the C4 hole, in the other language.
3. Does it contain ML system morphemes, or does its boundary cut a constituent that EL
   grammar requires be complete?

   > ⚠ **New, unresolved — found 2026-08-16 during Phase 2 pilot item review, not yet
   > fixed.** Applied literally, this diagnostic can fire on cases it was never meant
   > for. Take a plain T1 violation, `*Compré the libros ayer`: the EL stretch modulo
   > intrusion is `the` alone (q1: yes, a determiner is a constituent); it is internally
   > well-formed English (q2: yes); and an English determiner's boundary "cuts a
   > constituent that EL grammar requires be complete," since a determiner obligatorily
   > takes an NP complement (q3: yes, on this reading) — returning **T3**, not T1, for
   > every T1 item in the pilot set. The same literal reading returns T3 for T5's bare-verb
   > items too (a verb's VP boundary being "cut"). Because T3 sits first in the
   > mutual-exclusivity ordering, a diagnostic that fires this loosely would silently
   > swallow other types. The narrow reading — the one every worked example in this
   > document and every Phase 2 T1/T5 item was built against — is obviously intended, and
   > T3's canonical example is a genuine multi-word EL constituent, not a bare function
   > word. But the diagnostic as literally worded does not itself enforce that narrowing,
   > which matters because mutual exclusivity is the entire basis for `matriz`'s held-out
   > split. Not fixed here: any change to a shipped diagnostic requires the full
   > case-set re-run this document's own house rule demands (see "Mutual exclusivity"),
   > and that has not been done for this fix. Candidate fix, unapplied: require the q1
   > stretch to be a multi-word constituent whose lexical head is EL-sourced, which would
   > exclude a bare function word from ever satisfying q1 on its own.

A yes to 3 is the violation. Note this type is about the island's *internal* integrity,
which is what keeps it distinct from T1 — T1 concerns a system morpheme inside an
ML-framed constituent, T3 concerns ML material intruding into EL-framed material. The
direction of intrusion is the discriminator.

**Constructed example.** Spanish ML with an intended English island:

> \*Me dio **a el book** ayer.

The intended island *a book* is broken by the ML determiner. Contrast the licensed island
*Me dio a book ayer* `[VERIFY: this contrast against the literature — the licensing of a
bare English NP here is exactly the kind of judgment that needs a second reviewer]`.

**Attested example.** `[PENDING]`

**Populability.** Good. EL islands are well attested and frequently discussed.

---

## T4 — EL late outsider system morpheme

**Prediction.** 4-M model, @myersscotton2000fourm; outsider late system morphemes are
supplied by the ML. `[VERIFY: page]`

**Claim.** Morphemes depending on information outside their head constituent — subject-verb
agreement, structural case — come from the ML. An EL-sourced one is a violation.

**Diagnostic.**

1. Is an ML frame established?
2. Is the morpheme *late outsider* by the 4-M test — does its form depend on something
   outside its own maximal projection?
3. Is it sourced from the EL?

**Constructed example.** `[PENDING — see the risk below]`

**Attested example.** `[PENDING]`

> **RESOLVED — T4 is folded into T1. This type does not ship.**
>
> Two independent lines of evidence. The populability argument below, plus the ordering
> stress test's failure to construct even a *hypothetical* clean case: every attempt
> produced something unattestable (\*`camina-s`) or better described as T1. See C10 in
> `ordering-stress-test.md`.
>
> At the time this was decided, the taxonomy still shipped T2, so folding T4 into T1 kept
> four types and cleared the (then-current) `docs/charter.md` minimum. **T2 was itself dropped
> later in Phase 1** (see "⚠ T2 dropped" below), so the taxonomy now ships three types —
> T1, T3, T5. The reasoning for folding T4 stands independently of that later change: T4
> would not have been populable whether the taxonomy ended up with three types or four.
> The cost is real: the 4-M early/outsider distinction is what makes MLF's predictions
> graded rather than binary, and we lose it. Recorded in `limitations.md`.
>
> Section retained rather than deleted, so the reasoning survives for anyone who asks why
> a five-type taxonomy became three.

**⚠ Populability risk — the argument that killed it.** English inflectional
morphology is impoverished. Subject-verb agreement reduces to third-person singular
*-s*, and structural case surfaces only on pronouns. That gives a thin set of probes for
an English EL, and English-EL-into-Spanish-ML is the more common direction in the
corpora. The reverse direction (Spanish EL into English ML) has richer agreement
morphology to work with but is less attested.

The alternative — keeping T4 small and documenting its low count — was rejected because a
type `matriz` cannot meaningfully hold out is not a type, it is a rounding error with a
name.

Deciding this before items were built, rather than discovering it at item 200, is what
Track A and the stress test were for.

---

## T5 — Congruence failure / bare form

**Prediction.** Blocking Hypothesis, @myersscotton1993duelling. `[VERIFY: page]`

**Claim.** An EL content morpheme not congruent with the ML at the relevant levels of
abstraction is blocked. Surfacing it anyway — typically as a bare, uninflected form where
the ML obligatorily supplies morphology — is a violation.

**Diagnostic.**

1. Is an ML frame established?
2. Is the element an EL *content* morpheme (assigns or receives a thematic role)?
3. Does the ML obligatorily require morphology **on the EL element itself** that is
   absent? The qualifier matters: Spanish gender is realised on the determiner, not
   affixally on the noun, so without it the diagnostic flags licensed cases like
   `la table` (C11).
4. Is the element outside any EL island? (Inside an island it is licensed, and the item
   is T3 or nothing.)

Question 4 is the tie-break that keeps T5 from collapsing into T3.

**C8 lands here**, not in T1. \*`Compré los book ayer` has no EL system morpheme at all —
the determiner is Spanish and correct, and the plural is absent rather than English. T1's
question 3 (morpheme must be present) is what excludes it. Two independent passes reached
this verdict, and the losing argument is recorded in `council-c8-c9.md`.

**Constructed example.** Spanish ML requiring finite verbal inflection:

> \*Yo **walk** a la escuela todos los días.

versus attested integration strategies such as *Yo camino* or the morphologically
integrated *waTchear*-type borrowing `[VERIFY: use an attested integrated form from the
corpus rather than a coined one]`.

**Attested example.** `[PENDING]`

**Populability.** Good. Bare forms are frequently discussed in the Spanish/English
literature.

---

## Mutual exclusivity

An item gets exactly one primary type. Where more than one diagnostic returns yes, apply
this ordering — **first match wins**:

1. **T3** — if ML material intrudes into EL-framed material, it is T3 regardless of what
   else is true. Island integrity is evaluated before frame-internal violations, because
   an ill-formed island changes what counts as the frame.
2. **T1** — EL system morpheme in an ML frame.
3. **T5** — the residual. A congruence failure is only T5 if no system-morpheme violation
   accounts for it.

T2 dropped out of this ordering entirely — see "⚠ T2 dropped" below. It is no longer a
rank to adjudicate between; nothing is left of it to rank.

**Stress-tested against twenty-six constructed ambiguous cases** across two rounds
(`ordering-stress-test.md`, `ordering-stress-test-v2.md`): round 1, eight clean/five
contested/seven failures on twenty cases; round 2 added six bridge/outsider-focused cases
(C21–C26) and re-ran all twenty, finding eleven verdict changes (three unannounced) and
one regression (C3, T3's own canonical example, temporarily broken and then fixed). **No
failure at either round required changing the T3/T1/T5 rank itself** — every fix turned on
a type's *scope*. The one case that looked like it might force a rank change (C9) instead
resolved by tightening T2's own scope, and then T2 was dropped rather than kept at a
rank nothing else needed adjusting around it.

Both originally contested cases are now resolved:

- **C8 → T5.** T1 requires the EL morpheme be present; \*`los book` lacks a morpheme
  rather than importing one. Reached independently by the stress test and the council.
- **C9 → T1 (late bridge).** English possessive `'s` is a late bridge system morpheme.
  Under the tightened T2 q5 (see T2 section above), T2's order-based claim on this item
  fails — the prenominal order is the obligatory linearization of one imported morpheme,
  not a general EL-frame effect — so T1 is the only type that fires. This reverses the
  council's original T2 verdict, whose own stated reasoning (`council-c8-c9.md`) anticipated
  exactly this outcome as one live possibility once T1 widened, and recorded a — mistaken —
  prediction that "the ordering would probably still return T2." It did not, once q5 itself
  was corrected rather than merely re-ranked.

Losing arguments for both are recorded verbatim in `council-c8-c9.md` with explicit flip
conditions; C9's flip conditions there are superseded by the tightened-q5 reasoning above.

## ⚠ T2 dropped — three types ship, not four

**Decided 2026-08-16, after the population-verification premise this document previously
required could not be fully cleared, and after an additional, independent search found no
new candidate probes.** This amends `docs/charter.md`'s stated four-type minimum; see the
amendment recorded there and in `journal.md` for the full reasoning and its cost.

**What was checked before deciding.** Three independent lines of evidence converge:

1. **`t2-variety-check.md`'s dialect-level survey** checked every candidate word-order
   probe the taxonomy had proposed or that the survey itself surfaced against
   Caribbean-influenced Bangor Miami Spanish. Most were dead: several on dialect grounds
   (wh-inversion, subject pronoun position — both natively licensed for this population
   and therefore *false-positive-generating*, not merely unusable), one on optionality
   grounds independent of dialect (clitic climbing), and one (preverbal clitic placement,
   the taxonomy's own headline probe) on a structural rather than dialectal defect —
   it cannot form a mixed constituent at all. Negation survived at low yield. Only
   nominal possessor order (C9) survived as a strong probe. (The source document's own
   summary count of surviving/dead probes is internally inconsistent between its headline
   and its full table — noted here rather than propagated as a precise figure.)
2. **`ordering-stress-test-v2.md`'s diagnostic-level re-run** found, independently and for
   a structural rather than a dialectal reason, that C9 does not actually belong to T2:
   the deviation is the obligatory linearization of one imported morpheme (English `'s`
   is lexically prenominal), not evidence of general EL-frame order pressure — exactly
   the defect that produced the false positive at C19. Tightening T2 q5 to close that
   hole removes C9 from T2's probe pool by the diagnostic's own logic, independent of the
   population question.
3. **A further targeted search this session** for heritage/contact-Spanish-specific
   obligatory order phenomena outside the original probe inventory (differential object
   marking, subject-verb order convergence, DP-internal order beyond possessives) found
   no viable candidate. Differential object marking (personal *a*) is real and frequently
   documented in exactly this contact setting, but its violation is *omission*, not
   *order* — already covered by the C25 gap, declared out of scope above, not by T2.
   Subject-verb order and adjective order are both independently documented as
   *converging toward* English-compatible patterns in heritage Spanish-English
   populations — the opposite of what a T2 probe needs, since a construction the
   population has plausibly already grammaticalized as optional cannot license a
   violation judgment. This is a negative result, not an absence of search effort, and it
   replicates rather than contradicts the two documents above.

**What was not fully checked, and why the decision proceeds anyway.** Bangor Miami's
exact speaker national-origin breakdown is still unverified — the corpus's own public
documentation (`Miami_doc.pdf`, read this session) gives age, sex, and recording length
per file but explicitly states that "additional information about the speakers ... is
available to researchers on request," meaning this needs a direct request to the Bangor
research team, not merely a TalkBank account. That request has not been made. If it comes
back showing the population is less Caribbean-influenced than assumed, some of the
dialect-level rejections in point 1 could weaken. It would not change point 2 (C9's
diagnostic failure is structural, not dialectal) or point 3 (the convergence pattern is
reported across heritage Spanish-English populations generally, not Miami specifically).
Two of three independent lines of evidence are population-independent, so this decision
is not made to conditional on a check that may take an unbounded amount of time to clear,
consistent with `docs/charter.md`'s general instruction to build over ask on reversible
decisions — and this one is reversible: if the population data later arrives and changes
the picture, T2 can be reopened the same way T4's fold was documented rather than deleted.

**The alternative rejected: keeping C9 in T2 by fiat.** Doing so would mean the shipped
type's classifications contradict its own stated diagnostic — the tightened q5 is
independently required to fix C19's false positive regardless of what happens to C9 — and
would leave T2 as a one-construction type whose held-out label tests "English possessive
order inside Spanish NPs" rather than a general word-order constraint. Per the T4
precedent already established in this document: *a type `matriz` cannot meaningfully hold
out is not a type, it is a rounding error with a name.* That standard was applied to T4
for populability; applying a different, more lenient standard to T2 only because a fourth
type happened to be procedurally convenient would be reasoning backward from a quota,
which is the exact failure this project exists to avoid.

**Cost, stated rather than buried.** The Morpheme Order Principle is no longer
independently tested as a held-out violation type — it survives only as one of the two
criteria used to *identify* the Matrix Language in the first place (see above). `matriz`
holds out from three types (T1, T3, T5) rather than four; recalculated cell density in
`docs/charter.md`'s Phase 4 target is addressed there. Recorded in `limitations.md`.

## Resolved gap — missing free-standing ML system morphemes (C25)

**Decided: out of scope. Option 3 below, chosen.**

\*`Vi la teacher en la tienda` omits the obligatory Spanish personal *a*. No type catches
it:

- **T1** requires the morpheme be *present* (added to fix C17)
- **T5** requires the missing morphology be *on the EL element itself* (added to fix C11)

A missing, free-standing ML system morpheme satisfies neither escape. Each fix is correct
in isolation; their conjunction removed coverage nobody decided to remove. C8 escapes only
by accident — Spanish plural happens to be a noun affix, so T5 catches it.

Three options were on the table:

1. **A fifth type for ML system-morpheme omission.** Theoretically clean but the SMP is
   about morpheme *source*, and this is about absence — it may not be an MLF violation at
   all. Rejected: it also needs the SMP's exact wording read before it could be built —
   `[VERIFY: page]` — which is not available (no page-level access to
   @myersscotton1993duelling in this pass), so a fifth type would be built on an unread
   citation.
2. **Widen T5** to cover ML-required morphology not realised on the EL element. Rejected:
   this re-opens the C11 false positive (`la table`, licensed) that T5 question 3 was
   written to close, trading one hole for a previously-fixed one.
3. **Declare it out of scope**, on the grounds that MLF predicts where morphemes come
   from rather than whether all required ones appear. **Chosen.**

The reasoning is the same one already governing C12 (agreement-value failure, below): the
SMP is a claim about morpheme *source*, not about completeness. A missing morpheme has no
source to evaluate — there is nothing there to be EL-sourced or ML-sourced. Treating
omission as in-scope would require a different theoretical claim than the one this
taxonomy tests, and manufacturing one to catch C25 risks exactly the "code becomes the
source of truth ahead of the theory" failure `docs/charter.md` names. C25 (and the class it
represents — missing personal *a*, missing obligatory prepositions, missing
complementizer *que*) is added to the documented out-of-scope list below. The cost is
named in `limitations.md`: this is a real, frequently-discussed contact phenomenon that
the benchmark will not detect at all, not a rare edge case being waved away.

## Documented out-of-scope cases

Written down because annotators will otherwise reach for a type that does not fit, and an
unwritten exclusion is indistinguishable from an oversight.

**Agreement-value failure on an EL noun** (C12) — e.g. gender conflict between a Spanish
determiner and an English noun. No type covers it, and that is defensible: MLF predicts
where a morpheme is *sourced from*, not whether an agreement *value* is correct. Gender
assignment on EL nouns is heavily discussed in the Spanish/English literature (Poplack,
Pousada & Sankoff 1982 `[VERIFY]`), so annotators will reach for it. It is out of scope,
not unclassified.

**Internally ill-formed EL with no ML intrusion** (C16) — an English grammar error inside
otherwise English material. Terminated at T3 question 2.

**Monolingual word-order errors** (C4) — out of scope under the live T3/T1/T5 ordering,
structurally rather than by one named terminator: with no EL material present at all,
T3 (requires an EL stretch), T1 (requires an EL-sourced morpheme), and T5 (requires an
EL content morpheme) all fail to fire independently. Originally caught by an explicit T2
question 2 terminator, before T2 was dropped — retained here as the historical reason the
exclusion was first written down, since C4's own discovery (an item passing what a
diagnostic's *other* questions asked while failing to contain any EL material) is what
motivated adding this class of out-of-scope check to T3 and T5 as well.

**Missing free-standing ML system morphemes** (C25) — e.g. omitted personal *a*
(\*`Vi la teacher en la tienda`), an omitted obligatory preposition, an omitted
complementizer *que*. No type covers it: T1 requires the EL morpheme be present, T5
requires the missing morphology be realised on the EL element itself. Out of scope
because the SMP constrains morpheme *source*, not morpheme *presence* — there is no
source to evaluate for a morpheme that never surfaced. See the resolved-gap section
above for the two rejected alternatives.

## Segmentation is an unstated input

The ordering assumes constituent segmentation is given, and it is not. C13 and C20 both
resolve to T3 purely because an island reading is *available* and T3 sits first.
T3 question 1's constituenthood-modulo-intrusion test (renamed from the earlier
"contiguity" wording after round 2 — see T3 above) fixes C13, where scattered EL material
is not a constituent under any grouping; it does not fix C20, where segmentation is
genuinely undecidable.

**Therefore segmentation is recorded as its own annotation, scored separately from
violation typing.** An item whose type assignment depends on a contested segmentation is
flagged as such, and that flag is reported rather than resolved. This is the same
discipline as the disagreement rate: the ambiguity is data.

**Secondary tags** are permitted and unordered. An item that is primarily T1 may carry a
secondary T5 tag. Only the primary is single-valued, and only the primary is what
`matriz` holds out.

**Genuinely ambiguous items are not forced through this ordering.** Where two annotators
apply the ordering and disagree, that disagreement is logged as data, per the provenance
rules. It is not resolved by a third tiebreaker vote, because a coin-flip resolution
recorded as agreement is the failure mode this project exists to avoid.

## Ratification checklist

- [x] **Three mutually exclusive types survive review: T1, T3, T5.** T2 and T4 both
      considered and dropped/folded; `docs/charter.md`'s four-type floor amended accordingly
      (see `journal.md` for the full reasoning and cost).
- [ ] Every type has a citation to a named MLF prediction, page-verified — work-level
      verified for all three (T1: SMP; T3: EL Island Trigger Hypothesis; T5: Blocking
      Hypothesis), but page-level verification remains blocked (see "Citation practice"
      above), so this stays open. Also: a live,
      unresolved question whether the SMP as literally worded covers early/bridge system
      morphemes at all, or only outsiders — flagged above, top-priority `[VERIFY: page]`.
- [x] Every type has a stated, applicable diagnostic
- [ ] **New, 2026-08-16 — T3 q1 needs a multi-word/EL-headed-constituent clause.** Applied
      literally, T3 q1 can misfire on plain T1/T5 items (a bare function/content word
      trivially satisfies "constituent"). Found during Phase 2 item review, not yet
      fixed — any diagnostic change needs the full case-set re-run this document's own
      rule requires, not done here. See the flagged note under T3 above.
- [ ] Every type has one attested and one constructed example — constructed done for
      T1/T3/T5; T2's constructed example is retired along with the type. Attested
      examples remain open for all three, and not as work merely queued: the Bangor
      Miami transcripts are behind a login gate that was tried and confirmed on
      2026-08-16, and the principal declined to pursue account creation, so no attested
      example will come from raw corpus files (`journal.md`, "Phase 1 → Phase 2
      transition"). The route left open is an example quoted and cited from a published
      paper, which `docs/charter.md`'s provenance rules admit alongside corpora. None has been
      collected, and all 402 shipped items are `constructed`, so this box stays open
      into v1.0 rather than being quietly reinterpreted as met.
- [x] T4's populability resolved — folded into T1
- [x] T2's populability resolved — dropped; MOP survives only as an ML-identification
      criterion, not a held-out violation type
- [x] The first-match ordering tested against at least ten hand-built ambiguous cases —
      `ordering-stress-test.md`, two defects found and fixed
- [x] Expand the stress test to twenty cases — 8 clean, 5 contested, 7 failures; all
      failures produced applied diagnostic fixes
- [x] Add stress cases for late bridge and outsider morphemes, now that T1 admits them —
      `ordering-stress-test-v2.md` Part 3, C21–C26
- [x] Resolve C8 and C9 at reasoning council — C8 → T5. C9's council verdict (T2) was
      later superseded by the tightened T2 q5 diagnostic; final: C9 → T1
- [x] Re-adjudicate C9 under the widened T1 — done, resolves to T1 (late bridge)
- [x] Re-run all twenty cases against the revised diagnostics — done in
      `ordering-stress-test-v2.md`, eleven verdict changes found and reconciled
- [x] Resolve the C25 missing-ML-morpheme gap — declared out of scope, see above
- [ ] Each surviving type plausibly populable to roughly 133 items (400 ÷ 3) — not yet
      checked against corpus supply; T1 and T5 both previously rated "good," T3 rated
      "good," none rated against the new, larger per-type target
