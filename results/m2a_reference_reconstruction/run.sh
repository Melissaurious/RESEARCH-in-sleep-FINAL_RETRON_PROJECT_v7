#!/usr/bin/env bash
# run.sh — M2a (+ the M2b freeze): the recorded commands, in creation order, written for THIS
# bundle's layout.
# ⚠ Not re-executed end to end after assembly (README STATUS: UNVERIFIED). A full rerun costs
#   about 60 CPU-h, and the approved M2a-c budget is exhausted. verify.sh re-derives every
#   table that follows from the shipped placements/fits/trees (12/12 byte-identical).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$HERE"
E=/home/borg/miniconda3/envs/retron_tradicional/bin; PY=$E/python3
export PYTHONDONTWRITEBYTECODE=1
AUD=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-mestre-audit
# 0. MCC-v3.1 freeze. This is an analysis-layer script; its frozen outputs ship in tables/MCC_V3_*
#    $PY scripts/m10_mcc_v3_freeze.py $AUD/ARIS_OUTPUT/mestre_audit/m10_work $AUD/analysis/mestre_audit/m2_design/mcc_v3
$PY scripts/mcc_v3.py work_selftest                                  # must print: selftest mismatches: 0
# 1. reference sets, denominator ledger, pruned published trees, K1 monophyly
$PY scripts/a01_reference_sets.py
# 2. reference alignments (MAFFT FFT-NS-2, untrimmed)
for x in v3 v2; do $E/mafft --retree 2 --thread 8 --anysymbol ref/${x}_ref.faa > aln/${x}_fftns2.afa; done
# 3. 85 %-identity groups
for x in v3 v2; do $E/mmseqs easy-cluster ref/${x}_ref.faa groups2/${x}_c85 groups2/tmp_$x --min-seq-id 0.85 -c 0.8 --cov-mode 0 --threads 8; done
# 4. fixed-topology LG+F+R10 fits (IQ-TREE; 13.0 + 8.4 CPU-h measured)
mkdir -p fit
for x in v3 v2; do $E/iqtree -s aln/${x}_fftns2.afa -te ref/${x}_pruned_published.nwk -m LG+F+R10 -nt 8 -pre fit/${x}_te -quiet -redo; done
# 5. full-reference raxml-ng fit, used by the controls and by M2c placement
mkdir -p rx
$E/raxml-ng --evaluate --msa aln/v3_fftns2.afa --tree ref/v3_pruned_published.nwk --model LG+F+R10 --prefix rx/v3_full --threads 8 --redo
# 6. leave-out replicates: PRIMARY blocked x10 per extractor; SECONDARY random x5, v3 only
for r in $(seq 1 10); do $PY scripts/a03_leaveout_validation.py v3 blocked $r; $PY scripts/a03_leaveout_validation.py v2 blocked $r; done
for r in $(seq 1 5); do $PY scripts/a03_leaveout_validation.py v3 random $r; done
# 7. calibrate on reps 1-5; evaluate on 6-10 (and on the random reps)
$PY scripts/a04_calibrate_evaluate.py v3
$PY scripts/a04_calibrate_evaluate.py v2
# 8. historical-tree comparison: published + recovered V4. The clean tree was CANCELLED for budget (see slurm/)
$PY scripts/a05_tree_comparison.py
# 9. controls: K3 negative panels, substitutes
$PY scripts/a06_controls.py
# 10. M2b freeze. It writes m2b/; the table is stored LOCAL ONLY in data/derived/m2_mestre/
$PY scripts/b01_query_freeze.py
# 11. M2c smoke — NOT RUN: K3 (shuffled controls) fired at step 7, and M2c is gated on M2a passing.
#     $PY scripts/c01_smoke.py
