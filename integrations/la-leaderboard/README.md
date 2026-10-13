# csw-bench on La Leaderboard

[La Leaderboard](https://huggingface.co/spaces/la-leaderboard/la-leaderboard) is the
open leaderboard for LLMs in the languages and varieties of Ibero-America (Spanish and
its varieties, Catalan, Basque, Galician), run by SomosNLP and published at ACL 2025
(https://aclanthology.org/2025.acl-long.1561). It evaluates with
[lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) through
their fork, https://github.com/somosnlp/lm-evaluation-harness (branch `main`), where a
group `laleaderboard` lists one subgroup per language and each subgroup lists ordinary
harness tasks with a per-task `num_fewshot`. Their About page says they are looking for
datasets to extend the leaderboard, especially for tasks not currently covered, and asks
contributors to reach out on the Space's Community tab.

This folder holds the harness task for csw-bench in exactly that format. **Nothing here
has been submitted.**

## What is in `csw_bench/`

A drop-in task directory for `lm_eval/tasks/csw_bench/`, matching how the Spanish tasks
in the fork are laid out (`lm_eval/tasks/spanish_bench/` is the model):

| File | Role |
|---|---|
| `csw_bench.yaml` | group `csw_bench` over the two tasks |
| `csw_bench_judgment.yaml` | 102 minimal pairs, log-likelihood comparison (BLiMP template), `acc` and `acc_norm` |
| `csw_bench_repair.yaml` | 100 minimal repairs, csw-bench's own prompt, custom `repair_score` and `repair_minimal` |
| `utils.py` | the repair scorer ported from `csw_bench.scoring`, held to the original by `tests/test_la_leaderboard_port.py` |
| `README.md` | the task README in the harness's house format |

Both tasks read the Hugging Face dataset `yungmanny/csw-bench`, configs
`grammaticality_judgment` and `repair`, split `test`. That dataset is `data/hf/` in this
repository (`uv run csw-bench export-hf` regenerates it; the card is `data/hf/README.md`).
If the dataset is published under another id, change `dataset_path` in both task files.

The lines to add to the fork's `lm_eval/tasks/laleaderboard/laleaderboard_es.yaml`, in
the same shape as its existing entries:

```yaml
  - task: csw_bench_judgment
    num_fewshot: 0
  - task: csw_bench_repair
    num_fewshot: 0
```

Zero-shot is deliberate. The set has no train split, every item is a test item, and
exemplars drawn from the same 402 items would leak gold strings into the prompt.

## The row for the Space

The Space registers each task in `tasks/tasks.csv` (columns: Task, Name, Description,
Language, Donated By, Origin, Bench, Harness, Metric, Task type, Subtask, Domain, Format,
Num labels, Paper, Test examples, Num few shots, License). The two rows csw-bench would
add, ready to paste:

```csv
[csw-bench judgment](https://huggingface.co/datasets/yungmanny/csw-bench),csw-bench judgment,Spanish/English code-switching acceptability: minimal pairs under the Matrix Language Frame model,ES,Emmanuel Hernandez (UCLA),Original,csw-bench,csw_bench_judgment,acc,Language Proficiency,Linguistic Acceptability,Miscellaneous,Multi choice QA,2,[📄](nan),102,0,MIT
[csw-bench repair](https://huggingface.co/datasets/yungmanny/csw-bench),csw-bench repair,Minimal repair of Spanish/English code-switched utterances that violate the Matrix Language Frame model,ES,Emmanuel Hernandez (UCLA),Original,csw-bench,csw_bench_repair,repair_score,Language Proficiency,Grammatical Error Correction,Miscellaneous,Open QA,0,[📄](nan),100,0,MIT
```

The Space's `src/tasks.py` reads the metric as `<Metric>,none` from the harness results,
which is what `acc` and the custom `repair_score` produce.

## How it would be submitted

1. The dataset is public on Hugging Face with the card in `data/hf/README.md`.
2. Fork `somosnlp/lm-evaluation-harness`, copy `csw_bench/` to `lm_eval/tasks/csw_bench/`,
   add the two entries above to `laleaderboard_es.yaml`.
3. Run the task once end to end on a small open model and keep the output:
   `lm_eval --model hf --model_args pretrained=Qwen/Qwen2.5-0.5B --tasks csw_bench --num_fewshot 0 --batch_size 1 --output_path out/`.
4. Open a pull request against the fork's `main` with that output in the description.
5. Open a thread on the Space's Community tab pointing at the PR and the dataset, with the
   `tasks.csv` rows above. Their maintainers decide whether a code-switching task fits
   the leaderboard's scope; US Spanish/English mixing is a Spanish variety in the broad
   sense but not one of the national varieties they list, and the About page's call for
   "complex tasks not currently covered" is the argument for including it.

## Honest differences from the csw-bench runner

The numbers these tasks produce are not the numbers in `docs/results.md`, and should not
be compared to them:

- The csw-bench runner prompts a chat model, allows 8192 output tokens, strips a leaked
  reasoning preamble, then scores. The harness judgment task never prompts at all; it
  compares sentence log-likelihoods, which is the standard acceptability protocol for
  base models and the one the leaderboard's other acceptability tasks (EsCoLA, CatCoLA)
  are closest to.
- The harness repair task stops generation at the first newline with a 64-token cap,
  because the leaderboard evaluates base models that would otherwise keep writing. The
  scorer is identical; the response it sees is not.
- The leaderboard normalizes every score as `(raw - random_baseline) / (max -
  random_baseline)` with `random_baseline = 1/n` for multiple choice and 0 for generation.
  That is the same above-chance rescaling csw-bench reports, with the same floors (0.5
  and 0), which is one reason these two tasks port cleanly and the other two do not.
