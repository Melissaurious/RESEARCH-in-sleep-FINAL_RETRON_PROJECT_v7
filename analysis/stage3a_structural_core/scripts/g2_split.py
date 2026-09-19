#!/usr/bin/env python3
"""Stage 3A g2 step 2 — structural-diversity calibration/held-out split, at the BIOLOGICAL GROUP
level, declared and frozen BEFORE any boundary criterion is fixed. Deterministic, no RNG, no labels.

Rule: group-group structural similarity = max alntmscore between any of their chains.
Single-linkage clustering at TM >= 0.5 (a standard fold-similarity threshold, declared a priori).
Clusters are ordered by (size desc, first member) and every third cluster goes to held-out.
"""
import csv, os, collections, json
ROOT="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit"
OUT=ROOT+"/analysis/stage3a_structural_core"; T=os.environ["TMPDIR"]+"/s3a"
reg=list(csv.DictReader(open(OUT+"/STRUCTURE_REGISTER.tsv"),delimiter="\t"))
grp={f"{r['pdb_id']}_{r['chain']}":r["biological_group"] for r in reg}
best=collections.defaultdict(float)
for l in open(T+"/ava.tsv"):
    p=l.rstrip("\n").split("\t")
    q,t=p[0].replace(".pdb",""),p[1].replace(".pdb","")
    if q not in grp or t not in grp: continue
    gq,gt=grp[q],grp[t]
    if gq==gt: continue
    tm=float(p[8]); k=tuple(sorted((gq,gt)))
    if tm>best[k]: best[k]=tm
TM_LINK=0.50
groups=sorted(set(grp.values()))
par={g:g for g in groups}
def f(x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
for (a,b),tm in best.items():
    if tm>=TM_LINK:
        ra,rb=f(a),f(b)
        if ra!=rb: par[ra]=rb
cl=collections.defaultdict(list)
for g in groups: cl[f(g)].append(g)
clusters=sorted(cl.values(), key=lambda v:(-len(v), sorted(v)[0]))
rows=[]
for i,c in enumerate(clusters):
    tier = "HELD_OUT" if i%3==2 else "CALIBRATION"
    for g in sorted(c):
        rows.append(dict(biological_group=g, structural_cluster=f"SC{i+1:02d}",
                         cluster_size=len(c), split=tier))
info={r["biological_group"]:r for r in rows}
ex={r["biological_group"]:r for r in csv.DictReader(open(OUT+"/BIOLOGICAL_GROUPS.tsv"),delimiter="\t")}
for r in rows:
    e=ex[r["biological_group"]]
    r["n_pdb_entries"]=e["n_pdb_entries"]; r["n_chains"]=e["n_chains"]
    r["lineage_METADATA_ONLY"]=e["lineage_METADATA_ONLY"]; r["family_METADATA_ONLY"]=e["family_METADATA_ONLY"]
    r["best_resolution_A"]=e["best_resolution_A"]
with open(OUT+"/CALIBRATION_SPLIT.tsv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys()),delimiter="\t",lineterminator="\n")
    w.writeheader(); w.writerows(rows)
print(f"structural clusters at TM>={TM_LINK}: {len(clusters)}  sizes {[len(c) for c in clusters]}")
print("split:",dict(collections.Counter(r["split"] for r in rows)))
for i,c in enumerate(clusters):
    tier="HELD_OUT" if i%3==2 else "CALIBRATION"
    fams=sorted({ex[g]["family_METADATA_ONLY"].split(";")[0] for g in c})
    print(f"  SC{i+1:02d} n={len(c):2d} {tier:12s} {', '.join(sorted(c))[:44]:46s} {', '.join(fams)[:56]}")
cal=[r for r in rows if r["split"]=="CALIBRATION"]; ho=[r for r in rows if r["split"]=="HELD_OUT"]
print(f"\ncalibration groups {len(cal)} / held-out groups {len(ho)}")
print(f"held-out structural clusters: {len({r['structural_cluster'] for r in ho})}")
json.dump({"TM_LINK":TM_LINK,"n_clusters":len(clusters)},open(T+"/split.json","w"))
