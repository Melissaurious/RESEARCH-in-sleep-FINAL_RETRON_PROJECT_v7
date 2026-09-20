---
record: WORKTREE_HYGIENE
date: 2026-09-20
status: AUDIT ONLY — nothing deleted
---

# Worktree hygiene — 34 worktrees, nothing removed

## 1 · The three checks you asked for

| check | result |
|---|---|
| **no two active tasks share an output directory** | ✅ **PASS** — 19 declared `output_directory` values, **19 distinct, 0 collisions** |
| **canonical large inputs referenced in place, not copied per worktree** | ✅ **PASS for task worktrees** — ⚠️ but see §3, there are 16 redundant copies inside the main worktree's gitignored scratch |
| **only one coordinating process writing `project-synthesis`** | ⚠️ **one writer, two resident** — see §4 |

## 2 · Task worktrees

`clean` = `git status --porcelain` empty. Size is the task's own `analysis/t_*` output only.

| task | branch | state | clean | output dir | size | removable after integration? |
|---|---|---|---|---|---|---|
| `T-P1b-identity-partition` | `task/T-P1b…` | **PILOT DONE**, full run gated | clean | `t_p1b_identity_partition` | 85M | ⛔ **NO — active**, full run pending |
| `T-C1b-pf00078-envelope-census` | `task/T-C1b…` | COMPLETE, awaiting review | clean | `t_c1b_envelope_census` | 235M | after review + integration |
| `T-A23c-source-retrieval` | `task/T-A23c…` | COMPLETE, erratum required | clean | `t_a23c_source_retrieval` | 60K | after the erratum is applied |
| `T-F1-motif-scan` | `task/T-F1…` | COMPLETE, never reviewed | clean | `t_f1_motif_scan` | 35M | after review |
| `T-REG3-content-hash` | `task/T-REG3…` | COMPLETE, never reviewed | clean | `t_reg3_content_hash` | 196K | after review |
| `T-M1-embedding-cache-verification` | `task/T-M1…` | ACCEPT_WITH_CHANGES | clean | `t_m1_embedding_cache_verification` | 476K | ⛔ **NO** — `T-M1b` supersedes it |
| `T-S1-structure-asset-inventory` | `task/T-S1…` | ACCEPT_WITH_CHANGES | clean | `t_s1_structure_asset_inventory` | 64K | ⛔ **NO** — `T-S1b` supersedes it |
| `T-C1-rt-core-extraction` | `task/T-C1…` | **REVIEW_FAILED**, superseded | clean | `t_c1_rt_core_extraction` | **149M** | ✅ **yes** — evidence is committed on its branch |
| `T-N1-neighbourhood-extraction-qa` | `task/T-N1…` | **REVIEW_FAILED**, superseded | clean | `t_n1_neighbourhood_extraction_qa` | **336M** | ✅ **yes** |
| `T-P1-relatedness-backbone` | `task/T-P1…` | **VOID**, superseded by P1b | clean | `t_p1_relatedness_backbone` | **436M** | ✅ **yes** |
| `T-N1b-neighbourhood-census` | `task/T-N1b…` | **VOID** | clean | `t_n1b_neighbourhood_census` | 28K | ✅ yes |
| `T-N1c-neighbourhood-census` | `task/T-N1c…` | **VOID, escalated** | clean | `t_n1c_neighbourhood_census` | 24K | ⛔ **NO** — D2's evidence |
| `T-LINT2-prose-numbers-gated` | `task/T-LINT2…` | **VOID ×2** | clean | `t_lint2_prose_numbers_gated` | 12M | ✅ yes |
| `T-LINT-prose-numbers` | `task/T-LINT…` | SUPERSEDED | clean | `t_lint_prose_numbers` | 5.9M | ✅ yes |
| `T-REG-asset-registration` | `task/T-REG…` | REVIEW_FAILED | clean | `t_reg_asset_registration` | 25M | ✅ yes |
| `T-A0-lineage-variance` | `task/T-A0…` | ACCEPT_WITH_CHANGES | clean | `t_a0_lineage_variance` | 156K | after `T-A0b` |
| `T-A2-ladder-population` | `task/T-A2…` | ACCEPT_WITH_CHANGES | clean | `t_a2_ladder_population` | 112K | after `T-A2b` |
| `T-A23-crosspair-curation` | `task/T-A23…` | REVIEW_FAILED, asset kept | clean | `t_a23_crosspair_curation` | 96K | ⛔ **NO** — unpromoted asset |
| `T-R1-rtdna-direct-mapping` | `task/T-R1…` | not run | clean | `t_r1_rtdna_direct_mapping` | 20K | ⛔ NO — D7 open |
| `T-AUDIT1`, `T-GATE1`, `T-A16`, `T-A3`, `T-A5b` | `task/…` | frozen / never run | clean | — | 0 | ⛔ NO — pending |

**Reclaimable from superseded/VOID task worktrees: ≈ 0.96 GB.** Every one has its evidence
**committed on its own branch**, so removing the worktree loses nothing — `git worktree remove`
does not delete the branch.

## 3 · ⚠️ The real disk problem is not worktrees — it is scratch in the main worktree

| location | size |
|---|---|
| `…_v7/ARIS_OUTPUT/` | **23 GB** |
| `…_v7/data/` | 2.2 GB |
| `…_v7/MELISSA_DATA/` | 1.8 GB |
| `…_v7/results/` | 177 MB |
| all 33 other worktrees combined | ≈ 11 GB |

⛔ **`rt_exact_v1.faa`, `rt_records_v1.parquet` and `rt_window_cds_v1.parquet` each exist in
17 copies** — 1 canonical + **16 inside `ARIS_OUTPUT/`**, in Stage-1 `rerun-*` and `dev/fixture/work`
directories. **Total duplicated: 4.9 GB.**

✅ **No copy is in a task worktree.** The "reference in place" rule is being followed by tasks. The
duplication is old Stage-1 rerun scratch in the main worktree.

⚠️ `docs/DATASET_REGISTRY.md` §7 records *"up to **four** copies"*. **There are sixteen.** The
registry understates it by 4×, and §7 already states these are *"rerun scratch and are safe to
delete independently"* of the `rt07_g5/` shard set.

⛔ **`ARIS_OUTPUT/rt07_g5/` is 12 GB and must NOT be deleted** — `DATASET_REGISTRY` §4 sets three
conditions, none met: off-host backup, hashes registered after backup, and `g6` no longer needing
shard diagnostics.

**Nothing has been deleted.** Reclaiming the 4.9 GB is an operator decision.

## 4 · Processes

| pid | elapsed | what |
|---|---|---|
| `327615` | 3 h 17 m | **this coordinating session** — holds `.agent-lock`, the only writer |
| `118496` | 11 h 41 m | the **previous coordinator**, still resident, **idle** — no writes observed since 13:19 |
| `3101448` | 1 d 3 h | a session in a **different project** (`RESEARCH-in-sleep-RETRON-DB_V4`) |

✅ **No compute is running** — no `mmseqs`, `hmmsearch`, `foldseek` or `cmsearch` process exists.
✅ **No Ibex job** — `squeue --me` empty.
⚠️ **Two coordinator processes remain resident against one worktree.** Only one is writing, but
`.agent-lock` is advisory and was silently overwritten once already today. **Closing `118496` would
remove the hazard.**

## 5 · Dirty worktrees — three, none harmful

| worktree | dirty | what |
|---|---|---|
| `synthesis` | 3 untracked | the A22 whitelist artefacts written this turn; committed below |
| `embeddings` | 1 untracked | `t0.npy` — stray scratch from an old run |
| `spire-ncrna` | 2 untracked | two `s10*` scripts never committed |

⚠️ The two stray files in `embeddings`/`spire-ncrna` are **uncommitted work in branches nothing
currently reads**. They are not deleted and not committed here — flagged so they are a decision
rather than a surprise when those worktrees are eventually removed.

## 6 · Recommended order, when you decide to reclaim

1. Close coordinator process `118496`. *(hazard, not disk)*
2. `git worktree remove` the five VOID/superseded task worktrees — **≈0.96 GB**, branches retained.
3. Delete the 16 duplicated canonical inputs under `ARIS_OUTPUT/rerun-*` and
   `ARIS_OUTPUT/01_database_characterization/*/dev|work|work2|smoke/derived/` — **≈4.9 GB**.
4. Correct `DATASET_REGISTRY` §7 from "four copies" to sixteen.
5. ⛔ Leave `ARIS_OUTPUT/rt07_g5/` (12 GB) alone until all three §4 conditions are met.

**Total safely reclaimable now: ≈ 5.9 GB of 2.8 TB free. This is hygiene, not pressure.**
