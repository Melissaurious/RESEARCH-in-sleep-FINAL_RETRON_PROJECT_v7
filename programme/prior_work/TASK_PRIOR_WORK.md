# TASK_PRIOR_WORK — has THIS analysis already been done inside the governed record?

**Run 2026-09-20T10:29:56Z by the reconciliation session, elapsed 152.3 s.** Instrument:
`programme/prior_work/task_prior_work.py` v1.0.0, committed at `9bcbb71` and re-run unmodified.
Outputs: `TASK_PRIOR_WORK_SUMMARY.tsv` (per task), `TASK_PRIOR_WORK_BY_ROOT.tsv`
(per task × root), `TASK_PRIOR_WORK_CONTROLS.tsv`, `TASK_PRIOR_WORK_META.json`.

> **Why this exists as a second sweep.** `PRIOR_WORK_LOOKUP.md` answers *"does material on this
> topic exist anywhere in the 155 GB estate"* — 24 topics, size-capped, 707,902 files.
> This answers the sharper question per task: *has this analysis already been done inside the
> **governed** record, on which substrate, and is the number re-derivable?* The governed roots are
> ~1,400 files, so this sweep is **unbounded**: every file read, every `.tsv`/`.csv` header parsed,
> every parquet schema opened.

---

## ⛔ Why it was re-run: the outputs were claimed and never landed

`programme/LIVE_EXECUTION.tsv` records `T-PRIORWORK-task-audit` as `COMPLETE_AWAITING_REVIEW`,
declares `TASK_PRIOR_WORK_*.tsv` among its expected outputs, and reports the result
**"15/15 named anchors PASS"**.

**No `TASK_PRIOR_WORK_*` file existed anywhere on disk.** Only the script was committed. The
"15/15" was therefore a number in prose with no table cell behind it, which
`WORKING_RULES` §7 forbids.

The script was re-run unmodified. **The claim reproduces exactly: 15 named anchors, 15 PASS, 0
failures.** The finding is not that the number was wrong — it is that it was unverifiable for eight
hours, and the standing rule exists precisely so that cannot happen.

---

## 1 · Controls — two kinds, both blocking

| control | result |
|---|---|
| **substrate liveness**, per root × substrate — asserts the reader actually parsed something of that kind | **39 PASS**, 12 `NOT_EVALUABLE` (substrate empty on that root), **1 FAIL** |
| **named anchor**, per task — a term asserted present at a named root on a named substrate | **15 PASS, 0 FAIL**, 35 `NO_ANCHOR` |

⛔ **One dead substrate: `rdb_data_derived:header`.** Absence is **not reportable** for that root ×
substrate combination. Recorded in `TASK_PRIOR_WORK_META.json` under `dead_substrates`.

⚠️ **`NO_ANCHOR` is a real weakness, not a formality.** 35 of 50 tasks have no named anchor, so
their absence rests on substrate liveness alone. For those, `NOT_DONE` means *the reader was alive
on this root and did not find it* — not *a term known to be present was checked and this was
absent*. Every `NO_ANCHOR` classification below is correspondingly weaker and is marked.

## 2 · The four tasks with genuinely zero prior material

These returned `n_roots_with_hits = 0` across path, content, header and parquet:

| task | reading |
|---|---|
| `T-REG2-registry-coverage-validated` | the validated re-derivation does not exist; the withdrawn 0.217 % endpoint is all there is |
| `T-LINT5-prose-numbers-gated` | third linter design, never written |
| `T-AUDIT2-task-report-backfill` | **no task report satisfying the §5 contract exists anywhere** — independently consistent with review `01a0bdfa`'s finding that nothing is consumable |
| `T-A23d-primary-verification` | the four SIM2019 primaries have never been read at first hand in this estate |

All four are `NOT_DONE`, all four `WEAK — no anchor`.

## 3 · The heaviest prior material, and what it does and does not license

| task | content files | roots | classification |
|---|---|---|---|
| `T-RT07-definition-status` | 1,305 | 13 | `SCIENTIFICALLY_ADMISSIBLE` — Stage 2 closed and independently reviewed |
| `T-S1-structure-asset-inventory` | 919 | 13 | `ASSET_ONLY` — executed, `ACCEPT_WITH_CHANGES` |
| `T-F2-domain-architecture` | 892 | 13 | `DONE_NEEDS_IDENTITY_CHECK` — corrects the dead-instrument absence claim |
| `T-A5b2-ncrna-architecture` | 892 | 13 | `DONE_NEEDS_IDENTITY_CHECK`, and its control is circular |
| `T-AUDIT1-circular-control-sweep` | 829 | 10 | material is the launchers themselves |
| `T-A5b1-rtdna-anchors` | 819 | 13 | `DONE_NEEDS_IDENTITY_CHECK` — and duplicates `T-R1` |
| `T-C1-rt-core-extraction` | 813 | 13 | `SUPERSEDED` by `T-C1b` |
| `T-A10-genomic-architecture` | 806 | 13 | `DONE_NEEDS_REPRODUCTION` — 44.3 M CDS rows already landed |
| `T-P2-character-economy-audit` | 672 | 12 | `BOUNDED_NEGATIVE` upstream — 312 trees, 157 alignable characters |

> **Take the files and the refutations. Leave the numbers.** A hit can only move a task **out of**
> `NOT_DONE`. It can never move one **into** `SCIENTIFICALLY_ADMISSIBLE`.

## 4 · Declared blind spots

- `parquet` is `NOT_EVALUABLE` on 11 of 13 roots — those roots hold no parquet. Absence of a
  *quantity* is therefore established from `header` on most roots, and `header` is dead on one.
- `idea_stage:header` is `NOT_EVALUABLE`.
- The sweep covers the **governed** record only: this worktree, `…_v7`, `RESEARCH-retron-db`,
  `references/`, `idea-stage/` and seven task worktrees. The wider 155 GB estate is
  `PRIOR_WORK_LOOKUP.md`'s job, and its bound is declared there.
