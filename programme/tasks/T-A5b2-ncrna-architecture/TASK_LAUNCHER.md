---
task_id: T-A5b2-ncrna-architecture
governance_base: 9a793c9
base_commit: 94a1a78
stage_id: S08
title: Infer ncRNA coordinate architecture from the experimental anchors
state: HELD
autonomy_tier: A
compute_class: CPU_MEDIUM
worktree: TBC
branch: TBC
output_directory: analysis/t_a5b2_ncrna_architecture/
hard_dependencies: ["T-A5b1-rtdna-anchors"]
populations_touched: ["exact ncRNA catalogue: inspected"]
iteration_budget: 2
claim_ids_touched: []
---

# T-A5b2 · Infer ncRNA coordinate architecture from the experimental anchors

**HELD.** Opens only if `T-A5b1` returns `TASK_STATE=PASS` with unambiguous anchors above its declared
floor. Its scope is then set by what A5b1 actually anchored, not by what was hoped for.

## Question
Given the experimental anchor set, can ncRNA coordinate architecture be inferred for molecules that
have no experimental RT-DNA, and with what confidence?

## Why this is a separate task
A5b1 is direct measurement: a sequence maps somewhere, or it does not. This is inference from a small
anchor set to a large population. Different logic, different controls, different failure modes.
Merging them would let a caller's performance borrow credibility from the mapping's directness.

## Population and inferential unit
- fitting and evaluation population: the anchors produced by A5b1
- application population: whatever subset A5b1's result licenses, which may be far short of 16,458
- inferential unit: ncRNA instance for calls; retron type for any rate
- dependence structure: anchors are not independent across types; evaluation is lineage-blocked

## Reusable assets, not to be recomputed
Existing folds cover 99.35% of the catalogue and existing a1/a2 calls cover 95.83%, both with their
failure modes already measured. Reuse them, join on the current sequence hash, and fold only what is
genuinely missing. Their prior **conclusions** remain unverified and are not cited.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| held-out anchors | **positive** | anchors withheld from fitting are recovered at a declared tolerance | the caller does not generalise even inside the anchor set; VOID |
| lineage-blocked splitting | **positive** | held-out sets are blocked by RT lineage, never drawn at random | near-duplicates inflate the result |
| dinucleotide-shuffled ncRNAs | **negative** | recovery collapses to chance | the signal is composition |
| group II intron and DGR upstream windows | **negative** | no architecture is recovered | the caller fires on anything |
| fixed positional split at the median | **baseline** | the caller must beat it | there is no method, only a prior. This is the exact bar the previous ncRNA arm died to, 343 against 901 |

## Reachability
Attainable in both directions once A5b1 has reported.

## Endpoint and criterion
- primary endpoint: boundary agreement on lineage-blocked held-out anchors, at a declared tolerance
- **falsification criterion:** failing to beat the fixed positional baseline on lineage-blocked
  held-out anchors closes coordinate-level ncRNA inference for this project
- **death condition:** the above, permanently

## Expected result patterns
| pattern | TASK_STATE | SCIENTIFIC_OUTCOME |
|---|---|---|
| beats the positional baseline on blocked held-out anchors | PASS | SUPPORTS_H1; S08b pair expansion may be proposed |
| beats it only within model-recoverable types | PASS | BOUND; report the limit, do not claim corpus scale |
| does not beat it | PASS | FALSIFIED; a clean, cheap, permanent closure |

## What this task may NOT conclude
That a coordinate set across 16,458 is validated. Only the anchored and held-out subsets are.
Nothing about the branching guanosine, whose sequence-only route is already refuted and whose stated
precondition is exactly the boundary this task would produce.
