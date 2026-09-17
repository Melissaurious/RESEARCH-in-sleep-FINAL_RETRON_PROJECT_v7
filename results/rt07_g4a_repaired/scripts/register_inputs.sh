#!/usr/bin/env bash
# Repair B: register EVERY input the pipeline depends on - sources, ALL scripts (incl. the
# sensitivity step), ALL control documents (incl. Addendum 2), the verifier, the interpreter,
# the tools, AND the expected-output hashes.
set -euo pipefail
cd "$(dirname "$0")/.."
B=/home/borg/miniconda3/envs/retron_tradicional/bin
C=/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/RTs-collection.faa
{ printf 'path\trole\tsha256\n'
  printf '%s\tSOLE_SEQUENCE_INPUT\t%s\n' "$C" "$(sha256sum "$C"|cut -d' ' -f1)"
  for f in scripts/*.py scripts/*.sh control/*.md control/*.txt verify.sh \
           g4a_repaired_comparison_report.md; do
    [ -f "$f" ] && printf '%s\tpipeline_or_control\t%s\n' "$f" "$(sha256sum "$f"|cut -d' ' -f1)"
  done
  printf '%s\tinterpreter\t%s\n' "$B/python3.12" "$(sha256sum $B/python3.12|cut -d' ' -f1)"
  for t in mafft muscle hmmbuild hmmsearch hhmake hhalign mmseqs esl-reformat; do
    printf '%s\ttool\t%s\n' "$B/$t" "$(sha256sum $B/$t|cut -d' ' -f1)"
  done
  for f in tables/*.tsv; do
    printf '%s\texpected_output\t%s\n' "$f" "$(sha256sum "$f"|cut -d' ' -f1)"
  done
} > INPUTS.tsv
echo "registered $(( $(wc -l < INPUTS.tsv) - 1 )) entries ($(grep -c expected_output INPUTS.tsv) expected outputs)"
