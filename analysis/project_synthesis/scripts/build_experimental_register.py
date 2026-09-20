#!/usr/bin/env python3
"""Build EXPERIMENTAL_RT_NCRNA_REGISTER.tsv from local assets only.

Read-only over the source assets. One row per element for which a LOCAL asset
carries experimental evidence, plus prediction-only rows for the historically
named retrons that have no local assay.

Sources (hashed in the register's own provenance block, not here):
  K = /home/borg/RESEARCH-retron-db/results/stage1_mestre_replication_and_insights/inputs/support.csv
      sha256 80b2f565515c96bb1b9b0082c261dd6184c67672e29bb96c813cf6abdd9d9577
  F = /home/borg/RETRONS_january_2026/the-retron-project/REPEATE_positive_dataset/
      41587_2024_2384_MOESM4_ESM_extracted_ncRNAs.fasta
      sha256 8a51cf71efbcecb48ecf4ec3dac8f4c899f14605d2458433f3e56bba8923a40f
  M = references/rt0_rt7/mestre_2020/Mestre_supplementary_material.csv
  S = /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/
  T = <asset-audit>/analysis/stage3b_design/TRUTH_TABLE.tsv   (catalytic truth, schema v2.1)

Nothing here asserts evidence that a local file does not state.
"""
import csv
import os

K = "/home/borg/RESEARCH-retron-db/results/stage1_mestre_replication_and_insights/inputs/support.csv"
F = ("/home/borg/RETRONS_january_2026/the-retron-project/REPEATE_positive_dataset/"
     "41587_2024_2384_MOESM4_ESM_extracted_ncRNAs.fasta")
M = ("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis/references/rt0_rt7/"
     "mestre_2020/Mestre_supplementary_material.csv")
SDIR = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures"
MSEQ = ("/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/"
        "Mestre_sequences/terminal_{tid}/protein_aminoacid.fasta")
EVO2 = "/home/borg/evo2/retron_project_april_15/gold_std_dataset_data/{name}/ncRNA.fasta"

PAPER_KHAN = "Khan et al. 2024 Nat Biotechnol doi:10.1038/s41587-024-02384-z (An experimental census of retrons)"
PAPER_MESTRE = "Mestre et al. 2020 NAR (systematic prediction) - PREDICTION SET, no assay column"

# Structures held locally that contain a retron RT together with RNA and/or DNA chains.
# Keys are element names as the structure files themselves state them.
STRUCT = {
    "Ec86":  "7V9U(RT+msDNA+RNA,3.2A);7V9X(+effector,2.8A);7XJG(+effector,2.5A);8QBM(Eco1 filament+ADPr effector);8QBK;8QBL",
    "Ec83":  "9E8Z(4-component retron Ec83; DNA 79mer labelled msDNA + RNA 38mer)",
    "Ec78":  "9VHE(retron-Eco7 complex; msrRNA+msdDNA chains);9NNB(PtuA:PtuB:RT 4:2:1; RNA 41mer);9VHL",
    "Eco8":  "9X94(apo retron-Eco8; RNA 81mer + DNA 75mer);23OR;9LBQ;9LPA;9WN8;9X9B",
    "Ec67":  "9I2F;9I2G(catalytic Asp 202, OWN_CHAIN truth);9S1F",
    "St85":  "9L7P(RVT-Retrons St85);effector chain named 'retron ST85 family effector' in 7V9X/7XJG",
}
# Stage-3B catalytic truth, schema v2.1 (TRUTH_TABLE.tsv + EVIDENCE_REPAIR_2026-09-18.md)
CAT_TRUTH = {
    "Ec86": ("HARD_SINGLE D198 (7XJG, 8QBL OWN_CHAIN)", "NO_MUTATIONAL_FLAG_LOCALLY (structural assignment only)"),
    "Ec67": ("HARD_SINGLE D202 (9I2G OWN_CHAIN); metal also at D460 -> multisite, unresolved",
             "NO_MUTATIONAL_FLAG_LOCALLY"),
    "Eco8": ("FUNCTIONAL_PAIR, empty structural set; Mg METAL_ASSERTED_NOT_DEPOSITED",
             "YES: D107A individuated; YADD->AAAA implicates D200/D201 JOINTLY (Nat Commun 2026;17:7374, recorded in stage3b EVIDENCE_REPAIR_2026-09-18.md)"),
}
# Historically named retrons in the Mestre table (17 names) -> short name used above.
NAMED_SHORT = {
    "Retron-Eco1 (Ec86)": "Ec86", "Retron-Eco2 (Ec67)": "Ec67", "Retron-Eco3 (Ec73)": "Ec73",
    "Retron-Eco4 (Ec83)": "Ec83", "Retron-Eco5 (Ec107)": "Ec107", "Retron-Eco6 (Ec48)": "Ec48",
    "Retron-Eco7 (Ec78)": "Ec78", "Retron-Sen1 (Se72)": "Se72", "Retron-Sen2 (St85)": "St85",
    "Retron-Sau1 (Sa163)": "Sa163", "Retron-Vch1 (Vc95)": "Vc95", "Retron-Vch2 (Vc81)": "Vc81",
    "Retron-Vch3 (Vc137)": "Vc137", "Retron-Vpa1 (Vp96)": "Vp96", "Retron-Mxa1 (Mx162)": "Mx162",
    "Retron-Mxa2 (Mx65)": "Mx65", "Retron-Nex2 (Ne144)": "Ne144",
}
EVO2_NCRNA = {"Mx65", "Vc81", "Vc95", "Vp96"}

COLS = [
    "pair_id", "element_name", "mestre_terminal_id", "rt_accession_local", "mestre_rt_clade",
    "retron_subtype_local", "rt_protein_seq_local", "rt_aa_len", "ncrna_seq_local", "ncrna_len_nt",
    "ncrna_boundaries_known", "msdna_rtdna_sequence_local", "rtdna_len_nt", "msdna_demonstrated",
    "rtdna_production_xEco1", "human_editing_xEco1", "bacterial_editing_xEco1", "phage_editing_xEco1",
    "cognate_rt_experimentally_linked", "ncrna_mutagenesis_local", "rt_mutagenesis_local",
    "swap_or_cross_reactivity_local", "orthogonality_exchange_local", "catalytic_truth_local",
    "experimental_structure_local", "source_paper", "supplementary_source_local",
    "provenance_quality", "evidence_tier", "usable_denovo_seed", "usable_heldout_benchmark",
    "usable_pairing_specificity_validation", "caveats",
]


def num(x):
    try:
        return float(str(x).strip())
    except Exception:
        return None


def read_csv(path, enc="utf-8-sig"):
    with open(path, encoding=enc, newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    khan = read_csv(K)
    fasta_ids = set()
    with open(F) as fh:
        for line in fh:
            if line.startswith(">"):
                fasta_ids.add(line[1:].strip().split()[0])

    # Mestre table: terminal -> (clade, subtype, accession, retron name)
    mestre = {}
    mrows = read_csv(M)
    hdr = list(mrows[0].keys())
    c_node = hdr[0]
    c_clade = next(h for h in hdr if h.lower().startswith("rt/clade"))
    c_sub = next(h for h in hdr if h.lower().startswith("retron (sub"))
    c_acc = next(h for h in hdr if h.lower().startswith("acces"))
    c_name = next(h for h in hdr if h.lower().startswith("retron name"))
    # Nodes are bare integers in the file ("1550"), and the Retron-name column carries the
    # paper's footnote markers ("Retron-Vpa1 (Vp96)g"). The a-g legend is absent from every
    # local copy, so the marker is stripped for matching and reported verbatim beside it.
    for r in mrows:
        node = (r[c_node] or "").strip()
        if not node:
            continue
        raw_name = (r[c_name] or "").strip()
        base_name = raw_name[:-1] if (len(raw_name) > 1 and raw_name[-1].islower()
                                      and raw_name[-2] == ")") else raw_name
        mestre[node] = (r[c_clade].strip(), r[c_sub].strip(), r[c_acc].strip(), base_name, raw_name)

    rows = []
    khan_terminals = set()

    for i, r in enumerate(khan, start=1):
        tid_raw = (r["terminal_id"] or "").strip()
        tid = tid_raw.split(".")[0]
        khan_terminals.add(tid)
        node = "terminal_%s" % tid
        clade, sub, acc, mname, mname_raw = mestre.get(tid, ("", "", "", "", ""))
        short = NAMED_SHORT.get(mname, "")
        name = mname or (r.get("potential_abbreviation") or "").strip() or node

        prod = num(r["rtdna_production_xeco1"])
        hum = num(r["human_editing_xeco1"])
        bac = num(r["bacterial_editing_xeco1"])
        pha = num(r["phage_editing_xeco1"])
        rtdna = (r["RTDNA_sequence"] or "").strip()
        has_rtdna = len(rtdna) > 3
        nclen = (r["ncRNA_length"] or "").strip()
        any_pos = any(v is not None and v > 0 for v in (prod, hum, bac, pha))

        if has_rtdna:
            msdna = "YES_EMPIRICAL_RTDNA_SEQUENCE_IN_PANEL"
        elif prod is not None and prod > 0:
            msdna = "YES_PRODUCTION_MEASURED_NO_SEQUENCE"
        elif short in STRUCT and short in ("Ec86", "Ec83", "Ec78", "Eco8"):
            msdna = "YES_STRUCTURAL_DNA_CHAIN_ONLY"
        elif prod is not None and prod == 0:
            msdna = "NO_PRODUCTION_MEASURED_ZERO"
        else:
            msdna = "NOT_DETERMINED_LOCALLY"

        struct = STRUCT.get(short, "")
        cat, mut = CAT_TRUTH.get(short, ("", "NOT_IN_LOCAL_ASSETS"))

        if struct and any_pos:
            tier = "X1_STRUCTURE_PLUS_FUNCTIONAL_ASSAY"
        elif has_rtdna and any_pos:
            tier = "X2_RTDNA_SEQUENCE_PLUS_FUNCTIONAL_ASSAY"
        elif has_rtdna:
            tier = "X2b_RTDNA_SEQUENCE_ONLY"
        elif any_pos:
            tier = "X3_FUNCTIONAL_ASSAY_ONLY"
        elif struct:
            tier = "X5_STRUCTURE_ONLY"
        else:
            tier = "X4_SYNTHESISED_AND_TESTED_OUTCOME_UNDETERMINED"

        rows.append({
            "pair_id": "EXP-K%03d" % i,
            "element_name": name,
            "mestre_terminal_id": node,
            "rt_accession_local": acc or "NOT_IN_MESTRE_TABLE",
            "mestre_rt_clade": clade,
            "retron_subtype_local": (r.get("retron_sub") or "").strip(),
            "rt_protein_seq_local": "%s ; %s:rt_protein_aa" % (MSEQ.format(tid=tid), K),
            "rt_aa_len": (r["rt_protein_aa_length"] or "").strip(),
            "ncrna_seq_local": "%s:ncRNA_sequence ; %s" % (K, F if tid_raw in fasta_ids or ("terminal_%s" % tid) in fasta_ids else F),
            "ncrna_len_nt": nclen,
            "ncrna_boundaries_known": "PUBLISHED_SEQUENCE_EXTENT_ONLY (paper-defined; not independently verified here; no genomic coordinates in the local file)",
            "msdna_rtdna_sequence_local": "YES (%s:RTDNA_sequence)" % K if has_rtdna else "NO",
            "rtdna_len_nt": (r["RTDNA_length"] or "").strip(),
            "msdna_demonstrated": msdna,
            "rtdna_production_xEco1": r["rtdna_production_xeco1"].strip(),
            "human_editing_xEco1": r["human_editing_xeco1"].strip(),
            "bacterial_editing_xEco1": r["bacterial_editing_xeco1"].strip(),
            "phage_editing_xEco1": r["phage_editing_xeco1"].strip(),
            "cognate_rt_experimentally_linked":
                "YES_ASSAYED_AS_A_UNIT (RT + its own ncRNA synthesised and measured together)" if any_pos
                else "CO_REPORTED_AND_TESTED_ONLY (no positive readout recorded locally)",
            "ncrna_mutagenesis_local": "NOT_IN_LOCAL_ASSETS",
            "rt_mutagenesis_local": mut,
            "swap_or_cross_reactivity_local": "NOT_IN_LOCAL_ASSETS",
            "orthogonality_exchange_local": "NOT_IN_LOCAL_ASSETS",
            "catalytic_truth_local": cat,
            "experimental_structure_local": struct or "NONE_LOCAL",
            "source_paper": PAPER_KHAN,
            "supplementary_source_local": "%s (curated panel; original MOESM workbook NOT on disk) + %s" % (K, F),
            "provenance_quality":
                "MEDIUM: assay values and sequences are present and self-consistent, but support.csv carries no header, README or hash record naming who assembled it; attribution to the paper rests on project docs + matching DOI-tokened FASTA",
            "evidence_tier": tier,
            "usable_denovo_seed": "YES",
            "usable_heldout_benchmark":
                "CONDITIONAL_CHECK_LEAKAGE (80 of 175 published ncRNAs match a project corpus sequence at >=90% id over >=80% length; see spire pubval/pub_vs_oriented.tsv)",
            "usable_pairing_specificity_validation":
                "YES_PRIMARY" if (has_rtdna and any_pos) else ("YES_SECONDARY" if any_pos else "NO_NO_POSITIVE_READOUT"),
            "caveats": "174 of 175 panel rows lie inside Mestre's own reference set by accession, so the panel is an assay layer on the prediction set, NOT independent validation of it. RT_sequence column is empty in all 175 rows (use rt_protein_aa).",
        })

    # Named retrons with no Khan panel row, and Eco8 (structure only, not one of the 17 names).
    extra = []
    for mname, short in NAMED_SHORT.items():
        tid = next((n for n, v in mestre.items() if v[3] == mname), None)
        if tid is None:
            continue
        node = "terminal_%s" % tid
        if tid in khan_terminals:
            continue
        clade, sub, acc, _, mname_raw = mestre[tid]
        struct = STRUCT.get(short, "")
        cat, mut = CAT_TRUTH.get(short, ("", "NOT_IN_LOCAL_ASSETS"))
        nc = EVO2.format(name=short) if short in EVO2_NCRNA else ""
        extra.append((mname, short, node, tid, clade, sub, acc, struct, cat, mut, nc, mname_raw))

    for j, (mname, short, node, tid, clade, sub, acc, struct, cat, mut, nc, mname_raw) in enumerate(sorted(extra), start=1):
        if struct:
            tier = "X5_STRUCTURE_ONLY"
            msdna = "YES_STRUCTURAL_DNA_CHAIN_ONLY"
        else:
            tier = "P0_HISTORICAL_NAME_PREDICTION_ONLY_LOCALLY"
            msdna = "NOT_DETERMINED_LOCALLY"
        rows.append({
            "pair_id": "EXP-N%02d" % j,
            "element_name": mname,
            "mestre_terminal_id": node,
            "rt_accession_local": acc,
            "mestre_rt_clade": clade,
            "retron_subtype_local": sub,
            "rt_protein_seq_local": MSEQ.format(tid=tid),
            "rt_aa_len": "",
            "ncrna_seq_local": nc + " (PROVENANCE UNSTATED: no local file records coordinates, source span or method)" if nc else "NONE_LOCAL",
            "ncrna_len_nt": "",
            "ncrna_boundaries_known": "NO" if not nc else "SEQUENCE_PRESENT_BUT_PROVENANCE_UNSTATED",
            "msdna_rtdna_sequence_local": "NO",
            "rtdna_len_nt": "",
            "msdna_demonstrated": msdna,
            "rtdna_production_xEco1": "",
            "human_editing_xEco1": "",
            "bacterial_editing_xEco1": "",
            "phage_editing_xEco1": "",
            "cognate_rt_experimentally_linked":
                "STRUCTURAL_COMPLEX_LOCALLY" if struct else "NO_LOCAL_EVIDENCE (name only; Mestre's 'experimentally validated' status is stated in the paper's Methods prose, not in any local file)",
            "ncrna_mutagenesis_local": "NOT_IN_LOCAL_ASSETS",
            "rt_mutagenesis_local": mut,
            "swap_or_cross_reactivity_local": "NOT_IN_LOCAL_ASSETS",
            "orthogonality_exchange_local": "NOT_IN_LOCAL_ASSETS",
            "catalytic_truth_local": cat,
            "experimental_structure_local": struct or "NONE_LOCAL",
            "source_paper": PAPER_MESTRE,
            "supplementary_source_local": M,
            "provenance_quality": "LOW: prediction table + tree only; the a-g footnote legend is absent from every local copy, so what marks a row 'validated' cannot be resolved locally",
            "evidence_tier": tier,
            "usable_denovo_seed": "NO_NO_LOCAL_NCRNA" if not nc else "CONDITIONAL_PROVENANCE_UNSTATED",
            "usable_heldout_benchmark": "NO",
            "usable_pairing_specificity_validation": "NO",
            "caveats": ("Mestre 'Retron name' verbatim: %s (footnote legend a-g absent from every local copy). " % (mname_raw or mname)) + "Retron-Sen2 (St85) download is an RNA-polymerase substitute in the local asset set (mestre-audit REPORT); Vc137 has no protein accession locally, only a PATRIC fig| id.",
        })

    # Eco8: no Mestre name, structure + mutational truth only.
    cat, mut = CAT_TRUTH["Eco8"]
    rows.append({
        "pair_id": "EXP-N99", "element_name": "retron-Eco8 (not among the 17 Mestre names)",
        "mestre_terminal_id": "NOT_IN_MESTRE_TABLE",
        "rt_accession_local": "UNP P0DV59 (RT), P0DV58 (OLD nuclease), GB CP057441.1 (from 9X94 header)",
        "mestre_rt_clade": "", "retron_subtype_local": "",
        "rt_protein_seq_local": "ONLY AS STRUCTURE COORDINATES: %s/9X94.pdb" % SDIR, "rt_aa_len": "",
        "ncrna_seq_local": "ONLY AS A STRUCTURE CHAIN (RNA 81-mer in 9X94)", "ncrna_len_nt": "81nt_chain",
        "ncrna_boundaries_known": "STRUCTURAL_CHAIN_EXTENT_ONLY",
        "msdna_rtdna_sequence_local": "ONLY AS A STRUCTURE CHAIN (DNA 75-mer in 9X94)", "rtdna_len_nt": "75nt_chain",
        "msdna_demonstrated": "YES_STRUCTURAL_DNA_CHAIN_ONLY",
        "rtdna_production_xEco1": "", "human_editing_xEco1": "", "bacterial_editing_xEco1": "", "phage_editing_xEco1": "",
        "cognate_rt_experimentally_linked": "YES_STRUCTURAL_COMPLEX (RT x4 + OLD nuclease x4 + RNA + DNA in one entry)",
        "ncrna_mutagenesis_local": "NOT_IN_LOCAL_ASSETS", "rt_mutagenesis_local": mut,
        "swap_or_cross_reactivity_local": "NOT_IN_LOCAL_ASSETS", "orthogonality_exchange_local": "NOT_IN_LOCAL_ASSETS",
        "catalytic_truth_local": cat, "experimental_structure_local": STRUCT["Eco8"],
        "source_paper": "Nat Commun 2026;17:7374 (cited inside stage3b EVIDENCE_REPAIR_2026-09-18.md; PDF not on disk)",
        "supplementary_source_local": "%s/9X94.pdb ; <asset-audit>/analysis/stage3b_design/EVIDENCE_REPAIR_2026-09-18.md" % SDIR,
        "provenance_quality": "MEDIUM-HIGH for the catalytic claim (deposited coordinates + a mutational statement recorded with its source), LOW for sequence-level reuse (no FASTA on disk)",
        "evidence_tier": "X5_STRUCTURE_ONLY_PLUS_RT_MUTAGENESIS",
        "usable_denovo_seed": "NO_NOT_AS_A_SEQUENCE", "usable_heldout_benchmark": "NO",
        "usable_pairing_specificity_validation": "NO",
        "caveats": "The Eco8 Mg is METAL_ASSERTED_NOT_DEPOSITED; YADD->AAAA implicates D200/D201 jointly, so no single residue is individuated by mutagenesis except D107A.",
    })

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "EXPERIMENTAL_RT_NCRNA_REGISTER.tsv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, delimiter="\t", lineterminator="\n",
                           extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: (r.get(c, "") or "") for c in COLS})
    print("wrote", out, len(rows), "rows")
    from collections import Counter
    print(Counter(r["evidence_tier"] for r in rows))


if __name__ == "__main__":
    main()
