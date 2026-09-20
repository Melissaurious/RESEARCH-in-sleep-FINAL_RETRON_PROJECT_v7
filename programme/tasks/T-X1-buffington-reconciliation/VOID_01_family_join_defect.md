---
record: T-X1-VOID-01
task_id: T-X1-buffington-reconciliation
date: 2026-09-20
kind: VOID — a blocking control failed. STOP, escalate, new task ID.
freeze_commit: 7e7f598
state: VOID
successor: T-X1b-buffington-reconciliation (not yet drafted)
---

# T-X1 is VOID — `X1_POS_populations_unchanged` failed

```
expectation : after the run the populations still count (501561, 16458, 30924, 78287)
observed    : (501561, 16458, 30924, 0)
state       : FAIL
```

**The control worked exactly as intended.** Three of four populations returned unchanged; the
fourth — the Retron subset — came back **0** where 78,287 was expected. `WORKING_RULES` §6b: a
failed blocking control ends the task. **No v2 under this identity.**

## 1 · Root cause — a silent fallback, not a data problem

`x1_reconcile.py` resolved the family column like this:

```python
cols = ft.schema.names
fcol = "rt_family" if "rt_family" in cols else cols[1]      # ⛔ the defect
```

`rt_family_baseline_v1.parquet` has **no column named `rt_family`**. Its schema is:

```
rt_seq_hash · rt_aa_len · n_records · n_loci · n_genomes · n_species · …
             ^^^^^^^^^ cols[1]
```

So the fallback bound the "family" to **`rt_aa_len` — the protein length in residues**. The join
then asked *which sequences have `rt_aa_len == "Retron"`*, which is never true, giving **0**.

**The correct column is `family_label`.** Verified directly:

| | |
|---|---|
| `family_label` distinct values | **42** |
| `family_label == "Retron"` | **78,287** ✅ matches the expectation exactly |
| top five | RVT-GII 256,624 · Retron 78,287 · RVT-DGRs 76,111 · RVT-UG2 8,423 · MULTI 7,593 |

⛔ **The defect is the fallback itself, not the column name.** `else cols[1]` turns *"the column I
expected is absent"* — which should stop the task — into *"use whatever is second"*, which produces
a confident wrong number. A missing expected column must be a **STOP**.

## 2 · What is and is not affected in X1

| output | status |
|---|---|
| `X1_row_classification.tsv` | ⚠️ the `rt_is_retron_family` column is **always False** |
| everything else in that file | overlap classes, both RT hashes, msr orientation, pair presence, Axis B — **computed without the family join** |
| `X1_hashes.tsv` | unaffected |
| `X1_operator_nominations.tsv` | unaffected |
| `X1_summary.tsv` | unaffected — it has no family row |

**Nothing is promoted from a VOID task.** The outputs are preserved exactly as executed and are
**not consumable**.

## 3 · ⛔ The same defect is in T-P1b, which is running now

`p1b_identity_partition.py` line 454 carries the identical line. **`T-P1b`'s `describe()` has been
joining on `rt_aa_len` as well** — in the accepted pilot and in the full run now executing.

| P1b output | status |
|---|---|
| `P1b_cluster_family_composition.tsv` | ⛔ **INVALID** — `dominant_family` holds protein lengths (`990`, `482`, `340`), not families |
| `P1b_cross_family_clusters.tsv` | ⛔ **INVALID** — counts distinct *lengths* per cluster |
| `P1b_clusters_id{40…95}.tsv` | ✅ **unaffected** |
| `P1b_level_summary.tsv` | ✅ unaffected |
| `P1b_component_incidence.tsv` | ✅ unaffected |
| `P1b_component_multimembership.tsv` | ✅ unaffected |
| every P1b control | ✅ unaffected — none touches `describe()` |

✅ **P1b's primary deliverable is intact.** Cluster formation is label-blind by construction;
`describe()` runs *after* every cluster file is written and feeds nothing. The clustering, the level
summary and the component incidence — including the multi-membership table `T-A0b` needs — never
see a family label.

⛔ **RETRACTION.** The figure I reported from the P1b pilot — *"multi-family clusters fall from
0.3029 at id40 to 0.0611 at id95"* — **is withdrawn.** It counted distinct **protein lengths** per
cluster, not families. It means nothing. Longer clusters simply contain more distinct lengths.

**The running P1b job is NOT being touched**, per the standing instruction. It will land two invalid
descriptive tables; they are recorded here as invalid in advance, and its `TASK_REPORT.md` will say
so rather than presenting them.

## 4 · Required in the successor, `T-X1b`

1. Use **`family_label`**, named explicitly.
2. ⛔ **Delete the `else cols[1]` fallback.** An absent expected column is a **blocking STOP**.
3. Add a control: *the family join returns exactly 78,287 `Retron` sequences* — the assertion whose
   absence let this through as a post-run surprise rather than a pre-run gate.
4. Everything else in `T-X1` is unchanged and was correct — 10/10 pre-run controls passed, the
   Buffington reconciliation logic is untouched by this defect.

## 5 · Registry correction required

`programme/CANONICAL_DATASETS.tsv` → `RT-FAMILY-LABELS-613` states its source column wrongly and
its count is from a **different vocabulary**:

| field | recorded | verified |
|---|---|---|
| column | implied `rt_family` | **`family_label`** |
| distinct values | **613** | **42** in `family_label`; `file_label` in `rt_records_v1` is **also 42** |

⚠️ **Where 613 comes from is not established.** `T-C1b` reported 613 families and read
`type_set_norm` from `rt_records_v1.parquet` — a third vocabulary. **Identifying it is backlog**,
not chased here: no task in the current wave consumes it except through the join now being fixed.
The dataset id keeps its name for continuity; the row is corrected to state what was verified and
to flag the 613 as unresolved.
