---
task_id: T-A5b-msrmsd-coordinates
governance_base: b5443e1
stage_id: S08
title: msr/msd coordinates and RT-DNA extent, anchored on experimental RT-DNA
state: AUTHORIZED
autonomy_tier: A
compute_class: CPU_MEDIUM
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A5b-msrmsd-coordinates
branch: task/T-A5b-msrmsd-coordinates
output_directory: analysis/t_a5b_msrmsd_coordinates/
hard_dependencies: []
soft_dependencies: ["T-REG-asset-registration"]
populations_touched: ["exact ncRNA catalogue 16,458: inspected", "published panel 175: used as ANCHOR, not as a model test set"]
iteration_budget: 2
claim_ids_touched: ["C-34", "C-09"]
thesis_artifacts: ["S08 figures, tables, methods, limitations"]
---

# T-A5b · msr/msd coordinates and RT-DNA extent, anchored on experimental RT-DNA

## Question
Can the msr/msd boundary and the RT-DNA extent be located as **coordinates** on retron ncRNAs, using
the experimentally determined RT-DNA sequences as an anchor that is independent of the covariance
models?

## Hypothesis
Yes for the anchored subset, because msd is the template for the RT-DNA, so an experimentally
determined RT-DNA sequence maps onto ncRNA coordinates and fixes one boundary directly. Alternative:
the mapping is ambiguous or the anchor set is too small, in which case the task returns a bounded
negative and the ncRNA boundary question closes.

## Why existing evidence does not answer it — registry lookup result
**This is a revision of an earlier, wider proposal that the registry lookup partly closed.**

| component | prior state | consequence for this task |
|---|---|---|
| folding | **DONE**: 16,351 of 16,458 (99.35%) already folded with RNAfold + bpRNA, dot-bracket stored | **reuse, do not recompute**; build the join on the current sequence hash and fold only the ~107 missing |
| a1/a2 inverted repeat | **DONE**: 15,772 of 16,458 (95.83%) already called, with a per-span shuffle null and a 210,862-sequence negative | **reuse**; gold 0.8129 against group II background 0.0959 |
| msr/msd as features | **DONE but demoted**: presence flags from `cmalign` against the same 21 covariance models; the rule classified 47% of confirmed ssDNA producers as incomplete | **inherit as a warning, not as input.** Coordinates were never landed and must not be built this way |
| branching guanosine | **REFUTED from sequence alone**: every set passes its bar and so does its own shuffle; the gold panel does not beat its shuffle | **out of scope.** The prior work states its precondition is the msr/msd boundary, which is what this task produces |
| RT-DNA extent | **NEVER COMPUTED**; the 81 RT-DNA sequences were never used for it | **this is the gap** |

## Population and inferential unit
- **anchor population:** the 81 elements with an empirically determined RT-DNA sequence
- **application population:** 16,458 exact ncRNAs, output as a confidence-graded coordinate set
- inferential unit: ncRNA instance for calls; **retron type for any rate**
- dependence structure: anchor molecules are not independent of each other by type; report per-type
- **effective n for any claim: 81, and the honest evaluation split is 56 CM-recoverable against 64 CM-gap**

## Inputs
| input | path | role |
|---|---|---|
| oriented ncRNAs, 16,458 | `data/derived/rt_ncrna_oriented_v1.fna` | application population |
| prior folds, 16,359 | prior project `stage4_ncRNA_assessment/cache/p2_structures.parquet` | **ASSET** — reuse |
| prior a1/a2 per span | prior project `ncrna_extractor_detector/tables/c1_a1a2_per_span.tsv.gz` | **ASSET** — reuse |
| experimental panel, 81 RT-DNA sequences | `support.csv` in the prior project's supporting material | **the anchor. Not in v7; register it first** |
| deposited complexes, 8 | registered structure cache | independent geometric check |

Hash every input. Prior tables enter as **assets**; none of their conclusions may be cited.

## Forbidden inputs
`cmalign` msr/msd consensus coordinates against the 21 production covariance models, as a source of
truth. They define the population and cannot adjudicate a boundary within it. They may be reported as
a **comparator**, declared in advance.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| RNAfold base-pair recovery on known msr-msd | **positive** | reproduces the prior 0.9137–0.9508 range on the same molecules | the folding instrument is not behaving as it did; stop before any boundary work |
| deposited complexes | **positive** | called coordinates agree with the RNA chain geometry in the 8 structures | the coordinate frame is wrong |
| group II intron and DGR upstream windows | **negative** | no msr/msd architecture recovered | the caller fires on anything |
| dinucleotide-shuffled real ncRNAs | **negative** | recovery collapses to chance | the signal is composition |
| fixed positional split at the median msr/msd ratio | **baseline** | the method must beat it | there is no method, only a prior |

## Reachability
Both outcomes attainable. The anchor is 81 real molecules with real RT-DNA sequences; a mapping
either exists or does not, and both are measurable. **The PASS branch requires the positive control
to reproduce first**, which is exactly the check the prior branching-G work shows to be decisive.

## Method
Map each experimental RT-DNA sequence onto its cognate ncRNA to fix the msd extent. Derive msr as the
complement region bounded by the a1/a2 arms already called. Fold only what is not already folded.
Report coordinates with a confidence grade and with the distance from every call to the sequence
edge, because the extent is a covariance-model cut and a boundary near an edge may be its artefact.

## Endpoint and criterion
- primary endpoint: agreement between the RT-DNA-anchored msd boundary and the called boundary, on
  the anchor population, at a declared tolerance
- **falsification criterion:** if the method does not beat the fixed positional split on the anchored
  molecules and the deposited complexes at the declared tolerance, the decomposition is not
  established and is not used downstream
- **death condition:** failing the above closes coordinate-level ncRNA decomposition for this project
  and the boundary chapter becomes a bounded negative

## Expected result patterns
| pattern | reading |
|---|---|
| anchored boundaries recovered, generalise to the 16,458 with grades | the project gains its first biological object on the RNA side; S08b pair expansion opens |
| recovered only on the 56 CM-recoverable, chance on the 64 CM-gap | matches the prior work's own limit; report as a bound, do not claim corpus scale |
| not recovered above the positional split | a clean, cheap, permanent closure; the chapter is a negative |

## Outputs
`tables/A5b_anchor_mapping.tsv`, `tables/A5b_coordinates_graded.tsv`, `tables/A5b_controls.tsv`,
`tables/A5b_comparator_cmalign.tsv`, `figures/`, `ARTIFACT_MANIFEST.tsv`

## What this task may NOT conclude
That an ncRNA lacking a call lacks the architecture. That a coordinate set at 16,458 is validated;
only the anchored subset is. Anything about the branching guanosine. Anything about RT–ncRNA pairing.
