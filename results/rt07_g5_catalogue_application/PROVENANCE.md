# PROVENANCE — rt07_g5_catalogue_application

gate: rt07_g5_catalogue_application
scratch: ARIS_OUTPUT/rt07_g5 (512 shard FASTAs, ~12 GB of per-shard TSV, per-shard DONE sidecars). Retained until review; deleted only after merge.py verified every shard against its sidecar.
git_sha: see the commit that lands this bundle
agreements: cff9831
env_lock_sha256: ba6c8519a1b5bf5a9eee67dc798a1cc3f4871c005a61ce5098ccad0ca47ab6cc
seed: n/a — no RNG anywhere in the application path. Shard assignment is sha256(sequence_id) mod 512; ordering is sorted identifier throughout.
models: claude-opus-5[1m]
date: 2026-09-17
operator: Melissa Rios

## The instrument — verified field by field before the run, unchanged after it

mapper_version: rtmap-1.0.0/53a1e738a19b3896
instrument_sha256: 53a1e738a19b38967563b4f4d733047b26123f754a7d592fd0186e7bd9c331f5
mapper_code_sha256: 69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef
schema_version: rtmap-schema-1.0
profile_sha256: 292495a4f4ec2d04c47cf73c658b0f5cbaec7b202de70d97e6fc2496dd82e97b (LENG 471)
anchor_set: 150 frozen conserved states, sha256 3eca033357f5f7ca...
match_state_definition: hhmake -M 50
CAT_STATE: 262 (NOT one of the 150 anchors)
PP_HI: 0.75   PP_LO: 0.50   S_MIN: 10   K_MIN: 30
T1: 0.32      D_MAX: 0.48   D_RANDOM: 0.067
dyad_pattern: [YF].DD
domain_scoring_protocol: PER_SEQUENCE_DB_SIZE_1
hmmer: HMMER 3.4 (Aug 2023); hmmalign 532f1ed4..., hmmsearch e73bad9d...
python: 3.12.12 (retron_tradicional)
bundle_root_verified: 0b025cbab192f64d05ef0a9aff47859b998fe3158dc0199cd47cbbd040620d3f

Every one of the 512 shards verified the whole g4b bundle against that EXTERNAL pinned root
before emitting a record, and recorded bundle_root_status=VERIFIED in its own provenance.
merge.py asserted a single instrument identifier and a single verified root across all 512.

## Population

G5_ELIGIBLE_N: 369381 — the frozen census denominator from results/rt07_g5a_eligibility_census
n_total_exact_rt: 501561
n_ineligible: 132180 (censused out before sharding; retained in g5_ineligible.parquet)
reconciliation: 369381 identifiers, each appearing exactly once across all shards'
  sequences.tsv and TOOL_FAILURE rows; 0 duplicated, 0 missing, 0 unexpected

The eligibility rule was applied exactly ONCE, in g5a. shard.py reads the censused partition
and does not re-apply it, so this stage cannot disagree with the census.

## Execution

shards: 512, by sha256(sequence_id) mod 512; min 626, median 722, max 796 sequences
batch size: 500
parallelism: 44 concurrent shards on one 48-core host
wall: 244.84 s for the mapping pass; 365 s for verification + merge
peak RSS: 182 MB per runner; 3.5 GB for the merge
compute: CPU only. No GPU, no Ibex, no SLURM job.
shard failures: 0
tool failures: 0
input invalid at run time: 0

## Inputs

exact_rt_faa: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_exact_v1.faa
  sha256 bcde6e9a64de90e6e791256f79c87799a00a95f0d1730f3460301220379e2655
eligibility_partition: data/derived/rt07_g5a/g5a_eligibility_partition.tsv.gz
metadata (joined AFTER mapping): rt_exact_v1, rt_family_baseline_v1, rt_tool_calls_v1,
  rt_records_v1 — all Stage-1 canonical parquet

## Metadata separation

Every shard ran with NO --metadata. The runner's only metadata destination is the single
schema column family_metadata, which is NOT_SUPPLIED on all 369,381 rows. Stage-1 labels are
joined in merge.py, after mapping, against landed outputs. preflight.py asserts structurally
that the runner never reads by_myRT, by_PADLOC, by_DefenseFinder, family_label,
source_database or any tax_ field.

## Canonical dataset — data/derived/rt07_g5/ (gitignored by project convention)

g5_catalytic.parquet: 26660834 bytes  sha256 95dcb20aac95946cb3c54c41b7bd0dc496239422620416d15675611806bf0887
g5_ineligible.parquet: 10192406 bytes  sha256 253a092fd4d72b1593cbb15a5b82ca2739891cc3570336da0370f5aff36b4635
g5_metadata_crosswalk.parquet: 56149583 bytes  sha256 02c6e54d12e4a1c2ec3d35f8d0260d8104077f87365e16a509a9940d4f47dd14
g5_run_failures.parquet: 4177 bytes  sha256 4b1d1ae5ce9033c3e1471b20a68633ba51e20ee643ad4998114fc6142de0f52a
g5_sequences.parquet: 41842661 bytes  sha256 55bd268a1b8ff01bd8d4cf61f85bfda3909919b3faec74da752186a6a6ebbbb5
g5_states.parquet: 108189029 bytes  sha256 5bdcb6e3ef4344da8d64a8fe9f59fd641138115b68dc88aff4c3e80b970a4eae

## Governing documents

- results/rt07_g4b_production_mapper/docs/G5_EXECUTION_PLAN.md — the plan this run follows
- results/rt07_g4b_production_mapper/docs/STAGE1_METADATA_ROLE.md — metadata are strata, never truth
- results/rt07_g4b_production_mapper/docs/OUTPUT_SCHEMA.md — rtmap-schema-1.0
- results/rt07_g5a_eligibility_census/ — the frozen denominator
- docs/decisions/2026-09-17_stage2_launcher_g4b_freeze_amendment.md
