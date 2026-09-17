# Execution audit — deviations surfaced during the repair, in an AUTHORED file

`tables/g4a_repair_audit.tsv` is **regenerated** by `step1_split.py`, so anything appended to it by
hand is destroyed on the next run. This file is authored and is never regenerated. Both are listed
in `control/AUTHORED_TABLES.txt` where applicable.

Every row carries the six fields the audit principle requires.

---

## A1 · Pilot-cap violation in the ORIGINAL bundle (GII, DGRs)

- **expected:** pilot_N ≤ 90 per family, per the original predeclaration
- **observed:** **GII = 111**, **DGRs = 97**
- **when_detected:** visible in the original bundle's first pipeline run; **not disclosed then**;
  re-detected and surfaced at repair time
- **scientific_effect:** the derivation, development and challenge populations for those two
  families differed from the declared design, so every per-family statistic computed on them was
  computed on an undeclared population
- **repair:** components are dealt only while the family total stays ≤ 90; a component that would
  overshoot is skipped. The declaration was **not** retroactively redefined
- **results_before_repair_invalidated:** **YES** for GII's and DGRs' per-family statistics

> The failure to disclose this at the time is the specific conduct the operator's audit principle
> was written to prevent. It is recorded here rather than absorbed into the repaired numbers.

## A2 · Within-family independence is unachievable for 5 of 7 families

- **Note, errata A9:** the phrase "at any defensible separation level" below is WITHDRAWN. At identity 0.50 the families do fragment (largest GII 98, DGRs 104, CRISPR 15, UG3 5, Retrons 6). The supportable wording is "at the declared 0.30 / 0.50 rule".

- **expected:** each family fragments into ≥2 separation components, so an independent
  within-family challenge set exists
- **observed:** at `identity ≥ 0.30` and `min(coverage) ≥ 0.50` —
  **DGRs 1 component (488/488)**, **UG3 1 (86/86)**, **GII 2 (495/496)**, **CRISPR 2 (125/129)**,
  **Retrons 4 (92/95)** *(CORRECTED 2026-09-16, errata A9: the mmseqs `sp|` prefix bug created a phantom singleton; the verified structure is 3 components, largest 93)*. Only **UG5** (42/21/3/1) and **AbiA** (12/3/3/1) fragment
- **when_detected:** repaired split, **before any repaired analysis was interpreted**
- **scientific_effect:** for those five families **no independent within-family held-out set exists
  at any defensible separation level**; the original bundle's holdout-integrity claim is false, and
  any within-family transfer or generalisation claim for them is unsupportable
- **repair:** `PREDECLARATION_ADDENDUM_1` — threshold **not** lowered; derivation drawn
  deterministically from the dominant component; remainder labelled `NON_INDEPENDENT_CHALLENGE`;
  transfer reported only for `INDEPENDENT_CHALLENGE` families
- **results_before_repair_invalidated:** **YES** for the original within-family transfer and
  holdout claims

Measured maximum derivation↔challenge identity in the repaired split: Retrons 0.797, DGRs 0.745,
GII 0.712, CRISPR 0.654, UG3 0.821 — with 24–78 pairs at or above 50% identity per family.
UG5 0.373 and AbiA 0.538 with **zero** rule violations.

## A3 · Single-component roles where a family did fragment

- **expected:** >1 independent component per role
- **observed:** `UG5.derivation`, `UG5.challenge`, `AbiA.derivation` are each one component
- **when_detected:** repaired split
- **scientific_effect:** those roles do not represent diverse held-out sequence structure
- **repair:** reported and flagged; the split is **not** forced
- **results_before_repair_invalidated:** **NO** — the role is retained, its diversity claim downgraded

## A4 · Row-order non-determinism, caught by the repaired verifier on its first use

- **expected:** byte-identical reproduction of every computed table
- **observed:** `g4a_split_pairwise_audit.tsv` reproduced with **identical rows in a different
  order**
- **when_detected:** first run of the repaired verifier, before the bundle was frozen
- **scientific_effect:** **none on any measurement** — the row set and every value were identical.
  The sort key `(family, −identity)` has ties and mmseqs row order is not stable
- **repair:** sort key made **total** by appending `query_id` and `reference_id`
- **results_before_repair_invalidated:** **NO** — no value changed

> The previous bundle's `tee`-based harness could not have detected this.

## A5 · An appended audit row was destroyed by regeneration

- **expected:** an audit row appended to `tables/g4a_repair_audit.tsv` persists
- **observed:** it was **overwritten** — `step1_split.py` rewrites that table wholesale
- **when_detected:** immediately after `regenerate.sh` ran
- **scientific_effect:** none on measurements, but an audit trail that a rerun silently erases is
  not an audit trail
- **repair:** execution-level audit items moved to **this authored file**, which no script
  regenerates. `tables/g4a_repair_audit.tsv` now holds only the rows the pipeline itself emits
- **results_before_repair_invalidated:** **NO**

## A6 · Minimum correspondence probability moved after repair

- **expected:** correspondence comparable to the original (74.2–100.0)
- **observed:** **16.2–100.0**; the weak pair is **UG5 → AbiA (16.2)**, reciprocal AbiA → UG5 69.2
- **when_detected:** repaired step 2
- **scientific_effect:** the two smallest, most divergent families correspond weakly and
  asymmetrically. The same asymmetry appears in transfer (AbiA→UG5 median bit score −1.5, 5/21
  detected). This is a **real limit of the shared core**, not a processing artefact
- **repair:** none — it is a result. The original 74.2 floor was computed on cap-violating
  populations; the repaired floor is the honest one
- **results_before_repair_invalidated:** the original probability *range* is superseded
