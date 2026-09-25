#!/usr/bin/env python3
"""Compare an Ibex Mestre inventory (from ibex_mestre_inventory.sh) against borg.

For each Ibex file this assigns:
  identity    COPY_ON_BORG (same sha256 at >= 1 borg path; paths listed) | IBEX_ONLY |
              NOT_HASHED (SKIPPED_SIZE / UNREADABLE on the Ibex side)
  category    script | alignment | tree | sequence | hmm_cm | log | table | genome | other
  relevance   TREE_REINFERENCE_INPUT_CANDIDATE (aligned sequence file or tree product) |
              RT0_RT7_EXTRACTION_LOGIC_CANDIDATE (script or log whose grep hits name
              hmmalign/hmmbuild/extract/RT0/RT7) | PLACEMENT_LOGIC_CANDIDATE | -
A COPY_ON_BORG file adds no independent evidence: the finding it supports is the finding
already recorded for its borg twin. Only IBEX_ONLY files can add anything new.

Borg index: size-first. Only borg files whose byte size equals some Ibex file's size are
hashed, so the comparison is exact and still cheap. Roots searched are declared in BORG_ROOTS.

usage: m05_compare_ibex_inventory.py <ibex_out_dir> <report.tsv>
"""
import csv, hashlib, os, re, sys
from collections import defaultdict

BORG_ROOTS = ["/home/borg/RESEARCH-retron-db", "/home/borg/RESEARCH-in-sleep-RETRON-DB_V2",
              "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3", "/home/borg/RESEARCH-in-sleep-RETRON-DB_V4",
              "/home/borg/RESEARCH-in-sleep-RETRON-DB_V5", "/home/borg/RETRONS_january_2026/the-retron-project",
              "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA",
              "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references"]
CAT = [("genome", r"/genomes?/|genome\.fasta"), ("script", r"\.(py|sh|slurm|sbatch|pl|r|smk|nf|ipynb)$"),
       ("tree", r"\.(nwk|newick|tre|tree|treefile|contree|iqtree|jplace)$"),
       ("alignment", r"\.(afa|aln|sto|stk|phy|phylip)$"), ("sequence", r"\.(fa|fas|fasta|faa|fna)(\.gz)?$"),
       ("hmm_cm", r"\.(hmm|cm|h3[fimp])$"), ("log", r"\.(log|out|err)$"), ("table", r"\.(tsv|csv|txt|json|ya?ml|list|ids)$")]
EXTRACT = re.compile(r"hmmalign|hmmbuild|extract|\bRT0|\bRT7|RT0.?-?.?7", re.I)
PLACE = re.compile(r"epa-ng|pplacer|raxml|--mapali|guppy|gappa", re.I)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main(ibex_dir, out):
    inv = [r for r in csv.DictReader(open(f"{ibex_dir}/inventory.tsv"), delimiter="\t") if r["type"] == "f"]
    headers = {r["path"]: r for r in csv.DictReader(open(f"{ibex_dir}/headers.tsv"), delimiter="\t")}
    grep_files = defaultdict(set)
    for line in open(f"{ibex_dir}/grep_hits.tsv", errors="replace"):
        path, _, rest = line.partition(":")
        grep_files[path].add(rest)
    sizes = {int(r["bytes"]) for r in inv if r["sha256"] not in ("SKIPPED_SIZE", "UNREADABLE", "NA")} - {0}
    index = defaultdict(list)
    for root in BORG_ROOTS:
        for d, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs if x != ".git"]
            for f in files:
                p = os.path.join(d, f)
                try:
                    if os.path.islink(p) or os.path.getsize(p) not in sizes:
                        continue
                    index[sha(p)].append(p)
                except OSError:
                    continue
    w = csv.writer(open(out, "w", newline=""), delimiter="\t", lineterminator="\n")
    w.writerow(["ibex_path", "bytes", "mtime", "sha256", "identity", "n_borg_copies", "borg_copies", "category",
                "relevance", "n_records", "n_columns_if_aligned", "any_rescued_header"])
    tally = defaultdict(int)
    for r in inv:
        p, h = r["path"], r["sha256"]
        ident = "NOT_HASHED" if h in ("SKIPPED_SIZE", "UNREADABLE", "NA") else ("COPY_ON_BORG" if index.get(h) else "IBEX_ONLY")
        if r["bytes"] == "0":
            ident = "EMPTY_FILE"  # an empty file "matches" every empty file; that is not identity evidence
        cat = next((c for c, rx in CAT if re.search(rx, p, re.I)), "other")
        hd = headers.get(p, {})
        rel = "-"
        if cat == "tree" or (cat in ("alignment", "sequence") and hd.get("n_columns_if_aligned", "NA") not in ("NA", "")):
            rel = "TREE_REINFERENCE_INPUT_CANDIDATE"
        if cat in ("script", "log") and any(EXTRACT.search(x) for x in grep_files.get(p, ())):
            rel = "RT0_RT7_EXTRACTION_LOGIC_CANDIDATE"
        elif cat in ("script", "log") and any(PLACE.search(x) for x in grep_files.get(p, ())):
            rel = "PLACEMENT_LOGIC_CANDIDATE"
        copies = index.get(h, []) if ident == "COPY_ON_BORG" else []
        tally[(ident, rel)] += 1
        w.writerow([p, r["bytes"], r["mtime"], h, ident, len(copies), " | ".join(sorted(copies)[:5]), cat, rel,
                    hd.get("n_records", ""), hd.get("n_columns_if_aligned", ""), hd.get("any_rescued_header", "")])
    for k, v in sorted(tally.items()):
        print(*k, v, sep="\t")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
