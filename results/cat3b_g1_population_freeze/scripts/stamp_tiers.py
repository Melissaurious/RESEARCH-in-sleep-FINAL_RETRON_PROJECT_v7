#!/usr/bin/env python3
"""Add group class, tier and truth_source to a scanned truth table. Deterministic."""
import csv, sys, collections
RANK={"HARD_PAIR":4,"FUNCTIONAL_PAIR":3,"HARD_SINGLE":2,"AUTHOR_PAIR":2,
      "HARD_MULTISITE_UNRESOLVED":1,"WEAK":1,"NONE":0}
p=sys.argv[1]
tt=list(csv.DictReader(open(p),delimiter="\t"))
g=collections.defaultdict(list)
for r in tt: g[r["replicate_group"]].append(r)
gcls={}
for rg,ms in g.items():
    if any(m["S_class"]=="HARD_MULTISITE_UNRESOLVED" for m in ms):
        gcls[rg]="HARD_MULTISITE_UNRESOLVED"; continue
    best=max(ms,key=lambda m:RANK.get(m["S_class"],0))["S_class"]
    if any(m["F_mutational"]=="YES" for m in ms) and RANK[best]<RANK["FUNCTIONAL_PAIR"]:
        best="FUNCTIONAL_PAIR"
    gcls[rg]=best
cl=collections.defaultdict(set)
for r in tt: cl[r["relatedness_cluster_30pct"]].add(r["replicate_group"])
tier={c:("A_calibration" if max(RANK[gcls[x]] for x in rgs)==4 else
         ("B_heldout" if max(RANK[gcls[x]] for x in rgs)>=2 else "C_no_truth_yet"))
      for c,rgs in cl.items()}
for r in tt:
    r["group_evidence_class"]=gcls[r["replicate_group"]]
    r["tier"]=tier[r["relatedness_cluster_30pct"]]
    r["truth_source"]=("OWN_CHAIN" if r["S_catalytic_asp"] else
        ("TRANSFERRED_WITHIN_REPLICATE_GROUP" if any(x["S_catalytic_asp"] for x in g[r["replicate_group"]]) else "NONE"))
hdr=list(tt[0].keys())
with open(p,"w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=hdr,delimiter="\t",lineterminator="\n"); w.writeheader(); w.writerows(tt)
print("tiers stamped:", {k:sum(1 for r in tt if r['tier']==k) for k in sorted(set(tier.values()))})
