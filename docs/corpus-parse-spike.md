# Bangor Miami download and parse spike

Closes the open item "Confirm Bangor Miami download is reachable and parses" in
`docs/corpora.md` §5 — with a negative result at step one.

**Verdict: blocked at download.** Not 404, not licence refusal — TalkBank now puts an
authentication wall in front of every bulk download URL under `/data/`. Nothing was
parsed, so every claim below about file format is marked as unverified and sourced to
TalkBank's own pages, not to files on disk.

## 1. What was tried

Every URL below was fetched with `curl -sSL` on 2026-08-15. No file was left on disk;
`data/corpora/restricted/` was removed after the probes.

| URL | HTTP | Bytes | Result |
|---|---|---|---|
| `talkbank.org/data-xml/BilingBank/Bangor/Miami.zip` | 404 | 162 | path does not exist |
| `talkbank.org/data/BilingBank/Bangor/Miami.zip` | 200 | 319 | auth modal HTML |
| `talkbank.org/data/biling/Bangor/Miami?f=zip` | 200 | 319 | auth modal HTML |
| `media.talkbank.org/biling/Bangor/Miami/` | 200 | 319 | auth modal HTML |
| `talkbank.org/data-xml/biling/Bangor/Miami.zip` | 404 | 162 | path does not exist |
| `sla.talkbank.org/data/BilingBank/Bangor/Miami.zip` | 404 | 279 | path does not exist |
| `biling.talkbank.org/data/Bangor/Miami.zip` | 404 | 162 | path does not exist |

The two URLs given as known-good in the task brief are both dead ends: the `data-xml`
path 404s, and the `data` path returns HTTP 200 with a 319-byte HTML page — a `curl`
run that does not check content type will silently write this to `Miami.zip` and look
like it succeeded. It is not a zip:

```html
<html><body><script type="module">
  import { initAuthModals } from 'https://sla2.talkbank.org:443/authUI/authModals.js';
  initAuthModals('https://sla2.talkbank.org:443', ...);
</script></body></html>
```

The canonical download link, scraped from the corpus's own access page, is
`/data/biling/Bangor/Miami?f=zip`. It returns the same auth modal.

## 2. The gate is site-wide, not corpus-specific

`talkbank.org/data/Eng-NA/Brown.zip` — the Brown CHILDES corpus, openly licensed and
historically a plain anonymous download — returns the identical 319-byte auth modal.

So this is a login requirement across all of TalkBank's bulk-download endpoints, not a
restriction imposed on Bangor Miami or on BilingBank. TalkBank's own ground rules
(`talkbank.org/0share/rules.html`) still describe password protection as applying only
to the clinical banks (AphasiaBank, DementiaBank, FluencyBank, RHDBank, TBIBank),
HomeBank, and PsychosisBank — BilingBank is not in that list. The documentation has not
caught up with the deployed auth layer.

Practical consequence: this is a free-account problem, not a permission-request problem.
It should be resolvable by registering a TalkBank account and passing a session cookie,
rather than by negotiating access with the depositors.

## 3. A licence constraint found while reading the rules

TalkBank's ground rules contain a clause not recorded in `docs/corpora.md`, and it bites
Phase 3 directly:

> Users cannot upload TalkBank data to web-based systems unless those systems include
> assurance that they will not keep the data. In particular, data can only be uploaded
> for processing by OpenAI, Anthropic, Google, Rev-AI and similar systems if the user
> has specifically selected the option for non-storage of data.

The Phase 3 harness sends items to at least three model families. If those items carry
Bangor Miami excerpts, every provider account used for a run must have training/retention
opted out, and which accounts were configured how becomes a reportable detail of the run
— not a footnote. This is a stronger constraint than the NC clause already documented,
because it applies to evaluation, not only to `matriz`'s fine-tuning.

> **Amended 2026-08-17 — same treatment as `docs/design.md` §5.7.** Phase 3 now runs
> exclusively against a local Ollama server, not the three cloud vendors this section
> assumed; "provider accounts" no longer exist as a concept for this project. The
> constraint stops binding only for a run that is *actually* local — a property
> `OllamaProvider` now enforces (explicit host pinning, rejection of `:cloud`-routed model
> tags) and records (`RunConfig.provider_host`), not one that follows automatically from
> "it's Ollama." See `docs/journal.md`, "Phase 3 pivot: local models," for the full
> account, including the gap a self-review found in the first draft of this exact
> amendment.

There is also an NIH Certificate of Confidentiality clause: downloaded identifiable data
may be stored only on a local device for analysis and may not be circulated further.
That is consistent with the §4.4 decision to store references plus minimal excerpts, and
is a further argument against ever committing transcript bulk.

## 4. Format — unverified, from documentation only

None of this was observed in a file. It is recorded so the next attempt knows what to
check, and every line of it must be confirmed against real data before any item cites it.

From the corpus access page (`talkbank.org/biling/access/Bangor/Miami.html`): 56 audio
recordings and corresponding transcripts, 84 speakers, informal conversation, recorded
2008–2011. TalkBank distributes transcripts in CHAT (`.cha`), and the Bangor project's
own site (`bangortalk.org.uk`, currently returning 503) distributes a glossed format
produced by the Bangor Autoglosser (Donnelly & Deuchar 2011, cited on the access page).

The three questions this spike existed to answer are all still open:

- **Is language ID token-level?** `docs/corpora.md` asserts it is. Unconfirmed here. The
  specific thing to check is whether CHAT precodes (`[- spa]`, utterance-level) or `@s`
  language suffixes on individual words (token-level) are used, and whether both appear.
  Utterance-level marking alone would be much weaker than the table in `docs/corpora.md`
  currently implies, and would change what item extraction can claim.
- **Are `%mor` tiers present?** Unknown. This is the load-bearing question. The violation
  taxonomy distinguishes system from content morphemes, and without morphological tiers
  that distinction has to be reconstructed by a tagger we would then have to validate —
  turning a parsing job into an annotation project. The Autoglosser output suggests
  gloss and POS tiers exist in *some* distribution of the corpus, but whether they ship
  in the TalkBank `.cha` files is exactly what could not be checked.
- **Speaker IDs and timestamps?** Almost certainly yes for speaker IDs (CHAT `*SPK:`
  is structural) and likely for timestamps given the access page lists audio media and
  `docs/corpora.md` records start/end alignment. Still unverified.

## 5. What a parser would need to do

Sketch only, contingent on §4 being confirmed.

Read `.cha` files as UTF-8, split on the CHAT tier structure: `@`-prefixed headers, one
`*SPK:` main tier per utterance with an optional trailing `NNNN_NNNN` millisecond
bullet, and `%`-prefixed dependent tiers bound to the preceding main tier. Language
membership per token comes from the `@s` suffix convention if present, otherwise falls
back to whatever the `%mor` or gloss tier encodes. An utterance is a code-switching
candidate when its tokens carry more than one language tag and the switch is
clause-internal rather than a turn boundary.

Do not hand-roll this. `pylangacq` and `chatparser` both parse CHAT, and PyPI's
`pylangacq` handles `%mor` tiers specifically. Per the no-new-dependencies rule this is
recorded as a recommendation, not added to `pyproject.toml` — and the choice should be
made after seeing real files, since the right library depends on whether the morphology
tiers are actually there.

## 6. Is item extraction feasible?

**Blocked, pending a login.** Not hard, not straightforward — unknown, and it stays
unknown until the files are in hand. The evidence says the blocker is authentication
rather than permission, which is the cheap kind of blocker, but calling the parse
"feasible" now would be a guess dressed as a finding.

Next actions, in order:

1. Register a TalkBank account and retry `/data/biling/Bangor/Miami?f=zip` with the
   session cookie. Verify the response is `application/zip` and not 319 bytes of HTML.
2. Re-run this spike against real files and replace §4 with observed facts.
3. Record the answer to the `%mor` question in `docs/taxonomy.md`, because if the tiers
   are absent the taxonomy's system/content diagnostic needs a different evidence source.
4. Add the Phase 3 provider-retention requirement from §3 to `docs/design.md`.

Any download script written later must assert on content type. A 200 from TalkBank is
not a successful download.
