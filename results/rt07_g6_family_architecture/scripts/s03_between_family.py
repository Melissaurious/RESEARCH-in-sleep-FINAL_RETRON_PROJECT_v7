#!/usr/bin/env python3
"""s03 - the between-family arm: is organization reproducible across labelled RT families?

Reports rho continuously, against BOTH nulls (control/REPAIR_1.md), and reports every control
whatever it shows. Each control gets its own null, because each changes the population.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arms                                                               # noqa: E402
from g6lib import (CLUSTER_PRIMARY, CLUSTER_SENSITIVITY, NULL_PERCENTILE,  # noqa: E402
                   NULL_REPLICATES, TABLES, WORK, write_tsv)

UNIT = "exact RT (INSPECTABLE)"
CTRL_REPS = 60
ROWS, NULLROWS = [], []


def run(tag, label, M, labels, halves, mask, reps, strat, note, n_rep=CTRL_REPS,
        both_nulls=True, seed=20260918):
    r, groups, ns = arms.rho(M, labels, halves, mask)
    n2 = arms.cluster_permuted_null(M, labels, halves, mask, reps, n_rep, seed, strat)
    p2 = float(np.percentile(n2, NULL_PERCENTILE)) if len(n2) else float("nan")
    p1 = float("nan")
    if both_nulls:
        n1 = arms.permuted_null(M, labels, halves, mask, n_rep, seed, strat)
        p1 = float(np.percentile(n1, NULL_PERCENTILE)) if len(n1) else float("nan")
        NULLROWS.extend([
            dict(analysis_id=tag, null="NULL-1 sequence-level (DECLARED, retained)",
                 n_replicates=len(n1), median=f"{np.median(n1):.4f}",
                 p99=f"{p1:.4f}", max=f"{n1.max():.4f}",
                 note="breaks within-cluster label constancy; conservative against the "
                      "alternative - see control/REPAIR_1.md"),
            dict(analysis_id=tag, null="NULL-2 cluster-level (REPAIR 1)",
                 n_replicates=len(n2), median=f"{np.median(n2):.4f}",
                 p99=f"{p2:.4f}", max=f"{n2.max():.4f}",
                 note="preserves within-cluster label constancy; anti-conservative because it "
                      "breaks between-cluster relatedness - see control/REPAIR_1.md")])
    else:
        NULLROWS.append(dict(analysis_id=tag, null="NULL-2 cluster-level (REPAIR 1)",
                             n_replicates=len(n2), median=f"{np.median(n2):.4f}",
                             p99=f"{p2:.4f}", max=f"{n2.max():.4f}",
                             note="own null for this control's own population"))
    ROWS.append(dict(arm="between_family", analysis_id=tag, analysis=label,
                     rho=f"{r:.4f}" if not np.isnan(r) else "NA",
                     null1_p99=f"{p1:.4f}" if not np.isnan(p1) else "",
                     null2_p99=f"{p2:.4f}" if not np.isnan(p2) else "",
                     exceeds_null1="YES" if (not np.isnan(p1) and r > p1) else
                                   ("NO" if not np.isnan(p1) else ""),
                     exceeds_null2="YES" if (not np.isnan(p2) and r > p2) else "NO",
                     n_groups=len(groups), groups=";".join(groups),
                     n_sequences=int(sum(a + b for a, b in ns.values())) if ns else 0,
                     unit=UNIT, note=note))
    print(f"  {tag:<20} rho={r:>7.4f}  null2_p99={p2:>7.4f}  "
          f"{'EXCEEDS' if (not np.isnan(p2) and r > p2) else 'within null':<12} "
          f"groups={len(groups)}")
    return r, groups


def main():
    d = arms.load()
    M, fam, mf, comp = d["M"], d["family"], d["mapped_fraction"], d["completeness"]
    print(f"s03: INSPECTABLE {len(fam)} exact RTs, {len(set(fam.tolist()))} families")

    rep_map = arms.load_clusters(CLUSTER_PRIMARY)
    reps = np.array([rep_map.get(h, h) for h in d["rt_hash"].tolist()])
    halves = arms.halves_from(d["rt_hash"], rep_map)
    allm = np.ones(len(fam), dtype=bool)
    dec = arms.decile(mf)

    pure, tot = arms.cluster_family_purity(reps, fam)
    print(f"s03: cluster/family purity {pure}/{tot} = {pure/tot:.4f}  "
          f"(the evidence that triggered repair 1)")

    r0, g0 = run("PRIMARY", f"split-half by cluster @ id {CLUSTER_PRIMARY}", M, fam, halves,
                 allm, reps, dec,
                 "halves share no cluster; families need >=100 inspectable in BOTH halves",
                 n_rep=NULL_REPLICATES, both_nulls=True)

    for lo, hi in ((0.0, 0.5), (0.5, 0.8), (0.8, 1.01)):
        m = (mf >= lo) & (mf < hi)
        run(f"CTRL-VIS[{lo},{hi})", "narrow mapped_fraction stratum", M, fam, halves, m, reps,
            dec, f"{int(m.sum())} sequences with mapped_fraction in [{lo},{hi})")

    for ident in [CLUSTER_PRIMARY] + CLUSTER_SENSITIVITY:
        rp = arms.load_clusters(ident)
        rr = np.array([rp.get(h, h) for h in d["rt_hash"].tolist()])
        seen, keep = set(), np.zeros(len(fam), dtype=bool)
        for i, c in enumerate(rr.tolist()):
            if c not in seen:
                seen.add(c)
                keep[i] = True
        hv = arms.halves_from(d["rt_hash"], rp)
        run(f"CTRL-REL@{ident}", "one representative per cluster", M, fam, hv, keep, rr, dec,
            f"{int(keep.sum())} cluster representatives at identity {ident}")

    for c in sorted(set(comp.tolist())):
        m = comp == c
        if m.sum() < 1000:
            continue
        run(f"CTRL-COMP[{c}]", "one completeness class", M, fam, halves, m, reps, dec,
            f"{int(m.sum())} sequences in completeness_class {c}")

    write_tsv(os.path.join(TABLES, "g6_between_family_rho.tsv"),
              ["arm", "analysis_id", "analysis", "rho", "null1_p99", "null2_p99",
               "exceeds_null1", "exceeds_null2", "n_groups", "groups", "n_sequences", "unit",
               "note"], ROWS)
    write_tsv(os.path.join(TABLES, "g6_between_family_null.tsv"),
              ["analysis_id", "null", "n_replicates", "median", "p99", "max", "note"], NULLROWS)

    prof = []
    for g in g0:
        sel = fam == g
        p = M[sel].mean(axis=0)
        prof.append(dict(family=g, n_inspectable=int(sel.sum()),
                         mean_mapped_fraction=f"{p.mean():.4f}",
                         profile=";".join(f"{x:.4f}" for x in p),
                         unit=UNIT, denominator=f"{int(sel.sum())} inspectable in this family"))
    write_tsv(os.path.join(TABLES, "g6_family_state_profiles.tsv"),
              ["family", "n_inspectable", "mean_mapped_fraction", "profile", "unit",
               "denominator"], prof)
    write_tsv(os.path.join(TABLES, "g6_cluster_family_purity.tsv"),
              ["quantity", "value", "unit", "denominator"],
              [dict(quantity="clusters_spanning_one_family", value=pure, unit="cluster",
                    denominator=f"{tot} clusters at identity {CLUSTER_PRIMARY}"),
               dict(quantity="purity_fraction", value=f"{pure/tot:.4f}", unit="fraction",
                    denominator=f"{tot} clusters")])
    np.save(os.path.join(WORK, "state_ids.npy"), d["state_ids"])
    print(f"s03: primary rho={r0:.4f}")


if __name__ == "__main__":
    main()
