#!/usr/bin/env bash
# dbchar_g2b_rt_cds_recovery - reruns the gate END TO END FROM THIS ASSEMBLED BUNDLE (BS-3).
# Measured on borg: ~1 min wall.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/scripts"
WORK="$HERE/../../ARIS_OUTPUT/rerun-dbchar_g2b_rt_cds_recovery"

CORPUS=/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june
DERIVED=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived
G2=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/dbchar_g2_canonical_units

export PATH=/home/borg/miniconda3/envs/retron_tradicional/bin:$PATH
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
mkdir -p "$WORK/tables"

echo "== c03 self-validation: the controls must reject a seeded-bad expectation"
if "$PY" "$S/c03_controls.py" --out "$WORK/seedbad" --g2-scripts "$G2/scripts" --seed-bad >/dev/null 2>&1; then
  echo "FATAL: the controls ACCEPTED a seeded-bad expectation - they are untested." >&2
  exit 1
fi
echo "   rejected the seeded-bad case, as required"

echo "== c03 positive controls (synthetic corpus through the landed g2 pipeline)"
"$PY" "$S/c03_controls.py" --out "$WORK" --g2-scripts "$G2/scripts"

echo "== r01 recovery classification + the independent Biopython translation check"
"$PY" "$S/r01_recovery.py" --derived "$DERIVED" --corpus "$CORPUS" --work "$WORK"

echo "== c02 independent second count (awk on the raw bytes)"
bash "$S/c02_second_count.sh" "$CORPUS" "$WORK" 16

echo "== c04 reconcile against the second count and the landed g2 bundle"
"$PY" "$S/c04_reconcile.py" --work "$WORK" --g2-bundle "$G2"

echo "== assemble"
"$PY" "$S/assemble.py" --work "$WORK"

echo "== BS-3 / WA-B.2: does this reproduce the landed tables byte for byte?"
rc=0
for f in "$HERE"/tables/*.tsv; do
  b="$(basename "$f")"
  if [ ! -f "$WORK/tables/$b" ]; then echo "  MISSING on rerun: $b"; rc=1; continue; fi
  if cmp -s "$f" "$WORK/tables/$b"; then echo "  OK   $b"; else echo "  DIFF $b"; rc=1; fi
done
for f in "$WORK"/tables/*.tsv; do
  b="$(basename "$f")"
  [ -f "$HERE/tables/$b" ] || { echo "  NEW on rerun (not landed): $b"; rc=1; }
done
if cmp -s "$HERE/MANIFEST.tsv" "$WORK/MANIFEST.tsv"; then echo "  OK   MANIFEST.tsv"
else echo "  DIFF MANIFEST.tsv"; rc=1; fi

if [ "$rc" -eq 0 ]; then echo "REPRODUCED: every landed table is byte-identical on rerun."
else echo "NOT REPRODUCED - see the DIFF/MISSING/NEW lines above." >&2; fi
exit "$rc"
