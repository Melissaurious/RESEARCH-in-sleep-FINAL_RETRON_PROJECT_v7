# Stage-2 final reporting package — outline, inventory and file paths

Source of record: `main` at **`94a1a78868d6039297c78b3fdcc047d633d6645e`** (Stage 2 closed).
Bundle: `results/rt07_stage2_final_report/` · branch `rt07-stage2-final-report`.

**This package computes no science.** It re-reads landed tables and reviewed records. Every
number in the prose is a lookup resolved at build time from a named landed table, or a quoted
literal verified to be present in a named reviewed record. The build fails if any lookup does
not match exactly one row, if any placeholder is left unresolved, or if the RT0–RT7 statuses
differ from the reviewed statuses. Frozen bundles are not modified or re-run.

---

## 1 · The five layers the narrative keeps separate

| layer | question | where it lives |
|---|---|---|
| **L1 · historical definition** | what did RT0–RT7 ever mean, and on what evidence? | `g1`, `g2`, `g3` |
| **L2 · operational mapping** | can a modern instrument map conserved HMM states to residues, and does it transfer? | `g4a` → validation trail → UG25 → `g4b` → `g5a`/`g5` |
| **L3 · family-level description** | is the mapper-derived descriptor reproducible across family strata? | `g6` |
| **L4 · historical bridge** | how do the historical labels correspond to the operational states on LtrA? | `g7a` |
| **L5 · reviewed interpretation** | what survives independent adversarial review? | review records + errata + closure |

## 2 · Technical report — `report/STAGE2_TECHNICAL_REPORT.md`

1. Summary and final statuses
2. The scientific question and why RT0–RT7 was a problem
3. Data and analytical units
4. **L1** Historical definition — sources, genealogy, reconstruction on `ALIGN_000044`, prior-method audit
5. **L2** The operational mapper — design, calibration, the validation trail including every failed design, UG25 confirmatory transfer, `-M` sensitivity, production freeze, eligibility census, catalogue application
6. **L3** Family-level description (`g6`) — concordance across largely MyRT-defined strata
7. **L4** The historical bridge (`g7a`)
8. **L5** Independent review — full review ledger and the final errata
9. Negative and null results, and why each is informative
10. Limitations
11. Final statuses and what may be claimed
12. Reproducibility and audit

## 3 · Thesis sections

| file | content |
|---|---|
| `report/THESIS_METHODS.md` | historical-evidence audit; reconstruction; mapper construction and calibration; validation design and controls; confirmatory transfer; production freeze; census and application; family-level analysis; historical bridge; independent review protocol |
| `report/THESIS_RESULTS.md` | results in L1 → L5 order, every number resolved from a landed table |
| `report/THESIS_DISCUSSION.md` | concise discussion and limitations; why UNRESOLVED/PARTIAL are informative |

## 4 · Table inventory — `tables/`

| id | file | content |
|---|---|---|
| T1 | `stage2_rt0_rt7_final.tsv` | **RT0–RT7 final table**: region, historical evidence, mapper reach on LtrA, operational status, caveats |
| T2 | `stage2_claim_evidence_matrix.tsv` | every thesis claim → bundle, table, selector, value, landing commit |
| T3 | `stage2_review_ledger.tsv` | every Stage-2 independent review: object, verdict, score, disposition, record |
| T4 | `stage2_negative_results.tsv` | every negative / falsified / withdrawn result and what it taught |
| T5 | `stage2_frozen_parameters.tsv` | the frozen instrument, read from its control tables |
| T6 | `stage2_resolved_values.tsv` | every resolved value with its exact source (the audit trail) |
| T7 | `stage2_figure_plan.tsv` | the figure plan: source tables, what each figure may and may not show |
| — | `stage2_bundle_index.tsv` | the 13 landed Stage-2 bundles with landing commits |

## 5 · Figure inventory — `figures/`

All re-plotted from landed tables; frozen original figures are not altered.

| id | file | shows | source tables |
|---|---|---|---|
| F1 | `F1_review_trajectory` | every recorded independent review score in sequence, by layer, against the ≥ 6 transition threshold (built instead of a data-free schematic) | `tables/stage2_review_ledger.tsv`, transcribed and verified from `docs/decisions/` |
| F2 | `F2_validation` | construction callability by family vs `T1`; UG25 components; synthetic controls vs weakest real sequence | `construction_validation_family.tsv`, `ug25_component_summary.tsv`, `ug25_control_summary.tsv`, `ug25_sequence_results.tsv` |
| F3 | `F3_match_state_sensitivity` | `ALL_PARTNERS` share per family under `-M 50 / 60 / a2m` — the refuted universal core | `g4a_hhmake_M_sensitivity.tsv` |
| F4 | `F4_catalogue_application` | denominator funnel 501,561 → 369,381 → 354,102; call-state composition | `g5a_census_summary.tsv`, `g5_qc_headline.tsv`, `g6_summary.tsv` |
| F5 | `F5_g6_concordance` | split-half concordance vs both nulls, reviewed wording (sensitivity nulls, not bounds; ordinal tie-breaking) | `g6_between_family_rho.tsv`, `g6_within_retron_rho.tsv` |
| F6 | `F6_rt0_rt7_final` | **final reviewed RT0–RT7 statuses on LtrA**, anchor reach, RT4 frame instability, joint RT5+RT6, RT0/RT1 outside reach | `g7a_state_to_residue.tsv`, `g7a_crosswalk_resolved.tsv`, `docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv` |

Not produced, because frozen outputs do not support them without recomputation: any
re-analysis of g6 under standard tie-aware Spearman (per-half vectors not landed); any structural
placement (Stage 3, independent).

## 6 · Index and audit

| file | content |
|---|---|
| `DELIVERABLES_INDEX.md` | pointers to every canonical frozen asset, every report file, and the final commits |
| `README.md`, `PROVENANCE.md`, `MANIFEST.tsv`, `INPUTS.tsv`, `OUTPUTS.tsv`, `run.sh`, `verify.sh`, `env.lock` | governance bundle standard |
| `scripts/findings.py` | the value registry: every number's source |
| `scripts/ledger.py` | transcribed reviews, negative results, claims and figure plan |
| `scripts/build.py` | resolves values, builds tables, renders `templates/` → `report/`, fails closed |
| `scripts/figures.py` | re-plots F1–F6 from landed tables |
| `scripts/seal.py` | writes MANIFEST, INPUTS, PROVENANCE and OUTPUTS (these may not be hand-written) |
