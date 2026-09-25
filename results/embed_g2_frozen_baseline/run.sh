#!/usr/bin/env bash
# embed_g2_frozen_baseline - reproduce the gate end to end.
# Requires the pooled caches fetched from the Ibex namespace into work/ (see README §Inputs).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
S="$HERE/scripts"
"$PY" "$S/a01_assemble.py"
"$PY" "$S/a03_validation.py"     # baselines + CCA grid; TEST IS NOT OPENED
"$PY" "$S/a04_test.py"           # confirmatory; opens test once
echo "compare tables/ against this bundle's tables/ to verify reproduction"
