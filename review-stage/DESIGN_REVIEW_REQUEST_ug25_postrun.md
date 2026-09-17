# POST-UG25 REVIEW — interpretation and integrity

**This is not another method-development cycle.** The confirmatory run has executed once and is
frozen. Please assess only whether it was executed and interpreted honestly.

```
CONFIRMATORY BUNDLE : results/rt07_ug25_confirmatory/        root 6bf14eb47022f062f6d7a10d8ae86cb1d7d7c4d412625f0b229b9dd129a8095e  (15 files)
PRE-UG25 BUNDLE     : results/FINAL_PRE_UG25_VALIDATION_BUNDLE/  root fc9cde03a13282b2aaa176a10b5da7c5798a4f2cce763dffad076575a8d2d889  (44 files, UNCHANGED)
manifests + roots   : review-stage/manifests/ , review-stage/roots/   (all 444, outside their bundles)
```

Verify either with `code/integrity.py verify <bundle> <manifest> <root>`.

## What was run

Once, at **2026-09-17T14:05:41Z**, via `run_ug25_once.sh`, which first verified the pre-UG25
bundle against its external pinned root and then executed the gate from a **temp copy** of the
frozen code. Authorisation was supplied at run time as
`RT07_AUTHORISED_FAMILIES=Retrons,GII,DGRs,CRISPR,UG3,AbiA,UG25` — not from any source constant.
Execution record in `control/EXECUTION_RECORD.txt`.

## Result

**7 of 7 predeclared criteria PASS, 0 FAIL, 0 NOT TESTABLE**, on a holdout the genealogy audit
classified **`FRESH_LINEAGE`**.

| # | observed | result |
|---|---|---|
| C1 callability ≥ T1 0.32 | comp0 0.5133, comp1 0.5933 | PASS |
| C2 frozen posterior rule | PP_HI 0.75 / PP_LO 0.50 read at run time | PASS |
| C3 catalytic ≥ 0.80 | 26/27 = 0.9630 | PASS |
| C4 no collapse ≤ D_MAX 0.48 | 0.0800 | PASS (declared weak) |
| C5 reason vocabulary / call classes | {OK: 28}; MAPPED 2400, AMBIGUOUS 375, UNSUPPORTED 297, DELETED 1128 | PASS |
| C6 per-class controls + identity accounting | PASS, no violations | PASS |
| C7 no post-authorisation change | parameters read from frozen tables | PASS |

Components 19/5/4; qualifying 19 and 5. Controls (max mapped): MONO 10, DI 13, REV 17; weakest
real sequence maps 54. Zero di-shuffle failures.

## Three things the executor flagged against its own result — please check each

1. **The genealogy identity figure is misreadable.** Median best identity to construction is
   **0.588** (max 0.818), *higher* than G2L's 0.326 — yet UG25 is classified more independent.
   The reason: those hits cover a **median 2.1%** of the sequence (max 6.7%), so **0 of 28** meet
   the full link rule (identity ≥0.30 **and** min-coverage ≥0.50), against G2L's 28 of 51.
   Landed in `tables/ug25_identity_coverage_diagnostic.tsv` as a **post-run diagnostic** that
   changes no criterion and no verdict. Is `FRESH_LINEAGE` the right call, and is the diagnostic
   an honest clarification rather than a post-hoc rescue?
2. **The reverse control is deterministic.** `s[::-1]` is identical every replicate, so REV's 84
   replicates are **28 distinct sequences counted three times** (MONO and DI give 84 distinct
   each). `n_distinct_sequences` is landed in the control table. Does this materially weaken C6?
3. **C4 = 0.0800 sits above the same-population null `D_RANDOM` = 0.067**, while passing
   `D_MAX` = 0.48 by a wide margin. It was declared non-evidential before the run and is
   reported as such.

## Please verify

1. no mapper or threshold changed after authorization;
2. UG25 was executed only after authorization;
3. execution matched the frozen predeclaration;
4. criteria were evaluated exactly as written;
5. controls were interpreted per class (no pooled summary hiding a class);
6. `MAPPED` / `AMBIGUOUS` / `UNSUPPORTED` / `DELETED_STATE` separated correctly, with only
   `MAPPED` counted as positive evidence;
7. catalytic evidence handled separately from anchor callability and not pooled;
8. no post-hoc tuning occurred;
9. the final scientific claim matches the observed outcome and is not inflated.

Specifically: the executor claims the mapper hash `69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef` is unchanged across all bundles, that
the gate restates no threshold of its own (reading them from the frozen control tables instead),
and that a single mapping pass was made. Please check the gate source for any restated constant
or second pass.

## Proposed claim — please accept, narrow, or reject

> Under the tested `hhmake -M 50` / `-M 60` match-state conventions, the frozen GII-derived
> alignment-path mapper transfers to **UG25, a held-out RT family with no sequence-level link to
> any construction family** under the registered 0.30/0.50 rule. All seven predeclared criteria
> pass: conserved states are callable at median **51%** (n=19) and **59%** (n=5) of the 150
> frozen anchors against a threshold of 32%; the catalytic coordinate at HMM state 262 is
> confirmed in **26 of 27** sequences whose state-262 call is `MAPPED`; and real sequences
> separate completely from three classes of order-disruption control (weakest real 54 anchors vs
> strongest control 17).
>
> This does **not** establish robustness under `-M a2m`, independent residue-level accuracy,
> general biological specificity against unrelated natural proteins, or transfer beyond this one
> family of 28 sequences.

## Required verdict

`PASS` / `PASS_WITH_REQUIRED_REPAIRS` / `FAIL/BLOCK`, numeric score, and whether the
confirmatory transfer is **SUPPORTED** or **NOT SUPPORTED**. Please do not open a new
method-development cycle; if you find an interpretation defect, state the corrected claim.
Write only into your own temporary directory and do not modify any bundle.
