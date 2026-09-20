---
task_id: T-R2a-tierA-internal-geometry
governance_base: 9a793c9
base_commit: SET_BY_AUTONOMOUS_PREPARE_FROM_CURRENT_PROJECT_SYNTHESIS
base_branch: project-synthesis
stage_id: S08
title: Tier-A experimental RT-DNA geometry within retron ncRNA
state: APPROVED_FOR_AUTONOMOUS_PREP
autonomy_tier: A
compute_class: CPU_SMALL
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-R2a-tierA-internal-geometry
branch: task/T-R2a-tierA-internal-geometry
output_directory: analysis/t_r2a_tierA_internal_geometry/
hard_dependencies: ["T-R1b-rtdna-anchor-mapping"]
populations_touched: ["PANEL-RTDNA-81 :: already spent by T-R1b for rtdna_anchor_mapping; descriptive reuse only"]
population_state: ALREADY_SPENT_FOR_THIS_ANCHOR; no new confirmatory spend
confirmatory_spend: none
iteration_budget: 1
frozen: false
freeze_rule: WORKING_RULES §6b
operator_authorisation: scientific design approved for autonomous implementation/freeze/execution; no further implementation-level review unless a genuinely new biological decision appears
---

# T-R2a · Tier-A internal geometry

## 1 · Question

> What descriptive internal geometry do the 81 experimentally measured RT-DNA extents occupy within their own retron ncRNAs?

This task is deliberately **Tier A only**. It does not consume Buffington material and does not consume `NCRNA-16458`.

## 2 · Evidence and interpretation ceiling

Input is the accepted `T-R1b-rtdna-anchor-mapping` coordinate table: 81/81 `EXACT_UNIQUE`, all `REVCOMP`.

This task may report **descriptive experimental-anchor geometry and predicted boundary context**. It may not infer a general msr/msd, a1/a2 or template boundary; may not validate a covariance model; may not propagate to Tier D; and may not treat the absence of 3′-flush examples in these same 81 as independent validation of a biological rule.

## 3 · Coordinate convention — fixed before execution

All coordinates are reported on the **ncRNA sequence in its stored 5′→3′ orientation**, 1-based inclusive.

Because each RT-DNA is the reverse complement of the mapped ncRNA segment:

- ncRNA `start` = the 5′ boundary of the mapped ncRNA segment = base paired to the **3′ terminus of RT-DNA**;
- ncRNA `end` = the 3′ boundary of the mapped ncRNA segment = base paired to the **5′ terminus of RT-DNA**.

The output must carry explicit fields naming both mappings. It must never call ncRNA `start` the RT-DNA 5′ end.

## 4 · Blocking consistency gate

Before any measurement, independently recheck all 81 against the raw SHA-pinned panel and accepted R1b table:

1. accepted R1b table hash matches its recorded value;
2. panel hash matches `80b2f565515c96bb1b9b0082c261dd6184c67672e29bb96c813cf6abdd9d9577`;
3. 81 anchors occur in both sources;
4. `len(RT-DNA) <= len(ncRNA)` for all 81;
5. mapped span length equals RT-DNA length;
6. `1 <= start <= end <= len(ncRNA)`;
7. `revcomp(ncRNA[start:end]) == RT-DNA` for all 81;
8. mapping state is `EXACT_UNIQUE` for all 81;
9. per-element RT-DNA/ncRNA ratio <= 1.0.

Any failure = **STOP before primary output**. No anomaly exclusion rule exists.

## 5 · Measurements

For each of the 81 elements report:

- ncRNA length;
- RT-DNA length;
- exact ncRNA start/end, 1-based inclusive;
- normalised start/end using the same verified ncRNA object;
- RT-DNA/ncRNA length fraction;
- 5′ and 3′ ncRNA flanking lengths;
- explicit RT-DNA-terminus↔ncRNA-boundary mapping from §3.

### Sequence context

For each experimental boundary, emit the fixed **±10 nt** ncRNA window centred on the boundary nucleotide, inclusive, clipped to sequence ends. Maximum window length is therefore 21 nt. Report the unclipped requested interval and clipped interval so edge handling is auditable.

### Predicted secondary-structure context

Run full-ncRNA ViennaRNA `RNAfold` MFE prediction (`--noPS`) on each complete ncRNA. This is **prediction, not truth**.

At each experimental boundary report:

- full MFE structure string and MFE value in the per-element evidence table or linked structure table;
- boundary nucleotide state: `PAIRED` or `UNPAIRED`;
- if paired, the 1-based partner index in the same ncRNA orientation; otherwise partner is empty/NA.

No local folding window substitutes for the full sequence.

## 6 · Stratification — one pinned vocabulary only

If subtype summaries are emitted, the **only allowed annotation** is `support.csv` column `retron_sub`, propagated unchanged into the accepted R1b table as column `retron_sub`.

- source panel SHA-256 is the panel hash above;
- no positional-column fallback;
- no `family_label`, `rt_family`, filename-derived family, or alternate vocabulary;
- no stratum summary for n < 5;
- every stratum statistic prints n.

## 7 · Controls — blocking

In addition to the 9-check consistency gate:

- `R2a_POS_revcomp_boundary_fixture`: planted reverse-complement segment recovers the correct ncRNA start/end and explicitly maps ncRNA-start↔RT-DNA-3′ and ncRNA-end↔RT-DNA-5′;
- `R2a_POS_context_clip`: synthetic boundary at sequence end yields the declared clipped ±10 window and no coordinate under/overflow;
- `R2a_POS_dotbracket_partner`: a synthetic dot-bracket with known paired and unpaired boundary positions yields the exact partner indices;
- `R2a_GATE_no_tierD`: implementation contains no read of `NCRNA-16458` or `rt_ncrna_oriented_v1` and emits no propagated/candidate Tier-D coordinate table.

Any blocking control failure ends this task under the normal new-ID rule.

## 8 · Outputs

- `R2a_tierA_geometry.tsv` — 81 rows, one per experimental anchor;
- `R2a_tierA_boundary_context.tsv` — sequence ±10 and predicted RNAfold boundary state/partner;
- `R2a_tierA_strata.tsv` — only `retron_sub` strata with n >= 5, if any;
- `R2a_controls.tsv`;
- `logs/run_log.json`;
- `OUTPUT_MANIFEST.sha256`;
- `TASK_REPORT.md`.

There is **no** `R2_candidate_coordinates.tsv` and no Tier-D output.

## 9 · STOP conditions

Input hash/row mismatch; any consistency/control failure; any attempted Tier-D read/propagation; any fallback to an unpinned annotation vocabulary; any change to the fixed ±10 context definition after seeing results.

## 10 · Results ceiling

The observed absence of a 3′-flush RT-DNA among these 81 may be reported as an observation in this panel and nominated as a hypothesis. It is not a validation criterion and is not an independently tested rule within these same 81.
