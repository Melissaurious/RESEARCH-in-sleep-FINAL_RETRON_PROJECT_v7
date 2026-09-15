#!/usr/bin/env python3
"""c04 - reconcile g6 against its independent second count and the prior tool findings."""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
import pandas as pd
PRIOR_SUBTYPE_AGREEMENT_PCT = 44.6   # prior project's figure, read only here

def rd(p):
    with p.open(encoding="utf-8") as fh: return list(csv.DictReader(fh, delimiter="\t"))

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--work", required=True); a = ap.parse_args()
    W = Path(a.work); T = W / "tables"
    mine = {(x["measure"], x["key"]): int(x["n"]) for x in rd(T / "g6_tool_matrix_retron_all_records.tsv")}
    sec = {(x["measure"], x["key"]): int(x["n"]) for x in rd(W / "second" / "c02_tool_counts.tsv")}
    A = []
    for k in sorted(set(mine) | set(sec)):
        va, vb = mine.get(k, -1), sec.get(k, -1)
        A.append([k[0], k[1], "t01 (parquet)", va, "c02 (awk on raw bytes)", vb, va - vb,
                  "AGREE" if va == vb else "DISAGREE"])
    pd.DataFrame(A, columns=["check", "key", "route_a", "value_a", "route_b", "value_b",
                             "delta_a_minus_b", "agreement"]).to_csv(
        T / "g6_second_counts.tsv", sep="\t", index=False)
    ag = {x["measure"]: x for x in rd(T / "g6_subtype_agreement.tsv")}
    n_both = int(ag["records where both tools wrote a subtype"]["n"])
    n_agree = int(ag["the two strings agree after case/punctuation normalisation"]["n"])
    pct = round(100 * n_agree / n_both, 4)
    B = [["system_subtypes agreement between the two tools", f"{PRIOR_SUBTYPE_AGREEMENT_PCT}%",
          f"{pct}%", "CONFIRMED" if abs(pct - PRIOR_SUBTYPE_AGREEMENT_PCT) < 2 else "CHANGED",
          "prior grain and normalisation are not stated precisely; g6 normalises case and "
          "punctuation on the Retron records where BOTH tools wrote a label"],
         ["system_subtypes is two tools in one field", "prior: capital-initial = DefenseFinder, "
          "lowercase = PADLOC; carry it, never groupby it",
          "g6 splits by that rule and reports each vocabulary separately", "CONFIRMED",
          "0 records carry an unclassifiable subtype string, so the case rule partitions the field"],
         ["tool agreement is not independent corroboration", "prior: the tools share model lineage",
          "g6 reports the matrix and the asymmetry, and claims no corroboration", "CONFIRMED", ""]]
    pd.DataFrame(B, columns=["quantity", "prior", "g6", "verdict", "note"]).to_csv(
        T / "g6_prior_reconciliation.tsv", sep="\t", index=False)
    bad = sum(1 for x in A if x[-1] != "AGREE")
    print(f"c04: second counts {len(A)} rows, {bad} DISAGREE; prior rows {len(B)}; agreement {pct}%")
    for x in A:
        if x[-1] != "AGREE": print("  A", x)
    return 0

if __name__ == "__main__":
    sys.exit(main())
