#!/usr/bin/env bash
# s02 — ncRNA-blind RT homolog clusters over the master table's exact RTs (our population).
# RT50 (>=50% id, >=80% bidirectional cov) = homolog set key within a type label;
# RT90 (>=90% id) = near-duplicate collapse so a set is not 40 copies of one strain variant.
# Protein sequences only; no ncRNA, CM or SPIRE HMM information enters.
set -euo pipefail
S=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-spire-ncrna/analysis/spire_ncrna_audit/scripts
OUT=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-spire-ncrna/ARIS_OUTPUT/spire_ncrna_audit/s02
PY=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-dbchar-workbench/ARIS_OUTPUT/dbchar_workbench/.venv/bin/python
MM=/home/borg/miniconda3/envs/retron_tradicional/bin/mmseqs
mkdir -p "$OUT"
$PY - "$OUT/master_rt.faa" <<'EOF'
import sys, duckdb
M='/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-spire-ncrna/ARIS_OUTPUT/spire_ncrna_audit/master/master_rt_system.parquet'
D='/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_exact_v1.parquet'
rows=duckdb.sql(f"""SELECT e.rt_seq_hash, e.rt_seq FROM read_parquet('{D}') e
  WHERE e.rt_seq_hash IN (SELECT DISTINCT rt_seq_hash FROM read_parquet('{M}')) ORDER BY 1""").fetchall()
open(sys.argv[1],'w').write(''.join(f'>{h}\n{s}\n' for h,s in rows)); print(len(rows),'exact RTs')
EOF
for id in 0.5 0.9; do
  tag=RT$(echo "$id*100/1" | bc)
  $MM easy-cluster "$OUT/master_rt.faa" "$OUT/$tag" "$OUT/tmp_$tag" \
      --min-seq-id $id -c 0.8 --cov-mode 0 --threads 40 -v 1
done
sha256sum "$OUT"/master_rt.faa "$OUT"/RT50_cluster.tsv "$OUT"/RT90_cluster.tsv > "$OUT/SHA256SUMS"
cut -f1 "$OUT/RT50_cluster.tsv" | sort -u | wc -l; cut -f1 "$OUT/RT90_cluster.tsv" | sort -u | wc -l
