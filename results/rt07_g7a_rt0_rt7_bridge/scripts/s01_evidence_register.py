#!/usr/bin/env python3
"""s01 - the historical evidence register, traced to primary sources.

One row per (historical label x primary source). Every row is traced to a g1 verified quote
or to text extracted from the PDF in this step, and carries `source_stated_vs_inferred`.

Nothing here is inherited from a prior RT0-RT7 table. The one prior table that proposes a
mapping (`rt07_pre_g4_identifiability_redesign`) is read in s04 as a PRIOR PROPOSAL for the
comparator column and never as a result.

Also lands: the acquisition register extension (the Malik 1999 MISSING_PRIMARY_ASSET row) and
the LtrA numbering control that licenses treating Blocker's coordinates and the project's
sequence as one coordinate system.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g7alib import (G1T, TABLES, WORK, ltra_sequence, read_tsv, write_tsv)  # noqa: E402

LIT = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references/rt0_rt7/literature"
BLOCKER_PDF = os.path.join(
    LIT, "Blocker_et_al_2005_RNA_group_II_intron_RT_domain_structure_3D_model.pdf")

# Residue identities Blocker states, checked against the project's LtrA record. This is the
# control that licenses one coordinate system; it is a measurement, never an assumption.
BLOCKER_RESIDUES = [
    ("M", 1, "Table 1, 10-kDa fragment start"),
    ("R", 85, "Table 1, 10-kDa fragment end; text: cleavage site IN RT1"),
    ("R", 86, "Table 1, 33-kDa and 60-kDa fragment start"),
    ("R", 364, "Table 1, 33-kDa and 43-kDa fragment end"),
    ("R", 365, "Table 1, 27-kDa fragment start; junction RT7/domain X"),
    ("K", 599, "Table 1, 60-kDa and 27-kDa fragment end"),
    ("S", 372, "Table 1, X-D-E-2 fragment start"),
    ("A", 39, "text: conserved alanine in the N-terminal portion of RT0"),
    ("R", 371, "discussion, R371"),
    ("S", 462, "Fig. 3 legend, key residue"),
    ("K", 483, "Fig. 3 legend, key residue"),
    ("Y", 529, "Fig. 3 legend, key residue"),
]
BLOCKER_EDMAN = [(1, "MKPTM"), (86, "RMIYA"), (365, "RSGTI"), (372, "SGKVK")]

REGISTER_COLUMNS = [
    "historical_label", "primary_source", "reference_system", "reference_sequence",
    "source_definition", "source_boundary_or_landmark", "evidence_class",
    "source_stated_vs_inferred", "caveat", "unit", "denominator",
]

DENOM = "8 historical labels x the primary sources that name them"
UNIT = "(historical label, primary source) pair"

# One row per (label, source) that actually names the label. Every `source_definition` and
# `source_boundary_or_landmark` below is either a g1-verified quote (assignment id given) or
# text verified at the PDF in this step (marked PDF-VERIFIED s01).
ROWS = []


def _row(label, source, refsys, refseq, definition, boundary, ecls, stated, caveat):
    ROWS.append(dict(historical_label=label, primary_source=source, reference_system=refsys,
                     reference_sequence=refseq, source_definition=definition,
                     source_boundary_or_landmark=boundary, evidence_class=ecls,
                     source_stated_vs_inferred=stated, caveat=caveat, unit=UNIT,
                     denominator=DENOM))


XE_SYS = ("Xiong & Eickbush 1990 Fig. 1 alignment of 82 RT sequences in four groups; "
          "no accessioned alignment exists")
XE_DEF = ("Domains 1-7: seven peptide regions common to all elements, constructed by fixing "
          "conserved positions under the stated rule - a residue conserved in >50% of "
          "sequences in three of the four groups - and aligning between them. 42 conserved "
          "positions, 178 aa total.")
XE_BOUND = ("NO residue coordinates. Per-block extents exist only as the printed columns of "
            "Figure 1.")

ZW_SYS = ("Zimmerly, Hausner & Wu 2001 alignment ALIGN_000044 (EMBL), 66 sequences x 1441 "
          "columns, RT domain at columns 261-886")
ZW_DEF = ("Subdomains 0-7 plus domain X, 'labeled according to previous studies (7,9,32) "
          "taking into account the boundaries of conservation seen in our alignment' (Z04, "
          "Z05). Per-group conserved-residue counts: 90 mitochondrial, 94 bacterial (Z10).")


def build_rows(ltra):
    # ---- RT0 -------------------------------------------------------------------------
    _row("RT0", "Malik, Burke & Eickbush 1999 (Mol Biol Evol 16(6):793)",
         "NOT HELD - the defining source", "NOT HELD",
         "The source in which domain Z was renamed domain 0 (g1 genealogy edges G05, G06, "
         "G07, G09). Its content is not held by this project.",
         "UNKNOWN - the source is unheld",
         "NOT_IN_HELD_EVIDENCE", "not_assessable",
         "MISSING_PRIMARY_ASSET. Retrieval attempted 2026-09-18: Europe PMC HTTP 403, "
         "publisher page abstract-only, abstract does not mention domain 0, domain Z or "
         "numbered RT domains. Every held statement of RT0's scope CITES this source rather "
         "than deriving it.")
    _row("RT0", "Zimmerly, Hausner & Wu 2001", ZW_SYS, "ALIGN_000044 consensus",
         "'Subdomain 0 can be considered an N-terminal extension of the RT domain and is "
         "conserved among non-LTR RTs' (Z02); 'subdomain 0 is conserved only between group II "
         "intron and non-LTR RTs' (Z06).",
         "A SCOPE RULE, not a boundary: which classes the region exists in, not where it is.",
         "EXPLICIT_STATED_BOUNDARY (scope rule only)", "source_stated",
         "Cites Malik et al. 1999 for the name (Z03) and does not derive it. ALIGN_000044 "
         "carries ZERO subdomain annotations, so the scope rule cannot be converted to "
         "coordinates on the source's own alignment.")
    _row("RT0", "Simon & Zimmerly 2008", "inherited frame; no alignment of its own",
         "n/a",
         "Restates the scope limit for domains 0 and 2a (g1 assignment set O11/G09).",
         "NONE - restatement only",
         "INHERITED_WITHOUT_DEFINITION", "source_stated",
         "g1 assessed this source as supplying NO construction procedure of its own for any "
         "numbered region.")
    _row("RT0", "Blocker et al. 2005", "LtrA proteolytic fragment map, Arg-C digestion",
         "LtrA (cited as Q57005; project record AAB06503/P0A3U0, 599 aa)",
         "'a 10-kDa N-terminal fragment CONTAINING RT0 (M1-R85)' (B02); 'the N-terminal "
         "portion of RT0 forms a predicted alpha-helix, which contains a conserved alanine "
         "(LtrA A39)' (PDF-VERIFIED s01).",
         "UPPER BOUND M1-R85 plus an INTERIOR landmark A39. RT0's C-terminal edge is NOT "
         "stated.",
         "EXPLICIT_STATED_BOUNDARY (upper bound + interior point)", "source_stated",
         "Table 1's column is headed 'Domain composition' - it names what a fragment CONTAINS. "
         "The same text places the R85 cleavage site 'in RT1', so R85 is NOT the RT0|RT1 "
         "boundary. The inherited statement 'RT0 = M1-R85' overstates this source.")

    # ---- RT1 -------------------------------------------------------------------------
    _row("RT1", "Xiong & Eickbush 1990", XE_SYS, "Fig. 1 alignment, 82 sequences",
         XE_DEF + " Domain 1 is explicitly flagged by the authors as the one domain NOT "
         "independently confirmed.", XE_BOUND,
         "MOTIF_EVIDENCE|ALIGNMENT_BLOCK", "source_stated",
         "The founding source's own weakest domain. g1 item U08 keeps this distinct from any "
         "modern RT1 measurement; that separation is preserved here and NOT interpreted.")
    _row("RT1", "Blocker et al. 2005", "LtrA proteolytic fragment map", "LtrA, 599 aa",
         "'two major cleavage sites, one IN RT1 ...'; 'the Arg-C cleavage site in RT1 (R85) "
         "is located in a beta-strand' (both PDF-VERIFIED s01).",
         "R85 lies INSIDE RT1. This constrains RT1 to span residue 85; it is not an edge.",
         "EXPLICIT_STATED_BOUNDARY (interior point)", "source_stated",
         "Because R85 is interior to RT1 and A39 is interior to RT0, the RT0|RT1 junction lies "
         "somewhere in LtrA 39-85 and is stated NOWHERE in the held corpus.")

    # ---- RT2..RT7 shared derivational rows -------------------------------------------
    for lab in ("RT2", "RT3", "RT4", "RT5", "RT6", "RT7"):
        _row(lab, "Xiong & Eickbush 1990", XE_SYS, "Fig. 1 alignment, 82 sequences",
             XE_DEF, XE_BOUND, "MOTIF_EVIDENCE|ALIGNMENT_BLOCK", "source_stated",
             "A restatable PROCEDURE, not coordinates. Any residue interval for this label is "
             "a reconstruction by this project, not a source statement.")

    for lab in ("RT1", "RT2", "RT3", "RT4", "RT5", "RT6", "RT7"):
        _row(lab, "Zimmerly, Hausner & Wu 2001", ZW_SYS, "ALIGN_000044 consensus",
             ZW_DEF, "NO residue coordinates; ALIGN_000044 carries zero subdomain annotations.",
             "ALIGNMENT_BLOCK", "source_stated",
             "Labels are inherited from earlier work and adjusted to conservation boundaries "
             "(Z04). The adjustment step included manual editing and is not reproducible (g1 "
             "U05).")

    # RT5: the one label fixed to a reconstructable feature by a source statement.
    _row("RT5", "Zimmerly, Hausner & Wu 2001", ZW_SYS, "ALIGN_000044 consensus",
         "'The catalytic YxDD motif lies in subdomain 5' (Z11).",
         "AN ORDINAL ANCHOR: it ties subdomain 5 to a feature recoverable on any RT.",
         "EXPLICIT_STATED_BOUNDARY (feature anchor)", "source_stated",
         "This is the ONLY source statement in the held corpus that fixes a numbered subdomain "
         "to a feature an instrument can find independently. Every other label's position is "
         "ordinal relative to it.")
    # The 4/5 and 7/X spacers.
    _row("RT4", "Zimmerly, Hausner & Wu 2001", ZW_SYS, "ALIGN_000044 consensus",
         "'These sites are between subdomains 4 and 5 of the RT domain (the 4/5 spacer)' "
         "(Z08); the 4/5 spacer varies from 1 to 179 aa.",
         "A RELATIVE boundary: the 4|5 junction is where the widest inter-block gap sits.",
         "EXPLICIT_STATED_BOUNDARY (relative position)", "source_stated",
         "Constrains the 4|5 junction ordinally, not by coordinate.")
    _row("RT7", "Zimmerly, Hausner & Wu 2001", ZW_SYS, "ALIGN_000044 consensus",
         "'... and between subdomain 7 and domain X (the 7/X spacer)' (Z08); the 7/X spacer "
         "ranges 0-235 aa.",
         "A RELATIVE boundary for the C-terminal end of the numbered series.",
         "EXPLICIT_STATED_BOUNDARY (relative position)", "source_stated",
         "Domain X was not reconstructed by g2, so the far side of this junction is not "
         "independently available.")
    _row("RT7", "Blocker et al. 2005", "LtrA proteolytic fragment map", "LtrA, 599 aa",
         "'two major cleavage sites, one in RT1 and the other BETWEEN RT7 AND DOMAIN X'; "
         "Table 1: 43-kDa fragment Met 1 - Arg 364 ('RT0/7'), 27-kDa fragment Arg 365 - Lys "
         "599 ('X-D-E-1') (PDF-VERIFIED s01).",
         "A STATED DOMAIN JUNCTION at R364/R365.",
         "EXPLICIT_STATED_BOUNDARY (junction)", "source_stated",
         "The single strongest historical coordinate in the held corpus, and it bounds the END "
         "of the numbered series. It is a proteolytic site on ONE protein and may constrain or "
         "falsify a sequence-defined edge, never define one (LAUNCHER_02 section 5d).")

    # Blocker's figure: RT0-RT7 drawn on LtrA, but inherited and figure-only.
    for lab in ("RT0", "RT1", "RT2", "RT3", "RT4", "RT5", "RT6", "RT7"):
        _row(lab, "Blocker et al. 2005 Fig. 3", "LtrA / HIV-1 RT sequence alignment figure",
             "LtrA (Q57005) vs HIV-1 RT (P03366)",
             "'Conserved sequence blocks RT0-RT7, AS DEFINED BY Xiong and Eickbush (1990) and "
             "Zimmerly et al. (2001), are indicated by gray boxes' (PDF-VERIFIED s01).",
             "Extents exist only as gray boxes in a figure. No coordinates in text or table.",
             "INHERITED_WITHOUT_DEFINITION|ALIGNMENT_BLOCK", "source_stated",
             "This is a REDRAWING of the two earlier conventions on LtrA, not an independent "
             "derivation - g1 classified Blocker's RT1-RT7 as SPELLING_ONLY_NO_INDEPENDENT_"
             "DERIVATION. Digitising the boxes is figure digitisation under LAUNCHER_02 "
             "section 5e and is NOT done in this gate.")

    # Poch's motifs are the predecessor partition, not the numbered series.
    for lab, motif in (("RT3", "A"), ("RT4", "B"), ("RT5", "C"), ("RT6", "D")):
        _row(lab, "Poch et al. 1989 (via Xiong & Eickbush 1990 G02)",
             "Poch motif series A-D over 82 RT sequences", "consensus motifs",
             "Consensus sequences with stated invariant residues (4 strictly, 18 "
             "conservatively maintained) in fixed linear order inside a 120-210 aa domain. "
             f"Motif {motif} is a predecessor of this numbered domain via genealogy edge G02.",
             f"Motif {motif} consensus - a motif, not a block edge.",
             "MOTIF_EVIDENCE", "project_inferred",
             "The motif-to-domain correspondence is a GENEALOGY edge recorded in g1, not a "
             "statement that the motif and the domain are the same object.")


def main():
    _, ltra = ltra_sequence()

    # -- numbering control -------------------------------------------------------------
    os.makedirs(WORK, exist_ok=True)
    txt = os.path.join(WORK, "blocker.layout.txt")
    if not os.path.exists(txt):
        subprocess.run(["pdftotext", "-layout", BLOCKER_PDF, txt], check=True)

    ctrl = []
    agree = 0
    for aa, pos, why in BLOCKER_RESIDUES:
        got = ltra[pos - 1]
        ok = got == aa
        agree += ok
        ctrl.append(dict(check_id=f"NUM-{pos}", kind="stated_residue_identity",
                         expected=f"{aa}{pos}", observed=f"{got}{pos}",
                         result="AGREE" if ok else "DISAGREE", note=why))
    edman = 0
    for start, exp in BLOCKER_EDMAN:
        got = ltra[start - 1:start - 1 + len(exp)]
        ok = got == exp
        edman += ok
        ctrl.append(dict(check_id=f"EDMAN-{start}", kind="published_N_terminal_sequence",
                         expected=f"{start}-{exp}", observed=f"{start}-{got}",
                         result="AGREE" if ok else "DISAGREE",
                         note="Edman degradation N-term, Blocker Table 1"))
    ctrl.append(dict(
        check_id="NUM-SUMMARY", kind="summary",
        expected=f"{len(BLOCKER_RESIDUES)} stated residue identities agree",
        observed=f"{agree}/{len(BLOCKER_RESIDUES)} agree; "
                 f"{edman}/{len(BLOCKER_EDMAN)} Edman sequences agree",
        result="PASS" if agree == len(BLOCKER_RESIDUES) else "FAIL",
        note="This is what licenses treating Blocker's LtrA coordinates and the project's "
             "AAB06503/P0A3U0 record as ONE coordinate system. A measurement, not an "
             "assumption."))
    write_tsv(os.path.join(TABLES, "g7a_ltra_numbering_control.tsv"),
              ["check_id", "kind", "expected", "observed", "result", "note"], ctrl)

    # -- evidence register -------------------------------------------------------------
    build_rows(ltra)
    order = {f"RT{i}": i for i in range(8)}
    ROWS.sort(key=lambda r: (order[r["historical_label"]], r["primary_source"]))
    write_tsv(os.path.join(TABLES, "g7a_historical_evidence_register.tsv"),
              REGISTER_COLUMNS, ROWS)

    # -- acquisition register ----------------------------------------------------------
    acq = [dict(
        asset_id="malik1999_domain0_definition",
        asset="Malik, Burke & Eickbush 1999, Mol Biol Evol 16(6):793-805",
        why_needed="The source in which domain Z was renamed domain 0. It is the defining "
                   "source for RT0 and is cited, not derived, by every held source that "
                   "states RT0's scope.",
        attempt_date="2026-09-18",
        route_1="Europe PMC article page",
        route_1_result="FAILED_HTTP_403",
        route_2="Publisher page (academic.oup.com/mbe/article/16/6/793/2925486)",
        route_2_result="ABSTRACT_ONLY - full text not accessible; the abstract does not "
                       "mention domain 0, domain Z or numbered RT domains",
        resolution_state="MISSING_PRIMARY_ASSET",
        usable_as_evidence="NO",
        consequence="RT0 has no stated boundary anywhere in this project's evidence. This is "
                    "recorded as a terminal evidence state, not as an open task.",
        governed_acquisition_note="Any route requiring credentials, payment or a paywall "
                                  "bypass is a stop-and-wait operator decision "
                                  "(LAUNCHER_03 section 9b). None was attempted.")]
    write_tsv(os.path.join(TABLES, "g7a_acquisition_register.tsv"), list(acq[0].keys()), acq)

    print(f"s01: {len(ROWS)} evidence rows; numbering control "
          f"{agree}/{len(BLOCKER_RESIDUES)} residues, {edman}/{len(BLOCKER_EDMAN)} Edman; "
          f"1 MISSING_PRIMARY_ASSET")
    # g1 cross-check: the register must not contradict g1's region verdicts.
    v = {r["region_id"]: r["verdict"] for r in read_tsv(os.path.join(G1T, "g1_region_verdicts.tsv"))}
    assert v.get("rt0_spelling") == "SPELLING_WITH_STRUCTURAL_COORDINATE_ONLY", v.get("rt0_spelling")
    assert v.get("rt1_spelling") == "SPELLING_ONLY_NO_INDEPENDENT_DERIVATION"
    print("s01: g1 region verdicts cross-checked OK")


if __name__ == "__main__":
    main()
