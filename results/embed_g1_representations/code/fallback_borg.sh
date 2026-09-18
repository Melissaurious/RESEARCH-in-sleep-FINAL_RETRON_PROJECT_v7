#!/usr/bin/env bash
# embed_g1 FALLBACK - run production on borg's RTX 4090s instead of Ibex.
#
# WHEN THIS IS ALLOWED TO RUN. Only when the Ibex A100 queue has not delivered, and only as an
# ALL-OR-NOTHING switch per cache. It REFUSES to start if any shard of the target cache has
# already landed on Ibex, because a cache half-produced on sm_80 (A100) and half on sm_89
# (4090) is two computations wearing one name. merge_shards.py now has gpu_arch in its frozen
# contract and would reject such a mix at verification time; this check just fails earlier and
# more cheaply.
#
# WHAT IS AND IS NOT DIFFERENT FROM THE IBEX RUN.
#   same:      embed_shard.py, the frozen (len,hash) order, BATCH=8, shard boundaries, fp32 /
#              bf16 forwards, BOS-EOS stripping, fp16 on disk, hash keying, the DONE/resume
#              contract, and the validate-then-copy discipline.
#   different: gpu_arch sm_89 not sm_80, and for RiNALMo torch 2.7.1 not 2.1.0. Both are
#              recorded per shard and both are contract fields, so the difference is visible
#              in provenance rather than silent.
#
# MEASURED COST (embed_g0 pilot, same machine, same scripts):
#   ESM-C    69,900 res/s -> 11,236,474 residues ~= 2.7 min
#   RiNALMo  25,634 nt/s  ->  2,719,581 nt       ~= 1.8 min
# The 4090 is Ada (sm_89) and DOES support bf16, so RiNALMo runs here where the 1080 Ti failed.
#
# GPU 1 is used by default, leaving GPU 0 for other local work. Override with EMB_GPU.
set -euo pipefail

ROOT=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings
CODE="$ROOT/ARIS_OUTPUT/embed_g1_ibex/code"
OUT=${EMB_OUT:-$ROOT/data/derived/embeddings}
GPU=${EMB_GPU:-1}
IBEX=/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings

PY_ESMC=/home/borg/miniconda3/envs/retron_esmc/bin/python
PY_RINALMO=/home/borg/miniconda3/envs/rinalmo/bin/python

export CUDA_VISIBLE_DEVICES="$GPU"
export TMPDIR=${TMPDIR:-/tmp}          # transient work; never the persistent tree

echo "=== borg fallback: GPU $GPU, out $OUT, scratch $TMPDIR ==="
nvidia-smi -i "$GPU" --query-gpu=name,memory.total --format=csv,noheader

# --- refuse a mixed-architecture cache -------------------------------------------------
for cache in esmc300m_v1 rinalmo_giga_v1; do
  n=$(ssh -o BatchMode=yes ibex "ls -d $IBEX/$cache/shards/shard_* 2>/dev/null | wc -l" 2>/dev/null || echo 0)
  if [ "${n:-0}" -gt 0 ]; then
    echo "REFUSING: $n shard(s) of $cache already landed on Ibex (sm_80)."
    echo "  Producing the rest here (sm_89) would make one cache out of two computations."
    echo "  Decide explicitly: either let Ibex finish $cache, or delete its shards and"
    echo "  rebuild the whole cache here. Not both."
    exit 1
  fi
done
echo "no Ibex shards present for either cache - a clean switch"

mkdir -p "$OUT"/{esmc300m_v1/shards,rinalmo_giga_v1/shards,inputs,manifests,logs}
cp -n "$ROOT/ARIS_OUTPUT/embed_g0_population_audit/work/rt_pair_universe.faa" "$OUT/inputs/" 2>/dev/null || true
cp -n "$ROOT/data/derived/rt_ncrna_oriented_v1.fna" "$OUT/inputs/" 2>/dev/null || true

run() {   # model, python, fasta, cache, n_shards
  echo; echo "=== $1: $5 shards ==="
  for i in $(seq 0 $(($5 - 1))); do
    "$2" "$CODE/embed_shard.py" --model "$1" --fasta "$OUT/inputs/$3" \
         --project "$OUT/$4/shards" --shard "$i" --shard-size 4096 \
         2>&1 | tee -a "$OUT/logs/$1.log"
  done
}

run esmc    "$PY_ESMC"    rt_pair_universe.faa      esmc300m_v1     8
run rinalmo "$PY_RINALMO" rt_ncrna_oriented_v1.fna  rinalmo_giga_v1 5

echo; echo "=== verify both caches ==="
for c in esmc300m_v1 rinalmo_giga_v1; do
  /home/borg/miniconda3/envs/retron_tradicional/bin/python "$CODE/merge_shards.py" \
      --base "$OUT" --cache "$c"
done

cat <<'NOTE'

=== NOT DONE AUTOMATICALLY: publishing to the persistent namespace ===
The operator designated /ibex/project/.../embeddings as the persistent home. This run wrote
to a local tree. Pooled is ~0.1 GB and trivial to push; the token cache is ~28.6 GB and that
transfer may cost more wall-clock than the queue wait it avoided. Decide, then:

  rsync -av --info=progress2 <OUT>/ ibex:/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings/

and re-run merge_shards.py against the Ibex copy to prove the transfer preserved every hash.
NOTE
