#!/usr/bin/env python3
"""Select the v3 order statistic using CONSTRUCTION-FAMILY DATA ONLY. UG5 is never opened.
Candidates are scored on interpretability and behaviour on non-UG5 data, NOT on what makes
UG5 look best."""
import sys, os, random, statistics, collections, itertools
sys.path.insert(0,"/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/scripts")
from repaired_lib import *
G4AWORK, WORK, TABLES = sys.argv[1], sys.argv[2], sys.argv[3]
REF="GII"; DEV=["Retrons","DGRs","CRISPR","UG3","AbiA"]; MIN_SCORE=8.0
random.seed(20260916)
elig=eligible_by_family()
CON=["Retrons","GII","DGRs","CRISPR","UG3","AbiA"]
pm={}
for a,b in itertools.permutations(CON,2):
    m=pair_map(f"{WORK}/con_{a}__{b}.hhr")
    if m: pm[(a,b)]=m
sup=collections.Counter()
for b in CON:
    if b!=REF and (REF,b) in pm:
        for q in pm[(REF,b)]: sup[q]+=1
n_other=sum(1 for b in CON if b!=REF and (REF,b) in pm)
ANCH=sorted(k for k,v in sup.items() if v==n_other)
def placed(sid,seq,tag):
    fp=f"{WORK}/om_{tag}.faa"; write_fasta({sid:seq},fp)
    dom=f"{WORK}/om_{tag}.domtbl"
    run([BIN+"hmmsearch","--max","-E",HMMSEARCH_E,"--noali","--domtblout",dom,
         f"{G4AWORK}/{REF}.deriv.hmm",fp])
    best={}
    for line in open(dom):
        if line.startswith("#"): continue
        p=line.split(); sc=float(p[13])
        if sc<MIN_SCORE: continue
        hs,he,as_,ae=int(p[15]),int(p[16]),int(p[17]),int(p[18])
        for a in ANCH:
            if hs<=a<=he:
                fr=(a-hs)/max(1,(he-hs)); pos=as_+fr*(ae-as_)
                if a not in best or sc>best[a][1]: best[a]=(pos,sc)
    return best
def metrics(b):
    if len(b)<3: return None
    ks=sorted(b); v=[b[k][0] for k in ks]
    n=len(v); pairs=n*(n-1)//2
    conc=sum(1 for i in range(n) for j in range(i+1,n) if v[j]>v[i])
    tau=(2*conc-pairs)/pairs
    inv=sum(1 for i in range(n-1) if v[i+1]<=v[i])
    # longest monotone increasing subsequence
    import bisect
    tails=[]
    for x in v:
        i=bisect.bisect_left(tails,x)
        if i==len(tails): tails.append(x)
        else: tails[i]=x
    return dict(n=n,tau=tau,ordered_pair_frac=conc/pairs,
                inv_frac=inv/max(1,n-1),lms_frac=len(tails)/n,
                monotone=1 if inv==0 else 0)
rows=[]
for fam in DEV:
    for i,(sid,seq) in enumerate(sorted(elig[fam].items())):
        m=metrics(placed(sid,seq,f"r{fam}{i}"))
        if m: rows.append(("REAL",fam,sid,m))
        s=list(seq.upper()); random.shuffle(s)
        m=metrics(placed(sid,"".join(s),f"d{fam}{i}"))
        if m: rows.append(("DECOY",fam,sid,m))
out=[]
for met in ("tau","ordered_pair_frac","inv_frac","lms_frac","monotone"):
    R=[r[3][met] for r in rows if r[0]=="REAL"]; D=[r[3][met] for r in rows if r[0]=="DECOY"]
    out.append([met,str(len(R)),f"{statistics.median(R):.4f}",f"{min(R):.4f}",
                str(len(D)),f"{statistics.median(D):.4f}" if D else "n/a",
                f"{100*sum(1 for x in R if x>=0.9)/len(R):.1f}" if met!="inv_frac" else
                f"{100*sum(1 for x in R if x<=0.1)/len(R):.1f}"])
with open(f"{TABLES}/order_metric_development.tsv","w") as f:
    f.write("metric\tn_real\treal_median\treal_min\tn_decoy\tdecoy_median\t"
            "pct_real_at_or_beyond_0.9_threshold\n")
    for r in out: f.write("\t".join(r)+"\n")
print(f"{'metric':22s}{'n_real':>7}{'real_med':>10}{'real_min':>10}{'n_decoy':>9}{'dec_med':>9}{'real>=0.9%':>12}")
for r in out: print(f"{r[0]:22s}{r[1]:>7}{r[2]:>10}{r[3]:>10}{r[4]:>9}{r[5]:>9}{r[6]:>12}")
