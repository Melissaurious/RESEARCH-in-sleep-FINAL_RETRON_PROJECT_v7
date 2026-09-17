#!/usr/bin/env bash
# g5a — regenerate the eligibility census. Deterministic: same inputs, same bytes out.
#   run.sh [derived_dir]
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python3
DERIVED="${1:-$HERE/../../data/derived/rt07_g5a}"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$DERIVED"
"$PY" -B -u "$HERE/scripts/census.py" "$HERE/tables" "$DERIVED"
