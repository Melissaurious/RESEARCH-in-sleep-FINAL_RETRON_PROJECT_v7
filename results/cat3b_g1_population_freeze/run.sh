#!/usr/bin/env bash
# cat3b_g1 - population freeze. Deterministic; no network, no RNG.
# NON-DESTRUCTIVE: rebuilds into scratch and verifies the landed population.
set -euo pipefail
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
cd "$(dirname "$0")"
SCRATCH="${TMPDIR:-/tmp}/cat3b_g1_verify"
mkdir -p "$SCRATCH"
$PY scripts/scan.py "$SCRATCH/TRUTH_TABLE.tsv"
$PY scripts/stamp_tiers.py "$SCRATCH/TRUTH_TABLE.tsv"
$PY scripts/verify_population.py "$SCRATCH/TRUTH_TABLE.tsv"
