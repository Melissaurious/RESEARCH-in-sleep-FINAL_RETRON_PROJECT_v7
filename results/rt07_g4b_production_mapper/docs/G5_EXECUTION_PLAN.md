# g5 — Stage-1 catalogue application. PLAN ONLY. Not executed in g4b.

`rt07_g5_catalogue_application`. **g5 is blocked until the operator authorises it.** Nothing
in this plan has been run; the only sequences g4b touched are the 560 construction sequences
used for the smoke test and the throughput measurement.

g5 is an **application**, not a validation. It produces call states over a population. It
produces no accuracy statement, no new threshold and no new claim.

---

## 1 · Frozen input

| | |
|---|---|
| instrument | `rtmap-1.0.0/53a1e738a19b3896` |
| mapper | `code/rtmap/mapper.py` sha256 `69575dc7…` |
| profile | `GII.deriv.hmm` sha256 `292495a4…`, LENG 471 |
| anchors | `control/FROZEN_ANCHORS.tsv` sha256 `c48315ae…`, 150 states |
| schema | `rtmap-schema-1.0` |
| population | `data/derived/rt_exact_v1.faa` — 501,561 exact RT proteins |

`verify.sh` must pass, and `scripts/test_production_freeze.py` must pass, immediately before
the run and again after it. The instrument identifier recorded in every shard's provenance
must be the one above.

**`--pinned-root` is REQUIRED for every g5 shard.** Each shard verifies the whole production
bundle against `review-stage/roots/RT07_G4B.root` — supplied from outside the bundle,
because a bundle cannot authenticate itself — before emitting any record, and records the
root and `bundle_root_status=VERIFIED` in provenance. A run whose provenance says
`UNVERIFIED_NOT_REQUESTED` is not a g5 run. This closes review finding R1: the instrument
digest binds `code/` and `control/`, and the pinned root binds the bundle on disk.

---

## 2 · Step 1 — eligibility census (cheap, and it fixes the denominator)

Before any mapping: one pass over `rt_exact_v1.faa` recording, per record, only the
identifier, the cleaned length, and whether it passes the inherited eligibility rule
(≥ 250 aa, standard residues). No alignment, no scoring, no annotation.

Lands `tables/g5_eligibility_census.tsv`: eligible / `BELOW_MIN_LENGTH` /
`NON_STANDARD_RESIDUE` / `EMPTY_SEQUENCE` / duplicate-identifier counts, overall and by
Stage-1 family stratum, plus the distinct-`rt_hash` count.

**It also lands the GLOBAL duplicate-identifier census**, `tables/g5_id_conflicts.tsv`: every
identifier that carries more than one distinct sequence anywhere in the catalogue. That file
is passed to every shard as `--reject-ids`. Shard-local detection cannot see a conflict whose
two records landed in different shards, which is review finding R2.

This matters because the landed Stage-1 length distribution
(`results/dbchar_g7_stage1_report/tables/fig01_rt_length_by_family_restyled.tsv`) shows
substantial mass below 250 aa — RVT-GII q25 = 244, RVT-UG4 q25 = 198, RVT-CRISPR-like
q25 = 169, minima in the 20–80 aa range. **The eligible population is smaller than 501,561
and its size is not yet known.** Every later denominator is the censused eligible count, not
the catalogue count. Ineligible records are reported as `INPUT_INVALID`, never as absent RTs.

---

## 3 · Batching, sharding and ordering

* Shard the eligible population by **`sequence_id` hash prefix**, not by file position, not
  by family, and **not by `rt_hash`**: 512 shards on the first 9 bits. Hash-prefix sharding
  is stable under re-partitioning, expected to be approximately family-balanced (a hash
  prefix is balanced *in expectation*, not by construction — g5 reports the realised
  shard-size distribution), and reproducible from the input alone.

  Sharding on `sequence_id` rather than `rt_hash` is review finding R2's second half: it
  guarantees that every record sharing an identifier lands in the **same** shard, so a
  conflict cannot hide by being split across two. The cost is that identical sequences under
  different identifiers now usually land in different shards, so deduplication saves less
  work. That is the right trade: deduplication is an optimisation, identifier integrity is
  not, and the whole run is under two core-hours either way.
* Within a shard, work is ordered by `(rt_hash, sequence_id)`; batch boundaries are a
  function of that order and `--batch-size` only.
* `--batch-size 500`. Measured peak RSS 150 MB at batch 1000, 102 MB at batch 100; 500 sits
  comfortably inside a 4 GB allocation with room for the input.
* **Shard and batch geometry cannot move a result.** Verified: `states.tsv`,
  `sequences.tsv` and `failures.tsv` are byte-identical at batch sizes 1, 100, 500 and 1000
  (smoke S4 and the 560-sequence measurement). This is why domain scoring is per-sequence —
  see `PRODUCTION_SPEC.md` §3.

## 4 · Deduplication

Exact-sequence duplicates are collapsed to one mapping call by `rt_hash`; every identifier
still receives its own output row, so per-sequence denominators are unaffected. The number
collapsed is recorded per shard in provenance.

With `sequence_id` sharding the collapse is **shard-local**, and is described that way rather
than overstated: identical sequences under different identifiers may be mapped more than once
across the run. They produce identical calls — smoke check S7 asserts that — so this costs
compute, not correctness. The merge reports the cross-shard `rt_hash` duplication rate.

**Duplicate identifiers** (review finding R2): an identifier carrying *different* sequences
is a `DUPLICATE_SEQUENCE_ID_CONFLICT` and **every** occurrence is rejected — never "the
first", which made the retained science depend on input order. An identifier repeated with an
*identical* sequence is kept once and the redundant copy logged. The global census from §2
supplies the conflict set to every shard.

**Reconciliation** (review finding R3): each shard fails closed unless every valid input
identifier appears exactly once across `sequences.tsv` and the `TOOL_FAILURE` rows of
`failures.tsv`. The merge repeats this check across the whole run against the eligibility
census.

## 5 · Compute estimate — from a measured smoke test, not an assumption

Measured on 560 construction sequences, mean length 477 aa, single core, by
`scripts/measure_throughput.py`, which produces every figure below **in one run on one
substrate** and writes `tables/g4b_throughput_measurement.tsv` itself. The round-1 review
noted the earlier component figures came from different harnesses and did not add up; they
now do, and the script is re-runnable.

| quantity | measured |
|---|---|
| end-to-end per-sequence cost | **13.1 ms** |
| component: batched `hmmalign` | 1.4 ms |
| component: per-sequence `hmmsearch` | 11.4 ms |
| components sum | 12.8 ms — **less** than the end-to-end total; the remainder is process startup, I/O and row rendering, which is why the estimate uses the total, not the sum |
| peak RSS | 102 MB @ batch 100, 150 MB @ batch 1000 |
| `states.tsv` | 175.7 bytes/row |
| `sequences.tsv` | 277.0 bytes/row |
| gzip ratio on `states.tsv` | 22.2× |

**Run-to-run variation is real and is not hidden.** Three runs of this script on this host
gave end-to-end costs spanning **12.9 to 14.1 ms**, and the currently landed run gives
13.1 ms; the round-2 reviewer independently measured 12.9 ms. The landed table is whichever run last wrote it, and the plan quotes that
run. These are measurements on a shared host, not frozen constants, and they are **not** part
of the instrument identifier. Use ≈ 13–14 ms as the planning figure.

Projected at the full 501,561. **This is not an upper bound** — it is a full-count
extrapolation *at this substrate's rate*, and two effects push in opposite directions: the
eligible count is lower than 501,561, but the Stage-1 length distribution is wider than this
477 aa substrate (family medians 253–1232 aa) and `hmmalign` cost scales with length, so the
per-record cost can be higher.

| quantity | projection |
|---|---|
| single-core wall | **≈ 1.8 core-hours** |
| 48 local cores, ideal scaling | ≈ 2.3 min |
| `states.tsv` rows | 75.2 M |
| `states.tsv` raw / gzipped | 13.2 GB / **0.60 GB** |
| `sequences.tsv` | 139 MB |

The 48-core figure assumes ideal scaling and has **not** been measured; it is an arithmetic
division, labelled as such. What is measured is the single-core cost.

**CPU only. No GPU. No Ibex allocation is required.** On the projection above the run
completes on the local 48-core host in minutes rather than hours — a projection, not a
measurement, until g5 makes it one. Even a 2× or 3× overrun from the wider Stage-1 length
distribution stays well inside budget, which is why no allocation is requested.

Storage, not compute, is the binding constraint, and gzipping shards after verification
reduces it to under a gigabyte.

## 6 · Restart / resume

* Each shard writes `<shard>.DONE` carrying the input sha256, the instrument digest and the
  sha256 of its four outputs. A shard is skipped **only if all of them verify** — a tampered
  or missing output, a changed input or a changed instrument forces a redo. Presence alone is
  not completion (review finding R4: an empty `DONE` previously skipped a shard that had
  produced nothing). `--force` redoes a shard unconditionally.
* Every write is `.part` → atomic `rename`, so an interrupted run leaves no half-written
  shard — a partial shard simply has no `DONE` and is redone whole.
* Resume is therefore idempotent and needs no external job-state database.
* A completed run is re-verified by recomputing each output's sha256 against its `DONE`
  sidecar before the merge.

## 7 · Failure logging

Per-shard `failures.tsv` with `INPUT_INVALID` / `TOOL_FAILURE` and a machine-readable reason
code. A batch that raises is retried one sequence at a time, so one bad record costs one
`TOOL_FAILURE` row instead of a batch of them. Failure counts are reported alongside every
result and are **never** converted into biological absence.

`g5_failure_summary.tsv` aggregates reason codes overall and by stratum. A `TOOL_FAILURE`
rate above zero is investigated before the merge, not written off.

## 8 · Merge and final products

1. Verify every shard against its `DONE`.
2. Concatenate in shard order → `sequences.tsv` (single file, 139 MB) and a partitioned
   `states/` directory (one gzipped TSV per shard, plus a parquet conversion for g6).
3. Land `g5_manifest.tsv`: shard, row counts, sha256 of each output, instrument identifier.
4. Assert a single instrument identifier **and a single verified bundle root** across all
   shards — a second value of either is a hard stop.
5. Reconcile the whole run against the eligibility census: every eligible identifier appears
   exactly once across all shards' `sequences.tsv` and `TOOL_FAILURE` rows.
6. Land the headline call-state distribution over the eligible population, with the
   eligibility census as the denominator, plus the per-stratum tables the launcher names
   (`exact-RT by block call table`, `long-format exact-RT and block boundary table`).

## 9 · Production smoke test before the real run

`bash verify.sh` — the same seven checks that pass in g4b, re-run against the g5 instrument
immediately before the catalogue pass. It tests **engineering** only, on sequences already
seen in development and validation. **It is not new scientific validation**, and no number
from it is reported as a result.

## 10 · What g5 must not do

* No new threshold, rule, control, family or criterion.
* No holdout, no transfer test, no re-validation of the mapper, no re-run of UG25.
* No accuracy statement against MyRT / PADLOC / DefenseFinder labels.
* No RT0–RT7 renaming of production output.
* No conversion of `DELETED_STATE` or `NO_SUPPORTED_MAPPING` into biological absence.
* No filtering of atypical biology before it is reported.
