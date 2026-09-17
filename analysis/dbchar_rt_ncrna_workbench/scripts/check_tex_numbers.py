#!/usr/bin/env python
"""Verify the numbers in the thesis chapter against the cached workbench tables.

Every check computes its expected value FROM tables/*.tsv and then asserts that the
corresponding literal is present in the .tex. A number that is edited in the chapter but
not in the data, or recomputed in the data but not carried into the chapter, fails here.

    .venv/bin/python scripts/check_tex_numbers.py [path/to/chapter.tex]
"""
import re
import sys
from pathlib import Path

import pandas as pd

WB = Path(__file__).resolve().parent.parent
TABLES = WB / "tables"
TEX = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    WB / "exports_v2" / "results_database_characterization.tex"

S = TEX.read_text()
# strip comments so a number that survives only in a commented-out block does not count
S = "\n".join(l for l in S.split("\n") if not l.lstrip().startswith("%"))


def t(name):
    return pd.read_csv(TABLES / f"{name}.tsv", sep="\t")


def num(v):
    """The \\num{...} form the chapter uses for an integer."""
    return r"\num{%d}" % int(round(float(v)))


CHECKS = []


def check(label, needle, source):
    CHECKS.append((label, needle, source))


# ---- populations (Z0 registry) ------------------------------------------------------------
reg = t("Z0_population_registry").set_index("pop_id").n
for pid in ["REC-ALL", "REC-DIST", "LOC", "PLOC", "GEN", "RT-BASE", "RT-BASE-1F",
            "RT-MULTI", "RT-SEQ", "RT-CTX", "PL-ALL", "PL-CANON", "NC-ALL",
            "PAIR-ELIG", "PAIR-CANON"]:
    check(f"registry {pid}", num(reg[pid]), "Z0_population_registry")

# RT-SEQ must be described as single-family + cross-labelled, never as RT-BASE minus MULTI
check("RT-SEQ single-family split", num(493952), "Z0 guard rail")

# ---- geometry (D1 / D3) -------------------------------------------------------------------
d1 = t("D1_direction").set_index(["population", "direction"]).n_placements
for d in ["upstream", "overlapping", "downstream"]:
    check(f"canonical {d}", num(d1[("CANONICAL", d)]), "D1_direction")
ss = t("D1_same_strand")
check("same strand", num(ss[(ss.canonical) & (ss.same_strand)].n.iloc[0]), "D1_same_strand")
d3 = t("D3_cds_between").set_index("ord").n_placements  # n_cds_between is a string column ('>3')
check("no intervening CDS", num(d3[0]), "D3_cds_between")
check("one intervening CDS", num(d3[1]), "D3_cds_between")

# ---- N5, re-based onto PL-CANON -----------------------------------------------------------
n5 = t("N5_geometry_retron_vs_not").set_index("grp")
check("non-Retron placements", str(int(n5.loc["non-Retron", "n"])), "N5_geometry_retron_vs_not")
check("non-Retron pct upstream", f"{n5.loc['non-Retron', 'pct_upstream']:.2f}",
      "N5_geometry_retron_vs_not")
check("Retron pct upstream", f"{n5.loc['Retron', 'pct_upstream']:.2f}",
      "N5_geometry_retron_vs_not")
ov = t("N5_overlap_profile")
check("fully enclosed in a CDS", str(int(ov[ov.overlap_extent.str.startswith("d.")].n.iloc[0])),
      "N5_overlap_profile")

# ---- downstream mode (D2) -----------------------------------------------------------------
d2 = t("D2_downstream_strata").set_index("stratum")
mode = d2.loc["THE MODE: within +/-150 bp of 2682 bp"]
nc = d2.loc["downstream, NOT clipped (near-range)"]
check("mode placements", num(mode.n_placements), "D2_downstream_strata")
check("mode distinct ncRNAs", str(int(mode.n_exact_ncrna)), "D2_downstream_strata")
check("mode pct clipped", f"{mode.pct_true_start_clipped:.2f}", "D2_downstream_strata")
check("near-range downstream", num(nc.n_placements), "D2_downstream_strata")
check("near-range distinct ncRNAs", str(int(nc.n_exact_ncrna)), "D2_downstream_strata")

# ---- lengths (N3) — complete-only, the correction that inverted the draft ------------------
n3 = t("N3_completeness_length_shift").set_index("completeness_class").median_aa
check("overall median, complete calls", f"{int(n3['all_complete'])}~aa", "N3_completeness_length_shift")
n3f = t("N3_length_by_family_completeness")
n3f = n3f[n3f.completeness_class == "all_complete"].set_index("family_label")["median"]
check("Retron median, complete", f"{int(n3f['Retron'])}~aa", "N3_length_by_family_completeness")
check("RVT-GII median, complete", f"{int(n3f['RVT-GII'])}~aa", "N3_length_by_family_completeness")

# ---- ncRNA models and confidence ----------------------------------------------------------
c3 = t("C3_model_composition").set_index("detection_model")
check("OutgroupA distinct sequences", num(c3.loc["OutgroupA", "n_exact_ncrna"]), "C3_model_composition")
check("OutgroupB distinct sequences", str(int(c3.loc["OutgroupB", "n_exact_ncrna"])), "C3_model_composition")
conf = t("N6_cm_confidence")
hi = 100.0 * conf[conf.evalue_band < "d"].n_placements.sum() / conf.n_placements.sum()
check("pct calls at E<=1e-5", f"{hi:.2f}", "N6_cm_confidence")
bym = t("N6_cm_confidence_by_model").iloc[0]
check("worst model pct above 1e-5", f"{bym.pct_above_1e5:.1f}", "N6_cm_confidence_by_model")
z = t("C1_zero_class_by_family")
check("Retron carriage", f"{100 - z[z.file_label == 'Retron'].pct_zero.iloc[0]:.2f}",
      "C1_zero_class_by_family")

# ---- pair basis and funnel ----------------------------------------------------------------
f0 = t("F0_pair_view_basis").set_index("placement_population").n_exact_pairs
check("pairs, all placements", num(f0["ALL placements"]), "F0_pair_view_basis")
n8 = t("N8_dataset_funnel")
for _, r in n8.iterrows():
    check(f"funnel step {int(r.step)}", num(r.n_pairs), "N8_dataset_funnel")

# ---- resulting tiers (Z1) -----------------------------------------------------------------
z1 = t("Z1_association_resource_tiers").set_index("tier")
for tier in z1.index:
    check(f"tier {tier} pairs", num(z1.loc[tier, "n_exact_pairs"]), "Z1_association_resource_tiers")
topo = t("Z1_t3_topology").set_index("side")
check("T3 RT with one partner", f"{topo.loc['RT -> ncRNA', 'pct_with_one_partner']:.2f}",
      "Z1_t3_topology")
check("T3 ncRNA with one partner", f"{topo.loc['ncRNA -> RT', 'pct_with_one_partner']:.2f}",
      "Z1_t3_topology")
check("T3 max RT partners", str(int(topo.loc["ncRNA -> RT", "max_partners"])), "Z1_t3_topology")
jit = t("Z1_t3_partner_jitter").iloc[0]
check("RTs with several partners", str(int(jit.rts_with_several_partners)), "Z1_t3_partner_jitter")
check("partners within 5nt", str(int(jit.spread_le_5nt)), "Z1_t3_partner_jitter")

# ---- tool agreement (generated table) ------------------------------------------------------
ag = t("N1_tool_agreement_table").set_index("detected_by_set")
for k in ag.index:
    check(f"tool region {k} records", num(ag.loc[k, "n_records"]), "N1_tool_agreement_table")
    check(f"tool region {k} proteins", num(ag.loc[k, "n_exact_rt"]), "N1_tool_agreement_table")
    check(f"tool region {k} pct RNA (protein)", f"{ag.loc[k, 'pct_exact_rt_with_rna']:.2f}",
          "N1_tool_agreement_table")

# ---- domain redundancy (Z2) ----------------------------------------------------------------
dm = t("Z2_redundancy_by_domain").set_index("domain")
check("bacteria records per protein", f"{dm.loc['Bacteria', 'records_per_protein']:.2f}",
      "Z2_redundancy_by_domain")
check("archaea records per protein", f"{dm.loc['Archaea', 'records_per_protein']:.2f}",
      "Z2_redundancy_by_domain")

# ---- exact-sequence grain (Z3) --------------------------------------------------------------
z3 = t("Z3_singleton_diagnosis").set_index("stratum")
for k, lbl in [("a. all Retron proteins", "all"),
               ("b. drop metagenome-only", "no MAG"),
               ("c. drop metagenome-only AND partial calls", "no MAG, complete")]:
    check(f"singletons {lbl} n", num(z3.loc[k, "n_seen_once"]), "Z3_singleton_diagnosis")
    check(f"singletons {lbl} pct", f"{z3.loc[k, 'pct_seen_once']:.1f}", "Z3_singleton_diagnosis")
ch = t("Z3_chao1_illustration").iloc[0]
check("f2 doubletons", num(ch.f2_doubletons), "Z3_chao1_illustration")
check("chao1 estimate", num(ch.chao1), "Z3_chao1_illustration")
sc = t("Z3_singleton_sampling_context").set_index("sampling_depth_of_its_species")
check("singletons in >=1000-genome species",
      num(sc.loc["a. >=1000 genomes of that species sequenced", "n_proteins_seen_once"]),
      "Z3_singleton_sampling_context")
ws = t("Z3_distinct_rt_within_species").set_index("tax_species")
for sp in ["Escherichia_coli", "Salmonella_enterica"]:
    check(f"{sp} distinct exact RTs", num(ws.loc[sp, "n_distinct_exact_rt"]),
          "Z3_distinct_rt_within_species")
    check(f"{sp} genomes", num(ws.loc[sp, "n_genomes"]), "Z3_distinct_rt_within_species")

# ---- run -------------------------------------------------------------------------------------
fails = [(l, n, s) for l, n, s in CHECKS if n not in S]
print(f"{TEX.name}: {len(CHECKS)} numbers checked against tables/")
print(f"  present .... {len(CHECKS) - len(fails)}")
print(f"  MISSING .... {len(fails)}")
for l, n, s in fails:
    print(f"    - {l:<46} expected {n!r:<20} from {s}")

# structural checks
labs = set(re.findall(r"\\label\{((?:fig|tab):[^}]+)\}", S))
refs = set(re.findall(r"\\ref\{((?:fig|tab):[^}]+)\}", S))
print(f"\n  labels {len(labs)} | refs {len(refs)} | "
      f"orphan labels {sorted(labs - refs) or 'none'} | dangling refs {sorted(refs - labs) or 'none'}")
bad_si = re.findall(r"\\SI\{[^}]*\}\{((?!\\percent)[^}]*)\}", S)
print(f"  non-percent \\SI units (must be none): {sorted(set(bad_si)) or 'none'}")
sys.exit(1 if (fails or (labs - refs) or (refs - labs) or bad_si) else 0)
