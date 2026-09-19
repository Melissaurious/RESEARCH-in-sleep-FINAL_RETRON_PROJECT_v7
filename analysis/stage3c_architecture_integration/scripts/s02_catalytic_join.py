#!/usr/bin/env python3
"""s3c_gA — JOIN of Stage-3B catalytic evidence onto frozen Stage-3A units (LAUNCHER_03C 7a, A).

Scope (DECLARED): truth only where 3B's own frozen Tier-A evaluation used it — the 19 chains with
a non-empty `truth` in G2_TIERA_EVALUATION.tsv (13 HIT / 6 MISS). Tier-A chains that 3B scored
NO_TRUTH (incl. the 4 transferred-truth chains) contribute detector output only, flagged.
Tier-B / Tier-C rows are counted and excluded (K3): no residue of theirs is placed.

Target unit (DECLARED, handoff): the palm-like unit when C4 = CALL; otherwise the unit with the
largest max_strands_one_sheet (a tie is reported as TIED, not broken).

Writes STRUCTURE_STAGE3B_CROSSWALK.tsv (one row per chain x partition arm) and
tables/A_residue_join.tsv (one row per placed residue).
"""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3clib as L  # noqa: E402

JOIN_MIN = 0.95   # DECLARED (K6): fraction of modelled external residues that must resolve to a PDP key

ev = {r["chain"]: r for r in L.read_tsv(os.path.join(L.CAT3B_G2, "tables", "G2_TIERA_EVALUATION.tsv"))}
truth_tab = {f"{r['pdb_id']}_{r['chain']}": r for r in L.read_tsv(os.path.join(L.CAT3B_G2, "tables", "TRUTH_TABLE.tsv"))}
t1 = L.t1()


def parse_res(s):
    s = (s or "").strip()
    if s in ("", "[]", "()"):
        return []
    return [int(x) for x in ast.literal_eval(s)]


def tightest(chain, pair):
    """Carboxylate O-O distance of a residue pair from 3B's frozen tightest_asp_pairs column."""
    if len(pair) < 2:
        return None
    want = f"{min(pair)}-{max(pair)}"
    for tok in truth_tab[chain]["tightest_asp_pairs"].split():
        p, d = tok.split(":")
        if p == want:
            return float(d)
    return None


rows, rrows, k6 = [], [], []
for c in L.chains():
    tr = truth_tab[c]
    tier = tr["tier"]
    e = ev.get(c)
    if tier != "A_calibration":
        scope = "EXCLUDED_TIER_B_OR_C_3B_CLOSURE"
        truth, pred = [], []
    else:
        truth = parse_res(e["truth"]) if e else []
        pred = parse_res(e["pred"]) if e else []
        if truth:
            scope = "IN_SCOPE_OWN_CHAIN_TRUTH"
        elif tr["truth_source"] == "TRANSFERRED_WITHIN_REPLICATE_GROUP":
            scope = "TIER_A_TRANSFERRED_TRUTH_NOT_SCORED_BY_3B_DETECTOR_ONLY"
        else:
            scope = "TIER_A_NO_TRUTH_DETECTOR_ONLY"
    res = L.ss_residues(c)
    modelled = {x["key"]: x for x in res}
    n_mod = len(res)
    for arm in ("primary", "p4"):
        lab = L.pdp_labels(arm)[c]
        members = L.unit_members(lab)
        units = L.units_table(arm)
        call = L.calls_table(arm)[c]
        palm = int(call["palm_unit"]) if call["palm_unit"] else None
        # target unit
        if call["C4"] == "CALL":
            target, target_rule = palm, "PALM_LIKE_CALL"
        else:
            best = max(int(units[(c, u)]["max_strands_one_sheet"]) for u in members)
            tops = sorted(u for u in members if int(units[(c, u)]["max_strands_one_sheet"]) == best)
            target = tops[0] if len(tops) == 1 else None
            target_rule = ("MAX_SAME_SHEET_STRANDS" if len(tops) == 1 else
                           "TIED:" + ",".join(map(str, tops))) + f" (C4={call['C4']})"

        def place(resnums, kind):
            out = []
            for rn in resnums:
                key = (rn, "")
                st, u = L.residue_state(lab, key, modelled)
                aa = modelled[key]["resname"] if key in modelled else ""
                out.append((rn, st, u, aa))
                rrows.append(dict(chain=c, arm=arm, kind=kind, resnum=rn, resname=aa, residue_state=st,
                                  unit=u if u is not None else "", is_palm_unit="YES" if (u is not None and u == palm) else "NO",
                                  is_target_unit="YES" if (u is not None and u == target) else "NO", scope=scope))
            return out

        tp = place(truth, "truth")
        pp = place(pred, "detector_prediction")
        for kind, placed in (("truth", tp), ("pred", pp)):
            mod = [p for p in placed if p[1] != "NOT_MODELLED"]
            if mod:
                ok = sum(p[1] in ("IN_UNIT", "PDP_UNASSIGNED") for p in mod) / len(mod)
                if ok < JOIN_MIN:
                    k6.append((c, arm, kind, ok))
            if kind == "truth":
                for p in placed:
                    if p[1] != "NOT_MODELLED" and p[3] != "ASP":
                        k6.append((c, arm, "truth residue is not ASP: " + p[3], 0))

        def site_state(placed):
            if not placed:
                return "NO_RESIDUES", "", ""
            us = sorted({p[2] for p in placed if p[2] is not None})
            if any(p[1] != "IN_UNIT" for p in placed):
                return "PARTLY_OUTSIDE_UNITS:" + ";".join(p[1] for p in placed if p[1] != "IN_UNIT"), ",".join(map(str, us)), ""
            return ("ONE_UNIT" if len(us) == 1 else "SPLIT"), ",".join(map(str, us)), (us[0] if len(us) == 1 else "")

        t_state, t_units, t_unit = site_state(tp)
        p_state, p_units, _ = site_state(pp)
        tu = units.get((c, t_unit)) if t_unit != "" else None
        frac_target = (sum(1 for p in tp if p[2] is not None and p[2] == target) / len(tp)) if tp and target is not None else None
        role_of = {palm: "palm-like"} if palm else {}
        if call["thumb_unit"]:
            role_of[int(call["thumb_unit"])] = "thumb-like"
        if call["fingers_unit"]:
            role_of[int(call["fingers_unit"])] = "fingers-like"
        rows.append(dict(
            chain=c, arm=arm, biological_group=t1[c]["biological_group"], stratum=t1[c]["stratum"],
            implementation_sensitive=t1[c]["implementation_sensitive"],
            tier_3B=tier, scope_3C=scope, group_evidence_class_3B=tr["group_evidence_class"],
            truth_source_3B=tr["truth_source"],
            n_modelled=n_mod, n_units=len(members), C4_palm=call["C4"], palm_unit=palm or "",
            target_unit=target if target is not None else "", target_rule=target_rule,
            target_unit_n_res=len(members[target]) if target is not None else "",
            size_expected_fraction=(len(members[target]) / n_mod) if target is not None else None,
            truth_residues=",".join(map(str, truth)),
            truth_residue_units=";".join(f"{p[0]}:{p[2] if p[2] is not None else p[1]}" for p in tp),
            truth_site_state=t_state if tp else "",
            truth_site_unit=t_unit, truth_frac_in_target=frac_target,
            truth_site_in_palm_like=("YES" if (t_unit != "" and palm and t_unit == palm) else ("NO" if tp else "")),
            truth_site_unit_role=role_of.get(t_unit, "unclassified") if t_unit != "" else "",
            truth_site_unit_n_res=tu["n_res"] if tu else "", truth_site_unit_n_segments=tu["n_segments"] if tu else "",
            truth_site_unit_discontinuous=("YES" if tu and int(tu["n_segments"]) > 1 else ("NO" if tu else "")),
            truth_site_unit_frac_E=tu["frac_E"] if tu else "", truth_site_unit_frac_H=tu["frac_H"] if tu else "",
            truth_site_unit_max_strands_one_sheet=tu["max_strands_one_sheet"] if tu else "",
            truth_pair_carboxylate_A=tightest(c, truth[:2] if len(truth) == 2 else []) if tp else None,
            detector_verdict_3B=e["verdict"] if e else "", detector_outcome_3B=e["outcome"] if e else "",
            detector_prediction=",".join(map(str, pred)),
            detector_residue_units=";".join(f"{p[0]}:{p[2] if p[2] is not None else p[1]}" for p in pp),
            detector_site_state=p_state if pp else "", detector_site_units=p_units,
        ))

cols = list(rows[0])
L.write_tsv(os.path.join(L.S3C, "STRUCTURE_STAGE3B_CROSSWALK.tsv"), rows, cols)
L.write_tsv(os.path.join(L.TABLES, "A_residue_join.tsv"), rrows, list(rrows[0]))

from collections import Counter  # noqa: E402
prim = [r for r in rows if r["arm"] == "primary"]
print("scope:", dict(Counter(r["scope_3C"] for r in prim)))
print("K6 violations:", k6)
leak = [r for r in rows if r["scope_3C"].startswith("EXCLUDED") and (r["truth_residues"] or r["detector_prediction"])]
print("K3 leakage rows:", len(leak))
if k6 or leak:
    sys.exit("KILL K3/K6")
