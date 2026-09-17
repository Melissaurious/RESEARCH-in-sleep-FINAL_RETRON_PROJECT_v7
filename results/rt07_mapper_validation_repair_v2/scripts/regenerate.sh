#!/usr/bin/env bash
# Regenerate every computed product of this bundle into the given directories.
# Usage: regenerate.sh <work_dir> <tables_dir> <control_dir>
# Regeneration lives OUTSIDE the verifier: verify.sh calls this into a temp tree and diffs.
set -euo pipefail
WORK="$1"; TABLES="$2"; CONTROL="$3"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$WORK" "$TABLES" "$CONTROL"

# REPAIR 3: no bytecode. v1 left an unmanifested scripts/__pycache__/*.pyc inside a bundle
# that claimed nothing was ever written into it. __pycache__ is no longer excluded from the
# manifest either, so a stray .pyc would now show up as an ADDED file (freeze test F11).
export PYTHONDONTWRITEBYTECODE=1

python3 -B "$HERE/register_inputs.py"            "$TABLES"
python3 -B "$HERE/loader_equivalence.py"         "$TABLES"
python3 -B "$HERE/calibrate_support.py"          "$WORK" "$TABLES" "$CONTROL"
python3 -B "$HERE/catalytic_rule.py"             "$WORK" "$TABLES" "$CONTROL"
python3 -B "$HERE/control_policy_tests.py"       "$TABLES"
python3 -B "$HERE/freeze_tests.py"               "$WORK" "$TABLES"
python3 -B "$HERE/unit_tests_v2.py"              "$WORK" "$TABLES" "$CONTROL"
python3 -B "$HERE/construction_validation_v2.py" "$WORK" "$TABLES" "$CONTROL"
