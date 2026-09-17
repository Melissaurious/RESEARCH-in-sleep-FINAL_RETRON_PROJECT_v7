#!/usr/bin/env python3
"""UG5 holdout gate v3. Rule FROZEN in control/UG5_V3_PREDECLARATION.md, derived from
construction-family data only. Writes ONLY ug5_v3_* tables; overwrites no v2 output."""
import sys, os, re, random, itertools, collections, statistics, bisect
sys.path.insert(0,"/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/scripts")
from repaired_lib import *
G4AWORK, WORK, TABLES = sys.argv[1], sys.argv[2], sys.argv[3]
CON=["Retrons","GII","DGRs","CRISPR","UG3","AbiA"]; HELD="UG5"; REF="GII"
MIN_SCORE=8.0; AMBIG_WINDOW=10; DYAD_WINDOW=10
aud=Audit(); elig=eligible_by_family(); ug5=elig[HELD]
ug5_ids,ug5_seqs=set(ug5),set(ug5.values())

# provenance, fails closed
prov=[];fail=False
for fam in CON:
    for suf in (".derivation.faa",".deriv.mafft.afa",".deriv.hmm",".deriv.hhm"):
        p=f"{G4AWORK}/{fam}{suf}"
        if not os.path.exists(p): sys.exit("FAIL CLOSED: missing "+p)
        txt=open(p,errors="replace").read()
        bid=any(i in txt for i in ug5_ids)
        bsq=any(clean(s) in ug5_seqs for s in read_fasta(p).values()) if p.endswith((".faa",".afa")) else False
        fail|=bid or bsq
        prov.append([os.path.basename(p),sha256(p),"YES" if bid else "NO","YES" if bsq else "NO",
                     "TRUE" if (bid or bsq) else "FALSE"])
with open(f"{TABLES}/ug5_v3_provenance_audit.tsv","w") as f:
    f.write("construction_input\tsha256_at_gate_time\tUG5_id_found\tUG5_sequence_found\tUG5_GENEALOGY_PRESENT\n")
    for r in prov: f.write("\t".join(r)+"\n")
if fail: sys.exit("FAIL CLOSED: UG5 genealogy in construction")

# frozen anchors (recomputed, must match the landed set)
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
landed=[int(l.split('\t')[2]) for l in open(f"{TABLES}/ug5_frozen_anchor_coordinates.tsv") if not l.startswith("anchor_index")]
if sorted(landed)!=ANCH:
    aud.add("frozen_anchor_set","matches the landed 150",f"{len(ANCH)} vs {len(landed)}","v3","frame drift","FAIL CLOSED","YES")
    sys.exit("FAIL CLOSED: anchor set differs from the landed frozen set")

def place(sid,seq,tag,outdir):
    fp=f"{outdir}/{tag}.faa"; write_fasta({sid:seq},fp)
    dom=f"{outdir}/{tag}.domtbl"
    run([BIN+"hmmsearch","--max","-E",HMMSEARCH_E,"--noali","--domtblout",dom,f"{G4AWORK}/{REF}.deriv.hmm",fp])
    cand=collections.defaultdict(list)
    ndom=0; nqual=0
    for line in open(dom):
        if line.startswith("#"): continue
        p=line.split(); sc=float(p[13]); ndom+=1
        if sc<MIN_SCORE: continue
        nqual+=1
        hs,he,as_,ae=int(p[15]),int(p[16]),int(p[17]),int(p[18])
        for a in ANCH:
            if hs<=a<=he:
                fr=(a-hs)/max(1,(he-hs)); cand[a].append((as_+fr*(ae-as_),sc))
    placed,ambig={},set()
    for a,lst in cand.items():
        lst.sort(key=lambda x:-x[1]); placed[a]=lst[0]
        if len(lst)>1 and max(abs(lst[0][0]-o[0]) for o in lst[1:])>AMBIG_WINDOW: ambig.add(a)
    return placed,ambig,nqual

def order_stats(placed):
    ks=sorted(placed); v=[placed[k][0] for k in ks]; n=len(v)
    if n<3: return None
    pairs=n*(n-1)//2
    conc=sum(1 for i in range(n) for j in range(i+1,n) if v[j]>v[i])
    tau=(2*conc-pairs)/pairs
    inv=sum(1 for i in range(n-1) if v[i+1]<=v[i])
    tails=[]
    for x in v:
        i=bisect.bisect_left(tails,x)
        if i==len(tails): tails.append(x)
        else: tails[i]=x
    return dict(n=n,tau=tau,inv=inv,mono=1 if inv==0 else 0,lms=len(tails)/n)

# UG5 split (same link rule)
pairs5=all_vs_all(ug5,WORK,"UG5v3"); comps5=components(list(ug5),pairs5)
comp_of={i:ci for ci,c in enumerate(comps5) for i in c}
role={i:("evaluation_reference" if ci==0 else "challenge") for ci,c in enumerate(comps5) for i in c}

rows,seqrows,ordrows,ambrows,absrows=[],[],[],[],[]
os.makedirs(f"{WORK}/v3real",exist_ok=True)
for sid,seq in sorted(ug5.items()):
    pl,amb,ndom=place(sid,seq,f"r_{abs(hash(sid))%10**9}",f"{WORK}/v3real")
    for a,(pos,sc) in sorted(pl.items()):
        rows.append([sid,role[sid],str(comp_of[sid]),str(a),f"{pos:.1f}",f"{sc:.1f}",
                     "AMBIGUOUS" if a in amb else "PLACED"])
    if not pl:
        absrows.append([sid,role[sid],str(comp_of[sid]),
                        "NO_QUALIFYING_DOMAIN" if nqual==0 else "QUALIFYING_DOMAIN_COVERS_NO_ANCHOR"])
    o=order_stats(pl)
    dy=DYAD.search(seq); dyv=""
    if dy:
        dp=dy.start()+1
        dyv="YES" if any(abs(p-dp)<=DYAD_WINDOW for p,_ in pl.values()) else "NO"
    seqrows.append([sid,role[sid],str(comp_of[sid]),str(len(ANCH)),str(len(pl)),
                    f"{100*len(pl)/len(ANCH):.1f}",str(len(amb)),dyv,
                    "ABSTAIN" if not pl else "PLACED",
                    f"{max(s for _,s in pl.values()):.1f}" if pl else ""])
    if o: ordrows.append([sid,role[sid],str(comp_of[sid]),str(o["n"]),f"{o['tau']:.4f}",
                          str(o["inv"]),"MONOTONE" if o["mono"] else "NON_MONOTONE",f"{o['lms']:.4f}"])
    if amb: ambrows.append([sid,str(len(pl)),str(len(amb)),f"{100*len(amb)/len(pl):.1f}"])

# decoys: 3 replicates, EVERY record retained, no file reuse
dec=[]
for rep in range(3):
    random.seed(20260916+rep); os.makedirs(f"{WORK}/v3dec{rep}",exist_ok=True)
    for sid,seq in sorted(ug5.items()):
        s=list(seq.upper()); random.shuffle(s)
        pl,amb,ndom=place(sid,"".join(s),f"d_{abs(hash(sid))%10**9}",f"{WORK}/v3dec{rep}")
        if pl:
            for a,(pos,sc) in sorted(pl.items()):
                dec.append([str(rep),sid,str(a),f"{pos:.1f}",f"{sc:.1f}",
                            "AMBIGUOUS" if a in amb else "PLACED"])
        else:
            dec.append([str(rep),sid,"","","","NO_PLACEMENT"])

for name,data,hdr in [
 ("ug5_v3_anchor_placement.tsv",rows,"sequence_id\tsubset\tcomponent\tanchor_ref_coord\tmapped_position\tdomain_bitscore\tstate\n"),
 ("ug5_v3_sequence_summary.tsv",seqrows,"sequence_id\tsubset\tcomponent\tn_frozen_anchors\tn_placed\tpct_placed\tn_ambiguous\tdyad_within_placed\tverdict\tbest_domain_bitscore\n"),
 ("ug5_v3_order_metrics.tsv",ordrows,"sequence_id\tsubset\tcomponent\tn_anchors\tkendall_tau\tn_inversions\tmonotonicity_DESCRIPTIVE\tlongest_monotone_fraction\n"),
 ("ug5_v3_ambiguity.tsv",ambrows,"sequence_id\tn_placed\tn_ambiguous\tpct_ambiguous\n"),
 ("ug5_v3_abstention.tsv",absrows,"sequence_id\tsubset\tcomponent\treason\n"),
 ("ug5_v3_decoy_results.tsv",dec,"replicate\tsequence_id\tanchor_ref_coord\tmapped_position\tdomain_bitscore\tstate\n")]:
    with open(f"{TABLES}/{name}","w") as f:
        f.write(hdr)
        for r in data: f.write("\t".join(r)+"\n")

comp=[]
for ci,c in enumerate(comps5):
    sub=[r for r in seqrows if r[2]==str(ci)]
    pl=[int(r[4]) for r in sub]
    od=[float(r[4]) for r in ordrows if r[2]==str(ci)]
    comp.append([str(ci),"evaluation_reference" if ci==0 else "challenge",str(len(c)),
                 f"{statistics.median(pl):.0f}",f"{100*statistics.median(pl)/len(ANCH):.1f}",
                 f"{statistics.median(od):.4f}" if od else "",
                 str(sum(1 for r in sub if r[8]=="ABSTAIN")),
                 str(sum(1 for r in sub if r[7]=="YES"))])
with open(f"{TABLES}/ug5_v3_component_summary.tsv","w") as f:
    f.write("component\tsubset\tn_sequences\tmedian_anchors_placed\tmedian_pct_placed\t"
            "median_kendall_tau\tn_abstained\tn_dyad_within_placed\n")
    for r in comp: f.write("\t".join(r)+"\n")
aud.write(f"{TABLES}/ug5_v3_audit.tsv")
rp=[int(r[4]) for r in seqrows]
dseq=collections.defaultdict(int)
for r in dec:
    if r[5]!="NO_PLACEMENT": dseq[(r[0],r[1])]+=1
print(f"REAL   n={len(rp)} median_placed={statistics.median(rp):.0f}/{len(ANCH)} "
      f"({100*statistics.median(rp)/len(ANCH):.1f}%) abstain={sum(1 for r in seqrows if r[8]=='ABSTAIN')}")
print(f"DECOY  {len(ug5)*3} sequence-replicates, with any placement: {len(dseq)} "
      f"({100*len(dseq)/(len(ug5)*3):.2f}%)")
tau=[float(r[4]) for r in ordrows]
print(f"TAU    n={len(tau)} median={statistics.median(tau):.4f} min={min(tau):.4f} "
      f"monotone={sum(1 for r in ordrows if r[6]=='MONOTONE')}/{len(ordrows)}")
