# Execution incidents — recorded, not hidden

Execution safety only. **No scientific parameter, rule, population, threshold or verdict in
this gate was changed by anything on this page.** The frozen design in
`control/PREDECLARATION.md` and `control/REPAIR_1.md` is untouched.

---

## INC-1 · `s04_within_retron.py` was wrongly declared dead, and a duplicate was launched

**2026-09-18, during g6 execution.**

### What happened

1. `s04_within_retron.py` was launched as a background task (`b4x5snha3`) while
   `s03_between_family.py` (`b87yqx3qy`) was still running.
2. Its output showed the `DF_subtype` and `PL_subtype` analyses completing, then no further
   output while the `LABEL_FREE` analysis ran.
3. The executing session ran `ps aux | grep s04`, saw no match, observed that
   `tables/g6_within_retron_rho.tsv` did not exist, and **concluded the process had died** —
   attributing it, in text, to "likely memory contention with s03".
4. On that wrong conclusion a **second, duplicate** `s04` process (`bb18hyydl`) was launched.
5. The operator challenged the unevidenced cause. Checking properly showed `b4x5snha3` was
   **still running the whole time**. It was then stopped, and the later run kept.

### What was actually wrong with the diagnosis

| claim made | status |
|---|---|
| "s04 died" | **FALSE.** The task was still running and was stopped manually. |
| "likely memory contention" | **UNEVIDENCED, and contradicted.** `free -g` at the time: **251 GB total, 230 GB available, 18 GB used.** Both scripts hold a 354,102 x 150 `float32` matrix, about 212 MB each. Memory contention is not a plausible cause. |
| "`ps` shows it is not running" | **INVALID METHOD.** `ps` in this sandbox is namespace-limited and lists only the current command's own processes (PIDs 1-6). It **cannot** see background tasks, so it could never have detected the process either way. |
| "the output table is missing, so it failed" | **INVALID INFERENCE.** `s04` writes all of its tables in one block at the very end; absence of output mid-run is expected, not evidence of failure. |

### Was it an OOM kill?

**No evidence of one, and the question cannot be fully closed from inside the sandbox.**

* `dmesg` returns `read kernel buffer failed: Operation not permitted`; `journalctl -k` returns
  nothing. Kernel OOM records are **not readable here**, so their absence is not evidence of
  absence.
* What *is* positive evidence against OOM: 230 GB of 251 GB available, and a per-process
  working set of roughly 0.2 GB.
* The task's captured output ends after `PL_subtype` with **no Python traceback and no
  `[exited with code N]` marker**, whereas tasks that really finished
  (`b87yqx3qy`, `bejqzp4p3`) both end with `[exited with code 0]`. That pattern is consistent
  with a task **still running**, which is what it turned out to be.

**Conclusion: there was no failure to explain.** The only failure was in the diagnosis.

### Corrective actions, adopted for the rest of this gate

1. **Background task state is read with `TaskList` / `TaskGet`, never with `ps`.**
2. **Heavy analysis steps run serially**, one at a time.
3. **`free -g` is checked before launching a heavy step**, and the reading is recorded.
4. **A step is never assumed dead from the absence of its output file**, because every step in
   this gate writes its tables at the end.
5. Processes belonging to other project sessions are never inspected or signalled. The `ps`
   namespace limitation means they are not visible from here in any case.

### Effect on the science

**None.** `s04` is deterministic: same inputs, same seed (`20260918`), same declared
labellings. The duplicate and the original were computing identical values, and the retained
run is the one whose numbers are landed. No result was selected on the basis of which process
finished.
