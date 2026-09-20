---
task_id: T-A5b1-rtdna-anchors
governance_base: 7e7ccd8
base_commit: 94a1a78
stage_id: S08
title: Experimental RT-DNA coordinate anchors on cognate ncRNAs
state: AWAITING_SPECIFICATION
autonomy_tier: A
compute_class: CPU_SMALL
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A5b1-rtdna-anchors
branch: task/T-A5b1-rtdna-anchors
output_directory: analysis/t_a5b1_rtdna_anchors/
hard_dependencies: []
soft_dependencies: ["T-REG-asset-registration"]
populations_touched: ["experimental panel: RT-DNA sequences used as a coordinate anchor, not as a model test set"]
iteration_budget: 1
claim_ids_touched: []
---

# T-A5b1 · Experimental RT-DNA coordinate anchors on cognate ncRNAs

**Supersedes the withdrawn `T-A5b`, which conflated two questions and contained an arithmetic error.**

> ⚠️ **AWAITING_SPECIFICATION: the minimum unambiguous-anchor floor is referenced but not stated. Declare it before execution**

## Question
Where does each experimentally determined RT-DNA sequence map onto its cognate ncRNA?

## Hypothesis
A substantial fraction map unambiguously, because the RT-DNA is reverse-transcribed from a defined
template region of the ncRNA. Alternative: mappings are ambiguous or absent at a rate that makes the
anchor set unusable, which is itself a reportable bound.

## Scope, stated negatively and bindingly
This task establishes **where the reverse-transcribed extent sits**. It does **not** establish:

- the full biological **msd** segment beyond the reverse-transcribed extent;
- the **msr/msd boundary**;
- **msr coordinates** by any route, including "the complement region bounded by the a1/a2 arms",
  which an earlier draft wrongly proposed and which is hereby withdrawn;
- transcript boundaries, branching-guanosine placement, pairing, or orthogonality.

Those are inference steps and belong to `T-A5b2`.

## Population and inferential unit — read the arithmetic carefully
- **anchor population:** the **81** panel elements carrying an empirically determined RT-DNA
  sequence. Of these, **62** come from elements with measured RT-DNA production above zero.
- **a different population, do not conflate:** prior work reports **120** published molecules that
  locate in the ncRNA pool, splitting **56** covariance-model-recoverable against **64** model-gap.
  That is a property of the 120, **not of the 81**.
  ⚠️ An earlier draft wrote "effective n 81, split 56/64". 56 + 64 = 120. That was wrong.
- **first computational step, before anything else:** compute and report the **actual overlap**
  between the 81 anchors and the 120 located molecules, and the recoverable/gap split *within the
  81*. Do not assume it.
- inferential unit: assayed retron element.

## Inputs
| input | role |
|---|---|
| `support.csv`, 175 rows, 81 with `RTDNA_sequence` | **the anchor. Not in the v7 tree; register it via T-REG first** |
| oriented exact ncRNAs, 16,458 | the coordinate frame |
| deposited RT-RNA-DNA complexes, 8 | independent geometric cross-check, diagnostic only |

Hash every input before reading.

## Forbidden inputs
`cmalign` consensus coordinates against the 21 production covariance models, as truth. They may be
reported as a **comparator**, declared in advance, and never as an adjudicator.

## Controls — run FIRST and BLOCK
These validate **sequence mapping, orientation and coordinate handling**. They do not validate a
folding tool, which is irrelevant to this task. Per WORKING_RULES section 6a, no biological contrast
is a blocking control here.

| control | type | must show | if it fails |
|---|---|---|---|
| synthetic exact-substring fixture | **positive** | a known substring planted at a known offset, in both orientations, is recovered at exactly that offset with the correct orientation flag | coordinate or strand handling is wrong; VOID |
| synthetic mutated fixture | **positive** | a substring carrying a declared number of mismatches is recovered with the expected identity and coverage | the tolerance model is wrong; VOID |
| scrambled-pairing fixture | **negative** | RT-DNA sequences deliberately paired with non-cognate ncRNAs yield `NO_MAP` or `AMBIGUOUS` at a high rate | the mapper matches anything; VOID |
| off-by-one round trip | **positive** | converting a called coordinate back to sequence returns the original substring | classic frame error; VOID |

## Reachability
Both outcomes are attainable. A high `NO_MAP` rate is a valid, reportable result, not a failure.

## Method
Map each RT-DNA sequence to its cognate ncRNA in both orientations. Record identity, coverage,
uniqueness and every equivalent best hit. Classify. No folding, no inference, no extrapolation.

## Output schema, one row per anchor element
```
element_id · rtdna_sequence · mapping_orientation · start · end · identity · coverage
n_equivalent_best_mappings · mapping_class · distance_to_5prime_edge · distance_to_3prime_edge
cm_recoverable_flag · source · evidence_provenance
```
`mapping_class` is one of `EXACT_UNIQUE`, `HIGH_CONFIDENCE_UNIQUE`, `AMBIGUOUS`, `NO_MAP`.

**Report the distance to each sequence edge for every call.** The ncRNA extent is a covariance-model
cut, so a mapping that abuts an edge may be truncated by the cut rather than by biology.

## Endpoint and criterion
- primary endpoint: the count of `EXACT_UNIQUE` plus `HIGH_CONFIDENCE_UNIQUE` anchors
- **falsification criterion:** if unambiguous anchors fall below a floor declared before running,
  the anchor set is insufficient and `T-A5b2` does not open
- **death condition:** none. Either outcome is informative and publishable as a bound

## Expected result patterns
| pattern | TASK_STATE | SCIENTIFIC_OUTCOME |
|---|---|---|
| most anchors map unambiguously | PASS | SUPPORTS_H1; A5b2 opens |
| anchors map only for model-recoverable elements | PASS | BOUND; A5b2 opens on the anchored subset only |
| widespread ambiguity or no-map | PASS | FALSIFIED; the coordinate route closes, and that is the result |

## What this task may NOT conclude
Anything about msr, about the full msd, about ncRNAs outside the anchor set, or about pairing.
