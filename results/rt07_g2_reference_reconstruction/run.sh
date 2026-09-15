#!/usr/bin/env bash
# rt07_g2_reference_reconstruction - reruns the gate END TO END FROM THIS BUNDLE (BS-3).
# Measured on borg: ~60 s wall, CPU only, no network. MAFFT is run deterministically.
#
# The seeded-bad guard runs FIRST: with the group threshold set to 0 every column counts as
# conserved, and the null controls MUST then fail. If they still pass, the controls are not
# testing anything and no number below is worth reading, so the rerun stops there.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/scripts"
WORK="$HERE/../../ARIS_OUTPUT/rerun-rt07_g2_reference_reconstruction"
export PATH=/home/borg/miniconda3/envs/retron_tradicional/bin:$PATH
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python

rm -rf "$WORK"
mkdir -p "$WORK/tables" "$WORK/reference"

echo "== 1. curated reference set (identity verified against the g1 acquisition record)"
"$PY" "$S/s01_reference_set.py" --work "$WORK" --out "$WORK/tables"

echo "== 2. reconstruct blocks by the Xiong & Eickbush criterion, over the declared sweep"
"$PY" "$S/s02_reconstruct_blocks.py" --work "$WORK" --out "$WORK/tables"

echo "== 3. seeded-bad guard: a criterion that calls everything conserved MUST fail its nulls"
if "$PY" "$S/s04_controls.py" --out "$WORK/tables" --seed-bad >/dev/null 2>&1; then
  echo "SEEDED-BAD GUARD PASSED (the broken criterion failed its null controls, as required)"
else
  echo "FATAL: the seeded-bad criterion passed its null controls - controls test nothing" >&2
  exit 1
fi

echo "== 4. landmarks, LtrA test, spacers, N-terminal region, recovery table"
"$PY" "$S/s03_landmarks_and_recovery.py" --out "$WORK/tables"

echo "== 5. controls and null models (overwrites the seeded-bad tables)"
"$PY" "$S/s04_controls.py" --out "$WORK/tables"

echo "== 6. second alignment frame (MAFFT FFT-NS-2), frame-independence"
"$PY" "$S/s05_second_frame.py" --work "$WORK" --out "$WORK/tables"

echo "== 7. summary, kill-criterion assessment, unresolved carried forward"
"$PY" "$S/s06_summary.py" --out "$WORK/tables"

echo "== 8. report (computes nothing; every value resolves to a landed table)"
mkdir -p "$WORK/report"
"$PY" "$S/assemble_report.py" --bundle "$WORK" --out "$WORK/report"

echo "== 9. manifest and inputs"
"$PY" "$S/assemble.py" --bundle "$HERE" --out "$WORK"

echo "== 10. byte comparison against the landed bundle"
rc=0
compare() {
  if [ ! -f "$2" ]; then echo "MISSING ON RERUN: $1" >&2; rc=1
  elif ! cmp -s "$1" "$2"; then echo "DIFF: $1" >&2; rc=1; fi
}
for f in "$HERE"/tables/*.tsv; do
  compare "$f" "$WORK/tables/$(basename "$f")"
done
for f in "$HERE"/reference/*; do
  compare "$f" "$WORK/reference/$(basename "$f")"
done
compare "$HERE/REPORT.md"    "$WORK/report/REPORT.md"
compare "$HERE/REPORT.html"  "$WORK/report/REPORT.html"
compare "$HERE/MANIFEST.tsv" "$WORK/MANIFEST.tsv"
for f in "$WORK"/tables/*.tsv; do
  [ -f "$HERE/tables/$(basename "$f")" ] || { echo "NEW ON RERUN: $(basename "$f")" >&2; rc=1; }
done
# INPUTS.tsv carries mtimes, which are filesystem state, not content: compare the hashes.
if ! diff <(cut -f1,2,3 "$HERE/INPUTS.tsv") <(cut -f1,2,3 "$WORK/INPUTS.tsv") >/dev/null; then
  echo "DIFF: INPUTS.tsv (path/sha256/bytes)" >&2; rc=1
fi

if [ "$rc" -eq 0 ]; then
  echo "REPRODUCED: every landed table, sequence product, report and manifest is byte-identical on rerun."
else
  echo "NOT REPRODUCED - see the DIFF/MISSING/NEW lines above." >&2
fi
exit "$rc"
