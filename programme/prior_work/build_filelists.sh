#!/usr/bin/env bash
# PRIOR_WORK_LOOKUP -- step 1: bounded file lists, one per registered root.
#
# Bounded on purpose.  The evidence estate is 155.6 GB, and one root alone holds
# 738k text-ish files; an unbounded content sweep is not the "lookup of seconds"
# TASK_PROTOCOL step 2 describes, and would not finish.  The bound is declared
# here so the sweep's blind spots are auditable rather than accidental:
#
#   - text-bearing extensions only (.md .py .sh .R .tex .txt .json .tsv .csv .yml .ipynb)
#   - .tsv/.csv capped at 40 MB so one multi-GB table cannot dominate the sweep
#   - no .git, no __pycache__, no node_modules, no site-packages, no conda envs
#   - the largest root is capped at depth 6, which covers its docs/scripts/reports
#     and excludes its per-record data leaves
#
# A directory-NAME index is built alongside, because in this estate what was
# computed is encoded in directory names, and those leaves are excluded above.
set -uo pipefail
OUT="${1:?usage: build_filelists.sh <outdir>}"
mkdir -p "$OUT"

sweep () {  # sweep <root> <maxdepth>
  local root="$1" depth="$2" tag
  tag="$(basename "$root")"
  if [ ! -d "$root" ]; then
    echo "MISSING $root" >&2
    : > "$OUT/$tag.files"; : > "$OUT/$tag.dirs"; return
  fi
  timeout 900 find "$root" -maxdepth "$depth" \
      \( -name .git -o -name __pycache__ -o -name node_modules \
         -o -name .ipynb_checkpoints -o -name site-packages \
         -o -name conda-environments \) -prune -o \
      -type f \( -name '*.md' -o -name '*.py' -o -name '*.sh' -o -name '*.R' \
                 -o -name '*.r' -o -name '*.tex' -o -name '*.txt' \
                 -o -name '*.json' -o -name '*.tsv' -o -name '*.csv' \
                 -o -name '*.yaml' -o -name '*.yml' -o -name '*.ipynb' \) \
      -size -40M -print 2>/dev/null > "$OUT/$tag.files"
  timeout 600 find "$root" -maxdepth "$depth" \
      \( -name .git -o -name __pycache__ -o -name node_modules \
         -o -name site-packages -o -name conda-environments \) -prune -o \
      -type d -print 2>/dev/null > "$OUT/$tag.dirs"
  printf '%-46s %8d files %8d dirs\n' "$tag" \
      "$(wc -l < "$OUT/$tag.files")" "$(wc -l < "$OUT/$tag.dirs")"
}

sweep /home/borg/RETRONS_january_2026                                       6
sweep /home/borg/RESEARCH-in-sleep-RETRON-DB_V4                            12
sweep /home/borg/RESEARCH-in-sleep-RETRON-DB_V3                            12
sweep /home/borg/RESEARCH-in-sleep-RETRON-DB_V2                            12
sweep /home/borg/RESEARCH-in-sleep-RETRON-DB                               12
sweep /home/borg/RESEARCH-in-sleep-RETRON-DB_V5                            12
sweep /home/borg/RESEARCH-retron-db                                        12
sweep /home/borg/RETRON_STAGES                                              4
sweep /home/borg/JUNE_RETRONS                                               4
sweep /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7                 12
sweep /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings      12
sweep /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-spire-ncrna     12
sweep /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-mestre-audit    12
sweep /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-stage3c         12
sweep /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit     12
sweep /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-dbchar-workbench 12
sweep /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embedding-report 12
