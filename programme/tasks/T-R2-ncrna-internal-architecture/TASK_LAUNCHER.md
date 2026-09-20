---
task_id: T-R2-ncrna-internal-architecture
governance_base: 9a793c9
base_commit: 0a220e3
base_branch: project-synthesis
stage_id: S09
title: Experimentally anchored internal architecture of retron ncRNA
state: DRAFT_AWAITING_SCIENTIFIC_REVIEW
autonomy_tier: A
compute_class: CPU_MEDIUM
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-R2-ncrna-internal-architecture
branch: task/T-R2-ncrna-internal-architecture
output_directory: analysis/t_r2_ncrna_internal_architecture/
hard_dependencies: ["T-R1b (ACCEPTED) — the 81 Tier-A coordinates", "T-X1b/T-X1c — overlap states, DESCRIPTIVE USE ONLY"]
populations_touched: ["PANEL-RTDNA-81 :: already spent by T-R1b, no further spend", "BUFFINGTON2025_RETRON_CATALOGUE :: EXTERNAL", "NCRNA-16458 :: Tier D, annotated NEVER validated"]
population_state: NO NEW CONFIRMATORY SPEND
confirmatory_spend: none
iteration_budget: 1
frozen: false
freeze_rule: WORKING_RULES §6b — NOT YET FROZEN
operator_authorisation: drafting authorised 2026-09-20; execution NOT authorised
---

# T-R2 · ncRNA internal architecture

⛔ **DRAFT. Not frozen, not executed.** No control has been run.

## 1 · The question

> **What experimentally anchored internal architecture is revealed by the 81 exact RT-DNA
> coordinates within their ncRNAs?**

Stage 2 then asks what **external comparative material** adds — without letting it become the
evidence.

## 2 · ⛔ The evidence hierarchy is the design, not a caveat

**Every coordinate this task emits carries its tier. A coordinate without a tier is not a result.**

| tier | source | strength | ⛔ limit |
|---|---|---|---|
| **A** | `T-R1b` — 81 **measured** RT-DNA extents, `EXACT_UNIQUE`, 81/81 | the only experimental coordinates in the project | 81 elements, one panel |
| **B** | published experimentally characterised retron architecture | external experimental anchors | ⚠️ each source must be **traced**, per the `T-A23c` failure — a title match is not an identification |
| **C** | Buffington native + modified msr-msd | external **predicted** architecture | ⛔ **not experimental truth**; bioinformatic identification |
| **D** | `NCRNA-16458` | the population to be annotated | ⛔ **CM-derived. It can be annotated; it can NEVER validate the covariance models that defined it** |

⛔ **The cycle that must not close:** `CM-CALLS` defines `NCRNA-16458`. Scoring a CM-derived
prediction against CM-derived calls adjudicates nothing. **Tier D is a target, never a truth set.**

## 3 · Stage 1 — characterise the 81 Tier-A systems

**Input: `T-R1b`'s `R1b_anchor_coordinates.tsv`, 81 rows, all `EXACT_UNIQUE`, all `REVCOMP`.**

⛔ **The R1b mapping is not redone and not reinterpreted.** Its 81 reverse-complement mappings
**establish the coordinate orientation** for everything below. Stage 1 consumes them as given.

### 3a · Per-element measurements

| measurement | note |
|---|---|
| ncRNA length | from the panel |
| RT-DNA length | from the panel |
| RT-DNA exact start / end | **from R1b**, 1-based inclusive |
| **normalised** start / end | position ÷ ncRNA length, so systems of different size are comparable |
| RT-DNA / ncRNA length fraction | |
| 5′ and 3′ flanking lengths | nucleotides outside the measured extent |
| **sequence context at both measured boundaries** | a declared window either side of the 5′ and 3′ RT-DNA termini |
| **predicted secondary-structure context at those boundaries** | RNAfold on the ncRNA; report the structural state at each boundary |
| subtype/family summaries | ⛔ **only where the annotation and n support it** — see §3c |

### 3b · What R1b already shows, and what Stage 1 must therefore explain

Computed **per element** from the landed R1b table and declared here so Stage 1 is not
rediscovering it:

| | min | median | max |
|---|---|---|---|
| RT-DNA / ncRNA length ratio | **0.3925** | **0.5455** | **0.8602** |
| nt 5′ of the RT-DNA | **0** | 55 | 126 |
| nt 3′ of the RT-DNA | **3** | 17 | 110 |

- The RT-DNA occupies about **half** its ncRNA at the median.
- It sits **internally** in all but one element (one is flush to the 5′ end).
- ⭐ **None is flush to the 3′ end; the minimum 3′ remainder is 3 nt.** A candidate landmark —
  **to be tested, not assumed.**

⚠️ **CORRECTED.** An earlier draft of this table reported a maximum ratio of **2.148** and made it
an anomaly Stage 1 had to explain, with those elements excluded from aggregates. **That was wrong,
and the error was mine, not the data's.** 2.148 is `max(rtdna_len) / min(ncrna_len)` computed
**across different elements** — the longest RT-DNA over the shortest ncRNA, two retrons never
compared to each other. The per-element maximum is **0.8602**, and **no element violates
`len(RT-DNA) <= len(ncRNA)`**.

⛔ **`R2_tierA_anomalies.tsv` is withdrawn and the exclusion rule with it.** There are no anomalous
elements; excluding them would have discarded real data to accommodate a bad statistic. Full
account: `R2_COORDINATE_FRAME_DIAGNOSIS.md`.

### 3b-gate · ⛔ BLOCKING pre-analysis consistency gate

**`r2_consistency_gate.py` runs before any Stage-1 measurement. Nothing runs if it fails.**
Demonstrated: **9 checks, 9 PASS.**

| check | result |
|---|---|
| R1b table sha256 `713237ac…58dca` | **PASS** |
| panel sha256 `80b2f565…d9577` | **PASS** |
| 81 anchors in both sources | **PASS** |
| **`len(RT-DNA) <= len(ncRNA)`** for all 81 | **81/81** |
| mapped span == `len(RT-DNA)` | **81/81** |
| `1 <= start <= end <= len(ncRNA)` | **81/81** |
| ⭐ **`revcomp(ncRNA[start:end]) == RT-DNA`** | **81/81** |
| all `EXACT_UNIQUE` | **81/81** |
| **per-element** max ratio ≤ 1.0 | **0.8602** |

⛔ **The ncRNA object R2 measures is verified byte-identical to the one R1b matched**, and
normalised coordinates are computed **only** from these verified objects.

⭐ `R2_GATE_revcomp_roundtrip` **re-derives R1b's result independently** from the coordinates and
the raw sequences, so Stage 1 cannot silently build on a mis-transcribed table.

⚠️ The gate is kept **permanently**, even though it passes. A statistic that mixed elements reached
a launcher; the invariant is now machine-checked rather than trusted.

### 3b-provenance · ⛔ BLOCKING INTERPRETIVE GATE — added after the adversarial pre-check

An adversarial pre-check (`R2_ADVERSARIAL_PRECHECK.md`) found that the RT-DNA fraction is **real**
— sd 0.1166 against a shuffled-pairing median of 0.2203, tighter than **100 %** of 2,000 random
re-pairings — and **subtype-structured**, with XIII, II-A1 and XI each holding it to within ±4 %.

⛔ **It also found the result may be circular, and the draft did not say so.**

**If the panel annotated its `ncRNA_sequence` boundaries by reference to the msDNA it observed,
then "the RT-DNA occupies ~58 % of its ncRNA" is true by construction and carries no biological
information.** The shuffled null does **not** detect this: shuffling breaks the pairing, so it tests
whether *this* RT-DNA matches *this* ncRNA — not whether the ncRNA bound was drawn using it.

This is the same error class this launcher already guards against for Buffington's
`ENGINEERED_DELTA`. **It applies to Tier A with equal force.**

| provenance of `ncRNA_sequence` | what Stage 1 may say |
|---|---|
| annotated **independently** of the RT-DNA | the fraction and normalised coordinates are interpretable as **architecture** |
| **derived from** the observed RT-DNA extent | ⛔ the fraction is **definitional**; only *residual* structure retains meaning (e.g. why XIII is tight and I-C1 is not) |
| **cannot be established** | report **with the ambiguity stated**, never as architecture |

⛔ **Stage 1 may COMPUTE the fraction regardless. It may not INTERPRET it as architecture until this
is resolved.** Resolving it is a **Tier-B** question requiring the panel's own publication, traced —
and **Tier B is currently empty**.

⚠️ **Effective n is ~23, not 81.** The 81 elements span 23 `retron_sub` values; 8 strata reach
n ≥ 5, covering 57 of 81; 8 are singletons. The §3c rule is necessary but does not by itself fix
the independence problem.

### 3c · Stratification rule, declared in advance

Subtype/family summaries are reported **only** for strata with **n ≥ 5**, and every stratum's n is
printed beside its statistic. ⛔ **No stratum statistic is computed on fewer than 5 elements**, and
the 81 are **not** a random sample of retrons.

## 4 · Stage 2 — Buffington as external comparative material

**All 105 published native/modified msr-msd pairs are evaluated**, not only the 11 that overlap our
ncRNA catalogue exactly. Coverage and architecture are different questions.

For each of the 105:

1. **Align native against modified** msr-msd.
2. **Identify the exact `ENGINEERED_DELTA`** — the difference between them.
3. **Retain insertions, deletions and replacements explicitly**, with coordinates. Not summarised
   to a length difference.

⛔ **The delta is called `ENGINEERED_DELTA` and nothing else.** It may **not** be called `msd`,
`template`, `a1` or `a2` **until the experimental construct design supports that interpretation.**
A repair template is inserted where the engineers chose to put it, which may or may not coincide
with a natural boundary. **Verifying construct design is a prerequisite for any such promotion, and
it is not part of this task.**

⛔ **`T-X1b`/`T-X1c` overlap states are used ONLY to describe each system's relationship to our
resource** — `PAIR_EXACT_PRESENT` 5 · `RT_ONLY` 51 · `NCRNA_ONLY` 6 · `NEITHER` 43. They are **not**
an architecture signal and carry no weight in any coordinate call.

## 5 · Methods — each tied to a question, none chosen for availability

**All verified present** (the `PROPOSAL_OUTLINE` flagged CMfinder and R-scape as unverified; that
prerequisite is now resolved):

| method | path | the ONE question it answers | ⛔ not for |
|---|---|---|---|
| exact / local alignment | (R1b, done) | where is the measured RT-DNA? | anything general |
| pairwise native↔modified | Biopython 1.87 | where is the `ENGINEERED_DELTA`? | calling it an msd |
| **MAFFT / Q-INS-i** | `dep_maps/bin/mafft` | within a subtype, do Tier-A boundaries fall at alignable positions? | cross-family alignment |
| **RNAfold / RNAalifold** | `~/.local/bin` | what structure sits at a measured boundary? | ⛔ a prediction is not a measurement |
| **CMfinder / Infernal** | `retrons/bin/cmfinder`, `cmbuild`, `cmalign` | can a Tier-A-anchored model propagate to homologues? | ⛔ evaluation against CM-derived calls |
| **R-scape 2.0.4a** | `retron_tradicional/bin/R-scape` | is a proposed pairing supported by covariation? | significance without its assumptions stated |

⛔ **Propagation (MAFFT → CMfinder/Infernal → R-scape) is Stage 3 and is NOT authorised by this
launcher.** Stages 1 and 2 are descriptive and external-comparative. **Stage 3 requires its own
review**, because that is where Tier D enters and where the circularity risk lives.

## 6 · Outputs

| file | tier | contents |
|---|---|---|
| `R2_tierA_geometry.tsv` | **A** | 81 rows: lengths, exact and normalised coordinates, fractions, flanks |
| `R2_tierA_boundary_context.tsv` | **A** | sequence and predicted structure at both measured boundaries |
| `R2_tierA_strata.tsv` | **A** | subtype summaries, **n ≥ 5 only**, each with its n |
| `R2_tierC_engineered_delta.tsv` | **C** | 105 rows: delta coordinates, insertions/deletions/replacements, **labelled `ENGINEERED_DELTA`** |
| `R2_candidate_coordinates.tsv` | **A–D** | every candidate element with `evidence_tier`, `confidence`, `source`, and an explicit `UNRESOLVED` state |
| `R2_controls.tsv` | | §7 |

⛔ **No single unqualified annotation is emitted anywhere.**

## 7 · Controls — proposed, to be demonstrated before freeze

| control | type | must show |
|---|---|---|
| **the full §3b-gate battery** | blocking | **9 checks, demonstrated 9 PASS** — see §3b-gate |
| `R2_POS_synthetic_delta` | blocking | a constructed native/modified pair with a known 81 nt insertion at a known position is recovered exactly |
| `R2_NEG_identical_pair` | blocking | a native/modified pair that is **identical** yields an **empty** delta, not a spurious one |
| `R2_GATE_tier_required` | blocking | **no row in `R2_candidate_coordinates.tsv` may lack an `evidence_tier`** |
| `R2_GATE_no_tierD_validation` | blocking | no output scores a Tier-D-derived call against a CM-derived truth set |

⚠️ `R2_POS_coordinate_roundtrip` is the important one: it re-derives R1b's result **independently
from the coordinates**, so Stage 1 cannot silently build on a mis-transcribed table.

## 8 · STOP conditions

| condition | action |
|---|---|
| R1b table hash or row count mismatch | **STOP** before any measurement |
| any blocking control fails | **STOP**, `VOID`, escalate, **new task ID** |
| a candidate coordinate would be written without a tier | **STOP** |
| the consistency gate fails on any of its 9 checks | **STOP before any Stage-1 measurement.** No table written |
| Stage 3 propagation is attempted | **STOP** — it is not authorised by this launcher |

## 9 · Interpretation ceiling

⛔ Candidate architecture coordinates **with explicit evidence tiers**. **Not** a validated
annotation of retron ncRNA architecture, **not** a replacement for experimental determination,
**not** evidence about the covariance models that defined Tier D, and **not** an msd/a1/a2 call
anywhere the construct design has not been verified.

**Tier A is 81 elements from one published panel.** Everything else is external, predicted, or
CM-derived, and is labelled as such in every row it touches.
