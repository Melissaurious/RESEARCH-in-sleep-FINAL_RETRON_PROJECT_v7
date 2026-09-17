#!/usr/bin/env python3
"""s07 - the terminal decision, per arm, under control/PREDECLARATION.md section 8 as amended
by control/REPAIR_1.md.

The repair replaced a single significance test with a BRACKET, because neither null is
correct and they err in opposite directions. The vocabulary below is that bracket made
explicit; it does not loosen the declared criteria, it reports which of them are met.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g6lib import RHO_FLOOR, TABLES, read_tsv, write_tsv  # noqa: E402

BOTH = "REPRODUCIBLE_UNDER_BOTH_NULLS"
CLUS = "REPRODUCIBLE_UNDER_CLUSTER_NULL_ONLY"
NOT = "NOT_REPRODUCIBLE"
UNDER = "UNDERPOWERED"


MIN_GROUPS_FOR_A_VERDICT = 5   # below this the distance matrix has too few pairs to be read


def verdict(r, p1, p2, n_groups=None):
    if np.isnan(r):
        return UNDER
    if n_groups is not None and n_groups < MIN_GROUPS_FOR_A_VERDICT:
        # e.g. 3 groups gives 3 pairwise distances and rho saturates at 1.0 trivially
        return UNDER
    if p2 is None or np.isnan(p2):
        # No null could be computed: after permutation no labelling reached the stratum
        # threshold in both halves. "Not reproducible" cannot be asserted against a null that
        # does not exist, so this is UNDERPOWERED.
        return UNDER
    if r < RHO_FLOOR:
        return NOT
    e1 = (p1 is not None) and (not np.isnan(p1)) and r > p1
    e2 = (p2 is not None) and (not np.isnan(p2)) and r > p2
    if e1 and e2:
        return BOTH
    if e2:
        return CLUS
    return NOT


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def main():
    bf = read_tsv(os.path.join(TABLES, "g6_between_family_rho.tsv"))
    wr = read_tsv(os.path.join(TABLES, "g6_within_retron_rho.tsv"))
    ctrl = {c["control_id"]: c for c in read_tsv(os.path.join(TABLES, "g6_controls.tsv"))}

    rows = []

    # ---- between-family arm ----------------------------------------------------------
    prim = next(r for r in bf if r["analysis_id"] == "PRIMARY")
    r0, p1, p2 = f(prim["rho"]), f(prim["null1_p99"]), f(prim["null2_p99"])
    v0 = verdict(r0, p1, p2, int(prim["n_groups"]))
    surv = []
    for r in bf:
        if r["analysis_id"] == "PRIMARY":
            continue
        rr, pp2 = f(r["rho"]), f(r["null2_p99"])
        surv.append((r["analysis_id"], rr, pp2,
                     verdict(rr, f(r.get("null1_p99")), pp2, int(r["n_groups"]))))
    held = [s for s in surv if s[3] in (BOTH, CLUS)]
    rows.append(dict(
        arm="between_family", labelling="stage1_collapsed_family (42 families, 36 qualifying)",
        rho=f"{r0:.4f}", null1_p99=f"{p1:.4f}", null2_p99=f"{p2:.4f}",
        effect_floor_met="YES" if r0 >= RHO_FLOOR else "NO",
        terminal_verdict=v0,
        controls_held=f"{len(held)}/{len(surv)}",
        controls_detail="; ".join(f"{a}:{d}" for a, _b, _c, d in surv),
        what_it_means=(
            "Family labels replicate across halves that share no cluster. The two nulls "
            "disagree, and that disagreement IS the result: under the cluster-level null the "
            "structure is real; under the sequence-level null it is not distinguishable from "
            "visibility composition. REPAIR_1 argues the sequence-level null is invalid here "
            "(99.92% of clusters span one family), but also that the cluster-level null errs "
            "the other way. The honest statement is the bracket, not either endpoint."
            if v0 == CLUS else
            "See rho against both nulls and the per-control verdicts."),
        unit="exact RT (INSPECTABLE)", denominator="354,102 inspectable exact RTs"))

    # ---- within-Retron arm -----------------------------------------------------------
    for r in wr:
        rr, pp2 = f(r["rho"]), f(r["null2_p99"])
        v = verdict(rr, f(r.get("null1_p99")), pp2, int(r["n_groups"]))
        rows.append(dict(
            arm="within_retron", labelling=r["analysis"][:110],
            rho=r["rho"], null1_p99=r.get("null1_p99", ""),
            null2_p99=r["null2_p99"],
            effect_floor_met="YES" if (not np.isnan(rr) and rr >= RHO_FLOOR) else "NO",
            terminal_verdict=v, controls_held="n/a - the arm IS the labelling",
            controls_detail=f"{r['n_groups']} qualifying groups",
            what_it_means=("a tool annotation used as a stratum, never as truth; no accuracy "
                           "statement of any kind is made against it"
                           if "subtype" in r["analysis_id"] else
                           "no tool annotation participates in this labelling"),
            unit="exact RT (INSPECTABLE, Retron)", denominator="53,722 inspectable retrons"))

    write_tsv(os.path.join(TABLES, "g6_terminal_decision.tsv"),
              ["arm", "labelling", "rho", "null1_p99", "null2_p99", "effect_floor_met",
               "terminal_verdict", "controls_held", "controls_detail", "what_it_means",
               "unit", "denominator"], rows)

    # ---- summary ---------------------------------------------------------------------
    tot = read_tsv(os.path.join(TABLES, "g6_call_state_totals.tsv"))
    clu = read_tsv(os.path.join(TABLES, "g6_clustering_resource.tsv"))
    pur = read_tsv(os.path.join(TABLES, "g6_cluster_family_purity.tsv"))
    strata = read_tsv(os.path.join(TABLES, "g6_retron_subtype_strata.tsv"))
    S = [("population_catalogue", 501561, "context only, never a denominator"),
         ("population_eligible", 369381, "G5_ELIGIBLE_N"),
         ("population_inspectable", 354102, "verdict MAPPED - the architecture denominator"),
         ("families_total", 42, "stage1_collapsed_family"),
         ("families_qualifying", prim["n_groups"], ">=100 inspectable in BOTH halves"),
         ("clusters_primary_id0.90", next(c["n_clusters"] for c in clu if c["role"] == "PRIMARY"),
          "label-blind mmseqs linclust, 369,381 eligible sequences"),
         ("cluster_family_purity", next(p["value"] for p in pur
                                        if p["quantity"] == "purity_fraction"),
          "the evidence that triggered repair 1"),
         ("rho_between_family", f"{r0:.4f}", "split-half, halves share no cluster"),
         ("null1_p99_between_family", f"{p1:.4f}", "sequence-level - declared, retained"),
         ("null2_p99_between_family", f"{p2:.4f}", "cluster-level - repair 1"),
         ("terminal_verdict_between_family", v0, "see g6_terminal_decision.tsv"),
         ("retron_subtype_strata_underpowered",
          sum(1 for s in strata if s["powered"] == "UNDERPOWERED"),
          f"of {len(strata)} strata, threshold 100 inspectable"),
         ("controls_pass", sum(1 for c in ctrl.values() if c["result"] == "PASS"),
          f"of {len(ctrl)} declared in s05"),
         ("repair_cycles_used", "1 of 1", "control/REPAIR_1.md - the allowance is now spent")]
    for c in tot:
        S.append((f"call_state_{c['call_state']}", c["n_state_calls"],
                  f"fraction {c['fraction']} of 55,407,150 state calls"))
    write_tsv(os.path.join(TABLES, "g6_summary.tsv"),
              ["quantity", "value", "note"],
              [dict(quantity=a, value=b, note=c) for a, b, c in S])

    print("s07: terminal decision")
    for r in rows:
        print(f"  {r['arm']:<15} {r['labelling'][:42]:<42} rho={r['rho']:>7} "
              f"-> {r['terminal_verdict']}")


if __name__ == "__main__":
    main()
