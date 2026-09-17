#!/usr/bin/env python3
"""Implementation validation of the residue mapper on CONSTRUCTION families (not biology)."""
import sys, os, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from residue_mapper import *
sys.path.insert(0,"/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/scripts")
from repaired_lib import eligible_by_family, DYAD
WORK, TABLES = sys.argv[1], sys.argv[2]
G4A="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/work"
HMM=f"{G4A}/GII.deriv.hmm"
CON=["Retrons","GII","DGRs","CRISPR","UG3","AbiA"]
elig=eligible_by_family()
ANCH=sorted(int(l.split('\t')[2]) for l in open(
  "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_ug5_holdout_gate/"
  "tables/ug5_frozen_anchor_coordinates.tsv") if not l.startswith("anchor_index"))
rows=[]
for fam in CON:
    seqs={k:v for k,v in sorted(elig[fam].items())[:40]}
    m,ins,L=state_to_residue(HMM,seqs,WORK,f"cv_{fam}")
    call=[];dele=[];revok=0;monot=0;dy=0;n=0
    for sid,st in m.items():
        n+=1
        mapped=[st[a]["residue_index"] for a in ANCH if a<=L and st[a]["residue_index"]]
        call.append(len(mapped)/len(ANCH))
        dele.append(sum(1 for a in ANCH if a<=L and st[a]["alignment_state"]=="DELETE")/len(ANCH))
        if all(seqs[sid][st[a]["residue_index"]-1]==st[a]["aa"]
               for a in ANCH if a<=L and st[a]["residue_index"]): revok+=1
        if all(mapped[i]<mapped[i+1] for i in range(len(mapped)-1)): monot+=1
        d=DYAD.search(seqs[sid])
        if d and any(abs(p-(d.start()+1))<=3 for p in mapped): dy+=1
    rows.append([fam,str(n),f"{statistics.median(call):.3f}",f"{statistics.median(dele):.3f}",
                 f"{revok}/{n}",f"{monot}/{n}",f"{dy}/{n}"])
with open(f"{TABLES}/construction_mapper_validation.tsv","w") as f:
    f.write("family\tn_sequences\tmedian_anchor_state_callability\tmedian_anchor_deletion_rate\t"
            "coordinate_reversibility_ok\tmonotone_mapped_order_IMPLEMENTATION_INVARIANT\t"
            "dyad_within_3aa_of_a_mapped_anchor\n")
    for r in rows: f.write("\t".join(r)+"\n")
for r in rows: print(f"  {r[0]:9s} n={r[1]:3s} call={r[2]} del={r[3]} rev_ok={r[4]} mono={r[5]} dyad={r[6]}")
