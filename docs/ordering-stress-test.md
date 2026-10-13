# First-match ordering stress test

Phase 1 blocker. The taxonomy claims mutual exclusivity via a first-match ordering:

**T3 → T2 → T4 → T1 → T5** (C1–C10)
**T3 → T2 → T1 → T5** (C11–C20, after T4's removal)

Asserting that is easy. This file tries to break it with twenty cases built to be ambiguous
on purpose. All are **constructed**, so no corpus access is needed and none may ever be
promoted to a benchmark item without a recorded derivation. No case here is a corpus
token and none may be presented as one.

C1–C10 were built before T4 was folded into T1 and are frozen — their verdicts and
conclusions stand as written. C11–C20 were built afterwards, specifically to attack the
ordering rather than exercise it: cases where two types genuinely both fire, cases sitting
on the system/content boundary where C8 already failed, cases where the island boundary is
undecidable, cases where Spanish variation independently licenses the apparent violation,
and cases that must come back **licensed** and test whether the diagnostics produce false
positives.

Spanish is the ML throughout unless stated. `*` marks the intended violation.

---

## C1 — English determiner on a Spanish-framed noun

> \*Compré **the** libros ayer.

T1 (EL early system morpheme). T3 does not fire: no EL-framed material for ML to intrude
into — *the libros* is not an English island, it is a Spanish NP with an English
determiner. **T1. Clean.**

## C2 — English determiner plus English noun

> Compré **the books** ayer.

Not a violation. *the books* is a well-formed EL island. **No type. Licensed.**

Included because C1 and C2 differ by one word and land on opposite sides. If an annotator
cannot separate these two, the T1 diagnostic is underspecified.

## C3 — Spanish determiner inside an intended English island

> \*Me dio **el a book** ayer.

T3 fires (ML determiner intruding into EL-framed material) and T1 arguably fires (system
morpheme trouble in a mixed constituent). Ordering puts T3 first. **T3.**

This is the case the ordering exists for. Without it, two annotators split.

## C4 — Postverbal clitic under English order pressure

> \*Yo veo **lo** en la tienda.

T2 (Morpheme Order). Preverbal clitic placement is obligatory with Spanish finite verbs.
No EL material at all — the whole utterance is Spanish. **T2, and note it is monolingual.**

⚠ **Problem surfaced.** This is a word-order error in monolingual Spanish, not a
code-switching violation. It tests Spanish grammar, not MLF. **A T2 item must contain EL
material**, or the benchmark measures the wrong construct. Diagnostic needs a fourth
question: *is there EL material in the constituent?* If no, the item is out of scope.

## C5 — Postverbal clitic with an English EL noun

> \*Yo veo **lo** en la **store**.

T2, and now genuinely code-switched. **T2.** This is what C4 should have been.

## C6 — Bare English verb stem in a Spanish frame

> \*Yo **walk** a la escuela todos los días.

T5 (congruence failure — Spanish obligatorily inflects the finite verb). T1 does not
fire: *walk* is a content morpheme, not a system morpheme. T3 does not fire: single word,
no island. **T5. Clean.**

## C7 — Bare English verb inside an English island

> Yo dije que **I walk to school every day**.

Not a violation — well-formed EL island. Diagnostic question 4 of T5 ("outside any EL
island?") is what excludes it. **No type. Licensed.**

C6/C7 pair-tests that question the way C1/C2 tests T1.

## C8 — English plural on an English noun in a Spanish frame

> \*Compré los **book** ayer.

Ambiguous by construction. Two readings:
- **T1**: the plural marker is missing where the ML frame requires number concord — a
  system-morpheme failure.
- **T5**: *book* is an EL content morpheme surfacing bare without ML-required morphology.

Ordering says T1 before T5, so **T1**. But the reading is genuinely contested, and the
losing argument gets recorded in item metadata per the working-style rule.

⚠ **This is the ordering's weakest point.** Number marking sits exactly on the
system/content boundary. Flag for the reasoning council.

## C9 — English possessive `-s` in a Spanish frame

> \*Es **Juan's** casa.

T1 (English possessive is an early system morpheme; Spanish requires *la casa de Juan*).
T2 also fires — the possessive forces English prenominal order against Spanish
postnominal *de*-phrase order. Ordering puts **T2 before T1**, so **T2**.

⚠ **Counterintuitive and worth challenging.** The morpheme is what is foreign; the order
change is a *consequence* of importing it. Ordering gives T2, intuition says T1. Either
the ordering is wrong here or the intuition is. **Unresolved — reasoning council.**

## C10 — English third-person `-s` on a Spanish verb

> \*Juan **camina-s** a la tienda.

Intended as T4 (EL late outsider system morpheme — subject-verb agreement). But the form
is incoherent rather than code-switched: no bilingual would produce it, and *-s* on a
Spanish stem is not attestable.

⚠ **Confirms the T4 populability risk** flagged in `taxonomy.md`. Every attempt to
construct a clean Spanish/English T4 case produces something either unattestable or
better described as T1. **Evidence for folding T4 into T1.**

## C11 — Spanish gender on an English noun

> Compré **la table** ayer.

*table* carries no gender; Spanish requires the determiner to carry one, and bilinguals
assign it — most often by the gender of the translation equivalent (*mesa*, feminine),
sometimes by a masculine default (Poplack, Pousada & Sankoff 1982).

T1 does not fire: the determiner is ML-sourced, which is what MLF requires. T3 does not
fire: *table* alone is not an island. T2 does not fire: Det-N is Spanish order. T5 is the
one that has to be argued. Question 3 asks whether the ML obligatorily requires morphology
on the EL element that is absent, and Spanish gender is obligatory in the constituent —
but it is realised on the determiner, not affixed to the noun. Spanish has no productive
gender inflection a noun must carry. So question 3 is *no* and T5 does not fire.
**No type. Licensed.**

⚠ **Near-miss worth recording.** T5 survives here only because Spanish gender happens not
to be affixal. An annotator reading question 3 as "does the ML require morphology in this
constituent that this element fails to supply" flags a licensed string. Question 3 needs
tightening to *morphology realised on the EL element itself*; agreement discharged on an
ML agreement target elsewhere in the constituent does not count. **Clean, with a
diagnostic-wording fix.**

## C12 — Gender assignment conflict on an English noun

> \*Compré **un table** nuevo, pero **la** otra **table** era mejor.

Both assignments appear, and each is independently defensible: masculine by default
assignment, feminine by analogy to *mesa*. Nothing in MLF adjudicates which gender an EL
noun gets, because gender assignment to EL nouns is not a system-morpheme *source*
question — the determiner is ML-sourced under either reading.

T3, T2, T1, T5 all return no, by the C11 reasoning. The ordering returns **no type** for a
string that a Spanish/English bilingual would flag immediately. **Failure — coverage gap.**

The taxonomy has no type for ML-internal agreement failure on an EL element. That is not a
gap the ordering can fix; it is a missing type or an explicit out-of-scope declaration.
Declaring it out of scope is the honest option — MLF predicts the *source* of system
morphemes, not the *value* of an agreement feature on a noun the ML has no lexical entry
for — but it has to be written down, because gender assignment is one of the most heavily
discussed phenomena in the Spanish/English literature and annotators will reach for it.

## C13 — Undecidable island boundary around a lone EL determiner

> \*Compré **the** libros **yesterday**.

Two segmentations, same string:

- *the* is a lone EL early system morpheme in a Spanish NP, *yesterday* is an EL adverb
  adjunct → **T1** (this is C1 plus an adverb).
- *the … yesterday* is an attempted English island *the books yesterday* into which the ML
  noun *libros* has intruded → **T3**.

Ordering evaluates T3 first, so it returns **T3** — which commits the analysis to English
framing the constituent, contradicting the ML assignment that Spanish is the ML. The
correct answer is almost certainly T1.

⚠ **The ordering inherits a segmentation it was never given.** T3 question 1 ("is there a
stretch of EL material forming a constituent?") does not require the EL material to be
contiguous, so a determined annotator can glue non-adjacent EL words into a phantom island
and win the first-match race. **Contested.** Proposed fix: T3 question 1 requires two or
more **contiguous** EL morphemes that form a constituent under EL grammar.

## C14 — Finite English clause under a Spanish complementizer

> Dijo que **the books I bought were expensive**.

Looks like every violation at once: English determiner, English past-tense marking,
English subject-verb agreement, all inside a clause the Spanish verb selects. Each of
those is an EL system morpheme, and a naive T1 read fires on all of them.

It is a well-formed EL island — structurally complete, internally English, ML material
stops at *que*. T3 question 3 is no. T1 does not reach inside an island; T5 question 4
excludes it explicitly. **No type. Licensed.**

The C7 pair-test at clause scale. C7 tests one bare verb inside an island; this tests
whether a dense stack of EL system morphemes inside an island still reads as licensed. If
an annotator flags this, the island concept is not being applied and every T1 count is
inflated.

## C15 — Wh-question order with an English EL subject

> \*¿Qué **the teacher** dijo en la clase?

Standard-variety Spanish requires subject-verb inversion in wh-questions (*¿Qué dijo la
maestra?*), the constituent contains EL material, and the preverbal subject looks like
imported English order. T3 does not fire, so ordering returns **T2**.

⚠ **But non-inversion is licensed in Caribbean Spanish** (*¿Qué tú dijiste?*), which is a
variety heavily represented in exactly the Spanish/English contact settings the corpora
sample. Under that variety the order is native and no violation exists.

**Failure.** T2 question 4 asks whether the deviation is attributable to EL order "rather
than to a licensed ML alternative", but *licensed* is silently relative to a variety the
item never declares. The C4 fix made T2 require EL material; it did not make T2 require a
declared ML variety. Proposed fix: either every T2 item declares its Spanish variety and
is judged against it, or T2 probes are restricted to constructions obligatory across all
major varieties. Clitic placement on finite verbs survives that restriction; wh-inversion
does not. The second option is preferable — it keeps the ML label single-valued — but it
shrinks an already thin type, which sharpens the populability warning in `taxonomy.md`.

## C16 — Internally ill-formed EL string with no ML material

> \*Me dio **book the** ayer.

T3 question 2 asks whether the EL stretch is internally well formed by EL grammar. It is
not. But the violation is registered by question 3, which asks about ML intrusion — and
there is none. A no at question 2 makes T3 *unreachable* rather than triggered. T2: EL
material is present and the order is wrong, but question 4 fails, because the deviation is
not attributable to EL order — English requires Det-N too. T1: *the* is an EL system
morpheme, but it is not inside an ML-framed constituent under the island reading. T5: no
missing ML morphology.

The ordering returns **no type** for an unambiguously broken string. **Failure.**

The right resolution mirrors C4 exactly: this is a monolingual English word-order error
wearing a Spanish frame, so it is **out of scope**, and T3 should say so. Write it into T3
as a scope note — a no at question 2 with no ML material present terminates the diagnostic
as out of scope, not as "not T3, try the next type." Without that, every downstream type
gets a shot at a string that measures English grammar.

## C17 — English plural on an English noun under a Spanish determiner

> Compré los **books** ayer.

T3 no, T2 no. T1 fires on a literal reading: *-s* is an EL early system morpheme (number
is conceptually activated with its head) inside a Spanish-framed NP. Ordering returns
**T1**.

⚠ **This is a false positive, and it breaks C8.** Double plural marking — ML determiner
plural plus EL noun plural — is among the most commonly discussed patterns in
Spanish/English data and is not treated as ill-formed. More damagingly, compare C8:

| | C8 \*`los book` | C17 `los books` |
|---|---|---|
| EL plural marker | absent | present |
| C8/C17 verdict under T1 as written | T1 | T1 |

T1 cannot be violated by both the presence and the absence of the same morpheme. Its claim
is about the **source** of a system morpheme that is *there*. Absence is not a
source violation; it is a congruence failure. **Failure.**

This resolves C8. C8's T1 reading is invalid — a missing plural is not an EL-sourced system
morpheme — so **C8 is T5**, and the T1-versus-T5 contest that `taxonomy.md` sent to the
reasoning council is settled on the diagnostic's own terms rather than by intuition.
C17 itself then needs a licensing rule: EL number marking on an EL noun that also carries
ML concord is licensed, and T1 fires on EL system morphemes attached to **ML** material.

## C18 — English progressive `-ing` in a Spanish periphrasis

> \*Estoy **enjoying** la película.

Spanish requires *-ndo* (*disfrutando*). Two readings, and they split on 4-M
classification:

- *-ing* is an early system morpheme conceptually activated with its verbal head → **T1**.
- *enjoy* is an EL content morpheme surfacing without the ML-required participial
  morphology → **T5**.

Ordering says T1 before T5, so **T1**.

⚠ **The 4-M test has never been exercised on verbal morphology here.** `taxonomy.md` names
determiners and plural marking as "the productive probes", and every T1 case in this file
before C18 is one of those two. The diagnostic itself is unbounded, so annotators must
classify arbitrary morphemes as early-versus-late with no worked examples outside the noun
phrase. **Contested.** Proposed fix: T1 ships a closed probe list, or a 4-M classification
table covering every morpheme class the item set actually uses, decided once and cited
rather than re-derived per item.

## C19 — English compound inside a Spanish NP

> Fui a la **movie theater** con ella.

T3: *movie theater* is EL material forming a constituent, internally well formed, no ML
intrusion — no violation, and arguably an island. T1: the determiner is ML-sourced,
correct. T5: no ML morphology is missing.

T2 is the problem. The NP *la movie theater* contains EL material, and its internal order
is English N-N compounding where Spanish requires *sala de cine*. Questions 1–4 all return
yes, so ordering returns **T2** on a licensed string. **Failure — false positive.**

T5 has an island exemption (question 4). **T2 does not.** EL islands carry EL-internal
order by definition — that is what makes them islands — so an order diagnostic without an
island exclusion flags every island containing more than one EL word. Proposed fix: T2
gains an island exclusion mirroring T5 question 4. This is the single highest-yield fix in
this round, because compound and multiword EL nominals are common and would have
contaminated T2 at scale.

## C20 — English complementizer with a Spanish subject

> \*Me dijo **that ella** viene.

Same defect as C13, at a different constituent. Segmentation decides the type:

- *that* is a lone EL complementizer in a Spanish CP → **T1**.
- *that ella viene* is an attempted English island with the ML pronoun *ella* intruding →
  **T3**.

Ordering returns **T3**. Nothing in the diagnostics says which segmentation is correct,
and C13's contiguity fix does not help here — *that ella viene* is contiguous.

⚠ **Generalizes C13 into a structural finding.** The first-match ordering assumes a
constituent segmentation that no diagnostic supplies, and T3 sits first in the ordering, so
whichever segmentation makes an island available wins by default. **Contested.**

Proposed fix: segmentation becomes a separate recorded annotation field, fixed and
reviewed *before* type assignment, and segmentation disagreement is logged as its own
statistic distinct from type disagreement. Two annotators who segment differently are not
disagreeing about the taxonomy, and collapsing the two disagreement rates would hide the
real problem behind the smaller number.

---

## Results

| Case | Assigned | Clean? |
|---|---|---|
| C1 | T1 | ✅ |
| C2 | none | ✅ |
| C3 | T3 | ✅ ordering did its job |
| C4 | T2 | ❌ out of scope — monolingual |
| C5 | T2 | ✅ |
| C6 | T5 | ✅ |
| C7 | none | ✅ |
| C8 | T1 | ⚠ contested |
| C9 | T2 | ⚠ counterintuitive |
| C10 | T4 | ❌ unattestable |
| C11 | none | ✅ licensed — T5 q3 needs tightening |
| C12 | none | ❌ coverage gap — gender assignment |
| C13 | T3 | ⚠ segmentation artefact, should be T1 |
| C14 | none | ✅ licensed |
| C15 | T2 | ❌ licensed in Caribbean Spanish |
| C16 | none | ❌ falls through every type |
| C17 | T1 | ❌ false positive — and breaks C8 |
| C18 | T1 | ⚠ 4-M untested on verbal morphology |
| C19 | T2 | ❌ false positive — no island exclusion |
| C20 | T3 | ⚠ segmentation undecidable |

**Eight clean, five contested, seven failures** across twenty cases. The second ten were
built to break the ordering and did: two clean, three contested, five failed.

The failure rate is the finding, not an embarrassment. C1–C10 exercised the ordering on
cases the ordering was designed around; C11–C20 attacked it, and five of the seven total
failures come from the attacking half. Read the first-round six-clean result as evidence
that the first ten cases were too easy.

## What this changes

1. **T2 diagnostic gains a fourth question: is there EL material in the constituent?**
   Without it, T2 admits monolingual Spanish word-order errors, which measure the wrong
   construct entirely. This is the most valuable thing the stress test found — it would
   have contaminated the item set silently.

2. **T4 should be folded into T1.** Two independent lines of evidence now: the
   populability argument from English's impoverished inflection, and C10's failure to
   produce even a *constructed* clean case. The taxonomy ships **four** types, which
   still clears the `docs/charter.md` minimum. Record in `journal.md`.

3. **C8 and C9 go to the reasoning council** before ratification. Both turn on where the
   system/content boundary sits, and both need the losing argument recorded.

4. **Ten cases was too few.** Every one of the four types produced at least one edge, so
   the ordering is under-tested, not validated. Expand to twenty before ratification —
   and treat a stress test that finds nothing as evidence the cases were too easy.

### From C11–C20

5. **T1 fires on presence, never on absence — and this resolves C8.** C17 (`los books`)
   and C8 (\*`los book`) both return T1 under the diagnostic as written, which is
   incoherent: one has the EL plural morpheme, the other lacks it. The System Morpheme
   Principle is about the *source* of a system morpheme that surfaces, so absence cannot
   be T1. **C8 is T5.** T1's diagnostic gains an explicit precondition: the morpheme must
   be present and EL-sourced, and it must attach to ML material. C17 is then licensed
   rather than typed, matching the widely discussed double-marking pattern. This removes
   one of the two items `taxonomy.md` holds for the reasoning council and it removes it on
   the diagnostic's own terms, not by vote.

6. **T2 needs an EL-island exclusion.** C19 (`la movie theater`) is licensed and T2 flags
   it, because islands carry EL-internal order by definition and T2 has no exemption while
   T5 has one. Add a question mirroring T5 question 4: *is the constituent an EL island?*
   If yes, T2 does not apply. Highest-yield fix in this round — multiword EL nominals are
   common and this would have contaminated T2 silently, exactly as the C4 hole would have.

7. **T2 items must declare a Spanish variety, or drop variety-sensitive probes.** C15's
   wh-non-inversion is a violation in standard Spanish and native in Caribbean Spanish,
   which is well represented in the contact settings the corpora sample. The C4 fix made
   T2 require EL material; it did not make "licensed ML alternative" well defined.
   Preferred resolution: restrict T2 probes to constructions obligatory across all major
   varieties. That keeps the ML label single-valued but shrinks the type further, so
   `taxonomy.md`'s populability warning on T2 gets stronger, not weaker.

8. **T3 must terminate as out-of-scope on internally ill-formed EL material.** C16
   (\*`book the`) fails T3 question 2, which makes T3 unreachable rather than triggered,
   and then falls through T2, T1 and T5 to no type at all. This is C4's problem in the
   other language: a monolingual error inside a code-switched frame. T3 gets a scope note —
   a no at question 2 with no ML material present ends the diagnostic as out of scope.

9. **Segmentation is an unstated input to the whole ordering.** C13 and C20 produce T3
   purely because an island reading is available, and T3 sits first. No diagnostic tells
   an annotator how to segment. Two fixes, both needed: T3 question 1 requires **contiguous**
   EL morphemes forming an EL-grammatical constituent (kills C13's phantom island), and
   segmentation becomes a separate recorded annotation field fixed before type assignment,
   with its own disagreement statistic (C20, which contiguity does not solve). Reporting
   segmentation disagreement inside the type-disagreement rate would hide the larger
   problem behind the smaller number.

10. **T5 question 3 must say "on the EL element itself."** C11 (`la table`) is licensed and
    survives only because Spanish gender is not affixal. An annotator reading question 3 as
    "morphology the ML requires in this constituent" flags it. Agreement discharged on an
    ML agreement target elsewhere does not count as morphology missing from the EL element.

11. **The taxonomy has no type for agreement-value failure on an EL noun, and must say so.**
    C12 (gender conflict on `table`) returns no type. MLF predicts the *source* of system
    morphemes, not the *value* of an agreement feature on a noun the ML has no lexical
    entry for, so out-of-scope is the defensible call — but it has to be written into
    `taxonomy.md` explicitly. Gender assignment to English nouns is among the most
    discussed phenomena in the Spanish/English literature (Poplack, Pousada & Sankoff 1982);
    annotators will reach for it, and silence guarantees inconsistent tagging.

12. **The 4-M early/late test has only ever been run on determiners and plurals.** C18
    (`estoy enjoying`) puts it on verbal morphology and T1-versus-T5 splits immediately.
    T1 needs either a closed probe list or a 4-M classification table covering every
    morpheme class the item set uses, decided once and cited — not re-derived per item by
    each annotator. Note this is the same boundary that produced C8, so it is a recurring
    fault line rather than an isolated edge.

### Status of the two cases held for the reasoning council

- **C8 — resolved by C17.** T5, not T1. No council needed.
- **C9 — still open,** and C19 sharpens it. C9's counterintuitive T2 verdict comes from T2
  firing on an order consequence of an imported morpheme; C19 shows T2 firing on order that
  is not a violation at all. Both point at T2 being over-eager. Take C9 to council *after*
  the island exclusion (fix 6) is written, because the fix may change C9's inputs.
