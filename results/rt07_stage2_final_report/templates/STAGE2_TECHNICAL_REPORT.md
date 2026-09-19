# Stage 2 — RT0–RT7 definition and the conserved-state mapper: final technical report

Source of record: `main` at `{{pinned}}`. Every number below is resolved at build time from
a landed table, a declared count over landed rows, or a literal checked against a reviewed record
(`tables/stage2_resolved_values.tsv` gives the source for each). This report computes nothing,
changes no frozen output and reopens no Stage-2 question.

`human_input_audit`: **{{hia_pending}}** on the landed bundles. The governance layer requires that
audit before any number here becomes a thesis claim.

---

## 1 · Summary and final statuses

Stage 2 asked whether the historical reverse-transcriptase "domains" RT0–RT7 can be given an
operational meaning on modern RT sequences, and built a frozen instrument to test that. The
instrument is a conserved-state mapper, `{{mapper_version}}`. It places residues of any RT on
{{n_anchors}} frozen conserved states of a group-II-intron-derived profile HMM (LENG
{{profile_leng}}, `{{profile_m}}`). It was validated by one confirmatory transfer to a fresh
lineage (UG25). It was then frozen and applied to the {{g5a_eligible}} eligible exact RTs of the
Stage-1 catalogue, of which {{g5_inspectable}} are inspectable. The mapped catalogue was used for
a family-level descriptive analysis (`g6`) and for a historical bridge from RT0–RT7 to the frozen
states on the group-II intron RT LtrA (`g7a`). Both passed independent, vendor-disjoint review
with zero blockers.

The final reviewed statuses, from the governing erratum table
`docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv`, are:

- **RT0** — UNRESOLVED / NOT IDENTIFIABLE
- **RT1** — UNRESOLVED / NOT IDENTIFIABLE
- **RT2** — PARTIAL / INTERPRETIVE CORRESPONDENCE (only LtrA {{rt2_obs}} of the reconstructed {{rt2_ref}} is observed)
- **RT3** — ESTABLISHED OPERATIONAL CORRESPONDENCE, with qualification (Route C corroborates placement; it is not independent historical replication)
- **RT4** — ESTABLISHED OPERATIONAL CORRESPONDENCE, with frame-instability qualification (1:1 in the primary frame, split into three in the independent frame, Jaccard {{g2_b4_j}})
- **RT5** — ESTABLISHED OPERATIONAL CORRESPONDENCE, named only as the joint RT5+RT6 region; direct YxDD catalytic-feature anchor
- **RT6** — PARTIAL / INTERPRETIVE CORRESPONDENCE, jointly with RT5 only
- **RT7** — ESTABLISHED OPERATIONAL CORRESPONDENCE, with narrowed wording (strongest LtrA-local terminal coordinate, not "the strongest" correspondence without that qualifier)

All eight are **LtrA-local interpretation-layer correspondences**. Production emits `state_id`
only, and the production crosswalk stays `UNRESOLVED` in all eight rows. `g6` shows **descriptive
concordance of the mapper-derived descriptor across largely MyRT-defined strata**. It does not
show independent biological family discovery. {{closure_line}}

![F6 — final reviewed statuses on LtrA](../figures/F6_rt0_rt7_final.png)

## 2 · The scientific question and why RT0–RT7 was a problem

The retron and RT literature describes RT catalytic cores by numbered regions. Xiong & Eickbush
(1990) defined domains 1–7 by alignment. Later work added a domain 0 (RT0) for some
non-LTR-retrotransposon and group-II-intron RTs, and domain X beyond RT7. These labels are
still used to describe RT architecture and to compare RT families. Stage 1 left the project with
a catalogue of {{g5a_total}} exact RT sequences and no defensible way to say which residues of a
given RT belong to "RT3" or "RT0". There were three problems with the inherited labels:

1. **They were defined by procedure, not by coordinates.** Of {{g1_regions}} region names in
   the {{g1_sources}} held sources, {{g1_stated_boundary}} has a stated residue boundary;
   {{g1_derivable}} can be derived only as a procedure (align, then read printed columns).
2. **The defining source for RT0 is not held.** {{malik_missing}} could not be retrieved. What the
   held sources say about RT0 is an upper bound (the LtrA fragment M1–R85 *contains* RT0) and an
   interior point (A{{g3_rt0_alanine}}). No held source states an RT0|RT1 boundary.
3. **Prior project frames were not independent evidence.** They were coordinate transfers over
   one anchor-derived landmark set (g3), so their agreement looked like replication but was not.

Stage 2 therefore separated the question into five layers and kept them apart in every
deliverable:

| layer | question | bundles |
|---|---|---|
| L1 historical definition | what did RT0–RT7 ever mean, on what evidence? | g1, g2, g3 |
| L2 operational mapping | can a frozen instrument map conserved states to residues, and does it transfer? | g4a → validation trail → UG25 → g4b → g5a/g5 |
| L3 family-level description | is the mapper-derived descriptor reproducible across family strata? | g6 |
| L4 historical bridge | how do historical labels correspond to operational states on LtrA? | g7a |
| L5 reviewed interpretation | what survives independent adversarial review? | review records, errata, closure |

## 3 · Data and analytical units

| unit | n | source |
|---|---|---|
| exact RT sequence, Stage-1 catalogue | {{g5a_total}} | `rt07_g5a_eligibility_census` |
| eligible (≥ {{min_aa}} aa, 20 standard residues) — **the frozen denominator** | {{g5a_eligible}} | `g5a_census_summary.tsv` |
| ineligible: below minimum length / non-standard residue | {{g5a_short}} / {{g5a_nonstd}} | same |
| inspectable (frozen verdict MAPPED) | {{g5_inspectable}} | `g5_qc_headline.tsv` |
| abstained (not failure, not absence) | {{g5_abstained}} | same |
| state call (eligible × {{n_anchors}} anchors) | {{g5_state_rows}} | same |
| CAT_STATE-mapped sequence (**separate denominator**) | {{g5_cat_mapped}} | same |
| historical reference alignment ALIGN_000044 | {{g1_aln_seqs}} sequences × {{g1_aln_cols}} columns | g1 |
| bridge substrate | LtrA (P0A3U0) | g7a |
| historical label | 8 (RT0–RT7) | g7a |

The analytical unit for the mapper is the **exact RT sequence**. For g6 it is the **family or
subtype stratum**, and for g7a it is the **historical label on LtrA**. Numbers from different
units are never pooled.

## 4 · L1 — Historical definition (g1, g2, g3)

**g1 — sources and evidence.** {{g1_sources}} held sources were read against {{g1_regions}}
region names, giving a {{g1_cells}}-cell evidence matrix with {{g1_cells_evidence}} cells carrying
evidence. {{g1_quotes}} quotations were verified against the PDFs ({{g1_quotes_bad}}
unverifiable). The citation genealogy has {{g1_edges}} edges, {{g1_edges_unheld}} of them to
sources the project does not hold. The Zimmerly RT alignment ALIGN_000044 (submitted
{{g1_aln_submitted}}) was acquired and verified. It carries {{g1_aln_subdomains}} numbered
subdomain annotations, so every coordinate has to be reconstructed.

**g2 — independent reconstruction.** On ALIGN_000044 ({{g2_proteins}} proteins, {{g2_groups}}
lineage groups) the project reconstructed conserved blocks independently in two alignment
frames. Conserved positions ({{g2_cons}}; null p = {{g2_p_cons}}) and the widest inter-block gap
(p = {{g2_p_gap}}) exceed their nulls. The **block count does not** (p = {{g2_p_block}}):
{{g2_blocks}} blocks in frame 1, {{g2_blocks_f2}} in frame 2. The seven-way partition is recovered
in frame 2 ({{g2_seven_f2}}) and not in frame 1 ({{g2_seven_f1}}), so the verdict on the partition
itself is **{{g2_kill_verdict}}**. {{g2_one_to_one}} blocks correspond one-to-one across frames
(median Jaccard {{g2_median_j}}). Block 4 is the exception: it splits into three in frame 2
(Jaccard {{g2_b4_j}}). No block corresponds to RT0 (`rt0_block_created` = {{g2_rt0_block}}). The
main kill criterion (landmarks unrecoverable on their own substrate) was **{{g2_kill_main}}**:
{{g2_rec}} landmarks were recovered and {{g2_part}} partially recovered.

**g3 — prior-method audit.** {{g3_claims}} prior project claims were regenerated.
{{g3_repro}} reproduced on the same object and frame and {{g3_partial}} partially. {{g3_circular}}
were circular or seed-dependent, {{g3_objmis}} were object mismatches and {{g3_framemis}} was a
frame mismatch; {{g3_withdrawn}} had been withdrawn by the prior work itself and {{g3_nottest}}
were not testable. The prior anchors were {{g3_anchor_seed_pct}}% inside the seed that defined
them. {{g3_landmarks_inside}} prior landmarks fall inside a g2 region, but only
{{g3_blocks_anchored}} prior-frame blocks were fixed by a published motif. {{g3_collapsing}}
collapse onto a single reconstructed region, and RT0 is **{{g3_rt0_verdict}}**: the prior frame
spans LtrA {{g3_rt0_frame_extent}} and does not cover RT0's source-stated alanine
A{{g3_rt0_alanine}}.

**What L1 establishes.** RT2–RT7 can be reconstructed as **intervals** on LtrA. Placement is
recoverable; the number of numbered regions depends on the alignment frame. RT0 has no
recoverable coordinate object in the held evidence.

## 5 · L2 — The operational mapper

### 5.1 Design

Three design reviews rejected the first designs before the working design emerged (§8, F1). The rejected
designs tried to estimate RT0–RT7 architecture directly. They failed on identifiability. The
accepted design estimates something smaller: whether each of {{n_anchors}} frozen conserved
states of `GII.deriv.hmm` (LENG {{profile_leng}}) is occupied by a residue of the query, and
which one. Each state call is **MAPPED** (posterior ≥ PP_HI {{pp_hi}}), **AMBIGUOUS** (between
PP_LO {{pp_lo}} and PP_HI), **UNSUPPORTED** or **DELETED_STATE**. A sequence is committed
(verdict MAPPED) only if its domain bitscore exceeds S_MIN {{s_min}} and at least K_MIN
{{k_min}} anchors are MAPPED. Otherwise it abstains with a reason code. DELETED_STATE means the
alignment path skips the state. It does not mean the region is biologically absent.

### 5.2 Calibration and construction validation

Parameters were calibrated on six construction families only and then frozen (T5,
`tables/stage2_frozen_parameters.tsv`). On {{cv_n}} construction sequences, {{cv_ok}} were
committed. Median per-sequence MAPPED fraction ranged from {{cv_med_retron}} (Retrons) to
{{cv_med_gii}} (GII), against the floor T1 = {{t1}}. The catalytic state was frozen as
CAT_STATE {{cat_state}}: {{cat_count}} MAPPED [YF].DD occurrences, construction agreement
{{cat_agree}}, runner-up state {{cat_runner}}. CAT_STATE is **not** one of the {{n_anchors}}
anchors and always has its own denominator.

### 5.3 Match-state sensitivity: no universal core

The set of states shared by all families depends on the HMM match-state convention (F3). Under
`hhmake -M 50`, GII keeps {{m50_gii_all}} all-partner states ({{m50_gii_pct}}% of its full
consensus), and UG5 keeps only {{m50_ug5_pct}}%. Under `-M a2m`, DGRs and AbiA keep
**{{a2m_dgr_all}}** and **{{a2m_abia_all}}**. There is therefore no convention-invariant universal
conserved core. The instrument is validated under `-M 50` only.

![F3](../figures/F3_match_state_sensitivity.png)

### 5.4 Falsified transfer designs (retained)

- **UG5 v2** failed its predeclared criterion 2: monotone placement held for {{ug5_v2_monotone}}. This is a valid falsifying result and is kept.
- **UG5 v3** was reviewed FAIL/BLOCK (5/10) because it was a detection sub-gate, not a mapper
  gate.
- **G2L residue transfer** was reviewed {{g2l_score}}. The predeclared criterion requiring
  support under a frozen score rule was not met (the gate code had no score or posterior), and
  G2L is a fresh family within a related lineage, not a fresh lineage. The review found no
  leakage into construction. This led to the posterior-based support rule and to an untouched,
  genealogically audited holdout (UG25).

### 5.5 UG25 confirmatory transfer (Endpoint A)

UG25 was opened once, after every parameter was frozen. The genealogy audit found
{{ug25_overlap}} exact overlaps with construction and {{ug25_fulllink}} sequences meeting the
full link rule, so UG25 is classified **{{ug25_class}}**. Both qualifying components passed C1
(medians {{ug25_k0_med}}, n = {{ug25_k0_n}}; {{ug25_k1_med}}, n = {{ug25_k1_n}}; T1 = {{t1}}).
Catalytic concordance C3 was {{ug25_c3}}. The component difference C4 was {{ug25_c4}}, within
D_MAX {{d_max}}. This is a weak bound: the same-population null D_RANDOM is {{d_random}}. Of
{{ug25_ctrl_n}} synthetic controls (MONO/DI/REV shuffles of real RTs), {{ug25_ctrl_valid}} were
valid. The largest MAPPED-anchor count in any control was {{ug25_ctrl_max}} (MONO
{{ug25_mono_max}}, DI {{ug25_di_max}}, REV {{ug25_rev_max}}), against K_MIN {{k_min}} and a weakest
real UG25 sequence of {{ug25_min_real_mapped}}. Post-run review: {{ug25_review}} — confirmatory
transfer SUPPORTED.

![F2](../figures/F2_validation.png)

### 5.6 Production freeze (g4b) and application (g5a, g5)

The validated mapper was frozen as `{{mapper_version}}` (instrument sha256
`{{instrument_sha}}`). The identifier hashes the mapper code, the profile, the anchor set, the
parameters, the eligibility rule and the domain-scoring protocol. Packaging review:
{{g4b_review}}. The eligibility census (g5a) selected {{g5a_eligible}} of {{g5a_total}} exact RTs
(fraction {{g5a_frac}}) exactly once. The application (g5) processed all of them with
{{g5_failures}} tool failures: {{g5_inspectable}} inspectable, {{g5_abstained}} abstained. By
inspectability status: MAPPABLE {{g5_mappable}}, PARTIAL_MAPPING {{g5_partial}},
AMBIGUOUS_MAPPING {{g5_ambig}}, NO_SUPPORTED_MAPPING {{g5_nosupp}}. Of {{g5_cat_mapped}}
CAT_STATE-mapped sequences, {{g5_cat_conf}} ({{g5_cat_ratio}}) begin [YF].DD at that state. This
is motif concordance at a state, not residue-level truth. Application review: {{g5_review}}.

![F4](../figures/F4_catalogue_application.png)

## 6 · L3 — Family-level description (g6)

**Question.** Is the per-family profile of conserved-state occupancy reproducible between two
halves of the catalogue that share no sequence cluster?

**Result as landed.** Between families ({{g6_groups}} qualifying of {{g6_families}};
{{g6_nseq}} sequences; {{g6_clusters}} clusters at identity 0.90), the split-half rank
correlation is {{g6_rho}}. The sequence-level null (NULL-1) p99 is {{g6_null1}} and the
cluster-level null (NULL-2) p99 is {{g6_null2}}, so the observed value exceeds NULL-2 but not
NULL-1. The landed verdict is `{{g6_verdict}}`. {{g6_ctrl_exceed_both}} visibility-restricted and
relatedness-collapsed analyses exceed every sampled replicate of both nulls. Within retrons, the
DefenseFinder subtype strata give {{g6_df_rho}} ({{g6_df_groups}} strata) and the PADLOC strata
give {{g6_pl_rho}} ({{g6_pl_groups}} strata), each on its own denominator. The label-free arm is
{{g6_lf_verdict}}. The catalytic positive control (PC-POS) result is {{g6_pcpos_result}}.

**Reviewed interpretation (errata E-g6-1..8).**

- **Concordance, not discovery.** The between-family labels are essentially MyRT-derived:
  `stage1_collapsed_family` equals the raw MyRT label on {{myrt_match}} eligible records, and
  {{myrt_direct}} carry a direct MyRT call. g6 shows that the descriptor is reproducible and
  concordant across MyRT-defined strata. It does **not** show independent discovery of
  biological RT family structure. Grouping and measurement are both sequence/profile-derived. A
  pure sequence-partition counter-test ({{g6_c2}}) shows that beating NULL-2 is not automatic.
  It does not remove the partial circularity.
- **The two nulls are sensitivity analyses with opposite biases, not bounds.** The observed
  statistic exceeds one imperfect permutation distribution and not the other.
- **"Exceeds both nulls" is descriptive.** 60 permutations cannot calibrate a 1% tail (floor
  {{g6_perm_floor}}), and no multiplicity control was applied across {{g6_n_analyses}} analyses.
- **Subtype power.** {{g6_strata_excluded}} of {{g6_strata_total}} strata did not enter a
  distance matrix, not {{g6_strata_underpowered}} as the frozen summary states.
- **Leakage has two units.** Cross-half identity ≥ 0.90 affects {{g6_leak_hits}}; and
  {{g6_leak_queries}} have at least one such opposite-half partner. The search kept at most five
  targets per query, and the query figure is a one-direction sample.
- **The rank statistic uses ordinal tie-breaking.** On the positive control it gives
  {{g6_pcpos_bundle}} where standard tie-aware Spearman gives {{g6_pcpos_std}}. The per-half
  vectors were not landed, so the values stay frozen as reported. Each g6 ρ is read as "a rank
  correlation with ordinal tie-breaking".
- **Visibility.** Concordance persists after conditioning on scalar MAPPED fraction. This does
  not remove state-specific callability effects: profile distance correlates with the MAPPED-
  fraction difference at ρ = {{g6_vis_assoc}}.
- **Post-hoc additions disclosed.** Both nulls on every analysis, the five-group minimum and the
  "missing null → UNDERPOWERED" rule were added after predeclaration.

![F5](../figures/F5_g6_concordance.png)

## 7 · L4 — The historical bridge (g7a)

**Question.** On one well-characterised RT (LtrA, P0A3U0), which frozen conserved states fall
inside the reconstructed interval of each historical label?

**Substrate and reach.** LtrA is inspectable: {{g7_anchors_ltra}} of {{n_anchors}} anchors are
MAPPED, spanning state_id {{g7_state_span}} and **LtrA {{g7_anchor_span}}**. Everything
N-terminal of that span is out of the instrument's reach. LtrA numbering was checked against
the sources ({{g7_numbering}}). Controls: {{g7_ctrl_pass}} pass, {{g7_ctrl_fail}} fail,
{{g7_ctrl_inc}} inconclusive. The evidence register has {{g7_register}} (label, source) rows,
{{g7_register_stated}} of them source-stated.

**Routes.** Route P uses the reconstructed g2 interval, anchored on LtrA. Route C uses prior-frame
comparator points. Route S uses source-stated residues. Per E-g7a-1, Route C is computationally
distinct from Route P but is not an independent primary historical determination. g3 showed the
prior frames are transfers over {{g7a_route_c_note}}. Agreement between them is therefore
**corroboration of placement**.

**Per label** (T1, `tables/stage2_rt0_rt7_final.tsv`):

{{TABLE:rt0_rt7_final}}

**Source-stated correspondences (E-g7a-2).** Xiong & Eickbush 1990 state two motif-set
correspondences directly: X05, {{x05}}, and X06, {{x06}}. Neither gives LtrA coordinates and
neither touches RT0 or RT1. RT5 remains the only label with a source-stated residue-level
catalytic feature measured on LtrA: CAT_STATE {{cat_state}} → {{cat_ltra}}.

## 8 · L5 — Independent review

Every Stage-2 gate that moved the project forward passed an independent review by a
vendor-disjoint reviewer (Codex `gpt-5.6-sol`, read-only). Failed reviews were recorded and
never overwritten. The ledger (T3) lists every review recorded in the decision records and the
g5 commit message; each verdict and score is checked verbatim against its record at build time.

{{TABLE:review_ledger}}

![F1](../figures/F1_review_trajectory.png)

The terminal reviews: g6 {{g6_review}} (thread `{{g6_thread}}`) and g7a {{g7a_review}} (thread
`{{g7a_thread}}`). They produced 13 required repairs, applied as **additive errata**: E-g6-1..8 in
`docs/decisions/2026-09-19_stage2_g6_review_errata.md` and E-g7a-1..5 in
`docs/decisions/2026-09-19_stage2_g7a_review_errata.md`, with the machine-readable
`docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv`. **No sealed bundle was edited.** All
eight RT0–RT7 statuses were preserved. The review changed the wording: RT3/RT4/RT7 qualified,
RT4 frame instability made mandatory, RT7 ranking narrowed, the X05/X06 correspondences
restored, the withdrawn RT0 fragment equation removed from LAUNCHER_03, and g6 reframed as
concordance.

## 9 · Negative and null results, and why each is informative

{{TABLE:negatives}}

These results are kept on purpose. Each one removes a claim that would otherwise be tempting —
a universal core, a stable seven-domain count, independent prior frames, an RT0 coordinate —
and each one narrows the scope of what the instrument is validated for.

## 10 · Limitations

1. **LtrA-local.** Every RT0–RT7 correspondence is established on one protein. Transfer of the
   historical labels to other RTs is not claimed, even though the frozen `state_id` system is
   applied catalogue-wide.
2. **N-terminal blind spot.** The anchors reach only LtrA {{g7_anchor_span}}. RT0, RT1
   and the N-terminal part of RT2 cannot be observed with this instrument.
3. **Primary evidence gap.** {{malik_missing}}, the defining source for RT0, is not held. RT0 and RT1 may not be resolved by inference,
   analogy, interpolation or structural reasoning.
4. **Validation scope.** Transfer is shown to one fresh lineage (UG25) under `-M 50`. Not
   established: transfer beyond UG25, specificity against unrelated natural proteins, residue
   accuracy against external truth, robustness under `-M a2m` or equivalence under `-M 60`.
5. **Frame dependence.** The number of numbered regions, and RT4's cardinality, depend on the
   alignment frame.
6. **g6 modality and statistics.** Labels and measurement share sequence/profile modality. The
   rank statistic uses ordinal tie-breaking. The nulls are too small for 1% tails and there is
   no multiplicity control. {{g6_strata_excluded}} of {{g6_strata_total}} subtype strata are excluded.
7. **Reviewer coverage.** The g7a packet hashes cover review artefacts, not generator scripts.
   The reviewer did not verify printed figure extents or the unheld Malik definition.
8. **Human input audit pending.**

## 11 · Final statuses and what may be claimed

{{TABLE:claims}}

**Not claimable from Stage 2:** universal RT architecture; universal RT0–RT7 domains;
residue-level accuracy against external truth; transfer beyond UG25; specificity against
unrelated natural proteins; robustness under `-M a2m`; equivalence under `-M 60`; independent
discovery of RT family structure; accuracy against MyRT / PADLOC / DefenseFinder labels;
biological absence of any region the instrument cannot see.

**Why UNRESOLVED and PARTIAL are results, not failures.** An `UNRESOLVED` status here is a
localised, evidenced statement. It says which evidence is missing (a stated boundary, the Malik
definition) and which part of the protein the instrument cannot see (N-terminal of LtrA 97).
Both limits are named and measured, and it is known what new evidence could change them. The
alternative would be to assign RT0 and RT1 coordinates from the inherited frames, which g3
showed to be circular, or to read the fragment M1–R85 as RT0's extent, which the source does not
say. Either would put an unsupported label on every RT in the catalogue. `PARTIAL` for RT2 and
RT6 records resolution rather than doubt about location. For RT2, part of the interval lies
outside the instrument's reach. For RT6, the reconstruction cannot separate it from RT5. Keeping
these statuses is what lets the four ESTABLISHED correspondences stand: the same rules that
refused RT0 and RT1 accepted RT3, RT4, RT5 and RT7.

## 12 · Reproducibility and audit

{{TABLE:bundles}}

- Rebuild: `bash results/rt07_stage2_final_report/run.sh` reruns the figures and this report
  into scratch and compares every landed artefact byte for byte.
- `verify.sh` checks, independently: the eight statuses against the erratum, the production
  crosswalk (still UNRESOLVED), the absence of superseded wording, every review literal, the
  source hashes in `INPUTS.tsv`, and that no frozen bundle has uncommitted changes.
- Every number: `tables/stage2_resolved_values.tsv`. Every claim: `tables/stage2_claim_evidence_matrix.tsv`.
