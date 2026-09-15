#!/usr/bin/env python3
"""c04 - reconcile g2b against its independent second count and against the landed g2 bundle."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    ap.add_argument("--g2-bundle", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    T = W / "tables"
    m = pd.read_parquet(W / "derived" / "rt_cds_recovery_v1.parquet")
    sec = {x["measure"]: int(x["n"]) for x in rd(W / "second" / "c02_classes.tsv")}
    g2 = {(x["population"], x["no_rt_cds_class"]): int(x["n_records"])
          for x in rd(Path(a.g2_bundle) / "tables" / "g2_rt_cds_classes.tsv")}

    rows = []

    def cmp(check, ra, va, rb, vb):
        rows.append([check, ra, va, rb, vb, va - vb, "AGREE" if va == vb else "DISAGREE"])

    cmp("records_without_a_marked_RT_CDS", "r01 (parquet)", len(m),
        "c02 (awk on raw bytes)", sec["records_without_is_rt_gene_true"])
    cmp("rt_inside_its_window", "r01", int((m.representation_class == "rt_inside_window").sum()),
        "c02", sec["rt_inside_its_window"])
    cmp("rt_beyond_window_end", "r01",
        int(m.representation_class.str.startswith("rt_beyond").sum()), "c02", sec["rt_beyond_window_end"])
    cmp("rt_crossing_a_window_edge", "r01",
        int(m.representation_class.str.contains("crosses").sum()), "c02", sec["rt_crossing_a_window_edge"])
    cmp("window_inverted", "r01",
        int((m.representation_class == "window_inverted_no_sequence_retrieved").sum()),
        "c02", sec["window_inverted"])
    cmp("rt_before_window_start", "r01",
        int((m.representation_class == "rt_before_window_start").sum()), "c02",
        sec["rt_before_window_start"])
    for cls, n in m.no_rt_cds_class.value_counts().items():
        tot = sum(v for (p, c), v in g2.items() if c == cls)
        cmp(f"class:{cls}", "r01", int(n), "landed g2 bundle g2_rt_cds_classes.tsv", tot)
    cmp("recovered_total", "r01", int((m.recovery_state == "RECOVERED").sum()),
        "landed g2: the two bt-verified no-Prodigal-call classes",
        sum(v for (p, c), v in g2.items() if c.startswith("no_prodigal_call_bt_verified")))
    cmp("every_record_keeps_a_usable_RT_sequence", "r01 elig_exact_rt", int(m.elig_exact_rt.sum()),
        "r01 row count", len(m))

    pd.DataFrame(rows, columns=["check", "route_a", "value_a", "route_b", "value_b",
                                "delta_a_minus_b", "agreement"]).to_csv(
        T / "g2b_second_counts.tsv", sep="\t", index=False)
    bad = sum(1 for r in rows if r[-1] != "AGREE")
    print(f"c04: {len(rows)} rows, {bad} DISAGREE")
    for r in rows:
        if r[-1] != "AGREE":
            print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
