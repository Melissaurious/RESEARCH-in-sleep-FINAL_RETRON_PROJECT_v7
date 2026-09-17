# rt07_pre_g4_identifiability_redesign

**Design artifacts only. No measurement is produced here and no compute was spent on data.**

This directory holds the reviewed object for the Stage-2 `g4` redesign that follows the round-1
design review's `3/10 / not ready` verdict. The binding record is
`docs/decisions/2026-09-16_stage2_g4_identifiability_redesign.md`, which supersedes §5–§8 of
`docs/decisions/2026-09-16_stage2_g4_design_amendment.md` **without rewriting it**.

This is not a gate bundle. It has no `run.sh` and reproduces no number, because it computes
none: every value in `tables/g2_stability_decomposition.tsv` is a re-tabulation of a cell that
is already landed in `results/rt07_g2_reference_reconstruction/` or
`results/rt07_g3_prior_method_replication/`, cited by source table in its own column. The
naming follows the precedent of `results/rt07_pre_g4_seed_provenance/`.

## The finding, in one paragraph

No available population supplies independent ground-truth start/end boundaries for the
conserved RT sequence regions, so **`BOUNDARY_ACCURACY = UNESTABLISHED`** and
**`BOUNDARY_CALIBRATION = UNESTABLISHED`**, declared before any method is chosen. What *is*
identifiable is a coordinate system over the conserved-**position** set — which reproduces
across independent alignment frames (81 vs 82 positions) and collapses to zero under a
residue-shuffle null — together with localization against the one landmark whose position is
fixed by the query's own residues (the catalytic `[YF]xDD`), region-interval **stability** under
a declared perturbation ensemble, and **transferability** across sequence distance and family.
The region *count* is a free parameter (5–16 across the declared sweep, 6 vs 7 across frames,
never separable from a column-permutation null) and is therefore not a target object.

## Files

| file | what it is |
|---|---|
| `tables/estimand_matrix.tsv` | the identifiability review: 16 candidate quantities, each classified `ESTABLISHABLE` / `PARTIALLY_ESTABLISHABLE` / `UNESTABLISHED` with its truth source, evidence and allowable claim |
| `tables/g2_stability_decomposition.tsv` | what the **full** g2 sensitivity landscape supports, separated from what only its reporting point supports |
| `tables/derivation_allowlist.tsv` | clean-room allowlist / quarantine, per asset, with `circularity_risk` |
| `tables/evaluation_arms.tsv` | the four arms plus controls, each by what it *can* and *cannot* test |
| `tables/bounded_sampling_plan.tsv` | the Stage-1 sampling frame, declared before any draw |
| `tables/method_comparison_plan.tsv` | methods, budgets, splits and six binding rules — written after the estimand, not before |
| `tables/acceptance_criteria.tsv` | 10 criteria, none weakenable |
| `tables/claim_vocabulary.tsv` | permitted, restricted and prohibited terms with the evidence each requires |
| `tables/historical_to_operational_mapping_proposed.tsv` | RT0–RT7 onto operational objects, with cardinality including non-correspondence |
| `proposed/LAUNCHER_02_g4_diff.md` | **not applied** — proposed minimal launcher changes |
| `proposed/research_contract_C3_C9_amendment.md` | **not applied** — proposed `C3` narrowing and `C9` metrics-row footnote |

## Status

`g4` NOT EXECUTED; `g5` NOT STARTED. Design repair only, per the operator's instruction that
review is required between identifying the new estimand and spending another compute cycle.
