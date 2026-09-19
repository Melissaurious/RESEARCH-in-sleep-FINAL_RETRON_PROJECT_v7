# METHODS — thesis-ready draft, with provenance

**Scope.** Methods for the RT–ncRNA representation and conditional-modelling chapter: dataset
construction, leakage-aware splitting, frozen representations, the shared-representation
baseline, and the conditional RNA model (X1, and X2 as specified-but-pending). Every numbered
subsection ends with a `provenance` line naming the frozen bundle and commit it is read from.

These methods are **stable** — they describe analyses that are already frozen. They are written
to be lifted into the thesis with minimal editing. Where a method exists only as a frozen
*design* (X2), it is marked **specified, result pending**.

**Nothing in this file was recomputed.** The single derived artifact of this workbench
(`derived/x1_component_level.tsv`) is a re-aggregation of frozen per-sequence outputs, verified
against the frozen summary tables by 46 of 46 checks.

---

## 1 · Study design and pre-registration

The embedding track (`embed`) was specified in `LAUNCHER_03_rt_ncrna_embedding_compatibility.md`
before any representation was computed. The launcher fixes, in advance: the analysis population,
the split discipline, the trivial-baseline ladder that must be run first, the six-rung candidate
ladder, the confirmatory readout ("opened once"), and five kill criteria — including a
**rung-3 kill**: if signal survives random and composition-matched candidates but vanishes when
candidates are matched on retron type, the result is reported as *explained by retron type*, not
as pairing compatibility.

The launcher also fixes an **interpretation boundary** that binds every gate: a positive result
may support, at most, *"RT and ncRNA sequences carry pairing-compatible information beyond the
tested nuisance structure"*. It does not establish molecular binding, physical interaction,
causal co-evolution, or residue–nucleotide contact.

Three claim levels are distinguished throughout and never collapsed:

| level | statement | addressable with these data? |
|---|---|---|
| **1 · broad association** | RT and ncRNA sequence properties track retron type / lineage | yes |
| **2 · RT-specific statistical association** | knowing the *individual* RT improves prediction or scoring of its observed ncRNA beyond broad retron type | yes, with the stated power limits |
| **3 · functional compatibility / orthogonality** | an RT functions with one ncRNA and not another | **no** — requires experiment |

Level 3 is never inferred from level 1 or 2, and natural co-occurrence is never treated as
evidence of function.

> `provenance` — `launchers/LAUNCHER_03_rt_ncrna_embedding_compatibility.md` @ `89d06b1`;
> closure decision `docs/decisions/2026-09-18_embed_g2_closure.md` @ `9154972`.

## 2 · Analysis population

### 2.1 The observed-pair universe

The analysis population is the registered eligible exact-pair resource
`data/derived/rt_ncrna_exact_pairs_v1.parquet` (Stage-1 gate `dbchar_g3`), designated
**PAIR-ELIG**: **30,924 observed RT–ncRNA pairs**, **29,192 unique exact RT protein sequences**,
**16,458 unique exact oriented ncRNA sequences**, spanning **21 retron types** (covariance
models).

**Terminology, used without exception.** These 30,924 are *observed* or *natural associations* —
RT–ncRNA combinations recorded together in the mined corpus. None has been experimentally
validated as functional or compatible. A combination absent from the corpus is a **non-observed
pairing**, never an incompatible one. In retrieval, a candidate that is not the observed partner
is a **mismatched candidate** or **retrieval decoy**; in conditional modelling, an alternative RT
substituted at evaluation time is a **counterfactual conditioning control**. The words *negative
pair* and *incompatible pair* do not appear in this work.

Four nested analytical tiers are carried as pair-level views and never as the representation
population, so that no filter pre-deletes the stratum needed to keep a later test non-circular:

| tier | rule added | pairs | RTs | ncRNAs |
|---|---|---|---|---|
| T1 observed | eligible, non-redundant, Retron-labelled | 30,287 | 28,838 | 15,906 |
| T2 architecture | + same strand, not downstream, no intervening CDS, ≤ 200 bp | 25,673 | 24,677 | 13,258 |
| T3 high-confidence | + covariance-model hit E ≤ 1e-5 | 23,680 | 22,727 | 11,849 |
| T4 independently recurrent | + recurs across genomes or species | 7,476 | 7,187 | 3,829 |

**T4 is the tier where a repeated observation is a repeated biological *event* rather than
repeated *deposition***, and it is therefore the highest-independence stratum available. It is
also the smallest, which is why it is under-powered rather than uninformative.

### 2.2 ncRNA sequence reconstruction and orientation

The Stage-1 derived layer carried `nc_seq_hash` and `nc_seq_len` but no ncRNA sequence.
Sequences were reconstructed from the raw mining corpus and registered as
`data/derived/rt_ncrna_oriented_v1.{fna,parquet}`.

- **Orientation**: `dbchar_g2` defines `nc_seq_hash = sha256(sequence_oriented.upper())`, so the
  registered hash is already that of the oriented molecule. All 345,313 eligible placements carry
  `orientation_corrected = True` and zero hashes appear under conflicting orientation states.
- **Validation**: every reconstructed sequence had its sha256 recomputed and asserted equal to the
  registered hash — **16,458 / 16,458, zero mismatches**. The FASTA is self-verifying.
- File identity: `.fna` sha256 `d04297a8…`, 3,953,406 B, deterministic ordering.

This check is load-bearing rather than ceremonial: an earlier project in this lab cached 21.4 GB
of RNA embeddings computed on **unoriented** sequence, i.e. on reverse complements that do not
exist as molecules.

### 2.3 Composition and multiplicity

| | n | min | median | max | total |
|---|---|---|---|---|---|
| RT (aa) | 29,192 | 21 | 370 | 2,860 | 11,236,474 |
| ncRNA (nt) | 16,458 | 34 | 151 | 395 | 2,719,581 |

The ncRNA alphabet is `ACGKNRTY`: 214 sequences (1.30 %) carry IUPAC ambiguity codes over
4,117 nt (0.151 %), almost all `N`. RiNALMo's vocabulary covers these natively, so nothing mapped
to `<unk>` and **no substitution was applied**.

**Multiplicity shapes the entire design.** 96.85 % of RTs have exactly one observed ncRNA partner
(max 176), but only 82.28 % of ncRNAs have one RT partner, and **one ncRNA is observed with 705
different RTs**. This asymmetry is why naive in-batch negatives are biologically wrong here, why
false-candidate exclusion is mandatory, and why the split unit must be joint over both modalities.

Provenance note: the maxima (176 ncRNA partners for one RT; 705 RT partners for one ncRNA) are
read from `results/embed_g0_input_contract/tables/g0_multiplicity.tsv`; the accompanying
percentages (96.85 %, 82.28 % and their complements 3.15 %, 17.72 %) are quoted from the landed
track report `analysis/embedding_rt_ncrna/RT_NCRNA_EMBEDDING_REPORT.md` @ `4f56519`, which is a
frozen derived document rather than a bundle table. Re-derive them from the pair table before
they enter the thesis.

> `provenance` — `results/embed_g0_input_contract/` @ `fe6e1a3`; upstream
> `results/dbchar_g3_pair_geometry/` @ `2b13a9e`; registry `docs/DATASET_REGISTRY.md` §3b.

## 3 · Frozen representations

Both encoders are **frozen pretrained models**; no encoder weight was updated at any point in
this work.

| | RT | ncRNA |
|---|---|---|
| model | ESM-C 300M | RiNALMo giga-v1 |
| parameters | 332,997,184 | 650,901,793 |
| pooled dimension | 960 | 1280 |
| sequences | 29,192 | 16,458 |
| weights identity | HF `EvolutionaryScale/esmc-300m-2024-12` | `giga-v1.pt` sha256 `cd93c3f2…` |
| package / torch | esm 3.2.0 / 2.5.1+cu121 | rinalmo / 2.1.0 |
| pooled cache | 29,192 × 960 fp16 | 16,458 × 1280 fp16 |
| token cache | 11,236,474 × 960 fp16 (21 GB) | 2,719,581 × 1280 fp16 (6.6 GB) |
| truncation | none | none |

Production ran on an Ibex A100 in 8 + 5 shards. Every shard file is mode 444 with a per-file
sha256 in `manifests/<cache>.tsv`. Verification confirmed full coverage (29,192/29,192 and
16,458/16,458), exact unit totals, no gaps or duplicates, each shard the contiguous block of the
frozen (length, hash) order its position implies, and one identical frozen contract across shards.

Two facts are carried forward because they are methodological, not incidental:

1. **A100 was a correctness requirement, not a preference.** RiNALMo's frozen contract is a bf16
   autocast forward; on a GTX 1080 Ti it fails with `Current CUDA Device does not support
   bfloat16`, and silently dropping to fp16 would have produced a cache that is not the declared
   computation.
2. **ESM-C has no architectural context limit** (rotary position embeddings, no learned position
   table), so the longest RT (2,860 aa) forwards intact. Sequences beyond 2,048 aa carry an
   explicit `LEN_EXTRAPOLATED` state and are never silently pooled into a headline number.

**Token-level arrays were produced and deliberately not analysed.** Residue–nucleotide
interpretation requires msr/msd/a1/a2 and RT-domain annotations that are not independently
established in this project; the arrays are retained so that work is possible later without
recomputation. The one exception is their *reduction* to 32 mean-pooled chunks as the X1/X2
conditioning input (§6.2), which makes no positional claim.

> `provenance` — `results/embed_g1_representations/` @ `5dbd368`; Ibex namespace registered in
> `docs/DATASET_REGISTRY.md` §8.

## 4 · Leakage-aware split

This is the part of the methods that determines whether any downstream number means anything, and
it is reported at length for that reason.

### 4.1 Why pair counts are the wrong sample size

Pairs are not independent: they concentrate into relatedness components. A fold's **effective**
number of independent units is the inverse-Simpson quantity

> **n_eff = (Σᵢ sᵢ)² / Σᵢ sᵢ²**,  sᵢ = pairs in component *i*,

which equals the component count for equal-sized components and collapses toward 1 when one
dominates. The frozen test fold holds **357 components but n_eff = 14.1**. Treating its 4,638
pairs as 4,638 observations would overstate precision by more than two orders of magnitude.

### 4.2 Threshold selection, blind to any compatibility result

Twelve RT × ncRNA identity-threshold combinations were evaluated with **no embedding loaded and
no cross-modal similarity computed**. Two measurements decided the choice, neither in the original
plan:

1. **The leakage instrument must be independent of the clustering**, or it grades its own
   homework. An all-vs-all probe more sensitive than any threshold tested (mmseqs `-s 7.5
   --min-seq-id 0`; blastn `-word_size 7`) was used, plus an **exact** held-out-vs-training-only
   search. The exact search mattered: the whole-universe probe retains ≤ 300 hits per query, and
   at RT 0.30 the strict thresholds were systematically flattered (4.9 % censored vs **15.7 %**
   exact).
2. **Component count is misleading; n_eff is the quantity that bounds inference.** This overturned
   the strict-blocking candidate: RT 0.30 blocks leakage superbly and is unusable, because its
   validation fold is a *single* component.

**Strict relatedness blocking and statistical power are in direct opposition in this universe.**
That trade-off is a finding, not a nuisance, and is reported as one (Figure F1d).

### 4.3 The frozen split

| | |
|---|---|
| RT clustering | `mmseqs easy-cluster --min-seq-id 0.50 -c 0.8 --cov-mode 0` (mmseqs 18.8cc5c), **bidirectional** coverage |
| ncRNA clustering | `cd-hit-est -c 0.80 -aS 0.8 -n 8 -T 1` (CD-HIT 4.8.1), **shorter-sequence** coverage |
| split unit | connected component of the bipartite RT-cluster ↔ ncRNA-cluster graph, **indivisible** |
| fragment bridge | none (evaluated and rejected) |
| allocation | deterministic greedy to 70/15/15 by pair count; components sorted by (pairs desc, key asc); ties break train > val > test; **no RNG, no seed** |

The coverage rules differ deliberately: a protein pair aligning over 80 % of *both* sequences is
homologous along its length, whereas ncRNAs at 34–395 nt are short enough that anchoring on the
shorter member avoids discarding a genuine relative over a length difference. `-T 1` is required
because `cd-hit-est`'s multithreaded path is **not order-deterministic** — measured, not assumed.

**Why the component and not the cluster.** Splitting on RT clusters alone leaks through shared
ncRNAs (one ncRNA has 705 RT partners); splitting on ncRNA clusters leaks symmetrically. Only the
connected component of the bipartite graph is closed under both relations.

| fold | pairs | % | components | **n_eff** | T4 pairs | T4 % |
|---|---|---|---|---|---|---|
| train | 21,647 | 70.00 | 361 | 6.4 | 5,408 | 72.34 |
| validation | 4,639 | 15.00 | 357 | 14.2 | 1,077 | 14.41 |
| **test** | **4,638** | **15.00** | **357** | **14.1** | 991 | 13.26 |

The assignment is landed as an explicit table (sha256 `78a9556378d4a787…`) and never re-derived at
use time; the manifest reconstructs the split exactly (32/32 checks, 30,924/30,924 fold labels
agreeing, with a seeded-bad run confirming the verifier can fail).

### 4.4 Measured, not asserted, leakage

Held-out (= test) sequences were searched against a **training-only** database, so censoring is
impossible; training includes validation, because validation is inspected during development.

| modality | id ≥ 0.50, cov ≥ 0.50 | id ≥ 0.70, cov ≥ 0.50 | id ≥ 0.90, cov ≥ 0.30 |
|---|---|---|---|
| RT | 82.46 % | 1.28 % | **0.07 %** (3 / 4,469) |
| ncRNA | 42.63 % | 40.71 % | **9.54 %** (263 / 2,756) |

Three coverage rules give three different numbers at the same identity threshold (at id ≥ 0.50, RT
leakage is 82.46 % under `max(qcov,tcov)`, 77.0 % under query coverage, **55.2 %** under the
bidirectional rule that actually built the clusters), so **the rule is quoted with every number**.
Because all 29,192 sequences are reverse transcriptases — one protein family — *detectability* is
saturated (100 % of held-out pairs are reachable from training by some alignment) and therefore
uninformative; the identity-and-coverage tiers carry the information. Unfiltered maximum ncRNA
identity is never quoted: every held-out ncRNA has a 100 %-identity training match at < 30 %
coverage, which is a short conserved msr/msd motif, not homology.

### 4.5 Near-duplicate sensitivity population

A stratum was pre-declared — local identity ≥ 0.90 **and** aligned coverage ≥ 0.30, with
`aligned_coverage = max(query_coverage, target_coverage)` because a fragment must count whichever
way round it is — giving a frozen list of **3 RT + 263 ncRNA** sequences. Excluding whole affected
components (consistent with the component being the split unit) leaves **1,525 pairs, 284
components, n_eff 24.5**. Structural "fragment bridges" were priced and rejected: the best variant
closes the RT channel (3 → 0) but only reduces ncRNA 263 → 54 while costing **82 % of validation
independence**. The residual ncRNA near-duplicate channel is **accepted and reported, not
eliminated**, and every headline result is repeated on the excluded population.

### 4.6 Inference unit

Pairs within a component share relatedness on both modalities and are not exchangeable.
**Every interval in this work is a bootstrap over components (10,000 resamples), and every
permutation null is computed at component level.** The frozen interpretation is: *the experiment
evaluates generalization across the declared sequence-relatedness component split; it does not
establish generalization to evolutionarily unrelated RT or ncRNA sequences.*

> `provenance` — `results/embed_g2a_split_selection/` @ `fd5efc9`;
> `results/embed_g2b_frozen_split/` @ `15e00b8` (verification: `verify.sh`, 32/32).

## 5 · Shared-representation baseline (retrieval)

### 5.1 Task

**50-way retrieval**: one observed partner plus **49 retrieval decoys**, direction RT → ncRNA
primary and ncRNA → RT secondary. Chance MRR = 0.0900. Decoys are drawn under a fixed seed and the
**candidate sets are identical for every scorer**, so model comparisons are paired.

**False-candidate exclusion is mandatory**: any decoy that is an observed partner of the query RT
*anywhere in the full 30,924-pair table* is removed and redrawn — without this, a "decoy" would
frequently be a genuine observed partner, because one ncRNA is observed with 705 RTs.

### 5.2 The candidate ladder

| rung | decoys drawn from |
|---|---|
| 0F failure control | pair assignment permuted within fold; must read chance |
| 1 | uniform over ncRNAs in the fold |
| 2 | length- and GC-matched (\|Δlen\|/len ≤ 0.10, \|ΔGC\| ≤ 0.05) |
| 3 | **same retron type** (`detection_model`) — the decisive rung |
| 4 | same ncRNA identity cluster |
| 5 | ncRNAs observed with RTs in the same RT cluster |
| 6 | same `tax_species`, within one taxonomy system only |

A rung whose pool cannot supply enough independent components is reported **UNDETERMINED**, never
silently replaced by an easier pool and never reported as a null.

### 5.3 Scorers

Trivial baselines were run **first**, by design, and are reported beside every embedding number:
`B-pop` (ncRNA training frequency), `B-len`, `B-gc`, `B-kmer` (ridge RT-dipeptide → ncRNA-4-mer
cosine; the strongest trivial baseline) and `B-model` (retron type predicted from the RT
embedding — the label shortcut). An RT-only score is constant across candidates and therefore
exactly chance, which is why the informative RT-only baseline is the type shortcut.

**M-CCA** is regularized canonical correlation analysis by symmetric whitening: `Cxx`, `Cyy` ridge-
regularized by `α·trace(C)/dim` (dimensionless, hence comparable across the 960-d and 1280-d
spaces), then SVD of the whitened cross-covariance; the score is cosine in the shared space. It
was **fit on training components only**, selected on validation over a deliberately small grid
(`k ∈ {16,32,64} × α ∈ {1e-2,1e-1,1}`) by the single pre-declared rule *maximise validation rung-1
MRR*, giving `k = 32, α = 0.01`. **The test fold was opened once**, after that selection was
frozen.

CCA was chosen ahead of any higher-capacity model because it is the lowest-capacity probe that
can express "a linear subspace of the protein space aligns with a linear subspace of the RNA
space": closed form, two interpretable hyperparameters, per-dimension diagnostics readable against
retron type — and because a model with millions of parameters cannot be honestly assessed against
n_eff ≈ 14 independent test units.

> `provenance` — `results/embed_g2_frozen_baseline/` @ `2c9127b` (PREREG.md in-bundle);
> descriptive atlas `results/embed_g2c_atlas/` @ `9154972`.

## 6 · Conditional RNA modelling (X1)

### 6.1 Question and arms

> Does conditioning an RNA sequence model on the **specific retron RT representation** improve
> prediction of the observed ncRNA beyond RNA sequence regularities and **retron-type information
> alone**?

The primary comparison is **R vs T**, declared before any model existed — not R vs U, which would
only re-establish level 1.

| arm | conditioning | total params | shared decoder | conditioning path |
|---|---|---|---|---|
| **U** RNA-only | one learned constant vector | 665,483 | 665,355 | 128 |
| **T** type-conditioned | learned embedding of 21 retron types | 668,043 | 665,355 | 2,688 |
| **R** RT-conditioned | frozen ESM-C of the observed RT | 788,363 | 665,355 | 123,008 |

**The decoder is byte-identical across arms**; only the conditioning input path differs.

### 6.2 Architecture and conditioning representation

The model is *adapted, not reimplemented*, from the vendored Profluent `grna-modeling` release:
`transformer.py` (sha256 `c1f2112b…`) supplies `EncoderLayer` and `CrossDecoderLayer` and is
imported read-only at a pinned hash; `gRNAModel.py` is **not** used, because its batch plumbing
requires the unpublished `profluent.*` namespace.

```
conditioning → Linear(d_in→128) → 1 bidirectional EncoderLayer
             → 3 × CrossDecoderLayer (causal RNA self-attention + cross-attention, RoPE)
             → LayerNorm → LM head over 11 tokens
d_s 128 · 8 heads · dropout 0.1
```

RT conditioning uses the verified per-residue ESM-C cache reduced to **K = 32 equal-width
mean-pooled chunks** (declared in the pre-registration before any model existed), giving (32, 960)
per RT; one RT of 29,192 is shorter than K and carries masked-out empty chunks. **ESM-C was not
fine-tuned.** The vocabulary `<pad> <bos> <eos> A C G T K N R Y` keeps the four IUPAC codes present
in the corpus as tokens — they are not substituted and not filtered, and **no sequence was removed
from any fold at any point**.

### 6.3 Training and the one validation-selected quantity

AdamW, lr 2e-4, 4,000-step warmup, weight decay 0, accumulation 2, batch 32, fp32, seed 20260918,
≤ 40 epochs. Validation was used for **exactly one thing**: selecting the lowest-validation-NLL
checkpoint (patience 5), applied identically to each arm. **The test fold was opened once**,
afterwards.

### 6.4 Evaluation

Per-sequence NLL → **per-component token-weighted mean** → paired per-component difference →
bootstrap over components (10,000 resamples). Pair count is never the inferential sample size.
Results are repeated on the frozen near-duplicate-excluded population and reported descriptively
by tier T1–T4.

**Same-type counterfactual conditioning control** (evaluation only; sampling rule fixed in the
pre-registration): **M = 8** alternative RTs drawn uniformly without replacement from the same
retron type in the test fold, excluding the observed RT and any RT observed with that ncRNA; a
type needs ≥ 9 distinct test RTs. The reported quantity is
`Δ log P per nt = NLL(ncRNA | alternative RT) − NLL(ncRNA | observed RT)`, positive favouring the
observed RT. **These alternatives are controls, not biological negatives**, and are never used as
training labels.

### 6.5 Compute gate

Before the full run: loader correctness; **no component leakage** (train∩val, train∩test, val∩test
all empty); masking correctness; **conditioning provably reaches the decoder**; determinism on
identical batches; parameter budget; loss decrease.

One gate finding is methodologically important and is reported in the thesis rather than buried:
the vendored layers **zero-initialise their residual output projections**, so at step 0 the
cross-attention branch contributes exactly zero and no gradient reaches the conditioning
projection. An init-time "is conditioning wired up?" check therefore returns a **false negative**.
The check was moved to after 30 optimizer steps (|grad| = 3.9; perturbing the RT changes the loss
by 9e-2). Without it, arm R could have been arm U with unused parameters, and R ≈ T would have
been reported as a finding.

> `provenance` — `results/embed_x1_conditional_pilot/` @ `8bf7207` (PREREG.md in-bundle).

## 7 · Cross-fitted confirmation (X2) — **specified, result pending**

X2 is **running**. Its design, counterfactual rules and cross-fit manifest were frozen before any
X2 number existed, so the methods below are stable and writable now; **no X2 result is anticipated
anywhere in this workbench.**

- **Cross-fitting**: 5 folds over the same connected components used by `embed_g2`, whole
  components assigned deterministically (largest component to the currently smallest fold, no RNG,
  never optimised against R−T). For fold *k*: test = *k*, validation = (*k*+1) mod 5, train = the
  remaining three. Verified by assertion that no component, RT cluster or ncRNA cluster crosses
  train/val/test in any fold, and that each of the 1,075 components is evaluated out-of-fold
  exactly once. Manifest sha256 `65228b34…`.
- **Prospective power statement, made before the result**: cross-fitting raises T4 coverage from
  83 to 247 components, but n_eff moves from **9.0 to 8.6** — it does not improve. n_eff is a
  property of the component-size distribution, not of the number of folds. **Cross-fitting buys
  coverage and robustness, not power**; if T4 remains unresolved that is predicted in advance and
  is an X2-D outcome for that stratum, not evidence of absence.
- **Arms**: U, T, R as in X1, plus **G** (conditioning on the ESM-C representation of the frozen
  `rt_id0.50` cluster **representative** — coarse RT lineage) and **P** (conditioning on a
  **permuted** RT during training only, with validation and test conditioning on the true RT — a
  falsification control). G uses the representative's frozen embedding rather than a learned
  cluster embedding because components never share RT clusters across folds, so a learned table
  would be untrained for every evaluation cluster.
- **Counterfactual tiers**, increasing in stringency, all evaluation-only and all requiring the
  alternative RT to lie in the **same cross-fit fold** as the query (so novelty is not confounded
  with specificity): **C1** same retron type; **C2** C1 + RT length within 10 %; **C3** C1 + the 8
  nearest admissible RTs by cosine on the frozen pooled ESM-C representation; **C4** the same
  frozen `rt_id0.50` homolog cluster. A tier spanning fewer than **30 independent components** is
  reported `UNDETERMINED`.
- **Architecture and hyperparameters are imported unchanged from X1.** No architecture tuning, no
  added capacity, no contrastive term, no hyperparameter search.
- **Outcome gate frozen in advance**: X2-A (RT-specific signal confirmed, requiring all five
  conditions including that P materially weakens the effect and that G does not explain it);
  X2-B (population/lineage signal only); X2-C (not replicated); X2-D (under-powered — absence of
  significance is not converted into absence of signal).

> `provenance` — `ARIS_OUTPUT/embed_x2_confirmation/DESIGN.md` and `COUNTERFACTUAL_RULES.md`
> (frozen pre-result; scratch and uncommitted at the time of writing, 2026-09-19).

## 8 · Statistical conventions

- **Inference unit**: the relatedness component, everywhere. Intervals are percentile bootstraps
  over components (10,000 resamples, seed 20260918); permutation nulls are component-level.
- **Reported alongside every effect**: the number of components, n_eff, and the fraction of
  components favouring the compared arm — because a mean shift with 65 % of components favouring
  one arm is a different statement from a uniform gain.
- **Ties**: retrieval metrics are reported under both the pre-registered pessimistic convention and
  the standard expected-rank convention; no conclusion depends on which is used.
- **Under-support**: any stratum or rung without sufficient independent components is reported
  `UNDETERMINED`, never as a null.
- **Negative and null results are retained and reported** at the same prominence as positive ones.

## 9 · Software, data and reproducibility

| | |
|---|---|
| local environment | `/home/borg/miniconda3/envs/retron_tradicional` (numpy 1.26.4, pandas 3.0.2, matplotlib 3.10.5) |
| Ibex environment | `/ibex/user/rioszemm/conda-environments/retron_tradicional` |
| clustering | mmseqs 18.8cc5c; CD-HIT 4.8.1 (`-T 1`) |
| encoders | ESM-C 300M (esm 3.2.0); RiNALMo giga-v1 (torch 2.1.0) |
| conditional model | adapted from vendored Profluent `grna-modeling` `transformer.py` @ sha256 `c1f2112b…`, imported read-only |
| seeds | 20260918 throughout (decoys, training, bootstrap) |
| split assignment | `results/embed_g2b_frozen_split/tables/split_assignment.tsv.gz`, sha256 `78a9556378d4a787…` |

Every figure in this workbench renders from frozen tables or from the verified derived table, with
no model or embedding code in the path (`scripts/f_figures.py`). The derived table is produced and
checked by `scripts/r01_x1_component_table.py`, which fails rather than writes if any of its 46
checks disagrees with the frozen bundle.

## 10 · Ethics of interpretation (statements this work does not make)

- No claim of **co-evolution**: that requires phylogenetic congruence against a shared-ancestry
  null, and this design has neither phylogeny nor such a null.
- No claim of **physical binding** or **residue–nucleotide contact**: sequence representations
  cannot supply either, and the msr/msd/a1/a2 and RT-domain annotations that would be needed are
  not independently established in this project.
- No claim of **biochemical compatibility or incompatibility**: non-observed pairings are
  non-observed, and corpus absence reflects sampling and covariance-model detection limits (every
  ncRNA call in the corpus has `nc_source = 'infernal'`).
- No generated ncRNA is claimed to be functional, and none is ranked as biologically compatible.
- Any future pairing score is a **predicted pairing / cross-reactivity score** until experimentally
  validated.
