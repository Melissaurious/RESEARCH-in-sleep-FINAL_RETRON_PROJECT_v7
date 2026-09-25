#!/usr/bin/env bash
# embed_g2/s01 - the INDEPENDENT relatedness probe used to MEASURE leakage across a split.
#
# WHY THIS IS NOT THE CLUSTERING RUN. If leakage were measured with the same tool and the same
# threshold that built the split, the answer would be zero by construction - the split would be
# grading its own homework. This probe is deliberately MORE SENSITIVE than any clustering
# threshold under consideration, so it can see relatedness that the clustering deliberately
# ignored. It is run ONCE and reused for all 12 threshold combinations.
#
# RT   : mmseqs search at -s 7.5 (maximum sensitivity), --min-seq-id 0, e-value 1e-3.
#        No identity floor at all: we want the identity DISTRIBUTION across the boundary, not
#        a thresholded verdict.
# ncRNA: blastn -task blastn (word_size 7) - the right instrument for 34-395 nt sequences,
#        where megablast's 28-mer seeding would miss diverged relatives entirely.
#
# --max-seqs / -max_target_seqs 300: per query we keep the 300 best hits. For any split, the
# maximum identity from a held-out sequence to a training sequence is exact UNLESS all 300 of
# that query's retained hits fall in the held-out side. s02 counts those censored queries and
# reports them rather than hiding them.
set -euo pipefail

TASK="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(cd "$TASK/../.." && pwd)"
W="$TASK/work"; mkdir -p "$W"
T="${TMPDIR:-/tmp}/g2probe"; mkdir -p "$T"

MM=/home/borg/miniconda3/envs/colabfold/bin/mmseqs
BN=/home/borg/miniconda3/envs/retrons/bin/blastn
MK=/home/borg/miniconda3/envs/retrons/bin/makeblastdb

FAA="$ROOT/ARIS_OUTPUT/embed_g0_population_audit/work/rt_pair_universe.faa"
FNA="$ROOT/data/derived/rt_ncrna_oriented_v1.fna"

echo "=== RT all-vs-all: mmseqs search -s 7.5, no identity floor ==="
"$MM" createdb "$FAA" "$T/rtdb" -v 1
"$MM" search "$T/rtdb" "$T/rtdb" "$T/rtres" "$T/rttmp" \
      -s 7.5 --min-seq-id 0.0 -e 1e-3 --max-seqs 300 -c 0.0 --threads 16 -v 1
"$MM" convertalis "$T/rtdb" "$T/rtdb" "$T/rtres" "$W/rt_hits.tsv" \
      --format-output "query,target,fident,alnlen,qcov,tcov,evalue,bits" -v 1
echo "    RT hits: $(wc -l < "$W/rt_hits.tsv")"

echo "=== ncRNA all-vs-all: blastn -task blastn (word_size 7) ==="
"$MK" -in "$FNA" -dbtype nucl -out "$T/ncdb" > /dev/null
"$BN" -task blastn -word_size 7 -query "$FNA" -db "$T/ncdb" \
      -evalue 1e-3 -max_target_seqs 300 -num_threads 16 \
      -outfmt "6 qseqid sseqid pident length qlen slen evalue bitscore" \
      -out "$W/nc_hits.tsv"
echo "    ncRNA hits: $(wc -l < "$W/nc_hits.tsv")"

rm -rf "$T"
echo "DONE"
