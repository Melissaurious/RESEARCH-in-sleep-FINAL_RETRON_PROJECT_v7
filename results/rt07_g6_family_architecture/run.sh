#!/usr/bin/env bash
# rt07_g6_family_architecture - reruns the gate end to end from the landed g5 products.
#
# Order is the audit trail: control/PREDECLARATION.md was written BEFORE any statistic
# existed; control/REPAIR_1.md records the one permitted repair cycle and why it was
# triggered. Nothing here reads results/rt07_g7a_rt0_rt7_bridge/.
#
#   bash results/rt07_g6_family_architecture/run.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
BUNDLE="results/rt07_g6_family_architecture"
S="$BUNDLE/scripts"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python3
export PATH="/home/borg/miniconda3/envs/retron_tradicional/bin:$PATH"
export MPLCONFIGDIR="${TMPDIR:-/tmp}"

mkdir -p ARIS_OUTPUT/rt07_g6/work

# 0. the frozen instrument is not touched by this gate, but its identity is recorded.
$PY -c "import sys; sys.path.insert(0,'results/rt07_g4b_production_mapper/code'); \
from rtmap import version as V; print('instrument (read-only):', V.mapper_version(V.check_instrument()))"

# 0b. the g5 dataset this gate consumes must verify before it is analysed.
G5LOG=ARIS_OUTPUT/rt07_g6/work/g5_verify.log
bash results/rt07_g5_catalogue_application/verify.sh > "$G5LOG" 2>&1
tail -1 "$G5LOG"

$PY "$S/s01_clustering.py"        # audit prior clustering; build the clean label-blind resource
$PY "$S/s02_matrix.py"            # the frozen-state representation, 369,381 x 150
$PY "$S/s03_between_family.py"    # between-family arm, both nulls, all controls
$PY "$S/s04_within_retron.py"     # within-Retron arm: DF, PADLOC, label-free
$PY "$S/s05_controls.py"          # PC-SPLIT (measured independence) and PC-POS
$PY "$S/s06_figure.py"            # the figure
$PY "$S/s07_decision.py"          # terminal decision per arm

$PY "$S/seal.py" inputs
$PY "$S/seal.py" manifest
bash "$BUNDLE/verify.sh"
$PY "$S/seal.py" outputs          # LAST, after README carries its final STATUS line
echo "rt07_g6_family_architecture: complete"
