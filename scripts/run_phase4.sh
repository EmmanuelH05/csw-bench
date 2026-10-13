#!/usr/bin/env bash
# Phase 3's last open gate (template b against the pilot set) and the Phase 4 full-set
# runs, in one resumable sequence. A stage is skipped when its run.json exists, so a
# rerun after an interruption redoes only the unfinished stage -- and inside that stage
# the response cache serves every item that already completed. Errored items are never
# cached and are retried; for deepseek-r1:32b that is the ml_identification timeout
# pattern (docs/findings.md), ~100 items at 300 s each on the full set.
#
# Operator notes, all learned from the pilot (docs/journal.md, 2026-08-24 and -27):
#   * One model at a time. qwen3:30b and deepseek-r1:32b are 18-19 GB on a 24 GB
#     machine; a second model request evicts the loaded one and every in-flight item
#     times out. No second Ollama request, no LM Studio model, while this runs.
#   * The video-pipeline launch agent (com.mannie.videogen) restarts ComfyUI (18 GB)
#     every 60 s on AC power. Unload it before starting and reload it after:
#       launchctl bootout gui/$(id -u)/com.mannie.videogen
#       launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.mannie.videogen.plist
#     The 2026-09-09 runs did not, and the collision crashed the Ollama runner eight
#     times (docs/journal.md).
#   * caffeinate -i keeps the machine awake. A sleep mid-run looks exactly like a hang.
#   * Wall-clock at pilot-observed rates: qwen3 5-7 h, gpt-oss ~4 h, deepseek ~13 h
#     (8+ h of it the ml_identification timeouts). Budget a day and a half.
#   * Progress: tail -f runs/logs/<stage>.log  -- one timestamped line per item.
#
# Usage:  mkdir -p runs/logs
#         nohup scripts/run_phase4.sh > runs/logs/run_phase4.out 2>&1 &
#         nohup scripts/watchdog.sh > /dev/null 2>&1 &      # kills the run if the machine fails
set -euo pipefail
cd "$(dirname "$0")/.."

MODELS=("qwen3:30b" "gpt-oss:20b" "deepseek-r1:32b")
COMMON=(--provider ollama --seed 42 --minimality-threshold 0.7 --retention zero --max-tokens 8192)
mkdir -p runs/logs

safe() { printf '%s' "$1" | tr ':' '-'; }

stage() {
  local out="$1"; shift
  if [[ -f "$out/run.json" ]]; then
    echo "skip $out: run.json exists"
    return
  fi
  echo "=== $(date '+%F %T') start $out"
  # Unload whatever the previous stage left resident so the next model never has to
  # evict it mid-request, and so the watchdog can treat any other loaded model as foreign.
  local m
  for m in $(ollama ps | awk 'NR > 1 {print $1}'); do ollama stop "$m"; done
  caffeinate -i uv run csw-bench "$@" --out "$out" 2>&1 | tee -a "runs/logs/$(basename "$out").log"
  echo "=== $(date '+%F %T') done $out"
}

preflight() {
  curl -sf http://localhost:11434/api/tags > /dev/null \
    || { echo "ollama is not answering on localhost:11434" >&2; exit 1; }
  local pulled
  pulled=$(ollama list | awk 'NR > 1 {print $1}')
  for m in "${MODELS[@]}"; do
    grep -qx "$m" <<< "$pulled" || { echo "model $m is not pulled" >&2; exit 1; }
  done
  if [[ $(ollama ps | wc -l) -gt 1 ]]; then
    echo "warning: a model is already loaded; a competing request will time items out:" >&2
    ollama ps >&2
  fi
  if pgrep -f "main.py --listen" > /dev/null; then
    echo "ComfyUI is running; it will crash the Ollama runner. Unload com.mannie.videogen first." >&2
    exit 1
  fi
  uv run csw-bench validate > /dev/null
  uv run csw-bench --items-root data/items-pilot validate > /dev/null
}

preflight

# Phase 3, prompt sensitivity: template b on the pilot set, same model as the cleanest
# template-a pilot (qwen3:30b, 0 provider errors), compared item-paired against it.
stage runs/pilot-qwen3-30b-b --items-root data/items-pilot run --model qwen3:30b --template b "${COMMON[@]}"
uv run csw-bench report runs/pilot-qwen3-30b-b --compare runs/pilot-qwen3-30b-a \
  | tee runs/logs/prompt-sensitivity.txt

# Phase 4: the full 402-item set, three model lineages, template a.
for m in "${MODELS[@]}"; do
  stage "runs/full-$(safe "$m")-a" run --model "$m" --template a "${COMMON[@]}"
done

FULL=()
for m in "${MODELS[@]}"; do FULL+=("runs/full-$(safe "$m")-a"); done
uv run python scripts/continuation_escape_hatch.py "${FULL[@]}" | tee runs/logs/escape-hatch.txt

# Writes docs/results.md and the README headline block, and prints every remaining
# number the PENDING RUNS sections need. Nothing below this line transcribes a figure.
uv run python scripts/finalize_phase4.py "${FULL[@]}" | tee runs/logs/finalize.txt

cat <<'DONE'

All runs complete. docs/results.md and the README headline table are written. What is
left is prose and bookkeeping -- every number it needs is in runs/logs/finalize.txt,
runs/logs/prompt-sensitivity.txt, and runs/logs/escape-hatch.txt. The qwen3:30b and
gpt-oss:20b halves were written 2026-09-10; only deepseek-r1:32b is open:

  1. docs/findings.md: replace each "deepseek-r1:32b: PENDING RUNS" marker with that
     model's lines from finalize.txt's 'Headline result' and 'Error patterns by
     violation type' blocks, and its escape-hatch counts.
  2. docs/limitations.md: the PENDING RUNS section -- deepseek's provider-error rate and
     violation-production rate; update the 0-of-158 evidence-citation count if it moved.
  3. README.md: drop "results pending one model" from the status banner; recheck
     caveat 1's evidence-citation count against finalize.txt.
  4. docs/journal.md: the Phase 4 results entry for the third run.
  5. docs/charter.md: check the two Phase 4 boxes; update the Phase 5 README/findings/
     limitations annotations.
  6. uv run ruff check . && uv run ruff format --check . && uv run mypy src scripts && uv run pytest
  7. git add runs/full-deepseek-r1-32b-a docs README.md docs/charter.md && git commit
     (item count 402 and the disagreement rate in the message)
  8. Set the v1.0 date in docs/versions.md, then:
     git tag -a v1.0 -m "csw-bench v1.0, item set baf85c44"
  9. Reload the video pipeline's launch agent (command in the header).
DONE
