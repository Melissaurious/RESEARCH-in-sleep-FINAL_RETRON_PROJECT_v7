#!/usr/bin/env python3
"""fig01 - the two g4 figures. Reads tables/ and nothing else; ships the TSV it plots."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLUE, ORANGE, GREY = "#2f6f9f", "#d1834a", "#9aa5ad"


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def stamp(ax, unit, denom, n):
    ax.text(0.0, -0.30, f"unit: {unit}   denominator: {denom} (n = {n:,d})",
            transform=ax.transAxes, fontsize=7.5, color="#444", va="top")


def save(fig, F, T, name, rows):
    for ext in ("png", "svg"):
        fig.savefig(F / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    with (T / f"{name}.tsv").open("w") as fh:
        fh.write("\t".join(rows[0]) + "\n")
        for r in rows:
            fh.write("\t".join(str(v) for v in r.values()) + "\n")
    print(f"  {name}.png / .svg / .tsv")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    T, F = W / "tables", W / "figures"
    F.mkdir(parents=True, exist_ok=True)

    # ---- figure 1: RT length per family, median with the IQR box --------------------
    g = [r for r in rd(T / "g4_rt_length_by_family.tsv") if int(r["n_exact_rt"]) >= 30]
    g.sort(key=lambda r: -int(r["n_exact_rt"]))
    g = g[:25]
    fig, ax = plt.subplots(figsize=(9, 0.38 * len(g) + 1.8))
    for i, r in enumerate(g):
        q1, q3, med = float(r["q25"]), float(r["q75"]), float(r["median"])
        ax.plot([q1, q3], [i, i], color=BLUE, lw=6, solid_capstyle="butt", alpha=.75)
        ax.plot([med], [i], "|", color="#13324b", markersize=14, markeredgewidth=2)
        ax.text(q3 + 20, i, f"n={int(r['n_exact_rt']):,d}  med={med:.0f}", va="center",
                fontsize=7, color="#444")
    ax.set_yticks(range(len(g)))
    ax.set_yticklabels([r["family_label"] for r in g], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("RT protein length (aa) — bar spans the interquartile range, tick is the median")
    ax.set_xlim(0, max(float(r["q75"]) for r in g) * 1.45)
    ax.set_title("RT length by family label, one observation per exact RT protein", fontsize=10)
    stamp(ax, "exact RT sequences", "V-RT-SINGLE exact RTs of that family (top 25 by n)",
          sum(int(r["n_exact_rt"]) for r in g))
    save(fig, F, T, "fig01_rt_length_by_family",
         [dict(family_label=r["family_label"], n_exact_rt=r["n_exact_rt"], q25=r["q25"],
               median=r["median"], q75=r["q75"], min=r["min"], max=r["max"]) for r in g])

    # ---- figure 2: the MULTI label basis, against its control ------------------------
    m = rd(T / "g4_multi_hmm_margin_comparison.tsv")
    fig, ax = plt.subplots(figsize=(7.0, 2.1))
    names = [r["population"] for r in m]
    med = [float(r["median_margin_bits"]) for r in m]
    q1 = [float(r["q25_margin_bits"]) for r in m]
    q3 = [float(r["q75_margin_bits"]) for r in m]
    for i, (lo, hi, md, col) in enumerate(zip(q1, q3, med, (ORANGE, BLUE))):
        ax.plot([lo, hi], [i, i], color=col, lw=8, solid_capstyle="butt", alpha=.8)
        ax.plot([md], [i], "|", color="#13324b", markersize=16, markeredgewidth=2)
        ax.text(hi + 3, i, f"median {md:.1f} bits", va="center", fontsize=8, color="#444")
    ax.margins(y=0.35)
    ax.set_yticks(range(len(m)))
    ax.set_yticklabels(names, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("bit-score margin between the best and second-best RT family profile")
    ax.set_title("Why MULTI records carry several labels: the profiles tie", fontsize=10)
    ax.set_xlim(0, max(q3) * 1.35)
    stamp(ax, "exact RT sequences", "the population named on the axis",
          sum(int(r["n_exact_rt"]) for r in m))
    save(fig, F, T, "fig02_multi_label_margins",
         [dict(population=r["population"], n_exact_rt=r["n_exact_rt"],
               median_margin_bits=r["median_margin_bits"], q25=r["q25_margin_bits"],
               q75=r["q75_margin_bits"],
               pct_below_10_bits=r["pct_margin_below_10_bits"]) for r in m])
    return 0


if __name__ == "__main__":
    sys.exit(main())
