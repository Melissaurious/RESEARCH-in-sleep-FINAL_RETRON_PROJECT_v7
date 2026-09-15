#!/usr/bin/env bash
# dbchar_g7_stage1_report - reruns the gate END TO END FROM THIS ASSEMBLED BUNDLE (BS-3).
# Measured on borg: ~10 s wall. This gate COMPUTES NO SCIENTIFIC RESULT: it re-plots two landed
# tables and resolves every number in the report out of the seven landed bundles by an exact row
# selector. A selector that matches anything other than one row fails the build.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/scripts"
RESULTS="$(cd "$HERE/.." && pwd)"
DERIVED="$(cd "$HERE/../../data/derived" 2>/dev/null && pwd || true)"
WORK="$HERE/../../ARIS_OUTPUT/rerun-dbchar_g7_stage1_report"
export PATH=/home/borg/miniconda3/envs/retron_tradicional/bin:$PATH
export MPLCONFIGDIR="${MPLCONFIGDIR:-$WORK/.mpl}"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
mkdir -p "$WORK/tables" "$WORK/figures" "$MPLCONFIGDIR"

echo "== guard: the assembler must REFUSE a number it cannot resolve from a landed table"
if "$PY" - "$S" "$RESULTS" "$WORK/guard" <<'GUARD' >/dev/null 2>&1
import sys, pathlib, runpy
sys.path.insert(0, sys.argv[1])
import findings as F
F.SECTIONS = [dict(F.SECTIONS[0])]
F.SECTIONS[0]["finding"] = "an undeclared {placeholder_that_has_no_lookup} must fail the build"
sys.argv = ["assemble_report.py", "--results", sys.argv[2], "--out", sys.argv[3],
            "--self-figures", sys.argv[3]]
runpy.run_path(pathlib.Path(sys.argv[0]).parent / "assemble_report.py", run_name="__main__")
GUARD
then echo "FATAL: the assembler ACCEPTED an unresolvable placeholder - it is untested." >&2; exit 1; fi
echo "   refused the unresolvable placeholder, as required"

echo "== f01 re-plot two landed figures legibly, from their landed TSVs only"
"$PY" "$S/f01_restyle_figures.py" --results "$RESULTS" --work "$WORK"

echo "== assemble the report: resolve every number out of the landed bundles"
"$PY" "$S/assemble_report.py" --results "$RESULTS" --out "$WORK" --self-figures "$WORK/figures" ${DERIVED:+--derived "$DERIVED"}

echo "== BS-3 / WA-B.2: does this reproduce the landed artifacts byte for byte?"
rc=0
cmp_one() {
  if [ ! -f "$WORK/$1" ]; then echo "  MISSING on rerun: $1"; rc=1; return; fi
  if cmp -s "$HERE/$1" "$WORK/$1"; then echo "  OK   $1"; else echo "  DIFF $1"; rc=1; fi
}
for f in "$HERE"/tables/*.tsv;  do cmp_one "tables/$(basename "$f")"; done
for f in "$HERE"/figures/*;     do cmp_one "figures/$(basename "$f")"; done
cmp_one REPORT.html
cmp_one REPORT.md
cmp_one MANIFEST.tsv
for f in "$WORK"/tables/*.tsv; do b="$(basename "$f")"; [ -f "$HERE/tables/$b" ] || { echo "  NEW on rerun: tables/$b"; rc=1; }; done
for f in "$WORK"/figures/*;    do b="$(basename "$f")"; [ -f "$HERE/figures/$b" ] || { echo "  NEW on rerun: figures/$b"; rc=1; }; done
if [ "$rc" -eq 0 ]; then echo "REPRODUCED: every landed artifact is byte-identical on rerun."
else echo "NOT REPRODUCED - see the DIFF/MISSING/NEW lines above." >&2; fi
exit "$rc"
