# Provenance audit: retron RT "region X" and "region Y"

Read-only literature audit. Every statement below that is offered as evidence was read
verbatim in a retrieved text (see `XY_REGION_EVIDENCE.tsv`, column `retrieval_status`).
Anything I reasoned to rather than read is marked **INFERENCE**. Anything I could not read
is in the "Could not verify" list and is not used as evidence.

## 1. Citation corrections to the project's prior secondary notes

- Toro & Nisa-Martínez 2014 is **PLoS One 9:e114083** (PMID 25423096, PMC4244168), *not*
  Front Microbiol. The percentages quoted in the project notes (NAXXH 59%, H 100%, A 87%,
  N 62%; VTG 47% + 26% I/L) are verbatim correct, but their denominator is narrow (below).
- Mestre et al. 2020 (NAR 48:12632) does **not** cite Inouye 1999 for X/Y. It cites only
  **ref 28 = Simon, Ellington & Finkelstein 2019** — a review. Mestre 2020 adds no data.
- Toro & Nisa-Martínez 2014 cites **Inouye et al. 1999 for the Y region only**; its NAXXH /
  region X sentence carries **no citation at all**.

## 2. Provenance chain — region Y

1. **Inouye S, Hsu MY, Xu A, Inouye M. 1999, JBC 274:31236–31244** (ABSTRACT_ONLY).
   Primary experiment: domain exchanges between **RT-Ec86 (320 aa)** and **RT-Ec73 (316 aa)**
   (22% identity), 10 constructs. Verbatim: "the C-terminal 91-residue sequence of RT-Ec86
   was found to be essential for the recognition of the unique stem-loop structure and the
   branching G residue in the primer-template RNA for retron-Ec86". The abstract **never uses
   the labels "region X" or "region Y"**, gives no construct boundaries, and does not mention
   VTG or NAXXH. **INFERENCE**: 91 C-terminal residues of a 320-aa protein = residues 230–320.
2. **Lampson, Inouye & Inouye 2005, Cytogenet Genome Res 110:491–499** (ABSTRACT_ONLY,
   paywalled at Karger). **Simon & Zimmerly 2008 cite *this* review (their ref 15) as the
   source of "the retron-specific regions X and Y"**, and Simon et al. 2019 cite it (their
   ref 12) for the region Y definition. Whether the labels were coined here, or earlier in
   Inouye 1999, **could not be verified**. Wang et al. 2022 instead attribute the designation
   "X and Y" to Inouye 1999. The two attributions conflict and neither could be checked.
3. **Simon & Zimmerly 2008, NAR 36:7219** (FULL_TEXT) — first retrieved text using the labels:
   "Region Y lies within RT domain 7 and has been shown to be functionally important for
   recognizing the msRNA structure for the priming reaction".
4. **Simon, Ellington & Finkelstein 2019, NAR 47:11007** (FULL_TEXT) — the operational
   definition everyone now reuses: "Region Y is a ∼90 aa segment at the C-terminus… defined as
   beginning within motif 7 at a highly conserved VTG triplet and extending to the C-terminal
   end of the protein". This review is also where the Inouye experiments acquire residue
   numbers (below), second-hand.
5. **Mestre 2020 → the project's secondary notes.** Wording ("directs the RT to its cognate
   msr", "G the most conserved residue") originates at this step, not in any primary paper.

### Functional evidence strength for Y — how thin it actually is
- Deletion of region Y: **two RTs only**, Ec86 and Ec73 (reported second-hand by Simon 2019
  from Inouye 1999; readout "ability to bind their msrs").
- Region-Y **swap**: **one pair**, Ec86 ↔ Ec73, "produced chimeric proteins with 'swapped' msr
  recognition" (again second-hand from Inouye 1999; the primary text was unreadable, so the
  readout — in vivo msDNA production vs in vitro binding — is **unverified**).
- Purified-fragment binding (**Inouye et al. 2004, JBC 279:50735**, ABSTRACT_ONLY, primary):
  **RT-Ec86-(255–320)** binds the Ec86 primer-template RNA with Kd 5×10⁻⁸ M, and needs only
  an 8-bp stem + UUU loop; **RT-Ec73-(251–316)** cannot bind the Ec86 RNA but binds its own
  AGU-loop stem-loop. Reciprocal specificity, still **two retrons**.
- Simon et al. 2019 themselves flag the limit: "all region Y studies to date have focused on
  Retron-Eco1 (Ec86) and Retron-Eco3 (Ec73). Additional biochemical experiments will be
  required to confirm that region Y broadly recognizes the stem of its cognate msr in diverse
  retrons." **I found no source that tested Y-mediated RT–msr pairing across many retrons.**

### Does a residue-numbered Y interval exist?
Yes, but not for "region Y" as defined:
- **Ec86 numbering**: C-terminal 91 residues (⇒ 230–320, INFERENCE) from Inouye 1999;
  **255–320** for the fragment actually purified and shown to bind (Inouye 2004);
  **thumb = 238–320** from the Ec86 cryo-EM structure (Wang 2022); VTG = **243–245**.
- **Ec73 numbering**: **251–316** (primary, Inouye 2004 abstract). Simon et al. 2019 print
  "residues 251–311" for the same fragment — a **discrepancy** (Ec73 RT is 316 aa; 251–316 is
  the 66-residue fragment). Downstream users should take 251–316.
- Modern retron RTs give their own thumb boundaries: Eco7 Δ235–313 (deletion abolishes
  defence), Eco8 267–374 and 270–374 (two papers), Ec78 RT 311 aa.

## 3. Provenance chain — region X

1. No primary paper naming region X could be read. The **only** functional statement anywhere
   in the retrieved literature is second-hand, in Simon et al. 2019: "Deletion of region X from
   RT-Eco1 (Ec86) and RT-Eco3 (Ec73) does not block RT-cognate msr binding, but abrogates
   synthesis of the msDNA product, suggesting that it may be essential in reverse transcription
   initiation or catalysis (32)", citing **Inouye 1999** — whose *abstract* mentions no such
   deletion. This experiment is therefore **unverified at the primary level**.
2. Operational interval: "region X is a ∼16 aa segment that is between RT motifs 2 and 3"
   (Simon 2019), cited to **Toro 2014 and Zimmerly & Wu 2015** — both sequence surveys.
   There is **no residue-numbered X interval in any protein** in the retrieved literature; only
   motif positions: Ec86 NAxxH **105–109** (Wang 2022), Eco7 NAxxH **82–86** (NAR 2025),
   RT-Vmi1 NAXXH **90–94** (2025).
3. "H most conserved" traces to Toro 2014: NAXXH "identified in 59% of the sequences", and
   within those, H 100%, A 87%, N 62%. **Denominator = 102 retron-lineage RT sequences at
   ≤85% identity** from that survey — not all retrons, and the per-residue figures are
   conditional on the 59% subset. The "G most conserved" claim for VTG in Mestre 2020 has **no
   traceable numeric support** in Toro 2014, which gives no per-position VTG statistics.
4. Structural reading (Wang 2022, Ec86): "The NAxxH and VTG residues are in close proximity to
   the YADD active site"; Eco7 (NAR 2025): NAxxH and VTG "flank the YADD active site and likely
   stabilize it to promote catalysis". So the "essential for initiation or catalysis" language
   is now structurally plausible but still not directly tested by mutagenesis in anything I read.
5. Simon 2019 explicitly maps region X to group II intron **region 2a** (not domain X), and calls
   the active-site-stabilization idea a conjecture.

## 4. Is "VTG in RT7" the same object as "region Y directs the RT to its cognate msr"?

**No — these have been conflated, and the conflation is visible in the sources.**
- The msr-specificity evidence concerns a **C-terminal ~66–91 residue element** (Ec86 255–320 /
  230–320), i.e. the **thumb**. In the Ec86 structure every residue contacting the cognate msr
  recognition stem-loop RSLb is in the thumb: R238, Q240, S249, R257, R298, K261, R264, and
  loop-contacting H268/Y302 (Wang 2022). **VTG (243–245) is not among the listed RSLb contacts.**
- VTG itself sits **next to the YADD active site** (Wang 2022; Eco7 NAR 2025) and, in a
  predicted retron I-A structure, near the priming guanosine and the DNA backbone. That is a
  **catalytic/priming placement, not a specificity determinant**.
- Region Y as operationally defined (VTG → C-terminus) simply **contains** both: the VTG
  active-site element and the msr-binding thumb. Saying "the VTG triplet … directs the RT to
  its cognate msr" (Mestre 2020's phrasing, inherited by the project notes) **fuses a conserved
  catalytic-proximal motif with a variable RNA-binding domain**. Simon 2019 keeps them apart
  ("Beyond the conserved VTG, region Y is variable"). **Recommendation**: treat VTG-in-RT7 as a
  sequence marker and the thumb/C-terminal segment as the msr-recognition element, and do not
  infer pairing specificity from VTG identity.

## 5. Terminology hazard: group II "domain X" vs retron "region X"

- Group II / non-LTR: **domain X follows RT motifs 1–7 and is the thumb** (Blocker et al. 2005:
  "domain X is related structurally to the thumb of retroviral RTs"; Simon & Zimmerly 2008:
  "Downstream of the RT domain is domain X, which corresponds to the thumb of the polymerase").
- Retron **region X is between RT motifs 2 and 3** and is equivalent to group II **region 2a**.
- Both usages appear side by side in the same texts: Simon & Zimmerly 2008 Methods list
  "domain X for group II introns, regions X and Y for retrons, TR–VR repeats for DGRs";
  **Toro & Nisa-Martínez 2014 uses "the X domain" for the group II maturase domain in its
  Introduction and region "X" for the retron NAXXH region in its Results** — the highest-risk
  single document for confusion, and it is the source of the project's percentages.
- Second, subtler hazard: the retron element that later reviews call **region Y is the thumb**,
  and the group II object called **domain X is also the thumb**. So "domain X" (group II) is
  positionally homologous to retron **region Y**, not to retron region X. Inouye et al. 2004
  already called the Ec86 255–320 element a "putative 66-residue **thumb** domain"; modern
  retron structure papers use only "thumb" and never say "region Y".

## 6. Structural literature: what it says about X/Y (full-text searched)

- **Only Wang et al. 2022 (Ec86, PDB 7V9U/7XJG) names regions X and Y**, with numbers:
  NAxxH 105–109, VTG 243–245, YADD 195–198; Extended Data Fig. 7 delimits "the Y region" as
  only the β6–α11 loop plus α11 — i.e. **structurally, "region Y" in that paper is a small
  active-site-adjacent element, far smaller than the ~90 aa review definition.**
- NAxxH/VTG without the X/Y labels: Eco7 (NAR 2025, residues 82–86 / 236–238), retron I-A
  (Nat Commun 2025), Eco2 (Cell Discov 2025).
- **Null findings** (searched full text for "region X", "region Y", "NAxxH", "NAXXH", "VTG",
  zero hits): Retron-Eco7 Nat Commun 2025; Ec78 NSMB 2026 (9NNB); Ec78 Commun Biol 2026 (9VKZ);
  Eco2 NSMB 2026 (9I2F/9I2G/9S1F); Eco8 NAR 2026; Eco8 Nat Commun 2026 (9LBQ); Ec83 Science 2025
  (9E8Z). They all describe the same region only as the **thumb**.
- Convergent structural support for the *function* attributed to Y, in ≥5 retrons: the msr
  recognition stem-loop (RSLb/SL2) contacts the RT thumb in Ec86, Ec83, Ec78, Eco7, Eco8, Eco2;
  Mol Cell 2025 states "all four systems display a conserved interaction mode between RSLb and
  the RT thumb domain". Eco7 thumb deletion (Δ235–313) abolishes defence in vivo.
  **INFERENCE**: this is strong evidence that the C-terminal/thumb element *binds* the msr in
  many retrons; it is **not** evidence that region Y sequence *selects which* msr, since no
  structure paper performed a cross-pairing test.

## 7. Could not verify (NOT_RETRIEVED / ABSTRACT_ONLY)

- **Inouye 1999 JBC full text** — jbc.org, sciencedirect.com and linkinghub all HTTP 403
  (Cloudflare); not in PMC; Unpaywall lists only the blocked publisher page. ⇒ the region X
  deletion, the region Y deletion, the Y-swap readout, and whether the paper coined "X"/"Y"
  are all **unverified**.
- **Inouye 2004 JBC full text** — same 403s (abstract used).
- **Lampson, Inouye & Inouye 2005** (Karger 403) — the leading candidate for first naming X/Y.
- **Zimmerly & Wu 2015 Microbiol Spectrum** (ASM 403) — co-cited for the region X delimitation.
- **Carabias et al. 2024 Mol Cell (8QBK/8QBL/8QBM)** and **Cell Rep 2024 Ec86 filaments** —
  cell.com 403; unknown whether they mention X/Y.
- **Millman et al. 2022 Nature** and **Lopez et al. 2025 Nat Biotechnol retron census** — Europe
  PMC returned empty stubs; not read. The census is the most likely place to find many-retron
  RT/ncRNA pairing data and remains an **open gap**.
- Structures listed in the task but not located as papers here: **7XJG** is part of Wang 2022;
  **St85/9L7P**, **Ec67/9I2F–9S1F** (covered by Eco2 NSMB 2026), **Eco8 23OR/9LPA/9WN8/9X94/9X9B**,
  **9VHL** were not individually resolved to papers within the time budget.
- Xiong & Eickbush 1990 (RT motif numbering) — PMC copy is a scan with no machine-readable text.

## 8. One-line summary for downstream use

Region X = a survey-defined ~16 aa NAXXH segment between RT2 and RT3 with **no primary,
verifiable functional experiment** and no residue-numbered interval; region Y = a review-defined
~90 aa C-terminal segment whose msr-recognition function rests on **one RT pair (Ec86/Ec73)**
and whose only residue-numbered intervals are Ec86 255–320 and Ec73 251–316 — an interval that
modern structures call the **thumb**, which in group II intron nomenclature is **domain X**.
