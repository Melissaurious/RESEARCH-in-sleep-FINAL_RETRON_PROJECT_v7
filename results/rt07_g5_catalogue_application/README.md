# rt07_g5_catalogue_application

STATUS: VERIFIED — `verify.sh` re-checks the landed dataset: the instrument is still
canonical, every dataset file still hashes to its manifest entry, the 512-shard manifest sums
exactly to the frozen census, and every QC table regenerates byte-identically from the landed
parquet. `g5 VERIFY OK`.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

    n_attempted:  369381   the censused eligible population — G5_ELIGIBLE_N
    n_succeeded:  369381   produced a full scientific row
    n_dropped:         0   0 tool failures, 0 invalid inputs at run time

Weight **FULL** (launcher §7, `rt07_g5_catalogue_application`). The measurement is the
per-state call-state distribution over the eligible Stage-1 exact-RT catalogue, with family,
MULTI and completeness strata retained.

---

## 1 · What was run

The **frozen** production mapper `rtmap-1.0.0/53a1e738a19b3896` was applied, unchanged, to
every sequence in the censused eligible population. Nothing was retuned, no threshold moved,
no validation family was added, and no tool label entered the inference.

| | |
|---|---|
| instrument | `rtmap-1.0.0/53a1e738a19b3896` |
| instrument sha256 | `53a1e738a19b38967563b4f4d733047b26123f754a7d592fd0186e7bd9c331f5` |
| mapper code | `69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef` |
| profile | `GII.deriv.hmm`, LENG 471, `hhmake -M 50` |
| schema | `rtmap-schema-1.0` |
| bundle root verified on every shard | `0b025cbab192f64d05ef0a9aff47859b998fe3158dc0199cd47cbbd040620d3f` |
| shards | 512, 44 in parallel, one 48-core host, CPU only |
| wall | 244.8 s mapping + 365 s verify/merge |
| shard failures | **0** |

`preflight.py` verified the instrument field by field — version, sha256, mapper hash, schema,
profile hash and LENG, anchor set, `CAT_STATE` 262, all eight calibrated parameters, HMMER
version, domain-scoring protocol — and would have stopped the run on any difference. It then
ran a production shard and confirmed schema, exact row counts, 150 state rows per sequence,
catalytic fields, deterministic rerun and batch-size independence.

## 2 · Population and reconciliation

| | n |
|---|---|
| Stage-1 exact RT catalogue | 501,561 |
| ineligible (censused, retained) | 132,180 |
| **ELIGIBLE — the g5 denominator** | **369,381** |
| processed | 369,381 |
| state rows | 55,407,150 = 369,381 × 150 |

    369,381 identifiers, each appearing exactly once
    0 duplicated · 0 missing · 0 unexpected

Asserted in `merge.py`, not merely reported, before a single row was written. The eligibility
rule was applied **once**, in `rt07_g5a_eligibility_census`; this stage reads that partition
and cannot disagree with it.

## 3 · Application QC — descriptive only

| | n | fraction of ELIGIBLE |
|---|---|---|
| `MAPPABLE` | 341,335 | 0.9241 |
| `PARTIAL_MAPPING` | 12,767 | 0.0346 |
| `AMBIGUOUS_MAPPING` | 6,455 | 0.0175 |
| `NO_SUPPORTED_MAPPING` | 8,824 | 0.0239 |
| **INSPECTABLE** (verdict `MAPPED`) | **354,102** | **0.9586** |
| abstained | 15,279 | 0.0414 |
| tool failures | **0** | — |

Median MAPPED fraction 0.8267 over ELIGIBLE, 0.8400 over INSPECTABLE. Full distributions of
all four call-state fractions: `tables/g5_qc_call_fraction_distributions.tsv`.

**Catalytic, on its own denominator** — `CAT_STATE` 262 is not one of the 150 anchors and is
never pooled with them: MAPPED in 356,229 (0.9644 of ELIGIBLE); `CATALYTIC_CONFIRMED` in
343,880, which is 0.9310 of ELIGIBLE and **0.9653 of CAT-MAPPED**. "Confirmed" means motif
concordance at a state, not independent residue truth.

## 4 · The canonical dataset — `data/derived/rt07_g5/`

| file | rows | bytes |
|---|---|---|
| `g5_sequences.parquet` | 369,381 | 41,842,661 |
| `g5_states.parquet` | 55,407,150 | 108,189,029 |
| `g5_catalytic.parquet` | 369,381 | 26,660,834 |
| `g5_ineligible.parquet` | 132,180 | 10,192,406 |
| `g5_run_failures.parquet` | 0 | 4,177 |
| `g5_metadata_crosswalk.parquet` | 501,561 | 56,149,583 |

Gitignored by project convention (`data/*`); every file is hashed in
`tables/g5_dataset_manifest.tsv` and in `PROVENANCE.md`. All joins are on `rt_hash`. The
crosswalk covers the **whole** catalogue with an `in_g5_eligible` flag, so g6 can take any
denominator without re-deriving eligibility.

Per-shard TSV outputs (~12 GB) remain in `ARIS_OUTPUT/rt07_g5/` and are deleted only after
review — `merge.py` verified each against its `DONE` sidecar before anything was merged.

## 5 · Metadata never touched the mapping

Every shard ran with **no** `--metadata`; `family_metadata` is `NOT_SUPPLIED` on all 369,381
rows. Stage-1 labels are joined afterwards, in `merge.py`, against landed outputs.
`preflight.py` asserts structurally that the runner never reads `by_myRT`, `by_PADLOC`,
`by_DefenseFinder`, `family_label`, `source_database` or any `tax_` field, and that the only
destination of a supplied label is the single `family_metadata` column.

## 6 · What this bundle does not say

* **No accuracy against tool labels.** No sensitivity, specificity, precision, recall, F1 or
  ROC against MyRT, PADLOC or DefenseFinder, and tool disagreement is never mapper error.
  The allowed form is *"among sequences labelled F, state S was MAPPED in X % of inspectable
  sequences."*
* **`NO_SUPPORTED_MAPPING` is not biological absence**, and `DELETED_STATE` is a statement
  about the alignment path, not about protein content.
* **Abstention is not failure.** 15,279 sequences abstained under the frozen rule; 0 failed.
* **No family-architecture conclusion.** That is g6. See `docs/G6_READINESS.md`.
* **Scope remains `-M 50` only** — no `-M 60`, no `-M a2m`, no universal RT architecture, no
  residue-level accuracy, no transfer claim beyond UG25.
* **Historical RT0–RT7 stays `UNRESOLVED`**; every state is a `state_id`.

## 7 · Reproducing

```bash
bash run.sh      # preflight, shard, apply, verify+merge, QC  (~10 min on 44 cores)
bash verify.sh   # re-check the landed dataset without re-running the pass
```

`run.sh` is resumable: a shard is skipped only if its `DONE` sidecar verifies — input hash,
instrument digest and all four output hashes. Interrupt it freely.
