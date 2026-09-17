#!/usr/bin/env python3
"""REPAIR 4 - hhmake -M is an IMPLEMENTATION CHOICE, not a default (HHmake's documented
default is -M a2m). It controls match states and therefore the frozen frame, so its effect
on the supported intersection is measured. -M 50 remains primary regardless of the outcome."""
import sys, os, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from repaired_lib import *          # noqa
WORK, TABLES = sys.argv[1], sys.argv[2]
FAMILIES = ["Retrons","GII","DGRs","CRISPR","UG3","UG5","AbiA"]
rows = []
for M in ("50", "60", "a2m"):
    tag = f"M{M}"
    for f in FAMILIES:
        run([BIN+"hhmake", "-i", f"{WORK}/{f}.deriv.mafft.afa",
             "-o", f"{WORK}/{f}.{tag}.hhm", "-name", f"g4a_{f}_{tag}", "-M", M])
    pm = {}
    for a, b in itertools.permutations(FAMILIES, 2):
        o = f"{WORK}/sens_{tag}_{a}__{b}.hhr"
        run([BIN+"hhalign", "-i", f"{WORK}/{a}.{tag}.hhm", "-t", f"{WORK}/{b}.{tag}.hhm", "-o", o])
        m = pair_map(o)
        if m: pm[(a,b)] = m
    for a in FAMILIES:
        sup = collections.Counter()
        for b in FAMILIES:
            if a != b and (a,b) in pm:
                for q in pm[(a,b)]: sup[q] += 1
        n_other = sum(1 for b in FAMILIES if b != a and (a,b) in pm)
        allp = sum(1 for v in sup.values() if v == n_other)
        leng = 0
        for ln in open(f"{WORK}/{a}.{tag}.hhm"):
            if ln.startswith("LENG"): leng = int(ln.split()[1]); break
        rows.append([M, a, str(leng), str(len(sup)), str(allp),
                     f"{100*allp/len(sup):.1f}" if sup else "",
                     f"{100*allp/leng:.1f}" if leng else ""])
with open(f"{TABLES}/g4a_hhmake_M_sensitivity.tsv", "w") as fh:
    fh.write("hhmake_M\tfamily\tfull_consensus_LENG\tn_covered\tn_ALL_PARTNERS\t"
             "pct_of_covered\tpct_of_full_consensus\n")
    for r in rows: fh.write("\t".join(r)+"\n")
for M in ("50","60","a2m"):
    v = [float(r[6]) for r in rows if r[0]==M and r[6]]
    c = [float(r[5]) for r in rows if r[0]==M and r[5]]
    print(f"-M {M:4s}  pct_of_full_consensus {min(v):.1f}-{max(v):.1f}   pct_of_covered {min(c):.1f}-{max(c):.1f}")
