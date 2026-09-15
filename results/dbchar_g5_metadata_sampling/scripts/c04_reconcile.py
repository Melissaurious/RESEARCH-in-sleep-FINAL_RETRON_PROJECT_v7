#!/usr/bin/env python3
"""c04 - reconcile g5 against its independent second count and against prior join work."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd

# The prior project's landed join rates, quoted from its g0 bundle table and read ONLY here.
PRIOR_G0_JOIN = "tables/g0_join_rate.tsv"


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    ap.add_argument("--prior-g0", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    T = W / "tables"
    join = {x["source_database"]: x for x in rd(T / "g5_join_coverage.tsv")}
    shape = {x["source_database"]: x for x in rd(T / "g5_catalogue_shape.tsv")}
    sec_g = {x["source_database"]: int(x["n_genomes"]) for x in rd(W / "second" / "c03_genomes_per_database.tsv")}
    sec_k = {x["file"]: int(x["n_distinct_keys"]) for x in rd(W / "second" / "c03_catalogue_keys.tsv")}
    A = []

    def cmp(check, scope, va, vb, rb="c03 (awk + sort -u)"):
        A.append([check, scope, "j01 (parquet/python)", va, rb, vb, va - vb,
                  "AGREE" if va == vb else "DISAGREE"])

    for db, row in join.items():
        cmp("genomes_per_database", db, int(row["n_genomes"]), sec_g.get(db, -1))
    for db, row in shape.items():
        cmp("catalogue_distinct_keys", row["file"], int(row["n_distinct_keys"]),
            sec_k.get(row["file"], -1))
    pd.DataFrame(A, columns=["check", "scope", "route_a", "value_a", "route_b", "value_b",
                             "delta_a_minus_b", "agreement"]).to_csv(
        T / "g5_second_counts.tsv", sep="\t", index=False)

    # ---- prior work ------------------------------------------------------------------
    B = []
    prior = rd(Path(a.prior_g0) / PRIOR_G0_JOIN)
    qual = {(x["source_database"], x["concept"]): x for x in rd(T / "g5_quality_availability.tsv")}
    # one grain only: the prior table repeats each database at P-REC, P-ATTR and P-LOC
    for x in [y for y in prior if y.get("grain") == "P-ATTR"]:
        db = x.get("source_database") or x.get("database") or ""
        if db not in join:
            continue
        mine = float(join[db]["pct_genomes_joined"])
        prior_a = x.get("pct_native_join_READING_A", "")
        B.append([db, "catalogue row resolves for a genome (reading A)", prior_a,
                  f"{mine:.4f}", "CONFIRMED" if prior_a and abs(float(str(prior_a).rstrip('%')) - mine) < 0.01
                  else "COMPARE", "g5 joins on the genome, the prior on its attribution grain"])
    for db in join:
        q = qual.get((db, "completeness"))
        if not q:
            continue
        B.append([db, "a completeness VALUE is obtainable natively", "see prior reading B",
                  q["pct_genomes_with_a_value"],
                  "CHANGED" if q["column"] == "no column in this catalogue" else "CONFIRMED",
                  "g5 measures NATIVE availability only; the prior reached NCBI completeness "
                  "through a GTDB accession bridge, which g5 does not implement"])
    pd.DataFrame(B, columns=["source_database", "quantity", "prior", "g5", "verdict", "note"]).to_csv(
        T / "g5_prior_reconciliation.tsv", sep="\t", index=False)

    bad = sum(1 for x in A if x[-1] != "AGREE")
    print(f"c04: second counts {len(A)} rows, {bad} DISAGREE; prior rows {len(B)}")
    for x in A:
        if x[-1] != "AGREE":
            print("  A", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
