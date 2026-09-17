#!/usr/bin/env python3
"""s06 - the RT0-RT7 bridge figure. Only supported regions are drawn; nothing is interpolated.

Two panels, one shared story:

  (a) LtrA P0A3U0 residue axis - the common currency of every historical coordinate. Shows the
      frozen instrument's anchor coverage, the six g2 reconstructed blocks, and the
      source-stated Blocker landmarks.
  (b) The frozen state axis - the operational coordinate system. A historical label appears
      ONLY where the crosswalk supports it. Unsupported labels are drawn as an explicit
      "no frozen-state support" marker in the region where the literature places them, never
      as an interpolated bar.

Writes PNG and SVG plus the figure's data TSV (REPORTING_STANDARDS).
"""
import os
import sys

os.environ.setdefault("MPLCONFIGDIR", os.environ.get("TMPDIR", "/tmp"))
import matplotlib                                                        # noqa: E402
matplotlib.use("Agg")
import matplotlib.patches as mpatches                                    # noqa: E402
import matplotlib.pyplot as plt                                          # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g7alib import FIGURES, TABLES, read_tsv, write_tsv                  # noqa: E402

C_SUP = "#2c6fbb"      # supported
C_MANY = "#7a4fa3"     # many-to-one
C_PART = "#d98c00"     # partial
C_NONE = "#b23b3b"     # no support / unresolved
C_BLOCK = "#c8d3de"
C_ANCHOR = "#8fbf73"


def colour(corr):
    return {"SUPPORTED_1_TO_1": C_SUP, "SUPPORTED_1_TO_MANY": C_SUP,
            "SUPPORTED_MANY_TO_1": C_MANY, "PARTIAL": C_PART}.get(corr, C_NONE)


def main():
    cross = read_tsv(os.path.join(TABLES, "g7a_crosswalk_resolved.tsv"))
    coords = read_tsv(os.path.join(TABLES, "g7a_coordinate_carriage.tsv"))
    bridge = read_tsv(os.path.join(TABLES, "g7a_state_to_residue.tsv"))
    mapped = [(int(r["state_id"]), int(r["ltra_residue"])) for r in bridge
              if r["call_state"] == "MAPPED"]
    res_lo, res_hi = min(r for _, r in mapped), max(r for _, r in mapped)
    st_lo, st_hi = min(s for s, _ in mapped), max(s for s, _ in mapped)

    blocks = [(int(c["coordinate_id"].split("-")[1]), int(c["ltra_start"]), int(c["ltra_end"]))
              for c in coords if c["route"] == "P"]
    cpts = {c["historical_label"]: int(c["ltra_start"]) for c in coords if c["route"] == "C"}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 7.8),
                                   gridspec_kw={"height_ratios": [1, 1.35]})
    fig.suptitle("RT0–RT7 historical bridge: what the frozen conserved-state system can and "
                 "cannot support", fontsize=13, fontweight="bold", y=0.985)

    # ---------------- panel (a): LtrA residue axis --------------------------------------
    ax1.set_xlim(0, 600)
    ax1.set_ylim(0, 4.95)
    ax1.add_patch(mpatches.Rectangle((1, 3.25), 599, 0.45, fc="#f0f0f0", ec="#999"))
    ax1.text(4, 3.9, "LtrA P0A3U0 (AAB06503), 599 aa", fontsize=9, fontweight="bold")

    ax1.add_patch(mpatches.Rectangle((res_lo, 2.35), res_hi - res_lo, 0.45,
                                     fc=C_ANCHOR, ec="#4a7a36", alpha=.85))
    ax1.text(res_lo + 3, 2.98, f"frozen anchor coverage: {len(mapped)}/150 anchors MAPPED, "
                               f"LtrA {res_lo}–{res_hi}  (states {st_lo}–{st_hi})",
             fontsize=8.5, color="#2f5224")
    ax1.annotate("", xy=(res_lo, 2.3), xytext=(1, 2.3),
                 arrowprops=dict(arrowstyle="-", color=C_NONE, lw=1.4, ls=(0, (3, 2))))
    ax1.text(4, 2.03, f"LtrA 1–{res_lo - 1}: NO anchor coverage", fontsize=8, color=C_NONE)

    for i, lo, hi in blocks:
        ax1.add_patch(mpatches.Rectangle((lo, 1.42), max(hi - lo, 2), 0.42,
                                         fc=C_BLOCK, ec="#6b7b8c"))
        ax1.text((lo + hi) / 2, 1.63, str(i), ha="center", va="center", fontsize=7.5)
    ax1.text(4, 1.05, "g2 reconstructed blocks (Route P) — SIX, not seven", fontsize=8.5)

    for lab, pt in cpts.items():
        ax1.plot([pt], [0.72], marker="v", ms=5, color="#444")
        ax1.text(pt, 0.42, lab, ha="center", fontsize=7)
    ax1.text(4, 0.08, "Route C comparator point landmarks (may corroborate, never resolve)",
             fontsize=8.5, color="#444")

    for x, lbl, col, yy in ((39, "A39 · RT0 interior", "#b23b3b", 4.70),
                            (85, "R85 · cleavage IN RT1", "#b23b3b", 4.40),
                            (364, "R364/365 · RT7|domain X", "#1a7a4c", 4.70)):
        ax1.axvline(x, ymin=0.02, ymax=yy / 4.95 - 0.06, color=col, lw=1.1, ls=":")
        ax1.text(x + 5, yy, lbl, fontsize=7.2, color=col, va="top", ha="left")
    ax1.set_yticks([])
    ax1.set_xlabel("LtrA residue", fontsize=9)
    for s in ("top", "right", "left"):
        ax1.spines[s].set_visible(False)

    # ---------------- panel (b): frozen state axis --------------------------------------
    order = [r for r in cross]
    ax2.set_xlim(st_lo - 30, st_hi + 14)
    ax2.set_ylim(-0.75, len(order) - 0.25)
    data = []
    for y, r in enumerate(reversed(order)):
        lab, corr = r["historical_label"], r["correspondence"]
        col = colour(corr)
        if r["state_span"]:
            a, b = (int(x) for x in r["state_span"].split("-"))
            ax2.add_patch(mpatches.Rectangle((a, y - 0.3), max(b - a, 1), 0.6, fc=col,
                                             ec="#333", alpha=.9))
            ax2.text(b + 3, y, f"{corr}  ·  {r['n_supporting_states']} states  ·  "
                               f"LtrA {r['ltra_residue_span_supported']}",
                     va="center", fontsize=7.6)
            data.append(dict(historical_label=lab, correspondence=corr, state_start=a,
                             state_end=b, n_supporting_states=r["n_supporting_states"],
                             ltra_span=r["ltra_residue_span_supported"], drawn="YES"))
        else:
            ax2.add_patch(mpatches.Rectangle((st_lo - 28, y - 0.3), 26, 0.6, fc="none",
                                             ec=C_NONE, lw=1.2, ls=(0, (2, 2)), hatch="///"))
            ax2.text(st_lo - 1, y, f"{corr} — no frozen anchor state lies in the region the "
                                   f"literature places this label (LtrA "
                                   f"{r['reference_interval_ltra']})",
                     va="center", fontsize=7.6, color=C_NONE)
            data.append(dict(historical_label=lab, correspondence=corr, state_start="",
                             state_end="", n_supporting_states=0,
                             ltra_span="", drawn="NO - not interpolated"))
        ax2.text(st_lo - 34, y, lab, va="center", ha="right", fontsize=9.5, fontweight="bold")
    ax2.set_yticks([])
    ax2.set_xlabel("frozen conserved state_id  (GII.deriv.hmm, LENG 471, hhmake -M 50 — "
                   "150 anchors span 107–317)", fontsize=9)
    for s in ("top", "right", "left"):
        ax2.spines[s].set_visible(False)
    fig.legend(handles=[mpatches.Patch(fc=C_SUP, ec="#333", label="SUPPORTED_1_TO_1"),
                        mpatches.Patch(fc=C_MANY, ec="#333", label="SUPPORTED_MANY_TO_1"),
                        mpatches.Patch(fc=C_PART, ec="#333", label="PARTIAL"),
                        mpatches.Patch(fc="none", ec=C_NONE, hatch="///",
                                       label="NO_SUPPORTED_CROSSWALK — drawn, never interpolated")],
               loc="lower center", fontsize=8, frameon=False, ncol=4,
               bbox_to_anchor=(0.5, -0.004))

    fig.tight_layout(rect=(0, 0.052, 1, 0.965))
    os.makedirs(FIGURES, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(FIGURES, f"g7a_bridge.{ext}"), dpi=200)
    plt.close(fig)

    write_tsv(os.path.join(TABLES, "g7a_bridge.tsv"),
              ["historical_label", "correspondence", "state_start", "state_end",
               "n_supporting_states", "ltra_span", "drawn"], data)
    print(f"s06: figure written; {sum(1 for d in data if d['drawn'] == 'YES')} of {len(data)} "
          f"labels drawn on the state axis, {sum(1 for d in data if d['drawn'] != 'YES')} "
          f"marked unsupported rather than interpolated")


if __name__ == "__main__":
    main()
