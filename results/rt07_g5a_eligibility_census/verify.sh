#!/usr/bin/env bash
# g5a verifier: regenerate into a temp tree and diff against what is landed.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python3
W="${1:-${TMPDIR:-/tmp}/verify_g5a_$$}"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$W/tables" "$W/derived"
status=0
"$PY" -B -u "$HERE/scripts/census.py" "$W/tables" "$W/derived" > "$W/run.log" 2>&1 \
  || { echo "FAIL: census errored"; tail -20 "$W/run.log"; exit 1; }
for f in "$HERE/tables"/*.tsv; do
    b="$(basename "$f")"
    if diff -q "$f" "$W/tables/$b" >/dev/null 2>&1; then echo "  ok    $b"
    else echo "FAIL  $b DRIFTED"; diff "$f" "$W/tables/$b" | head -5; status=1; fi
done
for b in g5a_eligibility_partition.tsv.gz g5a_ineligible_records.tsv.gz g5a_eligible_ids.txt.gz; do
    a="$(sha256sum "$HERE/../../data/derived/rt07_g5a/$b" | cut -d' ' -f1)"
    c="$(sha256sum "$W/derived/$b" | cut -d' ' -f1)"
    if [ "$a" = "$c" ]; then echo "  ok    $b  ${a:0:16}"
    else echo "FAIL  $b DRIFTED  $a != $c"; status=1; fi
done
[ $status -eq 0 ] && echo "g5a VERIFY OK" || echo "g5a VERIFY FAILED"
echo "artefacts: $W"
exit $status
