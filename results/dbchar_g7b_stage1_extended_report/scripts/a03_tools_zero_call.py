#!/usr/bin/env python3
"""a03 - sections 6, 7 and the tool-coupled parts of 4 and 13.

Tool-call combinations and ncRNA carriage at four units; the zero-call structure of Retron loci;
carriage against upstream context, subtype and RT length; and the reconciliation of the old
report's headline geometry/detection numbers against the canonical Stage-1 definitions.

⛔ Carriage is NOT read as biology here. The PADLOC rule table (t22) is landed beside it because
the ncRNA is a scoring element of the detector's own rule for most retron subtypes.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

import common as C

SCRIPT = "a03_tools_zero_call.py"


def subtype_rows(loci: pd.DataFrame, col: str, tool: str) -> pd.DataFrame:
    """Carriage per subtype label of one tool. A locus carrying two labels of one tool (the '||'
    case) is counted under each - stated in the denominator."""
    s = loci[[col, "n_canonical"]].dropna(subset=[col])
    s = s.assign(label=s[col].str.split(r"\|+")).explode("label")
    g = s.groupby("label").agg(n_loci=("label", "size"),
                               n_with_ncrna=("n_canonical", lambda v: int((v > 0).sum())))
    g = C.add_rate(g.reset_index(), "n_with_ncrna", "n_loci", "pct_with_ncrna")
    g["tool"] = tool
    return g.sort_values("n_loci", ascending=False)


def padloc_rules() -> pd.DataFrame:
    rows = []
    for f in sorted(C.PADLOC_SYS.glob("retron_*.yaml")):
        txt = f.read_text()

        def block(name):
            m = re.search(rf"{name}:\s*((?:\s*-\s*\S+\n?)+)", txt)
            return [x.strip("- \n") for x in m.group(1).strip().splitlines()] if m else []

        def scalar(name):
            m = re.search(rf"{name}:\s*(\S+)", txt)
            return m.group(1) if m else ""
        core, sec, pro = block("core_genes"), block("secondary_genes"), block("prohibited_genes")
        min_core, min_total = int(scalar("minimum_core")), int(scalar("minimum_total"))
        if "ncRNA" in pro:
            role = "PROHIBITED - a call requires the ncRNA to be absent"
        elif "ncRNA" in sec and min_total > min_core and len(sec) == 1:
            role = "REQUIRED IN PRACTICE - min_total exceeds min_core and the ncRNA is the only secondary gene"
        elif "ncRNA" in sec:
            role = "SECONDARY - scores towards min_total, not required"
        else:
            role = "ABSENT from the rule"
        rows.append(dict(padloc_subtype=f.stem, ncrna_role=role, minimum_core=min_core,
                         minimum_total=min_total, core_genes="|".join(core),
                         secondary_genes="|".join(sec), prohibited_genes="|".join(pro),
                         maximum_separation=int(scalar("maximum_separation"))))
    return pd.DataFrame(rows).sort_values("padloc_subtype")


def main() -> None:
    C.log("== a03 sections 6-7")
    loci = C.physical_retron_loci()
    tc = C.derived("rt_tool_calls_v1", ["record_key", "locus_key", "rt_seq_hash", "file_label",
                                        "by_myRT", "by_PADLOC", "by_DefenseFinder", "n_ncrna"])
    tcr = tc[tc.file_label == "Retron"].copy()
    tcr["combo"] = C.combo_name(tcr)
    pairs = C.derived("rt_ncrna_pairs_v1", ["physical_locus_key", "locus_key", "rt_seq_hash",
                                            "nc_seq_hash", "detection_model", "canonical",
                                            "file_label", "direction", "signed_distance_bp",
                                            "n_cds_between", "same_strand", "source_database"])
    can = pairs[pairs.canonical]
    rec = C.records()

    # ================================================================ t18 combos at four units
    loci["has_ncrna"] = loci.n_canonical > 0
    rows = []
    rec_can_loci = set(can.locus_key)
    for combo, g in tcr.groupby("combo"):
        rows.append(dict(view_unit="distinct record", combo=combo, n=len(g),
                         n_with_ncrna=int((g.n_ncrna > 0).sum())))
        lo = g.groupby("locus_key").n_ncrna.max()
        rows.append(dict(view_unit="locus (union of its records' tools)", combo=combo, n=len(lo),
                         n_with_ncrna=int(lo.gt(0).sum())))
    for combo, g in loci.groupby("combo"):
        rows.append(dict(view_unit="physical locus (union of its records' tools)", combo=combo,
                         n=len(g), n_with_ncrna=int(g.has_ncrna.sum())))
        ex = g.groupby("rt_seq_hash").has_ncrna.max()
        rows.append(dict(view_unit="exact RT (non-exclusive across combinations)", combo=combo,
                         n=len(ex), n_with_ncrna=int(ex.sum())))
    t18 = C.add_rate(pd.DataFrame(rows), "n_with_ncrna", "n", "pct_with_ncrna")
    t18["combo_n_tools"] = t18.combo.str.count(r"\|") + 1
    t18 = t18.sort_values(["view_unit", "n"], ascending=[True, False])
    C.write_table("t18_tool_combination_carriage", t18,
                  "the unit named in view_unit (Retron family label)",
                  "units of that tool combination; carriage = >=1 CANONICAL ncRNA placement "
                  "(record unit: >=1 ncRNA call in the record). Exact RTs are NOT exclusive "
                  "between combinations: one protein can occur at loci called by different tools",
                  SCRIPT, estimate="census; Wilson 95% interval on the rate")

    dis = pd.DataFrame([dict(
        measure="Retron physical loci whose records disagree on the tool combination",
        n=int((loci.n_combos > 1).sum()), n_total=len(loci),
        pct=100 * float((loci.n_combos > 1).mean()))])
    C.write_table("t18_combo_disagreement", dis, "physical loci",
                  "Retron physical loci (563,701)", SCRIPT)

    # ================================================================ t20 combo x PADLOC subtype
    s = loci[["combo", "padloc_subtype", "has_ncrna"]].dropna(subset=["padloc_subtype"])
    s = s.assign(label=s.padloc_subtype.str.split(r"\|+")).explode("label")
    m = s.groupby(["combo", "label"]).agg(n_loci=("has_ncrna", "size"),
                                          n_with_ncrna=("has_ncrna", "sum")).reset_index()
    m = C.add_rate(m, "n_with_ncrna", "n_loci", "pct_with_ncrna")
    m["masked_small_n"] = m.n_loci < C.MIN_N_RATE
    C.write_table("t20_combo_by_padloc_subtype", m.sort_values(["combo", "n_loci"],
                                                               ascending=[True, False]),
                  "physical loci", "Retron physical loci of that (tool combination, PADLOC subtype); "
                  "rates on fewer than 30 loci are flagged masked_small_n",
                  SCRIPT, estimate="census; Wilson 95% interval on the rate")

    # ================================================================ t21 carriage by subtype
    t21 = pd.concat([subtype_rows(loci, "padloc_subtype", "PADLOC"),
                     subtype_rows(loci, "defensefinder_subtype", "DefenseFinder")],
                    ignore_index=True)
    rules = padloc_rules()
    t21 = t21.merge(rules[["padloc_subtype", "ncrna_role"]], left_on="label",
                    right_on="padloc_subtype", how="left").drop(columns="padloc_subtype")
    t21["ncrna_role"] = t21.ncrna_role.fillna("n/a - DefenseFinder models carry no ncRNA element")
    C.write_table("t21_carriage_by_subtype", t21, "physical loci",
                  "Retron physical loci carrying that tool's subtype label; a locus whose "
                  "records carry two labels of one tool is counted under each label",
                  SCRIPT, estimate="census; Wilson 95% interval on the rate")
    C.write_table("t22_padloc_rules", rules, "PADLOC system rules",
                  "n/a - describes the detector's own rule files, not the corpus", SCRIPT,
                  estimate="n/a - rule text")

    cmm = pd.read_csv(C.PADLOC_CM_META, sep="\t")
    cmm = cmm.rename(columns={c: c.replace(".", "_") for c in cmm.columns})
    C.write_table("t22_cm_meta", cmm, "covariance models",
                  "n/a - describes the detector's CM library, not the corpus", SCRIPT,
                  estimate="n/a - model metadata")

    # ================================================================ t11 subtype x CM
    lab = loci[["physical_locus_key", "padloc_subtype", "defensefinder_subtype"]].copy()
    cm = can[["physical_locus_key", "detection_model"]].drop_duplicates()
    j = lab.merge(cm, on="physical_locus_key", how="left")
    out = []
    for tool, col in (("PADLOC", "padloc_subtype"), ("DefenseFinder", "defensefinder_subtype")):
        k = j.dropna(subset=[col]).copy()
        k = k.assign(label=k[col].str.split(r"\|+")).explode("label")
        tot = k.groupby("label").physical_locus_key.nunique().rename("n_loci")
        cnt = (k.dropna(subset=["detection_model"]).groupby(["label", "detection_model"])
               .physical_locus_key.nunique().rename("n_loci_with_model").reset_index())
        cnt = cnt.merge(tot, left_on="label", right_index=True)
        cnt["pct_of_subtype_loci"] = 100 * cnt.n_loci_with_model / cnt.n_loci
        cnt["tool"] = tool
        out.append(cnt)
    C.write_table("t11_subtype_by_model", pd.concat(out, ignore_index=True).sort_values(
        ["tool", "n_loci", "n_loci_with_model"], ascending=[True, False, False]),
        "physical loci", "Retron physical loci carrying that tool's subtype label", SCRIPT)

    # ================================================================ t23 zero-call structure
    rows = []
    for db, g in loci.groupby("source_database_set"):
        b = g.n_canonical_seqs.clip(upper=3)
        rows.append(dict(source_database_set=db, n_loci=len(g),
                         n_0=int((b == 0).sum()), n_1=int((b == 1).sum()),
                         n_2=int((b == 2).sum()), n_gt2=int((b == 3).sum()),
                         pct_zero=100 * float((b == 0).mean()),
                         n_loci_with_2plus_placements=int((g.n_canonical > 1).sum())))
    t23 = pd.DataFrame(rows).sort_values("n_loci", ascending=False)
    t23 = C.add_rate(t23, "n_0", "n_loci", "pct_zero_ci")
    C.write_table("t23_zero_call_by_database", t23, "physical loci",
                  "Retron physical loci whose records carry that set of source databases; the "
                  "0/1/2/>2 classes count DISTINCT exact ncRNA sequences at the locus, not "
                  "placements (a locus deposited in two databases carries the same call twice; "
                  "n_loci_with_2plus_placements counts those)",
                  SCRIPT, estimate="census; Wilson 95% interval on the zero rate")

    # the same for non-Retron families, at locus grain, so the detector-scope statement is visible
    fam = C.derived("rt_loci_v1", ["locus_key", "family_label_set", "physical_locus_key"])
    hits = can.groupby("locus_key").size().rename("n_can")
    fam = fam.merge(hits, left_on="locus_key", right_index=True, how="left")
    fam["n_can"] = fam.n_can.fillna(0)
    z = fam.groupby("family_label_set").agg(n_loci=("locus_key", "size"),
                                            n_with_call=("n_can", lambda v: int((v > 0).sum()))
                                            ).reset_index()
    z["pct_zero"] = 100 * (1 - z.n_with_call / z.n_loci)
    z = z.sort_values("n_loci", ascending=False)
    C.write_table("t23_zero_call_by_family", z, "loci",
                  "loci carrying that family label set; a call is a CANONICAL placement. "
                  "Outside Retron this measures detector scope, never biological absence", SCRIPT)

    # ================================================================ t24 upstream context
    repcols = ["record_key", "win_start", "win_end", "rt_start", "rt_end", "rt_strand",
               "true_start_clipped", "clipped_end_flag", "elig_geometry", "rt_aa_len"]
    r = rec[repcols].set_index("record_key")
    L = loci.merge(r, left_on="representative_record_key", right_index=True, how="left")
    L = L[L.elig_geometry.fillna(False)]
    plus = L.rt_strand.to_numpy() == "+"
    up_bp = np.where(plus, L.rt_start - L.win_start, L.win_end - L.rt_end)
    # the clipped flag that matters is the one on the UPSTREAM side in transcription frame
    up_clipped = np.where(plus, L.true_start_clipped.to_numpy(), L.clipped_end_flag.to_numpy())
    L = L.assign(upstream_context_bp=np.clip(up_bp, 0, None), upstream_side_clipped=up_clipped)
    bins = [-1, 0, 200, 500, 1000, 2000, 5000, 9000, 10**9]
    labels = ["0", "1-200", "201-500", "501-1,000", "1,001-2,000", "2,001-5,000", "5,001-9,000",
              ">9,000"]
    L["context_bin"] = pd.cut(L.upstream_context_bp, bins=bins, labels=labels)
    rows = []
    for (b, clipped), g in L.groupby(["context_bin", "upstream_side_clipped"], observed=True):
        rows.append(dict(upstream_context_bin=b, upstream_side_clipped=bool(clipped),
                         n_loci=len(g), n_with_ncrna=int(g.has_ncrna.sum())))
    t24 = C.add_rate(pd.DataFrame(rows), "n_with_ncrna", "n_loci", "pct_with_ncrna")
    C.write_table("t24_carriage_by_upstream_context", t24, "physical loci",
                  "geometry-eligible Retron physical loci in that bin of upstream window context "
                  "(bp between the RT gene and the upstream window edge, transcription-relative; "
                  "upstream_side_clipped is the contig-clipping flag of that same side)",
                  SCRIPT, estimate="census; Wilson 95% interval on the rate")

    # ================================================================ t25 carriage vs RT length
    fb = C.derived("rt_family_baseline_v1", ["rt_seq_hash", "rt_aa_len", "completeness_class",
                                             "family_label", "view"])
    fbr = fb[(fb.family_label == "Retron") & (fb.view == "V-RT-SINGLE")]
    exl = loci.groupby("rt_seq_hash").has_ncrna.max().rename("has_ncrna").reset_index()
    exl = exl.merge(fbr, on="rt_seq_hash", how="inner")
    edges = [0, 200, 250, 300, 350, 400, 500, 700, 10**9]
    labs = ["<200", "200-249", "250-299", "300-349", "350-399", "400-499", "500-699", ">=700"]
    exl["length_bin"] = pd.cut(exl.rt_aa_len, bins=edges, labels=labs, right=False)
    rows = []
    for (b, comp), g in exl.groupby(["length_bin", "completeness_class"], observed=True):
        rows.append(dict(length_bin=b, completeness_class=comp, n_exact_rt=len(g),
                         n_with_ncrna=int(g.has_ncrna.sum())))
    t25 = C.add_rate(pd.DataFrame(rows), "n_with_ncrna", "n_exact_rt", "pct_with_ncrna")
    C.write_table("t25_carriage_by_rt_length", t25, "exact RT sequences",
                  "Retron-labelled V-RT-SINGLE exact RTs of that length bin and completeness class "
                  "that occur at >=1 physical locus", SCRIPT,
                  estimate="census; Wilson 95% interval on the rate")

    # ================================================================ t26 per-database annotation
    rows = []
    for db, g in loci.groupby("source_database_set"):
        for combo, h in g.groupby("combo"):
            rows.append(dict(source_database_set=db, combo=combo, n_loci=len(h),
                             n_with_ncrna=int(h.has_ncrna.sum()), n_loci_db=len(g)))
    t26 = C.add_rate(pd.DataFrame(rows), "n_with_ncrna", "n_loci", "pct_with_ncrna")
    t26["pct_of_database_loci"] = 100 * t26.n_loci / t26.n_loci_db
    C.write_table("t26_tool_mix_by_database", t26.sort_values(["n_loci_db", "n_loci"],
                                                             ascending=False),
                  "physical loci", "Retron physical loci of that source-database set and tool "
                  "combination", SCRIPT, estimate="census; Wilson 95% interval on the rate")

    # ================================================================ t27 old-report reconciliation
    canr = can[can.file_label == "Retron"]
    lo_dir = canr.groupby("physical_locus_key").direction.first()
    pl_up = 100 * float(lo_dir.eq("upstream").mean())
    plc = canr.groupby("physical_locus_key").n_cds_between.min()
    one_cds = 100 * float(plc.eq(1).mean())
    zero_cds = 100 * float(plc.eq(0).mean())
    # retron_V, as PADLOC labels it
    v = loci[loci.padloc_subtype.fillna("").str.contains("retron_V")]
    vpl = canr[canr.physical_locus_key.isin(set(v.physical_locus_key))]
    v_dn = 100 * float(vpl.groupby("physical_locus_key").direction.first().eq("downstream").mean())
    prof = C.landed("dbchar_g3_pair_geometry", "g3_downstream_mode_profile.tsv")
    med_dn = float(prof.loc[prof.measure == "median_signed_distance_bp", "value"].iloc[0])
    v_tech = 100 * float(vpl[vpl.direction.eq("downstream")].signed_distance_bp.between(
        med_dn - C.TECH_MODE_HALF_WIDTH, med_dn + C.TECH_MODE_HALF_WIDTH).mean())
    t18p = t18[t18.view_unit.str.startswith("physical locus")].set_index("combo")
    rows = [
        dict(old_report_claim="ncRNA is upstream of the RT in 73.7% of Retron placements",
             old_value="73.71%", canonical_value=f"{pl_up:.2f}%",
             canonical_unit="Retron physical loci with a CANONICAL placement",
             reading="different denominator and direction rule: the old figure splits "
                     "'upstream' from 'adjacent', which the coordinate rule does not"),
        dict(old_report_claim="43.5% are separated by exactly one intervening CDS "
                              "(the 'effector slot')",
             old_value="43.50%", canonical_value=f"{one_cds:.2f}%",
             canonical_unit="Retron physical loci with a CANONICAL placement",
             reading=f"definitional: the old count used gene-order offsets, the canonical rule "
                     f"counts CDS lying WHOLLY in the gap; {zero_cds:.2f}% have none. Not a "
                     f"correction of arithmetic - the two measure different things"),
        dict(old_report_claim="retron_V is structurally distinct: ncRNA downstream in 67.4% of "
                              "cases, a fixed architectural inversion",
             old_value="67.40%", canonical_value=f"{v_dn:.2f}%",
             canonical_unit="PADLOC retron_V-labelled Retron physical loci with a CANONICAL placement",
             reading=f"technical: {v_tech:.2f}% of those downstream placements fall in the "
                     f"contig-start-clipped mode g3 identified, where the RT sits at the window's "
                     f"left edge and any call is forced downstream"),
        dict(old_report_claim="PADLOC|myRT anomaly: 88.7% ncRNA rate, above 3-tool agreement",
             old_value="88.70%",
             canonical_value=f"{t18p.loc['myRT|PADLOC', 'pct_with_ncrna']:.2f}%",
             canonical_unit="Retron physical loci of that tool combination",
             reading="reproduced at a different unit; §6 shows it is not a confidence gradient - "
                     "carriage tracks the PADLOC subtype composition, and the ncRNA is a scoring "
                     "element of PADLOC's own rule"),
        dict(old_report_claim="Retron_XII is a confirmed CM-model gap (0.0065% ncRNA rate)",
             old_value="0.0065%",
             canonical_value=f"{t21[(t21.tool == 'PADLOC') & (t21.label == 'retron_XII')].pct_with_ncrna.iloc[0]:.2f}%",
             canonical_unit="PADLOC retron_XII-labelled Retron physical loci",
             reading="definitional: PADLOC's retron_XII rule lists the ncRNA as a PROHIBITED gene, "
                     "so a retron_XII call cannot coexist with an ncRNA hit in that rule"),
    ]
    C.write_table("t27_old_report_reconciliation", pd.DataFrame(rows),
                  "as named in canonical_unit",
                  "n/a - a comparison of the old report's published values with canonical Stage-1 "
                  "re-derivations; the old numbers are quoted, never reused", SCRIPT)


if __name__ == "__main__":
    main()
