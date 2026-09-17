#!/usr/bin/env bash
# g4b — regenerate every landed product in this bundle from its scripts.
#
#   run.sh [work_dir]
#
# What it regenerates, and how reproducible each is:
#
#   tables/smoke_input.faa        DETERMINISTIC - rebuilt from the registered loader
#   tables/smoke_states.tsv       DETERMINISTIC - byte-identical on every rerun
#   tables/smoke_sequences.tsv    DETERMINISTIC
#   tables/smoke_failures.tsv     DETERMINISTIC
#   tables/smoke_provenance.tsv   DETERMINISTIC except timestamps, host, paths and the
#                                 bundle root (verify.sh compares the other keys)
#   tables/smoke_run.log          run log; timings and paths vary
#   tables/g4b_throughput_measurement.tsv
#                                 WALL-CLOCK MEASUREMENT - deliberately NOT byte-reproducible.
#                                 Re-running it rewrites the table with that run's timings.
#
# `verify.sh` is the check that matters: it reruns the deterministic products into a temp
# directory and diffs them against what is landed here, without overwriting anything.
# Use run.sh to RE-LAND after an intentional change; use verify.sh to CHECK.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python3
WORK="${1:-${TMPDIR:-/tmp}/g4b_run_$$}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$WORK/pycache"
mkdir -p "$WORK"
status=0

echo "== freeze tests =="
"$PY" -B "$HERE/scripts/test_production_freeze.py" || status=1

echo "== smoke test =="
bash "$HERE/scripts/run_smoke.sh" "$WORK/smoke" 2>&1 | tee "$WORK/smoke.log" || status=1

echo "== review-repair checks R1-R5 =="
"$PY" -B "$HERE/scripts/check_repairs.py" "$WORK/repairs" || status=1

echo "== re-landing the deterministic smoke products =="
cp "$WORK/smoke/main/smoke.states.tsv"     "$HERE/tables/smoke_states.tsv"     || status=1
cp "$WORK/smoke/main/smoke.sequences.tsv"  "$HERE/tables/smoke_sequences.tsv"  || status=1
cp "$WORK/smoke/main/smoke.failures.tsv"   "$HERE/tables/smoke_failures.tsv"   || status=1
cp "$WORK/smoke/main/smoke.provenance.tsv" "$HERE/tables/smoke_provenance.tsv" || status=1
cp "$WORK/smoke/smoke_input.faa"           "$HERE/tables/smoke_input.faa"      || status=1
cp "$WORK/smoke.log"                       "$HERE/tables/smoke_run.log"        || status=1

echo "== re-measuring throughput (wall-clock; rewrites the table) =="
"$PY" -B "$HERE/scripts/measure_throughput.py" "$WORK/tp" \
      "$HERE/tables/g4b_throughput_measurement.tsv" > "$WORK/tp.log" 2>&1 || status=1
tail -4 "$WORK/tp.log"

echo
[ $status -eq 0 ] && echo "run.sh OK" || echo "run.sh FAILED"
echo "artefacts: $WORK"
exit $status
