# UG5 gate v2 — STOP CONDITION TRIGGERED

`PREDECLARATION_ADDENDUM_2 §9`: *if any repair materially changes the currently supported
scientific conclusion, work stops and returns to the operator before the review is requested.*

**It does. Work is stopped. No independent review was requested.**

---

## 1 · What changed

The reviewer's objection was that the v1 gate's monotone-order and zero-ambiguity results were
*"largely guaranteed by the one-to-one, order-preserving pairwise-alignment map"* — i.e.
tautological. The per-sequence rework makes both falsifiable, because `hmmsearch` against an
individual sequence **can** emit out-of-order, duplicated or missing anchors.

Made falsifiable, **they fail.**

| criterion | v1 (aggregate profile) | v2 (per sequence) |
|---|---|---|
| anchor placement | **90.0%** (135/150) | **median 89/150 = 59.3%**; IQR 56–101; min 34, max 128 |
| anchor order | **monotone YES**, all targets | **31 of 67 monotone — 46.3%**; 36 sequences show 1–8 inversions |
| ambiguity | **0.0%** | 2 sequences with **29** and **38** ambiguous anchors |
| decoy separation | 0/150, prob 0.0 | median **0.0%** across 3 replicates — but **max 117 / 67 / 150 anchors** |
| abstention | not measured | **0** sequences abstained |

Per component, including the singleton the v1 gate omitted:

| component | subset | n | median % placed | monotone | dyad within anchors |
|---|---|---|---|---|---|
| 0 | evaluation_reference | 42 | 59.0% | 15/42 | 38/42 |
| 1 | challenge | 21 | 57.3% | 13/21 | 19/21 |
| 2 | challenge | 3 | 70.0% | 2/3 | 3/3 |
| 3 | challenge (singleton) | 1 | 74.7% | 1/1 | 1/1 |

Note the v1 claim that the 3-sequence component transferred poorly (36.0%) does **not** hold
per-sequence — components 2 and 3 place *more* anchors than the large ones. The v1 component
asymmetry was an artefact of aggregate-profile construction on tiny alignments.

## 2 · A weakness in the v2 placement rule itself, surfaced not hidden

The decoy **median is 0.0%** — decisive — but the **maximum reaches 150 anchors**. Inspection of a
surviving decoy domain table shows the cause: the placement rule marks an anchor as placed if **any**
hit envelope spans its HMM coordinate, **with no score filter at all**. A single spurious envelope
(observed score **−2.8**, i-Evalue 0.1) therefore "places" every anchor it covers.

So the decoy tail overlaps the real range for a reason that is **my rule's fault, not the data's**.
A defensible v3 would require a per-anchor score or posterior threshold rather than envelope
coverage — but choosing that threshold *after* seeing these results would be exactly the
outcome-driven tuning this whole repair cycle exists to eliminate. **It is therefore not done here,
and the operator is asked to authorise a predeclared placement rule instead.**

A second, smaller defect: the decoy loop reuses one filename per replicate, so only the last
sequence's intermediate survives for inspection. Counts were taken inside the loop and are valid;
post-hoc per-sequence decoy inspection is not possible. Recorded.

## 3 · What is NOT affected

The **g4a** conclusions are untouched by this and survive repairs 1–3 intact: dyad **42/42**,
correspondence **42/42**, transitivity ~87%, shared core a minority. The two verified g4a bugs are
fixed and confirmed — Retrons is now **93/1/1**, and the `LENG` denominator gives **7.5–27.5%**,
matching the reviewer's independent computation exactly.

The **holdout remains genuine**: 24/24 construction inputs `UG5_GENEALOGY_PRESENT = FALSE`, and
the frozen 150 anchors (11 contiguous runs, span 107–317) are now fully landed.

## 4 · What is now supportable about UG5, and what is not

**Supportable:** a frame derived without any UG5 information places a **median 59%** of its anchors
on individual UG5 sequences, with the catalytic dyad falling inside the placed span in **61 of 67**
sequences, against a decoy median of **0%**.

**No longer supportable:** *"anchor order is coherent"* (fails for 54% of sequences) ·
*"zero ambiguity"* · *"90% callability"* · *"all six success criteria met"* · and therefore
**the v1 statement that the UG5 gate passed.**

## 5 · Consequence

`ug5_transfer_summary.md` and `docs/decisions/2026-09-16_stage2_g4a_repair_and_ug5_gate.md` §4
are **superseded** on the UG5 result. They are not rewritten; this file and the accompanying
decision record carry the correction.

**The mapper cannot be frozen on this evidence.** The gate's own predeclared criterion 2 — *anchor
order is coherent* — is not met under non-tautological measurement.
