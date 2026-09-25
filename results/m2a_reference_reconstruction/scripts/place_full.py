#!/usr/bin/env python3
"""Place extracted cores onto the FULL MCC-v3.1 reference: the same route as validation step 6.

  query extract -> mafft --add --keeplength into aln/v3_fftns2.afa
                -> epa-ng on the raxml-ng LG+F+R10 full-reference fit (rx/v3_full)
                -> gappa EDPL -> edge labels attached AFTER placement
Statuses come from a04.status() with the thresholds frozen in eval/v3_tau_FROZEN.json.
"""
import json, os, re, subprocess
from collections import defaultdict
import pandas as pd
from ete3 import Tree

E = "/home/borg/miniconda3/envs/retron_tradicional/bin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLADES = [str(i) for i in range(1, 12)] + ["Orphan"]


def _run(cmd, out=None):
    with (open(out, "w") if out else open(os.devnull, "w")) as fh:
        subprocess.run(cmd, check=True, stdout=fh, stderr=subprocess.DEVNULL)


def _fasta(p):
    d, n = {}, None
    for l in open(p):
        l = l.rstrip("\n")
        if l.startswith(">"):
            n = l[1:].split()[0]; d[n] = []
        else:
            d[n].append(l.strip())
    return {k: "".join(v) for k, v in d.items()}


def place(queries, work, threads=8):
    """queries: {id: extract}. Returns a DataFrame with one row per query."""
    os.makedirs(work, exist_ok=True)
    qf = f"{work}/q.faa"; open(qf, "w").write("".join(f">{k}\n{v}\n" for k, v in queries.items()))
    ref = f"{ROOT}/aln/v3_fftns2.afa"
    _run([f"{E}/mafft", "--add", qf, "--keeplength", "--thread", str(threads), "--anysymbol", ref], out=f"{work}/comb.afa")
    comb = _fasta(f"{work}/comb.afa")
    open(f"{work}/qa.afa", "w").write("".join(f">{k}\n{comb[k]}\n" for k in queries))
    _run([f"{E}/epa-ng", "--tree", f"{ROOT}/rx/v3_full.raxml.bestTree", "--ref-msa", ref, "--query", f"{work}/qa.afa",
          "--model", f"{ROOT}/rx/v3_full.raxml.bestModel", "--outdir", work, "--threads", str(threads), "--redo"])
    _run([f"{E}/gappa", "examine", "edpl", "--jplace-path", f"{work}/epa_result.jplace", "--out-dir", work, "--allow-file-overwriting"])
    st = pd.read_csv(f"{ROOT}/ref/v3_tip_status.tsv", sep="\t", dtype={"clade_EVALUATION_ONLY": str})
    clade = dict(zip(st.taxon.dropna(), st.loc[st.taxon.notna(), "clade_EVALUATION_ONLY"]))
    jp = json.load(open(f"{work}/epa_result.jplace"))
    et = Tree(re.sub(r"\{(\d+)\}", r"[&&NHX:edge=\1]", jp["tree"].replace(";", "")) + ";", format=1)
    allv = {l.name for l in et.get_leaves()}
    elab = {}
    for n in et.traverse():
        if not hasattr(n, "edge"):
            continue
        side = {l.name for l in n.get_leaves()}; lab = "NONE"
        for s in (side, allv - side):
            cs = {clade.get(x, "?") for x in s}
            if len(cs) == 1:
                lab = cs.pop(); break
            if cs <= {"10", "11"}:
                lab = "GRADE_10_11"
        elab[int(n.edge)] = lab
    ed = pd.read_csv(f"{work}/edpl_list.csv")
    edpl = dict(zip(ed.Pquery.astype(str), ed.EDPL))
    f = jp["fields"]; iE, iL, iP = f.index("edge_num"), f.index("like_weight_ratio"), f.index("pendant_length")
    rows, seen = [], set()
    for pl in jp["placements"]:
        lw = defaultdict(float)
        for p in pl["p"]:
            lw[elab.get(int(p[iE]), "NONE")] += p[iL]
        best = max(pl["p"], key=lambda p: p[iL]); blab = max(lw, key=lw.get)
        for nm in [x if isinstance(x, str) else x[0] for x in pl.get("n", pl.get("nm", []))]:
            seen.add(nm)
            rows.append(dict(query=nm, best_label=blab, best_label_lwr=round(lw[blab], 4), pendant=best[iP], edpl=edpl.get(nm, ""),
                             aligned_frac=sum(c not in "-." for c in comb[nm]) / max(1, len(queries[nm])),
                             label_lwr=json.dumps({k: round(v, 4) for k, v in lw.items()})))
    for nm in queries:
        if nm not in seen:
            rows.append(dict(query=nm, best_label="UNPLACED", aligned_frac=0))
    return pd.DataFrame(rows)


def status(r, tau):
    """Identical rule to a04.status (duplicated verbatim; a05 asserts that the two agree)."""
    if r.best_label == "UNPLACED" or r.aligned_frac < 0.5:
        return "UNABLE_TO_ALIGN_OR_PLACE_RELIABLY"
    ok = r.best_label_lwr >= tau["LWR"] and (pd.isna(r.edpl) or r.edpl == "" or float(r.edpl) <= tau["EDPL"])
    if not ok:
        return "AMBIGUOUS"
    if r.best_label == "NONE":
        return "OUTSIDE_WELL_SUPPORTED_HISTORICAL_CLADE_SPACE"
    if r.best_label not in CLADES:
        return "AMBIGUOUS"
    if r.pendant > tau["pend"].get(r.best_label, tau["pend_pooled"]):
        return "OUTSIDE_WELL_SUPPORTED_HISTORICAL_CLADE_SPACE"
    return "CONFIDENTLY_PLACED"
