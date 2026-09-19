#!/usr/bin/env bash
#SBATCH --job-name=m1_ibex_mestre_inventory
#SBATCH --account=pi-hohndor
#SBATCH --partition=batch
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=8G
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err
# ============================================================================
# M1 — READ-ONLY inventory and hash audit of the Ibex Mestre replication root.
#
#   ROOT = /ibex/project/c2366/RETRONS/Mestre_replication
#
# Writes ONLY to $OUT (default: $HOME/m1_ibex_mestre_audit_<date>). It never writes to,
# moves or deletes anything under ROOT. Bounded: 2 h wall, 8 cores, and files larger than
# HASH_MAX_BYTES are listed with size and mtime but not hashed; each one is listed as
# SKIPPED_SIZE, never silently omitted.
#
# Run on Ibex (borg has no SLURM and no /ibex mount):
#   scp ibex_mestre_inventory.sh rioszemm@ilogin.ibex.kaust.edu.sa:~/
#   ssh rioszemm@ilogin.ibex.kaust.edu.sa 'sbatch ~/ibex_mestre_inventory.sh'
# or interactively on a compute node: bash ibex_mestre_inventory.sh
#
# Outputs (in $OUT):
#   inventory.tsv        one row per filesystem object: type, bytes, mtime, sha256|SKIPPED_SIZE|UNREADABLE, path
#   dirs.tsv             per-directory file count and bytes (depth <= 4)
#   env.txt              host, date, tool versions visible on the node, sha256sum version
#   text_bundle.tar.gz   COPY of every small text-like file (scripts, logs, alignments, trees,
#                        HMMs, tables), <= TEXT_MAX_BYTES each, excluding genomes/; its list
#                        is in text_bundle.list and anything skipped is in text_bundle.skipped
#   headers.tsv          for every FASTA/alignment-like file: n_records, n_columns if aligned,
#                        first header, whether any header carries '|rescued'
#   grep_hits.tsv        lines in scripts/logs naming mafft|iqtree|raxml|FastTree|trimal|
#                        clipkit|hmmalign|hmmbuild|epa-ng|pplacer|RT0|RT7|extract
#   DONE                 written last; its absence means the audit did not finish
# ============================================================================
set -euo pipefail
ROOT=${ROOT:-/ibex/project/c2366/RETRONS/Mestre_replication}
OUT=${OUT:-$HOME/m1_ibex_mestre_audit_$(date +%Y%m%d)}
HASH_MAX_BYTES=${HASH_MAX_BYTES:-4294967296}   # 4 GiB
TEXT_MAX_BYTES=${TEXT_MAX_BYTES:-52428800}     # 50 MiB
TEXT_TOTAL_MAX=${TEXT_TOTAL_MAX:-2147483648}   # 2 GiB for the whole text bundle
NPROC=${SLURM_CPUS_PER_TASK:-8}
mkdir -p "$OUT"
[ -d "$ROOT" ] || { echo "ROOT NOT FOUND: $ROOT" | tee "$OUT/ROOT_NOT_FOUND"; exit 2; }

{ echo "host=$(hostname)"; echo "date=$(date -Is)"; echo "root=$ROOT"; echo "user=$(id -un)"
  v=$(sha256sum --version 2>/dev/null) || true; echo "${v%%$'\n'*}"   # no pipe: `| head` SIGPIPEs under pipefail (Ibex job 52089097, exit 13)
  for t in mafft iqtree iqtree2 iqtree3 raxml-ng raxmlHPC FastTree trimal clipkit hmmalign hmmbuild epa-ng pplacer python3; do
    p=$(command -v $t 2>/dev/null || true); echo "tool $t ${p:-ABSENT}"; done; } > "$OUT/env.txt"

# 1. inventory (files, dirs, symlinks); hashing in parallel, bounded by size
find "$ROOT" -xdev \( -type f -o -type l -o -type d \) -printf '%y\t%s\t%TY-%Tm-%TdT%TH:%TM:%TS\t%p\n' \
  | LC_ALL=C sort -t$'\t' -k4,4 > "$OUT/objects.tsv"
awk -F'\t' '$1=="f"{print $4}' "$OUT/objects.tsv" > "$OUT/files.list"
hash_one() { f=$1; s=$(stat -c %s "$f" 2>/dev/null || echo -1)
  if [ "$s" -lt 0 ]; then printf 'UNREADABLE\t%s\n' "$f"
  elif [ "$s" -gt "$HASH_MAX_BYTES" ]; then printf 'SKIPPED_SIZE\t%s\n' "$f"
  else h=$(sha256sum -- "$f" 2>/dev/null | cut -c1-64) || h=UNREADABLE; printf '%s\t%s\n' "${h:-UNREADABLE}" "$f"; fi; }
export -f hash_one; export HASH_MAX_BYTES
tr '\n' '\0' < "$OUT/files.list" | xargs -0 -n 1 -P "$NPROC" bash -c 'hash_one "$0"' | LC_ALL=C sort -t$'\t' -k2,2 > "$OUT/hashes.tsv"
LC_ALL=C join -t$'\t' -1 4 -2 2 -a 1 -e NA -o 1.1,1.2,1.3,2.1,1.4 \
  <(LC_ALL=C sort -t$'\t' -k4,4 "$OUT/objects.tsv") "$OUT/hashes.tsv" \
  | awk -F'\t' 'BEGIN{OFS="\t"; print "type","bytes","mtime","sha256","path"} {print}' > "$OUT/inventory.tsv"

# 2. per-directory summary (depth <= 4)
find "$ROOT" -xdev -mindepth 0 -maxdepth 4 -type d | while read -r d; do
  n=$(find "$d" -xdev -type f | wc -l); b=$(du -sb "$d" 2>/dev/null | cut -f1)
  printf '%s\t%s\t%s\n' "$n" "$b" "$d"; done | awk 'BEGIN{print "n_files\tbytes\tdir"}{print}' > "$OUT/dirs.tsv"

# 3. text-like copy bundle (excluding genomes/)
TXT_RE='\.(py|sh|slurm|sbatch|pl|R|r|smk|nf|ipynb|log|out|err|txt|tsv|csv|json|yaml|yml|md|nwk|newick|tre|tree|treefile|iqtree|contree|mldist|bionj|ckp|afa|aln|fa|fas|fasta|faa|fna|sto|stk|phy|phylip|hmm|cm|jplace|list|ids)$'
# Every file is HASHED (step 1). The COPY bundle may skip bulky per-terminal outputs via
# BUNDLE_EXCLUDE_RE, but paths matching BUNDLE_FORCE_RE are always copied. Both are recorded
# in env.txt, so the choice is visible.
BUNDLE_EXCLUDE_RE=${BUNDLE_EXCLUDE_RE:-/genomes/}
BUNDLE_FORCE_RE=${BUNDLE_FORCE_RE:-^\$NEVER}
printf 'bundle_exclude_re=%s\nbundle_force_re=%s\n' "$BUNDLE_EXCLUDE_RE" "$BUNDLE_FORCE_RE" >> "$OUT/env.txt"
awk -F'\t' -v re="$TXT_RE" -v ex="$BUNDLE_EXCLUDE_RE" -v fo="$BUNDLE_FORCE_RE" \
  'NR>1 && $1=="f" && tolower($5) ~ re && ($5 !~ ex || $5 ~ fo) {print $2"\t"$5}' "$OUT/inventory.tsv" \
  | LC_ALL=C sort -t$'\t' -k2,2 > "$OUT/text_candidates.tsv"
awk -F'\t' -v m="$TEXT_MAX_BYTES" -v T="$TEXT_TOTAL_MAX" -v L="$OUT/text_bundle.list" -v S="$OUT/text_bundle.skipped" \
  '{ if ($1>m) {print "OVER_FILE_MAX\t"$1"\t"$2 > S} else if (tot+$1>T) {print "OVER_TOTAL_MAX\t"$1"\t"$2 > S} else {tot+=$1; print $2 > L} }' \
  "$OUT/text_candidates.tsv"
touch "$OUT/text_bundle.list" "$OUT/text_bundle.skipped"
tar -czf "$OUT/text_bundle.tar.gz" --absolute-names -T "$OUT/text_bundle.list"

# 4. FASTA / alignment headers (answers: are there RT0-RT7 extracts? substitutes inside?)
printf 'path\tn_records\tn_columns_if_aligned\tfirst_header\tany_rescued_header\n' > "$OUT/headers.tsv"
grep -Ei '\.(afa|aln|fa|fas|fasta|faa|sto|stk|phy|phylip)$' "$OUT/text_bundle.list" | while read -r f; do
  awk -v f="$f" 'BEGIN{n=0;L=-1;ok=1;h="";r="N"} /^>/{n++; if(n==1)h=$0; if($0~/\|rescued/)r="Y"; if(s!=""){ if(L<0)L=length(s); else if(length(s)!=L) ok=0}; s=""; next} {gsub(/[ \r]/,""); s=s $0}
       END{ if(s!=""){ if(L<0)L=length(s); else if(length(s)!=L) ok=0}; printf "%s\t%d\t%s\t%s\t%s\n", f, n, (ok&&n>1?L:"NA"), h, r }' "$f" >> "$OUT/headers.tsv" || true
done

# 5. method grep over scripts and logs
grep -Ein 'mafft|iqtree|raxml|fasttree|trimal|clipkit|hmmalign|hmmbuild|epa-ng|pplacer|\bRT0|\bRT7|RT0-7|RT0.RT7|extract' \
  $(grep -Ei '\.(py|sh|slurm|sbatch|pl|R|smk|nf|log|out|err|md|txt)$' "$OUT/text_bundle.list") 2>/dev/null \
  | cut -c1-400 > "$OUT/grep_hits.tsv" || true

( cd "$OUT" && sha256sum inventory.tsv dirs.tsv env.txt text_bundle.tar.gz headers.tsv grep_hits.tsv > SHA256SUMS )
date -Is > "$OUT/DONE"
echo "M1 Ibex inventory complete: $OUT"; wc -l "$OUT/inventory.tsv" "$OUT/text_bundle.list" "$OUT/text_bundle.skipped"
