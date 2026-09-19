# Provenance audit: fingers/palm/thumb boundary annotations for experimental RT structures

Read-only literature audit, 2026-09-19. All retrieved texts are cached under `cache/`
(sha256 in `SHA256SUMS.txt` and in the `cached_text_sha256` / `sha256` columns).
Primary retrieval route: RCSB entry JSON (primary citation PMID/DOI) -> Europe PMC
`fullTextXML` / NCBI `efetch db=pmc` -> plain text. Publisher sites (science.org,
cell.com, sciencedirect, nature.com, pnas.org, pmc.ncbi.nlm.nih.gov PDF) returned
HTTP 403 / bot challenges / paywall redirects for both `curl` and `WebFetch`, so no
paywalled text was read. Nothing that could not be read verbatim was recorded as a boundary.

Files:
- `LITERATURE_BOUNDARIES.tsv` — 73 boundary statements (one row per region per source).
- `SOURCES.tsv` — 49 sources with status (FULL_TEXT / ABSTRACT_ONLY / NOT_RETRIEVED / NOT_SEARCHED)
  and, where applicable, FIGURE_ONLY_NO_NUMBERS notes.
- `cache/` — retrieved XML/text; `citations.tsv`, `ids.tsv`, `pmc_map.tsv` — PDB -> PMID/PMCID map.

## Headline result

**Almost no primary structure paper numbers fingers/palm/thumb.** Of ~45 structures audited,
exactly **two** papers give explicit residue intervals for all three canonical RT subdomains —
and they are two papers about the *same* protein (Retron-Eco8) and they **disagree**.
Everything else is either (a) colour-coded schematics with no numbers in text or legend
(FIGURE_ONLY_NO_NUMBERS), (b) numbers only for *non-canonical* accessory domains
(tower, wrist, NTE-1, HEPN, Toprim, nitrilase, EN, DBD), or (c) construct/ordered-region
boundaries that are often mistaken for domain boundaries.

## Coverage by protein

| Protein (PDB) | Status |
|---|---|
| HIV-1 RT (1RTD) | Primary (Huang 1998) ABSTRACT_ONLY; Kohlstaedt 1992 ABSTRACT_ONLY; Jacobo-Molina 1993 ABSTRACT_ONLY (scanned PMC record). **Numbers only from secondary reviews** (London 2016; Singh & Das 2022; Vergara 2024) — and they disagree with each other. |
| MMLV RT (5VBS) | 5VBS primary (Singh 2017) FULL_TEXT: "fingers and palm domains", **no numbers**. Georgiadis 1995 and Das & Georgiadis 2004 ABSTRACT_ONLY (Elsevier 403). **No MMLV boundary numbers obtained.** |
| LtrA (5G2X) | FULL_TEXT. fingers-palm 82-360, thumb 424-473 (initial) / 391-474 (complete), EN 525-591 — all from homology-model docking in Methods. |
| GsI-IIC (6AR1) | FULL_TEXT. Only RT0 loop 23-31. Subdomains FIGURE_ONLY. |
| R.i./E.r. maturase (5HHJ/5HHK/5HHL) | FULL_TEXT. RT domain 12-305 (R.i., fig. legend), constructs 1-305 / 1-293. Fingers/palm/RT0/IFD FIGURE_ONLY. |
| Maturase 7UIM/7UIN, 6ME0/6MEC, 8FLI | FULL_TEXT, **no numbers** (thumb, DBD, thumb/X, IFD, RT0 named only). |
| Retron Ec86 (7V9U/7XJG/8QBK/8QBL/8QBM/7V9X) | **NOT_RETRIEVED** — Nat Microbiol and Mol Cell paywalled; 7V9X unpublished. No Ec86 boundaries. |
| Retron Eco8 (9X94/9X9B vs 23OR/9LBQ/9WN8) | **Both FULL_TEXT, full fingers/palm/thumb numbers, mutually contradictory** (see below). Third Eco8 paper (9LPA, Mol Cell) NOT_RETRIEVED. |
| Retron Eco2/Ec67 (9I2F/9I2G/9S1F) | FULL_TEXT. Trimerization loop 325-347, YADD 199-202. Subdomains FIGURE_ONLY. Second Eco2 paper (PMC12405507) also FIGURE_ONLY. |
| Retron Ec78/Eco7 (9NNB, 9VHE/9VHL, 9L7P) | FULL_TEXT x3. Only motifs/loops numbered (YADD 185-188, NAxxH 82-86, VTG 236-238, sensing loop 135-155). Subdomains FIGURE_ONLY. |
| Retron Ec83 (9E8Z), 9N69 | FULL_TEXT. YADD 183-186 only / nothing. Subdomains FIGURE_ONLY. |
| AbiK/AbiP2 (7R06/7R08), AbiA (8OZ7) | FULL_TEXT. Subdomains FIGURE_ONLY (AbiA Fig. 1A legend explicitly says the numbers are *on the figure*). Numbered: HEPN helices 510-540/565-585, motif 581-588, palm helix 251-266, RT->helical linker loops 290-310 (AbiA) and 286-294 (AbiK). |
| CRISPR RT 7KFT | FULL_TEXT. Only modelled/unmodelled ranges; RT domain brackets 383-616 within protomer 1-981. |
| DGR bRT (8UB7/8UBD) | FULL_TEXT. NTE/finger/palm/thumb named; **all numeric ranges in the paper are RNA nucleotides**, not protein residues. |
| DRT1 (9YFD) | FULL_TEXT. Nitrilase 934-1229; unresolved 382-478, 837-846. |
| DRT2 (9C0I) | FULL_TEXT, no numbers. 9LJE NOT_RETRIEVED. |
| DRT3 (9Z6Y/9Z6Z) | FULL_TEXT. Drt3a thumb beta-hairpin 323-338; Drt3b C-term 645-650, loop 112-169. |
| G2L4 (9D4S/9D5X) | FULL_TEXT. Thumb C-terminal extension 390-411 (a4 394-401, a5 407-411); RT3a helix 186-193. |
| 8BGJ (CART-CAPP; task list "UG26") | FULL_TEXT. "RT domain composed of the fingers-palm subdomains (RT; aa 1-204)" — fingers and palm not separated. |
| LINE-1 ORF2p (8C8J/8SXT, 8UW3, 9HDO) | FULL_TEXT x3. Rich numbering for tower/wrist/NTE-1/PIP/CTS, **none for fingers/palm/thumb**. |
| R2Bm (8GH6), R2Tg/R2Pm (9NL2/9NL3, 9DOU) | FULL_TEXT. No domain residue numbers anywhere (R2Bm numbers only reachable third-hand via Baldwin 2024: "tower-like" 305-374). |
| 24NC (DRT4), 26CZ (UG8), 9IOA (UG28), 9WY8 (DRT6), 9K6G (LINE-1), 9LPA, 9LJE | **NOT_RETRIEVED** (paywalled) or **NOT_SEARCHED** (no primary citation: 7V9X, 26CZ). |

## Inter-source disagreements (the main finding)

1. **Retron-Eco8, same protein, same numbering frame, incompatible splits.**
   - Xiong et al. 2026 NAR (9X94/9X9B): fingers **41-58**, palm **1-40 and 59-266**, thumb **267-374**.
   - Ji et al. 2026 Nat Commun (23OR/9LBQ/9WN8): fingers **1-100 and 115-167**, palm **101-114 and 168-269**, thumb **270-374**.
   Both place YADD at 198-201 and both PDB entries are author-numbered 1-374 (verified from RCSB
   `auth_to_entity_poly_seq_mapping`), so the frames agree and the disagreement is substantive:
   Xiong's "fingers" is an 18-residue beta-hairpin, Ji's "fingers" is 150+ residues. Ji et al.
   assign the PMG motif (163-165) to the fingers; under Xiong et al. those residues are palm.
2. **HIV-1 RT: no two secondary sources agree.** London 2016: F 1-84;119-154 / P 85-118;155-241 /
   T 242-313 / connection 314-426 / RNase H 427-560, with an explicit statement that these differ
   from Kohlstaedt et al. and Ding et al. Singh & Das 2022: F 1-85;118-155 / P 86-117;156-236 /
   T 237-318 / connection 319-426. Vergara 2024 agrees with Singh & Das on fingers.
   Zhao & Pyle 2016 (fig. legend) treat HIV p66 fingers+palm as residues **1-246**.
   The canonical numbers therefore enter the literature only through reviews, not through a
   verbatim primary statement that this audit could read.
3. **LINE-1 PIP box:** Baldwin 2024 "PIP box helix (residues 404-419)" in the *tower*;
   Ghanim 2025 "PIP box motif in the NTE domain of ORF2p (residues 407-415)".
4. **LINE-1 tower, internal to one paper:** Baldwin 2024 states 240-440 in one paragraph and
   239-440 in the next.
5. **LtrA thumb, internal to one paper:** Qu 2016 gives 424-473 (initial homology model) and
   391-474 (complete, built model).
6. **PtuA CTD (retron effector):** 478-550 (Li 2025, 9L7P) vs 480-551 (Dai 2025, 9VHE/9VHL).
7. **LtrA EN start:** Zabrady 2023 purified "RT domain of LtrA (aa 1-472) ... lacking the EN domain",
   whereas Qu 2016 models EN at 525-591 — i.e. 473-524 is unassigned by either statement.

## Numbering hazards (verified against RCSB where possible)

- **Fusion/tag constructs carry NEGATIVE author numbering in the PDB, so PDB author numbers match
  the native protein.** Verified via `auth_to_entity_poly_seq_mapping`:
  - 9WY8 (DRT6, MBP fusion): auth **-397 .. 564** — MBP+tag negative, RT native 1-564.
  - 9HDO (LINE-1 ORF2p, His/Strep/MBP-SUMO tag): auth **-521 .. 1275** — ORF2p native 1-1275.
  - 26CZ (UG8/DRT3b, SUMO fusion, Q12306): auth **-107 .. 667** — RT native 1-667.
  - 8BGJ (CART-CAPP, His-tag): auth **-19 .. 204** — native 1-204, matching the paper's "aa 1-204".
  The "+398 / +522 / +108" offsets in the task brief are therefore *sequence-index* offsets, not
  author-numbering offsets; papers' native numbers can be used directly against these PDB chains.
- 8C8J chain A: auth 238-1069, i.e. ORF2p full-length numbering, matching Baldwin's "core (238-1061)".
- 9X94 and 23OR chain A: both auth 1-374 (confirms the Eco8 conflict is not a numbering artefact).
- 5VBS chain A: auth 20-278 (native MMLV RT numbering; the paper quotes "modelled 24-278").
- 1RTD: p66 is entity 3 (chains A,C; 554 modelled residues), p51 is entity 4 (chains B,D; 440).
  The RCSB *instance* endpoint for 1RTD/A returned the 27-nt DNA template, so chain-letter
  assumptions for this old entry should be re-checked before use.
- 9L7P: the task list calls chain E "St85"; RCSB names the entity "Retron St85 family
  RNA-directed DNA polymerase" (a *family* name) and the primary paper (Li et al. 2025) studies
  the E. coli **Ec78** system, UniProt Q46666. Same for 9VHE/9VHL ("Retron-Eco7" = Ec78 family).
- 9DOU (R2Tg): the paper warns that ORF residue numbers are counted "from the earliest plausible
  start codon" because the true start codon is unknown — any R2Tg boundary is offset-uncertain.
- Zhao & Pyle Fig. 1a legend says "The finger subdomain is shown in blue and the **thumb** subdomain
  is shown in red" for a construct that has no thumb (RT domain 1-305 only) — apparent legend error;
  do not use that legend as a subdomain source.
- 9I2F chain A is a 67-residue chain; the Eco2 RT is not chain A in that entry (task list should be
  re-checked against the deposited chain IDs).

## What could not be verified

- No verbatim boundary statement was obtained for: HIV-1 RT primaries, MMLV RT (any paper),
  Ec86/Eco1, Eco8 third paper (9LPA), DRT4 (24NC), UG8 (26CZ), UG28 (9IOA), DRT6 (9WY8),
  LINE-1 9K6G, DRT2 9LJE. These are NOT_RETRIEVED/ABSTRACT_ONLY in `SOURCES.tsv`.
- Supplementary materials (where subdomain tables most plausibly live, e.g. GsI-IIC Fig. S1,
  Eco/DRT supplementary figures) were **not** retrieved; only the PMC main-text + figure legends
  + methods were parsed. This is the largest remaining gap and the obvious next step if
  institutional access is available.
- Image-only schematics were never read for numbers, by instruction.

## Practical implication for a fingers/palm/thumb annotation pipeline

There is no usable literature consensus to validate against: for 40+ of the audited structures the
primary paper supplies no residue-numbered subdomain definition at all, and for the one protein
where two papers do supply one, they contradict each other. Any FPT boundary set used downstream
will be *operationally defined* (structure-based, e.g. by transfer from a reference) rather than
literature-derived, and the four HIV-1 review variants above are the closest thing to a reference
standard — each of which disagrees at the 1-5 residue level, and Zhao & Pyle's palm end (246)
disagrees by ~10.
