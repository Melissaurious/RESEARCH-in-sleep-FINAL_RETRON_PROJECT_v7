# PROPOSED minimal launcher diff — `launchers/LAUNCHER_02_rt0_rt7_definition.md`

**NOT APPLIED.** This file records what the redesign would change in the launcher if the
independent reviewer passes it and the operator accepts. The launcher is not in this track's
write boundary (§9c lists `ARIS_OUTPUT/02_rt0_rt7_definition/`, `results/rt07_*/`,
`data/derived/` and `docs/decisions/`), and §9b reserves changing the scientific question to
the operator. Nothing below has been written into the launcher.

Five changes. Each names the evidence that forces it.

---

## 1 · §7, the `rt07_g4_operational_boundary_model` row — the ONE measurement

**Current** (in part): *"per-region detector performance across four separately reported
validation arms … with detection evidence, boundary uncertainty and out-of-distribution
context kept as separate quantities, and calibration claimed only on the population it was
demonstrated on."*

**Proposed**: replace "detector performance" and "boundary uncertainty" with the identifiable
quantities, and move the two unestablished ones into the row itself so they are declared
before execution rather than discovered after it:

> per-region **localization and transferability** across four arms of **explicitly different
> epistemic status** — derivational (A1), structural comparator (A2, ≤25 after excluding
> LtrA), retron literature challenge (A3) and a bounded Stage-1 transfer sample (A4) —
> reporting landmark localization offset against the catalytic dyad, ordered-architecture
> recovery rate, region-interval stability across a declared perturbation ensemble, and
> call-state distribution with inspectability retained. **`BOUNDARY_ACCURACY` and
> `BOUNDARY_CALIBRATION` are declared `UNESTABLISHED` at the outset**; presence calibration is
> claimed only for the dyad-carrying region on the population it was demonstrated on.

**Why**: `estimand_matrix.tsv` Q06–Q08 and Q16. No population supplies true region boundaries,
and the derivation bundle itself declares `edge_precision_claim = INTERVAL_ONLY` for all six
regions. The launcher's own `rt07_g4` kill criterion already contemplates landing with
calibration unestablished, so this is a narrowing the launcher anticipated.

**Also add to the row**: the detector object is a **portable operational coordinate system for
the conserved RT core** — the conserved-position set plus a declared region-grouping *view*
carried with its ensemble — **not** a fixed partition at six, seven or any other number.

**Why**: `g2_stability_decomposition.tsv`. Conserved-position membership is stable (81 vs 82
across independent frames, residue-shuffle null returns 0 in 200/200 replicates); the region
*count* is a free function of two merge parameters, ranges 5–16 across the declared sweep, and
never separates from a column-permutation null at any gap tested.

---

## 2 · §7c, reusable datasets — three renames and three additions

| current | proposed | why |
|---|---|---|
| `boundary_uncertainty.tsv` | `region_stability_intervals.tsv` | the quantity is derivational dispersion, not uncertainty about a true boundary (Q09) |
| `family_holdout_or_transferability.tsv` | `family_transferability.tsv` | there is no held-out split: the derivation substrate is 66 group II intron ORFs and contains **no Stage-1 family**, so every family is out-of-family by construction and nothing can be held out (Q13) |
| "phylogeny-ready core substrate" | "**candidate** core substrate" | failed-review repair 15; orthology, recombination, homologous-column, masking, missingness and compositional checks are unspecified |

Add to the `g4` product list: `estimand_matrix.tsv`, `derivation_allowlist.tsv`,
`claim_vocabulary.tsv`. Add to `calibration.tsv` a mandatory `scope` and `estimand` column so a
calibration row cannot exist without naming what event it calibrates.

---

## 3 · §8, compute — the open governance question

`docs/BLOCKED.md` (2026-09-16) records an unresolved HIGH-STAKES item: whether *"No full
501,561-sequence pass runs during planning, and none runs in `g1`–`g4`"* covers using the
catalogue as a **search target** for a bounded query set, or only catalogue-scale
*scoring/annotation*.

**This redesign does not depend on the ruling.** `bounded_sampling_plan.tsv` draws keys from
the landed metadata tables and extracts sequences for sampled keys only — it builds no index
over `rt_exact_v1.faa` and issues no search against the full catalogue — so it satisfies both
readings.

**Proposed §8 wording, for the operator to accept or reject** (not applied):

> No catalogue-scale pass runs during planning or in `g1`–`g4`. "Catalogue-scale" means
> scoring, annotating or building a persistent index over the full 501,561-sequence set. A
> bounded key draw from landed Stage-1 metadata, and sequence extraction for the drawn keys
> only, is permitted and is not a catalogue-scale pass. Any operation whose cost scales with
> 501,561 rather than with the bounded N stops for an operator decision.

The already-executed breach stays recorded in `docs/BLOCKED.md` either way. Under this wording
it remains a breach of the *prior* text, narrowed going forward — it is not retroactively
excused.

---

## 4 · §2, the `rt07_g4` kill criterion — no change, one pointer

Current text already reads: *"if no validation population can be constructed whose seed overlap
is measured and materially below the prior `anchors72` state, the detector lands with
**calibration declared unestablished** and `g5`/`g6` report call states without accuracy
claims."*

**Proposed**: leave it, and add one clause so the criterion covers the case that actually
obtains — the problem is not seed overlap, it is that no arm supplies boundary truth at all:

> … **or if no arm supplies independent truth for the quantity the detector predicts**, the
> detector lands with boundary accuracy and calibration declared unestablished …

---

## 5 · §7a, call-state vocabulary — no change

`PRESENT_HIGH_CONF`, `PRESENT_LOW_CONF`, `NOT_DETECTED_INSPECTABLE`, `UNINSPECTABLE_PARTIAL`,
`AMBIGUOUS`, `OUT_OF_FRAME` all survive the redesign unchanged and are what the detector emits.
`OUT_OF_FRAME` is what carries RT0 (`AC8`).
