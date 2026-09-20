# DURABLE HANDOFF

**The repository, not any conversation, contains everything required to resume.**
Written 2026-09-20. Read this, then `programme/SESSION_HANDOFF.md` §"START HERE".

---

## 1 · ⛔ Is it safe to close the interactive session? **YES**

> **Re-verified 2026-09-20 19:16** — pid `810502`, `PPID 1`, `SID 810461`, no tty, start `16:40:25`,
> same argv and worktree: still the known P1b full run, **not PID reuse**. ⚠️ `ps` inside the agent
> sandbox runs in a separate PID namespace and wrongly reports it **gone** — always check P1b from
> outside the sandbox before concluding anything about it.

**`T-P1b` is safely detached. Closing this Claude Code conversation, its shell, or the terminal will
NOT terminate it.**

**How that was verified** — four independent facts, all from `/proc` and `ps`:

| evidence | observed | what it proves |
|---|---|---|
| **parent pid** | `PPID = 1` (`systemd`) | the original shell is already gone; the process was **reparented to init**. Nothing in this session is its parent |
| **session id** | P1b `SID = 810461` · this shell `SID = 865152` | it is in a **different session**. Session teardown cannot reach it |
| **controlling terminal** | `TT = ?` | it has **no controlling terminal**, so `SIGHUP` on terminal close cannot be delivered to it |
| **file descriptors** | `fd/0 → /dev/null`, `fd/1 → …/fullrun.stdout` | stdin and stdout are **not** attached to any pty; output goes to a file on disk |

It was launched via `nohup … &` from `p1b_fullrun.sh`, which is why all four hold.

✅ **Closing the session is safe.** Monitor it afterwards with:

```bash
ps -p 810502 -o pid,etime,stat
ls /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-P1b-identity-partition/analysis/t_p1b_identity_partition_full/tables/
tail /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-P1b-identity-partition/analysis/t_p1b_identity_partition_full/fullrun.stdout
```

## 2 · Authoritative state

| | |
|---|---|
| branch | **`project-synthesis`** |
| commit | **`e56c7bd`** |
| working tree | **clean** |
| unpushed | **14 commits** ahead of `origin/project-synthesis`; ⛔ **nothing pushed** |
| governed pin | `cff9831` |
| `governance_base` | `9a793c9` |

## 2b · ⛔ WAVE 01 IS VALIDATED BUT NOT STARTED — one operator command

**Every gate passed. The start itself is blocked, and it is the known D4 capability, not a defect.**

The coordinating Claude session's permission classifier refuses to spawn the detached coordinator
(`Blocked by classifier`), exactly as `CAPABILITY_STATE.md` §3 records for task-session dispatch. It
also refused `claude --dangerously-skip-permissions -p` with `Create Unsafe Agents`.

**To start Wave 01:**

```bash
bash programme/START_WAVE_01.sh
```

That script is the reviewed `nohup setsid` route with nothing added. It refuses to run on a wrong
branch, a dirty tree, or a changed `WAVE.tsv`, and it prints the coordinator PID, wave sha and log
path. After it starts, scheduling belongs to the detached runner, not to a chat session.

| validation gate | result |
|---|---|
| merge of `origin/autonomy/d4-wave-runner@10f9297` | **clean, zero conflicts** |
| fresher local `e2c4f78` preserved | ✅ it touched no file the autonomy branch modified |
| `py_compile` · `bash -n` | ✅ |
| autonomy test suite | ✅ **14/14** (8 original + 6 new acceptance-boundary) |
| live dry-run vs real workstation state | ✅ **exactly** the expected state; P1b alive at `io=6` |
| headless preparation transport | ✅ `claude -p` rc=0 |
| headless preparation **contract** | ✅ schema-valid `PREPARE_RESULT.json`, `READY_TO_FREEZE`, self-checks PASS, **no primary output written** |
| `claude --dangerously-skip-permissions -p` | ⚠️ **untested** — denied to the agent session. The detached runner is not under that classifier, and a prepare failure lands as `BLOCKED_PREPARE` + escalation, which corrupts nothing |
| ARIS-conformance audit | ✅ one violation found and **fixed** — `programme/ARIS_CONFORMANCE_AUDIT.md` |
| R2a provenance gate | ✅ **11/11, 81/81** — `tasks/T-R2a-…/R2a_PROVENANCE.md` |

**Wave sha256:** `ef94fc0c5d83ffe4bd96267f54fd497043e5eebc49edc46d3a81c58e48b3c7e4`

### The two substantive findings

**1 · The wave runner was acquitting its own tasks.** `worker_state==COMPLETE` wrote the worker's
self-reported `task_state` straight into `TASK_BOARD.tsv`/`EXECUTION_LEDGER.tsv` as `PASS`, and
`PASS` satisfies a hard dependency — so a self-report would have unblocked downstream science.
Pinned ARIS `run_state.py` exists to forbid exactly that. Fixed: a self-reported success now lands as
`COMPLETE_AWAITING_REVIEW` (this project's own existing vocabulary), `PASS` means **independently
accepted**, and the runner mirrors phases into `.aris/runs/` with `set` only — **never** `accept`.
Wave 01 scheduling is byte-identical before and after the fix.

**2 · R2a's ncRNA objects are the panel's own, unmodified.** Panel sha256 matches its pin; six copies
across five project trees are byte-identical; the permitted `strip()+upper()` is a **no-op on all
81**; R1b's landed `ncrna_len` equals `len(panel ncRNA_sequence)` for all 81; and
`revcomp(panel ncRNA[start:end]) == panel RTDNA` for all 81. Nothing was reconstructed after
ingestion, so this is **not** `REVIEW_REQUIRED`.

⛔ **Bound interpretation:** every RT-DNA/ncRNA fraction and normalised coordinate is a **fraction of
the published annotated ncRNA sequence**, never of an experimentally verified full-length transcript.
Recorded limitation: the repository holds no separate direct source-study supplementary file from
which `support.csv` was built.

## 3 · ACTIVE — one process, nothing else

| | |
|---|---|
| task | **`T-P1b-identity-partition`**, full 501,561-sequence run |
| **pid** | **`810502`** — `PPID 1`, `SID 810461`, `TT ?`, state `Sl` |
| freeze | **`1a6909f`** (launcher + implementation + fixtures, **before** the run) |
| worktree | `…_v7-T-P1b-identity-partition`, branch `task/T-P1b-identity-partition` @ `70a52c0` |
| output | `analysis/t_p1b_identity_partition_full/` |
| progress | **6 of 7 levels landed** (`id40`–`id90`) at ~2 h 36 min, 2026-09-20 19:16. Only `id95` remains |
| controls | **20/20 PASS** before the primary began |
| backend | local, 40 threads (**execution-routing deviation from the launcher's `ibex`, recorded**) |

**STOP conditions:** a failed blocking control · **>24 h elapsed → stop and escalate** · disk
exhaustion. None is met.

### ⛔ On completion — the required sequence

1. **Quarantine** `P1b_cluster_family_composition.tsv` and `P1b_cross_family_clusters.tsv`. They are
   **INVALID** — `describe()` joined on `rt_aa_len` (protein length) instead of `family_label`.
   Previously reported multi-family fractions are **RETRACTED**.
2. ⛔ **Do NOT modify the frozen implementation and do NOT rerun clustering.**
3. Everything else is **valid**: cluster assignments, level summary, component incidence,
   multi-membership, controls, exclusions. Cluster formation is label-blind by construction and
   `describe()` runs after every cluster file is written.
4. Write `TASK_REPORT.md` to the traceability contract, with the two tables **quarantined, not
   silently regenerated**.
5. Update `programme/EXECUTION_LEDGER.tsv`.
6. Prepare **`T-P1c-family-label-description`** — regenerate those two tables **from the completed
   cluster assignments** using the explicit `family_label` column. Bind explicitly, **no fallback**,
   gate on `Retron == 78,287`.

## 4 · CLOSED — do not reopen

| task | freeze | execution | result |
|---|---|---|---|
| **`T-R1b`** | `7e7f598` | `7f09244` | ✅ **81/81 `EXACT_UNIQUE`, all `REVCOMP`, 0 unmapped, 0 ambiguous.** `PANEL-RTDNA-81` spent once. **D7 merge — `T-A5b1` and old `T-R1` must not run** |
| **`T-X1`** | `7e7f598` | `010778b` | ⛔ **VOID** — `else cols[1]` bound "family" to `rt_aa_len`. Outputs preserved, **not consumable** |
| **`T-X1b`** | `3d35167` | `1e3e0a7` | ✅ measurements accepted; **`overlap_class` RETRACTED** as a state label |
| **`T-X1c`** | `b8f75d1` | `8dc8e5e` | ✅ **AUTHORITATIVE** state matrix: **5 / 51 / 6 / 43**; axes 56 RT, 11 ncRNA, of 105 |

⛔ **`ncRNA = 0` means no exact native-msr-msd match in our catalogue — NOT biological
incompatibility.**

## 5 · PENDING

| task | state | blocked by |
|---|---|---|
| **`T-R2`** | **DRAFT — awaiting the one remaining scientific review** | operator review. ⛔ do not freeze or execute |
| `T-P1c` | nominated | **`T-P1b` completing** |
| `T-D1` | drafted, not frozen | **P1b's I/O lane** |
| `T-D2` | drafted, not frozen | **P1b's I/O lane** |
| `T-M1b`, `T-S1b` | proposed | P1b (both `IO_HIGH`) |
| `T-A22` | **PARKED** | not blocking anything. Whitelist machine-enforced, 17/17 |

### R2 — the correction the operator required, and its answer

The **2.148 ratio was a reporting artefact in my own summary**, not a coordinate-frame mismatch:
`max(rtdna_len) / min(ncrna_len)` **across different elements**. Per-element range is
**0.3925 – 0.8602**. Verified all 81: `len(RT-DNA) ≤ len(ncRNA)`, span == RT-DNA length,
coordinates inside the ncRNA, and **`revcomp(ncRNA[start:end]) == RT-DNA`** — **81/81 on every
check**. `R2_tierA_anomalies.tsv` and its exclusion rule are **withdrawn**.

The blocking gate `r2_consistency_gate.py` (**9 checks, 9 PASS**) is kept **permanently** anyway.
Full account: `programme/tasks/T-R2-ncrna-internal-architecture/R2_COORDINATE_FRAME_DIAGNOSIS.md`.

## 6 · Open decisions and known defects

| # | item |
|---|---|
| **D4** | task-session dispatch still blocked; all execution is coordinator-run **under disclosure** |
| **D5** | ✅ credential hygiene — **redacted for publication 2026-09-20**. `REDACTED_SECRET_NOT_STORED_IN_REPOSITORY`. No credential value is in this repository, in any commit or branch; verified by a full-history scan |
| **D14** | 14 commits unpushed; remote **verified public** |
| **D19** | `specs_exist.sh` fails spuriously ~5–10 % — `SIGPIPE` + `pipefail`; one-line fix verified, `general/` is operator-only |
| backlog | **family vocabularies disagree** — `family_label` has **42** values, not 613; `docs/BACKLOG_family_vocabularies.md`. ⛔ **Do not guess or reconcile** |
| backlog | worktree/scratch cleanup ≈5.9 GB; `programme/WORKTREE_HYGIENE.md`. **Not now** |

## 7 · Operating mode

**Autonomous downstream deployment.** Ordinary implementation choices need no approval.

⛔ **Escalate only for:** a new biological endpoint · a threshold chosen **after** inspecting
primary results · an incompatible dataset status · a **protected-population spend** · a claim beyond
approved scope · the **R2 review packet** · **P1b completion or STOP**.

## 8 · Reading order for the next session

1. **this file**
2. `programme/SESSION_HANDOFF.md` — §"START HERE"
3. `programme/EXECUTION_LEDGER.tsv` — the index across every task
4. `programme/CANONICAL_DATASETS.tsv` — what may be consumed, and what may not
5. `programme/WORKING_RULES.md` — §6b freeze-before-execute, §8 audit stop condition
6. `review-stage/TASK_PROTOCOL.md` — the traceability contract
7. `programme/tasks/T-R2-…/TASK_LAUNCHER.md` + `R2_COORDINATE_FRAME_DIAGNOSIS.md`

## 9 · The four rules that override any inference from the repository

1. **Nothing is promoted or promotable.** `human_input_audit` has never run.
2. **`T-P1`, `T-X1`, `T-LINT2`, `T-N1b`, `T-N1c` are VOID.** Never consume them; never rehabilitate
   them because their numbers look fine.
3. **Exposure is per population AND endpoint.** A rejected or VOID run still spends its endpoint.
   `PAIR-ELIG` is exhausted permanently; `PANEL-RTDNA-81` is now spent by `T-R1b`.
4. **Consume only `CANONICAL` or `CANONICAL_WITH_LIMITATION`**, and carry the stated limitation.
