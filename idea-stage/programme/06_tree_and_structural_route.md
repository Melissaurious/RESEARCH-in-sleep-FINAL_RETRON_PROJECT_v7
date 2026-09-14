# Stage 6 · The tree negative, and the one untested structural route

*(operator's title: "Construct a tree (select part of RT to add, sequence or structural
trees?)")*

## 0 · The point of this task

Five sequence-based tree routes have already failed against criteria declared before they
ran, and the reference lab published the same failure — so the negative is real, expected,
and finished. What remains genuinely unknown is whether **structure** carries phylogenetic
signal that sequence does not: we hold an all-vs-all structural distance matrix for 1,919
proteins that has only ever been used as a distance matrix, never as a tree. Once this
lands we know whether a structural phylogeny resolves what sequence cannot, and the
published literature is split enough that either answer is reportable. **This stage is not
five more sequence routes** — those are foreclosed.

## 1 · Where this stands — 🔴 a confirmed negative

| | finding |
|---|---|
| `C1` | **Five inference routes, five failures** against pre-declared criteria. `G87` was the best-powered attempt |
| `s8_tree_declared` | The **third pre-registered conjunct**, declared by `s6_trees` and skipped, was computed: **17.2–28.4% holds**, the negative is **CONFIRMED**, and the tree-free classification basis gets **STRONGER** |
| `C2` | The failure is **partly self-inflicted** by cd-hit-50 — 19.1 → **28.5%** with redundancy restored. Must be reported *with* `C1`, never instead of it |
| `C3` | ⭐ **pLDDT filtering helps pairwise-similarity methods, not alignment-column methods** — three replications. A genuine mechanistic result |
| `C4` | **Toro 2018 reported the same failure in print** — our negative is *expected*, not anomalous |
| `C5` | ⚠️ **Limit:** we do **not** show published pan-RT phylogenies are wrong. Our sampling is not theirs, and we measured support in **no** published tree |
| `E3` | **Dereplication ENRICHES truncated tips**: 30.8% full-window before cd-hit-50, **24.1%** after. Compounds `C2` |

⚠️ `s6_trees` also found that **`RESOLVED` was declared as a three-way conjunction and only
two conjuncts were ever computed**, so every resolution figure in the earlier drafts was
an **upper bound** on the quantity the pre-registration defined. `s8_tree_declared` closed
that.

## 2 · ⛔ The untested route — "sequence or structural?"

**The structural tree has never been built as a tree.**

- `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/foldseek/tm.npy` + `tm.ids` — the all-vs-all TM matrix over **1,919 proteins**,
  computed for `G89` and used only as a distance matrix.
- **FoldMason is installed**: `miniconda3/pkgs/foldmason-4.dd3c235` (an earlier "absent"
  claim was scoped to two conda envs and measured wrong).
- **Ibex holds 5,256 span-sliced structures** at `struct/span_pdb/` — the object the trees
  were actually built on — plus `struct90/` and `struct/db/` (48 foldseek DB files).
- **Parked sensitivity axis:** PMSF / site-heterogeneous models (`C10`–`C60`) — are the
  deep splits an artefact of a site-homogeneous model?

**⚠️ The literature is split, and we hold claims on both sides:**

| claim | direction |
|---|---|
| `huang2023-structure-clustering-recovers-clades-sequence-misses` | for structure |
| `mutti2025-structure-does-not-outperform-sequence-for-phylogenomics` | against |
| `foldmason-limited-to-small-single-domain-groups` | scope limit |
| `ufboot2-overestimates-support-under-model-violation` | support values are inflated |

## 3 · ⛔ On "select part of RT to add" — this is the load-bearing decision

- `D3`: the tree tips were a **341-aa tetrad window, NOT the derived domain** — Jaccard
  **0.736** against `B_coreflank`'s 0.912. **Never say "domain-based phylogeny."**
- `X04`: the window cut (anchor −220 … +120) is recorded as **THE LOAD-BEARING
  PARAMETER**, basis `[CHOICE]`, *"and not even ours"*.
- So the honest options are: the **full-length protein** (a tree of architectures), the
  **declared RT0–RT7 domain** from stage 2 (which has never been used as tips), or the
  **341-aa window** (what was actually used). These are three different objects — see
  stage B.

## 4 · Prerequisites and gates

- **Stage 2**, if the tips are to be the declared domain rather than a window.
- **Stage C**, a positive control: a tree route that fails on an instrument that could not
  have succeeded proves nothing. The earlier tree audit produced 5 refutations in 45 rows
  *because its instruments could not have returned another answer*.
- ⛔ **Route 1 is already occupancy-trimmed** — `occ50` keeps 287 of ~2,100 columns, so any
  "never block-trimmed" premise is half wrong; `-strict` leaves only 68–115.

## 5 · Foreclosed here

⛔ **Five more sequence routes.** ⛔ **Pagel's λ** as pre-registered — binary-only, needs a
resolved tree we do not have (`E9`). ⛔ **The δ statistic** — named in our record, not
executable; recorded so nobody proposes it a third time.

---

# 6 · Refinements from `RETRON_RT_PROJECT_IDEAS.md` §8

## ⭐ The ideas document states the question better than the record does

> **"Which part of the RT sequence or structure provides the most stable and biologically
> meaningful phylogeny?"**

That is the live question, and it reframes the stage correctly: not *build a tree*, but
**compare representations**. The five failures were five *methods* on essentially one
representation family — they did not answer this.

## Representations to compare

| representation | status here |
|---|---|
| full-length RT | ⚠️ risks a tree of **architectures**, not RTs — `D5`'s fusion bias (2.04× → 1.22×, residual remains) is exactly this |
| full conserved RT core | ⛔ never used as tips — this is stage 2's output and the obvious candidate |
| **palm only** | ⛔ never tried; needs stage 4 |
| **fingers + palm** | ⛔ never tried |
| selected RT0–RT7 blocks | ⛔ never tried; `s4_motifs` says which blocks are informative |
| trimmed alignment | ⛔ **Route 1 is already occupancy-trimmed** — `occ50` keeps 287 of ~2,100 columns; `-strict` leaves 68–115 |
| family-specific core | ⛔ never tried |
| **341-aa tetrad window** | ⚠️ **this is what was actually used** (`D3`, `X04`) — and it is one row in this table, not the default |

⭐ **Five of the eight rows have never been attempted.** That is the honest state of "which
part of the RT" — and it means the closed negative is narrower than it looks: *five methods
on one representation failed*, not *every representation failed*.

## Scope options, and the one the record supports

**One broad bacterial RT tree · retron-only tree · broad tree + retron subtree ·
family-specific trees.** ⚠️ `C5` is the constraint: *we do not show published pan-RT
phylogenies are wrong — our sampling is not theirs, and we measured support in no
published tree.* A broad tree therefore cannot be framed as a correction of the literature.

## Model robustness — folds into stage H

Alignment method · trimming · substitution model · redundancy level · taxonomic balancing.
These are **stage H's perturbations applied to the tree**, and `C2` already proves the
redundancy knob moves the headline (**19.1 → 28.5%**). Run them as a stability test, not as
a search for the route that succeeds — the latter is how a result gets manufactured.

## One ideas question the record already answers

> *Do sequence-based and structure-based trees agree?*

⛔ **Unanswerable today** — the structural tree has never been built. But `C3` gives the
mechanism to expect: **pLDDT filtering helps pairwise-similarity methods and not
alignment-column methods**, replicated three times. So a foldseek-distance tree and a
structural-MSA tree are **not** the same experiment, and should be reported separately.
