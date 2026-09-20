# CAPABILITY STATE — what this programme can and cannot actually do

**Measured 2026-09-20 by the coordinating session.** Every row says **which context it was measured
from**, because this project has now recorded **four** capabilities as absent that were present at
the root and hidden in a spawned context.

---

## 1 · Verified present

| capability | state | evidence | measured from |
|---|---|---|---|
| local CPU | 48 logical / 24 physical | `nproc` | sandbox |
| local RAM | 251 GB, 232 GB available | `free -g` | sandbox |
| local GPU | **2 × RTX 4090, 24,564 MiB each, both idle** (247 MiB / 11 MiB used, 0 % util) | `nvidia-smi --query-gpu` | ⚠️ **outside the sandbox** |
| local disk | 2.8 TB free of 7.0 TB, single NVMe | `df -h` | sandbox |
| Ibex login | reachable, key-based, `login509-02-l` | `ssh -o BatchMode=yes rioszemm@ilogin.ibex.kaust.edu.sa` | ⚠️ **outside the sandbox** |
| Ibex queue | empty, 0 jobs | `squeue --me` | outside the sandbox |
| Ibex env | `/ibex/user/rioszemm/conda-environments/retron_tradicional` present | `ls -d` | outside the sandbox |
| Ibex `batch` partition | 14-day limit, 99 idle nodes | `sinfo` | outside the sandbox |
| local conda env | `retron_tradicional`, python 3.12.12 | `conda activate` | sandbox |
| independent reviewer | Codex available, fresh read-only threads | four dispatched today: `01a0bc96`, `01a0bc97`, `01a0bc99`, `01a0bcb…` | sandbox |
| git worktrees | creatable | ⚠️ **outside the sandbox only** | both |

## 2 · Verified absent or blocked

| capability | state | consequence |
|---|---|---|
| **task-session dispatch** | ⛔ **BLOCKED_CAPABILITY** | **the single largest blocker in the programme** — see §3 |
| `rg` (ripgrep binary) | absent; `rg` is a Claude Code **shell function**, not a binary | any tool shelling out to `rg` silently finds nothing. Cost this programme one dead instrument — see §4 |
| SLURM client on `borg` | absent **by design** | not a defect. `general/site/IBEX.md`: every scheduler command runs on Ibex over SSH |
| sandbox write outside the synthesis worktree | blocked | worktree creation and all task-worktree writes need `dangerouslyDisableSandbox` |
| sandbox network DNS | blocked | `ilogin.ibex.kaust.edu.sa` does not resolve inside the sandbox; it resolves outside it |
| sandbox GPU device nodes | hidden | `nvidia-smi` inside the sandbox reports no driver. **The GPUs are present and idle** |

## 3 · ⛔ Task-session dispatch, the blocker that shapes this whole run

`WORKING_RULES` §1: the coordinating session *"never runs a scientific analysis itself"*. Execution
belongs to task sessions, one per task, one worktree each, dispatched through
`programme/launch_task.sh`.

**The host harness refuses to spawn one.** A headless `claude -p` dispatch is denied by the
permission classifier with `Create Unsafe Agents`. `launch_task.sh` ends in
`exec claude --dangerously-skip-permissions`, which is interactive and cannot be queued overnight.

| consequence | detail |
|---|---|
| 22 Wave-1 tasks specified and gated | **none launched** |
| `T-LINT2` executed by the coordinator | only because the operator instructed this session directly to repair and rerun it; disclosed in its report and its amendment |
| role separation | **not achieved**, and not claimed anywhere |
| the independent review | became the **only** outside check on `T-LINT2`, which is why its REJECT was implemented in full |

**Operator decision required.** Options in `PARALLEL_EXECUTION_PLAN.md` §7: **(A)** a Bash
permission rule allowing dispatch, **(B)** manual `bash programme/launch_task.sh <task-id>` per
task, **(C)** authorise the coordinator to execute `ZERO`/`CPU_SMALL` tasks directly with mandatory
disclosure. **Recommended: A, with B as tonight's fallback.**

## 4 · ⛔ `general/tools/status.sh` points at the wrong host

`status.sh` defaults `IBEX_HOST=ibex`. On this machine that alias resolves into the **vscode pool**:

```
ssh ibex                                  hostname → vsc509-03-l
ssh rioszemm@ilogin.ibex.kaust.edu.sa     hostname → login509-02-l
```

`general/site/IBEX.md` says explicitly: **do not use `vscode.ibex.kaust.edu.sa` for scripted
access** — it is load-balanced and at least one member hangs at SSH userauth, which looks exactly
like an account problem and is a sick node. `WORKING_RULES` §4 flagged this as a *latent* break.
**It is live.**

> **Every scripted Ibex call sets `IBEX_HOST=rioszemm@ilogin.ibex.kaust.edu.sa` explicitly.**
> Fixing the default is a `general/` change and therefore a governed pin move with a decision
> record — not something this session does.

## 5 · The pattern, now with four instances

Each time, the capability was **present at the root and absent in a spawned context**, and each time
the spawned context's report was believed.

| # | read as absent | actually |
|---|---|---|
| 1 | an independent reviewer | a deferred tool arriving as a bare name |
| 2 | the governance layer | a submodule that had not initialised in a task worktree |
| 3 | two idle GPUs | device nodes hidden by the sandbox |
| 4 | **every content search in the prior-work sweep** | `rg` resolved to a shell function that `xargs` could not exec |

Instance 4 was found today, by this session, in an instrument this session wrote — and **its own
control did not catch it**, because the control asked whether the term was found in content **or**
in directory names. Directory names still matched, so every root reported `PASS` while the content
substrate returned zero for all 24 topics.

> **The rule that follows, and it is the one to keep:** a control that aggregates across substrates
> cannot detect a dead substrate. Controls are now **per substrate**, and a dead one reports
> `SUBSTRATE_BLOCKED`, under which absence is not reportable.

**Before recording any capability as absent, establish which context you are measuring from, and
make sure the control can tell "absent" from "not looked".**
