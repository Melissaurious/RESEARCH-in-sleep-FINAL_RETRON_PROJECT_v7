# DECISION — g4a repaired; UG5 whole-family holdout executed and passed

Date: 2026-09-16 · Track: `rt07` · Status: **executed and reproducible; pending independent review**

Implements the seven required repairs from
`docs/decisions/2026-09-16_stage2_g4a_review_outcome_and_repairs.md` (review
`PASS_WITH_REQUIRED_REPAIRS`, 6/10) and executes the reviewer-mandated whole-family holdout gate
(`WHOLE_FAMILY_HOLDOUT: REQUIRED`, classification **B**).

Supersede this record by a new record, never by rewriting it.

Bundles: `results/rt07_g4a_repaired/` · `results/rt07_ug5_holdout_gate/`.

**g4b NOT STARTED. g5 BLOCKED. NO FULL-CATALOGUE APPLICATION.**

---

## 1 · The repair produced a finding larger than the defect

Enforcing the separation rule **directly** — all-vs-all identity plus bidirectional coverage,
connected components, whole components to roles — instead of inferring it from cd-hit membership,
showed that at `identity ≥ 0.30` / `min(coverage) ≥ 0.50`:

| family | components | largest | independent challenge set |
|---|---|---|---|
| DGRs | **1** | 488/488 (100%) | **NO** |
| UG3 | **1** | 86/86 (100%) | **NO** |
| GII | 2 | 495/496 (99.8%) | **NO** |
| CRISPR | 2 | 125/129 (96.9%) | **NO** |
| Retrons | 4 | 92/95 (96.8%) | **NO** |
| UG5 | 4 | 42/21/3/1 | **YES** |
| AbiA | 4 | 12/3/3/1 | **YES** |

**For five of seven families an independent within-family held-out set does not exist at any
defensible separation level.** The family is one homology component — which is, after all, what
makes it a family.

**The threshold was not lowered to manufacture a split.** Doing so would be exactly the
outcome-driven tuning this repair existed to remove. Those challenge sets are labelled
`NON_INDEPENDENT_CHALLENGE` and license no transfer claim; transfer is reported for **UG5 and AbiA
only**.

Measured max derivation↔challenge identity: **Retrons 0.797 · UG3 0.821 · DGRs 0.745 · GII 0.712 ·
CRISPR 0.654**, with 24–78 pairs ≥50% identity each. The original claim was comprehensively false.

**This sharpens the reviewer's mandate.** The UG5 gate is not the preferred transfer test — it is
the **only valid one available**.

## 2 · The seven repairs

1. **Split integrity** — enforced pairwise identity + bidirectional coverage; components, not
   cd-hit membership. `g4a_split_pairwise_audit.tsv` lands every near-threshold cross-role pair.
2. **Cap** — enforced at 90; the original violations (GII 111, DGRs 97) recorded, not redefined.
3. **Cluster diversity** — components per role landed; single-component roles flagged; no family
   forced.
4. **Contradictory dyad outputs purged** — the superseded match-state verdict is **not produced at
   all**; `g4a_repaired_dyad_correspondence_CANONICAL.tsv` is the sole canonical result. The
   per-sequence coordinate bug is fixed: each sequence's dyad maps through **its own** alignment row.
5. **Fail-closed** — every external call uses `check=True`; a missing hit lands an explicit
   `NO_HIT` row. Zero failures occurred.
6. **Aligner measure renamed** to `per_column_entropy_difference_MAFFT_vs_MUSCLE`, described as a
   method-sensitivity diagnostic, never as homology or coordinate-stability evidence.
7. **Summary numbers and denominators** — corrected, and both denominators always reported.
   `CLASS_LEVEL` → **`MULTI_FAMILY`**, `GLOBAL_CANDIDATE` → **`ALL_PARTNERS`**; no biological-class
   language, because no biological class was predefined or tested.

Plus: **parameter registry** with the five undeclared parameters classified, and a bounded
sensitivity sweep of the one genuinely scientific one — transitivity tolerance: pooled consistency
**82.5% at exact ±0**, 87.0 / 88.9 / 91.7 / 94.5% at ±1/±2/±3/±5. **The conclusion does not depend
on the ±2 choice.** The ≥20-position triple filter excludes **zero** of 210 triples and is inert.

And the **verifier is repaired**: it enforces registered input hashes, runs into a fresh temp dir,
diffs against frozen canonical outputs, exits non-zero on drift, and **never** writes into
`tables/`. Regeneration now lives in a separate `scripts/regenerate.sh`, so verification cannot
bless changed code. Result: *"OK: inputs authenticated and every computed table reproduced
byte-identically."*

## 3 · The qualitative conclusion survives

| | original | repaired |
|---|---|---|
| dyad correspondence | 42/42 | **42/42** |
| between-family correspondence | 42/42 | **42/42, 0 failures** |
| hhalign probability | 74.2–100.0 | **16.2–100.0** |
| best E-value | 2E-53 | **9.3E-78** |
| transitivity mean | 88.2% | **87.0%** |
| shared core, % of covered | 18.9–57.3% | **22.0–47.9%** |
| shared core, % of full consensus | *not reported* | **7.7–44.9%** |
| decoys | 0.0–4.3 | **SHUF 0.0–0.4 · REV 0.1–17.4** |

The one material change — minimum probability 74.2 → **16.2**, the pair being **UG5→AbiA** — is a
consequence of enforcing the cap and is the honest floor. The same asymmetry appears in transfer
(AbiA→UG5 median bit score **−1.5**). A real limit of the shared core, reported as such.

## 4 · UG5 whole-family holdout — PASSED

**24 of 24 construction inputs `UG5_GENEALOGY_PRESENT = FALSE`**, audited by file **content** for
UG5 ids *and* UG5 sequences — not by filename. Construction on six families with **UG3 retained**.
Frozen frame: **150 anchors** in GII coordinates, span 107–317, fixed before UG5 was examined.
UG5 split by whole components: evaluation-reference 42, challenge 25; max cross-subset identity
0.373 with **zero** link-rule violations.

| estimand | result |
|---|---|
| **A** anchor callability | **135/150 = 90.0%** (eval-ref 148/150 = 98.7%) |
| **B** ordering | **monotone YES**, every real target |
| **C** coordinate stability | **54** anchors map in every subset; mean range **14.72**, max 16 |
| **D** ambiguity | **0.0%** |
| **E** support | probability **97.3** / **97.9**; E 2.7E-11 / 5E-13 |
| **F** decoy separation | shuffled challenge **0/150 anchors, prob 0.0** |
| **G** challenge transfer | **90.0%** |

All six success criteria met — **with one limitation stated, not buried**: transfer is **not
uniform**. The large held-out component maps 90.0%; the 3-sequence component maps **36.0%**. The
predeclaration anticipated this: *"a smaller transferable intersection is a valid positive
outcome"*, and 54 anchors is that intersection.

## 5 · Audit trail

`results/rt07_g4a_repaired/control/EXECUTION_AUDIT.md`, six entries with all required fields:
**A1** the undisclosed cap violation — *the specific conduct the audit principle was written to
prevent*; **A2** within-family independence unachievable for five families; **A3** single-component
roles; **A4** row-order non-determinism caught by the new verifier; **A5** an appended audit row
destroyed by regeneration, prompting the move to an authored file; **A6** the correspondence
minimum moving to 16.2.

## 6 · Permitted claims

**Supported:** a compact shared RT core is recoverable de novo across the tested families ·
**whole-family transfer demonstrated to UG5** · the shared core is a minority of each family's
sequence · the catalytic dyad corresponds across all tested family pairs.

**Not supported:** any universal RT core · transfer to all unseen RT families · class-level frames
(no biological class was predefined) · any biological boundary, absence, family-assignment or
phylogenetic-eligibility claim · any within-family transfer claim for the five
`NON_INDEPENDENT_CHALLENGE` families.

## 7 · Reviewer

Routed to an independent non-Claude-family reviewer. **g4b does not begin on this session's
judgement**; `g5` remains blocked until the mapper is frozen and reviewed.
