#!/usr/bin/env python3
"""c05 - reconcile g4 against its independent second count and against prior family baselines."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd


def rd(p: Path, comment: str | None = None) -> pd.DataFrame:
    return pd.read_csv(p, sep="\t", comment=comment)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    ap.add_argument("--prior-c16", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    T = W / "tables"
    mine = rd(T / "g4_exact_rt_per_family_label.tsv")
    sec = rd(W / "second" / "c03_exact_rt_per_label.tsv")
    A = []

    def cmp(check, scope, va, vb):
        A.append([check, scope, "b01 (parquet)", va, "c03 (awk + sort -u)", vb,
                  (va - vb) if isinstance(va, int) and isinstance(vb, int) else "",
                  "AGREE" if va == vb else "DISAGREE"])

    j = mine.merge(sec, on="file_label", how="outer", suffixes=("_mine", "_awk"))
    for r in j.itertuples():
        cmp("distinct_exact_rt_per_label", r.file_label,
            int(r.n_exact_rt_mine) if pd.notna(r.n_exact_rt_mine) else -1,
            int(r.n_exact_rt_awk) if pd.notna(r.n_exact_rt_awk) else -1)
        cmp("min_aa_len_per_label", r.file_label,
            int(r.min_aa_len_mine) if pd.notna(r.min_aa_len_mine) else -1,
            int(r.min_aa_len_awk) if pd.notna(r.min_aa_len_awk) else -1)
        cmp("max_aa_len_per_label", r.file_label,
            int(r.max_aa_len_mine) if pd.notna(r.max_aa_len_mine) else -1,
            int(r.max_aa_len_awk) if pd.notna(r.max_aa_len_awk) else -1)
    tot = rd(W / "second" / "c03_totals.tsv")
    cmp("sum_of_distinct_exact_rt_per_label", "all family labels",
        int(mine.n_exact_rt.sum()), int(tot.n.iloc[0]))
    pd.DataFrame(A, columns=["check", "scope", "route_a", "value_a", "route_b", "value_b",
                             "delta_a_minus_b", "agreement"]).to_csv(
        T / "g4_second_counts.tsv", sep="\t", index=False)

    # ---- prior work, read only now ---------------------------------------------------
    prior = rd(Path(a.prior_c16), comment="#")
    prior = prior[prior.group_kind.eq("rt_family")][["group", "n", "median"]].rename(
        columns={"group": "family_label", "n": "prior_n", "median": "prior_median"})
    ln = rd(T / "g4_rt_length_by_family.tsv")[["family_label", "n_exact_rt", "median"]]
    m = ln.merge(prior, on="family_label", how="outer")
    m["delta_n"] = m.n_exact_rt - m.prior_n
    m["delta_median"] = m["median"] - m.prior_median
    m["verdict"] = [
        "CONFIRMED" if (pd.notna(x.delta_n) and x.delta_n == 0 and x.delta_median == 0)
        else ("CHANGED" if pd.notna(x.prior_n) and pd.notna(x.n_exact_rt) else "UNRESOLVED")
        for x in m.itertuples()]
    m["note"] = [
        "" if v == "CONFIRMED" else
        ("prior grain is V-RT over its collapsed locus table; g4's is V-RT-SINGLE over the g1 "
         "corpus, and a protein spanning two family labels is V-RT-CROSS here"
         if v == "CHANGED" else "family absent from one of the two tables")
        for v in m.verdict]
    m.sort_values("n_exact_rt", ascending=False).to_csv(
        T / "g4_prior_reconciliation.tsv", sep="\t", index=False)

    nA = sum(1 for x in A if x[-1] != "AGREE")
    print(f"c05: second counts {len(A)} rows, {nA} DISAGREE; prior families {len(m)}, "
          f"CONFIRMED {(m.verdict == 'CONFIRMED').sum()}, CHANGED {(m.verdict == 'CHANGED').sum()}")
    for x in A:
        if x[-1] != "AGREE":
            print("  A", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
