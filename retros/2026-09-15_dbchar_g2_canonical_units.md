# Retro — dbchar_g2_canonical_units (2026-09-15)

Bundle: `results/dbchar_g2_canonical_units/` — REPRODUCIBLE, human_input_audit PENDING.
Rerun 13:01 wall, peak 27.8 GB.

## What happened

- Extraction and table-building were split into two processes on purpose: a pass-only extractor
  (64 MB newline-aligned chunks, 40 workers → parquet shards + `shard_index.tsv`) and a merge that
  reads only those shards. The 81 GB corpus is then read exactly once per rerun.
- The analytical-unit ladder came out **non-constant**: loci per exact RT runs 1.11–5.49 depending
  on the source database. This is the gate's main result and the reason no downstream number may
  convert between units by a fixed factor.
- RT back-translation verified 99.47% of RT-family records against the window DNA under the
  declared recoding classes, strand-aware, with `frame_disambiguating` kept as its own stratum.

## What went wrong

- **The merge was written with per-group Python lambdas** over ~3M groups and was unusably slow
  and memory-hungry. Replaced with a vectorised `set_cols` that builds joined set strings only for
  the groups that actually have more than one value. 8:36, 7.5 GB.
- **The seeded-bad control crashed instead of failing cleanly** (`ValueError: truth value of a
  Series is ambiguous`). A control that raises is not a control that rejects: the run.sh guard
  would have been satisfied either way. Fixed with a `cell()` helper that returns `.iloc[0]`.
- **The prior exact-RT comparison read 501,570 against my 501,561** — the prior file has 9 comment
  lines that my row count included. Switched to a set comparison: the two sets are identical, 0
  differences either way. A count comparison can disagree where the things counted agree.
- **"Loci appearing in more than one source file = 0"** was an artefact of the first-copy filter,
  not a finding. Added the all-records measure: **9**, which confirms the prior project's number.
  A zero produced by a deduplication rule is a property of the rule.
- I briefly concluded the extraction had **died** because `ps` showed no such process. The sandbox
  runs each command in its own PID namespace, so `ps` cannot see it. The job had finished with
  exit 0; I had already deleted its outputs and had to re-run (~20 min).

## Proposal (not an amendment — WA-S.2)

**A control that raises must fail the gate, not pass it.** `run.sh`'s seeded-bad guard inverts the
exit status, so a control that crashes for an unrelated reason looks like a correct rejection.
Guards should require the control to exit with a *declared* rejection code (e.g. 3), not merely
non-zero.
- *Would have caught:* this gate's `ValueError`, which "passed" the seeded-bad guard while proving
  nothing.
- *Would wrongly reject:* a control that legitimately aborts on a missing input — which should be
  a hard error anyway, so the rejection is correct but the message would be confusing.

## Carried into later gates

Non-constant conversion factors; the eligibility flag set (`elig_exact_rt`, `elig_rt_coords`,
`elig_geometry`, `elig_rt_length`, `elig_rt_completeness`) with reason strings; `VIEWS.md` and
`pull.py` as the declared vocabulary over the derived tables.
