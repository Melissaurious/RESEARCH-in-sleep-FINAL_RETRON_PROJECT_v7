#!/usr/bin/env python3
"""Audit positive control (agent_v4): apply the s7i-style criterion (unrooted smallest side containing
all clade members; purity>=0.90; support) to Mestre's PUBLISHED newick, which carries ONE support
value per node. Reports purity + support; recovered at support>=95 and at >=85 (Mestre's threshold)."""
import csv, collections, sys
from ete3 import Tree
M = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/supporting_material/"
rows = list(csv.DictReader(open(M+"supp_material_systematic_prediction_paper.csv", encoding="utf-8-sig")))
clade = {(r["Accesion"] or "").strip(): (r["RT_Clade"] or "").strip() for r in rows}
t = Tree(M+"Supplementary_mestre_Tree.nwk", format=0)
alltips = frozenset(t.get_leaf_names()); N = len(alltips)
edges = [(frozenset(n.get_leaf_names()), n.support) for n in t.traverse() if not n.is_leaf() and not n.is_root()]
byc = collections.defaultdict(set)
for l in alltips:
    c = clade.get(l, "")
    if c and c != "Orphan": byc[c].add(l)
w = csv.writer(sys.stdout, delimiter="\t")
w.writerow(["tree","n_tips","clade","n","unrooted_min_side","purity","support","rec_at95","rec_at85"])
k95 = k85 = 0
for c in sorted(byc, key=lambda x: (len(x), x)):
    mem = byc[c]; best = (N, float("nan"))
    for side, s in edges:
        for S in (side, alltips - side):
            if mem <= S and len(S) < best[0]: best = (len(S), s)
    pur = len(mem)/best[0]
    r95 = pur >= .9 and best[1] >= 95; r85 = pur >= .9 and best[1] >= 85
    k95 += r95; k85 += r85
    w.writerow(["published", N, c, len(mem), best[0], f"{pur:.3f}", best[1], r95, r85])
w.writerow(["published", N, "TOTAL", "", "", "", "", f"{k95}/{len(byc)}", f"{k85}/{len(byc)}"])
