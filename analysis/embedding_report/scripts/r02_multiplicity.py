#!/usr/bin/env python
"""Re-derive the RT/ncRNA partner-multiplicity statistics from FROZEN canonical tables.

Background: the workbench previously quoted 96.85 % / 82.28 % from the landed track report, a
derived document rather than a bundle table. This script re-derives them by counting partners in
two independent frozen tables that both enumerate the full 30,924-pair PAIR-ELIG universe:

  1. results/embed_g2b_frozen_split/tables/split_assignment.tsv.gz  (the hashed frozen split)
  2. results/embed_x2_rt_specificity_confirmation/tables/X2_PAIR_LEVEL_EFFECTS.tsv.gz (X2 export)

The two must agree exactly, and the totals must match the declared population, or the script
fails and writes nothing. This is a count over frozen tables; no model output is recomputed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SRC = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings/results")
SOURCES = {
    "embed_g2b_frozen_split (15e00b8)": SRC / "embed_g2b_frozen_split/tables/split_assignment.tsv.gz",
    "embed_x2 pair export (fdf0872)": SRC / "embed_x2_rt_specificity_confirmation/tables/X2_PAIR_LEVEL_EFFECTS.tsv.gz",
}
OUT = Path(__file__).resolve().parents[1] / "derived"
EXPECT = dict(pairs=30924, rts=29192, ncrnas=16458)


def stats(df):
    nc_per_rt = df.groupby("rt_seq_hash")["nc_seq_hash"].nunique()
    rt_per_nc = df.groupby("nc_seq_hash")["rt_seq_hash"].nunique()
    return {
        "n_pairs": len(df),
        "n_rt": len(nc_per_rt),
        "n_ncrna": len(rt_per_nc),
        "pct_rt_exactly_one_ncrna_partner": round(100 * float((nc_per_rt == 1).mean()), 2),
        "pct_rt_more_than_one_ncrna_partner": round(100 * float((nc_per_rt > 1).mean()), 2),
        "max_ncrna_partners_per_rt": int(nc_per_rt.max()),
        "pct_ncrna_exactly_one_rt_partner": round(100 * float((rt_per_nc == 1).mean()), 2),
        "pct_ncrna_more_than_one_rt_partner": round(100 * float((rt_per_nc > 1).mean()), 2),
        "max_rt_partners_per_ncrna": int(rt_per_nc.max()),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for label, path in SOURCES.items():
        df = pd.read_csv(path, sep="\t", usecols=["rt_seq_hash", "nc_seq_hash"])
        s = stats(df)
        s["source"] = label
        rows.append(s)

    a, b = rows
    keys = [k for k in a if k != "source"]
    if any(a[k] != b[k] for k in keys):
        print("FAIL: the two frozen tables disagree", file=sys.stderr)
        print(pd.DataFrame(rows).to_string(index=False), file=sys.stderr)
        return 1
    if (a["n_pairs"], a["n_rt"], a["n_ncrna"]) != (EXPECT["pairs"], EXPECT["rts"], EXPECT["ncrnas"]):
        print(f"FAIL: population totals differ from the declared universe {EXPECT}", file=sys.stderr)
        return 1

    tab = pd.DataFrame(rows)[["source"] + keys]
    tab.to_csv(OUT / "multiplicity_rederived.tsv", sep="\t", index=False)
    print(tab.to_string(index=False))
    print("\nOK: both frozen tables agree and match the declared PAIR-ELIG totals.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
