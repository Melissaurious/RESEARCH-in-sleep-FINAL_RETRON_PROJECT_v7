#!/usr/bin/env python3
"""Stage 3A g2 step 3 — label-blind structural module detection.

For every chain: build the secondary-structure-element contact graph, take the normalised
Laplacian spectrum, and let the EIGENGAP choose the number of modules. k is NOT forced to 3 -
whether a three-module core emerges is the falsification test of this stage.

Deterministic: eigendecomposition + Ward linkage on the spectral embedding. No RNG.
No sequence, no motif, no label, no prior boundary is read.
"""
import gemmi, csv, os, sys, numpy as np, collections
from scipy.cluster.hierarchy import linkage, fcluster
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sse
ROOT="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit"
OUT=ROOT+"/analysis/stage3a_structural_core"
CONTACT_A, KMAX, MIN_H, MIN_E = 10.0, 8, 4, 2
reg=list(csv.DictReader(open(OUT+"/STRUCTURE_REGISTER.tsv"),delimiter="\t"))
def elements(d3):
    els=[]; i=0
    while i<len(d3):
        c=d3[i]
        if c=="C": i+=1; continue
        j=i
        while j<len(d3) and d3[j]==c: j+=1
        if (c=="H" and j-i>=MIN_H) or (c=="E" and j-i>=MIN_E): els.append((c,i,j-1))
        i=j
    return els
rows=[]; chains=[]; cache={}
for r in reg:
    f=r["source_file"]
    if f not in cache:
        st=gemmi.read_structure(f); st.setup_entities(); st.remove_alternative_conformations(); cache[f]=st
    ch=[c for c in cache[f][0] if c.name==r["chain"]][0]
    bb=sse._bb(ch)
    if len(bb)<60: continue
    d3,_=sse.dssp_ks(bb); els=elements(d3)
    n=len(els)
    if n<6: continue
    CA=np.array([b["CA"] for b in bb])
    W=np.zeros((n,n))
    for a in range(n):
        sa=CA[els[a][1]:els[a][2]+1]
        for b2 in range(a+1,n):
            sb=CA[els[b2][1]:els[b2][2]+1]
            d=np.linalg.norm(sa[:,None,:]-sb[None,:,:],axis=-1)
            W[a,b2]=W[b2,a]=float((d<=CONTACT_A).sum())
    deg=W.sum(1); deg[deg==0]=1e-9
    Dm=np.diag(1.0/np.sqrt(deg))
    L=np.eye(n)-Dm@W@Dm
    ev,evec=np.linalg.eigh(L)
    gaps=[(ev[k]-ev[k-1],k) for k in range(2,min(KMAX,n-1)+1)]
    knat=max(gaps)[1] if gaps else 1
    def partition(k):
        emb=evec[:,:k]
        nrm=np.linalg.norm(emb,axis=1,keepdims=True); nrm[nrm==0]=1
        return fcluster(linkage(emb/nrm,method="ward"),k,criterion="maxclust")
    def modularity(lab):
        m=W.sum()/2
        if m<=0: return 0.0
        q=0.0
        for c in set(lab):
            idx=np.where(lab==c)[0]
            lc=W[np.ix_(idx,idx)].sum()/2; dc=deg[idx].sum()
            q+= lc/m-(dc/(2*m))**2
        return q
    lab_nat=partition(knat); lab3=partition(3) if n>=3 else lab_nat
    for tag,lab,k in (("natural",lab_nat,knat),("k3",lab3,3)):
        for c in sorted(set(lab)):
            idx=[i for i in range(n) if lab[i]==c]
            res=[]
            for i in idx: res.extend(range(els[i][1],els[i][2]+1))
            res=sorted(res)
            spans=[]; s=res[0]; p=res[0]
            for x in res[1:]:
                if x==p+1: p=x
                else: spans.append((s,p)); s=x; p=x
            spans.append((s,p))
            big=max(e-b+1 for b,e in spans)
            nH=sum(els[i][2]-els[i][1]+1 for i in idx if els[i][0]=="H")
            nE=sum(els[i][2]-els[i][1]+1 for i in idx if els[i][0]=="E")
            rows.append(dict(pdb_id=r["pdb_id"], chain=r["chain"], biological_group=r["biological_group"],
                partition=tag, k=k, module=int(c), n_elements=len(idx),
                n_H_elements=sum(1 for i in idx if els[i][0]=="H"),
                n_E_elements=sum(1 for i in idx if els[i][0]=="E"),
                n_residues=len(res), frac_H=round(nH/max(nH+nE,1),3), frac_E=round(nE/max(nH+nE,1),3),
                n_spans=len(spans), contiguity=round(big/len(res),3),
                first_resnum=bb[res[0]]["num"], last_resnum=bb[res[-1]]["num"],
                modularity_Q=round(modularity(lab),4)))
    chains.append((r["pdb_id"]+"_"+r["chain"], n, knat, round(modularity(lab_nat),4), round(modularity(lab3),4)))
with open(OUT+"/DOMAIN_ASSIGNMENTS.tsv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys()),delimiter="\t",lineterminator="\n")
    w.writeheader(); w.writerows(rows)
print(f"chains analysed: {len(chains)}")
kd=collections.Counter(c[2] for c in chains)
print("NATURAL number of structural modules (eigengap), per chain:")
for k in sorted(kd): print(f"   k={k}: {kd[k]:3d} chains  ({kd[k]/len(chains):.2f})")
import statistics as S
print(f"\nmodularity Q at natural k: median {S.median(c[3] for c in chains):.3f}")
print(f"modularity Q forced to k=3 : median {S.median(c[4] for c in chains):.3f}")
n3=[r for r in rows if r["partition"]=="k3"]
print(f"\nforced k=3 modules: median contiguity {S.median(r['contiguity'] for r in n3):.3f}, "
      f"median spans per module {S.median(r['n_spans'] for r in n3)}")
print(f"  modules that are a single contiguous span: {sum(1 for r in n3 if r['n_spans']==1)}/{len(n3)}")
