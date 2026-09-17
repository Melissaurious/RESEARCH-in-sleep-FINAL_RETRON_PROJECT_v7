# INDEPENDENT REVIEW REQUEST — G2L fresh-family residue-level transfer gate

Track `rt07`, Stage 2. Bundle: `results/rt07_residue_mapper_gate/` (frozen; do not modify).
Reviewer must be independent of the executor (WA-A.5). This is a **design and integrity review of a
completed, frozen gate**, not a request to re-run it.

---

## 0 · What you are reviewing

A frozen HMM-state → sequence-residue mapper, and one single-shot evaluation of it on a held-out RT
family (`G2L`) that was mechanically selected under a prospectively declared rule.

The two previous gates on this line **failed**, and the failures are preserved:

- **UG5 v2** — `FAILED on predeclared criterion 2`. Preserved, not repaired in place.
- **UG5 v3** — scored 5/10 at review. Its placement rule used **linear interpolation between domain
  endpoints** to infer internal residue coordinates. That is the defect the present mapper exists to
  remove.

The operator has forbidden returning to UG5 as the confirmatory lineage.

---

## 1 · Selection rule (declared before any holdout performance was seen)

`control/FRESH_LINEAGE_SELECTION_STOP.md` records that the **v1** rule — "rank eligible unused
families by N descending, take the first with ≥2 separation components" — selected **UG7**
(components 76/1), whose second component is a **singleton**. Work **stopped** there and the
decision was returned to the operator rather than silently overridden.

The operator then authorised a **prospective supersession**, recorded in
`control/FRESH_LINEAGE_RULE_V2.md`:

> A lineage is eligible as a fresh holdout when it has **at least 2 sequence components, each
> containing at least 5 eligible sequences**, under the already-registered component definition
> (connected components of the link graph at `identity ≥ 0.30` **and** `min(qcov, tcov) ≥ 0.50`).

The component definition and its thresholds were **not** changed. The tie-break was declared in the
same record, **before** the audit ran:

1. most components with ≥5 sequences;
2. then largest N in the **second**-largest qualifying component;
3. then largest eligible N;
4. then lexicographically smallest label.

The record states explicitly: *"Mapping outcome may not enter the tie-break, and no candidate is
privileged in advance — including G2L."*

## 2 · Mechanical application

`tables/fresh_lineage_candidate_audit.tsv` — all **38** family labels, no pre-filtering by N.
Ineligible because used: `Retrons`, `GII`, `DGRs`, `CRISPR`, `UG3`, `AbiA` (construction); `UG5`
(development/tuning).

**Three** families passed:

| family | eligible N | components | ≥5 |
|---|---|---|---|
| G2L | 51 | 40/9/1/1 | 2 |
| UG14 | 16 | 10/6 | 2 |
| UG25 | 28 | 19/5/4 | 2 |

Tie-break criterion 1 ties at 2. Criterion 2 — second qualifying component — selects **G2L (9)** over
UG14 (6) and UG25 (5).

Note for your assessment: the v1 STOP record (written earlier) already observed G2L's 40/9/1/1
structure while explaining why UG7 was unusable. So G2L's *component structure* was known before
rule v2 was written, and rule v2 was written knowing it. Its *transfer performance* was not known.
Judge whether this constitutes rule-fitting.

## 3 · Genealogy / provenance audit — `tables/g2l_gii_genealogy_audit.tsv`

Contamination, all zero:

- 0 exact sequence overlap with any of the 6 construction derivation sets;
- 0 exact overlap with the 50 GII construction sequences specifically;
- 0 G2L identifiers in any construction object;
- 0 hits from a content scan of construction sequence and alignment files;
- no G2L object in anchor selection, threshold setting, placement-rule development, mapper
  development or the `-M` sensitivity analysis.

Relatedness, non-zero:

- median best identity G2L → GII construction = **0.326**;
- **48 of 51** at or above 0.30 (the identity leg of the link rule);
- **2 of 51** at ≥0.50; max **0.636**; min **0.296**;
- G2L has its own myRT model (`RVT-G2L`, distinct from `RVT-GII-I` / `RVT-GII-II`);
- the label denotes *group-II-like*.

Classification claimed: **`FRESH_FAMILY_WITHIN_RELATED_LINEAGE`** — not `FRESH_LINEAGE`, not
`NOT_INDEPENDENT`.

## 4 · The mapper — `scripts/residue_mapper.py`

`hmmalign` produces a Stockholm alignment; match columns are read from the `#=GC RF` line; the
mapper fails closed if `len(match_cols) != LENG`. For each sequence a residue index is accumulated
over non-gap alignment positions, and each HMM state is emitted as `MATCH` (with a real residue
index) or `DELETE`. Insertions are recorded as runs between match states.

**No interpolation of any kind appears in the file.** The word does not occur except in the
docstring forbidding it.

HMM: `GII.deriv.hmm` from the g4a repaired bundle, `LENG` = 471.
Anchors: the 150 frozen `ALL_PARTNERS` states from
`results/rt07_ug5_holdout_gate/tables/ug5_frozen_anchor_coordinates.tsv`, span 107–317.

### Unit tests — `tables/state_to_residue_unit_tests.tsv`

| test | result | detail |
|---|---|---|
| T1_consensus_identity | **FAIL** | L=471; states not mapping 1:1 = **1** |
| T2_internal_deletion | PASS | states 50–59 deleted 10/10; state 100 → residue 90 |
| T3_insertion | PASS | 25 residues between states 80 and 81; insert run [25] |
| T4_terminal_clipping | PASS | N-term 40/40 deleted, C-term 40/40, middle 40/40 matched |
| T5_coordinate_reversibility | PASS | residue_index → amino-acid mismatches = 0 |
| T6_shuffled_behaviour | PASS | only 1 state mapped |

**T1 is a recorded FAIL and is put to you deliberately.** On the `hmmemit -c` consensus, 1 of 471
states does not map to residue index == state index. It is not mentioned in
`fresh_lineage_transfer_summary.md`. Assess whether this is a benign consensus/emission artefact or
a mapper defect, and whether its omission from the summary is a reporting defect.

### Construction validation — `tables/construction_mapper_validation.tsv`

| family | n | median anchor callability | median deletion | reversibility | monotone (invariant) | dyad ≤3aa of mapped anchor |
|---|---|---|---|---|---|---|
| Retrons | 40 | 0.713 | 0.287 | 40/40 | 40/40 | 1/40 |
| GII | 40 | 0.953 | 0.047 | 40/40 | 40/40 | 3/40 |
| DGRs | 40 | 0.927 | 0.073 | 40/40 | 40/40 | 4/40 |
| CRISPR | 40 | 0.947 | 0.053 | 40/40 | 40/40 | 6/40 |
| UG3 | 40 | 0.733 | 0.267 | 40/40 | 40/40 | 0/40 |
| AbiA | 19 | 0.733 | 0.267 | 19/19 | 19/19 | 4/19 |

Monotone order is labelled `IMPLEMENTATION_INVARIANT` — `hmmalign` is globally colinear by
construction — and is **not** used as transfer evidence.

## 5 · Frozen success criterion — `control/G2L_SUCCESS_PREDECLARATION.md`

Frozen before any G2L sequence was mapped. Test population: components 0 (n=40) and 1 (n=9); the two
singletons are descriptive only. Success requires **all** of:

1. multiple frozen states callable in **both** non-trivial components;
2. mappings supported under the frozen score rule;
3. catalytic landmark maps via the actual alignment path where a dyad is present;
4. no collapse to one component, judged against the construction spread 0.713–0.953;
5. abstention and ambiguity explicitly represented;
6. real sequences separate from decoys under the identical mapper;
7. no G2L-specific tuning.

Explicitly **not** evidence: monotone state order. Explicitly **not** required: universal or
complete mapping. Stop rule: **one run, no iteration after results are visible.**

## 6 · Result — one run, `scripts/g2l_gate.py`

```
REAL  n=51  median_mapped=141/150  abstain=1
DECOY n=153 median_mapped=0  max=33  with_any=37
  comp0 n=40  QUALIFYING        median 141/150 = 94.0%  abstain=0  catalytic_at_anchor=0
  comp1 n=9   QUALIFYING        median 126/150 = 84.0%  abstain=0  catalytic_at_anchor=0
  comp2 n=1   descriptive_only  median 123/150 = 82.0%  abstain=0  catalytic_at_anchor=0
  comp3 n=1   descriptive_only  median   0/150 =  0.0%  abstain=1  catalytic_at_anchor=0
```

Verdict recorded: **5 MET, 1 NOT TESTABLE, 0 FAILED.**

**Criterion 3 — why NOT TESTABLE.** The catalytic dyad occupies **HMM state 262** in 27 of 30 GII
construction sequences. 262 lies inside the anchor span (107–317) but is **not one of the 150
`ALL_PARTNERS` anchors** (nearest 267). Anchors are states aligned across all six construction
families; 262 is not one. So `catalytic_at_anchor = 0` everywhere is a property of the **anchor
set**, not of the mapper or of G2L. The mapper does map state 262 — it maps every state — but there
is no catalytic anchor to recover. Reported as not testable rather than as pass or fail.

**Decoys.** 3 replicates × 51 within-sequence shuffles = 153, all retained. Median 0, but **37 of
153 (24%) map ≥1 state**, max **33/150 (22%)**. Reported explicitly as "MET, not absolute". Note the
decoy design is composition-preserving shuffle only; no reversed or unrelated-protein decoys were
used in this gate.

## 7 · Claim as currently written

> The frozen state→residue mapping transfers to a **held-out RT family within a related GII-like
> lineage**, mapping a median **94%** (component 0) and **84%** (component 1) of 150 frozen
> conserved states to actual residues via the alignment path, with no family-specific tuning,
> against a decoy median of 0.

Not an unseen-lineage claim, not universal, order not claimed as evidence.

## 8 · Surviving context you should hold against this

- The architectural frame is already narrowed to **GII-centred and implementation-dependent**: under
  HHmake's documented default `-M a2m`, DGRs and AbiA retain **zero** `ALL_PARTNERS` positions while
  GII retains 115. The 150-anchor frame comes from `-M 50`.
- For **5 of 7** g4a families no independent within-family holdout exists at the declared 0.30/0.50
  rule.
- `BOUNDARY_ACCURACY` and `BOUNDARY_CALIBRATION` remain **UNESTABLISHED**; there is no RT0
  occupancy; the seven-way partition is unsupported.
- myRT is valid as derivation material but **invalid as family-label validation** — and the G2L
  family label itself comes from myRT.

---

## 9 · Questions (answer each explicitly)

1. Was the revised lineage-selection rule declared before holdout **performance** was examined?
2. Was the rule applied mechanically across the candidate families?
3. Was G2L selected by the frozen rule/tie-break rather than because it produced favourable transfer
   results?
4. Is `FRESH_FAMILY_WITHIN_RELATED_LINEAGE` scientifically appropriate given the measured G2L↔GII
   relatedness?
5. Is the genealogy/provenance audit sufficient to rule out direct leakage from G2L into
   construction or mapper development?
6. Is the mapper truly alignment-state→residue and free of the endpoint-interpolation problem that
   invalidated the previous gate?
7. Are insertions, deletions, clipping, ambiguity and abstention handled correctly?
8. Are any primary transfer metrics still **mathematically guaranteed** by the alignment procedure —
   i.e. tautological rather than empirical?
9. Is state callability across the two non-trivial G2L components a valid empirical transfer test?
10. Is the catalytic criterion correctly classified `NOT TESTABLE` rather than PASS/FAIL?
11. Does the decoy evidence support discrimination, given 37/153 replicates map ≥1 state while the
    median is 0?
12. Does ≈94% / ≈84% support a related-family transfer claim?
13. Does G2L's proximity to GII make this too weak to support even cross-family transfer, or is the
    narrowed claim defensible?
14. Is a more distant holdout such as **UG25** scientifically **REQUIRED** before g4b, or optional
    strengthening? Classify explicitly as **A** (G2L sufficient, g4b may proceed), **B** (development
    result only, more distant holdout required first), or **C** (mapper itself inadequately validated
    for transfer).
15. Does the evidence justify freezing a mapper whose scope is explicitly limited to *GII-centred /
    related-family RT conserved-state mapping* rather than general unseen-lineage mapping?
16. May g4b begin under that narrowed scope?
17. Does g5 remain blocked until the g4b mapper is frozen?

Additionally, state whether the **T1 unit-test FAIL** is load-bearing.

## 10 · Required verdict

Return exactly one of `PASS`, `PASS_WITH_REQUIRED_REPAIRS`, `FAIL/BLOCK`, with a **numeric score out
of 10**, plus: load-bearing findings; required repairs; optional improvements; the explicit A/B/C
answer; the exact supportable scientific claim in your own words; whether g4b may begin; whether a
farther holdout is required first.

Be adversarial. Prefer finding a real defect over endorsing. Do not modify any file.
