#!/usr/bin/env python3
"""Evaluate the frozen detector on Tier A ONLY. Tier B is never read."""
import csv, gemmi, os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detector import *
ROOT="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit"
tt=list(csv.DictReader(open(ROOT+"/analysis/stage3b_design/TRUTH_TABLE.tsv"),delimiter="\t"))
A=[r for r in tt if r["tier"]=="A_calibration"]
assert all(r["tier"]!="B_heldout" for r in A)
cache={}; rows=[]; decoys=0; decoy_chains=0
for r in sorted(A, key=lambda x:(x["pdb_id"],x["chain"])):
    res=float(r["resolution_A"])
    truth=set(int(x) for x in r["S_catalytic_asp"].split(",") if x)
    if res > RES_MAX:
        rows.append(dict(chain=f"{r['pdb_id']}_{r['chain']}", res=res, verdict="NOT_SCOREABLE",
            cause=f"resolution {res} > {RES_MAX}", pred="", truth=sorted(truth), n_cand=0, outcome="EXCLUDED")); continue
    f=r["source_file"]
    if f not in cache:
        st=gemmi.read_structure(f); st.setup_entities(); st.remove_alternative_conformations(); cache[f]=st
    poly=[c for c in cache[f][0] if c.name==r["chain"]][0]
    P={x.seqid.num:[a.pos for a in x if a.name in ("OD1","OD2")] for x in poly if x.name=="ASP"}
    P={k:v for k,v in P.items() if v}   # detector spec: both residues must have a MODELLED carboxylate
    v,pair,c = predict(P)
    nd=sum(1 for d,i,j in c if not (i in truth and j in truth))
    decoys+=nd; decoy_chains+= (1 if nd else 0)
    if not truth: outcome="NO_TRUTH"
    elif v=="ABSTAIN": outcome="ABSTAIN"
    else: outcome = "HIT" if (pair[0] in truth and pair[1] in truth) else "MISS"
    rows.append(dict(chain=f"{r['pdb_id']}_{r['chain']}", res=res, verdict=v,
        cause=("no admissible candidate" if v=="ABSTAIN" else ""), pred=str(pair) if pair else "",
        truth=sorted(truth), n_cand=len(c), n_decoy_cand=nd, outcome=outcome,
        top3=" ".join(f"{i}-{j}:{d}" for d,i,j in c[:3])))
hdr=["chain","res","verdict","outcome","pred","truth","n_cand","n_decoy_cand","cause","top3"]
dest=ROOT+"/analysis/stage3b_design/G2_TIERA_EVALUATION.tsv"
with open(dest,"w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=hdr,delimiter="\t",lineterminator="\n",extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
withtruth=[r for r in rows if r["outcome"] in ("HIT","MISS","ABSTAIN")]
nonabst=[r for r in withtruth if r["outcome"]!="ABSTAIN"]
print(f"Tier A chains: {len(A)}  scoreable: {len([r for r in rows if r['verdict']!='NOT_SCOREABLE'])}  "
      f"excluded by resolution: {len([r for r in rows if r['verdict']=='NOT_SCOREABLE'])}")
print(f"chains carrying truth: {len(withtruth)}   no-truth chains: {len([r for r in rows if r['outcome']=='NO_TRUTH'])}")
print(f"\nHIT   {sum(1 for r in withtruth if r['outcome']=='HIT')}")
print(f"MISS  {sum(1 for r in withtruth if r['outcome']=='MISS')}")
print(f"ABSTAIN {sum(1 for r in withtruth if r['outcome']=='ABSTAIN')}")
if nonabst: print(f"hit rate among non-abstaining truth-bearing chains: "
      f"{sum(1 for r in nonabst if r['outcome']=='HIT')}/{len(nonabst)} = "
      f"{sum(1 for r in nonabst if r['outcome']=='HIT')/len(nonabst):.3f}")
print(f"abstention rate among truth-bearing chains: {sum(1 for r in withtruth if r['outcome']=='ABSTAIN')}/{len(withtruth)}")
print(f"AMBIGUOUS verdicts: {sum(1 for r in rows if r['verdict']=='AMBIGUOUS')}")
print(f"\nDECOY POOL over scoreable Tier A: {decoys} admissible non-truth candidate pairs across {decoy_chains} chains")
print("\nper-chain:")
for r in rows: print(f"  {r['chain']:10s} {str(r['res']):5s} {r['verdict']:12s} {r['outcome']:10s} pred={r['pred']:14s} truth={r['truth']} cand={r['n_cand']} {r['cause']}")
