# Independent adversarial design review — rt07_g4, request record

Routed through ARIS's governed reviewer mechanism (`/auto-review-loop` conventions;
transition decided by `/home/borg/ARIS_CODE/tools/review_gate.py`).

    backend:          codex  (mcp__codex__codex)
    reviewer_model:   gpt-5.6-sol
    executor_model:   claude-opus-5[1m]
    sandbox:          read-only, cwd = the project root (the reviewer reads the repo itself;
                      the executor cannot filter what it sees)
    round:            1
    date:             2026-09-16
    positive_threshold: score >= 6 AND verdict in {ready, almost}   (both must hold)

## What the reviewer was asked to falsify

The amended g4 design in `docs/decisions/2026-09-16_stage2_g4_design_amendment.md`, against
the 17 operator-specified checks: implicit seven-region forcing; g2 as unexamined ground
truth; all167/anchors72 boundary leakage; whether the 26 PDB structures are genuinely held
out; GOLD171/127 selection bias; CAND95 provenance completeness; identity leakage beyond
exact duplicates; family-held-out claims exceeding boundary truth; RT0 treated as ordinary
occupancy; RT1 tuned after the fact; structural contamination of a sequence instrument;
population-specific calibration; whether the portable detector can annotate an unseen
sequence; core extraction sufficiency without claiming a tree; method-comparison fairness;
premature full-catalogue scanning; and whether every claim carries frame, stratum, unit and
denominator.

The reviewer was instructed not to inflate the score, and told that a design which would
produce an overclaimed result must not score >= 6.

## Outcome

Recorded in `review-stage/AUTO_REVIEW.md` after the round completes.
