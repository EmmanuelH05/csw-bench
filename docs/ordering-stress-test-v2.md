# Ordering stress test, round 2 — regression against the revised diagnostics

Round 1 (`ordering-stress-test.md`) found seven failures and produced a diagnostic fix for
each. Every fix was written *in response to* the case that exposed it, and none was tested
against the other nineteen. This file runs that regression: all twenty cases re-adjudicated
against `docs/taxonomy.md` as it currently stands, plus six new cases probing what the
widened T1 admits.

All cases are **constructed**. None is a corpus token and none may be presented as one.
Citations are to work and named principle only; anything needing a page is
`[VERIFY: page]`. Spanish is the ML throughout unless stated. `*` marks the intended
violation.

`ordering-stress-test.md` and `taxonomy.md` are unmodified by this file.

## The diagnostics as they now stand

Reproduced compactly because the re-run turns on exact wording, and three of the failures
below are wording failures rather than substantive ones.

- **T1** — (1) ML frame; (2) system morpheme by 4-M, class recorded; (3) **morpheme present
  in the string**; (4) EL-sourced **and attaches to ML material**.
- **T2** — (1) ML frame; (2) **EL material in the constituent**; (3) **not an EL island**;
  (4) order mismatches ML requirement; (5) mismatch attributable to EL order, not a
  licensed ML alternative. Plus a prose constraint: probes obligatory across all major
  Spanish varieties.
- **T3** — (1) **contiguous** EL stretch forming a constituent; (2) internally well formed
  by EL grammar — **no + no ML material ⇒ out of scope, terminate**; (3) contains ML system
  morphemes, or its boundary cuts a constituent EL grammar requires be complete.
- **T5** — (1) ML frame; (2) EL content morpheme; (3) ML obligatorily requires morphology
  **on the EL element itself** that is absent; (4) outside any EL island.

Ordering: **T3 → T2 → T1 → T5**, first match wins.

---

## Part 1 — regression on C1–C20

### C1 — \*Compré **the** libros ayer.

T3 q1 no: `the` is one morpheme and does not form an EL constituent. T2 q4 no: Det-N is
Spanish order. T1: system morpheme, present, EL-sourced, attaches to ML `libros` — all
four yes. **T1 (early). Unchanged, clean.**

### C2 — Compré **the books** ayer.

T3 q1–q2 yes, q3 no ⇒ well-formed island, no violation. T2 excluded at the new q3. T1 now
fails at q4: `the` attaches to `books`, which is EL, not ML. T5 excluded at q4.
**None, licensed. Unchanged, clean.** Note the licensing is now carried by T1 q4 rather
than by intuition — an improvement.

### C3 — \*Me dio **el a book** ayer. ⚠ **BROKEN BY THE FIXES**

Round 1 called this "the case the ordering exists for" and scored it clean T3.

T3 q1 requires a **contiguous** EL stretch forming a constituent. The contiguous EL stretch
is `a book`; the ML determiner `el` sits outside it. q2 yes — `a book` is internally well
formed. q3 asks whether **it** — the stretch identified at q1 — contains ML system
morphemes. It does not: `el` is outside the stretch by the very contiguity test that
defined it. Its boundary does not cut an incomplete EL constituent either. **T3 fails.**

T2: the constituent `el a book` contains EL material, is not an island, and its order is
wrong — but q5 fails, because Det-Det-N is not licensed by English either, so the deviation
is not attributable to EL order. T1: `a` is an EL determiner, present and EL-sourced, but
q4 asks whether it attaches to ML material and its host is `book`, which is EL. Fails. T5:
no ML morphology is missing from `book`.

**No type.** A case round 1 scored clean now falls through the entire ordering.

The mechanism generalises, and it is worse than one case. **T3's own canonical example in
`taxonomy.md` — \*`Me dio a el book ayer` — also fails.** There the ML `el` sits *between*
`a` and `book`, so the maximal contiguous EL stretch is a single morpheme and q1 fails
outright.

This is a self-contradiction inside T3, not a coincidence:

> **q1 requires the EL material to be contiguous. q3 requires ML material to be inside it.
> ML material inside a stretch breaks its contiguity. The two questions cannot both be
> satisfied by the intrusion configuration T3 is defined over.**

Every ML intrusion either splits the EL material (q1 fails) or sits at its edge and is
therefore outside the stretch (q3 fails). T3's remaining live path is q3's second clause —
a boundary cutting an incomplete EL constituent — but an incomplete EL constituent is
exactly what q1's "forming a constituent" rules out. **T3 is close to empty as written.**

Round 1 introduced contiguity to kill C13's phantom island. It did that, and it took T3
with it. This is the clearest overfitting casualty in the set.

**Proposed repair.** Contiguity is the wrong instrument. C13's phantom island is better
killed by **constituenthood under EL grammar**: `the … yesterday` would have to be the
English string `the books yesterday`, and an NP plus a temporal adverb is not an English
constituent. C13 dies on that test alone, without contiguity. Rewrite T3 q1 as: *is there a
stretch of EL material which, with any intervening ML material set aside, forms a
constituent under EL grammar?* That restores C3 and the canonical example, still kills C13,
and — checked below — still leaves C20 undecided, which is what the segmentation section
claims.

### C4 — \*Yo veo **lo** en la tienda.

T2 q2: no EL material anywhere. **Out of scope.** Changed from T2. Fix works.

### C5 — \*Yo veo **lo** en la **store**.

T3 no, T2 q2 yes / q3 no / q4 yes / q5 yes — clitic placement on finite verbs is obligatory
across all major varieties, so the new probe restriction is satisfied. **T2. Unchanged,
clean.**

⚠ **Latent wording problem the C4 fix introduced.** T2 q2 asks whether "the constituent"
contains EL material. The order violation is in the VP; the EL material `store` is inside a
separate PP. C5 passes only if "the constituent" means the clause. Under a constituent-local
reading C5 fails q2 and joins C4 as out of scope — which would delete T2's flagship
example. The clause-level reading is obviously intended; it is not stated. **Fix: q2 should
name the domain explicitly** (the minimal clause containing the order violation), or T2
inherits an ambiguity that will show up as inter-annotator disagreement rather than as a
visible defect.

### C6 — \*Yo **walk** a la escuela todos los días.

T3 no, T2 no (SVO matches), T1 no (`walk` is content). T5: q3 satisfied — Spanish finite
inflection is affixal on the verb itself, so the "on the EL element itself" tightening does
not exclude it. **T5. Unchanged, clean.**

### C7 — Yo dije que **I walk to school every day**.

Island, no ML intrusion. **None, licensed. Unchanged, clean.**

### C8 — \*Compré los **book** ayer.

T1 q3: the plural morpheme is absent, not EL-sourced. T1 fails. T5: q3 satisfied — Spanish
plural *is* affixal on the noun. **T5.** Changed from T1, as expected. The fix works and
the C11 tightening does not collide with it: Spanish plural is realised on the noun,
Spanish gender is not, and q3 discriminates them correctly.

⚠ **But the escape is an accident of Spanish exponence, not a principle.** C8 lands in T5
only because the missing ML morpheme happens to be affixal on an EL element. C25 below
constructs the same violation with a free-standing missing ML morpheme, and nothing catches
it. The C8 verdict is right; the reasoning does not generalise, and `council-c8-c9.md`'s
flip-condition 1 (the SMP's scope over *absence*) still decides whether the whole class is
covered.

### C9 — \*Es **Juan's** casa.

Re-adjudicated in full in Part 2.

### C10 — \*Juan **camina-s** a la tienda.

T4 no longer exists. Under widened T1: `-s` is a system morpheme (late outsider), present,
EL-sourced, and — uniquely among the outsider cases here — attaches to **ML** material
(`camina`). All four yes. **T1 (late outsider).** Changed from T4.

The case now *resolves*, and the resolution is worthless. This is the only configuration in
which widened T1 reaches an outsider morpheme, and it is precisely the form round 1 rejected
as unattestable. See C23/C24: **the widening does not recover outsider coverage in
practice.**

### C11 — Compré **la table** ayer.

T5 q3 now reads "on the EL element itself"; Spanish gender is discharged on the determiner
and Spanish has no productive nominal gender affix. q3 no. **None, licensed. Unchanged**;
the fix converts a near-miss into a principled licensing.

### C12 — \*Compré **un table** nuevo, pero **la** otra **table** era mejor.

Still no type; now explicitly declared out of scope in `taxonomy.md` § documented
out-of-scope. Verdict unchanged, status changed from failure to documented exclusion.

### C13 — \*Compré **the** libros **yesterday**.

T3 q1: `the` and `yesterday` are non-contiguous, so the phantom island is unavailable. T3
fails. T2 no. T1: `the` attaches to ML `libros`. **T1.** Changed from T3, as expected.

The fix does what it was written to do. It also breaks C3. The repair proposed under C3
(constituenthood rather than contiguity) keeps this result: `the books yesterday` is not an
English constituent.

### C14 — Dijo que **the books I bought were expensive**.

Island, complete, no ML intrusion. T1 blocked by q4 throughout — every EL system morpheme
in the island attaches to EL material. **None, licensed. Unchanged, clean.**

### C15 — \*¿Qué **the teacher** dijo en la clase?

T2 q5 fails: Caribbean non-inversion is a licensed ML alternative. T1 q4 fails: `the`
attaches to EL `teacher`. T5 no. **None.** Changed from T2.

The intended outcome, reached — but by suppression rather than resolution. The string *is*
a violation in standard Spanish; the diagnostics now return "no type" rather than "excluded
probe", which is a different annotation. ⚠ **The variety restriction lives in prose, not in
a numbered question.** An annotator running the five questions mechanically has to import
variety knowledge at q5 unprompted. Promote it to a question, or T2's most important scope
limit is the one an annotator is least likely to apply.

### C16 — \*Me dio **book the** ayer.

Intended: T3 q1 identifies the stretch, q2 finds it ill formed, no ML intrudes, terminate as
out of scope. That is the charitable reading and it works.

⚠ **The strict reading reopens the hole.** q1 says "a contiguous stretch of EL material
**forming a constituent**". `book the` does not form a constituent under English grammar, so
q1 returns no, T3 terminates before reaching q2, and the out-of-scope terminator is never
consulted. The string then falls through T2 (q5 fails), T1 (q4 fails, `the` attaches to EL
`book`) and T5 (nothing missing) to **no type** — exactly the round 1 failure.

The fix is load-bearing and its reachability depends on reading q1 as identifying a
*candidate* stretch rather than a verified one. **Fix: split q1 into candidate
identification (a contiguous EL stretch of two or more morphemes) and constituenthood, and
put the out-of-scope terminator before constituenthood.** As written, C16's repair is
fragile.

### C17 — Compré los **books** ayer.

T1 q4: `-s` attaches to `books`, EL material. Fails. T5 q3: the required plural is present,
merely EL-realised. Fails. **None, licensed.** Changed from T1, as expected. Fix works.

### C18 — \*Estoy **enjoying** la película. ⚠ **UNEXPECTED CHANGE**

T1 q4: `-ing` attaches to `enjoy`, which is EL. Fails. T5: `enjoy` is an EL content
morpheme, Spanish obligatorily supplies `-ndo` affixally on the verb itself, absent, outside
any island. **T5.** Changed from T1 — and this change was not on the expected list.

The change is, on its face, an improvement: it settles a contest round 1 left open, on the
diagnostic's own terms. But it settles it by a clause written for the plural in C17, and the
consequence reaches much further than either case:

> **T1 now fires only when an EL system morpheme attaches to ML material.** No EL affix on
> an EL stem can ever be T1. Since affixal and clitic system morphemes are by default hosted
> by their own EL stems, T1 in practice reduces to **free-standing EL function words
> adjacent to ML material** — determiners, prepositions, conjunctions, complementizers.

That is a large, undocumented narrowing, and it lands on exactly the classes the widening was
supposed to add. It is also the clause that decides C9, C17, C18, C21–C24 — six of the
twenty-six cases in this file turn on it. ⚠ **"Attaches to ML material" is nowhere defined.**
For an affix it plainly means the host stem. For a free morpheme it has no obvious referent:
`of` in `el libro of Juan` is adjacent to `libro` (ML) and takes `Juan` (neutral) as
complement, and only a stipulation says which counts. This is now the single most
load-bearing undefined term in the taxonomy and it must be specified before ratification.

### C19 — Fui a la **movie theater** con ella.

T2 q3 excludes it. **None, licensed.** Changed from T2, as expected.

⚠ Same under-specification as C5, mirrored: q3 asks "is **the constituent** an EL island?"
The DP `la movie theater` is *not* an island — it contains the ML determiner. Only the
sub-constituent carrying the offending N-N order is. q3 works only if read as *is the
offending order internal to an EL island?* State that, or the fix does not apply to the case
it was written for.

### C20 — \*Me dijo **that ella** viene. ⚠ **UNEXPECTED CHANGE**

The only EL material is `that`. A single morpheme cannot be a contiguous EL stretch forming
a constituent, so T3 q1 fails and the island reading is unavailable. T2: `que ella viene` is
Spanish order, no mismatch. T1: `that` present, EL-sourced, attaches to ML `ella viene`.
**T1.**

`taxonomy.md` § "Segmentation is an unstated input" asserts that "Contiguity (T3 question 1)
fixes C13; it does not fix C20, where segmentation is genuinely undecidable." **That is now
false on the diagnostic as written.** Contiguity decides C20 too, because C20's EL material
is a single morpheme regardless of how the string is bracketed.

Two consequences, and they pull opposite ways:

1. The segmentation section is stale. It retains C20 as one of its two motivating examples
   and C20 no longer motivates it. The segmentation-as-separate-annotation policy is still
   defensible on general grounds — nothing supplies a segmentation — but it now has zero
   worked examples in the case set, which is a weaker position than the document claims.
2. C20 falling out of T3 and C3 falling out of T3 are the **same mechanism**. Here the
   result is desirable, there it is fatal. A rule that produces the right answer and the
   wrong answer by identical reasoning is not doing the work attributed to it. Under the
   constituenthood repair proposed at C3, C20 returns to genuinely undecidable (`that ella
   viene` *is* an English CP constituent with ML material set aside) and the segmentation
   section regains its example — which is a further argument for that repair.

### Round 1 → round 2 results

| Case | Round 1 | Round 2 | Δ |
|---|---|---|---|
| C1 | T1 | T1 | — |
| C2 | none | none | — |
| C3 | T3 ✅ | **none** | ❌ **broken** |
| C4 | T2 ❌ | out of scope | fixed |
| C5 | T2 | T2 | — (wording risk) |
| C6 | T5 | T5 | — |
| C7 | none | none | — |
| C8 | T1 ⚠ | **T5** | resolved |
| C9 | T2 ⚠ | see Part 2 | re-adjudicated |
| C10 | T4 ❌ | **T1** | resolves, still unusable |
| C11 | none | none | — (reasoning fixed) |
| C12 | none ❌ | none | documented out of scope |
| C13 | T3 ⚠ | **T1** | fixed |
| C14 | none | none | — |
| C15 | T2 ❌ | **none** | suppressed, not resolved |
| C16 | none ❌ | out of scope | fixed, fragile |
| C17 | T1 ❌ | **none** | fixed |
| C18 | T1 ⚠ | **T5** | ⚠ unexpected |
| C19 | T2 ❌ | **none** | fixed |
| C20 | T3 ⚠ | **T1** | ⚠ unexpected, contradicts taxonomy.md |

**Eleven verdict changes** (C3, C4, C8, C10, C13, C15, C16, C17, C18, C19, C20), of which
three were unannounced (C10, C18, C20) and one is a regression (C3). C12 changed status
without changing verdict.

**One previously-working case broke: C3** — and with it T3's own canonical example, which is
the more serious half of the finding.

---

## Part 2 — C9 re-adjudicated under the widened T1

> \*Es **Juan's** casa.

### The overlap is now real

`council-c8-c9.md` decided C9 for T2 on a **decisive second ground**: possessive `'s` is a
late *bridge* morpheme `[VERIFY: page — @myersscotton2000fourm]`, the old T1 admitted only
early morphemes, so T1 was never available and the ordering never adjudicated anything. The
council recorded this precisely: "the ordering was never load-bearing for C9."

Widening T1 removes that ground. Running the current diagnostics:

- **T3** — EL material is `'s` alone (`Juan` is language-neutral in form). No stretch, no
  constituent. No.
- **T2** — q1 ML frame (short, but `Es` + `casa` establish Spanish); q2 EL material present;
  q3 not an island; q4 Spanish requires postnominal *de*-phrase, this is prenominal; q5 no
  Spanish variety licenses a prenominal genitive, so the mismatch is attributable to EL
  order on the strongest possible grounds. **Four yes.**
- **T1** — q1 yes; q2 system morpheme, class late bridge; q3 present; q4 EL-sourced, and it
  attaches to ML material under any reading that also lets `of` attach to `libro` in C21.
  **Four yes.**

Both fire. The ordering decides. It returns **T2**.

### Is T2 defensible here? No.

Not because the intuition is loud, but because **T2's stated justification for its rank does
no work in this case, and T2 q5 rests on a false dichotomy.**

**On rank.** `taxonomy.md` justifies T2-before-T1 structurally: "constituent order determines
which elements are even *in* the constituent under evaluation." In C9 that is simply untrue.
The constituent is `[Juan's casa]` under either analysis; nothing about which elements are in
it depends on resolving the order question first. The rank's own rationale is inapplicable,
so the T2 verdict here is not justified by the ground the document gives for the ordering —
it is arbitrary with respect to it.

**On q5.** T2 q5 asks whether the deviation is attributable to *EL order* rather than to a
licensed ML alternative. It offers two options where there are three. The third is the one
C9 instantiates: the deviation is attributable to **the obligatory linearisation of a single
imported EL morpheme**. English `'s` is lexically prenominal; importing it and preserving
Spanish order is not a possible string. That is not the Morpheme Order Principle being
violated — the MOP is a claim about the *frame* supplying order — it is one lexical item's
exponence requirement, showing up as order because it has nowhere else to show up.

This is not a request to encode etiology, which the council rightly refused as unrecoverable
from a string. The test is structural and lexical, and it is decidable by inspection:
*is there a single EL morpheme in the string whose lexical entry forces the observed
linearisation?* In C9, yes — `'s`. In C5, no: `store` sits in an unrelated PP and forces
nothing about clitic placement; the displacement is general EL frame pressure. The two cases
separate cleanly.

**And C19 is the same defect without the disguise.** C19 was T2 firing on order that is a
property of EL lexical material (`movie theater` compounding) rather than of the frame. It
was repaired with an island exclusion — which works only because that particular EL material
happened to be multiword and therefore island-shaped. C9 is a single morpheme, so there is no
island to exclude, and the same disease goes untreated. Two cases, one underlying fault:
**T2 does not distinguish frame order from EL-lexical order.**

### Verdict — **T1 (late bridge)**, reached by tightening T2 q5, not by reordering

Proposed wording for T2 q5:

> Is the deviation attributable to EL **frame** order — as opposed to being the obligatory
> linearisation of an individual EL morpheme present in the string, or of EL-internal
> compounding? If the latter, T2 does not apply.

Under it, C9 fails T2 at q5, falls to T1, and returns **T1, system_morpheme_class = late
bridge**. C5 is unaffected. C19 is excluded twice over, which is harmless.

This keeps round 1's pattern intact — every failure so far has been a *scope* fix, not a
*rank* fix — and it does so honestly rather than by preference: the scope fix is
independently motivated by C19 and generalises, whereas reordering T1 above T2 would be a
change motivated by one case with unknown consequences for the nineteen others.

### The honest cost, and the alternative if the fix is rejected

Three costs, stated rather than buried.

1. **T2 gets thinner again.** Round 1 already cut variety-sensitive probes (C15) and island
   order (C19). Removing single-morpheme-forced order removes another class. What remains is
   essentially clitic placement, some negation, and some interrogatives — with the
   interrogatives partly gone to C15. `taxonomy.md` flags T2 as "the type most likely to fall
   short of its item quota"; that flag should now be raised to a stated risk that T2 may not
   reach ~100 items. **Recommend re-checking T2 populability before ratification, not after.**
2. **The C9/C22 pair becomes the argument's own evidence.** C22 below is `Es la casa of Juan`
   — same bridge class, same EL-sourced system morpheme, no order side-effect. Under the
   ordering as written C9 is T2 and C22 is T1, so two items differing only in an English
   morpheme's linear requirements land in different held-out types. That is precisely the
   mechanistic incoherence in T2 that `council-c8-c9.md`'s Reading A warned would damage the
   `matriz` holdout, and the widened T1 has made it demonstrable rather than hypothetical.
3. **If the q5 tightening is rejected, the ordering must be revised.** I do not think T2 is
   defensible for C9 on any reading now that T1 is available. If the project prefers to keep
   q5 as written, then the remaining repair *is* an ordering change — T1 above T2 — and the
   claim in `taxonomy.md` that "no failure required changing the ordering itself" no longer
   holds. Those are the only two options I can see; retaining both the current q5 and the
   current rank means shipping C9 and C22 in different types for no principled reason.

The council's recorded flip-condition 1 for C9 anticipated exactly this ("the verdict would
probably still be T2 on ordering grounds"). I disagree with that prediction, on the two
grounds above, and record the disagreement rather than deferring to it.

---

## Part 3 — new cases C21–C26

### C21 — EL late bridge `of`, no order change

> \*Compré el libro **of** Juan ayer.

The case `council-c8-c9.md` § "The gap C9 exposed" named as the minimal demonstration of the
coverage hole, and the case the widening was written for.

T3: `of Juan` is contiguous and forms an English PP, internally well formed, no ML inside —
no T3 violation. T2 q4: N + PP is Spanish order (`el libro de Juan`), no mismatch. T1: `of`
is a late bridge system morpheme, present, EL-sourced, and attaches to ML `libro` as its
complement-marker. Four yes. **T1 (late bridge).**

**The hole is closed.** This is the widening's one unambiguous win.

### C22 — EL bridge morpheme inside an EL island ⚠ **new false positive**

> Fui a la casa **of my friend**.

`of my friend` is a contiguous, internally well-formed English PP with no ML intrusion — an
EL island, and licensed. T3 q3 no. T2 excluded at q3. T5 excluded at q4.

**T1 has no island exclusion.** T5 q4 has one, T2 q3 now has one, T1 has none. `of` is a
late bridge system morpheme, present, EL-sourced, and attaches outward to ML `casa`. All four
questions pass. **T1 fires on a licensed island. False positive.**

This gap is *created by the widening*, not merely exposed by it. Under narrow T1 the missing
exclusion was harmless: early system morphemes inside an island (determiners, plurals) attach
to EL hosts, so q4 blocked them — which is exactly why C2 and C14 come back licensed. Bridge
morphemes attach **outward**, integrating two elements; that is what "bridge" means. So
admitting bridge morphemes to T1 necessarily makes q4 stop blocking island-internal cases,
and nothing else stands in the way.

**Fix: T1 gains an island exclusion mirroring T5 q4.** This is the highest-yield fix in this
round, for the same reason C19's was in round 1: EL PPs are common, and the false positives
would inflate T1 counts silently.

### C23 — EL late outsider on an EL stem

> \*Juan **walks** a la tienda todos los días.

Subject-verb agreement `-s` is the textbook late outsider morpheme, present, EL-sourced.
T1 q4: it attaches to `walk`, EL material. **T1 does not fire.** T5: `walk` is an EL content
morpheme, Spanish obligatorily inflects the finite verb affixally, that inflection is absent,
and it is outside any island. **T5.**

Identical routing to C6. The outsider morpheme is invisible to the taxonomy — the item is
typed by what is *missing from Spanish*, not by what English supplied.

Combined with C10, this settles the question the new cases were built to ask:

> **The widened T1 reaches an EL outsider morpheme only when that morpheme attaches to an ML
> stem.** For Spanish/English that is `camina-s` — C10 — which round 1 rejected as
> unattestable and which no bilingual produces. Every attestable outsider configuration puts
> the EL affix on an EL host, where q4 blocks it.

`taxonomy.md` T1's widening note claims the change "recovers most of what T4's removal cost."
**It does not.** It recovers bridge coverage (C21, C26) and recovers nothing at all for
outsiders. The claim should be corrected to say so; the `system_morpheme_class` metadata
field will contain no late-outsider values, because no item can reach one.

### C24 — fused outsider: EL structural case

> \*Vi a **him** en la tienda.

Accusative case is a late outsider morpheme — its form depends on a governor outside the
pronoun's own projection. It is EL-sourced and it is present in the string. But it is
**fused with the pronoun**: there is no segmentable case morpheme to point at.

T3: single word, no stretch. T2: `Vi a X` is Spanish order. T1 q2/q3: the questions presume a
segmentable morpheme that can be classified and located; a portmanteau form defeats both, and
if one classifies the whole word instead, `him` receives a thematic role and is a content
morpheme, so q2 returns no. T5: `him` is an EL content morpheme, but Spanish supplies `lo`/`él`
by **suppletion**, not by affixing morphology to `him` — so q3, tightened at C11 to
"morphology on the EL element itself", returns no.

**No type.** A second outsider gap, orthogonal to C23: not blocked by q4 but by the
morpheme's non-segmentability.

Together C10, C23 and C24 exhaust the Spanish/English outsider space: EL-affix-on-ML-stem is
unattestable, EL-affix-on-EL-stem is blocked at q4, and fused case is unsegmentable.
**T4 was correctly folded for populability reasons, and the widening did not compensate. The
loss recorded in `limitations.md` is larger than the taxonomy currently states.**

### C25 — a missing ML system morpheme that is not affixal ⚠ **new gap, as commissioned**

> \*Vi **la teacher** en la tienda.

Spanish requires the personal *a* with a specific animate direct object: *Vi **a** la
teacher*. Personal *a* is an ML system morpheme whose distribution depends on information
outside its head constituent — animacy and objecthood — so it is late outsider on the 4-M
test `[VERIFY: page — @myersscotton2000fourm on differential object marking]`. Here it is
**missing**.

- T3 — `teacher` is one EL morpheme, no stretch. No.
- T2 — the surviving order `V + DP` is Spanish order; nothing is displaced. No.
- T1 — q3: the morpheme is absent. This is exactly the C17-motivated precondition. No.
- T5 — q2 yes, `teacher` is an EL content morpheme. q3: does the ML obligatorily require
  morphology **on the EL element itself** that is absent? No — personal *a* is a free-standing
  preposition preceding the DP, not affixal morphology on the noun, and the C11 tightening
  explicitly excludes ML requirements discharged elsewhere in the constituent. No.

**No type.** This is the gap the brief predicted, and it is created by the *interaction* of
two round 1 fixes written independently for different cases:

> T1 q3 (from C17) closes the door on absent morphemes. T5 q3 (from C11) closes the door on
> ML requirements not realised affixally on the EL element. A **missing, non-affixal ML
> system morpheme in a mixed constituent** satisfies neither escape and falls through the
> whole ordering.

Neither fix is wrong on its own case. Their conjunction removes coverage nobody voted to
remove. C8 survives this only because Spanish plural happens to be a noun affix — swap the
missing morpheme for a free-standing one and the same violation type is unclassifiable.

This is also not a marginal configuration. Missing personal *a*, missing obligatory
prepositions, and missing complementizer *que* are all frequently discussed in Spanish/English
contact contexts, and all three are free-standing.

**Three options, none free:**

1. **Widen T1 to cover a required ML system morpheme that is absent from a mixed constituent.**
   This is precisely `council-c8-c9.md`'s C8 flip-condition 1, and it reopens C8 as T1. It
   also needs the SMP's actual wording — `[VERIFY: page — @myersscotton1993duelling]` — since
   the whole question is whether the SMP constrains absence or only source.
2. **Loosen T5 q3** back toward "morphology the ML obligatorily requires in this constituent."
   Cheapest, and it re-breaks C11 (`la table`), which is licensed. Rejected.
3. **Declare missing-ML-morpheme violations out of scope**, alongside C12's agreement-value
   gap. Honest and cheap, and it concedes a class MLF arguably does predict.

I recommend (1), conditional on the page verification, and note it converts the C8 verdict
from settled to page-dependent again. That is an unwelcome result and I record it rather than
routing around it.

### C26 — EL bridge coordinator between ML constituents

> \*Voy a la tienda **and** la escuela.

T3: single EL morpheme, no stretch. T2: `X y Y` is Spanish order, no mismatch. T1: `and` is a
system morpheme — coordinators are standardly late bridge, structurally assigned within the
projection they join `[VERIFY: page — @myersscotton2000fourm on coordinators]` — present,
EL-sourced, and attaching to ML material on both sides. **T1 (late bridge).**

Included as the positive control on the widening and as a populability probe. Coordinators
and prepositions are frequent and closed-class, so if bridge morphemes are to populate T1
beyond `of` and `'s`, this is where the items come from.

⚠ **Conditional on the 4-M classification.** If coordinators are treated as outside the
system-morpheme classes, or as language-neutral discourse material, T1 over-fires on a
licensed string and this becomes a false positive rather than a probe. The `[VERIFY]` is not
decorative — it flips the verdict.

### New-case results

| Case | String | Verdict | What it shows |
|---|---|---|---|
| C21 | \*Compré el libro **of** Juan | T1 (bridge) | widening closes the council's hole |
| C22 | Fui a la casa **of my friend** | T1 ❌ | **false positive — T1 lacks an island exclusion** |
| C23 | \*Juan **walks** a la tienda | T5 | outsider invisible to T1; routes as a bare form |
| C24 | \*Vi a **him** en la tienda | none ❌ | **fused outsider case unclassifiable** |
| C25 | \*Vi **la teacher** en la tienda | none ❌ | **missing non-affixal ML morpheme falls through** |
| C26 | \*Voy a la tienda **and** la escuela | T1 (bridge) | bridge populability probe, `[VERIFY]`-dependent |

Two of six are new failures the round 1 fixes created (C22, C25); one (C24) is a pre-existing
gap the widening was claimed to close and does not.

---

## What this round changes

Ordered by cost of not doing it.

1. **T3 q1's contiguity requirement contradicts T3 q3 and must be replaced.** It breaks C3
   and T3's own canonical example, and it makes T3 near-unreachable in the intrusion
   configuration the type is defined over. Replace with: *a stretch of EL material which,
   with intervening ML material set aside, forms a constituent under EL grammar.* This still
   kills C13's phantom island (`the books yesterday` is not an English constituent) and it
   restores C20 to genuinely undecidable, which is what the segmentation section needs.

2. **T1 needs an EL-island exclusion.** C22. Widening T1 to bridge morphemes — which attach
   outward by definition — removed the incidental protection q4 was providing. Mirror T5 q4.

3. **"Attaches to ML material" must be defined.** C9, C17, C18, C21, C22, C23, C26 all turn
   on it, and it is undefined for free morphemes. State the affix rule (host stem) and the
   free-morpheme rule (the ML element it selects, governs, or agrees with) explicitly.

4. **T2 q5 must distinguish frame order from EL-lexical order.** C9 and C19 are one defect.
   Without it, C9 and C22 land in different held-out types on the basis of one English
   morpheme's linearisation requirements.

5. **The missing-morpheme gap must be closed or declared.** C25. Recommend widening T1 to
   absent required ML system morphemes, contingent on the SMP page check — which reopens C8.

6. **T3 q1 must separate candidate identification from constituenthood**, or C16's
   out-of-scope terminator is unreachable and the round 1 fix does not hold.

7. **Three claims in `taxonomy.md` are now false and should be corrected.**
   - The widening "recovers most of what T4's removal cost" — it recovers bridge, not
     outsider (C10, C23, C24).
   - "Contiguity fixes C13; it does not fix C20" — it fixes C20 too, as written (C20).
   - "No failure required changing the ordering itself" — still true only if the T2 q5
     tightening is adopted. Reject that and C9 forces a rank change.

8. **T2 and T3 populability both need re-checking before ratification.** T2 has lost
   variety-sensitive probes, island-internal order, and (under fix 4) single-morpheme-forced
   order. T3 under the current q1 is close to empty and under the repaired q1 is limited to
   genuine ML intrusion, which is narrower than round 1 assumed. `taxonomy.md` names T2 as
   the quota risk; **T3 is now the more acute one.**

9. **Every fix in round 1 was written against one case and none was regression-tested.** One
   broke a clean case (C3), two changed verdicts without being announced (C18, C20), two
   created new gaps in combination (C22, C25), and one is reachable only under a charitable
   reading (C16). The round 1 conclusion that "four of the five diagnostics failed but the
   ordering survived" is defensible; the implicit conclusion that the failures were *repaired*
   is not. **Any further diagnostic edit gets a full 26-case re-run before it is called
   fixed.**

## Ratification items this round adds

- [ ] Replace T3 q1 contiguity with constituenthood-modulo-intrusion; re-run C3, C13, C16, C20
- [ ] Add an EL-island exclusion to T1; re-run C2, C7, C14, C21, C22
- [ ] Define "attaches to ML material" for affixes and for free morphemes
- [ ] Tighten T2 q5 to frame order, or change the T1/T2 rank; decide C9 explicitly
- [ ] Decide the C25 missing-morpheme gap: widen T1, or declare out of scope
- [ ] `[VERIFY: page]` — 4-M class of coordinators (@myersscotton2000fourm), decides C26
- [ ] `[VERIFY: page]` — 4-M treatment of differential object marking, decides C25's framing
- [ ] Re-check T2 and T3 populability against their post-fix scope
