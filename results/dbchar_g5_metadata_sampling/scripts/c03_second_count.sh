#!/usr/bin/env bash
# c03 - the independent second count for g5 (WA-D.3).
#
# Distinct (source_database, genome_id) pairs straight from the raw corpus bytes, and the
# distinct key count of every catalogue, both by awk + sort -u. No Python, no parquet.
set -euo pipefail
CORPUS="$1"; META="$2"; OUT="$3"; PROCS="${4:-16}"
mkdir -p "$OUT/second" "$OUT/second/parts"
export LC_ALL=C

one() {
  f="$1"; o="$2"; b="$(basename "$f")"
  awk '
    function str(line, key,   r) {
      if (!match(line, "\"" key "\": \"[^\"]*\"")) return ""
      r = substr(line, RSTART, RLENGTH); sub(/^"[a-z_]+": "/, "", r); sub(/"$/, "", r); return r
    }
    { db = str($0, "source_database"); g = str($0, "genome_id")
      sub(/^RS_/, "", g); sub(/^GB_/, "", g)      # the same normalisation j01 declares
      if (db != "") print db "\t" g }' "$f" > "$o/second/parts/g_$b"
}
export -f one

find "$CORPUS" -maxdepth 1 -type f -name '*.jsonl' ! -name 'master_ncRNA-anchored_merged.jsonl' -print0 \
  | xargs -0 -P "$PROCS" -I{} bash -c 'one "$1" "$2"' _ {} "$OUT"
cat "$OUT"/second/parts/g_* | sort -u -S 8G --parallel="$PROCS" \
  | awk -F'\t' '{n[$1]++} END {for (k in n) printf "%s\t%d\n", k, n[k]}' | sort \
  > "$OUT/second/parts/genomes_per_db.tsv"

{ printf 'source_database\tn_genomes\troute\n'
  awk -F'\t' '{printf "%s\t%s\tawk + sort -u over the raw corpus\n", $1, $2}' \
      "$OUT/second/parts/genomes_per_db.tsv"; } > "$OUT/second/c03_genomes_per_database.tsv"

# catalogue key counts: the header is the first line carrying the key name; comments are skipped
keycount() {  # file, key, gz
  local f="$1" key="$2" gz="$3"
  if [ "$gz" = "1" ]; then zcat "$META/$f"; else cat "$META/$f"; fi \
    | awk -v K="$key" 'BEGIN{i=-1}
        i<0 { for (j=1; j<=NF; j++) if ($j == K) { i=j; next } ; next }
        /^#/ { next }
        { k=$i; sub(/^RS_/, "", k); sub(/^GB_/, "", k); print k }' FS='\t' \
    | sort -u -S 4G | wc -l
}
{ printf 'file\tkey\tn_distinct_keys\troute\n'
  printf 'gtdb_bacteria_metadata.tsv.gz\taccession\t%s\tawk + sort -u\n' "$(keycount gtdb_bacteria_metadata.tsv.gz accession 1)"
  printf 'gtdb_archaea_metadata.tsv.gz\taccession\t%s\tawk + sort -u\n' "$(keycount gtdb_archaea_metadata.tsv.gz accession 1)"
  printf 'gem_metadata.tsv\tgenome_id\t%s\tawk + sort -u\n' "$(keycount gem_metadata.tsv genome_id 0)"
  printf 'mgnify_human_gut_metadata.tsv\tGenome\t%s\tawk + sort -u\n' "$(keycount mgnify_human_gut_metadata.tsv Genome 0)"
  printf 'mgnify_marine_metadata.tsv\tGenome\t%s\tawk + sort -u\n' "$(keycount mgnify_marine_metadata.tsv Genome 0)"
  printf 'mgnify_soil_metadata.tsv\tGenome\t%s\tawk + sort -u\n' "$(keycount mgnify_soil_metadata.tsv Genome 0)"
  printf 'ncbi_bacteria_assembly_summary.txt\t#assembly_accession\t%s\tawk + sort -u\n' "$(keycount ncbi_bacteria_assembly_summary.txt '#assembly_accession' 0)"
  printf 'ncbi_archaea_assembly_summary.txt\t#assembly_accession\t%s\tawk + sort -u\n' "$(keycount ncbi_archaea_assembly_summary.txt '#assembly_accession' 0)"
} > "$OUT/second/c03_catalogue_keys.tsv"
rm -rf "$OUT/second/parts"
cat "$OUT/second/c03_genomes_per_database.tsv"
cat "$OUT/second/c03_catalogue_keys.tsv"
