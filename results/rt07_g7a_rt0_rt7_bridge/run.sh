#!/usr/bin/env bash
# rt07_g7a_rt0_rt7_bridge - reruns the gate end to end from the landed inputs.
#
# Order matters and is the gate's audit trail:
#   control/ASSIGNMENT_RULE.md was written BEFORE s03 ran. s01 traces the literature and
#   produced the Amendment 1 correction; s03 is the only new measurement; s04-s07 derive
#   from it. Nothing reads g5 or g6.
#
#   bash results/rt07_g7a_rt0_rt7_bridge/run.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
BUNDLE="results/rt07_g7a_rt0_rt7_bridge"
S="$BUNDLE/scripts"
export PATH="/home/borg/miniconda3/envs/retron_tradicional/bin:$PATH"
export MPLCONFIGDIR="${TMPDIR:-/tmp}"

mkdir -p ARIS_OUTPUT/rt07_g7a/work

# 0. the frozen instrument must verify before anything is measured against it.
python3 -c "import sys; sys.path.insert(0,'results/rt07_g4b_production_mapper/code'); \
from rtmap import version as V; print('instrument:', V.mapper_version(V.check_instrument()))"

# 0b. the frozen bundle's own crosswalk must STILL be unresolved: this gate does not edit it.
python3 -c "import sys; sys.path.insert(0,'results/rt07_g4b_production_mapper/code'); \
from rtmap import crosswalk as C; C.assert_unresolved_until_g7(); \
print('g4b control/CROSSWALK_RT0_RT7.tsv: still UNRESOLVED in every row, as required')"

python3 "$S/s01_evidence_register.py"     # historical evidence register + acquisition register
python3 "$S/s02_coordinates.py"           # Route S / P / C coordinate carriage
python3 "$S/s03_bridge.py"                # THE MEASUREMENT: state_id -> LtrA residue + controls
python3 "$S/s04_crosswalk.py"             # correspondence class per label
python3 "$S/s05_structural.py"            # structural comparators + PC-3
python3 "$S/s06_figure.py"                # the bridge figure
python3 "$S/s07_closure.py"               # terminal status per label + summary

python3 "$S/seal.py" inputs               # hash everything the gate READ
python3 "$S/seal.py" manifest             # artifact -> producing script

bash "$BUNDLE/verify.sh"

# OUTPUTS.tsv is written LAST, after README.md carries its final STATUS: line (BS-11).
python3 "$S/seal.py" outputs
echo "rt07_g7a_rt0_rt7_bridge: complete"
