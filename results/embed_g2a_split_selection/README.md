# embed_g2a_split_selection — relatedness-threshold trade-off

> **STATUS: PROPOSAL. NOTHING HERE IS FROZEN.** It recommends a primary split rule for
> operator approval. No threshold is in force until an operator decision record says so.

**Gate weight: LIGHT.** Structure only.

## The blindness guarantee

This analysis never loaded an embedding, never computed an RT–ncRNA similarity, and never read
a retrieval, CCA, CKA, contrastive or paired-vs-mismatched result. Every quantity is a property
of sequence relatedness and pair topology. The threshold decision therefore cannot have been
contaminated by the thing the split will later be used to test.

## Declared coverage rule

| side | tool | coverage semantics |
|---|---|---|
| RT | `mmseqs easy-cluster --min-seq-id X -c 0.8 --cov-mode 0` | **bidirectional**: both sequences ≥80 % covered |
| ncRNA | `cd-hit-est -c X -n 8 -aS 0.8 -T 1` | **shorter-sequence**: the shorter member ≥80 % aligned |

Deliberately different. A protein pair aligning over 80 % of both is homologous along its
length; ncRNAs at 34–395 nt are short enough that anchoring on the shorter member is standard
and avoids discarding a real relative over a length difference. `-T 1` because cd-hit's
multithreaded path is not order-deterministic (measured in `embed_g0`).

## Split unit and frozen split rule

Split unit = connected component of the bipartite graph with RT exact sequences collapsed to RT
relatedness clusters, ncRNA exact sequences to ncRNA clusters, and an observed pair as an edge.
Components are indivisible.

Rule: target 70/15/15 by pair count; components sorted by (pairs desc, key asc); each assigned
to the fold with the largest remaining deficit; ties break train > val > test. Deterministic,
no seed.

## The leakage instrument is independent of the clustering

Measuring leakage with the clustering tool at the clustering threshold returns zero by
construction. Two separate measurements were used instead:

- `s01` — all-vs-all probe over the whole universe, **more sensitive than any threshold tested**:
  mmseqs `-s 7.5 --min-seq-id 0` (8.71 M RT hits), blastn `-task blastn -word_size 7`
  (2.76 M ncRNA hits), both e ≤ 1e-3.
- `s03` — **exact** test-vs-train search for the candidate combinations. `s01` keeps ≤300 hits
  per query against the whole universe, and at RT 0.30 **75–82 % of held-out RTs never reached a
  training sequence in the retained list**, making their leakage a lower bound that flattered
  the strict thresholds. Searching against a training-only database removes the censoring.
  It mattered: RT 0.30/0.95 measured 4.9 % censored vs **15.7 % exact** at ≥0.5 identity.

Held-out = test. Training = train **+ validation**, because validation is inspected during
development, so leakage into it is leakage.

Two coverage views are reported because they answer different questions: `qcov≥0.5` ("does a
training sequence look like most of this held-out one") and `qcov≥0.8 & tcov≥0.8` (the same
bidirectional rule that built the RT clusters — a cross-boundary pair passing this is a genuine
clustering failure, whereas a high-identity pair failing it is the **coverage rule** letting a
fragment through, a different problem with a different remedy).

## The finding that decides it

Component **count** is misleading. `n_eff = (Σs)² / Σs²` is the effective number of independent
components, and it collapses toward 1 when one component dominates a fold.

| combo | RT leak ≥0.5 (bidir80) | ncRNA leak ≥0.5 (bidir80) | test n_eff | val n_eff |
|---|---|---|---|---|
| 0.30/0.95 | **1.7 %** | **10.0 %** | **4.0** | **1.0** |
| 0.50/0.80 | 55.2 % | **17.7 %** | 14.1 | 14.2 |
| 0.50/0.90 | 50.9 % | 34.3 % | 18.2 | 18.0 |
| 0.50/0.95 | 47.3 % | 39.2 % | 19.1 | 18.7 |
| 0.70/0.90 | 89.4 % | 75.3 % | 631.1 | 631.0 |

RT 0.30 blocks relatedness superbly and is **unusable**: its validation fold is a *single*
component of 4,781 pairs (n_eff 1.0) and its test fold has n_eff 4.0. RT 0.30 with ncRNA
0.80/0.90 fails earlier still — the frozen rule reaches only 5.4–5.7 % test.

## Recommendation, pending approval

**Primary: RT 0.50 / ncRNA 0.80.** Strictest blocking that leaves a usable number of
independent components, per the stated decision principle. Sensitivity: RT 0.50/ncRNA 0.90 and
0.95, RT 0.70/ncRNA 0.90, and RT 0.30/ncRNA 0.95 as the strict-blocking bound.

## Honest limit of the current pair universe

The universe supports a split that is either relatedness-strict **or** statistically powerful,
not both. At the strictest feasible blocking effective n collapses to ~4; at comfortable n
(RT 0.70+) leakage reaches ~90 %. The recommendation sits at n_eff ≈ 14 with ~55 % of held-out
RTs having a ≥50 %-identity training relative. The confirmatory readout therefore measures
**generalization to moderately diverged RTs, not to unrelated ones**, and must say so.
