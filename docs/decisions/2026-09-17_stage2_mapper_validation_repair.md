# DECISION — Mapper validation repair (repairs 1–6 executed; repair 7 prepared only)

Date: 2026-09-17 · Track: `rt07` · Status: **repairs complete; UG25 NOT run; g4b/g5/g6 closed**

Executes the seven repairs recorded in `2026-09-17_stage2_g2l_transfer_review_FAILED.md` §8,
under operator authorisation. Bundle: `results/rt07_mapper_validation_repair/`.

Manifest `ROOT_SHA256 = 2f0cacc5793e46bdb0b9d0924278f42ceaceb0eecd1c87075700ae2c9f3efe6a`
(162 files), held **outside** the bundle at
`review-stage/manifests/rt07_mapper_validation_repair.MANIFEST`. Bundle locked read-only.

Supersede by a new record, never by rewriting.

---

## 1 · Repair status

| # | repair | status | changes mapper? |
|---|---|---|---|
| 1 | immutable provenance / freeze enforcement | **DONE** | no |
| 2 | non-rewriting correction of the G2L verdict | **DONE** (the FAILED record) | no |
| 3 | construction-only score/support + ambiguity + reason-coded abstention | **DONE** | **yes** |
| 4 | non-vacuous tests | **DONE** | no |
| 5 | numeric falsifiable criteria 1/4/6 | **DONE** | no |
| 6 | multi-motif catalytic rule | **DONE** | **yes** |
| 7 | UG25 confirmatory holdout | **PREPARED, NOT EXECUTED** | no |

## 2 · The frozen support rule (construction data only)

| parameter | value | derivation |
|---|---|---|
| `PP_LO` | 0.50 | fixed by principle — posterior <0.5 means the alternative path is likelier. Never searched |
| `PP_HI` | **0.75** | smallest of `{0.55, 0.65, 0.75, 0.85, 0.95}` with negative p95 = 0 and median real fraction ≥ 0.50 |
| `S_MIN` | **10** | smallest of `{0,2,4,6,8,10,15,20,30}` strictly above the observed negative max **8.1** bits |
| `K_MIN` | **30** | smallest of `{1,2,3,5,10,15,20,30}` strictly above the observed negative max **25** anchors |
| `T1` | **0.32** | 5th percentile of per-sequence `MAPPED` fraction over construction |
| `D_MAX` | **0.48** | spread of construction family medians (**predeclared C4 bound; weak**) |
| `D_RANDOM` | **0.067** | 95th pct of \|median diff\| over 2000 random half-splits (stricter diagnostic) |

**The full grid is landed with the failures visible** (0.55 → negative p95 = 12; 0.65 → 8), so
minimality is checkable rather than asserted. This is the discipline errata A1 established.

**Per-state calls:** `MAPPED` (PP ≥ 0.75) · `AMBIGUOUS` (0.50 ≤ PP < 0.75) · `UNSUPPORTED`
(PP < 0.50) · `DELETED_STATE`. Only `MAPPED` counts as evidence.

**Abstention reasons:** `NO_QUALIFYING_DOMAIN`, `INSUFFICIENT_SUPPORTED_ANCHORS`, both
demonstrated reachable and distinguishable (U10, U10b).

## 3 · Two findings that change how earlier results should be read

### 3.1 The previous decoy design understated the null

Maximum negative `MAPPED`-anchor count at `PP_HI = 0.75`, by control class:

| class | preserves | worst case |
|---|---|---|
| mono-shuffle *(the only class the G2L gate used)* | composition | **17** |
| di-shuffle | composition + every dipeptide count | **24** |
| reverse | composition + local pair structure + length | **25** |

The G2L gate's reported decoy ceiling was measured against the **weakest** of the three classes.
Its "real vs decoy" separation was therefore flattered by the control design. `K_MIN = 30` exists
because a sequence must beat the strongest observed negative before it may be called at all.

### 3.2 Criterion C4 is weak, and stays weak by choice

`D_MAX = 0.48` is a between-**family** bound applied to two components **within** one family.
The same-population null is `D_RANDOM = 0.067` — seven times tighter. Within-family *component*
spread cannot be measured on construction (only GII/CRISPR/Retrons have a second component, of
sizes 1, 4 and 1).

**The predeclared `D_MAX` is kept as the pass/fail bound.** Substituting `D_RANDOM` after seeing
calibration output would be replacing a predeclared criterion mid-flight — the exact error that
sank UG5 v2. `D_RANDOM` is reported alongside as a diagnostic. **A C4 pass is close to
uninformative and must not be presented as evidence.**

## 4 · Catalytic rule (repair 6)

`CAT_STATE = 262`, derived from construction only: the modal HMM state of `[YF].DD` across **210**
dyad-bearing construction sequences, with **207/210 = 98.6%** agreement against a predeclared
falsification floor of 80%. Runner-up state has **5** occurrences against 262's **207**.

**This independently confirms state 262 without using G2L.** The G2L observation (40/40 at state
262) is now corroborated by a construction-only derivation rather than resting on the holdout.

The rule is inverted from v1: the catalytic position is an **HMM state**, and the call is the
residue the alignment path places there. Motif matching only *characterises* that residue. The
number of `[YF].DD` occurrences becomes irrelevant to *where* the call is made, which dissolves
the multi-motif problem instead of special-casing it. Test U8 constructs the G2L failure class
synthetically and shows motif-first picks residue 21 while the state rule picks 262.

## 5 · Test matrix (repair 4)

**13/13 pass — 11 falsifiable empirical tests, 2 implementation invariants**, plus **9/9** freeze
tests. Every row carries `passes_when`, `fails_when`, positive control and negative control, and
every executable negative control is **executed**.

- **U6 replaces the vacuous T6.** v1's `t6()` returned `True` on every branch. U6 asserts in both
  directions — shuffle must map < `K_MIN` **and** real must map ≥ `K_MIN` — and can fail.
- **U9 proves ambiguity is not vacuous**: 1346 `AMBIGUOUS` calls across 45/45 construction
  sequences. v1's `ambrows` would have scored 0 here.
- **U2 resolves the unexplained T1 FAIL**: state 471 is `DELETED_STATE` with exactly one
  insert-assigned residue — a C-terminal placement tie, outside the 107–317 anchor span, changing
  no reported number. Asserted exactly rather than waived.
- **U11/U12 are labelled `IMPLEMENTATION_INVARIANT`** and are explicitly **not** transfer evidence.

## 6 · Construction validation under the frozen rule

| family | n | median `MAPPED` | OK | abstain | cat. confirmed | cat. substituted |
|---|---|---|---|---|---|---|
| GII | 40 | 0.950 | 40 | 0 | 40 | 0 |
| CRISPR | 40 | 0.913 | 40 | 0 | 39 | 1 |
| DGRs | 40 | 0.800 | 40 | 0 | 35 | 5 |
| UG3 | 40 | 0.550 | 40 | 0 | 40 | 0 |
| AbiA | 19 | 0.493 | 19 | 0 | 19 | 0 |
| Retrons | 40 | 0.473 | 38 | 2 | 34 | 6 |

237/239 callable; 2 Retrons abstain on `NO_QUALIFYING_DOMAIN`. The frame remains **GII-centred** —
Retrons and AbiA sit near half the anchors even under construction conditions, which is why
`T1 = 0.32` is low.

## 7 · Reproducibility and freeze

`verify.sh` regenerates into a temp tree and diffs: **14/14 computed products byte-identical**,
no product outside the reproduction path, no regenerated product missing from the bundle. It
never writes into the bundle — the `tee` defect cannot recur.

`freeze_manifest.py` detects **added**, **changed**, **removed** and **renamed** files and exits
non-zero. The ADDED case is the exact breach that occurred during the G2L review and that a
content-only checksum list would have missed. Manifests live under `review-stage/manifests/`,
outside the bundles they cover. The G2L bundle is now also manifest-covered
(`ROOT_SHA256 e6eb62bd…`, 132 files).

A defect found in the freeze checker during development is recorded rather than quietly fixed:
`build` hashed in `os.walk` order while `verify` hashed in sorted order, so the root hashes
disagreed on an intact bundle while still reporting `FREEZE INTACT`. Test F1c now pins it.

## 8 · Disclosures

- **`work/probe.*` and `work/probe2.*`** are scratch alignments from interactive probing while
  locating the second abstention reason code. They are **not** produced by `regenerate.sh` and are
  not part of any product. Removal was attempted and declined by the environment's command policy,
  so they are hashed into the manifest and disclosed here rather than left unexplained.
- **`di_shuffle` failed** to find a valid last-edge tree for **3** sequences (CRISPR 2, UG3 1).
  Those are absent from the DI rows; the table header states it. No mono-shuffle was substituted.
- **A first di-shuffle implementation was wrong** — a greedy Eulerian walk without the
  Altschul–Erikson last-edge constraint stranded edges and produced **0/19** successes, yielding an
  empty negative-control file. Caught by `hmmalign` failing closed on an empty input, not by
  inspection.
- **No UG25 object was read.** Verified by grep over all scripts and landed tables: the only
  occurrences of `UG25` are the `FORBIDDEN` guard and documentation strings; `work/` contains
  construction families only; no UG25 or G2L sequence identifier appears in any table.

## 9 · Gate state

- **UG25: prepared, not executed.** `control/UG25_PREDECLARATION.md`.
- **g4b, g5, g6: closed.** Unchanged by this record.
- **G2L: development/diagnostic evidence only**, preserved and not rewritten. It may not be
  described as a clean confirmatory holdout.

## 10 · Standing claim

> A GII-derived alignment model assigns actual sequence residues to conserved HMM states in a
> related held-out G2L family, and the catalytic state maps correctly in 40/40 dyad-bearing
> sequences; however, mapping support and ambiguity were not calibrated sufficiently for
> confirmatory transfer validation.

The repairs supply that calibration. **They do not upgrade the G2L result** — G2L was evaluated
under the old uncalibrated rule, and re-running it under the new rule would be evaluating a
holdout whose outcome is already known. Confirmatory evidence must come from UG25.
