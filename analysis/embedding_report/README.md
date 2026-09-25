# embedding_report — reporting and synthesis workbench

A **reporting and synthesis** workspace for the RT–ncRNA representation and conditional-modelling
thesis chapter. It audits, indexes and writes up work that is already frozen elsewhere.

> **It is not an experiment.** No model is trained here, no frozen bundle is modified or
> reinterpreted, and no result is recomputed to obtain nicer numbers. Every number is read from a
> frozen bundle, or re-derived from frozen tables by a script that fails if the two disagree.

Source of truth (read-only from here):
`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings` — bundles `embed_g0` … `embed_g2c`,
`embed_x1_conditional_pilot`, **`embed_x2_rt_specificity_confirmation`** (@ `4f8550b`, closed at
`fdf0872`), the landed track report, the OpenCRISPR comparison and the historical asset audit.
Where this workbench and a frozen bundle disagree, **the bundle wins** and the disagreement is a
finding to record, not to smooth over.

**State: X2 has landed and closed; nothing in the track is pending computation.** The frozen gate
returned `X2-A`, and the conclusion of record is the qualified interpretation, not the label:
specific RT information reproducibly improves prediction of the cognate ncRNA beyond broad retron
type and, directionally, beyond a coarse 50 %-identity homolog group — but **most of the gain is
lineage-level**, the residue is small and seed-unstable in magnitude, and pair-level discrimination
under the strictest controls is near chance.

## The chapter question

> Do naturally associated retron RTs and ncRNAs contain partner-specific sequence information
> beyond broad retron lineage/type, and can that information eventually be used to prioritize
> candidate low-cross-reactivity RT–ncRNA pairs for experimental testing?

Three levels, never collapsed: **(1) broad association** — established; **(2) RT-specific
statistical association** — confirmed by X2 but **lineage-dominated**, small, and weak at pair
level; **(3) functional compatibility / orthogonality** — not addressable without experiment, and
never inferred from (1) or (2).

## Contents

| file | what it is |
|---|---|
| `RESULT_INVENTORY.tsv` | every frozen bundle, prior synthesis and derived artifact: path, commit, key quantities, inferential unit, status |
| `CLAIM_EVIDENCE_MATRIX.tsv` | 29 candidate thesis claims: analysis, population, unit, estimate, limitations, SUPPORTED (some qualified) / PENDING / NOT_SUPPORTED, source + commit |
| `THESIS_RESULT_STATUS.md` | **living status board** — frozen and writable now · supported only with their qualifier attached · exploratory only · rejected/negative · future experimental validation |
| `METHODS_PROVENANCE.md` | thesis-ready METHODS draft, each subsection carrying its `provenance` line |
| `RESULTS_DRAFT.md` | thesis-ready RESULTS draft; every section is frozen, including §7 on the X2 confirmation and its three qualifications |
| `THESIS_OUTLINE.md` | chapter structure, section by section, with what is writable now and what is blocked |
| `OPENCRISPR_COMPARISON.md` | what methodological idea was borrowed, which components were and were not reused, how the datasets/splits/evaluations differ, what could later be adapted, and what cannot be reproduced without experimental exchangeability labels |
| `FIGURE_PLAN.md` | specifications for F1–F10 (all generated) and F11–F12 (specified, blocked), with the reason each blocked figure is blocked |
| `CANDIDATE_SELECTION_DESIGN.md` | the prospective laboratory-prioritisation framework — **design only, nothing executed** |
| `figures/` | F1–F10 as PNG (300 dpi) + PDF |
| `derived/` | `x1_component_level.tsv` (+ meta and check log): per-component re-aggregation of frozen X1 outputs · `multiplicity_rederived.tsv`: partner-multiplicity percentages re-derived from two independent frozen tables |
| `scripts/` | `r01_x1_component_table.py` and `r02_multiplicity.py` (derivations, each self-verifying), `f_figures.py` (all figures) |

## Reproducing

```bash
P=/home/borg/miniconda3/envs/retron_tradicional
cd analysis/embedding_report
LD_LIBRARY_PATH=$P/lib $P/bin/python scripts/r01_x1_component_table.py   # must print 46/46
LD_LIBRARY_PATH=$P/lib $P/bin/python scripts/r02_multiplicity.py         # two frozen sources must agree
LD_LIBRARY_PATH=$P/lib $P/bin/python scripts/f_figures.py                # F1-F10
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
7. **Quote X2's qualified interpretation, not its gate label.** `X2-A` on its own overstates what
   was found. Every level-2 sentence carries its qualifier: lineage dominance (G − T is ~78 % of
   R − T), the ~10-fold counterfactual decay, 52.5 % of pairs at C3, R − G's seed instability, and
   the relatedness gradient whose least-similar quartile spans zero.
8. **Downstream work uses the X2 exports**: `X2_COMPONENT_LEVEL_EXPORT.tsv` for inference,
   `X2_PAIR_LEVEL_EFFECTS.tsv.gz` for joins only, under the binding requirements R1–R6 in
   `X2_HANDOFF.md`.

## Update protocol

When a bundle lands or a run finishes: add its row to `RESULT_INVENTORY.tsv`, move the affected
claims in `CLAIM_EVIDENCE_MATRIX.tsv`, and update `THESIS_RESULT_STATUS.md` **in the same commit**.
Read a landed run against its own frozen outcome gate *before* writing any prose, and release only
the sentences that outcome licenses — for X2 that meant recording `X2-A` and simultaneously
narrowing the interpretation the label alone would have implied.
