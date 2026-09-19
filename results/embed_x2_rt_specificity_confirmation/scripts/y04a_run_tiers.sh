#!/usr/bin/env bash
# Run the four counterfactual tiers as independent processes.
#
# The tiers share no state: each reseeds its own rng at SEED and writes its own
# cf_selection_{tier}.npz, which y04a_merge.py combines. Splitting is a scheduling change
# only -- it does not alter the selection.
#
# Thread caps matter here. The unsplit version let BLAS grab every core for tiny per-pair
# matrices and spent 14.5 CPU-hours without finishing C3.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PY=/home/borg/miniconda3/envs/retron_esmc/bin/python
LOG="$HERE/../logs"; mkdir -p "$LOG"
for t in C1 C2 C3 C4; do
  CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3 MKL_NUM_THREADS=3 \
    nohup "$PY" -u "$HERE/y04a_tier_sizing.py" --tier "$t" > "$LOG/tier_$t.log" 2>&1 &
  echo "launched $t pid $!"
done
wait
