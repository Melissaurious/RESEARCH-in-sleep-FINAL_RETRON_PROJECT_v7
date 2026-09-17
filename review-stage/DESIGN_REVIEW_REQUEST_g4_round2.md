# Independent adversarial design review — rt07_g4 redesign, request record

Round 2 of at most 4, continuing the round-1 thread so the reviewer can check its own required
repairs against the new artifact. Routed through ARIS's governed reviewer mechanism
(`/auto-review-loop` conventions; transition decided by `/home/borg/ARIS_CODE/tools/review_gate.py`).

    backend:            codex  (mcp__codex__codex-reply)
    thread:             01a0a71c-7bc0-77a3-938d-29b38e90bda4
    reviewer_model:     gpt-5.6-sol
    executor_model:     claude-opus-5[1m]
    sandbox:            read-only, cwd = the project root (the reviewer reads the repo itself)
    round:              2
    date:               2026-09-16
    positive_threshold: score >= 6 AND verdict in {ready, almost}   (both must hold)

## Reviewed object

    docs/decisions/2026-09-16_stage2_g4_identifiability_redesign.md
      sha256 70c5be73ba1707feb5665cfc7464e5259e07a76a73f45d6569df3df2288ff157

    results/rt07_pre_g4_identifiability_redesign/
      tables/estimand_matrix.tsv                          a112f035c8dae0bd91...
      tables/g2_stability_decomposition.tsv               779fe66c0fa72720f3...
      tables/derivation_allowlist.tsv                     5e706b905a16822950...
      tables/evaluation_arms.tsv                          875e8cab0ce1e6a8ba...
      tables/bounded_sampling_plan.tsv                    caf9cdeecaeeb6f440...
      tables/method_comparison_plan.tsv                   51fed8c67c4b2ed8e5...
      tables/acceptance_criteria.tsv                      cd73dff446f22a2661...
      tables/claim_vocabulary.tsv                         95c29f9cde177d6c1d...
      tables/historical_to_operational_mapping_proposed.tsv  bd4c77c8c6985de5ce...
      proposed/LAUNCHER_02_g4_diff.md                     not applied
      proposed/research_contract_C3_C9_amendment.md       not applied

The round-1 record `docs/decisions/2026-09-16_stage2_g4_design_amendment.md` is not the reviewed
object. Its §1–§4 are retained as measurements; its §5–§8 are superseded.

⚠️ **Amended 2026-09-16 for precision.** This line first read that the round-1 record is
"unchanged". Accurate statement: it is unchanged **by this session** — last modified
2026-09-16 01:20:06, before this session acquired `.agent-lock` at 11:23:12. Its current hash is
`cf2f4ee10d8e020d54364c3a4564ac32f2a74556a1af59c9cbd5345b6d7f3fea`, which differs from the
`006b5160…` that `review-stage/AUTO_REVIEW.md` records for round 1 — that divergence is the
already-documented prior-session breach (the record was edited while its review was in flight,
and §9a was appended afterwards), not a change made here. Superseded text left visible.

## What the reviewer was asked to falsify

Identifiability (is the proposed quantity observable and testable; is boundary truth being
invented; is g2 still treated as ground truth); circularity (all167 / anchors72 / CAND95 /
prior HMM labels re-entering derivation; structure used for both definition and validation);
independence ("held out" sequences that are near-identical relatives; unacknowledged lineage
and selection conditioning); methodology (estimands before methods; untouched test populations;
thresholds chosen without test leakage; comparisons measuring the same quantity); generalization
(whether family-held-out evaluation means what the report claims; identity distance separated
from family novelty); claims (every intended use of accuracy, validated, calibration,
independent, held-out, boundary, domain, absence, RT0, RT1, RT0–RT7, general RT detector); and
downstream usefulness for later phylogeny, motif localization, structural comparison,
insertion/expansion, domain fusion and RT–ncRNA co-evolution.

The reviewer was told not to inflate the score, that a narrower claim is acceptable if the
coordinate system remains reproducible and useful, and that a design which would produce an
overclaimed result must not score >= 6.

## Outcome

Recorded in `review-stage/AUTO_REVIEW.md` after the round completes.
