#!/usr/bin/env python3
"""M2a step 5b — which of the 11 historical clades are reproducibly recovered?

Trees compared:
  published       Supplementary_mestre_Tree.nwk, all 1,928 tips (one support value per node)
  V4_<tag> x6     the recovered contaminated V4 re-inferences, reused as comparators and NOT
                  recomputed (K0_FIRED_RESOLVED_COMPARATOR_ONLY); 1,843 tips, labels 'SH/UFB'
  clean_v3        the clean MCC-v3.1 reconstruction (IQ-TREE LG+F+R10), if present
Per tree and clade (evaluation labels):
  n_present, exact_unrooted_split, best_jaccard (the max over both sides of every edge),
  support_at_best_split. A clade counts as "recovered" when an exact unrooted split exists.
  "purity>=0.9" uses best_jaccard >= 0.9. Support thresholds are REPORTED, not used to
  recount: the historical 10/11, 9/10, <=3/11 and 4-6/11 figures are reconciled from their
  own producing tables (see RECONCILIATION).
"""
import glob, os, re
import pandas as pd
from ete3 import Tree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references/rt0_rt7/mestre_2020"
V4 = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/mestre_trees"
mt = pd.read_csv(f"{REF}/Supp_material_T1_R1_systematic_prediction.csv", encoding="utf-8-sig")
mt = mt[mt.Node.notna()].copy(); mt["Node"] = mt.Node.astype(int); mt["Clade"] = mt.Clade.astype(str)
short = mt.Retron_name.astype(str).str.extract(r"\(([^)]+)\)")[0]
clade_by = {}
for a, s, n, c in zip(mt.Accesion.astype(str).str.strip(), short, mt.Node, mt.Clade):
    clade_by[a] = c; clade_by[f"terminal_{n}"] = c; clade_by[f"n{n}"] = c
    if isinstance(s, str):
        clade_by[s] = c


def load(path, fmt=1):
    t = Tree(path, format=fmt, quoted_node_names=True)
    t.unroot()
    return t


def analyse(name, t):
    leaves = {l.name for l in t.get_leaves()}
    lab = {x: clade_by.get(x) for x in leaves}
    splits = []
    for n in t.traverse():
        if n.is_leaf() or n.is_root():
            continue
        side = {l.name for l in n.get_leaves()}
        splits.append((side, leaves - side, n.name))
    rows = []
    for c in [str(i) for i in range(1, 12)]:
        C = {x for x, v in lab.items() if v == c}
        if not C:
            rows.append(dict(tree=name, clade=c, n_present=0)); continue
        best, bsup, exact = 0.0, "", False
        for a, b, sup in splits:
            for s in (a, b):
                j = len(s & C) / len(s | C)
                if j > best:
                    best, bsup = j, sup
                if s == C:
                    exact = True
        rows.append(dict(tree=name, clade=c, n_present=len(C), exact_unrooted_split=exact or len(C) == 1,
                         best_jaccard=round(best, 4), support_at_best_split=bsup))
    return rows


rows = analyse("published", load(f"{REF}/Supplementary_mestre_Tree.nwk"))
for f in sorted(glob.glob(f"{V4}/*.treefile")):
    rows += analyse("V4_" + os.path.basename(f).split(".")[0], load(f))
for f in sorted(glob.glob(f"{ROOT}/tree/clean_*.treefile")):
    rows += analyse(os.path.basename(f).split(".")[0], load(f))
D = pd.DataFrame(rows)
os.makedirs(f"{ROOT}/eval", exist_ok=True)
D.to_csv(f"{ROOT}/eval/TREE_COMPARISON_per_clade.tsv", sep="\t", index=False)
S = D.groupby("tree").agg(clades_present=("n_present", lambda x: int((x > 0).sum())),
                          exact_splits=("exact_unrooted_split", lambda x: int(x.fillna(False).sum())),
                          purity_ge_0_9=("best_jaccard", lambda x: int((x >= 0.9).sum())))
S.to_csv(f"{ROOT}/eval/TREE_COMPARISON_summary.tsv", sep="\t")
print(S.to_string())
print(D.pivot(index="clade", columns="tree", values="best_jaccard").to_string())
