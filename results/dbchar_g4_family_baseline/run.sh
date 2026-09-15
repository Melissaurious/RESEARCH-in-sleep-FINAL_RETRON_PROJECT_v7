#!/usr/bin/env bash
# dbchar_g4_family_baseline - reruns the gate END TO END FROM THIS ASSEMBLED BUNDLE (BS-3).
# Measured on borg: ~3 min wall (hmmsearch over 9,593 proteins x 45 profiles included).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/scripts"
WORK="$HERE/../../ARIS_OUTPUT/rerun-dbchar_g4_family_baseline"

CORPUS=/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june
DERIVED=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived
G2=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/dbchar_g2_canonical_units
HMM=/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/HMM/RVT-All.hmm
PRIOR_C16=/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c16_rt_length_stats_by_family.tsv

export PATH=/home/borg/miniconda3/envs/retron_tradicional/bin:$PATH
export MPLCONFIGDIR="$WORK/.mpl"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
mkdir -p "$WORK/tables" "$WORK/figures" "$WORK/.mpl"

echo "== c04 self-validation: the controls must reject a seeded-bad expectation"
if "$PY" "$S/c04_controls.py" --out "$WORK/seedbad" --g2-scripts "$G2/scripts" --seed-bad >/dev/null 2>&1; then
  echo "FATAL: the controls ACCEPTED a seeded-bad expectation - they are untested." >&2
  exit 1
fi
echo "   rejected the seeded-bad case, as required"

echo "== c04 positive controls: known lengths, families and completeness evidence"
"$PY" "$S/c04_controls.py" --out "$WORK" --g2-scripts "$G2/scripts"

echo "== b01 the per-family baseline on the declared views"
"$PY" "$S/b01_baseline.py" --derived "$DERIVED" --work "$WORK"

echo "== h02 why MULTI carries several labels: myRT HMM evidence + its positive control"
"$PY" "$S/h02_multi_hmm.py" --derived "$DERIVED" --hmm "$HMM" --work "$WORK"

echo "== c03 independent second count (awk slice + sort -u over the raw corpus)"
bash "$S/c03_second_count.sh" "$CORPUS" "$WORK" 16

echo "== c05 reconcile: second count, then the prior family baseline"
"$PY" "$S/c05_reconcile.py" --work "$WORK" --prior-c16 "$PRIOR_C16"

echo "== figures (read tables/ and nothing else)"
"$PY" "$S/fig01_family.py" --work "$WORK"

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
echo "  (figures verified through their sidecar TSVs above)"

if [ "$rc" -eq 0 ]; then echo "REPRODUCED: every landed table is byte-identical on rerun."
else echo "NOT REPRODUCED - see the DIFF/MISSING/NEW lines above." >&2; fi
exit "$rc"
