# g5 APPLICATION REVIEW — is the canonical dataset trustworthy for g6?

**Scope is the APPLICATION, not the mapper.** Stage-2 validation closed at Endpoint A and the
g4b packaging review reached 9/10 and authorised g5. **Do not reopen mapper validation,
generalisation or transfer. Do not propose new validation families, holdouts, thresholds or
controls.** Such recommendations are out of scope.

Assess only:

1. did the full application use the **exact frozen mapper**;
2. are the **denominators** correct;
3. was **metadata kept separate** from mapper inference;
4. is the **merge/shard logic complete** — no missing, duplicated or stale shard output;
5. is the **canonical g5 dataset trustworthy for g6**.

```
CENSUS BUNDLE : results/rt07_g5a_eligibility_census/       (bundle_valid.sh: passes BS-1..BS-10)
g5 BUNDLE     : results/rt07_g5_catalogue_application/      (passes BS-1..BS-10)
DATASET       : data/derived/rt07_g5/*.parquet              (hashed in tables/g5_dataset_manifest.tsv)
SCRATCH       : ARIS_OUTPUT/rt07_g5/  512 shard FASTAs, 512 shard TSV sets, 512 DONE sidecars
INSTRUMENT    : rtmap-1.0.0/53a1e738a19b3896  (g4b bundle root 0b025cba...040620d3f)

verify : bash results/rt07_g5_catalogue_application/verify.sh
         bash results/rt07_g5a_eligibility_census/verify.sh
```

## What is claimed

**Denominator.** 501,561 exact RTs → 369,381 eligible (`G5_ELIGIBLE_N`), 132,180 ineligible
(108,439 `BELOW_MIN_LENGTH`, 23,741 `NON_STANDARD_RESIDUE`, 4,000 short-and-also-nonstandard
reported as a secondary flag). The eligibility rule is imported from the frozen package and
applied **once**, in g5a; `shard.py` reads that partition and does not re-apply it.

**Application.** All 369,381 mapped with the frozen instrument. 512 shards by
sha256(sequence_id) mod 512, batch 500, 44-way parallel, 244.8 s, 0 shard failures, 0 tool
failures, 0 invalid inputs. Every shard verified the g4b bundle against the external pinned
root before emitting a record and recorded `bundle_root_status=VERIFIED`.

**Merge, asserted before anything was written:** all 512 DONE sidecars verify (input sha256,
instrument digest, all four output hashes); exactly one instrument identifier and one
verified root across the run; every censused-eligible identifier appears exactly once across
all shards' `sequences.tsv` and `TOOL_FAILURE` rows — 0 duplicated, 0 missing, 0 unexpected.

**Result.** 354,102 inspectable (0.9586), 15,279 frozen abstentions, 55,407,150 state rows.
`CAT_STATE` 262 MAPPED in 356,229; `CATALYTIC_CONFIRMED` 343,880 = 0.9653 of CAT-MAPPED, on
its own denominator, never pooled with the 150 anchors.

**Metadata separation.** Every shard ran with no `--metadata`; `family_metadata` is
`NOT_SUPPLIED` on all 369,381 rows; Stage-1 labels are joined afterwards in `merge.py`.
`preflight.py` asserts structurally that the runner reads no tool, family, database or
taxonomy field, and that the only destination of a supplied label is `family_metadata`.

## Please attack these specifically

* a. Is the instrument used in the run **provably** the canonical g4b instrument, on every
  shard — not just on the one preflight checked?
* b. Is the reconciliation argument airtight, or can a sequence be **silently missing** —
  e.g. present in a shard FASTA but absent from both `sequences.tsv` and `failures.tsv`, or
  counted twice across shards?
* c. Does the parquet dataset faithfully represent the shard TSVs? Spot-check rows end to end:
  shard FASTA → shard TSV → parquet. Do type coercions lose or corrupt anything (`posterior`,
  `sequence_residue_index`, empty strings vs null)?
* d. Are the denominators right? In particular: is `INSPECTABLE` (verdict `MAPPED`) used
  consistently; is the catalytic denominator genuinely separate; does any QC table pool the
  150 anchors with `CAT_STATE`?
* e. Could metadata have influenced mapping in any path the structural check misses?
* f. Is anything **stale** — a table regenerated from a different dataset version, a path
  pointing at scratch that will be deleted, a hash that no longer matches?
* g. Is `docs/G6_READINESS.md` free of biological conclusions and of tool-label accuracy
  claims, and are its denominators stated correctly?
* h. Anything the executor **overclaimed**.

## What to return

1. VERDICT: PASS / PASS_WITH_REQUIRED_REPAIRS / FAIL_BLOCK
2. SCORE: n/10
3. Is the canonical g5 dataset TRUSTWORTHY FOR g6: YES / NO
4. Per question a–h, what you ran and what you found
5. Any load-bearing data-integrity defect
6. Anything you could not verify
