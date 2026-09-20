#!/usr/bin/env bash
# T-P1b · FULL 501,561-sequence run.  PREPARED, NOT SUBMITTED.
#
#   bash p1b_fullrun.sh --dry-run
#   bash p1b_fullrun.sh --run --i-have-operator-authorisation
#
# ⛔ REFUSES to run without the explicit flag.  A passing pilot is NOT that
#    authorisation -- TASK_LAUNCHER.md section 11.
#
# ============================================================================
# ⛔ WHY THIS RUNS LOCALLY AND NOT ON IBEX, THOUGH THE LAUNCHER SAYS "ibex"
# ============================================================================
# The FROZEN implementation cannot run on Ibex as written.  p1b_identity_partition.py
# takes only --mode/--out/--fixtures/--threads and hardcodes SIX local absolute
# paths that do not exist on Ibex:
#
#     rt_exact_v1.faa · rt_ncrna_exact_pairs_v1.parquet · g3_topology_components.tsv
#     rt_family_baseline_v1.parquet · the project root · the local mmseqs binary
#
# Adding a --faa/--pairs override would EDIT A FROZEN ARTEFACT after its pilot
# validated it, which WORKING_RULES section 6b exists to prevent.  The choices are
# therefore:
#
#   (A) run the frozen implementation LOCALLY, unmodified          <-- this script
#   (B) open a NEW task id whose implementation takes path arguments, freeze it,
#       re-pilot it, and run that on Ibex
#
# (A) is preferred and is defensible on the project's own terms: WORKING_RULES
# section 4 puts CPU_HIGH on the workstation -- "48 cores and 232 GB free make most
# of this local" -- and a local run also avoids staging 220 MB across the shared
# NVMe, which section 2 of the execution plan counts against the I/O budget.
#
# The launcher's "preferred_backend: ibex (full)" is therefore superseded by this
# note, which is recorded rather than silently ignored.  It is an EXECUTION
# routing change, not a change to any criterion, threshold, control or population.
# ============================================================================
set -uo pipefail

FREEZE_COMMIT="1a6909f"
WT="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-P1b-identity-partition"
TASKDIR="${WT}/programme/tasks/T-P1b-identity-partition"
OUT="${WT}/analysis/t_p1b_identity_partition_full"
PY="/home/borg/miniconda3/envs/retron_tradicional/bin/python"
FAA="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_exact_v1.faa"
FAA_SHA256="bcde6e9a64de90e6e791256f79c87799a00a95f0d1730f3460301220379e2655"
THREADS=40

MODE=""; AUTH="no"
for a in "$@"; do
  case "$a" in
    --dry-run) MODE="dry" ;;
    --run)     MODE="run" ;;
    --i-have-operator-authorisation) AUTH="yes" ;;
    *) echo "unknown argument: $a"; exit 1 ;;
  esac
done
[[ -n "$MODE" ]] || { echo "REFUSED: --dry-run or --run required"; exit 1; }

echo "=== preflight ==="
[[ -f "$FAA" ]] || { echo "REFUSED: catalogue missing"; exit 1; }
got="$(sha256sum "$FAA" | cut -d' ' -f1)"
[[ "$got" == "$FAA_SHA256" ]] || { echo "REFUSED: catalogue sha256 $got != $FAA_SHA256"; exit 1; }
echo "  catalogue sha256 OK"
n="$(grep -c '^>' "$FAA")"
[[ "$n" == "501561" ]] || { echo "REFUSED: $n records, expected 501561"; exit 1; }
echo "  catalogue records OK: $n"
git -C "$WT" merge-base --is-ancestor "$FREEZE_COMMIT" HEAD 2>/dev/null \
  || { echo "REFUSED: worktree does not descend from freeze $FREEZE_COMMIT"; exit 1; }
echo "  worktree descends from freeze $FREEZE_COMMIT"
[[ -z "$(git -C "$WT" status --porcelain)" ]] \
  || { echo "REFUSED: task worktree dirty"; exit 1; }
echo "  task worktree clean"
[[ -e "$OUT" ]] && { echo "REFUSED: $OUT already exists; refusing to overwrite a landed run"; exit 1; }
echo "  output directory is free"
load="$(cut -d' ' -f1 /proc/loadavg)"
echo "  local load ${load} of 48 cores; requesting ${THREADS} threads"

cat <<PLAN

=== plan ===
  backend     : LOCAL workstation (see the header for why, not Ibex)
  input       : ${FAA}  (501,561 sequences, 220 MB)
  output      : ${OUT}
  threads     : ${THREADS}
  ladder      : 40 50 60 70 80 90 95 %
  controls    : run FIRST, on separate fixtures, and BLOCK

=== runtime expectation, extrapolated from the pilot and declared here ===
  The pilot did 10,000 sequences x 7 levels in 266.7 s on 24 threads.
  MMseqs2 cascaded clustering is superlinear in n, so a 50x larger input is
  expected to take MORE than 50x: order 4-12 hours on 40 threads.
  ⚠️ This is an EXTRAPOLATION, not a measurement. If it exceeds 24 h, stop it and
     escalate rather than letting it run -- an unbounded job is not a result.

=== I/O ===
  IO_MEDIUM. Nothing else in the IO_HIGH lane may run concurrently
  (T-M1b and T-S1b are the IO_HIGH tasks; keep them out of this window).
PLAN

if [[ "$MODE" == "dry" ]]; then
  echo; echo "DRY RUN — nothing executed."; exit 0
fi
if [[ "$AUTH" != "yes" ]]; then
  echo; echo "⛔ REFUSED: --run requires --i-have-operator-authorisation."
  echo "   The passing pilot is NOT that authorisation."
  exit 1
fi

echo; echo "=== executing ==="
mkdir -p "${OUT}/fixtures"
"$PY" "${TASKDIR}/p1b_fixtures.py" --out "${OUT}/fixtures" || exit 1
nohup "$PY" "${TASKDIR}/p1b_identity_partition.py" \
      --mode full --out "$OUT" --fixtures "${OUT}/fixtures" --threads "$THREADS" \
      > "${OUT}/fullrun.stdout" 2>&1 &
echo "  pid $!  -> ${OUT}/fullrun.stdout"
echo "  ⚠️ record the pid and freeze ${FREEZE_COMMIT} in programme/LIVE_EXECUTION.tsv"
