# DECISION — Stage-2 g4 identifiability redesign: what g4 can validly estimate

Date: 2026-09-16 · Track: `rt07` · Status: **proposed; pending independent review and operator acceptance**

**Supersedes §5–§8 of** `docs/decisions/2026-09-16_stage2_g4_design_amendment.md`, which the
round-1 independent design reviewer returned at **score 3 / 10, verdict `not ready`**. That
record is **not rewritten**. Its own rule — *"Supersede this record by a new record, never by
rewriting it"* — was breached once already while its review was in flight, and that breach is
recorded in `review-stage/AUTO_REVIEW.md`. This record exists so it is not breached twice.

Supersede this record by a new record, never by rewriting it.

Design artifacts: `results/rt07_pre_g4_identifiability_redesign/`.

---

## 0 · What this record is, and is not

It is an **identifiability review**: it answers what quantity `g4` can validly estimate, given
that no currently available population supplies independent ground-truth start/end boundaries
for the conserved RT sequence regions.

It is **not** a method proposal that happens to carry some caveats. The order is deliberate and
is the correction the failed review demanded: the estimand is identified first
(`tables/estimand_matrix.tsv`), and only then are methods compared against it
(`tables/method_comparison_plan.tsv`).

**`g4` is not executed by this record. `g5` is not started.**

---

## 1 · Relationship to the prior g4 decision record

| portion of `2026-09-16_stage2_g4_design_amendment.md` | disposition |
|---|---|
| §1 — what g2 established | **RETAINED** in full. Measurements. |
| §2 — what g3 established | **RETAINED** in full. Measurements. |
| §3 — the corrected lineage of all167, anchors72, GOLD171, ph38, CAND95 | **RETAINED** in full. Measurements, landed in `results/rt07_pre_g4_seed_provenance/`. |
| §4 — statements superseded | **RETAINED**, and extended by §7 below. |
| §4a — the archive correction that could not be applied in place | **RETAINED**. Still requires operator action; the read-only mount is unchanged. |
| §5 — "the revised scientific object of g4" | **SUPERSEDED** by §3 here. The portable *region* detector becomes a portable *core-coordinate* detector; the region partition stops being the target object. |
| §6 — "the revised validation architecture" | **SUPERSEDED and NARROWED** by §4 here. Four arms survive, but with explicitly different epistemic status; the PDB arm is a structural comparator at ≤25, not a held-out validation arm. |
| §7 — revised reusable deliverables | **NARROWED** by `proposed/LAUNCHER_02_g4_diff.md` §2. Three renames, three additions. |
| §8 — non-goals and stop conditions | **SUPERSEDED** by §8 here, which adds the stop conditions the failed review showed were missing. |
| §9a — the round-1 verdict | **RETAINED** as history. Not re-argued, not weakened. |

**UNRESOLVED and reserved to the operator** — this record proposes, it does not decide:

1. the `docs/BLOCKED.md` compute-prohibition ruling (HIGH-STAKES, still `OPEN`);
2. the `C3` / `C9` contract consequence (`proposed/research_contract_C3_C9_amendment.md`);
3. `U08` — whether RT1's concordance failure is a limitation of the method or an independent
   recovery of a weakness the founding authors flagged;
4. `U01` — RT0's primary definitional source (Malik et al. 1999) is still unheld;
5. `U11` — the expression-tag offsets on 7 His6 / 1 SUMO / 3 thrombin / 1 Strep anchors, which
   gate the structural arm.

---

## 2 · The identifiability finding

Sixteen candidate `g4` outputs were classified separately in
`tables/estimand_matrix.tsv`. Summary:

| classification | quantities |
|---|---|
| `ESTABLISHABLE` | Q01 existence of conserved regions · Q02 region ordering · Q03 localization of the catalytic dyad · Q09 boundary **stability** interval · Q10 localization stability under perturbation · Q11 transferability to related sequences · Q12 transferability to identity-distant sequences |
| `PARTIALLY_ESTABLISHABLE` | Q04 region presence / non-detection (dyad region only) · Q05 approximate region location (only relative to the dyad, or as stability) · Q13 transferability to unseen families (measurable, but not as a held-out split) · Q14 structural correspondence (containment only, ≤25 structures) · Q15 presence calibration (dyad region only) |
| `UNESTABLISHED` | Q06 start accuracy · Q07 end accuracy · **Q08 full boundary accuracy** · **Q16 boundary calibration** |

Two declarations follow, and they are made **before** any method is chosen so that they cannot
later read as an excuse for one that failed:

    BOUNDARY_ACCURACY    = UNESTABLISHED
    BOUNDARY_CALIBRATION = UNESTABLISHED

The launcher's own `rt07_g4` kill criterion already contemplates landing with calibration
declared unestablished. This is a narrowing the launcher anticipated, not a new failure.

### Why boundary accuracy is unestablished

Not because a method failed — no method has been run. Because **no population supplies a true
region boundary**:

- the derivation bundle declares `edge_precision_claim = INTERVAL_ONLY` for all six regions,
  in its own words because *"the sources state a procedure and no residue edges"*;
- edge dispersion across the declared 150-setting sweep is 21–58 columns on starts and 3–72 on
  ends; the largest, 72 columns on region 4, exceeds the width of four of the six regions;
- Blocker's LtrA `M1–R85` / `R86–R364` are the edges of a **different two-way partition**, not
  per-region boundaries;
- PDB structures carry fingers/palm/thumb, a **different representation** that launcher §5d
  forbids using to manufacture the sequence partition;
- GOLD171 and the Stage-1 catalogue carry no boundary annotation of any kind.

A quantity with no truth source is not made estimable by choosing a better model.

### The one landmark that *is* independently determinable

The catalytic `[YF]xDD` dyad. Its position on any query sequence is fixed by that sequence's own
residues — no model, alignment or prior frame is required to locate it. `g2` located it at
`ALIGN_000044` column 783 / LtrA residue 306 **without using it to place any boundary**, and its
two declared positive controls (`C1`, `C2`) both passed.

This makes dyad containment a genuine held-out check, and it is the reason Q03 and Q15 are
identifiable at all — **conditional on one binding rule**:

> **Rule R-DYAD.** The catalytic motif may not enter the detector's derivation, its scoring
> function, its feature set, or any threshold selection. A method that uses the motif forfeits
> Q03 and Q15 entirely.

Without R-DYAD, dyad containment is a tautology. With it, it is the track's only non-circular
landmark truth.

---

## 3 · The revised scientific object of g4

> **A portable, reproducible operational coordinate system for the conserved RT core** —
> defined as the set of conserved positions reconstructed from the primary derivational
> alignment by the founding criterion, carried with **derivational stability intervals rather
> than exact edges** — **together with a measured statement of how far that coordinate system
> transfers across bacterial RT diversity.**

Binding consequences:

- **The region partition is not the target object.** `tables/g2_stability_decomposition.tsv`
  separates what g2 supports from what it does not: conserved-**position membership** is stable
  (81 vs 82 across independent frames; residue-shuffle null returns 0 in 200/200 replicates),
  while the region **count** is a free function of two merge parameters, ranges 5–16 across the
  declared sweep, differs between frames (6 vs 7), and never separates from a column-permutation
  null at any gap tested. Regions become a **declared reporting view** over the conserved-position
  set, carried with their ensemble. **Neither six nor seven is a finding.**
- **This is what dissolves the failed review's blocker 2.** The single g2 reporting point is no
  longer reified as target truth, because the target is no longer a partition.
- **Region 4 is named unstable in advance.** Cross-frame Jaccard 0.410; it splits into three;
  it is the entire source of the 6-vs-7 disagreement. Under `AC3` it carries no interval claim.
  This is recorded *before* execution so its failure cannot later be presented as a surprise.
- **The historical RT0–RT7 labels are a mapping layer**, with measured cardinality including
  non-correspondence (`tables/historical_to_operational_mapping_proposed.tsv`): RT0
  `NO_VALID_CORRESPONDENCE`; RT1 `UNRESOLVED`; RT2, RT3, RT7 `1:1` candidates; RT4 `1:many` and
  unstable; **RT5 and RT6 `many:1` onto one region**. Historical labels may not force, split or
  merge an operational region.
- **RT0 produces nothing.** No occupancy, no rate, no correspondence — `OUT_OF_FRAME` (`AC8`).
  That one conserved region falls inside Blocker's RT0 zone is consistent with conservation
  *within* this class and is **not** a recovery of RT0, whose defining claim is about what it is
  *not* conserved in.
- **RT1 is not rescued.** One preregistered rule applies to every region; no region-specific
  threshold, no post-hoc method choice (`AC9`). `U08` stays with the operator.

### Three representations, kept separate

**A. Operational conserved sequence regions** — from `ALIGN_000044` and the founding criterion.
**B. Historical RT0–RT7 terminology** — a mapping layer over A, with cardinality.
**C. Structural fingers/palm/thumb** — independent, Stage 04, and **used only after A is frozen**.

C may never define A and then be presented as A's independent validation. Launcher §5d already
forbids this; `tables/derivation_allowlist.tsv` makes it an asset-level rule.

---

## 4 · The four arms, by what each can actually test

`tables/evaluation_arms.tsv`. They are not all "validation" and are not named as if they were.

| arm | status | can test | cannot test |
|---|---|---|---|
| **A1** historical derivational, n=66 | **derivational — not a validation population** | existence, reference ordering, stability, the leave-one-out positive control | anything held out. A number computed here is self-consistency |
| **A2** PDB structures, **n ≤ 25** | **structural comparator** | whether the predicted dyad region lies in the palm; gross order correspondence | boundary truth of any kind |
| **A3** GOLD171 | **retron challenge population** | transfer within a retron lineage, in four strata | universal RT generalisation; and it is not a gold set |
| **A4** bounded Stage-1 sample, **max N 5,000** | **untouched evaluation** | ordered-architecture rate, dyad offset, call-state distribution, transferability by identity and by family | boundary accuracy; and family-held-out CV |

Three arm-level findings the previous design did not state:

1. **The PDB sequences are clean with respect to the *new* derivation.** The new substrate is
   `ALIGN_000044` alone, and only **one** of its 66 proteins is an old-seed member: `PDB_5G2X_3`
   — LtrA. The other 25 PDB anchors are absent from the derivation set. This is a real
   improvement the previous design could not claim. Their *selection* history remains
   structure-conditioned and 10 of 26 overlap the ph38 re-scan; both are reported, not argued
   away. **LtrA is excluded** because it is the coordinate carrier and cannot also be the test.
2. **There is nothing to hold out by family.** The derivation substrate is 66 group II intron
   ORFs in four lineage groups (mitochondrial 29, bacterial 20, algal/chloroplast 11, euglenoid 6)
   and contains **no Stage-1 family label at all**. Every Stage-1 family is out-of-family by
   construction, so no family-held-out cross-validation split exists to be defined. What is
   measurable is per-family transferability with the derivation composition stated beside it.
   The phrases `FAMILY_HELD_OUT` and "leave-family-out" are prohibited (`claim_vocabulary.tsv`).
3. **This makes non-transfer a live and admissible outcome.** A coordinate system derived on
   group II intron ORFs may transfer poorly to retrons and to distant families. Launcher §1 is
   explicit: *"Failure to transfer a block is a result, not a failed track."* The design is built
   to return that finding rather than to avoid it.

---

## 5 · Clean-room derivation allowlist

`tables/derivation_allowlist.tsv`, with columns `allowed_for_derivation`,
`allowed_for_threshold_selection`, `allowed_for_validation`, `allowed_as_comparator`, `reason`,
`circularity_risk`.

**Allowed for derivation** — `ALIGN_000044` and its 66 proteins; the Xiong & Eickbush stated
criterion; Zimmerly 2001's textual criteria; the g2 conserved-position set; the g2 sweep and the
MAFFT second frame **as the perturbation ensemble only**.

**Quarantined — comparator or audit only, never derivation, never threshold selection** —
`all167.faa`; all 72 anchors; CAND95; the prior palm-HMM frozen boundary coordinates; all 488
prior profile HMMs including `RT17_CORE`/`B_span17`; the prior 29-block frame table and its 24
`order_interpolated` blocks; structure-derived boundary products; myRT, Toro 2014, Toro 2026,
Mestre, SPIRE.

Three rules carry the weight:

- **the g2 reported six-region partition is itself quarantined for derivation.** Only the
  ensemble enters. This is the asset-level form of "do not reify the reporting point";
- **no asset plays conflicting derivation and independent-validation roles for the same
  estimand.** The one asset that would have — LtrA, simultaneously derivation member, coordinate
  carrier and PDB structure — is resolved by excluding it from A2;
- **Rule R-DYAD**, above.

---

## 6 · Bounded Stage-1 sampling frame, declared before any draw

`tables/bounded_sampling_plan.tsv`. Unit: exact RT. Frame: landed Stage-1 metadata only.

Inclusion `all_complete`, not clipped, no contig edge, length within 0.5–2.0× the family median
from `g4_completeness_by_family.tsv`. **The prior 200–900 aa window is deliberately not
inherited** — it came from the CAND95 recruitment gate, and importing it would import the old
seed's selection.

Exclusion: ≥90% identity **with ≥80% bidirectional coverage** to any of the 66 derivation
proteins — thresholds declared here, before any sample is drawn, and anchored on the **g2
derivation set rather than on all167**, which is failed-review repair 3. Old-seed neighbours are
additionally excluded, measured on sampled candidates only.

Family cap 120, floor "all where fewer than 30", MULTI as its own stratum. Computed from landed
tables: **4,809 across 41 family labels** before exclusions (40 families reach the cap;
RVT-AbiA contributes 9), plus ≤120 MULTI. **Hard ceiling max N = 5,000** — 0.997% of the
catalogue. Seed `20260916`.

**The entire Stage-1 sample is untouched evaluation.** No threshold, hyperparameter or method
choice is made on it; thresholds come from the derivation substrate and the negative controls
only. This removes the dev/test leakage question rather than managing it. A separate
`DEV_PILOT` of n=200 exists solely for throughput measurement and is permanently excluded from
the evaluation draw.

**Compute boundary.** Keys are drawn from metadata; sequences are extracted for sampled keys
only. No index is built over `rt_exact_v1.faa`; no search uses the full catalogue as target.
**This satisfies both readings of launcher §8 and does not depend on the open `BLOCKED`
ruling.** The recorded breach stays recorded.

---

## 7 · Statements superseded by this record

| superseded statement | where it came from | replacement |
|---|---|---|
| g4's object is a detector of the six reconstructed regions | prior record §5 | a coordinate system over the conserved-**position** set; regions are a declared view, and the count is not a finding |
| the 26 PDB anchors are an independent structural challenge arm | prior record §6.2 | **≤25** after excluding LtrA, and a **structural comparator**, not a held-out accuracy arm; tag offsets (`U11`) gate it |
| "boundary uncertainty" as a g4 deliverable | prior record §7 | `operational_boundary_stability_interval` — derivational dispersion, never a CI on a true boundary |
| "family-held-out transferability" | prior record §7; launcher §7c | `family_transferability`. There is no held-out split because the derivation set contains no Stage-1 family |
| "calibration claimed only on the population it was demonstrated on" | prior record §6 | correct as far as it goes, but insufficient: **no arm has boundary event labels**, so boundary calibration is `UNESTABLISHED` and presence calibration is confined to the dyad-carrying region |
| "phylogeny-ready core substrate" | prior record §7; launcher §7c | "**candidate** core substrate" |

---

## 8 · Non-goals and stop conditions

`g4` does not run the full catalogue, build a tree, settle the RT1 interpretation, or produce
any RT0 occupancy. No detector is implemented by *this* record at all.

**Stop and report** if: the leave-one-out positive control `AC1` fails (the instrument cannot
find the dyad on its own derivation substrate); the null control `AC2` fails (the instrument
cannot fail); the tag offsets `U11` cannot be resolved and the structural arm falls below a
usable n; any claim would need a denominator that does not exist; or any operation's cost would
scale with 501,561 rather than with the bounded N.

A `g4` that lands as *"the coordinate system is reproducible and stable on its derivation
substrate, transfers to X% of a bounded Stage-1 sample at identity distance D, and boundary
accuracy is unestablished"* is a **successful** gate under this design. So is one that lands
non-transfer. Negative and narrowed findings are results (`WA-G.5`).

---

## 9 · Reviewer verdict

Routed through ARIS's governed reviewer mechanism (`/auto-review-loop` conventions, backend
`codex`, reviewer `gpt-5.6-sol`, transition by `/home/borg/ARIS_CODE/tools/review_gate.py`;
positive requires **score ≥ 6 AND verdict ∈ {ready, almost}**). Round 2 of at most 4, continuing
the round-1 thread so the reviewer can check its own required repairs.

Verdict, per-check outcomes and repairs applied are recorded in `review-stage/AUTO_REVIEW.md`
and appended at §9a below. **No success criterion in this record may be weakened to obtain a
pass** (`WA-A.5`).
