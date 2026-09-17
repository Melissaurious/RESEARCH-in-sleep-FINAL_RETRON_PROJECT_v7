#!/usr/bin/env bash
# g4a reproducibility harness — REPAIRED.
#
# The previous bundle's run.sh piped `measure.py | tee tables/measured_values.tsv`,
# which OVERWROTE the expected output with the reproduction and therefore could never
# detect drift. The independent reviewer named this. This harness:
#   1. runs from registered inputs;
#   2. writes into a temporary reproduction directory;
#   3. diffs reproduced against landed;
#   4. exits non-zero on any drift;
#   5. never writes into tables/.
#
#   ./verify.sh              verify against the landed tables
#   ./verify.sh --regenerate deliberately refresh the landed tables (prints a warning)

set -euo pipefail
cd "$(dirname "$0")"

PY="/home/borg/miniconda3/envs/retron_tradicional/bin/python"
COLL="/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/RTs-collection.faa"
REGEN=0
[ "${1:-}" = "--regenerate" ] && REGEN=1

if [ ! -r "$COLL" ]; then
  echo "FAIL: registered input not readable: $COLL" >&2
  exit 2
fi

if [ "$REGEN" = "1" ]; then
  echo "WARNING: regenerating the landed tables in place. This is not a verification."
  OUT="tables"; WRK="work"
else
  OUT="$(mktemp -d "${TMPDIR:-/tmp}/g4a_repro.XXXXXX")/tables"
  WRK="$(mktemp -d "${TMPDIR:-/tmp}/g4a_work.XXXXXX")"
  mkdir -p "$OUT"
  echo "reproducing into $OUT (landed tables are not touched)"
fi

$PY scripts/g4a_pipeline.py        "$COLL" "$WRK" "$OUT" >/dev/null
$PY scripts/g4a_correspondence.py  "$WRK"  "$OUT"        >/dev/null
$PY scripts/g4a_dyad_check.py      "$WRK"  "$OUT"        >/dev/null
$PY scripts/g4a_intersection.py    "$WRK"  "$OUT"        >/dev/null
$PY scripts/g4a_transfer.py        "$WRK"  "$OUT"        >/dev/null
$PY scripts/g4a_negative_control.py "$WRK" "$OUT"        >/dev/null
$PY scripts/g4a_retron_split.py            "$OUT"        >/dev/null

[ "$REGEN" = "1" ] && { echo "regenerated."; exit 0; }

# Authored design tables are asserted to exist but not diffed: no script produces them.
is_authored() { grep -qxF "$1" control/AUTHORED_TABLES.txt; }

rc=0
shopt -s nullglob
for f in tables/*.tsv; do
  b="$(basename "$f")"
  if is_authored "$b"; then
    [ -s "$f" ] || { echo "MISSING: authored table $b is absent or empty"; rc=1; }
    continue
  fi
  if [ ! -f "$OUT/$b" ]; then
    echo "DRIFT: $b was not reproduced"; rc=1; continue
  fi
  if ! diff -q "$f" "$OUT/$b" >/dev/null; then
    echo "DRIFT: $b differs from the landed copy"
    diff "$f" "$OUT/$b" | head -8
    rc=1
  fi
done
for f in "$OUT"/*.tsv; do
  b="$(basename "$f")"
  is_authored "$b" && continue
  [ -f "tables/$b" ] || { echo "DRIFT: $b reproduced but not landed"; rc=1; }
done

if [ "$rc" = "0" ]; then
  echo "OK: every landed table reproduced byte-identically from registered inputs."
else
  echo "FAILED: drift detected (see above)." >&2
fi
exit $rc
