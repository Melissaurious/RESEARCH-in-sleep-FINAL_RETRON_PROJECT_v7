"""Shared paths and constants for the SPIRE ncRNA audit (exploratory analysis, not a gate)."""
from pathlib import Path

ROOT = Path('/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-spire-ncrna')
AUDIT = ROOT / 'analysis/spire_ncrna_audit'
TABLES = AUDIT / 'tables'
FIGS = AUDIT / 'figures'
SCRATCH = ROOT / 'ARIS_OUTPUT/spire_ncrna_audit'

# Canonical inputs are read from the MAIN checkout (external project asset, read-only);
# this worktree's data/ holds only the README.
DERIVED = Path('/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived')
RAW = Path('/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june')

ENV = Path('/home/borg/miniconda3/envs')
MLOCARNA = ENV / 'locarna_test/bin/mlocarna'          # LocARNA 2.0.1 (== SPIRE README)
LOCARNA_BIN = ENV / 'locarna_test/bin'
RSCAPE = ENV / 'retron_tradicional/bin/R-scape'      # R-scape 2.0.4.a (SPIRE README: 2.0.4)
MAFFT = ENV / 'retron_tradicional/bin/mafft'         # 7.525
CMSEARCH = ENV / 'retron_tradicional/bin/cmsearch'   # Infernal 1.1.5
MMSEQS = ENV / 'retron_tradicional/bin/mmseqs'
RNAFOLD = ENV / 'retron_tradicional/bin/RNAfold'
PADLOC_CM = Path('/home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data/cm/padlocdb.cm')

# Tier predicates, verbatim from analysis/dbchar_rt_ncrna_workbench/scripts/build_nb_part9.py
T1 = "canonical AND file_label = 'Retron'"
T2 = T1 + (" AND same_strand AND direction <> 'downstream' AND n_cds_between = 0"
           " AND abs(signed_distance_bp) <= 200")
T3 = T2 + " AND evalue <= 1e-5"
T4_RECURRENCE = ('multiple_species', 'one_species_multiple_genomes')

# Tool-rule structure (read from the rule files, 2026-09-18; see NCRNA_METHOD.md §population):
# DefenseFinder retron models never use an ncRNA. PADLOC Ec107-like/outgroup need RT + ncRNA.
DF_MULTI = {'Retron_I_A', 'Retron_I_B', 'Retron_II', 'Retron_III', 'Retron_IV', 'Retron_IX',
            'Retron_V', 'Retron_VI', 'Retron_VII_2', 'Retron_VIII', 'Retron_X', 'Retron_XIII'}
DF_FUSED = {'Retron_I_C', 'Retron_VII_1', 'Retron_XI', 'Retron_XII'}
PAD_MULTI = {'retron_I-A', 'retron_I-B', 'retron_II-A', 'retron_III-A', 'retron_IV', 'retron_IX',
             'retron_V', 'retron_VI', 'retron_VII-A2', 'retron_VIII', 'retron_X', 'retron_XIII'}
PAD_FUSED = {'retron_I-C', 'retron_VII-A1', 'retron_XI', 'retron_XII'}
PAD_NCDEP = {'retron_Ec107-like', 'retron_outgroup'}

# Harmonised type name so DefenseFinder and PADLOC labels can be compared (label only).
HARMONISE = {
    'Retron_I_A': 'I-A', 'retron_I-A': 'I-A', 'Retron_I_B': 'I-B', 'retron_I-B': 'I-B',
    'Retron_I_C': 'I-C', 'retron_I-C': 'I-C', 'Retron_II': 'II-A', 'retron_II-A': 'II-A',
    'Retron_III': 'III-A', 'retron_III-A': 'III-A', 'Retron_IV': 'IV', 'retron_IV': 'IV',
    'Retron_IX': 'IX', 'retron_IX': 'IX', 'Retron_V': 'V', 'retron_V': 'V',
    'Retron_VI': 'VI', 'retron_VI': 'VI', 'Retron_VII_1': 'VII-A1', 'retron_VII-A1': 'VII-A1',
    'Retron_VII_2': 'VII-A2', 'retron_VII-A2': 'VII-A2', 'Retron_VIII': 'VIII',
    'retron_VIII': 'VIII', 'Retron_X': 'X', 'retron_X': 'X', 'Retron_XI': 'XI',
    'retron_XI': 'XI', 'Retron_XII': 'XII', 'retron_XII': 'XII', 'Retron_XIII': 'XIII',
    'retron_XIII': 'XIII',
}

WINDOW_BP = 300   # SPIRE 07 usage: "300bp upstream sequences" (04 default is 270)
MAX_SET = 40      # SPIRE README: "mLocARNA input size <= 40 seqs"
