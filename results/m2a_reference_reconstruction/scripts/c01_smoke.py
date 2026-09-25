#!/usr/bin/env python3
"""M2c — bounded modern placement smoke test (launcher rev-4 §7c). Purpose: check that the
status rules behave as declared. It is NOT for discovering clades.

Sampling (seed 2026), from the frozen M2B table only. Nearest-reference identity is MMseqs2
`fident` of the MCC-v3.1 extract against the reference extracts (ref/v3_ref.faa); no hit = 0.
  A_IDENT          stratum A, INCLUDED, REF_MESTRE (identical to a clean Mestre protein)   40
  A / B1 / B0      INCLUDED, not REF_MESTRE, by identity bin
                   [0.90,1.00) [0.70,0.90) [0.50,0.70) [0,0.50)       A 30/bin, B1 15/bin, B0 15/bin
  M                20 sampled regardless of inclusion (M has no INCLUDED rows); reported as is
  RNAP             the 15 RNA-polymerase substitutes
  SHUF_A           40 residue-shuffled extracts of sampled A (bin) queries
  NONRETRON        30 Toro-2014 non-retron extracts + 30 stratum-X RTs, from a06's panel
A bin with fewer rows than its quota takes all of them; the shortfall is reported, never
back-filled.
Every row carries the downstream identifiers (evidence lines, ncRNA CM models, family/type
labels, n_genomes). They are NEVER used to place.
"""
import json, os, random, subprocess, sys, time
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mcc_v3, place_full

E = "/home/borg/miniconda3/envs/retron_tradicional/bin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = f"{ROOT}/m2c"; os.makedirs(W, exist_ok=True)
rng = random.Random(2026)
tau = json.load(open(f"{ROOT}/eval/v3_tau_FROZEN.json"))
T = pd.read_csv(f"{ROOT}/m2b/M2B_QUERY_FREEZE.tsv.gz", sep="\t", index_col=0, low_memory=False)
ext = {}
name = None
for l in open(f"{ROOT}/m2b/M2B_extracts.faa"):
    if l.startswith(">"):
        name = l[1:].strip(); ext[name] = ""
    else:
        ext[name] += l.strip()

inc = T[T.inclusion == "INCLUDED"]
qf = f"{W}/inc.faa"; open(qf, "w").write("".join(f">{h}\n{ext[h]}\n" for h in inc.index))
m8 = f"{W}/inc_vs_ref.m8"
subprocess.run([f"{E}/mmseqs", "easy-search", qf, f"{ROOT}/ref/v3_ref.faa", m8, f"{W}/tmp", "--threads", "16", "-s", "7.5",
                "--max-seqs", "20", "--format-output", "query,target,fident,bits"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
best = {}
for l in open(m8):
    q, t, fi, b = l.split("\t")
    if q not in best or float(b) > best[q][1]:
        best[q] = (float(fi), float(b), t)
T["nearest_ref_identity"] = [best.get(h, (0.0,))[0] if h in inc.index else "" for h in T.index]
T["nearest_ref_taxon"] = [best.get(h, ("", "", ""))[2] if h in inc.index else "" for h in T.index]
BINS = [("[0.90,1.00)", 0.90, 1.0), ("[0.70,0.90)", 0.70, 0.90), ("[0.50,0.70)", 0.50, 0.70), ("[0,0.50)", 0.0, 0.50)]

sample, ledger = [], []


def take(df, n, label):
    ids = sorted(df.index); rng.shuffle(ids)
    got = ids[:n]
    ledger.append(dict(stratum_bin=label, quota=n, available=len(ids), taken=len(got), shortfall=n - len(got)))
    sample.extend((h, label) for h in got)


I = T.loc[inc.index]
take(I[(I.stratum == "A") & (I.REF_MESTRE == True)], 40, "A_IDENT")
for st, q in (("A", 30), ("B1", 15), ("B0", 15)):
    sub = I[(I.stratum == st) & (I.REF_MESTRE != True)]
    for lab, lo, hi in BINS:
        idn = sub.nearest_ref_identity.astype(float)
        take(sub[(idn >= lo) & (idn < hi)], q, f"{st}_{lab}")
take(T[T.stratum == "M"], 20, "M")
queries = {h: ext[h] for h, lab in sample if h in ext}
labels = dict(sample)
a_bins = [h for h, lab in sample if lab.startswith("A_[")]
rng.shuffle(a_bins)
for h in a_bins[:40]:
    s = list(ext[h]); rng.shuffle(s)
    queries[f"SHUF_{h}"] = "".join(s); labels[f"SHUF_{h}"] = "SHUF_A"
ledger.append(dict(stratum_bin="SHUF_A", quota=40, available=len(a_bins), taken=min(40, len(a_bins)), shortfall=40 - min(40, len(a_bins))))
C = pd.read_csv(f"{ROOT}/eval/CONTROLS_v3.tsv", sep="\t")
for pn, n in (("NONRETRON_TORO", 30), ("NONRETRON_X", 30), ("RNAP_SUBSTITUTE", 15)):
    ids = sorted(C[C.panel == pn].id); rng.shuffle(ids)
    for i in ids[:n]:
        labels[i] = pn
    ledger.append(dict(stratum_bin=pn, quota=n, available=len(ids), taken=min(n, len(ids)), shortfall=n - min(n, len(ids))))
ctrl_ext = {}
if any(v.startswith("NONRETRON") or v == "RNAP_SUBSTITUTE" for v in labels.values()):
    Cx = C.set_index("id")
    for i, lab in labels.items():
        if lab in ("NONRETRON_TORO", "NONRETRON_X", "RNAP_SUBSTITUTE") and Cx.loc[i, "extraction"] == "EXTRACTED":
            ctrl_ext[i] = True

t0 = time.time()
P = place_full.place(queries, f"{W}/place", threads=16).set_index("query")
dt = time.time() - t0
rows = []
for q, lab in labels.items():
    if lab in ("NONRETRON_TORO", "NONRETRON_X", "RNAP_SUBSTITUTE"):
        c = C.set_index("id").loc[q]
        rows.append(dict(id=q, stratum_bin=lab, status=c.status, best_label=c.get("best_label", ""))); continue
    if q not in queries:
        r = T.loc[q]
        rows.append(dict(id=q, stratum_bin=lab, status="UNABLE_TO_EXTRACT_HISTORICAL_CORE_RELIABLY", inclusion=r.inclusion)); continue
    p = P.loc[q]
    h = q.replace("SHUF_", "")
    r = T.loc[h]
    rows.append(dict(id=q, stratum_bin=lab, status=place_full.status(p, tau), best_label=p.best_label,
                     best_label_lwr=p.get("best_label_lwr", ""), pendant=p.get("pendant", ""), edpl=p.get("edpl", ""),
                     nearest_ref_identity=r.nearest_ref_identity, template=r.mcc_v3_template, template_identity=r.mcc_v3_template_identity,
                     any_DF=r.any_DF, any_PAD=r.any_PAD, any_NC=r.any_NC, ncrna_cm_models=r.ncrna_cm_models,
                     family_label_set=r.family_label_set, type_set_norm_set=r.type_set_norm_set, n_genomes=r.n_genomes))
R = pd.DataFrame(rows)
R.to_csv(f"{W}/M2C_SMOKE_rows.tsv", sep="\t", index=False)
pd.DataFrame(ledger).to_csv(f"{W}/M2C_SAMPLING_LEDGER.tsv", sep="\t", index=False)
S = R.groupby(["stratum_bin", "status"]).size().unstack(fill_value=0)
S.to_csv(f"{W}/M2C_status_by_stratum.tsv", sep="\t")
meta = dict(n_rows=len(R), n_placed=len(queries), place_wall_s=round(dt, 1), s_per_query=round(dt / max(1, len(queries)), 3), tau=tau)
json.dump(meta, open(f"{W}/M2C_META.json", "w"), indent=1)
print(pd.DataFrame(ledger).to_string()); print(S.to_string()); print(meta["n_rows"], meta["n_placed"], meta["s_per_query"])
