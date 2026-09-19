# PROVENANCE — Stage 3C (`s3c`)

seed: 20260919 - used only by the Region-X shuffle negative control (100 shuffles per scanned
interval, scripts/s07_xy_regions.py). Every other computation here is deterministic and has no RNG.
agreements: cff983144e2ad6fc01f648982fb61810dd77ddbe
env_lock_sha256: b1a63d8a7745c82c16cb88b871b51dbbe9c71cbd3bcd2cf10fb0219f14d2acbf
models: claude-opus-5-1m

    track:              s3c — post-hoc integration of frozen RT architecture analyses
    launcher:           launchers/LAUNCHER_03C_architecture_integration.md
    date:               2026-09-19
    operator:           Melissa Rios
    worktree:           /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-stage3c (branch worktree-stage3c)
    scratch dir:        none — this stage wrote only into analysis/stage3c_architecture_integration/
                        and a disposable literature cache under the session scratchpad
    git sha (start):    67c137ba  (Stage-3A closure; the branch point for this work)
    git sha (packaged): 260d3e5a  + this commit
    agreements:         cff9831   (general/ submodule pin, per docs/decisions/2026-09-15_general_pin_cff9831.md)
    env:                conda env `retron_tradicional` at /home/borg/miniconda3/envs/retron_tradicional
    env.lock:           conda env export, verbatim
    env_lock_sha256:    b1a63d8a7745c82c16cb88b871b51dbbe9c71cbd3bcd2cf10fb0219f14d2acbf
    python:             3.12.12 · gemmi 0.7.5 · matplotlib 3.10.5
    seed:               20260919 — used only for the Region-X shuffle negative control
                        (100 shuffles per scanned interval, scripts/s07_xy_regions.py).
                        Every other computation in this stage is deterministic and has no RNG.
    models:             Claude Opus 5 (1M context) — planning, code, analysis and report.
                        Two subagents of the same model family performed literature RETRIEVAL only;
                        their outputs were re-verified here before use, and one of their claims was
                        NOT reproduced and not adopted (CONTRADICTIONS_AND_UNCERTAINTY.tsv X05).
                        No independent adversarial review has been run on this stage; a reviewer
                        must be DISJOINT from this set (BS-15, WA-A.5).

## Instruments, by identity not by name

| instrument | identity | role |
|---|---|---|
| Stage-3A partition | `rt_pdp_primary.residues.tsv` sha256 `79fc0f42…`, frozen at commit `76526444`, closure `67c137ba` | the units every comparison joins to |
| Stage-3A BJ-p4 arm | `rt_pdp_p4.residues.tsv` sha256 `915f2825…` | sensitivity arm, carried in A and B |
| Stage-3B detector + truth | bundles `cat3b_g1_population_freeze`, `cat3b_g2_contract_and_thresholds`, every file hash-checked against their own `OUTPUTS.tsv` | catalytic evidence, Tier A only |
| Stage-2 mapper | `rtmap-1.0.0/53a1e738a19b3896`, verified by `version.check_instrument()` | applied unmodified to 62 chain sequences |
| Stage-2 closed state | git objects at `94a1a78868d6039297c78b3fdcc047d633d6645e` (main), copied into `inputs/stage2_94a1a788/` and hash-verified against the blobs | state blocks, statuses, erratum |
| coordinates | 62 chains, `file_sha256` from `STRUCTURE_REGISTER.tsv` re-verified | nucleic-acid contacts, sequence check |
| historical boundaries | `RETRON-DB_V3/MELISSA_DATA/crystal_structures/reference_boundaries.*` — hashed here for the first time | audited RED stratum, never truth |

## Governing decisions

* `docs/decisions/2026-09-19_stage2_closed.md` + `docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv`
  (read together; the erratum supersedes the frozen `downstream_may_say` column).
* `launchers/LAUNCHER_03B_catalytic_site_architecture.md` closure banner — Tier B contributes zero rows.
* `analysis/stage3a_structural_core/closure/STAGE3C_HANDOFF.md` — rules 1–6, adopted as the design basis.
* `docs/BLOCKED.md`, 2026-09-19 — two entries: the pre-existing `specs_exist.sh` failure (LOW-STAKES,
  default taken) and the Tier-B exclusion (operator decision, default taken).

## Kill criteria, as executed

K1/K2/K4 in `scripts/s00_inputs.py` · K3/K6 in `scripts/s02_catalytic_join.py` ·
K5/K7 in `scripts/s04_states_join.py`. None fired. K5 passed at 140/143 = 0.979 against the declared
0.95 bar. No threshold was moved after any join; the three post-hoc corrections that were made are
listed in `README.md` question 6 and are controls and measures, not outcome-bearing thresholds.

## Compute actually used

CPU only, no GPU, no Ibex, no SLURM. Full `run.sh` wall clock ≈ 30 s. Network used only for the
one-time literature retrieval (Europe PMC, NCBI); nothing was uploaded, and no result depends on a
live network.
