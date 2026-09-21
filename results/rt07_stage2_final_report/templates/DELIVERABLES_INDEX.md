# Stage 2 — deliverables index

Source of record: **`main` @ `{{pinned}}`** (Stage 2 closed, reviewed, errata applied).
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

{{TABLE:figures}}

The frozen figures `results/rt07_g6_family_architecture/figures/g6_reproducibility.png` and
`results/rt07_g7a_rt0_rt7_bridge/figures/g7a_bridge.png` carry wording superseded on 2026-09-19
(E-g6-2, E-g7a-3). They remain unchanged as audit history. **Use F5 and F6 in the thesis.**

## 4 · RT0–RT7 at a glance

{{TABLE:rt0_rt7_compact}}

## 5 · Canonical frozen assets

{{TABLE:bundles}}

| asset | path |
|---|---|
| production instrument | `results/rt07_g4b_production_mapper/` (`{{mapper_version}}`) |
| profile HMM | `results/rt07_g4a_repaired/work/GII.deriv.hmm` (LENG {{profile_leng}}) |
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
| `review-stage/INDEPENDENT_REVIEW_RESULT_g6.md`, `..._g7a.md` | verbatim reviews (threads `{{g6_thread}}`, `{{g7a_thread}}`) |
| `docs/decisions/2026-09-17_stage2_ug25_confirmatory_closed.md` | validation closure, Endpoint A |
| `docs/decisions/2026-09-17_stage2_g4b_production_packaging.md` | the production freeze |

## 7 · Final commits

| commit | what |
|---|---|
| `{{pinned}}` | source of record: Stage-2 closure aligned in PROJECT_MAP |
| `{{commit_closure}}` | Stage 2 closed with explicit residual limitations |
| `{{commit_errata}}` | 13 required review repairs applied as additive errata (g6, g7a) |
| `{{commit_reviews}}` | completed independent reviews of g6 and g7a recorded |
| per bundle | landing commits in §5 and `tables/stage2_bundle_index.tsv` |

The commit that lands this bundle is on branch `rt07-stage2-final-report`.
