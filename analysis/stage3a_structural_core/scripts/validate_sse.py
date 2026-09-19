#!/usr/bin/env python3
"""Validate the DSSP-KS implementation against the historical mkdssp 4.5.5 outputs.

The historical .dssp files are used ONLY as an instrument check. They carry no boundary,
no motif and no label, so this validation cannot leak anything forbidden into Stage 3A.
"""
import gemmi, os, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sse
D="/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache"
def parse_dssp(p, want_chain=None):
    """The historical .dssp files were computed on the FULL deposition, so the chain column
    must be honoured; otherwise residues from other chains collide on residue number."""
    out={}; on=False
    for l in open(p, errors="ignore"):
        if l.startswith("  #  RESIDUE"): on=True; continue
        if not on or len(l)<17: continue
        if l[13]=="!": continue
        if want_chain is not None and l[11]!=want_chain: continue
        try: num=int(l[5:10])
        except ValueError: continue
        c=l[16]
        out[num]= "H" if c in "HGI" else ("E" if c in "EB" else "C")
    return out
rows=[]
for f in sorted(glob.glob(D+"/d21_sse/*.dssp")):
    aid=os.path.basename(f)[:-5]
    pdbf=D+f"/d21_backbones/{aid}.pdb"
    if not os.path.exists(pdbf): continue
    st0=gemmi.read_structure(pdbf); st0.setup_entities()
    want=max(st0[0], key=lambda c: len(c.get_polymer())).name
    ref=parse_dssp(f, want)
    st=gemmi.read_structure(pdbf); st.setup_entities(); st.remove_alternative_conformations()
    ch=max(st[0], key=lambda c: len(c.get_polymer()))
    bb=sse._bb(ch)
    if not bb: continue
    mine,_=sse.dssp_ks(bb)
    # the historical .dssp and the backbone extract can differ in residue NUMBERING,
    # so align positionally: both are the same chain in the same order.
    refseq=[v for _,v in sorted(ref.items())]
    if len(refseq)==len(bb):
        pairs=list(zip(mine, refseq))
    else:
        byn=[(mine[i], ref[b["num"]]) for i,b in enumerate(bb) if b["num"] in ref]
        pairs=byn if len(byn)>0.9*len(bb) else list(zip(mine, refseq))[:min(len(mine),len(refseq))]
    if not pairs: continue
    agree=sum(a==b for a,b in pairs)/len(pairs)
    hh=sum(1 for a,b in pairs if a=="H" and b=="H"); refH=sum(1 for _,b in pairs if b=="H")
    ee=sum(1 for a,b in pairs if a=="E" and b=="E"); refE=sum(1 for _,b in pairs if b=="E")
    rows.append((aid, len(pairs), round(agree,4),
                 round(hh/refH,3) if refH else float('nan'),
                 round(ee/refE,3) if refE else float('nan')))
print(f"{'chain':14s}{'n':>6s}{'3-state agree':>14s}{'H recall':>10s}{'E recall':>10s}")
for r in rows: print(f"{r[0]:14s}{r[1]:6d}{r[2]:14.4f}{r[3]:10.3f}{r[4]:10.3f}")
import statistics as S
print(f"\nchains compared: {len(rows)}")
print(f"median 3-state agreement vs mkdssp 4.5.5: {S.median(r[2] for r in rows):.4f}")
print(f"median H recall: {S.median(r[3] for r in rows):.3f}   median E recall: {S.median(r[4] for r in rows):.3f}")
