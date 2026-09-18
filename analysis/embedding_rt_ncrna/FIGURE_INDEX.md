# Figure index

Every figure regenerates deterministically from its plotting table via
`results/embed_g2c_atlas/scripts/a06_figures.py`, which reads only `plotdata/` and `tables/` —
no embedding, model or GPU code re-runs. Copies for this report are in
`analysis/embedding_rt_ncrna/figures/`; the canonical originals are in
`results/embed_g2c_atlas/figures/`.

| # | file | plotting table | compute script | descriptive / inferential |
|---|---|---|---|---|
| 1 | `figures/fig1_rt_atlas.png` | `results/embed_g2c_atlas/plotdata/atlas_rt.tsv` | `a05_atlas.py` | descriptive |
| 2 | `figures/fig2_ncrna_atlas.png` | `results/embed_g2c_atlas/plotdata/atlas_ncrna.tsv` | `a05_atlas.py` | descriptive |
| 3 | `figures/fig3_shared_cca_atlas.png` | `results/embed_g2c_atlas/plotdata/atlas_shared_cca.tsv` | `a05_atlas.py` | descriptive |
| 4 | `figures/fig4_similarity_retrieval.png` | `plotdata/similarity_long.tsv` + `tables/g2a_neighbourhood.json` + `results/embed_g2_frozen_baseline/tables/g2_test_ladder.tsv` | `a05_atlas.py`, `a05b_neighbourhood_topk.py`, `a04_test.py` | panel (b) **inferential**; (a), (c) descriptive |
| 5 | `figures/fig5_cca_dimensions.png` | `tables/g2a_cca_dimensions.tsv` + `tables/g2a_type_encoding.tsv` | `a05_atlas.py` | (a), (b) descriptive; (c) probe, explanatory |

---

## Captions

**Figure 1 — RT embedding atlas.** UMAP of frozen pooled ESM-C 300M representations for 8,000 RT
sequences sampled from the 29,192-sequence pair universe, coloured by (a) retron type,
(b) T1–T4 tier, (c) RT length in amino acids, (d) major NCBI species. Grey points are retron
types outside the legend. PC1–2 of the full space explain 69.1 % of variance.
*Descriptive only; UMAP geometry is not evidence of discrete biological classes.*

**Figure 2 — ncRNA embedding atlas.** UMAP of frozen pooled RiNALMo giga-v1 representations for
8,000 of the 16,458 oriented ncRNA sequences, coloured by (a) the retron type of the associated
RT, (b) T1–T4 tier, (c) ncRNA length in nucleotides, (d) major NCBI species. PC1–2 explain
49.7 %. *Descriptive only.*

**Figure 3 — Shared CCA-space atlas.** RT (circles, ESM-C) and ncRNA (triangles, RiNALMo)
projected into the shared regularized-CCA latent space (k = 32, α = 0.01, fit on training
components only) and laid out by UMAP, for 1,200 observed pairs sampled from the test fold
(2,400 points). Colour = retron type. **Left**: all sampled points. **Right**: a readable
150-pair subset with light segments joining each RT to its observed partner; a 30,924-segment
rendering would be uninterpretable and is deliberately not produced. RT and ncRNA of the same
retron type co-localize. *Descriptive only.*

**Figure 4 — Cross-modal similarity, retrieval ladder and neighbourhood composition.**
**(a)** Distribution of CCA cosine similarity for observed pairs and three classes of retrieval
decoy (random, length+GC-matched, type-matched); the separation shrinks monotonically as decoys
are matched more closely on retron type. *Descriptive.*
**(b)** Retrieval MRR across the candidate ladder for the cross-modal probe (M-CCA) and the
strongest trivial baseline (B-kmer), with component-level 95 % bootstrap intervals, the chance
line at MRR 0.0900, and rungs 4–6 explicitly marked **UNDETERMINED** because their candidate
pools draw on only 1, 10 and 22 independent relatedness components. *Inferential — this panel
carries the result.*
**(c)** Neighbourhood composition in the open 2,756-candidate pool: the fraction of queries whose
observed partner is retrieved at rank 1/5/10, against the fraction of those neighbours sharing
the query's retron type, with the background type-prevalence line at 9.4 %. *Descriptive.*

**Figure 5 — Canonical structure is dominated by retron type.**
**(a)** Canonical correlations across all 32 retained dimensions (0.987 → 0.774) with the
cumulative share of summed correlation; the top 5 dimensions carry 17.3 %, so correlation is
spread rather than concentrated. **(b)** η² of retron type per canonical dimension, separately
for the RT and ncRNA sides; dimension 1 reaches 0.809 and 0.724. **(c)** Retron-type probe
accuracy per modality (ESM-C 0.498, RiNALMo 0.656) against the majority-class rate of 0.269 —
a multinomial logistic probe fit on training components and reported on test components.
*(a) and (b) descriptive; (c) explanatory, and explicitly not an escalation gate.*
