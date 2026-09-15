#!/usr/bin/env python3
"""f03 - figures for sections 6-13. Reads ONLY this bundle's tables/."""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Circle

import common as C

SCRIPT = "f03_tools_taxonomy.py"
plt = C.mpl_setup()
PL_UNIT = "physical locus (union of its records' tools)"


def _combo_set(name: str) -> set[str]:
    return set(str(name).split("|"))


def fig17_venn():
    d = C.read_table("t18_tool_combination_carriage")
    d = d[d.view_unit == PL_UNIT].set_index("combo")
    total = int(d.n.sum())
    fig, ax = plt.subplots(figsize=(8.4, 6.0))
    centres = {"myRT": (-0.34, 0.20), "PADLOC": (0.34, 0.20), "DefenseFinder": (0.0, -0.34)}
    colours = {"myRT": C.PALETTE[0], "PADLOC": C.PALETTE[2], "DefenseFinder": C.PALETTE[3]}
    for t, (cx, cy) in centres.items():
        ax.add_patch(Circle((cx, cy), 0.62, facecolor=colours[t], alpha=0.22, edgecolor=colours[t],
                            linewidth=2.0))
    label_pos = {
        "myRT": (-0.66, 0.45), "PADLOC": (0.66, 0.45), "DefenseFinder": (0.0, -0.72),
        "myRT|PADLOC": (0.0, 0.62), "myRT|DefenseFinder": (-0.46, -0.28),
        "PADLOC|DefenseFinder": (0.46, -0.28), "myRT|PADLOC|DefenseFinder": (0.0, 0.02)}
    for combo, (x, y) in label_pos.items():
        if combo not in d.index:
            continue
        r = d.loc[combo]
        ax.text(x, y + 0.055, f"{int(r.n):,d}", ha="center", va="center", fontsize=10.5,
                color=C.INK, fontweight="bold")
        ax.text(x, y - 0.075, f"{r.pct_with_ncrna:.1f}% with ncRNA", ha="center", va="center",
                fontsize=7.6, color=C.INK2)
    name_pos = {"myRT": (-0.98, 0.95), "PADLOC": (0.98, 0.95), "DefenseFinder": (0.0, -1.12)}
    for t, (nx, ny) in name_pos.items():
        ax.text(nx, ny, t, ha="center", fontsize=10.5, color=colours[t], fontweight="bold")
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.35, 1.15)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Which tools called each Retron locus, and how many carry an ncRNA", loc="left")
    C.stamp(ax, f"unit: Retron physical locus (the union of its records' tools) · denominator: "
                f"all {total:,d} Retron physical loci · carriage = ≥1 CANONICAL ncRNA placement · "
                f"CAUTION: the gradient is NOT read as biology: the ncRNA is a scoring element of "
                f"PADLOC's own retron rules (fig22)", y=0.03)
    C.save_fig(fig, "fig17_tool_venn", d.reset_index(), "physical loci",
               "Retron physical loci of that tool combination", SCRIPT)


def fig18_upset():
    d = C.read_table("t18_tool_combination_carriage")
    order = (d[d.view_unit == PL_UNIT].sort_values("n", ascending=False).combo.tolist())
    tools = list(C.TOOLS)
    fig = plt.figure(figsize=(11.4, 6.6))
    gs = fig.add_gridspec(3, 1, height_ratios=[2.1, 0.95, 1.7], hspace=0.08)

    axb = fig.add_subplot(gs[0])
    units = [("distinct record", C.NEUTRAL), ("locus (union of its records' tools)", "#c5d9ef"),
             (PL_UNIT, C.PALETTE[0]),
             ("exact RT (non-exclusive across combinations)", C.PALETTE[6])]
    x = np.arange(len(order))
    w = 0.2
    for i, (u, colr) in enumerate(units):
        sub = d[d.view_unit == u].set_index("combo").reindex(order)
        axb.bar(x + (i - 1.5) * w, sub.n, width=w, color=colr,
                label=f"{u.split(' (')[0]} (n={int(sub.n.sum()):,d})")
    for i, combo in enumerate(order):
        v = int(d[(d.view_unit == PL_UNIT) & (d.combo == combo)].n.iloc[0])
        axb.text(i + 0.5 * w, v * 1.12, f"{v:,d}", ha="center", fontsize=7, color=C.INK)
    axb.set_yscale("log")
    axb.set_ylim(1e3, 1.2e6)
    axb.set_ylabel("units in the combination (log)")
    axb.set_xticks([])
    axb.set_xlim(-0.6, len(order) - 0.4)
    axb.legend(fontsize=7.2, ncols=2, loc="upper right")
    axb.grid(axis="y")
    axb.set_axisbelow(True)
    axb.set_title("Tool-call combinations on Retron loci, at four analytical units", loc="left")

    axm = fig.add_subplot(gs[1], sharex=axb)
    for j, t in enumerate(tools):
        for i, combo in enumerate(order):
            on = t in _combo_set(combo)
            axm.plot([i], [len(tools) - 1 - j], "o", ms=9,
                     color=C.PALETTE[0] if on else "#dedcd7")
        axm.text(-0.62, len(tools) - 1 - j, t, ha="right", va="center", fontsize=8, color=C.INK2)
    for i, combo in enumerate(order):
        ys = [len(tools) - 1 - tools.index(t) for t in tools if t in _combo_set(combo)]
        if len(ys) > 1:
            axm.plot([i, i], [min(ys), max(ys)], color=C.PALETTE[0], linewidth=2.0)
    axm.set_ylim(-0.6, len(tools) - 0.4)
    axm.axis("off")

    axc = fig.add_subplot(gs[2], sharex=axb)
    for i, (u, colr, mark) in enumerate([(PL_UNIT, C.PALETTE[0], "o"),
                                         ("exact RT (non-exclusive across combinations)",
                                          C.PALETTE[6], "D")]):
        sub = d[d.view_unit == u].set_index("combo").reindex(order)
        off = (i - 0.5) * 0.16
        axc.errorbar(x + off, sub.pct_with_ncrna,
                     yerr=[sub.pct_with_ncrna - sub.pct_with_ncrna_ci_lo,
                           sub.pct_with_ncrna_ci_hi - sub.pct_with_ncrna],
                     fmt=mark, ms=6, color=colr, elinewidth=1.4, capsize=3,
                     label=f"{u.split(' (')[0]}")
        for xi, v in zip(x + off, sub.pct_with_ncrna):
            axc.text(xi, v + 4.5, f"{v:.1f}%", ha="center", fontsize=6.8, color=colr)
    axc.set_xticks(x, [c.replace("|", " + ") for c in order], rotation=18, ha="right", fontsize=7.6)
    axc.set_ylim(0, 105)
    axc.set_ylabel("% carrying a canonical ncRNA")
    axc.legend(fontsize=7.2, loc="upper right")
    axc.grid(axis="y")
    axc.set_axisbelow(True)
    axb.tick_params(labelbottom=False)     # sharex would repeat the combination labels up top
    axm.tick_params(labelbottom=False)
    C.stamp(axc, "unit: as in the legends · denominator: Retron units of that tool combination · "
                 "bars = Wilson 95% intervals · exact RTs are NOT exclusive between combinations "
                 "(one protein can sit at loci called by different tools) · CAUTION: carriage differences "
                 "across combinations are detector-definition coupled, not shown to be biological",
            y=-0.44)
    C.save_fig(fig, "fig18_tool_upset_carriage", d, "the unit named in view_unit",
               "Retron units of that tool combination", SCRIPT)


def fig19_combo_by_subtype():
    d = C.read_table("t20_combo_by_padloc_subtype")
    subs = d.groupby("label").n_loci.sum().sort_values(ascending=False).head(12).index
    combos = C.read_table("t18_tool_combination_carriage")
    order = combos[combos.view_unit == PL_UNIT].sort_values("n", ascending=False).combo.tolist()
    piv = d.pivot_table(index="label", columns="combo", values="pct_with_ncrna")
    npiv = d.pivot_table(index="label", columns="combo", values="n_loci")
    piv = piv.reindex(index=subs, columns=[c for c in order if c in piv.columns])
    npiv = npiv.reindex(index=piv.index, columns=piv.columns)
    masked = np.where(npiv.values < C.MIN_N_RATE, np.nan, piv.values)
    fig, ax = plt.subplots(figsize=(10.0, 5.2))
    im = ax.imshow(masked, aspect="auto", cmap="Blues", vmin=0, vmax=100)
    ax.set_xticks(range(piv.shape[1]), [c.replace("|", " +\n") for c in piv.columns], fontsize=7.4)
    ax.set_yticks(range(piv.shape[0]),
                  [f"{s}  (n={int(npiv.loc[s].sum()):,d})" for s in piv.index], fontsize=8)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v, n = masked[i, j], npiv.values[i, j]
            if np.isnan(v):
                ax.text(j, i, "·" if not np.isnan(n) else "", ha="center", va="center",
                        fontsize=8, color="#b9b8b3")
            else:
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7,
                        color="white" if v > 55 else C.INK)
    fig.colorbar(im, ax=ax, pad=0.012, fraction=0.024).set_label("% with a canonical ncRNA",
                                                                fontsize=8)
    ax.set_title("Is the carriage gradient composition? Carriage by tool combination × PADLOC subtype",
                 loc="left")
    C.stamp(ax, "unit: Retron physical locus · denominator: loci of that (combination, subtype) · "
                "cells with fewer than 30 loci are masked (·) · the myRT-only and "
                "DefenseFinder-only columns are absent BY CONSTRUCTION: a locus PADLOC did not "
                "call carries no PADLOC subtype · carriage varies both between subtypes and, "
                "within a subtype, between combinations - so the gradient is neither purely "
                "composition nor purely detector coupling", y=-0.22)
    C.save_fig(fig, "fig19_combo_by_padloc_subtype", d, "physical loci",
               "Retron physical loci of that (tool combination, PADLOC subtype)", SCRIPT)


def fig20_zero_call():
    d = C.read_table("t23_zero_call_by_database").sort_values("n_loci", ascending=False)
    d = d[d.n_loci >= 100]
    fig, ax = plt.subplots(figsize=(9.6, 4.4))
    y = np.arange(len(d))[::-1]
    cats = [("n_0", "0", C.PALETTE[1]), ("n_1", "1", C.PALETTE[0]),
            ("n_2", "2", C.PALETTE[2]), ("n_gt2", ">2", C.PALETTE[6])]
    left = np.zeros(len(d))
    for col, lab, colr in cats:
        vals = 100 * d[col].to_numpy() / d.n_loci.to_numpy()
        ax.barh(y, vals, left=left, height=0.6, color=colr, label=lab, edgecolor="white",
                linewidth=1.2)
        for yy, (v, l0) in zip(y, zip(vals, left)):
            if v > 4:
                ax.text(l0 + v / 2, yy, f"{v:.1f}%", ha="center", va="center", fontsize=7,
                        color="white")
        left += vals
    ax.set_yticks(y, [f"{r.source_database_set}\n(n={int(r.n_loci):,d} loci)"
                      for r in d.itertuples()], fontsize=7.6)
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of the database's Retron physical loci")
    ax.legend(fontsize=8, ncols=4, loc="lower left", bbox_to_anchor=(0, 1.02),
              title="distinct exact ncRNA sequences per locus", title_fontsize=8)
    ax.set_title("Zero-call structure of Retron loci, by source database", loc="left", pad=44)
    C.stamp(ax, "unit: Retron physical locus · denominator: Retron physical loci whose records "
                "carry that source-database set · classes count DISTINCT exact ncRNA sequences, so "
                "a locus deposited in two databases is not counted as carrying two ncRNAs · "
                "CAUTION: a zero here is detector scope and missing upstream context (fig21), not "
                "demonstrated biological absence", y=-0.19)
    C.save_fig(fig, "fig20_zero_call_by_database", d, "physical loci",
               "Retron physical loci of that source-database set", SCRIPT)


def fig21_upstream_context():
    d = C.read_table("t24_carriage_by_upstream_context")
    order = ["0", "1-200", "201-500", "501-1,000", "1,001-2,000", "2,001-5,000", "5,001-9,000",
             ">9,000"]
    fig, ax = plt.subplots(figsize=(9.8, 4.6))
    for i, clipped in enumerate([True, False]):
        s = d[d.upstream_side_clipped == clipped].set_index("upstream_context_bin").reindex(order)
        if s.n_loci.dropna().empty:
            continue
        x = np.arange(len(order))
        ax.errorbar(x + (i - 0.5) * 0.12, s.pct_with_ncrna,
                    yerr=[(s.pct_with_ncrna - s.pct_with_ncrna_ci_lo).fillna(0),
                          (s.pct_with_ncrna_ci_hi - s.pct_with_ncrna).fillna(0)],
                    fmt="o-" if clipped else "s--", ms=6, linewidth=1.8, capsize=3,
                    color=C.PALETTE[1] if clipped else C.PALETTE[0],
                    label=("window clipped on the upstream side" if clipped
                           else "upstream side not clipped"))
        for xi, (v, n) in zip(x + (i - 0.5) * 0.12, zip(s.pct_with_ncrna, s.n_loci)):
            if not np.isnan(v):
                ax.text(xi, v + 3.0, f"{v:.0f}%", ha="center", fontsize=6.8,
                        color=C.PALETTE[1] if clipped else C.PALETTE[0])
                ax.text(np.arange(len(order))[list(x).index(xi - (i - 0.5) * 0.12)],
                        -5.5 if clipped else -9.0, f"n={int(n):,d}", ha="center", fontsize=6.0,
                        color=C.PALETTE[1] if clipped else C.PALETTE[0])
    ax.set_xticks(range(len(order)), order, fontsize=8)
    ax.set_xlabel("bp of window context available upstream of the RT (transcription-relative)")
    ax.set_ylabel("% of loci with a canonical ncRNA")
    ax.set_ylim(-12, 78)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    ax.set_title("Most of the Retron zero-ncRNA class is missing upstream context, not absence",
                 loc="left")
    C.stamp(ax, "unit: Retron physical locus · denominator: geometry-eligible Retron physical loci "
                "in that context bin · bars = Wilson 95% intervals · the ncRNA sits a median of "
                "~30–50 bp upstream, so a locus with no upstream window cannot show one", y=-0.20)
    C.save_fig(fig, "fig21_carriage_by_upstream_context", d, "physical loci",
               "geometry-eligible Retron physical loci in that bin of upstream window context",
               SCRIPT)


def fig22_carriage_by_subtype():
    d = C.read_table("t21_carriage_by_subtype")
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.2), sharex=True,
                             gridspec_kw=dict(wspace=0.55))
    for ax, tool in zip(axes, ("PADLOC", "DefenseFinder")):
        t = d[(d.tool == tool) & (d.n_loci >= C.MIN_N_RATE)].sort_values("pct_with_ncrna")
        y = np.arange(len(t))
        for i, r in enumerate(t.itertuples()):
            colr = (C.PALETTE[7] if "PROHIBITED" in str(r.ncrna_role)
                    else C.PALETTE[2] if "REQUIRED" in str(r.ncrna_role) else C.PALETTE[0])
            ax.hlines(i, 0, r.pct_with_ncrna, color=C.GRID, linewidth=1.8)
            ax.errorbar([r.pct_with_ncrna], [i],
                        xerr=[[r.pct_with_ncrna - r.pct_with_ncrna_ci_lo],
                              [r.pct_with_ncrna_ci_hi - r.pct_with_ncrna]],
                        fmt="o", ms=6, color=colr, elinewidth=1.3, capsize=2.5)
            ax.text(101, i, f"n={int(r.n_loci):,d}", va="center", fontsize=6.8, color=C.INK2)
        ax.set_yticks(y, t.label, fontsize=8)
        ax.set_xlim(0, 100)
        ax.set_xlabel("% of the subtype's loci with a canonical ncRNA")
        ax.grid(axis="x")
        ax.set_axisbelow(True)
        ax.set_title(f"{tool} subtype", loc="left", fontsize=9.8)
    axes[0].plot([], [], "o", color=C.PALETTE[7], label="PADLOC rule PROHIBITS an ncRNA")
    axes[0].plot([], [], "o", color=C.PALETTE[2], label="PADLOC rule effectively REQUIRES one")
    axes[0].plot([], [], "o", color=C.PALETTE[0], label="ncRNA is a secondary gene in the rule")
    axes[0].legend(fontsize=7.2, loc="lower right")
    C.stamp(axes[0], "unit: Retron physical locus · denominator: loci carrying that tool's subtype "
                     "label (≥30 loci) · bars = Wilson 95% intervals · the colour is the ncRNA's "
                     "role in PADLOC's own rule file: retron_XII PROHIBITS an ncRNA, so its 0% is "
                     "a rule, not a model gap", y=-0.16, width=74)
    C.save_fig(fig, "fig22_carriage_by_subtype", d, "physical loci",
               "Retron physical loci carrying that tool's subtype label", SCRIPT)


SHORT_CLASS = {
    "single_placement": "single placement",
    "one_physical_locus_multiple_database_copies": "same locus, \u22652 databases",
    "one_physical_locus_multiple_records": "same locus, \u22652 records",
    "one_genome_multiple_loci": "same genome, \u22652 loci",
    "one_species_multiple_genomes": "same species, \u22652 genomes",
    "multiple_species": "\u22652 species",
}


def fig23_topology():
    comp = C.read_table("t28_topology_components")
    cls = C.read_table("t29_recurrence_classes").sort_values("n_exact_pairs", ascending=False)
    cc = C.read_table("t29_recurrence_ccdf")
    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.2),
                             gridspec_kw=dict(width_ratios=[1, 1.1, 1.1], wspace=0.52))
    ax = axes[0]
    x = np.arange(len(comp))
    for i, (col, lab) in enumerate([("n_components", "components"), ("n_exact_rt", "exact RTs"),
                                    ("n_exact_ncrna", "exact ncRNAs")]):
        ax.bar(x + (i - 1) * 0.27, comp[col], width=0.27, color=C.PALETTE[i], label=lab)
    for i, r in enumerate(comp.itertuples()):
        ax.text(i - 0.27, r.n_components * 1.35, f"{int(r.n_components):,d}", ha="center",
                fontsize=6.6, color=C.INK2)
    ax.set_xticks(x, comp["shape"], fontsize=8.4)
    ax.set_yscale("log")
    ax.set_ylim(1, 5e4)
    ax.set_ylabel("count (log)")
    ax.legend(fontsize=7.2)
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    ax.set_title("Bipartite component shapes", loc="left", fontsize=9.6)
    C.stamp(ax, "unit: connected component of the exact RT–ncRNA graph · denominator: the 14,918 "
                "components over 30,924 exact pairs", y=-0.17, width=52)

    ax2 = axes[1]
    y = np.arange(len(cls))[::-1]
    ax2.barh(y, cls.pct_of_exact_pairs, height=0.36, color=C.PALETTE[0], label="% of exact pairs")
    ax2.barh(y - 0.38, cls.pct_of_placements, height=0.36, color=C.PALETTE[1],
             label="% of placements")
    for yy, r in zip(y, cls.itertuples()):
        ax2.text(r.pct_of_exact_pairs + 1, yy, f"{r.pct_of_exact_pairs:.1f}%", va="center",
                 fontsize=6.8, color=C.PALETTE[0])
        ax2.text(r.pct_of_placements + 1, yy - 0.38, f"{r.pct_of_placements:.1f}%", va="center",
                 fontsize=6.8, color=C.PALETTE[1])
    ax2.set_yticks(y - 0.19, [SHORT_CLASS.get(s, s) for s in cls.recurrence_class], fontsize=7.6)
    ax2.set_xlim(0, 100)
    ax2.set_xlabel("% of the unit")
    ax2.legend(fontsize=7.2, loc="lower right")
    ax2.grid(axis="x")
    ax2.set_axisbelow(True)
    ax2.set_title("Why a pair recurs", loc="left", fontsize=9.6)
    C.stamp(ax2, "unit: exact pairs and placements · denominator: the 30,924 exact pairs and the "
                 "placements they carry · most recurrence is re-deposition of one physical locus",
            y=-0.17, width=58)

    ax3 = axes[2]
    d = cc[cc.metric == "placements per pair"]
    for i, cl in enumerate(cls.recurrence_class):
        g = d[d.recurrence_class == cl].sort_values("at_least")
        if g.empty:
            continue
        ax3.plot(g.at_least, g.pct, marker="o", ms=3.6, linewidth=1.6, color=C.PALETTE[i % 8],
                 label=f"{SHORT_CLASS.get(cl, cl)} (n={int(g.n_pairs_total.iloc[0]):,d})")
    ax3.set_xscale("log")
    ax3.set_yscale("log")
    ax3.set_xlabel("placements per exact pair")
    ax3.set_ylabel("% of the class's pairs at or above x")
    ax3.legend(fontsize=6.2, loc="lower left")
    ax3.grid(True)
    ax3.set_axisbelow(True)
    ax3.set_title("Recurrence depth", loc="left", fontsize=9.6)
    C.stamp(ax3, "unit: exact pair · denominator: exact pairs of that recurrence class",
            y=-0.17, width=52)
    C.save_fig(fig, "fig23_pair_topology_recurrence", pd.concat([comp.assign(panel="components"),
                                                                cls.assign(panel="recurrence")]),
               "components / exact pairs", "the 14,918 components and 30,924 exact pairs", SCRIPT)


def fig24_partner_consistency():
    h = C.read_table("t30_dominant_partner_histogram")
    t = C.read_table("t30_partner_consistency")
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2),
                             gridspec_kw=dict(width_ratios=[1.2, 1], wspace=0.28))
    ax = axes[0]
    ax.bar(h.dominant_partner_pct, h.n_exact_rt, width=1.6, color=C.PALETTE[0])
    ax.set_yscale("log")
    ax.set_xlabel("% of the protein's loci that carry its single most frequent ncRNA partner")
    ax.set_ylabel("exact RT sequences (log)")
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    ax.set_title("Recurrent proteins keep the same partner", loc="left", fontsize=9.8)
    C.stamp(ax, "unit: exact RT sequence · denominator: exact RTs with CANONICAL placements at ≥2 "
                "physical loci", y=-0.17, width=64)

    ax2 = axes[1]
    x = np.arange(len(t))
    ax2.bar(x - 0.2, t.pct_single_partner, width=0.4, color=C.PALETTE[0],
            label="only ever one ncRNA partner")
    ax2.bar(x + 0.2, t.pct_dominant_ge_90, width=0.4, color=C.PALETTE[2],
            label="dominant partner at ≥90% of loci")
    for i, r in enumerate(t.itertuples()):
        ax2.text(i - 0.2, r.pct_single_partner + 1.6, f"{r.pct_single_partner:.0f}%", ha="center",
                 fontsize=7, color=C.PALETTE[0])
        ax2.text(i + 0.2, r.pct_dominant_ge_90 + 1.6, f"{r.pct_dominant_ge_90:.0f}%", ha="center",
                 fontsize=7, color=C.PALETTE[2])
        ax2.text(i, 4, f"n={int(r.n_exact_rt):,d}", ha="center", fontsize=6.6, color=C.INK2)
    ax2.set_xticks(x, [f"{b}\nloci" for b in t.recurrence_bin], fontsize=8)
    ax2.set_ylim(0, 112)
    ax2.set_ylabel("% of the exact RTs in the bin")
    ax2.legend(fontsize=7.2, loc="lower left", bbox_to_anchor=(0, 1.02), ncols=2)
    ax2.grid(axis="y")
    ax2.set_axisbelow(True)
    ax2.set_title("…even when re-deposited hundreds of times", loc="left", fontsize=9.8, pad=24)
    C.stamp(ax2, "unit: exact RT sequence · denominator: exact RTs occurring at that many physical "
                 "loci · an exact ncRNA difference is a sequence difference, not necessarily a "
                 "different ncRNA family", y=-0.17, width=58)
    C.save_fig(fig, "fig24_partner_consistency", t, "exact RT sequences",
               "exact RTs carrying CANONICAL placements at ≥2 physical loci", SCRIPT)


def fig25_candidates():
    fam = C.read_table("t31_candidates_family_model")
    vs = C.read_table("t31_candidates_vs_retron")
    pl = C.read_table("t31_candidate_placements")
    rts = C.read_table("t31_candidate_exact_rts")
    fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.4),
                             gridspec_kw=dict(width_ratios=[1.05, 1.2, 0.85], wspace=0.62))
    ax = axes[0]
    piv = fam.pivot_table(index="file_label", columns="detection_model", values="n_placements",
                          fill_value=0)
    piv = piv.loc[piv.sum(1).sort_values(ascending=False).index,
                  piv.sum(0).sort_values(ascending=False).index]
    im = ax.imshow(piv.values, aspect="auto", cmap="Blues", vmin=0, vmax=max(2, piv.values.max()))
    ax.set_xticks(range(piv.shape[1]), piv.columns, rotation=45, ha="right", fontsize=6.6)
    ax.set_yticks(range(piv.shape[0]), piv.index, fontsize=7.4)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            if piv.values[i, j]:
                ax.text(j, i, int(piv.values[i, j]), ha="center", va="center", fontsize=6.4,
                        color="white" if piv.values[i, j] > piv.values.max() * 0.55 else C.INK)
    ax.set_title("RT family × covariance model", loc="left", fontsize=9.4)
    C.stamp(ax, "unit: placement · denominator: the 266 retained candidate placements",
            y=-0.30, width=46)

    ax2 = axes[1]
    ret = vs[vs.population.str.startswith("CANONICAL Retron")].iloc[0]
    cand = pl.copy()
    rng = np.random.default_rng(C.SEED)
    ax2.axvspan(-1100, 0, color=C.PALETTE[2], alpha=0.10, zorder=0)
    ax2.text(0.02, 0.97, "declared Retron envelope:\nupstream, same strand, 0 CDS, \u22641.1 kb",
             transform=ax2.transAxes, fontsize=6.4, color=C.PALETTE[2], va="top")
    for i, (lab, sel) in enumerate([("candidates: single-family RT", ~cand.file_label.eq("MULTI")),
                                    ("candidates: MULTI stratum", cand.file_label.eq("MULTI"))]):
        sub = cand[sel]
        jit = rng.uniform(-0.10, 0.10, len(sub))
        ax2.scatter(sub.signed_distance_bp, np.full(len(sub), 0.72 - i * 0.30) + jit,
                    s=15, color=C.PALETTE[1 + i * 5], alpha=0.75, label=lab, edgecolor="none")
    ax2.axvline(0, color=C.INK2, linewidth=0.8, linestyle=(0, (3, 3)))
    ax2.set_ylim(-0.75, 1.0)
    ax2.set_yticks([])
    ax2.set_xscale("symlog", linthresh=100)
    ax2.set_xlabel("signed distance (bp, symlog)")
    ax2.legend(fontsize=6.6, loc="lower right", framealpha=0.9)
    ax2.set_title("Candidate geometry vs the Retron prior", loc="left", fontsize=9.4)
    lines = [(f"CANONICAL Retron: n={int(ret.n_placements):,d} \u00b7 "
              f"{ret.pct_upstream:.1f}% upstream \u00b7 median |d| "
              f"{ret.median_abs_distance_bp:,.0f} bp \u00b7 "
              f"{ret.pct_in_retron_envelope:.1f}% in the envelope", C.INK2)]
    for _, r in vs[~vs.population.str.startswith("CANONICAL")].iterrows():
        lines.append((f"{r.population.replace('non-Retron retron-CM ', '')}: "
                      f"n={int(r.n_placements)} \u00b7 {r.pct_upstream:.1f}% upstream \u00b7 "
                      f"median |d| {r.median_abs_distance_bp:,.0f} bp \u00b7 "
                      f"{r.pct_in_retron_envelope:.1f}% in the envelope", C.PALETTE[1]))
    for k, (txt, colr) in enumerate(lines):
        ax2.text(0.0, 0.20 - 0.085 * k, txt, transform=ax2.transAxes, fontsize=6.2, color=colr,
                 va="top")
    C.stamp(ax2, "unit: placement \u00b7 denominator: the 266 candidates; the Retron line is all "
                 "CANONICAL Retron placements \u00b7 one dot = one candidate placement",
            y=-0.30, width=58)

    ax3 = axes[2]
    d = rts.sort_values("n_placements", ascending=False).head(12)[::-1]
    y = np.arange(len(d))
    ax3.barh(y, d.n_placements, color=C.PALETTE[0], height=0.6)
    for i, r in enumerate(d.itertuples()):
        ax3.text(r.n_placements + 0.3, i, f"{int(r.n_species)} sp · {int(r.n_databases)} db",
                 va="center", fontsize=6.4, color=C.INK2)
    ax3.set_yticks(y, [f"{r.family} · {r.model}" for r in d.itertuples()], fontsize=6.0)
    ax3.set_xlabel("candidate placements")
    ax3.set_xlim(0, d.n_placements.max() * 1.7)
    ax3.grid(axis="x")
    ax3.set_axisbelow(True)
    ax3.set_title("Most recurrent candidate proteins", loc="left", fontsize=9.4)
    C.stamp(ax3, "unit: exact RT sequence · denominator: the 139 exact RTs carrying a candidate "
                 "placement · NOT called novel retrons: an annotation-disagreement population",
            y=-0.30, width=48)
    C.save_fig(fig, "fig25_candidates", pl, "placements",
               "the 266 retained retron-CM placements beside non-Retron-labelled RTs", SCRIPT)


def fig26_multi():
    e = C.read_table("t32_margin_ecdf")
    cmpt = C.read_table("t32_margin_comparison")
    ml = C.read_table("t32_multi_margin_length")
    pairs = C.read_table("t33_multi_family_pairs")
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.2),
                             gridspec_kw=dict(width_ratios=[1, 1, 1.1], wspace=0.56))
    ax = axes[0]
    g = e.sort_values("margin_bits")
    ax.step(g.margin_bits, g.cumulative_pct, where="post", color=C.PALETTE[1], linewidth=2.2,
            label=f"MULTI exact RTs (n={int(g.n_total.iloc[0]):,d})")
    ctrl_med = None
    for _, r in cmpt.iterrows():
        vals = [v for k, v in r.items() if "median" in str(k).lower()
                and isinstance(v, (int, float))]
        if str(r.iloc[0]).lower().startswith(("control", "single")) and vals:
            ctrl_med = float(vals[0])
    med = float(g.loc[g.cumulative_pct >= 50, "margin_bits"].min())
    ax.axvline(med, color=C.PALETTE[1], linewidth=1, linestyle=(0, (3, 3)))
    ax.text(med * 1.15, 12, f"MULTI median\n≈{med:.0f} bits", fontsize=7, color=C.PALETTE[1])
    if ctrl_med:
        ax.axvline(ctrl_med, color=C.PALETTE[0], linewidth=1.6)
        ax.text(ctrl_med * 1.1, 60, f"single-family control\nmedian {ctrl_med:.1f} bits",
                fontsize=7, color=C.PALETTE[0])
    ax.set_xscale("symlog", linthresh=1)
    ax.set_xlabel("best-vs-second HMM margin (bits)")
    ax.set_ylabel("cumulative % of MULTI exact RTs")
    ax.grid(True)
    ax.set_axisbelow(True)
    ax.set_title("The two best families tie", loc="left", fontsize=9.6)
    C.stamp(ax, "unit: exact RT sequence · denominator: the 7,593 V-RT-MULTI exact RTs; the "
                "control is g4's seeded 2,000 single-family exact RTs", y=-0.17, width=52)

    ax2 = axes[1]
    hb = ax2.hexbin(ml.rt_aa_len, ml.margin_bits.clip(lower=0.1), gridsize=30, bins="log",
                    yscale="log", cmap="Blues", mincnt=1, linewidths=0)
    ax2.set_xlim(0, 1000)
    ax2.set_xlabel("RT length (aa)")
    ax2.set_ylabel("margin (bits, log)")
    ax2.set_title("Margin vs length (the stated confound)", loc="left", fontsize=9.6)
    # no colourbar: it would sit on the next panel's labels. The density legend is in the stamp.
    C.stamp(ax2, "unit: exact RT sequence · denominator: the 7,593 MULTI exact RTs · darker "
                 "hexagons hold more exact RTs (log scale) · score scales with length, so part of "
                 "the tie may be a length effect - Stage 1 does not separate them",
            y=-0.17, width=52)

    ax3 = axes[2]
    top = pairs.sort_values("n_exact_rt", ascending=False).head(12)[::-1]
    y = np.arange(len(top))
    ax3.barh(y, top.n_exact_rt, color=C.PALETTE[0], height=0.62)
    for i, r in enumerate(top.itertuples()):
        ax3.text(r.n_exact_rt * 1.04, i, f"{int(r.n_exact_rt):,d} · {r.median_margin_bits:.1f} bits",
                 va="center", fontsize=6.6, color=C.INK2)
    ax3.set_yticks(y, [f"{r.family_a} ↔ {r.family_b}" for r in top.itertuples()], fontsize=7)
    ax3.set_xscale("log")
    ax3.set_xlim(1, top.n_exact_rt.max() * 6)
    ax3.set_xlabel("MULTI exact RTs carrying both labels (log)")
    ax3.grid(axis="x")
    ax3.set_axisbelow(True)
    ax3.set_title("Which families are confused with which", loc="left", fontsize=9.6)
    C.stamp(ax3, "unit: exact RT sequence · denominator: MULTI exact RTs whose label set contains "
                 "both families · a 3-label set contributes to all three pairs", y=-0.17, width=52)
    C.save_fig(fig, "fig26_multi_ambiguity", ml, "MULTI exact RT sequences",
               "the 7,593 V-RT-MULTI exact RTs", SCRIPT)


def fig27_prevalence_phylum():
    d = C.read_table("t34_gtdb_prevalence_by_rank")
    p = d[(d["rank"] == "phylum") & (d.meets_min_sampled)].sort_values("n_sampled_genomes",
                                                                       ascending=False).head(16)
    p = p[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.2), sharey=True,
                             gridspec_kw=dict(width_ratios=[1, 1], wspace=0.06))
    y = np.arange(len(p))
    ax = axes[0]
    ax.barh(y + 0.19, p.n_sampled_genomes, height=0.36, color=C.NEUTRAL, label="genomes sampled")
    ax.barh(y - 0.19, p.n_rt_positive_genomes, height=0.36, color=C.PALETTE[0],
            label="genomes with ≥1 RT locus")
    ax.set_yticks(y, p.taxon, fontsize=8)
    ax.set_xscale("log")
    ax.set_xlim(20, 1e6)
    ax.set_xlabel("genomes (log)")
    ax.legend(fontsize=7.6, loc="lower right")
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    ax.set_title("Sampling vs recovery", loc="left", fontsize=9.6)
    C.stamp(ax, "unit: genome · denominator: genomes of that phylum in the GTDB bacterial "
                "catalogue", y=-0.13, width=58)

    ax2 = axes[1]
    ax2.errorbar(p.prevalence_pct, y,
                 xerr=[p.prevalence_pct - p.prevalence_pct_ci_lo,
                       p.prevalence_pct_ci_hi - p.prevalence_pct],
                 fmt="o", ms=6, color=C.PALETTE[0], elinewidth=1.4, capsize=3)
    for i, r in enumerate(p.itertuples()):
        ax2.text(r.prevalence_pct + 2.2, i, f"{r.prevalence_pct:.1f}%", va="center", fontsize=7,
                 color=C.INK)
        ax2.text(97, i, f"{r.exact_rt_per_positive_genome:.2f} exact RT/genome", va="center",
                 ha="right", fontsize=6.4, color=C.INK2)
    ax2.set_xlim(0, 100)
    ax2.set_xlabel("% of sampled genomes carrying ≥1 RT locus")
    ax2.grid(axis="x")
    ax2.set_axisbelow(True)
    ax2.set_title("Prevalence, with a real denominator", loc="left", fontsize=9.6)
    C.stamp(ax2, "unit: genome · denominator: sampled genomes of that phylum · bars = Wilson 95% "
                 "intervals · gtdb_bacteria only (the NCBI block carries no phylum) · 'sampled' "
                 "is the catalogue, an upper bound on what the pipeline attempted", y=-0.13,
            width=58)
    C.save_fig(fig, "fig27_gtdb_prevalence_phylum", p, "genomes",
               "genomes of that phylum in the GTDB bacterial catalogue", SCRIPT)


def fig28_family_phylum():
    d = C.read_table("t35_family_by_phylum_prevalence")
    phyla = (d.groupby("cat_phylum").n_sampled_genomes.max().sort_values(ascending=False)
             .head(14).index)
    fams = (d[d.cat_phylum.isin(phyla)].groupby("family").n_positive_genomes.sum()
            .sort_values(ascending=False).head(10).index)
    piv = (d[d.cat_phylum.isin(phyla) & d.family.isin(fams)]
           .pivot_table(index="cat_phylum", columns="family", values="prevalence_pct",
                        fill_value=0.0).reindex(index=phyla, columns=fams))
    fig, ax = plt.subplots(figsize=(10.6, 5.0))
    im = ax.imshow(piv.values, aspect="auto", cmap="Blues", vmin=0, vmax=np.nanmax(piv.values))
    ax.set_xticks(range(piv.shape[1]), piv.columns, rotation=40, ha="right", fontsize=8)
    samp = d.groupby("cat_phylum").n_sampled_genomes.max()
    ax.set_yticks(range(piv.shape[0]),
                  [f"{p}  (n={int(samp[p]):,d})" for p in piv.index], fontsize=7.8)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.values[i, j]
            if v >= 0.5:
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=6.6,
                        color="white" if v > np.nanmax(piv.values) * 0.55 else C.INK)
    fig.colorbar(im, ax=ax, pad=0.012, fraction=0.026).set_label(
        "% of the phylum's sampled genomes carrying ≥1 locus of the family", fontsize=7.6)
    ax.set_title("Family prevalence per phylum (GTDB schema, gtdb_bacteria only)", loc="left")
    C.stamp(ax, "unit: genome · denominator: sampled genomes of that phylum in the GTDB bacterial "
                "catalogue (phyla with ≥1,000 sampled genomes) · cells below 0.5% are unlabelled",
            y=-0.22)
    C.save_fig(fig, "fig28_family_phylum_prevalence", d, "genomes",
               "genomes of that phylum in the GTDB bacterial catalogue", SCRIPT)


def fig29_rank_prevalence():
    d = C.read_table("t34_gtdb_prevalence_by_rank")
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.6), gridspec_kw=dict(wspace=0.62))
    for ax, rank in zip(axes, ("class", "order", "genus")):
        t = d[(d["rank"] == rank) & d.meets_min_sampled].copy()
        t = pd.concat([t.sort_values("prevalence_pct", ascending=False).head(8),
                       t.sort_values("prevalence_pct").head(6)])
        t = t.sort_values("prevalence_pct")
        y = np.arange(len(t))
        colr = [C.PALETTE[1] if v < 5 else C.PALETTE[0] for v in t.prevalence_pct]
        ax.errorbar(t.prevalence_pct, y,
                    xerr=[t.prevalence_pct - t.prevalence_pct_ci_lo,
                          t.prevalence_pct_ci_hi - t.prevalence_pct],
                    fmt="none", ecolor=C.GRID, elinewidth=2)
        ax.scatter(t.prevalence_pct, y, s=40, color=colr, zorder=3)
        for i, r in enumerate(t.itertuples()):
            ax.text(r.prevalence_pct + 3, i, f"{r.prevalence_pct:.0f}%  (n={int(r.n_sampled_genomes):,d})",
                    va="center", fontsize=6.4, color=C.INK2)
        ax.set_yticks(y, t.taxon, fontsize=7)
        ax.set_xlim(-2, 168)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xlabel("% of sampled genomes with ≥1 RT locus")
        ax.grid(axis="x")
        ax.set_axisbelow(True)
        ax.set_title(f"{rank}: highest and lowest", loc="left", fontsize=9.4)
    C.stamp(axes[0], "unit: genome · denominator: sampled genomes of that taxon in the GTDB "
                     "bacterial catalogue (class/order ≥1,000 or ≥500, genus ≥500 genomes) · "
                     "orange = below 5% · a zero is 'not recovered here', not proof of absence: "
                     "pipeline failures are not recorded in any Stage-1 input", y=-0.16, width=150)
    C.save_fig(fig, "fig29_rank_prevalence", d[d.meets_min_sampled & d["rank"].isin(
        ["class", "order", "genus"])], "genomes",
        "sampled genomes of that taxon in the GTDB bacterial catalogue", SCRIPT)


def fig30_ncbi_representation():
    d = C.read_table("t36_ncbi_genus_representation").sort_values("pct_of_records")
    fig, ax = plt.subplots(figsize=(9.4, 5.0))
    y = np.arange(len(d))
    for i, r in enumerate(d.itertuples()):
        ax.plot([r.pct_of_records, r.pct_of_exact_rt], [i, i], color=C.GRID, linewidth=2.2)
    ax.scatter(d.pct_of_records, y, s=48, color=C.PALETTE[1], label="% of NCBI-schema records")
    ax.scatter(d.pct_of_exact_rt, y, s=48, color=C.PALETTE[0], label="% of exact RTs")
    for i, r in enumerate(d.itertuples()):
        ax.text(max(r.pct_of_records, r.pct_of_exact_rt) + 0.5, i,
                f"{r.records_per_exact_rt:.0f} records per exact RT", va="center", fontsize=6.6,
                color=C.INK2)
    ax.set_yticks(y, d.tax_genus, fontsize=8)
    ax.set_xlabel("share of the NCBI-schema catalogue (%)")
    ax.set_xlim(0, 30)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    ax.set_title("NCBI block: representation, not prevalence", loc="left")
    C.stamp(ax, "unit: records and exact RTs · denominator: all NCBI-schema records carrying a "
                "genus · CAUTION: no sampled-genome denominator exists for this block, so no taxon here "
                "may be called enriched - only over-represented in the catalogue", y=-0.14)
    C.save_fig(fig, "fig30_ncbi_genus_representation", d, "records / exact RTs",
               "all NCBI-schema records carrying a genus (top 20 by records)", SCRIPT)


def fig31_quality():
    bt = C.read_table("t39_bt_status_by_database")
    rec = C.read_table("t39_no_rt_cds_recovery_by_database")
    tr = C.read_table("t39_context_truncation_by_database")
    tier = C.read_table("t40_inspectability")
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 7.6),
                             gridspec_kw=dict(hspace=1.05, wspace=0.42))

    ax = axes[0, 0]
    dbs = [d for d in C.DB_ORDER if d in set(bt.source_database)]
    states = (bt.groupby("bt_status").n_records.sum().sort_values(ascending=False).index.tolist())
    mat = np.array([[float(bt[(bt.source_database == db) & (bt.bt_status == st)]
                            .pct_of_database_records.sum()) for st in states] for db in dbs])
    im1 = ax.imshow(mat, aspect="auto", cmap="Blues", vmin=0, vmax=100)
    ax.set_xticks(range(len(states)), [st.replace("not_testable_", "not testable:\n")
                                       .replace("_", " ") for st in states],
                  rotation=32, ha="right", fontsize=6.4)
    ax.set_yticks(range(len(dbs)), dbs, fontsize=7.2)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            if v > 0:
                ax.text(j, i, f"{v:.1f}" if v < 10 else f"{v:.0f}", ha="center", va="center",
                        fontsize=6.2, color="white" if v > 55 else C.INK)
    ax.set_title("RT back-translation status (% of the database's records)", loc="left",
                 fontsize=9.4)
    C.stamp(ax, "unit: distinct record · denominator: distinct RT-anchored records of that "
                "database · the recoding classes are real properties of the corpus, not failures",
            y=-0.56, width=56)

    ax2 = axes[0, 1]
    states2 = ["RECOVERED", "SEQUENCE_ONLY", "ILL_POSED"]
    y2 = np.arange(len(dbs))[::-1]
    left = np.zeros(len(dbs))
    for i, st in enumerate(states2):
        vals = np.array([float(rec[(rec.source_database == db) & (rec.recovery_state == st)]
                                .n_records.sum()) for db in dbs])
        ax2.barh(y2, vals, left=left, height=0.62, color=C.PALETTE[[2, 1, 7][i]], label=st)
        left += vals
    ax2.set_yticks(y2, dbs, fontsize=7.6)
    ax2.set_xscale("symlog", linthresh=10)
    ax2.set_xlabel("records with no marked RT CDS (symlog)")
    ax2.legend(fontsize=7, loc="lower right")
    ax2.set_title("Recovery of records without an RT CDS", loc="left", fontsize=9.4)
    ax2.text(0.02, 0.97, "every record without an RT CDS comes from a MAG\ncatalogue: the two "
                         "NCBI and two GTDB rows are exactly zero",
             transform=ax2.transAxes, fontsize=6.4, color=C.INK2, ha="left", va="top")
    C.stamp(ax2, "unit: distinct record · denominator: the 31,504 records with no marked RT CDS, "
                 "split by database", y=-0.20, width=56)

    ax3 = axes[1, 0]
    cols = [("pct_window_inverted", "window inverted"),
            ("pct_rt_outside_window", "RT outside its window"),
            ("pct_rt_at_window_edge", "RT touching a window edge"),
            ("pct_true_start_clipped", "clipped at contig start"),
            ("pct_clipped_at_contig_end", "clipped at contig end"),
            ("pct_geometry_eligible", "geometry-eligible")]
    mat = np.array([[float(tr[tr.source_database == db][c].iloc[0]) for c, _ in cols]
                    for db in dbs])
    im3 = ax3.imshow(mat, aspect="auto", cmap="Blues", vmin=0, vmax=100)
    ax3.set_xticks(range(len(cols)), [lab for _, lab in cols], rotation=32, ha="right",
                   fontsize=6.8)
    ax3.set_yticks(range(len(dbs)), dbs, fontsize=7.2)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            ax3.text(j, i, f"{v:.1f}" if v < 10 else f"{v:.0f}", ha="center", va="center",
                     fontsize=6.2, color="white" if v > 55 else C.INK)
    ax3.set_title("Context truncation (% of the database's records)", loc="left", fontsize=9.4)
    C.stamp(ax3, "unit: distinct record · denominator: distinct RT-anchored records of that "
                 "database · the flags are not exclusive", y=-0.52, width=56)

    ax4 = axes[1, 1]
    t = tier.sort_values("n_records", ascending=True)
    y4 = np.arange(len(t))
    colours = [C.PALETTE[2] if "fully" in s else C.PALETTE[7] if "ill-posed" in s
               else C.PALETTE[1] if "sequence only" in s else C.PALETTE[0]
               for s in t.inspectability_tier]
    ax4.barh(y4, t.pct_of_distinct_records, color=colours, height=0.6)
    for i, r in enumerate(t.itertuples()):
        ax4.text(r.pct_of_distinct_records + 0.6, i,
                 f"{r.pct_of_distinct_records:.1f}%  ({int(r.n_records):,d})", va="center",
                 fontsize=7, color=C.INK)
    import textwrap as _tw
    ax4.set_yticks(y4, ["\n".join(_tw.wrap(s.split(" (")[0], 26)) for s in t.inspectability_tier],
                   fontsize=6.4)
    ax4.set_xlim(0, 62)
    ax4.set_xlabel("% of distinct records")
    ax4.grid(axis="x")
    ax4.set_axisbelow(True)
    ax4.set_title("How much of the catalogue is directly inspectable", loc="left", fontsize=9.4)
    C.stamp(ax4, "unit: distinct record · denominator: all 3,051,238 distinct RT-anchored records",
            y=-0.40, width=56)
    C.save_fig(fig, "fig31_data_quality", tier, "distinct records",
               "distinct RT-anchored records (per database in three panels; corpus-wide in the "
               "inspectability panel)", SCRIPT)


def fig32_carriage_by_length():
    d = C.read_table("t25_carriage_by_rt_length")
    order = ["<200", "200-249", "250-299", "300-349", "350-399", "400-499", "500-699", ">=700"]
    fig, ax = plt.subplots(figsize=(9.6, 4.4))
    for i, comp in enumerate(["all_complete", "all_partial", "mixed_or_codon_evidence"]):
        s = d[d.completeness_class == comp].set_index("length_bin").reindex(order)
        x = np.arange(len(order)) + (i - 1) * 0.16
        ax.errorbar(x, s.pct_with_ncrna,
                    yerr=[(s.pct_with_ncrna - s.pct_with_ncrna_ci_lo).fillna(0),
                          (s.pct_with_ncrna_ci_hi - s.pct_with_ncrna).fillna(0)],
                    fmt="o-", ms=5.5, linewidth=1.6, capsize=3, color=C.PALETTE[i],
                    label=comp.replace("_", " "))
        for xi, (v, n) in zip(x, zip(s.pct_with_ncrna, s.n_exact_rt)):
            if not np.isnan(v) and n >= C.MIN_N_RATE:
                ax.text(xi, v + 2.6, f"{v:.0f}", ha="center", fontsize=6.2, color=C.PALETTE[i])
    ax.set_xticks(range(len(order)), order, fontsize=8)
    ax.set_xlabel("RT length (aa)")
    ax.set_ylabel("% of exact RTs with a canonical ncRNA")
    ax.set_ylim(0, 85)
    ax.legend(fontsize=7.6, title="Prodigal completeness", title_fontsize=7.6)
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    ax.set_title("ncRNA carriage against RT length and completeness (Retron)", loc="left")
    C.stamp(ax, "unit: exact RT sequence · denominator: Retron V-RT-SINGLE exact RTs of that "
                "length bin and completeness class · bars = Wilson 95% intervals · association "
                "only: short partial RTs also sit in clipped windows (fig21)", y=-0.16)
    C.save_fig(fig, "fig32_carriage_by_rt_length", d, "exact RT sequences",
               "Retron-labelled V-RT-SINGLE exact RTs of that length bin and completeness class",
               SCRIPT)


def fig33_recurrence_breadth():
    sc = C.read_table("t38_recurrence_scatter")
    br = C.read_table("t38_recurrence_breadth")
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.4),
                             gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.3))
    ax = axes[0]
    hb = ax.hexbin(sc.n_genomes, sc.n_species.clip(lower=1), xscale="log", yscale="log",
                   gridsize=30, bins="log", cmap="Blues", mincnt=1, linewidths=0)
    ax.set_xlabel("genomes carrying the exact RT (log)")
    ax.set_ylabel("distinct species (log)")
    fig.colorbar(hb, ax=ax, pad=0.012, fraction=0.04).set_label("exact RTs (log)", fontsize=7.6)
    ax.set_title("High recurrence is not the same as taxonomic breadth", loc="left", fontsize=9.6)
    C.stamp(ax, "unit: exact RT sequence · denominator: the 8,019 exact RTs occurring in ≥20 "
                "genomes · species counts mix taxonomy schemas and are a lower bound", y=-0.17,
            width=60)

    ax2 = axes[1]
    fams = br.groupby("family").n_exact_rt.sum().sort_values(ascending=False).head(8).index
    classes = ["one species (database duplication or clonal)", "2-5 species", ">5 species"]
    y = np.arange(len(fams))[::-1]
    left = np.zeros(len(fams))
    for i, cl in enumerate(classes):
        vals = np.array([float(br[(br.family == f) & (br.breadth_class == cl)]
                               .pct_of_family_high_recurrence.sum()) for f in fams])
        ax2.barh(y, vals, left=left, height=0.6, color=C.PALETTE[[1, 3, 2][i]], label=cl,
                 edgecolor="white", linewidth=1)
        for yy, (v, l0) in zip(y, zip(vals, left)):
            if v > 7:
                ax2.text(l0 + v / 2, yy, f"{v:.0f}%", ha="center", va="center", fontsize=6.8,
                         color="white")
        left += vals
    tot = br.groupby("family").n_exact_rt.sum()
    ax2.set_yticks(y, [f"{f}  (n={int(tot[f]):,d})" for f in fams], fontsize=7.6)
    ax2.set_xlim(0, 100)
    ax2.set_xlabel("% of the family's high-recurrence exact RTs")
    ax2.legend(fontsize=6.8, loc="lower left", bbox_to_anchor=(0, 1.01), ncols=2)
    ax2.set_title("Breadth class of high-recurrence proteins", loc="left", fontsize=9.6, pad=24)
    C.stamp(ax2, "unit: exact RT sequence · denominator: exact RTs of that family occurring in "
                 "≥20 genomes", y=-0.17, width=56)
    C.save_fig(fig, "fig33_recurrence_breadth", br, "exact RT sequences",
               "exact RTs occurring in ≥20 genomes, of that family", SCRIPT)


def fig34_tool_mix_by_database():
    d = C.read_table("t26_tool_mix_by_database")
    dbs = (d.groupby("source_database_set").n_loci_db.max().sort_values(ascending=False)
           .head(8).index)
    combos = C.read_table("t18_tool_combination_carriage")
    order = combos[combos.view_unit == PL_UNIT].sort_values("n", ascending=False).combo.tolist()
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6),
                             gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.3))
    ax = axes[0]
    y = np.arange(len(dbs))[::-1]
    left = np.zeros(len(dbs))
    for i, combo in enumerate(order):
        vals = np.array([float(d[(d.source_database_set == db) & (d.combo == combo)]
                               .pct_of_database_loci.sum()) for db in dbs])
        ax.barh(y, vals, left=left, height=0.62, color=C.PALETTE[i % 8],
                label=combo.replace("|", "+"), edgecolor="white", linewidth=0.8)
        for yy, (v, l0) in zip(y, zip(vals, left)):
            if v > 9:
                ax.text(l0 + v / 2, yy, f"{v:.0f}", ha="center", va="center", fontsize=6.6,
                        color="white")
        left += vals
    nn = d.groupby("source_database_set").n_loci_db.max()
    ax.set_yticks(y, [f"{db}\n(n={int(nn[db]):,d} loci)" for db in dbs], fontsize=7)
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of the database's Retron physical loci")
    ax.legend(fontsize=5.8, ncols=4, loc="lower left", bbox_to_anchor=(0, 1.02))
    ax.set_title("Which tools called the loci, per database", loc="left", fontsize=9.6, pad=42)
    C.stamp(ax, "unit: Retron physical locus · denominator: Retron loci of that source-database "
                "set", y=-0.18, width=62)

    ax2 = axes[1]
    for i, db in enumerate(list(dbs)[:5]):
        s = d[d.source_database_set == db].set_index("combo").reindex(order)
        ax2.plot(np.arange(len(order)), s.pct_with_ncrna, marker="o", ms=5, linewidth=1.6,
                 color=C.PALETTE[i % 8], label=f"{db} (n={int(s.n_loci.sum()):,d})")
    ax2.set_xticks(range(len(order)), [c.replace("|", "+\n") for c in order], fontsize=6.0,
                   rotation=16, ha="right")
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("% of loci with a canonical ncRNA")
    ax2.legend(fontsize=6.4)
    ax2.grid(axis="y")
    ax2.set_axisbelow(True)
    ax2.set_title("Carriage within each tool combination", loc="left", fontsize=9.6)
    C.stamp(ax2, "unit: Retron physical locus · denominator: loci of that (database, combination) "
                 "· the ordering of combinations repeats across databases, so the gradient is not "
                 "a property of one catalogue", y=-0.18, width=56)
    C.save_fig(fig, "fig34_tool_mix_by_database", d, "physical loci",
               "Retron physical loci of that source-database set and tool combination", SCRIPT)


if __name__ == "__main__":
    C.log("== f03 figures, sections 6-13")
    fig17_venn()
    fig18_upset()
    fig19_combo_by_subtype()
    fig20_zero_call()
    fig21_upstream_context()
    fig22_carriage_by_subtype()
    fig23_topology()
    fig24_partner_consistency()
    fig25_candidates()
    fig26_multi()
    fig27_prevalence_phylum()
    fig28_family_phylum()
    fig29_rank_prevalence()
    fig30_ncbi_representation()
    fig31_quality()
    fig32_carriage_by_length()
    fig33_recurrence_breadth()
    fig34_tool_mix_by_database()
