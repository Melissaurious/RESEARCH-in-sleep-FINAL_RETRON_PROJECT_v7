#!/usr/bin/env python3
"""Toro 2014 <-> Toro tree <-> Mestre 2020 crosswalk, plus a source-stated boundary test for MCC.

Read-only on every source. No Mestre clade label is used to build anything here: clade
appears only as a carried-through column of the crosswalk, for later evaluation.

A. Toro 2014 FASTA (742 aligned RT0-RT7 extracts) joined to Table S1. The key type is chosen
   from the header form:
     gi|<GI>|ref|<ACC>|_extraction   -> GenBank GI (fallback: accession)
     fid|<PATRIC fid>|locus|...      -> Patric Code (fid)
     <GIIdb name>/<acc>/...          -> 'GII database/[28]' name
B. Suppl_Toro_Tree.txt tips ('<accession> | <species>') and Mestre tree tips, each against the
   Mestre per-tip table (Node, Accesion, Retron_name). Identifier-level only.
C. Toro 2014 ungapped extracts -> clean published-accession Mestre proteins, BY SEQUENCE:
   an exact substring test, plus MMseqs2 (extract as query). A pair is MAPPED when identity is
   >= 0.95 and extract coverage >= 0.95. Its Mestre-protein start/end is then the Toro
   SOURCE-STATED RT0-RT7 interval on that protein (extended by any unaligned extract ends).
D. For mapped clean Mestre proteins, compare the MCC-v1/v2 extracted windows and the MCC-v2
   required-core bounds (from m06/m07 outputs) against the source-stated interval.
"""
import csv, glob, hashlib, os, re, subprocess, sys
from collections import Counter, defaultdict
import pandas as pd

ENV = "/home/borg/miniconda3/envs/retron_tradicional/bin"
REF = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references/rt0_rt7"
TORO = f"{REF}/historical/toro_2014_Rt0-Rt7.FASTA"
S1 = f"{REF}/historical/TableS1_Toro_2014.XLSX"
TTREE = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material/Suppl_Toro_Tree.txt"
MTREE = f"{REF}/mestre_2020/Supplementary_mestre_Tree.nwk"
MTAB = f"{REF}/mestre_2020/Supp_material_T1_R1_systematic_prediction.csv"
D2 = "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences"
MCC = {"v1": "analysis/mestre_audit/m2_design/mcc_v1/MCC_FEASIBILITY_per_sequence.tsv",
       "v2": "analysis/mestre_audit/m2_design/mcc_v2/MCC_FEASIBILITY_per_sequence.tsv"}
WORK, OUT = sys.argv[1], sys.argv[2]
os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True)
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()


def fasta(p):
    out, name, buf = [], None, []
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if line.startswith(">"):
            if name is not None:
                out.append((name, "".join(buf)))
            name, buf = line[1:], []
        else:
            buf.append(line.strip())
    if name is not None:
        out.append((name, "".join(buf)))
    return out


def tips(nwk):
    """Terminal names via a real Newick parser. A quote-regex mis-pairs labels that contain an
    apostrophe (found on the Toro tree: it returned 9,165 fragments, many of them branch-length
    junk)."""
    from Bio import Phylo
    return [c.name for c in Phylo.read(nwk, "newick").get_terminals()]


def base(acc):
    return str(acc).strip().split(".")[0] if acc is not None else ""


# ---------------- A. Toro 2014 FASTA x Table S1 ------------------------------------------
s1 = pd.read_excel(S1, sheet_name=0)
s1["_gi"] = s1["GenBank GI"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
s1["_fid"] = s1["Patric Code (fid)"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
s1["_acc"] = s1["Accesion"].astype(str).str.strip().map(base)
s1["_gii"] = s1["GII database/[28]"].astype(str).str.strip()
idx = {k: {v: i for i, v in s1[k].items() if v and v != "nan"} for k in ("_gi", "_fid", "_acc", "_gii")}
toro = fasta(TORO)
A = []
for n, (h, aln) in enumerate(toro):
    hid = h.split()[0]
    f = hid.split("|")
    if f[0] == "gi":
        kt, key, row = "gi", f[1], idx["_gi"].get(f[1])
        if row is None and len(f) > 3:
            kt, key, row = "accession", base(f[3]), idx["_acc"].get(base(f[3]))
    elif f[0].endswith("fid"):  # 'fid', 'Afid', 'Gfid', 'cianobacteriafid', ... = taxon-group tag + fid
        kt, key, row = "patric_fid", f[1], idx["_fid"].get(f[1])
    else:
        kt, key = "gii_db_name", hid.split("/")[0]
        row = idx["_gii"].get(key)
    ung = aln.replace("-", "").replace(".", "").upper()
    cols = [i + 1 for i, c in enumerate(aln) if c not in "-."]
    r = s1.loc[row] if row is not None else None
    A.append(dict(fasta_index=n + 1, header=hid, key_type=kt, key=key, s1_row=(row + 2) if row is not None else "",
                  s1_rt_phylogeny=r["RT phylogeny"] if r is not None else "", s1_rt_class=r["RT class"] if r is not None else "",
                  s1_accession=r["Accesion"] if r is not None else "", s1_species=r["Species"] if r is not None else "",
                  aln_len=len(aln), n_residues=len(ung), first_col=cols[0] if cols else "", last_col=cols[-1] if cols else "",
                  n_gap_chars=len(aln) - len(ung), extract_sha256=sha(ung)))
pd.DataFrame(A).to_csv(f"{OUT}/TORO2014_FASTA_x_TABLES1.tsv", sep="\t", index=False)

# ---------------- B. trees x Mestre table ------------------------------------------------
mt = pd.read_csv(MTAB, encoding="utf-8-sig")
mt = mt[mt["Node"].notna()].copy()
mt["Node"] = mt["Node"].astype(int)
mt["_acc"] = mt["Accesion"].astype(str).str.strip()
short = mt["Retron_name"].astype(str).str.extract(r"\(([^)]+)\)")[0]
ttips = tips(TTREE)
tacc = {t.split("|")[0].strip() if not t.startswith("fig|") else "|".join(t.split("|")[:2]).strip() for t in ttips}
tacc_base = {base(a) if not a.startswith("fig|") else a for a in tacc}
mtips = tips(MTREE)
B = []
for _, r in mt.iterrows():
    a = r["_acc"]
    in_mtree = (a in mtips) or (isinstance(short[_], str) and short[_] in mtips)
    in_ttree = (a in tacc) or ((base(a) if not a.startswith("fig|") else a) in tacc_base)
    B.append(dict(node=r["Node"], mestre_accession=a, retron_name=r["Retron_name"] if isinstance(r["Retron_name"], str) else "",
                  clade_EVALUATION_ONLY=r["Clade"], in_mestre_tree=in_mtree, in_toro_tree=in_ttree))
Bd = pd.DataFrame(B)

# ---------------- C. Toro 2014 extracts -> clean Mestre proteins by sequence -------------
clean = {}
for f in sorted(glob.glob(f"{D2}/terminal_*/protein_aminoacid.fasta")):
    L = open(f).read().split("\n")
    if "|rescued" in L[0]:
        continue
    clean[f.split("/")[-2]] = "".join(x.strip() for x in L[1:]).rstrip("*").upper()
q, t = f"{WORK}/toro_extracts.faa", f"{WORK}/mestre_clean.faa"
with open(q, "w") as fh:
    for a in A:
        pass
    for n, (h, aln) in enumerate(toro):
        fh.write(f">T{n + 1}\n{aln.replace('-', '').replace('.', '').upper()}\n")
with open(t, "w") as fh:
    for k, s in clean.items():
        fh.write(f">{k}\n{s}\n")
m8 = f"{WORK}/toro_vs_mestre.m8"
subprocess.run([f"{ENV}/mmseqs", "easy-search", q, t, m8, f"{WORK}/tmp", "--threads", "8", "-s", "7.5",
                "--format-output", "query,target,fident,alnlen,qstart,qend,qlen,tstart,tend,tlen,evalue,bits",
                "--max-seqs", "50"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
hits = defaultdict(list)
for line in open(m8):
    p = line.split("\t")
    qs, qe, ql, ts, te = int(p[4]), int(p[5]), int(p[6]), int(p[7]), int(p[8])
    hits[p[0]].append(dict(target=p[1], fident=float(p[2]), qcov=(qe - qs + 1) / ql, qs=qs, qe=qe, ql=ql, ts=ts, te=te,
                           tlen=int(p[9]), bits=float(p[11])))
C = []
toro_seq = {f"T{n + 1}": aln.replace("-", "").replace(".", "").upper() for n, (h, aln) in enumerate(toro)}
node_of = {f"terminal_{int(r['node'])}": r for r in B}
for n, a in enumerate(A):
    tid = f"T{n + 1}"
    ex = toro_seq[tid]
    subs = [k for k, s in clean.items() if ex and ex in s]
    for h in sorted(hits.get(tid, []), key=lambda x: -x["bits"]):
        mapped = h["fident"] >= 0.95 and h["qcov"] >= 0.95
        # source-stated interval on the Mestre protein, extended by unaligned extract ends
        s_start = max(1, h["ts"] - (h["qs"] - 1)); s_end = min(h["tlen"], h["te"] + (h["ql"] - h["qe"]))
        mr = node_of.get(h["target"], {})
        C.append(dict(toro_index=n + 1, toro_header=a["header"], s1_rt_phylogeny=a["s1_rt_phylogeny"],
                      mestre_terminal=h["target"], mestre_accession=mr.get("mestre_accession", ""),
                      clade_EVALUATION_ONLY=mr.get("clade_EVALUATION_ONLY", ""), fident=h["fident"], extract_coverage=round(h["qcov"], 4),
                      exact_substring=h["target"] in subs, mapped=mapped, toro_stated_start=s_start, toro_stated_end=s_end,
                      extract_len=h["ql"], extract_sha256=a["extract_sha256"], mestre_protein_sha256=sha(clean[h["target"]])))
Cd = pd.DataFrame(C)
Cd.to_csv(f"{OUT}/TORO2014_x_MESTRE2020_CROSSWALK.tsv", sep="\t", index=False)

# ---------------- D. MCC windows vs the source-stated interval ---------------------------
Mp = Cd[Cd.mapped].sort_values("fident", ascending=False).drop_duplicates("mestre_terminal")
D = []
for v, p in MCC.items():
    m = pd.read_csv(p, sep="\t").set_index("terminal")
    for _, r in Mp.iterrows():
        if r.mestre_terminal not in m.index:
            continue
        x = m.loc[r.mestre_terminal]
        ok = str(x.status).startswith("EXTRACTABLE")
        D.append(dict(mcc=v, mestre_terminal=r.mestre_terminal, toro_index=r.toro_index, fident=r.fident, mcc_status=x.status,
                      toro_start=r.toro_stated_start, toro_end=r.toro_stated_end,
                      mcc_window_start=x.mcc_start if ok else "", mcc_window_end=x.mcc_end if ok else "",
                      d_window_start=(int(x.mcc_start) - r.toro_stated_start) if ok else "",
                      d_window_end=(int(x.mcc_end) - r.toro_stated_end) if ok else "",
                      core_start=x.core_start_route1 if ok else "", core_end=x.core_end_route1 if ok else "",
                      core_inside_toro=(ok and int(x.core_start_route1) >= r.toro_stated_start and int(x.core_end_route1) <= r.toro_stated_end)))
Dd = pd.DataFrame(D)
Dd.to_csv(f"{OUT}/MCC_vs_TORO_STATED_BOUNDARIES.tsv", sep="\t", index=False)

# ---------------- summary ----------------------------------------------------------------
S = []
S.append(("toro2014_fasta_sequences", len(A)))
S.append(("toro2014_aligned_columns", sorted({a["aln_len"] for a in A})))
S.append(("toro2014_joined_to_TableS1", sum(1 for a in A if a["s1_row"] != "")))
S.append(("toro2014_join_key_types", dict(Counter(a["key_type"] for a in A))))
S.append(("toro2014_by_S1_phylogeny", dict(Counter(a["s1_rt_phylogeny"] for a in A))))
S.append(("toro2014_distinct_extract_sequences", len({a["extract_sha256"] for a in A})))
S.append(("toro_tree_tips", len(ttips)))
S.append(("mestre_tree_tips", len(mtips)))
S.append(("mestre_table_rows_with_node", len(Bd)))
S.append(("mestre_rows_in_mestre_tree", int(Bd.in_mestre_tree.sum())))
S.append(("mestre_rows_in_toro_tree_by_identifier", int(Bd.in_toro_tree.sum())))
S.append(("clean_mestre_proteins", len(clean)))
mp = Cd[Cd.mapped]
S.append(("toro2014_extracts_mapped_to_a_clean_mestre_protein", mp.toro_index.nunique()))
S.append(("  of_which_retrons", mp[mp.s1_rt_phylogeny == "Retrons"].toro_index.nunique()))
S.append(("  of_which_exact_substring", mp[mp.exact_substring].toro_index.nunique()))
S.append(("  mapped_non_retron_classes", dict(Counter(mp.drop_duplicates("toro_index").s1_rt_phylogeny))))
S.append(("clean_mestre_proteins_with_a_toro2014_extract", mp.mestre_terminal.nunique()))
for v in MCC:
    d = Dd[(Dd.mcc == v) & (Dd.d_window_start != "")]
    if len(d):
        ds, de = d.d_window_start.astype(int), d.d_window_end.astype(int)
        S.append((f"{v}: n_compared (extractable)", len(d)))
        S.append((f"{v}: window_start - toro_start  median / |d|<=5 frac", f"{ds.median()} / {(ds.abs() <= 5).mean():.3f}"))
        S.append((f"{v}: window_end - toro_end      median / |d|<=5 frac", f"{de.median()} / {(de.abs() <= 5).mean():.3f}"))
        S.append((f"{v}: required core inside toro interval", f"{d.core_inside_toro.mean():.3f}"))
    S.append((f"{v}: mapped proteins not extractable", int(((Dd.mcc == v) & (Dd.d_window_start == "")).sum())))
with open(f"{OUT}/TORO_MESTRE_SUMMARY.tsv", "w") as fh:
    for k, v in S:
        fh.write(f"{k}\t{v}\n")
print(open(f"{OUT}/TORO_MESTRE_SUMMARY.tsv").read())
