# Methods — Defining RT0–RT7 operationally with a frozen conserved-state mapper

*Thesis chapter section. Numbers are resolved from the landed Stage-2 record at `{{pinned_short}}`;
see `tables/stage2_resolved_values.tsv` for the source of each.*

## Overview and design principles

The analysis had five layers, kept separate throughout: (i) the historical definition of the
RT0–RT7 labels; (ii) an operational instrument that maps residues to conserved profile-HMM
states; (iii) a family-level descriptive analysis of the mapped catalogue; (iv) a bridge from
the historical labels to the operational states on one reference RT; and (v) independent review
of every step that moved the project forward. Each layer landed as a sealed, hash-verified
bundle. Thresholds were fixed before the data that tested them were opened. Failed designs and
falsifying results were kept. No absence was inferred from a non-observation without a positive
control showing that the instrument recovers a known-present case on the same substrate.

## Historical evidence audit

The primary literature defining the numbered RT regions was assembled into an evidence set of
{{g1_sources}} held sources. Each of {{g1_regions}} region names was scored against each source
for the kind of evidence given: explicit stated boundary, alignment block, motif evidence,
derivable procedure, inherited without definition, or not in held evidence. Every supporting
quotation ({{g1_quotes}}) was checked verbatim against the source PDF. Citation genealogy was
traced to separate original statements from restatements. The Zimmerly group-II-intron RT
alignment (ALIGN_000044; {{g1_aln_seqs}} sequences, {{g1_aln_cols}} columns) was acquired and
verified as the historical reference substrate.

## Independent reconstruction of the historical landmarks

Conserved blocks were reconstructed on the {{g2_proteins}} reference proteins in two alignment
frames: the published alignment, and an independent realignment with MAFFT FFT-NS-2. Blocks were
defined by column conservation. Each reconstruction statistic (number of conserved positions,
block count, largest inter-block gap) was tested against a column-permutation null. Blocks were
matched across frames by Jaccard overlap of their LtrA residue spans. Block edges were reported
as intervals across a parameter sweep. No single-column edge was claimed, because the sources
state a procedure rather than residue edges.

## Audit of prior coordinate frames

{{g3_claims}} RT0–RT7 claims from earlier project work were regenerated from their inputs and
classified as reproduced, partially reproduced, circular or seed-dependent, object mismatch,
frame mismatch, withdrawn, or not testable. For each prior anchor set, the fraction lying inside
its own defining seed was measured.

## The conserved-state mapper

**Profile and states.** A profile HMM was built from group-II-intron RTs (`GII.deriv.hmm`, LENG
{{profile_leng}}) with `{{profile_m}}` as the match-state convention. The instrument uses
{{n_anchors}} frozen conserved states: the states aligned in every construction family ("all
partners"). The catalytic state CAT_STATE was fixed separately as the modal state of MAPPED
[YF].DD occurrences in the construction set.

**Calls.** Each query was scored against the profile (per-sequence, database size 1) and aligned
to it. Each anchor state received one call from the posterior probability of the aligned
residue: MAPPED if the posterior was ≥ PP_HI ({{pp_hi}}), AMBIGUOUS if it lay between PP_LO
({{pp_lo}}) and PP_HI, UNSUPPORTED if it was lower, and DELETED_STATE if the alignment path
skipped the state. A sequence was committed only if its domain bitscore exceeded S_MIN
({{s_min}}) and at least K_MIN ({{k_min}}) anchors were MAPPED. Otherwise it abstained with a
reason from a closed vocabulary.

**Calibration.** Each threshold was the smallest value on a predeclared grid that met a rule
fixed in advance. PP_HI: the pooled negative-control 95th percentile of MAPPED fraction was zero
and the median real fraction was ≥ 0.50. S_MIN: strictly above the highest negative-control domain
bitscore. K_MIN: strictly above the highest negative-control MAPPED-anchor count. T1 ({{t1}}), the fifth
percentile of per-sequence MAPPED fraction over construction, was the transfer floor. D_MAX
({{d_max}}) bounded the difference between component medians, with a same-population random-split
companion D_RANDOM ({{d_random}}) reported alongside. Calibration used six construction families.
All parameters were then frozen in control tables that the mapper reads at run time.

**Match-state sensitivity.** Profiles were rebuilt under `-M 50`, `-M 60` and `-M a2m`, and the
all-partner state set was recounted per family.

## Transfer validation

Holdout lineages were used for confirmation only. Two earlier holdout designs (UG5 v2 and v3) and
a residue-transfer gate on G2L were reviewed and rejected. After the G2L failure, the posterior-based support
rule was adopted and a genealogy audit was predeclared: exact-sequence and identifier overlap with construction, and a full link
rule requiring identity ≥ 0.30 and coverage ≥ 0.50. UG25 was classified by this audit before
mapping and opened exactly once. Seven predeclared criteria were evaluated:

- C1: each qualifying component (≥ 5 sequences) has median MAPPED fraction ≥ T1.
- C2: the frozen posterior rule is used.
- C3: ≥ 0.8 of CAT_STATE-MAPPED sequences begin [YF].DD.
- C4: the difference between component medians is ≤ D_MAX.
- C5: the abstention vocabulary is closed.
- C6: synthetic controls are separated per control class with exact identity accounting.
- C7: no threshold was changed after UG25 was opened.

Controls were {{ug25_ctrl_n}} shuffles of real UG25 RTs in three classes: MONO (composition
kept), DI (dipeptide counts kept) and REV (sequence reversed).

## Production freeze, eligibility census and catalogue application

The validated mapper was frozen with a compact identifier. The identifier hashes the schema, the
match-state definition, the mapper code, the profile and its LENG, the anchor set, the parameter
values, the dyad pattern, the HMMER binaries, the instrument source tree, the eligibility rule
and the domain-scoring protocol. It is `{{mapper_version}}`. Eligibility (≥ {{min_aa}} residues,
20 standard amino acids) was applied once, in a separate census of the {{g5a_total}} exact RT
sequences of the Stage-1 catalogue. That census fixed the denominator at {{g5a_eligible}}. The
eligible sequences were sharded, mapped with the frozen runner, verified shard by shard against
their completion records, and merged into the canonical mapped dataset. Inspectability was
summarised per sequence (MAPPABLE, PARTIAL_MAPPING, AMBIGUOUS_MAPPING, NO_SUPPORTED_MAPPING).
CAT_STATE results were reported on their own denominator.

## Family-level descriptive analysis

For each family stratum, the per-state occupancy profile of inspectable sequences was summarised.
Between-family distances were compared between two halves of the catalogue. The halves were
split by label-blind sequence clusters (MMseqs2 linclust, identity 0.90), so that no cluster
contributes to both halves. Concordance was the rank correlation of the two halves' pairwise
distance vectors. Families needed ≥ 100 inspectable sequences in each half. Two permutation nulls
were computed: NULL-1 permutes sequences and NULL-2 permutes clusters. Both are reported for every
analysis. Control analyses restricted the population to narrow MAPPED-fraction strata (CTRL-VIS),
kept one representative per cluster at 0.90, 0.50 and 0.30 identity (CTRL-REL), or used one
completeness class (CTRL-COMP). Within retrons, DefenseFinder and PADLOC subtype strata were
analysed on separate denominators and never pooled. A label-free arm used clusters at 0.30
identity. The rank statistic ranks ties ordinally rather than averaging them. It is reported as
landed and described as a rank correlation with ordinal tie-breaking.

## Historical bridge on LtrA

LtrA (UniProt P0A3U0) was mapped with the frozen instrument. Each MAPPED anchor state was placed
on an LtrA residue. For each historical label, the anchor states falling inside its
reconstructed interval (Route P) were counted, and prior-frame points (Route C) and source-stated
residues (Route S) were recorded alongside. Correspondence classes were assigned by predeclared
rules: RT5 and RT6 are reported jointly when they fall in one reconstructed block, and a label is
not resolved from Route C evidence alone. Negative controls (NC-1 to NC-3, including a shuffled
decoy), a catalytic positive control (CAT_STATE on the LtrA YxDD dyad) and an LtrA numbering
control against the structure 5G2X were run. An anti-circularity check confirmed that no g5 or g6
output was read. The production crosswalk was not changed. Correspondences exist only in the
interpretation layer.

## Independent review

Every gate that authorised a next step was reviewed by a reviewer from a different vendor and
model family than the producer. The reviewer was Codex `gpt-5.6-sol` at maximum reasoning effort,
with a read-only sandbox and no approval escalation. It worked from a fixed review packet whose
artefacts were hash-listed. Verdicts, scores and required repairs were recorded verbatim in
decision records. A positive transition required a score ≥ 6 with no open blocker. When a review
attempt failed for external reasons, the gate stayed open; it was never self-reviewed. Required
repairs to a sealed bundle were applied as additive errata: the frozen files were unchanged, and
a machine-readable erratum table supersedes interpretive columns where needed.

## Software and provenance

All bundles pin their environment by content (`env.lock`), record input hashes (`INPUTS.tsv`)
and output hashes (`OUTPUTS.tsv`), and pass the governance bundle checks. Parameters,
identifiers and landing commits are listed in `tables/stage2_frozen_parameters.tsv` and
`tables/stage2_bundle_index.tsv`.
