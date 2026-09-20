---
record: REVIEW_PACKET_P1b_A22
date: 2026-09-20
purpose: manual scientific review of the frozen T-P1b pilot and the T-A22 design freeze
status: READ-ONLY PACKET — no frozen file was modified to produce it
---

# Review packet — T-P1b pilot, T-A22 design freeze

**No frozen file was modified.** Verified: `git diff 1a6909f HEAD -- programme/tasks/T-P1b-identity-partition/`
and `git diff d4617e5 HEAD -- programme/tasks/T-A22-functional-contrast/` are both **empty**.

## 1 · Commits

| what | commit | branch |
|---|---|---|
| **T-P1b FREEZE** (launcher + implementation + fixtures + manifest, **before** any run) | **`1a6909f`** | `project-synthesis` |
| **T-P1b pilot output** | **`70a52c0`** | `task/T-P1b-identity-partition` |
| **T-A22 design freeze** | **`d4617e5`** | `project-synthesis` |
| task base for both | `0a220e3` | `project-synthesis` |
| governed `general/` pin | `cff9831` | — |

`70a52c0`'s parent is `1a6909f`, so the preregistration provably predates the outputs.

## 2 · Paths

Roots: `SYN = /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis` ·
`WT = /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-P1b-identity-partition`

| # | artefact | path | sha256 (16) |
|---|---|---|---|
| 1 | **P1b frozen launcher** | `$SYN/programme/tasks/T-P1b-identity-partition/TASK_LAUNCHER.md` | `5d37e7a9381ca512` |
| 2 | **P1b pilot report** | `$WT/analysis/t_p1b_identity_partition/TASK_REPORT.md` | — |
| 3 | **`P1b_controls.tsv`** (22 rows) | `$WT/analysis/t_p1b_identity_partition/tables/P1b_controls.tsv` | `771c6c3584913f73` |
| 4 | **`P1b_level_summary.tsv`** (7 rows) | `$WT/analysis/t_p1b_identity_partition/tables/P1b_level_summary.tsv` | `cdfdc628f1bafde8` |
| 5 | **multi-membership — the 17/457** | `$WT/analysis/t_p1b_identity_partition/tables/P1b_component_multimembership.tsv` | `a8ff31a35680c81c` |
| 5b | per-component incidence (3,199 rows) | `$WT/analysis/t_p1b_identity_partition/tables/P1b_component_incidence.tsv` | `03ce0f728389838a` |
| 6 | **`logs/run_log.json`** | `$WT/analysis/t_p1b_identity_partition/logs/run_log.json` | — |
| 7 | **`EXACT-BIPARTITE-COMPONENTS-14918` registry row** | `$SYN/programme/CANONICAL_DATASETS.tsv`, **line 31** | — |
| 8 | **T-A22 design freeze** | `$SYN/programme/tasks/T-A22-functional-contrast/DESIGN_FREEZE_01.md` | `e6085cf0ece4fd60` |
| 9 | **T-A22 feature whitelist** | ⛔ **DOES NOT EXIST AS CODE — see §4** | — |
| — | P1b implementation | `$SYN/programme/tasks/T-P1b-identity-partition/p1b_identity_partition.py` | `5163391b19a407e2` |
| — | P1b fixture generator | `$SYN/programme/tasks/T-P1b-identity-partition/p1b_fixtures.py` | `45b7a94dd58c09d4` |
| — | frozen fixture manifest | `$SYN/programme/tasks/T-P1b-identity-partition/FIXTURE_MANIFEST.tsv` | `9f613e477d234ed5` |

**To read item 7 alone:**

```bash
head -1 "$SYN/programme/CANONICAL_DATASETS.tsv"; sed -n '31p' "$SYN/programme/CANONICAL_DATASETS.tsv"
```

**To read any P1b artefact exactly as frozen**, independent of the working tree:

```bash
git -C "$SYN" show 1a6909f:programme/tasks/T-P1b-identity-partition/TASK_LAUNCHER.md
git -C "$WT"  show 70a52c0:analysis/t_p1b_identity_partition/TASK_REPORT.md
```

## 3 · The numbers a reviewer will want to check first

| quantity | value | where |
|---|---|---|
| controls | **22 / 22 PASS** | item 3 |
| duplicate control | **100/100 at all 7 levels** | item 3 |
| shuffled control | **0/100 at all 7 levels** | item 3 |
| assignment | **10,000 / 10,000, every level, 0 exclusions** | item 4 |
| clusters 40 % → 95 % | 2,905 · 4,092 · 5,602 · 6,858 · 7,605 · 8,151 · 8,443 | item 4 |
| components touched | **457** of 14,918 | item 5b |
| **components with ≥2 clusters at id40** | **17** (10×2, 1×3, 4×4, 1×5, 1×6) | item 5 |
| component reproduction | **14,918** derived independently | item 3 |
| runtime | 266.7 s, 24 threads | item 6 |

## 4 · ⛔ Item 9 does not exist, and that is a real gap

`DESIGN_FREEZE_01.md` §2d specifies a control:

> `A22_GATE_feature_whitelist` — *"no feature outside §2b is present in the model matrix — enforced
> by column-name whitelist, not by review"*

**That is a specification in prose. There is no code.** `programme/tasks/T-A22-functional-contrast/`
contains exactly one file, the design freeze itself. `T-A22` has **no launcher and no
implementation**, so nothing machine-enforces the whitelist today.

**Why this is not yet a defect:** the freeze exists to fix the *design* before `T-R1b` exposes
`PANEL-RTDNA-81`. The ordering it protects is freeze → `T-R1b` → `T-A22`, and `T-A22` has not been
drafted, let alone run.

**Why it must not be forgotten:** a whitelist that lives only in prose is exactly the class of
defect that produced *"I described a gate; I shipped a function"* in `T-GATE1`, and the comment that
claimed a guarantee the code did not provide in `launch_task.sh`. **When `T-A22` is drafted, the
whitelist must be an executable, blocking control with its own fixture** — a model matrix
deliberately containing a forbidden column must fail it.

✅ **Nothing is unprotected in the meantime**, because `PANEL-RTDNA-81` is unspent and `T-R1b` is
not authorised. The freeze's binding content — §2b's admissible/inadmissible feature lists — is
recorded and immutable at `d4617e5`.

## 5 · What this packet asks you to decide

1. Does the P1b pilot justify authorising the **full 501,561-sequence run**?
2. Is the `EXACT-BIPARTITE-COMPONENTS-14918` registration a sound resolution of the `PAIR-ELIG`
   conflict, or does the component-incidence join belong in `T-A0b` after all?
3. Is `DESIGN_FREEZE_01` §2b's feature list adequate to protect `T-A22`, given the measured
   62-of-81 overlap and the 5-versus-21 anchor-independent arm?
4. Should the `A22_GATE_feature_whitelist` be implemented **now**, as a standalone control, rather
   than waiting for `T-A22`'s launcher?

## 6 · Standing constraints, unchanged

⛔ The full P1b catalogue run is **not** authorised and has **not** started.
⛔ `PANEL-RTDNA-81` is **unspent**; `T-R1b` is **not** authorised.
⛔ Nothing has been pushed to GitHub.
