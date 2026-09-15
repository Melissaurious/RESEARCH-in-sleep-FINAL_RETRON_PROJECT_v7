#!/usr/bin/env python3
"""fig01 - the two geometry figures. Reads tables/ and NOTHING else.

A figure script that can reach the source data can disagree with the table beside it; this one
cannot. Every panel stamps the unit and the denominator it was drawn on, and each figure ships
the TSV it plots (BS-13).
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLUE, GREY, ORANGE = "#2f6f9f", "#9aa5ad", "#d1834a"


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh, delimiter="\t")]


def stamp(ax, unit: str, denom: str, n: int) -> None:
    ax.text(0.0, -0.22, f"unit: {unit}   denominator: {denom} (n = {n:,d})",
            transform=ax.transAxes, fontsize=7.5, color="#444", va="top")


def save(fig, out: Path, name: str, rows: list[dict], tables: Path) -> None:
    """PNG + SVG + the numbers the figure plots, under the figure's own basename (BS-13)."""
    for ext in ("png", "svg"):
        fig.savefig(out / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    with (tables / f"{name}.tsv").open("w") as fh:
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

    # ---- figure 1: bp spacing, canonical vs atypical ---------------------------------
    h = [r for r in rd(T / "g3_distance_histogram.tsv")
         if r["bin_left_bp"] not in ("below",) and r["bin_right_bp"] not in ("above",)]
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6), sharey=False)
    for ax, pop, col in ((axes[0], "CANONICAL", BLUE), (axes[1], "ATYPICAL", ORANGE)):
        rows = [r for r in h if r["population"] == pop]
        labels = [f"{r['bin_left_bp']}..{r['bin_right_bp']}" for r in rows]
        vals = [float(r["pct_of_population"]) for r in rows]
        n = int(rows[0]["n_in_population"]) if rows else 0
        ax.bar(range(len(vals)), vals, color=col)
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(labels, rotation=90, fontsize=6)
        ax.set_ylabel("% of placements")
        ax.set_title(f"RT↔ncRNA signed spacing — {pop}", fontsize=10)
        ax.axvline(len(vals) / 2 - 0.5, color="#333", lw=0.8, ls=":")
        ax.text(len(vals) / 2 - 0.6, max(vals) * 0.9, "upstream ← | → downstream",
                fontsize=7, ha="right", color="#333")
        stamp(ax, "placements", f"{pop} placements with a defined signed distance", n)
    save(fig, F, "fig01_distance_distribution",
         [dict(population=r["population"], bin_left_bp=r["bin_left_bp"], bin_right_bp=r["bin_right_bp"],
               n_placements=r["n_placements"], n_in_population=r["n_in_population"],
               pct_of_population=r["pct_of_population"])
          for r in h if r["population"] in ("CANONICAL", "ATYPICAL")], T)

    # ---- figure 2: intervening CDS, explicit 0/1/2/3/>3 ------------------------------
    c = rd(T / "g3_cds_between_explicit.tsv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    cats = ["0", "1", "2", "3", ">3"]
    for ax, pop, col in ((axes[0], "CANONICAL", BLUE), (axes[1], "ATYPICAL", ORANGE)):
        rows = {r["n_cds_between"]: r for r in c if r["population"] == pop and not r["stratum"]}
        vals = [float(rows[k]["pct_of_population"]) for k in cats]
        ns = [int(rows[k]["n_placements"]) for k in cats]
        n = int(rows["0"]["n_in_population"])
        b = ax.bar(cats, vals, color=col)
        for rect, nv in zip(b, ns):
            ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height(), f"{nv:,d}",
                    ha="center", va="bottom", fontsize=7)
        ax.set_xlabel("complete CDS between the RT and the ncRNA")
        ax.set_ylabel("% of placements")
        ax.set_title(f"Intervening CDS — {pop}", fontsize=10)
        stamp(ax, "placements", f"{pop} placements", n)
    save(fig, F, "fig02_cds_between",
         [dict(population=r["population"], n_cds_between=r["n_cds_between"],
               n_placements=r["n_placements"], n_in_population=r["n_in_population"],
               pct_of_population=r["pct_of_population"])
          for r in c if r["population"] in ("CANONICAL", "ATYPICAL") and not r["stratum"]], T)

    # ---- figure 3: direction by RT family, canonical ----------------------------------
    g = [r for r in rd(T / "g3_geometry_by_family.tsv") if int(r["n_placements"]) >= 30]
    g.sort(key=lambda r: -int(r["n_placements"]))
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(g) + 1.6))
    names = [r["file_label"] for r in g]
    up = [float(r["pct_upstream"]) for r in g]
    ov = [float(r["pct_overlapping"]) for r in g]
    dn = [float(r["pct_downstream"]) for r in g]
    ax.barh(names, up, color=BLUE, label="upstream")
    ax.barh(names, ov, left=up, color=GREY, label="overlapping")
    ax.barh(names, dn, left=[u + o for u, o in zip(up, ov)], color=ORANGE, label="downstream")
    for i, r in enumerate(g):
        ax.text(101, i, f"n={int(r['n_placements']):,d}", va="center", fontsize=7, color="#444")
    ax.set_xlim(0, 118)
    ax.set_xlabel("% of CANONICAL placements")
    ax.set_title("RT↔ncRNA direction by RT family label (CANONICAL placements, families with n ≥ 30)",
                 fontsize=10)
    ax.legend(fontsize=7, loc="lower right")
    ax.invert_yaxis()
    stamp(ax, "placements", "CANONICAL placements of that family label",
          sum(int(r["n_placements"]) for r in g))
    save(fig, F, "fig03_direction_by_family",
         [dict(file_label=r["file_label"], n_placements=r["n_placements"],
               pct_upstream=r["pct_upstream"], pct_overlapping=r["pct_overlapping"],
               pct_downstream=r["pct_downstream"]) for r in g], T)
    return 0


if __name__ == "__main__":
    sys.exit(main())
