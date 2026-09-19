#!/usr/bin/env python3
"""s3c_gD — ANALYSIS of the committed X/Y annotation (descriptive).

Writes tables/D_summary.tsv (per family stratum), tables/D_region_y_rna_enrichment.tsv and
tables/D_region_y_length_vs_literature.tsv.

The Region-Y pairing-specificity question is addressed ONLY as: where the deposited nucleic acid
contacts fall, how that compares with a length-proportional expectation, and what the historical
experiments did and did not test. No specificity claim is made here.
"""
import collections
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3clib as L  # noqa: E402

LIT_Y_LENGTH = 90  # the literature's "~90 aa" (Simon et al. 2019); a comparator, not a criterion

R = L.read_tsv(os.path.join(L.S3C, "XY_REGION_ANNOTATIONS.tsv"))
E = L.read_tsv(os.path.join(L.S3C, "TERMINI_FUSION_SUMMARY.tsv"))
fus = {r["chain"]: r for r in E}

strata = collections.defaultdict(list)
for r in R:
    strata["ALL"].append(r)
    strata["retron" if r["is_retron_family"] == "YES" else "non-retron"].append(r)
    strata["family:" + r["family_METADATA"]].append(r)

rows = []
for k in sorted(strata, key=lambda x: (x != "ALL", x != "retron", x)):
    S = strata[k]
    n = len(S)
    xdef = [r for r in S if r["region_X_status"].startswith("X_INTERVAL_FROM_BLOCKS")]
    xwide = [r for r in S if r["region_X_status"].startswith("X_INTERVAL_WIDE")]
    xscan = xdef + xwide
    ydef = [r for r in S if r["region_Y_status"].startswith("Y_INTERVAL_FROM_VTG")]
    rows.append(dict(
        stratum=k, n_chains=n, n_groups=len({r["biological_group"] for r in S}),
        n_X_interval_from_blocks=len(xdef), n_X_interval_wide_window=len(xwide),
        n_X_undefined=n - len(xscan),
        n_NAXXH_strict=sum(r["region_X_motif"] == "NAXXH_STRICT" for r in S),
        n_AXXH_relaxed=sum(r["region_X_motif"] == "AXXH_RELAXED" for r in S),
        n_no_motif_in_scanned_interval=sum(r["region_X_motif"] == "NO_MOTIF_IN_INTERVAL" for r in S),
        frac_NAXXH_of_scanned=(sum(r["region_X_motif"] == "NAXXH_STRICT" for r in S) / len(xscan)) if xscan else None,
        n_Y_interval_from_VTG=len(ydef), frac_Y_defined=len(ydef) / n,
        n_no_VTG_like_in_window=sum(r["region_Y_motif"] == "NO_VTG_LIKE_TRIPLET_IN_WINDOW" for r in S),
        median_Y_length=statistics.median([int(r["region_Y_length"]) for r in ydef]) if ydef else None,
        n_chains_with_nucleic_acid=sum(r["chain_has_nucleic_acid"] == "YES" for r in S),
        unit="chain",
        note="a motif absence is not a region absence; X scanning depends on the GII-centred mapper reaching SB2p/SB3"))
L.write_tsv(os.path.join(L.TABLES, "D_summary.tsv"), rows, list(rows[0]))

# ---- Region Y and the nucleic acid: observed vs length-proportional expectation ---------------
enr = []
for r in R:
    if r["chain_has_nucleic_acid"] != "YES" or not r["region_Y_status"].startswith("Y_INTERVAL_FROM_VTG"):
        continue
    n_mod = int(r["n_modelled"])
    ylen = int(r["region_Y_length"])
    y_rna, y_dna = int(r["region_Y_rna_contact_residues"]), int(r["region_Y_dna_contact_residues"])
    ch_rna, ch_dna = int(r["chain_rna_contact_residues"]), int(r["chain_dna_contact_residues"])
    exp = ylen / n_mod
    enr.append(dict(chain=r["chain"], family_METADATA=r["family_METADATA"],
                    is_retron_family=r["is_retron_family"], n_modelled=n_mod,
                    region_Y_start=r["region_Y_start_resnum"], region_Y_length=ylen,
                    region_Y_frac_of_chain=exp,
                    chain_rna_contact_residues=ch_rna, region_Y_rna_contact_residues=y_rna,
                    frac_rna_contacts_in_Y=(y_rna / ch_rna) if ch_rna else None,
                    rna_ratio_observed_over_expected=((y_rna / ch_rna) / exp) if ch_rna and exp else None,
                    chain_dna_contact_residues=ch_dna, region_Y_dna_contact_residues=y_dna,
                    frac_dna_contacts_in_Y=(y_dna / ch_dna) if ch_dna else None,
                    dna_ratio_observed_over_expected=((y_dna / ch_dna) / exp) if ch_dna and exp else None,
                    region_Y_3A_unit=r["region_Y_unit"], unit="residue with >=1 contact at 4.0 A",
                    note="the deposited nucleic acid differs between entries (msr RNA, msDNA, duplex); "
                         "this is a location measurement, not a specificity measurement"))
L.write_tsv(os.path.join(L.TABLES, "D_region_y_rna_enrichment.tsv"), enr, list(enr[0]))

# ---- Y length against the literature's ~90 aa, with fusion state -------------------------------
ylen_rows = []
for r in R:
    if not r["region_Y_status"].startswith("Y_INTERVAL_FROM_VTG"):
        continue
    f = fus[r["chain"]]
    ylen = int(r["region_Y_length"])
    ylen_rows.append(dict(chain=r["chain"], family_METADATA=r["family_METADATA"],
                          is_retron_family=r["is_retron_family"], region_Y_length=ylen,
                          literature_expectation_aa=LIT_Y_LENGTH, difference=ylen - LIT_Y_LENGTH,
                          within_1_5x="YES" if ylen <= 1.5 * LIT_Y_LENGTH else "NO",
                          fused_or_accessory_register=f["fused_or_accessory_register"],
                          external_accessions=f["external_accessions"],
                          n_units_outside_core=f["n_units_outside_core"],
                          interpretation=("consistent with the literature ~90 aa C-terminal region"
                                          if ylen <= 1.5 * LIT_Y_LENGTH else
                                          "the VTG-to-C-terminus rule also swallows C-terminal accessory or fused "
                                          "content in this chain; the literature '~90 aa' does not describe it"),
                          unit="chain"))
L.write_tsv(os.path.join(L.TABLES, "D_region_y_length_vs_literature.tsv"), ylen_rows, list(ylen_rows[0]))

ret = [r for r in enr if r["is_retron_family"] == "YES"]
non = [r for r in enr if r["is_retron_family"] == "NO"]
for name, S in (("retron", ret), ("non-retron", non)):
    if S:
        rr = [x["rna_ratio_observed_over_expected"] for x in S if x["rna_ratio_observed_over_expected"] is not None]
        print(f"{name}: n={len(S)} median RNA obs/exp in Y = {statistics.median(rr):.2f} "
              f"(range {min(rr):.2f}-{max(rr):.2f})" if rr else f"{name}: no RNA")
for r in rows:
    if r["stratum"] in ("ALL", "retron", "non-retron"):
        print(r["stratum"], "X scanned:", r["n_X_interval_from_blocks"] + r["n_X_interval_wide_window"],
              "NAXXH:", r["n_NAXXH_strict"], "| Y defined:", r["n_Y_interval_from_VTG"],
              "no VTG:", r["n_no_VTG_like_in_window"], "| median Y len:", r["median_Y_length"])
