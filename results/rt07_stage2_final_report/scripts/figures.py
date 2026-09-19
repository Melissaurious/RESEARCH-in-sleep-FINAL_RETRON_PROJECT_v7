#!/usr/bin/env python3
"""figures - re-plot the Stage-2 thesis figures from landed tables, with the reviewed wording.

Computes no science. Each figure reads only landed tables (paths in findings.py) or the
transcribed, build-verified review ledger, and writes the exact numbers it plots to
tables/<figure>.tsv. The frozen figures in the g6 and g7a bundles are NOT touched; they carry
wording superseded by the 2026-09-19 errata, which is why the thesis versions are re-drawn here.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
matplotlib.rcParams["svg.hashsalt"] = "rt07_stage2_final_report"
matplotlib.rcParams["font.size"] = 9
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import findings as F  # noqa: E402
import ledger as L  # noqa: E402

INK, MUTED, ACC = "#1b2733", "#6b7b8a", "#2f6f9f"
COL = {"ESTABLISHED": "#2f7d4f", "PARTIAL": "#d08a1c", "UNRESOLVED": "#9aa5b1"}
LAYER = {"L1": "#e8eef4", "L2": "#eef4e8", "L3": "#f4efe6", "L4": "#f1e8f4", "L5": "#e6f1f4"}


def rows(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader((ln for ln in fh if not ln.startswith("#")), delimiter="\t"))


def write_tsv(p: Path, rs: list[dict]) -> None:
    cols = list(rs[0])
    with p.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rs:
            fh.write("\t".join(str(r[c]) for c in cols) + "\n")


def save(fig, out: Path, stem: str, plotted: list[dict]) -> None:
    fig.savefig(out / "figures" / f"{stem}.png", dpi=200, metadata={"Software": None})
    fig.savefig(out / "figures" / f"{stem}.svg", metadata={"Date": None})
    plt.close(fig)
    write_tsv(out / "tables" / f"{stem}.tsv", plotted)


def caption(fig, text: str) -> None:
    fig.text(0.01, 0.005, text, ha="left", va="bottom", fontsize=7, color=MUTED, wrap=True)


# ---------------------------------------------------------------------------------------------
def f1(root: Path, out: Path) -> None:
    rs = L.REVIEWS
    fig, ax = plt.subplots(figsize=(10, 4.8))
    plotted = []
    for seq, layer, obj, verdict, score, _, rec, _ in rs:
        ax.axvspan(seq - 0.5, seq + 0.5, color=LAYER[layer], zorder=0)
        if score:
            s = int(score)
            c = "#2f7d4f" if verdict.startswith("PASS") else ("#b3472f" if ("FAIL" in verdict or "not ready" in verdict) else ACC)
            ax.bar(seq, s, color=c, width=0.62, zorder=2)
            ax.text(seq, s + 0.15, score, ha="center", fontsize=7)
        else:
            ax.text(seq, 0.3, "not\ncompleted", ha="center", fontsize=6, color=MUTED)
        plotted.append(dict(seq=seq, layer=layer, object=obj, verdict=verdict,
                            score_of_10=score or "n/a - not completed", record=rec))
    ax.axhline(6, ls="--", lw=0.8, color=INK)
    ax.set_xticks([r[0] for r in rs])
    ax.set_xticklabels([r[2].replace("FINAL_PRE_UG25_VALIDATION_BUNDLE", "pre-UG25 bundle")
                        for r in rs], rotation=55, ha="right", fontsize=6.5)
    ax.set_ylim(0, 10.5)
    ax.set_xlim(0.5, len(rs) + 0.5)
    ax.set_ylabel("independent review score (/10)")
    ax.set_title("Stage 2 as shaped by independent review", loc="left", fontsize=10)
    ax.legend(handles=[Patch(color="#2f7d4f", label="PASS_WITH_REQUIRED_REPAIRS"),
                       Patch(color="#b3472f", label="FAIL/BLOCK or not ready"),
                       Patch(color=ACC, label="class B (repairs, no formal pass)")]
              + [plt.Line2D([], [], ls="--", color=INK, lw=0.8, label="transition threshold (score >= 6)")]
              + [Patch(fc=LAYER[k], ec=MUTED, lw=0.4, label=k) for k in ("L2", "L3", "L4", "L5")],
              fontsize=6.5, ncol=4, loc="upper left", frameon=False)
    fig.subplots_adjust(bottom=0.40, left=0.07, right=0.99, top=0.92)
    caption(fig, "Scores transcribed from docs/decisions/ (and the g5 commit message); each verified verbatim at "
                 "build time. Row 11's formal field is recorded as written, not reconciled. L2 operational mapping; "
                 "L3 family-level description; L4 historical bridge; L5 final reviewed interpretation.")
    save(fig, out, "F1_review_trajectory", plotted)


def f2(root: Path, out: Path) -> None:
    cv = [r for r in rows(root / F.CV) if r["family"] != "TOTAL"]
    comp = rows(root / F.UGK)
    ctl = [r for r in rows(root / F.UGN) if r["control_class"] in ("MONO", "DI", "REV")]
    seqs = rows(root / F.UGS)
    sup = {r["parameter"]: r["value"] for r in rows(root / F.SUP)}
    t1, kmin = float(sup["T1"]), int(sup["K_MIN"])
    weakest = min(int(r["n_mapped"]) for r in seqs)
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.6), gridspec_kw={"width_ratios": [6, 3, 4]})
    plotted = []
    for ax, data, key, title in [(axs[0], cv, "family", "a  construction (calibration) families"),
                                 (axs[1], comp, "component", "b  UG25 holdout components")]:
        for i, r in enumerate(data):
            med = float(r["median_mapped_fraction"])
            lo = float(r.get("min_mapped_fraction") or r.get("min"))
            hi = float(r.get("max_mapped_fraction") or r.get("max"))
            role = r.get("role", "construction")
            c = MUTED if role == "descriptive_only" else ACC
            ax.plot([i, i], [lo, hi], color=c, lw=1.2)
            ax.plot(i, med, "o", color=c)
            lab = r[key] if key == "family" else f"comp {r[key]}\n(n={r['n_sequences']})"
            plotted.append(dict(panel=title[0], item=lab.replace("\n", " "), median=med, low=lo, high=hi,
                                reference=f"T1={t1}", role=role))
        ax.axhline(t1, ls="--", lw=0.8, color="#b3472f")
        ax.text(-0.35, t1 - 0.06, f"T1 = {t1}", fontsize=7, color="#b3472f", ha="left")
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels([(r[key] if key == "family" else f"comp {r[key]}\nn={r['n_sequences']}")
                            for r in data], fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.set_title(title, loc="left", fontsize=8.5)
    axs[0].set_ylabel("per-sequence MAPPED fraction of 150 anchors\n(median, min-max)")
    ax = axs[2]
    names = [r["control_class"] for r in ctl] + ["weakest real\nUG25 seq"]
    vals = [int(r["max_mapped"]) for r in ctl] + [weakest]
    ax.bar(range(len(vals)), vals, color=[MUTED] * len(ctl) + [ACC])
    for i, v in enumerate(vals):
        ax.text(i, v + 1, str(v), ha="center", fontsize=7)
    ax.axhline(kmin, ls="--", lw=0.8, color="#b3472f")
    ax.text(-0.4, kmin + 1.5, f"K_MIN = {kmin}", fontsize=7, color="#b3472f")
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(names, fontsize=7)
    ax.set_ylabel("MAPPED anchors (max per class)")
    ax.set_title("c  synthetic controls vs commitment floor", loc="left", fontsize=8.5)
    for r in ctl:
        plotted.append(dict(panel="c", item=r["control_class"], median="", low="", high=r["max_mapped"],
                            reference=f"K_MIN={kmin}", role=f"n_attempted={r['n_attempted']}"))
    plotted.append(dict(panel="c", item="weakest real UG25 sequence", median="", low="", high=weakest,
                        reference=f"K_MIN={kmin}", role="min n_mapped over ug25_sequence_results.tsv"))
    fig.subplots_adjust(bottom=0.22, left=0.07, right=0.99, top=0.9, wspace=0.3)
    caption(fig, "Construction families calibrate the rule; UG25 is the single confirmatory holdout (components 0 and 1 "
                 "qualify, component 2 is descriptive only). Controls are composition/order shuffles of real RTs, not "
                 "unrelated natural proteins: specificity against natural non-RT proteins is not claimed.")
    save(fig, out, "F2_validation", plotted)


def f3(root: Path, out: Path) -> None:
    rs = rows(root / F.G4A)
    fams = list(dict.fromkeys(r["family"] for r in rs))
    ms = ["50", "60", "a2m"]
    colors = {"50": ACC, "60": "#7fa9c9", "a2m": "#c9a27f"}
    fig, ax = plt.subplots(figsize=(8, 3.4))
    w = 0.27
    plotted = []
    for j, m in enumerate(ms):
        for i, f in enumerate(fams):
            r = next(x for x in rs if x["hhmake_M"] == m and x["family"] == f)
            v = float(r["pct_of_full_consensus"])
            ax.bar(i + (j - 1) * w, v, w, color=colors[m], label=f"-M {m}" if i == 0 else None)
            if r["n_ALL_PARTNERS"] == "0":
                ax.text(i + (j - 1) * w, 0.5, "0", ha="center", fontsize=7, color="#b3472f")
            plotted.append(dict(hhmake_M=m, family=f, n_ALL_PARTNERS=r["n_ALL_PARTNERS"],
                                full_consensus_LENG=r["full_consensus_LENG"], pct_of_full_consensus=v))
    ax.set_xticks(range(len(fams)))
    ax.set_xticklabels(fams)
    ax.set_ylabel("all-partner states\n(% of family full consensus)")
    ax.set_title("The conserved core depends on the match-state convention", loc="left", fontsize=10)
    ax.legend(frameon=False, fontsize=8)
    fig.subplots_adjust(bottom=0.22, left=0.1, right=0.99, top=0.88)
    caption(fig, "Landed g4a sensitivity table. Under -M a2m, DGRs and AbiA keep 0 all-partner states: there is no "
                 "convention-invariant universal core. The instrument is validated under hhmake -M 50 only.")
    save(fig, out, "F3_match_state_sensitivity", plotted)


def f4(root: Path, out: Path) -> None:
    c = {r["quantity"]: r["value"] for r in rows(root / F.G5A)}
    h = {r["quantity"]: r["value"] for r in rows(root / F.G5H)}
    st = {r["inspectability_status"]: int(r["n"]) for r in rows(root / F.G5S)}
    cs = rows(root / "results/rt07_g6_family_architecture/tables/g6_call_state_totals.tsv")
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4), gridspec_kw={"width_ratios": [4, 3, 3]})
    plotted = []
    ax = axs[0]
    steps = [("exact RT catalogue", int(c["n_total_exact_rt"])), ("eligible (g5a)", int(c["G5_ELIGIBLE_N"])),
             ("inspectable (g5)", int(h["n_inspectable"]))]
    ax.barh(range(3)[::-1], [v for _, v in steps], color=[MUTED, ACC, "#2f7d4f"])
    for i, (n, v) in enumerate(steps):
        ax.text(v, 2 - i, f" {v:,d}", va="center", fontsize=7)
        plotted.append(dict(panel="a", category=n, n=v, denominator="exact RT sequences"))
    ax.set_yticks(range(3)[::-1])
    ax.set_yticklabels([n for n, _ in steps], fontsize=7.5)
    ax.set_xlim(0, int(c["n_total_exact_rt"]) * 1.3)
    ax.set_xlabel("exact RT sequences (thousands)")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}k"))
    ax.set_title("a  denominators", loc="left", fontsize=8.5)
    ax.text(0.02, -0.33, f"ineligible {int(c['n_ineligible']):,d}: < {c['MIN_AA']} aa {int(c['n_below_min_length']):,d}; "
                         f"non-standard residue {int(c['n_non_standard_residue']):,d}", transform=ax.transAxes,
            fontsize=6.5, color=MUTED)
    for n, k in (("ineligible: below MIN_AA", "n_below_min_length"), ("ineligible: non-standard residue",
                                                                      "n_non_standard_residue")):
        plotted.append(dict(panel="a", category=n, n=int(c[k]), denominator="exact RT sequences"))
    for ax, data, title, den in [
        (axs[1], [(k, st[k]) for k in ("MAPPABLE", "PARTIAL_MAPPING", "AMBIGUOUS_MAPPING", "NO_SUPPORTED_MAPPING")],
         "b  inspectability (of eligible)", int(c["G5_ELIGIBLE_N"])),
        (axs[2], [(r["call_state"], int(r["n_state_calls"])) for r in cs],
         "c  state calls (eligible x 150)", int(h["n_state_rows"]))]:
        left = 0
        pal = ["#2f7d4f", "#d08a1c", "#7fa9c9", "#9aa5b1"]
        for i, (k, v) in enumerate(data):
            ax.barh(0, v / den, left=left, color=pal[i], label=f"{k} {v / den:.3f}")
            left += v / den
            plotted.append(dict(panel=title[0], category=k, n=v, denominator=f"{den} ({title[3:]})"))
        ax.set_xlim(0, 1)
        ax.set_yticks([])
        ax.set_title(title, loc="left", fontsize=8.5)
        ax.legend(fontsize=6.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=1)
    fig.subplots_adjust(bottom=0.36, left=0.12, right=0.99, top=0.88, wspace=0.3)
    caption(fig, "Abstention, NO_SUPPORTED_MAPPING and DELETED_STATE are instrument outcomes, not biological absence. "
                 "Panel c counts state calls over all eligible sequences (369,381 x 150).")
    save(fig, out, "F4_catalogue_application", plotted)


def f5(root: Path, out: Path) -> None:
    rs = rows(root / F.G6B) + rows(root / F.G6W)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    plotted = []
    for i, r in enumerate(rs):
        y = len(rs) - 1 - i
        rho = float(r["rho"])
        n1 = float(r["null1_p99"]) if r["null1_p99"] else None
        n2 = float(r["null2_p99"]) if r["null2_p99"] else None
        ax.plot(rho, y, "o", color=ACC, zorder=3)
        if n1 is not None:
            ax.plot(n1, y, "|", color="#b3472f", ms=11, mew=2)
        if n2 is not None:
            ax.plot(n2, y, "|", color="#7a5a9a", ms=11, mew=2)
        plotted.append(dict(arm=r["arm"], analysis_id=r["analysis_id"], n_groups=r["n_groups"],
                            rank_corr_ordinal_ties=r["rho"], null1_p99=r["null1_p99"] or "n/a",
                            null2_p99=r["null2_p99"] or "n/a", exceeds_null1=r["exceeds_null1"],
                            exceeds_null2=r["exceeds_null2"]))
    ax.set_yticks(range(len(rs))[::-1])
    ax.set_yticklabels([f"{r['analysis_id']}  (k={r['n_groups']})" for r in rs], fontsize=7)
    ax.axhline(len(rs) - 10.5, color=MUTED, lw=0.6)
    ax.set_xlabel("split-half rank correlation with ordinal tie-breaking")
    ax.set_xlim(0.6, 1.01)
    ax.set_title("Split-half concordance among predominantly MyRT-derived family strata\n"
                 "in a GII-HMM-derived occupancy space", loc="left", fontsize=9.5)
    ax.legend(handles=[plt.Line2D([], [], marker="o", ls="", color=ACC, label="observed"),
                       plt.Line2D([], [], marker="|", ls="", color="#b3472f", ms=10, mew=2,
                                  label="NULL-1 p99 (sequence-level)"),
                       plt.Line2D([], [], marker="|", ls="", color="#7a5a9a", ms=10, mew=2,
                                  label="NULL-2 p99 (cluster-level)")], fontsize=7, frameon=False, loc="upper center",
              bbox_to_anchor=(0.45, -0.1), ncol=3)
    fig.subplots_adjust(bottom=0.27, left=0.3, right=0.98, top=0.88)
    caption(fig, "Upper block: between-family arm (MyRT-derived labels); lower block: within-Retron arms (DefenseFinder, "
                 "PADLOC, label-free), each on its own denominator. The two nulls are sensitivity analyses with opposite "
                 "biases, not bounds. 60 permutations cannot calibrate a 1% tail (floor 1/61); no multiplicity control "
                 "across the 13 analyses. Descriptive concordance, not independent family discovery (E-g6-1..E-g6-8).")
    save(fig, out, "F5_g6_concordance", plotted)


def f6(root: Path, out: Path) -> None:
    s2r = rows(root / "results/rt07_g7a_rt0_rt7_bridge/tables/g7a_state_to_residue.tsv")
    xw = {r["historical_label"]: r for r in rows(root / F.G7X)}
    err = {r["historical_label"]: r for r in rows(root / F.ERR)}
    g2f = {r["frame1_block"]: r for r in rows(root / F.G2F)}
    cat = {r["parameter"]: r["value"] for r in rows(root / F.CAT)}
    mapped = [int(r["ltra_residue"]) for r in s2r if r["call_state"] == "MAPPED" and r["ltra_residue"]]
    lo, hi = min(mapped), max(mapped)
    labels = ["RT0", "RT1", "RT2", "RT3", "RT4", "RT5+RT6", "RT7"]
    fig, ax = plt.subplots(figsize=(11, 4.8))
    plotted = []
    ax.axvspan(lo, hi, color="#eef3f7", zorder=0)
    ax.text((lo + hi) / 2, len(labels) + 0.35, f"frozen anchor reach on LtrA: {lo}-{hi}", ha="center",
            fontsize=7.5, color=ACC)
    for x in mapped:
        ax.plot([x, x], [len(labels) - 0.1, len(labels) + 0.1], color=ACC, lw=0.5)

    def span(s):
        a, b = s.split("-")
        return int(a), int(b)
    for i, lab in enumerate(labels):
        y = len(labels) - 1 - i
        key = "RT5" if lab == "RT5+RT6" else lab
        x, e = xw[key], err[key]
        short = e["terminal_status"].split()[0]
        if lab == "RT5+RT6":
            status = "RT5 ESTABLISHED + RT6 PARTIAL (joint only)"
            color = COL["ESTABLISHED"]
        else:
            status = e["terminal_status"]
            color = COL[short]
        a, b = span(x["reference_interval_ltra"])
        ax.add_patch(Rectangle((a, y - 0.3), b - a + 1, 0.6, fill=False, ec=INK, lw=0.9, ls=":"))
        sup = x["ltra_residue_span_supported"]
        if sup:
            sa, sb = span(sup)
            hatch = "////" if lab == "RT4" else None
            ax.add_patch(Rectangle((sa, y - 0.3), sb - sa + 1, 0.6, color=color, alpha=0.85, hatch=hatch,
                                   ec="white" if hatch else None))
        ax.text(392, y, status, va="center", fontsize=7, color=color if short != "UNRESOLVED" else INK)
        plotted.append(dict(label=lab, reference_interval_ltra=x["reference_interval_ltra"],
                            supported_ltra=sup or "none", n_supporting_states=x["n_supporting_states"],
                            final_status=status, drawn_as=("hatched: frame-unstable" if lab == "RT4" else
                                                           "joint box" if lab == "RT5+RT6" else
                                                           "outline only: unresolved" if not sup else "filled")))
    # RT4 independent-frame span, E-g7a-3
    f2a, f2b = span(g2f["4"]["frame2_ltra_span"])
    y4 = len(labels) - 1 - labels.index("RT4")
    ax.plot([f2a, f2b], [y4 - 0.42, y4 - 0.42], color=INK, lw=2)
    ax.text(f2a - 3, y4 - 0.42, f"independent frame: SPLIT_INTO_3, best match {f2a}-{f2b} (Jaccard "
            f"{g2f['4']['jaccard_on_ltra_residues']})", fontsize=6.3, va="center", ha="right")
    plotted.append(dict(label="RT4 independent frame", reference_interval_ltra=g2f["4"]["frame1_ltra_span"],
                        supported_ltra=g2f["4"]["frame2_ltra_span"], n_supporting_states="",
                        final_status="SPLIT_INTO_3", drawn_as="bar under RT4"))
    # landmarks: catalytic state -> LtrA 306 (g7a PC-1 / E-g7a advisory), A39 (g3), R85 (RT0 upper bound)
    y5 = len(labels) - 1 - labels.index("RT5+RT6")
    marks = [(306, y5, f"CAT_STATE {cat['CAT_STATE']} -> LtrA 306 (YADD)", "right"),
             (39, len(labels) - 1, "A39 (RT0 interior, Blocker)", "right"),
             (85, len(labels) - 2, "R85 (inside RT1; RT0 upper bound)", "left"),
             (364.5, len(labels) - 1 - labels.index("RT7"), "R364/R365 proteolytic landmark", "right")]
    for xm, ym, t, ha in marks:
        ax.plot(xm, ym + 0.42, "v", color="#b3472f", ms=5)
        ax.text(xm + (-3 if ha == "right" else 3), ym + 0.42, t, fontsize=6.3, ha=ha, va="center",
                color="#b3472f")
        plotted.append(dict(label="landmark", reference_interval_ltra=str(xm), supported_ltra="",
                            n_supporting_states="", final_status=t, drawn_as="marker"))
    ax.set_yticks(range(len(labels))[::-1])
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 520)
    ax.set_ylim(-0.8, len(labels) + 0.7)
    ax.set_xticks(range(0, 401, 50))
    ax.set_xlabel("LtrA residue (P0A3U0); residues 1-400 shown")
    ax.set_title("Final reviewed RT0-RT7 statuses on LtrA (LtrA-local interpretation layer)", loc="left", fontsize=10)
    ax.legend(handles=[Patch(fill=False, ls=":", ec=INK, label="reconstructed interval (g2) / historical bound"),
                       Patch(color=COL["ESTABLISHED"], label="frozen-state support: ESTABLISHED"),
                       Patch(color=COL["PARTIAL"], label="frozen-state support: PARTIAL"),
                       Patch(fc=COL["ESTABLISHED"], hatch="////", ec="white", label="frame-unstable (RT4)")],
              fontsize=6.5, frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.17), ncol=4)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.subplots_adjust(bottom=0.27, left=0.07, right=0.99, top=0.9)
    caption(fig, "RT0 and RT1 are UNRESOLVED: no source-stated boundary in held sources and no frozen anchor N-terminal of "
                 f"LtrA {lo}; this is a limit of sources and instrument, not biological absence. RT5 and RT6 are drawn as one "
                 "joint region; no state is attributed to RT6 alone. Production emits state_id only.")
    save(fig, out, "F6_rt0_rt7_final", plotted)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root, out = Path(a.root).resolve(), Path(a.out)
    for d in ("figures", "tables"):
        (out / d).mkdir(parents=True, exist_ok=True)
    for fn in (f1, f2, f3, f4, f5, f6):
        fn(root, out)
    print("figures: F1-F6 written (png + svg) with their plotted tables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
