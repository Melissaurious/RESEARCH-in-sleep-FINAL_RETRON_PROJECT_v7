#!/usr/bin/env python3
"""s04 - the within-Retron arm.

Three labellings, all declared in control/PREDECLARATION.md section 6:

  DF   subtypes_defensefinder  - a TOOL ANNOTATION used as a stratum, on its own denominator
  PL   subtypes_padloc         - a TOOL ANNOTATION used as a stratum, on its own denominator
  LF   label-free              - groups derived from the label-blind clustering at identity
                                 0.30, so the within-Retron question can be asked where no
                                 tool assigns a subtype at all

DF and PL are NEVER pooled with each other: the two tools agree on only 44.6% of
system_subtypes, and their provenance differs (capital-initial = DefenseFinder, lowercase =
PADLOC). No accuracy, sensitivity, specificity, precision, recall, F1 or ROC is computed
against either, and tool disagreement is never called mapper error.
"""
import collections
import os
import sys

import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arms                                                               # noqa: E402
from g6lib import (CLUSTER_PRIMARY, DERIVED, G5, MIN_STRATUM,             # noqa: E402
                   NULL_PERCENTILE, TABLES, write_tsv)

CTRL_REPS = 60
UNIT = "exact RT (INSPECTABLE, Retron-labelled)"
ROWS, NULLROWS, STRATA = [], [], []


def subtype_maps(retron_hashes):
    tc = pq.read_table(os.path.join(DERIVED, "rt_tool_calls_v1.parquet"),
                       columns=["rt_seq_hash", "subtypes_defensefinder",
                                "subtypes_padloc"]).to_pylist()
    df, pl = collections.defaultdict(set), collections.defaultdict(set)
    for r in tc:
        h = r["rt_seq_hash"]
        if h not in retron_hashes:
            continue
        for col, acc in (("subtypes_defensefinder", df), ("subtypes_padloc", pl)):
            v = r[col]
            if not v:
                continue
            for tok in str(v).split(","):
                tok = tok.strip()
                if tok and tok.lower() not in ("none", "nan", ""):
                    acc[h].add(tok)

    def collapse(acc):
        # An exact RT carrying several subtype calls is its OWN stratum, never assigned to one
        # of them. Same discipline as MULTI at family level.
        return {h: (sorted(v)[0] if len(v) == 1 else "MULTI_SUBTYPE") for h, v in acc.items()}
    return collapse(df), collapse(pl)


def run(tag, label, M, labels, halves, mask, reps, strat, note):
    r, groups, ns = arms.rho(M, labels, halves, mask)
    n2 = arms.cluster_permuted_null(M, labels, halves, mask, reps, CTRL_REPS, 20260918, strat)
    p2 = float(np.percentile(n2, NULL_PERCENTILE)) if len(n2) else float("nan")
    n1 = arms.permuted_null(M, labels, halves, mask, CTRL_REPS, 20260918, strat)
    p1 = float(np.percentile(n1, NULL_PERCENTILE)) if len(n1) else float("nan")
    NULLROWS.extend([
        dict(analysis_id=tag, null="NULL-1 sequence-level (DECLARED, retained)",
             n_replicates=len(n1),
             median=f"{np.median(n1):.4f}" if len(n1) else "NA",
             p99=f"{p1:.4f}" if len(n1) else "NA",
             max=f"{n1.max():.4f}" if len(n1) else "NA",
             note="conservative against the alternative - see control/REPAIR_1.md"),
        dict(analysis_id=tag, null="NULL-2 cluster-level (REPAIR 1)",
             n_replicates=len(n2),
             median=f"{np.median(n2):.4f}" if len(n2) else "NA",
             p99=f"{p2:.4f}" if len(n2) else "NA",
             max=f"{n2.max():.4f}" if len(n2) else "NA",
             note="anti-conservative - see control/REPAIR_1.md")])
    ROWS.append(dict(arm="within_retron", analysis_id=tag, analysis=label,
                     rho=f"{r:.4f}" if not np.isnan(r) else "NA",
                     null1_p99=f"{p1:.4f}" if not np.isnan(p1) else "",
                     null2_p99=f"{p2:.4f}" if not np.isnan(p2) else "",
                     exceeds_null1="YES" if (not np.isnan(p1) and r > p1) else
                                   ("NO" if not np.isnan(p1) else ""),
                     exceeds_null2="YES" if (not np.isnan(p2) and r > p2) else "NO",
                     n_groups=len(groups), groups=";".join(groups),
                     n_sequences=int(sum(a + b for a, b in ns.values())) if ns else 0,
                     unit=UNIT, note=note))
    print(f"  {tag:<12} rho={r if not np.isnan(r) else float('nan'):>7.4f}  "
          f"null2_p99={p2:>7.4f}  groups={len(groups):<3} "
          f"{'EXCEEDS' if (not np.isnan(p2) and r > p2) else 'within null / NA'}")
    return r, groups, ns


def main():
    d = arms.load()
    M, fam, mf = d["M"], d["family"], d["mapped_fraction"]
    cw = pq.read_table(os.path.join(G5, "g5_metadata_crosswalk.parquet"),
                       columns=["rt_hash", "stage1_collapsed_family"]).to_pylist()
    retron_all = {r["rt_hash"] for r in cw if r["stage1_collapsed_family"] == "Retron"}

    is_ret = fam == "Retron"
    print(f"s04: Retron INSPECTABLE {int(is_ret.sum())} exact RTs")

    rep_map = arms.load_clusters(CLUSTER_PRIMARY)
    reps = np.array([rep_map.get(h, h) for h in d["rt_hash"].tolist()])
    halves = arms.halves_from(d["rt_hash"], rep_map)
    dec = arms.decile(mf)
    hashes = d["rt_hash"].tolist()

    dfm, plm = subtype_maps(retron_all)
    print(f"s04: DefenseFinder resolves {len(dfm)} retron exact RTs; PADLOC {len(plm)}")

    for tool, m in (("DF", dfm), ("PL", plm)):
        lab = np.array([m.get(h, "") for h in hashes])
        mask = is_ret & (lab != "")
        run(f"{tool}_subtype", f"retron subtype stratum from "
            f"{'DefenseFinder' if tool == 'DF' else 'PADLOC'} - TOOL ANNOTATION, own "
            f"denominator, never pooled with the other tool",
            M, lab, halves, mask, reps, dec,
            f"{int(mask.sum())} retron exact RTs carry a {tool} subtype")
        for g, n in collections.Counter(lab[mask].tolist()).most_common():
            STRATA.append(dict(tool=("DefenseFinder" if tool == "DF" else "PADLOC"),
                               stratum=g, n_inspectable=n,
                               powered="YES" if n >= MIN_STRATUM else "UNDERPOWERED",
                               unit=UNIT,
                               denominator=f"{int(mask.sum())} retrons with a {tool} subtype"))

    # label-free arm: groups = clusters at identity 0.30, halves still by 0.90-cluster
    lf_map = arms.load_clusters("0.30")
    lab = np.array([lf_map.get(h, "") for h in hashes])
    run("LABEL_FREE", "groups from the label-blind clustering at identity 0.30 - no tool "
        "annotation of any kind participates", M, lab, halves, is_ret & (lab != ""), reps, dec,
        "answers the within-Retron question where no tool assigns a subtype")

    write_tsv(os.path.join(TABLES, "g6_within_retron_rho.tsv"),
              ["arm", "analysis_id", "analysis", "rho", "null1_p99", "null2_p99",
               "exceeds_null1", "exceeds_null2", "n_groups", "groups", "n_sequences", "unit",
               "note"], ROWS)
    write_tsv(os.path.join(TABLES, "g6_within_retron_null.tsv"),
              ["analysis_id", "null", "n_replicates", "median", "p99", "max", "note"], NULLROWS)
    write_tsv(os.path.join(TABLES, "g6_retron_subtype_strata.tsv"),
              ["tool", "stratum", "n_inspectable", "powered", "unit", "denominator"], STRATA)
    print(f"s04: {sum(1 for s in STRATA if s['powered'] == 'UNDERPOWERED')} of {len(STRATA)} "
          f"subtype strata are UNDERPOWERED (<{MIN_STRATUM}) and are excluded from distance "
          f"matrices but still reported")


if __name__ == "__main__":
    main()
