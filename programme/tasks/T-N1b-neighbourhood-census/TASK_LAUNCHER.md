---
task_id: T-N1b-neighbourhood-census
supersedes: T-N1-neighbourhood-extraction-qa (REVIEW_FAILED, preserved as executed)
governance_base: 7e7ccd8
base_commit: 94a1a78
stage_id: S06
title: CDS-neighbourhood census over all RT-family records, with edge status
state: AUTHORIZED
autonomy_tier: A
compute_class: CPU_MEDIUM
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-N1b-neighbourhood-census
branch: task/T-N1b-neighbourhood-census
output_directory: analysis/t_n1b_neighbourhood_census/
hard_dependencies: []
populations_touched: ["RT-RECORDS-ALL-FAMILIES :: analysis_family=neighbourhood_geometry :: INSPECTED_FOR_THIS_ENDPOINT"]
population_state: INSPECTED_FOR_ENDPOINT (operator ruling 2026-09-20 §1)
confirmatory_spend: none — exploratory / QC / asset construction
iteration_budget: 1
frozen: true
freeze_rule: WORKING_RULES §6b — launcher and implementation committed BEFORE execution
---

# T-N1b · CDS-neighbourhood census, with edge status

**A new task, not a patch.** `T-N1-neighbourhood-extraction-qa` is `REVIEW_FAILED` and is preserved
exactly as executed.

## What the review rejected, and what changes

| rejected | corrected here |
|---|---|
| the blocking negative was **structurally forced to zero** — it shifted each already-selected RT CDS against its own coordinates, which cannot overlap for ordinary gene lengths | the negative **permutes anchors across records** and runs **the same locator**. A record's CDS set is scored against a *different* record's anchor. It can return any value, and it can fail |
| the positive anchor test was near-definitional | retained as a **structural check**, explicitly labelled definitional, and no longer the only positive |
| **224,483 zero-neighbour records reported without their cause**, inviting a reading of genomic isolation | zero-neighbour is **split** into `TRUE_ZERO_NEIGHBOUR` and `EDGE_CLIPPED_ZERO`, and the **edge-clipping denominator is reported** |
| clipping, window and contig-edge fields **not landed** | `clipped_end_flag`, `true_start_clipped`, `rt_at_window_edge`, `window_inverted`, `win_start/win_end`, `dist_rt_to_contig_start/end` all landed per record |
| declared `RETRON-LOCI` (~630k physical loci) while producing 3,028,196 raw records across **all** RT families | population declared **`RT-RECORDS-ALL-FAMILIES`**. `RETRON-LOCI` is reserved for an actually retron-restricted population, and rows are **records, not independent loci** |

## Question

For each RT-anchored record, what is the CDS neighbourhood geometry, and what is the technical
state of the window it was computed in?

## Hypothesis

Not applicable — a census with QA. No falsification criterion, because no claim.

## Population and exposure

- population: **`RT-RECORDS-ALL-FAMILIES`** — records in `rt_window_cds_v1` carrying a called RT CDS
- ⚠️ **the row unit is a raw source record, not a physical locus.** Records are **not** independent:
  `locus_key` and `physical_locus_key` are landed so a consumer can collapse them, and any analysis
  treating rows as independent loci is misusing this table
- **analysis family:** `neighbourhood_geometry`
- **exposure:** `INSPECTED_FOR_THIS_ENDPOINT` per operator ruling §1

## Inputs

| input | path | role |
|---|---|---|
| window CDS | `…_v7/data/derived/rt_window_cds_v1.parquet` | 44,310,231 CDS rows |
| master records | `…_v7/data/derived/rt_records_v1.parquet` | 3,059,700 records: family, window, clipping, contig distances, locus keys |
| RT-CDS exceptions | `…_v7/data/derived/rt_cds_recovery_v1.parquet` | 31,504 records where the RT CDS was **not** called — **disjoint** from the anchored set, used as annotation only |

## Declared parameters, fixed in this commit

anchor-permutation negative ceiling **0.05** · anchor-uniqueness floor **0.99** ·
reproduction floor **0.999** · seed **20260920**.

## Controls — run FIRST and BLOCK; fixtures never alter the primary input

| control | type | must show | fails if |
|---|---|---|---|
| `N1b_NEG_permuted_anchor` | **negative** | scoring each record's CDS set against a **different** record's anchor recovers an RT CDS at ≤ 0.05 | the locator finds an anchor anywhere — **this one can genuinely fail** |
| `N1b_POS_anchor_unique` | positive (structural) | each anchored record carries exactly one `is_rt_gene` CDS, ≥ 0.99 | the anchor is ambiguous. **Declared definitional**, since anchors are defined by that flag |
| `N1b_POS_reproduce_n_cds` | positive | recomputed CDS-per-record reproduces the landed `rt_cds_recovery_v1.n_cds` on its 31,504 records, ≥ 0.999 | the CDS join is wrong |

## Outputs

`tables/N1b_neighbourhood_per_record.tsv`, `tables/N1b_zero_neighbour_causes.tsv`,
`tables/N1b_edge_state.tsv`, `tables/N1b_by_family.tsv`, `tables/N1b_summary.tsv`,
`tables/N1b_controls.tsv`, `TASK_REPORT.md`, `logs/run_log.json`

## What this task may NOT conclude

That a zero-neighbour record is genomically isolated — the census exists to separate that from
contig-edge truncation. Anything comparative between retrons and other RT families: that is `T-N2`,
it needs a lineage design, and neighbourhood is already a **settled non-detector** (retrons 27th of
41 families, inside a predeclared dead band).
