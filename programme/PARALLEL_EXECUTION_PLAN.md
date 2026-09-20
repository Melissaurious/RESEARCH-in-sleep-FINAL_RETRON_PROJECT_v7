# PARALLEL EXECUTION PLAN

**As of 2026-09-20.** Derived from `programme/SCIENTIFIC_DAG.md`, which was written first on
purpose. Task register: `programme/ALL_DOWNSTREAM_TASKS.tsv` (**59 tasks**).

> ⚠️ **Read §10 first.** Batch 02 and the reconciliation pass changed the capacity table, the
> routing and the auto-launch set. §§1–9 are the reviewed reasoning and are kept verbatim.

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
| `IO_LOW` | ~~unlimited~~ **counted, see below** | `ZERO` tasks, which read landed tables and write new ones |
| Ibex | **not independent — see below** | `T-C1`, `T-P1`, `T-F2` |

### `[REVIEW 01a0bcb2]` Three corrections to this model

⛔ **1. `IO_HIGH = 1` is not sufficient, and `IO_LOW = unlimited` is wrong.** One high-I/O task is
permitted beside four `IO_MEDIUM` and *unbounded* `IO_LOW`. But `T-LINT4`, `T-M2` and any
repository-wide audit are not meaningfully low-I/O — they walk whole worktrees.
**Required: a global NVMe token budget**, not high-versus-high serialisation. Every task declares a
token cost; the sum is capped; `IO_LOW` costs tokens too.

⛔ **2. A global scan cannot run while the roots it scans are being written.** `T-REG3`, `T-REG4`
and `T-LINT4` inventory collections and worktrees that other tasks emit into. Concurrent output
makes the inventory **non-deterministic** and can hash a partially written file.
**Required: run global scans against a snapshot, or in a declared quiescent window.**

⛔ **3. "Ibex is independent of all lanes" is unsupported.** Six jobs reading 501,561 local
sequences need staging or transfer first, and **no launcher declares it**. Ibex is independent only
*after* its inputs are staged; the staging itself is local I/O and belongs in a lane.
**Required: every Ibex task declares its staging step and that step's I/O cost.**

**Also corrected:** `T-P2` and `T-E1` are `CPU_MEDIUM`, which this plan's own routing rule sends to
the workstation, and the schedule sent them to Ibex anyway. **Both routed local** unless a pilot
measures otherwise. `T-P3` leaves the Ibex list — it overlaps `T-P1` and needs a non-duplicative
scope before it is scheduled at all.

⚠️ **No Ibex assignment here has a mandatory pilot, core/RAM request, expected I/O or runtime in its
launcher.** `T-P1` is the only one with a launcher, and it does declare a pilot. The rest are
**unproven routings, not wrong ones** — and they may not be queued until they are proven.

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

### ⛔ THE TABLE ABOVE IS WITHDRAWN. `[REVIEW 01a0bcb2]`

An independent read-only review of this plan returned **REJECT**, and its central finding is that
**"22 tasks are safe to auto-launch" is indefensible.** It is retained above as the record of what
was claimed. **The corrected auto-launch set is in §4a.**

Four reasons, each sufficient on its own:

1. ⛔ **Ten of the 22 touch unexhausted confirmatory-capable populations.** Seven on
   `RT-EXACT-501561`, three on `RETRON-LOCI`. I read `INSPECTED` as "already spent, so free". **The
   ledger says each `can_serve_as_confirmation`**, which makes them *unexhausted* under
   `WORKING_RULES` §4a — **one explicit operator authorisation per launch, never auto-scheduled.**
   §8's population-collision row was wrong for the same reason: seven tasks sharing one unexhausted
   population **is** a collision.
2. ⛔ **Wave 1 contains producer→consumer chains**, contradicting this plan's own claim that no
   Wave-1 task reads another's output: `T-C1 → T-P1/T-F1/T-F2/T-P2`, `T-P1 → T-P3`,
   `T-F2 → T-E1`, `T-REG4 → T-S1 → T-S2`, `T-LINT2 → T-LINT4`. That is a **queue with barriers**,
   not a concurrently launchable set.
3. ⛔ **21 of the 22 had no frozen launcher and no board row**, so `preflight.py` would have refused
   every one of them. "Ready" described a plan, not a state.
4. ⛔ **`T-LINT2` is `VOID`**, and was listed as done.

### 4a · The corrected auto-launch set

| launchable **now**, verified by `preflight.py` | |
|---|---|
| `T-AUDIT1-circular-control-sweep` | `NO_POPULATION_SPEND`, no upstream, launcher frozen, worktree created, **full `--dry-run` passes** |

**One.** Not twenty-two.

Six more are `LAUNCH_NOW` by readiness class and **have no launcher yet**, so they are eligible in
principle and not yet specified: `T-AUDIT2`, `T-REG3`, `T-REG4`, `T-S1`, `T-C2`, `T-M1`. Writing
each launcher is coordinator work and is the fastest route to a real second wave.

`T-GATE1` is frozen and dry-run-verified but now **`BLOCKED_DEPENDENCY`**: a gate that reads task
reports needs `T-AUDIT2` first. `T-P1` is frozen and dry-run-verified but now
**`READY_WAITING_OPERATOR`** on population grounds — it is the trunk, and it needs one sentence of
authorisation.

⛔ **Nothing launched tonight regardless.** See §7: the host refuses to spawn a task session. Even
with the corrected set of one, the capability to dispatch it is missing.

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

| check | verdict `[REVIEW 01a0bcb2]` |
|---|---|
| **no shared writes** | ✅ **holds** — one `output_directory` and one worktree per task, disjoint by construction |
| **no unfinished-producer reads** | ⛔ **FAILED.** The claim "no Wave-1 task reads another Wave-1 task's output" was false: `T-C1 → T-P1/T-F1/T-F2/T-P2`, `T-P1 → T-P3`, `T-F2 → T-E1`, `T-REG4 → T-S1 → T-S2`, `T-LINT2 → T-LINT4`. A queue with barriers, not a parallel set |
| **no population collision** | ⛔ **FAILED.** Seven tasks share unexhausted `RT-EXACT-501561`; three share unexhausted `RETRON-LOCI`. Calling them "already inspected, so depletes nothing further" was the same misreading as §4 |
| **no criterion coupling** | ⚠️ **partly.** `T-P1`'s identity ladder is declared in advance, so `T-P1`/`T-A0b` are genuinely uncoupled. But **`T-P2` and `T-E1` share the 157-character reopening bar**, `T-REG2`'s denominator depends on `T-REG4`, and `T-A22`'s feature set can be informed by `T-A5b1`'s producer-enriched anchors |

⚠️ **The fourth check is still the one that bites**, and the coupling above is exactly its shape. A
selection cutoff in this project landed at the winner-flip point of its own sweep; a repaired gate
passed on a rule class motivated by the failed attempt; and tonight a mutant's catcher was repointed
after the mutant escaped it. **If one task's bar is set using another's output, they are sequential
by definition** — `T-P2` and `T-E1` are therefore sequential, not parallel, until the 157-character
bar is predeclared by the operator.

⛔ **Future collisions to hold, not schedule:** `T-A5b1` with `T-R1` (**they are the same task** —
both map the 81 empirical RT-DNA sequences; running both spends the panel twice for one table);
`T-A7` with `T-S3` (control and headline on the same Tier B chains); and `T-A5b1` with `T-A22`
(**62 of the 81 RT-DNA anchors are measured producers**, so anchor-derived feature selection leans
on a population that heavily overlaps `T-A22`'s positive class).

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


---

## 10 · DELTA — re-measured 2026-09-20 by the reconciliation session

### 10.1 · Capacity, re-measured rather than inherited

| resource | measured now | change |
|---|---|---|
| local CPU | 48 logical / 24 physical, load **1.79** of 48 | unchanged |
| local RAM | 251 GB, **234 GB available** | unchanged |
| local GPU | **2 × RTX 4090**, 24,564 MiB each, 246 MiB / 11 MiB used, **0 % util** | unchanged, both idle |
| local disk | **2.8 TB free of 7.0 TB**, single NVMe | unchanged — I/O is still the binding constraint |
| Ibex login | reachable, `login509-02-l`, key-based | unchanged |
| Ibex queue | **`squeue --me` empty** | unchanged |
| Ibex `batch` | 14-day limit, **7 idle / 220 mix / 124 alloc / 10 resv** | ⚠️ **far tighter than the 99 idle nodes recorded earlier** |
| Ibex job history | `52124966 t_p1_relatedness` **COMPLETED**, exit `0:0`, 8 m 06 s | the only job this project has run today |

⚠️ **The `batch` partition is much busier than §1 recorded.** Seven idle nodes, not 99. An Ibex-scale
submission should expect to queue. This does not block anything; it changes what "send it to Ibex"
costs in wall-clock, and it is why `T-P1b`'s mandatory pilot matters more, not less.

### 10.2 · ⛔ A resource recorded absent that is present — foldseek

`LIVE_EXECUTION.tsv` held `T-S2-foldseek-calibration` at `READY_WAITING_RESOURCE` because
*"foldseek is NOT INSTALLED locally"*.

| check | result |
|---|---|
| `/home/borg/miniconda3/envs/esmologs/bin/foldseek` | **present, v10.941cd33** |
| `/home/borg/miniconda3/envs/retrons/bin/foldseek` | **present, v10.941cd33** |
| `data/README.md` L182 | **already registers the first path by name** |
| `data/README.md` L194 | already registers Ibex module `foldseek/10-941cd33` — same version |

**Fifth instance of `CAPABILITY_STATE.md` §5.** The first four needed a different measuring context
to explain; this one did not. `CLAUDE.md` names the exact register that answers it:
*"do not conclude a dependency is absent until the registered environments and Ibex resources have
been checked."*

> **Rule, added to this plan:** before any task is marked `READY_WAITING_RESOURCE`, the resource is
> looked up in `data/README.md` **and** on `PATH` across `/home/borg/miniconda3/envs/*/bin/`. A
> `which` in one environment is not a search.

Other tools confirmed present this way: `hmmsearch` (`diffab`), `mmseqs` (`colabfold`), `cmsearch`
and `foldseek` (`retrons`), `muscle` and `fasttree` (`retron_tradicional`), `mafft` (`dep_maps`).
**`iqtree2` is genuinely absent** from every local env — and that absence is bounded by `S09` being
closed, so nothing currently needs it.

### 10.3 · The auto-launch set is now ZERO

§4a recorded **one** launchable task, `T-AUDIT1-circular-control-sweep`. It is still `AUTHORIZED`
and still passes preflight. **But nothing should auto-launch at all**, because the operator has
asked to review the proposed scientific launchers before the next wave begins.

| lane | status |
|---|---|
| auto-launch | **suspended by operator instruction** |
| `T-AUDIT1` | remains the one preflight-clean task; dispatch on the operator's word |

### 10.4 · Maximum-safe parallel wave, when the operator releases it

Four lanes that genuinely do not collide on writes, producers, populations or criteria. **None
consumes an unexposed confirmatory population.**

| lane | task | class | backend | I/O | why it is safe beside the others |
|---|---|---|---|---|---|
| **A · audit** | `T-AUDIT1-circular-control-sweep` | ZERO | local | LOW | reads launchers and control tables; `SOFT_INTERPRETIVE`, blocks nothing |
| **A · audit** | `T-AUDIT2-task-report-backfill` | ZERO | local | LOW | reads landed artifacts, writes reports, promotes nothing. **Feeds `T-GATE1`** |
| **B · corrections** | `T-M1b` embedding-cache re-verification | CPU_SMALL | local | **HIGH, serial** | applies 4 named changes; `NO_POPULATION_SPEND` |
| **B · corrections** | `T-S1b` structure-inventory correction | CPU_SMALL | local | **HIGH, serial** | applies 3 named changes; `NO_POPULATION_SPEND` |
| **C · literature** | `T-A23d-primary-verification` | ZERO | local | LOW | external population, no compute, no biological population |
| **D · Ibex** | `T-P1b-identity-partition` **pilot only** | CPU_MEDIUM | **ibex** | MEDIUM | 10,000-sequence pilot with its expected result declared; the full run is a separate authorisation |

⛔ **Lane B is strictly serial within itself** — both are `IO_HIGH` on the one NVMe. Lanes A, C and D
run beside it. That is **4 concurrent streams**, not 22.

⛔ **`T-N1d` is not in any lane.** It is blocked on the control-design ruling, and scheduling it
would be scheduling a decision.

⛔ **Every Ibex task still needs its declared pilot**, and `T-P1b` is the only Ibex candidate. Its
staging cost is local I/O and belongs in a lane — the correction §2 item 3 made and no launcher has
yet honoured.

### 10.5 · Codex review capacity — the lane with the most idle throughput

Eight review threads have been dispatched and all returned. **Four executed tasks have never been
reviewed at all**, and reviewing them costs no compute, no population and no operator decision:

| awaiting first review | why it matters |
|---|---|
| `T-F1-motif-scan` | executed without a freeze; not covered by `01a0bdfa` |
| `T-REG3-content-hash` | same |
| `T-C1b-pf00078-envelope-census` | the Batch-02 repair; **frozen properly** |
| `T-A23c-source-retrieval` | frozen properly; **carries a known erratum** |

**This is the single most underused resource in the programme.** It can run entirely in parallel
with everything in §10.4 and needs nothing but dispatch.
