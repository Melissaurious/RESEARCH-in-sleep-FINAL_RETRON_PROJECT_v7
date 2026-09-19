#!/usr/bin/env python3
"""s3c_gE — termini, insertions, fusions and extra units, from the experimental register only.

No catalogue-wide scan (LAUNCHER_03C section 3). The frozen mapper's anchor span defines the RT
core operationally; residues outside it are extensions, never "extra domains" by assertion.

Internal insertion (DECLARED): between two consecutive MAPPED anchor states, observed residue
spacing exceeding the LtrA spacing of the same two states by >= 20 residues. This measure is BLIND
inside regions where the anchors are DELETED, so the instrument's own insertion-run counts are
carried beside it.

CAUTION, load-bearing: residues outside the mapped anchor span are only a TERMINAL EXTENSION when
the instrument actually reached both ends of the anchor series. Where the series is truncated (the
GII-centred frame does not commit on the N-terminal anchors of, e.g., retron RTs), those residues
are unseen RT sequence, not extension. Such chains are flagged ANCHOR_SERIES_TRUNCATED and their
extension counts are not interpretable as architecture.

Writes TERMINI_FUSION_SUMMARY.tsv, tables/E_insertions.tsv, tables/E_architecture_vs_calls.tsv.
"""
import collections
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3clib as L  # noqa: E402

INSERTION_MIN = 20     # DECLARED
EXCESS_REPORT_MIN = 5  # DECLARED: gaps this large are listed even when below INSERTION_MIN
FIRST_STATE_MAX = 115  # DECLARED: anchor series counted as reaching the N-terminal end at/below this state
LAST_STATE_MIN = 310   # DECLARED: ... and the C-terminal end at/above this state (anchors run 107-317)

# accessions that are expression-construct partners, not biology. Declared, and only for
# accessions whose identity is independently known; everything else stays UNCLASSIFIED.
EXPRESSION_PARTNER = {"P0AEX9": "E. coli maltose-binding protein (malE) - expression fusion"}

states = collections.defaultdict(dict)
for r in L.read_tsv(os.path.join(L.TABLES, "mapper", "s3c.states.tsv")):
    states[r["sequence_id"]][int(r["state_id"])] = r
seqsum = {r["sequence_id"]: r for r in L.read_tsv(os.path.join(L.TABLES, "mapper", "s3c.sequences.tsv"))}
imap = collections.defaultdict(dict)
for r in L.read_tsv(os.path.join(L.TABLES, "chain_index_map.tsv")):
    imap[r["chain"]][int(r["seq_index"])] = (int(r["resnum"]), r["icode"])
ltra = {int(r["state_id"]): int(r["ltra_residue"]) for r in L.read_tsv(os.path.join(L.STAGE2, "g7a_state_to_residue.tsv"))
        if r["call_state"] == "MAPPED"}

reg = L.register()
t1 = L.t1()
calls = L.calls_table("primary")
units_t = L.units_table("primary")
labs = L.pdp_labels("primary")

rows, ins_rows = [], []
for c in L.chains():
    r = reg[c]
    res = L.ss_residues(c)
    n_mod = len(res)
    idx_of = {x["key"]: i for i, x in enumerate(res)}
    mapped = sorted((int(s["sequence_residue_index"]), sid) for sid, s in states.get(c, {}).items()
                    if s["call_state"] == "MAPPED")
    if mapped:
        first_i, last_i = mapped[0][0], mapped[-1][0]
        first_key, last_key = imap[c][first_i], imap[c][last_i]
        n_nterm, n_cterm = first_i - 1, n_mod - last_i
        core_span = f"{first_key[0]}-{last_key[0]}"
        first_state, last_state = mapped[0][1], mapped[-1][1]
        full = first_state <= FIRST_STATE_MAX and last_state >= LAST_STATE_MIN
        span_states = f"{first_state}-{last_state}"
        coverage = ("ANCHOR_SERIES_REACHED_BOTH_ENDS" if full else
                    "ANCHOR_SERIES_TRUNCATED - residues outside the span are unseen RT sequence, "
                    "NOT a measured extension")
        # internal insertions between consecutive mapped anchors
        for (ia, sa), (ib, sb) in zip(mapped, mapped[1:]):
            if sa not in ltra or sb not in ltra:
                continue
            obs, exp = ib - ia - 1, ltra[sb] - ltra[sa] - 1
            if obs - exp >= EXCESS_REPORT_MIN:
                ins_rows.append(dict(chain=c, biological_group=t1[c]["biological_group"],
                                     family_METADATA=r["family_METADATA_ONLY"], after_state=sa, before_state=sb,
                                     resnum_start=imap[c][ia][0], resnum_end=imap[c][ib][0],
                                     observed_gap_residues=obs, ltra_gap_residues=exp, excess_residues=obs - exp,
                                     units_spanned=",".join(map(str, sorted({labs[c].get(x["key"], 0) for x in res[ia:ib - 1]} - {0}))),
                                     meets_declared_threshold="YES" if obs - exp >= INSERTION_MIN else "NO",
                                     unit="internal insertion",
                                     note="an insertion relative to the LtrA frame of the frozen instrument, not a domain call"))
    else:
        first_i = last_i = None
        n_nterm = n_cterm = ""
        core_span = span_states = ""
        coverage = "NO_MAPPED_ANCHOR (mapper ABSTAIN or INPUT_INVALID)"
    # units wholly outside the mapped core
    out_units = []
    for u, keys in sorted(L.unit_members(labs[c]).items()):
        ii = sorted(idx_of[k] for k in keys)
        if first_i is None:
            continue
        if ii[-1] + 1 < first_i:
            out_units.append(f"{u}:N_TERMINAL")
        elif ii[0] + 1 > last_i:
            out_units.append(f"{u}:C_TERMINAL")
    extra = [u for (ch, u), ur in units_t.items() if ch == c and ur["EXTRA_DOMAIN"] == "1"]
    accs = [a for a in r["external_accessions"].split(";") if a and a != "NONE"]
    expr = [f"{a} = {EXPRESSION_PARTNER[a]}" for a in accs if a in EXPRESSION_PARTNER]
    rows.append(dict(
        chain=c, biological_group=t1[c]["biological_group"], family_METADATA=r["family_METADATA_ONLY"],
        lineage_METADATA=r["lineage_METADATA_ONLY"], stratum=t1[c]["stratum"],
        n_modelled=n_mod, construct_len=r["construct_len"], n_missing_nterm=r["n_missing_nterm"],
        n_missing_cterm=r["n_missing_cterm"], n_internal_gaps=r["n_internal_gaps"],
        mapper_verdict=seqsum[c]["verdict"] if c in seqsum else "INPUT_INVALID",
        rt_core_span_author_numbering=core_span, mapped_anchor_state_span=span_states,
        anchor_series_coverage=coverage,
        n_nterm_extension_residues=n_nterm, n_cterm_extension_residues=n_cterm,
        frac_outside_rt_core=((n_nterm + n_cterm) / n_mod) if mapped else None,
        n_internal_insertions=sum(1 for x in ins_rows if x["chain"] == c and x["meets_declared_threshold"] == "YES"),
        max_gap_excess_residues=max([x["excess_residues"] for x in ins_rows if x["chain"] == c], default=0),
        mapper_n_insertion_runs=seqsum[c]["n_insertion_runs"] if c in seqsum else "",
        mapper_total_inserted_residues=seqsum[c]["total_inserted_residues"] if c in seqsum else "",
        mapper_max_insertion_run=seqsum[c]["max_insertion_run"] if c in seqsum else "",
        n_units=len(L.unit_members(labs[c])),
        units_outside_core=";".join(out_units) or "-", n_units_outside_core=len(out_units),
        n_extra_domain_units=len(extra), extra_domain_units=",".join(map(str, sorted(extra))) or "-",
        fused_or_accessory_register=r["fused_or_accessory"], fused_detail_register=r["fused_detail"] or "-",
        external_accessions=";".join(accs) or "NONE",
        fusion_partner_classification=("EXPRESSION_CONSTRUCT: " + "; ".join(expr)) if expr else
        ("MULTIPLE_ACCESSIONS_UNCLASSIFIED - needs literature" if len(accs) > 1 else
         "SUSPECTED_BY_LENGTH (construct >1.6x modelled)" if r["fused_or_accessory"] == "SUSPECTED" else "none recorded"),
        C4_palm=calls[c]["C4"], C5_thumb=calls[c]["C5"], C4b_fingers=calls[c]["C4b"],
        unit="chain", note="extensions are measured against the frozen instrument's anchor span, which is GII-centred"))

L.write_tsv(os.path.join(L.S3C, "TERMINI_FUSION_SUMMARY.tsv"), rows, list(rows[0]))
L.write_tsv(os.path.join(L.TABLES, "E_insertions.tsv"), ins_rows,
            list(ins_rows[0]) if ins_rows else ["chain", "note"])

# ---- does unusual architecture track the 3A decomposition outcome? (descriptive) --------------
out = []


def summarise(name, S, key, num=False):
    vals = [float(r[key]) for r in S if r[key] not in ("", None)]
    return dict(group=name, n=len(S), metric=key,
                median=statistics.median(vals) if vals else None,
                minimum=min(vals) if vals else None, maximum=max(vals) if vals else None, unit="chain")


groups = {
    "palm_CALL": [r for r in rows if r["C4_palm"] == "CALL"],
    "palm_NO_CALL_or_AMBIGUOUS": [r for r in rows if r["C4_palm"] != "CALL"],
    "stratum_primary": [r for r in rows if r["stratum"] == "primary"],
    "stratum_flagged": [r for r in rows if r["stratum"] == "flagged"],
}
for k, S in groups.items():
    for metric in ("n_modelled", "n_units", "n_units_outside_core", "n_extra_domain_units",
                   "mapper_total_inserted_residues", "mapper_max_insertion_run"):
        out.append(summarise(k, S, metric))
    # extension metrics only over chains where the anchor series reached both ends
    F = [r for r in S if r["anchor_series_coverage"] == "ANCHOR_SERIES_REACHED_BOTH_ENDS"]
    for metric in ("frac_outside_rt_core", "n_nterm_extension_residues", "n_cterm_extension_residues"):
        row = summarise(k + " [anchor series complete]", F, metric)
        out.append(row)
L.write_tsv(os.path.join(L.TABLES, "E_architecture_vs_calls.tsv"), out,
            ["group", "n", "metric", "median", "minimum", "maximum", "unit"])

print("gap excesses >=5:", len(ins_rows), "; meeting the declared >=20 rule:",
      sum(1 for x in ins_rows if x["meets_declared_threshold"] == "YES"))
print("anchor coverage:", collections.Counter(r["anchor_series_coverage"].split(" - ")[0] for r in rows))
for k in groups:
    F = [r for r in groups[k] if r["anchor_series_coverage"] == "ANCHOR_SERIES_REACHED_BOTH_ENDS"]
    fo = [float(r["frac_outside_rt_core"]) for r in F]
    print(f"{k:28} n={len(groups[k]):2} (complete anchor series {len(F):2}) "
          f"median frac outside core={statistics.median(fo):.3f} " if fo else f"{k:28} n={len(groups[k]):2} no complete-series chain",
          "median units=", statistics.median([r["n_units"] for r in groups[k]]))
