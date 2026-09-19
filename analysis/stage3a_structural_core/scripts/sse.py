#!/usr/bin/env python3
"""Two INDEPENDENT secondary-structure assignments. Deterministic, no RNG, no sequence input.

DSSP-KS : Kabsch & Sander (1983) backbone hydrogen-bond energy.
          H on N placed as N + unit(C_prev -> O_prev reversed); E = 0.084*332*(1/rON + 1/rCH
          - 1/rOH - 1/rCN) kcal/mol; H-bond if E < -0.5. n-turn(i) = hbond(i, i+n).
          alpha-helix H where 4-turn(i-1) and 4-turn(i); 3-10 (G) and pi (I) likewise from
          3- and 5-turns. Bridges from the parallel/antiparallel H-bond patterns; ladders of
          >=1 bridge give E. Collapsed to 3 states: H in {H,G,I}, E in {E,B}, else C.
P-SEA   : Labesse et al. (1997) CA-only geometry. Uses d(i,i+2), d(i,i+3), d(i,i+4), the CA
          pseudo-angle theta(i-1,i,i+1) and the CA pseudo-dihedral tau(i-1,i,i+1,i+2).
          helix: d2 5.5+-0.5, d3 5.3+-0.5, d4 6.4+-0.6, theta 89+-12, tau 50+-20
          strand: d2 6.7+-0.6, d3 9.9+-0.9, d4 12.4+-1.1, theta 124+-14, tau -170+-45
          A residue is assigned only inside a run of >=3 (helix) / >=2 (strand) consecutive hits.

NEITHER method sees the amino-acid sequence, any motif, any label, or any prior boundary.
"""
import numpy as np, math

def _bb(chain):
    """-> list of dicts with N, CA, C, O for residues that have all four."""
    out=[]
    for r in chain:
        a={x.name:np.array([x.pos.x,x.pos.y,x.pos.z]) for x in r}
        if all(k in a for k in ("N","CA","C","O")):
            out.append(dict(num=r.seqid.num, name=r.name, N=a["N"], CA=a["CA"], C=a["C"], O=a["O"]))
    return out

def dssp_ks(bb):
    n=len(bb)
    H=[None]*n
    for i in range(1,n):
        d=bb[i-1]["C"]-bb[i-1]["O"]; nrm=np.linalg.norm(d)
        H[i]=bb[i]["N"]+d/nrm if nrm>1e-6 else None
    def energy(i,j):
        if H[i] is None: return 0.0
        rON=np.linalg.norm(bb[i]["N"]-bb[j]["O"]); rCH=np.linalg.norm(H[i]-bb[j]["C"])
        rOH=np.linalg.norm(H[i]-bb[j]["O"]); rCN=np.linalg.norm(bb[i]["N"]-bb[j]["C"])
        if min(rON,rCH,rOH,rCN)<0.5: return 0.0
        return 0.084*332.0*(1.0/rON + 1.0/rCH - 1.0/rOH - 1.0/rCN)
    CA=np.array([b["CA"] for b in bb])
    close=(np.linalg.norm(CA[:,None,:]-CA[None,:,:],axis=-1)<9.0)
    hb=set()
    for i in range(n):
        for j in range(n):
            if abs(i-j)<2 or not close[i,j]: continue
            if energy(i,j)<-0.5: hb.add((i,j))      # N-H of i donates to C=O of j
    turn={k:[False]*n for k in (3,4,5)}
    for k in (3,4,5):
        for i in range(n-k):
            if (i+k,i) in hb: turn[k][i]=True
    ss=["C"]*n
    for k,ch in ((5,"I"),(3,"G"),(4,"H")):
        for i in range(1,n-k):
            if turn[k][i-1] and turn[k][i]:
                for x in range(i,min(i+k,n)): ss[x]=ch
    def bridge(i,j):
        if i<1 or j<1 or i+1>=n or j+1>=n: return None
        if ((i-1,j) in hb and (j,i+1) in hb) or ((j-1,i) in hb and (i,j+1) in hb): return "P"
        if ((i,j) in hb and (j,i) in hb) or ((i-1,j+1) in hb and (j-1,i+1) in hb): return "A"
        return None
    for i in range(n):
        for j in range(i+3,n):
            if bridge(i,j):
                if ss[i]=="C": ss[i]="E"
                if ss[j]=="C": ss[j]="E"
    three=["H" if c in "HGI" else ("E" if c in "EB" else "C") for c in ss]
    return three, ss

def _ang(a,b,c):
    v1=a-b; v2=c-b
    cs=np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)+1e-9)
    return math.degrees(math.acos(max(-1,min(1,cs))))
def _dih(p0,p1,p2,p3):
    b0=p0-p1; b1=p2-p1; b2=p3-p2
    b1n=b1/(np.linalg.norm(b1)+1e-9)
    v=b0-np.dot(b0,b1n)*b1n; w=b2-np.dot(b2,b1n)*b1n
    x=np.dot(v,w); y=np.dot(np.cross(b1n,v),w)
    return math.degrees(math.atan2(y,x))

def psea(bb):
    n=len(bb); CA=[b["CA"] for b in bb]
    def d(i,k): return np.linalg.norm(CA[i]-CA[i+k]) if i+k<n else None
    def th(i): return _ang(CA[i-1],CA[i],CA[i+1]) if 1<=i<n-1 else None
    def ta(i): return _dih(CA[i-1],CA[i],CA[i+1],CA[i+2]) if 1<=i<n-2 else None
    hel=[False]*n; strd=[False]*n
    for i in range(n):
        d2,d3,d4,t,u = d(i,2),d(i,3),d(i,4),th(i),ta(i)
        if None not in (d2,d3,d4) and abs(d2-5.5)<=0.5 and abs(d3-5.3)<=0.5 and abs(d4-6.4)<=0.6: hel[i]=True
        elif None not in (t,u) and abs(t-89)<=12 and abs(u-50)<=20: hel[i]=True
        if None not in (d2,d3,d4) and abs(d2-6.7)<=0.6 and abs(d3-9.9)<=0.9 and abs(d4-12.4)<=1.1: strd[i]=True
        elif None not in (t,u) and abs(t-124)<=14 and min(abs(u+170),abs(u-190))<=45: strd[i]=True
    ss=["C"]*n
    def runs(flag,minlen,ch,span):
        i=0
        while i<n:
            if flag[i]:
                j=i
                while j<n and flag[j]: j+=1
                if j-i>=minlen:
                    for x in range(i,min(j+span,n)): ss[x]=ch
                i=j
            else: i+=1
    runs(strd,2,"E",2); runs(hel,3,"H",4)
    return ss
