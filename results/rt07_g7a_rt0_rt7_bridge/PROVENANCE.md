# PROVENANCE — rt07_g7a_rt0_rt7_bridge

```
env_lock_sha256: ba6c8519a1b5bf5a9eee67dc798a1cc3f4871c005a61ce5098ccad0ca47ab6cc
agreements: cff983144e2ad6fc01f648982fb61810dd77ddbe
seed: 20260918
models: claude-opus-5[1m]
commit: 53ce53235786f7065c93b1de22dd116645575b43
date: 2026-09-18
operator: Melissa Rios
scratch: ARIS_OUTPUT/rt07_g7a/
```

| field | value |
|---|---|
| gate id | `rt07_g7a_rt0_rt7_bridge` |
| launcher | `launchers/LAUNCHER_03_rt0_rt7_closure.md` |
| track | `rt07` |
| branch | `worktree-rt07-g7a-bridge` |
| agreements pin | the `general/` submodule revision recorded in `docs/decisions/2026-09-15_general_pin_cff9831.md` |
| environment | `/home/borg/miniconda3/envs/retron_tradicional` — pinned by CONTENT via `env.lock`, not by name |
| seed use | used ONLY for the NC-1 shuffled decoy. Every other step is deterministic: the frozen mapper orders its work by `(rt_hash, sequence_id)` and its per-sequence calls are independent of batching. |
| models | `claude-opus-5[1m]` (Claude Opus 5, 1M context) — planning, code and reporting |
| machine | borg, CPU only. No Ibex, no GPU, no job submitted. |

## Independence

**This bundle has had no adversarial pass.** Under BS-15 an adversarial reviewer must assert its
own model is DISJOINT from the `models` list above, so a review by `claude-opus-5` would not
satisfy the independence gate for this bundle.

## The instrument

The frozen production mapper was **executed, never modified**:

```
rtmap-1.0.0/53a1e738a19b3896
profile GII.deriv.hmm, LENG 471, hhmake -M 50
```

`run.sh` verifies the instrument digest before any measurement, and verifies immediately
afterwards that the frozen bundle's own `control/CROSSWALK_RT0_RT7.tsv` is **still `UNRESOLVED`
in every row**. This gate does not edit a frozen bundle; it lands its own crosswalk table, which
a decision record adopts.

## Compute actually incurred

Well under the launcher's 30 CPU-minute budget: the bridge is six sequences through an
instrument whose landed throughput was measured against 369,381. The pilot (LtrA alone) and the
full panel each completed in seconds.

## Order of operations — the audit trail

`control/ASSIGNMENT_RULE.md` was written **before** `s03_bridge.py` ran, so no classification
rule was chosen after seeing a state-to-residue number. Its **Amendment 1** was made after `s01`
traced the Blocker PDF and still **before** `s03` ran; the amendment is sourced entirely from
primary literature and its effect is to make RT1 *less* determined, not more.

No `g5` or `g6` artefact is an input, is read by any script, or was consulted at any point.
`verify.sh` check NC-4 asserts this three ways.

## Reproduction

`bash results/rt07_g7a_rt0_rt7_bridge/run.sh` reruns the gate end to end from the hashed inputs.
It was run to completion from a cleared scratch directory on 2026-09-18 and reproduced every
number in this bundle, with all 12 `verify.sh` checks passing.
