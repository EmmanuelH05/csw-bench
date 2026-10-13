# Corpus sources and licensing

Phase 1 Track A. Gates Phase 2: no item may cite a source whose terms have not been read.

**Headline: the licensing is more restrictive than assumed, and it constrains `matriz`,
not just this repo.** Bangor Miami is CC BY-NC-SA 3.0 per TalkBank's access-page terms;
Spanish in Texas is CC BY-NC-**ND** 4.0, which forbids redistributing derived items at
all; LinCE states no license anywhere and its site is currently down. Details in §4.

**⚠ Update, 2026-08-16: Bangor Miami's license is contested between two public TalkBank
pages** (CC BY-NC-SA 3.0 vs. the depositor's own GPL v3) **and stays that way** — no
depositor contact is being pursued for this project. Operating permanently under the
union of both readings' obligations. See §1, "Decided, permanently."

## 1. Bangor Miami Corpus

| | |
|---|---|
| Content | 56 audio files, ~35 hours, 84 Spanish/English bilinguals in Miami, 2008–2011 |
| Size | ~242,475 transcribed words — 63% English, 34% Spanish, 3% undetermined |
| Annotation | Token-level language ID, start/end time alignment |
| Host | TalkBank / BilingBank |
| **License** | **Contested, permanently operating under the union of both readings.** TalkBank's access page says CC BY-NC-SA 3.0; the depositor's own documentation says GPL v3. No depositor contact is being pursued (see journal.md) — this project complies with the combined obligations of both rather than picking one. See "Decided, permanently" below. |
| Citation | Deuchar, M., & Parafita Couto, M. (2011). *The Bangor Miami Corpus.* TalkBank. doi:10.21415/T5J01D |

Attribution is mandatory and specific: TalkBank requires the corpus be named "the Bangor
Miami corpus" with a link to the access point used.

**This is the primary source.** It is the right size, it is naturalistic conversational
speech rather than elicited data, and it contains intrasentential switching of exactly
the kind the benchmark targets.

### ⚠ New, unresolved conflict — the depositor's own documentation states a different license

**2026-08-16.** `Miami_doc.pdf`, the corpus documentation file hosted at the canonical
TalkBank access page and authored by the corpus depositor (Margaret Deuchar, Bangor
University), states under "Conditions of use":

> "The corpus is being made available under the GNU General Public License version 3 or
> later (http://gnu.org/copyleft/gpl.html). Researchers who use it are requested to
> subscribe to the TalkBank Code of Ethics ... and acknowledge the corpus as set out
> below."

This is **GPL v3**, not CC BY-NC-SA 3.0. It is a primary source — the depositor's own
statement, at the canonical download location — and it directly conflicts with the
CC BY-NC-SA 3.0 finding this document was built around, which came from TalkBank's
separate access/terms page for the corpus (`Miami.html`, not `Miami_doc.pdf`) and from
TalkBank's site-wide data-sharing policy.

**Decided, permanently: comply with the union of both readings.** No email to the
depositor is being sent for this project — see `journal.md` for the scope decision this
follows from. Between the two live readings —

1. **Both apply, stacked.** TalkBank's site-wide terms (CC BY-NC-SA, no LLM incorporation)
   govern *access to data hosted on TalkBank*; the depositor's GPL v3 statement governs
   *the corpus content itself*, layered on top. A user satisfies both by satisfying the
   union of their obligations.
2. **The depositor's stated license controls** and TalkBank's page is a restatement
   error, in which case GPL v3's copyleft mechanics — not CC's NC/SA terms — actually
   govern, and whether a fine-tuned model counts as a GPL "derivative work" is a genuinely
   open question this project cannot resolve alone.

— **this project operates permanently under reading 1's obligations**, since compliance
with the union of both readings' restrictions satisfies either reading individually,
regardless of which authority turns out to be correct. Concretely: attribution (both
require it), non-commercial use only (from the CC reading; GPL does not relax this, since
GPL permits commercial use but does not forbid a stricter voluntary restriction on top of
it), and share-alike/no-relicensing for any adaptation (both require an equivalent
obligation). This does not resolve reading 2's open question about whether a fine-tuned
model is a GPL derivative work — that risk is accepted, named here, and carried into
`limitations.md` rather than chased down, since resolving it requires the depositor's own
answer and this project is not pursuing that contact.

### The three license clauses, and what each costs us

**BY — attribution.** Cheap. Already required by our own provenance rules.

**NC — non-commercial.** TalkBank states this "precludes the incorporation of the data
in commercial products, including systems such as large language models (LLMs) such as
ChatGPT," and separately that commercial enterprises with data access "can use the data
for the development of algorithms... but the data themselves cannot be included in
models."

**SA — share-alike.** Adaptations must carry the same license. Items derived from Bangor
Miami are adaptations. They therefore **cannot be MIT-licensed**, which is what the repo
currently declares.

## 2. Spanish in Texas Corpus

| | |
|---|---|
| Content | Spanish and bilingual Spanish–English speech from interviews and conversations, speakers of diverse profiles and regional origins across Texas; collected 2011–2013 |
| Size | **500,000+ words, 96 bilingual speakers** (the project's own web page says 97; the deposit metadata and the metadata file — 96 observations — say 96) |
| Materials | Video, audio, full transcripts, POS annotations (`-data-tag.zip`), plus `.srt` and `.vtt` caption tracks. 101 files, version 1.1, published 2024-07-11 |
| Annotation | POS. **No token-level language ID is documented in the deposit metadata.** |
| Host | Texas Data Repository (Dataverse), COERLL / UT Austin collection |
| **License** | **CC BY-NC-ND 4.0** — stated verbatim in the dataset's Custom Dataset Terms |
| Citation | Bullock, Barbara E. and Toribio, Almeida Jacqueline. 2013. *The Spanish in Texas Corpus Project.* COERLL, The University of Texas at Austin. https://doi.org/10.18738/T8/GBYLXB |

The deposit's **Terms of Use** field reads, in full: "The Spanish in Texas Corpus is
licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives 4.0
International License."

### ND is the whole story

**Derived data may not be redistributed.** ND forbids distributing adapted material. A
benchmark item built from a SpinTX transcript — retokenized, relabelled, spliced,
minimally-paired — is an adaptation. Under a plain reading of CC BY-NC-ND 4.0 we may
*use* the corpus to study, and we may reproduce verbatim portions with attribution, but
we may not publish modified versions. That is a harder constraint than Bangor Miami's SA,
which merely dictates *which* license adaptations carry.

The two are also mutually incompatible as a combined pool: BY-NC-SA requires adaptations
be shared alike, BY-NC-ND forbids sharing adaptations at all. Items must stay
single-sourced and per-item licensed; there is no merged corpus.

**NC applies too** — non-commercial, same posture as Bangor Miami.

### Registration and ethics terms

Access is free but gated. Downloading triggers a Dataverse **guestbook** ("Spanish in
Texas Corpus Preview Guestbook") that collects name and contact information, and the
project page asks users to "abide by our Code of Ethics." The deposit's **Restrictions**
field is the operative version of that Code, and it is short:

- *Respect for participants* — "All users will refrain from making any disparaging remarks
  about the individual persons, the views, or the speech represented in the corpus."
- *Confidentiality of participants* — "researchers will use pseudonyms when referring to
  individual participants."

The pseudonym rule binds us directly: any item drawn from this corpus must carry a
pseudonymous speaker reference, never a corpus speaker ID that resolves to a named person.

### A published source contradicts the deposit — trust the deposit

`spintx.org/about` states the corpus is under **CC BY-NC-SA 3.0**. The Texas Data
Repository deposit states **CC BY-NC-ND 4.0**. These are not compatible claims: SA permits
adaptations, ND forbids them. The deposit is the authoritative distribution channel and
carries the DOI in the required citation, so **we operate under BY-NC-ND 4.0**. This is
exactly the trap that a search-result summary walks into — verify at the deposit page, not
the project site.

*(Note: `dataverse.tdl.org` sits behind a CloudFront WAF that rejects default HTTP clients
with a 403. It serves normally to a browser User-Agent. A 403 here is not evidence of
restricted access.)*

## 3. LinCE

Aggregates ten corpora across four language pairs. Findings below are from the LinCE
datasets page, the LREC 2020 paper, the constituent shared-task papers, and the HF loader
script.

| | |
|---|---|
| **License** | **NONE STATED — UNVERIFIED.** See below. |
| Access | Account required: the datasets page reads "Please log in to download the datasets." |
| Availability | `ritual.uh.edu` was **unreachable** during this recon (connection refused, DNS resolves to 129.7.248.228). Findings come from Wayback snapshots. |

### 3.1 The Spanish/English constituents

| Task | Underlying corpus | Original source |
|---|---|---|
| LID | Molina et al. 2016, CALCS 2016 shared task | **Twitter** — 32,651 posts |
| POS | LinCE datasets page cites AlGhamdi et al. 2016 (CALCS 2016 POS); the LREC paper §4.2 says "the Miami Bangor corpus with the annotations provided by Soto and Hirschberg (2017)" | **Bangor Miami** either way — AlGhamdi et al. 2016 states its SPA-ENG data is two sets, a transcribed conversation set ("Spanglish") and "the Bangor Miami corpus" |
| NER | Aguilar et al. 2018, CALCS 2018 shared task | **Twitter** — 67,223 tweets |
| SA | Patwa et al. 2020, SemEval-2020 Task 9 (SentiMix) | **Twitter** — 18,789 tweets |

Three of the four SPA-ENG constituents are Twitter data. The fourth is Bangor Miami,
already covered in §1 — **which means the CC BY-NC-SA 3.0 obligation reaches into LinCE's
POS split**, and using LinCE does not launder it.

The two documentation sources disagree on which paper to cite for `pos_spaeng`. That is
LinCE's inconsistency, not an ambiguity about the data: both routes lead to Bangor Miami.

### 3.2 The Twitter constraint is real and it is a distribution constraint

The CALCS shared tasks distributed tweet IDs plus a crawler script, not text. Molina et
al. 2016 states its evaluation tables include "only the tweets that all the participants
managed to crawl from Twitter, and it is not the complete data set"; Aguilar et al. 2018
describes tweets removed because they were deleted, suspended, or failed "when they are
retrieved using the crawler script." Both are the signature of ID-based distribution.

LinCE itself distributes *tokenized surface text* behind its login — its HF loader pulls
per-user zips from `ritual.uh.edu/lince/libaccess/<base64 user token>`, and the HF dataset
card's own sample rows contain full tweet text and @-handles. So LinCE resolved the
hydration problem for its own users. **That does not transfer to us.** X/Twitter's
developer terms permit third parties to redistribute only Tweet IDs, and no LinCE page
grants us a redistribution right that would override that. *Inference, clearly marked:* we
should assume any LinCE-derived Twitter text cannot be republished as text in this repo.

### 3.3 The license is not merely restrictive — it is absent

**No license statement appears anywhere on the LinCE site.** The datasets page lists only
citations and the request "Please cite them if you use any of the related datasets." The
LREC paper is silent on licensing of constituents (the CC-BY-NC on its front matter is
ELRA's license for the *paper*). The HuggingFace mirror's Licensing Information section
reads "More Information Needed." SemEval-2020 Task 9's paper is CC BY 4.0 — again the
paper, not the data.

**Marked UNVERIFIED.** What was tried: `ritual.uh.edu/lince/` and `/lince/datasets` direct
(connection refused); Wayback snapshots of `/lince/home`, `/lince/datasets`, `/lince/faq`
(retrieved; faq body is JS-rendered and empty in archive); the LREC 2020 PDF; the CALCS
2016, CALCS 2018 and SemEval-2020 Task 9 PDFs; the HF dataset card and loader script.
Registering an account would surface whatever terms the login flow presents — but the site
is down, so that is not currently possible.

### 3.4 What LinCE is good for here

**Its tasks are LID, NER, POS, and sentiment — not grammaticality.** So LinCE supplies
*candidate code-switched utterances*, never gold MLF labels. Useful as raw material for
item construction, useless as a label source. Treating it otherwise would import
annotations that answer a different question.

## 4. Consequences — decisions this forces

### 4.1 The repo needs dual licensing

Code stays MIT. **Items derived from Bangor Miami must be CC BY-NC-SA 3.0.** The current
`LICENSE` note gestures at "source corpora licenses" without naming one, which is not
good enough now that we know the answer. This must be fixed before any attested item is
committed.

### 4.2 The benchmark is non-commercial, and that has to be said out loud

Anyone using `csw-bench` with attested items inherits NC. That belongs in `README.md`,
not buried here — a user who builds on this and later commercializes has a problem we
could have warned them about in one sentence.

### 4.3 `matriz` has real NC exposure — decided permanently, not assumed away

`matriz` fine-tunes models on these items. TalkBank explicitly names LLMs and says the
data cannot be included in models.

The favorable reading: that restriction appears in a passage addressed to *commercial
enterprises*, and `matriz` is non-commercial academic research, which is squarely what
CC BY-NC-SA permits. The unfavorable reading: "cannot be included in models" is stated
flatly, and a fine-tuned model is a model.

Written confirmation from the depositor would resolve this cleanly, but no email is being
sent for this project (see `journal.md`) — the choice is between the three options below
on the evidence already in hand, not a placeholder pending outside contact.

1. **Proceed on the non-commercial reading**, document it, and never release a model
   trained on attested items commercially. Lowest friction, carries residual risk.
2. **Email the corpus authors** for written clarification. Converts a risk into a
   documented permission, but requires external contact this project is not pursuing.
3. **Train `matriz` on constructed items only**, using attested items purely for
   evaluation. Cleanest legally, and the held-out design partly supports it — but it
   weakens the training set and needs to be a deliberate choice, not a fallback.

**Decided, permanently: option 1.** `matriz` treats attested items as non-commercial-only
and never releases a model trained on them commercially. This is a real, standing
constraint on the downstream project, not a stopgap — residual legal risk is accepted and
named rather than resolved, consistent with the scope decision to not pursue depositor
contact for this project.

### 4.4 Items store references plus minimal excerpts, not transcript dumps

Item design should record corpus ID, file, and token span, alongside the shortest excerpt
that makes the item interpretable. Minimal quotation for scholarly analysis is defensible
and keeps us well clear of redistributing transcript bulk.

### 4.5 Spanish in Texas is effectively unusable as an item source — new

ND kills the obvious use. We cannot ship items that adapt SpinTX material, which is what
every item does. Three live options, in preference order:

1. **Drop it as an item source.** Cite it as background, use it to calibrate intuitions,
   build no items from it. Zero legal exposure, small cost — Bangor Miami is the better
   corpus for this benchmark anyway.
2. **Email Bullock and Toribio** for permission to distribute derived items. Same email
   trip as §4.3; worth combining if we want the corpus.
3. **Verbatim-only items.** Arguably an unmodified quotation with attribution is not an
   adaptation. Thin ice, depends on item design never touching the text, and ND makes even
   the retokenization we would need for a token-span reference questionable. Not
   recommended without option 2.

**Decided: option 1.** Spanish in Texas is cited as background and used to calibrate
intuitions only; no item is built from it. Bangor Miami is the sole item source, and this
decision does not need to be revisited unless Bangor Miami's supply turns out to be
insufficient — at which point option 2 (email) is the fallback, not option 3.

The pseudonym requirement applies to any speaker reference regardless.

### 4.6 Sources cannot be pooled — new

BY-NC-SA (Bangor Miami) and BY-NC-ND (SpinTX) cannot coexist in one derived artifact: one
mandates that adaptations be shared alike, the other forbids adaptations. There is no
"csw-bench corpus." There are per-item licenses and a loader that filters on them, which
§4.7 already required for a different reason and now requires twice over.

### 4.7 The schema needs a per-item license field — Phase 3 consequence

Items will come from sources under different terms, so `license` is a required per-item
field and the loader must be able to filter on it. A user needing MIT-only items should
be able to get them. **This is a Phase 3 API requirement discovered in Phase 1**, which is
the point of doing Track A before building anything.

### 4.8 LinCE cannot be cited as a source until its terms are known — new

An absent license is not a permissive one. Combined with the Twitter redistribution
constraint and the fact that its POS split is Bangor Miami wearing a different name, LinCE
currently offers nothing we cannot get more cleanly from Bangor Miami directly. **Treat it
as blocked**, and if it is ever wanted, go to the constituent corpora rather than to LinCE.

## 5. Status

- [x] **Bangor Miami — license contested between two TalkBank pages, resolved by policy
      rather than by asking.** CC BY-NC-SA 3.0 (access page) vs. GPL v3 (depositor's own
      documentation). No depositor contact is being pursued for this project (see
      `journal.md`); operating permanently under the union of both readings' obligations.
      See §1.
- [x] Spanish in Texas — deposit terms read; **CC BY-NC-ND 4.0**, derived items may not be
      redistributed (§2, §4.5)
- [x] LinCE — Spanish/English constituents identified (§3.1); **no license is stated
      anywhere**, marked UNVERIFIED (§3.3)
- [x] Decide the `matriz` NC question (§4.3) — decided permanently: non-commercial
      reading, no model trained on attested items released commercially. Not contingent
      on depositor contact, since none is being pursued.
- [x] Decide the Spanish in Texas ND question (§4.5) — dropped as an item source,
      Bangor Miami only
- [x] Update `LICENSE` and `README.md` for dual licensing — both now state the license
      conflict explicitly and the union-compliance policy, rather than asserting
      CC BY-NC-SA 3.0 as settled fact
- [x] **Confirm Bangor Miami download is reachable — confirmed blocked, not pursued
      further.** `Miami_doc.pdf`, the corpus documentation, downloaded successfully over
      plain HTTPS with no account — the documentation and the transcript data sit behind
      different gates. The transcript browser (`sla.talkbank.org/TBB/...`) was tried
      directly this session and returns a 469-byte JS app shell containing a client-side
      `authModals` object — a genuine login gate, not a slow-loading page, and not
      something this project attempts to route around. **No attested items will be built
      from Bangor Miami transcripts this project**, since that requires an account this
      project is not creating (see `journal.md` for the scope decision). The documentation
      confirms corpus size (242,475 words, 84 speakers, 35:11:04 total) but does **not**
      give speaker national-origin or dialect background regardless.

## Sources

Pages actually fetched during this recon.

- [BilingBank Spanish-English Bangor Miami Corpus](https://talkbank.org/biling/access/Bangor/Miami.html)
- [TalkBank Basic Rules for Data Usage](https://talkbank.org/0share/rules.html)
- [Spanish in Texas Corpus — project site](https://corpus.spanishintexas.org/)
- [Spanish in Texas Corpus — Texas Data Repository deposit (authoritative terms)](https://dataverse.tdl.org/dataset.xhtml?persistentId=doi:10.18738/T8/GBYLXB)
- [SpinTX About page — states the contradicting CC BY-NC-SA 3.0](https://spintx.org/about/)
- [LinCE: A Centralized Benchmark for Linguistic Code-switching Evaluation](https://aclanthology.org/2020.lrec-1.223/) ([PDF](https://aclanthology.org/2020.lrec-1.223.pdf))
- [LinCE datasets page, Wayback 2020-10-21](https://web.archive.org/web/20201021081803/https://ritual.uh.edu/lince/datasets)
- [LinCE home, Wayback 2021-12-09](https://web.archive.org/web/20211209094613/https://ritual.uh.edu/lince/home)
- [HuggingFace `lince-benchmark/lince` dataset card](https://huggingface.co/datasets/lince-benchmark/lince) and [loader script](https://huggingface.co/datasets/lince-benchmark/lince/blob/main/lince.py)
- [Molina et al. 2016, CALCS 2016 LID shared task](https://aclanthology.org/W16-5805.pdf)
- [AlGhamdi et al. 2016, POS Tagging for Code Switched Data](https://aclanthology.org/W16-5812.pdf)
- [Aguilar et al. 2018, CALCS 2018 NER shared task](https://aclanthology.org/W18-3219.pdf)
- [Patwa et al. 2020, SemEval-2020 Task 9 SentiMix](https://aclanthology.org/2020.semeval-1.100.pdf)
