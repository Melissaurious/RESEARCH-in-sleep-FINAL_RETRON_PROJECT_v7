#!/usr/bin/env python3
"""f01 - figures for sections 1-3. Reads ONLY this bundle's tables/ (REPORTING_STANDARDS)."""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C

SCRIPT = "f01_corpus.py"
plt = C.mpl_setup()


def thousands(v: float) -> str:
    if v >= 1e6:
        return f"{v/1e6:.2f}M".rstrip("0").rstrip(".") + "M" if False else f"{v/1e6:.2f}M"
    if v >= 1e3:
        return f"{v/1e3:.0f}k"
    return f"{v:.0f}"


def fig01_funnel():
    d = C.read_table("t01_unit_funnel")
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    n0 = d.n.iloc[0]
    y = np.arange(len(d))[::-1]
    for i, r in d.iterrows():
        w = r.n / n0
        ax.barh(y[i], w, height=0.62, left=(1 - w) / 2, color=C.PALETTE[0],
                alpha=0.35 + 0.13 * i, edgecolor="white", linewidth=2)
        ax.text(0.5, y[i], f"{int(r.n):,d}", ha="center", va="center", fontsize=11,
                color=C.INK, fontweight="bold")
        ax.text(1.02, y[i] + 0.14, r.step, ha="left", va="center", fontsize=9.5, color=C.INK)
        ax.text(1.02, y[i] - 0.2, r.definition, ha="left", va="center", fontsize=7.6,
                color=C.INK2)
        if i:
            ax.text(-0.02, y[i] + 0.34, f"− {int(r.n_removed):,d}  {r.removed_by}", ha="right",
                    va="center", fontsize=7.8, color=C.PALETTE[1])
        ax.text(0.5, y[i] - 0.34, f"{r.pct_of_raw_records:.1f}% of raw records",
                ha="center", va="center", fontsize=7.2, color=C.INK2)
    ax.set_xlim(-0.52, 1.62)
    ax.set_ylim(-0.7, len(d) - 0.3)
    ax.axis("off")
    ax.set_title("From raw records to exact RT proteins: what each normalisation step removes",
                 loc="left", pad=12)
    C.stamp(ax, "unit: the level named on each bar · denominator: raw RT-anchored records "
                "(3,059,700) for the percentages · bar width ∝ count", y=0.02)
    C.save_fig(fig, "fig01_unit_funnel", d, "the unit named in the row",
               "raw RT-anchored records (3,059,700) for the percentage column", SCRIPT)


def fig02_database_structure():
    lad = C.read_table("t02_ladder_by_database")
    ups = C.read_table("t02_exact_rt_database_upset")
    fig = plt.figure(figsize=(11.2, 5.0))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.35], wspace=0.34)

    ax = fig.add_subplot(gs[0, 0])
    d = lad.sort_values("loci_per_exact_rt")
    y = np.arange(len(d))
    ax.hlines(y, 1, d.loci_per_exact_rt, color=C.GRID, linewidth=2)
    ax.scatter(d.loci_per_exact_rt, y, s=54, color=C.PALETTE[0], zorder=3)
    for i, r in enumerate(d.itertuples()):
        ax.text(r.loci_per_exact_rt + 0.1, i, f"{r.loci_per_exact_rt:.2f}", va="center",
                fontsize=8, color=C.INK, fontweight="bold")
        ax.text(6.45, i, f"{int(r.n_exact_rt):,d} exact RTs", va="center", ha="right",
                fontsize=7.2, color=C.INK2)
    ax.set_yticks(y, d.source_database, fontsize=8.5)
    ax.set_xlim(0, 6.6)
    ax.set_xlabel("loci per exact RT sequence")
    ax.set_title("Redundancy is database-specific", loc="left", fontsize=9.5)
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    C.stamp(ax, "unit: exact RT · denominator: exact RTs seen in that database", y=-0.13)

    ax2 = fig.add_subplot(gs[0, 1])
    sets = list(C.BIG_DBS) + ["other database"]
    d2 = ups.sort_values("n_exact_rt", ascending=False).head(10).reset_index(drop=True)
    x = np.arange(len(d2))
    ax2.bar(x, d2.n_exact_rt, color=C.PALETTE[0], width=0.66)
    for i, v in enumerate(d2.n_exact_rt):
        ax2.text(i, v * (1.08 if i % 2 == 0 else 2.2), f"{int(v):,d}", ha="center", fontsize=7.4,
                 color=C.INK)
    ax2.set_yscale("log")
    ax2.set_ylim(1, d2.n_exact_rt.max() * 8)
    ax2.set_ylabel("exact RT sequences (log)")
    ax2.set_xticks([])
    ax2.set_title("Which databases an exact RT protein is seen in", loc="left", fontsize=9.5)
    ax2.grid(axis="y")
    ax2.set_axisbelow(True)
    # the UpSet matrix under the bars
    base = -0.55
    step = 0.28
    for j, s in enumerate(sets):
        yy = base - j * step
        for i, r in d2.iterrows():
            on = s in str(r.membership).split("|")
            ax2.plot([i], [10 ** (yy)], "o", ms=7,
                     color=C.PALETTE[0] if on else "#dcdbd6",
                     transform=ax2.get_xaxis_transform(which="grid") if False else ax2.transData,
                     clip_on=False)
        ax2.text(-0.9, 10 ** yy, s, ha="right", va="center", fontsize=7.8, color=C.INK2)
    for i, r in d2.iterrows():
        members = [s for s in sets if s in str(r.membership).split("|")]
        if len(members) > 1:
            ys = [base - sets.index(s) * step for s in members]
            ax2.plot([i, i], [10 ** min(ys), 10 ** max(ys)], color=C.PALETTE[0], linewidth=1.6,
                     clip_on=False)
    ax2.set_xlim(-1.1, len(d2) - 0.4)
    C.stamp(ax2, "unit: exact RT sequence · denominator: all 501,561 exact RTs · "
                 "dots mark the databases the protein occurs in", y=-0.42)
    C.save_fig(fig, "fig02_database_structure", ups, "exact RT sequences",
               "all 501,561 exact RT sequences (right panel); exact RTs of that database "
               "(left panel)", SCRIPT)


def fig03_recurrence():
    cc = C.read_table("t03_recurrence_ccdf")
    conc = C.read_table("t03_recurrence_concentration")
    fams = (cc[cc.metric == "physical loci per exact RT"]
            .groupby("family").n_exact_rt_total.max().sort_values(ascending=False).head(6).index)
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.1))
    titles = ("physical loci per protein", "genomes per protein", "databases per protein")
    xmax = {"physical loci per exact RT": 2e4, "genomes per exact RT": 2e4,
            "databases per exact RT": 9}
    for ax, metric, ttl in zip(axes, ("physical loci per exact RT", "genomes per exact RT",
                                      "databases per exact RT"), titles):
        d = cc[cc.metric == metric]
        for i, fam in enumerate(fams):
            g = d[d.family == fam].sort_values("at_least")
            ax.plot(g.at_least, g.pct, marker="o", ms=4, color=C.PALETTE[i % 8], label=fam,
                    linewidth=1.8)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel(metric)
        ax.set_xlim(0.85, xmax[metric])
        ax.set_title(ttl, loc="left", fontsize=9.2)
        ax.grid(True, which="major")
        ax.set_axisbelow(True)
    axes[0].set_ylabel("% of the family's exact RTs at or above x")
    axes[0].legend(fontsize=7.4, loc="lower left")
    fig.suptitle("How often one exact RT protein is re-deposited", x=0.09, y=1.02, ha="left",
                 fontsize=11, fontweight="bold")
    c = conc[conc.top_fraction_of_exact_rt == 0.01].set_index("family")
    note = " · ".join(f"top 1% of {f} exact RTs carry {c.loc[f, 'pct_of_physical_loci']:.0f}% of "
                      f"its physical loci" for f in ("RVT-GII", "Retron") if f in c.index)
    C.stamp(axes[0], "unit: exact RT sequence · denominator: exact RTs of that family bucket · "
                     + note, y=-0.22)
    C.save_fig(fig, "fig03_exact_rt_recurrence", cc[cc.family.isin(fams)], "exact RT sequences",
               "exact RT sequences of that family bucket", SCRIPT)


def fig04_share_by_unit():
    d = C.read_table("t04_family_share_by_unit").sort_values("pct_records", ascending=True)
    d = d[d.family != "other"]
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    y = np.arange(len(d))
    for i, r in enumerate(d.itertuples()):
        ax.plot([r.pct_records, r.pct_exact_rt], [i, i], color=C.GRID, linewidth=2.4, zorder=1)
    ax.scatter(d.pct_records, y, s=52, color=C.PALETTE[1], zorder=3, label="% of raw records")
    ax.scatter(d.pct_physical_loci, y, s=34, color=C.NEUTRAL, zorder=3, marker="D",
               label="% of physical loci")
    ax.scatter(d.pct_exact_rt, y, s=52, color=C.PALETTE[0], zorder=3, label="% of exact RTs")
    for i, r in enumerate(d.itertuples()):
        lab = f"×{r.shift_records_to_exact_rt:.2f}"
        ax.text(max(r.pct_records, r.pct_exact_rt) + 1.2, i, lab, va="center", fontsize=7.6,
                color=C.PALETTE[0] if r.shift_records_to_exact_rt > 1 else C.PALETTE[1])
    ax.set_yticks(y, d.family, fontsize=8.6)
    ax.set_xlabel("share of the catalogue (%)")
    ax.set_xlim(0, 62)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    ax.set_title("Family abundance depends on the unit it is counted in", loc="left")
    C.stamp(ax, "unit: records / physical loci / exact RTs · denominator: all RT-anchored units "
                "of that level · ×n = exact-RT share ÷ record share", y=-0.14)
    C.save_fig(fig, "fig04_family_share_by_unit", d,
               "records / loci / physical loci / exact RTs",
               "all RT-anchored units of that level (MULTI included as its own row; the 29-family "
               "'other' bucket is omitted from the figure and present in the table)", SCRIPT)


def fig05_database_family_heatmap():
    d = C.read_table("t05_database_family_composition")
    piv = d.pivot_table(index="source_database", columns="family",
                        values="pct_of_database_exact_rt", fill_value=0.0)
    order = (C.read_table("t04_family_share_by_unit").sort_values("n_exact_rt", ascending=False)
             .family.tolist())
    piv = piv.reindex(columns=[c for c in order if c in piv.columns])
    piv = piv.reindex([x for x in C.DB_ORDER if x in piv.index])
    fig, ax = plt.subplots(figsize=(10.4, 3.6))
    im = ax.imshow(piv.values, aspect="auto", cmap="Blues", vmin=0, vmax=60)
    ax.set_xticks(range(piv.shape[1]), piv.columns, rotation=40, ha="right", fontsize=8)
    ax.set_yticks(range(piv.shape[0]), piv.index, fontsize=8.4)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.values[i, j]
            if v >= 1:
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7,
                        color="white" if v > 34 else C.INK)
    cb = fig.colorbar(im, ax=ax, pad=0.015, fraction=0.03)
    cb.set_label("% of that database's exact RTs", fontsize=8)
    ax.set_title("Family composition of each source database, on exact RT sequences", loc="left")
    C.stamp(ax, "unit: exact RT sequence (distinct within a database) · denominator: exact RTs "
                "seen in that database · cells below 1% are left unlabelled", y=-0.32)
    C.save_fig(fig, "fig05_database_family_heatmap", d,
               "exact RT sequences (distinct within a database)",
               "exact RT sequences seen in that source database", SCRIPT)


def fig06_family_ranked():
    d = C.read_table("t06_family_ranked").sort_values("n_exact_rt", ascending=True)
    fig, ax = plt.subplots(figsize=(9.4, 5.0))
    y = np.arange(len(d))
    colors = [C.PALETTE[3] if f == "MULTI" else (C.NEUTRAL if f == "other" else C.PALETTE[0])
              for f in d.family]
    ax.barh(y, d.n_exact_rt, color=colors, height=0.62)
    ax.scatter(d.n_physical_loci, y, marker="|", s=110, color=C.PALETTE[1], zorder=3,
               label="physical loci")
    ax.scatter(d.n_records, y, marker="|", s=110, color=C.INK2, zorder=3, label="raw records")
    for i, r in enumerate(d.itertuples()):
        ax.text(r.n_exact_rt * 1.15, i, f"{int(r.n_exact_rt):,d}", va="center", fontsize=7.6,
                color=C.INK)
    ax.set_yticks(y, d.family, fontsize=8.6)
    ax.set_xscale("log")
    ax.set_xlim(300, 6e6)
    ax.set_xlabel("count (log scale)")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    ax.set_title("RT families ranked by exact RT sequences (bars), with loci and records marked",
                 loc="left")
    C.stamp(ax, "unit: exact RT sequences (bars) · denominator: n/a - counts. MULTI (gold) is an "
                "ambiguity stratum, never merged into a family; 'other' pools 29 small families",
            y=-0.13)
    C.save_fig(fig, "fig06_family_ranked", d, "exact RTs (bar) with loci/records beside",
               "all RT-anchored units of that level", SCRIPT)


def fig07_rt_length_violins():
    h = C.read_table("t07_rt_length_histogram")
    q = C.read_table("t07_rt_length_quantiles")
    qa = q[q.completeness_class == "ALL"].sort_values("n_exact_rt", ascending=False)
    fams = [f for f in qa.family if f != "other"][:13]
    fig, ax = plt.subplots(figsize=(11.6, 5.2))
    classes = [("all_complete", C.PALETTE[0], "complete (Prodigal)"),
               ("all_partial", C.PALETTE[1], "partial (Prodigal)")]
    for xi, fam in enumerate(fams):
        for side, (cl, colr, _) in enumerate(classes):
            gall = h[(h.family == fam) & (h.completeness_class == cl)]
            if gall.empty:
                continue
            n = gall.n_exact_rt.sum()
            g = gall[gall.bin_start_aa < 1210]          # the pooled >=1,205 aa bin is not a bin
            n_over = int(gall[gall.bin_start_aa >= 1210].n_exact_rt.sum())
            if g.empty:
                continue
            w = g.n_exact_rt.to_numpy() / g.n_exact_rt.max() * 0.42
            yv = g.bin_start_aa.to_numpy() + 5
            sgn = -1 if side == 0 else 1
            ax.fill_betweenx(yv, xi, xi + sgn * w, color=colr, alpha=0.75, linewidth=0)
            qq = q[(q.family == fam) & (q.completeness_class == cl)]
            if not qq.empty:
                r = qq.iloc[0]
                ax.plot([xi + sgn * 0.06, xi + sgn * 0.06], [r.q25, r.q75], color="white",
                        linewidth=2.6, solid_capstyle="butt", zorder=4)
                ax.plot([xi + sgn * 0.06], [r["median"]], "o", ms=3.4, color="white", zorder=5)
                lab = f"n={int(n):,d}" + (f" (+{n_over} >1.2k)" if n_over else "")
                ax.text(xi + sgn * 0.46, 1145 if side else 1075, lab, fontsize=6.2,
                        ha="center", color=colr)
    ax.set_xticks(range(len(fams)), fams, rotation=35, ha="right", fontsize=8.2)
    ax.set_ylim(0, 1210)
    ax.set_ylabel("RT length (aa)")
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    for cl, colr, lab in classes:
        ax.fill_between([], [], color=colr, alpha=0.75, label=lab)
    ax.legend(fontsize=8, loc="lower left", bbox_to_anchor=(0.0, 1.005), ncols=2)
    ax.set_title("RT length per family, split by Prodigal completeness "
                 "(left half = complete, right half = partial)", loc="left", pad=22)
    C.stamp(ax, "unit: exact RT sequence · denominator: exact RTs of that family and completeness "
                "class (V-RT-SINGLE; MULTI is its own column) · each half is scaled to its own "
                "widest 10-aa bin, so widths compare shape, not count · white bar = IQR, dot = "
                "median · RTs above 1,200 aa and the 'mixed/no evidence' class are in the table",
            y=-0.17)
    C.save_fig(fig, "fig07_rt_length_violins", h[h.family.isin(fams)], "exact RT sequences",
               "exact RTs of that family and completeness class, binned at 10 aa", SCRIPT)


def fig08_rt_length_ecdf():
    e = C.read_table("t08_rt_length_ecdf")
    s = C.read_table("t08_rt_length_shape").sort_values("n_exact_rt", ascending=False)
    fams = [f for f in s.family if f != "other"][:8]
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.2),
                             gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.26))
    ax = axes[0]
    for i, fam in enumerate(fams):
        g = e[e.family == fam].sort_values("rt_aa_len")
        ax.step(g.rt_aa_len, g.cumulative_pct, where="post", color=C.PALETTE[i % 8], linewidth=1.9,
                label=f"{fam} (n={int(g.n_exact_rt.iloc[0]):,d})")
    ax.set_xlim(0, 1200)
    ax.set_xlabel("RT length (aa)")
    ax.set_ylabel("cumulative % of the family's exact RTs")
    ax.legend(fontsize=7.2, loc="lower right")
    ax.grid(True)
    ax.set_axisbelow(True)
    ax.set_title("Length ECDF: shifts and shoulders are visible without violins", loc="left",
                 fontsize=9.6)
    C.stamp(ax, "unit: exact RT · denominator: exact RTs of that family", y=-0.15)

    ax2 = axes[1]
    d = s[s.family != "other"].sort_values("iqr_over_median")
    y = np.arange(len(d))
    colors = [C.PALETTE[1] if m > 1 else C.PALETTE[0] for m in d.n_modes_declared_rule]
    ax2.barh(y, d.iqr_over_median, color=colors, height=0.6)
    for i, r in enumerate(d.itertuples()):
        ax2.text(r.iqr_over_median + 0.012, i,
                 f"{r.iqr_over_median:.2f}  ({r.n_modes_declared_rule} mode"
                 f"{'s' if r.n_modes_declared_rule > 1 else ''})", va="center", fontsize=7,
                 color=C.INK2)
    ax2.set_yticks(y, d.family, fontsize=8)
    ax2.set_xlim(0, d.iqr_over_median.max() * 1.45)
    ax2.set_xlabel("IQR ÷ median (length dispersion)")
    ax2.grid(axis="x")
    ax2.set_axisbelow(True)
    ax2.set_title("Which families have broad or multimodal length", loc="left", fontsize=9.6)
    C.stamp(ax2, "unit: exact RT · denominator: exact RTs of that family · modes by the declared "
                 "smoothed-histogram rule (see t08_rt_length_shape)", y=-0.15)
    C.save_fig(fig, "fig08_rt_length_ecdf", e[e.family.isin(fams)], "exact RT sequences",
               "exact RTs of that family (V-RT-SINGLE; MULTI separate)", SCRIPT)


if __name__ == "__main__":
    C.log("== f01 figures, sections 1-3")
    fig01_funnel()
    fig02_database_structure()
    fig03_recurrence()
    fig04_share_by_unit()
    fig05_database_family_heatmap()
    fig06_family_ranked()
    fig07_rt_length_violins()
    fig08_rt_length_ecdf()
