#!/usr/bin/env python3
"""M2a step 1 — the reference taxon sets, denominator ledger, tip mapping and pruned trees.

For each extractor (v3 = MCC-v3.1 primary; v2 = MCC-v2 required-core sensitivity):
  * input: clean published-accession terminals that the extractor extracted
  * extract: v3 = [start, end] from MCC_V3_per_sequence.tsv; v2 = [core_start_route1,
    core_end_route1] from the MCC-v2 feasibility table (required core only)
  * identical extracts collapse to one reference taxon (representative = lowest node
    number); every terminal -> taxon mapping is kept
  * published tree pruned to the representative tips; the topology is never re-estimated
Clade labels are carried ONLY for the evaluation columns and the K1 monophyly check; they do
not influence which taxa enter.
"""
import csv, glob, hashlib, json, os, sys
import pandas as pd
from ete3 import Tree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references/rt0_rt7/mestre_2020"
D2 = "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences"
AUD = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-mestre-audit/analysis/mestre_audit/m2_design"
OUT = os.path.join(ROOT, "ref"); os.makedirs(OUT, exist_ok=True)

mt = pd.read_csv(f"{REF}/Supp_material_T1_R1_systematic_prediction.csv", encoding="utf-8-sig")
mt = mt[mt.Node.notna()].copy(); mt["Node"] = mt.Node.astype(int)
tree0 = Tree(f"{REF}/Supplementary_mestre_Tree.nwk", format=1, quoted_node_names=True)
tips = {l.name for l in tree0.get_leaves()}
short = mt.Retron_name.astype(str).str.extract(r"\(([^)]+)\)")[0]
mt["tip"] = [a if a in tips else (s if isinstance(s, str) and s in tips else None) for a, s in zip(mt.Accesion.astype(str).str.strip(), short)]
assert mt.tip.notna().all(), "unmapped tips"
mt["terminal"] = "terminal_" + mt.Node.astype(str)
tip_of = dict(zip(mt.terminal, mt.tip)); clade_of = dict(zip(mt.terminal, mt.Clade.astype(str)))

prot = {}
for f in glob.glob(f"{D2}/terminal_*/protein_aminoacid.fasta"):
    L = open(f).read().split("\n")
    prot[f.split("/")[-2]] = ("|rescued" in L[0], "".join(x.strip() for x in L[1:]).rstrip("*").upper())

v3 = pd.read_csv(f"{AUD}/mcc_v3/MCC_V3_per_sequence.tsv", sep="\t").set_index("terminal")
v2 = pd.read_csv(f"{AUD}/mcc_v2/MCC_FEASIBILITY_per_sequence.tsv", sep="\t").set_index("terminal")
ledger = []
for ext in ("v3", "v2"):
    rows, seqs = [], {}
    for _, r in mt.iterrows():
        t = r.terminal
        st = "IN_REFERENCE"
        if t not in prot or prot[t][0]:
            st = "NO_PUBLISHED_PROTEIN"; s = None
        elif ext == "v3":
            x = v3.loc[t]
            if x.mcc_v3_status != "EXTRACTED":
                st = "NO_EXTRACTABLE_CORE:" + str(x.mcc_v3_reason)
            else:
                s = prot[t][1][int(x.start) - 1:int(x.end)]
        else:
            x = v2.loc[t]
            if not str(x.status).startswith("EXTRACTABLE") or str(x.status) == "EXTRACTABLE_MULTI_CORE":
                st = "NO_EXTRACTABLE_CORE:" + str(x.status)
            else:
                s = prot[t][1][int(x.core_start_route1) - 1:int(x.core_end_route1)]
        rows.append(dict(terminal=t, node=r.Node, tip=r.tip, status=st, seq=s if st == "IN_REFERENCE" else None,
                         clade_EVALUATION_ONLY=str(r.Clade)))
    df = pd.DataFrame(rows)
    inref = df[df.status == "IN_REFERENCE"].copy()
    inref["sha"] = inref.seq.map(lambda s: hashlib.sha256(s.encode()).hexdigest())
    rep = inref.sort_values("node").groupby("sha").node.first()
    inref["taxon"] = inref.sha.map(lambda h: f"n{rep[h]}")
    df = df.merge(inref[["terminal", "taxon"]], on="terminal", how="left")
    df.loc[(df.status == "IN_REFERENCE") & (df.taxon != "n" + df.node.astype(str)), "status"] = "DUPLICATE_COLLAPSED"
    df.drop(columns="seq").to_csv(f"{OUT}/{ext}_tip_status.tsv", sep="\t", index=False)
    reps = inref[inref.taxon == "n" + inref.node.astype(str)]
    with open(f"{OUT}/{ext}_ref.faa", "w") as fh:
        for _, r in reps.sort_values("node").iterrows():
            fh.write(f">{r.taxon}\n{r.seq}\n")
    t = tree0.copy()
    keep = set(reps.tip)
    t.prune([l for l in t.get_leaves() if l.name in keep], preserve_branch_length=True)
    rename = dict(zip(reps.tip, reps.taxon))
    for l in t.get_leaves():
        l.name = rename[l.name]
    t.unroot()
    t.write(outfile=f"{OUT}/{ext}_pruned_published.nwk", format=5)
    # K1: unrooted monophyly of each clade on the pruned tree (evaluation labels)
    cl = dict(zip(reps.taxon, reps.clade_EVALUATION_ONLY))
    names = set(cl)
    mono = {}
    for c in sorted(set(cl.values()) - {"Orphan"}, key=lambda x: int(x)):
        members = {n for n, v in cl.items() if v == c}
        ok = len(members) <= 1 or any({l.name for l in node.get_leaves()} in (members, names - members) for node in t.traverse())
        mono[c] = dict(n=len(members), unrooted_monophyletic=bool(ok))
    json.dump(mono, open(f"{OUT}/{ext}_pruned_monophyly_EVALUATION.json", "w"), indent=1)
    c = df.status.str.split(":").str[0].value_counts().to_dict()
    ledger.append(dict(extractor=ext, source_tips=len(df), **{k: int(v) for k, v in c.items()},
                       reference_taxa=len(reps), monophyletic_of_published_10={k: v["unrooted_monophyletic"] for k, v in mono.items()}))
    print(ext, c, "taxa", len(reps), {k: (v["n"], v["unrooted_monophyletic"]) for k, v in mono.items()})
json.dump(ledger, open(f"{OUT}/DENOMINATOR_LEDGER.json", "w"), indent=1, default=str)
