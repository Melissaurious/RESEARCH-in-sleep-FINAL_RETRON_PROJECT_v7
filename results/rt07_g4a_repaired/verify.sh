#!/usr/bin/env bash
# REPAIRED verifier. It ONLY verifies. Regeneration lives in scripts/regenerate.sh.
#  1 enforce registered input hashes   2 run into a fresh temp dir
#  3 diff against frozen canonical outputs   4 non-zero on drift   5 never overwrite
set -euo pipefail
cd "$(dirname "$0")"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
rc=0

echo "== 1. input hash enforcement =="
[ -s INPUTS.tsv ] || { echo "FAIL: INPUTS.tsv missing"; exit 2; }
while IFS=$'\t' read -r p role h; do
  [ "$p" = "path" ] && continue
  [ "$role" = "expected_output" ] && continue   # diffed in step 2-3, not hash-gated here
  if [ ! -r "$p" ]; then echo "FAIL: registered input unreadable: $p"; rc=1; continue; fi
  a=$(sha256sum "$p" | cut -d' ' -f1)
  [ "$a" = "$h" ] || { echo "FAIL: hash drift on $p"; echo "   registered $h"; echo "   actual     $a"; rc=1; }
done < INPUTS.tsv
[ "$rc" = "0" ] || { echo "ABORT: registered inputs changed; verification is meaningless." >&2; exit 1; }
echo "   all registered inputs match"

echo "== 2-3. reproduce into a temp dir and diff =="
OUT=$(mktemp -d "${TMPDIR:-/tmp}/g4aR_tab.XXXXXX")
WRK=$(mktemp -d "${TMPDIR:-/tmp}/g4aR_wrk.XXXXXX")
$PY scripts/step1_split.py    "$WRK" "$OUT" >/dev/null
$PY scripts/step2_analysis.py "$WRK" "$OUT" >/dev/null
$PY scripts/step3_decoys.py   "$WRK" "$OUT" >/dev/null
$PY scripts/step4_hhmake_sensitivity.py "$WRK" "$OUT" >/dev/null

shopt -s nullglob
for f in tables/*.tsv; do
  b=$(basename "$f")
  grep -qxF "$b" control/AUTHORED_TABLES.txt 2>/dev/null && continue
  if [ ! -f "$OUT/$b" ]; then echo "DRIFT: $b not reproduced"; rc=1; continue; fi
  diff -q "$f" "$OUT/$b" >/dev/null || { echo "DRIFT: $b differs"; diff "$f" "$OUT/$b" | head -6; rc=1; }
done
for f in "$OUT"/*.tsv; do
  b=$(basename "$f")
  grep -qxF "$b" control/AUTHORED_TABLES.txt 2>/dev/null && continue
  [ -f "tables/$b" ] || { echo "DRIFT: $b reproduced but not landed"; rc=1; }
done

[ "$rc" = "0" ] && echo "OK: inputs authenticated and every computed table reproduced byte-identically." \
                || echo "FAILED: drift detected." >&2
exit $rc
