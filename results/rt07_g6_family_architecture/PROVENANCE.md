# PROVENANCE — rt07_g6_family_architecture

```
env_lock_sha256: ba6c8519a1b5bf5a9eee67dc798a1cc3f4871c005a61ce5098ccad0ca47ab6cc
agreements: cff983144e2ad6fc01f648982fb61810dd77ddbe
seed: 20260918
models: claude-opus-5[1m]
commit: 34db87f
date: 2026-09-18
operator: Melissa Rios
scratch: ARIS_OUTPUT/rt07_g6/
```

| field | value |
|---|---|
| gate id | `rt07_g6_family_architecture` |
| authority | `launchers/LAUNCHER_02_rt0_rt7_definition.md` §7 (`g6` row) — no new launcher |
| plan | `results/rt07_g4b_production_mapper/docs/G6_ANALYSIS_PLAN.md` |
| predeclaration | `control/PREDECLARATION.md`, written before any statistic existed |
| repair | `control/REPAIR_1.md` — 1 of 1 allowed, now spent |
| incidents | `control/EXECUTION_INCIDENTS.md` — a wrong diagnosis, recorded not hidden |
| branch | `worktree-rt07-g7a-bridge` |
| environment | `/home/borg/miniconda3/envs/retron_tradicional` — pinned by CONTENT via `env.lock` |
| clustering tool | `mmseqs 18.8cc5c`, version pinned and recorded in `tables/g6_clustering_resource.tsv` |
| seed use | `20260918` seeds every permutation null and the PC-SPLIT sample. Cluster half-assignment is deterministic from `sha256` of the cluster representative and uses no seed. |
| models | `claude-opus-5[1m]` (Claude Opus 5, 1M context) |
| machine | borg, CPU only. No Ibex, no GPU, no job submitted. |

## Independence

**This bundle has had no adversarial pass.** Under BS-15 an adversarial reviewer must assert its
own model is DISJOINT from the `models` list above.

## The frozen instrument and the frozen dataset

Neither was modified. `run.sh` verifies the instrument digest
(`rtmap-1.0.0/53a1e738a19b3896`) read-only, then runs
`results/rt07_g5_catalogue_application/verify.sh` to completion before any analysis, so the
dataset this gate consumes is checked rather than assumed.

## Sealed external context

`results/rt07_g7a_rt0_rt7_bridge/` — the historical RT0–RT7 bridge — was landed before this
gate ran, chronologically, and was **treated as though it did not exist**. No g7a-derived
assignment, boundary, structural interpretation or region influenced any g6 feature, threshold,
family, state, clustering rule or hypothesis. `INPUTS.tsv` names no g7a path, no script reads
one, `seal.py` asserts it, and `verify.sh` V1/V2 check it mechanically.

This ordering is unusual and is recorded rather than glossed: the two gates are independent by
construction, and the mechanical check is what makes that auditable rather than a promise.

## Execution-safety posture

After the incident in `control/EXECUTION_INCIDENTS.md`, heavy analysis steps were run
**serially**, background task state was read with the task tools rather than `ps` (which is
namespace-limited here and cannot see them), and `free -g` was checked before each heavy launch.
No process belonging to another project session was inspected or signalled.

## Compute actually incurred

CPU only, minutes not hours. Clustering 369,381 sequences: 25 s. Matrix build over 55,407,150
state rows: 55 s. The permutation nulls dominate the rest. A counting loop in `arms.rho` was
made O(n) instead of O(n_groups x n_seq) partway through; the fix was verified to reproduce the
already-landed ρ = 0.9865 and group count of 36 exactly before being adopted.

## Reproduction

`bash results/rt07_g6_family_architecture/run.sh` reruns the gate end to end from the hashed
inputs.
