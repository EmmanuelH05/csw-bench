# csw-bench

### Paper

csw-bench is a Matrix Language Frame benchmark for Spanish/English intrasentential
code-switching: 402 constructed items, three violation types (T1 System Morpheme
Principle, T3 EL Island Trigger Hypothesis, T5 Blocking Hypothesis, all Myers-Scotton
1993), four task types. The code repository carries the design, taxonomy, scoring rubric
and limitations: https://github.com/yungmanny/csw-bench. No paper yet.

Homepage: https://huggingface.co/datasets/yungmanny/csw-bench

### Citation

```
@dataset{hernandez2026cswbench,
    author = {Hernandez, Emmanuel},
    title = {csw-bench: a Matrix Language Frame benchmark for intrasentential code-switching},
    year = {2026},
    version = {1.0.0},
    note = {Item set SHA-256 baf85c444ea741fd812f8f09eeafe9048db617b7383025c5b353a7c66fab069c},
    url = {https://github.com/yungmanny/csw-bench}
}
```

### Groups and Tasks

#### Groups

- `csw_bench`: both tasks below.

#### Tasks

- `csw_bench_judgment`: 102 minimal pairs. The licensed and violating member differ only
  in one MLF violation; the model's log-likelihood of each is compared, BLiMP style, with
  no prompt. Metrics `acc` and `acc_norm`, floor 0.5. Two of the three violation types
  (T5 in particular) build the violating member by deleting Spanish inflection, which
  makes it shorter; `acc_norm` is the length-normalized reading.
- `csw_bench_repair`: 100 violating utterances. The model is asked, in csw-bench's own
  prompt template, to fix the one error with the smallest change. `repair_score` is the
  csw-bench rubric (0, 1 or 2 points over 2: reached the gold or an alternate repair, and
  did it minimally); `repair_minimal` is the share of full-credit repairs. Floor 0.

The other two csw-bench tasks are deliberately not included. `ml_identification` is
scored by substring match against recorded evidence strings, which credited none of the
responses in the committed runs; `constrained_continuation` is scored as exact-string
coincidence and its 100 items render to 24 distinct prompts. Both are documented as v1.0
scorer limitations in the repository and are not fit for a leaderboard column.

### Checklist

For adding novel benchmarks/datasets to the library:
* [x] Is the task an existing benchmark in the literature?
  * [ ] Have you referenced the original paper that introduced the task?
  * [x] If yes, does the original paper provide a reference implementation? The
        repository's `csw_bench.scoring` is the reference; `utils.py` here is a tested
        port of its repair scorer, and the judgment task follows the BLiMP template.

If other tasks on this dataset are already supported:
* [x] Is the "Main" variant of this task clearly denoted?
* [x] Have you provided a short sentence in a README on what each new variant adds?
* [x] Have you noted which, if any, published evaluation setups are matched by this
      variant? Neither task reproduces the csw-bench runner's numbers: the runner uses
      chat prompting with an 8192-token budget and scores the extracted answer, while
      these tasks use log-likelihood (judgment) and a one-line generation (repair).
