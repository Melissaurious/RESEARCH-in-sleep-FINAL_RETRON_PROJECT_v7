# Independent adversarial review — Stage-2 scope separation, request record

A **fresh review of a new object**, not round 3 against the previous formulation. The operator's
task instruction is explicit: *"Do NOT write 'review round 3' against the previous formulation."*
A new thread was opened rather than continuing `01a0a71c-…` so the reviewer is not anchored on the
superseded g4 design; it was pointed at `review-stage/AUTO_REVIEW.md` so the failure history is
available to it as evidence.

    backend:            codex  (mcp__codex__codex, new thread)
    reviewer_model:     gpt-5.6-sol, model_reasoning_effort xhigh
    executor_model:     claude-opus-5[1m]
    sandbox:            read-only, cwd = the project root
    date:               2026-09-16
    verdict vocabulary: PASS | PASS_WITH_REQUIRED_REPAIRS | FAIL/BLOCK
    gate threshold:     score >= 6 AND verdict in {ready, almost} per review_gate.py

## Reviewed object

    docs/decisions/2026-09-16_stage2_scope_separation.md              e8d4672d3e53a7a3
    results/rt07_pre_g4_scope_separation/
      historical_vs_operational_scope.md                              b6ac18deba705e53
      proposed_stage2_gate_restructure.md                             8275b93301b3e005
      tables/candidate_reference_design.tsv                           ab50fc8c51790d2c
      tables/estimand_matrix.tsv                                      e119782594276b07
      tables/general_vs_retron_analysis_plan.tsv                      0b0207f97c25869e
      tables/myrt_reference_inventory.tsv                             8f423f5766c3fa58
      tables/reference_overlap_genealogy.tsv                          0aed073d5891d18c
      tables/reference_source_inventory.tsv                           f82870afb0468532
      tables/structure_reference_inventory.tsv                        f2ecd967670effd4
      proposed/LAUNCHER_02_diff.md                                    e458b13bfc2291f6   NOT APPLIED

The three prior decision records are unchanged and are background, not the reviewed object.

## What the reviewer was asked to falsify

The operator's twelve questions: historical/operational separation; myRT used appropriately rather
than as truth; breadth of the reference design; over-domination by any one class; whether
class-level occupancy comparison is supportable; presence/non-detection versus mapping failure;
RT0 handling; structural orthogonality; retrons focal without being exclusive; downstream
phylogeny/motif/structural support without overclaiming; whether exact boundary claims are
sneaking back in; and whether a major RT reference source was missed.

Plus, added by the executing session because they are the load-bearing risks:

- **verification of every new factual claim** made this session — the composition of the 66, the
  `O.s.petDI1` = `S.o.petDI1` duplicate, the 45-model / 1,988-`NSEQ` reconciliation, the
  `RVT-CRISPR-like` discrepancy, the `RVT-ref` subset relation, and the Pfam `RVT_1` LtrA 90–360
  window against Blocker's RT0 zone;
- **whether the proposed §5d amendment is a legitimate narrowing or a self-serving loosening of
  the one rule that was blocking the work.** This was flagged to the reviewer as the single most
  important question, because the executing session has an obvious incentive to amend it;
- whether *"the positions are a measurement, the count is a free parameter"* is sound or a rescue
  of `g2`;
- whether splitting `g4` into `g4a` + `g4b` fixes anything or defers the identifiability problem;
- whether Stage 2 is worth doing at all versus stopping at 2A with a documented impossibility
  result — the design's own option 2.

The reviewer was told not to inflate the score, that a design correctly declaring its central
quantity unestablishable is not thereby defective, and to name explicitly any fundamental fork the
executing session should not settle alone.

## Outcome

Recorded in `review-stage/AUTO_REVIEW.md` after the round completes.
