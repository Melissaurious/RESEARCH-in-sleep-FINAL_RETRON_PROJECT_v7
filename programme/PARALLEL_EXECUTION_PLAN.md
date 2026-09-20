# PARALLEL EXECUTION PLAN

**As of 2026-09-20.** Derived from `programme/SCIENTIFIC_DAG.md`, which was written first on
purpose. Task register: `programme/ALL_DOWNSTREAM_TASKS.tsv` (53 tasks).

> **This plan schedules compute. It does not decide science.** Every `READY_WAITING_OPERATOR` item
> stays where it is, and no wave consumes an `UNEXPOSED_CONFIRMATORY` population.

---

## 1 · Verified capacity, measured 2026-09-20, not assumed

| resource | measured | how |
|---|---|---|
| local CPU | **48 logical / 24 physical** | `nproc` |
| local RAM | **251 GB total, 232 GB available**, load ~2.9 of 48 | `free -g`, `uptime` |
| local GPU | **2 × RTX 4090, 24,564 MiB each, 247 MiB and 11 MiB used, 0 % utilisation** | `nvidia-smi`, **outside the sandbox** |
| local disk | `/` on `nvme0n1p2`, **2.8 TB free of 7.0 TB** | `df -h` |
| Ibex login | **reachable**, `login509-02-l` | `ssh -o BatchMode=yes rioszemm@ilogin.ibex.kaust.edu.sa` |
| Ibex queue | **empty**, 0 jobs for this user | `squeue --me` over SSH |
| Ibex env | `/ibex/user/rioszemm/conda-environments/retron_tradicional` **present** | `ls -d` over SSH |
| Ibex `batch` | 14-day limit, **99 idle nodes**, 172 mixed, 81 allocated | `sinfo` over SSH |

### 1a · Two context artefacts, and one live defect

⚠️ **Inside the Bash sandbox, `nvidia-smi` reports no driver and DNS does not resolve
`ilogin.ibex.kaust.edu.sa`.** Both are **sandbox artefacts**, confirmed by re-running outside it.
This is the fourth time in this programme that an absence turned out to be a property of the
measuring context. **Before recording any capability as absent, establish which context you are
measuring from.**

⛔ **`status.sh` defaults `IBEX_HOST=ibex`, and on this host that alias resolves into the vscode
pool** — `ssh ibex hostname` returns **`vsc509-03-l`**, while
`ssh rioszemm@ilogin.ibex.kaust.edu.sa hostname` returns **`login509-02-l`**. `general/site/IBEX.md`
states plainly: *do not use `vscode.ibex.kaust.edu.sa` for scripted access* — it is a load-balanced
pool with a documented member that hangs at SSH userauth. The latent break flagged in
`WORKING_RULES` §4 is **confirmed live**.

> **Every scripted Ibex call in this programme must set
> `IBEX_HOST=rioszemm@ilogin.ibex.kaust.edu.sa` explicitly.** Do not rely on the alias.

## 2 · The binding constraint is I/O, not CPU

`/home/borg` and `$TMPDIR` are the same NVMe. With 48 idle cores and 232 GB free, concurrency
saturates the disk first, so the schedule is written in **I/O lanes**, not core counts.

| lane | concurrency | tasks |
|---|---|---|
| `IO_HIGH` | **1 at a time, local** | `T-REG3` content hashing, `T-REG4` kind sweep, `T-N1` neighbourhood extraction, `T-M1` embedding cache verification, `T-S1` structure inventory |
| `IO_MEDIUM` | up to 4 local | most `CPU_SMALL`/`CPU_MEDIUM` work |
| `IO_LOW` | unlimited | `ZERO` tasks, which read landed tables and write new ones |
| Ibex | independent of all lanes | `T-C1`, `T-P1`, `T-F2`, `T-P2`, `T-P3` |

**A queued Ibex job blocks no local lane**, and a saturated local `IO_HIGH` lane blocks no Ibex
submission. That is the point of using both.

## 3 · Routing rule

| send local | send to Ibex |
|---|---|
| `ZERO` and `CPU_SMALL` | `CPU_HIGH`, `MEMORY_HIGH` |
| every pilot and preflight | large MMseqs2 / Foldseek / alignment jobs |
| lightweight CPU work | highly sharded array jobs |
| GPU work fitting in 24 GB VRAM | jobs over ~2 h, or needing >24 GB VRAM |

**A cheap pilot is mandatory before any Ibex-scale run**, with its size and its expected result
declared in the launcher. One acceptance criterion in this project had a ceiling of 84.8 % against a
required 95 % and was discovered only after the instrument was frozen. A pilot costs minutes.

**The method may not change because the backend changed.** Backend, job ID, software version, seed
and every input hash are recorded wherever it ran.

## 4 · Wave 1 — launchable tonight under the operator's standing authorisation

Every task below satisfies **all** of: `NO_POPULATION_SPEND` or an already-exhausted population; no
new hypothesis, threshold, endpoint or control choice; specification reproducible from settled
decisions; launcher frozen before execution; no artifact, population or resource collision.

| # | task | class | backend | lane | why it is safe |
|---|---|---|---|---|---|
| 1 | `T-LINT2-prose-numbers-gated` | ZERO | local | LOW | **done**, v3.0.0, 32/32 blocking controls; awaiting review |
| 2 | `T-GATE1-consumption-gate` | CPU_SMALL | local | LOW | pure engineering, no population, no science |
| 3 | `T-AUDIT1-circular-control-sweep` | ZERO | local | LOW | reads launchers and control tables only |
| 4 | `T-AUDIT2-task-report-backfill` | ZERO | local | LOW | reads landed artifacts; writes reports, promotes nothing |
| 5 | `T-REG2-registry-coverage-validated` | CPU_SMALL | local | MEDIUM | fixtures are constructed; endpoint stays unpromoted |
| 6 | `T-REG4-kind-extension-sweep` | CPU_SMALL | local | **HIGH, serial** | inventory extension, no interpretation |
| 7 | `T-REG3-content-hash-pass` | CPU_MEDIUM | local | **HIGH, serial** | hashing only; answers a stated open question |
| 8 | `T-M1-embedding-cache-verification` | CPU_SMALL | local | **HIGH, serial** | identity, dimension and coverage of existing caches |
| 9 | `T-S1-structure-asset-inventory` | CPU_SMALL | local | **HIGH, serial** | registration is not interpretation |
| 10 | `T-LINT4-cross-worktree-index` | ZERO | local | LOW | extends an index; changes no criterion |
| 11 | `T-M2-landed-interval-coverage-sweep` | CPU_MEDIUM | local | LOW | PAIR-ELIG already exhausted; nothing further is spent |
| 12 | `T-C1-rt-core-extraction` | CPU_HIGH | **ibex** | — | preparation; RT-EXACT inspected, not consumed |
| 13 | `T-P1-relatedness-backbone` | CPU_HIGH | **ibex** | — | **the trunk**; four HARD edges wait on it |
| 14 | `T-D1-annotation-disagreement` | CPU_SMALL | local | MEDIUM | RETRON-LOCI already exposed by Stage 1 |
| 15 | `T-D2-taxonomic-distribution` | CPU_SMALL | local | MEDIUM | same |
| 16 | `T-N1-neighbourhood-extraction-qa` | CPU_MEDIUM | local | **HIGH, serial** | extraction and QA only; comparison is `T-N2` |
| 17 | `T-F1-motif-scan` | CPU_MEDIUM | local | MEDIUM | feature extraction, no comparative claim |
| 18 | `T-F2-domain-architecture` | CPU_HIGH | **ibex** | — | feature extraction, no comparative claim |
| 19 | `T-P2-character-economy-audit` | CPU_MEDIUM | **ibex** | — | tests S09's own declared reopening condition |
| 20 | `T-S2-foldseek-calibration` | CPU_MEDIUM | local | MEDIUM | method calibration on external material |
| 21 | `T-P3-relatedness-representation` | CPU_HIGH | **ibex** | — | representation, explicitly not a topology claim |
| 22 | `T-E1-character-source-probe` | CPU_MEDIUM | **ibex** | — | probe only; a positive result is a proposal |

**22 tasks. 6 Ibex, 16 local, of which 5 share one serialised `IO_HIGH` lane.**

⛔ **Wave 1 did not launch tonight.** See §7. The plan is what *would* launch; the capability to
dispatch it is missing, and that gap is the single largest blocker in this report.

## 5 · Wave 2 — opens automatically when Wave 1 lands and is reviewed

| task | opens when |
|---|---|
| `T-A0b-lineage-partition-intervals` | `T-P1` produces a partition not nested in the component unit |
| `T-F3-retron-feature-contrast` | `T-P1` **and** `T-F1`, `T-F2` |
| `T-N2-neighbourhood-lineage-comparison` | `T-P1` **and** `T-N1` |
| `T-A10-genomic-architecture` | `T-N1`, **and** its launcher is written |
| `T-S3-structural-core-interpretation` | `T-S2` calibration **and** `T-A7` — and `T-A7` is operator-gated |
| `T-A17-core-sensitivity-arm` | `T-A16`, which is operator-gated |

**Wave 2 is not auto-promotable.** Each result still needs its own independent review before
anything downstream consumes it.

## 6 · What is deliberately withheld, and why

| withheld | reason |
|---|---|
| `T-A5b1`, `T-R1` | touch `PANEL-RTDNA-81`, **unexposed confirmatory** and the strongest anchor in the project |
| `T-A22` | `PANEL-PRODUCERS-67-36` is the **only** measured functional contrast anywhere here |
| `T-A7` | `STRUCT-62` Tier B is unopened and partly design-inspected, so not blind |
| `T-A16`, `T-A6`, `T-A1`, `T-A10` | launchers unwritten; writing one is a scientific specification |
| `T-A2b` | the matching design is a scientific choice, not a parameter |
| `T-E2`, `T-I1`, `T-S12-floor`, `T-A3a` | each requires declaring a number in advance — that declaration **is** the decision |
| `T-A23b/c/d` | need external retrieval, and `T-A23c` is the highest-yield action in the programme |
| `T-S07-reopen` | `CLOSED_CURRENT_DESIGN` with five predeclared reopening conditions |
| `T-LINT3` | needs human adjudication by definition |
| `T-HIA` | operator only, and it gates every claim in the project |

**No wave consumes an `UNEXPOSED_CONFIRMATORY` population.** Five tasks touch one; all five are
`READY_WAITING_OPERATOR`, and the operator authorises each spend individually.

## 7 · ⛔ The blocker: there is no way to dispatch a task session

`WORKING_RULES` §1 gives the coordinating session one job — authorise tasks, create worktrees,
receive reports, run the consumption gate — and forbids it from running a scientific analysis
itself. Execution belongs to **task sessions**, one per task, each in its own worktree.

**The host harness refuses to spawn one.** A headless `claude -p` dispatch is denied by the
permission classifier as `Create Unsafe Agents`. `programme/launch_task.sh` ends in
`exec claude --dangerously-skip-permissions`, which is interactive and cannot be backgrounded into
an overnight queue.

**Consequence, stated plainly:**

- The 22 Wave-1 tasks are **specified, gated and ready**, and **none of them launched**.
- `T-LINT2` ran anyway, because the operator instructed this session directly to repair and rerun
  it. Its report says in its own "what this does not show" section that role separation failed.
- Running the other 21 the same way would mean the coordinating session executing the entire
  programme, which is the opposite of what the separation exists for.

**Three ways out, for the operator to choose between** — this is the decision that unblocks the
most work:

| option | what it costs |
|---|---|
| **A** — add a Bash permission rule allowing `claude -p` dispatch from `launch_task.sh` | a settings change; restores the designed model exactly |
| **B** — run `bash programme/launch_task.sh <task-id>` manually per task in a terminal | operator time, one terminal per task; the model is preserved |
| **C** — authorise the coordinating session to execute `ZERO`/`CPU_SMALL` tasks directly, disclosing it in every report | throughput now, role separation gone, and the independent review becomes the only check |

**Recommendation: A, with B as the immediate fallback tonight.** C should be reserved for tasks with
no population and no inference, and even then every report must say so, as `T-LINT2`'s does.

## 8 · Collision matrix — why these may run together

Two tasks may run concurrently only if **all four** hold (`WORKING_RULES` §3):

| check | how Wave 1 satisfies it |
|---|---|
| **no shared writes** | one `output_directory` per task, one worktree per task, disjoint by construction |
| **no unfinished-producer reads** | Wave 1 reads only landed Stage 1 artifacts and the T-REG inventory; no Wave-1 task reads another Wave-1 task's output |
| **no population collision** | 18 tasks are `NO_POPULATION_SPEND`; the rest touch `RETRON-LOCI` or `RT-EXACT`, both already inspected, where concurrent inspection depletes nothing further |
| **no criterion coupling** | no Wave-1 task's threshold or selection rule is chosen from another's output. `T-P1`'s identity levels are declared in advance, **not** tuned to what `T-A0b` needs |

⚠️ **The fourth check is the one that bites.** A selection cutoff in this project landed exactly at
the winner-flip point of its own sweep, and a repaired gate passed on a rule class motivated by the
failed attempt. If `T-P1`'s clustering identity were chosen after seeing `T-A0b`'s intervals, they
would be sequential by definition. It is declared beforehand, so they are not.

## 9 · Failure handling — fail closed, per task, never per programme

| event | action |
|---|---|
| an input hash changes | that task → `BLOCKED`; every other task continues |
| Ibex unreachable | its tasks → `BLOCKED_BACKEND`, recorded with the probe output; **local work continues** |
| a reviewer is unavailable | the result stays unpromoted and is **never** substituted silently |
| a pilot fails | that task → `INCONCLUSIVE` and escalates; it does not iterate |
| a task requests undeclared resources | refused at preflight |
| a population state is uncertain | **default `READY_WAITING_OPERATOR`**, never "probably fine" |

**One blocked task never stops an independent one.** That rule is why `T-LINT2`'s REJECT cost this
run one task and not the night.
