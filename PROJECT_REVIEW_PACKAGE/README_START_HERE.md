# START HERE — retron RT/ncRNA project, scientific state as of 2026-09-19

You are reading a **self-contained onboarding package**. It carries the scientific state and its
provenance; it does **not** carry the heavy data, which is registered by absolute path, size and
hash in `DATASET_REGISTRY.tsv`.

**Nothing in this package is claim authority.** The project's claim authority is
`idea-stage/docs/research_contract.md`. This package is an independent synthesis with exact
pointers, written so a fresh reviewer, agent or planner can work without the conversation history.

---

## 1 · The scientific problem

> A large genome- and metagenome-derived catalogue of reverse transcriptase (RT) systems exists as
> heterogeneous mining records. **How is it converted into defensible biological objects, and what
> can those objects then say** about retron diversity, RT architecture and classification, genomic
> organisation, ncRNA association, annotation limits, and RT–ncRNA co-evolution?

Retrons are the primary target; other bacterial/archaeal RT families are comparators. A retron is
(in the molecular sense) an RT that, with its own cognate non-coding RNA (msr-msd), produces a short
RNA-linked DNA — **msDNA**. See `WHAT_IS_A_RETRON.md`, which separates three different answers.

## 2 · Canonical denominators — memorise these

| quantity | value | never confuse with |
|---|---|---|
| raw RT-anchored records | **3,059,700** | the corpus's 3,358,182 lines (298,482 are ncRNA-anchored and are held **outside** every RT denominator) |
| genomic loci / physical loci | 2,847,312 / **2,475,684** | each other (`NZ_` prefix normalisation) |
| **exact RT sequences** | **501,561** | the Stage-2 denominator |
| **Stage-2 eligible denominator** | **369,381** (0.7365 of 501,561) | ⛔ **501,561 is not the denominator for any mapper-derived rate** |
| inspectable (MAPPED) | 354,102 (0.9586 of eligible) | "found" — 15,279 are frozen abstentions, and abstention ≠ absence |
| exact ncRNA sequences | 16,458 | — |
| **exact RT–ncRNA pairs (PAIR-ELIG)** | **30,924** pairs in **1,075** components | the inference unit is the **component**, not the pair (n_eff ≈ 12.5) |
| Retron-labelled loci | 630,741 (Z6) / 632,688 (g3) | — |
| Retron-family exact RTs | 78,287 | — |
| experimental structure register | **62 chains / 31 biological groups** | a census — it is a *selected* panel |
| experimental retron panel | **175 elements** | an independent benchmark — **it is not** (§7) |

## 3 · Status of every major task

| arm | status | one-line conclusion |
|---|---|---|
| Stage 1 · database characterisation | **CLOSED, reproducible** | the units and their non-interconvertibility are established; the **6.6-fold tool-dependent ncRNA carriage asymmetry** is the key methodological result |
| Stage 2 · RT0–RT7 + conserved-state mapper | **CLOSED** with 6 residual limitations | a frozen instrument, validated on **one** fresh lineage under **one** convention, applied to 369,381 RTs; **RT0 and RT1 UNRESOLVED** |
| Stage 3A · structural decomposition | **CLOSED at FAIL** | the three-way fingers/palm/thumb partition is **not recovered** (palm-like 0.565 vs a 0.70 bar) |
| Stage 3B · catalytic geometry | **STOPPED on kill criterion K5** (mislabelled "CLOSED at PARTIAL") | in-sample calibration only (13/19); **Tier B never opened** and its PASS branch was unreachable |
| Stage 3C · architecture integration | **COMPLETE but NOT PROMOTABLE** | independent review **FAIL_BLOCK 4.5/10, 5 blockers upheld**; four claim rows withdrawn |
| Mestre · historical classification | **FAILED / closed** | re-inference failed; placement into the 11-clade system failed its control gate (shuffled placed at 7.9 %) |
| SPIRE · de novo ncRNA discovery | **CLOSED at held-out failure** | a fixed positional interval beats the method (901 vs 343); **two positional features are inherited** |
| Embeddings · retrieval | **CLOSED, escalation refused** | signal is real but **type-level**; the type-matched rung fails |
| X1 / X2 · conditional modelling | **X2 CLOSED**; chapter reporting package **FINAL** (`d7d3ece`) | lineage dominates (~78 % of the gain); a small, seed-unstable exact-RT residual survives; pair-level discrimination does not |
| Experimental panel | **REGISTERED with an exposure map** | only **16 of 175** elements are fully external |
| ncRNA boundary prediction | **NOT_YET_TESTED**; comparative recovery FAILED | the assumed 977-element truth set **does not exist** |
| Phylogeny / co-evolution | **NOT_YET_TESTED** | no phylogeny exists anywhere in this project |
| Accessory / fusion architecture | **NOT_YET_TESTED** | all 41,250,531 accessory CDS lack sequences |

## 4 · Key conclusions a reviewer should carry

1. **Type- and lineage-level structure is recovered easily; pair- and partition-level structure is
   not.** Four instrument families were each pushed to a predeclared criterion and each stopped at
   the same place.
2. **The single strongest positive result** is `embed_x2`, and it must be read at **four levels**,
   never as PASS/FAIL — ⛔ **and `X2-A` is a gate label, not a biological conclusion**. The
   conclusion of record is the qualified paragraph in `X2_CLOSURE.md` §2: *specific RT sequence
   information improves prediction of the cognate ncRNA beyond broad type and beyond a coarse
   50 %-identity homolog representation, but **most of the gain is explained at the homolog-lineage
   level**, and the additional specific-RT effect is small, weak at pair level under close
   counterfactuals, and uncertain in magnitude across seeds.* The four levels: broad RT lineage
   predicts the ncRNA (G − U −0.04256; G − T is **~78 %** of R − T); the exact RT adds a small
   residual (R − G −0.00551, sign replicated across 3 seeds, **magnitude undetermined**);
   close-counterfactual pair discrimination is **not demonstrated** (at C3, 52.5 % of pairs, and the
   raw pair-weighted mean is **−0.000205**, nominally negative); biochemical compatibility is
   **untested**, and there is no local data with which to test it.
3. **The frozen mapper is a real instrument** with a stated scope, and it is the project's most
   reusable asset — but its frame is group-II-intron-centred (median MAPPED 0.94 GII → 0.49 Retron),
   which confounds every between-family architectural comparison.
4. **Retron populations at genome scale are annotation-defined.** This is a statement about
   evidence independence, **not** a claim that annotation lineage is biology.
5. **Two closures need repair before citation**: Stage 3B's "PARTIAL" label, and Stage 3C's
   withdrawn rows. See `RESULT_BUNDLE_REGISTRY.tsv` and `OPEN_QUESTIONS.md`.

## 5 · Major negative results (full list in `NEGATIVE_RESULTS.md`)

- Three-way domain decomposition **FAILS** (0.565 < 0.70; 22/22 leave-one-group-out folds fail) —
  and the **literature does not agree with itself either** (literature fingers coincide with a unit
  **0/8** after erratum; two 2026 papers on the same protein publish incompatible partitions).
- De novo ncRNA discovery **FAILS** on held-out data; a fixed positional interval wins.
- Placement into the historical 11-clade system **FAILS** its shuffled-query control (7.9 % vs ≤ 1 %).
- Stage 3B **fires its own kill criterion** (decoy pool 23 vs ≥ 60).
- Retrieval **fails** the type-matched rung (+0.0298 [−0.0048, +0.0633]).
- The "**977 validated retron ncRNAs**" set **does not exist on this machine**.
- Region Y is **neither universal nor exclusive** (absent in all 6 Eco8 chains; present in 4
  non-retron chains).

## 6 · Major warnings and circularities (full treatment in `CIRCULARITY_AND_LEAKAGE.md`)

1. **One annotation lineage underlies the whole retron axis**: 21 Mestre-authored covariance models
   → PADLOC rules (the ncRNA is a scoring element in 17 of 18) → DefenseFinder profiles iterated to
   recover the same known set → MyRT family labels → g6's grouping → the embeddings' "retron type"
   variable. **Tool agreement is not corroboration.**
2. **"Retron type" is the ncRNA's own covariance model.** Any control matched on type is matched on
   a label from the other modality.
3. **Stage 3B calibrated its own thresholds on the same 19 truth pairs it then scored.**
4. **After X2 there is no untouched holdout inside PAIR-ELIG** — it cross-fits all five folds.
5. **The experimental panel is inside the prediction set**: 175/175 rows carry a Mestre accession;
   145/175 RTs are in the exact-RT catalogue.
6. **Stage 3C's headline numbers came partly from undeclared rules** (blockers B1, B4).

## 7 · What has experimental evidence

`EXPERIMENTAL_EVIDENCE_REGISTER.tsv`, 185 rows. Real measurements exist: **81** empirically
determined RT-DNA sequences; RT-DNA production measured for 103 elements with **67 > 0**; human
editing > 0 for **100**, bacterial **27**, phage **16**; **31** elements synthesised and tested with
outcome undetermined (a genuine negative population); and 8 deposited retron RT–RNA–DNA complexes.

Three things this evidence is **not**:
- **not independent** of the project's populations (58 train-exposed, 33 val/test-exposed, 56
  catalogue-only, 12 near-sequence, **16 fully external**);
- **not exchangeability data** — there is **no** swap, cross-reactivity or orthogonality experiment
  in any local asset, which is why biochemical compatibility stays `NOT_YET_TESTED`;
- **not a compatibility validation set**, not even the 16 external elements. They carry *functional*
  measurements. A prospective **functional** validation (RT-DNA production / editing) is a
  legitimate future use at a **different endpoint**.

## 8 · Minimum remaining work

Fully argued in `MINIMUM_REMAINING_WORK.md`. In short: **8 zero-compute repairs first** (4 change
what may be written), then **declare a confirmatory population**, then three or four bounded compute
items. Not approved: a compatibility model, cross-pair scoring, lab candidate prioritisation.

## 9 · Recommended reading order

| # | file | why |
|---|---|---|
| 1 | this file | state and denominators |
| 2 | `CURRENT_SCIENTIFIC_STATE.md` | one section per arm, with limitations and downstream relevance |
| 3 | `CIRCULARITY_AND_LEAKAGE.md` | read **before** believing any rate |
| 4 | `CLAIM_EVIDENCE_MATRIX.tsv` | 37 claims with safe wording and prohibited overclaim |
| 5 | `NEGATIVE_RESULTS.md` | what was refuted, what was merely underpowered |
| 6 | `OPEN_QUESTIONS.md` | four kinds of "unresolved", kept apart |
| 7 | `EXPERIMENTAL_EVIDENCE_REGISTER.tsv` | the only experimental layer, with exposure per element |
| 8 | `DATASET_REGISTRY.tsv`, `RESULT_BUNDLE_REGISTRY.tsv`, `WORKTREE_REGISTRY.tsv`, `METHODS_REGISTRY.tsv` | where everything lives and what state it is in |
| 9 | `WHAT_IS_A_RETRON.md` | the definitional question, evidence-graded |
| 10 | `PUBLICATION_OPTIONS.md`, `THESIS_ARCHITECTURE.md`, `MINIMUM_REMAINING_WORK.md` | planning |

## 10 · Canonical evidence — paths, commits and GitHub branches

Repository: `github.com/Melissaurious/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7`. Local root:
`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7` (worktrees are siblings with suffixes).
`general/` is a **git submodule** — clone with `--recurse-submodules` or the governance layer is
empty.

### 10.1 · Repository architecture — three tiers, deliberately not merged

| tier | branch | what it is |
|---|---|---|
| **index / review** | **`project-synthesis`** | this package plus the long-form synthesis. A lightweight, citable index over everything else. It **does not** contain the evidence and the task branches are **not merged into it** |
| **evidence / reports** | the eight task branches below | the actual bundles, reviews, errata and reporting packages, each on its own branch |
| **promoted state** | **`main`** | the formally promoted, governed project state — currently `94a1a78` |

Consequence for a reviewer: `main` is **not** the whole project. Several closed results (the Stage-2
final report, Stage 3C and its failed review, X2 and its closure, the Mestre closure) live only on
their own branches and are **not** on `main`.

### 10.2 · Evidence sources — local path ↔ GitHub branch

| what | local worktree path | GitHub branch | commit |
|---|---|---|---|
| Stage 1 + Stage 2 bundles; Stage-2 **final report** | `…_v7/results/` | **`rt07-stage2-final-report`** | `46414f4` (one ahead of `main`) |
| Stage-2 binding errata (`g7a_closure_decision_erratum_2026-09-19.tsv`) | `…_v7/docs/errata/` | `main` · `rt07-stage2-final-report` | `94a1a78` |
| g6 reading rules (`2026-09-19_stage2_g6_review_errata.md`) | `…_v7/docs/decisions/` | `main` · `rt07-stage2-final-report` | `94a1a78` |
| Stage 3A / 3B / 3C + **failed independent review** | `…_v7-stage3c/analysis/` | **`worktree-stage3c`** | bundle `34000ee`; review + errata `eeaf0ae` |
| Stage-3C errata (**binding — the report may not be cited without it**) | `…_v7-stage3c/docs/errata/2026-09-19_stage3c_review_errata.md` | **`worktree-stage3c`** | `eeaf0ae` |
| Stage 3A closure / Stage 3B design, as first landed | `…_v7-asset-audit/analysis/` | **`prior-asset-audit`** | `67c137b` |
| embeddings, X1, **X2 + closure** | `…_v7-embeddings/results/` | **`embeddings-g0`** | X2 results `4f8550b`; **closure `fdf0872` governs** |
| X2 canonical exports | `…_v7-embeddings/results/embed_x2_rt_specificity_confirmation/tables/` | **`embeddings-g0`** | `X2_COMPONENT_LEVEL_EXPORT.tsv` = **inference file** (1,075 rows); `X2_PAIR_LEVEL_EFFECTS.tsv.gz` = **join only** (30,924 rows) |
| RT-ncRNA chapter reporting package | `…_v7-embedding-report/analysis/embedding_report/` | **`worktree-embedding-report`** | **`d7d3ece`** — figures F8–F10, 29 claims, six-point OpenCRISPR subsection |
| Mestre audit + closure | `…_v7-mestre-audit/analysis/mestre_audit/` | **`worktree-mestre-audit`** | `b05934f`; closure `033bfcb`; MCC-v3.1 freeze `e047fdc` |
| SPIRE de novo ncRNA | `…_v7-spire-ncrna/analysis/spire_ncrna_audit/` | **`worktree-spire-ncrna`** | `ed4a663` |
| Stage-1 workbench (exploratory) | `…_v7-dbchar-workbench/analysis/` | **`dbchar-workbench`** | `12ea561` |
| full synthesis (long form) | `…_v7-synthesis/analysis/project_synthesis/` | **`project-synthesis`** | `48f9e1b` |
| **this package** | `…_v7-synthesis/PROJECT_REVIEW_PACKAGE/` | **`project-synthesis`** | current tip |

Per-branch publication state, including which tips are published, is in `WORKTREE_REGISTRY.tsv`
(`github_branch`, `published_state`); per-bundle branch attribution is in
`RESULT_BUNDLE_REGISTRY.tsv` (`github_branch`).

### 10.3 · What is still NOT on GitHub

- **Heavy data**: the corpus (~76 GB), `data/derived/` (2.2 GB), `MELISSA_DATA/` (1.8 GB), the
  embedding caches (~28 GB) and the X1/X2 model scratch (~3.6 GB) are gitignored. They are
  registered by absolute path, size and hash in `DATASET_REGISTRY.tsv`.
- **The Stage-1 writing workbench**: `…-dbchar-workbench/ARIS_OUTPUT/dbchar_workbench/` (88 MB) is
  gitignored and therefore in **no** branch, published or not — a genuine single point of failure.
  Only a text snapshot is tracked, at `docs/dbchar_workbench_snapshot/`.
- **The experimental panel and structures**, which live outside this repository entirely (paths and
  sha256 in `DATASET_REGISTRY.tsv`).

⚠️ **`human_input_audit` is PENDING on every bundle**, which governance requires before any number
becomes a thesis or paper claim. Publication to GitHub does not change that.
