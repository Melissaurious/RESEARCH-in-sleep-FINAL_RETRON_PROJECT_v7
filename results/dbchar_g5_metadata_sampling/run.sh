#!/usr/bin/env bash
# dbchar_g5_metadata_sampling - reruns the gate END TO END FROM THIS ASSEMBLED BUNDLE (BS-3).
# Measured on borg: ~4 min wall.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/scripts"
WORK="$HERE/../../ARIS_OUTPUT/rerun-dbchar_g5_metadata_sampling"
CORPUS=/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june
DERIVED=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived
META=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material/databases_metadata_files/metadata_files
PRIOR_G0=/home/borg/RESEARCH-retron-db/results/dbchar-g0-inventory
export PATH=/home/borg/miniconda3/envs/retron_tradicional/bin:$PATH
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
mkdir -p "$WORK/tables"

echo "== c02 self-validation: the controls must reject a seeded-bad expectation"
if "$PY" "$S/c02_controls.py" --out "$WORK/seedbad" --meta "$META" --derived "$DERIVED" --seed-bad >/dev/null 2>&1; then
  echo "FATAL: the controls ACCEPTED a seeded-bad expectation - they are untested." >&2; exit 1; fi
echo "   rejected the seeded-bad case, as required"

echo "== c02 positive controls: a key from each catalogue must join, a fabricated one must not"
"$PY" "$S/c02_controls.py" --out "$WORK" --meta "$META" --derived "$DERIVED"

echo "== j01 join coverage, taxonomy schemas, quality availability, overrepresentation"
"$PY" "$S/j01_join_and_sampling.py" --derived "$DERIVED" --meta "$META" --work "$WORK"

echo "== c03 independent second count (awk + sort -u over corpus and catalogues)"
bash "$S/c03_second_count.sh" "$CORPUS" "$META" "$WORK" 16

echo "== c04 reconcile: second count, then prior join work"
"$PY" "$S/c04_reconcile.py" --work "$WORK" --prior-g0 "$PRIOR_G0"

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
  b="$(basename "$f")"; [ -f "$HERE/tables/$b" ] || { echo "  NEW on rerun: $b"; rc=1; }
done
if cmp -s "$HERE/MANIFEST.tsv" "$WORK/MANIFEST.tsv"; then echo "  OK   MANIFEST.tsv"; else echo "  DIFF MANIFEST.tsv"; rc=1; fi
if [ "$rc" -eq 0 ]; then echo "REPRODUCED: every landed table is byte-identical on rerun."
else echo "NOT REPRODUCED - see the DIFF/MISSING/NEW lines above." >&2; fi
exit "$rc"
