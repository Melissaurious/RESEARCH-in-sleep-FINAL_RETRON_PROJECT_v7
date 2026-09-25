#!/usr/bin/env python
"""embed_x1/x08 - figures. Renders only from work/hist_*.json and tables/."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, pandas as pd

TASK = Path(__file__).resolve().parents[1]
W, OUT, FIG = TASK / "work", TASK / "tables", TASK / "figures"
PAL = {"U": "#BBBBBB", "T": "#E69F00", "R": "#0072B2"}
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 300, "font.size": 8,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white", "savefig.facecolor": "white"})

FIG.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(1, 4, figsize=(15, 3.6))

# (a) learning curves
for arm in "UTR":
    h = json.load(open(W / f"hist_{arm}.json"))
    e = [x["epoch"] for x in h["history"]]
    ax[0].plot(e, [x["train_nll"] for x in h["history"]], "--", c=PAL[arm], lw=1, alpha=.65)
    ax[0].plot(e, [x["val_nll"] for x in h["history"]], "-", c=PAL[arm], lw=1.6,
               label=f"{arm} (best ep {h['best_epoch']})")
    ax[0].scatter([h["best_epoch"]], [h["best_val_nll"]], c=PAL[arm], s=28, zorder=5,
                  edgecolor="white", lw=.6)
ax[0].set_xlabel("epoch"); ax[0].set_ylabel("per-nucleotide NLL (nats)")
ax[0].set_title("Learning curves\n(dashed = train, solid = validation)")
ax[0].legend(frameon=False, fontsize=6.5)

# (b) test NLL with component CIs
a = pd.read_csv(OUT / "x1_arms.tsv", sep="\t").set_index("arm").loc[["U", "T", "R"]]
x = np.arange(3)
ax[1].bar(x, a.test_nll_component_mean, .55, color=[PAL[i] for i in a.index])
ax[1].errorbar(x, a.test_nll_component_mean,
               yerr=[a.test_nll_component_mean - a.ci_lo, a.ci_hi - a.test_nll_component_mean],
               fmt="none", ecolor="#333", lw=1, capsize=3)
for xi, v in zip(x, a.test_nll_component_mean):
    ax[1].text(xi, v + .004, f"{v:.4f}", ha="center", fontsize=7)
ax[1].set_xticks(x); ax[1].set_xticklabels(["U\nRNA-only", "T\ntype-cond.", "R\nRT-cond."])
ax[1].set_ylim(1.30, 1.44); ax[1].set_ylabel("test NLL (component mean, 95 % CI)")
ax[1].set_title("Held-out per-nucleotide NLL")

# (c) paired per-component differences
c = pd.read_csv(OUT / "x1_comparisons.tsv", sep="\t")
lab = list(c.comparison); y = np.arange(len(lab))
ax[2].barh(y, c["diff"], .5, color=["#999999", "#56B4E9", "#0072B2"])
ax[2].errorbar(c["diff"], y, xerr=[c["diff"] - c.ci_lo, c.ci_hi - c["diff"]],
               fmt="none", ecolor="#333", lw=1, capsize=3)
ax[2].axvline(0, c="#666", lw=.8)
ax[2].set_yticks(y); ax[2].set_yticklabels(lab)
ax[2].set_xlabel("Δ NLL (negative = first arm better)")
ax[2].set_title("Paired per-component differences\n(bootstrap over components)")

# (d) counterfactual
cf = json.load(open(OUT / "x1_counterfactual.json"))
ax[3].axvline(0, c="#666", lw=.8)
ax[3].barh([0], [cf["delta_logP_per_nt"]], .4, color="#009E73")
ax[3].errorbar([cf["delta_logP_per_nt"]], [0],
               xerr=[[cf["delta_logP_per_nt"] - cf["ci_lo"]],
                     [cf["ci_hi"] - cf["delta_logP_per_nt"]]],
               fmt="none", ecolor="#333", lw=1, capsize=3)
ax[3].set_yticks([0]); ax[3].set_yticklabels(["observed RT\nvs same-type\nalternative"])
ax[3].set_xlabel("Δ log P per nt (positive favours the observed RT)")
ax[3].set_title(f"Same-type counterfactual control\n{cf['n_eligible']:,} pairs, "
                f"{cf['n_alternatives']} alternatives, {cf['n_components']} components")
ax[3].text(cf["delta_logP_per_nt"] / 2, .28,
           f"{100*cf['frac_pairs_favouring_observed']:.0f} % of pairs\nfavour observed",
           ha="center", fontsize=6.5)

fig.suptitle("embed_x1 — RT-conditioned ncRNA generation pilot: R (RT-conditioned) improves on "
             "T (retron-type-conditioned), and observed-RT conditioning beats same-type "
             "alternatives", y=1.03, fontsize=8.5)
fig.tight_layout(); fig.savefig(FIG / "x1_summary.png", bbox_inches="tight")
print("wrote figures/x1_summary.png")
