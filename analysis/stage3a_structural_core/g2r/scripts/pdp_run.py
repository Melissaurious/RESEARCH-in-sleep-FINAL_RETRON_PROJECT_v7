#!/usr/bin/env python3
"""Run the C3r PDP driver on a list of single-chain extracts and collect a combined per-residue table.

variant  primary : BioJava 7.1.4 jars, unmodified            (classpath  lib/*:drv3)
         p4      : same, with p4cls/ (make_pdp_p4.py) first   (classpath  p4cls:lib/*:drv3) — sensitivity only
Writes <out_prefix>.residues.tsv (chain + RunPDP per-residue columns) and <out_prefix>.summary.tsv.

Usage: pdp_run.py <variant> <work_dir> <out_prefix> <chain.pdb> [...]
"""
import sys, os, subprocess, tempfile

JAVA = "/home/borg/miniconda3/envs/retron_tradicional/bin/java"
variant, work, prefix, files = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
cp = {"primary": f"{work}/lib/*:{work}/drv3", "p4": f"{work}/p4cls:{work}/lib/*:{work}/drv3"}[variant]
jtmp = f"{work}/jtmp"
os.makedirs(jtmp, exist_ok=True)
with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as od:
    p = subprocess.run([JAVA, f"-Djava.io.tmpdir={jtmp}", f"-DPDB_DIR={jtmp}", f"-DPDB_CACHE_DIR={jtmp}",
                        "-cp", cp, "RunPDP", od] + files, capture_output=True, text=True)
    summ = [l.split("\t")[1:] for l in p.stdout.splitlines() if l.startswith("SUMMARY\t")]
    if p.returncode != 0 or len(summ) != len(files):
        sys.exit(f"driver failed rc={p.returncode} summaries={len(summ)}/{len(files)}\n{p.stdout[-3000:]}\n{p.stderr[-3000:]}")
    with open(prefix + ".summary.tsv", "w") as fh:
        fh.write("chain\tfile\tn_atoms\tn_domains\tstatus\n")
        for f, n, d, s in summ:
            fh.write(f"{os.path.basename(f)[:-4]}\t{f}\t{n}\t{d}\t{s}\n")
    with open(prefix + ".residues.tsv", "w") as fh:
        fh.write("chain\tidx\tmodel\tauth_chain\tresnum\ticode\tresname\tdomain\n")
        for f in files:
            name = os.path.basename(f)[:-4]
            rp = os.path.join(od, name + ".pdp.tsv")
            if not os.path.exists(rp):
                continue
            for l in list(open(rp))[1:]:
                fh.write(name + "\t" + l)
print(variant, "chains:", len(summ), "status:", sorted({s for *_, s in summ}))
