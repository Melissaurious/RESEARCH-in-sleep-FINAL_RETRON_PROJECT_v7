#!/usr/bin/env python3
"""Audit re-measurement (agent_v4): root-independent version of V4 s7i clade recovery.
s7i uses ete3 get_common_ancestor on IQ-TREE's arbitrarily rooted treefile. Here, for each clade,
find over all edges of the UNROOTED tree the smallest side that contains ALL clade members
(= unrooted 'MRCA'), and report purity and SH-aLRT/UFBoot of that edge. Same thresholds as s7i
(purity>=0.90, UFBoot>=95, SH-aLRT>=80, n>=4). Read-only on V4 inputs."""
import csv, re, collections, sys
from pathlib import Path
from ete3 import Tree
V4 = Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT")
FA = V4/"rt0_rt7_domain_test/cache/mestre_from_V3/mestre_1926_proteins.faa"
IDX = V4/"rt0_rt7_domain_test/cache/mestre_usable_index.tsv"
TD = V4/"rt0_rt7_domain_test_v4_and_tree/cache/mestre_trees"
term2acc = {}
for l in open(FA):
    if l[0] == ">":
        p = l[1:].strip().split("|"); term2acc[p[0]] = "|".join(p[2:])
acc2clade = {r["accession"]: r["clade"].strip() for r in csv.DictReader(open(IDX), delimiter="\t")}
term2clade = {t: acc2clade[a] for t, a in term2acc.items() if a in acc2clade}
out = csv.writer(sys.stdout, delimiter="\t")
out.writerow(["tree","root_tip_side","clade","n","unrooted_min_side","purity","shalrt","ufboot","recovered_unrooted","s7i_style_note"])
for frame in ("ours","toro","wide","narrow","fftnsi","linsi"):
    s = open(TD/f"{frame}.treefile").read()
    pairs = {}
    s2 = s
    t = Tree(re.sub(r"\)([0-9.]+)/([0-9.]+):", lambda m: ")"+m.group(1)+"_"+m.group(2)+":", s), format=1)
    alltips = frozenset(t.get_leaf_names())
    N = len(alltips)
    edges = []
    for nd in t.traverse():
        if nd.is_leaf() or nd.is_root(): continue
        a, b = (nd.name.split("_") + ["nan"])[:2] if nd.name else ("nan","nan")
        side = frozenset(nd.get_leaf_names())
        edges.append((side, float(a), float(b)))
    first_child_tips = [l.name for l in t.children[0]] if t.children else []
    byc = collections.defaultdict(set)
    for tip, c in term2clade.items():
        if tip in alltips: byc[c].add(tip)
    ok = 0
    for c in sorted(byc, key=lambda x:(len(x),x)):
        mem = byc[c]
        if len(mem) < 4 or c == "Orphan": continue
        best = (N, float("nan"), float("nan"))
        for side, a, b in edges:
            for S in (side, alltips - side):
                if mem <= S and len(S) < best[0]:
                    best = (len(S), a, b)
        size, a, b = best
        pur = len(mem)/size
        good = pur >= 0.90 and b >= 95 and a >= 80
        ok += good
        out.writerow([frame, "", c, len(mem), size, f"{pur:.3f}", a, b, "RECOVERED" if good else "no", ""])
    out.writerow([frame, "", "TOTAL", "", "", "", "", "", f"{ok}/11", ""])
