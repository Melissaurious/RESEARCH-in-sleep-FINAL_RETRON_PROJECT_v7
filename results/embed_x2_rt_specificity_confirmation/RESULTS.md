# embed_x2 — RT-specific conditioning confirmation · RESULTS

All numbers are **out-of-fold**, aggregated per-sequence → per-component (token-weighted) →
bootstrap over **independent connected components** (10,000 resamples). Components are the
inference unit throughout; pair counts are never used as a sample size.

Design, counterfactual rules and stratification axes were frozen before any effect estimate
was inspected (`DESIGN.md`, `COUNTERFACTUAL_RULES.md`, `scripts/y05_strata.py`).
Execution incidents are in `EXECUTION_NOTES.md`.

---

## 1 · Arm-level out-of-fold NLL (1,075 components, 30,924 pairs)

| arm | conditioning | OOF NLL (component mean) | 95 % CI |
|---|---|---|---|
| U | none | 1.40666 | [1.40433, 1.40895] |
| T | retron-type label | 1.38329 | [1.37840, 1.38831] |
| G | ESM-C of RT **cluster representative** | 1.36410 | [1.35966, 1.36850] |
| R | ESM-C of the **observed RT** | 1.35859 | [1.35401, 1.36316] |
| P | ESM-C of a **permuted** RT (training only) | 1.37739 | [1.37076, 1.38454] |

## 2 · Paired per-component contrasts (negative = first arm better)

| contrast | Δ | 95 % CI | median | % components favouring first |
|---|---|---|---|---|
| T − U | −0.02337 | [−0.02775, −0.01902] | −0.02588 | 76.1 % |
| G − U | −0.04256 | [−0.04619, −0.03893] | −0.03491 | 86.0 % |
| R − U | −0.04807 | [−0.05157, −0.04458] | −0.03988 | 87.3 % |
| **R − T (primary)** | **−0.02470** | **[−0.02907, −0.02037]** | −0.01360 | **64.9 %** |
| **R − G (lineage)** | **−0.00551** | **[−0.00797, −0.00312]** | −0.00264 | **55.3 %** |
| G − T | −0.01919 | [−0.02339, −0.01498] | −0.00979 | 62.4 % |
| **P − T (falsification)** | **−0.00590** | **[−0.01109, −0.00023]** | −0.00615 | 57.0 % |
| R − P | −0.01880 | [−0.02460, −0.01359] | −0.00839 | 59.7 % |

### 2.1 Primary endpoint replicates X1

X1 reported R − T = −0.01778 [−0.02428, −0.01052] with 65.0 % of components favouring R.
The cross-fitted estimate is **−0.02470 [−0.02907, −0.02037] with 64.9 %** favouring R.
Same sign, comparable magnitude, near-identical component fraction. **Criterion (1) met.**

### 2.2 The permutation control is NOT flat

P − T = −0.00590 [−0.01109, −0.00023]. A model trained on RTs **deranged within retron type**
still beats the type label, by roughly a quarter of the full R − T effect. R − P = −0.01880
confirms the observed correspondence supplies most of the advantage, but **not all of it**:
some benefit comes from conditioning on *a* real RT embedding rather than *the* right one.
This is a real qualification on the primary effect and is reported, not absorbed.

## 3 · Prespecified strata — T4 resolved

| population | R − T | 95 % CI | components | status |
|---|---|---|---|---|
| full | −0.02470 | [−0.02907, −0.02037] | 1,075 | OK |
| **T4** | **−0.02594** | **[−0.03508, −0.01731]** | **247** | **OK** |
| T3 | −0.02848 | [−0.03489, −0.02260] | 584 | OK |
| near-duplicate-excluded sensitivity | −0.02532 | [−0.03410, −0.01682] | 284 | OK |

`DESIGN.md` §3 predicted in advance that T4 might remain unresolved, because cross-fitting
raises T4 coverage from 83 to 247 components while n_eff moves 9.0 → 8.6. **That prediction
was wrong in the favourable direction**: the T4 interval excludes zero.
**Criterion (2) met.**

## 4 · Between-fold heterogeneity

| fold | R − T | 95 % CI | components |
|---|---|---|---|
| 0 | −0.01563 | [−0.03028, −0.00296] | 194 |
| 1 | −0.01438 | [−0.02074, −0.00831] | 219 |
| 2 | −0.02690 | [−0.03651, −0.01759] | 220 |
| 3 | −0.03567 | [−0.04256, −0.02789] | 221 |
| 4 | −0.02973 | [−0.04058, −0.01939] | 221 |

Mean −0.02446, sd 0.00921, **all five folds the same sign**, every fold interval excluding
zero. The effect is not carried by one fold.

## 5 · Counterfactual hierarchy — the decisive result

Δ log P per nt = NLL(ncRNA | alternative RT) − NLL(ncRNA | observed RT).
**Positive favours the observed RT.** All four tiers are adjudicable
(≥ 30 components; C4 has 451).

| tier | alternative drawn from | pairs | comps | Δ log P/nt | 95 % CI | % pairs favouring observed | % components |
|---|---|---|---|---|---|---|---|
| C1 | same retron type | 30,796 | 1,019 | **+0.01766** | [+0.01533, +0.01994] | 72.6 % | 81.1 % |
| C2 | + RT length within 10 % | 29,459 | 832 | **+0.01543** | [+0.01291, +0.01786] | 70.6 % | 80.4 % |
| C3 | + 8 nearest ESM-C neighbours | 30,922 | 1,073 | **+0.00397** | [+0.00202, +0.00586] | **52.5 %** | 60.8 % |
| C4 | within 50 %-identity RT cluster | 29,186 | 451 | **+0.00168** | [+0.00101, +0.00251] | 60.7 % | 66.3 % |

**Every tier's interval excludes zero — but the effect decays ~10-fold from C1 to C4.** Once
the alternative RT is drawn from the observed RT's own embedding neighbourhood (C3), only
**52.5 % of pairs** favour the observed RT: barely above a coin flip at the pair level, even
though the component-level mean is positive and its interval excludes zero.

The honest reading: the model carries information that distinguishes the observed RT from a
*same-type* alternative, and a small but reproducible residue that survives even a
*within-homolog-cluster* alternative. It does **not** carry information that cleanly
separates the observed RT from its nearest sequence neighbours on a per-pair basis.

## 6 · Lineage control (G) — sign stable, magnitude not

R − G = −0.00551 [−0.00797, −0.00312] on the primary seed, 55.3 % of components. Since
G − T = −0.01919 of the total R − T = −0.02470, **most of R's advantage over the type label
is already captured by the 50 %-identity homolog group**.

Seed replication (`SEED_STABILITY.tsv`, three seeds) shows:

| contrast | seed 20260918 | seed 20260919 | seed 20260920 | sd | same sign |
|---|---|---|---|---|---|
| R − T | −0.02470 | −0.03674 | −0.02093 | 0.00826 | yes |
| R − G | −0.00551 | −0.01133 | −0.01560 | 0.00506 | yes |

**R − T is robust to optimization noise.** **R − G is not well determined**: the across-seed
spread is a factor of three and the sd (0.0051) is as large as the primary point estimate
(0.0055). All three seeds agree on the *sign*, so R beats its own cluster representative
consistently, but the **magnitude of that increment cannot be pinned down** by this
experiment. Criterion (4) is met only in the weak, directional sense.

Per Amendment A the primary endpoint remains the seed-20260918 cross-fit. Seed-averaged
values (R − T = −0.02746) are a stability check, **not** the headline, and do not add
independent biological observations.

## 7 · Sensitivity strata (§10)

36 adjudicable R − T strata: **28 with the whole 95 % CI below zero, 1 above zero, 7 spanning
zero; 86.1 % favour R.** Full table in `SENSITIVITY_STRATA.tsv`.

### 7.1 The relatedness gradient — the most important caveat

Stratifying by cosine similarity between the evaluated RT and the **nearest RT the evaluating
model actually saw in training**:

| quartile | R − T | 95 % CI | comps | R − G | 95 % CI |
|---|---|---|---|---|---|
| Q1 < 0.983 | **−0.00584** | **[−0.01288, +0.00136]** | 371 | −0.00426 | [−0.01012, +0.00148] |
| Q2 0.983–0.988 | −0.02317 | [−0.02869, −0.01765] | 378 | −0.00686 | [−0.01135, −0.00259] |
| Q3 0.988–0.991 | −0.02298 | [−0.02793, −0.01831] | 447 | −0.00480 | [−0.00790, −0.00177] |
| Q4 ≥ 0.991 | −0.03193 | [−0.03994, −0.02454] | 473 | −0.00430 | [−0.00735, −0.00134] |

**R − T is monotonically stronger where the evaluated RT more closely resembles training
RTs, and in the least-similar quartile its interval spans zero.** This is exactly the
confound §10 was designed to expose, and it is a genuine limit on generalisation to
RT lineages unlike anything in training.

Two mitigating observations, stated without overstating them: (i) RT ESM-C embeddings are
highly compressed — the *median* nearest-training cosine is 0.987 and even Q1 sits above
0.983, so this is a narrow range, not near-vs-far homology; (ii) **R − G is flat across the
same quartiles** (≈ −0.004 to −0.007), so the gradient lives in the **T** arm rather than
being residual RT relatedness leaking into R.

### 7.2 Other axes

- **Retron type**: 6 of 8 largest types favour R with intervals excluding zero; `TypeIIIA3`
  (+0.0067) and `TypeIB1` (+0.0077) nominally favour T, neither significant. `TypeIB2`
  shows the largest effect (−0.0964) on 46 components.
- **RT homolog group size**: effect present in every adjudicable bin (−0.018 to −0.022); the
  largest bin (>100 members) is **UNDETERMINED** at 22 components.
- **ncRNA cluster size**: the effect is carried by small clusters (−0.025 at sizes 1 and 2–5)
  and is **not** demonstrated for the largest clusters (>100: UNDETERMINED, 14 components;
  21–100: CI spans zero).
- **Taxonomy** (`n_species`) and **deposition multiplicity** (`n_physical_loci`): effect
  present across all adjudicable levels, mildly *weaker* at high multiplicity
  (n_physical_loci ≥ 21: −0.0107) — i.e. **not** an artefact of repeated deposition.
- **Recurrence class**: present in all four well-supported classes, including
  `multiple_species` (−0.02507, 364 components), the repeated-*event* class.

---

## 8 · What these results do and do not support

**Supported.** A frozen RT-conditioned RNA decoder assigns reproducibly higher likelihood to
an ncRNA when conditioned on the RT actually observed with it than on the retron-type label,
under component-blocked cross-fitting that excludes RT-cluster and ncRNA-cluster leakage.
The effect survives the high-independence T4 stratum, near-duplicate exclusion, all five
folds, taxonomy and deposition strata, and three optimization seeds.

**Not supported, and not claimed.** Biochemical compatibility · binding · functional
interchangeability · physical interaction · causal co-evolution · that any counterfactual
pairing is biologically incompatible. Counterfactual RTs are **controls, not negatives**; a
combination absent from the corpus is a **non-observed pairing**. No log-likelihood
difference is converted into a compatibility label, interaction probability or pair score,
and no AUROC against mismatched pairs is reported.

**Explicit limits.**
1. Effect sizes are **small in absolute terms** (0.0017–0.0177 nats/nt).
2. **Most** of the advantage over the type label is explained by the 50 %-identity homolog
   group (G − T = −0.019 of −0.025); the specific-RT increment beyond it is small and its
   magnitude is seed-unstable.
3. The permutation control is **not flat** (P − T = −0.0059).
4. Generalisation degrades with distance from training RTs (§7.1, Q1 spans zero).
5. At the pair level under the strictest embedding-neighbour control, only 52.5 % of pairs
   favour the observed RT.
6. This is **INTERNAL cross-fitted confirmation, not external validation**. No new data
   exist; the same 30,924-pair population underlies X1 and X2.
