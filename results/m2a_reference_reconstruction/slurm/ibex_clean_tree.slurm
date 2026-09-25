#!/bin/bash
#SBATCH --account=pi-hohndor
#SBATCH --job-name=m2a_clean_tree_v3
#SBATCH --partition=batch
#SBATCH --cpus-per-task=12
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --mail-type=END,FAIL,TIME_LIMIT_90
#SBATCH --mail-user=rioszemm@kaust.edu.sa
# M2a step 5b: the clean MCC-v3.1 reconstruction tree. Budget cap = 12 CPU x 2 h = 24 CPU-h.
# Deviations from Mestre 2020, declared: IQ-TREE 3.1.3 (not 1.6.12); model FIXED to LG+F+R10
# (no 546-model ModelFinder); --fast tree search; SH-aLRT x1000 (no UFBoot) -- all for budget.
set -euo pipefail
CONDA_ENV=/ibex/user/rioszemm/conda-environments/retron_tradicional
export PATH="$CONDA_ENV/bin:$PATH"
module purge
echo "Host $(hostname) | $(iqtree --version | head -1) | cpus=$SLURM_CPUS_PER_TASK"
sha256sum in/v3_fftns2.afa in/v3_pruned_published.nwk
mkdir -p tree
iqtree -s in/v3_fftns2.afa -m LG+F+R10 --fast -alrt 1000 -nt "$SLURM_CPUS_PER_TASK" -seed 2026 -pre tree/clean_v3 -redo
echo "DONE $(date -Is)"
