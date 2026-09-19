#!/usr/bin/env python3
"""s1b - header scan: files whose record names resolve to Mestre terminals / published tip accessions.
Catches column-trimmed alignments that a k-mer content scan misses. Read-only."""
import os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load_mestre, build_index
from s1_scan import ROOTS, EXT, MAXBYTES
OUT = Path(__file__).resolve().parents[1]
ref, _ = load_mestre(); _, by_name = build_index(ref)
tips = set(re.findall(r"[(,]([^():,;]+):", open("/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/Supplementary_mestre_Tree.nwk").read()))
names = set(by_name) | tips
term = re.compile(rb"^(>|)terminal_\d+")
rows = []
for root in ROOTS:
    for dp, dn, fn in os.walk(root):
        if "/.git" in dp or "/Mestre_sequences/terminal_" in dp: continue
        for f in fn:
            if not (f.lower().endswith(EXT) or f.endswith(".phy")): continue
            p = Path(dp) / f
            try:
                if p.is_symlink() or p.stat().st_size == 0 or p.stat().st_size > MAXBYTES or f.endswith(".gz"): continue
                n = hit = 0; seen = set()
                with open(p, "rb") as fh:
                    for line in fh:
                        if line.startswith(b">"):
                            nm = line[1:].split()[0].decode(errors="replace") if line[1:].split() else ""
                        elif f.endswith((".sto",)) and line[:1] not in (b"#", b"/", b"\n", b" "):
                            nm = line.split()[0].decode(errors="replace")
                            if nm in seen: continue
                        else: continue
                        seen.add(nm); n += 1
                        if nm.startswith("terminal_") or nm in names or nm.split("|rescued")[0] in names: hit += 1
                if hit >= 50: rows.append((str(p), n, hit))
            except Exception as e:
                print("ERR", p, e, file=sys.stderr)
with open(OUT / "header_scan_hits.tsv", "w") as fh:
    fh.write("path\tn_records\tn_mestre_named\n")
    for r in sorted(rows): fh.write("\t".join(map(str, r)) + "\n")
print(len(rows))
