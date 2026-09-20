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

# ---- PREFLIGHT GATE ----
# The full gate lives in programme/preflight.py: board state, governance base currency,
# worktree existence and ancestry from the declared base, output directory, unresolved
# criteria, and hard-dependency satisfaction. It refuses on any failure.
echo "[preflight] ${TASK}"
python3 "${PROGRAMME}/preflight.py" "$TASK" || { echo "REFUSED: preflight could not run"; exit 1; }
if ! python3 - "$TASK" <<'PYGATE'
import sys, pathlib
sys.path.insert(0, "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis/programme")
import preflight
sys.exit(0 if preflight.preflight(sys.argv[1]).launchable else 1)
PYGATE
then
  echo
  echo "REFUSED: ${TASK} did not pass preflight. Nothing was launched."
  exit 1
fi
echo "[preflight] LAUNCHABLE"
echo

cd "$WT" || exit 1

# ---- per WORKTREE, once: the governance layer. FAILS CLOSED. ----
# Batch One ran with general/ empty in every task worktree, because this block warned and
# continued. A governance layer that is optional is not a governance layer. It now blocks.
if [[ -z "$(ls -A general 2>/dev/null)" ]]; then
  echo "[setup] general/ is empty; initialising the governance submodule"
  # Prefer objects already in the repository. The submodule is a GitHub HTTPS remote, and a
  # sandboxed session behind a filtering proxy can fail the fetch; that is the most likely
  # way this worktree ended up empty. Only reach the network if the local path fails.
  git submodule update --init --recursive --no-fetch 2>/dev/null \
    || git submodule update --init --recursive \
    || { echo "REFUSED: governance submodule could not be initialised. Not launching."; exit 1; }
fi

# Assert the governed PIN, not merely a populated directory. Until this existed the comment
# here claimed a pin check the code did not perform: it only tested that files were non-empty,
# so any revision of general/ would have satisfied it.
# Pin of record: docs/decisions/2026-09-15_general_pin_cff9831.md
GENERAL_PIN="cff983144e2ad6fc01f648982fb61810dd77ddbe"
recorded="$(git ls-tree HEAD general 2>/dev/null | awk '{print $3}')"
checked_out="$(git -C general rev-parse HEAD 2>/dev/null)"
[[ "$recorded" == "$GENERAL_PIN" ]] || {
  echo "REFUSED: general/ is RECORDED at ${recorded:-<none>}, governed pin is ${GENERAL_PIN}."
  echo "         Moving the pin is a deliberate commit with a decision record, never drift."
  exit 1; }
[[ "$checked_out" == "$GENERAL_PIN" ]] || {
  echo "REFUSED: general/ is CHECKED OUT at ${checked_out:-<none>}, governed pin is ${GENERAL_PIN}."
  exit 1; }

# Then assert the specific assets the programme depends on are present and non-empty.
for asset in general/site/IBEX.md general/tools/status.sh general/checks/specs_exist.sh; do
  [[ -s "$asset" ]] || { echo "REFUSED: missing governance asset ${asset}. Not launching."; exit 1; }
done

# CLAUDE.md requires this before provenance-bearing execution. It was written into the rules
# and never executed. It is executed here, and it blocks.
if ! bash general/checks/specs_exist.sh >/dev/null 2>&1; then
  echo "REFUSED: general/checks/specs_exist.sh did not pass. Not launching."
  exit 1
fi

# ---- per SESSION. ALSO FAILS CLOSED. ----
# CLAUDE.md: "Do not use base." Warning and proceeding would run the task in the wrong
# environment, which is the same fail-open shape as the block above.
if ! CONDA_BASE=$(conda info --base 2>/dev/null); then
  echo "REFUSED: conda not found; cannot activate retron_tradicional. Not launching."; exit 1
fi
# shellcheck disable=SC1091
source "${CONDA_BASE}/etc/profile.d/conda.sh"
# `set -u` must be lifted across conda activation and no further. The env's own
# activate.d hooks are not written for nounset -- retron_tradicional ships
# openjdk_activate.sh, which reads JAVA_HOME before setting it and aborts the
# whole launcher under -u. That made every task refuse at the last step, after
# preflight and the governance check had both passed, which is the most expensive
# place to fail. Restored immediately after, so the rest of the script keeps it.
set +u
conda activate retron_tradicional \
  || { set -u; echo "REFUSED: could not activate retron_tradicional. Not launching."; exit 1; }
set -u
[[ "${CONDA_DEFAULT_ENV:-}" == "retron_tradicional" ]] \
  || { echo "REFUSED: active env is '${CONDA_DEFAULT_ENV:-none}', not retron_tradicional."; exit 1; }
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
