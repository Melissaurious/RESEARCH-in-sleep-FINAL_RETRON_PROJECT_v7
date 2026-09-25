#!/usr/bin/env bash
# embed_x2 cross-fit, run LOCALLY across both RTX 4090s.
#
# WHY LOCAL RATHER THAN AN IBEX ARRAY. The 25 cells are short (~6 min each on a 4090) and the
# model is a ~0.7M-parameter head over PRECOMPUTED frozen ESM-C embeddings, so no language
# model runs and no large GPU is needed. On Ibex they landed on GTX 1080 Ti (correct: fp32, no
# bf16 requirement) but ran ~3-4x slower, and 25 separate allocations throttled behind a %8
# concurrency cap bought nothing. Two idle local 4090s finish the whole cross-fit in ~1 hour.
#
# SINGLE INSTANCE. The first attempt at this cross-fit was launched twice about a minute
# apart, so every cell was trained by two concurrent processes writing the SAME
# oof_{arm}_f{fold}.npz and m_{arm}_f{fold}.pt. Each process could then load a checkpoint
# the other had written, which breaks the design's assertion that every cell is one
# independent training run under its own validation trajectory. Those outputs were
# quarantined, not used. The flock below makes a second launch fail loudly instead.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec 200>"$HERE/../work/.y_run_local.lock"
flock -n 200 || { echo "FATAL: another y_run_local.sh is already running" >&2; exit 1; }
echo "runner pid $$ holds the lock"
PY=/home/borg/miniconda3/envs/retron_esmc/bin/python
LOG="$HERE/../logs"; mkdir -p "$LOG"
ARMS=(U T G R P)

run_gpu () {   # $1 = gpu id, $2... = cell indices
  local gpu=$1; shift
  for i in "$@"; do
    local arm=${ARMS[$((i / 5))]} fold=$((i % 5))
    echo "[gpu$gpu] cell $i : arm $arm fold $fold"
    CUDA_VISIBLE_DEVICES=$gpu "$PY" "$HERE/y03_train_cv.py" --arm "$arm" --fold "$fold" \
        >> "$LOG/cell_${arm}_f${fold}.log" 2>&1
  done
}

EVEN=(); ODD=()
for i in $(seq 0 24); do
  if [ $((i % 2)) -eq 0 ]; then EVEN+=("$i"); else ODD+=("$i"); fi
done
run_gpu 0 "${EVEN[@]}" &
P0=$!
run_gpu 1 "${ODD[@]}" &
P1=$!
wait $P0 $P1
echo "ALL 25 CELLS DONE"
