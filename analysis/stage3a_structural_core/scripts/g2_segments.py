#!/usr/bin/env python3
"""Stage 3A g2 step 4 — CONTIGUOUS structural-domain decomposition, label-blind.

Positive criterion: a structural domain is a contiguous stretch of chain whose residues contact
each other far more than they contact the rest of the chain. For each k we find, by exact dynamic
programming, the cut points minimising the normalised cut

    NC(k) = sum over segments s of  cut(s, rest) / vol(s)

on the residue contact graph (CA-CA <= 8 A, |i-j| >= 3). NC is monotone-ish in k, so the reported
quantity is the RELATIVE IMPROVEMENT NC(k-1) -> NC(k); the natural k is where improvement stops.

k is never forced. No sequence, motif, label or prior boundary is read.
"""
import gemmi, csv, os, sys, numpy as np, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sse
ROOT="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit"
OUT=ROOT+"/analysis/stage3a_structural_core"
CUT_A, SEQ_SEP, KMAX, MINSEG = 8.0, 3, 6, 25
reg=list(csv.DictReader(open(OUT+"/STRUCTURE_REGISTER.tsv"),delimiter="\t"))
def segment(C, kmax):
    n=C.shape[0]
    P=np.zeros((n+1,n+1))
    P[1:,1:]=np.cumsum(np.cumsum(C,0),1)
    def block(a,b,c,d):           # sum of C[a:b, c:d]
        return P[b,d]-P[a,d]-P[b,c]+P[a,c]
    vol=C.sum(1); tot=C.sum()
    res={}
    for k in range(1,kmax+1):
        INF=1e18
        dp=np.full((k+1,n+1),INF); bk=np.zeros((k+1,n+1),dtype=int)
        dp[0,0]=0.0
        for kk in range(1,k+1):
            for e in range(kk*MINSEG, n+1):
                best=INF; arg=-1
                for s in range((kk-1)*MINSEG, e-MINSEG+1):
                    if dp[kk-1,s]>=INF: continue
                    v=vol[s:e].sum()
                    if v<=0: continue
                    internal=block(s,e,s,e)
                    cost=dp[kk-1,s]+(v-internal)/v
                    if cost<best: best=cost; arg=s
                dp[kk,e]=best; bk[kk,e]=arg
        if dp[k,n]>=INF: continue
        cuts=[]; e=n
        for kk in range(k,0,-1):
            s=bk[kk,e]; cuts.append((s,e)); e=s
        res[k]=(dp[k,n], list(reversed(cuts)))
    return res
rows=[]; summary=[]; cache={}
for r in reg:
    f=r["source_file"]
    if f not in cache:
        st=gemmi.read_structure(f); st.setup_entities(); st.remove_alternative_conformations(); cache[f]=st
    ch=[c for c in cache[f][0] if c.name==r["chain"]][0]
    bb=sse._bb(ch); n=len(bb)
    if n<3*MINSEG: continue
    CA=np.array([b["CA"] for b in bb])
    D=np.linalg.norm(CA[:,None,:]-CA[None,:,:],axis=-1)
    C=((D<=CUT_A)&(np.abs(np.subtract.outer(np.arange(n),np.arange(n)))>=SEQ_SEP)).astype(float)
    res=segment(C, min(KMAX, n//MINSEG))
    if 1 not in res: continue
    d3,_=sse.dssp_ks(bb)
    ks=sorted(res)
    impr={k:(res[k-1][0]-res[k][0])/max(res[k-1][0],1e-9) for k in ks if k-1 in res}
    knat=1
    for k in ks:
        if k in impr and impr[k]>=0.10: knat=k
        elif k>1: break
    summary.append(dict(chain=f"{r['pdb_id']}_{r['chain']}", biological_group=r["biological_group"],
        n_res=n, natural_k=knat,
        **{f"NC_k{k}":round(res[k][0],4) for k in ks if k<=KMAX},
        **{f"impr_k{k}":round(impr[k],3) for k in ks if k in impr and k<=KMAX}))
    for k in (3, knat):
        tag="k3" if k==3 else "natural"
        if k not in res: continue
        for si,(a,b2) in enumerate(res[k][1],1):
            seg=d3[a:b2]
            nH=sum(1 for c in seg if c=="H"); nE=sum(1 for c in seg if c=="E")
            rows.append(dict(pdb_id=r["pdb_id"], chain=r["chain"], biological_group=r["biological_group"],
                partition=tag, k=k, segment=si,
                start_resnum=bb[a]["num"], end_resnum=bb[b2-1]["num"], n_residues=b2-a,
                frac_H=round(nH/max(b2-a,1),3), frac_E=round(nE/max(b2-a,1),3),
                frac_coil=round(1-(nH+nE)/max(b2-a,1),3),
                normalised_cut=round(res[k][0],4)))
with open(OUT+"/DOMAIN_ASSIGNMENTS_CONTIGUOUS.tsv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys()),delimiter="\t",lineterminator="\n")
    w.writeheader(); w.writerows(rows)
hdr=sorted({k for s in summary for k in s})
with open(OUT+"/tables/g2_segmentation_curve.tsv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["chain","biological_group","n_res","natural_k"]+[h for h in hdr if h.startswith(("NC_","impr_"))],
                     delimiter="\t",lineterminator="\n",extrasaction="ignore")
    w.writeheader(); w.writerows(summary)
import statistics as S
print(f"chains segmented: {len(summary)}")
kd=collections.Counter(s["natural_k"] for s in summary)
print("NATURAL number of CONTIGUOUS structural domains (>=10% normalised-cut improvement):")
for k in sorted(kd): print(f"   k={k}: {kd[k]:3d} chains ({kd[k]/len(summary):.2f})")
for k in (2,3,4,5):
    v=[s.get(f"impr_k{k}") for s in summary if s.get(f"impr_k{k}") is not None]
    if v: print(f"  median improvement going to k={k}: {S.median(v):+.3f}")
