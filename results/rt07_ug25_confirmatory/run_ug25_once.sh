#!/usr/bin/env bash
# UG25 CONFIRMATORY RUN — ONE SHOT.
#
# Verifies the frozen pre-UG25 bundle against its externally pinned root, copies the frozen
# code to a temp location (so the frozen bundle is never the import root), and runs the gate
# exactly once with UG25 added to the runtime family authorisation.
#
# UG25 authorisation is supplied HERE, at run time, by the operator — not by any constant in
# the source tree.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FROZEN="$HERE/../FINAL_PRE_UG25_VALIDATION_BUNDLE"
MAN="$HERE/../../review-stage/manifests/FINAL_PRE_UG25.MANIFEST"
PINNED="$(tr -d '[:space:]' < "$HERE/../../review-stage/roots/FINAL_PRE_UG25.root")"

echo "== pre-run: frozen bundle must verify against the external pinned root =="
python3 -B "$FROZEN/code/integrity.py" verify "$FROZEN" "$MAN" "$PINNED"

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/ug25_pycache_$$"
export RT07_AUTHORISED_FAMILIES="Retrons,GII,DGRs,CRISPR,UG3,AbiA,UG25"   # operator authorisation

CODE="${TMPDIR:-/tmp}/ug25_code_$$"
WORK="${1:?usage: run_ug25_once.sh <work_dir>}"
mkdir -p "$CODE" "$WORK" "$HERE/tables"
cp "$FROZEN"/code/*.py "$CODE"/
cp "$HERE"/code/ug25_gate.py "$CODE"/
chmod u+w "$CODE"/*.py
trap 'rm -rf "$CODE" "$PYTHONPYCACHEPREFIX"' EXIT

echo "== executing the confirmatory gate ONCE =="
echo "   RT07_AUTHORISED_FAMILIES=$RT07_AUTHORISED_FAMILIES"
python3 -B "$CODE/ug25_gate.py" "$WORK" "$HERE/tables" "$FROZEN"
