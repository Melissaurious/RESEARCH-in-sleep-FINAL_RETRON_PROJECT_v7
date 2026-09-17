#!/usr/bin/env bash
# Regenerate every computed product of this bundle into the given directories.
# Usage: regenerate.sh <work_dir> <tables_dir> <control_dir>
# Regeneration lives OUTSIDE the verifier: verify.sh calls this into a temp tree and diffs.
set -euo pipefail
WORK="$1"; TABLES="$2"; CONTROL="$3"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$WORK" "$TABLES" "$CONTROL"

python3 "$HERE/register_inputs.py"           "$TABLES"
python3 "$HERE/calibrate_support.py"         "$WORK" "$TABLES" "$CONTROL"
python3 "$HERE/catalytic_rule.py"            "$WORK" "$TABLES" "$CONTROL"
python3 "$HERE/freeze_tests.py"              "$WORK" "$TABLES"
python3 "$HERE/unit_tests_v2.py"             "$WORK" "$TABLES" "$CONTROL"
python3 "$HERE/construction_validation_v2.py" "$WORK" "$TABLES" "$CONTROL"
