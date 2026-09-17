# rt07_pre_g4_full_length_design

**Design and evidence inventory. No detector built; no Stage-1 catalogue access.**

Implements the operator's full-length-first direction. Binding record:
`docs/decisions/2026-09-16_stage2_full_length_first.md`.

## The finding, in one paragraph

Mapping all 1,988 myRT seed fragments back onto their full-length parents shows RVT_1 excision
discards a **median 97 aa N-terminal** (mean 112.3, max 631), and **62.0% of proteins carry >=80 aa
there** — the size of the LtrA RT0 zone (1-85). A fragment-only design makes that space
unobservable by construction. Full-length-first restores it. The usable population is **2,166
eligible** of 2,339 records, and it is **already dereplicated** (2,165 non-redundant at 4-mer
Jaccard 0.90), so family imbalance — not redundancy — is the binding constraint. The primary
anchor `[YF]xDD` occurs in **94.9%** of the broad collection against 84.8% on the historical GII
substrate, but **7 families fall below 90%** (UG13 52.0%) and **251 proteins carry more than one**,
so the design is multi-anchor with anchor-poor families predeclared.

## Files

| file | what it is |
|---|---|
| `tables/full_length_reference_inventory.tsv` | per-label audit of the 2,339 full-length proteins: uniqueness, length, fragments, fusions, seed-source status |
| `tables/myrt_fragment_vs_full_length_mapping.tsv` | what RVT_1 excision discards, per family: N/C-terminal extensions and the coverage gap |
| `tables/stage1_myrt_label_crosswalk.tsv` | 46 myRT models to Stage-1 labels: 38 one-to-one, 7 fine-to-coarse, 1 rename, 1 Stage-1-only construct |
| `tables/balanced_reference_panel_design.tsv` | hierarchical lineage-first panel, the three UG options, and the newly located resources |
| `tables/candidate_anchor_definitions.tsv` | seven anchor candidates with measured occupancy and three binding rules |
| `tables/common_frame_failure_criteria.tsv` | ten declared failure criteria and the global -> class -> family fallback ladder |
| `tables/broad_vs_family_specific_architecture_plan.tsv` | the T1-T6 architecture tiers that replace a fixed region count |
| `tables/validation_estimands.tsv` | 15 quantities classified, keeping homology support / mapping confidence / biological presence distinct |
| `alignment_strategy_comparison.md` | four strategies against the measured substrate; staged recommendation |
| `rt0_test_design.md` | how RT0 becomes testable without being assumed |
| `proposed/LAUNCHER_02_full_length_amendment.md` | **not applied** — five proposed edits |

## Status

**NO FULL-CATALOGUE APPLICATION; g5 NOT STARTED.**
