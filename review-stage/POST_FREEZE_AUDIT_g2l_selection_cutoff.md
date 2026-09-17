# AUDIT ITEM — the `≥5` cutoff is the exact value at which the selection winner becomes G2L

Authored file. No script regenerates it. Surfaced **during preparation of the independent review**,
**before** the reviewer returned, and **before** any operator decision on g4b. No scientific output
was modified, and no result was re-run.

This is recorded because the standing audit principle requires every deviation to be surfaced with
the six fields at the moment of detection, not absorbed into a favourable summary.

---

## A7 · Selection-cutoff sensitivity

| field | content |
|---|---|
| **expected** | the rule v2 cutoff *"at least 2 components, each with at least 5 sequences"* is a neutral restatement of the operator's "multiple independent clusters" requirement, and its precise value is not load-bearing for which family is selected |
| **observed** | **the value is load-bearing.** Re-applying rule v2's own tie-break at other cutoffs, over the same 38-family audit table: |

```
cutoff >=2 : winner UG25   passing UG25 UG19 G2L UG14 UG9 UG12 UG13 UG21 UG23 UG10
cutoff >=3 : winner UG25   passing UG25 G2L UG14 UG19 UG9 UG12
cutoff >=4 : winner UG25   passing UG25 G2L UG14 UG19 UG9
cutoff >=5 : winner G2L    passing G2L UG14 UG25      <- the cutoff actually used
cutoff >=6 : winner G2L    passing G2L UG14
cutoff >=7 : winner G2L    passing G2L
cutoff >=8 : winner G2L    passing G2L
```

| field | content |
|---|---|
| **mechanism** | UG25's components are **19/5/4**. At any cutoff ≤4 it has **three** qualifying components against G2L's **two** (40/9/1/1), so **tie-break criterion 1 — "the largest number of components with ≥5 sequences" — selects UG25**. At cutoff 5 UG25 drops to two qualifying components, criterion 1 ties, and criterion 2 (size of the second qualifying component: G2L 9 vs UG25 5) selects G2L. **The winner flips at exactly the chosen value.** |
| **when_detected** | during assembly of the independent-review packet, after the gate was frozen and run, before the reviewer's verdict and before any g4b decision |
| **scientific_effect** | the *mechanical application* of rule v2 is not in question — it was applied to all 38 labels, three families passed, and the declared tie-break was followed without exception. What is in question is the **provenance of the number 5**. It was first written in `control/FRESH_LINEAGE_SELECTION_STOP.md` §"Option 3", in a paragraph whose stated purpose was *"reaching the same lineage by a stated rule rather than by preference"* — i.e. the value was proposed while G2L's 40/9/1/1 component structure was already tabulated in the same document. G2L's **transfer performance** was unknown and is not implicated. But **a free parameter whose value determines the selected family was chosen with the candidate structure visible**, and that is the definition of a fitted selection parameter, however transparently it was arrived at |
| **repair** | **none applied. Not this session's call.** Changing the cutoff now, after the G2L result is visible, would be strictly worse — it would be tuning a selection rule against an observed outcome, which the operator has forbidden. The honest options are to (1) accept the G2L result with this limitation stated on its face, or (2) run the identical frozen mapper on **UG25** as a pre-registered second holdout and report both. Option 2 costs one run and is the only one that resolves the concern rather than disclosing it |
| **results_before_repair_invalidated** | **NO.** No measurement changes. The 94% / 84% figures, the decoy results, the genealogy audit and the seven-criterion verdict all stand exactly as landed. What narrows is the **strength of the selection claim**: "selected by a prospectively declared rule" remains true, "selected by a rule whose free parameter was fixed independently of the candidate structure" is **not** supportable |

## Bearing on the claim

The supportable selection statement becomes:

> G2L was selected by mechanically applying a rule declared before any transfer result was observed.
> The rule's size cutoff (5) was fixed while the candidate component structures were already known,
> and is the exact value at which the declared tie-break selects G2L rather than UG25. Selection was
> therefore blind to **performance** but **not** blind to **structure**.

## Note on a false statement in the v1 STOP record

`control/FRESH_LINEAGE_SELECTION_STOP.md` §"Option 3" states: *"Under that rule only **G2L**
qualifies."* That is **FALSE** — `UG14` and `UG25` also qualify, as the mechanical audit
subsequently showed. The error is recorded here and the STOP record is **not** rewritten. It does
not change any measurement; it weakens the original argument for Option 3, since the rule is less
discriminating than claimed. It also, incidentally, cuts *against* the fitting concern: had the
author been fitting deliberately, the expectation "only G2L qualifies" would not have been wrong.

---

## A8 · Unit test T1 is a recorded FAIL and is absent from the transfer summary

| field | content |
|---|---|
| **expected** | on the `hmmemit -c` consensus, every one of the 471 HMM states maps `MATCH` with `residue_index == state` |
| **observed** | **state 471 only** returns `alignment_state=DELETE, residue_index=None`; the consensus's final residue is placed in an **insert** column after state 471 (`total inserted residues = 1`, run `(471, 1)`). States 1–470 map exactly 1:1. Verified by re-running the mapper on the landed consensus |
| **when_detected** | recorded as `FAIL` in `tables/state_to_residue_unit_tests.tsv` at the time the tests were run; **not carried into `fresh_lineage_transfer_summary.md`** |
| **scientific_effect** | **none on this gate.** It is a C-terminal tie in `hmmalign`'s placement of the last residue, not an interpolation or indexing defect: the residue is fully accounted for as an insertion, and `T5_coordinate_reversibility` passes with 0 mismatches. Critically, **state 471 lies far outside the anchor span 107–317**, so **no anchor state is affected** and no reported number changes. The mapper's failure mode here is to under-call (DELETE), which is conservative |
| **repair** | none to the mapper — the behaviour is correct-by-design fail-closed conduct at a terminal state. The **reporting** gap is repaired by this entry |
| **results_before_repair_invalidated** | **NO** |

A `FAIL` row that appears in a landed table but not in the human-readable summary is a reporting
defect regardless of its size, and is recorded as one.
