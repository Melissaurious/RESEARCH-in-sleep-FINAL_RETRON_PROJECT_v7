# Stage 3B — bounded follow-up: PDB 9Z6Y (elongating EcDRT3)

**Scope:** one structure. Rules applied **unchanged**; no threshold moved, no rule added.
Stage 3A untouched. `ANTICIRCULARITY_CONTRACT.tsv` untouched.

**Acquisition.** `9Z6Y.cif`, HTTP 200, 7,551,713 bytes,
sha256 `f4e826146521453aef8af65f82e92b8f0b6f582e455b58f506494ebf5be7ed2f`, landed in
`data/stage3b_external_structures/` and logged in `FETCH_LOG.tsv` in the same format as the other
ten external structures.

---

## 1 · What the coordinates show

| | |
|---|---|
| title | *Structure of the elongating EcDRT3 reverse transcriptase in complex with its non-coding RNA* |
| method / resolution | cryo-EM, **2.6 Å** |
| entities | 1 Drt3a RT (chains A–F, 415 res, 2–420) · 2 Drt3b RT (chains H–M, 626 res, 4–650) · 3 ncRNA (R–W, 113 nt) · 4+5 two cDNA strands per protomer (17-mer poly-TG, 18-mer poly-CA) · 6 **MG ×18** · 7 **POP ×6** · 8 water |
| metal placement | **6 Mg on Drt3a** (one per chain, seqid 501) and **12 Mg on Drt3b** (two per chain, 701/702) |
| POP placement | Drt3b only (seqid 703) |
| PTR | phosphotyrosine as the **C-terminal residue 650 of Drt3b** — the protein primer |
| author site records | **none** (`_struct_site` empty) |

### Chain A — Drt3a, RVT-UG3

`METAL_CAT` at **D115 (1.99 Å)** and **D197 (2.01 Å)** from the single Mg A501; their carboxylates
are **2.78 Å** apart, so one cluster under the frozen 8.0 Å site-locality rule → **HARD_PAIR**.
D198 lies 3.88 Å from the same Mg — *outside* the frozen 3.2 Å cut, recorded, **not counted**.
D197 is also within 2.92 Å of nucleic acid.

### Chain H — Drt3b, RVT-UG8

`METAL_CAT` at **D192 (2.08 Å)**, **D291 (2.04 Å)** and **D292 (2.31 Å)**, across **two** Mg ions
(H701, H702) — a genuine two-metal-ion polymerase centre. Mutual carboxylate distances 3.24 / 2.97 /
3.56 Å → one cluster → **HARD_PAIR**. Pyrophosphate P1 is 4.79 Å from D192.

### Is it the polymerase site, or another domain?

**Polymerase, unambiguously, in both chains.** Each chain yields exactly **one** hard-evidence
cluster, so the site-attribution rule is not triggered. Each cluster is a motif-A Asp plus the
motif-C Asp pair, coordinating Mg, in contact with the nucleic-acid duplex, with the reaction
leaving group adjacent in Drt3b. No second metal-carboxylate centre exists in either chain — unlike
HIV-1 RT (RNase H) or Ec67 (fused nuclease).

---

## 2 · Primary paper

**Deng P, Lee H, Armijo C, Wang H, Gao A.** *Protein-templated synthesis of dinucleotide repeat DNA
by an antiphage reverse transcriptase.* **Science 2026 Jun 18;392(6804):1274-1281.**
DOI `10.1126/science.aed1656` · PMID `41990131` · **PMC13533446**, full text read.

| evidence class | what the paper supports |
|---|---|
| **coordinate-derived** | *"The atomic models for the elongating and resting state hexamers have been deposited in the PDB under accession codes **9Z6Y** and **9Z6Z**, respectively."* The state assignment is the authors' own. |
| **author catalytic-site assignment** | Drt3a **YVDD** motif named (*"Tyr195 (from the YVDD motif)"*, Y195–D198); Drt3b active site at D291/D292 |
| **biochemical / mutational** | *"Catalytic mutants (YVAA) denote the following alanine substitutions: EcDRT3a (**D197A/D198A**), EcDRT3b (**D291A/D292A**)"*; the Drt3b mass shift *"was abolished in complexes harboring a Drt3b active site mutation (D291A/D292A) but retained with a Drt3a mutation (D197A/D198A)"*; both mutants lose anti-phage activity |
| **mechanistic interpretation** | Drt3b synthesises poly(AC) ssDNA *de novo* without a nucleic-acid template, covalently attached to the protein; Drt3a is templated by the ncRNA. This is interpretation and is **not** used as truth |

**Two asymmetries worth recording.** The paper names **D197/D198** for Drt3a and **D291/D292** for
Drt3b; the coordinates additionally place **D115** (Drt3a) and **D192** (Drt3b) on the catalytic
metal, and **neither is mentioned anywhere in the paper**. Conversely, the accessible text contains
**no mention of Mg or of a two-metal mechanism** — here the metal is coordinate-derived only, the
exact mirror image of the Eco8 case, where the metal was asserted in text and absent from every
deposited model.

---

## 3 · Relationship to 9Z6Z

Construct (SEQRES) comparison, the frozen grouping procedure:

| chain | 9Z6Y | 9Z6Z | verdict |
|---|---|---|---|
| A — Drt3a | 426 aa, sha256 `ddef78bade1141c5…` | 426 aa, sha256 `ddef78bade1141c5…` | **byte-identical** |
| H — Drt3b | 650 aa | 650 aa | **1 positional difference, at residue 650 only**, where 9Z6Y writes the canonical code `Y` and 9Z6Z writes `X` for the same modelled **PTR**. The protein is the same; the difference is annotation |

So `9Z6Y_A` joins **RG30** and `9Z6Y_H` joins **RG31** — the existing 9Z6Z groups. 9Z6Y is the
**elongating** state, 9Z6Z the **resting** state, of one system.

---

## 4 · Effect under the frozen rules

| | before | after |
|---|---|---|
| `RG30` Drt3a (UG3) | `NONE` | **`HARD_PAIR`** |
| `RG31` Drt3b (UG8) | `HARD_PAIR` | `HARD_PAIR` — conformational replicate; adds the second Mg, adds D192, adds verified literature |
| cluster `C30_20` | `C_no_truth_yet` | **`A_calibration`** |
| cluster `C30_09` | `A_calibration` | unchanged |
| Tier A — clusters / groups / chains | 10 / 18 / 31 | **11 / 19 / 34** |
| Tier B | 3 / 4 / 17 | unchanged |
| Tier C | 7 / 9 / 12 | **6 / 8 / 11** |
| register rows | 60 | **62** |

**For Drt3a this is a genuine class change; for Drt3b it is a conformational replicate only.**

### Denominators

| stratum | before | after |
|---|---|---|
| **retron** groups (6) | 1 `HARD_SINGLE`, 1 `FUNCTIONAL_PAIR`, 1 `HARD_MULTISITE_UNRESOLVED`, 3 `NONE` | **unchanged** — EcDRT3 is a DRT, not a retron |
| **defence-RT (UG/DRT)** groups (9) | 5 `HARD_PAIR`, 1 `HARD_SINGLE`, **3 `NONE`** | **6 `HARD_PAIR`**, 1 `HARD_SINGLE`, **2 `NONE`** |
| all bacterial groups (25) | 9 `HARD_PAIR`, 2 `HARD_SINGLE`, 1 `FUNCTIONAL_PAIR`, 1 multisite, 12 `NONE` | **10 `HARD_PAIR`**, 2, 1, 1, **11 `NONE`** |

---

## 5 · Rule behaviour — three gaps found, none repaired, none consequential here

Reported rather than fixed, per instruction. **No verdict in this follow-up depended on any of them**;
both chains are `HARD_PAIR` on metal coordination alone.

1. **`POP` (pyrophosphate) is not in the frozen `NT_CODES` set.** The frozen substrate rule covers
   dNTP/NTP and analogues; it has **no category for a reaction product or leaving group**. So the
   pyrophosphate 4.79 Å from Drt3b D192 — direct evidence of a post-chemistry polymerase state —
   contributes nothing. `g2` should decide whether product ligands count, and must decide it for all
   62 chains at once, not for this one.
2. **`PTR` (phosphotyrosine) has no category.** It is the C-terminal residue of Drt3b *and* the
   protein primer for DNA synthesis. The frozen rules treat it as neither residue nor ligand.
3. **Coordinate-derived and literature-derived residue sets can disagree at one member.** Drt3a:
   coordinates give {D115, D197}; the paper's mutational pair is {D197, D198}. They overlap at D197
   and each names a residue the other does not. The frozen rules have no reconciliation procedure —
   they simply record both. `g2` must state how a truth label is formed when the two sources are
   partially disjoint.

**Not a defect, recorded for completeness:** in Drt3a both hard residues coordinate the *same single*
Mg ion. The frozen `HARD_PAIR` rule accepted that, and it gave the biologically correct answer — the
motif-A and motif-C aspartates.
