#!/usr/bin/env python3
"""Stage 3A g2 step 1 — per-chain coordinate extracts and all-vs-all structural alignment.

Pinned foldseek build only. Residues keep their author numbering so every alignment column
maps back to the register without a renumbering table.
"""
import gemmi, csv, os, sys, subprocess
ROOT="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit"
OUT=ROOT+"/analysis/stage3a_structural_core"
T=os.environ["TMPDIR"]+"/s3a"
CH=T+"/chains"; os.makedirs(CH,exist_ok=True)
FOLDSEEK="/home/borg/miniconda3/envs/esmologs/bin/foldseek"
reg=list(csv.DictReader(open(OUT+"/STRUCTURE_REGISTER.tsv"),delimiter="\t"))
cache={}
for r in reg:
    f=r["source_file"]
    if f not in cache:
        st=gemmi.read_structure(f); st.setup_entities(); st.remove_alternative_conformations(); cache[f]=st
    st=cache[f]
    sel=gemmi.Selection(f"/1/{r['chain']}")
    sub=sel.copy_structure_selection(st)
    sub.remove_ligands_and_waters()
    sub.setup_entities()
    out=f"{CH}/{r['pdb_id']}_{r['chain']}.pdb"
    if not os.path.exists(out): sub.write_pdb(out)
print("chain files:",len(os.listdir(CH)))
aln=T+"/ava.tsv"
if not os.path.exists(aln):
    cmd=[FOLDSEEK,"easy-search",CH,CH,aln,T+"/tmp",
         "--alignment-type","1","-e","inf","--exhaustive-search","1","--tmscore-threshold","0.0",
         "--max-seqs","200","--format-output",
         "query,target,qstart,qend,tstart,tend,qaln,taln,alntmscore,lddt,alnlen","-v","1"]
    print(" ".join(cmd))
    subprocess.run(cmd,check=True,capture_output=True,text=True)
print("alignment rows:",sum(1 for _ in open(aln)))
