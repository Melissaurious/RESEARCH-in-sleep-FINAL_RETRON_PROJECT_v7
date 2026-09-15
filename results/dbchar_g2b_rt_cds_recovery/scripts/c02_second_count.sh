#!/usr/bin/env bash
# c02 - independent second count for g2b (WA-D.3).
#
# One awk pass over the raw bytes recomputes, for the lines that carry NO `"is_rt_gene": true`,
# the same class split r01 derives from the parquet tables: RT inside its window, RT beyond the
# window end, RT before the window start, RT crossing a window edge, inverted window. No Python,
# no parquet, no g2lib.
set -euo pipefail
CORPUS="$1"; OUT="$2"; PROCS="${3:-16}"
mkdir -p "$OUT/second" "$OUT/second/parts"
export LC_ALL=C

one() {
  f="$1"; o="$2"; b="$(basename "$f")"
  awk -v B="$b" '
    function block(line, key,   i, s, e) {
      i = index(line, "\"" key "\": {"); if (i == 0) return ""
      s = substr(line, i + length(key) + 5); e = index(s, "}")
      return e ? substr(s, 1, e - 1) : ""
    }
    function num(blk, key,   r) {
      if (!match(blk, "\"" key "\": -?[0-9]+")) return ""
      r = substr(blk, RSTART, RLENGTH); sub(/^"[a-z_]+": /, "", r); return r + 0
    }
    index($0, "\"is_rt_gene\": true") == 0 {
      rt = block($0, "rt_gene"); aw = block($0, "actual_window")
      rs = num(rt, "start"); re = num(rt, "end"); ws = num(aw, "start"); we = num(aw, "end")
      n++
      if (ws > we) { inv++ }
      else if (ws <= rs && re <= we) { inside++ }
      else if (rs <= we && re >= ws) { cross++ }
      else if (re < ws) { before++ }
      else { beyond++ }
    }
    END { printf "%s\t%d\t%d\t%d\t%d\t%d\t%d\n", B, n, inside, beyond, before, cross, inv }
  ' "$f" > "$o/second/parts/cnt_$b"
}
export -f one

find "$CORPUS" -maxdepth 1 -type f -name '*.jsonl' ! -name 'master_ncRNA-anchored_merged.jsonl' -print0 \
  | xargs -0 -P "$PROCS" -I{} bash -c 'one "$1" "$2"' _ {} "$OUT"

{ printf 'measure\tn\troute\n'
  cat "$OUT"/second/parts/cnt_* | awk -F'\t' '
    {n+=$2; i+=$3; b+=$4; f+=$5; c+=$6; v+=$7}
    END {printf "records_without_is_rt_gene_true\t%d\tawk substring test\n", n
         printf "rt_inside_its_window\t%d\tawk numeric compare\n", i
         printf "rt_beyond_window_end\t%d\tawk numeric compare\n", b
         printf "rt_before_window_start\t%d\tawk numeric compare\n", f
         printf "rt_crossing_a_window_edge\t%d\tawk numeric compare\n", c
         printf "window_inverted\t%d\tawk numeric compare\n", v}'
} > "$OUT/second/c02_classes.tsv"
rm -rf "$OUT/second/parts"
cat "$OUT/second/c02_classes.tsv"
