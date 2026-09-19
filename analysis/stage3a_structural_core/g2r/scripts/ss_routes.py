#!/usr/bin/env python3
"""g2r secondary structure, routes A (mkdssp 4.5.5) and B (pydssp 0.9.1), on the single-chain extracts.
Run in env `retron_tradicional`; route B is delegated to env `opencrispr_retrons`.

Residue key = (author seq number, insertion code) of the extract's single chain. The ordered residue list
is every residue carrying a CA, in file order (idx = position in that list; this is the index space the
PDP per-residue table and the Foldseek ordered-index map are checked against).

Per chain writes <out_dir>/<chain>.ss.tsv:
  idx resnum icode resname bb_complete break_before A_dsspnum A_ss8 A_ss3 A_sheet A_bp1_idx A_bp2_idx B_ss3
break_before = 1 when this residue is the first listed or its peptide bond to the previous listed residue is
absent (C(i-1)-N(i) > 2.0 A or either atom missing). Element runs are split there (F6).
A_bp*_idx are mkdssp bridge partners translated from DSSP serial numbers to idx (-1 = none).
Nothing is reused from a previous run: every call recomputes both routes from the extract.

Usage: ss_routes.py <out_dir> <manifest.tsv>   (columns: name, extract, source_cif, chain)
"""
import sys, os, csv, subprocess, hashlib, tempfile
import gemmi

MKDSSP = "/home/borg/miniconda3/envs/retron_tradicional/bin/mkdssp"
DIC = "/home/borg/miniconda3/envs/retron_tradicional/share/libcifpp/mmcif_pdbx.dic"
PYB = "/home/borg/miniconda3/envs/opencrispr_retrons/bin/python"
ROUTE_B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pydssp_route.py")


def three(c):
    return "H" if c in "HGI" else ("E" if c in "EB" else "C")


def residues(pdb):
    st = gemmi.read_structure(pdb)
    st.remove_alternative_conformations()
    assert len(st) >= 1
    model = st[0]
    chains = [c for c in model if any(r.find_atom("CA", "*") for r in c)]
    assert len(chains) == 1, (pdb, [c.name for c in chains])
    res = [r for r in chains[0] if r.find_atom("CA", "*")]
    keys = [(r.seqid.num, r.seqid.icode.strip()) for r in res]
    assert len(set(keys)) == len(keys), pdb
    return st, chains[0].name, res, keys


def run_mkdssp(source_cif, chain, tmp):
    """Route A input: the original deposition mmCIF reduced at the text level to model 1, the chain's polymer
    asym, first altloc ('.' or 'A') -- the same atoms as the extract. (gemmi-written mmCIF lacks
    pdbx_poly_seq_scheme, which makes this mkdssp build fall into its broken dictionary-directory path.)"""
    doc = gemmi.cif.read(source_cif)
    b = doc.sole_block()
    asym = {r[0] for r in b.find("_pdbx_poly_seq_scheme.", ["asym_id", "pdb_strand_id"]) if r[1] == chain}
    assert len(asym) == 1, (source_cif, chain, asym)
    t = b.find("_atom_site.", ["label_asym_id", "pdbx_PDB_model_num", "label_alt_id"])
    first = t[0][1]
    for i in reversed([i for i, r in enumerate(t) if not (r[0] in asym and r[1] == first and r[2] in (".", "A"))]):
        t.remove_row(i)
    t2 = b.find("_pdbx_poly_seq_scheme.", ["asym_id"])
    for i in reversed([i for i, r in enumerate(t2) if r[0] not in asym]):
        t2.remove_row(i)
    cif = os.path.join(tmp, "in.cif")
    doc.write_file(cif)
    out = os.path.join(tmp, "out.dssp")
    subprocess.run([MKDSSP, "--mmcif-dictionary", DIC, "--output-format", "dssp", cif, out],
                   check=True, capture_output=True, text=True)
    rec, on = {}, False
    for l in open(out, errors="ignore"):
        if l.startswith("  #  RESIDUE"):
            on = True
            continue
        if not on or len(l) < 40 or l[13] == "!":
            continue
        rec[(int(l[5:10]), l[10].strip())] = dict(num=int(l[0:5]), ss8=(l[16] if l[16] != " " else "-"),
                                                  sheet=l[33].strip(), bp1=int(l[25:29]), bp2=int(l[29:33]))
    return rec


def main():
    out_dir, manifest = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    for m in csv.DictReader(open(manifest), delimiter="\t"):
        name, pdb = m["name"], m["extract"]
        st, ch, res, keys = residues(pdb)
        rows = []
        prevC = None
        for i, r in enumerate(res):
            at = {a: r.find_atom(a, "*") for a in ("N", "CA", "C", "O")}
            bb = all(at.values())
            brk = 1 if (i == 0 or prevC is None or at["N"] is None or prevC.pos.dist(at["N"].pos) > 2.0) else 0
            prevC = at["C"]
            rows.append(dict(idx=i, resnum=keys[i][0], icode=keys[i][1], resname=r.name, bb_complete=int(bb),
                             break_before=brk, at=at))
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            assert ch == m["chain"], (name, ch, m["chain"])
            A = run_mkdssp(m["source_cif"], m["chain"], tmp)
            num2idx = {A[k]["num"]: i for i, k in enumerate(keys) if k in A}
            # route B input: residues with complete backbone, in order; donor disabled after any break
            bpath, opath = os.path.join(tmp, "bb.tsv"), os.path.join(tmp, "b.tsv")
            with open(bpath, "w") as fh:
                fh.write("idx\tdonor_ok\t" + "\t".join(f"{a}_{c}" for a in ("N", "CA", "C", "O") for c in "xyz") + "\n")
                last = None
                for x in rows:
                    if not x["bb_complete"]:
                        last = None
                        continue
                    contiguous = (last is not None and last == x["idx"] - 1 and not x["break_before"])
                    donor = int(contiguous and x["resname"] != "PRO")
                    xyz = [f"{getattr(x['at'][a].pos, c):.3f}" for a in ("N", "CA", "C", "O") for c in "xyz"]
                    fh.write(f"{x['idx']}\t{donor}\t" + "\t".join(xyz) + "\n")
                    last = x["idx"]
            subprocess.run([PYB, ROUTE_B, bpath, opath], check=True, capture_output=True, text=True)
            B = {int(l.split("\t")[0]): l.split("\t")[1].strip() for l in list(open(opath))[1:]}
        with open(os.path.join(out_dir, name + ".ss.tsv"), "w") as fh:
            cols = ["idx", "resnum", "icode", "resname", "bb_complete", "break_before", "A_dsspnum", "A_ss8",
                    "A_ss3", "A_sheet", "A_bp1_idx", "A_bp2_idx", "B_ss3"]
            fh.write("\t".join(cols) + "\n")
            for x in rows:
                a = A.get((x["resnum"], x["icode"]))
                vals = [x["idx"], x["resnum"], x["icode"], x["resname"], x["bb_complete"], x["break_before"],
                        a["num"] if a else "", a["ss8"] if a else "", three(a["ss8"]) if a else "",
                        a["sheet"] if a else "",
                        num2idx.get(a["bp1"], -1) if a else -1, num2idx.get(a["bp2"], -1) if a else -1,
                        B.get(x["idx"], "")]
                fh.write("\t".join(str(v) for v in vals) + "\n")
        print(name, len(rows), "A:", len(A), "B:", len(B), "sha256(extract):",
              hashlib.sha256(open(pdb, "rb").read()).hexdigest()[:16])


if __name__ == "__main__":
    main()
