#!/usr/bin/env bash
# Launch a task session.   Usage:  bash programme/launch_task.sh <task-id> [--dry-run]
#
# Handles the one thing that is per-WORKTREE (submodule init) and the several that are
# per-SESSION (conda, env vars, pointing the session at its launcher).
set -uo pipefail

TASK="${1:?usage: launch_task.sh <task-id> [--dry-run]}"
DRY="${2:-}"

SYN="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis"
PROGRAMME="${SYN}/programme"
REVIEW="${SYN}/review-stage"
WT="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-${TASK}"
LAUNCHER="${PROGRAMME}/tasks/${TASK}/TASK_LAUNCHER.md"

[[ -d "$WT" ]]       || { echo "no worktree: $WT"; exit 1; }
[[ -f "$LAUNCHER" ]] || { echo "no launcher: $LAUNCHER"; exit 1; }

# The board is the authority on what may run.
STATE=$(awk -F'\t' -v t="$TASK" 'NR>1 && $1==t {print $4}' "${PROGRAMME}/TASK_BOARD.tsv")
if [[ "$STATE" != "AUTHORIZED" ]]; then
  echo "REFUSED: ${TASK} is '${STATE:-not on the board}', not AUTHORIZED."
  exit 1
fi

cd "$WT" || exit 1

# ---- per WORKTREE, once ----
if [[ -z "$(ls -A general 2>/dev/null)" ]]; then
  echo "[setup] general/ empty in this worktree; initialising submodule (needs network)"
  git submodule update --init --recursive || echo "[warn] submodule init failed; governance layer unavailable"
fi

# ---- per SESSION ----
if CONDA_BASE=$(conda info --base 2>/dev/null); then
  # shellcheck disable=SC1091
  source "${CONDA_BASE}/etc/profile.d/conda.sh" && conda activate retron_tradicional
else
  echo "[warn] conda not found; retron_tradicional NOT activated"
fi
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
export RETRON_PROGRAMME="$PROGRAMME"
export RETRON_TASK="$TASK"
export RETRON_LAUNCHER="$LAUNCHER"

cat <<BANNER

================ TASK SESSION | ${TASK} ================
worktree : ${WT}
branch   : $(git rev-parse --abbrev-ref HEAD 2>/dev/null)
env      : ${CONDA_DEFAULT_ENV:-<none>}    python: $(command -v python3)

READ THESE THREE, IN ORDER, BEFORE ANYTHING ELSE:
  1. ${LAUNCHER}
  2. ${PROGRAMME}/WORKING_RULES.md
  3. ${REVIEW}/TASK_PROTOCOL.md
(They are NOT in this worktree. Read them at those absolute paths.)

RULES OF ENGAGEMENT
  - Execute exactly this one task. A second question is a NOMINATION, not work.
  - Controls run FIRST and BLOCK. No primary analysis until every control is PASS.
  - Write only inside this worktree, and only under the launcher's output_directory.
  - Never modify a frozen bundle. Never use bare 'git stash' (the stack is shared).
  - Every number written into prose must resolve to a table cell you produced.
  - Prior work supplies ASSETS and BOUNDED NEGATIVES. Its numbers are UNVERIFIED.
  - Report in the contract at WORKING_RULES.md section 5. Facts only, no interpretation.
  - On budget exhaustion, a failed control, or an unreachable PASS: ESCALATE, do not iterate.
========================================================

BANNER

if [[ "$DRY" == "--dry-run" ]]; then
  echo "[dry-run] environment prepared; not launching a session"
  exit 0
fi

exec claude --dangerously-skip-permissions
