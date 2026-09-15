#!/usr/bin/env bash
# dbchar_g2_canonical_units - reruns the gate END TO END FROM THIS ASSEMBLED BUNDLE (BS-3).
#
# Scripts are read from scripts/ beside this file; working files (shards, the derived
# datasets, regenerated tables) are written OUTSIDE the bundle, because they re-derive in
# minutes and a bundle is write-once (BS-6). The last step compares every regenerated table
# and MANIFEST.tsv with the landed ones byte for byte (WA-B.2).
#
# Measured on borg (48 cores, corpus page-cached): ~15 min wall end to end, ~28 GB peak.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/scripts"
WORK="$HERE/../../ARIS_OUTPUT/rerun-dbchar_g2_canonical_units"

CORPUS=/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june
G1=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/dbchar_g1_corpus_identity
PRIOR_LOCUS=/home/borg/RESEARCH-retron-db/data/derived/locus_table_v1.parquet
PRIOR_RT=/home/borg/RESEARCH-retron-db/data/derived/rt_unique_v1.tsv

export PATH=/home/borg/miniconda3/envs/retron_tradicional/bin:$PATH
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
mkdir -p "$WORK/tables"

# WA-A.3: the controls must REJECT a seeded-bad expectation before anything is trusted.
echo "== c04 self-validation: the controls must reject a seeded-bad expectation"
if "$PY" "$S/c04_controls.py" --out "$WORK/seedbad" --seed-bad >/dev/null 2>&1; then
  echo "FATAL: the controls ACCEPTED a seeded-bad expectation - they are untested." >&2
  exit 1
fi
echo "   rejected the seeded-bad case, as required"

echo "== c04 positive controls on the synthetic corpus (known ground truth)"
"$PY" "$S/c04_controls.py" --out "$WORK"

echo "== e01 extraction pass over the 42 RT-anchored files"
"$PY" "$S/e01_extract.py" --corpus "$CORPUS" --out "$WORK" --procs 40

echo "== m02 build the derived tables from the shards"
"$PY" "$S/m02_build_tables.py" --work "$WORK"

echo "== a02 unit ladder, integrity QC and eligibility denominators"
"$PY" "$S/a02_units.py" --work "$WORK"

echo "== c03 independent second count (awk + sort -u, no JSON parser)"
bash "$S/c03_second_count.sh" "$CORPUS" "$WORK" 16

echo "== c05 reconcile: second counts, the landed g1 bundle, then prior work"
"$PY" "$S/c05_reconcile.py" --work "$WORK" --g1-bundle "$G1" \
  --prior-locus-table "$PRIOR_LOCUS" --prior-rt-unique "$PRIOR_RT"

echo "== assemble: registry, rollup, MANIFEST"
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
