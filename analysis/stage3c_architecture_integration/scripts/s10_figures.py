#!/usr/bin/env python3
"""s3c figures — views over landed tables ONLY (REPORTING_STANDARDS: a figure adds no measurement).

Every figure ships PNG + SVG in figures/ and its data as tables/<same basename>.tsv.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3clib as L  # noqa: E402

# svg.hashsalt pins matplotlib's element-id hashing; without it every SVG differs on rerun (BS-3)
plt.rcParams.update({"svg.hashsalt": "stage3c", "figure.dpi": 150, "font.size": 8, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.bbox": "tight"})
C = {"a": "#3b6ea5", "b": "#c1666b", "c": "#6e9887", "d": "#d4a24c", "grey": "#9a9a9a"}


def save(fig, name, rows, cols):
    fig.savefig(os.path.join(L.FIGURES, name + ".png"))
    # matplotlib stamps a creation date into SVG metadata; suppressed so the figure is
    # byte-reproducible on rerun (BS-3)
    fig.savefig(os.path.join(L.FIGURES, name + ".svg"), metadata={"Date": None})
    plt.close(fig)
    # a figure may plot rows from two landed tables; pad the union of columns so the shipped
    # data TSV is rectangular and every plotted value is present in it (BS-13)
    padded = [{c: r.get(c, "") for c in cols} for r in rows]
    L.write_tsv(os.path.join(L.TABLES, name + ".tsv"), padded, cols)
    print("figure", name, len(rows), "data rows")


# ---------------------------------------------------------------- F1: catalytic site vs units
A = L.read_tsv(os.path.join(L.TABLES, "A_summary.tsv"))
keep = ["site_in_one_unit", "site_in_palm_like_unit_given_palm_CALL",
        "site_in_max_strand_unit_given_no_palm_CALL", "site_unit_discontinuous",
        "detector_prediction_in_same_unit_as_truth", "detector_HIT_as_frozen_by_3B"]
rows = [r for r in A if r["arm"] == "primary" and r["stratum"] == "all_in_scope" and r["metric"] in keep]
rows.sort(key=lambda r: keep.index(r["metric"]))
fig, ax = plt.subplots(figsize=(6.4, 2.8))
y = range(len(rows))
vals = [float(r["value"]) for r in rows]
ax.barh(list(y), vals, color=[C["a"] if r["metric"] != "detector_HIT_as_frozen_by_3B" else C["grey"] for r in rows])
for i, r in enumerate(rows):
    ax.text(float(r["value"]) + 0.015, i, f"{r['numerator']}/{r['denominator']}", va="center", fontsize=7)
ax.set_yticks(list(y))
ax.set_yticklabels([r["metric"].replace("_", " ") for r in rows], fontsize=7)
ax.set_xlim(0, 1.15)
ax.set_xlabel("fraction of Tier-A truth-bearing chains (n = 19)")
ax.set_title("A · Stage-3B catalytic site vs frozen Stage-3A units", loc="left", fontsize=9)
ax.invert_yaxis()
save(fig, "F1_catalytic_site_vs_units", rows, list(rows[0]))

# ---------------------------------------------------------------- F2: state blocks vs units
B = [r for r in L.read_tsv(os.path.join(L.TABLES, "B_block_summary.tsv"))
     if r["arm"] == "primary" and r["stratum"] == "all"]
order = ["RT0_none", "RT1_none", "SB2p", "SB3", "SB4", "SB56", "SB7", "CAT262"]
B.sort(key=lambda r: order.index(r["block"]))
fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.0), gridspec_kw={"width_ratios": [1.25, 1]})
ax = axes[0]
x = range(len(B))
av = [int(r["n_available"]) for r in B]
co = [int(r["n_contained"]) for r in B]
sp = [int(r["n_split"]) for r in B]
ax.bar(list(x), [62] * len(B), color="#eeeeee", label="not available")
ax.bar(list(x), av, color=C["b"], label="available, split")
ax.bar(list(x), co, color=C["a"], label="available, contained in one unit")
ax.set_xticks(list(x))
ax.set_xticklabels([r["block"] for r in B], rotation=45, ha="right", fontsize=7)
ax.set_ylabel("chains (of 62)")
ax.set_title("B · Stage-2 state blocks on structures", loc="left", fontsize=9)
ax.legend(fontsize=6, frameon=False)
ax2 = axes[1]
lin = [r for r in L.read_tsv(os.path.join(L.TABLES, "B_block_by_lineage.tsv"))
       if r["stratum_METADATA"] in ("bacterial:retron", "non-LTR", "bacterial")]
strat = ["bacterial", "bacterial:retron", "non-LTR"]
w = 0.26
for i, s in enumerate(strat):
    S = {r["block"]: r for r in lin if r["stratum_METADATA"] == s}
    ax2.bar([j + (i - 1) * w for j in range(len(order))],
            [float(S[b]["frac_available"]) if b in S else 0 for b in order], width=w,
            color=[C["a"], C["b"], C["c"]][i], label=s)
ax2.set_xticks(range(len(order)))
ax2.set_xticklabels(order, rotation=45, ha="right", fontsize=7)
ax2.set_ylabel("fraction of chains with the block available")
ax2.set_title("by metadata stratum (GII-centred frame)", loc="left", fontsize=8)
ax2.legend(fontsize=6, frameon=False)
save(fig, "F2_state_blocks_vs_units", B + lin, sorted(set(list(B[0]) + list(lin[0]))))

# ---------------------------------------------------------------- F3: literature/historical overlap
O = L.read_tsv(os.path.join(L.TABLES, "C_overlap.tsv"))
fig, ax = plt.subplots(figsize=(6.4, 3.0))
kinds = ["fingers", "palm", "thumb", "fingers_palm_combined"]
strata = ["LITERATURE", "HISTORICAL_RED"]
for i, k in enumerate(kinds):
    for j, s in enumerate(strata):
        vals = [float(r["best_jaccard"]) for r in O if r["region"] == k and r["stratum"] == s]
        if not vals:
            continue
        xs = [i + (j - 0.5) * 0.3 + (n - len(vals) / 2) * 0.012 for n in range(len(vals))]
        ax.scatter(xs, vals, s=14, color=C["a"] if s == "LITERATURE" else C["d"],
                   label=s if i == 0 else None, alpha=0.85, edgecolors="none")
ax.axhline(0.70, color=C["b"], lw=1, ls="--")
ax.text(3.35, 0.72, "3A C7 bar 0.70", color=C["b"], fontsize=6)
ax.set_xticks(range(len(kinds)))
ax.set_xticklabels([k.replace("_", " ") for k in kinds], fontsize=7)
ax.set_ylabel("best Jaccard with a frozen PDP unit")
ax.set_ylim(0, 1.02)
ax.set_title("C · literature and historical fingers/palm/thumb vs frozen units", loc="left", fontsize=9)
ax.legend(fontsize=6, frameon=False, loc="upper left")
save(fig, "F3_literature_overlap", O, list(O[0]))

# ---------------------------------------------------------------- F4: region Y and the nucleic acid
E = L.read_tsv(os.path.join(L.TABLES, "D_region_y_rna_enrichment.tsv"))
fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.3, 1]})
ax = axes[0]
E2 = sorted(E, key=lambda r: (r["is_retron_family"] != "YES", -float(r["rna_ratio_observed_over_expected"] or 0)))
xs = range(len(E2))
ax.bar(list(xs), [float(r["rna_ratio_observed_over_expected"] or 0) for r in E2],
       color=[C["b"] if r["is_retron_family"] == "YES" else C["grey"] for r in E2])
ax.axhline(1.0, color="k", lw=0.8)
ax.set_xticks(list(xs))
ax.set_xticklabels([r["chain"] for r in E2], rotation=90, fontsize=6)
ax.set_ylabel("RNA-contact residues in Y\n÷ length-proportional expectation")
ax.set_title("D · Region Y and the deposited RNA", loc="left", fontsize=9)
ax.text(0.02, 0.95, "red = retron family", transform=ax.transAxes, fontsize=6, color=C["b"], va="top")
D = [r for r in L.read_tsv(os.path.join(L.TABLES, "D_summary.tsv")) if r["stratum"] in ("retron", "non-retron")]
ax2 = axes[1]
cats = ["n_NAXXH_strict", "n_Y_interval_from_VTG", "n_no_VTG_like_in_window", "n_X_undefined"]
for i, r in enumerate(D):
    ax2.bar([j + (i - 0.5) * 0.35 for j in range(len(cats))], [int(r[c]) for c in cats], width=0.35,
            color=[C["b"], C["grey"]][i], label=r["stratum"] + f" (n={r['n_chains']})")
ax2.set_xticks(range(len(cats)))
ax2.set_xticklabels([c.replace("n_", "").replace("_", " ") for c in cats], rotation=30, ha="right", fontsize=6)
ax2.set_ylabel("chains")
ax2.set_title("X/Y motif and interval status", loc="left", fontsize=8)
ax2.legend(fontsize=6, frameon=False)
save(fig, "F4_region_y_rna", E + D, sorted(set(list(E[0]) + list(D[0]))))

# ---------------------------------------------------------------- F5: architecture vs decomposition
T = L.read_tsv(os.path.join(L.S3C, "TERMINI_FUSION_SUMMARY.tsv"))
fig, ax = plt.subplots(figsize=(6.0, 3.0))
groups = [("palm-like CALL", [r for r in T if r["C4_palm"] == "CALL"]),
          ("no palm-like call", [r for r in T if r["C4_palm"] != "CALL"])]
for i, (name, S) in enumerate(groups):
    xs = [int(r["n_units"]) + (0.08 * (n % 5 - 2)) for n, r in enumerate(S)]
    ys = [int(r["n_units_outside_core"]) + 0.08 * (n % 5 - 2) for n, r in enumerate(S)]
    ax.scatter(xs, ys, s=18, color=[C["a"], C["b"]][i], alpha=0.8, edgecolors="none", label=f"{name} (n={len(S)})")
ax.set_xlabel("PDP units in the chain")
ax.set_ylabel("units lying wholly outside the mapped RT core")
ax.set_title("E · accessory architecture vs the 3A palm-like call", loc="left", fontsize=9)
ax.legend(fontsize=6, frameon=False)
save(fig, "F5_architecture_vs_calls", T, list(T[0]))
