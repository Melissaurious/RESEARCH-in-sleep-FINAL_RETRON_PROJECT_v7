#!/usr/bin/env bash
# rt07_stage2_final_report - reruns the gate END TO END FROM THIS ASSEMBLED BUNDLE (BS-3).
# Measured on borg: ~15 s wall. This gate COMPUTES NO SCIENTIFIC RESULT: it re-plots landed
# tables and resolves every number in the report out of the landed Stage-2 bundles and the
# reviewed records at the pinned commit. A selector that matches anything but one row, an
# unresolved placeholder, a status that differs from the erratum, or superseded wording fails
# the build.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/scripts"
ROOT="$(cd "$HERE/../.." && pwd)"
WORK="$ROOT/ARIS_OUTPUT/rerun-rt07_stage2_final_report"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$WORK/.mpl}"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
mkdir -p "$WORK/tables" "$WORK/figures" "$WORK/report" "$MPLCONFIGDIR"
find "$WORK" -maxdepth 2 -type f \( -name '*.tsv' -o -name '*.md' -o -name '*.png' -o -name '*.svg' \) -delete

echo "== guard: the builder must REFUSE a placeholder it cannot resolve"
if "$PY" - "$S" "$ROOT" "$WORK/guard" <<'GUARD' >/dev/null 2>&1
import sys, runpy
sys.path.insert(0, sys.argv[1])
import ledger as L
L.CLAIMS = [("S2-XX", "L5", "an undeclared {{placeholder_that_has_no_lookup}} must fail", ["g6_rho"], "")]
sys.argv = ["build.py", "--root", sys.argv[2], "--out", sys.argv[3]]
runpy.run_path(sys.path[0] + "/build.py", run_name="__main__")
GUARD
then echo "FATAL: the builder ACCEPTED an unresolvable placeholder - it is untested." >&2; exit 1; fi
echo "   refused, as required"

echo "== guard: the builder must REFUSE superseded wording"
if "$PY" - "$S" "$ROOT" "$WORK/guard2" <<'GUARD' >/dev/null 2>&1
import sys, runpy
sys.path.insert(0, sys.argv[1])
import ledger as L
L.CLAIMS = L.CLAIMS + [("S2-XX", "L4", "the two nulls bracket the truth", ["g6_rho"], "")]
sys.argv = ["build.py", "--root", sys.argv[2], "--out", sys.argv[3]]
runpy.run_path(sys.path[0] + "/build.py", run_name="__main__")
GUARD
then echo "FATAL: the builder ACCEPTED withdrawn wording - the guard is untested." >&2; exit 1; fi
echo "   refused, as required"

echo "== figures: re-plot F1-F6 from landed tables only"
"$PY" "$S/figures.py" --root "$ROOT" --out "$WORK"

echo "== build: resolve every value, write tables, render the report"
"$PY" "$S/build.py" --root "$ROOT" --out "$WORK"
"$PY" "$S/seal.py" --root "$ROOT" --out "$WORK"

echo "== BS-3: does this reproduce the landed artefacts byte for byte?"
rc=0
cmp_one() {
  if [ ! -f "$WORK/$1" ]; then echo "  MISSING on rerun: $1"; rc=1; return; fi
  if cmp -s "$HERE/$1" "$WORK/$1"; then echo "  OK   $1"; else echo "  DIFF $1"; rc=1; fi
}
for f in "$HERE"/tables/*.tsv;  do cmp_one "tables/$(basename "$f")"; done
for f in "$HERE"/figures/*;     do cmp_one "figures/$(basename "$f")"; done
for f in "$HERE"/report/*.md;   do cmp_one "report/$(basename "$f")"; done
cmp_one DELIVERABLES_INDEX.md
cmp_one MANIFEST.tsv
for d in tables figures report; do
  for f in "$WORK/$d"/*; do [ -f "$f" ] || continue; b="$(basename "$f")"
    [ -f "$HERE/$d/$b" ] || { echo "  NEW on rerun: $d/$b"; rc=1; }; done
done
if [ "$rc" -eq 0 ]; then echo "REPRODUCED: every landed artefact is byte-identical on rerun."
else echo "NOT REPRODUCED - see the DIFF/MISSING/NEW lines above." >&2; fi
exit "$rc"
