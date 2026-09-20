# SESSION HANDOFF

**The purpose of this file is that no important project state exists only in a conversation.**
A completely fresh coordinating session, or a fresh ChatGPT thread, should be able to recover the
whole project from this file and the eight documents in §8.

---

## 1 · AUTHORITATIVE STATE

| | |
|---|---|
| **branch** | `project-synthesis` |
| **worktree** | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis` |
| **HEAD when written** | `65146a5` (parent `be11fe7` + 3 reconciliation commits) |
| **`main`** | `ba3154a` — **passes `specs_exist.sh`**; 1 commit ahead of `origin/main`, unpushed |
| **governed `general/` pin** | `cff983144e2ad6fc01f648982fb61810dd77ddbe` (`cff9831`), VERSION 7.0.0 — recorded gitlink **and** checked-out SHA both verified |
| **`governance_base`** | `7e7ccd8` (`programme/GOVERNANCE_BASE.tsv`) |
| **ARIS pin** | `58d46de1…` (`ARIS.lock`), pinned 2026-09-14 |
| **written** | 2026-09-20, ~13:40 +03:00 |
| **working tree** | clean |
| **bootstrap** | `specs_exist.sh` **OK** · `test_bootstrap.sh` **24/24** · env `retron_tradicional` (Python 3.12.12) present |
| ⛔ **gate defect** | `specs_exist.sh` **fails spuriously ~5–10 % of runs** — a `SIGPIPE` + `pipefail` race in `resolve()`. Root cause demonstrated, one-line repair verified, **not applied** because `general/` is operator-only. See **D19** and `docs/BLOCKED.md` |
| **remote** | `origin` → `git@github.com:Melissaurious/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7.git` — **public**. **Nothing pushed.** |

⚠️ **Two coordinating sessions wrote this worktree today.** The first finished; sole ownership was
verified (HEAD stable, tree clean, no writes, no local compute, Ibex queue empty, lock held by one
session) before this session wrote anything. Its process is still resident (host pid `118496`) but
idle. `WORKING_RULES` §1 permits **one**, and nothing enforces it.

---

## 2 · CURRENT SCIENTIFIC STATE

### 2.1 · ⛔ Nothing has ever been promoted, and nothing is promotable

`human_input_audit: DONE` appears **nowhere** except the specification that defines it, and
`BUNDLE_SPEC.md` makes it a precondition. Separately, **no task carries a `WORKING_RULES` §5
`TASK_REPORT.md`**, so no output is formally consumable. Both are true of *every* result below.

### 2.2 · Strongest valid findings — measured, reconciled, **not promoted**

| finding | number | what it rests on | status |
|---|---|---|---|
| **PF00078 call fraction across the catalogue, with no-hits retained** | 434,289 HIT / 67,272 NO_HIT of **501,561** = **0.865875** | `T-C1b`, frozen at `c77adb9`, **4/4 blocking controls PASS** incl. a completeness gate requiring exactly 501,561 rows | awaiting first review |
| **…and the heterogeneity the earlier omission hid** | **0.4279** (RVT-UG5) → **0.9648** (RVT-CRISPR) across **613** families | same | awaiting review |
| **Published native non-cognate RT–ncRNA function is TWO examples** | 2 | `SIM2019` own full text, quoted verbatim in `A23c_crosspair_passages.tsv` | awaiting review; **survives** `ERRATUM_01` |
| **The region-Y "swap" rows are engineered chimeras, not native pairs** | 42 of 56 curated rows change meaning | same | awaiting review; **survives** `ERRATUM_01` |
| **The neighbourhood locator works and position matters** | discrimination **1.000 − 0.285 = 0.715** vs floor 0.50; anchor uniqueness 3,028,196/3,028,196; reproduction 31,504/31,504 | `T-N1c` controls — **the task is VOID, these three controls passed** | diagnostic evidence only |
| **YxDD carriage** | 380,948 / 501,561 = **0.7595**, 98.87 % inside the RVT envelope, chance rate 0.0784 | `T-F1` — ⚠️ executed **without a pre-run freeze** | never reviewed |
| **Name+size is not content identity** | 602 shared-pin groups: 245 identical, **357 DISTINCT** | `T-REG3` — ⚠️ no pre-run freeze | never reviewed |
| **Structure inventory reconciles exactly** | 97 collections, 44,608 **files**, 11.55 GB; all 97 manifest hashes match | `T-S1`, independently rescanned by the reviewer | `ACCEPT_WITH_CHANGES`, changes unapplied |

### 2.3 · Bounded negatives — inherit as design constraints, do **not** re-run

| negative | bound | reopens only on |
|---|---|---|
| RT deep phylogeny does not resolve | 312 trees; **157 alignable characters**; 1.39 taxa/character | a character source **materially exceeding 157** positions (number must be predeclared), **or** shallow-clade restriction with the independent-unit count declared in advance |
| De novo ncRNA discovery as implemented | a fixed positional interval beats the method **901 to 343**; per-type priors reach **969** | **five** declared conditions, not one — see `SCIENTIFIC_DAG.md` §6 |
| Neighbourhood as a retron detector | retrons **27th of 41** families, inside a **predeclared** dead band | not reopenable as posed |
| palm/fingers/thumb partition | not operationally defined in this project's parser **or in the literature**; two 2026 papers publish incompatible partitions | not reopenable as posed |
| Historical 11-clade placement | shuffled queries confidently placed at **7.9 %** against a ≤1 % limit | not reopenable as posed |
| Published cross-pair evidence | **7 experimental blocks**, not 56 rows; **zero** carry a numeric value; `BUF2025` paywalled so `U1`/`U2` (42 of 56 rows) are unadjudicable | primary-source access |
| Cross-pair panel labels on disk | **0** measured functional labels | — |

### 2.4 · Invalid / VOID — history, never silently promoted

| task | state | why |
|---|---|---|
| `T-P1-relatedness-backbone` | **VOID** | four declared blocking controls **never implemented as gates**, two never ran; duplicate control **failed 98/100 and was reported as a pass**; monotonicity failed at **every** adjacent pair; **controls contaminated the primary input**. `ERRATUM_01` was **itself false** and is superseded by `ERRATUM_02`. Ibex job `52124966` COMPLETED exit `0:0` — **the job ran; the task is void** |
| `T-LINT2-prose-numbers-gated` | **VOID**, rejected twice | a catcher was repointed **after** watching the mutant escape, then recorded as preregistered; the amendment was a Tier-C criterion change taken without authority |
| `T-N1b` | **VOID** | `N1b_NEG_permuted_anchor` **0.070506** vs declared 0.05. Sound control, **ill-posed construction** |
| `T-N1c` | **VOID, ESCALATED** | `N1c_NEG_random_position` **0.284691** vs declared 0.25. **Third** null design; no fourth attempted |
| `T-C1`, `T-N1`, `T-REG`, `T-A23`, `T-LINT` | **REVIEW_FAILED** | naming, denominator, omission and control defects. **The numbers reconciled; what they were called did not** |
| `T-A23c` | **PASS, erratum required** | four "secondhand primaries" resolved by keyword match to **2026** papers cited by a **2019** review |

### 2.5 · Unresolved scientific questions

1. **Is there a lineage partition that is not nested inside the pairing inference unit?** `T-P1b`
   exists to answer it. A negative **closes** `T-A0b` rather than leaving it open.
2. **Is a ceiling on the null rate the right blocking criterion for the neighbourhood locator at
   all?** Three designs have failed. `T-N1c` `ESCALATION_01` gives options A/B/C and recommends A.
3. **What do `SIM2019` refs 32/33/35/36 actually report?** Still unknown — `T-A23c` read four
   different papers.
4. **What is the ~40 % zero-ncRNA class at full upstream context?** Unexplained, not attributed.
5. **How wide are the landed pairing intervals really?** The unclustered generator covered **0.65**
   against a nominal 0.95 on a fitted fixture. A warning about a shared method, **currently
   unbounded** — `T-M2` exists for it and each bundle needs its own fixture.
6. **What are `rt_positives_emb` actually embeddings of?** Upstream provenance says ncRNA
   positive-region, not RT.

---

## 3 · TASK STATUS

Full register: `programme/ALL_DOWNSTREAM_TASKS.tsv` — **59 tasks**, all twelve goals plus
cross-cutting. Live board: `programme/LIVE_EXECUTION.tsv`.

| bucket | n | tasks |
|---|---|---|
| **running** | **0** | nothing is executing, locally or on Ibex |
| **queued** | **0** | auto-launch **suspended by operator instruction** pending launcher review |
| **under review / awaiting first review** | 4 | `T-C1b` · `T-A23c` (erratum) · `T-F1` · `T-REG3` |
| **changes pending** | 2 | `T-M1` · `T-S1` — `ACCEPT_WITH_CHANGES`, unapplied |
| **ready for operator review** (launchers proposed, not written) | 5 | `T-AUDIT2` · `T-M1b` · `T-S1b` · `T-A23d` · `T-P1b` |
| **ready after a named dependency** | 6 | `T-GATE1`←`T-AUDIT2` · `T-A0b`←`T-P1b`+multiway design · `T-F3`,`T-N2`←`T-P1b` · `T-A17`←`T-A16` · `T-S3`←`T-S2`+`T-A7` |
| **waiting operator — population** | 5 | `T-A5b1`/`T-R1` (**merge first**) · `T-A22` · `T-A7` · `T-A19` |
| **held — a number or design must be declared** | 13 | `T-N1d` · `T-S2` · `T-A16` · `T-A1` · `T-A6` · `T-A10` · `T-A2b` · `T-A3a` · `T-E2` · `T-I1` · `T-S12-floor` · `T-LINT3` · `T-LINT5` |
| **closed** | 5 | `S09` · `S07` · palm/fingers/thumb · 11-clade · neighbourhood-as-detector |
| **void / superseded** | 6 | `T-P1` · `T-LINT2` · `T-N1b` · `T-N1c` · `T-C1` · `T-N1` |

**One task remains preflight-clean and authorised:** `T-AUDIT1-circular-control-sweep`
(`NO_POPULATION_SPEND`, launcher frozen, worktree created, full dry-run passes). It is held only by
the operator's instruction to review launchers first.

---

## 4 · POPULATION STATE

Exposure is tracked as **`population_id + analysis_family/endpoint + exposure_state`**
(operator ruling 2026-09-20 §1). Authority: `programme/EXPOSURE_BY_ENDPOINT.tsv`, with
`programme/POPULATION_LEDGER.tsv` for sizes and units.

> ⛔ **A rejected or VOID run still counts as an exposure.** `T-C1`, `T-N1`, `T-P1` all failed
> review and all three spent their endpoint.

### 4.1 · Exposed — no longer untouched confirmatory evidence *for that endpoint*

| population | endpoint | exposed by |
|---|---|---|
| `RT-EXACT-501561` | `rt_profile_detection` | `T-C1` (REVIEW_FAILED), `T-C1b` |
| `RT-EXACT-501561` | `rt_motif_detection` | `T-F1` |
| `RT-EXACT-501561` | `rt_identity_clustering` | `T-P1` (VOID) |
| `RT-RECORDS-ALL-FAMILIES` | `neighbourhood_geometry` | `T-N1`, `T-N1b`, `T-N1c` |
| `LIT-CROSSPAIR` | `crosspair_evidence_geometry` | `T-A23`, `T-A23c` |
| `PAIR-ELIG` | **every** pairing endpoint | `embed_x2` cross-fitting, all five folds — **EXHAUSTED, permanently** |
| `STRUCT-62` | Tier A structural truth | Stage 3B on the 19 Tier-A truth pairs |

Each may still be used for exploratory work, QC, asset construction, method development, and
unrelated preregistered endpoints with no plausible leakage.

### 4.2 · Remaining confirmatory resources — **spend only on explicit authorisation**

| population | size | note |
|---|---|---|
| `RT-EXACT-501561` at **any other endpoint** | 501,561 | a preregistered confirmatory endpoint **may still be drawn here** |
| `RETRON-LOCI` | 630,741 / 632,688 | ⚠️ **reserved and never actually used** — `T-N1` only *declared* it. A genuinely retron-restricted population can still be defined |
| `NCRNA-16458` | 16,458 | 99.35 % already folded and 95.83 % a1/a2-called **in a prior project** — assets, not this project's conclusions |
| **`PANEL-RTDNA-81`** | 81 | ⭐ **the strongest anchor in the project.** Never a training target. ⛔ `T-A5b1` and `T-R1` would spend it **twice for one table** |
| **`PANEL-PRODUCERS-67-36`** | 67 / 36 | ⭐ **the only measured functional retron / non-functional contrast anywhere.** ⚠️ 62 of the 81 RT-DNA anchors are measured producers — `T-A5b1` leaks into `T-A22`'s positive class |
| `STRUCT-62` **Tier B** | 21 retron chains | **unopened**, partly design-inspected so not blind. ⛔ `T-A7` and `T-S3` both claim it |
| `PANEL-175` | 175 | only the **16 fully external** are usable, and 16 is an anecdote, not a population |
| `DEPOSITED-COMPLEXES` | 8 | external; **calibration only**, too few for a rate |
| `CM-CALLS` | 21 models | ⛔ **the instrument, never a test set.** Cannot adjudicate the population it defines |

---

## 5 · COMPUTE STATE

**Measured 2026-09-20 by this session.** ⚠️ `nvidia-smi` and Ibex DNS are **sandbox artefacts** —
both fail inside the Bash sandbox and succeed outside it. Establish your measuring context before
recording any capability as absent.

| resource | state |
|---|---|
| local CPU | 48 logical / 24 physical, load **1.79** |
| local RAM | 251 GB, **234 GB available** |
| **local GPU** | **2 × RTX 4090**, 24,564 MiB each, 246 MiB / 11 MiB used, **0 % util — both idle** |
| local disk | **2.8 TB free of 7.0 TB**, single NVMe — ⚠️ **I/O is the binding constraint, not CPU** |
| Ibex login | reachable, `login509-02-l`, key-based |
| **Ibex queue** | **`squeue --me` EMPTY — 0 running, 0 queued** |
| Ibex `batch` | 14-day limit; **7 idle / 220 mix / 124 alloc / 10 resv** — ⚠️ far tighter than the 99 idle recorded earlier; **expect to queue** |
| local running jobs | **none** — no `hmmsearch`/`mmseqs`/`foldseek`/`cmsearch` process on the host |
| checkpoints | none outstanding |

**Job IDs on record:** `52124966` `t_p1_relatedness` — **COMPLETED**, exit `0:0`, 11:28:47→11:36:53,
8 m 06 s. The task built on it is **VOID**.

⛔ **Every scripted Ibex call must set `IBEX_HOST=rioszemm@ilogin.ibex.kaust.edu.sa` explicitly.**
`general/tools/status.sh` defaults to the alias `ibex`, which resolves to `vsc509-03-l` — the vscode
pool `general/site/IBEX.md` **forbids** for scripted access. Fixing the default is a governed-pin
change.

**Tooling, verified present** (`data/README.md` is the register — check it before declaring
absence): `foldseek` v10.941cd33 (`esmologs`, `retrons`, and Ibex module `foldseek/10-941cd33`) ·
`hmmsearch` (`diffab`) · `mmseqs` (`colabfold`) · `cmsearch` (`retrons`) · `muscle`, `fasttree`
(`retron_tradicional`) · `mafft` (`dep_maps`). **`iqtree2` is genuinely absent**, and nothing needs
it while `S09` is closed.

**Blocked capability:** task-session dispatch. A headless `claude -p` from `launch_task.sh` is
denied by the permission classifier (`Create Unsafe Agents`); the script ends in an interactive
`exec claude`. Options in `PARALLEL_EXECUTION_PLAN.md` §7 — **A** permission rule, **B** manual
`bash programme/launch_task.sh <task-id>`, **C** coordinator executes `ZERO`/`CPU_SMALL` with
mandatory disclosure.

---

## 6 · NEXT OPERATOR DECISIONS

**D1 — Review the six proposed launchers.** `programme/LAUNCHER_PROPOSALS_WAVE_02.md`. Approve,
amend or reject each. Nothing is written or dispatched until you do. *This is the gate you asked
for.*

**D2 — `T-N1c` control design.** Three null designs have failed. Choose: **(A)** discrimination
margin `true − null ≥ 0.50` is the blocking criterion and the null rate is **reported not gated**;
**(B)** keep a ceiling but derive it from the actual `L`/`W` distributions, not medians;
**(C)** a different null entirely. The escalating session recommends **A**. *Blocks `T-N1d`, which
blocks `T-A10` and `T-N2`.*

**D3 — Confirm the operator ruling record.** `docs/decisions/2026-09-20_operator_ruling_exposure_freeze_controls.md`
is `PROVISIONAL`, reconstructed from repository citations because the ruling existed only in chat.
**§§4–7 are cited nowhere and are not reconstructed.** Confirm, correct, or supply the missing
sections.

**D4 — Task-session dispatch.** A, B or C above. *This has blocked the designed execution model
since the programme began.* Recommended: **A**, with **B** as fallback.

**D5 — Rotate the exposed API key.** Still live in plaintext in the Claude configuration, in an MCP
environment block, and printed into a transcript. Deliberately not inspected further, because
inspecting it repeats the exposure. **Not in this repository** — `git grep` for key patterns over
tracked files returns nothing.

**D6 — `human_input_audit`.** It gates **every claim in the project** and blocks **no** computation.
Nothing is promotable until it clears.

**D7 — Merge or differentiate `T-A5b1` and `T-R1`.** They are the same task and would spend
`PANEL-RTDNA-81`, the strongest anchor in the project, **twice for one table**.

**D8 — Allocate `STRUCT-62` Tier B** between `T-A7` (control) and `T-S3` (headline). A control and
an inference cannot both claim the same chains as independent evidence. The independent spec names
**HIV-1 p66 and externally partitioned RTs** as the positive, which dissolves the conflict.

**D9 — Protect `T-A22` from `T-A5b1`.** 62 of 81 RT-DNA anchors are measured producers. Freeze
`T-A22`'s feature set and validation design **before** that exposure, or evaluate on a genuinely
independent subset.

**D10 — Declare `T-S2`'s metric and threshold.** foldseek is installed and registered; the only
blocker is that no metric and no threshold exist. Declaring them **is** the scientific decision.

**D11 — Predeclare "materially exceeding 157 alignable positions".** `T-E1` may inventory character
counts autonomously but cannot classify its own result against `S09`'s reopening condition without
a number fixed in advance.

**D12 — Rule on `T-P1b`'s premise** (`ERRATUM_02`): may a full-catalogue clustering inform a lineage
design at all, given that components hold multiple RT lineages? *Blocks the trunk.*

**D13 — `T-P3`.** Give it a non-duplicative scope or merge it into `T-P1b`. Both compute distances
and groupings.

**D14 — Push or do not.** 35 unpushed commits on `project-synthesis`, 1 on `main`. Remote is
**public — verified**, not assumed. ⛔ **One item to resolve first:** publishing
`programme/COORDINATION_STATE.md` announces an *unremediated* API-key exposure. Rotate (D5) or
redact before pushing. Full report: `programme/GITHUB_READINESS.md`.

**D15 — `T-LINT5`.** A new task ID responding to a rejected criterion is Tier C. Authorise, or leave
`BLOCKED`. The reviewer's instruction: *if the host cannot run it in a separate session, leave it
`BLOCKED`.*

**D16 — Reconcile `WORKING_RULES` §3 with the §1 exposure ruling.** §3 and the ledger's
`(pre-ruling row)` entries still read as though exposure were dataset-wide. The programme now
operates on the endpoint model. The wording should follow.

**D17 — Fix `general/tools/status.sh`** (`IBEX_HOST` default). A governed-pin change with a decision
record, so not a session's to make.

**D19 — ⛔ Repair `general/checks/specs_exist.sh`.** The **blocking** governance gate fails
spuriously on **~5–10 % of runs**, naming a different file each time, **inside and outside the
sandbox**. Cause: `set -uo pipefail` plus `printf '%s\n' "$TRACKED" | grep -qxF "$1"` in `resolve()`
— `grep -q` exits on first match, `printf` dies of `SIGPIPE` (141), and `pipefail` makes the
pipeline fail *even though grep matched*. `TRACKED` is 100,024 bytes, above the 64 KiB pipe buffer,
which is why it is marginal. **Repair: use a herestring, `grep -qxF "$1" <<<"$TRACKED"`, in all
three `resolve()` branches — verified 0 spurious misses in 300 runs.** A governed-pin change with a
decision record, so not a session's to make. *Until it is fixed, a failing gate may be a real
failure or may be this bug; re-running until green is exactly the habit that makes a real one
invisible.*

**D18 — Confirm the `0.217 %` registry-coverage withdrawal.** Withdrawn with no operator decision
preserving it; `T-REG2` is specified to re-derive it under fixtures.

---

## 7 · NEXT RECOMMENDED EXECUTION WAVE

**Only after D1.** Four concurrent streams; none consumes an unexposed confirmatory population.

| lane | task | class | backend | runs beside |
|---|---|---|---|---|
| **A · audit** | `T-AUDIT1` then `T-AUDIT2` | ZERO | local `IO_LOW` | everything |
| **B · corrections** | `T-M1b` **then** `T-S1b` — **serial, one NVMe** | CPU_SMALL | local `IO_HIGH` | A, C, D |
| **C · literature** | `T-A23d` | ZERO | local, network | everything |
| **D · Ibex** | `T-P1b` **pilot only** (10,000 seqs) | CPU_MEDIUM | ibex | everything |
| **E · review** | dispatch reviews for `T-C1b`, `T-A23c`, `T-F1`, `T-REG3` | — | Codex | everything |

⭐ **Lane E is the most underused resource in the programme.** Four executed tasks have never been
reviewed; reviewing them costs no compute, no population and no operator decision beyond dispatch.

⛔ **`T-N1d` is in no lane** — it is blocked on D2, and scheduling it would schedule a decision.
⛔ **`T-P1b`'s full run is a separate authorisation** taken after the pilot's controls report.

---

## 8 · NEW SESSION READING ORDER

The minimum to recover complete project state. **Read in this order.**

1. **`CLAUDE.md`** — project conventions, environments, the governance contract.
2. **`programme/SESSION_HANDOFF.md`** — this file.
3. **`programme/RECONCILIATION_2026-09-20.md`** — bootstrap evidence, the reconciled task ×
   review table, and seven independently verified findings.
4. **`programme/WORKING_RULES.md`** — session model, parallel safety, the §5 reporting contract,
   §6a what may be a blocking control, **§6b freeze-before-execute**.
5. **`docs/decisions/2026-09-20_operator_ruling_exposure_freeze_controls.md`** — the exposure,
   freeze and control rules the programme now runs on. **`PROVISIONAL`, pending D3.**
6. **`programme/EXPOSURE_BY_ENDPOINT.tsv`** + **`programme/POPULATION_LEDGER.tsv`** — what may
   still be spent, and on what.
7. **`programme/SCIENTIFIC_DAG.md`** — dependency structure. **§10 first**, then §§0–9.
8. **`programme/ALL_DOWNSTREAM_TASKS.tsv`** — all 59 tasks with typed dependencies.
9. **`programme/LAUNCHER_PROPOSALS_WAVE_02.md`** — what is proposed next and why.
10. **`programme/PARALLEL_EXECUTION_PLAN.md`** — what runs where. **§10 first.**
11. **`programme/CAPABILITY_STATE.md`** — what this programme can and cannot do, and **§5, the
    five-instance pattern of capabilities recorded absent that were present**.
12. **`programme/EXECUTION_BATCH_01_VERDICT.md`** — the independent verdict that reshaped the
    programme, and why four of five tasks failed.
13. **`programme/tasks/T-N1c-neighbourhood-census/ESCALATION_01_third_null_failed.md`** — the open
    control-design decision, D2.
14. **`programme/tasks/T-A23c-source-retrieval/ERRATUM_01_source_identity_unverified.md`** — what
    survives and what does not in the cross-pair evidence.
15. **`docs/BLOCKED.md`** — open questions with their recommended defaults.
16. **`general/CLAUDE.md`** — the governance layer, read at session start.

**Before any provenance-bearing execution:**

```bash
git submodule update --init --recursive
bash general/checks/specs_exist.sh
bash programme/test_bootstrap.sh
python3 general/tools/check_launcher.py launchers/LAUNCHER_02_rt0_rt7_definition.md
```

---

## 9 · GIT / GITHUB READINESS

**Nothing has been pushed. No push will happen without explicit operator approval.** Full report:
`programme/GITHUB_READINESS.md`.

| | |
|---|---|
| remote | `origin` → `git@github.com:Melissaurious/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7.git` |
| **visibility** | ⚠️ **PUBLIC — verified**, not assumed: `api.github.com` returns HTTP 200 with `"private": false`, `"visibility": "public"` |
| `project-synthesis` | **35 ahead, 0 behind** `origin/project-synthesis` |
| `main` | **1 ahead, 0 behind** `origin/main` — the `docs/BLOCKED.md` repair |
| secrets in tracked files | **none** — pattern scan over all tracked content returns nothing |
| heavy / private data | correctly ignored: `data/*`, `MELISSA_DATA/`, `ARIS_OUTPUT/`, `**/.venv/`, `results/**/work/`, publisher PDFs |
| invalid output presented as evidence | **none** — every VOID and REVIEW_FAILED task is labelled as such in the register, the live board and this file |
| ⛔ **blocker before push** | `programme/COORDINATION_STATE.md` would be published for the first time and states that a **live, unrotated** API key sits in plaintext in the Claude configuration. The key is **not** in the repository, but publishing the text advertises an open hole on a named person's machine. **Rotate (D5) or redact first** |

---

## 10 · STANDING RULES A SUCCESSOR MUST NOT RELAX

- **Freeze before execute.** Launcher + implementation, one commit, **before** the run. Four of
  five Batch-01 tasks failed because code entered git with its own outputs.
- **A failed blocking control ends the task.** Escalate and open a new ID. **Never a v2 in place**,
  and **never raise the threshold after seeing the number.**
- **A control may not touch the primary input.** Controls run on fixtures or in a separate pilot.
- **A control that shows the instrument *returned something* cannot show it returned *the right
  thing*.** Five instances now: a null forced to zero, a control OR-ing across substrates, a
  CM-derived caller judged by CM-derived calls, a bibliographic search taking its top hit, and a
  positive control that used the one source carrying a DOI.
- **Before recording any capability as absent, establish which context you measured from** — and
  check `data/README.md`. **Five instances.**
- **Task validity is not hypothesis truth.** A refuted hypothesis is a **successful task**.
- **Populations deplete, per endpoint.** A rejected or VOID run still spends its endpoint.
- **No number in prose without a table cell behind it.** `TASK_PRIOR_WORK_*` was claimed for eight
  hours with no file on disk.
- **Prior work supplies assets and bounded negatives. Its numbers are `[UNVERIFIED]`** until
  re-derived.
- **Fail closed.** If a reviewer is unavailable, record it and stop. Never substitute silently.
- **"Ready to launch" is not true until the chain has been run.**
- **A gate that passes on a re-run has not passed.** When a blocking check fails once and succeeds
  on retry, that is a finding to chase, not noise to clear. `specs_exist.sh` was caught this way,
  and the habit it would otherwise teach — re-run until green — is how a real governance failure
  becomes invisible.
- **One coordinating session per worktree.** Nothing enforces this; two ran today.
