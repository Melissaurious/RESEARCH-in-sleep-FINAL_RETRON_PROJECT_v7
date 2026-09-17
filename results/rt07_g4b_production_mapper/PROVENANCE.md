# PROVENANCE — rt07_g4b_production_mapper

gate: rt07_g4b_production_mapper
scratch: none — g4b produced no scratch stage; every artefact was written directly into the bundle
git_sha: see the commit that lands this bundle
agreements: cff9831
env_lock_sha256: ba6c8519a1b5bf5a9eee67dc798a1cc3f4871c005a61ce5098ccad0ca47ab6cc
seed: n/a — the production path contains no RNG. `scripts/test_production_freeze.py` T8 asserts it: no `Random`, no `shuffle`, no synthetic-control generation in any module under `code/rtmap/`. Deterministic ordering comes from sorting on (rt_hash, sequence_id), not from a seeded stream.
models: claude-opus-5[1m] (executor); gpt-5.6-sol xhigh read-only (independent packaging reviewer, rounds 1 and 2)
date: 2026-09-17
operator: Melissa Rios

## Instrument identity

mapper_version: rtmap-1.0.0/53a1e738a19b3896
instrument_sha256: 53a1e738a19b38967563b4f4d733047b26123f754a7d592fd0186e7bd9c331f5
schema_version: rtmap-schema-1.0
match_state_definition: hhmake -M 50
frozen_mapper_sha256: 69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef
profile_sha256: 292495a4f4ec2d04c47cf73c658b0f5cbaec7b202de70d97e6fc2496dd82e97b
anchor_table_sha256: c48315aef8dccdcee1f41ebef512cc69a63e51cfad22df28c73a84c564a30e49

The instrument identifier is a hash over the schema version, match-state convention, mapper
sha256, profile sha256 and LENG, anchor-set sha256, the eight calibrated parameters,
`CAT_STATE`, the dyad pattern, both HMMER binaries, a tree digest over every file in `code/`
and `control/`, the eligibility rule and the domain-scoring protocol. `tables/` is excluded,
so landing an output does not change it. Recompute with:

    python3 -c "import sys; sys.path.insert(0,'code'); from rtmap import version as V; \
                print(V.mapper_version(V.check_instrument()))"

## External pinned root

manifest: review-stage/manifests/RT07_G4B.MANIFEST
root_file: review-stage/roots/RT07_G4B.root

Both live OUTSIDE the bundle: a bundle cannot authenticate itself. Verify with

    python3 code/freeze.py verify . <manifest> "$(cat <root_file>)"

## Software

python: 3.12.12 (/home/borg/miniconda3/envs/retron_tradicional)
hmmer: 3.4 (Aug 2023)
hmmalign_sha256: 532f1ed4c21dc03a12007b31c2dc0568e82cab659b0d75c20efd20e6374f53e2
hmmsearch_sha256: e73bad9d701f129795dd3ffb108ee2d4724ab4c8b1a46269bd5671bdcfcdc8f2

No GPU. No Ibex. No SLURM job. Total compute for the whole gate: a few minutes of one core.

## Governing decisions

- `docs/decisions/2026-09-17_stage2_ug25_confirmatory_closed.md` — Stage-2 validation closed
  at Endpoint A; the parameters this bundle freezes.
- `docs/decisions/2026-09-17_stage2_g4b_production_packaging.md` — this gate's decision
  record, including the two executor-found packaging repairs, the five review-required
  repairs, and every corrected overclaim.
- `launchers/LAUNCHER_02_rt0_rt7_definition.md` — the track's autonomy envelope. Note that
  `g4b` is not a row in its gate table; it is an operator-defined packaging step satisfying
  the launcher's requirement that `g4` be frozen before `g5`.

## Independent review

- Round 1: `review-stage/DESIGN_REVIEW_REQUEST_g4b_packaging.md`, thread `01a0afd9-39e8` —
  `PASS_WITH_REQUIRED_REPAIRS`, 6/10, g5 may NOT begin, five REQUIRED findings.
- Round 2: `review-stage/DESIGN_REVIEW_REQUEST_g4b_round2.md`, thread `01a0aff7-9be3` —
  `PASS_WITH_REQUIRED_REPAIRS`, 9/10, **MAY g5 BEGIN: YES**, all five FIXED, no science
  changed, two documentary overstatements repaired here.
