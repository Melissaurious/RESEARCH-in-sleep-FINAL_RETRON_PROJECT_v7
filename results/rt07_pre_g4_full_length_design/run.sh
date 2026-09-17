#!/usr/bin/env bash
# Reproduce every number quoted in this bundle. Read-only; no Stage-1 catalogue access.
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/measure.py "${1:-/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/}" \
  | tee tables/measured_values.tsv
