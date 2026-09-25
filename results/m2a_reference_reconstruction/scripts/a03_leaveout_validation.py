#!/usr/bin/env python3
"""M2a step 6 — relatedness-blocked leave-out placement validation (PRIMARY) and the
sequence-level random holdout (SECONDARY).

usage: a03_leaveout_validation.py <extractor v3|v2> <design blocked|random> <rep 1..10>

Per replicate:
  1. Withhold >= 10 % of reference taxa by sampling WHOLE 85 %-identity groups (blocked) or
     single taxa (random) uniformly at random. seed = 2026 * 100 + rep; blocked and random
     use disjoint seed offsets. NO clade label enters the split.
  2. Reference = the primary MSA minus withheld rows, dropping columns that become all-gap;
     tree = the pruned published tree minus withheld tips (topology never re-estimated).
  3. raxml-ng --evaluate --model LG+F+R10 on the reduced reference: re-fits branch lengths and
     model parameters without the withheld taxa.
  4. Queries: the withheld extracts, plus a residue-shuffled copy of each (a negative control;
     composition kept, order destroyed; seed-fixed). Aligned by the MODERN QUERY ROUTE:
     `mafft --add <q> --keeplength` into the reduced reference.
  5. epa-ng with the fitted model; `gappa examine edpl` for EDPL.
Writes per-query rows: placement edge, LWR per edge label, pendant length, EDPL. Clade labels
are attached AFTER placement, for edge labelling and evaluation only.
"""
import json, os, random, re, subprocess, sys
from collections import defaultdict
import pandas as pd
from ete3 import Tree

E = "/home/borg/miniconda3/envs/retron_tradicional/bin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ext, design, rep = sys.argv[1], sys.argv[2], int(sys.argv[3])
W = f"{ROOT}/val/{ext}_{design}_r{rep:02d}"; os.makedirs(W, exist_ok=True)


def run(cmd, out=None, log=None):
    """stdout -> out (data); stderr -> log, never into a data file."""
    with (open(out, "w") if out else open(os.devnull, "w")) as fh, \
         (open(log, "w") if log else open(os.devnull, "w")) as lh:
        subprocess.run(cmd, check=True, stdout=fh, stderr=lh)


def fasta(p):
    d, n = {}, None
    for l in open(p):
        l = l.rstrip("\n")
        if l.startswith(">"):
            n = l[1:].split()[0]; d[n] = []
        else:
            d[n].append(l.strip())
    return {k: "".join(v) for k, v in d.items()}


msa = fasta(f"{ROOT}/aln/{ext}_fftns2.afa")
raw = fasta(f"{ROOT}/ref/{ext}_ref.faa")
taxa = sorted(msa)
grp = defaultdict(list)
for l in open(f"{ROOT}/groups2/{ext}_c85_cluster.tsv"):
    a, b = l.split()
    grp[a].append(b)
rng = random.Random(2026 * 100 + rep + (0 if design == "blocked" else 5000))
target = int(round(0.10 * len(taxa)))
held = []
units = [sorted(v) for k, v in sorted(grp.items())] if design == "blocked" else [[t] for t in taxa]
rng.shuffle(units)
for u in units:
    if len(held) >= target:
        break
    held += u
held = sorted(set(held))
keep = [t for t in taxa if t not in set(held)]

cols = [i for i in range(len(msa[keep[0]])) if any(msa[t][i] != "-" for t in keep)]
ref_afa = f"{W}/ref.afa"
with open(ref_afa, "w") as fh:
    for t in keep:
        fh.write(f">{t}\n{''.join(msa[t][i] for i in cols)}\n")
tr = Tree(f"{ROOT}/ref/{ext}_pruned_published.nwk", format=5)
tr.prune(keep, preserve_branch_length=True); tr.unroot()
tr.write(outfile=f"{W}/ref.nwk", format=5)

q = {t: raw[t] for t in held}
srng = random.Random(9000 + rep)
for t in held:
    s = list(raw[t]); srng.shuffle(s); q[f"SHUF_{t}"] = "".join(s)
q_fa = f"{W}/queries.faa"
open(q_fa, "w").write("".join(f">{k}\n{v}\n" for k, v in q.items()))

if not os.path.exists(f"{W}/rx.raxml.bestModel"):
    run([f"{E}/raxml-ng", "--evaluate", "--msa", ref_afa, "--tree", f"{W}/ref.nwk", "--model", "LG+F+R10",
         "--prefix", f"{W}/rx", "--threads", "8", "--redo"], out=f"{W}/raxml.log")
run([f"{E}/mafft", "--add", q_fa, "--keeplength", "--thread", "8", "--anysymbol", ref_afa], out=f"{W}/combined.afa")
comb = fasta(f"{W}/combined.afa")
open(f"{W}/query_aln.afa", "w").write("".join(f">{k}\n{comb[k]}\n" for k in q))
run([f"{E}/epa-ng", "--tree", f"{W}/rx.raxml.bestTree", "--ref-msa", ref_afa, "--query", f"{W}/query_aln.afa",
     "--model", f"{W}/rx.raxml.bestModel", "--outdir", W, "--threads", "8", "--redo"], out=f"{W}/epa.log")
run([f"{E}/gappa", "examine", "edpl", "--jplace-path", f"{W}/epa_result.jplace", "--out-dir", W, "--allow-file-overwriting"],
    out=f"{W}/gappa.log")

# ---- label edges AFTER placement (evaluation), and tabulate -------------------------------
st = pd.read_csv(f"{ROOT}/ref/{ext}_tip_status.tsv", sep="\t")
clade = dict(zip(st.taxon.dropna(), st.loc[st.taxon.notna(), "clade_EVALUATION_ONLY"].astype(str)))
jp = json.load(open(f"{W}/epa_result.jplace"))
nwk = jp["tree"]
edge_tree = Tree(re.sub(r"\{(\d+)\}", r"[&&NHX:edge=\1]", nwk.replace(";", "")) + ";", format=1)
leaves_all = {l.name for l in edge_tree.get_leaves()}
edge_label = {}
for n in edge_tree.traverse():
    if not hasattr(n, "edge"):
        continue
    side = {l.name for l in n.get_leaves()}
    other = leaves_all - side
    lab = "NONE"
    for s in (side, other):
        cs = {clade.get(x, "?") for x in s}
        if len(cs) == 1:
            lab = cs.pop(); break
        if cs <= {"10", "11"}:
            lab = "GRADE_10_11"
    edge_label[int(n.edge)] = lab
fields = jp["fields"]
iE, iL, iP = fields.index("edge_num"), fields.index("like_weight_ratio"), fields.index("pendant_length")
edpl = {}
if os.path.exists(f"{W}/edpl_list.csv"):  # gappa v0.9: Sample,Pquery,Multiplicity,EDPL
    ed = pd.read_csv(f"{W}/edpl_list.csv")
    edpl = dict(zip(ed.Pquery.astype(str), ed.EDPL))
rows = []
placed = set()
for pl in jp["placements"]:
    names = [x if isinstance(x, str) else x[0] for x in pl.get("n", pl.get("nm", []))]
    lw = defaultdict(float)
    for p in pl["p"]:
        lw[edge_label.get(int(p[iE]), "NONE")] += p[iL]
    best = max(pl["p"], key=lambda p: p[iL])
    blab = max(lw, key=lw.get)
    for nm in names:
        placed.add(nm)
        true = clade.get(nm.replace("SHUF_", ""), "?")
        rows.append(dict(extractor=ext, design=design, rep=rep, query=nm, shuffled=nm.startswith("SHUF_"),
                         true_clade_EVALUATION=true, best_label=blab, best_label_lwr=round(lw[blab], 4),
                         best_edge_label=edge_label.get(int(best[iE]), "NONE"), best_edge_lwr=round(best[iL], 4),
                         pendant=best[iP], edpl=edpl.get(nm, ""), n_placements=len(pl["p"]),
                         label_lwr=json.dumps({k: round(v, 4) for k, v in lw.items()})))
for nm in q:
    if nm not in placed:
        rows.append(dict(extractor=ext, design=design, rep=rep, query=nm, shuffled=nm.startswith("SHUF_"),
                         true_clade_EVALUATION=clade.get(nm.replace("SHUF_", ""), "?"), best_label="UNPLACED"))
pd.DataFrame(rows).to_csv(f"{W}/placements.tsv", sep="\t", index=False)
json.dump(dict(ext=ext, design=design, rep=rep, n_taxa=len(taxa), n_held=len(held), n_cols=len(cols)),
          open(f"{W}/meta.json", "w"))
print(ext, design, rep, "held", len(held), "placed", len(placed))
