#!/usr/bin/env python
"""Thesis figures for the RT-ncRNA representation / conditional-modelling narrative.

Renders ONLY from frozen bundle tables and from derived/x1_component_level.tsv (which is itself
checked against the frozen bundle by r01_x1_component_table.py). No model is run, no embedding is
loaded, nothing in the source worktree is written.

    python scripts/f_figures.py             # all figures
    python scripts/f_figures.py --only F3   # one figure

Terminology enforced in every caption and label: observed pair, candidate, counterfactual
conditioning control, non-observed pairing. Never "negative pair", never "incompatible pair".
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parents[1]
DERIVED, FIG = HERE / "derived", HERE / "figures"
SRC = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings")
R = SRC / "results"

PAL = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]
GREY, LGREY = "#666666", "#DDDDDD"
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 300, "font.size": 8,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 9, "axes.labelsize": 8, "legend.fontsize": 7,
                     "figure.facecolor": "white", "savefig.facecolor": "white"})


def box(ax, x, y, w, h, text, fc="white", ec=GREY, fs=6.2, lw=1.0, ha="center"):
    """Rounded box with text auto-shrunk to fit inside it (schematics must never overflow)."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                fc=fc, ec=ec, lw=lw, zorder=2))
    t = ax.text(x + w / 2 if ha == "center" else x + 0.015, y + h / 2, text,
                ha=ha if ha != "center" else "center", va="center", fontsize=fs, zorder=3,
                linespacing=1.4)
    fig = ax.figure
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    for _ in range(14):
        bb = t.get_window_extent(renderer=r).transformed(ax.transData.inverted())
        if bb.width <= w * 0.93 and bb.height <= h * 0.93:
            break
        fs *= 0.93
        t.set_fontsize(fs)
    return t


def arrow(ax, xy_from, xy_to, style="-|>", color=GREY, lw=1.0, ls="-"):
    ax.add_patch(FancyArrowPatch(xy_from, xy_to, arrowstyle=style, mutation_scale=9,
                                 color=color, lw=lw, linestyle=ls, shrinkA=2, shrinkB=2, zorder=1))


def blank(ax):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote figures/{name}.png and .pdf")


# ---------------------------------------------------------------- F1 dataset and split schematic
def f1():
    comps = pd.read_csv(R / "embed_g2b_frozen_split/tables/split_components.tsv", sep="\t")
    fig = plt.figure(figsize=(7.2, 5.4))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.25, 1.0], hspace=0.55, wspace=0.52)

    ax = fig.add_subplot(gs[0, :]); blank(ax)
    ax.set_title("a  From observed RT–ncRNA associations to an indivisible split unit", loc="left")
    box(ax, 0.005, 0.30, 0.17, 0.42,
        "PAIR-ELIG\n30,924 observed pairs\n29,192 exact RTs\n16,458 oriented ncRNAs\n21 retron types",
        fc="#F2F6FA", ec=PAL[0])
    box(ax, 0.205, 0.55, 0.20, 0.30,
        "RT clustering\nmmseqs --min-seq-id 0.50\n-c 0.8 bidirectional", fc="white", ec=PAL[1])
    box(ax, 0.205, 0.14, 0.20, 0.30,
        "ncRNA clustering\ncd-hit-est -c 0.80\n-aS 0.8, -T 1 (determinism)", fc="white", ec=PAL[2])
    box(ax, 0.435, 0.30, 0.20, 0.42,
        "bipartite graph\nRT cluster ↔ ncRNA cluster\n\nconnected component\n= indivisible split unit\n1,075 components",
        fc="#FBF3EC", ec=PAL[4])
    box(ax, 0.665, 0.30, 0.16, 0.42,
        "deterministic\nallocation\n70 / 15 / 15\nby pair count\nno RNG, no seed", fc="white", ec=GREY, fs=6.0)
    box(ax, 0.845, 0.615, 0.15, 0.20, "train\n21,647 pairs\n361 comps · n_eff 6.4", fc="#EFEFEF", ec=GREY, fs=5.4)
    box(ax, 0.845, 0.385, 0.15, 0.20, "validation\n4,639 pairs\n357 comps · n_eff 14.2", fc="#EFEFEF", ec=GREY, fs=5.4)
    box(ax, 0.845, 0.155, 0.15, 0.20, "test\n4,638 pairs\n357 comps · n_eff 14.1", fc="#FDECEC", ec=PAL[1], fs=5.4)
    for a, b in (((0.175, 0.62), (0.205, 0.70)), ((0.175, 0.40), (0.205, 0.29)),
                 ((0.405, 0.70), (0.435, 0.60)), ((0.405, 0.29), (0.435, 0.40)),
                 ((0.635, 0.51), (0.665, 0.51)),
                 ((0.825, 0.56), (0.845, 0.71)), ((0.825, 0.51), (0.845, 0.48)),
                 ((0.825, 0.46), (0.845, 0.25))):
        arrow(ax, a, b)
    ax.text(0.005, 0.10, "Why the component: one ncRNA is observed with 705 distinct RTs, so an RT-only split leaks "
                         "through shared ncRNAs, and an ncRNA-only split leaks symmetrically.\nOnly the connected "
                         "component is closed under both relations. Splitting is blind to any compatibility result.",
            fontsize=6.4, color="#333333", va="top")

    ax = fig.add_subplot(gs[1, 0])
    s = np.sort(comps["n_pairs"].values)[::-1]
    ax.loglog(np.arange(1, len(s) + 1), s, lw=1.2, color=PAL[0])
    ax.set_xlabel("component rank"); ax.set_ylabel("pairs in component")
    ax.set_title("b  Uneven component sizes", loc="left", fontsize=8)
    ax.annotate(f"largest = {s[0]:,} pairs\n({100*s[0]/s.sum():.1f} % of the universe)",
                xy=(1, s[0]), xytext=(6, 400), fontsize=6.2,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.text(0.98, 0.05, f"{len(s):,} components\nmedian {int(np.median(s))} pairs",
            transform=ax.transAxes, ha="right", fontsize=6.5)

    ax = fig.add_subplot(gs[1, 1])
    folds = [("train", 21647, 361, 6.4), ("validation", 4639, 357, 14.2), ("test", 4638, 357, 14.1)]
    x = np.arange(3)
    ax.bar(x - 0.22, [f[2] for f in folds], 0.42, color=LGREY, ec=GREY, lw=0.6, label="components")
    ax.bar(x + 0.22, [f[3] for f in folds], 0.42, color=PAL[1], label="n_eff (inverse Simpson)")
    for i, f in enumerate(folds):
        ax.text(i - 0.22, f[2] + 8, f"{f[2]}", ha="center", fontsize=6.5)
        ax.text(i + 0.22, f[3] + 8, f"{f[3]}", ha="center", fontsize=6.5, color=PAL[1])
    ax.set_xticks(x); ax.set_xticklabels([f[0] for f in folds])
    ax.set_ylabel("count"); ax.set_ylim(0, 430)
    ax.set_title("c  Components ≠ independent", loc="left", fontsize=8)
    ax.legend(frameon=False, loc="upper right", fontsize=6.2)

    ax = fig.add_subplot(gs[1, 2])
    tt = pd.read_csv(R / "embed_g2a_split_selection/tables/g2_decision_table.tsv", sep="\t")
    leak = tt["rt_frac_ge_0.5"] * 100
    ax.scatter(tt["test_neff"], leak, s=18, color=GREY, zorder=2)
    sel = (tt["rt_id"] == 0.5) & (tt["nc_id"] == 0.8)
    ax.scatter(tt.loc[sel, "test_neff"], leak[sel], s=48, color=PAL[1], zorder=3)
    ax.annotate("adopted\nRT 0.50 / nc 0.80", (float(tt.loc[sel, "test_neff"].iloc[0]), float(leak[sel].iloc[0])),
                xytext=(14, -14), textcoords="offset points", fontsize=5.8, color=PAL[1],
                arrowprops=dict(arrowstyle="-", color=PAL[1], lw=0.7))
    for _, r in tt[tt["rt_id"].isin([0.3, 0.9])].iterrows():
        ax.annotate(f"RT {r['rt_id']:.2f}", (r["test_neff"], r["rt_frac_ge_0.5"] * 100),
                    fontsize=5.6, color="#888888", xytext=(4, 2), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_xlabel("test-fold n_eff  (statistical power)")
    ax.set_ylabel("held-out RT with a\n≥0.50-id training relative (%)", fontsize=7)
    ax.set_title("d  Blocking vs power", loc="left", fontsize=8)

    fig.text(0.5, -0.035,
             "Frozen split: results/embed_g2b_frozen_split (commit 15e00b8); threshold sweep: embed_g2a (fd5efc9). "
             "Assignment sha256 78a95563…c77d376. Panel d leakage column: rt_frac_ge_0.5 of the g2a whole-universe "
             "probe (retained-hit censored; the exact held-out-vs-training search gives higher values).",
             ha="center", fontsize=6, color="#555555")
    save(fig, "F1_dataset_split_schematic")


# ------------------------------------------------------- F2 conceptual conditioning ladder U/T/R
def f2():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.3), gridspec_kw=dict(width_ratios=[1.35, 1]))
    ax = axes[0]; blank(ax)
    ax.set_title("a  One decoder, three conditioning inputs", loc="left")
    box(ax, 0.02, 0.72, 0.30, 0.16, "U · RNA-only\none learned constant vector", fc="white", ec=GREY)
    box(ax, 0.02, 0.46, 0.30, 0.16, "T · type-conditioned\nembedding of 21 retron types", fc="white", ec=PAL[2])
    box(ax, 0.02, 0.20, 0.30, 0.16, "R · RT-conditioned\nfrozen ESM-C 300M of THIS RT\n(32 × 960 chunks)",
        fc="#F2F6FA", ec=PAL[0])
    box(ax, 0.42, 0.34, 0.24, 0.42,
        "shared decoder\nbyte-identical across arms\n\n3 × cross-attention\ncausal RNA self-attn\n665,355 parameters",
        fc="#FBF3EC", ec=PAL[4])
    box(ax, 0.74, 0.40, 0.24, 0.30, "held-out ncRNA\nlog-likelihood\n(nats / nucleotide)\ncomponent-level",
        fc="white", ec=GREY)
    for y in (0.80, 0.54, 0.28):
        arrow(ax, (0.32, y), (0.42, 0.55))
    arrow(ax, (0.66, 0.55), (0.74, 0.55))
    ax.text(0.02, 0.055, "Only the conditioning path differs. Comparisons are paired per component:\n"
                         "T − U isolates broad retron-type information; R − T isolates information specific\n"
                         "to the individual RT.", fontsize=6.2, va="top", color="#333333")

    ax = axes[1]; blank(ax)
    ax.set_title("b  Three levels of claim", loc="left")
    box(ax, 0.02, 0.70, 0.96, 0.22,
        "LEVEL 1 · broad association\nRT and ncRNA properties track retron type/lineage\nevidence: embed_g2, X1 (T − U)",
        fc="#EAF5EE", ec=PAL[2], fs=6.8)
    box(ax, 0.02, 0.42, 0.96, 0.22,
        "LEVEL 2 · RT-specific statistical association\nthe individual RT improves scoring of its observed ncRNA\n"
        "beyond type — X1 preliminary; X2 pending",
        fc="#F2F6FA", ec=PAL[0], fs=6.8)
    box(ax, 0.02, 0.10, 0.96, 0.26,
        "LEVEL 3 · functional compatibility / orthogonality\nwhether an RT works with one ncRNA and not another\n"
        "NOT addressable with these data — requires experiment",
        fc="#FDECEC", ec=PAL[1], fs=6.8)
    arrow(ax, (0.50, 0.70), (0.50, 0.645)); arrow(ax, (0.50, 0.42), (0.50, 0.365), ls=(0, (2, 2)))
    ax.text(0.52, 0.392, "no automatic inference", fontsize=6, color=PAL[1], ha="left", va="center")
    save(fig, "F2_conditioning_concept")


# ------------------------------------------------------------------- F3 X1 held-out NLL / ppl
def f3():
    T = R / "embed_x1_conditional_pilot/tables"
    arms = pd.read_csv(T / "x1_arms.tsv", sep="\t").set_index("arm")
    cmp_ = pd.read_csv(T / "x1_comparisons.tsv", sep="\t").set_index("comparison")
    sens = pd.read_csv(T / "x1_sensitivity.tsv", sep="\t")
    strat = pd.read_csv(T / "x1_strata.tsv", sep="\t").set_index("stratum")
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 3.0),
                             gridspec_kw=dict(wspace=0.62, width_ratios=[1, 1.1, 1.1]))

    ax = axes[0]
    for i, (a, c) in enumerate(zip(["U", "T", "R"], [GREY, PAL[2], PAL[0]])):
        r = arms.loc[a]
        ax.errorbar(i, r["test_nll_component_mean"],
                    yerr=[[r["test_nll_component_mean"] - r["ci_lo"]],
                          [r["ci_hi"] - r["test_nll_component_mean"]]],
                    fmt="o", ms=5, color=c, capsize=3, lw=1.2)
        ax.text(i + 0.16, r["test_nll_component_mean"],
                f"{r['test_nll_component_mean']:.5f}\nppl {r['test_ppl']:.3f}",
                fontsize=6.0, ha="left", va="center")
    ax.set_xticks(range(3)); ax.set_xticklabels(["U\nRNA-only", "T\ntype", "R\nRT"], fontsize=7)
    ax.set_xlim(-0.6, 2.6); ax.set_ylim(1.348, 1.423)
    ax.set_ylabel("held-out NLL (nats / nt)")
    ax.set_title("a  Component-mean test NLL", loc="left", fontsize=8)
    ax.text(0.03, 0.03, "357 components · n_eff 14.1\n95 % CI: bootstrap over components",
            transform=ax.transAxes, fontsize=6.0)

    ax = axes[1]
    rows = [("T − U", "type vs none", "T - U", PAL[2]),
            ("R − U", "RT vs none", "R - U", PAL[4]),
            ("R − T", "RT beyond type", "R - T", PAL[0])]
    for i, (lab, sub, key, c) in enumerate(rows):
        r = cmp_.loc[key]
        ax.errorbar(r["diff"], i, xerr=[[r["diff"] - r["ci_lo"]], [r["ci_hi"] - r["diff"]]],
                    fmt="o", ms=5, color=c, capsize=3, lw=1.2)
        ax.text(r["diff"], i + 0.20, f"{r['diff']:+.5f}", fontsize=6.2, ha="center")
        ax.text(r["diff"], i - 0.30, f"{100*r['frac_components_favouring_a']:.0f} % of components",
                fontsize=5.8, ha="center", color="#555555")
    ax.axvline(0, color="#999999", lw=0.8, ls="--")
    ax.set_yticks(range(3))
    ax.set_yticklabels([f"{r[0]}\n{r[1]}" for r in rows], fontsize=6.6)
    ax.set_ylim(-0.7, 2.7); ax.set_xlim(-0.068, 0.006)
    ax.set_xlabel("Δ NLL, paired per component\n(negative = first arm better)", fontsize=7)
    ax.set_title("b  Paired differences", loc="left", fontsize=8)

    ax = axes[2]
    rt_full, rt_sens = cmp_.loc["R - T"], sens[sens["comparison"] == "R - T"].iloc[0]
    t4 = strat.loc["T4"]
    entries = [("full test fold\n357 comps", rt_full["diff"], rt_full["ci_lo"], rt_full["ci_hi"], PAL[0], "o"),
               ("near-duplicate excl.\n284 comps", rt_sens["diff"], rt_sens["ci_lo"], rt_sens["ci_hi"], PAL[0], "o"),
               ("T4 recurrent\n83 comps", t4["diff"], t4["ci_lo"], t4["ci_hi"], PAL[1], "s")]
    for i, (lab, v, lo, hi, c, mk) in enumerate(entries):
        ax.errorbar(v, i, xerr=[[v - lo], [hi - v]], fmt=mk, ms=5, color=c, capsize=3, lw=1.2)
        ax.text(v, i + 0.20, f"{v:+.5f}", fontsize=6.2, ha="center", color=c)
    ax.text(t4["ci_hi"], 2 - 0.30, "interval includes 0", fontsize=5.8, ha="right", color=PAL[1])
    ax.axvline(0, color="#999999", lw=0.8, ls="--")
    ax.set_yticks(range(3)); ax.set_yticklabels([e[0] for e in entries], fontsize=6.4)
    ax.set_ylim(-0.7, 2.7)
    ax.set_xlabel("R − T Δ NLL", fontsize=7)
    ax.set_title("c  R − T across populations", loc="left", fontsize=8)

    fig.text(0.5, -0.10, "results/embed_x1_conditional_pilot (commit 8bf7207). PRELIMINARY: one pilot run, one seed "
                         "per arm; cross-fitted confirmation (X2) pending.", ha="center", fontsize=6, color="#555555")
    save(fig, "F3_x1_nll_comparison")


# ------------------------------------------------- F4 component-level R−T effect distribution
def f4():
    t = pd.read_csv(DERIVED / "x1_component_level.tsv", sep="\t")
    meta = json.loads((DERIVED / "x1_component_level.meta.json").read_text())
    d = t["d_R_minus_T"].values
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.0), gridspec_kw=dict(wspace=0.46, width_ratios=[1.1, 1.15, 1]))

    ax = axes[0]
    lim = np.percentile(np.abs(d), 99)
    ax.hist(np.clip(d, -lim, lim), bins=45, color="#C9DAEA", ec=PAL[0], lw=0.5)
    ax.axvline(0, color="#999999", lw=0.9, ls="--")
    ax.axvline(d.mean(), color=PAL[1], lw=1.2)
    ax.text(0.97, 0.94, f"mean {d.mean():+.5f}", color=PAL[1], fontsize=6.5,
            transform=ax.transAxes, ha="right", va="top")
    ax.set_xlabel("per-component R − T Δ NLL"); ax.set_ylabel("components")
    ax.set_title("a  Per-component R − T effect", loc="left", fontsize=8)
    ax.text(0.02, 0.86, f"{len(d)} components\n{100*(d<0).mean():.1f} % favour R",
            transform=ax.transAxes, fontsize=6.4)
    ax.text(0.02, 0.62, "a small shift of a wide\ndistribution, not a uniform gain",
            transform=ax.transAxes, fontsize=6.2, color="#333333")

    ax = axes[1]
    sizes = t["n_pairs"].values
    ax.scatter(sizes, d, s=np.clip(sizes, 6, 120), alpha=0.55, color=PAL[0], ec="none")
    ax.axhline(0, color="#999999", lw=0.9, ls="--")
    ax.axhline(d.mean(), color=PAL[1], lw=1.0)
    ax.set_xscale("log")
    ax.set_xlabel("pairs in component (marker area ∝ pairs)")
    ax.set_ylabel("R − T Δ NLL")
    ax.set_title("b  Equal weight per component", loc="left", fontsize=8)
    ax.text(0.98, 0.04, f"n_eff {meta['n_eff_test']} of {len(d)} components", transform=ax.transAxes,
            ha="right", fontsize=6.2)

    ax = axes[2]
    has_t4 = t["n_pairs_T4"] > 0
    groups = [("all", d, PAL[0]), ("has T4\npairs", d[has_t4.values], PAL[1]),
              ("no T4\npairs", d[~has_t4.values], GREY)]
    parts = ax.violinplot([g[1] for g in groups], showextrema=False, widths=0.75)
    for b, g in zip(parts["bodies"], groups):
        b.set_facecolor(g[2]); b.set_alpha(0.28); b.set_edgecolor(g[2])
    for i, g in enumerate(groups, start=1):
        m = g[1].mean()
        ax.plot([i - 0.24, i + 0.24], [m, m], color=g[2], lw=1.6)
        ax.text(i, ax.get_ylim()[1] * 0.93, f"{m:+.4f}\nn={len(g[1])}", fontsize=5.8,
                ha="center", va="top", color=g[2])
    ax.axhline(0, color="#999999", lw=0.9, ls="--")
    ax.set_xticks([1, 2, 3]); ax.set_xticklabels([g[0] for g in groups], fontsize=6.6)
    ax.set_ylabel("R − T Δ NLL")
    ax.set_title("c  By tier content (descriptive)", loc="left", fontsize=8)
    ax.text(0.02, 0.03, "not a confirmatory contrast", transform=ax.transAxes,
            fontsize=6.0, color="#555555")

    fig.text(0.5, -0.08, "Re-aggregated from the frozen embed_x1 per-sequence held-out NLL arrays by "
                         "scripts/r01_x1_component_table.py; 46/46 checks reproduce the frozen summary tables. "
                         "No model output recomputed.", ha="center", fontsize=6, color="#555555")
    save(fig, "F4_component_effect_distribution")


# -------------------------------------------- F5 observed RT vs same-type counterfactual control
def f5():
    cf = json.loads((R / "embed_x1_conditional_pilot/tables/x1_counterfactual.json").read_text())
    fig = plt.figure(figsize=(7.4, 3.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1], wspace=0.22)

    ax = fig.add_subplot(gs[0]); blank(ax)
    ax.set_title("a  The counterfactual conditioning control", loc="left")
    box(ax, 0.02, 0.70, 0.44, 0.17, "observed pair\nRT_A  →  ncRNA_A", fc="#F2F6FA", ec=PAL[0], fs=6.4)
    box(ax, 0.02, 0.38, 0.44, 0.24,
        f"M = {cf['n_alternatives']} alternative RTs\nsame retron type, not observed\nwith ncRNA_A "
        f"(type needs ≥ {cf['min_type_rts']} test RTs)", fc="white", ec=PAL[1], fs=6.0)
    box(ax, 0.54, 0.62, 0.44, 0.25,
        "score ncRNA_A under the SAME\narm-R model, swapping ONLY\nthe conditioning RT", fc="#FBF3EC", ec=PAL[4], fs=6.2)
    box(ax, 0.54, 0.28, 0.44, 0.25,
        "Δ log P per nt =\nNLL(alternative) − NLL(observed)\npositive favours the observed RT",
        fc="white", ec=GREY, fs=6.2)
    arrow(ax, (0.46, 0.78), (0.54, 0.74)); arrow(ax, (0.46, 0.50), (0.54, 0.66))
    arrow(ax, (0.76, 0.62), (0.76, 0.53))
    ax.text(0.02, 0.20, "Alternatives are evaluation-time controls: NOT biological negatives and NOT\n"
                        "incompatible pairs. A combination absent from the corpus is a non-observed\n"
                        "pairing, nothing more. No counterfactual RT is ever used as a training label.",
            fontsize=6.2, va="top", color="#333333")

    ax = fig.add_subplot(gs[1])
    mu, lo, hi = cf["delta_logP_per_nt"], cf["ci_lo"], cf["ci_hi"]
    ax.errorbar(mu, 0, xerr=[[mu - lo], [hi - mu]], fmt="o", ms=6, color=PAL[0], capsize=4, lw=1.4)
    ax.axvline(0, color="#999999", lw=0.9, ls="--")
    ax.text(mu, 0.16, f"{mu:+.6f}\n[{lo:+.6f}, {hi:+.6f}]", fontsize=6.6, ha="center")
    ax.set_yticks([0]); ax.set_yticklabels(["observed RT vs\nsame-type alternatives"], fontsize=6.6)
    ax.set_ylim(-1.0, 0.55); ax.set_xlim(-0.002, 0.021)
    ax.set_xlabel("Δ log P per nt  (positive favours the observed RT)", fontsize=7)
    ax.set_title("b  Frozen X1 result", loc="left", fontsize=8)
    ax.text(0.02, 0.30, f"{cf['n_eligible']:,} of 4,638 held-out pairs eligible ({100*cf['n_eligible']/4638:.1f} %)\n"
                        f"{cf['n_components']} components\n"
                        f"{100*cf['frac_pairs_favouring_observed']:.1f} % of pairs and "
                        f"{100*cf['frac_components_favouring_observed']:.1f} % of components\n"
                        f"favour the observed RT",
            transform=ax.transAxes, fontsize=6.2, va="top")
    ax.text(0.02, 0.08, "X2 adds stricter tiers: C2 length-matched, C3 nearest\nESM-C neighbours, C4 same "
                        "50 %-identity RT cluster — PENDING.",
            transform=ax.transAxes, fontsize=6.2, va="bottom", color=PAL[1])

    fig.text(0.5, -0.03, "results/embed_x1_conditional_pilot/tables/x1_counterfactual.json (commit 8bf7207). "
                         "Per-pair values were not frozen, so only the component-level summary is plotted.",
             ha="center", fontsize=6, color="#555555")
    save(fig, "F5_counterfactual_control")


# ------------------------------------------------------- F6 shared-space evidence (narrative use)
def f6():
    sim = pd.read_csv(R / "embed_g2c_atlas/plotdata/similarity_long.tsv", sep="\t")
    lad = pd.read_csv(R / "embed_g2_frozen_baseline/tables/g2_test_ladder.tsv", sep="\t")
    nb = json.loads((R / "embed_g2c_atlas/tables/g2a_neighbourhood.json").read_text())
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 3.1), gridspec_kw=dict(wspace=0.52, width_ratios=[1, 1.25, 0.85]))

    ax = axes[0]
    order = [("observed_pair", "observed pair", PAL[0]), ("type_matched_decoy", "type-matched candidate", PAL[4]),
             ("length_gc_matched_decoy", "length+GC-matched", PAL[2]), ("random_decoy", "random candidate", GREY)]
    present = [o for o in order if (sim["population"] == o[0]).any()]
    data = [sim.loc[sim["population"] == o[0], "cosine"].values for o in present]
    parts = ax.violinplot(data, vert=False, showextrema=False, widths=0.85)
    for b, o in zip(parts["bodies"], present):
        b.set_facecolor(o[2]); b.set_alpha(0.35); b.set_edgecolor(o[2])
    for i, (o, v) in enumerate(zip(present, data), start=1):
        ax.plot([np.mean(v)], [i], "o", ms=3.5, color=o[2])
    ax.set_yticks(range(1, len(present) + 1)); ax.set_yticklabels([o[1] for o in present], fontsize=6.6)
    ax.set_xlabel("cross-modal cosine in shared CCA space")
    ax.set_title("a  Similarity by candidate class", loc="left", fontsize=8)

    ax = axes[1]
    rungs = ["rung1_random", "rung2_len_gc", "rung3_model", "rung4_nc_cluster", "rung5_rt_cluster", "rung6_species"]
    names = ["1 random", "2 len+GC", "3 retron type", "4 ncRNA cluster", "5 RT cluster", "6 species"]
    undet = {"rung4_nc_cluster", "rung5_rt_cluster", "rung6_species"}
    x = np.arange(len(rungs))
    for model, c, off in (("B-kmer", GREY, -0.17), ("M-CCA", PAL[0], 0.17)):
        sub = lad[lad["model"] == model].set_index("rung")
        v = [sub.loc[r, "mrr"] for r in rungs]
        lo = [sub.loc[r, "mrr"] - sub.loc[r, "ci_lo"] for r in rungs]
        hi = [sub.loc[r, "ci_hi"] - sub.loc[r, "mrr"] for r in rungs]
        ax.errorbar(x + off, v, yerr=[lo, hi], fmt="o", ms=4, color=c, capsize=2.5, lw=1.0, label=model)
    ax.axhline(0.09, color=PAL[1], lw=0.9, ls="--")
    ax.text(len(rungs) - 0.5, 0.098, "chance 0.0900", fontsize=6, color=PAL[1], ha="right")
    ticks = []
    for i, (r, nm) in enumerate(zip(rungs, names)):
        n_c = int(lad[(lad["model"] == "M-CCA") & (lad["rung"] == r)]["n_components"].iloc[0])
        ticks.append(f"{nm}\n{n_c} comps")
        if r in undet:
            ax.axvspan(i - 0.45, i + 0.45, color="#F3F3F3", zorder=0)
            ax.text(i, 0.40, "UNDETERMINED", ha="center", fontsize=5.4, color=PAL[1], rotation=90)
    ax.set_xticks(x); ax.set_xticklabels(ticks, fontsize=5.8, rotation=30, ha="right")
    ax.set_ylabel("retrieval MRR (50-way)"); ax.set_ylim(0.0, 0.55)
    ax.set_title("b  The candidate ladder", loc="left", fontsize=8)
    ax.legend(frameon=False, loc="upper right", fontsize=6.4)

    ax = axes[2]
    vals = [nb["type_prevalence_in_pool"], nb["nearest_neighbour_shares_retron_type"],
            nb["top10_fraction_sharing_retron_type"]]
    ax.bar([0, 1, 2], vals, color=[LGREY, PAL[0], PAL[0]], ec=GREY, lw=0.6)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.015, f"{100*v:.1f} %", ha="center", fontsize=6.4)
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["pool\nprevalence", "nearest\nneighbour", "top-10"], fontsize=6.0)
    ax.set_ylabel("share with the query's retron type"); ax.set_ylim(0, 0.68)
    ax.set_title(f"c  {nb['type_sharing_enrichment_vs_prevalence']}× type enrichment", loc="left", fontsize=8)
    ax.text(0.03, 0.93, f"but the observed partner sits at\nmedian rank "
                        f"{nb['median_rank_of_observed_partner']} of {nb['pool_size']:,}",
            transform=ax.transAxes, fontsize=6.2, color=PAL[1], va="top")

    fig.text(0.5, -0.10, "results/embed_g2_frozen_baseline (2c9127b) and results/embed_g2c_atlas (9154972). "
                         "Panel b is the inferential panel; a and c are descriptive.",
             ha="center", fontsize=6, color="#555555")
    save(fig, "F6_shared_space_evidence")


# -------------------------------------------- F7 prospective candidate-selection matrix (METHODS)
def f7():
    rng = np.random.default_rng(7)
    n = 6
    labels = [f"RT-{c}" for c in "ABCDEF"]
    rlabels = [f"ncRNA-{c}" for c in "ABCDEF"]
    m = rng.normal(0.0, 0.35, size=(n, n))
    np.fill_diagonal(m, rng.normal(1.6, 0.18, size=n))
    m[1, 4] = m[4, 1] = 1.05          # an illustrative cross-supported pair

    fig = plt.figure(figsize=(7.2, 3.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.0, 1.15], wspace=0.34)

    ax = fig.add_subplot(gs[0])
    im = ax.imshow(m, cmap="BrBG", vmin=-2, vmax=2)
    ax.set_xticks(range(n)); ax.set_xticklabels(rlabels, rotation=45, ha="right", fontsize=6.4)
    ax.set_yticks(range(n)); ax.set_yticklabels(labels, fontsize=6.4)
    ax.set_title("a  Conditional pairing score matrix\n    (ILLUSTRATIVE — not a result)", loc="left", fontsize=8)
    for i in (0, 3):     # a candidate low-cross-reactivity SET: native high, cross low
        ax.add_patch(plt.Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False, ec=PAL[0], lw=1.6))
    for i, j in ((1, 4), (4, 1)):   # high cross score -> NOT selected
        ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec=PAL[1], lw=1.6, ls=(0, (2, 1))))
    ax.text(0.0, -1.15, "blue = candidate set (native high, cross low)   ·   orange dashed = high cross score, "
                        "deprioritised", fontsize=5.6, color="#444444")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("score(ncRNA_j | RT_i) − background", fontsize=6.2)
    cb.ax.tick_params(labelsize=6)

    ax = fig.add_subplot(gs[1]); blank(ax)
    ax.set_title("b  Selection rule", loc="left")
    box(ax, 0.02, 0.62, 0.96, 0.30,
        "SELECT pairs (A,A) and (B,B) such that\nnative scores are high AND\ncross scores (A,B), (B,A) are low",
        fc="#F2F6FA", ec=PAL[0], fs=6.8)
    box(ax, 0.02, 0.30, 0.96, 0.26,
        "margin = min(native) − max(cross)\nreported per candidate SET,\nwith its uncertainty",
        fc="white", ec=GREY, fs=6.8)
    box(ax, 0.02, 0.02, 0.96, 0.22,
        "OUTPUT: a ranked list of candidate\npairs for laboratory testing\n— a PREDICTED pairing score —",
        fc="#FBF3EC", ec=PAL[4], fs=6.8)
    arrow(ax, (0.5, 0.62), (0.5, 0.565)); arrow(ax, (0.5, 0.30), (0.5, 0.245))

    ax = fig.add_subplot(gs[2]); blank(ax)
    ax.set_title("c  Confidence must be conditioned on", loc="left")
    items = ["model uncertainty (seeds, folds, replicates)",
             "sequence relatedness of the two RTs",
             "retron type (same type = harder, more informative)",
             "phylogenetic / lineage distance",
             "inside the model's training distribution?",
             "consistency across seeds and cross-fit folds",
             "native-minus-counterfactual score margin"]
    for i, it in enumerate(items):
        ax.text(0.03, 0.90 - i * 0.115, "•", fontsize=8, color=PAL[0])
        ax.text(0.09, 0.90 - i * 0.115, it, fontsize=6.6, va="center")
    ax.text(0.03, 0.055, "Most-distant RTs are NOT automatically best:\ndistance itself produces "
                         "out-of-distribution scores.", fontsize=6.4, color=PAL[1], va="center")

    fig.text(0.5, -0.06, "PROSPECTIVE METHODS SCHEMATIC. The matrix values are synthetic illustration. No retron "
                         "RT–ncRNA cross-reactivity has been predicted, scored or tested in this project.",
             ha="center", fontsize=6.2, color=PAL[1])
    save(fig, "F7_candidate_selection_schematic")


FIGS = {"F1": f1, "F2": f2, "F3": f3, "F4": f4, "F5": f5, "F6": f6, "F7": f7}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=sorted(FIGS))
    a = ap.parse_args()
    for k in a.only:
        FIGS[k]()
