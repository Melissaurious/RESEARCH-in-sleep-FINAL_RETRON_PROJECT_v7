# LAUNCHER — 02_rt0_rt7_definition

**Historical derivation and operational reconstruction of RT subdomains 0–7 across bacterial
RT diversity, with particular focus on retron RTs.**

Track id: `rt07`. Written 2026-09-15. Stage 1 is complete and its bundles are landed.
This launcher is planning authority for the track; a session's reading of what the work
"obviously" needs does not override it (WA-L.1).

Three rules this launcher restates, with their ids:

- **WA-A.4** — measure and report counts; do not conclude. Interpretation lands as `PROPOSED:`.
- **WA-G.5** — a null or refuting measurement is a result and lands like any other.
- **WA-S.1** — never guess silently and never stall; LOW-STAKES takes the default and continues.

---

## 1. Objective and success criterion

### The question

> **What operational sequence definitions of the historically described RT subdomains 0–7
> are supported by primary evidence, how reproducibly can those definitions be transferred
> across bacterial RT diversity, and what patterns of presence, absence, divergence,
> expansion and truncation do they reveal, particularly in retron RTs?**

The task is **not** "assign RT0–RT7 to all RTs". That phrasing presumes the answer to the
transferability question this track exists to measure.

### The design must be able to return non-transferability

A legitimate, publishable outcome is that **RT1–RT7 form a broadly operational sequence
framework while RT0 is a historically narrower homology concept** that requires a separate
test in retrons. RT0 is therefore never scored on the same footing as RT1–RT7 by default,
and no gate may report a single "RT0–RT7 occupancy" number that hides the distinction.

The prior dossier records the primary-source basis for treating RT0 separately
(`general/RETRON_STAGES/02_rt0_rt7_definition.md` §0b, quoting Zimmerly, Hausner & Wu 2001
p.1241 that subdomain 0 is conserved only between group II intron and non-LTR RTs). That is
a **prior reading to be re-verified at the PDF in `rt07_g1`**, not an input assumption.

### Success criterion

The track succeeds when all of the following hold:

1. every region name in scope (motif, conserved block, domain, subdomain, RT1–RT7,
   subdomain/domain 0, RT0, domain X, 2a) is traced to the primary source that used it, with
   its evidence class recorded — motif evidence, alignment block, explicit stated boundary,
   terminology only, or inherited-without-definition;
2. an operational per-block detector exists that emits a **call state and an uncertainty
   interval** per (exact RT, block), derived on a conservative full-length set and evaluated
   on a held-out population whose independence from the seed is measured and reported;
3. the eligible Stage-1 exact-RT catalogue is scored with family, MULTI and completeness
   strata retained, and non-detection is never reported as biological absence;
4. every landed number names its **frame, stratum, unit and denominator**;
5. the reusable datasets in §7c exist as landed tables, not only as figures.

Failure to transfer a block is a result, not a failed track.

## 2. Kill criteria

Stated before any number exists, per LAUNCHER_SPEC.

- **`rt07_g1` kill:** if the primary literature cannot be shown to supply any stated
  boundary, alignment block or reproducible landmark for a region, that region is recorded
  `NO_OPERATIONAL_BASIS` and is **not** given a boundary later in the track. If that is true
  of most regions, the track lands as a negative historical result and stops before `g4`.
- **`rt07_g2` kill:** if the historical landmarks cannot be recovered on the sequences and
  alignments from which they were derived, the reconstruction arm stops. A frame that cannot
  be rebuilt on its own source data may not be propagated to 501,561 sequences.
- **`rt07_g4` kill:** if no validation population can be constructed whose seed overlap is
  measured and materially below the prior `anchors72` state, the detector lands with
  **calibration declared unestablished** and `g5`/`g6` report call states without accuracy
  claims. The track does not manufacture an independent validation set by relabelling.
- **Whole-track kill:** if `g3` shows that the surviving prior method is inseparable from
  its seed, and `g2` cannot rebuild an independent frame, the honest product is the history
  plus a documented impossibility result. That lands and the track closes.
- **Budget kill:** compute exceeding 2× the measured pilot estimate stops for diagnosis
  rather than pushing through.

## 3. Non-goals — out of scope

This stage is bounded. It does **not** become:

- a final RT phylogeny (that is stage 06);
- retron reclassification or subtype revision (stage 05);
- any ncRNA analysis, RT–ncRNA pairing or co-evolution work (stages 07, 10);
- de novo retron or novel-RT discovery (stage 11);
- a final fingers/palm/thumb structural segmentation project (stage 04);
- a motif-discovery project beyond what operational RT-subdomain reconstruction needs
  (stage 03);
- domain-fusion analysis (stage 08).

Structural evidence enters as **constraint and independent test only**. It is not permission
for this stage to absorb later structural work. Specifically: crystal geometry may constrain
where a block edge can sit and may falsify a proposed edge, but it may **not** be used to
manufacture the seven-way sequence partition, because the published RT0–RT7 conventions were
never derived from structure.

**Stage 04 is not a prerequisite for this track and is not merged into it.** Stage 2 first
reconstructs and operationalizes the historical sequence framework; Stage 04 later supplies an
independent structural representation against which that framework may be tested.

Discovered scope is not scope. A gate may be split if it does not fit one execution and
review unit; it may not be silently widened.

## 4. Inputs and trust grades

An ungraded input is `DO-NOT-USE` (WA-L.3). All inputs are read-only. No landed Stage-1
bundle is modified by this track.

| path | what it is | trust grade |
|---|---|---|
| `data/derived/rt_exact_v1.parquet` | Stage-1 exact-RT table, 501,561 rows, primary analytical unit for this track | `FROZEN` |
| `data/derived/rt_exact_v1.faa` | the same 501,561 exact RT amino-acid sequences as FASTA | `FROZEN` |
| `data/derived/rt_family_baseline_v1.parquet` | per-exact-RT family label, MULTI flag, completeness class, clipping and edge counts — the eligibility basis for the full-length rule | `FROZEN` |
| `data/derived/rt_cds_recovery_v1.parquet` | RT-CDS recovery state, geometry eligibility and reasons, 31,504 rows | `FROZEN` |
| `data/derived/rt_loci_v1.parquet` | locus-level support and occurrence counts per exact RT | `FROZEN` |
| `data/derived/rt_tool_calls_v1.parquet` | per-tool retron/RT call matrix; the provenance of every family label used as a stratum | `FROZEN` |
| `results/dbchar_g2_canonical_units/VIEWS.md` | the declared view and eligibility-predicate vocabulary every downstream number must name | `FROZEN` |
| `results/dbchar_g7_stage1_report/tables/g7_resolved_values.tsv` | Stage-1 resolved headline values, traceable to producing rows | `FROZEN` |
| `docs/decisions/2026-09-15_stage1_population_rules.md` | binding population rules: ncRNA-anchor-only exclusion, MULTI stratum, RT-CDS-less classification | `FROZEN` |
| `references/rt0_rt7/RESOURCE_REGISTER.tsv` | 26 registered reference rows with tier, provenance status and seeding permission | `FROZEN` |
| `references/rt0_rt7/literature/` | the four derivational primary PDFs plus the structural primary PDF | `RAW` |
| `references/rt0_rt7/historical/` | Toro 2014 RT0–RT7 block FASTA, 742 sequences (count verified 2026-09-15) and Table S1 | `RE-DERIVE` |
| `references/rt0_rt7/mestre_2020/` | Mestre 2020 reference tree and three header variants of the supplementary assignment table | `RE-DERIVE` |
| `references/rt0_rt7/myrt/` | myRT reference profile, alignments, tree, mapping, phylo model, run log and build script | `RE-DERIVE` |
| `references/rt0_rt7/toro_2026/` | Toro 2026 preprint EPA-ng phylogeny, 30 type HMMs plus calibration thresholds, type XI tree, pipeline scripts | `RE-DERIVE` |
| `references/rt0_rt7/SOURCE_AUDIT.tsv` | all 121 discovered copies with hashes and duplicate groups | `FROZEN` |
| `references/rt0_rt7/PRIOR_WORK_INVENTORY.tsv` | 18 prior RT0–RT7 artifacts with reuse class and provenance status | `FROZEN` |
| `general/RETRON_STAGES/02_rt0_rt7_definition.md` | prior scientific and design dossier; ideas, traps, paths and prior numbers | `RE-DERIVE` |
| `docs/decisions/2026-09-15_stage2_prior_dossier_audit.md` | this track's binding classification of every prior-dossier item; its §D and §G unresolved items are superseded by the operator-decision record below | `FROZEN` |
| `docs/decisions/2026-09-16_stage2_g4_design_amendment.md` | the amended g4 object, validation architecture and deliverables, and the corrected lineage of all167, anchors72, GOLD171, ph38 and CAND95 | `FROZEN` |
| `results/rt07_pre_g4_seed_provenance/` | the measured seed-provenance and leakage audit the amendment rests on | `FROZEN` |
| `docs/decisions/2026-09-15_stage2_operator_decisions.md` | the four resolved operator decisions this launcher encodes — `ALIGN_000044` acquisition, the external-structure inclusion rule, Stage 04 separation, Xiong & Eickbush Fig. 1 evidence priority — and the two that stay deferred | `FROZEN` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/` | prior main derivation arm, 50 scripts and 92 tables; code may be reused after inspection | `RE-DERIVE` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/d_instrument_audit/` | prior audit arm that measured the seed-overlap and concordance defects | `RE-DERIVE` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/M_models/` | prior model-building arm | `RE-DERIVE` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/` | 25 crystal structures with boundaries previously extracted, including 6AR1 group II intron RT | `RE-DERIVE` |
| EMBL alignment accession `ALIGN_000044` | Zimmerly 2001's own submitted alignment; registered missing, not on disk. Governed acquisition during `g1` is operator-approved (§9a, `docs/decisions/2026-09-15_stage2_operator_decisions.md` §A) | `DO-NOT-USE` until acquired, registered and validated |
| non-LTR R2-type RT structure | historically relevant structural comparator for testing RT0 correspondence; absent locally, needs network. Governed acquisition under the predeclared inclusion rule is operator-approved (§9a, decision record §B) | `DO-NOT-USE` until acquired, registered and validated |
| `/home/borg/foldseek/bin/foldseek` and the two other local foldseek builds | three installs, no agreed semantic version; one must be pinned before any structural comparison | `DO-NOT-USE` |

`DO-NOT-USE` here means **not usable as evidence in this track until the named condition is
met**, not that the asset is forbidden forever, and — for the two acquisition rows — **not a
revocation of the operator's acquisition approval**. Those two assets are already approved for
governed acquisition (§9a; `docs/decisions/2026-09-15_stage2_operator_decisions.md` §A and §B).
The grade records the separate fact that a downloaded file is not evidence: an acquired asset
stays `DO-NOT-USE` until it has been **acquired, registered and validated** — retrieved from an
authoritative source into the governed acquisition cache of §9c, registered with identity,
source, licence/access state, byte count and SHA256, and landed as an acquisition record in
`rt07_g1_history_and_definition` (§7c). Only the four grades of WA-L.3 are used here; this
launcher does not extend the governance vocabulary. §9 states the acquisition rules.

### 4a. Stage-1 population constants this track treats as fixed

From `results/dbchar_g7_stage1_report`. These are not recomputed by this track.

| constant | value |
|---|---|
| exact RT proteins, the primary unit | 501,561 |
| RT-anchored records in single-family files | 3,050,688 |
| MULTI-file records | 9,012 |
| ncRNA-anchor-only records, excluded from every RT denominator | 298,482 |
| genomes | 1,542,433 |
| RT taxonomic occurrences | 2,737,189 |
| RT-family records that are geometry-eligible | 99.47% |
| RT-CDS-less records fully recoverable | 14,188 |
| records with usable sequence but no defensible genomic context | 16,688 |
| of those, lying wholly beyond the retrieved contig | 9,128 |
| records remaining ill-posed | 628 |

The 298,482 ncRNA-anchor-only records enter no RT denominator anywhere in this track.

Nothing is silently discarded. `MULTI`, partial and truncated RTs, recovered RT-CDS cases
and ambiguous sequences are all retained and given an explicit eligibility state per
analysis. Stage 1 established that missing and unreliable sequence context exists, so every
per-block result in this track must distinguish four things that a single "absent" would
conflate: **biological absence · detector non-detection · ambiguous detection · sequence
uninspectability or partiality.**

## 5. What might already exist

Absence is loud; wrongness is quiet. The prior work here is extensive, partly correct and
partly withdrawn, so it is audited item by item in
`docs/decisions/2026-09-15_stage2_prior_dossier_audit.md`, which is binding for this track.

### 5a. Prior work that is worth reading before writing any code

- The prior derivation arm `D_instrument` (50 scripts, 92 tables) and its own audit arm
  `d_instrument_audit` (7 scripts, 10 tables). The audit arm is the more valuable of the
  two: it is what found the defects.
- `d20b_domain_methods.tsv` and `D2.0_METHOD_LANDSCAPE.md` — a prior method survey with
  explicit `can_define_RT0`, `circularity` and `what_it_CANNOT_do` columns. This is a
  ready-made starting row set for the operational-evidence matrix in `g1`.
- `d21b_truncation_verdict.py` and `d21c_sse_agreement.py` — two falsification tests
  declared as gates before running: whether a structural negative at the N-terminus is
  admissible, and whether two secondary-structure algorithms agree closely enough to set an
  edge. Both ask questions this track would otherwise re-ask from scratch.
- `d2j_boundary_crossval.tsv` — a prior Jaccard cross-validation of derived match states
  against DSSP fingers/palm/thumb, per structure.
- Method documents `X00_rt0_rt7_domain_derivation.md` and `X12_landmark_register.md`.

### 5b. Prior numbers that are known to be wrong or misquoted

Recorded so no session re-inherits them:

- **"72/72 concordance" is not a concordance.** It is the `n_anchor_rows` sample size. The
  prior per-motif concordance ranges 0.75–1.00.
- **`anchors72` is not "72 structure-validated anchors."** The prior audit measured 100%
  seed overlap, and only 26 of 72 have a structure at all; the other 46 are
  sequence-propagated. This phrasing is banned in this track's outputs.
- **`D6` is withdrawn by the prior work itself** — enrichments regenerate at 224× / 445×,
  not the 2,657× / 4,936× once reported, and Region X is weak rather than family-exclusive.
- **The prior dossier's myRT model counts are wrong.** It states roughly 2,051 seeds over 47
  families; `RVT-All.hmm` measured 2026-09-15 contains **45 models and 1,988 summed NSEQ**,
  which matches the myRT publication's own statement of 45 HMM models for 41 RT classes
  built from 1,988 RVT_1 sequences. Use the measured values.
- **The prior `tree tips` were a 341-aa tetrad window, not a derived domain.** The phrase
  "domain-based phylogeny" is banned for that object.

### 5c. Reference-asset provenance that must not be overstated

From the resource audit. Preserve these states; do not repair the files.

- Three files named in the myRT package manifest have observed checksums that **disagree**
  with it (`RVT-ref.fst`, `RVT-ref.tre`, `RVT-ref.log`) — registered
  `PROVENANCE_IDENTIFIED_CHECKSUM_UNVERIFIED`. The content is attributable to the myRT
  authors and the disagreement is not a line-ending artifact, so the accurate statement is
  that the manifest does not describe these versions.
- Three further files are **not represented in that manifest at all** (`RVT-ref.hmm`,
  `RVT-ref.sto`, `Mapping`) — registered `PROVENANCE_IDENTIFIED_NOT_IN_MANIFEST`. No
  published checksum exists for them. `RVT-ref.hmm` is in this set.
- One file matches (`phylo_modeldyadg_ia.json`).
- **All discovered local copies of each file are byte-identical to one another**, so the
  disagreement predates every local copy and is not a local-copy defect.

myRT may be used as a comparator. It may not be described as the published,
checksum-verified myRT reference package.

### 5d. The evidence hierarchy this track applies

| tier | assets | permission |
|---|---|---|
| derivational primary | Poch et al. 1989; Xiong & Eickbush 1990; Zimmerly, Hausner & Wu 2001; Simon & Zimmerly 2008; and `ALIGN_000044` if acquired under §9 | may inform reconstruction of the historical sequence framework |
| independent structural | Blocker et al. 2005 and the registered RT structures | may **constrain or test** sequence-defined blocks; may **not** manufacture the seven-way sequence partition |
| published comparators | Toro 2014; Mestre 2020; myRT reference assets; Toro 2026 and SPIRE assets | compared against only; must never seed the reconstructed frame |
| prior project work | `D_instrument`, `M_models`, prior HMMs, boundary tables, motif sets, the five prior `rt0_rt7_*` stages | `PRIOR / UNVERIFIED`. Code and methods reusable after inspection; **no prior numerical result becomes an acceptance criterion** |

Two representations are kept distinct throughout and neither is substituted for the other:
the **RT0–RT7 sequence/conservation framework** and the **fingers/palm/thumb structural
partition**. Simon & Zimmerly's published mapping between them may be tested and reported;
it may not be assumed.


### 5e. Historical reconstruction evidence priority

When reconstructing a historical block or landmark, evidence is used in this order:

1. the original digital or accessioned alignment, if recoverable;
2. explicit textual criteria in the primary paper;
3. digitisation of the published alignment figure as corroboration or fallback.

For Xiong & Eickbush Fig. 1 specifically, figure digitisation is permitted in `g1`/`g2` only
after the first two routes have been checked. Any coordinate inferred from a figure carries an
explicit extraction uncertainty; pixel-derived edges are not reported as exact residue
boundaries without independent support.

## 6. Claims this task tests

| id | role in this task |
|---|---|
| `C3` | `primary` |
| `C9` | `primary` |
| `C4` | `supporting` |
| `C7` | `supporting` |

Claim wording and status live only in `idea-stage/docs/research_contract.md`. Every claim is
born `UNPROVEN` there and no gate in this launcher promotes one.

## 7. Gates

One gate is one measurement (WA-G.1). Every gate lands a bundle whose `run.sh` reruns from
the landed inputs and reproduces its number (WA-G.2).

| gate id | the ONE measurement | weight | settles | stop condition |
|---|---|---|---|---|
| `rt07_g1_history_and_definition` | per (source, region-name) evidence class across the derivational primary literature: motif evidence, alignment block, explicit stated boundary, terminology only, or inherited-without-definition — counted, with the unresolved-definition register and the acquisition and source-resolution register covering `ALIGN_000044` | `FULL` | `C3` supporting, `C9` supporting | done when `results/rt07_g1_history_and_definition/` reruns and reproduces the terminology genealogy, literature evidence matrix, operational-evidence matrix, unresolved-definition register and the acquisition and source-resolution register, including the `ALIGN_000044` row |
| `rt07_g2_reference_reconstruction` | recovery rate of the historical landmarks on the sequences and reference alignments from which they were derived, before any Toro, Mestre or myRT convention is consulted | `FULL` | `C3` supporting | done when `results/rt07_g2_reference_reconstruction/` reruns and reproduces the reconstructed reference alignment, the curated reference sequence set and the per-landmark recovery table |
| `rt07_g3_prior_method_replication` | how many prior RT0–RT7 results survive independent regeneration under the Stage-1 inputs, with conditioning bias, seed overlap, frame identity and object identity audited per result | `FULL` | `C3` supporting, `C7` supporting | done when `results/rt07_g3_prior_method_replication/` reruns and reproduces the per-prior-result verdict table including each result's frame, stratum and n |
| `rt07_g4_operational_boundary_model` | per-region detector performance across four separately reported validation arms — historical reconstruction, held-out PDB structures, the GOLD171 retron literature challenge and a bounded family-stratified Stage-1 sample — with detection evidence, boundary uncertainty and out-of-distribution context kept as separate quantities, and calibration claimed only on the population it was demonstrated on. **Amended 2026-09-16** by `docs/decisions/2026-09-16_stage2_g4_design_amendment.md`: the object is a portable detector of the independently reconstructed conserved regions, NOT seven per-block calls; historical RT0–RT7 is a mapping layer over those regions with `1:1`/`1:many`/`many:1`/`none`/`unresolved` cardinality | `FULL` | `C3` primary, `C9` primary | done when `results/rt07_g4_operational_boundary_model/` reruns and reproduces the operational region definitions, the historical-to-operational mapping, the method comparison, the per-arm validation tables, the leakage audit, the calibration and boundary-uncertainty tables, and a frozen portable detector package that annotates an unseen RT sequence |
| `rt07_g5_catalogue_application` | per-block call-state distribution over the eligible Stage-1 exact-RT catalogue, family, MULTI and completeness strata retained | `FULL` | `C3` primary | done when `results/rt07_g5_catalogue_application/` reruns and reproduces the exact-RT by block call table and its per-stratum denominators |
| `rt07_g6_family_architecture` | per-family differences in called block architecture — occupancy, length, start, end, normalized position, inter-block distance, missing-block combination, insertion and expansion, truncation and inspectability, confidence — retron against major non-retron RT families | `FULL` | `C4` primary, `C3` supporting | done when `results/rt07_g6_family_architecture/` reruns and reproduces the family architecture summary and the missing-block-pattern table |
| `rt07_g7_structural_and_published_comparators` | agreement and disagreement between the independently reconstructed frame and each comparator — structures, Simon & Zimmerly's structural mapping, Toro 2014, Mestre, myRT, Toro 2026, prior project conventions | `FULL` | `C7` primary, `C3` supporting | done when `results/rt07_g7_structural_and_published_comparators/` reruns and reproduces the comparator-disagreement table and the ruler comparison figure from landed tables |

Every gate is `FULL` because every gate's number becomes claim-bearing or paper text. A gate
may be started as `LIGHT` recon and re-landed as `FULL`, which is one rerun (WA-B.3).

`g1` and `g2` run before `g3`, and `g3` before `g4`; `g4` must be frozen before `g5`.
`g6` and `g7` follow `g5`. Comparator assets are not read during `g2` at all.

**Amendment 2026-09-17 — how `g4` was frozen.** The dependency above is unchanged; this
records the artifact that satisfies it. `g4` was executed as two landed steps rather than
one, and the freeze is the second:

| step | what it did | landed at |
|---|---|---|
| `g4a` | mapper development and validation | `results/rt07_g4a_repaired/` and the repair bundles |
| confirmatory transfer validation | the single UG25 holdout run that closed Stage-2 validation at Endpoint A | `results/FINAL_PRE_UG25_VALIDATION_BUNDLE/`, `results/rt07_ug25_confirmatory/` |
| **`g4b`** | **production freeze** — the validated mapper packaged as a versioned instrument, with no scientific parameter, rule or call changed | **`results/rt07_g4b_production_mapper/`** |
| `g5` | catalogue application | `results/rt07_g5_catalogue_application/` |

**`results/rt07_g4b_production_mapper/` IS the frozen `g4` this launcher requires before
`g5`.** Its instrument is `rtmap-1.0.0/53a1e738a19b3896`, instrument sha256
`53a1e738a19b38967563b4f4d733047b26123f754a7d592fd0186e7bd9c331f5`, mapper code sha256
`69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef` (byte-identical to the
validation bundle's), schema `rtmap-schema-1.0`, bundle root
`0b025cbab192f64d05ef0a9aff47859b998fe3158dc0199cd47cbbd040620d3f`, landed in commit
`dd9cdae`.

`g5` was authorised by the **independent packaging review**, round 2, `9/10`,
`MAY g5 BEGIN: YES` — a review of packaging fidelity only. Stage-2 scientific validation
closed separately at Endpoint A and is not reopened by this amendment.

`g4b` is a **packaging gate**: it produces no claim-bearing number, so it carries no row in
the gate table above and no `FULL` weight. Its evidence is engineering reproduction, not
measurement. Record:
`docs/decisions/2026-09-17_stage2_g4b_production_packaging.md`, amendment recorded in
`docs/decisions/2026-09-17_stage2_launcher_g4b_freeze_amendment.md`.

### 7a. Call-state vocabulary

Every per-block call uses exactly one state. Non-detection is never reported as absence.

| state | meaning |
|---|---|
| `PRESENT_HIGH_CONF` | block called with confidence above the declared threshold |
| `PRESENT_LOW_CONF` | block called below that threshold; retained, flagged, never merged into `PRESENT_HIGH_CONF` |
| `NOT_DETECTED_INSPECTABLE` | the sequence could have shown the block and did not — the only state that can support a biological absence reading |
| `UNINSPECTABLE_PARTIAL` | truncation, clipping or contig edge means the region was not inspectable |
| `AMBIGUOUS` | competing placements not separable at the declared threshold |
| `OUT_OF_FRAME` | the block is not defined for this sequence class, e.g. an RT0 correspondence test on a class outside its defined scope |

`OUT_OF_FRAME` exists so that RT0 can be reported honestly on classes for which the
historical concept was never defined, rather than scored as a zero.

### 7b. Required retained fields on every final call

Every row of the final exact-RT by block table retains: exact RT key and hash · block ·
call state · start · end · length · normalized start and end · confidence · evidence method ·
inspectability and completeness class · uncertainty interval · family and MULTI stratum.

### 7c. Reusable datasets this track must land

Datasets, not only figures. Each lands in the gate named beside it.

| product | gate |
|---|---|
| literature and terminology evidence table | `g1` |
| unresolved-definition register | `g1` |
| acquisition and source-resolution register — one row per externally acquired or attempted asset (`ALIGN_000044` and any structure admitted under §9a), carrying asset identity, source URL or archive, retrieval date, licence/access state, byte count, SHA256, validation state and, where retrieval failed, `MISSING_PRIMARY_ASSET` | `g1` |
| operational region definitions (`operational_region_definitions.tsv`) | `g4` |
| historical-to-operational mapping, with cardinality (`historical_to_operational_mapping.tsv`) | `g4` |
| per-arm validation population (`validation_population.tsv`) | `g4` |
| sequence lineage and role table (`sequence_lineage.tsv`) | `g4` |
| identity-and-coverage leakage audit (`leakage_audit.tsv`) | `g4` |
| method comparison against a baseline and, where available, a challenger (`method_comparison.tsv`) | `g4` |
| declared thresholds (`thresholds.tsv`) and calibration with its scope (`calibration.tsv`) | `g4` |
| boundary uncertainty per region (`boundary_uncertainty.tsv`) | `g4` |
| family-holdout transferability (`family_holdout_or_transferability.tsv`) | `g4` |
| a versioned **portable detector package** — frozen model artifacts, coordinate definitions, thresholds, calibration scope, usage code and `MODEL_CARD.md` — able to annotate an unseen RT amino-acid sequence. The requirement is the instrument, not a preselected implementation; filenames are not forced to any method | `g4` |
| phylogeny-ready core substrate: `rt_core_coordinates`, `rt_core_extracted`, `rt_core_alignment`, `rt_core_alignment_mask`, `phylogeny_eligibility` — landed only AFTER the detector is frozen and the catalogue stage has run; no phylogenetic inference happens in Stage 2 | `g5`+ |
| inspectability-aware occupancy and architecture products: `region_occupancy_by_family.tsv`, `region_call_state_by_family.tsv`, `region_cooccurrence_patterns.tsv`, `region_length_distribution.tsv`, `inter_region_spacing.tsv`, `region_normalized_positions.tsv` | `g6` |
| curated reference sequence set | `g2` |
| reconstructed reference alignment | `g2` |
| prior-result verdict table with frame, stratum and n | `g3` |
| exact-RT by block call table | `g5` |
| long-format exact-RT and block boundary table | `g5` |
| family architecture summary | `g6` |
| missing-block-pattern table | `g6` |
| comparator-disagreement table | `g7` |
| validation and held-out audit table | `g4` |

### 7d. Validation-set contamination is a first-class design problem

The prior work measured, and this track must independently verify before reusing any of it:

| prior observation | prior value | status here |
|---|---|---|
| `anchors72` exact seed members | 72 of 72, 100% | `PRIOR / UNVERIFIED` — re-measure |
| `anchors72` members with an actual structure | 26 of 72; the other 46 sequence-propagated | `PRIOR / UNVERIFIED` — re-measure |
| `gold175_uniq` exact seed members | 44 of 171, 25.7% | `PRIOR / UNVERIFIED` — re-measure |
| "external" referee producers inside the seed | 42 of 63 | `PRIOR / UNVERIFIED` — re-measure |
| Khan experimental panel overlap with the Mestre lineage | reported strong | `PRIOR / UNVERIFIED` — re-measure |

`g4` must construct a **defensible held-out validation design** and report its measured seed
overlap. If a genuinely independent validation population cannot be constructed, that
limitation is stated explicitly in the bundle and in the report, and no accuracy claim is
made. Constructing independence by relabelling or by dropping the overlap silently is
forbidden.

### 7e. The full-length derivation rule

Preserved from the prior design recommendation, which was never executed.

Operational boundaries are derived **first** on a conservative, high-inspectability
full-length sequence set. A contig-edge-truncated CDS shifts the very boundary being
defined, so truncated proteins may not participate in deriving a boundary and then have
their missing blocks read biologically. Eligibility comes from the Stage-1 completeness and
recovery fields in `rt_family_baseline_v1` and `rt_cds_recovery_v1`.

**After** the detector and frame are frozen in `g4`, partial proteins are scored, and those
with evidence of a complete block set may be rescued as block-complete on merit. The rescue
is a separate, reported step with its own denominator.

## 8. Compute

- Expected machine: **borg CPU** for literature extraction, alignment reconstruction on the
  curated reference set, detector development and all descriptive analysis.
- **Pilot every expensive operation first.** Measure throughput on a representative,
  length- and family-stratified slice of the exact-RT set; the measured rate times N becomes
  the run estimate. Sizing by habit is how queues are wasted.
- Escalate to **Ibex** per GENERAL rules only when a representative pilot predicts
  >2 hours wall-clock locally, memory does not fit, or a registered resource exists only on
  Ibex. Call `general/tools/dispatch.py` before any job over 10 minutes and paste its reason
  into the gate bundle.
- **No full 501,561-sequence pass runs during planning**, and none runs in `g1`–`g4`. The
  catalogue-scale pass belongs to `g5` and only after `g4` is frozen.
- GPU: none required for `g1`–`g3`. Any structural or embedding work in `g4` or `g7` is
  piloted and costed before it is requested.
- Hard stop at **2× the measured estimate**; diagnose rather than push through.

No package is installed merely because the first environment lacks it; registered
environments and Ibex resources are checked first. Primary local environment is
`retron_tradicional`; `base` is never used.

| | budget |
|---|---|
| CPU-hours | `150` |
| GPU-hours | `0` unless a piloted structural arm is approved under §9 |
| max single job | `6` hr |
| review rounds per gate | `3` |

## 9. Autonomy: decide-alone vs stop-and-wait

**Auto-proceed:** `true`. This launcher is intended to run unattended to a landed bundle.

### 9a. Decide alone and continue

Inside the budget and the write boundary, ARIS may without asking:

- read every registered reference asset and every prior artifact, and classify it;
- port or rewrite prior scripts into scratch after recording what changed and why;
- choose the alignment tool, profile method and scoring scheme, and record the choice with
  its declared thresholds **before** scoring;
- declare each eligibility predicate and each confidence threshold in code before the data
  is scored, and report a sensitivity sweep around it;
- define the conservative full-length seed set from Stage-1 completeness fields;
- construct and measure the held-out validation design, including reporting that it is not
  independent if that is what the measurement shows;
- retain ambiguous, partial, MULTI and recovered cases with an explicit state rather than
  forcing a classification;
- choose borg versus Ibex from the measured pilot rule in §8;
- split a gate that does not fit one execution and review unit;
- add retained columns or QC flags needed by a downstream gate;
- record a prior number as not reproduced, and land that as the result (WA-G.5);
- digitise Xiong & Eickbush Fig. 1 as corroboration or fallback under §5e after the original
  digital-alignment and textual-criteria routes have been checked, with extraction uncertainty
  recorded explicitly;
- log surprises and propose biological interpretations as `PROPOSED:` without declaring
  them established (WA-A.4);
- acquire `ALIGN_000044` during `g1` from an authoritative archival source, writing it to the
  governed acquisition cache `data/derived/rt07_external_assets/` and recording accession,
  source URL, retrieval date, access/licence status, byte count and SHA256 in the `g1`
  acquisition and source-resolution register before use. If the accession is unavailable,
  inaccessible or resolves ambiguously, record `MISSING_PRIMARY_ASSET` and continue without
  inventing a replacement;
- acquire a non-LTR R2-type RT structure, or another non-retron/non-bacterial RT structure,
  only when it satisfies the predeclared inclusion rule: it must represent a historically
  relevant reference class required to test a reconstructed concept, or provide an independent
  structural comparator for a sequence-defined block. Such structures may constrain or falsify
  a sequence-defined boundary but may not define the RT1–RT7 partition. For RT0 specifically,
  group-II-intron and non-LTR RT structures are admissible historical comparison classes.
  Acquired structures land in `data/derived/rt07_external_assets/` and carry a row in the `g1`
  acquisition and source-resolution register on the same terms as `ALIGN_000044`;
- lift the `DO-NOT-USE` grade on the three foldseek installs by pinning one build and
  recording its identity, if and only if a structural comparison is actually needed.

### 9b. Human gate — stop and wait

Stop and wait for the operator only for:

- broadening the predeclared external-structure inclusion rule beyond historically relevant
  reference classes or independent structural comparators;
- acquiring any external asset whose licence/access conditions are unclear, whose identity
  cannot be established unambiguously, or whose acquisition would require credentials or
  permissions not already available to the operator;
- promoting any prior number to an acceptance criterion;
- modifying, deleting or replacing canonical raw data, a landed Stage-1 bundle, or ground
  truth;
- changing the project claim wording or the scientific question;
- introducing a hard biological filter that deletes observations from the canonical
  representation rather than flagging or stratifying them;
- exceeding the compute budget, or requesting GPU hours;
- adopting a new governance revision or moving the ARIS pin;
- deciding whether the operational definition is published as its own methods paper;
- deciding whether RT1's prior concordance failure is reported as a limitation of this
  method or as an independent recovery of a weakness the founding authors flagged — the
  prior dossier notes these are different objects and must not be conflated;
- publishing or sending any material outside the project.

### 9c. Write boundary

Writable: `ARIS_OUTPUT/02_rt0_rt7_definition/` for scratch, `results/rt07_*/` for landed
bundles, `data/derived/` only for datasets this launcher names in §7c, and
`docs/decisions/` for new decision records. Everything else, including every landed Stage-1
bundle and everything under `references/rt0_rt7/`, is read-only to this track.

**Governed acquisition cache — `data/derived/rt07_external_assets/`.** This is the one
destination for externally acquired assets (`ALIGN_000044`, any structure admitted under §9a).
It is writable by this track and gitignored like the rest of `data/`, so bytes stay out of git
while their identity stays in the record. Three rules hold:

- **an acquired asset is not evidence because it was downloaded.** It is `DO-NOT-USE` (§4)
  until its acquisition register row exists in `results/rt07_g1_history_and_definition/` with
  identity, source, licence/access state, byte count, SHA256 and validation state;
- **nothing is ever written into `references/rt0_rt7/`.** That package is frozen and read-only
  to this track; acquisitions extend the record through the `g1` register, never by editing it;
- a failed or ambiguous retrieval lands as `MISSING_PRIMARY_ASSET` in the same register, and
  no substitute is invented.

### 9d. Reporting architecture

Unchanged from Stage 1 and enforced, not promised:

    measurement scripts -> landed TSV/parquet -> interpretation -> assembler computes nothing
    -> REPORT.md + self-contained REPORT.html

- the report assembler computes **no** scientific result; every value it renders resolves to
  a (bundle, landed table, row selector, column, format) five-tuple, and an unresolved
  placeholder fails the build;
- every figure has a producing script and a landed numerical table;
- every figure and table declares its **analytical unit** and its **denominator**;
- every number names its **frame** and **stratum**; a number quoted without both is
  unattributable and is treated as a build failure;
- the finished HTML is self-contained and is visually inspected before the gate closes.
