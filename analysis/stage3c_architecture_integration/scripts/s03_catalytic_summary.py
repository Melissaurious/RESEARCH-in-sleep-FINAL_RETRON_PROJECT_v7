#!/usr/bin/env python3
"""s3c_gA — ANALYSIS of the committed Comparison-A join (descriptive; no inferential test).

Reads only STRUCTURE_STAGE3B_CROSSWALK.tsv, tables/A_residue_join.tsv and frozen 3A/3B tables.
Every denominator is counted a second time from the frozen 3B evaluation table (WA-D.3).

Writes tables/A_summary.tsv, tables/A_replicate_stability.tsv, tables/A_replicate_summary.tsv.
"""
import ast
import os
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3clib as L  # noqa: E402

X = L.read_tsv(os.path.join(L.S3C, "STRUCTURE_STAGE3B_CROSSWALK.tsv"))
ev = {r["chain"]: r for r in L.read_tsv(os.path.join(L.CAT3B_G2, "tables", "G2_TIERA_EVALUATION.tsv"))}
truth_tab = {f"{r['pdb_id']}_{r['chain']}": r for r in L.read_tsv(os.path.join(L.CAT3B_G2, "tables", "TRUTH_TABLE.tsv"))}

# ---- independent recount of the in-scope population straight from 3B's frozen tables ----------
recount = sorted(c for c, r in ev.items() if r["truth"] not in ("", "[]")
                 and truth_tab[c]["tier"] == "A_calibration")
recount_hit = sum(ev[c]["outcome"] == "HIT" for c in recount)

rows = []


def add(metric, stratum, arm, num, den, unit, recount_den="", note=""):
    rows.append(dict(metric=metric, stratum=stratum, arm=arm, numerator=num, denominator=den,
                     value=(num / den) if den else None, unit=unit, denominator_recount=recount_den,
                     recount_agrees=("YES" if recount_den == "" or recount_den == den else "NO"), note=note))


for arm in ("primary", "p4"):
    ins = [r for r in X if r["arm"] == arm and r["scope_3C"] == "IN_SCOPE_OWN_CHAIN_TRUTH"]
    for stratum in ("all_in_scope", "primary", "flagged"):
        S = ins if stratum == "all_in_scope" else [r for r in ins if r["stratum"] == stratum]
        rc = len(recount) if stratum == "all_in_scope" and arm == "primary" else ""
        if not S:
            continue
        n = len(S)
        add("in_scope_chains", stratum, arm, n, n, "chain", rc,
            f"{len({r['biological_group'] for r in S})} biological groups")
        add("site_in_one_unit", stratum, arm, sum(r["truth_site_state"] == "ONE_UNIT" for r in S), n,
            "chain with all truth Asp in one PDP unit")
        call = [r for r in S if r["C4_palm"] == "CALL"]
        add("site_in_palm_like_unit_given_palm_CALL", stratum, arm,
            sum(r["truth_site_in_palm_like"] == "YES" for r in call), len(call), "chain with palm-like CALL",
            note="site unit != called palm-like unit in the others")
        nocall = [r for r in S if r["C4_palm"] != "CALL"]
        tied = [r for r in nocall if r["target_rule"].startswith("TIED")]
        add("site_in_max_strand_unit_given_no_palm_CALL", stratum, arm,
            sum(r["target_unit"] != "" and r["truth_site_unit"] == r["target_unit"] for r in nocall),
            len(nocall), "chain with C4 NO_CALL or AMBIGUOUS",
            note=f"{len(tied)} TIED target (not broken)")
        single = [r for r in S if r["n_units"] == "1"]
        add("single_unit_chains", stratum, arm, len(single), n, "chain partitioned into one unit",
            note="site-in-unit is trivially true here")
        disc = [r for r in S if r["truth_site_unit_discontinuous"] == "YES"]
        add("site_unit_discontinuous", stratum, arm, len(disc), n, "chain whose site-containing unit has >1 segment")
        for role, k in Counter(r["truth_site_unit_role"] for r in S).items():
            add(f"site_unit_role={role}", stratum, arm, k, n, "chain")
        hit = sum(r["detector_outcome_3B"] == "HIT" for r in S)
        add("detector_HIT_as_frozen_by_3B", stratum, arm, hit, n, "chain",
            rc, note=f"control: must reproduce 3B's 13/19 on all_in_scope (recount HIT={recount_hit})"
            if stratum == "all_in_scope" else "")
        same = sum(r["detector_site_state"] == "ONE_UNIT" and r["detector_site_units"] == r["truth_site_unit"] for r in S)
        add("detector_prediction_in_same_unit_as_truth", stratum, arm, same, n, "chain",
            note="includes all 6 3B MISSes: residue-level miss, unit-level co-location")
        fr = [float(r["size_expected_fraction"]) for r in S if r["size_expected_fraction"]]
        add("median_size_expected_fraction_of_target_unit", stratum, arm, statistics.median(fr) if fr else None,
            "", f"fraction of modelled residues; n={len(fr)} chains with a defined target unit",
            note="chance of a random residue landing in the target unit")

# control: must reproduce 3B's frozen 13 HIT / 19
prim = [r for r in rows if r["metric"] == "detector_HIT_as_frozen_by_3B" and r["stratum"] == "all_in_scope"
        and r["arm"] == "primary"][0]
assert prim["numerator"] == 13 and prim["denominator"] == 19 == len(recount) and recount_hit == 13, prim

L.write_tsv(os.path.join(L.TABLES, "A_summary.tsv"), rows,
            ["metric", "stratum", "arm", "numerator", "denominator", "value", "unit", "denominator_recount",
             "recount_agrees", "note"])

# ---- replicate stability: catalytic identity/geometry vs partition, on the SAME pairs ------------
xp = {r["chain"]: r for r in X if r["arm"] == "primary"}
tierA = [c for c, r in xp.items() if r["tier_3B"] == "A_calibration" and r["detector_verdict_3B"] not in ("NOT_SCOREABLE", "")]
group = {c: xp[c]["biological_group"] for c in xp}
lab = L.pdp_labels("primary")
rep = []
for g, a, b in L.replicate_pairs(tierA, group):
    ok, common = L.numbering_consistent(a, b)
    ra, rb = xp[a], xp[b]
    both_truth = ra["scope_3C"] == rb["scope_3C"] == "IN_SCOPE_OWN_CHAIN_TRUTH"
    row = dict(biological_group=g, chain_a=a, chain_b=b, numbering_consistent="YES" if ok else "NO",
               n_shared_keys=len(common), both_own_truth="YES" if both_truth else "NO",
               truth_a=ra["truth_residues"], truth_b=rb["truth_residues"],
               truth_identical=("YES" if ra["truth_residues"] == rb["truth_residues"] else "NO") if both_truth else "",
               truth_pair_carboxylate_A_a=ra["truth_pair_carboxylate_A"], truth_pair_carboxylate_A_b=rb["truth_pair_carboxylate_A"],
               pred_a=ra["detector_prediction"] or ra["detector_verdict_3B"], pred_b=rb["detector_prediction"] or rb["detector_verdict_3B"],
               pred_identical="YES" if (ra["detector_prediction"] and ra["detector_prediction"] == rb["detector_prediction"]) else "NO",
               n_units_a=ra["n_units"], n_units_b=rb["n_units"],
               unit_count_equal="YES" if ra["n_units"] == rb["n_units"] else "NO",
               C4_a=ra["C4_palm"], C4_b=rb["C4_palm"], site_unit_jaccard=None, site_unit_basis="")
    if ok:
        basis, ua, ub = None, None, None
        if both_truth and ra["truth_site_state"] == rb["truth_site_state"] == "ONE_UNIT":
            basis, ua, ub = "truth", int(ra["truth_site_unit"]), int(rb["truth_site_unit"])
        elif ra["detector_site_state"] == rb["detector_site_state"] == "ONE_UNIT":
            basis, ua, ub = "detector_prediction", int(ra["detector_site_units"]), int(rb["detector_site_units"])
        if basis:
            sa = L.unit_members(lab[a])[ua] & common
            sb = L.unit_members(lab[b])[ub] & common
            row["site_unit_jaccard"], row["site_unit_basis"] = L.jaccard(sa, sb), basis
    rep.append(row)
L.write_tsv(os.path.join(L.TABLES, "A_replicate_stability.tsv"), rep, list(rep[0]))

cons = [r for r in rep if r["numbering_consistent"] == "YES"]
sm = []


def srow(metric, num, den, unit, note=""):
    sm.append(dict(metric=metric, numerator=num, denominator=den, value=(num / den) if den else None,
                   unit=unit, note=note))


srow("replicate_pairs_tierA_scoreable", len(rep), len(rep), "chain pair",
     f"{len({r['biological_group'] for r in rep})} groups")
srow("numbering_consistent_pairs", len(cons), len(rep), "chain pair", "3A C7 rule: shared keys, >=0.95 same residue")
bt = [r for r in cons if r["both_own_truth"] == "YES"]
srow("truth_set_identical", sum(r["truth_identical"] == "YES" for r in bt), len(bt), "pair with own-chain truth in both")
srow("detector_prediction_identical", sum(r["pred_identical"] == "YES" for r in cons), len(cons), "numbering-consistent pair")
srow("unit_count_equal", sum(r["unit_count_equal"] == "YES" for r in cons), len(cons), "numbering-consistent pair",
     "same pairs as the two rows above")
jj = [r["site_unit_jaccard"] for r in cons if r["site_unit_jaccard"] is not None]
srow("site_unit_jaccard_ge_0.70", sum(j >= 0.70 for j in jj), len(jj), "pair with a single site unit in both",
     f"median={statistics.median(jj):.3f}" if jj else "")
dd = [abs(float(r["truth_pair_carboxylate_A_a"]) - float(r["truth_pair_carboxylate_A_b"])) for r in bt
      if r["truth_pair_carboxylate_A_a"] and r["truth_pair_carboxylate_A_b"]]
srow("truth_pair_distance_abs_diff_le_0.5A", sum(d <= 0.5 for d in dd), len(dd), "pair with two-residue truth in both",
     f"max abs diff={max(dd):.2f} A" if dd else "")
L.write_tsv(os.path.join(L.TABLES, "A_replicate_summary.tsv"), sm, ["metric", "numerator", "denominator", "value", "unit", "note"])
for r in sm:
    print(r)
