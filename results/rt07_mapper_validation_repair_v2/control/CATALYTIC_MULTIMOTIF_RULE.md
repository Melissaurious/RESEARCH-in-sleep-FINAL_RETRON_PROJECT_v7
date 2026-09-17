# Catalytic-state correspondence and multi-motif resolution — PREDECLARED

Date: 2026-09-17. Written **before** `catalytic_rule.py` was run. Repair 6.
Derived from construction families only. **No G2L example was used to choose this rule, and
UG25 was not read.**

## 1 · The defect being repaired

The G2L gate matched `[YF].DD` with a regex and took the **first** hit:

```python
d = DYAD.search(seq)                 # first match wins
hit = [a for a in mapped if abs(st[a]["residue_index"] - dp) <= 3]
```

`SFJ98198.1_G2L` carries a spurious `FDDD` at residue 23 — far outside the RT core — while its
true `YADD` sits at residue 216. Motif-first matching picked the decoy. The same sequence also
exposes the deeper error: the search was anchored to a **regex position**, then tested against
anchor *proximity*, when the alignment model already states exactly which HMM state is catalytic.

## 2 · The rule — state-anchored, not motif-anchored

> **The catalytic position is an HMM state, not a sequence motif.** Determine `CAT_STATE` once,
> from construction data. For any sequence, the catalytic call is the residue the alignment path
> places **at `CAT_STATE`**. Motif matching is used only to *characterise* that residue, never to
> locate it.

This inverts the previous logic and makes the multi-motif case disappear: the number of `[YF].DD`
occurrences in a sequence is irrelevant to *where* the catalytic call is made.

## 3 · Deriving `CAT_STATE` (construction only)

For every construction sequence: map each `[YF].DD` occurrence's first residue back to its HMM
state via the alignment path. `CAT_STATE` is the **modal** such state across all dyad-bearing
construction sequences of all six families.

**Falsification condition, declared now:** if fewer than **80%** of dyad-bearing construction
sequences place a `[YF].DD` at the modal state, the construction families do not agree on a
catalytic state, and the rule **FAILS CLOSED** — no `CAT_STATE` is frozen and no catalytic claim
is made anywhere downstream. This is a condition the data can actually violate.

## 4 · Per-sequence verdicts

| verdict | condition |
|---|---|
| `CATALYTIC_CONFIRMED` | `CAT_STATE` call is `MAPPED` **and** its residue begins a `[YF].DD` |
| `CATALYTIC_SUBSTITUTED` | `CAT_STATE` call is `MAPPED` but the residue does **not** begin a `[YF].DD` |
| `CATALYTIC_AMBIGUOUS` | `CAT_STATE` call is `AMBIGUOUS` |
| `CATALYTIC_UNSUPPORTED` | `CAT_STATE` call is `UNSUPPORTED` |
| `CATALYTIC_STATE_DELETED` | `CAT_STATE` is a `DELETED_STATE` in this sequence |

Each row additionally records `n_motifs_in_sequence` and `motif_at_cat_state` (boolean), so a
multi-motif sequence is visible as data rather than silently resolved.

## 5 · What is NOT claimed

`CAT_STATE` is derived from a **GII-derived HMM** and six construction families. It is an
**operational** catalytic coordinate in that frame. It is **not** a claim about catalytic
mechanism, and not evidence that any particular residue is catalytically active in vivo.

## 6 · Relationship to the frozen 150 anchors

`CAT_STATE` is expected to fall **outside** the 150 `ALL_PARTNERS` anchors — the anchors require
alignment across all six construction families, and the catalytic state need not satisfy that.
**This is why the G2L criterion-3 result was mis-reported as `NOT TESTABLE`:** the criterion asks
about the alignment path, which covers all 471 states, while the test asked about anchor
proximity, which covers 150. Catalytic correspondence is evaluated over the **full state range**
and is reported separately from anchor callability. The two are never pooled.
