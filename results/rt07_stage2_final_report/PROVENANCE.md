# PROVENANCE — rt07_stage2_final_report

Written by `scripts/seal.py --provenance`. The env.lock hash and the agreements pin are computed,
not typed.

```
env_lock_sha256: 9baa18b79c80c46bd536a8b6383b98fcfb7179e495a3747ed2bab35787254353
agreements: cff983144e2ad6fc01f648982fb61810dd77ddbe
seed: n/a — no random number generator is used; every step is a deterministic lookup or plot
models: claude-opus-5[1m]
source_of_record: 94a1a78868d6039297c78b3fdcc047d633d6645e
date: 2026-09-19
operator: Melissa Rios
scratch: ARIS_OUTPUT/rerun-rt07_stage2_final_report/
```

| field | value |
|---|---|
| gate id | `rt07_stage2_final_report` |
| track | `rt07` (Stage 2 — closed; reporting only) |
| branch | `rt07-stage2-final-report`, cut from `main` at the source-of-record commit |
| governing closure | `docs/decisions/2026-09-19_stage2_closed.md` |
| agreements pin | the `general/` submodule revision above |
| environment | `/home/borg/miniconda3/envs/retron_tradicional`, pinned by content via `env.lock` (`conda env export --no-builds`) |
| machine | borg, CPU only. No Ibex, no GPU, no job submitted. |
| models | `claude-opus-5[1m]` — package design, code and prose |

## What was read

Every input is listed with its sha256 in `INPUTS.tsv` (57 files): landed tables of the
13 Stage-2 bundles, the governing decision records, the g7a erratum table and the production
crosswalk. One value (the g5 application review score) is read from the message of commit
`6f4a7fe`. Landing commits are read with `git log` at the source-of-record commit, never typed.

## What was not done

No Stage-2 analysis was run or re-run. No frozen bundle, figure, table or decision record was
modified. No Stage-3 work was started. Nothing was pushed.

## Independence

This bundle has had **no adversarial pass**. It makes no new scientific claim. Every status and
interpretation it reports comes from records that were reviewed independently (see
`tables/stage2_review_ledger.tsv`). An independent review of the package's fidelity to those
records has not been done and would need to be vendor-disjoint from the model above.
