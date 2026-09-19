#!/usr/bin/env bash
# verify.sh — re-derives every M2a number that follows from the shipped placements, fits and
# trees, WITHOUT recomputing any phylogenetics:
#   a04  tau calibration on reps 1-5; evaluation on blocked reps 6-10 and random reps 1-5
#   a05  historical-tree comparison: the published tree + the recovered V4 trees
# It works in a temporary COPY of this bundle, under $TMPDIR, so the landed files are never
# written. It byte-compares the regenerated tables with tables/ and leaves the copy in place.
# The expensive steps (a03 replicate re-fits, the IQ-TREE fixed-topology fits, the M2b
# extraction) live in run.sh; README STATUS says why run.sh was not re-executed.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python3
T="$(mktemp -d "${TMPDIR:-/tmp}/m2a_verify.XXXXXX")"
cp -a "$HERE"/. "$T"/
mkdir -p "$T/fresh_eval"
export PYTHONDONTWRITEBYTECODE=1
mv "$T/tables" "$T/tables_landed"
mkdir -p "$T/eval"
for f in "$T"/eval/*; do [ -e "$f" ] || true; done
$PY "$T/scripts/a04_calibrate_evaluate.py" v3 >/dev/null
$PY "$T/scripts/a04_calibrate_evaluate.py" v2 >/dev/null
$PY "$T/scripts/a05_tree_comparison.py" >/dev/null
fail=0
for f in "$T"/eval/*; do
  b=$(basename "$f")
  if cmp -s "$f" "$HERE/tables/$b"; then echo "IDENTICAL $b"; else echo "DIFFERS   $b"; fail=1; fi
done
echo "work copy left at $T"
exit $fail
