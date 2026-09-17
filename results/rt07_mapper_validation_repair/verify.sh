#!/usr/bin/env bash
# Reproducibility verifier. Regenerates into a TEMP tree and diffs against the frozen tables.
# NEVER writes into the bundle. Exits non-zero on ANY drift.
#
# The g4a lesson: a harness that `tee`s into the file it is meant to check can never detect
# drift. This one only ever reads the frozen copies.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP="${TMPDIR:-/tmp}/verify_mapper_repair_$$"
mkdir -p "$TMP"/{work,tables,control}
trap 'rm -rf "$TMP"' EXIT

echo "== regenerating into $TMP =="
if ! bash "$HERE/scripts/regenerate.sh" "$TMP/work" "$TMP/tables" "$TMP/control" \
        > "$TMP/regen.log" 2>&1; then
    echo "FAIL: regeneration errored"; tail -25 "$TMP/regen.log"; exit 1
fi

status=0
echo "== diffing computed products =="
for d in tables control; do
    for f in "$HERE/$d"/*; do
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
        b="$(basename "$f")"
        [ -f "$HERE/$d/$b" ] || { echo "FAIL  $d/$b regenerated but not landed"; status=1; }
    done
done

echo "== freeze manifest =="
MAN="$HERE/../../review-stage/manifests/rt07_mapper_validation_repair.MANIFEST"
if [ -f "$MAN" ]; then
    python3 "$HERE/scripts/freeze_manifest.py" verify "$HERE" "$MAN" || status=1
else
    echo "  (no manifest yet - build one before review)"
fi

[ $status -eq 0 ] && echo "VERIFY OK" || echo "VERIFY FAILED"
exit $status
