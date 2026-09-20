---
record: RECONCILIATION_2026-09-20
date: 2026-09-20
session: reconciliation / handoff session (second coordinating session)
head_at_start: c77adb96f3bacd4c9d3acecbcd142f2a0b225897
head_at_reconciliation: be11fe79b69f32be4a0096bf16875c3145ae9a89
governed_pin: cff983144e2ad6fc01f648982fb61810dd77ddbe
scope: state reconciliation, independent cross-check, downstream planning
executed_science: none — one read-only audit instrument re-run unmodified
---

# RECONCILIATION — 2026-09-20

What the repository actually says, checked against what the boards claim, by a session that did not
run any of the work.

---

## 1 · Bootstrap status — PASS

| check | result | evidence |
|---|---|---|
| branch / worktree identity | `project-synthesis` @ `be11fe7`, worktree `…-synthesis`, tree **clean** | `git rev-parse`, `git status --porcelain` empty |
| `general/` submodule | initialised, **15 entries**, no local modification | `git submodule status` |
| governed pin | `cff9831` — recorded gitlink **and** checked-out SHA both match | `git -C general rev-parse HEAD` |
| governed spec checks | **OK** — every referenced repo path tracked, every spec documented, pin matches branch | `bash general/checks/specs_exist.sh` → exit 0 |
| runtime environment | `retron_tradicional`, Python 3.12.12, present at the documented path | `--version` |
| `programme/test_bootstrap.sh` | **24 passed, 0 failed** | full run |
| stale `docs/BLOCKED.md` reference | **ALREADY RESOLVED** — see §2 finding F5 | `6aa6dcc` here, `ba3154a` on `main` |

### Sole-ownership verification

A second coordinating session was writing this worktree during the first four minutes of this one
(HEAD moved `c77adb9` → `18dc2c0` → `b270147` → `be11fe7`; `T-N1c` appeared untracked at 13:15 and
was committed by 13:17). The operator confirmed that session finished. Independently verified before
taking ownership:

| check | result |
|---|---|
| HEAD stable | `be11fe7` unchanged across the verification window |
| working tree | clean; no `index.lock` / `HEAD.lock` |
| recent writes | no file modified under any `…_v7*` worktree in the preceding 5 minutes |
| local compute | no `hmmsearch` / `mmseqs` / `foldseek` / `cmsearch` process on the host |
| Ibex | `squeue --me` **empty**; last job `52124966` `t_p1_relatedness` **COMPLETED** 11:36:53, exit `0:0` |
| locks | `.agent-lock` holds this session's pid only |

⚠️ **The previous coordinator's process is still resident** (host pid `118496`, ~8 h 41 m elapsed)
but idle and writing nothing. Sole ownership is safe only while that remains true.

---

## 2 · Independent cross-check findings

Seven findings this session established directly from files and tools, not from the boards.

### ⛔ F1 · `T-A23c` mis-identified all four "secondhand primary" sources

`A23c_sources.tsv` resolves `SIM2019_ref32/33/35/36` to:

| source | resolved DOI | year |
|---|---|---|
| `SIM2019` (the review) | `10.1093/nar/gkz865` | **2019** |
| `SIM2019_ref32` | `10.1002/mco2.70758` | **2026** |
| `SIM2019_ref33` | `10.1038/s42003-026-10199-8` | **2026** |
| `SIM2019_ref35` | `10.7554/elife.99554` | **2026** |
| `SIM2019_ref36` | `10.1093/nar/gkag111` | **2026** |

**A 2019 review cannot cite four 2026 papers.** The cause is in `a23c_retrieve.py`: none of the four
has a DOI in `SOURCES`, so each is queried by an **invented descriptive title string**
(e.g. `"retron msDNA reverse transcriptase specificity"`), falling back to free-text search, and the
code takes `res[0]` — the top keyword match — with **no check that the retrieved record is the cited
reference.**

**What this invalidates:**

- `U3_secondhand_primaries` is recorded `resolvable from retrieved text`. **It is not resolved**; the
  four primaries have still never been read.
- `U6_direct_noncognate` counts **19 candidate passages**; only **6 come from `SIM2019`**. The other
  13 come from the four misidentified papers (`ref36` 5, `ref33` 4, `ref35` 3, `ref32` 1).

**What survives, and it is the valuable part.** The two load-bearing conclusions rest on `SIM2019`'s
**own** full text, which was retrieved correctly by DOI-free title match verified against the
returned title:

> *"Swapping region Ys between RT-Eco1 (Ec86) and RT-Eco3 (Ec73) produced chimeric proteins with
> 'swapped' msr recognition (32)."* → `U5`: engineered chimeras, **not** native non-cognate pairs.
>
> *"These are the only two examples where an RT can function on a non-cognate msr-msd."*
> → `U6`: exactly **two** reported native non-cognate functional examples.

**Why the controls did not catch it.** `A23c_POS_known_record` checks only that *a* named
known-indexed article is retrievable, and it used `SIM2019` itself — a source that **does** carry a
DOI. No control asserted **identity** between a retrieved record and the reference it claims to be.
This is the programme's recurring control failure in a new substrate: *a control that cannot
distinguish "found the right thing" from "found something" cannot detect a wrong match.*

**Disposition:** `T-A23c` is not VOID — it was correctly executed, its prohibitions held, and its
two findings stand. Its `U3` verdict and its `U6` passage count require an erratum, and the four
source rows must be marked `MISIDENTIFIED_NOT_THE_CITED_REFERENCE`.

### ⛔ F2 · Foldseek is installed, registered, and recorded as absent

`programme/LIVE_EXECUTION.tsv` holds `T-S2-foldseek-calibration` at `READY_WAITING_RESOURCE` with
the reason **"foldseek is NOT INSTALLED locally"**.

| check | result |
|---|---|
| `/home/borg/miniconda3/envs/esmologs/bin/foldseek` | present, **v10.941cd33** |
| `/home/borg/miniconda3/envs/retrons/bin/foldseek` | present, **v10.941cd33** |
| `data/README.md` L182 | **already registers** the `esmologs` path by name |
| `data/README.md` L194 | already registers Ibex module `foldseek/10-941cd33` — the same version |

`CLAUDE.md` states the rule that was broken: *"Special tools/resources live outside the primary
environment and are registered in `data/README.md`; do not conclude a dependency is absent until the
registered environments and Ibex resources have been checked."*

**This is the fifth instance of the pattern in `CAPABILITY_STATE.md` §5** — a capability present at
the root and recorded absent from a narrower context. The previous four were a deferred reviewer
tool, an uninitialised submodule, sandbox-hidden GPUs, and an `rg` shell function. This one did not
even need a different context: the answer was in the project's own canonical registry.

**Disposition:** `T-S2` is **not** resource-blocked. It is blocked on one thing only — it has no
declared metric and no declared threshold, which is a scientific specification and therefore the
operator's.

### ⛔ F3 · The operator ruling of 2026-09-20 had no decision record

Cited by section number in four launchers, one executed script, one erratum and one escalation;
present in `docs/decisions/` nowhere. Reconstructed from those citations at
`docs/decisions/2026-09-20_operator_ruling_exposure_freeze_controls.md`, marked `PROVISIONAL`.
**Sections 4–7 are cited nowhere and are not reconstructed.**

### ⛔ F4 · `TASK_PRIOR_WORK_*.tsv` were claimed complete and never landed

`LIVE_EXECUTION.tsv` records `T-PRIORWORK-task-audit` `COMPLETE_AWAITING_REVIEW` with
`TASK_PRIOR_WORK_*.tsv` among its outputs and **"15/15 named anchors PASS"** as its result. No such
file existed on disk. Re-run unmodified from the committed script: **15 named anchors, 15 PASS, 0
fail**, 39 liveness PASS, 1 dead substrate (`rdb_data_derived:header`). Now landed with
`programme/prior_work/TASK_PRIOR_WORK.md`.

The number was right. It was unverifiable for eight hours, which is what `WORKING_RULES` §7 forbids.

### ✅ F5 · `docs/BLOCKED.md` is already repaired — on both branches

`COORDINATION_STATE.md` §2 records `main` @ `94a1a78` as **failing `specs_exist.sh`**, and §5 item 6
asks the operator to repair it. Both are **stale**: `main` is now `ba3154a`
(*"docs: point BLOCKED.md at the real path…"*), and `docs/BLOCKED.md` is **byte-identical** between
`main` and `project-synthesis`. `specs_exist.sh` passes here. **Open decision #6 is closed.**

### ⚠️ F6 · Two coordinating sessions wrote one worktree, for the second time

`WORKING_RULES` §1 permits exactly one coordinating session. Commit `6aa6dcc` already recorded this
hazard after a task session wrote into this worktree. It recurred today at coordinator level and was
caught only because the second session listed the directory twice. **There is still no mechanism
preventing it** — `.agent-lock` is advisory and was overwritten without complaint.

### ⚠️ F7 · Task-count drift

`PARALLEL_EXECUTION_PLAN.md` L4 says the register holds **53** tasks; the register holds **54**, and
`SCIENTIFIC_DAG.md` says 54 in two places and 53 in a third. Cosmetic, but it is the class of drift
the numeric linter was built to catch — and that linter is `VOID`.

---

## 3 · Reconciled task table

`TASK_STATE` / `SCIENTIFIC_OUTCOME` are the `WORKING_RULES` §5 fields where a report exists.
**No task in this programme carries a §5-conformant `TASK_REPORT.md`, so no output is formally
consumable.** That is review `01a0bdfa`'s finding and it still holds.

| task | pre-run freeze | output commit | TASK_STATE | SCIENTIFIC_OUTCOME | review verdict | consumable | non-consumable | population × endpoint exposed | required correction | status |
|---|---|---|---|---|---|---|---|---|---|---|
| `T-REG-asset-registration` | — | `9052ccb` | PASS (self) | DESCRIPTIVE | **REVIEW_FAILED** `01a0bc53` | none | `ASSET_SWEEP.tsv` inventory (kept as asset) | none | 0.217 % coverage endpoint **withdrawn** | closed; successors `T-REG2/3/4` |
| `T-LINT-prose-numbers` | — | `82059df` | PASS (self) | NOT_APPLICABLE | **REVIEW_FAILED** `01a0bc53` | none | linter artefacts | none | superseded, record inherited | `SUPERSEDED` |
| `T-LINT2-prose-numbers-gated` | — | `8d39c21` | **VOID** | NOT_APPLICABLE | **REJECT ×2** `01a0bc99`, `01a0bcac` | none | v2/v3 artefacts, preserved | none | catcher fitted post-failure; criterion change was Tier C | `VOID_REVIEW_FAILED`; successor `T-LINT5` |
| `T-A0-lineage-variance` | — | `c724df7` | PASS | **BOUND** (type-blocked) | ACCEPT_WITH_CHANGES `01a0bc53` → `01a0bc96`, **7/7 applied** | none (no §5 report) | correction record | PAIR-ELIG (already exhausted) | applied | `ACCEPT_WITH_CHANGES`; successor `T-A0b` |
| `T-A2-ladder-population` | — | `a1b76d1` | PASS | **DESCRIPTIVE** (was `SUPPORTS_H1`) | ACCEPT_WITH_CHANGES `01a0bc53` → `01a0bc97`, **7/7 applied** | none | correction record | PAIR-ELIG (already exhausted) | outcome corrected | `ACCEPT_WITH_CHANGES`; successor `T-A2b` |
| `T-A23-crosspair-curation` | — | `98f3125` | PASS (self) | DESCRIPTIVE | **REVIEW_FAILED** `01a0bc53` | none | `A23_geometry.tsv` as **unpromoted asset** | LIT-CROSSPAIR (external) | 56 refused as headline; **7 blocks** defensible; positive control circular | Stage 12 **not** opened |
| `T-A23c-source-retrieval` | **`c77adb9`** | `c77adb9`+ | PASS | DESCRIPTIVE | **not yet reviewed** | none pending review | 4 source rows **misidentified** (F1) | LIT-CROSSPAIR (external) | **erratum required**: `U3` verdict, `U6` passage count, 4 source rows | `COMPLETE_AWAITING_REVIEW` |
| `T-C1-rt-core-extraction` | ⛔ none | `65b2355` | PASS (self) | DESCRIPTIVE | **REJECT** `01a0bdfa` | none | envelope table | RT-EXACT × `rt_profile_detection` | superseded | `REVIEW_FAILED` → `T-C1b` |
| `T-C1b-pf00078-envelope-census` | **`c77adb9`** | `c77adb9`+ | PASS | DESCRIPTIVE | **not yet reviewed** | pending review | — | RT-EXACT × `rt_profile_detection` | none known | `COMPLETE_AWAITING_REVIEW` |
| `T-F1-motif-scan` | ⛔ none | `31b0860` | PASS (self) | DESCRIPTIVE | **not reviewed** | none | — | RT-EXACT × `rt_motif_detection` | needs its own review | `COMPLETE_AWAITING_REVIEW` |
| `T-P1-relatedness-backbone` | ⛔ none | `20f8bc2` | **VOID** | NOT_APPLICABLE | **REJECT → VOID** `01a0bdfa` | none | cluster tables, preserved | RT-EXACT × `rt_identity_clustering` | `ERRATUM_01` **false**, superseded by `ERRATUM_02` | `VOID` |
| `T-N1-neighbourhood-extraction-qa` | ⛔ none | `c374867` | PASS (self) | DESCRIPTIVE | **REJECT** `01a0bdfa` | none | per-record table | RT-RECORDS-ALL-FAMILIES × `neighbourhood_geometry` | population **misdeclared** as RETRON-LOCI | `REVIEW_FAILED` |
| `T-N1b-neighbourhood-census` | **`c77adb9`** | `c77adb9`+ | **VOID** | NOT_APPLICABLE | n/a — stopped by own control | none | controls table only | same endpoint | none — preserve as executed | `VOID` |
| `T-N1c-neighbourhood-census` | **`b270147`** | `b270147`+ | **VOID** | NOT_APPLICABLE | n/a — stopped by own control | none | controls only; **no primary table by design** | same endpoint | none — **escalated** | `VOID_ESCALATED` |
| `T-M1-embedding-cache-verification` | ⛔ none | `e1f828f` | PASS | DESCRIPTIVE | **ACCEPT_WITH_CHANGES** `01a0bdfa` | none until changes land | `rt_positives_emb` **misidentified** | none | 4 changes: identity, float32 norms, hash caches, land 4,000 rows | changes **pending** |
| `T-S1-structure-asset-inventory` | ⛔ none | `71f776a` | PASS | DESCRIPTIVE | **ACCEPT_WITH_CHANGES** `01a0bdfa` | none until changes land | 97-collection inventory | none | "0 missing" = directories; 44,608 = files not structures | changes **pending** |
| `T-REG3-content-hash` | ⛔ none | `12be219` | PASS (self) | DESCRIPTIVE | **not reviewed** | none | 602 pin groups | none | needs its own review | `COMPLETE_AWAITING_REVIEW` |
| `T-PRIORWORK-task-audit` | — | `9bcbb71` | PASS | DESCRIPTIVE | **not reviewed** | estate sweep tables | **task tables were missing** (F4) | none | re-run and landed by this session | `COMPLETE_AWAITING_REVIEW` |

**Reviews on record:** `01a0bc53` (Batch One, FAIL) · `01a0bc96` / `01a0bc97` (corrections,
ACCEPT_WITH_CHANGES) · `01a0bc99` / `01a0bcac` (T-LINT2, REJECT ×2) · `01a0bcb2` (downstream plan,
REJECT) · `01a0bde9` (scientific, ACCEPT_WITH_CHANGES) · `01a0bdfa` (six executed tasks, no
unconditional ACCEPT). **Nothing has ever been promoted.**

### The systemic pattern across the two batches

| | Batch 01 (7 tasks) | Batch 02 (4 tasks) |
|---|---|---|
| frozen before execution | **0 of 7** | **4 of 4** |
| rejected / VOID | 4 | 2 — **both stopped by their own controls** |
| failed *because* a control could not fail | 2 (`T-N1` null forced to zero; `T-P1` controls never gated) | 0 |

**The freeze worked.** Batch 02's two VOIDs are controls doing their job and a threshold not being
relaxed after the fact — the opposite failure mode from Batch 01, and much the better one.
