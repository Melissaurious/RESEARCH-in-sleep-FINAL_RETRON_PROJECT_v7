# DECISION — LAUNCHER_02 amendment: `g4b` is the production freeze that satisfies "g4 frozen before g5"

Date: 2026-09-17 · Track `rt07` · Status: **amendment applied · g5 unblocked**

Supersede by a new record, never by rewriting.

---

## 1 · What was amended, and what was not

`launchers/LAUNCHER_02_rt0_rt7_definition.md` §7 stated the dependency
`g4` must be frozen before `g5`, but named no artifact that had frozen it. `g4` was in fact
executed as more than one landed step, and nothing in the launcher recorded which one was
the freeze.

**The dependency sentence is unchanged.** One block was added immediately after it recording
the historical progression and naming the artifact:

| step | what it did | landed at |
|---|---|---|
| `g4a` | mapper development and validation | `results/rt07_g4a_repaired/` and the repair bundles |
| confirmatory transfer validation | the single UG25 holdout run, closing Stage-2 validation at Endpoint A | `results/FINAL_PRE_UG25_VALIDATION_BUNDLE/`, `results/rt07_ug25_confirmatory/` |
| **`g4b`** | **production freeze** | **`results/rt07_g4b_production_mapper/`** |
| `g5` | catalogue application | `results/rt07_g5_catalogue_application/` |

Recorded in the amendment: instrument `rtmap-1.0.0/53a1e738a19b3896`, instrument sha256
`53a1e738a19b38967563b4f4d733047b26123f754a7d592fd0186e7bd9c331f5`, mapper code sha256
`69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef`, schema
`rtmap-schema-1.0`, bundle root
`0b025cbab192f64d05ef0a9aff47859b998fe3158dc0199cd47cbbd040620d3f`, commit `dd9cdae`; and
that `g5` was authorised by the **independent packaging review** (round 2, 9/10,
`MAY g5 BEGIN: YES`) — a packaging-fidelity review, not a scientific one.

**Deliberately NOT done:**

* no gate-table row for `g4b`. It produces no claim-bearing number, so a `FULL` row would
  misrepresent engineering reproduction as measurement. The amendment says so explicitly.
* no change to any gate's ONE measurement, weight, stop condition or ordering.
* no reinterpretation of any historical result. The progression is recorded as it happened.
* no change to the architecture of §7, §7a–§7e, §8 or §9.

## 2 · Historical Stage-2 bundles — disposition

**`HISTORICAL / AUDIT ARTIFACTS — NOT PRODUCTION DEPENDENCIES`**

| bundle | `bundle_valid.sh` | disposition |
|---|---|---|
| `results/FINAL_PRE_UG25_VALIDATION_BUNDLE/` | 8 findings | historical / audit artifact |
| `results/rt07_ug25_confirmatory/` | 8 findings | historical / audit artifact |
| `results/rt07_g4a_repaired/` and the earlier repair bundles | not conformant | historical / audit artifact |
| `results/rt07_g4b_production_mapper/` | **passes BS-1..BS-10** | **production dependency** |

They were landed under the layout in force at the time and were reviewed and frozen under it.
They are **not** rebuilt or restructured to satisfy later packaging conventions. They remain
valuable as provenance and scientific history — including their failed designs and freeze
violations — and each carries its own external pinned root.

One is reopened only if a concrete `g5` dependency requires it. §3 records the one case where
that test actually bit.

## 3 · A production dependency that was not in version control

Auditing what `g5` consumes turned up a real gap, distinct from the bundle-conformance
question:

| file | role | was |
|---|---|---|
| `results/rt07_g4a_repaired/work/GII.deriv.hmm` | **the frozen profile — the production ruler**, sha256 `292495a4…`, LENG 471 | **untracked in git** |
| `results/rt07_ug5_holdout_gate/tables/ug5_frozen_anchor_coordinates.tsv` | the 150 frozen anchors, sha256 `c48315ae…` | untracked in git |
| `results/FINAL_PRE_UG25_VALIDATION_BUNDLE/code/mapper.py` | the frozen mapper's origin, sha256 `69575dc7…` | untracked in git |
| `results/FINAL_PRE_UG25_VALIDATION_BUNDLE/tables/construction_validation_sequence.tsv` | the expected values g4b's smoke check S1 compares against | untracked in git |

These exist on disk and every one is hash-verified at run time, so `g5` executes correctly —
this is a **provenance** gap, not an execution blocker. But the file that defines the
production coordinate system was not in the repository, and "git holds versions" is a
project rule.

**Decision: track those four files, and nothing else.** This is not retrofitting a bundle to
current conventions — it is putting a named `g5` dependency under version control, which §2
explicitly permits. The bundles' structure, content and roots are untouched.

The anchor table and the frozen parameter tables were already safe: `g4b` carries
byte-identical copies, which commit `dd9cdae` tracked. The profile HMM was **not** copied
into `g4b`, on purpose — copying it now would change `g4b`'s instrument tree digest and
therefore the instrument identifier, which is not permitted. Tracking it in place is the
only fix that leaves the instrument untouched.

## 4 · Working-tree classification

| item | classification | reasoning |
|---|---|---|
| `results/rt07_g4a_repaired/work/GII.deriv.hmm` untracked | **was `G5-BLOCKING` for provenance** — now resolved (§3) | the production ruler must be in version control |
| the other three untracked production inputs (§3) | `HOUSEKEEPING-NONBLOCKING` — resolved with the above | hash-verified at run time; now also tracked |
| `docs/BLOCKED.md` modified, uncommitted (+454 lines) | `UNRELATED / OTHER SESSION` | the prior session's open-question log. `g5` consumes nothing from it |
| `LAUNCHER_02` modified, uncommitted (+15 lines) | `UNRELATED / OTHER SESSION` | the 2026-09-16 `g4` design amendment, never committed. `g5` consumes nothing from it |
| ~25 untracked `docs/decisions/2026-09-16*`, `2026-09-17*` records | `UNRELATED / OTHER SESSION` | prior-session Stage-2 records |
| untracked prior Stage-2 `results/` bundles | `HOUSEKEEPING-NONBLOCKING` | audit artifacts per §2, except the four files in §3 |
| 13 `specs_exist.sh` MISSING references | `HOUSEKEEPING-NONBLOCKING` — see below | none is consumed by `g5` |

### `specs_exist.sh` — why it fails, and why `g5` proceeds

All 13 failures are references **from the uncommitted `docs/BLOCKED.md`** to files that are
not *tracked*. Checked individually:

* **12 of 13 exist on disk** and are untracked prior-session decision records, a stop report
  and a review request. The checker's complaint is about git tracking, not absence.
* **1 of 13 is genuinely absent**: `proposed/research_contract_C3_C9_amendment.md`. Its only
  reference, `BLOCKED.md` item 4, reads *"The separability argument in
  `proposed/research_contract_C3_C9_amendment.md` **is withdrawn as a rescue** — missing truth
  is not positive evidence."* It is cited in the past tense as a **withdrawn** proposal. No
  gate, no bundle and no production artifact consumes it.

**None of the 13 is a dependency of the frozen production mapper or of `g5` provenance.** The
frozen instrument's inputs are enumerated in
`results/rt07_g4b_production_mapper/INPUTS.tsv`, all hash-verified, and none of them appears
in the MISSING list. `specs_exist.sh` therefore does not block `g5`, and the prior session's
uncommitted work is not absorbed into the `g5` commits — it is committed separately, unchanged
and attributed, so the check can pass without this task claiming authorship of it.

## 5 · Verification performed before use

```
freeze.py verify results/rt07_g4b_production_mapper …   FREEZE INTACT
bundle_valid.sh results/rt07_g4b_production_mapper      OK: passes BS-1..BS-10
mapper_version                                          rtmap-1.0.0/53a1e738a19b3896
instrument_sha256                                       53a1e738…d9c331f5
code/rtmap/mapper.py sha256                             69575dc7…f10fceef
commit dd9cdae                                          present
```
