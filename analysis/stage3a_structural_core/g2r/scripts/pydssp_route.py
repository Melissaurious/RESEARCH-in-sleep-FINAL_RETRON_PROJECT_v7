#!/usr/bin/env python3
"""g2r secondary-structure route B: pydssp 0.9.1 (numpy backend), run in env `opencrispr_retrons`.

Input : backbone TSV written by ss_routes.py in canonical order with NaN spacer rows at every chain break and
        NaN rows for incomplete-backbone residues (R2 B4); `real` = 1 marks rows to report; `donor_ok` = 0 for
        Pro. pydssp is used unmodified; NaN geometry yields no H-bond.
Output: TSV  idx  B_ss3   (B_ss3 in {H, E, C}; pydssp's helix = 3/4/5-turn helices, strand = any bridge,
        i.e. the same partition as mkdssp {H,G,I} / {E,B} / rest).
Usage : pydssp_route.py <backbone.tsv> <out.tsv>
"""
import sys
import numpy as np
np.seterr(all="ignore")
import pydssp
from pydssp import pydssp_numpy

inp, out = sys.argv[1], sys.argv[2]
rows = [l.rstrip("\n").split("\t") for l in open(inp)]
hdr, rows = rows[0], rows[1:]
ix = {h: i for i, h in enumerate(hdr)}
coord = np.array([[[float(r[ix[f"{a}_{c}"]]) for c in "xyz"] for a in ("N", "CA", "C", "O")] for r in rows])
donor = np.array([int(r[ix["donor_ok"]]) for r in rows], dtype=float)
onehot = pydssp_numpy.assign(coord, donor_mask=donor)
ss = np.array(["C", "H", "E"])[onehot.argmax(-1)]
with open(out, "w") as fh:
    fh.write("idx\tB_ss3\n")
    for r, s in zip(rows, ss):
        if r[ix["real"]] == "1":
            fh.write(f"{r[ix['idx']]}\t{s}\n")
