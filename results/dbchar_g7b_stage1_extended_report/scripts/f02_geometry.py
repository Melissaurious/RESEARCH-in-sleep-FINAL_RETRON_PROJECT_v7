#!/usr/bin/env python3
"""f02 - figures for sections 4-5 (ncRNA/CM composition and RT<->ncRNA geometry).

Reads ONLY this bundle's tables/.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrow, Rectangle

import common as C

SCRIPT = "f02_geometry.py"
plt = C.mpl_setup()


def fig09_ncrna_length():
    q = (C.read_table("t09_ncrna_length_by_model").sort_values("median")
         .rename(columns={"median": "median_len"}))
    h = C.read_table("t09_ncrna_length_histogram")
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 5.0),
                             gridspec_kw=dict(width_ratios=[1.9, 1], wspace=0.08))
    ax = axes[0]
    y = np.arange(len(q))
    for i, r in enumerate(q.itertuples()):
        g = h[h.detection_model == r.detection_model]
        if not g.empty:
            w = g.n.to_numpy() / g.n.max() * 0.40
            xv = (g.bin_lo.to_numpy() + g.bin_hi.to_numpy()) / 2
            ax.fill_between(xv, i - w, i + w, color=C.PALETTE[0], alpha=0.30, linewidth=0)
        ax.plot([r.q25, r.q75], [i, i], color=C.PALETTE[0], linewidth=3.4, solid_capstyle="butt")
        ax.plot([r.min, r.max], [i, i], color=C.PALETTE[0], linewidth=0.8, alpha=0.7, zorder=0)
        ax.plot([r.median_len], [i], "o", ms=5, color="white", markeredgecolor=C.PALETTE[0],
                markeredgewidth=1.6, zorder=4)
        ax.text(r.max + 6, i, f"{int(r.median_len)} nt", va="center", fontsize=7, color=C.INK2)
    ax.set_yticks(y, q.detection_model, fontsize=8.2)
    ax.set_xlim(0, 420)
    ax.set_xlabel("exact ncRNA length (nt)")
    ax.set_title("ncRNA length by covariance model", loc="left")
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    C.stamp(ax, "unit: exact ncRNA sequence · denominator: exact ncRNAs called by that model · "
                "bar = IQR, ring = median, thin line = min-max, shaded = 5-nt density", y=-0.10)

    ax2 = axes[1]
    ax2.barh(y, q.n_exact_ncrna, color=C.NEUTRAL, height=0.55)
    for i, r in enumerate(q.itertuples()):
        ax2.text(r.n_exact_ncrna * 1.12, i, f"{int(r.n_exact_ncrna):,d}", va="center", fontsize=7,
                 color=C.INK2)
    ax2.set_yticks(y, [""] * len(q))
    ax2.set_xscale("log")
    ax2.set_xlim(20, 20000)
    ax2.set_xlabel("exact ncRNA sequences (log)")
    ax2.set_title("how many sequences", loc="left", fontsize=9)
    ax2.grid(axis="x")
    ax2.set_axisbelow(True)
    C.save_fig(fig, "fig09_ncrna_length_by_model", q, "exact ncRNA sequences",
               "exact ncRNA sequences called by that covariance model", SCRIPT)


def fig10_model_composition():
    d = C.read_table("t10_model_composition_by_unit").sort_values("n_placements", ascending=False)
    z = C.read_table("t13_signed_distance_zoom").groupby("view_unit").n_total.max()
    deg = C.read_table("t28_degree_distribution").groupby("side").n_total.max()
    n_rt = int(deg.get("exact RT -> distinct exact ncRNAs", d.n_exact_rt.max()))
    units = [("pct_placements", f"placements\n({int(z['placement']):,d})"),
             ("pct_physical_loci", f"physical loci\n({int(z['physical locus']):,d})"),
             ("pct_exact_ncrna", f"exact ncRNAs\n({int(d.n_exact_ncrna.sum()):,d})"),
             ("pct_exact_rt", f"exact RTs\n({n_rt:,d})")]
    top = d.head(8).detection_model.tolist()
    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    x = np.arange(len(units))
    bottom = np.zeros(len(units))
    for i, m in enumerate(top + ["other models"]):
        if m == "other models":
            vals = np.array([100 - d[d.detection_model.isin(top)][c].sum() for c, _ in units])
            colr = C.NEUTRAL
        else:
            vals = np.array([float(d.loc[d.detection_model == m, c].iloc[0]) for c, _ in units])
            colr = C.PALETTE[i % 8]
        ax.bar(x, vals, bottom=bottom, width=0.58, color=colr, edgecolor="white", linewidth=1.6,
               label=m)
        for xi, (v, b) in enumerate(zip(vals, bottom)):
            if v >= 4:
                ax.text(xi, b + v / 2, f"{v:.0f}%", ha="center", va="center", fontsize=7.4,
                        color="white" if v > 8 else C.INK)
        bottom += vals
    ax.set_xticks(x, [lab for _, lab in units], fontsize=8.6)
    ax.set_ylabel("% of the unit")
    ax.set_ylim(0, 100)
    ax.legend(fontsize=7.6, ncols=3, loc="lower left", bbox_to_anchor=(0, 1.02))
    ax.set_title("The dominant covariance model changes with the counting unit", loc="left",
                 pad=34)
    C.stamp(ax, "unit: as labelled on each bar · denominator: all CANONICAL placements counted at "
                "that unit · an exact RT can carry calls by two models, so the exact-RT column "
                "is a composition, not a partition", y=-0.12)
    C.save_fig(fig, "fig10_model_composition_by_unit", d,
               "placements / physical loci / exact ncRNAs / exact RTs",
               "all CANONICAL placements counted at that unit", SCRIPT)


def fig11_subtype_by_model():
    d = C.read_table("t11_subtype_by_model")
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.0),
                             gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.42))
    for ax, tool in zip(axes, ("PADLOC", "DefenseFinder")):
        t = d[d.tool == tool]
        subs = (t.groupby("label").n_loci.max().sort_values(ascending=False).head(14).index)
        mods = (t[t.label.isin(subs)].groupby("detection_model").n_loci_with_model.sum()
                .sort_values(ascending=False).head(12).index)
        piv = (t[t.label.isin(subs) & t.detection_model.isin(mods)]
               .pivot_table(index="label", columns="detection_model",
                            values="pct_of_subtype_loci", fill_value=0.0)
               .reindex(index=subs, columns=mods))
        im = ax.imshow(piv.values, aspect="auto", cmap="Blues", vmin=0, vmax=100)
        ax.set_xticks(range(piv.shape[1]), piv.columns, rotation=45, ha="right", fontsize=7.4)
        n_by = t.groupby("label").n_loci.max()
        ax.set_yticks(range(piv.shape[0]),
                      [f"{s}  (n={int(n_by[s]):,d})" for s in piv.index], fontsize=7.6)
        for i in range(piv.shape[0]):
            for j in range(piv.shape[1]):
                v = piv.values[i, j]
                if v >= 1:
                    ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=6.4,
                            color="white" if v > 55 else C.INK)
        ax.set_title(f"{tool} subtype × covariance model", loc="left", fontsize=9.6)
        C.stamp(ax, f"unit: Retron physical locus · denominator: loci carrying that {tool} subtype "
                    f"label · cell = % of the subtype's loci with a CANONICAL call by that model",
                y=-0.30, width=74)
    fig.colorbar(im, ax=axes, pad=0.012, fraction=0.018).set_label(
        "% of the subtype's loci", fontsize=8)
    C.save_fig(fig, "fig11_subtype_by_model", d, "physical loci",
               "Retron physical loci carrying that tool's subtype label", SCRIPT)


def fig12_configuration_schematic():
    d = C.read_table("t12_configuration_classes").sort_values("n_placements", ascending=False)
    order = [c for c in d.config_class]
    fig, ax = plt.subplots(figsize=(11.0, 5.6))
    rows = len(order)
    for i, cls in enumerate(order):
        r = d[d.config_class == cls].iloc[0]
        y = rows - i - 1
        ax.add_patch(Rectangle((0.02, y - 0.3), 0.96, 0.62, facecolor="#f7f9fb" if i % 2 == 0
                               else "white", edgecolor="none", zorder=0))
        # schematic: a 0..1 strip, RT box on the right, ncRNA marker placed by class
        rt_x, rt_w = 0.60, 0.16
        ax.add_patch(Rectangle((rt_x, y - 0.10), rt_w, 0.2, facecolor=C.PALETTE[0],
                               edgecolor="none", zorder=3))
        ax.text(rt_x + rt_w / 2, y, "RT", ha="center", va="center", fontsize=7.4, color="white",
                zorder=4, fontweight="bold")
        ax.annotate("", xy=(rt_x + rt_w + 0.02, y + 0.2), xytext=(rt_x - 0.02, y + 0.2),
                    arrowprops=dict(arrowstyle="->", color=C.INK2, lw=0.9), zorder=3)
        def nc(x, colr=C.PALETTE[2]):
            ax.add_patch(Rectangle((x, y - 0.07), 0.045, 0.14, facecolor=colr, edgecolor="none",
                                   zorder=3))
        def cds(x, w=0.09, colr="#c9c8c2"):
            ax.add_patch(Rectangle((x, y - 0.085), w, 0.17, facecolor=colr, edgecolor="none",
                                   zorder=2))
        if cls.startswith("upstream, adjacent"):
            nc(0.54)
        elif cls.startswith("upstream, long"):
            nc(0.38)
            ax.plot([0.43, 0.59], [y, y], color=C.INK2, linewidth=0.8, linestyle=(0, (2, 2)))
        elif cls.startswith("upstream, one"):
            nc(0.33); cds(0.45)
        elif cls.startswith("upstream, two"):
            nc(0.20); cds(0.31); cds(0.44)
        elif cls.startswith("overlapping the RT CDS"):
            nc(0.64, C.PALETTE[4])
        elif cls.startswith("overlapping the RT interval"):
            nc(0.70, C.PALETTE[4])
        elif cls.startswith("downstream: technical"):
            nc(0.86, C.PALETTE[1])
            ax.plot([0.585, 0.585], [y - 0.26, y + 0.26], color=C.PALETTE[1], linewidth=2.2)
            ax.text(0.575, y - 0.34, "contig start", ha="center", fontsize=6.2, color=C.PALETTE[1])
        elif cls.startswith("downstream: other"):
            nc(0.86)
        ax.text(0.015, y + 0.22, cls, fontsize=8.4, color=C.INK, va="center", ha="left")
        ax.text(1.005, y + 0.06,
                f"{int(r.n_placements):,d} placements   {r.pct_placements:5.2f}%", fontsize=8,
                color=C.INK, va="center", ha="left", family="DejaVu Sans")
        ax.text(1.005, y - 0.16,
                f"{int(r.n_physical_loci):,d} physical loci · {int(r.n_exact_pairs):,d} exact "
                f"pairs · {r.pct_same_strand:.1f}% same strand", fontsize=6.9, color=C.INK2,
                va="center", ha="left")
    ax.set_xlim(0, 1.46)
    ax.set_ylim(-0.55, rows - 0.3)
    ax.axis("off")
    ax.set_title("The dominant RT↔ncRNA configurations (schematic: categories, not to scale)",
                 loc="left", pad=10)
    C.stamp(ax, "unit: CANONICAL placements (344,154), with the same placements re-counted as "
                "physical loci and exact pairs · denominator: all CANONICAL placements · green = "
                "ncRNA, blue = RT gene, grey = an intervening CDS, arrow = direction of RT "
                "transcription · the technical class is the contig-start-clipped mode g3 "
                "identified and is excluded from biological readings", y=0.01)
    C.save_fig(fig, "fig12_configuration_schematic", d, "placements (loci/pairs beside)",
               "all CANONICAL placements (344,154)", SCRIPT)


def fig13_signed_distance():
    z = C.read_table("t13_signed_distance_zoom")
    w = C.read_table("t13_signed_distance_wide")
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.4),
                             gridspec_kw=dict(width_ratios=[1.1, 1], wspace=0.22))
    ax = axes[0]
    units = [("placement", C.PALETTE[0]), ("physical locus", C.PALETTE[2]),
             ("exact pair", C.PALETTE[1])]
    for name, colr in units:
        g = z[z.view_unit == name].sort_values("bin_lo")
        tot = g.n_total.iloc[0]
        ax.step(g.bin_lo, 100 * g.n / tot, where="post", color=colr,
                linewidth=3.0 if name == "placement" else 1.6,
                alpha=0.55 if name == "placement" else 1.0,
                label=f"{name} (n={int(tot):,d})")
    ax.axvline(0, color=C.INK2, linewidth=0.8, linestyle=(0, (3, 3)))
    ax.set_xlim(-300, 300)
    ax.set_xlabel("signed distance, ncRNA → RT (bp; negative = upstream)")
    ax.set_ylabel("% of the unit per 5-bp bin")
    ax.legend(fontsize=7.6)
    ax.grid(True)
    ax.set_axisbelow(True)
    ax.set_title("Central distribution (5-bp bins)", loc="left", fontsize=9.6)
    C.stamp(ax, "unit: as in the legend · denominator: units with a defined signed distance · "
                "the locus and pair series use the median distance of the unit's placements",
            y=-0.16, width=66)

    ax2 = axes[1]
    for name, colr in units:
        g = w[w.view_unit == name].sort_values("bin_lo")
        tot = g.n_total.iloc[0]
        xs, ys = [], []
        for r in g.itertuples():
            xs += [r.bin_lo, r.bin_hi]
            ys += [100 * r.n / tot] * 2
        ax2.plot(xs, ys, color=colr, linewidth=2.0, label=f"{name} (n={int(tot):,d})",
                 drawstyle="default")
        ax2.fill_between(xs, ys, color=colr, alpha=0.12, linewidth=0)
    tm = w[w.view_unit == "placement: technical clipped mode only"]
    if not tm.empty:
        lo, hi = tm.bin_lo.min(), tm.bin_hi.max()
        ax2.axvspan(lo, hi, color=C.PALETTE[1], alpha=0.10, zorder=0)
        ax2.text((lo + hi) / 2, ax2.get_ylim()[1] * 0.92, "technical\nclipped mode", fontsize=6.8,
                 ha="center", va="top", color=C.PALETTE[1])
    ax2.set_xscale("symlog", linthresh=100)
    ax2.set_xlabel("signed distance (bp, symlog)")
    ax2.set_ylabel("% of the unit per bin")
    ax2.legend(fontsize=7.2)
    ax2.grid(True)
    ax2.set_axisbelow(True)
    ax2.set_title("Tail-aware view (−10 kb … +10 kb)", loc="left", fontsize=9.6)
    C.stamp(ax2, "unit: as in the legend · denominator: units with a defined signed distance · "
                 "bin widths are unequal; bar height is the share of the unit in that bin",
            y=-0.16, width=66)
    C.save_fig(fig, "fig13_signed_distance", pd.concat([z, w]), "the unit named in view_unit",
               "units with a defined signed distance (CANONICAL placements; their median per "
               "physical locus; the landed median per exact pair)", SCRIPT)


def fig14_abs_distance_and_mode():
    e = C.read_table("t14_abs_distance_ecdf")
    g = C.read_table("t14_upstream_gap_by_unit")
    comp = C.read_table("t14_gap_mode_composition")
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.4),
                             gridspec_kw=dict(width_ratios=[1, 1.15], wspace=0.24))
    ax = axes[0]
    for i, name in enumerate(["placement", "placement, technical mode excluded",
                              "physical locus", "exact pair"]):
        d = e[e.view_unit == name].sort_values("abs_distance_bp")
        if d.empty:
            continue
        ax.step(d.abs_distance_bp.clip(lower=1), d.cumulative_pct, where="post",
                color=C.PALETTE[i % 8], linewidth=1.9,
                label=f"{name} (n={int(d.n_total.iloc[0]):,d})")
    ax.set_xscale("log")
    ax.set_xlabel("|distance| between ncRNA and RT (bp, log)")
    ax.set_ylabel("cumulative % of the unit")
    ax.legend(fontsize=7, loc="upper left")
    ax.grid(True)
    ax.set_axisbelow(True)
    ax.set_title("How close the ncRNA sits, by unit", loc="left", fontsize=9.6)
    C.stamp(ax, "unit: as in the legend · denominator: units with a defined signed distance",
            y=-0.24, width=66)

    ax2 = axes[1]
    series = ["all CANONICAL upstream placements", "placements, most recurrent exact RT removed",
              "physical loci (median gap)", "exact pairs (median gap)"]
    labels = [f"{b.split('.')[0]}" for b in []]
    bins = g[g.series == series[0]].sort_values("bin_lo")
    x = np.arange(len(bins))
    wdt = 0.2
    for i, s in enumerate(series):
        d = g[g.series == s].set_index("bin_lo").reindex(bins.bin_lo)
        tot = g[g.series == s].n_total.iloc[0]
        ax2.bar(x + (i - 1.5) * wdt, 100 * d.n.fillna(0) / tot, width=wdt,
                color=C.PALETTE[i % 8], label=f"{s} (n={int(tot):,d})")
    ax2.set_xticks(x, [f"{int(a)}–{int(b)}" for a, b in zip(bins.bin_lo, bins.bin_hi)],
                   rotation=40, ha="right", fontsize=7.4)
    ax2.set_xlabel("upstream gap (bp)")
    ax2.set_ylabel("% of the unit")
    ax2.legend(fontsize=6.8)
    ax2.grid(axis="y")
    ax2.set_axisbelow(True)
    ax2.set_title("The second upstream mode is one re-deposited protein", loc="left", fontsize=9.6)
    top_rt = comp.top_exact_rt_sha256.iloc[0][:12]
    sp = comp.top_species.iloc[0]
    C.stamp(ax2, f"unit: as in the legend · denominator: CANONICAL upstream placements counted at "
                 f"that unit · the 900–1,100 bp band holds "
                 f"{int(comp.value.iloc[0]):,d} placements but only "
                 f"{int(comp.value.iloc[2]):,d} exact RTs; {int(comp.value.iloc[6]):,d} of them "
                 f"come from one protein ({top_rt}…, {sp})", y=-0.30, width=66)
    C.save_fig(fig, "fig14_abs_distance_and_mode", pd.concat([e, g]),
               "the unit named in view_unit / series",
               "CANONICAL placements counted at that unit", SCRIPT)


def fig15_cds_strand_overlap():
    c = C.read_table("t15_cds_between_by_unit")
    s = C.read_table("t15_strand_and_overlap")
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.0),
                             gridspec_kw=dict(width_ratios=[1.15, 1, 1], wspace=0.3))
    ax = axes[0]
    cats = ["0", "1", "2", "3", ">3"]
    x = np.arange(len(cats))
    for i, unit in enumerate(["placement", "physical locus"]):
        d = c[c.view_unit == unit].set_index("n_cds_between").reindex(cats)
        ax.bar(x + (i - 0.5) * 0.36, d.pct.fillna(0), width=0.36, color=C.PALETTE[i],
               label=f"{unit} (n={int(d.n_total.dropna().iloc[0]):,d})")
        for xi, (v, n) in enumerate(zip(d.pct.fillna(0), d.n.fillna(0))):
            if v > 0.6:
                ax.text(xi + (i - 0.5) * 0.36, v + 1.5, f"{v:.1f}%", ha="center", fontsize=6.8,
                        color=C.INK2)
    ax.set_xticks(x, cats)
    ax.set_xlabel("CDS lying wholly between the ncRNA and the RT")
    ax.set_ylabel("% of the unit")
    ax.set_ylim(0, 105)
    ax.legend(fontsize=7.2)
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    ax.set_title("Intervening CDS", loc="left", fontsize=9.6)
    C.stamp(ax, "unit: as in the legend · denominator: CANONICAL placements, or physical loci "
                "taking the minimum CDS count of the locus's placements", y=-0.19, width=60)

    ax2 = axes[1]
    d = s.set_index("direction")
    dirs = [x for x in ("upstream", "overlapping", "downstream") if x in d.index]
    x2 = np.arange(len(dirs))
    same = [d.loc[k, "pct_same_strand"] for k in dirs]
    ax2.bar(x2, same, width=0.55, color=C.PALETTE[0])
    for i, k in enumerate(dirs):
        ax2.text(i, same[i] + 1.2, f"{same[i]:.1f}%", ha="center", fontsize=7.6, color=C.INK)
        ax2.text(i, 4, f"n={int(d.loc[k, 'n_placements']):,d}", ha="center", fontsize=6.8,
                 color="white")
    ax2.set_xticks(x2, dirs, fontsize=8.4)
    ax2.set_ylim(0, 108)
    ax2.set_ylabel("% on the same strand as the RT")
    ax2.grid(axis="y")
    ax2.set_axisbelow(True)
    ax2.set_title("Strand agreement", loc="left", fontsize=9.6)
    C.stamp(ax2, "unit: placement · denominator: CANONICAL placements of that direction",
            y=-0.19, width=52)

    ax3 = axes[2]
    tot = s.n_placements.sum()
    bars = [("overlaps any CDS", s.n_overlaps_any_cds.sum()),
            ("overlaps the RT CDS", s.n_overlaps_rt_cds.sum()),
            ("overlaps a non-RT CDS", s.n_overlaps_non_rt_cds.sum())]
    y3 = np.arange(len(bars))[::-1]
    ax3.barh(y3, [100 * v / tot for _, v in bars], color=C.PALETTE[4], height=0.5)
    for yy, (lab, v) in zip(y3, bars):
        ax3.text(100 * v / tot + 0.4, yy, f"{100*v/tot:.1f}%  ({int(v):,d})", va="center",
                 fontsize=7.4, color=C.INK)
    ax3.set_yticks(y3, [lab for lab, _ in bars], fontsize=8.2)
    ax3.set_xlim(0, 26)
    ax3.set_xlabel("% of CANONICAL placements")
    ax3.grid(axis="x")
    ax3.set_axisbelow(True)
    ax3.set_title("CDS overlap", loc="left", fontsize=9.6)
    C.stamp(ax3, "unit: placement · denominator: all CANONICAL placements (344,154) · g3's "
                 "'non-RT' flag means 'overlaps a CDS and not the RT CDS'", y=-0.19, width=52)
    C.save_fig(fig, "fig15_cds_strand_overlap", pd.concat([c, s]),
               "placements / physical loci", "CANONICAL placements counted at that unit", SCRIPT)


def fig16_geometry_by_model():
    g = C.read_table("t16_geometry_by_model").sort_values("n_physical_loci", ascending=False)
    h = C.read_table("t16_distance_histogram_by_model")
    mods = [m for m in g.detection_model if m in set(h.detection_model)][:12]
    fig, axes = plt.subplots(3, 4, figsize=(12.6, 6.4), sharex=True)
    for ax, m in zip(axes.ravel(), mods):
        d = h[h.detection_model == m].sort_values("bin_lo")
        tot = d.n_total.iloc[0]
        centres = (d.bin_lo + d.bin_hi) / 2
        widths = (d.bin_hi - d.bin_lo)
        r = g[g.detection_model == m].iloc[0]
        colr = C.PALETTE[1] if r.pct_in_technical_mode > 20 else C.PALETTE[0]
        ax.bar(centres, 100 * d.n / tot, width=widths * 0.92, color=colr, edgecolor="white",
               linewidth=0.4)
        ax.axvline(0, color=C.INK2, linewidth=0.7, linestyle=(0, (3, 3)))
        ax.set_xscale("symlog", linthresh=100)
        ax.set_ylim(0, max(1.0, float((100 * d.n / tot).max())) * 1.42)
        ax.set_title(f"{m}", loc="left", fontsize=8.2)
        ax.text(0.02, 0.98, f"n={int(r.n_physical_loci):,d} loci\n"
                            f"{r.pct_upstream:.0f}% upstream · {r.pct_0_cds_between:.0f}% 0 CDS\n"
                            f"median {r.median_signed_distance_bp:,.0f} bp",
                transform=ax.transAxes, fontsize=6.2, color=C.INK2, va="top")
        if r.pct_in_technical_mode > 20:
            ax.text(0.98, 0.62, f"{r.pct_in_technical_mode:.0f}% in the\ntechnical mode",
                    transform=ax.transAxes, fontsize=6.2, color=C.PALETTE[1], va="top", ha="right")
        ax.tick_params(labelsize=6.6)
        ax.grid(axis="y")
        ax.set_axisbelow(True)
    for ax in axes.ravel()[len(mods):]:
        ax.axis("off")
    for ax in axes[-1]:
        ax.set_xlabel("signed distance (bp, symlog)", fontsize=7.4)
    for ax in axes[:, 0]:
        ax.set_ylabel("% of the model's loci", fontsize=7.4)
    fig.suptitle("RT↔ncRNA geometry differs by covariance model (physical loci)", x=0.065,
                 y=0.99, ha="left", fontsize=11, fontweight="bold")
    C.stamp(axes[-1, 0], "unit: physical locus · denominator: CANONICAL physical loci carrying a "
                         "call by that model (models with ≥200 loci) · orange = a model whose "
                         "loci fall mostly in the contig-start-clipped technical mode",
            y=-0.42, width=150)
    C.save_fig(fig, "fig16_geometry_by_model", h[h.detection_model.isin(mods)], "physical loci",
               "CANONICAL physical loci of that model", SCRIPT)


if __name__ == "__main__":
    C.log("== f02 figures, sections 4-5")
    fig09_ncrna_length()
    fig10_model_composition()
    fig11_subtype_by_model()
    fig12_configuration_schematic()
    fig13_signed_distance()
    fig14_abs_distance_and_mode()
    fig15_cds_strand_overlap()
    fig16_geometry_by_model()
