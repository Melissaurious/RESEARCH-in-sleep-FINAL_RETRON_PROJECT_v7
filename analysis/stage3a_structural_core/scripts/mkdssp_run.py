#!/usr/bin/env python3
"""Run the established mkdssp 4.5.5 with an explicit dictionary (the default lookup is broken in
this install: it resolves to a directory). Parse the classic DSSP output by chain + residue."""
import subprocess, os, hashlib
MKDSSP="/home/borg/miniconda3/envs/retron_tradicional/bin/mkdssp"
DIC="/home/borg/miniconda3/envs/retron_tradicional/share/libcifpp/mmcif_pdbx.dic"
def run(cif, out):
    if not os.path.exists(out):
        subprocess.run([MKDSSP,"--mmcif-dictionary",DIC,"--output-format","dssp",cif,out],
                       check=True,capture_output=True,text=True)
    return out
def parse(p, chain=None):
    """-> {(chain, resnum_str): dict(ss8, sheet, bp1, bp2)} from classic DSSP."""
    out={}; on=False
    for l in open(p,errors="ignore"):
        if l.startswith("  #  RESIDUE"): on=True; continue
        if not on or len(l)<40 or l[13]=="!": continue
        ch=l[11]
        if chain is not None and ch!=chain: continue
        key=(ch, l[5:11].strip())
        out[key]=dict(ss8=(l[16] if l[16]!=" " else "-"), sheet=l[33].strip(),
                      bp1=l[25:29].strip(), bp2=l[29:33].strip())
    return out
def three(c): return "H" if c in "HGI" else ("E" if c in "EB" else "C")
