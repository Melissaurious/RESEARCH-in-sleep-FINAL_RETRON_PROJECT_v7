#!/usr/bin/env python3
"""s05 - the two remaining declared controls.

PC-SPLIT  independence of the two halves is MEASURED, not inferred from cluster ids.
          Principle 7: "a cluster split is not automatically an independent split".
PC-POS    a positive control: a known-present signal (CAT_STATE 262 catalytic concordance)
          must recover across the same halves, showing the instrument has power on this
          substrate. Without it, no absence statement may be made (Principle D of the g6 plan).
"""
import os
import random
import subprocess
import sys

import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arms                                                               # noqa: E402
from g6lib import (CLUSTER_PRIMARY, G5, MIN_STRATUM, MMSEQS, TABLES,      # noqa: E402
                   WORK, write_tsv)

SAMPLE = 3000
SEED = 20260918


def pc_split(d, halves):
    """Measure residual cross-half sequence identity directly."""
    hashes = np.array(d["rt_hash"])
    a = hashes[halves == "A"].tolist()
    b = hashes[halves == "B"].tolist()
    rng = random.Random(SEED)
    sa = set(rng.sample(a, min(SAMPLE, len(a))))
    sb = set(rng.sample(b, min(SAMPLE, len(b))))
    src = os.path.join(WORK, "eligible.faa")
    fa, fb = os.path.join(WORK, "halfA.faa"), os.path.join(WORK, "halfB.faa")
    for keep, out in ((sa, fa), (sb, fb)):
        with open(out, "w") as fh:
            w = False
            for line in open(src):
                if line.startswith(">"):
                    w = line[1:].strip().split()[0] in keep
                if w:
                    fh.write(line)
    m8 = os.path.join(WORK, "halfAB.m8")
    if not os.path.exists(m8):
        subprocess.run([MMSEQS, "easy-search", fa, fb, m8, os.path.join(WORK, "tmp_ab"),
                        "--threads", "8", "-s", "5.7", "--max-seqs", "5"],
                       check=True, stdout=subprocess.DEVNULL)
    ids = []
    for line in open(m8):
        p = line.split("\t")
        if len(p) > 2 and p[0] != p[1]:
            ids.append(float(p[2]))
    ids = np.array(ids) if ids else np.array([0.0])
    over90 = float((ids >= 0.90).mean())
    return dict(n_query=len(sa), n_target=len(sb), n_hits=len(ids),
                median_identity=f"{np.median(ids):.4f}", p95_identity=f"{np.percentile(ids,95):.4f}",
                max_identity=f"{ids.max():.4f}", fraction_hits_at_or_above_0_90=f"{over90:.4f}")


def pc_pos(d, halves):
    """Known-present signal: catalytic concordance must recover across halves."""
    cat = pq.read_table(os.path.join(G5, "g5_catalytic.parquet"),
                        columns=["rt_hash", "cat_call_state", "cat_motif_class"]).to_pylist()
    cm = {r["rt_hash"]: r for r in cat}
    fam = d["family"]
    rows = []
    xa, xb = [], []
    for g in sorted(set(fam.tolist())):
        out = {}
        for h in ("A", "B"):
            sel = (fam == g) & (halves == h)
            hs = np.array(d["rt_hash"])[sel].tolist()
            mapped = [cm[x] for x in hs if x in cm and cm[x]["cat_call_state"] == "MAPPED"]
            conf = sum(1 for r in mapped if r["cat_motif_class"] == "CATALYTIC_CONFIRMED")
            out[h] = (conf, len(mapped))
        if out["A"][1] >= MIN_STRATUM and out["B"][1] >= MIN_STRATUM:
            fa, fb = out["A"][0] / out["A"][1], out["B"][0] / out["B"][1]
            xa.append(fa)
            xb.append(fb)
            rows.append(dict(family=g, half_A_confirmed=out["A"][0], half_A_cat_mapped=out["A"][1],
                             half_A_fraction=f"{fa:.4f}", half_B_confirmed=out["B"][0],
                             half_B_cat_mapped=out["B"][1], half_B_fraction=f"{fb:.4f}",
                             unit="exact RT", denominator="CAT_STATE-MAPPED in that family-half"))
    r = arms._spearman(np.array(xa), np.array(xb)) if len(xa) >= 3 else float("nan")
    return rows, r


def main():
    d = arms.load()
    rep_map = arms.load_clusters(CLUSTER_PRIMARY)
    halves = arms.halves_from(d["rt_hash"], rep_map)

    split = pc_split(d, halves)
    pos_rows, pos_r = pc_pos(d, halves)
    write_tsv(os.path.join(TABLES, "g6_pc_pos_catalytic.tsv"),
              ["family", "half_A_confirmed", "half_A_cat_mapped", "half_A_fraction",
               "half_B_confirmed", "half_B_cat_mapped", "half_B_fraction", "unit",
               "denominator"], pos_rows)

    ctrl = [
        dict(control_id="PC-SPLIT", kind="independence of the two halves, MEASURED",
             expectation="halves share no cluster by construction; the RESIDUAL cross-half "
                         "identity is measured rather than assumed to be zero",
             observed=f"{split['n_query']} half-A vs {split['n_target']} half-B sequences, "
                      f"{split['n_hits']} hits; median identity {split['median_identity']}, "
                      f"p95 {split['p95_identity']}, max {split['max_identity']}; "
                      f"{split['fraction_hits_at_or_above_0_90']} of hits at identity >= 0.90",
             result="MEASURED",
             note="Principle 7: a cluster split is not automatically an independent split. "
                  "Residual identity is reported as a limitation on rho, not repaired."),
        dict(control_id="PC-POS", kind="positive control - known-present signal",
             expectation="catalytic concordance (CAT_STATE 262, CATALYTIC_CONFIRMED) recovers "
                         "across the same halves, demonstrating power on this substrate",
             observed=f"Spearman rho = {pos_r:.4f} between half-A and half-B per-family "
                      f"CATALYTIC_CONFIRMED fraction over {len(pos_rows)} qualifying families",
             result="PASS" if (not np.isnan(pos_r) and pos_r >= 0.5) else "FAIL",
             note="On its own denominator: CAT_STATE-MAPPED sequences, never pooled with the "
                  "150 anchors. If this fails, no absence statement may be made."),
    ]
    write_tsv(os.path.join(TABLES, "g6_controls.tsv"),
              ["control_id", "kind", "expectation", "observed", "result", "note"], ctrl)
    for c in ctrl:
        print(f"  {c['control_id']:<10} {c['result']:<9} {c['observed'][:100]}")


if __name__ == "__main__":
    main()
