# LAUNCHER — 03_rt0_rt7_closure

**Terminal closure of the historical RT0–RT7 nomenclature: what the labels meant in their
primary sources, and how far each can be defensibly cross-walked onto the frozen operational
conserved-state coordinate system.**

Track id: `rt07`. Gate id: `rt07_g7a_rt0_rt7_bridge`. Written 2026-09-18.

This launcher is a **supplement**, not a replacement. `launchers/LAUNCHER_02_rt0_rt7_definition.md`
remains planning authority for the `rt07` track and is not rewritten. This document exercises
the split that LAUNCHER_02 §3 already permits — *"A gate may be split if it does not fit one
execution and review unit; it may not be silently widened"* — by dividing LAUNCHER_02's `g7`
into two gates:

| gate | scope | status |
|---|---|---|
| **`g7a` — RT0–RT7 bridge** | the historical crosswalk only: question 5 of `results/rt07_g4b_production_mapper/docs/G7_STRUCTURE_PLAN.md` | **this launcher** |
| `g7b` — published and structural comparators | questions 1–4 of that plan, plus Toro 2014, Mestre 2020, myRT, Toro 2026, SPIRE and prior project conventions | unchanged, deferred, still governed by LAUNCHER_02 §7 |

`g7b` is **not** a prerequisite for `g7a` and `g7a` does not consume it. LAUNCHER_02's `g7`
row, its stop condition and its `C7 primary` weighting all pass to `g7b`.

Three rules this launcher restates, with their ids:

- **WA-A.4** — measure and report counts; do not conclude. Interpretation lands as `PROPOSED:`.
- **WA-G.5** — a null or refuting measurement is a result and lands like any other.
- **WA-S.1** — never guess silently and never stall; LOW-STAKES takes the default and continues.

---

## 1. Objective and success criterion

### The question

> **What do the historical RT0–RT7 labels actually mean in their primary sources, and to what
> extent can each historical region be defensibly cross-walked onto this project's frozen
> operational conserved-state coordinate system and the available structural/reference
> coordinates?**

### Three layers, kept apart

The gate reports three layers and **never forces them to coincide**:

| layer | what it is | its coordinate system |
|---|---|---|
| **historical / literature meaning** | what a primary source actually defined, and with what evidence class | the source's own reference sequence, alignment or figure |
| **operational conserved-state measurement** | the frozen instrument's `state_id` frame | `GII.deriv.hmm`, LENG 471, `hhmake -M 50` |
| **structural interpretation** | solved RT structures | PDB residue numbering, per entry |

A correspondence between two layers is a **measurement with a route and an uncertainty**, never
an identity. A label may be well defined historically and still have no operational
correspondence; that is a result (WA-G.5).

### The one measurement this gate makes

Everything else the crosswalk needs is already landed. Exactly one link is missing, and it is
named in the frozen bundle's own documentation:

> `results/rt07_g4b_production_mapper/docs/CROSSWALK_RT0_RT7.md`: *"g3 measured prior-frame match
> state → LtrA residue. Nothing has measured production state → LtrA residue or production state
> → prior-frame state. Producing that bridge is new measurement."*

**The gate's ONE measurement is therefore: production `state_id` → LtrA P0A3U0 residue, obtained
by applying the frozen instrument, unmodified, to the LtrA protein sequence and a small declared
reference panel — and the correspondence class that composing it with the landed
literature-derived LtrA coordinates does or does not support, per historical label.**

### Success criterion

The gate succeeds when all of the following hold:

1. every historical label RT0–RT7 has **one terminal evidence status** from
   `ESTABLISHED OPERATIONAL CORRESPONDENCE` / `PARTIAL / INTERPRETIVE CORRESPONDENCE` /
   `UNRESOLVED / NOT IDENTIFIABLE`, and a written statement of exactly what downstream analyses
   may say about it;
2. every row of the historical evidence register is traced to a **primary source**, with
   `source_stated_vs_inferred` recorded per row, and no row inherits a prior project table
   merely because it exists;
3. the crosswalk records one of `SUPPORTED_1_TO_1` / `SUPPORTED_1_TO_MANY` / `SUPPORTED_MANY_TO_1`
   / `PARTIAL` / `NO_SUPPORTED_CROSSWALK` / `UNRESOLVED` per label, with supporting frozen
   state(s), reference residue coordinates, mapping route and uncertainty where supported;
4. the bridge's positive and negative controls are reported **whatever they show**;
5. every landed number names its **frame, stratum, unit and denominator**.

**It is not necessary for all eight labels to resolve.** A terminal result of the form *"RT2–RT7
carry varying degrees of defensible historical correspondence, while RT0 cannot be given a
portable cross-family operational boundary from the available evidence"* is a full success if it
is supported.

### Stopping condition

The gate stops when every label carries a terminal status and the recorded uncertainty is
sufficient for thesis text and for `g7b` interpretation. **The gate does not keep trying methods
in order to convert `UNRESOLVED` into `SUPPORTED`.** At most **one bounded repair cycle** is
permitted, and only for a genuine load-bearing defect (§9b).

## 2. Kill criteria

Stated before any number exists, per LAUNCHER_SPEC.

- **Substrate kill.** If the frozen instrument does not commit on LtrA — sequence verdict is not
  `MAPPED` under the frozen rule — there is no bridge substrate. All eight rows land
  `NO_SUPPORTED_CROSSWALK`, the gate lands as a **negative result**, and it closes. The mapper is
  **not** adjusted to make LtrA map.
- **Positive-control kill.** `CAT_STATE` 262 must land on the LtrA catalytic `Y/FxDD` dyad — the
  frozen pattern: Y or F, then any residue, then D, then D. If
  it does not, the state→residue bridge is not demonstrated on the one coordinate the instrument
  commits to, every crosswalk row lands `UNRESOLVED`, and the gate closes as a negative.
- **Negative-control kill.** If a shuffled LtrA or a declared non-RT protein yields a confident
  mapping indistinguishable from real LtrA, the bridge measurement carries no information; all
  rows land `UNRESOLVED` and the gate closes as a negative.
- **Route kill.** If the only route that would resolve a given label is the comparator route
  (prior-frame points, §4 Route C) with no primary-evidence corroboration, that label lands
  `UNRESOLVED` rather than `SUPPORTED`. A comparator may corroborate; it may never resolve alone.
- **Budget kill.** Compute exceeding 2× the measured pilot estimate stops for diagnosis rather
  than pushing through.
- **Scope kill.** If closing a label would require re-deriving, re-fitting or re-parameterising
  the frozen instrument, that label lands `UNRESOLVED` and the gate closes with it unresolved.
  The instrument is never touched (§3).

## 3. Non-goals — out of scope

This gate is deliberately narrow. It does **not** become:

- another HMM, profile or mapper-development task;
- another validation campaign for the already-frozen mapper — Stage-2 validation is **CLOSED at
  Endpoint A** and is not reopened;
- a de novo motif-discovery project;
- a full RT phylogeny (stage 06);
- retron reclassification or subtype revision (stage 05);
- `g6` family-architecture analysis;
- any RT–ncRNA analysis (stages 07, 10);
- a generic fingers/palm/thumb segmentation project (stage 04);
- the remaining published-comparator campaign — that is `g7b`.

**Frozen objects this gate may read and may never modify:** the mapper code, `GII.deriv.hmm`, the
150 anchors, `CAT_STATE` 262, every threshold in `rtmap/params.py`, and all landed `g5` calls.

**The frozen g4b bundle is not edited.** Its `control/CROSSWALK_RT0_RT7.tsv` stays `UNRESOLVED`
in every row and `crosswalk.assert_unresolved_until_g7()` continues to pass, because the frozen
*production instrument* still emits no historical label — which remains true after this gate. The
resolution lands as this gate's own table, `tables/g7a_crosswalk_resolved.tsv`, and is adopted as
the interpretation layer of record by a decision record, never by rewriting a frozen bundle.

Structural evidence enters as **interpretation and challenge only**. It may agree with, disagree
with, or be non-comparable to the historical crosswalk. It may **not** be used to manufacture a
seven-way historical partition that the literature never defined (LAUNCHER_02 §3, §5d; operator
decision 2026-09-15 §B).

Discovered scope is not scope.

## 4. Inputs and trust grades

An ungraded input is `DO-NOT-USE` (WA-L.3). All inputs are read-only.

### Landed project evidence

| path | what it is | trust grade |
|---|---|---|
| `results/rt07_g1_history_and_definition/tables/g1_region_verdicts.tsv` | per-region evidence verdict over 32 region names, 6 sources | `FROZEN` |
| `results/rt07_g1_history_and_definition/tables/g1_operational_evidence_matrix.tsv` | per (source, region) operational capability, 7 `YES` / 18 `NO` | `FROZEN` |
| `results/rt07_g1_history_and_definition/tables/g1_evidence_quotes.tsv` | 36 verified quotes with page locators | `FROZEN` |
| `results/rt07_g1_history_and_definition/tables/g1_terminology_genealogy.tsv` | 12 genealogy edges, 6 to unheld sources | `FROZEN` |
| `results/rt07_g1_history_and_definition/tables/g1_unresolved_definition_register.tsv` | the open definitional questions, U01–U08 | `FROZEN` |
| `results/rt07_g1_history_and_definition/tables/g1_acquisition_source_resolution.tsv` | acquisition register to be extended by this gate | `FROZEN` |
| `results/rt07_g2_reference_reconstruction/tables/g2_ltra_mapping.tsv` | the six independently reconstructed blocks in LtrA residues | `FROZEN` |
| `results/rt07_g2_reference_reconstruction/tables/g2_reconstructed_blocks.tsv` | the same blocks in ALIGN_000044 columns | `FROZEN` |
| `results/rt07_g2_reference_reconstruction/tables/g2_block_uncertainty.tsv` | per-block start/end uncertainty across the declared sweep | `FROZEN` |
| `results/rt07_g2_reference_reconstruction/tables/g2_frame_correspondence.tsv` | cross-frame stability per block | `FROZEN` |
| `results/rt07_g2_reference_reconstruction/tables/g2_landmark_recovery.tsv` | 11 historical statements, recovery state each | `FROZEN` |
| `results/rt07_g2_reference_reconstruction/reference/g2_reference_set.faa` | the 66 ALIGN_000044 proteins, **including LtrA at 599 aa** | `FROZEN` |
| `results/rt07_g3_prior_method_replication/tables/g3_prior_region_correspondence.tsv` | prior RT1–RT7 landmark points on LtrA, four prior frames | `COMPARATOR` |
| `results/rt07_g3_prior_method_replication/tables/g3_rt0_object_audit.tsv` | the `OBJECT_MISMATCH` verdict for RT0 | `FROZEN` |
| `results/rt07_g3_prior_method_replication/tables/g3_handoff_to_g4.tsv` | the six constraints any bridge inherits | `FROZEN` |
| `results/rt07_g4b_production_mapper/` | the frozen instrument `rtmap-1.0.0/53a1e738a19b3896` | `FROZEN — READ AND EXECUTE ONLY` |
| `results/rt07_g4a_repaired/work/GII.deriv.hmm` | the frozen profile, LENG 471, sha256 `292495a4…` | `FROZEN — READ ONLY` |

### Primary literature

| path | what it is | trust grade |
|---|---|---|
| `references/rt0_rt7/literature/Xiong_Eickbush_1990_EMBO_J_*.pdf` | origin of domains 1–7 | `RAW — PRIMARY` |
| `references/rt0_rt7/literature/Zimmerly_Hausner_Wu_2001_NAR_*.pdf` | origin of subdomains 0–7, 2a, domain X in this lineage | `RAW — PRIMARY` |
| `references/rt0_rt7/literature/Poch_*_1989_EMBO_J_*.pdf` | motifs A–D | `RAW — PRIMARY` |
| `references/rt0_rt7/literature/Simon_Zimmerly_2008_NAR_*.pdf` | inherited frame, transferability benchmark | `RAW — PRIMARY` |
| `references/rt0_rt7/literature/Blocker_et_al_2005_RNA_*.pdf` | the modern RT0–RT7 spelling; the only source-stated LtrA residue coordinates | `RAW — PRIMARY (STRUCTURAL)` |
| `data/derived/rt07_external_assets/ALIGN_000044.{dat,aln}` | Zimmerly's own alignment, 66 seqs × 1441 cols | `ACQUIRED_VERIFIED` |
| Malik, Burke & Eickbush 1999, Mol Biol Evol 16(6):793 | **the defining source for domain 0 / RT0** | `MISSING_PRIMARY_ASSET` — see §5 |

### Structural comparators

| path | what it is | trust grade |
|---|---|---|
| `…/MELISSA_DATA/crystal_structures/5G2X.cif` | **LtrA P0A3U0 itself**, chain C, group II intron-encoded protein LtrA | `RE-DERIVE — PRIMARY STRUCTURAL COMPARATOR` |
| `…/MELISSA_DATA/crystal_structures/6AR1.cif` | GsI-IIC RT, *Geobacillus stearothermophilus*, His8-tagged, a **different protein** | `RE-DERIVE — SECONDARY` |
| `…/MELISSA_DATA/crystal_structures/7V9U.pdb` | *E. coli* retron Ec86 RT, untagged | `RE-DERIVE — SECONDARY` |
| `…/MELISSA_DATA/crystal_structures/reference_boundaries.{json,py,tsv}` | prior boundary extraction | **`DO-NOT-USE` — re-derive, never inherit** |
| non-LTR R2-type RT structure | not acquired | `DO-NOT-USE` — out of scope for this gate |
| `foldseek` | three local installs, no pinned build | `DO-NOT-USE` — not needed by this gate |

### Hard input exclusion — the anti-circularity rule

**No `g5` output is an input to this gate.** `g5_sequences.parquet`, `g5_states.parquet`,
`g5_catalytic.parquet`, `g5_state_occupancy.tsv`, `g6_readiness_by_family.tsv` and every other
catalogue-wide occupancy product are **`DO-NOT-USE`** here, for any purpose, and most especially
for choosing or adjusting a boundary.

The historical bridge is constructed from literature, reference and structural evidence
**independently of the catalogue-wide patterns it will later be used to interpret**. If the
bridge were tuned against g5 or g6 occupancy, any later statement of the form *"the g6 signal
localises to states X–Y, which overlap historical RTn"* would be circular. The gate's `run.sh`
reads no `g5` path, and `INPUTS.tsv` is the check: a `g5` row in it is a defect.

Likewise, **`g6` is not consulted**, has not been executed, and this gate is frozen before it is.

## 5. What might already exist

Absence is loud; wrongness is quiet.

### Already established, and not re-measured here

- **g1** traced 32 region names across 6 sources. Load-bearing results: the numbered series 1–7
  originates in Xiong & Eickbush 1990 as a **restatable procedure with no per-block residue
  coordinates**; "RT0"–"RT7" as spellings are Blocker 2005 and are
  `SPELLING_ONLY_NO_INDEPENDENT_DERIVATION`; Simon & Zimmerly 2008 supplies **no construction
  procedure of its own**; ALIGN_000044 carries **zero subdomain annotations**.
- **g2** reconstructed **six** blocks, not seven, on ALIGN_000044 and carried them to LtrA
  residues. Cross-frame: 5 of 6 one-to-one, median Jaccard 0.955; block 4 splits into 3.
- **g3** carried the prior RT1–RT7 landmark points onto LtrA (49, 102, 160, 213, 308, 344, 357),
  consistently across four prior frames, and ruled RT0 `OBJECT_MISMATCH`.

These are **inputs**, not questions. The gate re-derives none of them.

### Prior work that must not be inherited

- `results/rt07_pre_g4_identifiability_redesign/tables/historical_to_operational_mapping_proposed.tsv`
  is a **proposal**, produced before the mapper was frozen, and carries cardinalities
  (`1:1 candidate`, `many:1`, `NO_VALID_CORRESPONDENCE`). It is a **hypothesis to be tested by
  this gate's measurement**, never a result to be copied. Its rows may be quoted as "prior
  proposal" in the comparator table and nowhere else.
- The 29-block prior frame is **24/29 interpolated** between only 4 motif-anchored blocks. It is
  `COMPARATOR` grade throughout.
- `reference_boundaries.*` beside the crystal structures is a prior extraction and is `DO-NOT-USE`.

### Two corrections this gate carries, verified 2026-09-18

Both were found by reading the assets, and both correct a statement in the registered g7 plan.

1. **`6AR1` is not LtrA.** `docs/G7_STRUCTURE_PLAN.md` calls `6AR1` *"the group II intron RT
   structure and … the natural first crosswalk target"*. Read from the file, `6AR1` entity 1 is
   `GsI-IIC RT` from *Geobacillus stearothermophilus*, 417 modelled residues, His8-tagged.
   **`5G2X` entity 3 is `GROUP II INTRON-ENCODED PROTEIN LTRA`**, chain C, and its `auth_seq_id`
   numbering agrees with the P0A3U0 sequence at **487 of 487 modelled residues with zero offset**
   — Blocker's landmarks A39, R85 and R86 all confirmed *in the structure*. For a bridge
   denominated in LtrA numbering, **`5G2X` is the primary structural comparator**; `6AR1` is a
   secondary, tagged, different-protein comparator. This gate re-verifies the 487/487 agreement as
   a recorded control rather than inheriting the claim.
2. **The instrument emits 150 anchor states, not 471.** `rtmap-schema-1.0` is 150 rows per
   sequence plus `CAT_STATE` 262. The bridge therefore resolves historical regions onto **anchor
   states only**, and a historical *point* landmark will generally not coincide with an anchor.
   That asymmetry is designed into §7 Route C rather than hidden: interval-valued historical
   regions are resolvable in a way point landmarks are not.

### The one genuinely missing primary asset

**Malik, Burke & Eickbush 1999** (Mol Biol Evol 16(6):793–805) is the source in which domain Z was
renamed domain 0, per the g1 genealogy edges `G05`, `G06`, `G07`, `G09`. It is **not held**. Both
held sources that state RT0's scope (Zimmerly 2001, Simon 2008) **cite** it rather than derive it,
so RT0's definition reaches this project only as a scope statement at one remove.

Retrieval was attempted on 2026-09-18: Europe PMC returned HTTP 403 and the publisher page exposes
the abstract only; the abstract does not mention domain 0, domain Z or numbered RT domains. The
gate records this as a **`MISSING_PRIMARY_ASSET` row in the acquisition register** and proceeds.
Its consequence for RT0's terminal status is a finding, not an obstacle (§7, `S7`).

## 6. Claims this task tests

| id | role in this task |
|---|---|
| `C3` | `primary` |
| `C9` | `supporting` |
| `C7` | `supporting` |

Claim wording and status live only in `idea-stage/docs/research_contract.md`. Every claim is born
`UNPROVEN` there and this gate promotes none. `C7 primary` remains with `g7b`.

## 7. Gates

One gate is one measurement (WA-G.1). The gate lands a bundle whose `run.sh` reruns from the
landed inputs and reproduces its number (WA-G.2).

| gate id | the ONE measurement | weight | settles | stop condition |
|---|---|---|---|---|
| `rt07_g7a_rt0_rt7_bridge` | per historical label RT0–RT7, the correspondence class to the frozen `state_id` system, measured by composing landed literature-derived LtrA residue coordinates with a newly measured production `state_id` → LtrA residue map, with route and uncertainty retained per label | `FULL` | `C3` primary, `C9` supporting, `C7` supporting | done when `results/rt07_g7a_rt0_rt7_bridge/` reruns and reproduces the historical evidence register, the historical-to-operational crosswalk, the structural comparator table, the bridge figure and the closure decision, with all controls reported |

`FULL` because the closure decision becomes thesis and paper text and resolves a control table
that the frozen bundle currently holds open.

### 7a. Execution steps

The gate is one measurement executed in seven recorded steps.

| step | what it does | new measurement? |
|---|---|---|
| `S1` | **Historical evidence register** — one row per (historical label × primary source), built by tracing g1's landed verdicts, quotes and genealogy back to the PDFs, plus the Malik 1999 `MISSING_PRIMARY_ASSET` row | no — re-expression with tracing |
| `S2` | **Reference coordinate carriage** — assemble every historical LtrA-denominated coordinate by route (below), each tagged `source_stated` or `project_inferred` | no |
| `S3` | **The bridge measurement** — apply the frozen instrument, unmodified, to LtrA and the declared reference panel; emit `state_id` → LtrA residue; run the controls | **yes — this is the gate's number** |
| `S4` | **Crosswalk classification** — compose `S2` with `S3` and assign one correspondence class per label | no — derivation from `S3` |
| `S5` | **Structural comparator table** — `5G2X` primary, `6AR1` and `7V9U` secondary; agreement / disagreement / non-comparability, with an independence verdict per structure | yes — structural read-out |
| `S6` | **Bridge figure** — frozen state axis with only supportable historical regions drawn | no |
| `S7` | **Closure decision** — terminal status per label and the permitted downstream wording | no |

### 7b. The three coordinate routes, and what each may do

Every historical coordinate carried into `S2` is tagged with exactly one route. **The route
determines what the coordinate is allowed to resolve.**

| route | what it is | may it resolve a label alone? |
|---|---|---|
| **Route S — source-stated residue coordinate** | a residue boundary stated in a primary source. In the whole held corpus this is **only** Blocker 2005 on LtrA: a 10-kDa proteolytic fragment M1–R85 **containing** RT0 (not a boundary), R85 lying **inside** RT1, the conserved RT0 alanine at A39, and a cleavage site at R364/R365 described as between RT7 and domain X. **No source-stated RT0|RT1 boundary exists.** *[ERRATUM 2026-09-19, E-g7a-5: the earlier text here equated RT0 with the whole M1–R85 fragment and assigned RT1 onward to the residues after it — an interpretation withdrawn by Amendment 1 and removed on independent review — `docs/decisions/2026-09-19_stage2_g7a_review_errata.md`.]* | **yes**, and it is the strongest evidence available — but it is one protein, so what it resolves is a **LtrA-local** correspondence, never a portable cross-family one |
| **Route P — primary-derived interval** | the six g2 blocks in LtrA residues, reconstructed from ALIGN_000044 under Xiong & Eickbush's own stated criterion, with the landed per-block uncertainty attached | **yes**, with its uncertainty carried |
| **Route C — comparator point** | the prior-frame RT1–RT7 single-point landmarks on LtrA from g3 | **no.** May corroborate a label already supported by Route S or P; may never resolve one alone (§2, route kill) |

A label supported by Route S or P **and** corroborated by Route C is stronger than one supported
by Route P alone, and the crosswalk records which routes contributed.

### 7c. Correspondence vocabulary

Exactly one value per historical label.

| value | when |
|---|---|
| `SUPPORTED_1_TO_1` | the historical region maps to one contiguous run of frozen states, by Route S or P, with no competing assignment |
| `SUPPORTED_1_TO_MANY` | one historical region maps to several separated frozen state runs |
| `SUPPORTED_MANY_TO_1` | several historical labels map to one frozen state run — the expected outcome for RT5/RT6, which g3 already showed collapse onto a single g2 region |
| `PARTIAL` | part of the historical region has a supported correspondence and part does not, or the supporting route carries uncertainty wider than the region |
| `NO_SUPPORTED_CROSSWALK` | the composition is measurable and returns no correspondence — a positive negative |
| `UNRESOLVED` | the evidence needed to decide is absent, unheld or `OBJECT_MISMATCH` |

**No historical region is required to receive a frozen-state interval.** An unresolved or partial
region is drawn as such in the figure and is **never interpolated** between resolved neighbours.

### 7d. Controls, declared before running

| control | what it tests | what failure means |
|---|---|---|
| **PC-1 catalytic** | `CAT_STATE` 262 lands on the LtrA `Y/FxDD` catalytic dyad | bridge not demonstrated; §2 positive-control kill |
| **PC-2 structural numbering** | `5G2X` chain C `auth_seq_id` agrees with P0A3U0 at 487/487 modelled residues | the structural comparator carries an offset and is demoted to non-comparable |
| **PC-3 Blocker landmarks** | LtrA residues 39, 85, 86 are A, R, R in both sequence and structure | the LtrA numbering in use is not Blocker's; Route S is withdrawn |
| **NC-1 shuffled** | a seeded shuffle of LtrA does not produce a confident mapping | §2 negative-control kill |
| **NC-2 non-RT** | a declared non-RT protein of comparable length does not produce a confident mapping | §2 negative-control kill |
| **NC-3 no-g5** | `INPUTS.tsv` contains no `g5`/`g6` path | anti-circularity breach; the gate is void and re-run |

All controls are reported in the bundle **whatever they show** (WA-G.5).

### 7e. Required outputs

| product | file |
|---|---|
| historical evidence register — `historical_label`, `primary_source`, `reference_system`, `reference_sequence`, `source_definition`, `source_boundary_or_landmark`, `evidence_class`, `source_stated_vs_inferred`, `caveat` | `tables/g7a_historical_evidence_register.tsv` |
| historical-to-operational crosswalk — label, correspondence class, supporting frozen state(s)/interval, reference residue coordinates, mapping route(s), uncertainty, status reason | `tables/g7a_crosswalk_resolved.tsv` |
| the raw bridge — one row per (sequence, frozen state) with residue, call state and posterior | `tables/g7a_state_to_residue.tsv` |
| structural/reference comparator table with per-structure independence verdict | `tables/g7a_structural_comparators.tsv` |
| controls | `tables/g7a_controls.tsv` |
| closure decision — terminal status and permitted downstream wording per label | `tables/g7a_closure_decision.tsv` |
| unresolved items carried forward | `tables/g7a_unresolved_carried_forward.tsv` |
| acquisition register extension, incl. the Malik 1999 `MISSING_PRIMARY_ASSET` row | `tables/g7a_acquisition_register.tsv` |
| resolved-value summary with unit and denominator per row | `tables/g7a_summary.tsv` |
| the RT0–RT7 bridge figure, PNG **and** SVG, with its data TSV | `figures/g7a_bridge.{png,svg}` |

### 7f. What the bundle may and may not say

- It reports **counts and correspondence classes**. Any reading beyond that lands prefixed
  `PROPOSED:` (WA-A.4).
- It may **not** report an RT0 occupancy of any kind (g3 `OBJECT_MISMATCH`, carried forward).
- It may **not** describe the seven labels as a partition of the RT domain.
- It may **not** state that a family lacks a historical region: `DELETED_STATE` is an
  alignment-path state and non-detection is never biological absence.
- MyRT / PADLOC / DefenseFinder labels do not appear in this gate at all.

## 8. Compute

- Expected machine: **borg CPU**, local, `retron_tradicional`. No Ibex, no GPU, no job submission.
- Verified present in `/home/borg/miniconda3/envs/retron_tradicional/bin`: `hhmake`, `hhalign`,
  `hmmbuild`, `hmmalign`, `mafft`, `muscle`.
- Scale: the bridge runs the frozen instrument on a panel of **order 10 sequences**, against a
  landed g5 throughput of 369,381. Expected wall time is **seconds to a few minutes**.
- **Pilot first anyway.** Measure on LtrA alone before the panel, and record the measurement.
- Budget: **≤ 30 CPU-minutes total.** Exceeding 2× the measured pilot estimate is a §2 budget kill.
- **No full-catalogue pass.** No operation in this gate reads or scores the 501,561-sequence
  catalogue, and `data/derived/rt_exact_v1.{parquet,faa}` is not an input.

## 9. Autonomy: decide-alone vs stop-and-wait

### 9a. Decide alone and continue

- Membership of the reference panel, drawn from the landed `g2_reference_set.faa` and the declared
  structures, provided every member is recorded with its identity and length.
- The tie-breaking rule for assigning a historical point landmark to the nearest anchor state,
  **declared in writing before `S3` runs** and reported with the residue offset it produced.
- The choice of the seeded shuffle and the non-RT protein for NC-1/NC-2, recorded with the seed.
- Reporting thresholds that filter nothing (triage only), figure layout, table column order.
- Recording the Malik 1999 retrieval failure as `MISSING_PRIMARY_ASSET` and continuing.
- Landing a label as `UNRESOLVED` or `NO_SUPPORTED_CROSSWALK`. **Non-resolution never requires
  permission** (WA-G.5).
- Re-verifying rather than inheriting the `5G2X` 487/487 numbering agreement.

### 9b. Human gate — stop and wait

- **Any change to the frozen instrument**, profile, anchors, `CAT_STATE`, thresholds or any `g5`
  call. This is not an operator decision inside this gate; it requires a new decision record and
  reopens Stage-2 validation. The gate closes a label as `UNRESOLVED` instead.
- **Editing `results/rt07_g4b_production_mapper/control/CROSSWALK_RT0_RT7.tsv`** or any other file
  in a frozen bundle.
- **Resolving a label on Route C evidence alone** (§2 route kill).
- **Acquiring Malik 1999** by any route requiring credentials, payment or a paywall bypass.
- **Widening into `g7b`** — structures beyond the three declared, `foldseek`, DSSP
  fingers/palm/thumb segmentation, Toro/Mestre/myRT comparators, or the non-LTR R2 structure.
- **The single bounded repair cycle.** One repair is permitted for a genuine load-bearing defect
  found in review; a second is a stop-and-wait. "The result is unattractive" is never a defect.
- The two items LAUNCHER_02 §9b left deferred remain deferred and are **not** settled here:
  whether the operational method becomes its own methods paper, and how any RT1 concordance
  failure is interpreted (`U08`). This gate **measures** RT1 and does not interpret it.

### 9c. Write boundary

| what | where |
|---|---|
| scratch, disposable, gitignored | `ARIS_OUTPUT/rt07_g7a/` |
| the landed bundle | `results/rt07_g7a_rt0_rt7_bridge/` |
| the decision record adopting the crosswalk | `docs/decisions/2026-09-18_stage2_g7a_rt0_rt7_closure.md` |
| the LAUNCHER_02 split amendment | `docs/decisions/2026-09-18_stage2_g7_split_amendment.md` |

Nothing else is written. No frozen bundle, no `data/derived/` dataset, no `references/rt0_rt7/`
file is modified. `data/derived/rt07_external_assets/` is the governed acquisition cache and is
only appended to if an asset is actually acquired.

### 9d. Reporting architecture

The bundle satisfies BUNDLE_SPEC: `MANIFEST.tsv`, `INPUTS.tsv`, `OUTPUTS.tsv`, `env.lock`,
`run.sh`, `README.md` with a `STATUS:` line and the BS-14 six adversarial questions answered in
writing, and `PROVENANCE.md` carrying `env_lock_sha256`, `seed`, `agreements` sha and `models`.

`README.md` states, in its own words and before any correspondence is reported, that **historical
RT0–RT7 remains absent from every production column** and that this gate changes the interpretation
layer only.
