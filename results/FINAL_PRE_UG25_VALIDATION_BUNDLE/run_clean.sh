#!/usr/bin/env bash
# Clean-room execution. Usage: run_clean.sh <work_dir> <tables_dir> <control_dir>
#
# Code is COPIED to a temp location and executed from there. The frozen scientific bundle is
# never the import root, because importing from it is what wrote bytecode into the v1 bundle
# ~10 hours after it was frozen - a mutation caused by merely READING the bundle.
set -euo pipefail
WORK="$1"; TABLES="$2"; CONTROL="$3"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/pycache_$$"
: "${RT07_AUTHORISED_FAMILIES:?RT07_AUTHORISED_FAMILIES must be set explicitly - the
authorised development family list is a runtime input, never a source constant}"

CODE="${TMPDIR:-/tmp}/cleanroom_code_$$"
mkdir -p "$CODE" "$WORK" "$TABLES" "$CONTROL"
cp "$HERE"/code/*.py "$CODE"/
chmod u+w "$CODE"/*.py
trap 'rm -rf "$CODE" "$PYTHONPYCACHEPREFIX"' EXIT

python3 -B "$CODE/pipeline.py"      "$WORK" "$TABLES" "$CONTROL"
python3 -B "$CODE/tests_mapper.py"  "$WORK" "$TABLES" "$CONTROL"
python3 -B "$CODE/tests_c6.py"      "$TABLES"
python3 -B "$CODE/tests_freeze.py"  "${TMPDIR:-/tmp}" "$TABLES"
python3 -B "$CODE/sealing_proof.py" "$HERE" "$WORK" "$TABLES"
python3 -B "$CODE/register_inputs.py" "$TABLES"
