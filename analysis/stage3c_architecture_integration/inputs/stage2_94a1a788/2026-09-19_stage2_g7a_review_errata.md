# ERRATA — `g7a` historical RT0–RT7 bridge, from the independent review

Date: 2026-09-19 · Track `rt07` · Status: **5 required repairs applied as errata · all eight statuses PRESERVED · bundle UNCHANGED**

Review: `review-stage/INDEPENDENT_REVIEW_RESULT_g7a.md` — Codex `gpt-5.6-sol`, thread
`01a0b9a1`, `PASS_WITH_REQUIRED_REPAIRS`, 7/10, **0 blockers**.

**This record is additive.** `results/rt07_g7a_rt0_rt7_bridge/` is frozen and sealed; no file in
it is edited, regenerated or re-sealed, and **nothing is recomputed**. Its
`tables/g7a_crosswalk_resolved.tsv`, `tables/g7a_closure_decision.tsv`,
`tables/g7a_historical_evidence_register.tsv`, `control/ASSIGNMENT_RULE.md` and `README.md`
are read through this erratum. **The machine-readable superseding table is
`docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv`**; downstream work must use it in
place of the frozen `downstream_may_say` column.

The production crosswalk `results/rt07_g4b_production_mapper/control/CROSSWALK_RT0_RT7.tsv`
remains **unchanged and `UNRESOLVED` in all eight rows**. Production emits `state_id` only. The
reviewer confirmed this isolation.

---

## The eight statuses — ALL PRESERVED

| label | terminal status | qualification carried from the review |
|---|---|---|
| **RT0** | **UNRESOLVED / NOT IDENTIFIABLE** | upheld; historical *and* instrumental limits (reason C) |
| **RT1** | **UNRESOLVED / NOT IDENTIFIABLE** | upheld; historical *and* instrumental limits (reason C) |
| RT2 | PARTIAL / INTERPRETIVE | only LtrA 97–123 of reconstructed 79–123 observed |
| RT3 | ESTABLISHED OPERATIONAL CORRESPONDENCE | **with qualification** — Route C is not independent historical replication (E-g7a-1) |
| RT4 | ESTABLISHED OPERATIONAL CORRESPONDENCE | **with frame-instability qualification** (E-g7a-3) |
| RT5 | ESTABLISHED OPERATIONAL CORRESPONDENCE | direct YxDD feature anchor; named only as the joint RT5+RT6 region |
| RT6 | PARTIAL / INTERPRETIVE | **jointly with RT5 only**; not separable |
| RT7 | ESTABLISHED OPERATIONAL CORRESPONDENCE | **with narrowed wording** (E-g7a-4) |

**RT0 and RT1 are not resolved by this erratum and may not be resolved inferentially** — not by
analogy, interpolation, structural reasoning, or what "must" lie in the window. Only primary
historical evidence could change either. The defining source for RT0, Malik, Burke & Eickbush
1999, is not held. Non-observability is a statement about the sources and the instrument, not
about biology.

## `TERMINAL` — defined

Wherever it describes g7a, **`TERMINAL` means workflow closure for the current instrument and
evidence set — not complete historical recovery of RT0–RT7.** It is a decision that this project
will do no further RT0–RT7 bridging with the frozen mapper and the held sources. It does not
assert that the historical literature is fully recovered, and it does not prevent future primary
evidence from changing an `UNRESOLVED` or `PARTIAL` status.

---

## E-g7a-1 · Route C independence is overstated — REQUIRED

**Superseded:** `control/ASSIGNMENT_RULE.md` A4: *"This is genuine convergence, not
circularity"*, and any reading of Route C agreement as independent replication.

**Governing interpretation:** Route C comparator points are **computationally distinct** from
Route P intervals — different sequences, different method. But they are **not an independent
primary historical determination**: g3 established that the four prior frames are coordinate
transfers over **one** anchor-derived landmark set, not replication
(`results/rt07_g3_prior_method_replication/README.md:64`). Agreement between Route P and
Route C is **corroboration of placement**, not independent confirmation of historical
semantics. This qualifies RT3, RT4 and RT7; it changes no status.

## E-g7a-2 · The primary-evidence register omits source-stated Xiong correspondences — REQUIRED

**Superseded:** the claim that RT5/YxDD is the *only* source-stated feature-to-number
relationship (frozen `downstream_may_say` for RT5; `ASSIGNMENT_RULE.md` A2), and the
register's marking of Poch-to-domain relations as `project_inferred`.

**Governing correction:** the g1 transcriptions, **verified** against Xiong & Eickbush 1990,
p. 4, state two motif-set-to-domain correspondences directly:

| id | source | verbatim | status |
|---|---|---|---|
| **X05** | xiong1990 p. 4 | "In the case of Poch et al. (1989) the five motifs identified (regions a-e) correspond to our domains 3-7." | **SOURCE-STATED** |
| **X06** | xiong1990 p. 4 | "In the case of Webster et al. (1989) the four blocks identified correspond to our domains 2-5." | **SOURCE-STATED** |

These belong in the evidence chain as **source-stated correspondences**, with their limitation
retained: they relate published motif sets to domain *numbers* and **state no LtrA residue
coordinates**. The corrected statement is: *RT5 is the only label with a source-stated,
residue-level catalytic feature (YxDD) measured on LtrA; X05 and X06 are source-stated motif-set
correspondences for domains 2–7 without coordinates.* No status changes, and neither quote
touches RT0 or RT1.

## E-g7a-3 · Propagate RT4's frame instability — REQUIRED

**Superseded:** RT4 correspondence `SUPPORTED_1_TO_1`, unqualified (frozen crosswalk and
closure tables; `2026-09-18_stage2_g7a_rt0_rt7_closure.md:24`).

**Governing correction:** in the independent alignment frame, reconstructed block 4 is
**`SPLIT_INTO_3`**, Jaccard **0.410** (frame 1: LtrA 170–230; frame 2 best match 173–197, three
overlapping blocks) — `results/rt07_g2_reference_reconstruction/tables/g2_frame_correspondence.tsv`
row for block 4. RT4 stays **ESTABLISHED OPERATIONAL CORRESPONDENCE**, and its 42 supporting
states and LtrA localisation are unchanged, but its cardinality is **`SUPPORTED_1_TO_1` in the
primary frame, `SPLIT_INTO_3` in the independent frame**. Any figure annotating RT4 must show
this instability.

## E-g7a-4 · Narrow the RT7 wording — REQUIRED

**Superseded:** R364/R365 as "a stated domain junction" (`ASSIGNMENT_RULE.md` S-a); "Three
routes — primary text, independent reconstruction, and the frozen instrument — agree"; "RT7 is
the best-determined label"; "the strongest correspondence" (bundle `README.md:81–85`).

**Governing correction:**

* R364/R365 is a **source-described between-domain proteolytic landmark** — a cleavage site
  Blocker places "between RT7 and domain X". That a sequence-domain edge coincides with it is an
  **inference**.
* The frozen anchor span ending at LtrA **363** is numerical proximity to the instrument's own
  reach. It is **not a third independent validation route** and may not be counted as one.
* **No unconditional ranking.** RT7 has the strongest **LtrA-local terminal coordinate**; RT5
  has the strongest **transferable feature anchor** (YxDD). Neither is "the strongest" without
  that qualifier.

RT7 remains ESTABLISHED, supported by reconstructed block 6 (LtrA 356–361, reproduced exactly
across frames), Route C point 357, and the source-described C-terminal landmark.

## E-g7a-5 · Remove the withdrawn RT0 statement from LAUNCHER_03 — REQUIRED

`launchers/LAUNCHER_03_rt0_rt7_closure.md` §"Route S" still stated the interpretation withdrawn
by Amendment 1: *"RT0 = M1–R85, RT1/7 = R86–R364"*. Amendment 1 corrected execution, but the
governing launcher remained internally inconsistent. **The statement is removed from the launcher
in this commit and replaced by a marked correction** that points here; the launcher's structure
is otherwise unchanged.

Correct reading, from the landed Blocker transcription: M1–R85 is a proteolytic fragment
**containing** RT0; R85 lies **inside** RT1; **no source-stated RT0|RT1 boundary exists** in any
held source.

---

## Advisory notes (not required repairs)

* **D1 provenance.** The RT6 downgrade rule "D1" is defined in `scripts/s07_closure.py:6,29–30`,
  not in the predeclared `control/ASSIGNMENT_RULE.md`. It is conservative and appropriate; it
  should be described as an implementation-level rule, not a predeclared one.
* **Packet hash coverage.** The 25 review-packet hashes cover the review artefacts but not the
  generator scripts, which the bundle's own `OUTPUTS.tsv` does hash. Packet-level integrity is
  therefore narrower than bundle-level integrity.
* **RT5 residue note.** `CAT_STATE` 262 maps to LtrA 306 (YADD); the 34 anchor states covering
  block 5 begin at 311. The two are separate measurements and were correctly not pooled.
* **Unverified by the reviewer:** printed figure extents in Xiong and Blocker, page typography,
  the Malik definition (not held), and the claimed pre-execution timing of Amendment 1 beyond
  the bundle's own provenance.

## Strongest defensible statement — adopted from the review

> On LtrA, the frozen conserved-state system supports observable portions of
> project-reconstructed intervals corresponding operationally to RT3, RT4, the joint RT5+RT6
> region, and RT7; RT5 has a direct catalytic-feature anchor, while RT7 has a strong
> source-described C-terminal proteolytic landmark. RT2 is only partial. RT0 and RT1 remain
> unresolved because both their recoverable historical boundaries and the frozen instrument's
> N-terminal reach are insufficient.
>
> These are LtrA-local interpretation-layer correspondences. They neither define universal
> biological domains nor validate the mapper, and they do not license absence claims.

## Downstream use

| use | status |
|---|---|
| historical terminology in the thesis | **PERMITTED** — with statuses, LtrA-local scope and this erratum's wording |
| figure annotation on LtrA | **PERMITTED** — RT0/RT1 shown unresolved, RT2 partial, RT5/RT6 joint, RT4 frame-unstable |
| descriptive comparison with Stage-2 states | **PERMITTED** — through the erratum table only; production keeps `state_id` |
| Stage-3 structural interpretation | may use the bridge descriptively; **must not be presented as resolving any label** |
| classification reassessment | **NOT SUPPORTED** |
| RT0–RT7 as universal domains | **NOT SUPPORTED** |
