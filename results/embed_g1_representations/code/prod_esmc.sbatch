#!/bin/bash
#SBATCH --job-name=emb_esmc
#SBATCH --account=pi-hohndor
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100
#SBATCH --cpus-per-task=6
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --array=0-7%4
#SBATCH --output=/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings/logs/esmc_%A_%a.out
#SBATCH --error=/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings/logs/esmc_%A_%a.err
#
# embed_g1 PRODUCTION - ESM-C 300M over the 29,192-sequence PAIR-ELIG RT universe.
#
# RESOURCE REQUEST, SIZED FROM MEASUREMENT NOT FROM CAUTION:
#   --mem=32G   worst shard holds 4.22 GiB of token array; peak host ~8.4 GiB for the arrays
#               plus ~6 GiB model/runtime. The 1080 Ti smoke showed SLURM MaxRSS 5.0 GB on a
#               200-sequence run. 32G is ~2x the worst case, down from the 64G debug request.
#   --time=1:00 worst shard is 2,358,080 residues; at the 1080 Ti's measured 4,412 res/s that
#               is 9 min. An A100 is faster. 1 h is the array-task ceiling, not a reservation.
#   --gres a100 ESM-C runs fp32 and would work on any card, but the cache is pinned to ONE
#               GPU architecture so that shards of the same cache are numerically comparable.
#   %4          at most 4 concurrent tasks - this shares the queue rather than seizing it.
#
# Shards are contiguous blocks of the frozen (len, hash) order with boundaries at multiples
# of BATCH=8, so shard-local batch geometry equals a single-stream run. A shard already
# present and validating is SKIPPED, never recomputed: re-running this array is the resume.
set -euo pipefail

B=/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings
PY=/ibex/user/rioszemm/conda-environments/retron_esmc/bin/python

module load cuda/12.2 2>/dev/null || echo "[warn] cuda/12.2 module unavailable; using the wheel's bundled runtime"
echo "=== task ${SLURM_ARRAY_TASK_ID} on $(hostname) ==="
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

"$PY" "$B/code/embed_shard.py" \
    --model esmc \
    --fasta "$B/inputs/rt_pair_universe.faa" \
    --project "$B/esmc300m_v1/shards" \
    --shard "${SLURM_ARRAY_TASK_ID}" \
    --shard-size 4096
