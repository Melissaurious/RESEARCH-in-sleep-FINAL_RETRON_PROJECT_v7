#!/usr/bin/env python3
"""s06 - the g6 figure: the reproducibility statistic against BOTH nulls, plus the family
state-occupancy profiles that produced it.

Every state is a bare `state_id`. No historical RT0-RT7 label appears anywhere.
"""
import os
import sys

os.environ.setdefault("MPLCONFIGDIR", os.environ.get("TMPDIR", "/tmp"))
import matplotlib                                                        # noqa: E402
matplotlib.use("Agg")
import matplotlib.patches as mpatches                                    # noqa: E402
import matplotlib.pyplot as plt                                          # noqa: E402
import numpy as np                                                       # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g6lib import FIGURES, TABLES, WORK, read_tsv, write_tsv             # noqa: E402

C_OBS = "#2c6fbb"
C_N1 = "#b23b3b"
C_N2 = "#d98c00"


def main():
    rho = read_tsv(os.path.join(TABLES, "g6_between_family_rho.tsv"))
    wr = read_tsv(os.path.join(TABLES, "g6_within_retron_rho.tsv"))
    prof = read_tsv(os.path.join(TABLES, "g6_family_state_profiles.tsv"))
    state_ids = np.load(os.path.join(WORK, "state_ids.npy"))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9.4),
                                   gridspec_kw={"height_ratios": [1.05, 1]})
    fig.suptitle("g6 — is organization in the frozen conserved-state space reproducible?",
                 fontsize=13, fontweight="bold", y=0.985)

    # ---- panel a: rho vs both nulls --------------------------------------------------
    rows = [r for r in rho if r["rho"] not in ("", "NA")] + \
           [r for r in wr if r["rho"] not in ("", "NA")]
    y = np.arange(len(rows))[::-1]
    for yy, r in zip(y, rows):
        obs = float(r["rho"])
        n2 = float(r["null2_p99"]) if r.get("null2_p99") else None
        n1 = float(r["null1_p99"]) if r.get("null1_p99") else None
        ax1.plot([0, 1], [yy, yy], color="#eee", lw=0.8, zorder=0)
        if n1 is not None:
            ax1.plot([n1], [yy], marker="|", ms=13, mew=2.2, color=C_N1, zorder=3)
        if n2 is not None:
            ax1.plot([n2], [yy], marker="|", ms=13, mew=2.2, color=C_N2, zorder=3)
        ax1.plot([obs], [yy], marker="o", ms=7, color=C_OBS, zorder=4)
        ax1.text(1.015, yy, f"{r['analysis_id']}  (n={r['n_groups']} groups)",
                 va="center", fontsize=7.6)
    ax1.set_yticks([])
    ax1.set_xlim(0.0, 1.0)
    ax1.set_xlabel("split-half reproducibility  ρ  (Spearman on between-group distance "
                   "matrices)", fontsize=9)
    ax1.set_title("observed ρ against the 99th percentile of each null — the two nulls "
                  "BRACKET the truth", fontsize=9.5, pad=6)
    ax1.legend(handles=[
        plt.Line2D([], [], marker="o", ls="", color=C_OBS, label="observed ρ"),
        plt.Line2D([], [], marker="|", ls="", mew=2.2, ms=13, color=C_N1,
                   label="NULL-1 p99 — sequence-level (declared; conservative)"),
        plt.Line2D([], [], marker="|", ls="", mew=2.2, ms=13, color=C_N2,
                   label="NULL-2 p99 — cluster-level (repair 1; anti-conservative)")],
        loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, fontsize=7.8,
        frameon=False)
    for s in ("top", "right", "left"):
        ax1.spines[s].set_visible(False)

    # ---- panel b: family state-occupancy profiles ------------------------------------
    prof = sorted(prof, key=lambda r: -float(r["mean_mapped_fraction"]))
    show = prof[:6] + prof[-4:] if len(prof) > 10 else prof
    for r in show:
        p = np.array([float(x) for x in r["profile"].split(";")])
        ax2.plot(state_ids, p, lw=1.2, alpha=.85,
                 label=f"{r['family']}  (n={r['n_inspectable']}, mean {r['mean_mapped_fraction']})")
    ax2.set_xlabel("frozen conserved state_id  (150 anchors; GII.deriv.hmm LENG 471, "
                   "hhmake -M 50)", fontsize=9)
    ax2.set_ylabel("MAPPED fraction", fontsize=9)
    ax2.set_ylim(0, 1.02)
    ax2.set_title("per-family state-occupancy profiles — each on its OWN inspectable "
                  "denominator.\nMAPPED only; the other three call states are reported "
                  "separately and never collapsed into 'absent'",
                  fontsize=8.5, pad=6, loc="left")
    ax2.legend(fontsize=6.8, ncol=1, frameon=False, loc="center left",
               bbox_to_anchor=(1.005, 0.5))
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)

    fig.tight_layout(rect=(0.01, 0.01, 0.80, 0.955), h_pad=4.5)
    os.makedirs(FIGURES, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(FIGURES, f"g6_reproducibility.{ext}"), dpi=200)
    plt.close(fig)

    write_tsv(os.path.join(TABLES, "g6_reproducibility.tsv"),
              ["analysis_id", "arm", "rho", "null1_p99", "null2_p99", "n_groups"],
              [dict(analysis_id=r["analysis_id"], arm=r["arm"], rho=r["rho"],
                    null1_p99=r.get("null1_p99", ""), null2_p99=r.get("null2_p99", ""),
                    n_groups=r["n_groups"]) for r in rows])
    print(f"s06: figure written, {len(rows)} analyses plotted against both nulls")


if __name__ == "__main__":
    main()
