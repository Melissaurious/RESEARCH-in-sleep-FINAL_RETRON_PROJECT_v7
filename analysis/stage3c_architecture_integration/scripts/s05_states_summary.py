#!/usr/bin/env python3
"""s3c_gB — ANALYSIS of the committed Comparison-B join (descriptive; no inferential test).

Reads STRUCTURE_STAGE2_CROSSWALK.tsv, tables/B_*.tsv and the frozen 3B tables. Family and lineage
metadata enter the analysis here for the first time; that transition is recorded in the report.

Writes tables/B_block_summary.tsv, B_block_by_lineage.tsv, B_split_merge.tsv,
B_sensitivity.tsv, B_unavailable_cases.tsv, B_cat262_vs_3B_truth.tsv.
"""
import collections
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3clib as L  # noqa: E402

X = L.read_tsv(os.path.join(L.S3C, "STRUCTURE_STAGE2_CROSSWALK.tsv"))
MEM = L.read_tsv(os.path.join(L.TABLES, "B_unit_block_membership.tsv"))
RES = L.read_tsv(os.path.join(L.TABLES, "B_state_residue_join.tsv"))
reg = L.register()
BLOCK_ORDER = ["RT0_none", "RT1_none", "SB2p", "SB3", "SB4", "SB56", "SB7", "CAT262"]

# ---------------------------------------------------------------- per block, per stratum
rows = []
for arm in ("primary", "p4"):
    for block in BLOCK_ORDER:
        B = [r for r in X if r["arm"] == arm and r["block"] == block]
        for stratum in ("all", "primary", "flagged"):
            S = B if stratum == "all" else [r for r in B if r["stratum"] == stratum]
            n = len(S)
            av = [r for r in S if r["available"] == "YES"]
            cont = [r for r in av if r["containment"] == "CONTAINED"]
            groups = {r["biological_group"] for r in S}
            roles = collections.Counter(r["modal_unit_role"] for r in cont)
            byg = collections.defaultdict(set)
            for r in S:
                byg[r["biological_group"]].add(r["containment"])
            rows.append(dict(
                arm=arm, block=block, stratum=stratum,
                historical_label_LtrA_local=S[0]["historical_label_LtrA_local"], stage2_status=S[0]["stage2_status"],
                n_chains=n, n_groups=len(groups),
                n_available=len(av), frac_available=len(av) / n if n else None,
                n_groups_with_any_available=len({r["biological_group"] for r in av}),
                n_contained=len(cont), frac_contained_of_available=len(cont) / len(av) if av else None,
                n_split=sum(r["containment"] == "SPLIT" for r in av),
                n_no_residue_in_unit=sum(r["containment"] == "AVAILABLE_BUT_NO_RESIDUE_IN_A_UNIT" for r in av),
                modal_unit_role_counts=";".join(f"{k}={v}" for k, v in sorted(roles.items())) or "-",
                frac_contained_in_palm_like=(roles.get("palm-like", 0) / len(cont)) if cont else None,
                n_discontinuous_modal_unit=sum(r["modal_unit_discontinuous"] == "YES" for r in cont),
                median_units_holding=statistics.median([int(r["n_units_holding"]) for r in av]) if av else None,
                groups_uniform_containment=sum(1 for g, v in byg.items() if len(v) == 1), n_groups_counted=len(byg),
                unit="chain", denominator_meaning=f"{n} chains in stratum {stratum}"))
L.write_tsv(os.path.join(L.TABLES, "B_block_summary.tsv"), rows, list(rows[0]))

# ---------------------------------------------------------------- lineage / family strata
lin = []
for block in BLOCK_ORDER:
    B = [r for r in X if r["arm"] == "primary" and r["block"] == block]
    byl = collections.defaultdict(list)
    for r in B:
        byl[reg[r["chain"]]["lineage_METADATA_ONLY"]].append(r)
        if "Retron" in reg[r["chain"]]["family_METADATA_ONLY"]:
            byl["bacterial:retron"].append(r)
    for k in sorted(byl):
        S = byl[k]
        av = [r for r in S if r["available"] == "YES"]
        cont = [r for r in av if r["containment"] == "CONTAINED"]
        mf = [float(r["mapped_fraction"]) for r in S if r["mapped_fraction"]]
        lin.append(dict(block=block, stratum_METADATA=k, n_chains=len(S),
                        n_groups=len({r["biological_group"] for r in S}),
                        median_mapper_mapped_fraction=statistics.median(mf) if mf else None,
                        n_available=len(av), frac_available=len(av) / len(S),
                        n_contained=len(cont), frac_contained_of_available=len(cont) / len(av) if av else None,
                        modal_unit_roles=";".join(f"{k2}={v}" for k2, v in sorted(
                            collections.Counter(r["modal_unit_role"] for r in cont).items())) or "-",
                        unit="chain",
                        note="metadata stratum; the mapper frame is GII-centred, a confound for every between-family comparison"))
L.write_tsv(os.path.join(L.TABLES, "B_block_by_lineage.tsv"), lin, list(lin[0]))

# ---------------------------------------------------------------- split and merge
contained_lookup = {(r["arm"], r["chain"], r["block"]): r["containment"] for r in X}
sm = []
for arm in ("primary", "p4"):
    M = [r for r in MEM if r["arm"] == arm]
    merged = [r for r in M if r["merge"] == "MERGE"]
    chains_all = sorted({r["chain"] for r in M})
    sm.append(dict(measure="units_holding_2_or_more_blocks", arm=arm, numerator=len(merged),
                   denominator=len(M), value=len(merged) / len(M), unit="PDP unit",
                   detail=f"{len({r['chain'] for r in merged})} chains have at least one such unit"))
    pair = collections.Counter()
    for r in merged:
        bl = [b for b in r["blocks_contained"].split(",") if b]
        for i in range(len(bl)):
            for j in range(i + 1, len(bl)):
                pair[tuple(sorted((bl[i], bl[j])))] += 1
    for (a, b), k in sorted(pair.items(), key=lambda x: -x[1]):
        both = sum(1 for c in chains_all
                   if contained_lookup.get((arm, c, a)) == "CONTAINED"
                   and contained_lookup.get((arm, c, b)) == "CONTAINED")
        sm.append(dict(measure=f"blocks_in_same_unit:{a}+{b}", arm=arm, numerator=k, denominator=both,
                       value=k / both if both else None, unit="chain",
                       detail="denominator = chains where both blocks are CONTAINED somewhere"))
    for block in BLOCK_ORDER:
        S = [r for r in X if r["arm"] == arm and r["block"] == block and r["available"] == "YES"]
        spl = [r for r in S if r["containment"] == "SPLIT"]
        if S:
            sm.append(dict(measure=f"block_split_across_units:{block}", arm=arm, numerator=len(spl),
                           denominator=len(S), value=len(spl) / len(S), unit="chain",
                           detail=("units holding >=0.20: " + ";".join(sorted({r["units_holding"] for r in spl}))) if spl else "-"))
L.write_tsv(os.path.join(L.TABLES, "B_split_merge.tsv"), sm,
            ["measure", "arm", "numerator", "denominator", "value", "unit", "detail"])

# ---------------------------------------------------------------- threshold sensitivity
sens = []
for block in BLOCK_ORDER:
    if block.startswith("RT"):
        continue
    B = [r for r in X if r["arm"] == "primary" and r["block"] == block]
    for a_min in (0.30, 0.50, 0.70):
        av = [r for r in B if r["frac_mapped"] and float(r["frac_mapped"]) >= a_min]
        for c_min in (0.70, 0.80, 0.90):
            cont = [r for r in av if r["modal_unit_frac"] and float(r["modal_unit_frac"]) >= c_min]
            sens.append(dict(block=block, availability_min=a_min, containment_min=c_min,
                             n_chains=len(B), n_available=len(av), n_contained=len(cont),
                             frac_available=len(av) / len(B),
                             frac_contained_of_available=len(cont) / len(av) if av else None,
                             declared="YES" if (a_min == 0.50 and c_min == 0.80) else "NO", unit="chain"))
L.write_tsv(os.path.join(L.TABLES, "B_sensitivity.tsv"), sens, list(sens[0]))

# ---------------------------------------------------------------- unavailable cases, named
un = []
for r in X:
    if r["arm"] != "primary" or r["block"].startswith("RT") or r["available"] == "YES":
        continue
    un.append(dict(chain=r["chain"], biological_group=r["biological_group"],
                   family_METADATA=reg[r["chain"]]["family_METADATA_ONLY"], block=r["block"],
                   mapper_verdict=r["mapper_verdict"], mapped_fraction=r["mapped_fraction"],
                   n_mapped=r["n_mapped"], block_states=r["block_states"], frac_mapped=r["frac_mapped"],
                   reason=("mapper rejected the input" if r["mapper_verdict"].startswith("INPUT_INVALID")
                           else "mapper ABSTAIN on the whole sequence" if r["mapper_verdict"] == "ABSTAIN"
                           else "fewer than half the block's states are MAPPED in this chain"),
                   note="NOT an absence claim: a DELETED or UNSUPPORTED state is a statement about the alignment path"))
L.write_tsv(os.path.join(L.TABLES, "B_unavailable_cases.tsv"), un, list(un[0]))

# ------------------------------------- CAT_STATE 262 vs independent 3B catalytic truth ----------
A = {r["chain"]: r for r in L.read_tsv(os.path.join(L.S3C, "STRUCTURE_STAGE3B_CROSSWALK.tsv")) if r["arm"] == "primary"}
res_cat = {r["chain"]: r for r in RES if r["block"] == "CAT262"}
cat = []
for r in X:
    if r["arm"] != "primary" or r["block"] != "CAT262":
        continue
    c = r["chain"]
    a = A[c]
    if a["scope_3C"] != "IN_SCOPE_OWN_CHAIN_TRUTH":
        continue
    rr = res_cat.get(c)
    catnum = int(rr["resnum"]) if rr and rr["resnum"] else None
    truth = [int(x) for x in a["truth_residues"].split(",") if x]
    d = min((abs(catnum - t) for t in truth), default=None) if catnum else None
    cat.append(dict(chain=c, biological_group=r["biological_group"], cat_call_state=rr["call_state"] if rr else "",
                    cat_residue=catnum if catnum else "", cat_amino_acid=rr["amino_acid"] if rr else "",
                    cat_unit=r["modal_unit"], truth_residues=a["truth_residues"], truth_site_unit=a["truth_site_unit"],
                    residue_offset_to_nearest_truth_Asp=d,
                    same_unit_as_truth="YES" if (r["modal_unit"] and r["modal_unit"] == a["truth_site_unit"]) else "NO",
                    unit="chain",
                    note="two independent instruments: a sequence-HMM state vs structure-based metal/substrate/author truth"))
L.write_tsv(os.path.join(L.TABLES, "B_cat262_vs_3B_truth.tsv"), cat, list(cat[0]))

same = sum(x["same_unit_as_truth"] == "YES" for x in cat)
off = [x["residue_offset_to_nearest_truth_Asp"] for x in cat if x["residue_offset_to_nearest_truth_Asp"] is not None]
print(f"CAT262 vs 3B truth: same unit {same}/{len(cat)}; offsets {sorted(collections.Counter(off).items())}")
for r in rows:
    if r["arm"] == "primary" and r["stratum"] == "all":
        print(f"{r['block']:9} avail {r['n_available']:2}/{r['n_chains']} contained {r['n_contained']:2} "
              f"split {r['n_split']:2} roles {r['modal_unit_role_counts']}")
