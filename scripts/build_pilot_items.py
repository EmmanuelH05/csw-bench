"""One-shot Phase 2 pilot-item builder. Not part of the package -- run once, review the
output, delete or keep as a record. Computes violation_span from the actual tokenizer so
indices can't drift from what the schema/scorer will see.

Revision 2, 2026-08-16, after a second independent review pass (docs/journal.md, "Phase 2
— second review") found real problems in revision 1 and they are fixed here rather than
patched around:
  - T3's "a el X" pattern conflated with Spanish's obligatory a+el -> al contraction and
    the a/a homograph between the English indefinite article and the Spanish preposition.
    Replaced with "the el X" throughout -- no Spanish-preposition reading is available.
  - Several ml_identification required_evidence strings cited word order (adverb-PP
    order, SVO order) that Spanish and English actually share, which is not discriminating
    evidence for the Matrix Language and directly contradicts the shared-SVO-order threat
    already named in docs/limitations.md. Replaced throughout with genuinely discriminating
    evidence: finite Spanish verb morphology, null-subject licensing, and Spanish-sourced
    function words (not their order, which isn't diagnostic on its own).
  - Three T3 ml_identification items cited the island-internal intrusion itself as
    Matrix-Language evidence, which is circular -- the violation is what's being tested,
    not evidence for the frame that contains it.
  - The T3 double-article construction admits two independently-grammatical minimal
    repairs (delete either article), which the single-string gold_repair field couldn't
    express. Added RepairItem.alternate_repairs (schema.py) rather than force one answer.
  - Two items' gold repairs picked one of several standard variants with no
    disambiguating context (a bare-tense verb where the licensed integrated form's tense
    isn't otherwise recoverable). Added a temporal adverb to force the tense uniquely.
  - A demonstrative pair (that/esa) has a second valid Spanish translation (aquella) with
    no available fix short of adding distance-marking context; replaced with possessives
    (mi/su/nuestra), which have no such alternate for the persons used here.
  - Two blind-review-validated continuation alternatives licensed the sentence by a
    different mechanism than the one under test (a bare noun with no determiner at all;
    an English adverb with no EL verb at all) and were removed -- they were genuinely
    grammatical, just not evidence for or against the construct the item tests.
  - Vocabulary was templated too repetitively (the same violating string reused across
    3-4 items under different task types), which inflates how independent the 96.7%
    blind-review figure actually is. Diversified nouns/verbs across items below.
"""

from __future__ import annotations

import json
from pathlib import Path

from csw_bench.textnorm import tokenize

ITEMS_DIR = Path(__file__).resolve().parent.parent / "data" / "items" / "es-en"

T1_DERIVATION = "System Morpheme Principle"
T3_DERIVATION = "EL Island Trigger Hypothesis"
T5_DERIVATION = "Blocking Hypothesis"


def base(
    item_id: str, violation: str, difficulty: str, justification: str, derivation: str, **extra
):
    d = {
        "id": item_id,
        "matrix_language": "es",
        "primary_violation": violation,
        "difficulty": difficulty,
        "justification": justification,
        "provenance": {
            "source": "constructed",
            "license": "MIT",
            "derivation": derivation,
        },
    }
    d.update(extra)
    return d


def judgment(
    item_id, violation, difficulty, justification, derivation, licensed, violating, **extra
):
    return base(
        item_id,
        violation,
        difficulty,
        justification,
        derivation,
        task_type="grammaticality_judgment",
        licensed=licensed,
        violating=violating,
        **extra,
    )


def continuation(
    item_id,
    violation,
    difficulty,
    justification,
    derivation,
    prompt,
    licensed_c,
    violating_c,
    extra_licensed=(),
    **extra,
):
    return base(
        item_id,
        violation,
        difficulty,
        justification,
        derivation,
        task_type="constrained_continuation",
        prompt=prompt,
        licensed_continuations=[licensed_c, *extra_licensed],
        violating_continuations=[violating_c],
        **extra,
    )


def ml_id(item_id, violation, difficulty, justification, derivation, utterance, evidence, **extra):
    return base(
        item_id,
        violation,
        difficulty,
        justification,
        derivation,
        task_type="ml_identification",
        utterance=utterance,
        required_evidence=evidence,
        **extra,
    )


def repair(
    item_id,
    violation,
    difficulty,
    justification,
    derivation,
    violating,
    gold_repair,
    span_word,
    alternate_repairs=(),
    **extra,
):
    toks = tokenize(violating)
    idx = toks.index(tokenize(span_word)[0])
    return base(
        item_id,
        violation,
        difficulty,
        justification,
        derivation,
        task_type="repair",
        violating=violating,
        gold_repair=gold_repair,
        alternate_repairs=list(alternate_repairs),
        violation_span=[idx, idx + 1],
        **extra,
    )


items = []

# --- T1: EL system morpheme in ML frame (10 items) ---------------------------------
# Determiners (articles, possessives) as early system morphemes. Possessives are used
# in place of demonstratives where a second item was needed, since English "that" maps
# to two valid Spanish demonstratives (esa/aquella) with no disambiguator in short
# sentences, while singular possessives (mi/su/nuestra) have no such alternate here.

items.append(
    judgment(
        "csw-es-en-0001",
        "T1",
        "easy",
        "Spanish ML (verb 'compre', adverb-final order). The determiner 'the' is an "
        "early system morpheme sourced from the EL, attached to the ML-sourced noun "
        "'libros'. T1 q1-q5 all yes; the licensed form uses the ML determiner 'los'.",
        T1_DERIVATION,
        "Compré los libros ayer.",
        "Compré the libros ayer.",
        system_morpheme_class="early",
    )
)
items.append(
    judgment(
        "csw-es-en-0002",
        "T1",
        "medium",
        "Spanish ML. English determiner 'the' attaches to Spanish-sourced 'pelicula', "
        "an early system morpheme intrusion, T1 fires; licensed form uses 'la'.",
        T1_DERIVATION,
        "Vi la película anoche.",
        "Vi the película anoche.",
        system_morpheme_class="early",
    )
)
items.append(
    judgment(
        "csw-es-en-0003",
        "T1",
        "hard",
        "Spanish ML. Possessive determiners are early system morphemes under the 4-M "
        "test just as articles are. English 'my' inside a Spanish-framed NP is a T1 "
        "violation; licensed form uses the Spanish possessive 'mi', which has no "
        "competing valid alternative here (unlike a demonstrative, which would).",
        T1_DERIVATION,
        "Necesito mi computadora nueva.",
        "Necesito my computadora nueva.",
        system_morpheme_class="early",
    )
)
items.append(
    continuation(
        "csw-es-en-0004",
        "T1",
        "easy",
        "The prompt establishes a Spanish frame ('Ayer compré'). A licensed "
        "continuation keeps the object NP's determiner Spanish-sourced; the violating "
        "continuation imports the English determiner into that same frame.",
        T1_DERIVATION,
        "Ayer compré",
        "las revistas para la clase",
        "the revistas para la clase",
        system_morpheme_class="early",
    )
)
items.append(
    continuation(
        "csw-es-en-0005",
        "T1",
        "medium",
        "Spanish ML frame from the infinitive complement 'encontrar'. Licensed "
        "continuation uses Spanish 'los'; violating continuation substitutes English "
        "'the' as the NP's determiner.",
        T1_DERIVATION,
        "Necesito encontrar",
        "los papeles importantes",
        "the papeles importantes",
        system_morpheme_class="early",
    )
)
items.append(
    continuation(
        "csw-es-en-0006",
        "T1",
        "hard",
        "Spanish ML frame ('Ella tiene'). Licensed continuation uses the Spanish "
        "possessive 'su'; violating continuation imports English 'her' as an early "
        "system morpheme inside the Spanish-framed NP.",
        T1_DERIVATION,
        "Ella tiene",
        "su computadora nueva",
        "her computadora nueva",
        system_morpheme_class="early",
    )
)
items.append(
    ml_id(
        "csw-es-en-0007",
        "T1",
        "medium",
        "ML = Spanish. Verb morphology (compré) and the null subject are Spanish-only "
        "properties; only the single determiner 'the' is EL-sourced, which is what T1 "
        "predicts rather than a wholesale language switch. (Revision 2: dropped the "
        "earlier adverb-PP-order evidence, since 'yesterday at the store' has the same "
        "order in English and is not discriminating.)",
        T1_DERIVATION,
        "Compré the libros ayer en la tienda.",
        [
            "the verb 'compre' carries spanish 1sg preterite morphology",
            "no subject pronoun appears, licensed by spanish null-subject grammar",
        ],
        system_morpheme_class="early",
    )
)
items.append(
    ml_id(
        "csw-es-en-0008",
        "T1",
        "hard",
        "ML = Spanish. Verb morphology and the possessive's number agreement are "
        "Spanish-specific; 'that' is the sole EL-sourced system morpheme. (Revision 2: "
        "dropped the earlier clause-final-order evidence, non-discriminating.)",
        T1_DERIVATION,
        "Vi that película con mis amigos anoche.",
        [
            "the verb 'vi' carries spanish 1sg preterite morphology",
            "the possessive 'mis' agrees in number, unlike english 'my'",
        ],
        system_morpheme_class="early",
    )
)
items.append(
    repair(
        "csw-es-en-0009",
        "T1",
        "easy",
        "Minimal repair restores the ML-sourced determiner without touching any other "
        "material, since the violation is exactly the single EL-sourced determiner. No "
        "competing repair exists: 'los' is the only grammatical determiner for "
        "masculine plural 'libros'.",
        T1_DERIVATION,
        "Compré the libros ayer.",
        "Compré los libros ayer.",
        "the",
    )
)
items.append(
    repair(
        "csw-es-en-0010",
        "T1",
        "medium",
        "Minimal repair replaces the EL-sourced possessive with its ML-sourced "
        "counterpart. 'Nuestra' is the only grammatical 1pl possessive agreeing with "
        "feminine singular 'ayuda', so no competing repair exists.",
        T1_DERIVATION,
        "Necesito our ayuda hoy.",
        "Necesito nuestra ayuda hoy.",
        "our",
    )
)

# --- T3: Ill-formed EL island (10 items) --------------------------------------------
# Pattern (revision 2): a complete EL island with its own EL article ("the book"), with
# an ML article intruding immediately after it ("the el book"). Uses "the", not "a" --
# revision 1's "a el X" pattern was confounded with Spanish's obligatory a+el -> al
# contraction and the English/Spanish "a" homograph; "the" has neither problem.

items.append(
    judgment(
        "csw-es-en-0011",
        "T3",
        "easy",
        "'the book' is a complete, internally well-formed EL island under English "
        "grammar. The Spanish article 'el' intruding inside it breaks the island's "
        "internal integrity -- T3, not T1, because the violation is ML material inside "
        "an EL-framed constituent, the reverse direction from T1.",
        T3_DERIVATION,
        "Me dio the book ayer.",
        "Me dio the el book ayer.",
    )
)
items.append(
    judgment(
        "csw-es-en-0012",
        "T3",
        "medium",
        "'the gift' is a complete EL island; Spanish 'el' intruding inside it breaks "
        "the island's internal well-formedness under English grammar.",
        T3_DERIVATION,
        "Compró the gift ayer.",
        "Compró the el gift ayer.",
    )
)
items.append(
    judgment(
        "csw-es-en-0013",
        "T3",
        "hard",
        "'the whole magazine' is a complete EL island (article plus modifier plus "
        "noun, all English); the intruding Spanish 'el' breaks internal well-formedness "
        "exactly as in the taxonomy's canonical case, just with a longer island.",
        T3_DERIVATION,
        "Leyó the whole magazine anoche.",
        "Leyó the el whole magazine anoche.",
    )
)
items.append(
    continuation(
        "csw-es-en-0014",
        "T3",
        "easy",
        "Licensed continuation is a complete EL island ('the big house'). Violating "
        "continuation has Spanish 'el' intruding into that island.",
        T3_DERIVATION,
        "Vio",
        "the big house",
        "the el big house",
    )
)
items.append(
    continuation(
        "csw-es-en-0015",
        "T3",
        "medium",
        "Licensed continuation is a complete EL island ('the nice laptop'). Violating "
        "continuation has Spanish 'el' intruding into that island.",
        T3_DERIVATION,
        "Compró",
        "the nice laptop",
        "the el nice laptop",
    )
)
items.append(
    ml_id(
        "csw-es-en-0016",
        "T3",
        "medium",
        "ML = Spanish. The clause frame (verb morphology, the possessive) is Spanish; "
        "the island's internal breakage does not change which language supplies the "
        "frame. (Revision 2: the earlier evidence cited the intrusion itself as "
        "ML-identifying, which is circular -- the violation cannot be its own evidence "
        "for the frame that contains it. Replaced with independent evidence.)",
        T3_DERIVATION,
        "Compró the el nice laptop para su mamá.",
        [
            "the verb 'compro' carries spanish 3sg preterite morphology",
            "the possessive 'su' is a spanish-sourced system morpheme",
        ],
    )
)
items.append(
    ml_id(
        "csw-es-en-0017",
        "T3",
        "hard",
        "ML = Spanish, on evidence independent of the island violation itself: verb "
        "morphology and Spanish-sourced function words elsewhere in the clause.",
        T3_DERIVATION,
        "Leyó the el whole magazine durante el viaje.",
        [
            "the verb 'leyo' carries spanish 3sg preterite morphology",
            "'durante el viaje' has a spanish-sourced preposition and article",
        ],
    )
)
items.append(
    ml_id(
        "csw-es-en-0018",
        "T3",
        "easy",
        "ML = Spanish, on evidence independent of the island violation: verb "
        "morphology and Spanish-sourced function words elsewhere in the clause.",
        T3_DERIVATION,
        "Vio the el big house ayer en la calle.",
        [
            "the verb 'vio' carries spanish 3sg preterite morphology",
            "'en la calle' has a spanish-sourced preposition and article",
        ],
    )
)
items.append(
    repair(
        "csw-es-en-0019",
        "T3",
        "easy",
        "The double-article construction admits two independently grammatical minimal "
        "repairs: delete the intruding ML article (restoring the EL island) or delete "
        "the EL article (leaving a licensed ML-determiner-plus-EL-noun mixed NP, itself "
        "a well-formed construction). Both are recorded rather than picking one "
        "arbitrarily as the sole correct answer.",
        T3_DERIVATION,
        "Compró the el gift ayer.",
        "Compró the gift ayer.",
        "el",
        alternate_repairs=["Compró el gift ayer."],
    )
)
items.append(
    repair(
        "csw-es-en-0020",
        "T3",
        "medium",
        "Same double-article ambiguity as csw-es-en-0019: deleting either article "
        "yields a well-formed sentence, so both are recorded.",
        T3_DERIVATION,
        "Leyó the el whole magazine anoche.",
        "Leyó the whole magazine anoche.",
        "el",
        alternate_repairs=["Leyó el whole magazine anoche."],
    )
)

# --- T5: Congruence failure / bare form (10 items) ----------------------------------
# Pattern follows taxonomy.md's own documented contrast: an EL verb root either
# morphologically integrated with obligatory Spanish inflection (licensed) or
# surfacing bare (violating). Judgment/continuation items use infinitive-complement
# position (voy a / vamos a / clitic position), which forces the integrated form's
# shape unambiguously; repair items that don't have that structural anchor get an
# adverb added so the target tense is recoverable from context rather than picked
# arbitrarily among equally-valid tenses.

items.append(
    judgment(
        "csw-es-en-0021",
        "T5",
        "easy",
        "'park' is an EL content morpheme (assigns the agent role). Spanish "
        "obligatorily supplies finite verbal morphology; 'parquear' realizes it via "
        "integration, the bare 'park' does not -- T5 fires on the bare form.",
        T5_DERIVATION,
        "Voy a parquear el carro.",
        "Voy a park el carro.",
    )
)
items.append(
    judgment(
        "csw-es-en-0022",
        "T5",
        "medium",
        "'print' is an EL content morpheme; 'printeó' morphologically integrates it "
        "with the required Spanish inflection, the bare form does not. 'Ayer' forces "
        "the preterite reading, so there's no tense-choice ambiguity in the gold form.",
        T5_DERIVATION,
        "Ella printeó el documento ayer.",
        "Ella print el documento ayer.",
    )
)
items.append(
    judgment(
        "csw-es-en-0023",
        "T5",
        "medium",
        "'chat' is an EL content morpheme; 'chatear' morphologically integrates it, the "
        "bare infinitival-position form does not carry the Spanish infinitive marking "
        "the frame requires.",
        T5_DERIVATION,
        "Vamos a chatear un rato.",
        "Vamos a chat un rato.",
    )
)
items.append(
    continuation(
        "csw-es-en-0024",
        "T5",
        "easy",
        "Licensed continuation integrates the EL verb root with obligatory Spanish "
        "1sg present morphology ('texteo'); violating continuation leaves it bare. "
        "NOTE: the blind review's completion for this prompt ('...check my email antes "
        "de salir') is a genuine, unresolved disagreement about whether that "
        "completion is this item's violation type or a different, arguably-licensed "
        "clause-level switch -- logged in provenance.review_disagreement, not "
        "force-resolved, and deliberately left as the pilot's one open disagreement "
        "rather than patched away.",
        T5_DERIVATION,
        "Todos los días yo",
        "texteo a mis amigos",
        "text a mis amigos",
    )
)
items.append(
    continuation(
        "csw-es-en-0025",
        "T5",
        "medium",
        "Licensed continuation integrates the EL verb root with obligatory Spanish 3sg "
        "present morphology ('clickea'); violating continuation leaves it bare. "
        "'Cliquea' is a documented spelling variant of the same integrated form and is "
        "recorded as a second licensed answer rather than scored wrong.",
        T5_DERIVATION,
        "Ella siempre",
        "clickea el botón equivocado",
        "click el botón equivocado",
        extra_licensed=["cliquea el botón equivocado"],
    )
)
items.append(
    ml_id(
        "csw-es-en-0026",
        "T5",
        "medium",
        "ML = Spanish. No subject pronoun is expressed (licensed by Spanish's "
        "null-subject grammar) and the object determiner is Spanish-sourced; the bare "
        "EL verb 'park' is a congruence failure local to that one word, not a change of "
        "frame. (Revision 2: dropped 'yo' from the utterance so null-subject evidence "
        "is actually available, and dropped the earlier SVO-order claim, which English "
        "shares and is not discriminating.)",
        T5_DERIVATION,
        "Park el carro todos los días en la calle.",
        [
            "no subject pronoun is expressed, licensed by spanish's null-subject grammar",
            "the object determiner 'el' is spanish-sourced, agreeing with 'carro'",
        ],
    )
)
items.append(
    ml_id(
        "csw-es-en-0027",
        "T5",
        "hard",
        "ML = Spanish, on Spanish-sourced function words independent of the bare-verb "
        "violation itself. (Revision 2: dropped the earlier adverb-PP-order claim, "
        "which English shares and is not discriminating.)",
        T5_DERIVATION,
        "Ella print el documento ayer en la oficina.",
        [
            "the object determiner 'el' is spanish-sourced",
            "'en la oficina' has a spanish-sourced preposition and article",
        ],
    )
)
items.append(
    repair(
        "csw-es-en-0028",
        "T5",
        "easy",
        "Minimal repair replaces the bare EL verb with its morphologically integrated "
        "form, supplying the Spanish inflection the frame requires. The 'voy a + "
        "infinitive' frame forces the infinitive shape uniquely; no tense ambiguity.",
        T5_DERIVATION,
        "Voy a park el carro.",
        "Voy a parquear el carro.",
        "park",
    )
)
items.append(
    repair(
        "csw-es-en-0029",
        "T5",
        "medium",
        "Minimal repair replaces the bare EL verb with its morphologically integrated "
        "form. 'Ayer' forces the preterite reading, so the target tense is recoverable "
        "from context rather than picked arbitrarily among equally-valid tenses.",
        T5_DERIVATION,
        "Ella print el documento ayer.",
        "Ella printeó el documento ayer.",
        "print",
    )
)
items.append(
    repair(
        "csw-es-en-0030",
        "T5",
        "hard",
        "Minimal repair replaces the bare EL verb with its morphologically integrated "
        "infinitive form. The 'vamos a + infinitive' frame forces the infinitive shape "
        "uniquely; no tense ambiguity.",
        T5_DERIVATION,
        "Vamos a chat un rato.",
        "Vamos a chatear un rato.",
        "chat",
    )
)

# --- Second-pass review, 2026-08-16 -------------------------------------------------
# Blind AI review, round 1 (docs/journal.md, "Phase 1 -> Phase 2 transition" and "Phase
# 2"): every item rendered through the real prompts.py templates, answered by an
# independent agent with no access to gold labels, justifications, or taxonomy
# reasoning. 29/30 construct-validity agreement; one genuine disagreement
# (csw-es-en-0024, above); six continuation items' answer keys widened with validated
# alternatives (four kept -- they instantiate the tested construct; two were later
# reverted after a second review pass found they were licensed by a different mechanism
# than the one under test).
#
# Independent second review, round 2 (docs/journal.md, "Phase 2 — second review"): a
# separate reviewer read the taxonomy, schema, scorer, and all 30 items looking for
# problems the first review missed. Found the T3 confound, the evidence-citation
# problems, the repair-ambiguity problems, and the vocabulary-repetition problem that
# this revision fixes. That review's own account of what's correct: "All 30 items carry
# exactly one primary violation from the shipped taxonomy... No item's violating string
# is accidentally grammatical, and no item's licensed string is ungrammatical."
REVIEWED_BY = ["blind-ai-review-2026-08-16", "second-review-2026-08-16"]
DISAGREEMENTS = {
    "csw-es-en-0024": (
        "Independent blind reviewer completed the prompt as 'Todos los dias yo check my "
        "email antes de salir.' Unresolved whether 'check my email' is a bare EL verb "
        "phrase (this item's intended T5 violation, requiring Spanish inflection) or a "
        "full clause-level switch to English (a different, arguably licensed "
        "phenomenon). Not force-resolved; logged as genuine disagreement per the "
        "project's provenance rules."
    ),
}

for item in items:
    item["provenance"]["reviewed_by"] = REVIEWED_BY
    if item["id"] in DISAGREEMENTS:
        item["provenance"]["review_disagreement"] = DISAGREEMENTS[item["id"]]

ITEMS_DIR.mkdir(parents=True, exist_ok=True)
for old in ITEMS_DIR.glob("csw-es-en-*.json"):
    old.unlink()
for item in items:
    path = ITEMS_DIR / f"{item['id']}.json"
    path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"wrote {len(items)} items to {ITEMS_DIR}")
