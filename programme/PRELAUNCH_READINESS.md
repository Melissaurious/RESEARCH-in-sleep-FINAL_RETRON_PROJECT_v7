# PRELAUNCH READINESS

**Date:** 2026-09-20 · **Scope:** certification of the orchestration and governance machinery only.
**No scientific analysis has been executed. The programme has not been redesigned.**

---

## 1 · Authoritative governance commit

| | |
|---|---|
| **governance base** | **`9678a95`** |
| defined as | the commit at which any of the four governance files last changed |
| governance files | `programme/PROGRAM_LAUNCHER.md`, `programme/WORKING_RULES.md`, `programme/templates/TASK_LAUNCHER_TEMPLATE.md`, `review-stage/TASK_PROTOCOL.md` |
| content fingerprint | `aa2936e004fd3147` (sha256 over those four files, git-independent) |
| superseded | `b5443e1`, which predates the corrections from the independent launcher review |

**Reconciliation.** The packet previously stamped `b5443e1`. That was stale: `9678a95` introduced the
two-field state model and the control-admissibility rule, so any task running against `b5443e1`
would have used superseded rules. All nine launchers are restamped to `9678a95` and the preflight
refuses a mismatch.

**Why the base is stable under launcher edits.** It tracks the four governance files only. Editing a
task launcher does not move it, so stamping does not invalidate the stamp.

### A deviation from the review's wording, stated openly

The review asked that every runnable task worktree **descend from the governance commit**. That is
not achievable without collapsing a deliberate tier separation. Task worktrees are analysis-tier and
are based on `main` (`94a1a78`); the governance layer is index-tier and lives on `project-synthesis`.
The package states that the index branch does not contain the evidence and that task branches are
not merged into it. Merging would invert that design.

The requirement's **purpose**, that a task can never run against stale governance, is met by two
strict gates instead:

- `governance_base_current` — the launcher's recorded base must equal the actual base. Refuses on any
  drift, verified by failure injection FI-02.
- `worktree_descends_from_declared_base` — the worktree must descend from the `base_commit` its
  launcher declares.

Both are hard gates. A stale governance layer cannot be used.

## 2 · Remote branch and tag

**Not pushed.** Pushing is outward-facing and the operator has not asked for it. The control plane is
committed locally and tagged, ready to push on one word.

| | |
|---|---|
| local branch | `project-synthesis` |
| local tag | `programme-prelaunch-v1` |
| remote state | `origin/project-synthesis` is at `cfd0a7e`, **several commits behind**; nothing from this work is pushed |

The intended push is the control plane only: the governance files, all launchers, the board, the
launch script, the preflight and gate modules, their test outputs, the independent review and the
launcher packet. No large scientific dataset.

## 3 · Launcher count and states

**Nine launchers.** Earlier packet metadata said eight and described the review as both 17 and 18
sections; both are corrected. The review has **19** numbered sections (0 through 18).

| state | n | tasks |
|---|---|---|
| **AUTHORIZED** | **5** | T-REG-asset-registration, T-LINT-prose-numbers, T-A0-lineage-variance, T-A2-ladder-population, T-A23-crosspair-curation |
| AWAITING_SPECIFICATION | 2 | T-A16-reciprocal-frame, T-A5b1-rtdna-anchors |
| AWAITING_ADOPTION | 1 | T-A3a-rule-and-e0-freeze |
| HELD | 1 | T-A5b2-ncrna-architecture |

Two tasks were demoted from AUTHORIZED during this certification:

- **T-A16** needs its two positive-control families named with their evidence source, its negative
  profile named and built by the same procedure, and a numerical asymmetry statistic and threshold
  frozen before execution.
- **T-A5b1** refers to a minimum unambiguous-anchor floor that the launcher never states.

**T-A3a remains AWAITING_ADOPTION.** No far-confirmation count was invented to open it.

## 4 · Worktree, branch and base

| worktree | branch | head | declared base | descends |
|---|---|---|---|---|
| `…-T-REG-asset-registration` | `task/T-REG-asset-registration` | 94a1a78 | 94a1a78 | yes |
| `…-T-LINT-prose-numbers` | `task/T-LINT-prose-numbers` | 94a1a78 | 94a1a78 | yes |
| `…-T-A0-lineage-variance` | `task/T-A0-lineage-variance` | 94a1a78 | 94a1a78 | yes |
| `…-T-A2-ladder-population` | `task/T-A2-ladder-population` | 94a1a78 | 94a1a78 | yes |
| `…-T-A23-crosspair-curation` | `task/T-A23-crosspair-curation` | 94a1a78 | 94a1a78 | yes |
| `…-T-A16-reciprocal-frame` | `task/T-A16-reciprocal-frame` | 94a1a78 | 94a1a78 | yes |
| `…-T-A3-confirmatory-population` | `task/T-A3-confirmatory-population` | 94a1a78 | 94a1a78 | yes |
| **T-A5b1** | — | — | — | **no worktree; correctly refused** |
| **T-A5b2** | — | `TBC` | — | **no worktree; correctly refused** |

## 5 · Failure-injection results

`programme/test_gates.py` → `programme/PREFLIGHT_TESTS.tsv`. **10 of 10 pass.**

| id | rule | fault injected | expected | result |
|---|---|---|---|---|
| FI-01 | only AUTHORIZED tasks launch | state = HELD | refuse | **PASS** |
| FI-02 | governance base must be current | base advanced under the launcher | refuse | **PASS** |
| FI-03 | inputs match their preregistered hash | hash altered | refuse | **PASS** |
| FI-04 | writes stay in the declared output directory | write to `results/` and to an unrelated absolute path | refuse both | **PASS** |
| FI-05 | criteria are immutable | criterion rewritten post hoc | refuse | **PASS** |
| FI-06 | a confirmatory population is consumed once | two tasks claim the same population | refuse the second | **PASS** |
| FI-07 | no consumption from an invalid task | producer `TASK_STATE=VOID` | refuse | **PASS** |
| **FI-08** | **a valid negative is consumable** | producer `PASS` + `FALSIFIED` | **ALLOW** | **PASS** |
| FI-08b | only declared consumables are readable | artifact off the consumable list | refuse | **PASS** |
| FI-09 | preregistration precedes job submission | prereg timestamped after the job | refuse | **PASS** |

FI-08 is the one test that must **allow**. It certifies the fix to the defect that mattered most: a
task that executes correctly and refutes its own hypothesis is a successful task, and the consumption
gate must not discard it.

## 6 · Dry-run result for every task

`programme/preflight.py --all` → `programme/PREFLIGHT_STATUS.tsv`.

| task | state | launchable | failed checks |
|---|---|---|---|
| T-REG-asset-registration | AUTHORIZED | **yes** | — |
| T-LINT-prose-numbers | AUTHORIZED | **yes** | — |
| T-A0-lineage-variance | AUTHORIZED | **yes** | — |
| T-A2-ladder-population | AUTHORIZED | **yes** | — |
| T-A23-crosspair-curation | AUTHORIZED | **yes** | — |
| T-A16-reciprocal-frame | AWAITING_SPECIFICATION | no | state |
| T-A5b1-rtdna-anchors | AWAITING_SPECIFICATION | no | state, unresolved criterion, no worktree |
| T-A5b2-ncrna-architecture | HELD | no | state, no worktree, unmet hard dependency |
| T-A3a-rule-and-e0-freeze | AWAITING_ADOPTION | no | state |

`launch_task.sh` now calls the preflight and refuses on any failure before touching anything.

## 7 · Stage-1 backup

| | |
|---|---|
| archive | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7_SEPTEMBER/backups/dbchar_workbench_2026-09-20.tar.gz` |
| sha256 | `140a006238e822c8653888810421606b7ca05f8cb414f895257a847c43d39b25` |
| bytes | 91,292,252 |
| source | `ARIS_OUTPUT/dbchar_workbench` on branch `dbchar-workbench` |
| files | 1,207 |
| verified | `sha256sum -c` re-read: **OK** |
| manifest | `docs/BACKUP_MANIFEST.tsv`, tracked |

Completed before this certification. The workbench was gitignored and present in no branch.

## 8 · Unresolved placeholders and criteria

| # | where | what is missing | who resolves |
|---|---|---|---|
| 1 | **T-A3a rule §8** | the minimum `\|CONFIRMATORY_FAR\|`, tied to intended inferential precision | **operator, tier C** |
| 2 | **T-A5b1** | the minimum unambiguous-anchor floor | operator or stage design |
| 3 | **T-A16** | the two positive-control families and their source; the named negative profile; a numerical asymmetry statistic and threshold | stage design |
| 4 | T-A5b2 | worktree and branch are `TBC`; scope depends on what A5b1 anchors | after A5b1 |
| 5 | T-A1, T-A6, T-A10 | launchers not yet written | coordinating session |
| 6 | T-LINT | the declared-mapping schema is specified but unpopulated, so the linter is triage, not a gate | by design, this task |
| 7 | governance | `human_input_audit: DONE` appears nowhere but the spec defining it, so nothing is promotable | **operator** |
| 8 | remote | nothing pushed; `origin/project-synthesis` is behind | **operator** |

## 9 · Tasks safe to launch in Batch One

These five, and only these five. All zero compute, disjoint output directories, no population
collisions, all gates green.

```
bash /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis/programme/launch_task.sh T-REG-asset-registration
bash /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis/programme/launch_task.sh T-LINT-prose-numbers
bash /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis/programme/launch_task.sh T-A0-lineage-variance
bash /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis/programme/launch_task.sh T-A2-ladder-population
bash /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis/programme/launch_task.sh T-A23-crosspair-curation
```

Use the absolute path. `programme/` exists only on the index branch and is not present inside a task
worktree; the launch script supplies the paths the session must read.

**Nothing else may launch.** The remaining four are refused by the machinery, not by convention.
