#!/usr/bin/env bash
# DELIBERATE regeneration of canonical outputs. NOT a verification.
# Kept OUTSIDE verify.sh so verification can never bless changed code or inputs.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
echo "WARNING: regenerating canonical tables in place. This is not verification."
$PY scripts/step1_split.py    work tables
$PY scripts/step2_analysis.py work tables
$PY scripts/step3_decoys.py   work tables
$PY scripts/step4_hhmake_sensitivity.py work tables
echo "regenerated. Re-register hashes with scripts/register_inputs.sh, then run verify.sh."
