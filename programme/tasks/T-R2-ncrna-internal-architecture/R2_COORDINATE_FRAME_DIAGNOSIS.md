---
record: R2_COORDINATE_FRAME_DIAGNOSIS
task_id: T-R2-ncrna-internal-architecture
date: 2026-09-20
kind: DIAGNOSIS — required before R2 may freeze
verdict: NO coordinate-frame mismatch exists. The 2.148 was a reporting artefact in my own summary.
---

# Diagnosis — the 2.148 ratio

**The operator required the actual field/coordinate mismatch to be identified, not the anomalous
elements excluded. It has been identified. There is no mismatch in the data.**

## 1 · The claim that had to be checked

`T-R1b` established that all 81 RT-DNA sequences are **exact** matches to the reverse complement of
their own ncRNA. If R2 uses the same sequence objects, then for every element:

```
len(RT-DNA) <= len(ncRNA)
```

An R2 draft reported a **maximum ratio of 2.148**, which is impossible under that constraint. Either
R1b was wrong, or R2 was mixing fields, or the number was wrong.

## 2 · What the data actually says

Verified directly against the panel sequences and R1b's coordinates, all 81:

| check | result |
|---|---|
| `len(RT-DNA) <= len(ncRNA)` | **81 / 81** |
| mapped span == `len(RT-DNA)` | **81 / 81** |
| `1 <= start <= end <= len(ncRNA)` | **81 / 81** |
| **`revcomp(ncRNA[start:end]) == RT-DNA`** | **81 / 81** |
| `mapping_state == EXACT_UNIQUE` | **81 / 81** |

| **per-element** ratio | min | median | max |
|---|---|---|---|
| `len(RT-DNA) / len(ncRNA)` | **0.3925** | **0.5455** | **0.8602** |

**Zero elements violate anything.** R1b is internally consistent and its coordinates round-trip.

## 3 · ⛔ Where the 2.148 came from — my own summary line

During drafting I computed the "ratio" like this:

```python
min → min(rtdna_lens) / max(ncrna_lens)     # 55 / 293 = 0.188
max → max(rtdna_lens) / min(ncrna_lens)     # 189 / 88 = 2.148
```

**Those divide the longest RT-DNA by the shortest ncRNA — across *different* elements.** It is not a
ratio of anything. The longest RT-DNA (189 nt) and the shortest ncRNA (88 nt) belong to two
different retrons that were never compared to each other.

**Both the 0.188 and the 2.148 are artefacts of that line.** The correct per-element range is
**0.3925 – 0.8602**.

## 4 · Consequences, applied

1. **`R2_tierA_anomalies.tsv` is withdrawn**, and with it the rule that anomalous elements are
   excluded from aggregates. **There are no anomalous elements.** Excluding them would have removed
   real data to accommodate a bad statistic.
2. The launcher's §3b table is corrected to the **per-element** values.
3. ⛔ **The blocking gate is added anyway, and permanently** — `r2_consistency_gate.py`, 9 checks,
   9 PASS. A statistic that mixed elements reached a launcher; the invariant is now machine-checked
   against the sequences rather than trusted.
4. The gate includes `R2_GATE_revcomp_roundtrip`, which **re-derives R1b's result independently**
   from the coordinates and the raw sequences, so Stage 1 cannot build on a mis-transcribed table.

## 5 · The lesson, which is not about this number

**An aggregate computed across elements is not a per-element property**, and the two can look
identical in a summary line. `min(a)/max(b)` and `max(a)/min(b)` are bounds on a ratio **only** when
`a` and `b` are independent — which lengths of paired sequences are not.

This is the same class as the `T-X1` `else cols[1]` fallback and the `EXTERNAL_NEW` overload: **a
plausible-looking value produced by a subtly wrong reduction.** In each case the measurements were
fine and the summary was not. ⚠️ **Nothing downstream consumed the 2.148** — it appeared only in a
report and a draft launcher, both corrected here.
