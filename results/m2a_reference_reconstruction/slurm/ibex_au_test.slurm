#!/bin/bash
#SBATCH --account=pi-hohndor
#SBATCH --job-name=m2a_au_test_v3
#SBATCH --partition=batch
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --mail-type=END,FAIL,TIME_LIMIT_90
#SBATCH --mail-user=rioszemm@kaust.edu.sa
# M2a K1 AU test: pruned published topology vs the clean ML tree, same alignment and model.
# Budget cap = 8 CPU x 1 h = 8 CPU-h.
set -euo pipefail
CONDA_ENV=/ibex/user/rioszemm/conda-environments/retron_tradicional
export PATH="$CONDA_ENV/bin:$PATH"
module purge
echo "Host $(hostname) | $(iqtree --version | head -1)"
cat in/v3_pruned_published.nwk tree/clean_v3.treefile > tree/au_candidates.nwk
iqtree -s in/v3_fftns2.afa -m LG+F+R10 -z tree/au_candidates.nwk -te tree/clean_v3.treefile -n 0 -zb 10000 -au -nt "$SLURM_CPUS_PER_TASK" -seed 2026 -pre tree/au_v3 -redo
echo "DONE $(date -Is)"
