#!/usr/bin/env bash
# c03 - the independent second count for g2 (WA-D.3).
#
# Shares NO code with e01/a02: no Python, no JSON parser, no g2lib. One awk pass per file
# slices the `"rt_gene": { ... }` and `"actual_window": { ... }` blocks out of the raw bytes
# and emits the keys; coreutils `sort -u` counts the distinct ones. The unit keys it builds
# are the SAME definitions e01 uses, derived by a different route - that is the point.
#
#   bash c03_second_count.sh <corpus_dir> <out_dir> [procs]
set -euo pipefail
CORPUS="$1"; OUT="$2"; PROCS="${3:-16}"
mkdir -p "$OUT/second" "$OUT/second/parts"
export LC_ALL=C
: "${TMPDIR:=/tmp}"

one() {
  f="$1"; o="$2"; b="$(basename "$f")"
  awk -v B="$b" -v OUT="$o/second/parts" '
    function block(line, key,   i, s, e) {
      i = index(line, "\"" key "\": {"); if (i == 0) return ""
      s = substr(line, i + length(key) + 5)
      e = index(s, "}"); if (e == 0) return ""
      return substr(s, 1, e - 1)
    }
    function num(blk, key,   r) {
      if (!match(blk, "\"" key "\": -?[0-9]+")) return ""
      r = substr(blk, RSTART, RLENGTH); sub(/^"[a-z_]+": /, "", r); return r
    }
    function str(blk, key,   r) {
      if (!match(blk, "\"" key "\": \"[^\"]*\"")) return ""
      r = substr(blk, RSTART, RLENGTH); sub(/^"[a-z_]+": "/, "", r); sub(/"$/, "", r); return r
    }
    BEGIN { ids = OUT "/ids_" B; loci = OUT "/loci_" B; seqs = OUT "/seqs_" B }
    {
      n++
      # top-level contig: the FIRST "contig" occurrence on the line (cds entries repeat the key)
      contig = ""
      if (match($0, /"contig": "[^"]*"/)) { contig = substr($0, RSTART, RLENGTH)
        sub(/^"contig": "/, "", contig); sub(/"$/, "", contig) }
      rid = ""
      if (match($0, /"rt_system_id": "[^"]*"/)) { rid = substr($0, RSTART, RLENGTH)
        sub(/^"rt_system_id": "/, "", rid); sub(/"$/, "", rid) }
      rt = block($0, "rt_gene"); aw = block($0, "actual_window")
      rs = num(rt, "start"); re = num(rt, "end"); st = str(rt, "strand"); sq = str(rt, "sequence")
      ws = num(aw, "start"); we = num(aw, "end")
      if (index($0, "\"is_rt_gene\": true") == 0) n_nortcds++
      if (ws != "" && we != "" && ws + 0 > we + 0) n_inv++
      if (!(ws != "" && we != "" && rs != "" && re != "" && ws + 0 <= rs + 0 && re + 0 <= we + 0)) n_out++
      print rid > ids
      print contig ":" rs "-" re ":" st > loci
      # the exact-RT string: one trailing "*" removed, exactly as g2lib.rt_seq_norm declares
      sub(/\*$/, "", sq); print sq > seqs
    }
    END { printf "%s\t%d\t%d\t%d\t%d\n", B, n, n_nortcds, n_inv, n_out > (OUT "/cnt_" B) }
  ' "$f"
}
export -f one

find "$CORPUS" -maxdepth 1 -type f -name '*.jsonl' ! -name 'master_ncRNA-anchored_merged.jsonl' -print0 \
  | xargs -0 -P "$PROCS" -I{} bash -c 'one "$1" "$2"' _ {} "$OUT"

P="$OUT/second/parts"
{ printf 'source_file\tn_lines\tn_lines_without_is_rt_gene_true\tn_window_inverted\tn_rt_not_inside_window\n'
  cat "$P"/cnt_* | sort; } > "$OUT/second/c03_per_file.tsv"

n_ids=$(cat "$P"/ids_*   | sort -u -S 8G --parallel="$PROCS" | wc -l)
n_loc=$(cat "$P"/loci_*  | sort -u -S 8G --parallel="$PROCS" | wc -l)
n_seq=$(cat "$P"/seqs_*  | sort -u -S 16G --parallel="$PROCS" | wc -l)
{ printf 'measure\tn\troute\n'
  printf 'distinct_rt_system_id\t%s\tawk slice + sort -u\n' "$n_ids"
  printf 'distinct_locus_key\t%s\tawk slice + sort -u\n' "$n_loc"
  printf 'distinct_exact_rt_sequence\t%s\tawk slice + sort -u (one trailing * removed)\n' "$n_seq"
  awk -F'\t' 'NR>1{l+=$2; c+=$3; i+=$4; o+=$5}
    END{printf "lines_total\t%d\tawk line count\n", l
        printf "lines_without_is_rt_gene_true\t%d\tawk substring test\n", c
        printf "window_inverted\t%d\tawk numeric compare\n", i
        printf "rt_not_inside_window\t%d\tawk numeric compare\n", o}' "$OUT/second/c03_per_file.tsv"
} > "$OUT/second/c03_distinct.tsv"
rm -rf "$P"
echo "c03 done"
cat "$OUT/second/c03_distinct.tsv"
