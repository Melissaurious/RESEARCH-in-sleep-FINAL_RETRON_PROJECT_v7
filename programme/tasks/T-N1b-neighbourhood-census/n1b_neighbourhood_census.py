#!/usr/bin/env python3
"""
T-N1b · CDS-neighbourhood census over all RT-family records, with edge status.

FROZEN BEFORE EXECUTION (WORKING_RULES §6b).

KEY CORRECTION vs T-N1. Its blocking negative shifted each already-selected RT CDS
against its own coordinates, which for ordinary gene lengths CANNOT overlap -- the
control was structurally forced to zero and could never have failed. Here the
negative PERMUTES ANCHORS ACROSS RECORDS and runs the SAME locator: record A's CDS
set is scored against record B's anchor. It can return any value.

SECOND CORRECTION. Zero-neighbour records are split into TRUE_ZERO_NEIGHBOUR and
EDGE_CLIPPED_ZERO, and the edge-clipping denominator is reported, so a consumer
cannot read contig truncation as genomic isolation.

THIRD CORRECTION. The population is RT-RECORDS-ALL-FAMILIES, not RETRON-LOCI, and
rows are RECORDS, not independent loci. locus_key and physical_locus_key are landed
so a consumer can collapse them.
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import argparse, hashlib, json, os, time
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

D = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived"
CDS = f"{D}/rt_window_cds_v1.parquet"
RECS = f"{D}/rt_records_v1.parquet"
EXC = f"{D}/rt_cds_recovery_v1.parquet"

PERM_MAX = 0.05
ANCHOR_MIN = 0.99
REPRO_MIN = 0.999
SEED = 20260920


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def tsv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\t".join(header) + "\n")
        for r in rows:
            fh.write("\t".join("" if v is None else str(v) for v in r) + "\n")


def truthy(s):
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--prerun-commit", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.outdir)
    t0 = time.time()
    ctrl = []

    def add(c, t, b, e, o, s, d=""):
        ctrl.append([c, t, b, e, o, s, d])

    hashes = {os.path.basename(p): sha256(p) for p in (CDS, RECS, EXC)}

    cds = pq.read_table(CDS, columns=[
        "source_file", "line_no", "cds_start", "cds_end", "cds_strand",
        "is_rt_gene", "partial"]).to_pandas()
    cds["line_no"] = cds["line_no"].astype("int64")
    gk = ["source_file", "line_no"]

    rtc = cds[cds["is_rt_gene"]]
    per = rtc.groupby(gk, observed=True).size()
    frac_u = float((per == 1).mean()) if len(per) else 0.0
    add("N1b_POS_anchor_unique", "positive", "YES",
        f"each anchored record carries exactly one is_rt_gene CDS, >= {ANCHOR_MIN:.0%}",
        f"{int((per==1).sum())}/{len(per)} = {frac_u:.6f}",
        "PASS" if frac_u >= ANCHOR_MIN else "FAIL",
        "DECLARED DEFINITIONAL: anchors are defined by this flag; structural check only")

    anchor = rtc.drop_duplicates(gk)[gk + ["cds_start", "cds_end", "cds_strand"]].rename(
        columns={"cds_start": "rt_start", "cds_end": "rt_end", "cds_strand": "rt_strand"})

    # ---- FALSIFIABLE NEGATIVE: permute anchors ACROSS records ----------
    rng = np.random.default_rng(SEED)
    perm = anchor.copy()
    idx = rng.permutation(len(perm))
    perm[["rt_start", "rt_end"]] = anchor[["rt_start", "rt_end"]].to_numpy()[idx]
    # a permuted anchor is "recovered" if it overlaps an is_rt_gene CDS of THIS record
    pj = rtc.merge(perm[gk + ["rt_start", "rt_end"]], on=gk, how="inner")
    rec_rate = float(((pj["cds_start"] <= pj["rt_end"]) &
                      (pj["cds_end"] >= pj["rt_start"])).mean()) if len(pj) else 0.0
    add("N1b_NEG_permuted_anchor", "negative", "YES",
        f"scoring each record's CDS set against a DIFFERENT record's anchor recovers an "
        f"RT CDS at <= {PERM_MAX:.0%}",
        f"{rec_rate:.6f} over {len(pj):,} RT-CDS rows",
        "PASS" if rec_rate <= PERM_MAX else "FAIL",
        f"seed={SEED}; the same locator, a permuted anchor — this can fail")

    exc = pq.read_table(EXC, columns=["source_file", "line_no", "n_cds",
                                      "no_rt_cds_class"]).to_pandas()
    exc["line_no"] = exc["line_no"].astype("int64")
    sizes = cds.groupby(gk, observed=True).size().rename("n_recomp")
    em = exc.merge(sizes, left_on=gk, right_index=True, how="left")
    em["n_recomp"] = em["n_recomp"].fillna(0).astype("int64")
    rep = float((em["n_recomp"] == em["n_cds"].astype("int64")).mean())
    add("N1b_POS_reproduce_n_cds", "positive", "YES",
        f"recomputed CDS-per-record reproduces landed rt_cds_recovery_v1.n_cds >= {REPRO_MIN}",
        f"{int((em['n_recomp']==em['n_cds'].astype('int64')).sum())}/{len(em)} = {rep:.6f}",
        "PASS" if rep >= REPRO_MIN else "FAIL",
        "the exception table is DISJOINT from the anchored set; annotation only")

    fails = [c[0] for c in ctrl if c[2] == "YES" and c[5] != "PASS"]
    if fails:
        tsv(os.path.join(out, "tables/N1b_controls.tsv"),
            ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], ctrl)
        os.makedirs(os.path.join(out, "logs"), exist_ok=True)
        json.dump({"task_state": "VOID", "blocking_failures": fails,
                   "prerun_commit": a.prerun_commit},
                  open(os.path.join(out, "logs/run_log.json"), "w"), indent=2, sort_keys=True)
        print("BLOCKING CONTROL FAILURE: " + ";".join(fails)); print("TASK_STATE: VOID"); return 2

    # ---- PRIMARY --------------------------------------------------------
    nb = cds.merge(anchor, on=gk, how="inner")
    nb = nb[~nb["is_rt_gene"]].copy()
    nb["gap_up"] = nb["rt_start"].astype("int64") - nb["cds_end"].astype("int64")
    nb["gap_dn"] = nb["cds_start"].astype("int64") - nb["rt_end"].astype("int64")
    nb["same"] = nb["cds_strand"].astype(str) == nb["rt_strand"].astype(str)
    nb["part"] = nb["partial"].astype(str).ne("00")

    g = anchor.set_index(gk)
    g["n_neighbour_cds"] = nb.groupby(gk, observed=True).size()
    g["n_upstream_cds"] = nb[nb.gap_up > 0].groupby(gk, observed=True).size()
    g["n_downstream_cds"] = nb[nb.gap_dn > 0].groupby(gk, observed=True).size()
    g["nearest_upstream_gap_bp"] = nb[nb.gap_up > 0].groupby(gk, observed=True)["gap_up"].min()
    g["nearest_downstream_gap_bp"] = nb[nb.gap_dn > 0].groupby(gk, observed=True)["gap_dn"].min()
    g["frac_neighbours_same_strand"] = nb.groupby(gk, observed=True)["same"].mean()
    g["n_partial_neighbours"] = nb.groupby(gk, observed=True)["part"].sum()
    g["n_overlapping_rt"] = nb[(nb.gap_up <= 0) & (nb.gap_dn <= 0)].groupby(gk, observed=True).size()
    for c in ("n_neighbour_cds", "n_upstream_cds", "n_downstream_cds",
              "n_partial_neighbours", "n_overlapping_rt"):
        g[c] = g[c].fillna(0).astype("int64")

    meta = pq.read_table(RECS, columns=[
        "source_file", "line_no", "type_set_norm", "multilabel", "contig",
        "win_start", "win_end", "fullseq_len", "clipped_end_flag",
        "true_start_clipped", "window_inverted", "rt_at_window_edge",
        "dist_rt_to_contig_start", "dist_rt_to_contig_end", "contig_len_lower_bound",
        "locus_key", "physical_locus_key"]).to_pandas()
    meta["line_no"] = meta["line_no"].astype("int64")
    g = g.reset_index().merge(meta, on=gk, how="left")
    g = g.merge(exc[["source_file", "line_no", "no_rt_cds_class"]], on=gk, how="left")
    g["rt_cds_exception_class"] = g["no_rt_cds_class"].fillna("NOT_AN_EXCEPTION")

    g["edge_affected"] = (truthy(g["clipped_end_flag"]) | truthy(g["true_start_clipped"])
                          | truthy(g["rt_at_window_edge"]) | truthy(g["window_inverted"]))
    zero = g["n_neighbour_cds"] == 0
    g["neighbourhood_qa"] = np.where(
        zero & g["edge_affected"], "EDGE_CLIPPED_ZERO",
        np.where(zero, "TRUE_ZERO_NEIGHBOUR",
                 np.where(g["n_upstream_cds"] == 0, "NO_UPSTREAM_CDS",
                          np.where(g["n_downstream_cds"] == 0, "NO_DOWNSTREAM_CDS", "OK"))))
    g["row_unit"] = "raw_source_record"

    g.to_csv(os.path.join(out, "tables/N1b_neighbourhood_per_record.tsv"),
             sep="\t", index=False)

    n = len(g)
    qa = g["neighbourhood_qa"].value_counts()
    nz = int(zero.sum())
    nze = int((zero & g["edge_affected"]).sum())
    tsv(os.path.join(out, "tables/N1b_zero_neighbour_causes.tsv"),
        ["cause", "n_records", "pct_of_zero_neighbour", "pct_of_all_records"],
        [["EDGE_CLIPPED_ZERO", nze, f"{100*nze/nz:.4f}" if nz else "", f"{100*nze/n:.4f}"],
         ["TRUE_ZERO_NEIGHBOUR", nz - nze, f"{100*(nz-nze)/nz:.4f}" if nz else "",
          f"{100*(nz-nze)/n:.4f}"],
         ["__denominator_zero_neighbour__", nz, "100.0000", f"{100*nz/n:.4f}"],
         ["__denominator_all_records__", n, "", "100.0000"]])

    ea = int(g["edge_affected"].sum())
    tsv(os.path.join(out, "tables/N1b_edge_state.tsv"),
        ["edge_field", "n_true", "pct_of_records", "denominator"],
        [["clipped_end_flag", int(truthy(g["clipped_end_flag"]).sum()),
          f"{100*truthy(g['clipped_end_flag']).mean():.4f}", n],
         ["true_start_clipped", int(truthy(g["true_start_clipped"]).sum()),
          f"{100*truthy(g['true_start_clipped']).mean():.4f}", n],
         ["rt_at_window_edge", int(truthy(g["rt_at_window_edge"]).sum()),
          f"{100*truthy(g['rt_at_window_edge']).mean():.4f}", n],
         ["window_inverted", int(truthy(g["window_inverted"]).sum()),
          f"{100*truthy(g['window_inverted']).mean():.4f}", n],
         ["any_edge_affected", ea, f"{100*ea/n:.4f}", n]])

    fam = g.groupby(g["type_set_norm"].fillna("UNLABELLED"), observed=True).agg(
        n_records=("n_neighbour_cds", "size"),
        median_neighbours=("n_neighbour_cds", "median"),
        pct_edge_affected=("edge_affected", "mean"),
        pct_zero=("n_neighbour_cds", lambda s: (s == 0).mean())).reset_index()
    fam = fam.sort_values("n_records", ascending=False)
    fam.to_csv(os.path.join(out, "tables/N1b_by_family.tsv"), sep="\t", index=False)

    def med(c):
        v = g[c].dropna()
        return round(float(v.median()), 4) if len(v) else None
    rows = [["n_anchored_records", n, "raw source records (NOT independent loci)", n],
            ["n_distinct_locus_key", int(g["locus_key"].nunique()), "loci", n],
            ["n_distinct_physical_locus_key", int(g["physical_locus_key"].nunique()),
             "physical loci", n],
            ["n_cds_rows_total", len(cds), "CDS rows", len(cds)],
            ["median_neighbour_cds_per_record", med("n_neighbour_cds"), "CDS", n],
            ["median_upstream_gap_bp", med("nearest_upstream_gap_bp"), "bp",
             int(g["nearest_upstream_gap_bp"].notna().sum())],
            ["median_downstream_gap_bp", med("nearest_downstream_gap_bp"), "bp",
             int(g["nearest_downstream_gap_bp"].notna().sum())],
            ["median_frac_neighbours_same_strand", med("frac_neighbours_same_strand"),
             "fraction", int(g["frac_neighbours_same_strand"].notna().sum())],
            ["n_edge_affected", ea, "records", n],
            ["n_zero_neighbour", nz, "records", n],
            ["n_zero_neighbour_edge_clipped", nze, "records", nz],
            ["n_zero_neighbour_true", nz - nze, "records", nz]]
    for k, v in qa.items():
        rows.append([f"qa_{k}", int(v), "records", n])
    tsv(os.path.join(out, "tables/N1b_summary.tsv"),
        ["quantity", "value", "unit", "denominator"], rows)
    tsv(os.path.join(out, "tables/N1b_controls.tsv"),
        ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], ctrl)

    log = {"task_state": "PASS", "prerun_commit": a.prerun_commit,
           "population": "RT-RECORDS-ALL-FAMILIES", "row_unit": "raw_source_record",
           "n_records": int(n), "n_distinct_physical_loci": int(g["physical_locus_key"].nunique()),
           "n_zero_neighbour": nz, "n_zero_neighbour_edge_clipped": nze,
           "permuted_anchor_recovery_rate": rec_rate, "seed": SEED,
           "input_sha256": hashes, "elapsed_s": round(time.time() - t0, 1),
           "blocking_failures": []}
    os.makedirs(os.path.join(out, "logs"), exist_ok=True)
    json.dump(log, open(os.path.join(out, "logs/run_log.json"), "w"), indent=2, sort_keys=True)
    print(json.dumps(log, indent=2, sort_keys=True))
    for c in ctrl:
        print(f"{c[5]:<7} {c[0]:<28} {c[4]}")
    print("TASK_STATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
