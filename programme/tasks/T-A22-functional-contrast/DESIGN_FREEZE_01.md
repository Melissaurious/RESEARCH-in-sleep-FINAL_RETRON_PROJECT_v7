---
record: T-A22-DESIGN-FREEZE-01
task_id: T-A22-functional-contrast
date: 2026-09-20
kind: DESIGN FREEZE — a protection, not a launcher
status: FROZEN on this commit; binding on T-A22 and on T-R1b
reason: T-R1b would expose PANEL-RTDNA-81, and 62 of its 81 anchors are T-A22's positive class
---

# T-A22 · design freeze, taken BEFORE `T-R1b` spends the anchors

⛔ **This is not a launcher and authorises no execution.** It fixes `T-A22`'s feature set, endpoint
and validation design **in advance**, so that `T-R1b`'s exposure of `PANEL-RTDNA-81` cannot later
be accused — correctly — of having shaped them.

## 1 · The hazard, measured exactly

`PANEL-175`, sha256 `80b2f565…9577`. Counted directly from the file, 2026-09-20:

| set | n | producers | measured non-producers |
|---|---|---|---|
| panel total | **175** | — | — |
| `RTDNA_sequence` present — **`PANEL-RTDNA-81`**, what `T-R1b` spends | **81** | — | — |
| measured production — **`PANEL-PRODUCERS-67-36`**, `T-A22`'s population | **103** | **67** | **36** |
| ⛔ **anchor AND measured — the overlap** | **77** | **62** | 15 |
| measured but **no** anchor | **26** | **5** | 21 |
| anchor but no measurement | 4 | — | — |
| ⛔ **production cell EMPTY** | **72** | — | **never a negative** |

> **77 of the 81 anchors carry a measured production value, and 62 of them are producers.**
> An anchor-derived feature is therefore built, in large part, out of `T-A22`'s positive class.
> Choosing features *after* seeing the anchors would be selecting on the outcome.

## 2 · What is frozen, and it is frozen now

### 2a · Endpoint

> Do elements with **measured RT-DNA production > 0** differ from elements with a **measured
> production of exactly 0**, on the feature set fixed in §2b?

⛔ **The 72 elements with an empty production cell are NOT negatives and are excluded from the
contrast entirely.** An unmeasured element is not a measured zero. They may be described; they may
never be counted.

### 2b · Feature set — fixed here, before any anchor is seen

**Admissible.** Derived from the RT protein or the ncRNA sequence alone:

1. RT length;
2. PF00078 envelope presence, coordinates and score (`C1B-ENVELOPES-501561`);
3. YxDD motif presence and position (`T-F1`);
4. ncRNA length;
5. RT sequence composition;
6. `T-P1b` cluster membership at a declared level — **relatedness as a nuisance term, never as a
   predictor of function**.

⛔ **Inadmissible, permanently, in this task.** Anything derived from a measured RT-DNA sequence:
RT-DNA length, RT-DNA start/end coordinates, RT-DNA position within the ncRNA, anchor-derived
boundary features, or any `T-R1b` output. **These are the features the overlap contaminates.**

⚠️ Adding a feature to §2b after this commit is **a new task with a new ID**, not an amendment.
`WORKING_RULES` §7: a changed criterion is a new task inheriting the old record.

### 2c · Validation design — and its honest bound

| arm | n | producers | non-producers | status |
|---|---|---|---|---|
| **primary** — all measured | 103 | 67 | 36 | descriptive contrast on §2b features |
| **anchor-independent** — measured, no anchor | **26** | **5** | **21** | the only arm untouched by `T-R1b` |

⛔ **The anchor-independent arm is 5 producers against 21 non-producers. That is an anecdote, not a
validation set, and this document says so in advance rather than at review.** No statistic computed
on 5 positives is a confirmatory result. It is reported as counts, with its n, and never as a rate
or a p-value.

**This is a real ceiling on goal 12 and it is stated now**, while it is still a design constraint
rather than an excuse.

### 2d · Controls

| control | type | must show |
|---|---|---|
| `A22_POS_label_recovery` | positive | the pipeline recovers the known producer/non-producer split from the register, 103/103 |
| `A22_NEG_shuffled_labels` | negative | with production labels permuted, every feature contrast collapses to chance |
| `A22_GATE_empty_excluded` | blocking | exactly 72 empty-production elements are excluded and **none** is counted as a negative |
| `A22_GATE_feature_whitelist` | blocking | **no feature outside §2b is present in the model matrix** — enforced by column-name whitelist, not by review |

### 2e · Interpretation ceiling

⛔ `T-A22` reports a **descriptive contrast on 103 assayed elements from one published panel**. It
is not a predictor of retron function, not a general rule about retrons, and not transferable to the
501,561-sequence catalogue. `PANEL-175` is **not** a random sample of retrons.

## 3 · Consequence for `T-R1b` — the ordering rule

✅ **`T-R1b` may now proceed** when the operator authorises the `PANEL-RTDNA-81` spend, **because
this freeze exists**. The ordering that protects both tasks:

1. **This design freeze lands** ← *this commit*
2. `T-R1b` runs and exposes `PANEL-RTDNA-81`
3. `T-A22` runs on the **frozen** §2b feature set

⛔ **If §2b is edited after step 2, `T-A22` is VOID.** That is the whole point of the document.

⚠️ **Decision D7 is still open and still separate.** `T-A5b1` and `T-R1b` are the same task and
would spend the 81 anchors twice for one table. This freeze protects `T-A22`; it does **not** merge
`T-A5b1` and `T-R1b`.

## 4 · What this document does not do

- It does not authorise `T-A22` to run.
- It does not authorise `T-R1b` to spend `PANEL-RTDNA-81` — that is an operator decision per spend.
- It does not claim the anchor-independent arm is adequate. **It states the opposite.**
