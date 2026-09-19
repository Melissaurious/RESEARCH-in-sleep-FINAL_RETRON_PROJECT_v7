#!/usr/bin/env bash
# cat3b_g2 — contract, thresholds, frozen detector, Tier A calibration. Tier B is never read.
set -euo pipefail
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
cd "$(dirname "$0")"
$PY scripts/anticircularity_check.py --selftest
$PY scripts/anticircularity_check.py scripts/detector.py
$PY scripts/evaluate_tierA.py
$PY scripts/sensitivity_tierA.py
echo "g2 reproduces the Tier A evaluation and the sensitivity table"
