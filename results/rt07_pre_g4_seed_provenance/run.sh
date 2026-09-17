#!/usr/bin/env bash
# rt07_pre_g4_seed_provenance - reruns the pre-g4 provenance audit FROM THIS BUNDLE (BS-3).
# Measured on borg: ~60 s wall (mmseqs against the 501,561-sequence catalogue dominates).
# Reads prior project trees READ-ONLY. No network.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/scripts"
WORK="$HERE/../../ARIS_OUTPUT/rerun-rt07_pre_g4_seed_provenance"
export PATH=/home/borg/miniconda3/envs/retron_tradicional/bin:$PATH
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
rm -rf "$WORK"; mkdir -p "$WORK/tables"

echo "== 1. seed identity and per-member lineage"
"$PY" "$S/s01_seed_lineage.py" --out "$WORK/tables" --work "$WORK"
echo "== 2. leakage: identity and coverage against every population g4 might use"
"$PY" "$S/s02_leakage_audit.py" --out "$WORK/tables" --work "$WORK"
echo "== 3. which prior model was built from which subset"
"$PY" "$S/s03_model_lineage.py" --out "$WORK/tables"
echo "== 4. CAND_* provenance"
"$PY" "$S/s04_cand_provenance.py" --out "$WORK/tables"
echo "== 5. manifest and inputs"
"$PY" "$S/assemble.py" --bundle "$HERE" --out "$WORK"

echo "== 6. byte comparison against the landed bundle"
rc=0
for f in "$HERE"/tables/*.tsv; do
  b="$WORK/tables/$(basename "$f")"
  if [ ! -f "$b" ]; then echo "MISSING ON RERUN: $(basename "$f")" >&2; rc=1
  elif ! cmp -s "$f" "$b"; then echo "DIFF: $(basename "$f")" >&2; rc=1; fi
done
if ! diff <(cut -f1,2,3 "$HERE/INPUTS.tsv") <(cut -f1,2,3 "$WORK/INPUTS.tsv") >/dev/null; then
  echo "DIFF: INPUTS.tsv" >&2; rc=1; fi
if ! cmp -s "$HERE/MANIFEST.tsv" "$WORK/MANIFEST.tsv"; then echo "DIFF: MANIFEST.tsv" >&2; rc=1; fi
[ "$rc" -eq 0 ] && echo "REPRODUCED: every landed table and manifest is byte-identical on rerun." \
  || echo "NOT REPRODUCED - see above." >&2
exit "$rc"
