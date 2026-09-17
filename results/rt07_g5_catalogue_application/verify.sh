#!/usr/bin/env bash
# g5 verifier — re-checks the LANDED dataset without re-running the 369,381-sequence pass.
#
# It confirms: the instrument is still canonical; every dataset file still hashes to its
# manifest entry; the shard manifest sums to the frozen census; and the QC tables regenerate
# byte-identically from the landed parquet.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python3
DATASET="$ROOT/data/derived/rt07_g5"
W="${1:-${TMPDIR:-/tmp}/verify_g5_$$}"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$W/tables"
status=0

echo "== instrument still canonical =="
"$PY" -B -c "
import sys; sys.path.insert(0,'$ROOT/results/rt07_g4b_production_mapper/code')
from rtmap import version as V
c=V.check_instrument(); mv=V.mapper_version(c)
assert mv=='rtmap-1.0.0/53a1e738a19b3896', mv
print('  ok    '+mv)" || status=1

echo "== dataset files match the manifest =="
"$PY" -B -c "
import hashlib,os,sys
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda: f.read(1<<20), b''): h.update(c)
    return h.hexdigest()
bad=0
for ln in open('$HERE/tables/g5_dataset_manifest.tsv').read().splitlines()[1:]:
    f,b,h = ln.split('\t')
    p=os.path.join('$DATASET',f)
    if not os.path.isfile(p): print(f'FAIL  missing {f}'); bad=1; continue
    if str(os.path.getsize(p))!=b or sha(p)!=h: print(f'FAIL  changed {f}'); bad=1
    else: print(f'  ok    {f}')
sys.exit(bad)" || status=1

echo "== shard manifest reconciles to the frozen census =="
"$PY" -B -c "
import sys
rows=[l.split('\t') for l in open('$HERE/tables/g5_shard_manifest.tsv').read().splitlines()[1:]]
n_in=sum(int(r[1]) for r in rows); n_seq=sum(int(r[2]) for r in rows)
n_st=sum(int(r[3]) for r in rows); mvs={r[5] for r in rows}
print(f'  shards {len(rows)}  input {n_in}  sequences {n_seq}  state rows {n_st}')
assert len(rows)==512, len(rows)
assert n_in==369381==n_seq, (n_in,n_seq)
assert n_st==369381*150, n_st
assert mvs=={'rtmap-1.0.0/53a1e738a19b3896'}, mvs
print('  ok    reconciles to G5_ELIGIBLE_N=369381 under one instrument')" || status=1

echo "== QC regenerates identically from the landed dataset =="
"$PY" -B -u "$HERE/scripts/qc.py" "$DATASET" "$W/tables" > "$W/qc.log" 2>&1 || {
    echo "FAIL  qc.py errored"; tail -5 "$W/qc.log"; status=1; }
for f in "$HERE/tables"/g5_qc_*.tsv "$HERE/tables"/g5_state_occupancy.tsv \
         "$HERE/tables"/g6_readiness_*.tsv; do
    b="$(basename "$f")"
    if diff -q "$f" "$W/tables/$b" >/dev/null 2>&1; then echo "  ok    $b"
    else echo "FAIL  $b DRIFTED"; status=1; fi
done

[ $status -eq 0 ] && echo "g5 VERIFY OK" || echo "g5 VERIFY FAILED"
echo "artefacts: $W"
exit $status
