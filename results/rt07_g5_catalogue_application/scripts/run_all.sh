#!/usr/bin/env bash
# g5 step B — apply the frozen mapper to every eligible shard.
#
#   run_all.sh <shard_dir> <out_dir> <work_dir> [parallelism]
#
# Resumable: each shard is skipped only if its DONE sidecar VERIFIES (input hash, instrument
# digest and every output hash). Interrupt and rerun at will; completed shards are not
# recomputed and partial shards are redone whole.
#
# Every shard verifies the whole production bundle against the EXTERNAL pinned root before it
# emits a single record, and records the root and status in its own provenance.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python3
RUNNER="$ROOT/results/rt07_g4b_production_mapper/code/rtmap/run_mapper.py"
PINNED="$(tr -d '[:space:]' < "$ROOT/review-stage/roots/RT07_G4B.root")"

SHARDS="$1"; OUT="$2"; WORK="$3"; PAR="${4:-44}"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$OUT" "$WORK"

echo "instrument pinned root: $PINNED"
echo "shards: $(ls "$SHARDS"/shard_*.faa | wc -l)   parallelism: $PAR"

ls "$SHARDS"/shard_*.faa | sort | xargs -P "$PAR" -I{} bash -c '
  f="{}"; n="$(basename "$f" .faa)"
  "'"$PY"'" -B "'"$RUNNER"'" --in "$f" --out "'"$OUT"'" --shard "$n" \
      --work "'"$WORK"'/$n" --pinned-root "'"$PINNED"'" --batch-size 500 \
      >> "'"$OUT"'/$n.log" 2>&1 || echo "SHARD FAILED: $n" >> "'"$OUT"'/FAILURES.txt"
  rm -rf "'"$WORK"'/$n"
'
echo "done: $(ls "$OUT"/*.DONE 2>/dev/null | wc -l) shard(s) marked DONE"
[ -s "$OUT/FAILURES.txt" ] && { echo "FAILURES:"; cat "$OUT/FAILURES.txt"; exit 1; }
exit 0
