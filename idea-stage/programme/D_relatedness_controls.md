# Stage D · Relatedness and phylogenetic-signal controls
**Proposed addition. `PE1` + `PE0` in the existing record.**

## 0 · The point of this task

Our strongest classification claim is that several label sets co-vary beyond chance — and
the null it was tested against is **mathematically incapable of moving**, with a standard
deviation of exactly zero on the one comparison that matters. So we do not currently know
whether the co-variation is real biology or just related proteins resembling each other,
and the pre-registered fix was never executable because it needs a resolved tree we do not
have. Once this lands we either have a co-variation result that survives a control with
real power, or we know the effect was shared ancestry — and either way we can report a
number instead of a contested one. This gates every co-variation claim in stages 5, 10 and
12.

## 1 · ⛔ Why the current evidence decides nothing

| | |
|---|---|
| `B1` | Four label sets co-vary, three cross-lineage; V **0.384–0.511** against permutation nulls of **0.079–0.119**, on 1,814 proteins. 🔴 **The single biggest live risk in the project** |
| `A44` | ⛔ The same class of association is **25.9× a global null** and **1.03× a relatedness-preserving one**. The audit **withdrew its own A16/A24/A25** on these grounds |
| `E7` | ⛔⛔ **The relatedness null is mathematically INVARIANT on `landmark × clade` — sd = 0.000000.** It has power in general (injected α = 0.2 → **z = 6.1**) but **none on the pair that matters**. **`A44`/`L05`/`L06` decide nothing.** Part II is **under-tested, not refuted** |
| `E9` | ⛔ **`METHOD_BASIS` decision 21's Pagel's λ was never executable** — binary-only, requires a resolved tree; our labels are multi-state and no tree resolved |
| `E6` | ⛔⛔ **`msr_msd` is nested inside `clade`** — V = 1.0000 by construction. The axis count is **TWO, not four** |
| `D0` | 🔴🔴 The concordance table must be **recomputed before it can be debated** — `msr_msd_family` is 44.4% the literal string `nan`, scored as a category |

**Why the null cannot move:** the c50 clusters are **nested inside** the clades, so the
relatedness control and the label under test are **confounded by construction**.

## 2 · The design already worked out (`PE1`)

1. Build relatedness blocks from the **fold-distance matrix** (`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/fs_mestre/ava.tsv`,
   1,919 proteins, already computed) — **structure, not sequence**, so the blocks are not
   the c50 clusters that caused the confound.
2. Choose the granularity **by a declared criterion, before scoring**: the coarsest cut at
   which **≥50% of proteins sit in label-heterogeneous blocks**. Report the cut and the
   curve.
3. Permute **within blocks**; report **sd** and **z**, per `PE0`.
4. Use a **PP-style** comparison rather than Mantel: observed V against a
   block-constrained permutation distribution, **not** a distance-matrix correlation.

🔴 **Re-specified after reading the literature index.** The first proposal — *"use the
foldseek TM matrix as a continuous relatedness covariate"* — **is a Mantel test**, and
Harmon & Glor 2010 report inflated type-I error for exactly that, naming Lapointe &
Garland's PP as the alternative. ⚠️ Guillot & Rousset 2013 argues the other side; the
index's rule is **cite both or neither**.

🔴 **GATE, declared before scoring.** Run the `PE0` power curve **first**. If the new null
does not detect an injected α = 0.2 association at **z > 3**, **the result is not reported
at all** — the instrument failed, and that failure is the finding.

**Declared prediction, registered before running:** **z between 2 and 6** — some excess
over descent, well below the injected ceiling.

**What a negative looks like:** `z ≈ 0` with `sd > 0` and a passing power curve ⇒ **the
concordance is shared ancestry.** Part II narrows to *"the landmark instrument recovers
the published partition"* — a **reproducibility** result, not an independence one. Still
publishable, much weaker.

**Cost:** hours. **No new compute** — both inputs are already on disk.

## 3 · The standing rule (`PE0`)

> No permutation result may be reported without: (1) the null's **sd** — `sd = 0` ⇒ no
> information; (2) **z**, not the ratio; (3) an **injected-association power curve** on the
> same data and blocks.

**Method note:** an invariant null diagnoses the **shuffle unit**, not the claim — permute
*between* lineages, not within, and **name the depth the control reaches.**

## 4 · Order of operations (`D0`)

    (1) drop or mark the missing values   ->   (2) re-cut the labels (NA..H)   ->   (3) the phylogenetic null

**Doing (3) first tests the wrong table.** And note `B2`: re-cutting with `NA..H` takes V
from **0.511 → 0.588** (`NA..H` alone **0.689**) — so one open item **strengthens** the
result while the other may make it nothing. Run both.

## 5 · What it gates

⛔ Every co-variation claim in **stage 5** (Mestre concordance), **stage 10** (RT–ncRNA
co-evolution), and **stage 12** (does disagreement correlate with anything?). Without this
stage none of those three can report a number in either direction.
