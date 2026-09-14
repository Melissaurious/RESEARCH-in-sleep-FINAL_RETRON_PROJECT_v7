# Stage B · The object register
**Proposed addition. `PE14` in the existing record. Publishable with no computation.**

## 0 · The point of this task

Every study in this field aligns something slightly different — a full-length protein, a
catalytic window, a derived domain — and which one is almost never stated. Our own drafts
mixed two objects inside a single subsection, with the table computed on the full-length
protein and every fold in the prose computed on a 341-aa span; that error class is the most
frequent one in this project. Nobody has written down **what the field has actually
aligned, study by study, and whether the object changed over time.** Once this lands we
have a publishable methods result that costs no computation at all, and every later stage
can declare its object against a reference instead of inventing one.

## 1 · Where this stands

⛔ **`PE14` — proposed 2026-08-25, never run.** Rated ⭐⭐⭐ in
`PROPOSED_EXPERIMENTS.md` and described there as *"a publishable result with no
computation."*

Local groundwork exists: `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/OBJECT_REGISTER.md` already names
objects **`O1`–`O7`**, and every claim in `CLAIM_REGISTER.md` carries an object column.
`DEPENDENCY_CHAIN.md` traces the intended chain against what actually happened. What does
not exist is the **outward-facing** version: the same treatment applied to the published
literature.

## 2 · The evidence that this matters

| | |
|---|---|
| `crosscheck` | 🔴 **§4.10 is the exception**: its table is the full-length protein and every fold in its prose is the 341-aa span — §3's `O2` and `O3` mixed inside one subsection, **and inherited by §7.9** while §2 quotes the other object for the same element |
| `D3` | The tree tips were a **341-aa tetrad window, not the derived domain** (Jaccard 0.736). **Never say "domain-based phylogeny"** |
| `X04` | The window cut is **the load-bearing parameter**, basis `[CHOICE]`, *"and not even ours"* |
| structures | borg holds **5,109 full-length** folds; Ibex holds **5,256 span-sliced** ones. Two objects, two machines, no map between them until 2026-09-09 |
| `A10` | *"`[YFWH].DD` is the criterion the field uses"* — **killed.** Published tools admit by HMM bit score. The field's *object of admission* is not ours |

## 3 · What must be delivered

- **One row per published study:** what was aligned (full protein / domain / window /
  structure), how the boundary was set, whether the paper states it, and what the object
  was called.
- **A change-over-time axis** — has the object drifted between Toro 2014, Zimmerly 2001,
  Mestre 2020, Toro 2026?
- **Our own objects `O1`–`O7` placed in the same table**, so a reader can see which
  published object each of our claims is comparable to.
- **A rule for later stages:** every claim names its object, and cross-object comparisons
  are either forbidden or explicitly bridged.

## 4 · Why it belongs near the front

Every stage inherits an object choice. Stage 2 (which span defines the domain), stage 6
(what the tips are), stage 8 (fusion is only definable relative to a span), stage 4
(full-length vs span-sliced structures) — all of them silently depend on this. Writing it
first is cheaper than reconciling it afterwards, which is what `crosscheck` had to do.

## 5 · Prerequisites

None. It requires reading, not computing — which is exactly why it has survived unrun for
so long, and why it is the best value on the list.

## 6 · Related, and worth folding in

`PE15` — where do `W` and `H` in `[YFWH].DD` come from? A character class is an object
choice too. `D10` — the trap of citing Simon & Zimmerly 2008 for `[LIV]` when their claim
is about **position 2** and our excluded class differs at **position 1**.
