"""Phase 4 item builder: scales the item set from the 30-item pilot toward the ~400-item
target in docs/charter.md, at 31 new items per (violation type x task type) cell (372 new items,
csw-es-en-0031 through csw-es-en-0402), on top of the 30 pilot items already on disk.

Follows the same construction discipline as build_pilot_items.py: every item is
"constructed" provenance with a recorded derivation (the MLF prediction it instantiates),
not "synthetic" -- the derivation is a documented MLF prediction (T1/T3/T5's own
diagnostics), not an ungrounded LLM sample. Gender agreement, verb conjugation, and
loanword-integration spelling are hand-curated in the vocabulary tables below rather than
derived by a general spelling rule, because -ear loanword integration has irregular
spelling adjustments (e.g. "chequear" not "checkear", "parquear" not "parkear") that a
mechanical rule would get wrong.

Not part of the package -- run once, validate, review, commit the output like Phase 2's
builder.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from csw_bench.textnorm import tokenize

ITEMS_DIR = Path(__file__).resolve().parent.parent / "data" / "items" / "es-en"

T1_DERIVATION = "System Morpheme Principle"
T3_DERIVATION = "EL Island Trigger Hypothesis"
T5_DERIVATION = "Blocking Hypothesis"

NEXT_ID = 31
TARGET_PER_CELL = 31  # new items per (violation, task_type) cell

# --------------------------------------------------------------------------------------
# Shared helpers (deliberately duplicated from build_pilot_items.py rather than imported:
# that script executes a file-rewrite as a side effect of import, and re-running it here
# would delete every item this script writes).
# --------------------------------------------------------------------------------------


def base(item_id, violation, difficulty, justification, derivation, **extra):
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


DIFFICULTY_CYCLE = itertools.cycle(["easy", "medium", "hard"])


def next_difficulty() -> str:
    return next(DIFFICULTY_CYCLE)


# --------------------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------------------

# (spanish_singular, spanish_plural, gender) -- gender drives article/possessive
# agreement. Diverse across semantic domains to avoid the vocabulary-repetition problem
# build_pilot_items.py's revision 2 fixed at pilot scale.
NOUNS = [
    ("libro", "libros", "m"),
    ("carro", "carros", "m"),
    ("documento", "documentos", "m"),
    ("perro", "perros", "m"),
    ("telefono", "telefonos", "m"),
    ("cuaderno", "cuadernos", "m"),
    ("reloj", "relojes", "m"),
    ("zapato", "zapatos", "m"),
    ("boleto", "boletos", "m"),
    ("edificio", "edificios", "m"),
    ("piso", "pisos", "m"),
    ("cafe", "cafes", "m"),
    ("pelicula", "peliculas", "f"),
    ("computadora", "computadoras", "f"),
    ("casa", "casas", "f"),
    ("mochila", "mochilas", "f"),
    ("bicicleta", "bicicletas", "f"),
    ("camisa", "camisas", "f"),
    ("escuela", "escuelas", "f"),
    ("tarea", "tareas", "f"),
    ("llave", "llaves", "f"),
    ("mesa", "mesas", "f"),
    ("silla", "sillas", "f"),
    ("ventana", "ventanas", "f"),
    ("puerta", "puertas", "f"),
    ("maleta", "maletas", "f"),
    ("camara", "camaras", "f"),
    ("cartera", "carteras", "f"),
]

NAMES = ["Juan", "Maria", "Carlos", "Ana", "Pedro", "Sofia", "Luis", "Elena", "Miguel", "Rosa"]

ADVERBS = [
    "ayer",
    "anoche",
    "hoy",
    "temprano",
    "esta manana",
    "la semana pasada",
    "este fin de semana",
    "otra vez",
    "de nuevo",
    "rapido",
]

# 1sg / 3sg preterite carrier verbs (frame verbs for T1/T3 judgment+ml_id items).
CARRIER_VERBS = [
    ("compre", "compro", "compr"),  # (1sg pret, 3sg pret, stem-for-display)
    ("vi", "vio", "v"),
    ("perdi", "perdio", "perd"),
    ("encontre", "encontro", "encontr"),
    ("vendi", "vendio", "vend"),
    ("busque", "busco", "busc"),
    ("lleve", "llevo", "llev"),
    ("traje", "trajo", "traj"),
    ("devolvi", "devolvio", "devolv"),
    ("limpie", "limpio", "limpi"),
]

# English possessive -> Spanish possessive, by gender/number of the possessed noun.
POSSESSIVES = [
    ("my", {"m_s": "mi", "f_s": "mi", "m_p": "mis", "f_p": "mis"}),
    ("our", {"m_s": "nuestro", "f_s": "nuestra", "m_p": "nuestros", "f_p": "nuestras"}),
    ("her", {"m_s": "su", "f_s": "su", "m_p": "sus", "f_p": "sus"}),
    ("your", {"m_s": "tu", "f_s": "tu", "m_p": "tus", "f_p": "tus"}),
]

# EL islands: (english article-free NP, spanish-gender of the closest translation
# equivalent) -- the standard code-switching-literature convention for assigning gender
# to an English-origin NP intruded upon by a Spanish article.
ISLANDS = [
    ("new phone", "m"),
    ("red car", "m"),
    ("old book", "m"),
    ("big house", "f"),
    ("small dog", "m"),
    ("nice laptop", "f"),
    ("blue backpack", "f"),
    ("fast bike", "f"),
    ("tall building", "m"),
    ("green umbrella", "m"),
    ("funny movie", "f"),
    ("expensive watch", "m"),
    ("cheap ticket", "m"),
    ("broken window", "f"),
    ("clean shirt", "f"),
    ("dirty floor", "m"),
    ("small radio", "m"),
    ("long document", "m"),
    ("heavy suitcase", "f"),
    ("shiny camera", "f"),
]

# General-purpose transitive verbs of possession/handling only -- broadly compatible
# with any physical-object island. Two narrow-subcategorization verbs originally here
# ("lei/leyo", which takes only readables, and "rompi/rompio", awkward with abstract
# islands like "loud music") produced anomalous pairings like "leyo the red car" once
# crossed combinatorially against every island; dropped for the same reason VERB_OBJECTS
# replaced generic objects for T5 above.
ISLAND_CARRIER_VERBS = [
    ("compre", "compro"),
    ("vi", "vio"),
    ("perdi", "perdio"),
    ("encontre", "encontro"),
    ("vendi", "vendio"),
    ("guarde", "guardo"),
    ("limpie", "limpio"),
    ("devolvi", "devolvio"),
    ("traje", "trajo"),
    ("busque", "busco"),
    ("lleve", "llevo"),
    ("revise", "reviso"),
]

# EL content-morpheme verbs with hand-curated integration principal parts. Spelling
# adjustments (qu/gu insertion, etc.) are attested Spanglish loanword-integration forms,
# not mechanically derived.
VERBS = {
    "park": dict(
        inf="parquear", pres1="parqueo", pres3="parquea", pret1="parquee", pret3="parqueo_"
    ),
    "print": dict(
        inf="printear", pres1="printeo", pres3="printea", pret1="printee", pret3="printeo_"
    ),
    "chat": dict(inf="chatear", pres1="chateo", pres3="chatea", pret1="chatee", pret3="chateo_"),
    "text": dict(inf="textear", pres1="texteo", pres3="textea", pret1="textee", pret3="texteo_"),
    "email": dict(
        inf="emailear", pres1="emaileo", pres3="emailea", pret1="emailee", pret3="emaileo_"
    ),
    "click": dict(
        inf="clickear", pres1="clickeo", pres3="clickea", pret1="clickee", pret3="clickeo_"
    ),
    "google": dict(
        inf="googlear", pres1="googleo", pres3="googlea", pret1="googlee", pret3="googleo_"
    ),
    "post": dict(inf="postear", pres1="posteo", pres3="postea", pret1="postee", pret3="posteo_"),
    "tag": dict(inf="taguear", pres1="tagueo", pres3="taguea", pret1="taguee", pret3="tagueo_"),
    "delete": dict(
        inf="deletear", pres1="deleteo", pres3="deletea", pret1="deletee", pret3="deleteo_"
    ),
    "check": dict(
        inf="chequear", pres1="chequeo", pres3="chequea", pret1="chequee", pret3="chequeo_"
    ),
    "fax": dict(inf="faxear", pres1="faxeo", pres3="faxea", pret1="faxee", pret3="faxeo_"),
    "scan": dict(
        inf="escanear", pres1="escaneo", pres3="escanea", pret1="escanee", pret3="escaneo_"
    ),
    "type": dict(inf="taipear", pres1="taipeo", pres3="taipea", pret1="taipee", pret3="taipeo_"),
    "swipe": dict(inf="swipear", pres1="swipeo", pres3="swipea", pret1="swipee", pret3="swipeo_"),
    "like": dict(inf="likear", pres1="likeo", pres3="likea", pret1="likee", pret3="likeo_"),
    "forward": dict(
        inf="forwardear",
        pres1="forwardeo",
        pres3="forwardea",
        pret1="forwardee",
        pret3="forwardeo_",
    ),
    "download": dict(
        inf="downloadear",
        pres1="downloadeo",
        pres3="downloadea",
        pret1="downloadee",
        pret3="downloadeo_",
    ),
    "upload": dict(
        inf="uploadear", pres1="uploadeo", pres3="uploadea", pret1="uploadee", pret3="uploadeo_"
    ),
    "spam": dict(inf="spamear", pres1="spameo", pres3="spamea", pret1="spamee", pret3="spameo_"),
}
# pret1/pret3 above end in a bare vowel that needs an acute accent (e/o -> e-acute/o-acute);
# apply it here so the table above stays plain-ASCII and easy to review.
for _v in VERBS.values():
    _v["pret1"] = _v["pret1"][:-1] + "é" if _v["pret1"].endswith("e") else _v["pret1"]
    _v["pret3"] = _v["pret3"].rstrip("_")[:-1] + "ó"

# Per-verb complement, chosen for real-world argument-structure fit rather than crossed
# combinatorially with the modal frames below -- "chatear el archivo" ("to chat the
# file") is exactly the kind of semantically anomalous pairing a combinatorial cross
# product would produce, since chatear/textear take a person (or no object at all), not
# a document.
VERB_OBJECTS = {
    "park": "el carro",
    "print": "el documento",
    "chat": "un rato",
    "text": "a Juan",
    "email": "el reporte",
    "click": "el enlace",
    "google": "la direccion",
    "post": "la foto",
    "tag": "la foto",
    "delete": "el mensaje",
    "check": "el correo",
    "fax": "el documento",
    "scan": "el recibo",
    "type": "el reporte",
    "swipe": "la tarjeta",
    "like": "la publicacion",
    "forward": "el correo",
    "download": "el archivo",
    "upload": "la foto",
    "spam": "el chat",
}

MODAL_FRAMES = ["Voy a", "Vamos a", "Tiene que", "Necesito", "Quiere", "Va a"]

items: list[dict] = []
_id_counter = itertools.count(NEXT_ID)


def new_id() -> str:
    return f"csw-es-en-{next(_id_counter):04d}"


def art(gender: str, number: str = "s") -> str:
    return {"m_s": "el", "f_s": "la", "m_p": "los", "f_p": "las"}[f"{gender}_{number}"]


def nuevo(gender: str) -> str:
    return "nuevo" if gender == "m" else "nueva"


def cap(s: str) -> str:
    """Capitalizes only the first character, unlike str.capitalize() which also
    lowercases every other character in the string -- fatal for sentences containing a
    proper noun (e.g. "Vi el carro de Juan hoy.".capitalize() silently produces "de juan").
    """
    return s[0].upper() + s[1:] if s else s


# --------------------------------------------------------------------------------------
# T1 -- EL system morpheme in ML frame
# --------------------------------------------------------------------------------------


def build_t1_judgment(n: int) -> list[dict]:
    out = []
    noun_cycle = itertools.cycle(NOUNS)
    poss_noun_cycle = itertools.cycle(NOUNS)
    adv_cycle = itertools.cycle(ADVERBS)
    name_cycle = itertools.cycle(NAMES)
    verb_cycle = itertools.cycle(CARRIER_VERBS)
    poss_cycle = itertools.cycle(POSSESSIVES)
    sub_patterns = itertools.cycle(["article", "possessive", "bridge_s", "bridge_of"])
    number_cycle = itertools.cycle([False, True])
    for _ in range(n):
        pattern = next(sub_patterns)
        pret1, _, _ = next(verb_cycle)
        adv = next(adv_cycle)
        if pattern == "article":
            sg, pl, gender = next(noun_cycle)
            use_plural = next(number_cycle)
            noun, number = (pl, "p") if use_plural else (sg, "s")
            licensed = cap(f"{pret1.capitalize()} {art(gender, number)} {noun} {adv}.")
            violating = cap(f"{pret1.capitalize()} the {noun} {adv}.")
            out.append(
                judgment(
                    new_id(),
                    "T1",
                    next_difficulty(),
                    f"Spanish ML (verb '{pret1}', null subject). The determiner 'the' is an "
                    f"early system morpheme sourced from the EL, attached to the ML-sourced "
                    f"noun '{noun}'. Licensed form uses the ML article '{art(gender, number)}'.",
                    T1_DERIVATION,
                    licensed,
                    violating,
                    system_morpheme_class="early",
                )
            )
        elif pattern == "possessive":
            sg, pl, gender = next(poss_noun_cycle)
            eng_poss, mapping = next(poss_cycle)
            sp_poss = mapping[f"{gender}_s"]
            adj = nuevo(gender)
            licensed = cap(f"Necesito {sp_poss} {sg} {adj}.")
            violating = cap(f"Necesito {eng_poss} {sg} {adj}.")
            out.append(
                judgment(
                    new_id(),
                    "T1",
                    next_difficulty(),
                    f"Spanish ML. Possessive determiners are early system morphemes under "
                    f"the 4-M test. English '{eng_poss}' inside a Spanish-framed NP is a T1 "
                    f"violation; licensed form uses Spanish '{sp_poss}'.",
                    T1_DERIVATION,
                    licensed,
                    violating,
                    system_morpheme_class="early",
                )
            )
        elif pattern == "bridge_s":
            sg, _, gender = next(noun_cycle)
            name = next(name_cycle)
            licensed = cap(f"Vi {art(gender)} {sg} de {name} {adv}.")
            violating = cap(f"Vi {name}'s {sg} {adv}.")
            out.append(
                judgment(
                    new_id(),
                    "T1",
                    next_difficulty(),
                    f"Spanish ML. English possessive 's is a late bridge system morpheme "
                    f"(per taxonomy.md's resolution of C9); its presence inside the "
                    f"Spanish-framed NP is a T1 violation. Licensed form uses the Spanish "
                    f"possessive construction '{art(gender)} {sg} de {name}'.",
                    T1_DERIVATION,
                    licensed,
                    violating,
                    system_morpheme_class="late_bridge",
                )
            )
        else:
            sg, _, gender = next(noun_cycle)
            name = next(name_cycle)
            licensed = cap(f"Perdi {art(gender)} {sg} de {name} {adv}.")
            violating = cap(f"Perdi {art(gender)} {sg} of {name} {adv}.")
            out.append(
                judgment(
                    new_id(),
                    "T1",
                    next_difficulty(),
                    "Spanish ML. English 'of' is a late bridge system morpheme (taxonomy.md's "
                    "C21, 'el libro of Juan' -- the widening's one unambiguous win); its "
                    "presence inside the Spanish-framed NP is a T1 violation.",
                    T1_DERIVATION,
                    licensed,
                    violating,
                    system_morpheme_class="late_bridge",
                )
            )
    return out


def build_t1_continuation(n: int) -> list[dict]:
    out = []
    noun_cycle = itertools.cycle(NOUNS)
    verb_cycle = itertools.cycle(CARRIER_VERBS)
    poss_cycle = itertools.cycle(POSSESSIVES)
    sub_patterns = itertools.cycle(["article", "possessive"])
    number_cycle = itertools.cycle([False, True])
    poss_frame_cycle = itertools.cycle(["Ella busca", "Ella necesita", "Ella quiere", "Ella tiene"])
    for _ in range(n):
        pattern = next(sub_patterns)
        pret1, _, _ = next(verb_cycle)
        if pattern == "article":
            sg, pl, gender = next(noun_cycle)
            noun, number = (pl, "p") if next(number_cycle) else (sg, "s")
            prompt = pret1.capitalize()
            licensed_c = f"{art(gender, number)} {noun} para la clase"
            violating_c = f"the {noun} para la clase"
            out.append(
                continuation(
                    new_id(),
                    "T1",
                    next_difficulty(),
                    f"Spanish ML frame from '{pret1}'. Licensed continuation keeps the "
                    f"object NP's determiner ML-sourced; violating continuation imports the "
                    f"EL determiner into the same frame.",
                    T1_DERIVATION,
                    prompt,
                    licensed_c,
                    violating_c,
                    system_morpheme_class="early",
                )
            )
        else:
            sg, _, gender = next(noun_cycle)
            eng_poss, mapping = next(poss_cycle)
            sp_poss = mapping[f"{gender}_s"]
            adj = nuevo(gender)
            prompt = next(poss_frame_cycle)
            licensed_c = f"{sp_poss} {sg} {adj}"
            violating_c = f"{eng_poss} {sg} {adj}"
            out.append(
                continuation(
                    new_id(),
                    "T1",
                    next_difficulty(),
                    f"Spanish ML frame ('{prompt}'). Licensed continuation uses the Spanish "
                    f"possessive '{sp_poss}'; violating continuation imports English "
                    f"'{eng_poss}' as an early system morpheme inside the Spanish-framed NP.",
                    T1_DERIVATION,
                    prompt,
                    licensed_c,
                    violating_c,
                    system_morpheme_class="early",
                )
            )
    return out


def build_t1_ml_id(n: int) -> list[dict]:
    out = []
    noun_cycle = itertools.cycle(NOUNS)
    verb_cycle = itertools.cycle(CARRIER_VERBS)
    adv_cycle = itertools.cycle(ADVERBS)
    for _ in range(n):
        sg, _, _ = next(noun_cycle)
        pret1, _, _ = next(verb_cycle)
        adv = next(adv_cycle)
        utterance = cap(f"{pret1.capitalize()} the {sg} {adv} en la tienda.")
        out.append(
            ml_id(
                new_id(),
                "T1",
                next_difficulty(),
                f"ML = Spanish. Verb morphology ('{pret1}') and the null subject are "
                f"Spanish-only properties; only the single determiner 'the' is EL-sourced, "
                f"which is what T1 predicts rather than a wholesale language switch.",
                T1_DERIVATION,
                utterance,
                [
                    f"the verb '{pret1}' carries spanish 1sg preterite morphology",
                    "no subject pronoun appears, licensed by spanish null-subject grammar",
                ],
                system_morpheme_class="early",
            )
        )
    return out


def build_t1_repair(n: int) -> list[dict]:
    out = []
    noun_cycle = itertools.cycle(NOUNS)
    verb_cycle = itertools.cycle(CARRIER_VERBS)
    poss_cycle = itertools.cycle(POSSESSIVES)
    name_cycle = itertools.cycle(NAMES)
    sub_patterns = itertools.cycle(["article", "possessive", "bridge_of"])
    number_cycle = itertools.cycle([False, True])
    for _ in range(n):
        pattern = next(sub_patterns)
        pret1, _, _ = next(verb_cycle)
        if pattern == "article":
            sg, pl, gender = next(noun_cycle)
            noun, number = (pl, "p") if next(number_cycle) else (sg, "s")
            violating = cap(f"{pret1.capitalize()} the {noun} ayer.")
            gold = cap(f"{pret1.capitalize()} {art(gender, number)} {noun} ayer.")
            out.append(
                repair(
                    new_id(),
                    "T1",
                    next_difficulty(),
                    "Minimal repair restores the ML-sourced determiner, the only EL-sourced "
                    "element in the sentence. No competing repair exists for this "
                    "gender/number combination.",
                    T1_DERIVATION,
                    violating,
                    gold,
                    "the",
                )
            )
        elif pattern == "possessive":
            sg, _, gender = next(noun_cycle)
            eng_poss, mapping = next(poss_cycle)
            sp_poss = mapping[f"{gender}_s"]
            violating = cap(f"Necesito {eng_poss} {sg} hoy.")
            gold = cap(f"Necesito {sp_poss} {sg} hoy.")
            out.append(
                repair(
                    new_id(),
                    "T1",
                    next_difficulty(),
                    f"Minimal repair replaces the EL-sourced possessive with its ML-sourced "
                    f"counterpart, the only grammatical option agreeing with '{sg}'.",
                    T1_DERIVATION,
                    violating,
                    gold,
                    eng_poss,
                )
            )
        else:
            sg, _, gender = next(noun_cycle)
            name = next(name_cycle)
            violating = cap(f"Perdi {art(gender)} {sg} of {name} ayer.")
            gold = cap(f"Perdi {art(gender)} {sg} de {name} ayer.")
            out.append(
                repair(
                    new_id(),
                    "T1",
                    next_difficulty(),
                    "Minimal repair replaces the EL-sourced bridge preposition 'of' with "
                    "the ML-sourced 'de'; the rest of the sentence is untouched.",
                    T1_DERIVATION,
                    violating,
                    gold,
                    "of",
                )
            )
    return out


# --------------------------------------------------------------------------------------
# T3 -- Ill-formed EL island
# --------------------------------------------------------------------------------------


def build_t3_judgment(n: int) -> list[dict]:
    out = []
    island_cycle = itertools.cycle(ISLANDS)
    verb_cycle = itertools.cycle(ISLAND_CARRIER_VERBS)
    adv_cycle = itertools.cycle(ADVERBS)
    for _ in range(n):
        island, gender = next(island_cycle)
        pret1, _ = next(verb_cycle)
        adv = next(adv_cycle)
        licensed = cap(f"{pret1.capitalize()} the {island} {adv}.")
        violating = cap(f"{pret1.capitalize()} the {art(gender)} {island} {adv}.")
        out.append(
            judgment(
                new_id(),
                "T3",
                next_difficulty(),
                f"'the {island}' is a complete, internally well-formed EL island under "
                f"English grammar. The Spanish article '{art(gender)}' intruding inside it "
                f"breaks the island's internal integrity -- T3, not T1, because the "
                f"violation is ML material inside an EL-framed constituent.",
                T3_DERIVATION,
                licensed,
                violating,
            )
        )
    return out


def build_t3_continuation(n: int) -> list[dict]:
    out = []
    island_cycle = itertools.cycle(ISLANDS)
    verb_cycle = itertools.cycle(ISLAND_CARRIER_VERBS)
    for _ in range(n):
        island, gender = next(island_cycle)
        pret1, _ = next(verb_cycle)
        prompt = pret1.capitalize()
        licensed_c = f"the {island}"
        violating_c = f"the {art(gender)} {island}"
        out.append(
            continuation(
                new_id(),
                "T3",
                next_difficulty(),
                f"Licensed continuation is a complete EL island ('the {island}'). Violating "
                f"continuation has the Spanish article '{art(gender)}' intruding into that "
                f"island.",
                T3_DERIVATION,
                prompt,
                licensed_c,
                violating_c,
            )
        )
    return out


def build_t3_ml_id(n: int) -> list[dict]:
    out = []
    island_cycle = itertools.cycle(ISLANDS)
    verb_cycle = itertools.cycle(ISLAND_CARRIER_VERBS)
    noun_cycle = itertools.cycle(NOUNS)
    for _ in range(n):
        island, gender = next(island_cycle)
        _, pret3 = next(verb_cycle)
        _, _, filler_gender = next(noun_cycle)
        filler_art = art(filler_gender)
        filler_noun = "calle" if filler_gender == "f" else "trabajo"
        utterance = cap(
            f"{pret3.capitalize()} the {art(gender)} {island} en {filler_art} {filler_noun}."
        )
        out.append(
            ml_id(
                new_id(),
                "T3",
                next_difficulty(),
                "ML = Spanish. The clause frame (verb morphology, the Spanish-sourced PP) "
                "is Spanish; the island's internal breakage does not change which language "
                "supplies the frame. Evidence is independent of the intrusion itself, "
                "avoiding the circularity flagged in build_pilot_items.py's revision 2.",
                T3_DERIVATION,
                utterance,
                [
                    f"the verb '{pret3}' carries spanish 3sg preterite morphology",
                    f"'en {filler_art} {filler_noun}' has a spanish-sourced "
                    "preposition and article",
                ],
            )
        )
    return out


def build_t3_repair(n: int) -> list[dict]:
    out = []
    island_cycle = itertools.cycle(ISLANDS)
    verb_cycle = itertools.cycle(ISLAND_CARRIER_VERBS)
    for _ in range(n):
        island, gender = next(island_cycle)
        pret1, _ = next(verb_cycle)
        art_word = art(gender)
        violating = cap(f"{pret1.capitalize()} the {art_word} {island} ayer.")
        gold = cap(f"{pret1.capitalize()} the {island} ayer.")
        alt = cap(f"{pret1.capitalize()} {art_word} {island} ayer.")
        out.append(
            repair(
                new_id(),
                "T3",
                next_difficulty(),
                "The double-article construction admits two independently grammatical "
                "minimal repairs: delete the intruding ML article (restoring the EL "
                "island) or delete the EL article (leaving a licensed mixed NP). Both "
                "recorded rather than picking one arbitrarily.",
                T3_DERIVATION,
                violating,
                gold,
                art_word,
                alternate_repairs=[alt],
            )
        )
    return out


# --------------------------------------------------------------------------------------
# T5 -- Congruence failure / bare form
# --------------------------------------------------------------------------------------

VERB_ROOTS = list(VERBS.keys())


def build_t5_judgment(n: int) -> list[dict]:
    out = []
    root_cycle = itertools.cycle(VERB_ROOTS)
    frame_cycle = itertools.cycle(MODAL_FRAMES)
    next(root_cycle)  # offset by 1 so the first item doesn't reproduce the pilot's
    # csw-es-en-0021 ("Voy a park el carro."), which also starts at root[0]+frame[0]
    for _ in range(n):
        root = next(root_cycle)
        forms = VERBS[root]
        frame = next(frame_cycle)
        obj = VERB_OBJECTS[root]
        licensed = cap(f"{frame} {forms['inf']} {obj}.")
        violating = cap(f"{frame} {root} {obj}.")
        out.append(
            judgment(
                new_id(),
                "T5",
                next_difficulty(),
                f"'{root}' is an EL content morpheme (assigns the agent/theme role). "
                f"Spanish obligatorily supplies infinitival morphology in the '{frame.lower()}' "
                f"frame; '{forms['inf']}' realizes it via integration, the bare '{root}' "
                f"does not -- T5 fires on the bare form.",
                T5_DERIVATION,
                licensed,
                violating,
            )
        )
    return out


_T5_PROMPTS = [
    ("Todos los dias yo", "pres1"),
    ("Cada manana yo", "pres1"),
    ("Ella siempre", "pres3"),
]


def build_t5_continuation(n: int) -> list[dict]:
    out = []
    root_cycle = itertools.cycle(VERB_ROOTS)
    # Only 1sg/3sg prompts: VERBS only carries pres1/pres3 principal parts, and "Nosotros"
    # would need a distinct 1pl form ("parqueamos") that isn't in the table. 3 prompts,
    # not 2 or 4: with a fixed per-root object (VERB_OBJECTS), (root, prompt) is the
    # entire dedup key, and a prompt-cycle period that divides the 20-root period (as 2
    # and 4 both do) realigns exactly every 20 items regardless of how large a dedup
    # buffer is requested. 3 is coprime with 20, so (root, prompt) only repeats every
    # lcm(20, 3) = 60 items -- outside this cell's n=31+buffer range.
    prompts = itertools.cycle(_T5_PROMPTS)
    for _ in range(n):
        root = next(root_cycle)
        forms = VERBS[root]
        prompt, form_key = next(prompts)
        obj = VERB_OBJECTS[root]
        form = forms[form_key]
        licensed_c = f"{form} {obj}"
        violating_c = f"{root} {obj}"
        out.append(
            continuation(
                new_id(),
                "T5",
                next_difficulty(),
                f"Licensed continuation integrates the EL verb root with obligatory Spanish "
                f"present morphology ('{form}'); violating continuation leaves it bare.",
                T5_DERIVATION,
                prompt,
                licensed_c,
                violating_c,
            )
        )
    return out


def build_t5_ml_id(n: int) -> list[dict]:
    out = []
    root_cycle = itertools.cycle(VERB_ROOTS)
    place_cycle = itertools.cycle(["la oficina", "el trabajo", "la escuela"])
    for _ in range(n):
        root = next(root_cycle)
        obj = VERB_OBJECTS[root]  # real per-verb complement, not an arbitrary noun --
        # "text la ventana" ("text the window") was exactly the kind of semantically
        # anomalous pairing a generic noun cycle produced here before this fix.
        place = next(place_cycle)
        utterance = cap(f"{root.capitalize()} {obj} todos los dias en {place}.")
        out.append(
            ml_id(
                new_id(),
                "T5",
                next_difficulty(),
                f"ML = Spanish. No subject pronoun is expressed (licensed by Spanish's "
                f"null-subject grammar) and 'en {place}' is a Spanish-sourced "
                f"preposition and article; the bare EL verb '{root}' is a congruence "
                f"failure local to that one word, not a change of frame. Evidence is "
                f"drawn from the adjunct PP rather than the verb's own object, since "
                f"some objects here (e.g. 'un rato', 'a Juan') aren't article-headed.",
                T5_DERIVATION,
                utterance,
                [
                    "no subject pronoun is expressed, licensed by spanish's null-subject grammar",
                    f"'en {place}' has a spanish-sourced preposition and article",
                ],
            )
        )
    return out


def build_t5_repair(n: int) -> list[dict]:
    out = []
    root_cycle = itertools.cycle(VERB_ROOTS)
    frame_cycle = itertools.cycle(MODAL_FRAMES)
    for _ in range(2):
        next(root_cycle)  # offset by 2: avoids the pilot's csw-es-en-0028 (root[0]) and
        # this module's own build_t5_judgment phase (offset 1)
    next(frame_cycle)  # also offset frame_cycle by 1: root period 20 and frame period 6
    # would otherwise still realign on root[0]+frame[0] at local index 18 (< n=31)
    for _ in range(n):
        root = next(root_cycle)
        forms = VERBS[root]
        frame = next(frame_cycle)
        obj = VERB_OBJECTS[root]
        violating = cap(f"{frame} {root} {obj}.")
        gold = cap(f"{frame} {forms['inf']} {obj}.")
        out.append(
            repair(
                new_id(),
                "T5",
                next_difficulty(),
                f"Minimal repair replaces the bare EL verb with its morphologically "
                f"integrated infinitive form. The '{frame.lower()} + infinitive' frame "
                f"forces the infinitive shape uniquely; no tense ambiguity.",
                T5_DERIVATION,
                violating,
                gold,
                root,
            )
        )
    return out


# --------------------------------------------------------------------------------------
# Assemble
# --------------------------------------------------------------------------------------

BUILDERS = [
    build_t1_judgment,
    build_t1_continuation,
    build_t1_ml_id,
    build_t1_repair,
    build_t3_judgment,
    build_t3_continuation,
    build_t3_ml_id,
    build_t3_repair,
    build_t5_judgment,
    build_t5_continuation,
    build_t5_ml_id,
    build_t5_repair,
]

# Generation is combinatorial (vocabulary cycled against itself), which occasionally
# reproduces an existing pilot sentence pair exactly, or -- for T5, where each verb root
# now maps to a single fixed VERB_OBJECTS complement -- reproduces another new item's
# pair once the 20-root cycle wraps inside a 31-item target. Over-generate a buffer per
# cell and drop duplicates post hoc rather than hand-tuning cycle offsets against every
# collision found (fragile: the offset math above already broke once when VERB_OBJECTS
# replaced the combinatorial frame/object pairing).
BUFFER = 20


def dedup_key(item: dict) -> tuple:
    tt = item["task_type"]
    if tt == "grammaticality_judgment":
        return (tt, item["licensed"], item["violating"])
    if tt == "constrained_continuation":
        return (
            tt,
            item["prompt"],
            tuple(item["licensed_continuations"]),
            tuple(item["violating_continuations"]),
        )
    if tt == "ml_identification":
        return (tt, item["utterance"])
    return (tt, item["violating"], item["gold_repair"])


def pilot_keys() -> set[tuple]:
    keys = set()
    for path in ITEMS_DIR.glob("csw-es-en-*.json"):
        keys.add(dedup_key(json.loads(path.read_text(encoding="utf-8"))))
    return keys


seen: set[tuple] = pilot_keys()

for builder in BUILDERS:
    candidates = builder(TARGET_PER_CELL + BUFFER)
    accepted = []
    for candidate in candidates:
        key = dedup_key(candidate)
        if key in seen:
            continue
        seen.add(key)
        accepted.append(candidate)
        if len(accepted) == TARGET_PER_CELL:
            break
    assert len(accepted) == TARGET_PER_CELL, (
        f"{builder.__name__}: only {len(accepted)}/{TARGET_PER_CELL} unique items survived "
        f"dedup even with a buffer of {BUFFER} -- raise the buffer or diversify the "
        f"builder's vocabulary further"
    )
    items.extend(accepted)

# IDs are reassigned sequentially post-filter so dropped duplicates don't leave gaps in
# the numbering -- the id a builder attached to a candidate is discarded along with any
# rejected candidate.
for item, n in zip(items, itertools.count(NEXT_ID), strict=False):
    item["id"] = f"csw-es-en-{n:04d}"

seen_ids = [item["id"] for item in items]
assert len(seen_ids) == len(set(seen_ids)), "duplicate item id generated"
assert len(items) == TARGET_PER_CELL * len(BUILDERS), "expected item count mismatch"

ITEMS_DIR.mkdir(parents=True, exist_ok=True)
for item in items:
    path = ITEMS_DIR / f"{item['id']}.json"
    path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

last_id = int(items[-1]["id"].rsplit("-", 1)[1])
print(f"wrote {len(items)} new items ({NEXT_ID:04d}-{last_id:04d}) to {ITEMS_DIR}")
