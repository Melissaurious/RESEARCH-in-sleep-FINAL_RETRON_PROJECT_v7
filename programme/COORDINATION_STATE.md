# COORDINATION STATE

**As of 2026-09-20, after the overnight run.** One page. Everything a coordinating session needs to
take over, or to resume after a gap.

**Start with `programme/OVERNIGHT_RUN_REPORT.md`.** This page is the standing state; that one is
what happened and what the operator must decide.

---

## 1 · Urgent, not scientific

**A live API key is in plaintext in the user's Claude configuration, in an MCP environment block,
and was printed into a session transcript.** Rotate it. Reported by a task session; deliberately not
inspected further, because inspecting it repeats the exposure rather than fixing it.

**The 88 MB Stage-1 workbench is backed up** at
`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7_SEPTEMBER/backups/`, sha256
`140a0062…d39b25`, verified on read-back, manifest at `docs/BACKUP_MANIFEST.tsv`.

## 2 · Where the work is

| tier | branch | state |
|---|---|---|
| index, governance, review, programme | `project-synthesis` | **unpushed commits; nothing pushed tonight** |
| promoted state | `main` | `94a1a78` — ⚠️ **fails `specs_exist.sh`**, see §5 item 6 |
| evidence | task branches | `T-A0`, `T-A2`, `T-REG`, `T-A23`, `T-LINT`, `T-LINT2` (void), plus 3 new |
| newly dispatch-ready | `task/T-AUDIT1…`, `task/T-GATE1…`, `task/T-P1…` | launchers frozen, worktrees created, dry-run verified |

**The GitHub remote is public.** Nothing was pushed tonight.

## 3 · Board

| state | n |
|---|---|
| `READY_WAITING_OPERATOR` | 31 |
| `BLOCKED_DEPENDENCY` | 13 |
| `LAUNCH_NOW` (7; **one** has a frozen launcher) | 7 |
| `CLOSED` | 2 |
| `VOID_REVIEW_FAILED` | 1 |

Machine-checkable: `programme/PREFLIGHT_STATUS.tsv`. **Exactly one task is launchable:**
`T-AUDIT1-circular-control-sweep`. Full register: `programme/ALL_DOWNSTREAM_TASKS.tsv` (54 tasks,
all twelve goals). Dependencies: `programme/SCIENTIFIC_DAG.md`. Schedule:
`programme/PARALLEL_EXECUTION_PLAN.md`.

## 4 · What the five reviews decided

| review | thread | verdict |
|---|---|---|
| Batch One (earlier) | `01a0bc53` | **FAIL** — 3 FAIL, 2 ACCEPT_WITH_CHANGES |
| T-A0 correction | `01a0bc96` | ACCEPT_WITH_CHANGES, 7 changes, **all applied** |
| T-A2 correction | `01a0bc97` | ACCEPT_WITH_CHANGES, 7 changes, **all applied** |
| T-LINT2 v2.0.0 | `01a0bc99` | **REJECT** |
| T-LINT2 v3.0.0 | `01a0bcac` | **REJECT** → `VOID` |
| the downstream plan | `01a0bcb2` | **REJECT** → all coordinator-fixable findings applied |

⛔ **Nothing has ever been promoted in this project**, and nothing is promotable: `human_input_audit`
appears nowhere but the spec that defines it.

## 5 · Open decisions, operator only

1. **Task-session dispatch.** The host refuses to spawn one (`Create Unsafe Agents`). **This blocks
   the entire programme.** Three options in `PARALLEL_EXECUTION_PLAN.md` §7.
2. **Rotate the exposed key.**
3. **Clear `human_input_audit`.** It gates every claim and blocks no computation.
4. **The inspection contradiction.** `WORKING_RULES` §3 says inspection depletes; the population
   ledger says it does not and that `RT-EXACT-501561` can still confirm. **They cannot both hold**,
   and 21 tasks wait on the answer.
5. **Authorise or refuse each launch** on `RT-EXACT-501561`, `RETRON-LOCI`, `NCRNA-16458`.
6. **Repair `docs/BLOCKED.md` on `main`** — one broken relative path fails `specs_exist.sh` and
   blocked every task worktree. Fixed on the three new task branches; `main` is promoted state.
7. **Fix `general/tools/status.sh`** — it defaults `IBEX_HOST=ibex`, and that alias resolves to
   `vsc509-03-l`, the vscode pool `IBEX.md` forbids for scripted access. A governed pin change.
8. **Push or do not.** Remote is public.
9. Plus decisions 11–17 in `OVERNIGHT_RUN_REPORT.md` §10: duplicate tasks, panel overlap, Tier B
   allocation, four circular controls, the undeclared 157-character bar, `T-P3`'s scope.

## 6 · Findings that outlive tonight

| # | finding |
|---|---|
| 1 | The interval generator behind the landed pairing results covers **0.65** against a nominal 0.95 **on a fitted fixture**. A warning about a shared method, not a verdict on unexamined intervals. |
| 2 | Effective sample size settles three ways; **≈463** is the estimator's actual effective n. |
| 3 | **No lineage-blocked interval exists for the C-28 estimand.** The 50 %-identity grouping nests inside the inference unit, so it cannot block over it. `T-P1` exists to produce one that can. |
| 4 | The **0.217 %** registry-coverage endpoint is **withdrawn**; the inventory is kept. |
| 5 | Published cross-pair evidence is **7 experimental blocks**, not 56 rows, and **zero** carry a numeric value. |
| 6 | Five review conclusions reversed on looking outside the declared scope. The cause was scope, every time. |
| 7 | **`T-A19` scores a CM-derived caller against CM-derived calls** — the circularity the DAG claimed to have broken. |
| 8 | **`T-A5b1` and `T-R1` are the same task**, and would spend the project's strongest anchor twice. |

## 7 · Standing rules a successor must not relax

- Controls are tasks, they run first, and they block.
- **A control that aggregates across substrates cannot detect a dead substrate.** *(Learned tonight,
  from an instrument built to detect exactly that failure.)*
- **A catcher chosen after watching the mutant escape is not a preregistered catcher.** *(Learned
  tonight, expensively.)*
- **When a control fails and the budget is spent, the task is over.** Not "over unless the fix is
  obviously right".
- Task validity is not hypothesis truth. A refuted hypothesis is a **successful task**.
- A biological contrast may not be a blocking control unless independently established.
- Populations deplete. **`INSPECTED` is not `EXHAUSTED`** — check whether the ledger says the
  population can still serve as confirmation before calling any use of it free.
- No number in prose without a table cell behind it.
- Prior work supplies assets and bounded negatives. Its numbers are unverified until re-derived.
- Fail closed. If a reviewer is unavailable, record it and stop; never substitute silently.
- **"Ready to launch" is not true until the chain has been run.** Two blockers tonight were
  invisible to reading and obvious to a `--dry-run`.
