# RT–ncRNA embedding compatibility — summary for supervision meeting

**Melissa Rios · 2026-09-18 · embedding track closed**
Full report: `RT_NCRNA_EMBEDDING_REPORT.md` · artifacts: commits `15e00b8`, `2c9127b`, `9154972`

---

## 1 · Question

> Do naturally associated retron RT and ncRNA sequences carry cross-modal sequence information
> that distinguishes their **observed** association beyond composition, relatedness, retron type
> and dataset structure?

Not tested, and not claimed: co-evolution, physical binding, biochemical compatibility,
residue–nucleotide contacts.

## 2 · Data

**30,924 observed RT–ncRNA associations** · 29,192 unique RTs · 16,458 unique oriented ncRNAs ·
21 retron types. Tiers T1 30,287 / T2 25,673 / T3 23,680 / T4 7,476.

ncRNA sequences did not exist in the derived layer and were reconstructed for this track:
**16,458 / 16,458 verified by sha256 round-trip against the Stage-1 hash**, zero mismatches.
Orientation confirmed (all placements `orientation_corrected`), which matters — an earlier
project cached 21.4 GB of RNA embeddings computed on reverse complements.

Representations are **frozen**: ESM-C 300M (960-d) and RiNALMo giga-v1 (1280-d), produced on
Ibex A100, 29,192 / 16,458 sequences verified complete, no truncation.

## 3 · Split — the methodological core

```
 RT sequences ──mmseqs 0.50, bidirectional 80% cov──►  RT clusters   ┐
                                                                     ├─ bipartite graph
 ncRNA seqs  ──cd-hit-est 0.80, shorter-seq 80% cov──► ncRNA clusters ┘   (edge = observed pair)
                                   │
                                   ▼
                    CONNECTED COMPONENTS = indivisible split units
                                   │
        ┌──────────────────────────┼──────────────────────────┐
     TRAIN 21,647                VAL 4,639                TEST 4,638
     361 comps                   357 comps                357 comps
     n_eff  6.4                  n_eff 14.2               n_eff 14.1  ◄── the real sample size
```

**The single most important number in this work is not 4,638 — it is 14.1.** Pairs concentrate
into relatedness components; the effective number of independent test units
(`n_eff = (Σs)²/Σs²`) is 14.1. Treating pairs as observations would overstate precision by two
orders of magnitude. All inference is component-level bootstrap and permutation.

Choosing the threshold was itself a measured result: **strict relatedness blocking and
statistical power are in direct opposition here.** RT 0.30 blocks leakage superbly (1.7 %) and
leaves a *single-component validation fold*; RT 0.70+ gives hundreds of units and ~90 % leakage.
RT 0.50 / ncRNA 0.80 is the compromise, frozen before any model was run.

## 4 · Models

```
 RT  ──► ESM-C 300M (frozen) ──► 960-d ──┐
                                          ├─► regularized CCA (k=32, α=0.01) ─► cosine
 ncRNA ─► RiNALMo (frozen) ───► 1280-d ──┘      fit on TRAIN components only
```

Plus five trivial baselines run **first**: ncRNA popularity, length, GC, **RT-k-mer→ncRNA-k-mer**
(strongest), and a retron-type label shortcut. 50-way retrieval; chance MRR 0.0900; decoys that
are observed partners of the query RT anywhere in the corpus are excluded and redrawn.

## 5 · Key figures

`figures/fig3_shared_cca_atlas.png` · `figures/fig4_similarity_retrieval.png` ·
`figures/fig5_cca_dimensions.png` (plus fig1/fig2 per-modality atlases). Full captions in
`FIGURE_INDEX.md`.

## 6 · Findings

**Retrieval is strong against easy candidates and collapses as candidates are matched on type.**

| candidates matched on | k-mer baseline | **M-CCA** | difference (95 % CI) |
|---|---|---|---|
| nothing (random) | 0.2265 | **0.4407** | **+0.2142 [+0.1737, +0.2537]** |
| length + GC | 0.1418 | **0.2262** | **+0.0844 [+0.0503, +0.1187]** |
| **retron type** | 0.1534 | 0.1832 | **+0.0298 [−0.0048, +0.0633]** ← not distinguishable |
| ncRNA cluster / RT cluster / species | — | — | **UNDETERMINED** (1, 10, 22 components) |

Supporting: reverse direction 0.4738 · permutation control p = 0.0005 (null mean 0.0901) ·
near-duplicate-excluded population 0.4329, a −0.008 change.

**Why: the space organizes by retron type, not by partner.**

- Observed partner is the nearest cross-modal neighbour for **0.56 %** of queries;
  **median rank 238 of 2,756**.
- **50 %** of top-10 cross-modal neighbours share the query's retron type, against **9.4 %**
  prevalence — **5.3× enrichment**.
- Leading canonical dimension: correlation 0.9865, with **η² of retron type 0.81 (RT) / 0.72
  (ncRNA)**.
- Retron type is recoverable from **each modality alone**: ESM-C 0.498, RiNALMo 0.656 (majority
  0.269) — a sufficient route by which any alignment method could score well without learning
  partner compatibility.

## 7 · Principal limitation

**n_eff = 14.1.** The confirmatory test rests on ~14 independent units. The rung-3 result is an
absence of a *distinguishable* difference, not evidence of equivalence, and rungs 4–6 are absence
of *measurement*, not measured absence — their candidate pools draw on 1, 10 and 22 components.

## 8 · Why contrastive escalation was stopped

The pre-registered escalation condition — beat every trivial baseline on the held-out split —
was not met at rung 3. A high-capacity InfoNCE model with arbitrary mismatched candidates has an
easy path to a high score through retron-type recognition, and at n_eff ≈ 14 we could not tell
afterwards which it had learned.

**This is not hypothetical.** An independent line of work in this lab
(`openCRISPR_for_retrons`) trained the protein-conditioned generative architecture on retrons and
concluded *"the model does FAMILY RECOGNITION, not partner recognition"* — with a row-matched
control attributing **78 %** of its leave-one-family-out gap to family identity. Its contrastive
arm raised the metric it optimised **43-fold while degrading the rank statistic** (2AFC 0.9532 →
0.9072, t = −21). Two methods, two populations, same conclusion.

Status: **`NOT YET JUSTIFIED AS A CONFIRMATORY PARTNER-SPECIFIC TEST`**, not `METHOD REJECTED`.

## 9 · Framing

This is a **bounded negative that located the information scale**. It establishes:

- **Level 1 — shared RT–ncRNA organization at retron-type / system-class level: evidence for.**
- **Level 2 — individual partner specificity within that organization: not established.**

and it identifies the constraint precisely: **independent relatedness components, not model
capacity or raw pair count.**

## 10 · Concrete next steps

1. **Do not run a contrastive/cross-attention model on the current population.** It would be
   evaluated against ~14 independent units, and the prior generative attempt shows what that
   produces.
2. **Within-type feasibility is measured and mostly negative**: of 21 retron types, only
   **TypeIIIA3** and **TypeIB1** pass the population criteria, and even they have *test-fold*
   n_eff of **3.7** and **4.6**. `TypeIC1_IC2` has 6,277 pairs but n_eff **1.2** — raw counts are
   actively misleading.
3. **The highest-value scientific move is ncRNA recovery, not modelling.** Every ncRNA call in
   the corpus comes from a covariance model. Retron ncRNAs that no CM detects are invisible by
   construction, and those sit disproportionately in divergent lineages — exactly the ones that
   would add *independent components*. Any advance there should re-trigger the feasibility audit
   (`a07_within_type_feasibility.py`, one command).
4. **Reuse, don't rebuild.** InfoNCE, memory-aware in-batch negatives with measured VRAM, the
   cross-attention architecture and an N×N/2AFC evaluator all already exist
   (`HISTORICAL_MODEL_ASSET_AUDIT.md`). What they lack — and what this track now supplies — is a
   relatedness-aware split and component-level inference.
5. **Token-level arrays are cached and untouched**, awaiting independently established msr/msd
   and RT-domain annotations.

**Discussion question for the meeting:** is the priority (a) expanding independent RT–ncRNA
associations, especially via non-CM ncRNA recovery, or (b) accepting level-1 organization as the
thesis result for this chapter and directing modelling effort elsewhere?
