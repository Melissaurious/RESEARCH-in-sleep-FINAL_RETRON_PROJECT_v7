# Independent adversarial review — full-length-first design, request record

A fresh review of a new object, written to an explicit operator direction. Not a re-review of the
scope-separation formulation, which returned `FAIL/BLOCK`.

    backend:            codex (mcp__codex__codex, new thread)
    reviewer_model:     gpt-5.6-sol, model_reasoning_effort xhigh
    executor_model:     claude-opus-5[1m]
    sandbox:            read-only, cwd = the project root
    date:               2026-09-16
    verdict vocabulary: PASS | PASS_WITH_REQUIRED_REPAIRS | FAIL/BLOCK
    prior rounds:       3/10, 4/10, 4/10 — all on earlier formulations

## Reviewed object

    docs/decisions/2026-09-16_stage2_full_length_first.md              a09dc921d8f8c828
    results/rt07_pre_g4_full_length_design/
      README.md                                                        2c72194c7b263665
      alignment_strategy_comparison.md                                 967f37cc34732fc7
      rt0_test_design.md                                               e3f27502bf5ebb24
      tables/balanced_reference_panel_design.tsv                       f50e780aab4dc90f
      tables/broad_vs_family_specific_architecture_plan.tsv            05464e619b743f7d
      tables/candidate_anchor_definitions.tsv                          7805809a92f17e80
      tables/common_frame_failure_criteria.tsv                         9d854dcf6a4a8111
      tables/full_length_reference_inventory.tsv                       03be92a55e46aa4e
      tables/measured_values.tsv                                       4407845fd3f42e35
      tables/myrt_fragment_vs_full_length_mapping.tsv                  eda1983c0ddc2b1f
      tables/stage1_myrt_label_crosswalk.tsv                           b1f04f5787446722
      tables/validation_estimands.tsv                                  477144c5eddbc616
      proposed/LAUNCHER_02_full_length_amendment.md                    412adcd4083b363a   NOT APPLIED
      scripts/measure.py                                               53583aa205ae9c7b
      run.sh, INPUTS.tsv (53 rows, including all 47 seed FASTAs)

## Repairs this round claims to have made

Against the round-2 and scope-separation findings, and stated so the reviewer can check rather
than take on trust:

- **reproducibility** — the bundle now ships `scripts/measure.py` and `run.sh`, and every quoted
  number is regenerated into `tables/measured_values.tsv`. The previous bundle had no scripts, and
  that is what let six factual errors through;
- **`INPUTS.tsv`** now hashes all 47 seed FASTAs and the collection, which the previous one omitted;
- **the per-label cap is withdrawn** and replaced by hierarchical lineage-first balancing, with the
  73–77% UG / 3–4% retron failure measured and recorded in the design itself;
- **`C9` is assigned to no g4 gate**;
- **the seed fragments are comparator-only**; only the untrimmed collection may seed;
- **`NOT_DETECTED_INSPECTABLE` → `NOT_CALLED_ON_COMPLETE_SEQUENCE`**;
- **`g5`/`g6`/§7a/§7c are amended too**, not `g4` alone.

## What the reviewer was asked to falsify

The operator's twelve questions, plus, added by the executing session because they are the
load-bearing risks:

- whether the launcher amendment is **still self-serving** despite the three changes it claims;
- whether the **250 aa floor, 0.90 clustering threshold, 90% anchor bar and per-lineage target of
  90** are justified or arbitrary — and specifically whether **the 90% anchor bar, chosen after
  seeing the occupancy distribution, repeats the post-hoc-threshold violation** the round-2
  reviewer found in `AC3`;
- whether predeclaring 7 families `ANCHOR_POOR` is honest predeclaration or **pre-excusing expected
  failure**;
- whether `F01`–`F10` are real kill conditions or unfalsifiable;
- whether **Strategy A proposing Pfam `RVT_1` as the primary scaffold contradicts the operator's own
  direction** to stop treating `RVT_1` as the sequence universe;
- whether Stage 2 is worth doing at all versus the previous reviewer's recommendation to stop at 2A.

The reviewer was told not to inflate, that correctly declaring a quantity unestablishable is not a
defect, and explicitly: *"three prior rounds failed; do not fail this one out of momentum if it has
genuinely fixed the defects, and do not pass it out of fatigue if it has not."*

## Outcome

Recorded in `review-stage/AUTO_REVIEW.md` after the round completes.
