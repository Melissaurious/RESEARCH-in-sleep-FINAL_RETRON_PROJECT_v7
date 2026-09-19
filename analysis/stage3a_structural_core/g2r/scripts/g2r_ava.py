#!/usr/bin/env python3
"""g2r (F7): re-run the g2 all-vs-all with identical search parameters, adding the columns C6/EXTRA_DOMAIN need
(qtmscore, ttmscore, qlen, tlen), from the durable chain extracts. The alignment itself must be identical to
the pinned g2 table (tables/g2_foldseek_ava.tsv, sha256 46428e07...); this is checked and reported.

Usage: g2r_ava.py <chain_dir> <g2_table> <out.tsv>
"""
import sys, os, subprocess, tempfile

FOLDSEEK = "/home/borg/miniconda3/envs/esmologs/bin/foldseek"
cdir, g2, out = sys.argv[1:4]
COLS = "query,target,qstart,qend,tstart,tend,qaln,taln,alntmscore,lddt,alnlen,qtmscore,ttmscore,qlen,tlen"
with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
    o = os.path.join(tmp, "ava.tsv")
    subprocess.run([FOLDSEEK, "easy-search", cdir, cdir, o, os.path.join(tmp, "t"),
                    "--alignment-type", "1", "-e", "inf", "--exhaustive-search", "1", "--tmscore-threshold", "0.0",
                    "--max-seqs", "200", "--format-output", COLS, "-v", "1"], check=True, capture_output=True, text=True)
    new = [l.rstrip("\n").split("\t") for l in open(o)]
with open(out, "w") as fh:
    fh.write("\t".join(COLS.split(",")) + "\n")
    for r in new:
        r[0], r[1] = r[0].replace(".pdb", ""), r[1].replace(".pdb", "")
        fh.write("\t".join(r) + "\n")
old = {(r[0], r[1]): r[2:8] for r in (l.rstrip("\n").split("\t") for l in open(g2))}
newk = {(r[0], r[1]): r[2:8] for r in new}
same = sum(1 for k in old if k in newk and newk[k] == old[k])
print(f"rows g2={len(old)} g2r={len(newk)}; identical alignments (start/end/aln strings): {same}/{len(old)}")
