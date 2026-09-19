#!/usr/bin/env python3
"""g2r amendment 1 §1.3: primary vs BJ-p4 partition agreement per chain.
IMPLEMENTATION_SENSITIVE if domain counts differ or the Hungarian overlap (over residues present in both
tables) < 0.85. Label-0 residues match nothing.

Usage: pdp_compare.py <primary_prefix> <p4_prefix> <out.tsv>
"""
import sys, csv, collections
import numpy as np
from scipy.optimize import linear_sum_assignment

a_p, b_p, out = sys.argv[1:4]


def load(p):
    s = {r["chain"]: r for r in csv.DictReader(open(p + ".summary.tsv"), delimiter="\t")}
    L = collections.defaultdict(dict)
    for r in csv.DictReader(open(p + ".residues.tsv"), delimiter="\t"):
        L[r["chain"]][(r["resnum"], r["icode"])] = int(r["domain"])
    return s, L


sa, la = load(a_p); sb, lb = load(b_p)
rows = []
for c in sorted(sa):
    na, nb = sa[c]["n_domains"], sb[c]["n_domains"] if c in sb else "NA"
    keys = sorted(set(la[c]) & set(lb[c]))
    da = sorted({la[c][k] for k in keys} - {0}); db = sorted({lb[c][k] for k in keys} - {0})
    M = np.zeros((max(1, len(da)), max(1, len(db))))
    for k in keys:
        x, y = la[c][k], lb[c][k]
        if x and y: M[da.index(x), db.index(y)] += 1
    ri, ci = linear_sum_assignment(-M)
    ov = M[ri, ci].sum() / len(keys) if keys else 0.0
    sens = int(na != nb or ov < 0.85)
    rows.append(dict(chain=c, n_primary=na, n_p4=nb, overlap=round(float(ov), 4), IMPLEMENTATION_SENSITIVE=sens))
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(rows)
print("IMPLEMENTATION_SENSITIVE:", sum(r["IMPLEMENTATION_SENSITIVE"] for r in rows), "/", len(rows),
      [r["chain"] for r in rows if r["IMPLEMENTATION_SENSITIVE"]])
