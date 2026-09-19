#!/usr/bin/env python3
"""Stage 3B truth schema v2.0 — FROZEN at g2. Three predeclared rules, applied to all 62 chains.

Channels are NEVER merged:
  S  coordinate-derived structural evidence   -> determines HARD_* classes
  L  author-assigned catalytic residues       -> never overwrites S
  F  mutational / functional evidence         -> never overwrites S

Hard-evidence rule is UNCHANGED from v1: METAL_CAT (Mg/Mn <= 3.2 A) or SUBSTRATE_NT (<= 4.0 A).
REACTION_PRODUCT contributes CONTEXT ONLY and can never create a HARD class.
Modified polymer residues are polymer, never ligands.
"""
CATALYTIC_METAL = {"MG","MN"}
OTHER_METAL     = {"ZN","K","NA"}
SUBSTRATE_NT    = {"DTP","TTP","DGT","DCP","DAT","ATP","ADP","GTP","GDP","UTP","DUP","DUT",
                   "AMP","ANP","AGS","DCT","DDG","D3T"}          # frozen v1 list, unchanged
REACTION_PRODUCT= {"POP"}                                         # NEW: pyrophosphate 2-
MODIFIED_POLYMER= {"MSE":"M","PTR":"Y","CSX":"C"}                 # NEW: coord identity -> canonical
EFFECTOR_LIGAND = {"NAD","AR6"}
NUC_MONOPHOS    = {"DGP","GMP"}   # DECLARED UNCLASSIFIED (see AMBIGUITY_4); measured label-neutral
BUFFER_CRYO     = {"EDO","GLY","PO4","1PE","NH4","MPD","SO4","CIT","DMS","URE","SIN","TLA",
                   "DIO","CL","HOH","DOD"}
MODIFIED_NT     = {"DX","93D"}
D_METAL, D_NT, D_NA, D_PROD = 3.2, 4.0, 4.0, 4.0
SITE_MAX = 8.0
SCHEMA_VERSION = "stage3b-truth-2.1"
