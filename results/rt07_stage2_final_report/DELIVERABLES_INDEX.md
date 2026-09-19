# Stage 2 — deliverables index

Source of record: **`main` @ `94a1a78868d6039297c78b3fdcc047d633d6645e`** (Stage 2 closed, reviewed, errata applied).
This bundle: `results/rt07_stage2_final_report/` — reporting only. It computes no science and
modifies no frozen output.

## 1 · Report and thesis sections

| file | what it is |
|---|---|
| `report/STAGE2_TECHNICAL_REPORT.md` | full technical report: question, history, data, mapper, validation, g4–g7a, reviews, negatives, limitations, final statuses |
| `report/THESIS_METHODS.md` | thesis-ready Methods |
| `report/THESIS_RESULTS.md` | thesis-ready Results |
| `report/THESIS_DISCUSSION.md` | thesis-ready Discussion and limitations |
| `OUTLINE.md` | the outline and inventory agreed before the package was built |

## 2 · Tables

| id | file | content |
|---|---|---|
| T1 | `tables/stage2_rt0_rt7_final.tsv` | RT0–RT7: historical evidence, reconstructed interval, mapper reach, final status, caveats |
| T2 | `tables/stage2_claim_evidence_matrix.tsv` | every thesis claim → value → table/record → selector → bundle → landing commit |
| T3 | `tables/stage2_review_ledger.tsv` | every recorded Stage-2 review, with the verbatim literal it was verified against |
| T4 | `tables/stage2_negative_results.tsv` | negative, falsified and null results, and why each is informative |
| T5 | `tables/stage2_frozen_parameters.tsv` | the frozen instrument, read from its control tables |
| T6 | `tables/stage2_resolved_values.tsv` | every value in the prose, with its source |
| T7 | `tables/stage2_figure_plan.tsv` | figure plan: what each figure may and may not show |
| — | `tables/stage2_bundle_index.tsv` | landed Stage-2 bundles with landing and last commits |
| — | `tables/F*.tsv` | the exact numbers each figure plots |

## 3 · Figures (png + svg)

| id | file | question | must not be read as |
|---|---|---|---|
| F1 | figures/F1_review_trajectory.png | How did independent review shape Stage 2? | any quality ranking of the gates beyond their recorded scores |
| F2 | figures/F2_validation.png | Is the instrument callable, specific and transferable? | residue-level accuracy; transfer beyond UG25; specificity against natural non-RT proteins |
| F3 | figures/F3_match_state_sensitivity.png | Is there a universal conserved core? | robustness of the instrument under a2m |
| F4 | figures/F4_catalogue_application.png | What population was mapped, and how did it resolve? | DELETED_STATE or NO_SUPPORTED_MAPPING as biological absence |
| F5 | figures/F5_g6_concordance.png | Is the descriptor reproducible across family strata? | independent family discovery; bounds; 1%-level significance |
| F6 | figures/F6_rt0_rt7_final.png | What is the final reviewed status of each historical label on LtrA? | any RT0 or RT1 coordinate; RT6 alone; universal domains |

The frozen figures `results/rt07_g6_family_architecture/figures/g6_reproducibility.png` and
`results/rt07_g7a_rt0_rt7_bridge/figures/g7a_bridge.png` carry wording superseded on 2026-09-19
(E-g6-2, E-g7a-3). They remain unchanged as audit history. **Use F5 and F6 in the thesis.**

## 4 · RT0–RT7 at a glance

| label | reference interval on LtrA (g2 block; RT0: source upper bound) | frozen-state support | final reviewed status |
|---|---|---|---|
| RT0 | 1-85 | none - 0 frozen anchor states map inside the reference interval; anchor reach is LtrA 97-363 | UNRESOLVED |
| RT1 | 39-61 | none - 0 frozen anchor states map inside the reference interval; anchor reach is LtrA 97-363 | UNRESOLVED |
| RT2 | 79-123 | 17 states (107-133) -> LtrA 97-123 | PARTIAL |
| RT3 | 126-166 | 22 states (136-177) -> LtrA 126-166 | ESTABLISHED (with qualification) |
| RT4 | 170-230 | 42 states (181-241) -> LtrA 170-230 | ESTABLISHED (with frame-instability qualification) |
| RT5 | 304-347 | 34 states (267-301) -> LtrA 311-347 | ESTABLISHED (named jointly as RT5+RT6) |
| RT6 | 304-347 | 34 states (267-301) -> LtrA 311-347 | PARTIAL (jointly with RT5 only) |
| RT7 | 356-361 | 6 states (310-315) -> LtrA 356-361 | ESTABLISHED (with narrowed wording) |

## 5 · Canonical frozen assets

| bundle | layer | role | landing_commit |
|---|---|---|---|
| results/rt07_g1_history_and_definition | L1 | historical definition: sources, genealogy, evidence matrix | 558ee89 |
| results/rt07_g2_reference_reconstruction | L1 | independent reconstruction of the landmarks on ALIGN_000044 | 7fa61b4 |
| results/rt07_g3_prior_method_replication | L1 | audit of prior RT0-RT7 methods and frames | 7a73520 |
| results/rt07_g4a_frame_recovery | L2 | mapper frame recovery (reviewed 6/10, repaired) | 7a73520 |
| results/rt07_g4a_repaired | L2 | repaired mapper development; hhmake -M sensitivity; profile | 4961588 |
| results/rt07_ug5_holdout_gate | L2 | UG5 holdout gate v2/v3 - falsified designs, retained | cd5dcac |
| results/FINAL_PRE_UG25_VALIDATION_BUNDLE | L2 | frozen pre-holdout calibration and construction validation | 4961588 |
| results/rt07_ug25_confirmatory | L2 | single confirmatory transfer to a fresh lineage (Endpoint A) | 7a73520 |
| results/rt07_g4b_production_mapper | L2 | the frozen production instrument | dd9cdae |
| results/rt07_g5a_eligibility_census | L2 | the frozen eligibility denominator | cf96dd1 |
| results/rt07_g5_catalogue_application | L2 | the canonical mapped catalogue | cf96dd1 |
| results/rt07_g6_family_architecture | L3 | descriptive concordance across MyRT-defined strata | 049d7ab |
| results/rt07_g7a_rt0_rt7_bridge | L4 | historical RT0-RT7 bridge on LtrA | 34db87f |

| asset | path |
|---|---|
| production instrument | `results/rt07_g4b_production_mapper/` (`rtmap-1.0.0/53a1e738a19b3896`) |
| profile HMM | `results/rt07_g4a_repaired/work/GII.deriv.hmm` (LENG 471) |
| frozen parameters | `results/rt07_g4b_production_mapper/control/SUPPORT_RULE_FROZEN.tsv`, `CATALYTIC_STATE_FROZEN.tsv`, `FROZEN_ANCHORS.tsv` |
| production crosswalk (UNRESOLVED ×8, by design) | `results/rt07_g4b_production_mapper/control/CROSSWALK_RT0_RT7.tsv` |
| eligibility denominator | `results/rt07_g5a_eligibility_census/` (data in `data/derived/rt07_g5a/`, gitignored) |
| canonical mapped dataset | `results/rt07_g5_catalogue_application/` (data in `data/derived/`, gitignored; see `docs/DATASET_REGISTRY.md`) |

## 6 · Governing records (read the bundles through these)

| record | governs |
|---|---|
| `docs/decisions/2026-09-19_stage2_closed.md` | Stage-2 closure and residual limitations |
| `docs/decisions/2026-09-19_stage2_g6_g7a_independent_reviews.md` | the terminal independent reviews |
| `docs/decisions/2026-09-19_stage2_g6_review_errata.md` | E-g6-1..8 — g6 interpretation |
| `docs/decisions/2026-09-19_stage2_g7a_review_errata.md` | E-g7a-1..5 — g7a interpretation |
| `docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv` | machine-readable RT0–RT7 statuses and permitted wording |
| `review-stage/INDEPENDENT_REVIEW_RESULT_g6.md`, `..._g7a.md` | verbatim reviews (threads `01a0b99f-4837-7ce1-9ddd-9d0138441c55`, `01a0b9a1-1d76-7193-9d7b-89cb6a41e875`) |
| `docs/decisions/2026-09-17_stage2_ug25_confirmatory_closed.md` | validation closure, Endpoint A |
| `docs/decisions/2026-09-17_stage2_g4b_production_packaging.md` | the production freeze |

## 7 · Final commits

| commit | what |
|---|---|
| `94a1a78868d6039297c78b3fdcc047d633d6645e` | source of record: Stage-2 closure aligned in PROJECT_MAP |
| `93a4e88` | Stage 2 closed with explicit residual limitations |
| `3a19e2e` | 13 required review repairs applied as additive errata (g6, g7a) |
| `af7c405` | completed independent reviews of g6 and g7a recorded |
| per bundle | landing commits in §5 and `tables/stage2_bundle_index.tsv` |

The commit that lands this bundle is on branch `rt07-stage2-final-report`.
