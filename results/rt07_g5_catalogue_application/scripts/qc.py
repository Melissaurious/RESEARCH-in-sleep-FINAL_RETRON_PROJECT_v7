#!/usr/bin/env python3
"""g5 steps D and E — application QC (task §11) and the g6-readiness summary (task §14).

    qc.py <dataset_dir> <tables_dir>

DESCRIPTIVE ONLY. Every number here is application QC over a stated denominator.

Explicitly NOT done, per task §8 and §12:
  * no biological conclusion. Not that short sequences are incomplete, not that a family
    lacks architecture, not that failure to map means absence;
  * no accuracy, sensitivity, specificity, precision, recall, F1 or ROC against MyRT,
    PADLOC or DefenseFinder. Tool labels are strata; the allowed form is "among sequences
    labelled F, state S was MAPPED in X% of inspectable sequences", never "state S is X%
    accurate";
  * no family-architecture comparison. That is g6.

Denominators used, named wherever they appear:
  ELIGIBLE    the censused eligible population, 369,381 - the g5 denominator
  PROCESSED   eligible sequences that produced a full scientific row
  INSPECTABLE eligible sequences whose frozen verdict is MAPPED (the mapper committed);
              the complement is frozen abstention, which is NOT failure and NOT absence
  CAT-MAPPED  sequences whose CAT_STATE 262 call is MAPPED - a SEPARATE denominator from
              the 150 anchors, never pooled with them
"""
import collections
import os
import sys

import pandas as pd
import pyarrow.parquet as pq

DATASET, TABLES = sys.argv[1], sys.argv[2]

PCTLS = [("min", 0.0), ("p5", 0.05), ("p25", 0.25), ("median", 0.50), ("p75", 0.75),
         ("p95", 0.95), ("max", 1.0)]
# A family needs this many INSPECTABLE sequences before g6 treats a between-family
# difference as comparable. Declared here as a REPORTING threshold for readiness triage
# only: it selects nothing, filters nothing, and is not a scientific parameter.
G6_MIN_INSPECTABLE = 100


def write_tsv(path, header, rows):
    with open(path, "w") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join("" if x is None else str(x) for x in r) + "\n")
    print(f"  wrote {os.path.basename(path)} ({len(rows)} rows)")


def dist(series):
    v = sorted(float(x) for x in series.dropna())
    out = []
    for _, q in PCTLS:
        if not v:
            out.append("")
        elif q <= 0:
            out.append(f"{v[0]:.4f}")
        elif q >= 1:
            out.append(f"{v[-1]:.4f}")
        else:
            out.append(f"{v[int(q * (len(v) - 1) + 0.5)]:.4f}")
    out.append(f"{sum(v) / len(v):.4f}" if v else "")
    return out


def main():
    # Read the canonical product, not an intermediate: qc.py depends only on files that are
    # in the dataset manifest and hashed there.
    seq = pq.read_table(f"{DATASET}/g5_sequences.parquet", columns=[
        "rt_hash", "sequence_id", "sequence_length", "verdict", "reason",
        "inspectability_status", "n_mapped", "n_ambiguous", "n_unsupported", "n_deleted",
        "mapped_fraction", "domain_bitscore", "cat_state", "cat_call_state",
        "cat_residue_index", "cat_residue", "cat_motif_class", "cat_support",
        "cat_motif_window", "n_dyad_motifs_in_sequence"]).to_pandas()
    cross = pq.read_table(f"{DATASET}/g5_metadata_crosswalk.parquet").to_pandas()
    inel = pq.read_table(f"{DATASET}/g5_ineligible.parquet").to_pandas()
    fails = pq.read_table(f"{DATASET}/g5_run_failures.parquet").to_pandas()

    seq["rt_hash"] = seq.rt_hash.astype(str)
    cross["rt_hash"] = cross.rt_hash.astype(str)
    d = seq.merge(cross, on="rt_hash", how="left", validate="one_to_one")
    n_elig = len(seq)
    n_proc = len(seq)
    n_tool_fail = int((fails["inspectability_status"] == "TOOL_FAILURE").sum()) \
        if len(fails) else 0
    n_input_invalid = int((fails["inspectability_status"] == "INPUT_INVALID").sum()) \
        if len(fails) else 0

    for c in ("n_mapped", "n_ambiguous", "n_unsupported", "n_deleted"):
        d[c] = pd.to_numeric(d[c])
    d["mapped_fraction"] = pd.to_numeric(d.mapped_fraction)
    d["ambiguous_fraction"] = d.n_ambiguous / 150.0
    d["unsupported_fraction"] = d.n_unsupported / 150.0
    d["deleted_fraction"] = d.n_deleted / 150.0
    d["inspectable"] = d.verdict == "MAPPED"

    n_insp = int(d.inspectable.sum())
    cat_mapped = d.cat_call_state == "MAPPED"
    n_cat_mapped = int(cat_mapped.sum())
    n_cat_conf = int((d.cat_motif_class == "CATALYTIC_CONFIRMED").sum())

    # ---- §11 headline ----------------------------------------------------------------
    rows = [
        ["mapper_version", "rtmap-1.0.0/53a1e738a19b3896", "identifier", ""],
        ["G5_ELIGIBLE_N", n_elig, "exact RT sequences", "the frozen census denominator"],
        ["n_processed", n_proc, "exact RT sequences",
         "produced a full scientific row; ELIGIBLE denominator"],
        ["n_tool_failures", n_tool_fail, "exact RT sequences", "ELIGIBLE denominator"],
        ["n_input_invalid_at_run", n_input_invalid, "records",
         "0 expected: ineligible records were censused out before sharding"],
        ["n_ineligible_censused", len(inel), "exact RT sequences",
         "retained in g5_ineligible.parquet, never silently dropped"],
        ["n_inspectable", n_insp, "exact RT sequences",
         f"frozen verdict MAPPED; {n_insp / n_elig:.4f} of ELIGIBLE"],
        ["n_abstained", n_elig - n_insp, "exact RT sequences",
         "frozen abstention - NOT failure, NOT biological absence"],
        ["n_state_rows", n_elig * 150, "state calls",
         "150 frozen conserved states x ELIGIBLE"],
        ["n_cat_state_mapped", n_cat_mapped, "exact RT sequences",
         "CAT_STATE 262 call is MAPPED; SEPARATE denominator from the 150 anchors"],
        ["n_cat_state_confirmed", n_cat_conf, "exact RT sequences",
         "CAT_STATE MAPPED and the residue begins [YF].DD; motif concordance at a state, "
         "NOT independent residue truth"],
        ["cat_confirmed_over_cat_mapped",
         f"{n_cat_conf / n_cat_mapped:.4f}" if n_cat_mapped else "", "fraction",
         "denominator is CAT-MAPPED, never ELIGIBLE"],
    ]
    write_tsv(f"{TABLES}/g5_qc_headline.tsv", ["quantity", "value", "unit", "note"], rows)

    # ---- status and call-state distributions -----------------------------------------
    st = collections.Counter(d.inspectability_status)
    write_tsv(f"{TABLES}/g5_qc_status_counts.tsv",
              ["inspectability_status", "n", "fraction_of_eligible"],
              [[k, st[k], f"{st[k] / n_elig:.4f}"] for k in sorted(st)])
    vr = collections.Counter(zip(d.verdict, d.reason))
    write_tsv(f"{TABLES}/g5_qc_verdict_reason.tsv",
              ["verdict", "reason", "n", "fraction_of_eligible"],
              [[a, b, vr[(a, b)], f"{vr[(a, b)] / n_elig:.4f}"] for a, b in sorted(vr)])

    frac_rows = []
    for label, col, sub in (("MAPPED_fraction_all_eligible", "mapped_fraction", d),
                            ("AMBIGUOUS_fraction_all_eligible", "ambiguous_fraction", d),
                            ("UNSUPPORTED_fraction_all_eligible", "unsupported_fraction", d),
                            ("DELETED_STATE_fraction_all_eligible", "deleted_fraction", d),
                            ("MAPPED_fraction_inspectable", "mapped_fraction",
                             d[d.inspectable]),
                            ("AMBIGUOUS_fraction_inspectable", "ambiguous_fraction",
                             d[d.inspectable]),
                            ("UNSUPPORTED_fraction_inspectable", "unsupported_fraction",
                             d[d.inspectable]),
                            ("DELETED_STATE_fraction_inspectable", "deleted_fraction",
                             d[d.inspectable])):
        frac_rows.append([label, len(sub)] + dist(sub[col]))
    write_tsv(f"{TABLES}/g5_qc_call_fraction_distributions.tsv",
              ["quantity", "n"] + [n for n, _ in PCTLS] + ["mean"], frac_rows)

    cm = collections.Counter(d.cat_call_state)
    write_tsv(f"{TABLES}/g5_qc_catalytic.tsv",
              ["quantity", "n", "denominator", "fraction"],
              [[f"cat_call_state={k}", cm[k], "ELIGIBLE", f"{cm[k] / n_elig:.4f}"]
               for k in sorted(cm)]
              + [[f"cat_motif_class={k}", v, "ELIGIBLE", f"{v / n_elig:.4f}"]
                 for k, v in sorted(collections.Counter(d.cat_motif_class).items())]
              + [["CATALYTIC_CONFIRMED among CAT-MAPPED", n_cat_conf, "CAT-MAPPED",
                  f"{n_cat_conf / n_cat_mapped:.4f}" if n_cat_mapped else ""]])

    # ---- by metadata stratum (descriptive; tool labels are strata, never truth) -------
    def by(col, path, min_n=1):
        rows = []
        for key, sub in d.groupby(col, dropna=False, sort=True):
            if len(sub) < min_n:
                continue
            ins = sub[sub.inspectable]
            cmap = sub[sub.cat_call_state == "MAPPED"]
            rows.append([
                str(key), len(sub), len(ins), f"{len(ins) / len(sub):.4f}",
                f"{ins.mapped_fraction.median():.4f}" if len(ins) else "",
                f"{ins.ambiguous_fraction.median():.4f}" if len(ins) else "",
                f"{ins.unsupported_fraction.median():.4f}" if len(ins) else "",
                f"{ins.deleted_fraction.median():.4f}" if len(ins) else "",
                len(cmap), f"{len(cmap) / len(sub):.4f}",
                int((sub.cat_motif_class == "CATALYTIC_CONFIRMED").sum()),
                f"{(sub.cat_motif_class == 'CATALYTIC_CONFIRMED').sum() / len(cmap):.4f}"
                if len(cmap) else ""])
        rows.sort(key=lambda r: -r[1])
        write_tsv(path, [col, "n_eligible", "n_inspectable", "inspectable_fraction",
                         "median_MAPPED_fraction_inspectable",
                         "median_AMBIGUOUS_fraction_inspectable",
                         "median_UNSUPPORTED_fraction_inspectable",
                         "median_DELETED_fraction_inspectable",
                         "n_cat_state_mapped", "cat_mapped_fraction_of_eligible",
                         "n_cat_confirmed", "cat_confirmed_over_cat_mapped"], rows)
        return rows

    fam_rows = by("stage1_collapsed_family", f"{TABLES}/g5_qc_by_family.tsv")
    by("raw_myrt_family_label_set", f"{TABLES}/g5_qc_by_raw_myrt_family.tsv", min_n=100)
    by("multi_status", f"{TABLES}/g5_qc_by_multi_status.tsv")
    by("completeness_class", f"{TABLES}/g5_qc_by_completeness.tsv")
    by("view", f"{TABLES}/g5_qc_by_view.tsv")
    by("tax_domains", f"{TABLES}/g5_qc_by_tax_domain.tsv", min_n=100)
    by("source_databases", f"{TABLES}/g5_qc_by_source_database.tsv", min_n=100)
    d["tool_support"] = (d.by_myRT.fillna(False).astype(int).astype(str) + "/"
                         + d.by_PADLOC.fillna(False).astype(int).astype(str) + "/"
                         + d.by_DefenseFinder.fillna(False).astype(int).astype(str))
    by("tool_support", f"{TABLES}/g5_qc_by_tool_support.tsv")

    # ---- per-state occupancy over the whole run (states table, streamed) --------------
    print("  computing per-state occupancy")
    occ = collections.Counter()
    pf = pq.ParquetFile(f"{DATASET}/g5_states.parquet")
    for batch in pf.iter_batches(batch_size=2_000_000, columns=["state_id", "call_state"]):
        b = batch.to_pydict()
        occ.update(zip(b["state_id"], b["call_state"]))
    states = sorted({s for s, _ in occ})
    write_tsv(f"{TABLES}/g5_state_occupancy.tsv",
              ["state_id", "n_MAPPED", "n_AMBIGUOUS", "n_UNSUPPORTED", "n_DELETED_STATE",
               "n_total", "mapped_fraction", "denominator"],
              [[s, occ[(s, "MAPPED")], occ[(s, "AMBIGUOUS")], occ[(s, "UNSUPPORTED")],
                occ[(s, "DELETED_STATE")],
                sum(occ[(s, c)] for c in ("MAPPED", "AMBIGUOUS", "UNSUPPORTED",
                                          "DELETED_STATE")),
                f"{occ[(s, 'MAPPED')] / n_elig:.4f}", "ELIGIBLE"]
               for s in states])

    # ---- §14 g6 readiness -------------------------------------------------------------
    ready, notes = [], []
    for r in fam_rows:
        fam, n_el, n_in = r[0], r[1], r[2]
        verdict = ("READY" if n_in >= G6_MIN_INSPECTABLE else
                   "UNDERPOWERED_FOR_BETWEEN_FAMILY_COMPARISON")
        ready.append([fam, n_el, n_in, r[3], r[4], r[8], verdict])
    write_tsv(f"{TABLES}/g6_readiness_by_family.tsv",
              ["stage1_collapsed_family", "n_eligible", "n_inspectable",
               "inspectable_fraction", "median_MAPPED_fraction_inspectable",
               "n_cat_state_mapped", "g6_readiness"], ready)

    overall_insp = n_insp / n_elig
    flagged = [[r[0], r[1], r[2], r[3], f"{float(r[3]) - overall_insp:+.4f}"]
               for r in fam_rows
               if r[1] >= 100 and float(r[3]) < overall_insp - 0.10]
    write_tsv(f"{TABLES}/g6_readiness_flagged_strata.tsv",
              ["stage1_collapsed_family", "n_eligible", "n_inspectable",
               "inspectable_fraction", "delta_vs_run"], flagged)

    print(f"\nELIGIBLE {n_elig}  INSPECTABLE {n_insp} ({overall_insp:.4f})  "
          f"CAT-MAPPED {n_cat_mapped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
