#!/usr/bin/env bash
# Launch or execute one task.
#
# Backward-compatible interactive mode:
#   bash programme/launch_task.sh <task-id>
#   bash programme/launch_task.sh <task-id> --interactive
#
# Deterministic frozen execution (NO Claude):
#   bash programme/launch_task.sh <task-id> --execute --execution-spec <path>
#
# Environment/bootstrap dry run:
#   bash programme/launch_task.sh <task-id> --dry-run
set -uo pipefail

TASK="${1:?usage: launch_task.sh <task-id> [--interactive|--execute|--dry-run] [--execution-spec PATH]}"
shift
MODE="interactive"
SPEC=""
while (($#)); do
  case "$1" in
    --interactive) MODE="interactive"; shift ;;
    --execute) MODE="execute"; shift ;;
    --dry-run) MODE="dry-run"; shift ;;
    --execution-spec)
      [[ $# -ge 2 ]] || { echo "REFUSED: --execution-spec needs a path"; exit 2; }
      SPEC="$2"; shift 2 ;;
    *) echo "REFUSED: unknown argument $1"; exit 2 ;;
  esac
done

SYN="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis"
PROGRAMME="${SYN}/programme"
REVIEW="${SYN}/review-stage"
WT="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-${TASK}"
SYN_LAUNCHER="${PROGRAMME}/tasks/${TASK}/TASK_LAUNCHER.md"
WT_LAUNCHER="${WT}/programme/tasks/${TASK}/TASK_LAUNCHER.md"

[[ -d "$WT" ]] || { echo "no worktree: $WT"; exit 1; }

# Frozen execution MUST bind to the launcher inside the frozen task worktree.
# Interactive coordination retains the synthesis launcher as the live specification view.
if [[ "$MODE" == "execute" ]]; then
  LAUNCHER="$WT_LAUNCHER"
else
  LAUNCHER="$SYN_LAUNCHER"
fi
[[ -f "$LAUNCHER" ]] || { echo "no launcher for mode=$MODE: $LAUNCHER"; exit 1; }

# ---- PREFLIGHT GATE ----
echo "[preflight] ${TASK} mode=${MODE}"
if [[ "$MODE" == "execute" ]]; then
  python3 "${PROGRAMME}/preflight.py" --execute "$TASK" || { echo "REFUSED: execution preflight failed"; exit 1; }
else
  python3 "${PROGRAMME}/preflight.py" "$TASK" || { echo "REFUSED: preflight failed"; exit 1; }
fi
echo "[preflight] LAUNCHABLE"
echo

cd "$WT" || exit 1

# ---- per WORKTREE, once: governance layer. FAILS CLOSED. ----
if [[ -z "$(ls -A general 2>/dev/null)" ]]; then
  echo "[setup] general/ is empty; initialising the governance submodule"
  git submodule update --init --recursive --no-fetch 2>/dev/null \
    || git submodule update --init --recursive \
    || { echo "REFUSED: governance submodule could not be initialised. Not launching."; exit 1; }
fi
GENERAL_PIN="cff983144e2ad6fc01f648982fb61810dd77ddbe"
recorded="$(git ls-tree HEAD general 2>/dev/null | awk '{print $3}')"
checked_out="$(git -C general rev-parse HEAD 2>/dev/null)"
[[ "$recorded" == "$GENERAL_PIN" ]] || {
  echo "REFUSED: general/ is RECORDED at ${recorded:-<none>}, governed pin is ${GENERAL_PIN}."; exit 1; }
[[ "$checked_out" == "$GENERAL_PIN" ]] || {
  echo "REFUSED: general/ is CHECKED OUT at ${checked_out:-<none>}, governed pin is ${GENERAL_PIN}."; exit 1; }
for asset in general/site/IBEX.md general/tools/status.sh general/checks/specs_exist.sh; do
  [[ -s "$asset" ]] || { echo "REFUSED: missing governance asset ${asset}. Not launching."; exit 1; }
done
if ! bash general/checks/specs_exist.sh >/dev/null 2>&1; then
  echo "REFUSED: general/checks/specs_exist.sh did not pass. Not launching."
  exit 1
fi

# ---- per SESSION environment. FAILS CLOSED. ----
if ! CONDA_BASE=$(conda info --base 2>/dev/null); then
  echo "REFUSED: conda not found; cannot activate retron_tradicional. Not launching."; exit 1
fi
# shellcheck disable=SC1091
source "${CONDA_BASE}/etc/profile.d/conda.sh"
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

================ TASK | ${TASK} ================
mode     : ${MODE}
worktree : ${WT}
branch   : $(git rev-parse --abbrev-ref HEAD 2>/dev/null)
launcher : ${LAUNCHER}
env      : ${CONDA_DEFAULT_ENV:-<none>}    python: $(command -v python3)

RULES
  - exactly one task; a second question is a nomination;
  - controls block; no criterion changes after freeze;
  - writes stay under the declared output_directory;
  - never modify a frozen bundle;
  - every prose number resolves to a landed table cell;
  - on control failure/budget exhaustion/unreachable PASS: STOP, do not iterate.
=================================================

BANNER

case "$MODE" in
  dry-run)
    echo "[dry-run] environment prepared; nothing executed"
    exit 0
    ;;
  interactive)
    # Preserves the existing human/task-session behaviour.
    exec claude --dangerously-skip-permissions
    ;;
  execute)
    # D4 FIX: frozen execution never invokes Claude.
    if [[ -z "$SPEC" ]]; then
      SPEC="${PROGRAMME}/executions/${TASK}/TASK_EXECUTION.json"
    fi
    [[ -f "$SPEC" ]] || { echo "REFUSED: no TASK_EXECUTION.json: $SPEC"; exit 1; }
    RUNTIME_RECORD="${RETRON_RUNTIME_RECORD:-${PROGRAMME}/executions/${TASK}/RUN_RECORD.json}"
    exec python3 "${PROGRAMME}/task_worker.py" --spec "$SPEC" --runtime-record "$RUNTIME_RECORD"
    ;;
esac
