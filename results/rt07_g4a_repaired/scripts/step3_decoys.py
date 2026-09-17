#!/usr/bin/env python3
"""g4a REPAIRED step 3 - negative controls. SHUF and REV built from derivation sequences.
REV-vs-REV is retained and LABELLED in the table as an invalid negative (a positive control
in disguise: reversing both homologous families preserves mutual correspondence)."""
import sys, os, re, random, itertools, statistics, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from repaired_lib import *          # noqa
WORK, TABLES = sys.argv[1], sys.argv[2]
FAMILIES = ["Retrons","GII","DGRs","CRISPR","UG3","UG5","AbiA"]
random.seed(20260916)
def decoy(fam, mode):
    src = read_fasta(f"{WORK}/{fam}.derivation.faa")
    out = {}
    for k, v in src.items():
        s = list(v.upper())
        if mode == "SHUF": random.shuffle(s)
        else: s = s[::-1]
        out[k] = "".join(s)
    tag = f"{fam}.{mode}"
    write_fasta(out, f"{WORK}/{tag}.faa")
    r = run([BIN+"mafft","--localpair","--maxiterate","1000","--quiet","--thread","1",f"{WORK}/{tag}.faa"])
    open(f"{WORK}/{tag}.afa","w").write(r.stdout)
    run([BIN+"esl-reformat","-o",f"{WORK}/{tag}.sto","stockholm",f"{WORK}/{tag}.afa"])
    run([BIN+"hmmbuild","--amino","-n",f"neg_{tag}",f"{WORK}/{tag}.hmm",f"{WORK}/{tag}.sto"])
    run([BIN+"hhmake","-i",f"{WORK}/{tag}.afa","-o",f"{WORK}/{tag}.hhm","-name",f"neg_{tag}","-M",HHMAKE_M])
    return tag
rows=[]
for mode in ("SHUF","REV"):
    tags={f:decoy(f,mode) for f in FAMILIES}
    valid = "VALID_NEGATIVE" if mode=="SHUF" else "VALID_NEGATIVE"
    for a,b in itertools.permutations(FAMILIES,2):
        o=f"{WORK}/neg_{mode}_rd_{a}__{b}.hhr"
        run([BIN+"hhalign","-i",f"{WORK}/{a}.deriv.hhm","-t",f"{WORK}/{tags[b]}.hhm","-o",o])
        h=hhr_header(o)
        rows.append([mode,"REAL_vs_DECOY",a,b,h[0] if h else "",h[1] if h else "","VALID_NEGATIVE"])
    for a,b in itertools.permutations(FAMILIES,2):
        o=f"{WORK}/neg_{mode}_dd_{a}__{b}.hhr"
        run([BIN+"hhalign","-i",f"{WORK}/{tags[a]}.hhm","-t",f"{WORK}/{tags[b]}.hhm","-o",o])
        h=hhr_header(o)
        lab = "VALID_NEGATIVE" if mode=="SHUF" else "INVALID_NEGATIVE_positive_control_in_disguise"
        rows.append([mode,"DECOY_vs_DECOY",a,b,h[0] if h else "",h[1] if h else "",lab])
with open(f"{TABLES}/g4a_repaired_negative_control.tsv","w") as f:
    f.write("decoy_mode\tcomparison\tfamily_A\tfamily_B\thhalign_probability\thhalign_evalue\tcontrol_validity\n")
    for r in rows: f.write("\t".join(str(x) for x in r)+"\n")
for mode in ("SHUF","REV"):
    for comp in ("REAL_vs_DECOY","DECOY_vs_DECOY"):
        p=[float(r[4]) for r in rows if r[0]==mode and r[1]==comp and r[4]]
        lab=[r[6] for r in rows if r[0]==mode and r[1]==comp][0]
        print(f"{mode:5s} {comp:16s} n={len(p):3d} prob min={min(p):6.1f} median={statistics.median(p):6.1f} max={max(p):6.1f}  [{lab}]")
