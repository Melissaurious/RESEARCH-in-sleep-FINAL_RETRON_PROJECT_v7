# embed_g2c_atlas — descriptive embedding atlas and within-type feasibility audit

**Characterization of a completed experiment, not a new gate.** Nothing is fitted to improve a
metric. The M-CCA projection is the one frozen in `embed_g2` (k=32, α=0.01, fit on training
components) reused unchanged. No InfoNCE, contrastive, or cross-attention model was trained.

## Terminology (used throughout, including figure legends)

**observed / natural pair** · **mismatched candidate** · **retrieval decoy** ·
**non-observed pairing** · **type-matched decoy**.

A mismatched candidate is **not** a "negative pair" and **not** an "incompatible pair".
Absence from the corpus is absence of observation, not evidence of incompatibility. Nothing
here has been experimentally shown to be incompatible.

## Terminal interpretation

> Frozen ESM-C and RiNALMo representations contain substantial shared structure associated with
> naturally occurring RT–ncRNA systems. This supports strong retrieval against random and
> length/GC-controlled candidate sets. However, the current experiment does not establish
> individual partner-specific compatibility beyond retron-type-associated structure: when
> candidate ncRNAs are restricted by retron type, the M-CCA improvement over the k-mer baseline
> is no longer statistically distinguishable.

This does **not** state that retron type has been proven to explain all observed signal. Rungs
4–6 are `UNDETERMINED`, and the rung-3 comparison is an absence of a distinguishable difference,
not a demonstration of equivalence.

## Figures

| file | content |
|---|---|
| `fig1_rt_atlas.png` | ESM-C RT UMAP — retron type · T1–T4 · RT length · major species |
| `fig2_ncrna_atlas.png` | RiNALMo ncRNA UMAP — associated retron type · T1–T4 · length · species |
| `fig3_shared_cca_atlas.png` | shared CCA space; marker = modality, colour = retron type; observed partners joined in a readable 150-pair panel |
| `fig4_similarity_retrieval.png` | similarity distributions · retrieval ladder with rungs 4–6 marked UNDETERMINED · neighbourhood composition |
| `fig5_cca_dimensions.png` | canonical correlations · η² of retron type per dimension · per-modality type encoding |

Every panel renders from `plotdata/` and `tables/` via `scripts/a06_figures.py` alone.

## 4 · Cross-modal similarity (descriptive)

| population | mean cosine | Cohen's *d* vs observed |
|---|---|---|
| observed pair | **+0.3771** | — |
| type-matched decoy | +0.3217 | **0.248** |
| length+GC-matched decoy | +0.2803 | 0.420 |
| random decoy | +0.0872 | **1.364** |

The separation collapses as decoys are matched more closely on retron type.

## 5 · Neighbourhood analysis — the clearest statement of the two levels

Open pool of **2,756** candidate ncRNAs (test fold), shared CCA space:

| quantity | value |
|---|---|
| observed partner is the nearest cross-modal neighbour | **0.56 %** |
| observed partner in top-5 / top-10 / top-20 | 2.6 % / 4.5 % / 7.9 % |
| median rank of the observed partner | **238** of 2,756 |
| nearest neighbour shares the query's retron type | **51.9 %** |
| top-5 / top-10 share retron type | 51.2 % / 50.0 % |
| retron-type prevalence in the pool | 9.4 % |
| **enrichment over prevalence** | **5.3×** |

**Local neighbourhoods are type-specific, not pair-specific.**

## 6 · Canonical dimensions

Dimension 1: canonical correlation **0.9865**, with η² of retron type **0.809** (RT side) and
**0.724** (ncRNA side) — the leading canonical dimension is largely retron type. Correlation is
spread across dimensions rather than concentrated (top-5 carry 17.3 % of summed canonical
correlation, k=32 retained). Per-dimension associations with RT length, ncRNA length and GC in
`tables/g2a_cca_dimensions.tsv`.

## 7 · Modality-specific retron-type encoding

Multinomial logistic probe on frozen pooled embeddings, **fit on train components, reported on
test components**, 21 classes, majority class 0.269:

| modality | test accuracy |
|---|---|
| ESM-C RT | **0.498** |
| RiNALMo ncRNA | **0.656** |

Each modality independently encodes retron type. This is explanatory, not an escalation gate.

## 8 · Preserved retrieval result (from `embed_g2`, commit `2c9127b`)

| rung | M-CCA MRR | 95 % CI (component-level) | status |
|---|---|---|---|
| 1 random candidates | **0.4407** | [0.4039, 0.4772] | reported |
| 2 length+GC-controlled | **0.2262** | [0.1972, 0.2565] | reported |
| 3 retron-type-controlled | **0.1832** | [0.1550, 0.2126] | reported |
| 4 ncRNA-cluster-controlled | 0.0925 | degenerate (1 component) | **UNDETERMINED** |
| 5 RT-cluster-controlled | 0.0992 | [0.0867, 0.1127] (10 components) | **UNDETERMINED** |
| 6 species-controlled | 0.2982 | [0.1904, 0.4262] (22 components) | **UNDETERMINED** |

Reverse direction (ncRNA→RT, random candidates): **0.4738** [0.4380, 0.5104].
Near-duplicate sensitivity population (1,525 pairs): rung 1 **0.4329** [0.3910, 0.4751].
Permutation failure control: observed 0.4407 vs null mean 0.0901, **p = 0.0005**.
Chance MRR = 0.0900.

## 9 · Rungs 4–6 are UNDETERMINED, not negative

They are **not** evidence of absence. The candidate pools for cluster- and species-matched
decoys are drawn from too few independent relatedness components (1, 10 and 22 respectively)
to support component-level confirmatory inference — the immutable inference unit. This is a
structural limit of the current pair universe, not a measured null.

## Within-type feasibility audit

`tables/g2a_within_type_feasibility.tsv`, and `DOWNSTREAM_DECISION_NOTE.md` for the reading.
**Audit only — nothing was trained and no model outcome was inspected.**
