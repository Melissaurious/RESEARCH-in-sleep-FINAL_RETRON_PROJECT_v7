# PROVENANCE — rt07_g5a_eligibility_census

gate: rt07_g5a_eligibility_census
scratch: none — the census writes its products directly
git_sha: see the commit that lands this bundle
agreements: cff9831
env_lock_sha256: ba6c8519a1b5bf5a9eee67dc798a1cc3f4871c005a61ce5098ccad0ca47ab6cc
seed: n/a — no RNG. The census is a pure function of the catalogue and the frozen eligibility rule; ordering is by sorted rt_seq_hash throughout.
models: claude-opus-5[1m]
date: 2026-09-17
operator: Melissa Rios

## Instrument whose rule was applied

mapper_version: rtmap-1.0.0/53a1e738a19b3896
instrument_sha256: 53a1e738a19b38967563b4f4d733047b26123f754a7d592fd0186e7bd9c331f5
eligibility_rule: MIN_AA=250;ALPHABET=ACDEFGHIKLMNPQRSTVWY;CLEAN=strip[-.]upper,rstrip*
applied_by: rtmap.run_mapper.validate — the frozen function the production runner calls

The census maps nothing. It imports the eligibility rule from the frozen package and applies
it; it does not restate, relax or reinterpret it.

## The frozen denominator

G5_ELIGIBLE_N: 369381
n_total_exact_rt: 501561
n_ineligible: 132180
partition_reconciles: YES (369381 + 132180 = 501561; no id on both sides, none missing)

## Inputs

input.exact_rt_faa.sha256: bcde6e9a64de90e6e791256f79c87799a00a95f0d1730f3460301220379e2655
  /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_exact_v1.faa
input.exact_rt_parquet.sha256: 44fd615e73f97134eb20e9c5d2e142ca4eff733e919746cc622ecd2cf05f7b9f
  /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_exact_v1.parquet
input.family_baseline_parquet.sha256: 92e0197959174945eaad9b326c91a9e5030506fb6c4e166a721cf1c6ad9183e5
  /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_family_baseline_v1.parquet
input.tool_calls_parquet.sha256: 27c6b5c6fbf06f042fee8d5a46599124be51474966673a1079a3f2f786384009
  /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_tool_calls_v1.parquet
input.records_parquet.sha256: 546605034a2e5f21794a842db17849dfa7018689aea3a1bf43ee63b0837dfb6f
  /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_records_v1.parquet

## Large outputs, under data/derived/rt07_g5a/ (gitignored by project convention)

output.g5a_eligibility_partition.tsv.gz: 249e334b04b2db7975b498949d57bcc89613e43512baad5a007b47ea21de7dfa
output.g5a_ineligible_records.tsv.gz: 9fd48b77df6d8e3e1af0aa7e2b1358b1690b587cfb6e0911804991da42139a06
output.g5a_eligible_ids.txt.gz: 6f2028fa46563ebedb11442bf21341ce0565b230d5ccf68f748ba3b676d02d11

## Governing documents

- results/rt07_g4b_production_mapper/docs/G5_EXECUTION_PLAN.md §2 — this census is its step 1
- results/rt07_g4b_production_mapper/docs/STAGE1_METADATA_ROLE.md — metadata are strata, never truth
- docs/decisions/2026-09-17_stage2_launcher_g4b_freeze_amendment.md
