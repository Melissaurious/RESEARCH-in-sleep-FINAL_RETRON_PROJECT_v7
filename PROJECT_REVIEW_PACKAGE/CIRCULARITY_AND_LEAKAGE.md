# CIRCULARITY AND LEAKAGE

Read this before believing any rate in this project. Every item is a **dependency between things
that look independent**. None of them is fraud or error; all of them change what a number means.

---

## 1 · The master dependency: one annotation lineage

```
        Toro 9,141-tip RT tree
                 │
     Mestre 2020 (1,912 tips + 16 characterised retrons)
                 │
   CMfinder de novo motifs on clade-grouped upstream windows
                 │
     21 covariance models  ── all authored by Mestre MR ──►  padlocdb.cm
                 │                                              │
                 │                                              ▼
                 │                               PADLOC retron rules (17 of 18 score ON the ncRNA)
                 │                                              │
                 ├──► DefenseFinder profiles (iterated to recover the same known set)
                 ├──► MyRT family labels  ──► g6's family grouping (369,370 of 369,381)
                 └──► every ncRNA call in the corpus ──► PAIR-ELIG ──► "retron type" in the embeddings
```

**Consequences, stated plainly:**

- **Tool agreement is not corroboration.** DefenseFinder and PADLOC share model lineage; where both
  wrote a subtype they agree on only **43.85 %** of records, and that disagreement is data, not error.
- **"Retron type" is the ncRNA's own covariance model** (`detection_model` is a field of the ncRNA
  record). So in the embedding work, arm T and retrieval rung 3 condition on a label from the *other*
  modality. RiNALMo's type-probe accuracy (0.6557) is therefore near-tautological; only the ESM-C
  side (0.4978, protein → ncRNA-derived label) is informative.
- **Carriage rates are partly definitional.** ncRNA carriage swings **6.6-fold** with the tool
  combination (89.23 % myRT+PADLOC → 13.50 % myRT alone), and by subtype from 90.1 % to 0 % — the
  subtypes at 0 % are those with **no dedicated covariance model** (types VI, VII, VIII, X, XI, XII).
- **This is a statement about evidence independence, not about biology.** Annotation lineage is how
  the population was *defined*; it is not a determinant of what a retron *is*.

## 2 · Circular positive controls (two, both identified, neither repaired)

| claimed control | why it is circular |
|---|---|
| "a positive control exists for the instrument … 98.6 %" (Ec107-like ncRNA carriage) | PADLOC's `retron_Ec107-like` rule requires an ncRNA in practice, so near-total carriage is guaranteed by the rule that defines the stratum |
| SPIRE's per-type positional prior (92.2 % IoU ≥ 0.5) | scored against the **CM's own cut** — the boundary it was derived from |

A third, weaker case: a "≥ 2 of three lines" stratum counts the ncRNA line alongside PADLOC, which is
the same evidence twice.

## 3 · In-sample calibration (Stage 3B)

`SEP_MIN` 75, `SEP_MAX` 115 and `D_MAX` 6.0 Å were each **derived from the 19 Tier-A truth pairs and
then scored on those same pairs**. By construction every truth pair is admissible, which is most of
what "19/19 site-level overlap" and "0 truth-bearing abstentions" mean. Each window edge is set by a
single chain (`1RTD_A`, `9YFD_A`, `8SXT_A` — the last is itself a MISS). Out-of-sample LOCO gives
**12 HIT / 5 MISS / 2 ABSTAIN**.

## 4 · Constructed agreement (Stage 3C)

`CAT_STATE 262` was **constructed as the modal HMM state of `[YF].DD` motif starts**. Its landing two
residues before a catalytic aspartate in 17/17 chains is therefore an **expected motif-identity
check, not independent catalytic validation** (erratum E-3C-4). The Stage-3C synthesis originally
called the instruments "mutually independent"; the corrected wording says they are **not**.

Related: Stage 3C's `19/19` detector co-location uses a detector **whose thresholds were calibrated
on those same truth pairs** — in-sample co-location, not detector validation (E-3C-3).

## 5 · Population selection

- **Stage 3B assembled the 62-chain register** by collecting catalytic evidence; Stage 3A then used
  it and declared itself blind to Stage 3B. The blinding is real at the level of *inputs* (an
  executable allowlist) but cannot undo a selection made upstream. Stage 3C's erratum E-3C-2 states
  it: *"a selected experimental-structure panel … not an unbiased census"*.
- **Comparison A is retron-free**: all 19 truth-bearing chains are non-retron, so nothing in it
  speaks to retron catalytic architecture.
- 50 of 62 chains are cryo-EM; all 31 biological groups fall in **one** structural cluster (93 % of
  465 group pairs at TM ≥ 0.50), so leave-one-group-out is influence analysis, not independence.

## 6 · Training / test overlap in the modelling track

| fact | number |
|---|---|
| ncRNAs appearing in more than one fold | **0 of 16,458** (the split is genuinely cluster-disjoint) |
| held-out RTs with a ≥ 0.50-identity training relative | **82.46 %** |
| held-out ncRNAs with a ≥ 0.70-identity training relative | 40.71 % |
| held-out pairs reachable from training via either modality | **100 %** |
| median nearest-training-RT cosine | **0.987** (even Q1 > 0.983) |

**Cluster-disjoint is not homology-disjoint.** And after `embed_x2`, which cross-fits **all five
folds**, **no untouched holdout remains inside PAIR-ELIG**. The test fold was also opened more than
once across gates (g2, then X1, then X2) with no multiplicity accounting.

## 7 · Experimental-panel leakage

Measured by exact sequence hash (`EXPERIMENTAL_EVIDENCE_REGISTER.tsv`):

| exposure | n |
|---|---|
| `TRAIN_EXPOSED` | 58 |
| `VAL_TEST_EXPOSED` | 33 |
| `CATALOGUE_ONLY` | 56 |
| `SEQUENCE_NEAR_CORPUS` | 12 |
| **`FULLY_EXTERNAL`** | **16** |

Plus: **175/175** panel rows carry a Mestre accession, and **145/175** RTs are in the exact-RT
catalogue. The panel is an **assay layer on the prediction set**, not an independent benchmark.

A useful by-product: only **12** panel ncRNAs match the corpus by exact hash while **80** match by
blastn ≥ 90 % / ≥ 80 % length. That gap *is* the published-extent-versus-CM-cut disagreement, and it
is the quantity a boundary project needs.

## 8 · Phylogeny, taxonomy and redundancy

- **No phylogeny exists in this project**, so no analysis is phylogeny-corrected. The contract's
  "phylogenetically matched" control rung was never built.
- The prior co-variation result is **void by construction**: `msr_msd` is nested inside clade, giving
  V = **1.0000**; and `msr_msd_family` was 44.4 % the literal string `nan` scored as a category.
- **Taxonomy is two schemas** keyed by `taxonomy_system` (GTDB 7-field; NCBI 3-field with no phylum).
  Counting them pooled is an error the project has already paid for.
- **Deposition redundancy is large and structured**: of recurring exact pairs, 9,362 recur only as
  copies of one physical locus across databases, 4,452 within one species, and **5,056 across
  species** — only the last is a biological question. The largest pair has 101,792 placements.
- **Pooling hides the distribution**: a pooled cross-group rate is the largest group's rate
  (`PQG[GA]` read 41.78 % pooled vs 0.373 % median-family — a 112× gap).

## 9 · Frame and instrument confounds

- The mapper's frame is **group-II-intron-centred**: median MAPPED fraction 0.94 (GII) → **0.49**
  (Retron); on the structure panel, retron median mapped fraction is **0.427** vs 0.813 non-LTR. Any
  between-family architectural comparison inherits this.
- The profile itself derives from **66 group II intron ORFs containing zero retrons**.
- Eligibility is non-uniform: 11.3 % eligible for `mixed_or_codon_evidence`, 37.2 % for `MULTI`,
  57.4 % for `all_partial`, against 73.6 % catalogue-wide.

## 10 · Inert or absent controls

| control | state |
|---|---|
| embed_g2 `B-pop` and `B-model` trivial baselines | **inert by construction** — indexed from training rows, so both return a constant 0 on every held-out candidate; "beat every trivial baseline" was in practice "beat B-kmer" |
| embed_g2 rung-0 positive control | **predeclared, never run** |
| Stage 3A biological positive control | **absent by design** (literature forbidden); HIV-1 `1RTD_A` is itself AMBIGUOUS |
| Stage 3B negative / homologous-chemistry controls (C2b, C3, C3b) | **never scored as outcomes** |
| Mestre non-retron panel | a "PASS" that is **1,080/1,083 extraction failures** |
| V4 re-inference positive control | **never run** (the same rule on the published tree gives 10/11) |

## 11 · The rule this project already learned the hard way

A zero produced by a broken instrument reads exactly like biology. The canonical case is in the
prior project's `VOID_DO_NOT_CITE.md`: `cmsearch --cut_ga` against a covariance-model database with
**no GA lines** returned nothing unconditionally, and "0 % of 1,925 genomes carry a retron ncRNA"
was published internally before the correct figure — **67.76 %** — was found. Hence the standing
rule: **a zero needs a positive control showing the same instrument returns non-zero on a known case.**
