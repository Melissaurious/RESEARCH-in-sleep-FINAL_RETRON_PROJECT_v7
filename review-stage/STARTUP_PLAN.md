# STARTUP PLAN

**Companion to `INDEPENDENT_SCIENTIFIC_REVIEW_2026-09-20.md`.** That document is the assessment.
This one is the operational sequence. Short by design. Nothing here authorises a scientific analysis.

**Governing principle, from §17.6 of the review:** the scarce resource is not compute and not reviewer
attention. It is **untouched evidence**. This project has already consumed its only pairing holdout
and cannot get it back. Every step below is ordered so that nothing irreversible happens before the
things that cost nothing.

---

## Phase 0 · Done during the review

| item | state | output |
|---|---|---|
| Independent adversarial review, 17 sections | complete | `review-stage/INDEPENDENT_SCIENTIFIC_REVIEW_2026-09-20.md` |
| **Check 1 of 4 · asset discovery sweep** | **built and run** | `review-stage/tools/asset_sweep.py`, `review-stage/ASSET_SWEEP.tsv` |

**What the sweep found, and why it matters.** Across eight project roots it inventories
**155.6 GB** of scientific assets in 20,765 collections: 44,608 structure files, 520 trees, 15,427
sequence profiles, 1,059,907 matrix/embedding files and 406 PDFs. The current project's registries
list **almost none of it**. The sweep already changed four conclusions in the review and has
surfaced a fifth open question, below.

Everything in Phase 0 is uncommitted. **Decision needed: commit `review-stage/` or leave it
untracked.**

---

## Phase 1 · Zero compute, zero risk, unblocks everything

Nothing here touches a frozen bundle, consumes a population, or runs an analysis.

**1.1 · Register the assets.** Convert `ASSET_SWEEP.tsv` into rows in `data/README.md` and
`docs/DATASET_REGISTRY.md`, with paths, counts, sizes and the manifest hash the sweep computes.
Record for each collection whether it is an **asset** (reusable) or a **conclusion** (must be
re-derived under this project's `[UNVERIFIED]` rule). *Blocker removed: the project can no longer
conclude something is absent without having looked.*

**1.2 · Back up the single point of failure.** The 88 MB Stage-1 writing workbench exists in **no
branch, published or not**. Do this today, independently of every other decision.

**1.3 · Build the remaining three checks** (§17.2). In priority order:

| check | what it does | expected to find, immediately |
|---|---|---|
| **numeric linter over prose** | every number in a `.md`/`.tex` resolves to a canonical table cell or is tagged narrative | at least 3 known live defects: a same-strand figure wrong by 0.7 points and hardcoded in a script; a distance matrix cited at the wrong dimension; a superseded silhouette still in print in two files |
| **consumption gate** | artifacts carry their producer's terminal state; refuse to consume anything not in PASS | prevents a failed result silently becoming a downstream input, which is currently possible |
| **reachability precondition** | show the declared PASS outcome is attainable from the actual input population before running | would have caught two structurally unreachable PASS branches |

**1.4 · Apply the corrections** (§13, §16.6). The same-strand figure, the subtype-agreement
restatement, the SPIRE reversal, the mapper-seed description, the matrix dimension, the superseded
silhouette, the Stage-3B erratum, and moving the binding errata onto the index branch.

**1.5 · Declare the confirmatory population** (A3). Freeze a component block now, by a rule written
before the split is inspected. Zero compute, and it blocks every pairing follow-up.

**1.6 · Resolve the governance blocker.** `human_input_audit: DONE` appears nowhere except the spec
defining it. Under the project's own `BUNDLE_SPEC.md` no number is promotable. Decide how it clears.

**1.7 · Literature curation of cross-pair data (A23).** Reading, not compute. The named first target
is a published 7 × 7 cognate versus non-cognate editing matrix with three biological replicates.
Determines whether step 12 exists at all.

---

## Phase 2 · The pilot

**Adopt the proposed architecture on exactly one stage, end to end**, including the thesis artifact
layer and a stage decision report. If the architecture is wrong in a way neither reviewer
anticipated, the cost is one stage rather than the repository.

**Candidate pilot: ncRNA internal architecture (A5).** Chosen because it is cheap, it has a genuine
positive control in the 8 deposited RT-RNA-DNA complexes, its scoring is independent of the
annotation lineage, and it produces a biological object rather than a rate.

⚠️ **This choice is provisional pending an audit in progress.** Five prior versions of an ncRNA
extractor/detector task exist in the prior project, together with a refutation register and roughly
40 GB of cached ncRNA embeddings. If msr/msd architecture was already attempted there, the pilot
either inherits a bounded negative or moves to a different stage. **Do not start Phase 2 until that
audit reports.**

**Fallback pilot if A5 is not open:** genomic architecture (A10). Also cheap, also unstarted, and its
inputs are already landed as 44.3 million CDS rows with coordinates, strand, GC and ribosome-binding
features.

---

## Phase 3 · Generalise

Only after the pilot produces a stage decision report and a compiling artifact set. Then build the
program and stage launchers for the remaining stages, with the two structural modifications from
§17.3: the relatedness backbone is the trunk and the tree is an optional branch, and the two
circular stage questions carry their anti-circularity fixes in the launcher itself.

---

## Standing decision points

These are the operator's, not the reviewer's, and none is urgent except the last.

1. Commit `review-stage/` or leave untracked.
2. Accept withdrawal of the convergence claim (§11 D1).
3. Pre-commit to the verdict of the two cheap checks that decide the pairing paper (§11 D2).
4. Fund the msr/msd and genomic-architecture work (§11 D3).
5. How `human_input_audit` clears, and whether the resource is released (§11 D4).
6. Close the structural arm as a chapter, or spend its repairs (§11 D5).
7. **Back up the Stage-1 workbench. Today.**
