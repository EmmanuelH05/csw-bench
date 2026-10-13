#!/usr/bin/env bash
# Kills the run when the machine, not the model, is failing: memory pressure critical on
# consecutive checks, a model other than the current stage's loaded into Ollama, or no
# log progress for STALL_MIN minutes. It never reacts to per-item errors -- deepseek's
# ml_identification timeouts and gpt-oss's continuation budget errors are real results,
# and items are ordered by cell so they arrive in streaks of up to 31. An error-count
# rule would kill a healthy run.
#
# Usage:  nohup scripts/watchdog.sh > /dev/null 2>&1 &     (before or after run_phase4.sh)
# Log:    runs/logs/watchdog.log
# After a kill, `scripts/run_phase4.sh` resumes: finished stages skip, finished items
# come from cache.
set -uo pipefail
cd "$(dirname "$0")/.."

INTERVAL=${WATCHDOG_INTERVAL:-30}
STALL_MIN=${WATCHDOG_STALL_MIN:-20}
CRITICAL_CHECKS=${WATCHDOG_CRITICAL_CHECKS:-2}
FOREIGN_CHECKS=${WATCHDOG_FOREIGN_CHECKS:-2}
LOG=runs/logs/watchdog.log
mkdir -p runs/logs

say() { echo "$(date '+%F %T') $*" >> "$LOG"; }

newest_stage_log() { ls -t runs/logs/pilot-*.log runs/logs/full-*.log 2>/dev/null | head -1; }

# pilot-qwen3-30b-b.log -> qwen3:30b ; full-deepseek-r1-32b-a.log -> deepseek-r1:32b
expected_model() {
  local stem
  stem=$(basename "$1" .log)
  stem=${stem#pilot-}; stem=${stem#full-}; stem=${stem%-a}; stem=${stem%-b}
  printf '%s:%s' "${stem%-*}" "${stem##*-}"
}

loaded_models() { ollama ps 2>/dev/null | awk 'NR > 1 {print $1}'; }

kill_run() {
  say "KILL: $1"
  pkill -f scripts/run_phase4.sh
  # The uv wrapper and the venv entry point, never a bare "csw-bench": an editor opened
  # on this folder carries the path in its command line and would match too.
  pkill -f "uv run csw-bench"
  pkill -f "bin/csw-bench"
  local m
  for m in $(loaded_models); do ollama stop "$m"; done
  say "run stopped, models unloaded; rerun scripts/run_phase4.sh to resume"
  exit 1
}

critical=0
foreign=0
started=$(date +%s)
say "up: interval ${INTERVAL}s, stall ${STALL_MIN}m, kill after ${CRITICAL_CHECKS} critical / ${FOREIGN_CHECKS} foreign-model checks"
while true; do
  if ! pgrep -f scripts/run_phase4.sh > /dev/null; then
    say "run_phase4.sh is not running; exiting"
    exit 0
  fi

  level=$(sysctl -n kern.memorystatus_vm_pressure_level)
  free=$(sysctl -n kern.memorystatus_level)
  if (( level >= 4 )); then
    critical=$((critical + 1))
    say "memory CRITICAL, free ${free}%, check ${critical}/${CRITICAL_CHECKS}"
    (( critical >= CRITICAL_CHECKS )) && kill_run "memory pressure critical on ${critical} consecutive checks"
  else
    (( level >= 2 )) && say "memory warning, free ${free}%"
    critical=0
  fi

  stage_log=$(newest_stage_log)
  if [[ -n "$stage_log" ]]; then
    expected=$(expected_model "$stage_log")
    unexpected=""
    for m in $(loaded_models); do
      [[ "$m" != "$expected" ]] && unexpected="$m"
    done
    if [[ -n "$unexpected" ]]; then
      foreign=$((foreign + 1))
      say "foreign model loaded: $unexpected (stage expects $expected), check ${foreign}/${FOREIGN_CHECKS}"
      (( foreign >= FOREIGN_CHECKS )) && kill_run "another model ($unexpected) is competing with $expected for memory"
    else
      foreign=0
    fi

    # A stage log left by an earlier attempt predates this watchdog; a stall is measured
    # from whichever is later, or a resumed run is killed during its own preflight.
    last=$(stat -f %m "$stage_log")
    (( last < started )) && last=$started
    age=$(( $(date +%s) - last ))
    (( age > STALL_MIN * 60 )) && kill_run "no progress in $(basename "$stage_log") for $((age / 60)) minutes"
  fi

  sleep "$INTERVAL"
done
