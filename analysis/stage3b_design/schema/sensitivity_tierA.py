#!/usr/bin/env python3
"""Sensitivity analyses on Tier A ONLY. Reported, never used to move a frozen threshold."""
import csv, gemmi, itertools, os, sys, math, collections, statistics as S
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detector as DET
R="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit"
tt=list(csv.DictReader(open(R+"/analysis/stage3b_design/TRUTH_TABLE.tsv"),delimiter="\t"))
A=[r for r in tt if r["tier"]=="A_calibration" and float(r["resolution_A"])<=DET.RES_MAX]
cache={}
def carbox(r):
    f=r["source_file"]
    if f not in cache:
        st=gemmi.read_structure(f); st.setup_entities(); st.remove_alternative_conformations(); cache[f]=st
    poly=[c for c in cache[f][0] if c.name==r["chain"]][0]
    P={x.seqid.num:[a.pos for a in x if a.name in ("OD1","OD2")] for x in poly if x.name=="ASP"}
    return {k:v for k,v in P.items() if v}
def run(rows, sepmin, sepmax, dmax):
    hit=miss=abst=0
    for r in rows:
        truth=set(int(x) for x in r["S_catalytic_asp"].split(",") if x)
        if not truth: continue
        P=carbox(r); c=[]
        for i,j in itertools.combinations(sorted(P),2):
            if not (sepmin<=abs(i-j)<=sepmax): continue
            d=min(p.dist(q) for p in P[i] for q in P[j])
            if d<=dmax: c.append((d,i,j))
        c.sort()
        if not c: abst+=1; continue
        _,i,j=c[0]
        if i in truth and j in truth: hit+=1
        else: miss+=1
    n=hit+miss
    return hit, miss, abst, (hit/n if n else float('nan'))
out=[]
h,m,a,rate=run(A,DET.SEP_MIN,DET.SEP_MAX,DET.D_MAX)
out.append(dict(analysis="FROZEN", detail=f"SEP[{DET.SEP_MIN},{DET.SEP_MAX}] D_MAX={DET.D_MAX}",
                hit=h,miss=m,abstain=a,hit_rate=round(rate,3)))
# 1. leave-one-cluster-out
for cl in sorted({r["relatedness_cluster_30pct"] for r in A}):
    sub=[r for r in A if r["relatedness_cluster_30pct"]!=cl]
    # recalibrate the window on the remaining Tier A truth, then evaluate on the held-out cluster
    pairs=[]
    for r in sub:
        t=[int(x) for x in r["S_catalytic_asp"].split(",") if x]
        if len(t)<2: continue
        P=carbox(r)
        for i,j in itertools.combinations(sorted(t),2):
            if abs(i-j)>=5 and i in P and j in P:
                pairs.append((abs(i-j), min(p.dist(q) for p in P[i] for q in P[j])))
    if not pairs: continue
    sm=int(math.floor(min(x[0] for x in pairs)/5)*5); sx=int(math.ceil(max(x[0] for x in pairs)/5)*5)
    dm=math.ceil(max(x[1] for x in pairs)*2)/2
    ho=[r for r in A if r["relatedness_cluster_30pct"]==cl]
    h2,m2,a2,r2=run(ho,sm,sx,dm)
    if h2+m2+a2:
        out.append(dict(analysis="leave-one-cluster-out", detail=f"held out {cl}; window from the rest = SEP[{sm},{sx}] D_MAX={dm}",
                        hit=h2,miss=m2,abstain=a2,hit_rate=(round(r2,3) if h2+m2 else "n/a")))
# 2. threshold perturbation
for dm in (5.0,5.5,6.0,6.5,7.0):
    h2,m2,a2,r2=run(A,DET.SEP_MIN,DET.SEP_MAX,dm)
    out.append(dict(analysis="D_MAX perturbation", detail=f"D_MAX={dm}",hit=h2,miss=m2,abstain=a2,hit_rate=round(r2,3)))
for pad in (0,5,10,20):
    h2,m2,a2,r2=run(A,DET.SEP_MIN-pad,DET.SEP_MAX+pad,DET.D_MAX)
    out.append(dict(analysis="SEP window perturbation", detail=f"SEP[{DET.SEP_MIN-pad},{DET.SEP_MAX+pad}]",hit=h2,miss=m2,abstain=a2,hit_rate=round(r2,3)))
# 3. resolution band
for lo,hi in ((0,2.5),(2.5,3.0),(3.0,3.5)):
    sub=[r for r in A if lo<float(r["resolution_A"])<=hi]
    h2,m2,a2,r2=run(sub,DET.SEP_MIN,DET.SEP_MAX,DET.D_MAX)
    if h2+m2+a2: out.append(dict(analysis="resolution band", detail=f"({lo},{hi}] A",hit=h2,miss=m2,abstain=a2,hit_rate=(round(r2,3) if h2+m2 else "n/a")))
# 4. transferred truth excluded
sub=[r for r in A if r["truth_source"]=="OWN_CHAIN"]
h2,m2,a2,r2=run(sub,DET.SEP_MIN,DET.SEP_MAX,DET.D_MAX)
out.append(dict(analysis="exclude transferred truth", detail="truth_source == OWN_CHAIN only",hit=h2,miss=m2,abstain=a2,hit_rate=round(r2,3)))
# 5. one chain per replicate group (redundancy control)
seen=set(); sub=[]
for r in sorted(A,key=lambda x:(x["replicate_group"],x["resolution_A"])):
    if r["replicate_group"] in seen: continue
    seen.add(r["replicate_group"]); sub.append(r)
h2,m2,a2,r2=run(sub,DET.SEP_MIN,DET.SEP_MAX,DET.D_MAX)
out.append(dict(analysis="one chain per replicate group",detail=f"{len(sub)} chains",hit=h2,miss=m2,abstain=a2,hit_rate=round(r2,3)))
with open(R+"/analysis/stage3b_design/G2_SENSITIVITY_TIERA.tsv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["analysis","detail","hit","miss","abstain","hit_rate"],delimiter="\t",lineterminator="\n")
    w.writeheader(); w.writerows(out)
for o in out: print(f"  {o['analysis']:30s} {o['detail']:52s} hit={o['hit']:2d} miss={o['miss']:2d} abst={o['abstain']:2d} rate={o['hit_rate']}")
