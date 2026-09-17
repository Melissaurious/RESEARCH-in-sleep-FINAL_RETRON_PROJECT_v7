# g4b PACKAGING REVIEW — did operationalisation change the science?

**This is NOT a review of mapper universality, generalisation or transfer.** That question is
closed. Stage-2 validation ended at Endpoint A
(`docs/decisions/2026-09-17_stage2_ug25_confirmatory_closed.md`): UG25 confirmatory transfer
`SUPPORTED`, post-run review `PASS_WITH_REQUIRED_REPAIRS` 7/10, remaining repairs documentary.
**Please do not reopen it, and please do not propose new validation families, thresholds,
controls or holdouts.** A recommendation to do so is out of scope and will not be actioned.

g4b froze the already-validated mapper as a production instrument. Your job is to confirm the
packaging is faithful, deterministic and honest — or to name precisely where it is not.

```
G4B BUNDLE   : results/rt07_g4b_production_mapper/
               root 88425986c144bb5e41b9f6a05913f998b72115f8a59367f4db40bdbe70ecc86e  (35 files)
manifest     : review-stage/manifests/RT07_G4B.MANIFEST
pinned root  : review-stage/roots/RT07_G4B.root          (both OUTSIDE the bundle)

verify freeze : python3 results/rt07_g4b_production_mapper/code/freeze.py verify \
                  results/rt07_g4b_production_mapper \
                  review-stage/manifests/RT07_G4B.MANIFEST "$(cat review-stage/roots/RT07_G4B.root)"
verify bundle : bash results/rt07_g4b_production_mapper/verify.sh
```

Reference bundles, unchanged and read-only:
`results/FINAL_PRE_UG25_VALIDATION_BUNDLE/` (root `fc9cde03…`),
`results/rt07_ug25_confirmatory/` (root `6bf14eb4…`).

---

## 1 · What g4b claims

1. `code/rtmap/mapper.py` is the frozen mapper, **byte-identical**, sha256
   `69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef`.
2. Every frozen parameter is **read from** the frozen control tables, not restated:
   `PP_HI` 0.75, `PP_LO` 0.50, `S_MIN` 10, `K_MIN` 30, `T1` 0.32, `D_MAX` 0.48,
   `D_RANDOM` 0.067, `CAT_STATE` 262, 150 anchors, `hhmake -M 50`.
3. Production output reproduces the landed frozen results **exactly** on sequences whose
   answers are already on record.
4. Output is deterministic and independent of shard/batch geometry.
5. The four per-state call states are preserved and never collapsed.
6. Historical RT0–RT7 is a separate crosswalk, `UNRESOLVED` in every row.
7. Stage-1 tool labels are documented as strata, never validation truth.
8. `NO_SUPPORTED_MAPPING` and `DELETED_STATE` are documented as not biological absence.

## 2 · Evidence offered

**Ten freeze tests** (`tests/test_production_freeze.py`), including negative tests: a retuned
`PP_HI` in a copied control table is rejected at import; an appended byte in `mapper.py` is
rejected before any record is emitted; a changed threshold, mapper, profile or anchor set each
changes the compact instrument identifier.

**Seven smoke checks** (`smoke/check_smoke.py`), on 18 construction sequences the instrument
has already seen plus five planted invalid/duplicate records. **UG25 is not touched.**

* **S1** — per-sequence anchor counts, verdict, reason, catalytic class and domain bitscore
  equal the values landed in
  `FINAL_PRE_UG25_VALIDATION_BUNDLE/tables/construction_validation_sequence.tsv`. 18/18.
* **S2** — 2850 per-state calls identical to `state_to_residue` imported directly from the
  frozen bundle.
* **S3** — byte-identical rerun.
* **S4** — batch size 1 vs default agree on every scientific column, domain scores included.
* **S5** — all four call states reachable, no fifth value, 150 anchor rows per sequence.
* **S6** — every `INPUT_INVALID` reason reachable; no engineering-failure status leaks into
  `sequences.tsv`.
* **S7** — deduplication by `rt_hash` with per-identifier rows preserved.

## 3 · TWO PACKAGING REPAIRS — please scrutinise these hardest

Both were found by running the packaging at 560 sequences rather than 19. Both concern
`hmmsearch`, whose E-values scale with database size and whose default reporting threshold is
an E-value.

* **P1** — the reported domain E-value moved with shard size (same sequence: `2.1e-130` at
  shard 100, `1.2e-129` at shard 1000).
* **P2** — whether a marginal domain was reported **at all** moved with shard size
  (`YP_217686.1_Retrons`: bitscore −0.6 at shard 100, absent at shard 1000). That sequence's
  verdict does not move, because `classify_sequence` treats "no domain reported" and
  "bitscore < `S_MIN`" identically. The executor judged the hazard to generalise the wrong
  way: at Stage-1 shard sizes, a sequence with bitscore at or just above `S_MIN` = 10 could
  fall below the E-value reporting threshold purely because its shard was large.

**Repair:** production scores domains **one sequence at a time** (database size 1), so
bitscore and E-value are properties of the sequence alone, and no sequence can lose a reported
domain because of its neighbours.

**Executor's own test of the worst case, landed at
`tables/g4b_domain_scoring_repair_evidence.tsv`:** over the complete 219-sequence
construction population, batched (one call per family of 40, the frozen pipeline's own
geometry) against per-sequence — 219/219 reported in both arms, **0** reported only
per-sequence, **0** reported only batched, **0** bitscore differences, **0**
qualifying-domain verdict flips. Narrowest margin in the population:
`CBK99617.1_Retrons` at bitscore **10.3** against `S_MIN` = 10.

**Please check each of these specifically:**

* a. Is the repair genuinely packaging, or is it a change to the scientific instrument? The
  executor's argument: `domain_scores` is the frozen function called with a one-sequence
  FASTA; bit scores are database-size independent (measured: 0 differences over 120
  construction sequences); the landed construction run reported a domain for all 219
  sequences including both abstainers (1.9 and 7.3), so nothing on the calibration population
  moves — S1 confirms this sequence by sequence.
* b. Is the executor's claim that the repair is **strictly more inclusive** correct?
* c. Is P2 correctly characterised — is there a case where the *old* batched behaviour and the
  *new* per-sequence behaviour give different **verdicts** on the construction or UG25
  populations? If so, the executor has misreported the repair's impact.
* d. Alignment remains batched, on the argument that `hmmalign` scores each sequence
  independently. Is the empirical evidence (byte-identical `states.tsv` at batch 1/100/500/1000)
  sufficient, or is there a batch-composition dependence it would miss?

## 4 · Documentary errata landed, not rewritten

U1 `DELETED_STATE` was **26.9 %**, not "roughly half"; U2 the C7 gate *does* restate five
constants, each matching the predeclaration exactly — inaccurate provenance wording, not
tuning; U3 post-run root verification was run manually, not from inside the runner.
`UG25_RESULT.md` is **not** edited. Please confirm these are recorded honestly and that none
of them silently reinterprets the result.

## 5 · What to return

A verdict on **packaging only**:

1. Is `mapper.py` byte-identical and are all frozen parameters unchanged?
2. Does the schema preserve every required state and field, without collapsing call states or
   pooling the anchor and catalytic denominators?
3. Is provenance sufficient to trace a g5 record to its exact instrument?
4. Is production packaging deterministic, and is shard/batch geometry genuinely unable to move
   a result?
5. Does the smoke test reproduce expected mapper behaviour, and is it correctly framed as
   engineering rather than validation?
6. Did any accidental threshold, method or scope drift occur — including in the two repairs?
7. Is the historical RT0–RT7 crosswalk properly separated and honestly `UNRESOLVED`?
8. Are the g5/g6/g7 plans free of scope creep, and is the g5 compute estimate honestly derived
   from the measured smoke test (13.8 ms/sequence, 560 sequences, single core)?
9. **May g5 begin?**

Please also state plainly anything the executor has overclaimed.
