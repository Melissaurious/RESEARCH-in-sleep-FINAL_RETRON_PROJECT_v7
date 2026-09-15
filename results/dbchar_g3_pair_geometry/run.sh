#!/usr/bin/env bash
# dbchar_g3_pair_geometry - reruns the gate END TO END FROM THIS ASSEMBLED BUNDLE (BS-3).
# Measured on borg: ~4 min wall (the g2 derived datasets are inputs; the raw corpus is read
# only by the independent second count).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/scripts"
WORK="$HERE/../../ARIS_OUTPUT/rerun-dbchar_g3_pair_geometry"

CORPUS=/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june
DERIVED=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived
G2=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/dbchar_g2_canonical_units

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

echo "== c04 positive controls: synthetic placements with known geometry"
"$PY" "$S/c04_controls.py" --out "$WORK" --g2-scripts "$G2/scripts"

echo "== p01 build the placement table and the exact-pair view"
"$PY" "$S/p01_pairs.py" --derived "$DERIVED" --work "$WORK"

echo "== a02 geometry priors on named populations"
"$PY" "$S/a02_priors.py" --derived "$DERIVED" --work "$WORK"

echo "== a03 bipartite pairing topology"
"$PY" "$S/a03_topology.py" --work "$WORK"

echo "== a04 audits: the shipped field, non-Retron CM placements, the downstream mode"
"$PY" "$S/a04_audits.py" --work "$WORK"

echo "== c05 independent second count (awk geometry on the raw bytes)"
bash "$S/c05_second_count.sh" "$CORPUS" "$WORK" 16

echo "== c06 reconcile: second count, landed g2, then prior work"
"$PY" "$S/c06_reconcile.py" --work "$WORK" --derived "$DERIVED" --g2-bundle "$G2"

echo "== figures (read tables/ and nothing else)"
"$PY" "$S/fig01_geometry.py" --work "$WORK"

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
# figures are compared by their data TSV, not by their bytes: a PNG carries a renderer
# fingerprint that changes with the matplotlib build without any number changing.
echo "  (figures verified through their sidecar TSVs above)"

if [ "$rc" -eq 0 ]; then echo "REPRODUCED: every landed table is byte-identical on rerun."
else echo "NOT REPRODUCED - see the DIFF/MISSING/NEW lines above." >&2; fi
exit "$rc"
