#!/usr/bin/env bash
# g5 — apply the frozen mapper to the censused eligible Stage-1 exact-RT catalogue.
#
#   run.sh [scratch_dir] [parallelism]
#
# Four steps, each fail-closed, in this order:
#   A  shard.py      512 deterministic FASTA shards over the CENSUSED ELIGIBLE population
#   B  run_all.sh    the frozen production runner, one shard at a time, resumable
#   C  merge.py      verify every shard, reconcile against the census, write the dataset
#   D  qc.py         descriptive application QC and the g6-readiness summary
#
# preflight.py must pass first: it stops the run if the instrument differs in any field
# from the canonical g4b instrument rtmap-1.0.0/53a1e738a19b3896.
#
# Scratch holds ~12 GB of per-shard TSV. It is deleted only after merge.py has verified
# every shard's DONE sidecar against the outputs on disk - never before.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python3
SCRATCH="${1:-$ROOT/ARIS_OUTPUT/rt07_g5}"
PAR="${2:-44}"
DATASET="$ROOT/data/derived/rt07_g5"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$SCRATCH"/{shards,out,work} "$DATASET" "$HERE/tables"

echo "== preflight: instrument + production smoke test =="
"$PY" -B -u "$HERE/scripts/preflight.py" "$SCRATCH/work" "$SCRATCH/shards" || {
    echo "STOP: preflight failed - the instrument or the production path is not canonical"
    exit 1; }

echo "== A: shard the censused eligible population =="
"$PY" -B -u "$HERE/scripts/shard.py" "$SCRATCH/shards" 512 || exit 1

echo "== B: apply the frozen mapper =="
bash "$HERE/scripts/run_all.sh" "$SCRATCH/shards" "$SCRATCH/out" "$SCRATCH/work" "$PAR" || exit 1

echo "== C: verify every shard and merge =="
"$PY" -B -u "$HERE/scripts/merge.py" "$SCRATCH/out" "$SCRATCH/shards" "$DATASET" \
      "$HERE/tables" || exit 1

echo "== D: application QC and g6 readiness =="
"$PY" -B -u "$HERE/scripts/qc.py" "$DATASET" "$HERE/tables" || exit 1

echo "g5 run complete. Scratch retained at $SCRATCH (delete only after review)."
