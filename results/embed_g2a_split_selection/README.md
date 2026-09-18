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

---

# Addendum — the fragment-leakage channel (operator check, 2026-09-18)

Motivated by a problem the threshold analysis itself exposed: the primary clustering requires
80 % coverage, so a near-identical **fragment** of a training sequence fails the coverage test,
forms its own cluster, and is free to cross into the held-out fold. Identity thresholds were
**not** touched — RT stays 0.50, ncRNA stays 0.80.

## The channel, measured exactly (held-out vs training-only database, no censoring)

| modality | id≥0.50 & cov≥0.50 | id≥0.70 & cov≥0.50 | id≥0.90 & cov≥0.30 |
|---|---|---|---|
| RT | 3,685 / 4,469 = 82.46 % | 57 / 4,469 = **1.28 %** | 3 / 4,469 = **0.07 %** |
| ncRNA | 1,175 / 2,756 = 42.63 % | 1,122 / 2,756 = 40.71 % | 263 / 2,756 = **9.54 %** |

**The RT fragment channel is already closed under Option A** — three sequences out of 4,469.
The premise that motivated this check does not hold on the protein side. The ncRNA side is the
real channel, at 9.54 %.

## An artefact that invalidates unfiltered ncRNA identity

Every held-out ncRNA (2,756 / 2,756, median identity **1.000**) has a 100 %-identity training
match at <30 % coverage. These are short conserved msr/msd motifs, not homology. Unfiltered
maximum ncRNA identity is saturated at 1.0 and carries no information; only coverage-filtered
numbers are interpretable. At cov ≥ 0.80 only 21.3 % of held-out ncRNAs have any hit at all.

## Option B costs more than it buys

| | components | largest | train/val/test | test n_eff | val n_eff | T3 test | T4 test |
|---|---|---|---|---|---|---|---|
| **A — no bridge** | 1,075 | 18.5 % | 21,647/4,639/4,638 | **14.1** | **14.2** | 14.48 % | 13.26 % |
| B, id≥0.50 cov≥0.50 | 137 | 94.3 % | 29,163/881/880 | 1.6 | 1.2 | 2.09 % | 2.18 % |
| B, id≥0.70 cov≥0.50 | 480 | 34.1 % | 21,457/5,018/4,449 | 7.1 | **1.0** | 13.21 % | 13.44 % |
| B, id≥0.90 cov≥0.30 | 882 | 21.8 % | 21,647/4,639/4,638 | 13.3 | **2.6** | 12.69 % | 12.56 % |

And the bridge was **verified, not assumed** (`g2_bridge_verification.tsv`). The best variant
closes the RT channel completely (3 → 0) but only reduces the ncRNA channel 263 → 54 (1.96 %),
because bridges are built from a probe capped at 300 hits per query. It costs **82 % of
validation independence** (n_eff 14.2 → 2.6) to buy that.

A surgical alternative — quarantine the 73 test components containing an offender into train —
was also priced: test falls to 1,525 pairs (4.93 %) and T4 test retention to 3.20 %.

## Recommendation: **A**, plus a declared near-duplicate sensitivity stratum

No structural change. The 263 held-out ncRNAs and 3 held-out RTs crossing at id ≥ 0.90 /
cov ≥ 0.30 are recorded as a predeclared **near-duplicate stratum**, and the confirmatory
readout is reported twice: on the full test fold (4,638 pairs, n_eff 14.1) and on the
near-duplicate-free subset (1,525 pairs, n_eff 24.5, T4 3.20 %). That turns the residual from
an untested assumption into a measured sensitivity, at zero cost to the primary split.
