#!/usr/bin/env python3
"""M2a controls (K3), on the full MCC-v3.1 reference with the frozen thresholds.

Panels (declared in launcher rev-4 7a.7):
  NONRETRON_TORO   every Toro 2014 extract joined to a non-'Retrons' Table S1 class (the 57
                   unjoined extracts have no class and are excluded, stated)
  NONRETRON_X      500 exact RTs from census stratum X (no retron evidence), random, seed 2026
  RNAP_SUBSTITUTE  the 15 RNA-polymerase 'Mestre RTs'. Expected: never reach placement
  OTHER_SUBSTITUTE the 97 other rescued substitutes. Reported separately; never in the reference
Each panel runs MCC-v3.1 extraction in modern mode first. Only extracted cores are placed.
K3 fails if > 5 % of the NONRETRON panels combined are CONFIDENTLY_PLACED, counted over
ALL panel members (the unextractable ones count as not placed), or if any RNAP substitute
is placed at all.
"""
import glob, json, os, random, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mcc_v3, place_full

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-mestre-audit"
TORO = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references/rt0_rt7/historical/toro_2014_Rt0-Rt7.FASTA"
D2 = "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences"
tau = json.load(open(f"{ROOT}/eval/v3_tau_FROZEN.json"))

t14 = pd.read_csv(f"{AUD}/analysis/mestre_audit/m2_design/toro_crosswalk/TORO2014_FASTA_x_TABLES1.tsv", sep="\t")
nonret = set(t14.loc[t14.s1_rt_phylogeny.notna() & (t14.s1_rt_phylogeny != "Retrons"), "fasta_index"])
recs = []
for l in open(TORO, encoding="utf-8", errors="replace"):
    if l.startswith(">"):
        recs.append([l, ""])
    else:
        recs[-1][1] += l.strip()
panel = {}
for i, (h, s) in enumerate(recs, 1):
    if i in nonret:
        panel[f"TORO_NR_{i}"] = ("NONRETRON_TORO", s.replace("-", "").replace(".", "").upper())
cen = pd.read_csv(f"{AUD}/ARIS_OUTPUT/mestre_audit/m2b_census_per_rt.tsv.gz", sep="\t", index_col=0)
xs = sorted(cen.index[cen.stratum == "X"])
random.Random(2026).shuffle(xs)
pick = set(xs[:500])
ex = pd.read_parquet("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_exact_v1.parquet", columns=["rt_seq_hash", "rt_seq"])
for h, s in ex[ex.rt_seq_hash.isin(pick)].itertuples(index=False):
    panel[f"X_{h[:16]}"] = ("NONRETRON_X", s.upper().rstrip("*"))
rn = set(pd.read_csv(f"{AUD}/analysis/mestre_audit/subaudits/v2_v3_v5/v235_rnap_substitutes.tsv", sep="\t").terminal)
for f in glob.glob(f"{D2}/terminal_*/protein_aminoacid.fasta"):
    L = open(f).read().split("\n")
    if "|rescued" in L[0]:
        t = f.split("/")[-2]
        panel[t] = ("RNAP_SUBSTITUTE" if t in rn else "OTHER_SUBSTITUTE", "".join(x.strip() for x in L[1:]).rstrip("*").upper())

res = mcc_v3.extract({k: v[1] for k, v in panel.items()}, f"{ROOT}/work_controls", threads=8)
ext = {k: r["seq"] for k, r in res.items() if r["status"] == "EXTRACTED"}
P = place_full.place(ext, f"{ROOT}/work_controls/place") if ext else pd.DataFrame(columns=["query"])
P = P.set_index("query") if len(P) else P
rows = []
for k, (pn, _) in panel.items():
    r = res[k]
    if r["status"] != "EXTRACTED":
        rows.append(dict(id=k, panel=pn, extraction=r["status"] + ":" + r.get("reason", ""), status="NOT_PLACED_NO_EXTRACT")); continue
    p = P.loc[k]
    rows.append(dict(id=k, panel=pn, extraction="EXTRACTED", template=r["template"], template_identity=r["template_identity"],
                     best_label=p.best_label, best_label_lwr=p.get("best_label_lwr", ""), pendant=p.get("pendant", ""),
                     edpl=p.get("edpl", ""), status=place_full.status(p, tau)))
C = pd.DataFrame(rows)
C.to_csv(f"{ROOT}/eval/CONTROLS_v3.tsv", sep="\t", index=False)
S = C.groupby(["panel", "status"]).size().unstack(fill_value=0)
print(S.to_string())
nr = C[C.panel.str.startswith("NONRETRON")]
conf = (nr.status == "CONFIDENTLY_PLACED").mean()
rnap_placed = int(((C.panel == "RNAP_SUBSTITUTE") & (C.status != "NOT_PLACED_NO_EXTRACT")).sum())
K3 = dict(nonretron_n=len(nr), nonretron_confident=round(float(conf), 4), nonretron_pass=bool(conf <= 0.05),
          rnap_placed=rnap_placed, rnap_pass=rnap_placed == 0,
          by_panel=C.groupby("panel").status.value_counts().unstack(fill_value=0).to_dict(orient="index"))
json.dump(K3, open(f"{ROOT}/eval/CONTROLS_v3_K3.json", "w"), indent=1)
print(json.dumps({k: v for k, v in K3.items() if k != "by_panel"}, indent=1))
