#!/usr/bin/env python3
"""c02 - independent recount of the intervening-CDS geometry.

Section 5's configuration classes rest on `n_cds_between`, which g3 computed. This script
recomputes it for a seeded sample straight from `rt_window_cds_v1`, with an interval-array
implementation that shares no code with `g3lib.cds_between`, and compares per placement.

It also re-derives the ncRNA/CDS overlap flags the same way. A mismatch is landed, not hidden.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import common as C

SCRIPT = "c02_independent_cds_between.py"
N_SAMPLE = 5000


def main() -> int:
    C.log("== c02 independent intervening-CDS recount")
    cols = ["source_file", "line_no", "rt_start", "rt_end", "nc_start", "nc_end", "n_cds_between",
            "overlaps_any_cds", "overlaps_non_rt_cds", "overlaps_rt_cds", "canonical",
            "rtcds_start", "rtcds_end"]
    p = C.derived("rt_ncrna_pairs_v1", cols)
    can = p[p.canonical].reset_index(drop=True)
    rng = np.random.default_rng(C.SEED)
    idx = rng.choice(len(can), size=min(N_SAMPLE, len(can)), replace=False)
    s = can.iloc[np.sort(idx)].copy()

    keys = set(zip(s.source_file, s.line_no))
    cds = C.derived("rt_window_cds_v1", ["source_file", "line_no", "cds_start", "cds_end",
                                         "is_rt_gene"])
    mask = pd.Series(list(zip(cds.source_file, cds.line_no))).isin(keys).to_numpy()
    cds = cds[mask]
    C.log(f"   {len(s):,d} sampled placements; {len(cds):,d} window CDS rows pulled")

    by_rec: dict[tuple, tuple] = {}
    for (sf, ln), g in cds.groupby(["source_file", "line_no"], sort=False):
        by_rec[(sf, ln)] = (g.cds_start.to_numpy(), g.cds_end.to_numpy(),
                            g.is_rt_gene.to_numpy())

    n_between, ov_any, ov_nonrt, ov_rt = [], [], [], []
    for r in s.itertuples(index=False):
        st, en, isrt = by_rec.get((r.source_file, r.line_no), (np.array([]), np.array([]),
                                                               np.array([], dtype=bool)))
        # the gap: bases strictly between the two closed intervals, ncRNA either side of the RT
        if r.nc_end < r.rt_start:
            lo, hi = r.nc_end + 1, r.rt_start - 1
        elif r.rt_end < r.nc_start:
            lo, hi = r.rt_end + 1, r.nc_start - 1
        else:
            lo, hi = 1, 0                      # overlapping -> empty gap
        if hi < lo or len(st) == 0:
            n_between.append(0)
        else:
            wholly_inside = (st >= lo) & (en <= hi) & (~isrt)
            n_between.append(int(wholly_inside.sum()))
        if len(st) == 0:
            ov_any.append(False), ov_nonrt.append(False), ov_rt.append(False)
            continue
        hits = (st <= r.nc_end) & (en >= r.nc_start)
        ov_any.append(bool(hits.any()))
        ov_nonrt.append(bool((hits & ~isrt).any()))
        ov_rt.append(bool((hits & isrt).any()))

    s["recount_n_cds_between"] = n_between
    s["recount_overlaps_any_cds"] = ov_any
    s["recount_overlaps_non_rt_cds"] = ov_nonrt
    s["recount_overlaps_rt_cds"] = ov_rt
    # g3 defines overlaps_non_rt_cds as "overlaps SOME CDS and not the RT CDS", so an ncRNA
    # overlapping the RT CDS *and* a neighbour reads False there. This recount's own flag is the
    # literal "overlaps a CDS that is not the RT CDS". Both are landed; the comparison uses g3's.
    s["recount_overlaps_non_rt_cds_g3_rule"] = (s.recount_overlaps_any_cds
                                                & ~s.recount_overlaps_rt_cds)

    rows = []
    for landed_col, mine_col in (("n_cds_between", "recount_n_cds_between"),
                                 ("overlaps_any_cds", "recount_overlaps_any_cds"),
                                 ("overlaps_non_rt_cds", "recount_overlaps_non_rt_cds_g3_rule")):
        agree = int((s[landed_col] == s[mine_col]).sum())
        rows.append(dict(field=landed_col, n_compared=len(s), n_agree=agree,
                         n_disagree=len(s) - agree, pct_agree=100 * agree / len(s)))
    # the RT-CDS overlap flag is defined against the RT CDS INTERVAL when one exists; where the
    # record has no RT CDS, g3 falls back to the rt_gene interval, which this recount does not
    # reproduce - so it is reported separately rather than compared.
    has_rtcds = s.rtcds_start.notna()
    agree_rt = int((s.loc[has_rtcds, "overlaps_rt_cds"]
                    == s.loc[has_rtcds, "recount_overlaps_rt_cds"]).sum())
    rows.append(dict(field="overlaps_rt_cds (records with a marked RT CDS only)",
                     n_compared=int(has_rtcds.sum()), n_agree=agree_rt,
                     n_disagree=int(has_rtcds.sum()) - agree_rt,
                     pct_agree=100 * agree_rt / max(1, int(has_rtcds.sum()))))
    both = int((s.recount_overlaps_rt_cds & s.recount_overlaps_non_rt_cds).sum())
    rows.append(dict(field="(context) placements overlapping the RT CDS AND another CDS - these "
                            "are why the two overlaps_non_rt_cds definitions differ",
                     n_compared=len(s), n_agree=len(s) - both, n_disagree=both,
                     pct_agree=100 * (len(s) - both) / len(s)))
    t = pd.DataFrame(rows)
    C.write_table("t43_independent_cds_recount", t, "placements",
                  f"a seeded random sample of {N_SAMPLE:,d} CANONICAL placements (seed "
                  f"{C.SEED}), recomputed from rt_window_cds_v1 by an implementation that shares "
                  f"no code with g3", SCRIPT, estimate=f"seeded sample of {N_SAMPLE}, not a census")

    bad = t[(t.n_disagree > 0) & ~t.field.str.startswith("(context)")]
    C.log(f"   {len(t)} fields compared, {int(t.n_disagree.sum())} placement-level disagreements")
    if len(bad):
        print(bad.to_string(index=False), file=sys.stderr)
        # a disagreement here is a finding about THIS bundle's understanding, not a licence to
        # edit g3: the run stops and the row is landed.
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
