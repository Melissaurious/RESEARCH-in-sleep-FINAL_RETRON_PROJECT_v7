# Results — RT0–RT7 from historical labels to operational states

*Thesis chapter section. Every number is resolved from the landed Stage-2 record at
`{{pinned_short}}` (`tables/stage2_resolved_values.tsv`). Figures are in `../figures/`.*

## The historical labels are procedural, and RT0 has no recoverable coordinate

Of {{g1_regions}} region names in {{g1_sources}} held sources, {{g1_stated_boundary}} carries a
stated residue boundary; {{g1_derivable}} can be derived only by procedure. The alignment from
which the numbered series was later drawn (ALIGN_000044, {{g1_aln_seqs}} sequences) carries
{{g1_aln_subdomains}} subdomain annotations. The defining source for RT0, {{malik_missing}}, could
not be obtained. The held sources give RT0 only an upper bound (the LtrA fragment M1–R85, which
contains it) and an interior residue (A{{g3_rt0_alanine}}). They place R85 inside RT1 and state
no RT0|RT1 boundary.

Reconstructing the landmarks independently on {{g2_proteins}} reference proteins recovered their
**placement** but not their **number**. Conserved positions (p = {{g2_p_cons}}) and the widest
inter-block gap (p = {{g2_p_gap}}) exceeded column-permutation nulls. The block count did not
(p = {{g2_p_block}}): {{g2_blocks}} blocks in the published frame against {{g2_blocks_f2}} in an
independent realignment. A seven-way partition appeared in one frame and not the other. {{g2_one_to_one}} of
{{g2_blocks}} blocks matched one-to-one across frames (median Jaccard {{g2_median_j}}). Block 4 split into
three (Jaccard {{g2_b4_j}}). No block corresponded to RT0.

Earlier project frames were not independent evidence. Of {{g3_claims}} prior claims,
{{g3_repro}} reproduced on the same object and frame and {{g3_circular}} were circular or
seed-dependent. The prior anchors lay {{g3_anchor_seed_pct}}% inside their own defining seed. The
prior RT0 was an object mismatch, and {{g3_collapsing}} collapsed onto one reconstructed region.

## A conserved-state mapper transfers to a fresh lineage

Three design reviews rejected designs that estimated RT0–RT7 architecture directly (Fig. F1). The
accepted instrument maps residues to {{n_anchors}} frozen conserved states. It did not reveal a
universal conserved core. Under `-M a2m`, DGRs and AbiA shared **{{a2m_dgr_all}}** and
**{{a2m_abia_all}}** states with the other families (Fig. F3), so the instrument is valid under
`{{profile_m}}` only.

In construction, {{cv_ok}} of {{cv_n}} sequences were committed. Family medians of per-sequence
MAPPED fraction ranged from {{cv_med_retron}} to {{cv_med_gii}} (Fig. F2a). The catalytic state
(CAT_STATE {{cat_state}}) agreed with the [YF].DD motif in {{cat_agree}} of construction
occurrences. A first holdout design failed its predeclared monotonicity criterion
(monotone for {{ug5_v2_monotone}}), and a residue-transfer gate on G2L was rejected because it
had no frozen score rule and G2L was not a fresh lineage. On the predeclared fresh lineage UG25 ({{ug25_overlap}} exact overlaps with
construction; {{ug25_fulllink}} sequences meeting the full link rule), both qualifying components
cleared the floor T1 = {{t1}} (medians {{ug25_k0_med}} and {{ug25_k1_med}}; Fig. F2b). Catalytic
concordance was {{ug25_c3}}. No synthetic control reached the commitment floor: the maximum was
{{ug25_ctrl_max}} MAPPED anchors against K_MIN = {{k_min}}, while the weakest real UG25 sequence
had {{ug25_min_real_mapped}} (Fig. F2c). The confirmatory transfer was supported on independent
review ({{ug25_review}}).

## The frozen instrument resolves most of the Stage-1 catalogue

Of {{g5a_total}} exact RT sequences, {{g5a_eligible}} were eligible ({{g5a_frac}}). Most
exclusions were short sequences ({{g5a_short}}); {{g5a_nonstd}} had non-standard residues. All
eligible sequences were processed with {{g5_failures}} tool failures. {{g5_inspectable}} were
inspectable and {{g5_abstained}} abstained (Fig. F4). Of {{g5_state_rows}} state calls,
{{cs_mapped}} were MAPPED and {{cs_del}} were DELETED_STATE. Of {{g5_cat_mapped}} sequences with a
MAPPED catalytic state, {{g5_cat_ratio}} carried [YF].DD there. Abstention, NO_SUPPORTED_MAPPING
and DELETED_STATE are outcomes of the instrument; they are not evidence of biological absence.

## The conserved-state descriptor is concordant across MyRT-defined strata

Across {{g6_groups}} family strata, the between-family occupancy distances of two
cluster-disjoint halves had a rank correlation of {{g6_rho}}. This exceeded the cluster-level
null (p99 {{g6_null2}}) but not the sequence-level null (p99 {{g6_null1}}) (Fig. F5). The two
nulls are sensitivity analyses with opposite biases, not bounds on the truth.
{{g6_ctrl_exceed_both}} analyses restricted by MAPPED fraction or collapsed by relatedness
exceeded every sampled replicate of both nulls. With 60 permutations and {{g6_n_analyses}}
analyses, this is descriptive, not a calibrated 1% test. Within retrons, DefenseFinder and PADLOC
subtype strata gave {{g6_df_rho}} and {{g6_pl_rho}} on their own denominators. The label-free arm
was {{g6_lf_verdict}}, and {{g6_strata_excluded}} of {{g6_strata_total}} subtype strata lacked the
power to enter.

Because the family labels are essentially MyRT-derived ({{myrt_match}} records identical to the
raw MyRT label), this result shows **descriptive concordance of the mapper-derived descriptor
across largely MyRT-defined strata**. It does not show independent discovery of biological RT
family structure. The rank statistic uses ordinal tie-breaking; on the positive control, standard
Spearman would give {{g6_pcpos_std}} rather than {{g6_pcpos_bundle}}.

## RT3, RT4, RT5+RT6 and RT7 correspond operationally on LtrA; RT0 and RT1 remain unresolved

On LtrA, {{g7_anchors_ltra}} of {{n_anchors}} anchors were MAPPED, spanning residues
{{g7_anchor_span}}. Controls gave {{g7_ctrl_pass}} passes and {{g7_ctrl_fail}} failures. Placing
each reconstructed interval on this map gave the final reviewed statuses (Fig. F6; Table T1):

- RT0 — UNRESOLVED / NOT IDENTIFIABLE. No stated extent; 0 anchors in LtrA {{rt0_ref}}.
- RT1 — UNRESOLVED / NOT IDENTIFIABLE. 0 anchors in the reconstructed LtrA {{rt1_ref}}; the nearest MAPPED anchor lies beyond the declared tolerance.
- RT2 — PARTIAL / INTERPRETIVE CORRESPONDENCE. {{rt2_n}} states support LtrA {{rt2_obs}} of the reconstructed {{rt2_ref}}.
- RT3 — ESTABLISHED OPERATIONAL CORRESPONDENCE, with qualification. {{rt3_n}} states, LtrA {{rt3_obs}}; prior-frame agreement corroborates placement but is not independent replication.
- RT4 — ESTABLISHED OPERATIONAL CORRESPONDENCE, with frame-instability qualification. {{rt4_n}} states, LtrA {{rt4_obs}}; one-to-one in the primary frame, split into three in the independent frame (Jaccard {{g2_b4_j}}).
- RT5 — ESTABLISHED OPERATIONAL CORRESPONDENCE, as the joint RT5+RT6 region. {{rt5_n}} states, LtrA {{rt5_obs}}; the catalytic state maps to {{cat_ltra}}.
- RT6 — PARTIAL / INTERPRETIVE CORRESPONDENCE, jointly with RT5 only. No state can be attributed to RT6 rather than RT5.
- RT7 — ESTABLISHED OPERATIONAL CORRESPONDENCE, with narrowed wording. {{rt7_n}} states, LtrA {{rt7_obs}}, immediately N-terminal of the source-described proteolytic landmark R364/R365.

{{TABLE:rt0_rt7_compact}}

These are LtrA-local interpretation-layer correspondences. The production instrument emits
`state_id` only. Both terminal analyses passed independent review with zero blockers (g6:
{{g6_review}}; g7a: {{g7a_review}}). All eight statuses were preserved, and the 13 required
repairs changed wording only.
