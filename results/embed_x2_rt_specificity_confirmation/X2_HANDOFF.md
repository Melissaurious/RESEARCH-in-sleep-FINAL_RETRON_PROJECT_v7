# embed_x2 — HANDOFF

Minimum requirements for any later RT–ncRNA **pairing-specificity** analysis. These are not
style preferences: each one is the direct consequence of a finding in `X2_CLOSURE.md`, and an
analysis that skips one will report a number that X2 has already shown to be inflated,
unstable or unsupported.

---

## 1 · Six binding requirements

### R1 — Use C3/C4-strength counterfactuals, not merely same-type mismatches

Same-type contrasts (C1) are roughly **10× easier** than within-homolog-cluster contrasts
(C4): +0.0177 vs +0.0017 nats/nt. Any headline built on same-type mismatches will overstate
pairing specificity by about an order of magnitude.

A counterfactual must be admissible on the frozen rules (`COUNTERFACTUAL_RULES.md`): the
alternative RT differs from the observed one, is **not** observed with that ncRNA anywhere in
the full table, and lies in the **same cross-fit fold** as the query, so novelty is not
confounded with specificity.

### R2 — Evaluate at component/group level; pairs are not independent

The inference unit is the connected component of the bipartite RT-cluster ↔ ncRNA-cluster
graph. 30,924 pairs correspond to 1,075 components, and n_eff is **12.5** for the full
population — pair counts overstate the sample size by more than three orders of magnitude.
Aggregate per-sequence → per-component (token-weighted) → bootstrap over components.

Cross-fitting buys **coverage and robustness, not power**: it raised T4 coverage 83 → 247
components while n_eff moved 9.0 → 8.6. n_eff is a property of the component-size
distribution, not of the number of folds.

### R3 — Carry seed uncertainty

`R − G` moved from −0.0055 to −0.0156 across three seeds — a factor of three, with sd 0.0051
against a primary estimate of 0.0055. **A magnitude quoted from one seed is not a result.**
Run ≥ 3 seeds, average within component before any inference, and report the across-seed
spread beside the point estimate. Replicate seeds bound optimization noise; they do **not**
add independent biological observations and must never enlarge the bootstrap unit.

### R4 — Distinguish RT lineage information from exact-RT information

Conditioning on the **RT homolog-group representative** (G) already captures most of the
advantage over the broad type label: G − T = −0.019 of R − T = −0.025. An analysis reporting
only "RT beats type" measures lineage, not pairing. Both contrasts are required:

- `R − T` — specific RT versus broad type
- `R − G` — specific RT versus its own 50 %-identity homolog group ← **the pairing question**

Use the frozen `rt_id0.50` clusters and condition on the representative's frozen embedding,
not a learned per-cluster embedding: components never share RT clusters across folds, so a
learned cluster table would be untrained for every evaluation cluster and degenerate.

### R5 — Preserve distance-to-training diagnostics

The effect is not demonstrated in the quartile least similar to training RTs (R − T = −0.0058,
CI spanning zero, versus −0.0319 in the most similar). Report nearest-training-RT similarity
as a **primary stratification axis**, not a footnote, and state explicitly the similarity
range over which any claim holds. `X2_PAIR_LEVEL_EFFECTS.tsv.gz` carries
`nearest_train_rt_cosine` and `relatedness_stratum` for exactly this purpose.

### R6 — Never treat unobserved pairings as biological negatives

Absence from the corpus is **non-observation**, not incompatibility. Without experimental
evidence, a non-observed pairing may not be used as a negative label, scored as incompatible,
or counted in a discrimination metric that presumes it to be wrong. This forbids AUROC
against artificial mismatches, compatibility classifiers trained on unobserved combinations,
and any conversion of a likelihood difference into an interaction probability or pair score.

## 2 · Also carry forward

- **Include a permutation control**, and expect it to be non-zero. P − T = −0.0059: a model
  trained on within-type-deranged RTs still beats the type label. Without this arm, that
  portion of the gain would be misattributed to correct pairing.
- **Report pair-level as well as component-level discrimination.** At C3 the component mean
  is positive while only 52.5 % of pairs favour the observed RT; reporting only the former
  would misrepresent what the model can do.
- **Report UNDETERMINED as UNDETERMINED.** A stratum with < 30 independent components is not
  a null. Absence of significance is not evidence of absence.
- **Freeze the split and hash it before training.** `CROSSFIT_MANIFEST.tsv` rehashes to the
  value recorded pre-training, which is what makes "the split was not tuned against the
  result" checkable rather than merely asserted.

## 3 · Machine-readable exports

Both exports are out-of-fold throughout. Every `delta_logP_*` column is

> NLL(ncRNA | alternative RT) − NLL(ncRNA | observed RT),

**positive favouring the observed RT**. It is not a compatibility score, not an interaction
probability, and not evidence that an alternative RT is incompatible.

### `tables/X2_PAIR_LEVEL_EFFECTS.tsv.gz` — 30,924 rows

| group | columns |
|---|---|
| identifiers | `rt_seq_hash`, `nc_seq_hash`, `component_id`, `cv_fold` |
| grouping | `retron_type`, `rt_homolog_group` (frozen `rt_id0.50` representative) |
| size | `rt_aa_len`, `nc_len`, `n_tok` |
| strata | `T3`, `T4`, `in_sensitivity_population`, `nearest_train_rt_cosine`, `relatedness_stratum` |
| per-arm NLL/nt | `nll_per_nt_{U,T,G,R,P}` |
| contrasts | `delta_R_minus_T`, `delta_R_minus_G` |
| counterfactual | `delta_logP_{C1,C2,C3,C4}`, `n_alternatives_{C1..C4}` |

Pair-level values are exported for joining and completeness. **The inference unit of this
experiment is the component; no per-pair biological inference is supported.**

### `tables/X2_COMPONENT_LEVEL_EXPORT.tsv` — 1,075 rows

Component identity and composition (`n_pairs`, `n_distinct_rt`, `n_distinct_ncrna`,
`n_retron_types`, `n_rt_homolog_groups`, `dominant_retron_type`, `cv_fold`), strata
(`any_T3`, `any_T4`, `in_sensitivity_population`, `mean_nearest_train_rt_cosine`,
`relatedness_stratum`), token-weighted `nll_per_nt_*` for all five arms, the contrasts
`delta_R_minus_T`, `delta_R_minus_G`, `delta_R_minus_P`, `delta_P_minus_T`, and
token-weighted `delta_logP_{C1..C4}` with per-tier pair counts.

**This is the file to use for inference.**

### Reconciliation between the two files

The component export reproduces the preregistered analysis exactly through an independent
code path: C1 +0.017664, C2 +0.015434, C3 +0.003974, C4 +0.001683, and R − T = −0.024701 over
1,075 components, all matching `tables/COUNTERFACTUAL_EFFECTS.tsv` and
`tables/COMPONENT_LEVEL_EFFECTS.tsv`.

Aggregating the **pair** file naively will not reproduce those numbers, and must not be
treated as a discrepancy:

| tier | component-level | raw pair mean | % pairs > 0 |
|---|---|---|---|
| C1 | +0.017664 | +0.009894 | 72.6 % |
| C2 | +0.015434 | +0.007951 | 70.6 % |
| C3 | +0.003974 | **−0.000205** | 52.5 % |
| C4 | +0.001683 | +0.002391 | 60.7 % |

Component-level aggregation gives every independent component equal weight; an unweighted
pair mean lets the largest components dominate. At C3 the two differ in **sign**. Any
downstream analysis must aggregate to the component before inference (R2), and must not quote
a pair-weighted mean as the effect.

## 4 · Joins that may be performed later

These exports were built so that independently defined features can be joined **without
retraining X2**, on `rt_seq_hash`, `nc_seq_hash` or `component_id`:

- Region X/Y annotations from Stage 3C
- RT phylogeny
- ncRNA family
- terminal / fusion architecture

**No such join was performed in this session.** Two cautions for whoever does:

1. A feature correlated with RT lineage will inherit the lineage signal. Any claim that a
   joined feature explains *pairing* specificity must be tested against `delta_R_minus_G` or
   `delta_logP_C4`, not `delta_R_minus_T` or `delta_logP_C1`.
2. Joining a feature and re-testing on this same population is not external validation.
   X2 is internal cross-fitted confirmation on the population that produced X1.
