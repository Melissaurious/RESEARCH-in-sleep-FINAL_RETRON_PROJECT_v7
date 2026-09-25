#!/usr/bin/env bash
# embed_g0_input_contract - reruns the gate END TO END FROM THIS ASSEMBLED BUNDLE.
#
# Measured on borg: ~3 min CPU (a01 15 s, a02 32 s, a03 5 s, a04 ~90 s, a05 25 s) plus
# ~2 min GPU for the two pilots. The GPU steps are OPTIONAL here and are skipped unless
# --with-gpu is passed, because the CPU half is what fixes the input contract.
#
# The rerun writes to ARIS_OUTPUT/rerun-embed_g0_input_contract/ and does NOT overwrite
# data/derived/ or this bundle. Compare its tables against tables/ to verify reproduction.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
S="$HERE/scripts"
WORK="$ROOT/ARIS_OUTPUT/rerun-embed_g0_input_contract"

PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
PY_ESMC=/home/borg/miniconda3/envs/retron_esmc/bin/python
PY_RINALMO=/home/borg/miniconda3/envs/rinalmo/bin/python

mkdir -p "$WORK/scripts" "$WORK/tables" "$WORK/work" "$WORK/logs"
cp "$S"/*.py "$S"/*.sh "$WORK/scripts/"

echo "== a01 population audit - 9 declared counts must reproduce exactly"
"$PY" "$WORK/scripts/a01_universe.py"

echo "== a02 oriented ncRNA reconstruction - REQUIRES 16,458/16,458 hash round-trip"
# NOTE: this rewrites data/derived/rt_ncrna_oriented_v1.* byte-identically. Verify with
#   sha256sum -c <(awk 'NR>1{print $3"  "$1}' data/derived/rt_ncrna_oriented_v1.MANIFEST.tsv)
"$PY" "$WORK/scripts/a02_ncrna_fasta.py"

echo "== a03 RT protein FASTA for the pair universe"
"$PY" "$WORK/scripts/a03_rt_fasta.py"

echo "== a04 relatedness clustering sweep (mmseqs x4, cd-hit-est x4)"
bash "$WORK/scripts/a04_cluster.sh"

echo "== a05 connected-component structure - the split-feasibility evidence"
"$PY" "$WORK/scripts/a05_components.py"

if [[ "${1:-}" == "--with-gpu" ]]; then
  echo "== a06 ESM-C 300M gated pilot"
  "$PY_ESMC" "$WORK/scripts/a06_pilot_esmc.py"
  echo "== a07 RiNALMo giga-v1 gated pilot"
  "$PY_RINALMO" "$WORK/scripts/a07_pilot_rinalmo.py"
else
  echo "== a06/a07 GPU pilots SKIPPED (pass --with-gpu to run them)"
fi

echo
echo "== verify the landed dataset still matches its manifest"
cd "$ROOT" && sha256sum -c <(awk 'NR>1{print $3"  "$1}' \
    data/derived/rt_ncrna_oriented_v1.MANIFEST.tsv)

echo
echo "RERUN COMPLETE. Diff $WORK/tables against $HERE/tables to verify reproduction."
