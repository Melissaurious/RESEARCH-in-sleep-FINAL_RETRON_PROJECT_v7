# DECISION — UG25 confirmatory transfer SUPPORTED. Stage-2 validation CLOSED.

Date: 2026-09-17 · Track `rt07` · Status: **Stage 2 validation closed · Endpoint A · g4b may begin**

Post-run independent review: Codex `gpt-5.6-sol` (xhigh, read-only), thread `01a0afb3`.
**`PASS_WITH_REQUIRED_REPAIRS` · 7/10 · CONFIRMATORY TRANSFER: SUPPORTED · g4b may begin ·
g5 remains blocked.** The reviewer states the required repairs are "documentary and
interpretive; they do not warrant another confirmatory run or method-development cycle."

Supersede by a new record, never by rewriting.

---

## 1 · Pre-UG25 validation formally closed

Accepted: C6 identity binding closed; explicit attempted/valid/failed replicate identities
required; malformed reachable inputs fail closed; production identity binding present; mapper
unchanged; thresholds unchanged; controls unchanged; UG25 predeclaration current; UG25 sealed
from development execution; clean bundle reproducible across temp roots; external root/freeze
mechanism intact.

**Reviewer fields recorded verbatim, not reconciled:** formal verdict `FAIL_BLOCK`; score
`8/10`; classification `B`; and the reviewer's own statement that the originally authorised
blocker **is closed**.

**Operator disposition on the residual:** the newly raised issue — a dict key whose custom
`__eq__` raises during membership testing — is classified
**`OUT-OF-SCOPE / NON-LOAD-BEARING RESIDUAL ENGINEERING RISK`**. The registered confirmatory
pipeline does not accept arbitrary Python objects at that boundary: replicate IDs are generated
internally as f-string literals, the class keys are the literals `MONO`/`DI`/`REV`, and identity
containers are enforced as `list[str]`. No registered path admits a hostile object. Validator
hardening against arbitrary adversarial objects is **closed** and was not continued.

## 2 · Execution

One run, 2026-09-17T14:05:41Z, `run_ug25_once.sh`. Authorisation supplied at run time:
`RT07_AUTHORISED_FAMILIES=Retrons,GII,DGRs,CRISPR,UG3,AbiA,UG25`.

| root | value | status |
|---|---|---|
| pre-UG25 bundle, **before** the run | `fc9cde03a13282b2aaa176a10b5da7c5798a4f2cce763dffad076575a8d2d889` | INTACT |
| pre-UG25 bundle, **after** the run | `fc9cde03a13282b2aaa176a10b5da7c5798a4f2cce763dffad076575a8d2d889` | INTACT (unchanged) |
| confirmatory bundle, frozen | `6bf14eb47022f062f6d7a10d8ae86cb1d7d7c4d412625f0b229b9dd129a8095e` | 15 files, locked |

Reviewer independently confirmed: **one** real-sequence `state_to_residue` call (the other nine
are the required 3 classes × 3 replicates); authorisation checked before UG25 is materialised;
genealogy before mapping; mapper hash identical in all three bundles; no changed threshold.

## 3 · Result — 7/7 predeclared criteria PASS

| # | observed | result |
|---|---|---|
| C1 | comp0 **0.5133** (77/150, n=19), comp1 **0.5933** (89/150, n=5) vs T1 0.32 | PASS |
| C2 | frozen posterior rule, PP_HI 0.75 / PP_LO 0.50 | PASS |
| C3 | **26/27 = 0.9630** vs floor 0.80 | PASS |
| C4 | **0.0800** vs D_MAX 0.48 | PASS — **non-evidential by prior declaration** |
| C5 | reasons `{OK: 28}`; all four call classes present | PASS |
| C6 | per-class separation + exact identity accounting, no violations | PASS |
| C7 | no threshold changed after authorisation | PASS |

Genealogy: 0 exact overlap, 0 identifier overlap, **0 of 28** links under the registered
identity ≥0.30 **and** min-coverage ≥0.50 rule → **`FRESH_LINEAGE`**, recorded before mapping.

Controls (max MAPPED anchors): MONO **10**, DI **13**, REV **17**; weakest real sequence **54**.
Complete separation. Zero di-shuffle generation failures.

## 4 · ERRATA — three of the executor's own statements were wrong

| # | superseded | corrected |
|---|---|---|
| **U1** | "roughly **half** the frozen anchors are `DELETED_STATE` in UG25" (`UG25_RESULT.md` §8) | **FALSE.** `DELETED_STATE` is **1128/4200 = 26.9%**. Non-`MAPPED` of any kind is **42.9%**; `MAPPED` is **57.1%** of all anchor calls. The intended point — that callability is far from complete — stands, but the number quoted did not support it |
| **U2** | C7 reason string: "the gate restates no threshold of its own" | **FALSE.** `ug25_gate.py` restates five constants: `LINK_IDENTITY` 0.30, `LINK_COVERAGE` 0.50, `MIN_COMPONENT` 5, `REPLICATES` 3, `AGREEMENT_MIN` 0.80. **Each matches the frozen predeclaration exactly**, so this is inaccurate provenance wording, **not** tuning — the reviewer verified no threshold changed. The eight calibrated parameters (`PP_HI`, `PP_LO`, `S_MIN`, `K_MIN`, `T1`, `D_MAX`, `D_RANDOM`, `CAT_STATE`) *are* read from the frozen tables |
| **U3** | the predeclared post-run root verification was performed as specified | **PARTIALLY.** `run_ug25_once.sh` verifies the root **pre-run only**. The post-run verification was run as a separate manual command and is reported in §2, but the runner does not implement it, so §13 of the predeclaration was not satisfied verbatim |

Also accepted from the review, as wording corrections:

- **`FRESH_LINEAGE` must not be read as "no evolutionary relationship."** It is the registered
  operational classification. All 28 sequences have short high-identity local hits — median
  identity **0.588** at median min-coverage **0.021**.
- **REV replication is not independent.** 28 unique reversals repeated three times. "84
  independent REV controls" or "252 independent controls" would be inflated. Max-based C6 is
  unaffected: all 28 unique reversals were tested and the maximum 17 sits far below 54.
- The UG25 run tested **`-M 50` only**. Claiming it tested `-M 60` would be inflation.
- "Confirmed" for catalytic placement means motif concordance at a state, **not** independent
  residue truth.

`UG25_RESULT.md` is inside the frozen bundle and is **not edited**; these corrections live here.

## 5 · Final Stage-2 claim — reviewer's wording, adopted

> Using the frozen GII-derived HMM and 150-anchor frame under the operational `hhmake -M 50`
> convention, the frozen alignment-path mapper met all seven predeclared pass conditions in its
> single UG25 holdout run. UG25 had no exact sequence or identifier overlap with construction and
> no link satisfying the registered identity ≥0.30 and minimum-coverage ≥0.50 rule, making it
> `FRESH_LINEAGE` under that operational classification despite short high-identity local hits.
> Median MAPPED-anchor callability was **51.3%** in the qualifying component of 19 sequences and
> **59.3%** in the qualifying component of five sequences; the latter estimate is thin and ranged
> from 56.0% to 66.7% per sequence. Only MAPPED calls counted as evidence. At HMM state 262,
> **26 of 27** MAPPED calls began the predeclared `[YF].DD` motif. Each synthetic control class
> separated completely from the real sequences: maxima were **10, 13 and 17** MAPPED anchors for
> MONO, DI and REV, versus **54** for the weakest real sequence; REV represents 28 unique
> reversals repeated three times. This supports transfer of frozen-anchor callability and
> state-anchored motif concordance to this one UG25 family.
>
> It does **not** establish independent residue-level accuracy, UG25 performance under `-M 60` or
> `-M a2m`, general specificity against unrelated natural proteins, evolutionary unrelatedness
> beyond the registered link rule, or transfer beyond this family.

## 6 · Stage-2 terminal decision: **Endpoint A**

Confirmatory transfer is **SUPPORTED**. Stage-2 validation is **closed**. No further
transfer-validation cycle.

**g4b may begin** with the empirically demonstrated scope in §5 — and no wider.
**g5 remains BLOCKED. g6 NOT STARTED.**

Frozen for the record: the mapper is `69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef`;
no mapper code, threshold, control definition, anchor set, `CAT_STATE`, ambiguity or abstention
rule, or UG25 criterion may change without invalidating this confirmatory status.
