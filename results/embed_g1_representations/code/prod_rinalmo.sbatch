#!/bin/bash
#SBATCH --job-name=emb_rinalmo
#SBATCH --account=pi-hohndor
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100
#SBATCH --cpus-per-task=6
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --array=0-4%4
#SBATCH --output=/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings/logs/rinalmo_%A_%a.out
#SBATCH --error=/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings/logs/rinalmo_%A_%a.err
#
# embed_g1 PRODUCTION - RiNALMo giga-v1 over the 16,458-sequence oriented ncRNA universe.
#
# THE a100 CONSTRAINT IS NOT A PREFERENCE, IT IS A CORRECTNESS REQUIREMENT.
# The first Ibex submission was routed to a GTX 1080 Ti and died with
#   "Current CUDA Device does not support bfloat16"
# RiNALMo's frozen contract is a bf16 autocast forward. Dropping to fp16 to fit Pascal would
# produce a cache that is not the declared computation, so embed_shard.py now REFUSES any
# GPU without bf16 before running a single forward. Ampere or newer is required.
#
# RESOURCE REQUEST, SIZED FROM MEASUREMENT:
#   --mem=32G   worst shard holds 2.23 GiB of token array; peak host ~4.5 GiB plus ~6 GiB
#               model/runtime. RiNALMo is 651 M params against ESM-C's 333 M, so the model
#               is the larger share here. 32G is comfortable, down from the 64G debug request.
#   --time=1:00 worst shard is 933,337 nt; Borg's 4090 measured 25,634 nt/s -> 36 s. Even an
#               order of magnitude slower this finishes inside the hour.
#   %4          at most 4 concurrent tasks.
#
# A shard already present and validating is SKIPPED, never recomputed.
set -euo pipefail

B=/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings
PY=/ibex/user/rioszemm/conda-environments/rinalmo/bin/python

module load cuda/11.8 2>/dev/null || echo "[warn] cuda/11.8 module unavailable; using the wheel's bundled runtime"
echo "=== task ${SLURM_ARRAY_TASK_ID} on $(hostname) ==="
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

"$PY" "$B/code/embed_shard.py" \
    --model rinalmo \
    --fasta "$B/inputs/rt_ncrna_oriented_v1.fna" \
    --project "$B/rinalmo_giga_v1/shards" \
    --shard "${SLURM_ARRAY_TASK_ID}" \
    --shard-size 4096
