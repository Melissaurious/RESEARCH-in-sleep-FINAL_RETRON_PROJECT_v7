# embed_g2b_frozen_split — **FROZEN**

> **STATUS: FROZEN 2026-09-18, before any downstream embedding compatibility result was
> examined.** Operator decision: **Option A approved — no secondary fragment bridge.**

Thresholds, split membership, sensitivity definition and inference unit **must not** change in
response to downstream model performance. A change requires a new operator decision record that
supersedes this manifest; this bundle is never edited.

## The frozen rule

| | |
|---|---|
| RT clustering | `mmseqs easy-cluster --min-seq-id 0.50 -c 0.8 --cov-mode 0` (mmseqs 18.8cc5c) |
| ncRNA clustering | `cd-hit-est -c 0.80 -aS 0.8 -n 8 -T 1` (CD-HIT 4.8.1) |
| RT coverage | **bidirectional** — both sequences ≥80 % covered |
| ncRNA coverage | **shorter-sequence** — shorter member ≥80 % aligned |
| split unit | connected component of the bipartite RT-cluster ↔ ncRNA-cluster graph, **indivisible** |
| fragment bridge | **NONE** |
| allocation | deterministic greedy, largest component → largest pair deficit; **no random seed, no RNG**; ties break train > val > test |

## The frozen split

| fold | pairs | % | components | **n_eff** | T1 | T2 | T3 | T4 | T4 % |
|---|---|---|---|---|---|---|---|---|---|
| train | 21,647 | 70.00 | 361 | 6.4 | 21,214 | 18,032 | 16,754 | 5,408 | 72.34 |
| val | 4,639 | 15.00 | 357 | 14.2 | 4,499 | 3,719 | 3,496 | 1,077 | 14.41 |
| **test** | **4,638** | **15.00** | **357** | **14.1** | 4,574 | 3,922 | **3,430** | **991** | **13.26** |

`split_assignment.tsv.gz` sha256 (uncompressed)
`78a9556378d4a7871a566fe914d3b7b7d52924b20149104339f8c1f62c77d376`

## Populations

**Primary confirmatory population — the full frozen test fold**: 4,638 pairs, 357 components,
n_eff 14.1, T4 13.26 %.

**Near-duplicate sensitivity population — PREDECLARED SENSITIVITY ANALYSIS.** Not a replacement
primary test, and not an alternative split selected on model performance.

- Rule: **local identity ≥ 0.90 AND aligned coverage ≥ 0.30**.
- **Coverage symmetrization, frozen:** `aligned_coverage = max(query_coverage, target_coverage)`.
  RT uses mmseqs `qcov`/`tcov`; ncRNA uses `alignment_length/query_length` and
  `alignment_length/subject_length` from blastn. `max()` because a fragment must count
  whichever way round it is — `min()` would miss a short held-out sequence contained in a long
  training one *and* the reverse.
- Stratum: **3 RT + 263 ncRNA** sequences, listed concretely in
  `tables/near_duplicate_stratum.tsv`.
- Exclusion unit: **whole test components** containing any touched pair — the split unit is the
  component, and a component with a near-identical bridge into training is suspect as a whole.
- Resulting population: **1,525 pairs, 284 components, n_eff 24.5, T4 3.20 %**.
- Pair-level exclusion (4,114 pairs, n_eff 12.6) is recorded as a descriptive alternative and is
  **not** the frozen definition.

## Frozen interpretation

> The primary experiment tests RT–ncRNA compatibility generalization across the declared
> sequence-relatedness component split. It does not establish generalization to evolutionarily
> unrelated RT or ncRNA sequences.

## Frozen inference unit

Inference for confirmatory results **must operate at the component level**. The 4,638 test pairs
are **not** independent observations; the effective number of independent units is **n_eff =
14.1**. Any test treating pairs as exchangeable overstates significance.

`n_eff = (Σ sᵢ)² / Σ sᵢ²` (inverse Simpson) — equals the component count when components are
equal-sized, collapses toward 1 when one dominates. The raw component **count** does not bound
component-level inference; this does.

## Measured leakage at freeze

Instrument: **independent of the clustering and more sensitive than it** — held-out searched
against a **training-only** database, so censoring is impossible. Held-out = test; training =
train **+ validation**, because validation is inspected during development.

| modality | id≥0.50 cov≥0.50 | id≥0.70 cov≥0.50 | id≥0.90 cov≥0.30 |
|---|---|---|---|
| RT | 3,685/4,469 = 82.46 % | 57/4,469 = 1.28 % | **3/4,469 = 0.07 %** |
| ncRNA | 1,175/2,756 = 42.63 % | 1,122/2,756 = 40.71 % | **263/2,756 = 9.54 %** |

Also: RT at id≥0.50 with **bidirectional** cov≥0.80 = 55.2 %; with **query-only** cov≥0.50 =
77.0 %. Three different coverage rules, three different numbers — always quote the rule.

- Held-out pairs reachable from training via either modality: **4,638/4,638 = 100.00 %**
- Held-out components with no detectable relationship to training: **0/357 = 0.00 %**

Both follow from all 29,192 sequences being reverse transcriptases — one protein family — so
*detectability* is saturated and uninformative. The identity-and-coverage tiers carry the
information.

⚠️ **Never quote unfiltered maximum ncRNA identity.** Every held-out ncRNA has a 100 %-identity
training match at <30 % coverage: short conserved msr/msd motifs, not homology. The unfiltered
statistic is saturated at 1.0. Only coverage-filtered numbers are interpretable.

## Why fragment bridges were rejected

1. The motivating concern **does not hold on the protein side** — 3 of 4,469 held-out RTs
   (0.07 %) cross at id≥0.90/cov≥0.30 under Option A.
2. The best bridge variant was **verified, not assumed**: it closes the RT channel completely
   (3 → 0) but only reduces ncRNA 263 → 54 (1.96 %), because bridges are built from a probe
   capped at 300 hits per query.
3. It costs **82 % of validation independence** (val n_eff 14.2 → 2.6). Looser variants are
   worse: id≥0.70 gives val n_eff **1.0**; id≥0.50 collapses the graph to a 94.3 % giant.
4. A surgical quarantine of the 73 affected test components was priced and rejected: test falls
   to 1,525 pairs (4.93 %) and T4 retention to 3.20 %.

**The ncRNA near-duplicate channel is accepted and reported, not eliminated.** It is handled by
the predeclared sensitivity stratum, not by a structural change.

## Verifying

```bash
bash results/embed_g2b_frozen_split/verify.sh
```

Runs the seeded-bad case first (the verifier must reject a corrupted reconstruction — a check
that cannot fail is not evidence), then the real verification: 32 checks covering input hashes,
component membership, all 30,924 fold labels, fold statistics, every operator-enumerated
pre-freeze fact, the near-duplicate stratum, and the verbatim non-numeric commitments.

**Result at freeze: seeded-bad rejected; 32/32 passed; 30,924/30,924 fold labels agree.**
