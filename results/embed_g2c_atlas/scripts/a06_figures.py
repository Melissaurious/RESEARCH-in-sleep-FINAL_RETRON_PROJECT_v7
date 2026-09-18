#!/usr/bin/env python
"""embed_g2/a06 - publication figures. Renders ONLY from the plotdata/ and tables/ files, so
every panel is reproducible without re-running any embedding or model code.

Terminology in all captions and legends: observed pair, mismatched candidate, retrieval decoy,
non-observed pairing, type-matched decoy. Never "negative pair", never "incompatible pair".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

TASK = Path(__file__).resolve().parents[1]
OUT, PLOT, FIG = TASK / "tables", TASK / "plotdata", TASK / "figures"
# Okabe-Ito, colour-blind safe, extended with greys for the long tail of rare types
PAL = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]
GREY = "#BBBBBB"
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 300, "font.size": 8,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 9, "axes.labelsize": 8, "legend.fontsize": 6.5,
                     "figure.facecolor": "white", "savefig.facecolor": "white"})


def type_colours(series, k=7):
    top = series.value_counts().index[:k].tolist()
    cmap = {t: PAL[i] for i, t in enumerate(top)}
    return cmap, top


def scatter_by(ax, d, xc, yc, series, cmap, title, s=2.5):
    other = ~series.isin(cmap)
    ax.scatter(d[xc][other], d[yc][other], s=s, c=GREY, lw=0, alpha=.35, rasterized=True)
    for t, c in cmap.items():
        m = series == t
        ax.scatter(d[xc][m], d[yc][m], s=s, c=c, lw=0, alpha=.8, rasterized=True, label=t)
    ax.set_title(title); ax.set_xticks([]); ax.set_yticks([])


def panel_continuous(ax, d, xc, yc, v, title, cbar_label):
    sc = ax.scatter(d[xc], d[yc], s=2.5, c=v, cmap="viridis", lw=0, alpha=.8, rasterized=True)
    ax.set_title(title); ax.set_xticks([]); ax.set_yticks([])
    cb = plt.colorbar(sc, ax=ax, fraction=.046, pad=.02); cb.set_label(cbar_label, fontsize=7)
    cb.ax.tick_params(labelsize=6)


def fig_modality(tag, label, lenc, lenlab):
    d = pd.read_csv(PLOT / f"atlas_{tag}.tsv", sep="\t")
    cmap, top = type_colours(d.retron_type)
    fig, ax = plt.subplots(1, 4, figsize=(13.5, 3.5))
    scatter_by(ax[0], d, "umap1", "umap2", d.retron_type, cmap, f"{label} — retron type")
    ax[0].legend(loc="upper left", bbox_to_anchor=(0, -.02), ncol=2, frameon=False,
                 markerscale=3, handletextpad=.2, columnspacing=.8)
    tier = np.where(d.T4 == 1, "T4", np.where(d.T3 == 1, "T3",
                    np.where(d.T2 == 1, "T2", np.where(d.T1 == 1, "T1", "other"))))
    tmap = {"T4": PAL[1], "T3": PAL[0], "T2": PAL[2], "T1": PAL[4], "other": GREY}
    scatter_by(ax[1], d, "umap1", "umap2", pd.Series(tier), tmap, f"{label} — T1–T4 tier")
    ax[1].legend(loc="upper left", bbox_to_anchor=(0, -.02), ncol=3, frameon=False, markerscale=3)
    panel_continuous(ax[2], d, "umap1", "umap2", d[lenc], f"{label} — {lenlab}", lenlab)
    sp = d.species.fillna("unassigned")
    scmap, _ = type_colours(sp[sp != "unassigned"], k=6)
    scatter_by(ax[3], d, "umap1", "umap2", sp, scmap, f"{label} — major species (NCBI)")
    ax[3].legend(loc="upper left", bbox_to_anchor=(0, -.02), ncol=2, frameon=False, markerscale=3)
    fig.suptitle(f"{label} embedding atlas — UMAP of frozen pooled representations "
                 f"(n={len(d):,}); grey = types outside the legend", y=1.0, fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / f"fig{'1' if tag=='rt' else '2'}_{tag}_atlas.png", bbox_inches="tight")
    plt.close(fig)


def fig_shared():
    d = pd.read_csv(PLOT / "atlas_shared_cca.tsv", sep="\t")
    cmap, _ = type_colours(d.retron_type)
    rt, nc = d[d.modality == "RT"].set_index("pair_id"), d[d.modality == "ncRNA"].set_index("pair_id")
    fig, ax = plt.subplots(1, 2, figsize=(11, 5))
    for a, draw_seg, ttl in ((ax[0], False, "Shared CCA space — all sampled points"),
                             (ax[1], True, "Observed partners joined (150-pair readable panel)")):
        ids = rt.index if not draw_seg else rt.index[:150]
        if draw_seg:
            for i in ids:
                a.plot([rt.x[i], nc.x[i]], [rt.y[i], nc.y[i]], c="#999999", lw=.35, alpha=.55,
                       zorder=1)
        for t, c in cmap.items():
            for mod, mk, sz in (("RT", "o", 11), ("ncRNA", "^", 13)):
                s = (rt if mod == "RT" else nc).loc[ids]
                m = s.retron_type == t
                a.scatter(s.x[m], s.y[m], s=sz, c=c, marker=mk, lw=.2, edgecolor="white",
                          zorder=2, rasterized=True)
            other = (rt if True else nc)
        for mod, src, mk, sz in (("RT", rt, "o", 11), ("ncRNA", nc, "^", 13)):
            s = src.loc[ids]; m = ~s.retron_type.isin(cmap)
            a.scatter(s.x[m], s.y[m], s=sz, c=GREY, marker=mk, lw=0, alpha=.4, zorder=1,
                      rasterized=True)
        a.set_title(ttl); a.set_xticks([]); a.set_yticks([])
    handles = ([Line2D([], [], marker="o", ls="", color="k", ms=4, label="RT (ESM-C)"),
                Line2D([], [], marker="^", ls="", color="k", ms=4, label="ncRNA (RiNALMo)"),
                Line2D([], [], color="#999999", lw=.8, label="observed pair")]
               + [Line2D([], [], marker="s", ls="", color=c, ms=5, label=t) for t, c in cmap.items()])
    ax[1].legend(handles=handles, loc="center left", bbox_to_anchor=(1.01, .5), frameon=False)
    fig.suptitle("Shared CCA latent space (k=32, α=0.01, fit on training components) — "
                 "marker = modality, colour = retron type", y=1.0, fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "fig3_shared_cca_atlas.png", bbox_inches="tight")
    plt.close(fig)


def fig_similarity_and_retrieval():
    sim = pd.read_csv(PLOT / "similarity_long.tsv", sep="\t")
    st = pd.read_csv(OUT / "g2a_similarity_distributions.tsv", sep="\t")
    lad = pd.read_csv(OUT.parent / "tables" / "g2_test_ladder.tsv", sep="\t")
    nb = json.loads((OUT / "g2a_neighbourhood.json").read_text())
    order = ["observed_pair", "type_matched_decoy", "length_gc_matched_decoy", "random_decoy"]
    nice = {"observed_pair": "observed pair", "type_matched_decoy": "type-matched decoy",
            "length_gc_matched_decoy": "length+GC-matched decoy", "random_decoy": "random decoy"}
    cols = {"observed_pair": PAL[0], "type_matched_decoy": PAL[1],
            "length_gc_matched_decoy": PAL[4], "random_decoy": GREY}

    fig, ax = plt.subplots(1, 3, figsize=(13.5, 3.8))
    for i, k in enumerate(order):
        v = sim.cosine[sim.population == k].values
        ax[0].hist(v, bins=80, density=True, histtype="stepfilled", alpha=.45,
                   color=cols[k], label=nice[k])
    ax[0].set_xlabel("CCA cosine similarity"); ax[0].set_ylabel("density")
    ax[0].set_title("Cross-modal similarity"); ax[0].legend(frameon=False)

    m = lad[(lad.model.isin(["M-CCA", "B-kmer"])) & (lad.status == "OK")]
    rl = ["rung1_random", "rung2_len_gc", "rung3_model", "rung4_nc_cluster",
          "rung5_rt_cluster", "rung6_species"]
    lab = ["1 random", "2 len+GC", "3 retron type", "4 ncRNA cl.", "5 RT cl.", "6 species"]
    x = np.arange(len(rl))
    for mdl, c, off in (("M-CCA", PAL[0], -.16), ("B-kmer", PAL[4], .16)):
        s = m[m.model == mdl].set_index("rung").reindex(rl)
        ax[1].bar(x + off, s.mrr, .32, color=c, label=mdl)
        ax[1].errorbar(x + off, s.mrr, yerr=[s.mrr - s.ci_lo, s.ci_hi - s.mrr],
                       fmt="none", ecolor="#333333", lw=.8, capsize=2)
    ax[1].axhline(0.0900, ls="--", lw=.8, c="#666666")
    ax[1].text(-.45, .097, "chance", fontsize=6, color="#666666", ha="left")
    ax[1].set_ylim(0, .52)
    for xi in x[3:]:
        ax[1].text(xi, .475, "UNDETERMINED", ha="center", fontsize=5.5, color="#B00000",
                   rotation=0, fontweight="bold")
    ax[1].set_xticks(x); ax[1].set_xticklabels(lab, rotation=30, ha="right")
    ax[1].set_ylabel("MRR (component-level, 95 % CI)")
    ax[1].set_title("Retrieval across the candidate ladder"); ax[1].legend(frameon=False)

    ks = ["observed_partner_is_nearest", "observed_partner_in_top5", "observed_partner_in_top10"]
    kl = ["nearest", "top-5", "top-10"]
    ax[2].bar(np.arange(3) - .18, [nb[k] for k in ks], .34, color=PAL[0],
              label="observed partner retrieved")
    ax[2].bar(np.arange(3) + .18,
              [nb["top1_fraction_sharing_retron_type"],
               nb["top5_fraction_sharing_retron_type"],
               nb["top10_fraction_sharing_retron_type"]], .34, color=PAL[1],
              label="neighbour shares retron type")
    ax[2].axhline(nb["type_prevalence_in_pool"], ls="--", lw=.8, c="#666666")
    ax[2].text(2.45, nb["type_prevalence_in_pool"] + .02, "type prevalence", fontsize=6,
               color="#666666", ha="right")
    ax[2].set_xticks(np.arange(3)); ax[2].set_xticklabels(kl)
    ax[2].set_ylabel("fraction"); ax[2].set_ylim(0, 1)
    ax[2].set_title(f"Neighbourhoods in the open {nb['pool_size']:,}-candidate pool")
    ax[2].legend(frameon=False, loc="upper left")
    fig.suptitle("Cross-modal structure is type-associated: the observed partner is the nearest "
                 "cross-modal neighbour for only "
                 f"{100*nb['observed_partner_is_nearest']:.1f} % of queries, while "
                 f"{100*nb['top10_fraction_sharing_retron_type']:.0f} % of top-10 neighbours "
                 "share the query's retron type", y=1.02, fontsize=8.5)
    fig.tight_layout(); fig.savefig(FIG / "fig4_similarity_retrieval.png", bbox_inches="tight")
    plt.close(fig)


def fig_dimensions():
    d = pd.read_csv(OUT / "g2a_cca_dimensions.tsv", sep="\t")
    enc = pd.read_csv(OUT / "g2a_type_encoding.tsv", sep="\t")
    fig, ax = plt.subplots(1, 3, figsize=(13.5, 3.5))
    ax[0].bar(d.dim, d.canonical_corr, color=PAL[0]); ax[0].set_ylim(0, 1)
    ax[0].set_xlabel("canonical dimension"); ax[0].set_ylabel("canonical correlation")
    ax[0].set_title("Canonical correlations (k=32)")
    ax2 = ax[0].twinx(); ax2.plot(d.dim, d.cum_share, c=PAL[1], lw=1.2)
    ax2.set_ylabel("cumulative share of summed corr", color=PAL[1], fontsize=7)
    ax2.tick_params(labelsize=6, colors=PAL[1]); ax2.spines["top"].set_visible(False)
    ax[1].plot(d.dim, d.eta2_retron_type_rt, "o-", ms=3, c=PAL[0], label="RT (ESM-C) dim")
    ax[1].plot(d.dim, d.eta2_retron_type_nc, "^-", ms=3, c=PAL[1], label="ncRNA (RiNALMo) dim")
    ax[1].set_xlabel("canonical dimension"); ax[1].set_ylabel("η² of retron type")
    ax[1].set_title("Retron-type variance explained per dimension")
    ax[1].legend(frameon=False); ax[1].set_ylim(0, 1)
    b = ax[2].bar(enc.modality, enc.test_accuracy, .5, color=[PAL[0], PAL[1]])
    ax[2].axhline(enc.majority_class_rate.iloc[0], ls="--", lw=.8, c="#666666")
    ax[2].text(1.45, enc.majority_class_rate.iloc[0] + .02, "majority class", fontsize=6,
               color="#666666", ha="right")
    for r, bb in zip(enc.itertuples(), b):
        ax[2].text(bb.get_x() + bb.get_width() / 2, r.test_accuracy + .015,
                   f"{r.test_accuracy:.3f}", ha="center", fontsize=7)
    ax[2].set_ylim(0, 1); ax[2].set_ylabel("test accuracy (fit on train components)")
    ax[2].set_title("Retron type is encoded in EACH modality alone")
    fig.suptitle("Canonical structure is dominated by retron type", y=1.0, fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "fig5_cca_dimensions.png", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    FIG.mkdir(parents=True, exist_ok=True)
    fig_modality("rt", "RT (ESM-C 300M)", "rt_aa_len", "RT length (aa)")
    fig_modality("ncrna", "ncRNA (RiNALMo giga-v1)", "nc_len", "ncRNA length (nt)")
    fig_shared()
    fig_similarity_and_retrieval()
    fig_dimensions()
    for f in sorted(FIG.glob("*.png")):
        print(f"  {f.name}  {f.stat().st_size/1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
