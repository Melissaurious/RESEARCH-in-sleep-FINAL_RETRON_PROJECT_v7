#!/usr/bin/env bash
# Post-freeze verifier. FAIL-CLOSED throughout.
#
# Reproduces into a SEPARATE temp directory and compares against the frozen expected outputs.
# The frozen bundle is read-only input. Code is executed from a temp copy, never imported
# from the bundle.
#
# The expected root MUST come from outside the bundle:
#   verify.sh <pinned_root_sha256>
#   verify.sh --root-file <path>
# There is no unpinned mode. A bundle cannot authenticate itself.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAN="$HERE/../../review-stage/manifests/FINAL_PRE_UG25.MANIFEST"
ROOTFILE_DEFAULT="$HERE/../../review-stage/roots/FINAL_PRE_UG25.root"

PINNED=""
case "${1:-}" in
    --root-file) PINNED="$(tr -d '[:space:]' < "${2:?--root-file needs a path}")" ;;
    "")          [ -f "$ROOTFILE_DEFAULT" ] && PINNED="$(tr -d '[:space:]' < "$ROOTFILE_DEFAULT")" ;;
    *)           PINNED="$1" ;;
esac
if [ -z "$PINNED" ]; then
    echo "FAIL  no external pinned root supplied and no root file found."
    echo "      usage: verify.sh <root_sha256> | verify.sh --root-file <path>"
    exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
export RT07_AUTHORISED_FAMILIES="${RT07_AUTHORISED_FAMILIES:-Retrons,GII,DGRs,CRISPR,UG3,AbiA}"
TMP="${TMPDIR:-/tmp}/verify_final_pre_ug25_$$"
export PYTHONPYCACHEPREFIX="$TMP/pycache"
mkdir -p "$TMP"/{work,tables,control}
trap 'chmod -R u+w "$TMP" 2>/dev/null; rm -rf "$TMP"' EXIT
status=0

echo "== reproducing into $TMP (frozen bundle is read-only input) =="
if ! bash "$HERE/run_clean.sh" "$TMP/work" "$TMP/tables" "$TMP/control" \
        > "$TMP/run.log" 2>&1; then
    echo "FAIL: clean-room reproduction errored"; tail -30 "$TMP/run.log"; exit 1
fi

echo "== diffing computed products against frozen expected outputs =="
for d in tables control; do
    for f in "$HERE/$d"/*; do
        [ -e "$f" ] || continue
        b="$(basename "$f")"
        case "$b" in *.md) continue;; esac
        if [ ! -f "$TMP/$d/$b" ]; then
            echo "FAIL  $d/$b not regenerated - outside the reproduction path"; status=1; continue
        fi
        if diff -q "$f" "$TMP/$d/$b" >/dev/null; then echo "  ok    $d/$b"
        else echo "FAIL  $d/$b DRIFTED"; diff "$f" "$TMP/$d/$b" | head -6; status=1; fi
    done
done

echo "== regenerated products must all be landed =="
for d in tables control; do
    for f in "$TMP/$d"/*; do
        [ -e "$f" ] || continue
        b="$(basename "$f")"
        [ -f "$HERE/$d/$b" ] || { echo "FAIL  $d/$b regenerated but not landed"; status=1; }
    done
done

echo "== no bytecode, no symlinks inside the frozen bundle =="
if find "$HERE" -name '__pycache__' -type d 2>/dev/null | grep -q .; then
    echo "FAIL  __pycache__ present in the bundle"; status=1
else echo "  ok    no __pycache__"; fi
SL="$(find "$HERE" -type l 2>/dev/null | grep -v '/\.claude/' || true)"
if [ -n "$SL" ]; then echo "FAIL  symlink(s) present:"; echo "$SL"; status=1
else echo "  ok    no symlinks"; fi

echo "== manifest + EXTERNAL pinned root (both REQUIRED) =="
if [ ! -f "$MAN" ]; then
    echo "FAIL  manifest absent at $MAN - provenance is required, not optional"; status=1
else
    python3 -B "$HERE/code/integrity.py" verify "$HERE" "$MAN" "$PINNED" || status=1
fi

if [ $status -eq 0 ]; then echo "VERIFY OK"; else echo "VERIFY FAILED"; fi
exit $status
