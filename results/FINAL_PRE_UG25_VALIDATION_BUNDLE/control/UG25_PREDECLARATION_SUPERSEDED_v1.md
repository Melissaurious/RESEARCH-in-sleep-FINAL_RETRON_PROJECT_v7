> **SUPERSEDED 2026-09-17 — DO NOT USE TO GOVERN THE CONFIRMATORY RUN.**
> Replaced by `control/UG25_PREDECLARATION_v2.md`. This document describes implementation that
> no longer exists: `scripts/scoped_loader.py`, a public-constant `AUTHORISATION_TOKEN`,
> `loader_equivalence.py` and `scripts/mapper_v2.py`. It is retained unchanged below as
> historical evidence. Nothing in it has been rewritten.

# UG25 confirmatory holdout — PREDECLARATION (PREPARED, NOT EXECUTED)

Date: 2026-09-17. Track `rt07`. Status: **awaiting operator authorisation. Not run.**

## 0 · UG25 access — corrected statement (REPAIR 5)

**WITHDRAWN**, as literally false in the v1 bundle:

> ~~"No UG25 sequence has been aligned, scored or read by any script in this bundle."~~

The shared `eligible_by_family()` loader parsed the whole mixed collection and materialised all
38 families — UG25 (n=28) included — on every call. This was **the same defect as errata A5**
("UG5 was never opened"), in the same loader, repeated after it had already been corrected once.

**Accurate statement, which is what the evidence supports:**

> **UG25 was not used for alignment, scoring, calibration, thresholding, output generation or
> mapper development.**

> **`UNEVALUATED` is not the same as `UNREAD`.**

**Made true going forward:** `scripts/scoped_loader.py` takes an explicit family allow-list and
discards every other record at parse time, so no object exists to read. UG25 is additionally
`SEALED`: loading it raises unless the caller passes the explicit operator authorisation token.
Proven mechanically by `loader_equivalence.py` — L1 (construction families byte-identical to the
old loader), L2 (UG25 absent from scoped output), L3 (unauthorised request fails closed), L4 (the
token works, so the confirmatory run remains possible), L5 (the old loader demonstrably leaked).

The only UG25 facts used here are its eligible count and component sizes, from the pre-existing
`fresh_lineage_candidate_audit.tsv`, which contains **no mapping performance** — **sampling
feasibility only**.

## 1 · Why UG25 and not another family

The reviewer's classification was **C**: the mapper was inadequately validated, so a farther
holdout alone would not have cured it. The repairs address the mapper. UG25 is then the right
confirmatory family because:

- it passed the same prospective independence rule as G2L (`≥2 components each ≥5`);
- it is **not** group-II-like, so it is not adjacent to GII the way G2L is;
- it was never used in construction, development, threshold selection or anchor selection;
- **nothing about it has been inspected** — unlike G2L, whose component structure was visible
  when the selection cutoff was chosen.

UG25 is therefore the only remaining candidate that can support a claim stronger than
`FRESH_FAMILY_WITHIN_RELATED_LINEAGE` — **if** its genealogy audit clears.

## 2 · Feasibility (the only UG25 numbers used)

`eligible_N = 28`, components **19 / 5 / 4**. Qualifying components (≥5): **19** and **5**.
The component of 4 is `descriptive_only`.

**Stated limitation, before the fact:** the second qualifying component has **5** sequences. That
is a thin challenge set — thinner than G2L's 9. A per-component median over 5 sequences carries
wide uncertainty, and the gate must report it as such rather than treating 5 sequences as a
lineage replicate.

## 3 · Mandatory precondition — genealogy audit FIRST

Before any mapping, run the same audit applied to G2L, against **all six** construction
families: exact sequence overlap, identifier overlap, content scan of construction objects, and
best-identity distribution under **both** the identity leg and the **full** link rule
(identity ≥0.30 **and** min-coverage ≥0.50 — the G2L report quoted 48/51 on identity alone, where
the full rule gave 28/51; both must be reported this time).

Classify as exactly one of `FRESH_LINEAGE`, `FRESH_FAMILY_WITHIN_RELATED_LINEAGE`,
`NOT_INDEPENDENT`.

**`NOT_INDEPENDENT` stops the gate.** The classification is recorded **before** the mapping runs
and is not revised afterwards.

## 4 · Frozen inputs — nothing here may be re-derived

| item | value | source |
|---|---|---|
| mapper | `scripts/mapper_v2.py` | frozen, manifest-hashed |
| `PP_LO` / `PP_HI` | 0.50 / **0.75** | `SUPPORT_RULE_FROZEN.tsv` |
| `S_MIN` / `K_MIN` | **10** / **30** | `SUPPORT_RULE_FROZEN.tsv` |
| `T1` / `D_MAX` | **0.32** / **0.48** | `SUPPORT_RULE_FROZEN.tsv` |
| `D_RANDOM` (diagnostic) | **0.067** | addendum 1 |
| `CAT_STATE` | **262** | `CATALYTIC_STATE_FROZEN.tsv` |
| anchors | the same 150 `ALL_PARTNERS` states | unchanged since g4a |

All derived from construction families only. **None may be re-tuned against UG25.**

## 5 · Success criteria — numeric and falsifiable

| # | criterion | passes when | **fails when** |
|---|---|---|---|
| C1 | callability | every qualifying component median `MAPPED` fraction **≥ T1 = 0.32** | any qualifying component median < 0.32 |
| C2 | support | calls use the frozen posterior rule; `MAPPED` requires PP ≥ 0.75 | any call made outside the frozen rule |
| C3 | catalytic | among sequences whose `CAT_STATE` call is exactly `MAPPED`, the fraction beginning a `[YF].DD` is **≥ 0.80** | < 0.80, **or zero sequences have `CAT_STATE` = `MAPPED`** (undefined → FAIL CLOSED, never "not testable") |
| C4 | no collapse | \|median(comp0) − median(comp1)\| **≤ D_MAX = 0.48** | > 0.48 |
| C5 | abstention | every abstention carries a reason code; all four call classes representable | an unexplained abstention, or an unreachable class |
| C6 | decoy separation | **SUPERSEDED by `control/C6_CONTROL_POLICY.md` (repair 6).** Evaluated **per control class**: every class must satisfy `max(class) < min(real, non-abstaining)` | any **single** class violating separation — **even when the pooled statistic passes** — or an empty class, or a class below 76 valid replicates, or no non-abstaining real sequence. **p95 is reported, never a pass condition** |
| C7 | no tuning | no threshold changed after UG25 was opened | any post-hoc change |

**C4 is weak and is declared weak.** `D_MAX = 0.48` is a between-*family* bound applied to two
components within one family; `D_RANDOM = 0.067` is the same-population null. The gate reports
the observed difference against **both**. A C4 pass alone is close to uninformative and must not
be presented as evidence.

## 6 · Decoys — all three classes, as calibrated

Mono-shuffle, **di-shuffle** and **reverse**, 3 replicates each per UG25 sequence, all retained
and all reported. Mono-shuffle alone is insufficient: on construction data it reached 17 anchors
where di-shuffle reached 24 and reverse 25.

## 7 · Reporting rules

- Report `MAPPED`, `AMBIGUOUS`, `UNSUPPORTED` and `DELETED_STATE` counts separately. **Only
  `MAPPED` is transfer evidence.** `AMBIGUOUS` is never folded into a success count.
- The component of 4 is descriptive only and takes no part in pass/fail.
- Catalytic correspondence is evaluated over **all 471 states**, never restricted to the 150
  anchors, and reported separately from anchor callability. The two are never pooled — pooling
  them is what produced the false `NOT TESTABLE` on G2L.
- Monotone state order is an `IMPLEMENTATION_INVARIANT` and is not evidence.
- Uncertainty for the 5-sequence component is reported as a range, not a bare median.

## 8 · Execution discipline

**One run.** No iteration, no threshold adjustment, no re-selection after results are visible.
A failed criterion **fails closed** and is recorded as a failure — as UG5 v2 was — not repaired
into a pass.

Before the run: build the bundle manifest and lock the bundle. After the run: verify the
manifest. Both hashes go in the report. **A freeze violation is itself a gate failure.**

## 9 · What a PASS would support, and what it would not

A pass would support:

> The frozen, construction-calibrated state→residue mapper transfers to a held-out RT family
> outside the GII-like lineage, with posterior-supported calls, explicit ambiguity and
> reason-coded abstention, and complete separation from three classes of negative control.

It would **not** support universality across RT families, calibrated residue-level *accuracy*
against an independent truth set, or any claim about the `-M a2m` frame, under which DGRs and
AbiA retain zero `ALL_PARTNERS` positions.

## 10 · Not authorised

This gate is **prepared only**. It is not executed by this task, and g4b/g5/g6 remain closed.
