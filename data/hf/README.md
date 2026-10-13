---
pretty_name: csw-bench
license: mit
language:
  - es
  - en
language_creators:
  - expert-generated
multilinguality:
  - multilingual
size_categories:
  - n<1K
task_categories:
  - text-classification
  - text-generation
task_ids:
  - acceptability-classification
tags:
  - code-switching
  - spanglish
  - matrix-language-frame
  - bilingualism
  - linguistics
  - evaluation
  - benchmark
annotations_creators:
  - expert-generated
source_datasets:
  - original
configs:
  - config_name: grammaticality_judgment
    data_files:
      - split: test
        path: grammaticality_judgment.jsonl
  - config_name: constrained_continuation
    data_files:
      - split: test
        path: constrained_continuation.jsonl
  - config_name: ml_identification
    data_files:
      - split: test
        path: ml_identification.jsonl
  - config_name: repair
    data_files:
      - split: test
        path: repair.jsonl
---

# csw-bench v1.0

402 Spanish/English code-switching items that test whether a language model handles
mixing inside a single clause the way the Matrix Language Frame (MLF) model predicts,
instead of treating mixed input as broken Spanish or broken English.

- Version 1.0, released 2026-09-11.
- Item-set SHA-256: `baf85c444ea741fd812f8f09eeafe9048db617b7383025c5b353a7c66fab069c`.
  Record it with any result you publish; `csw-bench stats` recomputes it.
- Code, scorer, run artifacts and full documentation: https://github.com/yungmanny/csw-bench
- One language pair, Spanish/English. Every item's Matrix Language is Spanish.

## Dataset summary

MLF (Myers-Scotton 1993) says that in a code-switched clause one language, the Matrix
Language, supplies the grammatical frame (function words, inflection, word order) and
the other, the Embedded Language, contributes content words and whole well-formed
islands. "Compré the books ayer" follows that rule; "Compré the libros ayer" breaks it,
because an English function word sits where Spanish grammar is in charge. The items
operationalize three named MLF predictions as violation types:

| Type | MLF prediction | What the violation looks like |
|---|---|---|
| T1 | System Morpheme Principle | an English system morpheme (the, -s, ...) inside a Spanish-framed constituent |
| T3 | EL Island Trigger Hypothesis | Spanish material intrudes into, or cuts, an English island |
| T5 | Blocking Hypothesis | a bare English content word lacks the morphology Spanish obligatorily supplies |

Each type has 134 items, spread about 31 per (violation type x task type) cell.

## Configs

One config per task type, each a single `test` split. The task types test different
things and the repository never averages across them.

| Config | Items | The model is asked to | Gold |
|---|---|---|---|
| `grammaticality_judgment` | 102 | pick the acceptable member of a minimal pair | `licensed` vs `violating` |
| `constrained_continuation` | 100 | finish a code-switched prompt | `licensed_continuations` vs `violating_continuations` |
| `ml_identification` | 100 | name the Matrix Language and cite morphosyntactic evidence | `matrix_language`, `required_evidence` |
| `repair` | 100 | fix a violating utterance with the smallest change | `gold_repair`, `alternate_repairs`, `violation_span` |

```python
from datasets import load_dataset

judgment = load_dataset("yungmanny/csw-bench", "grammaticality_judgment", split="test")
repair = load_dataset("yungmanny/csw-bench", "repair", split="test")
```

## Data fields

Every row carries:

- `id`: `csw-es-en-NNNN`, unique across all four configs.
- `task_type`: the config name.
- `matrix_language`: `es` on every item (see "Known errata").
- `primary_violation`: exactly one of `T1`, `T3`, `T5`. `secondary_violations` lists any
  others present (usually empty).
- `difficulty`: `easy`, `medium` or `hard`, the author's rating.
- `justification`: why the gold answer is correct, in MLF terms.
- `system_morpheme_class`: for T1 items, the 4-M class of the offending morpheme
  (`early`, `late_bridge`, `late_outsider`); `null` otherwise.
- `contested_segmentation`: `true` when the constituent segmentation that decides the
  type is itself arguable. Reported, not resolved.
- `provenance`: `source` (`constructed` for all 402), `license` (`MIT` for all 402),
  `derivation` (the MLF prediction the item was built from), `reviewed_by` (review pass
  ids), `review_disagreement` (the losing argument when reviewers disagreed, kept rather
  than resolved; one item), and `citation_key` / `corpus_ref` (always `null` here, used
  only by corpus-derived items).

Per config:

- `grammaticality_judgment`: `licensed`, `violating`. The pair differs only in the
  violation. The csw-bench runner derives presentation order from a hash of `id` so that
  position is balanced across the set.
- `constrained_continuation`: `prompt`, `licensed_continuations`,
  `violating_continuations`.
- `ml_identification`: `utterance`, `required_evidence` (morphosyntactic evidence
  strings; lexical-frequency reasoning never appears here and earns no evidence credit).
- `repair`: `violating`, `gold_repair`, `alternate_repairs` (equally minimal fixes),
  `violation_span` (token index range of the violation in `violating`).

## Scoring

The reference scorer is `csw_bench.scoring` in the code repository. In short: judgment is
forced choice against a 0.5 floor; ML identification is 1 point for the label and 2 for
evidence, with a 1/3 floor because the constant answer "Spanish" earns the label point on
every item; continuation and repair are 0 to 2 points with no floor, and a repair that
reaches the gold string by rewriting more than the violation site earns 1 of 2. Hedging
("it depends", "both are") scores zero on every task. Scores are reported per task with
95% bootstrap intervals and are never averaged across tasks.

## Intended use

Evaluating whether a model represents the MLF constraints on Spanish/English
intrasentential switching, and, downstream, whether those constraints are learnable by
fine-tuning while holding out a whole violation type (the `primary_violation` field is
single-valued for exactly that reason). Spanish/English only; single clauses only;
constructed stimuli only.

Not intended for: measuring general code-switching competence, translation quality,
fluency in either language alone, or anything about other language pairs. Not a
training set. A low score is evidence against MLF-consistency, not evidence that a
model "cannot code-switch"; a model may follow a different, defensible theory of
switching.

## How the items were built

All 402 items are constructed from documented MLF predictions, with the derivation
recorded per item. No corpus-derived item shipped: the Spanish in Texas corpus is CC
BY-NC-ND (no derived items) and LinCE states no license; the Bangor Miami corpus was
usable in principle but its access is gated, and the repository's `docs/corpora.md`
records the licensing survey. An item and its gold label were never produced in the same
pass. Every item went through a second, blind review pass that never saw the gold label;
disagreement is logged in the item (`provenance.review_disagreement`) rather than
resolved. The 30 pilot items had 29/30 construct-validity agreement with one logged
disagreement. The 372 items added afterwards were blind-reviewed on a 120-item
stratified sample; the answer files behind that sample were lost before being committed,
so its agreement figures are recorded in the repository's journal as historical and are
not reproducible.

The reviewers were language models, not bilingual humans. This is a named degradation
from the original design and the repository's limitations document treats it as a
first-class threat: a model reviewer may share a blind spot with the models under test.

## Known errata

Found before the v1.0 tag and shipped as-is, because repairing them would disconnect
every committed result from the data it describes. Each is a v1.1 candidate. Full
account in the repository's `docs/limitations.md` ("Known item-set defects at v1.0"),
and anything found after the tag goes to `ERRATA.md` there.

1. **The 372 post-pilot items carry no Spanish diacritics** ("Compre", "manana"). The
   scorer strips diacritics before comparing, so answers are unaffected, but the model
   is shown non-standard Spanish on those items and standard Spanish on the 30 pilot
   items.
2. **Every item's Matrix Language is Spanish.** The `ml_identification` label point is
   earned by a constant answer; only the evidence points discriminate.
3. **The 100 `constrained_continuation` items render to 24 distinct prompts.** At
   temperature 0 one prompt gets one response, shared by every sibling item, and a
   response can match at most one sibling's gold string; the best possible score on
   that task is 24/100.
4. **Continuation is scored as exact-string coincidence** against the recorded
   continuations. A licensed construction with a different noun scores the same as a
   failure. Read that task through the violation-production rate, not the score.

A fifth caveat is about the scorer rather than the items: the `ml_identification`
evidence check is a substring match against `required_evidence`, which credited none of
the 158 scored responses across the three committed model runs. Under the v1.0 scorer
that task's above-chance value cannot be positive for any model.

## Results on this set

Three local models (qwen3:30b, gpt-oss:20b, deepseek-r1:32b via Ollama, temperature 0,
seed 42, 8192-token budget) are reported in the repository's `docs/results.md` with
bootstrap intervals and per-violation rows, and every number regenerates from the
committed run directories without a model call.

## Licensing

Code is MIT. Items carry their own `provenance.license` field, and at v1.0 all 402 are
MIT. The field exists because corpus-derived items would inherit their corpus license
(the Bangor Miami corpus, for instance, is read as CC BY-NC-SA 3.0); filter on it rather
than assuming.

## Citation

```bibtex
@dataset{hernandez2026cswbench,
  author  = {Hernandez, Emmanuel},
  title   = {csw-bench: a Matrix Language Frame benchmark for intrasentential code-switching},
  year    = {2026},
  version = {1.0.0},
  note    = {Item set SHA-256 baf85c444ea741fd812f8f09eeafe9048db617b7383025c5b353a7c66fab069c},
  url     = {https://github.com/yungmanny/csw-bench}
}
```

Theory: Myers-Scotton, C. (1993). *Duelling Languages: Grammatical Structure in
Codeswitching*. Oxford University Press.
