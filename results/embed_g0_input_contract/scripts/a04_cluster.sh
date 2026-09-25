#!/usr/bin/env bash
# embed-g0/a04 - relatedness resources for the PAIR-ELIG universe.
#
# RT proteins : mmseqs easy-cluster (colabfold env).
# ncRNA       : cd-hit-est (retron_tradicional env). 0.80 is cd-hit-est's floor for -n 8.
#
# Thresholds are SWEPT here, not chosen. One RT threshold and one ncRNA threshold are frozen
# LATER, with the component-size evidence from a05 in hand (operator amendment 3). Every
# other threshold becomes a sensitivity analysis.
#
# DETERMINISM - measured, not assumed. A first rerun of this gate moved the component counts
# by up to 3 in ~6,000. The cause was isolated by diffing the cluster files across the two
# runs: mmseqs was IDENTICAL, cd-hit-est DIFFERED. cd-hit's multithreaded path is not
# order-deterministic, so it runs SINGLE-THREADED here (-T 1). A split rule that cannot be
# regenerated is not a frozen split rule.
set -euo pipefail

W="$(cd "$(dirname "$0")/.." && pwd)/work"
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
MM=/home/borg/miniconda3/envs/colabfold/bin/mmseqs
CD=/home/borg/miniconda3/envs/retron_tradicional/bin/cd-hit-est
T="${TMPDIR:-/tmp}/mmtmp"
mkdir -p "$T" "$W/clusters"

FAA="$W/rt_pair_universe.faa"
FNA="$ROOT/data/derived/rt_ncrna_oriented_v1.fna"
test -s "$FAA" || { echo "missing $FAA"; exit 1; }
test -s "$FNA" || { echo "missing $FNA"; exit 1; }

for ID in 0.30 0.50 0.70 0.90; do
  echo "=== RT mmseqs easy-cluster --min-seq-id $ID -c 0.8 --cov-mode 0 ==="
  "$MM" easy-cluster "$FAA" "$W/clusters/rt_id${ID}" "$T/rt$ID" \
      --min-seq-id "$ID" -c 0.8 --cov-mode 0 --threads 16 -v 1 > "$W/clusters/rt_id${ID}.log" 2>&1
  echo "    clusters: $(cut -f1 "$W/clusters/rt_id${ID}_cluster.tsv" | sort -u | wc -l)"
done

for ID in 0.80 0.90 0.95 0.99; do
  echo "=== ncRNA cd-hit-est -c $ID -n 8 -aS 0.8 ==="
  "$CD" -i "$FNA" -o "$W/clusters/nc_id${ID}" -c "$ID" -n 8 -aS 0.8 \
      -M 8000 -T 1 -d 0 > "$W/clusters/nc_id${ID}.log" 2>&1
  echo "    clusters: $(grep -c '^>Cluster' "$W/clusters/nc_id${ID}.clstr")"
done

echo "DONE"
