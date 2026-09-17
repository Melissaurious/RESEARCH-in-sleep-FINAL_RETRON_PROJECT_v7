#!/usr/bin/env bash
# Reproducibility + provenance verifier. FAIL-CLOSED (REPAIR 2).
#
# Regenerates into a TEMP tree and diffs against the frozen products. NEVER writes into the
# bundle. Exits non-zero on ANY drift, ANY missing product, ANY extra product, a MISSING
# manifest, a TAMPERED manifest, or a root mismatch.
#
# v1 defect: the manifest step sat behind `if [ -f "$MAN" ]` whose else-branch printed a note
# and left status untouched, so a bundle with NO provenance at all printed VERIFY OK.
#
# Usage: verify.sh [expected_root_sha256]
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPECTED_ROOT="${1:-}"
TMP="${TMPDIR:-/tmp}/verify_mapper_repair_v2_$$"
mkdir -p "$TMP"/{work,tables,control}
trap 'chmod -R u+w "$TMP" 2>/dev/null; rm -rf "$TMP"' EXIT

export PYTHONDONTWRITEBYTECODE=1
status=0

echo "== regenerating into $TMP =="
if ! bash "$HERE/scripts/regenerate.sh" "$TMP/work" "$TMP/tables" "$TMP/control" \
        > "$TMP/regen.log" 2>&1; then
    echo "FAIL: regeneration errored"; tail -25 "$TMP/regen.log"; exit 1
fi

echo "== diffing computed products =="
for d in tables control; do
    for f in "$HERE/$d"/*; do
        [ -e "$f" ] || continue
        b="$(basename "$f")"
        case "$b" in *.md) continue;; esac          # authored, not computed
        if [ ! -f "$TMP/$d/$b" ]; then
            echo "FAIL  $d/$b was not regenerated - it is outside the reproduction path"
            status=1; continue
        fi
        if diff -q "$f" "$TMP/$d/$b" >/dev/null; then
            echo "  ok    $d/$b"
        else
            echo "FAIL  $d/$b DRIFTED"; diff "$f" "$TMP/$d/$b" | head -8; status=1
        fi
    done
done

echo "== checking for regenerated products absent from the bundle =="
for d in tables control; do
    for f in "$TMP/$d"/*; do
        [ -e "$f" ] || continue
        b="$(basename "$f")"
        [ -f "$HERE/$d/$b" ] || { echo "FAIL  $d/$b regenerated but not landed"; status=1; }
    done
done

echo "== no bytecode may have been written into the bundle =="
if find "$HERE" -name '__pycache__' -type d | grep -q .; then
    echo "FAIL  __pycache__ present inside the bundle"; status=1
else
    echo "  ok    no __pycache__"
fi

echo "== freeze manifest (REQUIRED - absence is a failure) =="
MAN="$HERE/../../review-stage/manifests/rt07_mapper_validation_repair_v2.MANIFEST"
if [ ! -f "$MAN" ]; then
    echo "FAIL  manifest absent at $MAN - provenance is REQUIRED, not optional"
    status=1
else
    if [ -n "$EXPECTED_ROOT" ]; then
        python3 -B "$HERE/scripts/freeze_manifest.py" verify "$HERE" "$MAN" "$EXPECTED_ROOT" \
            || status=1
    else
        python3 -B "$HERE/scripts/freeze_manifest.py" verify "$HERE" "$MAN" || status=1
    fi
fi

if [ $status -eq 0 ]; then echo "VERIFY OK"; else echo "VERIFY FAILED"; fi
exit $status
