#!/usr/bin/env bash
# T-P1b · Ibex staging + submission for the FULL 501,561-sequence run.
#
# ⛔ NOT SUBMITTED.  This script exists so the full run can start the minute the
#    operator authorises it, and NOT before.  It refuses to do anything without
#    an explicit --i-have-operator-authorisation flag.
#
#   bash p1b_ibex_fullrun.sh --dry-run                      # prints the plan, touches nothing
#   bash p1b_ibex_fullrun.sh --stage                        # copies inputs to Ibex, no job
#   bash p1b_ibex_fullrun.sh --submit --i-have-operator-authorisation
#
# The pilot is NOT a substitute for that authorisation.  TASK_LAUNCHER.md section 11:
# "the 501,561-sequence run does NOT follow automatically from a passing pilot."
set -uo pipefail

# --- Ibex access.  general/site/IBEX.md forbids the vscode pool for scripted
# --- access, and the bare alias `ibex` resolves INTO it on this host
# --- (ssh ibex -> vsc509-03-l).  The full hostname is therefore always explicit.
IBEX_HOST="rioszemm@ilogin.ibex.kaust.edu.sa"
IBEX_ENV="/ibex/user/rioszemm/conda-environments/retron_tradicional"
IBEX_ROOT="/ibex/user/rioszemm/t_p1b_identity_partition"

FREEZE_COMMIT="1a6909f"
V7="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
WT="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-P1b-identity-partition"
FAA="${V7}/data/derived/rt_exact_v1.faa"
FAA_SHA256="bcde6e9a64de90e6e791256f79c87799a00a95f0d1730f3460301220379e2655"

# Requested resources.  CPU_HIGH per the launcher.  batch showed 7 idle nodes at
# design time, so expect to queue; the walltime is generous rather than tight
# because a job that dies at the limit wastes the whole allocation.
CPUS=32
MEM="120G"
TIME="12:00:00"
PARTITION="batch"

MODE=""
AUTH="no"
for arg in "$@"; do
  case "$arg" in
    --dry-run) MODE="dry" ;;
    --stage)   MODE="stage" ;;
    --submit)  MODE="submit" ;;
    --i-have-operator-authorisation) AUTH="yes" ;;
    *) echo "unknown argument: $arg"; exit 1 ;;
  esac
done
[[ -n "$MODE" ]] || { echo "REFUSED: one of --dry-run | --stage | --submit is required"; exit 1; }

# ---------------------------------------------------------------- local gates
echo "=== local preflight ==="
[[ -f "$FAA" ]] || { echo "REFUSED: catalogue missing: $FAA"; exit 1; }
got="$(sha256sum "$FAA" | cut -d' ' -f1)"
[[ "$got" == "$FAA_SHA256" ]] || { echo "REFUSED: catalogue sha256 $got != $FAA_SHA256"; exit 1; }
echo "  catalogue sha256 OK"
n="$(grep -c '^>' "$FAA")"
[[ "$n" == "501561" ]] || { echo "REFUSED: catalogue has $n records, expected 501561"; exit 1; }
echo "  catalogue records OK: $n"
head="$(git -C "$WT" rev-parse --short HEAD 2>/dev/null)"
git -C "$WT" merge-base --is-ancestor "$FREEZE_COMMIT" HEAD 2>/dev/null \
  || { echo "REFUSED: worktree HEAD $head does not descend from freeze $FREEZE_COMMIT"; exit 1; }
echo "  worktree $head descends from freeze $FREEZE_COMMIT"
[[ -z "$(git -C "$WT" status --porcelain)" ]] \
  || { echo "REFUSED: task worktree is dirty; the run must record a clean tree"; exit 1; }
echo "  task worktree clean"

STAGE_BYTES="$(stat -c%s "$FAA")"
echo
echo "=== plan ==="
cat <<PLAN
  host        : ${IBEX_HOST}
  remote root : ${IBEX_ROOT}
  env         : ${IBEX_ENV}
  partition   : ${PARTITION}   cpus=${CPUS}  mem=${MEM}  time=${TIME}
  stage       : rt_exact_v1.faa  ($(numfmt --to=iec "$STAGE_BYTES"))
                + p1b_identity_partition.py, p1b_fixtures.py
  ⚠️ staging is LOCAL I/O on the shared NVMe and counts against the IO budget
  ⚠️ controls run FIRST on Ibex and BLOCK; a control failure means no primary table
PLAN

if [[ "$MODE" == "dry" ]]; then
  echo
  echo "DRY RUN — nothing was staged and nothing was submitted."
  exit 0
fi

if [[ "$AUTH" != "yes" && "$MODE" == "submit" ]]; then
  echo
  echo "⛔ REFUSED: --submit requires --i-have-operator-authorisation."
  echo "   The passing pilot is NOT that authorisation. See TASK_LAUNCHER.md section 11."
  exit 1
fi

# ------------------------------------------------------------------- staging
echo
echo "=== staging to Ibex ==="
ssh -o BatchMode=yes "$IBEX_HOST" "mkdir -p ${IBEX_ROOT}/{in,out,logs}" || exit 1
rsync -avP "$FAA" "${IBEX_HOST}:${IBEX_ROOT}/in/" || exit 1
rsync -avP "${WT}/programme/tasks/T-P1b-identity-partition/p1b_identity_partition.py" \
           "${WT}/programme/tasks/T-P1b-identity-partition/p1b_fixtures.py" \
           "${IBEX_HOST}:${IBEX_ROOT}/in/" || exit 1
echo "  verifying the staged catalogue by hash, not by byte count"
remote="$(ssh -o BatchMode=yes "$IBEX_HOST" "sha256sum ${IBEX_ROOT}/in/rt_exact_v1.faa | cut -d' ' -f1")"
[[ "$remote" == "$FAA_SHA256" ]] || { echo "REFUSED: staged copy hash $remote != $FAA_SHA256"; exit 1; }
echo "  staged catalogue sha256 OK"

[[ "$MODE" == "stage" ]] && { echo; echo "STAGED. No job submitted."; exit 0; }

# ---------------------------------------------------------------- submission
cat > /tmp/p1b_full.sbatch <<SBATCH
#!/bin/bash
#SBATCH --job-name=t_p1b_full
#SBATCH --partition=${PARTITION}
#SBATCH --cpus-per-task=${CPUS}
#SBATCH --mem=${MEM}
#SBATCH --time=${TIME}
#SBATCH --output=${IBEX_ROOT}/logs/%j.out
#SBATCH --error=${IBEX_ROOT}/logs/%j.err
set -euo pipefail
source "\$(conda info --base)/etc/profile.d/conda.sh"
conda activate ${IBEX_ENV}
[[ "\${CONDA_DEFAULT_ENV:-}" == *retron_tradicional* ]] || { echo "REFUSED: wrong env"; exit 1; }
cd ${IBEX_ROOT}
python in/p1b_fixtures.py --out out/fixtures
python in/p1b_identity_partition.py --mode full --out out --fixtures out/fixtures --threads ${CPUS}
SBATCH
rsync -q /tmp/p1b_full.sbatch "${IBEX_HOST}:${IBEX_ROOT}/in/p1b_full.sbatch"

echo
echo "=== submitting ==="
JOB="$(ssh -o BatchMode=yes "$IBEX_HOST" "cd ${IBEX_ROOT} && sbatch --parsable in/p1b_full.sbatch")"
echo "  SLURM job: ${JOB}"
echo "  poll: ssh ${IBEX_HOST} 'squeue --me'"
echo "  ⚠️ record ${JOB} in programme/LIVE_EXECUTION.tsv against freeze ${FREEZE_COMMIT}"
