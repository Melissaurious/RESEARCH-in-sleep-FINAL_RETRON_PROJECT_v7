# UG25 confirmatory holdout — PREDECLARATION v2 (SUPERSEDING). PREPARED, NOT EXECUTED.

Date: 2026-09-17 · Track `rt07` · Status: **frozen; awaiting operator authorisation; NOT run**

**Supersedes** `control/UG25_PREDECLARATION_SUPERSEDED_v1.md`, which is preserved unchanged
and must not be used to govern the confirmatory run. v1 described implementation that no
longer exists: `scripts/scoped_loader.py`, a public-constant `AUTHORISATION_TOKEN`,
`loader_equivalence.py`, and `scripts/mapper_v2.py`. Every one of those is obsolete.

This document describes the **actual** clean implementation, by path and by hash.

---

## 1 · UG25 access — exact and accurate wording

> **UG25 is sealed from development execution before operator authorization.**

This document does **not** claim UG25 has never been read by any audit process. It has:
`code/sealing_proof.py` loads UG25 **once, after development outputs exist**, solely to search
those outputs for leakage, and discards it immediately. It builds no alignment, no profile and
no score, and that read is declared in `tables/ug25_sealing_proof.tsv`.

What is guaranteed is narrower and true: **no development step — calibration, thresholding,
catalytic derivation, construction validation or table generation — materialised UG25.**

## 2 · Frozen implementation, by path and hash

| role | path | sha256 |
|---|---|---|
| mapper | `code/mapper.py` | `69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef` |
| loader | `code/loader.py` | `e39fb4eee45904cab3c681f033744950fe53e9316f5d54809a9c23285b2d3a24` |
| C6 policy | `code/c6_policy.py` | `41546742b6b2f6196664a632d73f480da92b1fcd49f07e558a8dbbbc2ff07a93` |
| controls | `code/controls.py` | `bf06e614ffec48144b68d317f3dc43f480208f998fa5fe5436cac550aa023d61` |
| canonical order | `code/canonical_order.py` | `3f7bf3b6c8245a33abb7899d648cbc4616fc82941c9e4174c6f11794ab52eec7` |
| integrity | `code/integrity.py` | `817dcbea66f8b7eb22ce3558536f12a1d79a73f832468f7f4165161dbf8e92d7` |
| pipeline | `code/pipeline.py` | `4fbeb49e9c69e30cb47e1dfef462a14b34062b330128490f999dc28770c7d2bd` |
| verifier | `verify.sh` | in the bundle manifest |

The mapper hash is identical to the one in `rt07_mapper_validation_repair` and
`..._v2` — the science is carried over, not rebuilt.

## 3 · Runtime family authorization — how it is supplied

`code/loader.py` contains **no** UG25 reference, no sealed-family list and no token. It reads
the permitted family list from the environment variable:

```
RT07_AUTHORISED_FAMILIES
```

Unset or empty → the pipeline **fails closed** with an explicit error. There is no default
list, precisely so a scope can never be inherited silently from source.

- **Development runs** are invoked with
  `RT07_AUTHORISED_FAMILIES=Retrons,GII,DGRs,CRISPR,UG3,AbiA`.
- **The confirmatory run** is the only invocation that may include `UG25`, and only after the
  operator authorises it. The authorisation is the operator setting that environment variable
  at run time; it is **not** a constant in the source tree and cannot be granted by editing a
  file in the bundle.

## 4 · Canonical order and seed — frozen

```
CANONICAL_FAMILY_ORDER = ("Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA")   # NOT sorted
CANONICAL_SEED         = 20260917
CANONICAL_ORDER_HASH   = sha256("Retrons|GII|DGRs|CRISPR|UG3|AbiA#20260917")
```

Load-bearing: one shared RNG feeds control generation, so the visit order determines which
di-shuffles fail. Sorting it produced a different failed-replicate set. `assert_canonical()`
fails closed on any drift of order or seed; tests S10 and S11 prove a reorder and a seed change
are both caught.

## 5 · Frozen scientific rules — unchanged, not re-derived

| parameter | value |
|---|---|
| `PP_LO` | 0.50 (fixed by principle; never searched) |
| `PP_HI` | 0.75 |
| `S_MIN` | 10 |
| `K_MIN` | 30 |
| `T1` | 0.32 |
| `D_MAX` | 0.48 (predeclared C4 bound; **weak** — see §11) |
| `D_RANDOM` | 0.067 (diagnostic only, never enforced) |
| anchors | the 150 frozen `ALL_PARTNERS` states, span 107–317 |
| `CAT_STATE` | **262** (MAPPED-only modal state; construction agreement 207/210 = 0.9857, floor 0.80) |
| match-state convention | `-M 50` operational; `-M 60` and `-M a2m` sensitivity reported |

**Per-state calls:** `MAPPED` (posterior ≥ 0.75) · `AMBIGUOUS` (0.50 ≤ p < 0.75) ·
`UNSUPPORTED` (p < 0.50) · `DELETED_STATE`. **Only `MAPPED` is evidence.**

**Abstention**, reason-coded, closed vocabulary: `(MAPPED, OK)`,
`(ABSTAIN, NO_QUALIFYING_DOMAIN)`, `(ABSTAIN, INSUFFICIENT_SUPPORTED_ANCHORS)`.

**Catalytic rule:** the catalytic position is an HMM **state**, not a motif. The call is the
residue the alignment path places at `CAT_STATE`; motif matching only characterises it. Only
`MAPPED` contributes positive catalytic evidence; `AMBIGUOUS`, `UNSUPPORTED` and
`DELETED_STATE` occurrences are landed in `catalytic_excluded_occurrences.tsv` and excluded.

## 6 · Control classes and construction — frozen

Three classes per sequence: **mono-shuffle** (composition), **di-shuffle** (every adjacent-pair
count, Altschul–Erikson), **reverse** (composition + local pair structure + length).
**3 replicates per sequence per class** for the confirmatory design (the construction
demonstration uses 1; the design parameter is explicit at every call site, never inferred).

Di-shuffle failures are recorded **by identity**, counted, landed and **never substituted**.

## 7 · C6 logic — per class, exact accounting

C6 **PASS** requires, for **every** class independently:
`max(class MAPPED-anchor count) < min(real MAPPED-anchor count among non-abstaining)`.
**One class violating fails C6 even when the pooled statistic is clean.**

**Identity binding is MANDATORY.** Every class must supply three explicit `list[str]`
collections — attempted, valid and failed — and C6 reconciles IDENTITIES, not totals:

```
set(valid_ids) | set(failed_ids) == set(attempted_ids)
set(valid_ids) & set(failed_ids) == empty
len(valid_ids) == n_valid ,  len(failed_ids) == n_failed ,  n_valid + n_failed == n_attempted
```

There is no count-only mode. Counts alone cannot detect a replicate that silently disappears,
because counts carry no names; an attempted-ID universe does.

**Type contract:** each ID collection must be exactly `list[str]` (`type(x) is list`, every
element `type(e) is str`, non-empty after stripping). Rejected with a reason code, never
coerced: `set`, `dict`, `tuple`, generator, iterator, `None`, `int`, `float`, scalar `str`,
`bytes`, nested containers, non-string elements. A malformed container is a controlled `FAIL`,
never an uncaught exception.

Failure also closes on: under- or over-accounting; duplicate valid or failed IDs; a replicate in
both sets; an ID absent from the attempted universe; an attempted ID in neither set; a
valid-ID/value count mismatch; an attempted-ID count disagreeing with the design; an undeclared
control class in any of the four containers; non-finite, negative, non-integer or non-numeric
counts; `n_real > n_eligible`; a non-positive or non-integer denominator; a bad design
parameter; a non-dict container.

The production control generator emits these identities itself
(`code/controls.py:make_negatives` returns attempted/valid/failed ID lists), so C6 re-verifies
them rather than reconstructing them from counts. They are landed in
`tables/control_replicate_identities.tsv`.

Replicate minimum: **≥ 90%** of expected per class, absolute floor 20. p95 is **reported**,
never a pass condition — the reverse class reaches p95 10 on construction data where the mapper
works correctly, so a per-class p95 requirement would be unpassable rather than strict.

## 8 · Integrity requirements for the confirmatory run

- Manifest and its detached `.sha256` sidecar live **outside** the bundle, in
  `review-stage/manifests/`; the expected root also lives outside, in
  `review-stage/roots/FINAL_PRE_UG25.root`.
- `verify.sh` and `integrity.py verify` **require** an externally supplied pinned root. There is
  no unpinned mode. An absent, malformed or all-zero root fails.
- Symlinks and hard-linked (aliased) files anywhere in the bundle are violations.
- `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, `PYTHONPYCACHEPREFIX` outside the bundle, and code
  executed from a temp copy so the bundle is never the import root.
- **Honest limit:** this is cryptographic *detection*, not OS immutability. The owner can
  rewrite files, manifest, sidecar and root file together. What that cannot do is match a root
  value a reviewer holds out-of-band. Filesystem modes are a speed bump; the external root is
  the anchor.

## 9 · Expected output schema for the confirmatory run

Per-sequence: `sequence_id`, `component`, `n_mapped`, `n_ambiguous`, `n_unsupported`,
`n_deleted`, `pct_mapped`, `verdict`, `reason`, `domain_bitscore`, `catalytic_verdict`.
Per-component: `component`, `n_sequences`, `role`, `median_mapped`, `median_pct`, `n_abstain`.
Controls: per class `n_attempted`, `n_valid`, `n_failed`, failed IDs, `max`, `mean`, `p95`,
`n_with_any_mapped`, plus a `POOLED` row. Plus a genealogy audit and a sealing proof.

## 10 · Numeric success / failure criteria

| # | criterion | passes when | fails when |
|---|---|---|---|
| C1 | callability | every qualifying component (≥5 seqs) median `MAPPED` fraction **≥ T1 = 0.32** | any qualifying component below 0.32 |
| C2 | support | all calls use the frozen posterior rule (`MAPPED` needs p ≥ 0.75) | any call outside the frozen rule |
| C3 | catalytic | among sequences whose `CAT_STATE` call is exactly `MAPPED`, the fraction beginning `[YF].DD` is **≥ 0.80** | < 0.80, **or zero sequences have `CAT_STATE` = `MAPPED`** (undefined → FAIL CLOSED, never "not testable") |
| C4 | no collapse | \|median difference between the two qualifying components\| **≤ D_MAX = 0.48** | > 0.48 |
| C5 | abstention | every abstention carries a reason from the closed vocabulary; all four call classes representable | an unexplained abstention or an unreachable class |
| C6 | controls | per-class separation and exact accounting, per §7 | any class violating, empty, depleted or unreconciled |
| C7 | no tuning | no threshold changed after UG25 was opened | any post-hoc change |

**C4 is weak and is declared weak.** `D_MAX = 0.48` is a between-*family* bound applied within
one family; the same-population null is 0.067. **A C4 pass is close to uninformative and must
not be presented as evidence.**

## 11 · Mandatory precondition — genealogy audit first

Before any mapping: the same audit applied to G2L, against all six construction families —
exact sequence overlap, identifier overlap, content scan, and the best-identity distribution
under **both** the identity leg **and** the full link rule (identity ≥0.30 **and** min-coverage
≥0.50; the G2L report quoted 48/51 on identity alone where the full rule gave 28/51 — **both**
must be reported). Classify as exactly one of `FRESH_LINEAGE`,
`FRESH_FAMILY_WITHIN_RELATED_LINEAGE`, `NOT_INDEPENDENT`. **`NOT_INDEPENDENT` stops the gate.**
The classification is recorded before mapping and not revised afterwards.

## 12 · Feasibility — the only UG25 numbers used

`eligible_N = 28`, components **19 / 5 / 4**; qualifying (≥5): **19** and **5**; the component
of 4 is descriptive only. From the pre-existing candidate audit, which contains **no mapping
performance**. Stated limitation: the second qualifying component has **5** sequences — thinner
than G2L's 9 — so its median carries wide uncertainty and must be reported as a range.

## 13 · Stop conditions

**One run.** No iteration, no threshold adjustment, no re-selection after results are visible.
A failed criterion **fails closed** and is recorded as a failure — as UG5 v2 was — never
repaired into a pass. Before the run: verify the external pinned root. After the run: verify it
again. Both values go in the report. **A freeze violation is itself a gate failure.**

## 14 · Not authorised

This gate is **prepared only**. It is not executed by this task. g4b, g5 and g6 remain closed.
