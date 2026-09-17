#!/usr/bin/env bash
# Production smoke test. ENGINEERING ONLY - never interpreted as scientific validation.
#
#   run_smoke.sh [work_dir]
#
# Builds a small input from construction sequences the instrument has already seen, runs the
# production packaging three ways (default batching, rerun, batch-size 1), then asserts that
# the packaging reproduces the frozen mapper's landed values exactly.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
G4B="$(dirname "$HERE")"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python3
SMOKE="${1:-${TMPDIR:-/tmp}/rtmap_smoke_$$}"

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$SMOKE/pycache"
mkdir -p "$SMOKE"/{main,rerun,batch1,work}

echo "== building smoke input (construction sequences only; UG25 is never touched) =="
"$PY" -B "$HERE/make_smoke_input.py" "$SMOKE/smoke_input.faa" 3 || exit 1

echo
echo "== run 1: default batching =="
"$PY" -B "$G4B/code/rtmap/run_mapper.py" --in "$SMOKE/smoke_input.faa" \
      --out "$SMOKE/main" --shard smoke --work "$SMOKE/work/a" || exit 1

echo "== resume behaviour: a completed shard is skipped =="
"$PY" -B "$G4B/code/rtmap/run_mapper.py" --in "$SMOKE/smoke_input.faa" \
      --out "$SMOKE/main" --shard smoke --work "$SMOKE/work/a" | grep -q '^SKIP' \
  && echo "  ok    completed shard skipped without recomputing" \
  || { echo "  FAIL  completed shard was not skipped"; exit 1; }

echo "== run 2: rerun into a separate directory (determinism) =="
"$PY" -B "$G4B/code/rtmap/run_mapper.py" --in "$SMOKE/smoke_input.faa" \
      --out "$SMOKE/rerun" --shard smoke --work "$SMOKE/work/b" || exit 1

echo "== run 3: batch size 1 (batch-composition invariance) =="
"$PY" -B "$G4B/code/rtmap/run_mapper.py" --in "$SMOKE/smoke_input.faa" \
      --out "$SMOKE/batch1" --shard smoke --batch-size 1 --work "$SMOKE/work/c" || exit 1

echo
"$PY" -B "$HERE/check_smoke.py" "$SMOKE"
status=$?

echo
echo "smoke artefacts: $SMOKE"
exit $status
