# embedding_report — reporting and synthesis workbench

A **reporting and synthesis** workspace for the RT–ncRNA representation and conditional-modelling
thesis chapter. It audits, indexes and writes up work that is already frozen elsewhere.

> **It is not an experiment.** No model is trained here, no frozen bundle is modified or
> reinterpreted, no result is recomputed to obtain nicer numbers, and X2 is never run or
> anticipated from this worktree.

Source of truth (read-only from here):
`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings` — bundles `embed_g0` … `embed_g2c`,
`embed_x1_conditional_pilot`, the landed track report, the OpenCRISPR comparison and the historical
asset audit. Where this workbench and a frozen bundle disagree, **the bundle wins** and the
disagreement is a finding to record, not to smooth over.

## The chapter question

> Do naturally associated retron RTs and ncRNAs contain partner-specific sequence information
> beyond broad retron lineage/type, and can that information eventually be used to prioritize
> candidate low-cross-reactivity RT–ncRNA pairs for experimental testing?

Three levels, never collapsed: **(1) broad association** — established; **(2) RT-specific
statistical association** — preliminary, stricter test pending; **(3) functional compatibility /
orthogonality** — not addressable without experiment, and never inferred from (1) or (2).

## Contents

| file | what it is |
|---|---|
| `RESULT_INVENTORY.tsv` | every frozen bundle, prior synthesis and derived artifact: path, commit, key quantities, inferential unit, status |
| `CLAIM_EVIDENCE_MATRIX.tsv` | 24 candidate thesis claims: analysis, population, unit, estimate, limitations, SUPPORTED / PRELIMINARY / PENDING / NOT_SUPPORTED, source + commit |
| `THESIS_RESULT_STATUS.md` | **living status board** — frozen and writable now · awaiting confirmation · exploratory only · rejected/negative · future experimental validation |
| `METHODS_PROVENANCE.md` | thesis-ready METHODS draft, each subsection carrying its `provenance` line |
| `RESULTS_DRAFT.md` | thesis-ready RESULTS draft for frozen analyses only; X2 sections are explicit `[PENDING]` placeholders |
| `THESIS_OUTLINE.md` | chapter structure, section by section, with what is writable now and what is blocked |
| `OPENCRISPR_COMPARISON.md` | what methodological idea was borrowed, which components were and were not reused, how the datasets/splits/evaluations differ, what could later be adapted, and what cannot be reproduced without experimental exchangeability labels |
| `FIGURE_PLAN.md` | specifications for F1–F7 (generated) and F8–F10 (specified, blocked), with the reason each blocked figure is blocked |
| `CANDIDATE_SELECTION_DESIGN.md` | the prospective laboratory-prioritisation framework — **design only, nothing executed** |
| `figures/` | F1–F7 as PNG (300 dpi) + PDF |
| `derived/` | `x1_component_level.tsv` (+ meta and check log): per-component re-aggregation of frozen X1 outputs |
| `scripts/` | `r01_x1_component_table.py` (derivation + verification), `f_figures.py` (all figures) |

## Reproducing

```bash
P=/home/borg/miniconda3/envs/retron_tradicional
cd analysis/embedding_report
LD_LIBRARY_PATH=$P/lib $P/bin/python scripts/r01_x1_component_table.py   # must print 46/46
LD_LIBRARY_PATH=$P/lib $P/bin/python scripts/f_figures.py                # F1-F7
```

`r01` re-aggregates the frozen per-sequence held-out NLL arrays from the X1 run to the component
level and **asserts that all 46 checks reproduce the frozen summary tables**; it fails rather than
writes if any disagrees. It recomputes no model output. `f_figures.py` renders only from frozen
tables and from that verified derived table.

## House rules for anything written here

1. **Terminology**: *observed pair*, *candidate*, *mismatched candidate*, *retrieval decoy*,
   *non-observed pairing*, *counterfactual conditioning control*. Never *negative pair*, never
   *incompatible pair*.
2. **Every number names its population, its inferential unit and its denominator.** The unit is the
   relatedness component; pairs are never the sample size.
3. **Under-supported quantities are `UNDETERMINED`**, never nulls.
4. **Absence of significance is never written as equivalence or absence of effect.**
5. **Negative and null results stay visible** (`THESIS_RESULT_STATUS.md` §4) and are not deleted to
   tidy the narrative.
6. **No claim of co-evolution, binding, biochemical compatibility or orthogonality** — and no
   prospective score is described as anything but a *predicted pairing / cross-reactivity score*
   until experimentally validated.
7. **X2 is pending.** Its design is written up; its outcome is not guessed, hinted at, or implied.

## Update protocol

When a bundle lands or a run finishes: add its row to `RESULT_INVENTORY.tsv`, move the affected
claims in `CLAIM_EVIDENCE_MATRIX.tsv`, and update `THESIS_RESULT_STATUS.md` **in the same commit**.
When X2 lands, read it against the frozen outcome gate in its `DESIGN.md` §8 *before* writing any
prose, then release only the sentences that outcome licenses.
