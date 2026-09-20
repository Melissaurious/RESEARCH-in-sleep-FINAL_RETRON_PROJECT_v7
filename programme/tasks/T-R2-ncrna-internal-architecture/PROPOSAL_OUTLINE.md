---
record: T-R2-PROPOSAL-OUTLINE
task_id: T-R2-ncrna-internal-architecture
date: 2026-09-20
status: NOMINATED — outline only. No launcher, no implementation, no execution.
depends_on: T-R1b (anchors), T-X1 (Buffington reconciliation)
---

# T-R2 · ncRNA internal architecture — proposal outline

⛔ **Nominated, not drafted.** No launcher, no implementation, no controls, nothing run. This is the
shape of the task and the evidence discipline it would need.

## 1 · The question

> Can experimentally anchored RT-DNA extents and comparative sequence/structure identify internal
> **msr / msd / a1 / a2** architecture across retron ncRNA families?

## 2 · ⛔ The evidence hierarchy, and it is the whole design

Every candidate coordinate carries the **tier of the evidence that produced it**. A single
unqualified annotation would be the failure mode this task exists to avoid.

| tier | source | what it is | what it is **not** |
|---|---|---|---|
| **A** | `PANEL-RTDNA-81` mapped by `T-R1b` | **experimentally measured RT-DNA extent** on its own ncRNA | not a general boundary |
| **B** | published experimentally characterised retrons | **external experimental anchors** | ⚠️ each needs its source **traced**, the `T-A23c` lesson |
| **C** | Buffington 105 putative native msr-msd | **external predicted architecture** | ⛔ **not experimental truth** — bioinformatic identification |
| **D** | `NCRNA-16458` | CM-derived expansion population | ⛔ **never independent validation of the covariance models that defined it** |

⛔ **The cycle that must not close:** `CM-CALLS` defines `NCRNA-16458`; scoring a CM-derived
prediction against CM-derived calls adjudicates nothing. Tier D is a **population to annotate**,
never a **truth set**.

## 3 · ⚠️ The engineered delta is not an msd boundary

Buffington supplies **both** a `Putative native msr-msd` **and** an `msr-msd with a 81nt RFP repair
template`. The difference between them is, initially and only, an **`ENGINEERED_DELTA`**.

⛔ **It must NOT be promoted to "the msd boundary" without first verifying how the constructs were
designed.** A repair template is inserted where the *engineers* chose to put it, which may or may
not coincide with a natural boundary. That verification is a **prerequisite**, not an output.

This is the same error class as `T-A23c`'s region-Y rows: an engineered construct read as a native
property.

## 4 · Methods, with roles kept separate

| method | role | ⛔ not |
|---|---|---|
| exact / local alignment | Tier-A RT-DNA → ncRNA mapping (`T-R1b`) | a boundary model |
| native-vs-modified pairwise comparison | locate the **`ENGINEERED_DELTA`** | an msd call |
| MAFFT / MAFFT Q-INS-i | family- and subtype-specific ncRNA alignment | cross-family alignment without declaring it |
| CMfinder / Infernal | structure-aware propagation to homologues | ⛔ evaluation against CM-derived calls |
| RNAfold | secondary structure | ⛔ a structure prediction is not a measurement |
| covariation / R-scape | statistical support for a proposed pairing | ⛔ significance without its assumptions stated |
| priming-G, inverted repeats, published architecture | **candidate internal landmarks** | automatic landmarks |

**Availability, checked:** MAFFT ✅ (`dep_maps`), `cmsearch` ✅ (`retrons`), RNAfold ✅
(`~/.local/bin`). **CMfinder and R-scape are NOT verified present** — that must be resolved before
this task is drafted, not discovered mid-run.

## 5 · Output shape

Per ncRNA, per proposed element (`msr`, `msd`, `a1`, `a2`): **start, end, evidence tier (A–D),
confidence, and the specific source**. Plus an explicit **`UNRESOLVED`** state.

⛔ **No single unqualified annotation.** A coordinate without its tier is not a result.

## 6 · Prerequisites before this can be drafted

1. `T-R1b` lands — Tier A does not exist without it.
2. `T-X1` lands — establishes what the Buffington catalogue actually overlaps.
3. **Construct-design verification** for the engineered delta (§3).
4. **Tier-B sources traced**, with the `T-A23d` identity discipline — a title match is not an
   identification.
5. CMfinder / R-scape availability resolved.
6. A declared rule for **what makes a Tier-C or Tier-D coordinate reportable at all**, fixed in
   advance.

## 7 · Interpretation ceiling

⛔ Candidate coordinates with explicit tiers. **Not** a validated annotation of retron ncRNA
architecture, **not** a replacement for experimental determination, and **not** evidence about the
covariance models that defined the population it annotates.
