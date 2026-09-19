#!/usr/bin/env python3
"""s1 - content scan: which historical sequence files hold Mestre-derived sequences?

For every candidate sequence/alignment file under the historical roots, sample up to 300 records,
ungap them, and score the fraction of their 10-mers present in the Mestre on-disk protein set
(1,926 proteins, clean + rescued). A record with >= 0.9 of its 10-mers in the set is called
Mestre-derived. Files with >= 20 Mestre-derived records are written to scan_hits.tsv.
Read-only against sources.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import load_mestre, read_fasta, read_stockholm, ungap  # noqa: E402

OUT = Path(__file__).resolve().parents[1]
ROOTS = [
    "/home/borg/RESEARCH-in-sleep-RETRON-DB_V2", "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3",
    "/home/borg/RESEARCH-in-sleep-RETRON-DB_V4", "/home/borg/RESEARCH-in-sleep-RETRON-DB_V5",
    "/home/borg/RESEARCH-retron-db", "/home/borg/RETRON_APRIL", "/home/borg/RETRON_3rd_BATCH",
    "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE",
    "/home/borg/RETRONS_january_2026/DATA_FROM_IBEX_PIPELINE/MSA_PIPELINE",
    "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references",
]
EXT = (".fa", ".faa", ".fasta", ".afa", ".aln", ".sto", ".fas", ".a2m", ".fa.gz", ".faa.gz",
       ".fasta.gz", ".sto.gz", ".afa.gz", ".reduced", ".c50", ".c70", ".c80", ".c90", ".c5", ".c7",
       ".c9", ".mafft", ".linsi", ".trim")
K = 10
MAXREC = 300
MAXBYTES = 400 * 1024 * 1024


def head_records(path: Path, n: int):
    """First n records of a FASTA (fast) or all of a Stockholm (must be read whole)."""
    s = str(path)
    if ".sto" in s:
        return read_stockholm(path)[0][:n]
    out, name, buf = [], None, []
    import gzip
    fh = gzip.open(path, "rt") if s.endswith(".gz") else open(path, errors="replace")
    with fh:
        for line in fh:
            line = line.rstrip("\r\n")
            if line.startswith(">"):
                if name is not None:
                    out.append((name, "".join(buf)))
                    if len(out) >= n:
                        return out
                name, buf = line[1:].strip(), []
            elif name is not None:
                buf.append(line.strip())
    if name is not None:
        out.append((name, "".join(buf)))
    return out


def main() -> None:
    ref, _ = load_mestre()
    kmers = set()
    for r in ref.values():
        s = r["seq"]
        kmers.update(s[i:i + K] for i in range(len(s) - K + 1))
    print(f"mestre proteins {len(ref)}  kmers {len(kmers)}", flush=True)
    rows = []
    nfiles = 0
    for root in ROOTS:
        for dp, dn, fn in os.walk(root):
            if "/.git" in dp or "/Mestre_sequences/terminal_" in dp or "__pycache__" in dp:
                continue
            for f in fn:
                if not f.lower().endswith(EXT):
                    continue
                p = Path(dp) / f
                try:
                    if p.is_symlink() or p.stat().st_size == 0 or p.stat().st_size > MAXBYTES:
                        continue
                    recs = head_records(p, MAXREC)
                except Exception as e:  # noqa: BLE001
                    print("ERR", p, e, file=sys.stderr)
                    continue
                nfiles += 1
                hit = 0
                ln = []
                for _h, s in recs:
                    u = ungap(s).rstrip("*")
                    if len(u) < K + 5:
                        continue
                    km = [u[i:i + K] for i in range(len(u) - K + 1)]
                    fr = sum(1 for x in km if x in kmers) / len(km)
                    if fr >= 0.9:
                        hit += 1
                        ln.append(len(u))
                if hit >= 20:
                    ln.sort()
                    rows.append((str(p), len(recs), hit, ln[len(ln) // 2]))
    with open(OUT / "scan_hits.tsv", "w") as fh:
        fh.write("path\tn_sampled\tn_mestre_like\tmedian_ungapped_len\n")
        for r in sorted(rows):
            fh.write("\t".join(map(str, r)) + "\n")
    print(f"scanned {nfiles} files; hits {len(rows)}")


if __name__ == "__main__":
    main()
