#!/usr/bin/env python3
"""f01_restyle_figures - re-plot two landed figures legibly, for the Stage-1 report.

Two figures landed in earlier gates are numerically correct and badly drawn:

  * `dbchar_g3_pair_geometry/fig01_distance_distribution` - raw-float bin labels rotated into
    the denominator stamp, and the two panels' stamps collide;
  * `dbchar_g4_family_baseline/fig01_rt_length_by_family` - the stamp sits at -0.22 axes
    fractions of a 26-row axis, which on a tall plot is a ~2-inch band of white.

REPORTING_STANDARDS puts a restyle in a NEW gate reading the landed table - never an edit to the
landed bundle (BS-6), and the launcher §"Decide alone" allows replacing a weak figure with a
better one over a measurement already in scope. So this script reads ONLY the landed TSV that
each figure shipped beside itself, recomputes NOTHING, and re-emits those rows verbatim beside
the new figure (BS-13). The only transformation applied to any number is a label format.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# matplotlib salts SVG element ids from a random seed, so two identical runs emit different
# clip-path/marker names. A declared salt makes the SVG byte-reproducible like everything else.
matplotlib.rcParams["svg.hashsalt"] = "dbchar_g7_stage1_report"

BLUE, ORANGE, DARK = "#2f6f9f", "#d1834a", "#13324b"
SRC_GEOM = "dbchar_g3_pair_geometry/tables/fig01_distance_distribution.tsv"
SRC_LEN = "dbchar_g4_family_baseline/tables/fig01_rt_length_by_family.tsv"


def rd(p: Path) -> list[dict]:
    if not p.exists():
        raise SystemExit(f"FATAL: landed input missing: {p}")
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def emit(fig, rows: list[dict], name: str, W: Path) -> None:
    """Save PNG+SVG and carry the plotted rows through unchanged (BS-13)."""
    # SVG carries a <dc:date> and PNG a software tag unless pinned; both would break the
    # byte-for-byte rerun comparison that is this gate's stop condition (BS-3).
    fig.savefig(W / "figures" / f"{name}.png", dpi=200, metadata={"Software": None})
    fig.savefig(W / "figures" / f"{name}.svg", metadata={"Date": None})
    plt.close(fig)
    cols = list(rows[0])
    with (W / "tables" / f"{name}.tsv").open("w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(r[c] for c in cols) + "\n")
    print(f"  {name}.png / .svg / .tsv  ({len(rows)} rows carried through unchanged)")


# --------------------------------------------------------------------------- geometry
def bp(v: str) -> str:
    """Compact edge label. 10000.0 -> 10k, -2000.0 -> -2k, -50.0 -> -50, -10000.001 -> -10k."""
    f = float(v)
    neg = "−" if f < 0 else ""
    a = abs(f)
    if a >= 1000:
        s = f"{a / 1000:.0f}k" if abs(a / 1000 - round(a / 1000)) < 0.01 else f"{a / 1000:.1f}k"
    else:
        s = f"{a:.0f}"
    return f"{neg}{s}"


def geom_panel(ax, rows: list[dict], pop: str, colour: str) -> int:
    labels = [f"{bp(r['bin_left_bp'])} to {bp(r['bin_right_bp'])}" for r in rows]
    vals = [float(r["pct_of_population"]) for r in rows]
    n = int(rows[0]["n_in_population"])
    ax.bar(range(len(vals)), vals, color=colour, width=0.78)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, rotation=55, ha="right", fontsize=7.2)
    ax.set_ylabel("% of placements", fontsize=9)
    ax.set_xlabel("signed RT↔ncRNA spacing (bp); negative = ncRNA upstream", fontsize=8.5,
                  labelpad=8)
    ax.set_title(f"{pop} placements  (n = {n:,d})", fontsize=10.5)
    ax.tick_params(axis="y", labelsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    zero_at = next(i for i, r in enumerate(rows) if float(r["bin_left_bp"]) >= 0) - 0.5
    ax.axvline(zero_at, color="#555", lw=0.9, ls=":")
    top = max(vals)
    ax.set_ylim(0, top * 1.24)
    ax.annotate("upstream", xy=(zero_at - 0.4, top * 1.16), fontsize=7.5, color="#555", ha="right")
    ax.annotate("downstream", xy=(zero_at + 0.4, top * 1.16), fontsize=7.5, color="#555", ha="left")
    for i, v in enumerate(vals):
        if v >= 10:
            ax.text(i, v + top * 0.025, f"{v:.1f}%", ha="center", fontsize=6.5, color="#333")
    return n


def restyle_geometry(results: Path, W: Path) -> None:
    rows = rd(results / SRC_GEOM)
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.4))
    ns = {}
    for ax, pop, col in ((axes[0], "CANONICAL", BLUE), (axes[1], "ATYPICAL", ORANGE)):
        sub = [r for r in rows if r["population"] == pop]
        if not sub:
            raise SystemExit(f"FATAL: no {pop} rows in {SRC_GEOM}")
        ns[pop] = geom_panel(ax, sub, pop, col)
    fig.suptitle("RT↔ncRNA signed spacing, canonical vs atypical placements", fontsize=12,
                 y=0.99)
    fig.text(0.008, 0.008,
             "unit: placements   denominator: placements of that population with a defined signed "
             f"distance (CANONICAL n = {ns['CANONICAL']:,d}; ATYPICAL n = {ns['ATYPICAL']:,d})   "
             f"source: {SRC_GEOM}", fontsize=7.2, color="#555")
    fig.tight_layout(rect=(0, 0.045, 1, 0.965))
    emit(fig, rows, "fig01_distance_distribution_restyled", W)


# ----------------------------------------------------------------------------- lengths
def restyle_rt_length(results: Path, W: Path) -> None:
    rows = rd(results / SRC_LEN)
    fig, ax = plt.subplots(figsize=(9.6, 0.34 * len(rows) + 1.5))
    for i, r in enumerate(rows):
        q1, q3, med = float(r["q25"]), float(r["q75"]), float(r["median"])
        ax.plot([q1, q3], [i, i], color=BLUE, lw=6, solid_capstyle="butt", alpha=.78)
        ax.plot([med], [i], "|", color=DARK, markersize=13, markeredgewidth=2)
        ax.text(q3 + 20, i, f"n={int(r['n_exact_rt']):,d}   med={med:.0f} aa", va="center",
                fontsize=7.2, color="#444")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r["family_label"] for r in rows], fontsize=8.2)
    ax.invert_yaxis()
    ax.set_ylim(len(rows) - 0.4, -0.6)
    ax.set_xlabel("RT protein length (aa) — bar spans the interquartile range, "
                  "tick is the median", fontsize=9)
    ax.set_xlim(0, max(float(r["q75"]) for r in rows) * 1.48)
    ax.tick_params(axis="x", labelsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color="#e8eef3", lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("RT length by family label, one observation per exact RT protein", fontsize=11)
    tot = sum(int(r["n_exact_rt"]) for r in rows)
    fig.text(0.008, 0.006,
             "unit: exact RT sequences   denominator: V-RT-SINGLE exact RTs of that family "
             f"(top {len(rows)} by n) (n = {tot:,d})   source: {SRC_LEN}",
             fontsize=7.2, color="#555")
    fig.tight_layout(rect=(0, 0.028, 1, 1))
    emit(fig, rows, "fig01_rt_length_by_family_restyled", W)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", required=True, help="directory holding the landed bundles")
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    results, W = Path(a.results), Path(a.work)
    (W / "figures").mkdir(parents=True, exist_ok=True)
    (W / "tables").mkdir(parents=True, exist_ok=True)
    restyle_geometry(results, W)
    restyle_rt_length(results, W)
    return 0


if __name__ == "__main__":
    sys.exit(main())
