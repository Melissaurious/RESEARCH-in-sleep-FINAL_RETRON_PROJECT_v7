#!/usr/bin/env python3
"""Stage 3B multisite-attribution rule — FROZEN before g1/g2 calibration (schema v2.1).

RULE. If a chain contains more than one structural catalytic-Asp cluster it may be resolved ONLY
when independent functional/site evidence uniquely attributes exactly one cluster to the
reverse-transcriptase POLYMERASE catalytic site. Allowed attribution evidence:
  (a) explicit PDB/mmCIF domain/site annotation;
  (b) primary structural literature assigning the active site to a NAMED enzymatic domain;
  (c) experimentally observed ligand/metal context that unambiguously belongs to one named
      catalytic domain.
The attribution step MUST NOT use: YXDD/YADD motif identity; expected catalytic-Asp sequence
separation; Stage-2 state/RT5 coordinates; fingers/palm/thumb boundaries; family labels; or the
sequence-separation window being calibrated.
AUTHOR_SITE records that annotate MULTIPLE different active sites do not themselves resolve a chain.
Resolved -> keep the polymerase cluster as structural catalytic truth; record the others as
NON_POLYMERASE_CATALYTIC_SITE. Unresolved -> HARD_MULTISITE_UNRESOLVED, excluded from calibration.

EXTENSION, applied for global consistency and reported: the same attribution also applies to a
SINGLE-cluster chain whose only cluster is independently attributed to a NON-polymerase catalytic
domain. Such a cluster is recorded as NON_POLYMERASE_CATALYTIC_SITE and contributes no polymerase
structural truth. Not applying it would let a nuclease active site count as RT polymerase truth
merely because the polymerase site lacked a metal in that particular structure.

Each entry below is a per-(pdb,chain) attribution with its evidence, recorded verbatim.
"""
ATTRIBUTION = {
 ("1RTD","A"): dict(
   polymerase=[110,185],
   non_polymerase={"RNase H": [443,498,549]},
   basis="(a)+(c)+(b). mmCIF _struct_site: AC7 = 'BINDING SITE FOR RESIDUE TTP A 700' contains "
         "ASP110, ASP113, ASP185; AC1/AC2 = Mg600/Mg601 sites, each containing ASP110, ASP185 and "
         "TTP700. AC3 = 'BINDING SITE FOR RESIDUE MG A 605' contains ASP443, ASP498, ASP549 and NO "
         "nucleotide. Ligand context: a deoxynucleoside triphosphate is the DNA-polymerase substrate; "
         "the RNase H domain is a hydrolase and binds no dNTP. Literature: Huang, Chopra, Verdine & "
         "Harrison, Science 1998;282:1669-1675 (PMID 9831551) - the structure is 'a stalled complex "
         "... with a DNA template:primer and a deoxynucleoside triphosphate (dNTP)' capturing 'a state "
         "in which the substrates are poised for attack on the dNTP'.",
   resolved=True),
 ("9I2G","B"): dict(
   polymerase=[202],
   non_polymerase={"TOPRIM (RNase-H-like) nuclease": [460]},
   basis="(b). Jasnauskaite et al., Nat Struct Mol Biol 2026;33(2):330-340 (PMID 41709047, "
         "PMC12916289): Eco2 'couples an amino-terminal RT domain fused to a carboxy-terminal "
         "RNase-H-like topoisomerase-primase (TOPRIM) domain'; the mutational variants are "
         "'dRT (D201A/D202A)' and 'dTOPRIM (E374A/D378A/D460A/D462A)'. D202 is therefore the RT "
         "polymerase active site and D460 belongs to the TOPRIM nuclease active site.",
   resolved=True),
 ("9S1F","B"): dict(
   polymerase=[],
   non_polymerase={"TOPRIM (RNase-H-like) nuclease": [460,462]},
   basis="(b), same source as 9I2G_B. SINGLE-cluster chain whose only cluster {460,462} is the "
         "TOPRIM nuclease active site ('dTOPRIM (E374A/D378A/D460A/D462A)'), not the RT polymerase "
         "site. Contributes no polymerase structural truth. This is the reported EXTENSION above.",
   resolved=True),
}
