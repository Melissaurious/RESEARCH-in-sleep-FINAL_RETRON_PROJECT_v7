#!/usr/bin/env python3
"""G2L held-out gate. Mapper frozen. One run. No tuning."""
import sys, os, random, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from residue_mapper import *
sys.path.insert(0,"/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/scripts")
from repaired_lib import eligible_by_family, components, all_vs_all, DYAD, clean
WORK,TABLES=sys.argv[1],sys.argv[2]
G4A="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/work"
HMM=f"{G4A}/GII.deriv.hmm"
ANCH=sorted(int(l.split('\t')[2]) for l in open(
 "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_ug5_holdout_gate/"
 "tables/ug5_frozen_anchor_coordinates.tsv") if not l.startswith("anchor_index"))
random.seed(20260916)
elig=eligible_by_family(); g2l=elig["G2L"]
comps=components(list(g2l), all_vs_all(g2l,WORK,'g2l_gate'))
comp_of={i:ci for ci,c in enumerate(comps) for i in c}
m,ins,L=state_to_residue(HMM,g2l,WORK,"g2l_real")
rows,seqrows,delrows,catrows,ambrows=[],[],[],[],[]
for sid in sorted(g2l):
    st=m[sid]; seq=g2l[sid]; ci=comp_of[sid]
    mapped=[a for a in ANCH if a<=L and st[a]["residue_index"]]
    dele=[a for a in ANCH if a<=L and st[a]["alignment_state"]=="DELETE"]
    for a in ANCH:
        if a>L: continue
        rows.append([sid,str(ci),str(a),str(st[a]["residue_index"] or ""),st[a]["aa"],
                     st[a]["alignment_state"]])
    d=DYAD.search(seq)
    cat=""
    if d:
        dp=d.start()+1
        hit=[a for a in mapped if abs(st[a]["residue_index"]-dp)<=3]
        cat="MAPPED_AT_ANCHOR" if hit else "DYAD_PRESENT_NOT_AT_AN_ANCHOR"
        catrows.append([sid,str(ci),str(dp),seq[dp-1:dp+3],cat,
                        str(hit[0]) if hit else ""])
    seqrows.append([sid,str(ci),str(len(ANCH)),str(len(mapped)),
                    f"{100*len(mapped)/len(ANCH):.1f}",str(len(dele)),
                    f"{100*len(dele)/len(ANCH):.1f}",
                    "ABSTAIN" if not mapped else "MAPPED",cat,str(len(seq))])
    delrows.append([sid,str(ci),str(len(dele)),str(sum(n for _,n in ins[sid])),
                    str(len([r for r in ins[sid] if r[1]>=10]))])
# decoys: 3 replicates, all retained
dec=[]
for rep in range(3):
    random.seed(20260916+rep)
    sh={}
    for sid,seq in sorted(g2l.items()):
        s=list(seq.upper()); random.shuffle(s); sh[sid+f"_SHUF{rep}"]="".join(s)
    md,_,_=state_to_residue(HMM,sh,WORK,f"g2l_dec{rep}")
    for sid,st in md.items():
        mp=[a for a in ANCH if a<=L and st[a]["residue_index"]]
        dec.append([str(rep),sid,str(len(mp)),f"{100*len(mp)/len(ANCH):.1f}"])
for name,data,hdr in [
 ("fresh_lineage_state_to_residue.tsv",rows,"sequence_id\tcomponent\thmm_state\tresidue_index\tamino_acid\talignment_state\n"),
 ("fresh_lineage_sequence_summary.tsv",seqrows,"sequence_id\tcomponent\tn_frozen_states\tn_states_mapped\tpct_mapped\tn_states_deleted\tpct_deleted\tverdict\tcatalytic\tseq_len\n"),
 ("fresh_lineage_deletions_insertions.tsv",delrows,"sequence_id\tcomponent\tn_anchor_states_deleted\ttotal_inserted_residues\tn_insert_runs_ge10\n"),
 ("fresh_lineage_catalytic_state.tsv",catrows,"sequence_id\tcomponent\tdyad_residue_index\tdyad_motif\tverdict\tanchor_state\n"),
 ("fresh_lineage_decoy_results.tsv",dec,"replicate\tdecoy_sequence_id\tn_states_mapped\tpct_mapped\n")]:
    with open(f"{TABLES}/{name}","w") as f:
        f.write(hdr)
        for r in data: f.write("\t".join(r)+"\n")
cs=[]
for ci,c in enumerate(comps):
    sub=[r for r in seqrows if r[1]==str(ci)]
    mp=[int(r[3]) for r in sub]
    cs.append([str(ci),str(len(c)),"QUALIFYING" if len(c)>=5 else "descriptive_only",
               f"{statistics.median(mp):.0f}",f"{100*statistics.median(mp)/len(ANCH):.1f}",
               str(sum(1 for r in sub if r[7]=="ABSTAIN")),
               str(sum(1 for r in sub if r[8]=="MAPPED_AT_ANCHOR"))])
with open(f"{TABLES}/fresh_lineage_component_summary.tsv","w") as f:
    f.write("component\tn_sequences\trole\tmedian_states_mapped\tmedian_pct_mapped\tn_abstain\tn_catalytic_at_anchor\n")
    for r in cs: f.write("\t".join(r)+"\n")
dm=[int(r[2]) for r in dec]
print(f"REAL  n={len(seqrows)} median_mapped={statistics.median([int(r[3]) for r in seqrows]):.0f}/{len(ANCH)} "
      f"abstain={sum(1 for r in seqrows if r[7]=='ABSTAIN')}")
print(f"DECOY n={len(dec)} median_mapped={statistics.median(dm):.0f} max={max(dm)} "
      f"with_any={sum(1 for x in dm if x>0)}")
print("components:")
for r in cs: print(f"  comp{r[0]} n={r[1]:3s} {r[2]:17s} median {r[3]:>3}/150 = {r[4]:>5}%  abstain={r[5]} catalytic_at_anchor={r[6]}")
