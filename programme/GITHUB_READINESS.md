---
record: GITHUB_READINESS
date: 2026-09-20
status: REPORT ONLY — nothing pushed, no push attempted
gate: explicit operator approval required before any push or publication
---

# GitHub readiness — what a push would publish, and one thing to fix first

**No push has been made and none will be without your explicit approval.**

---

## 1 · Remote and visibility

| | |
|---|---|
| remote | `origin` → `git@github.com:Melissaurious/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7.git` |
| **visibility** | ⚠️ **PUBLIC — verified**, not assumed |
| how verified | `GET https://api.github.com/repos/Melissaurious/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7` → **HTTP 200**, `"private": false`, `"visibility": "public"` |
| default branch | `main` |
| last remote push | `2026-09-19T20:45:17Z` |
| remote size | 71,866 KB |

> Earlier records asserted the remote was public without a verifiable check. **It is now verified.**
> Anything pushed becomes world-readable, indexable and effectively permanent.

## 2 · Ahead / behind

| branch | ahead | behind | contents |
|---|---|---|---|
| `project-synthesis` | **32** | 0 | the whole programme layer: governance, reviews, launchers, boards, this reconciliation |
| `main` | **1** | 0 | `ba3154a` — the `docs/BLOCKED.md` path repair that unblocks `specs_exist.sh` |

No branch is behind. No merge or rebase is needed. No force-push is involved.

## 3 · What would become remote

**77 files, +33,564 / −65 lines** on `project-synthesis`, plus this session's additions.

| group | files | notes |
|---|---|---|
| programme layer | 28 | boards, rules, DAG, execution plan, capability and coordination state |
| task launchers, errata, dispositions, escalations | 30 | the full audit trail, including every VOID and every rejection |
| prior-work instruments and tables | 8 | two sweeps, their controls and their declared blind spots |
| review stage | 6 | independent verdicts **verbatim**, including the ones that rejected this project's own work |
| project review package | 4 | handoff and registries |
| docs | 4 | `BLOCKED.md`, backup manifest, reviewer availability, human-input audit |

Largest: `review-stage/ASSET_SWEEP.tsv` (+20,766 lines),
`review-stage/INDEPENDENT_SCIENTIFIC_REVIEW_2026-09-20.md` (+2,488),
`programme/LAUNCHER_REVIEW_PACKET.md` (+1,210).

**This session adds:** `programme/SESSION_HANDOFF.md`, `programme/RECONCILIATION_2026-09-20.md`,
`programme/LAUNCHER_PROPOSALS_WAVE_02.md`, `programme/GITHUB_READINESS.md`,
`docs/decisions/2026-09-20_operator_ruling_exposure_freeze_controls.md`,
`programme/tasks/T-A23c-source-retrieval/ERRATUM_01_source_identity_unverified.md`,
`programme/prior_work/TASK_PRIOR_WORK*` (5 files), and modifications to six programme tables.

## 4 · Secrets and credential material — clean

| check | result |
|---|---|
| `sk-ant-…`, `AKIA…`, `ghp_…`, `xox[baprs]-`, `-----BEGIN … PRIVATE KEY-----` across **all tracked content** | **no matches** |
| `.gitignore` coverage | `*.env`, `.env`, `**/credentials*`, `*.pem`, `*.key` — all excluded |
| `.ssh` | not in the repository; read-denied to this session's sandbox |

**No credential material is tracked.**

## 5 · ⛔ One item to resolve before pushing

**`programme/COORDINATION_STATE.md` would be published for the first time, and line 13 states:**

> *"A live API key is in plaintext in the user's Claude configuration, in an MCP environment block,
> and was printed into a session transcript. Rotate it."*

`programme/OVERNIGHT_RUN_REPORT.md` L283 repeats it.

**The key itself is not in the repository** — the scan in §4 is clean. But publishing this text to a
**public** repository announces an **unremediated** credential exposure on a named person's machine.
That is worth more to an attacker than it is to a reader.

**Three ways to resolve, operator's choice:**

| option | effect |
|---|---|
| **A — rotate the key first, then push** *(recommended)* | the disclosure becomes historical and harmless. It is also decision **D5**, which is worth doing regardless |
| **B — redact the two lines to "a credential exposure was found and handled", then push** | keeps the governance record without advertising a live hole |
| **C — push as-is** | acceptable **only** once the key is rotated |

⚠️ This is the **only** finding in the push that is about disclosure rather than science.

## 6 · Already public, so not a new exposure

`data/README.md`, `CLAUDE.md` and `idea-stage/programme/*` are already on `origin` and already
contain the Ibex login (`rioszemm@ilogin.ibex.kaust.edu.sa`), local absolute paths under
`/home/borg/`, and the institutional address. Pushing does not change their status. Flagged so the
decision is informed, not because it is new.

## 7 · Heavy and private data — correctly excluded

| excluded | mechanism |
|---|---|
| all canonical data | `data/*` with `!data/README.md` — the register is tracked, the bytes are not |
| the ~1.8 GB local corpus | `MELISSA_DATA/` |
| scratch | `ARIS_OUTPUT/`, `scratch/`, `.agent-lock` |
| virtualenvs | `**/.venv/` (the workbench carries 72 MB) |
| per-gate bundle scratch | `results/**/work/`, with the frozen `GII.deriv.hmm` ruler deliberately re-included |
| publisher PDFs | `references/rt0_rt7/literature/*.pdf` — **copyright-reserved; the register carries citation, sha256 and byte count instead** |
| model weights / caches | `*.h5`, `*.npz`, `*.ckpt`, `*.pt` |
| harness artefacts | `.claude/`, `.mcp.json`, shell rc placeholders |

**The exclusion rules are by location and purpose, never by extension** — a blanket `*.tsv` or
`*.hmm` rule would have hidden the frozen profile HMM, the control tables and the anchor set, all of
which are load-bearing and must stay tracked.

## 8 · ⛔ Is any invalid output presented as promoted evidence? **No**

| task | state | labelled as such in |
|---|---|---|
| `T-P1` | **VOID** | register, live board, DAG §10, handoff §2.4, its own `ERRATUM_02` |
| `T-LINT2` | **VOID** ×2 rejections | register, board, handoff, `VOID_02` |
| `T-N1b`, `T-N1c` | **VOID** | register, board, DAG §10.3, `ESCALATION_01` |
| `T-C1`, `T-N1`, `T-REG`, `T-A23`, `T-LINT` | **REVIEW_FAILED** | register, board, `EXECUTION_BATCH_01_VERDICT` |
| `T-A23c` | PASS with **erratum required** | register, board, `ERRATUM_01` |
| `T-M1`, `T-S1` | `ACCEPT_WITH_CHANGES`, **unapplied** | register, board, handoff |

**Nothing in this repository is promoted**, and `docs/HUMAN_INPUT_AUDIT.tsv` contains a header row
and **no data** — independent confirmation that the promotion gate has never been run. Every
independent review is landed **verbatim, including the ones that rejected this project's own work**.

## 9 · Exact push commands — **for the operator to run, not this session**

```bash
cd /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis

# 1 · the programme layer: 32 commits + this session's reconciliation
git push origin project-synthesis

# 2 · the BLOCKED.md repair on promoted state: 1 commit
git push origin main
```

Neither is a force-push. Neither rewrites history. **Resolve §5 first.**

## 10 · Verdict

| question | answer |
|---|---|
| Is the repository in a pushable state? | **Yes** — tree clean, no secrets, no heavy data, no invalid result promoted |
| Can visibility be verified? | **Yes — verified public** (HTTP 200, `"private": false`) |
| Is there a blocker? | **One**, and it is not scientific: §5, the API-key disclosure |
| Was anything pushed? | **No.** No push was attempted |
