#!/usr/bin/env bash
# rt07_g3_prior_method_replication - reruns the gate END TO END FROM THIS BUNDLE (BS-3).
# Measured on borg: ~90 s wall, CPU only, no network. Reads prior project trees READ-ONLY.
#
# The seeded-bad guard runs first: it switches the identity measure from residues to
# identifiers - the exact defect the prior audit avoided - and the controls must then fail.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/scripts"
WORK="$HERE/../../ARIS_OUTPUT/rerun-rt07_g3_prior_method_replication"
export PATH=/home/borg/miniconda3/envs/retron_tradicional/bin:$PATH
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python

rm -rf "$WORK"; mkdir -p "$WORK/tables"

echo "== 1. independence and contamination, re-measured by exact sequence identity"
"$PY" "$S/s02_contamination.py" --out "$WORK/tables"

echo "== 2. frame correspondence: prior frames carried onto shared LtrA residues"
"$PY" "$S/s03_frame_correspondence.py" --work "$WORK" --out "$WORK/tables"

echo "== 3. the prior RT0-RT7 frame table, and the RT0 object audit"
"$PY" "$S/s04_prior_frame_and_rt0.py" --out "$WORK/tables"

echo "== 4. verdicts, one per prior claim"
"$PY" "$S/s05_verdicts.py" --out "$WORK/tables"

echo "== 5. seeded-bad guard: identifier matching MUST fail the controls"
if "$PY" "$S/s06_controls_and_summary.py" --out "$WORK/tables" --seed-bad >/dev/null 2>&1; then
  echo "SEEDED-BAD GUARD PASSED (identifier matching failed the controls, as required)"
else
  echo "FATAL: identifier matching passed the controls - they test nothing" >&2; exit 1
fi

echo "== 6. controls, summary, handoff"
"$PY" "$S/s06_controls_and_summary.py" --out "$WORK/tables"

echo "== 7. report (computes nothing; every value resolves to a landed table)"
mkdir -p "$WORK/report"
"$PY" "$S/assemble_report.py" --bundle "$WORK" --out "$WORK/report"

echo "== 8. manifest and inputs"
"$PY" "$S/assemble.py" --bundle "$HERE" --out "$WORK"

echo "== 9. byte comparison against the landed bundle"
rc=0
compare() {
  if [ ! -f "$2" ]; then echo "MISSING ON RERUN: $1" >&2; rc=1
  elif ! cmp -s "$1" "$2"; then echo "DIFF: $1" >&2; rc=1; fi
}
for f in "$HERE"/tables/*.tsv; do compare "$f" "$WORK/tables/$(basename "$f")"; done
compare "$HERE/REPORT.md"    "$WORK/report/REPORT.md"
compare "$HERE/REPORT.html"  "$WORK/report/REPORT.html"
compare "$HERE/MANIFEST.tsv" "$WORK/MANIFEST.tsv"
for f in "$WORK"/tables/*.tsv; do
  [ -f "$HERE/tables/$(basename "$f")" ] || { echo "NEW ON RERUN: $(basename "$f")" >&2; rc=1; }
done
if ! diff <(cut -f1,2,3 "$HERE/INPUTS.tsv") <(cut -f1,2,3 "$WORK/INPUTS.tsv") >/dev/null; then
  echo "DIFF: INPUTS.tsv (path/sha256/bytes)" >&2; rc=1
fi

if [ "$rc" -eq 0 ]; then
  echo "REPRODUCED: every landed table, report and manifest is byte-identical on rerun."
else
  echo "NOT REPRODUCED - see the DIFF/MISSING/NEW lines above." >&2
fi
exit "$rc"
