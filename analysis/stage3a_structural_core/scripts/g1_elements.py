#!/usr/bin/env python3
"""Stage 3A g1 — per-chain secondary-structure elements and the element contact graph.

Label-blind. Reads only coordinates. Emits STRUCTURAL_ELEMENTS.tsv.
"""
import gemmi, csv, os, sys, numpy as np, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sse
ROOT="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit"
OUT=ROOT+"/analysis/stage3a_structural_core"
reg=list(csv.DictReader(open(OUT+"/STRUCTURE_REGISTER.tsv"),delimiter="\t"))
MIN_H, MIN_E = 4, 2          # declared minimum element lengths
rows=[]; cache={}
for r in reg:
    f=r["source_file"]
    if f not in cache:
        st=gemmi.read_structure(f); st.setup_entities(); st.remove_alternative_conformations(); cache[f]=st
    ch=[c for c in cache[f][0] if c.name==r["chain"]][0]
    bb=sse._bb(ch)
    if len(bb)<30: continue
    d3,d8 = sse.dssp_ks(bb)
    ps    = sse.psea(bb)
    # elements from DSSP-KS
    els=[]; i=0
    while i<len(d3):
        c=d3[i]
        if c=="C": i+=1; continue
        j=i
        while j<len(d3) and d3[j]==c: j+=1
        if (c=="H" and j-i>=MIN_H) or (c=="E" and j-i>=MIN_E):
            els.append((c,i,j-1))
        i=j
    CA=np.array([b["CA"] for b in bb])
    # element-level contacts: CA-CA <= 10 A between residues of different elements
    for k,(c,a,b2) in enumerate(els):
        seg=CA[a:b2+1]
        nb=0
        for k2,(c2,a2,b3) in enumerate(els):
            if k2==k: continue
            d=np.linalg.norm(seg[:,None,:]-CA[a2:b3+1][None,:,:],axis=-1)
            nb+= int((d<=10.0).sum())
        agree=sum(1 for x in range(a,b2+1) if ps[x]==c)/(b2-a+1)
        rows.append(dict(pdb_id=r["pdb_id"], chain=r["chain"], biological_group=r["biological_group"],
            element_index=k, element_type=c,
            start_resnum=bb[a]["num"], end_resnum=bb[b2]["num"], length=b2-a+1,
            start_pos=a, end_pos=b2,
            psea_agreement=round(agree,3),
            n_interelement_contacts=nb))
with open(OUT+"/STRUCTURAL_ELEMENTS.tsv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys()),delimiter="\t",lineterminator="\n")
    w.writeheader(); w.writerows(rows)
per=collections.Counter((r["pdb_id"],r["chain"]) for r in rows)
print(f"chains with elements: {len(per)}   total elements: {len(rows)}")
print(f"elements per chain: median {sorted(per.values())[len(per)//2]}  min {min(per.values())}  max {max(per.values())}")
print("element types:",dict(collections.Counter(r["element_type"] for r in rows)))
import statistics as S
print(f"median P-SEA agreement within a DSSP-KS element: {S.median(r['psea_agreement'] for r in rows):.3f}")
