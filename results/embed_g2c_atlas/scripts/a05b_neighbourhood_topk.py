#!/usr/bin/env python
"""embed_g2/a05b - recompute the neighbourhood statistics with type-sharing at EVERY k.

a05 reported type-sharing only at k=1 and k=10, so the figure had no top-5 value and reused
the top-10 one. That is a plotting error, not a finding; this recomputes the missing quantity
from the same frozen M-CCA rather than relabelling the panel. No UMAP, no refit of anything
beyond the already-frozen projection.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from a02_engine import fit_rcca, project

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
df = pd.read_parquet(W / "analysis_pairs.parquet")
RT, NC = np.load(W / "rt_pooled.npy"), np.load(W / "nc_pooled.npy")
cfg = json.loads((W / "selected_config.json").read_text())
tr, te = df[df.fold == "train"], df[df.fold == "test"]
mdl = fit_rcca(RT[tr.rt_row.values], NC[tr.nc_row.values], cfg["k"], cfg["alpha"])
A, B = project(mdl, RT, NC)
te_nc = te.drop_duplicates("nc_row")
nc_rows = te_nc.nc_row.values
nc_type = np.asarray(te_nc.detection_model.values, dtype=object)
q_type = np.asarray(te.detection_model.values, dtype=object)
S = A[te.rt_row.values] @ B[nc_rows].T
order = np.argsort(-S, axis=1)
tcol = np.array([{r: i for i, r in enumerate(nc_rows)}[r] for r in te.nc_row.values])
rank = (S > S[np.arange(len(S)), tcol][:, None]).sum(1) + 1
nb = json.loads((OUT / "g2a_neighbourhood.json").read_text())
for k in (1, 5, 10, 20):
    nb[f"top{k}_fraction_sharing_retron_type"] = round(
        float((nc_type[order[:, :k]] == q_type[:, None]).mean()), 4)
    nb[f"observed_partner_in_top{k}"] = round(float((rank <= k).mean()), 4)
nb["observed_partner_is_nearest"] = nb["observed_partner_in_top1"]
nb["type_sharing_enrichment_vs_prevalence"] = round(
    nb["top10_fraction_sharing_retron_type"] / nb["type_prevalence_in_pool"], 2)
(OUT / "g2a_neighbourhood.json").write_text(json.dumps(nb, indent=2) + "\n")
for k, v in nb.items():
    print(f"  {k}: {v}")
