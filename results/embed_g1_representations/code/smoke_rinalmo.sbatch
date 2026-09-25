#!/bin/bash
#SBATCH --job-name=emb_smoke_rinalmo
#SBATCH --account=pi-hohndor
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --output=/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings/logs/smoke_rinalmo_%j.out
#SBATCH --error=/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings/logs/smoke_rinalmo_%j.err
#
# embed_g1 SMOKE - RiNALMo giga-v1, the declared 200-sequence length-stratified sample.
# Deliberately OVER-requested on mem/time: this job exists to MEASURE what production needs.
# The production request is sized from this job's numbers, not from this job's request.
set -euo pipefail

B=/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings
PY=/ibex/user/rioszemm/conda-environments/rinalmo/bin/python

module load cuda/11.8 2>/dev/null || echo "[warn] module load cuda/11.8 unavailable; relying on the wheel's bundled runtime"

echo "=== node ==="; hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo "=== scratch probe (reported by the script, not assumed here) ==="
echo "TMPDIR=${TMPDIR:-<unset>}  SLURM_JOB_ID=${SLURM_JOB_ID:-<unset>}"
ls -ld /local/scratch 2>&1 || echo "/local/scratch: absent"

"$PY" "$B/code/embed_shard.py" \
    --model rinalmo \
    --fasta "$B/inputs/rt_ncrna_oriented_v1.fna" \
    --project "$B/rinalmo_giga_v1/shards" \
    --smoke 200 --determinism

echo "=== peak resources as SLURM saw them ==="
sstat -j "${SLURM_JOB_ID}" --format=JobID,MaxRSS,MaxVMSize 2>/dev/null || true
