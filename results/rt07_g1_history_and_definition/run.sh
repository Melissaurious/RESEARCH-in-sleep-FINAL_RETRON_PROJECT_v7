#!/usr/bin/env bash
# rt07_g1_history_and_definition - reruns the gate END TO END FROM THIS ASSEMBLED BUNDLE (BS-3).
# Measured on borg: ~20 s wall, CPU only, no network.
#
# Order matters and is not cosmetic:
#   1. the SEEDED-BAD guard runs FIRST. If a deliberately broken detector still passes its
#      controls, the controls are decorative and every zero in this bundle is worthless, so
#      the rerun stops there.
#   2. then the real controls, then the measurement, then the second count.
#   3. then a byte comparison of every landed artifact against the rerun, in BOTH
#      directions - missing, differing, and new-on-rerun all fail.
#
# No step re-downloads anything. ALIGN_000044 was acquired once under launcher 9a and is
# verified here against the hash recorded at retrieval; reproduction must not depend on a
# remote host still answering.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/scripts"
WORK="$HERE/../../ARIS_OUTPUT/rerun-rt07_g1_history_and_definition"
export PATH=/home/borg/miniconda3/envs/retron_tradicional/bin:$PATH
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python

rm -rf "$WORK"
mkdir -p "$WORK/tables"

echo "== 0. extract the evidence text (sha256-verified inputs)"
"$PY" "$S/s01_extract_text.py" --work "$WORK"

echo "== 1. seeded-bad guard: a broken detector MUST fail its own controls"
if "$PY" "$S/s02_token_census.py" --work "$WORK" --out "$WORK/seedbad" --seed-bad; then
  echo "SEEDED-BAD GUARD PASSED (the broken detector failed its controls, as required)"
else
  echo "FATAL: the seeded-bad detector passed its controls - controls are not testing anything" >&2
  exit 1
fi
rm -rf "$WORK/seedbad"

echo "== 2. naming census + positive controls"
"$PY" "$S/s02_token_census.py" --work "$WORK" --out "$WORK/tables"

echo "== 3. evidence matrix, genealogy, operational matrix, unresolved register"
"$PY" "$S/s03_evidence_matrix.py" --work "$WORK" --out "$WORK/tables"

echo "== 4. acquisition and source-resolution register (verify, never re-fetch)"
"$PY" "$S/s04_acquisition_register.py" --out "$WORK/tables"

echo "== 5. independent second count (coreutils route, no shared code)"
bash "$S/s05_second_count.sh" "$WORK" "$WORK/tables"

echo "== 6. summary and prior reconciliation"
"$PY" "$S/s06_summary.py" --out "$WORK/tables"

echo "== 7. report (computes nothing; every value resolves to a landed table)"
cp -r "$WORK/tables" "$WORK/bundle_tables_tmp" >/dev/null 2>&1 || true
mkdir -p "$WORK/report"
"$PY" "$S/assemble_report.py" --bundle "$WORK" --out "$WORK/report"

echo "== 8. manifest and inputs"
"$PY" "$S/assemble.py" --bundle "$HERE" --out "$WORK"

echo "== 9. byte comparison against the landed bundle"
rc=0
compare() {  # compare <landed> <rerun>
  if [ ! -f "$2" ]; then echo "MISSING ON RERUN: $1" >&2; rc=1
  elif ! cmp -s "$1" "$2"; then echo "DIFF: $1" >&2; rc=1; fi
}
for f in "$HERE"/tables/*.tsv; do
  compare "$f" "$WORK/tables/$(basename "$f")"
done
compare "$HERE/REPORT.md"    "$WORK/report/REPORT.md"
compare "$HERE/REPORT.html"  "$WORK/report/REPORT.html"
compare "$HERE/MANIFEST.tsv" "$WORK/MANIFEST.tsv"
for f in "$WORK"/tables/*.tsv; do
  [ -f "$HERE/tables/$(basename "$f")" ] || { echo "NEW ON RERUN: $(basename "$f")" >&2; rc=1; }
done
# INPUTS.tsv carries mtimes, which are filesystem state rather than content: its hashes are
# compared instead, so a touched file does not read as a changed input.
if ! diff <(cut -f1,2,3 "$HERE/INPUTS.tsv") <(cut -f1,2,3 "$WORK/INPUTS.tsv") >/dev/null; then
  echo "DIFF: INPUTS.tsv (path/sha256/bytes)" >&2; rc=1
fi

if [ "$rc" -eq 0 ]; then
  echo "REPRODUCED: every landed table, report and manifest is byte-identical on rerun."
else
  echo "NOT REPRODUCED - see the DIFF/MISSING/NEW lines above." >&2
fi
exit "$rc"
