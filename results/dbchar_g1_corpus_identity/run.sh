#!/usr/bin/env bash
# dbchar_g1_corpus_identity - reruns the gate END TO END FROM THIS ASSEMBLED BUNDLE (BS-3).
#
# Scripts are read from scripts/ beside this file. Working files (the fixture, the per-record
# manifest cache, the grep sidecars, the regenerated tables) go OUTSIDE the bundle, because
# they re-derive in minutes (BUNDLE_SPEC) and a bundle is write-once (BS-6). The last step
# compares every regenerated table and MANIFEST.tsv with the landed ones byte for byte: that
# comparison, not a validator, is what re-derives the inventory (WA-B.2).
#
# Measured on borg (48 cores, corpus ~95% page-cached): ~4 min wall end to end.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/scripts"
WORK="$HERE/../../ARIS_OUTPUT/rerun-dbchar_g1_corpus_identity"

# registered source roots (data/README.md) - read-only
CORPUS=/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june
SCHEMA=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/templates/input_format_schema_only.md
SCHEMA_V5=/home/borg/RESEARCH-in-sleep-RETRON-DB_V5/templates/input_format_schema_only.md
PRIOR_G0=/home/borg/RESEARCH-retron-db/results/dbchar-g0-inventory

# environment by content, not by name - env.lock in this bundle is the pin (BS-8)
export PATH=/home/borg/miniconda3/envs/retron_tradicional/bin:$PATH
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
mkdir -p "$WORK/tables"

# WA-A.3 / EVIDENCE_STANDARDS 6: the controls must REJECT a seeded-bad expectation first.
echo "== s04 self-validation: controls must reject a seeded-bad expectation"
if "$PY" "$S/s04_controls.py" --schema "$SCHEMA" --prior-g0 "$PRIOR_G0" --out "$WORK/seedbad" --seed-bad \
     >/dev/null 2>&1; then
  echo "FATAL: the controls ACCEPTED a seeded-bad expectation - they are untested." >&2
  exit 1
fi
echo "   rejected the seeded-bad case, as required"

echo "== s04 positive controls: every parse class, check and count route must fire on the fixture"
"$PY" "$S/s04_controls.py" --schema "$SCHEMA" --prior-g0 "$PRIOR_G0" --out "$WORK"

echo "== s02 record census: one strict JSON pass over every line of the 43 files"
"$PY" "$S/s02_record_census.py" --corpus "$CORPUS" --schema "$SCHEMA" --out "$WORK" --procs 40

echo "== s01 file identity: sha256, bytes, newlines, CRLF, for every corpus-root entry"
"$PY" "$S/s01_file_identity.py" --corpus "$CORPUS" --schema "$SCHEMA" --schema "$SCHEMA_V5" --out "$WORK" --procs 16

echo "== s03 independent second count: coreutils wc -l + grep token pairs, no JSON parser"
bash "$S/s03_second_count.sh" "$CORPUS" "$WORK" 16

echo "== s05 reconcile: second counts, then prior assumptions"
"$PY" "$S/s05_reconcile.py" --work "$WORK" --schema "$SCHEMA" --prior-g0 "$PRIOR_G0"

echo "== assemble: rollup + MANIFEST"
"$PY" "$S/assemble.py" --out "$WORK"

echo "== BS-3 / WA-B.2: does this reproduce the landed tables byte for byte?"
rc=0
for f in "$HERE"/tables/*.tsv; do
  b="$(basename "$f")"
  if [ ! -f "$WORK/tables/$b" ]; then echo "  MISSING on rerun: $b"; rc=1; continue; fi
  if cmp -s "$f" "$WORK/tables/$b"; then echo "  OK   $b"; else echo "  DIFF $b"; rc=1; fi
done
for f in "$WORK"/tables/*.tsv; do
  b="$(basename "$f")"
  case "$b" in s04_positive_controls_SEEDBAD.tsv) continue ;; esac
  [ -f "$HERE/tables/$b" ] || { echo "  NEW on rerun (not landed): $b"; rc=1; }
done
if cmp -s "$HERE/MANIFEST.tsv" "$WORK/MANIFEST.tsv"; then echo "  OK   MANIFEST.tsv"
else echo "  DIFF MANIFEST.tsv"; rc=1; fi

if [ "$rc" -eq 0 ]; then echo "REPRODUCED: every landed table is byte-identical on rerun."
else echo "NOT REPRODUCED - see the DIFF/MISSING/NEW lines above." >&2; fi
exit "$rc"
