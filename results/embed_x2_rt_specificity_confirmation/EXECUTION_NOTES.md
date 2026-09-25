# embed_x2 — execution notes

Execution-level incidents and their handling. This file does **not** amend `DESIGN.md`:
no threshold, population, arm, endpoint, stopping rule or outcome gate is changed here.

## E1 — the first local cross-fit was launched twice and was discarded (2026-09-19)

**What happened.** `scripts/y_run_local.sh` was started twice, roughly one minute apart
(runner PIDs 3192079 and 3194050). Each runner executed the full 25-cell sequence with the
same GPU split, so every `(arm, fold)` cell was trained by **two concurrent processes** that
wrote to the same `work/oof_{arm}_f{fold}.npz`, `work/hist_{arm}_f{fold}.json` and
`work/m_{arm}_f{fold}.pt` paths.

**Why it matters.** The shared checkpoint path is the damaging part. `y03_train_cv.py` saves
`m_{tag}.pt` on every improving epoch and reloads it after training to produce the
out-of-fold predictions. With two processes on one path, a process could reload a checkpoint
written by the *other* process at a *different* epoch. That silently breaks the design's
assertion (§4, §5) that each cell is one independent training run whose out-of-fold
predictions come from its own lowest-validation-NLL checkpoint under the frozen stopping
rule. The corruption is **not detectable from the outputs**: each surviving `hist_*.json` is
internally self-consistent (`n_epochs = best_epoch + 6`, consistent with patience 5), and
every `.npz` loads cleanly.

**Detection.** `logs/cell_P_f4.log` showed 53 epoch lines against a 40-epoch cap, with epoch
numbers out of order (`ep 24`, `ep 26`, `ep 25`), and `ps` showed two live
`y03_train_cv.py --arm P --fold 4` processes with different parent runners.

**Handling.** No contaminated output was used for any reported number. Specifically:

- both runners and both live training processes were killed;
- all 24 completed `oof_*`, `hist_*` and `m_*` files were moved to
  `work/QUARANTINE_double_run/` (73 files) and the logs to `logs/QUARANTINE_double_run/`;
  they are retained as a record and are **not** inputs to any analysis;
- the full 25-cell cross-fit was re-run **once**, from the frozen scripts, with no change to
  the seed, data, split, arms, architecture or hyperparameters.

**Fixes, so the class of bug cannot recur.**

1. `y_run_local.sh` now takes an exclusive `flock` on `work/.y_run_local.lock` and a second
   launch exits non-zero with `FATAL: another y_run_local.sh is already running`. Verified by
   attempting a second launch while the first held the lock.
2. `y03_train_cv.py` now checkpoints to a **PID-unique** path
   (`.m_{tag}.pid{PID}.pt`) and publishes the canonical `m_{tag}.pt` by atomic rename only
   **after** reloading its own checkpoint. Even under an accidental concurrent run, no process
   can load another's weights.

**Scope.** Local only. The Ibex seed-replicate run is a single Slurm array (`52095027`, tasks
0–29, one submission timestamp `2026-09-19T15:46:42`), one task per `(arm, fold, seed)` cell
with distinct output filenames; it was not affected and was not restarted.

**Cost.** ~1 h of local GPU time, re-run on two idle RTX 4090s. No scientific content changed.
