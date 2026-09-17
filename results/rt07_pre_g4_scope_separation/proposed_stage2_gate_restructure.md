# PROPOSED Stage-2 gate restructure

**Assessment of whether the 2A / 2B / 2C / 2D decomposition is scientifically correct, and the
minimum launcher change it needs. Not implemented. Not applied.**

---

## 1 · Verdict on the proposed decomposition

**The decomposition is correct, with one modification and one addition.**

It is correct because it cuts along the line the evidence actually draws: `ALIGN_000044` is a
single-RT-class historical artefact and cannot carry a general instrument, while the broad
material that could carry one (myRT) cannot address RT0 and cannot validate family labels. Those
are different objects with different substrates, different estimands and different failure modes.
Two design reviews failed because one gate was asked to be both.

### Modification — 2C is not a separate gate

Crosswalk against historical landmarks is not separable from the instrument that produces the
coordinates: the crosswalk is how the instrument's output is *read*, and it needs the same frozen
coordinates, the same stability ensemble and the same claim vocabulary. Splitting it invites the
frozen instrument to be quietly re-tuned to improve the crosswalk.

**Proposal:** historical crosswalk lands *inside* 2B as a mapping layer, produced after the
instrument is frozen and before any catalogue application. **Structural and published-comparator
crosswalk stays separate** — it is genuinely orthogonal, needs structures rather than sequences,
and is already the existing `g7`.

### Addition — a reference-design gate must precede 2B

The single largest defect in both failed rounds was that the derivation population was assumed
rather than designed. The reference panel — which families, what cap, what redundancy reduction,
full-length or fragment, what is held out — is itself a measurement with an auditable answer, and
it must land and be reviewed **before** any instrument is derived. Otherwise the panel gets
chosen to make the instrument look good.

## 2 · The proposed structure

| id | gate | the ONE measurement | substrate | status |
|---|---|---|---|---|
| **2A** | `g1`, `g2`, `g3` | historical RT0–RT7 reconstruction and prior-method replication | `ALIGN_000044`, 66 records / 65 unique | **LANDED. Closed. Not reopened.** |
| **2B-0** | `g4a_reference_design` | the composition of a broad RT reference panel: families, caps, redundancy reduction, full-length eligibility, held-out classes, and the measured diversity actually available | myRT `RTs-collection.faa` + family seeds + `.sto` alignments | NEW — must land and be reviewed before 2B-1 |
| **2B-1** | `g4b_operational_core_coordinates` | reproducibility and class-transfer of a broad-RT homologous core coordinate mapper, with the historical crosswalk as a mapping layer over its frozen output | the 2B-0 panel | NEW — replaces the failed `g4` |
| **2C** | `g7` *(existing)* | agreement and disagreement against structures, Simon & Zimmerly's mapping, Toro 2014, Mestre, myRT, Toro 2026 | 39 local PDB entries + published comparators | EXISTS in the launcher; unchanged in scope |
| **2D** | `g5`, `g6` *(existing)* | catalogue application and per-family architecture, retrons as a focal stratum | bounded Stage-1 sample, then catalogue | EXISTS; gated on 2B-1 freezing |

`g4` as currently written is **withdrawn and replaced by `g4a` + `g4b`**. Nothing else in the
launcher's gate list changes.

## 3 · Why 2A is closed rather than deleted

`g1`–`g3` answer a well-posed question on the correct substrate and their results are reproducible
and landed. They become the **comparator layer** that prevents historical terminology being
mistaken for modern ground truth — which is a live risk precisely because 2B will produce a
coordinate system that people will want to label RT1–RT7.

2A's binding outputs for 2B: RT0 is `OUT_OF_FRAME`; RT5 and RT6 share one region; the seven-way
partition is unsupported; RT1 is unresolved; region counts are free parameters.

## 4 · The minimum launcher change

Four edits. The full text is in `proposed/LAUNCHER_02_diff.md`.

1. **§5d — the tier table.** The blocking change. Add a column distinguishing *may seed the
   historical reconstruction* from *may seed a broad operational instrument*. Without this, §5d's
   "published comparators … must never seed the reconstructed frame" forbids the only broad
   material that exists and Stage 2B cannot be built at all.
2. **§7 — the gate table.** Replace the `rt07_g4_operational_boundary_model` row with `g4a` and
   `g4b`.
3. **§4 — inputs and trust grades.** Register the myRT distribution objects at
   `/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/` with grades. Currently only the
   `references/rt0_rt7/myrt/` copy is registered, which is the reference *package* — the 1,844
   fragments — not the 45 family seed sets or the 2,339 full-length collection.
4. **§1 — the success criterion.** Criterion 2 requires "an operational per-block detector …
   derived on a conservative full-length set". Both halves need amending: "per-block" presumes the
   partition, and "conservative full-length set" was read as the historical substrate.

## 5 · What does not change

- The call-state vocabulary (§7a) — it already carries exactly the distinctions 2B needs, and
  `OUT_OF_FRAME` is what carries RT0.
- The compute rules (§8) and the bounded-sampling discipline landed in the previous round.
- `BOUNDARY_ACCURACY` and `BOUNDARY_CALIBRATION` remain `UNESTABLISHED`. Nothing in the broader
  reference design creates boundary truth; it creates **class-transfer testability**, which is a
  different and genuinely new capability.
- The prohibition on RT0 occupancy, on seven forced classes, and on tuning to rescue RT1.

## 6 · What this restructure does and does not buy

**Buys:** class-level held-out evaluation becomes possible for the first time — a 45-family panel
can hold out whole families, which a single-class 66-sequence substrate never could. That converts
`E05` transfer-across-RT-classes from untestable to `ESTABLISHABLE`, and makes the intended
downstream comparisons (occupancy by class, retrons against GII/DGR/Abi/CRISPR/UG) coherent for
the first time.

**Does not buy:** boundary truth, family-assignment truth, RT0, or phylogenetic eligibility. All
four remain `UNESTABLISHED` and the estimand matrix says so.
