# Cross-modal information in frozen RT and ncRNA sequence representations

**Retron reverse transcriptase ↔ retron ncRNA · embedding track (`embed`) · closed 2026-09-18**

| | |
|---|---|
| binding split | `results/embed_g2b_frozen_split/` · commit `15e00b8` |
| confirmatory result | `results/embed_g2_frozen_baseline/` · commit `2c9127b` |
| descriptive atlas | `results/embed_g2c_atlas/` · commit `9154972` |
| decision record | `docs/decisions/2026-09-18_embed_g2_closure.md` |
| claim tested | `C6` in `idea-stage/docs/research_contract.md` |

All numbers below are read from those frozen artifacts. Nothing was re-run for this report and
no model was trained to produce it.

---

## 1 · Biological motivation

The question the track was built to answer:

> **Do naturally associated retron RT and ncRNA sequences contain cross-modal sequence
> information that distinguishes their observed association beyond trivial sequence
> composition, relatedness, retron type and dataset structure?**

A retron is a tripartite element: a reverse transcriptase, a non-coding RNA (msr/msd) that the
RT uses as template and primer, and usually an effector. The RT and its ncRNA are functionally
interdependent, which makes it reasonable to ask whether that interdependence has left a
detectable signature in the two sequences — one readable by protein and RNA language models
that never saw the pairing.

**This is explicitly not a test of any of the following**, and no result here should be read as
bearing on them:

| not tested | why not |
|---|---|
| **co-evolution** | requires phylogenetic congruence with a null for shared ancestry; this design has no phylogeny and no such null |
| **physical binding** | requires biochemical or structural evidence; sequence representations cannot supply it |
| **biochemical compatibility** | requires experimental assay of function for a given RT–ncRNA combination |
| **residue–nucleotide contacts** | requires per-token analysis against independently established msr/msd and RT-domain annotations, which do not yet exist in this project |

The identifiable question is narrower and is the one actually addressed: given an RT, can a
frozen-representation model distinguish the ncRNA it is observed with from controlled
alternatives?

---

## 2 · Pair population

Source: the registered eligible exact-pair resource
`data/derived/rt_ncrna_exact_pairs_v1.parquet` (Stage-1 gate `dbchar_g3`), designated
**PAIR-ELIG**.

| quantity | value |
|---|---|
| **observed RT–ncRNA pairs** | **30,924** |
| unique exact RT sequences | **29,192** |
| unique exact oriented ncRNA sequences | **16,458** |
| retron types (covariance models) | 21 |

### Terminology

These 30,924 are **observed / natural associations** — RT–ncRNA combinations recorded together
in the mined corpus. They are **not** "positive examples" in the biological sense: none has been
experimentally validated as a functional or compatible pair. Equally, a combination absent from
the corpus is a **non-observed pairing**, not an incompatible one.

### Nested analytical tiers

| tier | rule added | pairs | RTs | ncRNAs |
|---|---|---|---|---|
| T1 observed | eligible, non-redundant, Retron-labelled | 30,287 | 28,838 | 15,906 |
| T2 architecture | + same strand, not downstream, no intervening CDS, ≤ 200 bp | 25,673 | 24,677 | 13,258 |
| T3 high-confidence | + covariance-model hit E ≤ 1e-5 | 23,680 | 22,727 | 11,849 |
| T4 independently recurrent | + recurs across genomes or species | 7,476 | 7,187 | 3,829 |

PAIR-ELIG is a **strict superset** of every tier (`T1 \ PAIR-ELIG = 0`); the 637-pair excess
decomposes exactly as 497 de-duplication-removed pairs + 140 non-Retron-file-label canonical
pairs. Tiers are carried as pair-level views, never as the representation population — filtering
to T3 at representation time would have been irreversible and would have pre-deleted the
architecture-independent tier needed to keep any test of architecture non-circular.

### ncRNA orientation and sequence validation

The Stage-1 derived layer carried `nc_seq_hash` and `nc_seq_len` but **no ncRNA sequence**. The
sequences were reconstructed for this track and registered as
`data/derived/rt_ncrna_oriented_v1.{fna,parquet}` (`docs/DATASET_REGISTRY.md` §3b).

- **Orientation**: `dbchar_g2` defined `nc_seq_hash = sha256(sequence_oriented.upper())`
  (`e01_extract.py:294`), so the registered hash is already the hash of the **oriented**
  sequence. All 345,313 eligible placements carry `orientation_corrected = True`, and **zero**
  hashes appear under conflicting orientation states. This matters: an earlier project cached
  21.4 GB of RNA embeddings computed on **unoriented** sequence, i.e. on reverse complements
  that do not exist as molecules.
- **Validation**: every reconstructed sequence had its sha256 recomputed and asserted equal to
  the registered hash. **16,458 / 16,458 verified, zero mismatches.** The FASTA is therefore
  self-verifying — it cannot silently hold the wrong molecule, the wrong strand, or a sequence
  from the wrong record.
- File identity: `.fna` sha256 `d04297a8…`, 3,953,406 B; deterministic (`sorted(nc_seq_hash)`).

### Length and composition

| | n | min | median | max | total |
|---|---|---|---|---|---|
| RT (aa) | 29,192 | 21 | 370 | 2,860 | 11,236,474 |
| ncRNA (nt) | 16,458 | 34 | 151 | 395 | 2,719,581 |

ncRNA alphabet `ACGKNRTY`: 214 sequences (1.30 %) carry IUPAC ambiguity codes over 4,117 nt
(0.151 %), almost all `N`. RiNALMo's vocabulary covers R/Y/K/M/S/W/B/D/H/V/N natively, so
nothing mapped to `<unk>` and no substitution was applied.

**Multiplicity, which shapes the whole design**: 96.85 % of RTs have exactly one observed ncRNA
partner (max 176), but only 82.28 % of ncRNAs have one RT partner and **one ncRNA is observed
with 705 different RTs**. That asymmetry is why naive in-batch negatives are biologically wrong
here and why false-candidate exclusion (§5) is mandatory.

---

## 3 · Embedding generation

Both encoders are **frozen pretrained models**; no weights were updated at any point in this
track.

| | RT | ncRNA |
|---|---|---|
| model | **ESM-C 300M** | **RiNALMo giga-v1** |
| parameters | 332,997,184 | 650,901,793 |
| pooled dimension | **960** | **1280** |
| sequences | **29,192** | **16,458** |
| weights identity | HF `EvolutionaryScale/esmc-300m-2024-12` | `giga-v1.pt`, sha256 `cd93c3f21eb3e767373c9491192686b5846247bd1110693e453c1dd0f321c0db` |
| package / torch | esm 3.2.0 / 2.5.1+cu121 | rinalmo / 2.1.0 |
| pooled cache | 29,192 × 960 fp16 | 16,458 × 1280 fp16 |
| token cache | 11,236,474 × 960 fp16 = **21 GB** | 2,719,581 × 1280 fp16 = **6.6 GB** |
| truncation | **none** | **none** |

Production ran on Ibex A100 (`gpu102-02`), 8 + 5 shards, ~1 min per shard. Persistent home
`/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings/`, registered in
`docs/DATASET_REGISTRY.md` §8. Every shard file is mode 444 with per-file sha256 in
`manifests/<cache>.tsv`.

**Verification**: 29,192/29,192 and 16,458/16,458 sequences covered, unit totals exact, no gap,
no duplicate, each shard the contiguous block of the frozen order its position implies, and a
single identical frozen contract across all shards.

Two implementation facts worth carrying forward:

1. **A100 was a correctness requirement, not a preference.** The first Ibex submission was
   routed to a GTX 1080 Ti; ESM-C ran there (16× slower) but RiNALMo died on
   `Current CUDA Device does not support bfloat16`. RiNALMo's frozen contract is a bf16 autocast
   forward, so falling back to fp16 would have produced a cache that is not the declared
   computation. **A100 is the only bf16-capable GPU on that cluster.**
2. **ESM-C has no architectural context limit** — rotary position embeddings, no learned
   position table — so the longest RT (2,860 aa) forwards intact. Sequences above 2,048 aa carry
   an explicit `LEN_EXTRAPOLATED` state and are never silently pooled into a headline number.

### Token-level representations: retained, unused

Per-residue and per-nucleotide arrays exist on Ibex and were deliberately **not opened** in this
baseline. Residue–nucleotide interpretation requires msr/msd/a1/a2 and RT-domain annotations
that are not independently established in this project; using token arrays before those exist
would invite reading structure into noise. They are retained so that work is possible later
without recomputation.

### Why pooled frozen embeddings first

A deliberate low-capacity first pass, for four reasons:

1. **It asks what is already there.** If pairing information is present in the pretrained
   representations, a linear probe should find some of it. If a linear probe finds nothing, a
   high-capacity model finding something is more likely to have learned nuisance structure.
2. **The effective sample size is small.** The confirmatory test fold carries **n_eff = 14.1**
   independent components (§4). A model with millions of parameters evaluated against ~14
   independent units cannot be assessed honestly.
3. **It is interpretable.** Canonical correlations and per-dimension associations can be read
   directly against retron type, length and GC (§10). A contrastive encoder's latent space
   cannot.
4. **It sets a floor for escalation.** A higher-capacity model is only worth running if the
   simple probe has established that the signal is not already explained by trivial structure.
   That is exactly the test that decided the outcome.

---

## 4 · Relatedness and split design

This section is long because the split, not the model, is what determines whether any result
means anything. Two RTs at 99 % identity in train and test would make retrieval trivial.

### 4.1 Why raw pair counts were misleading

The obvious reading of "30,924 pairs, hold out 15 %" gives 4,638 test pairs and suggests a
comfortable sample. It is wrong, and the correction is the central methodological result of the
track.

The pairs are not independent. They concentrate into relatedness components, and a fold's
**effective** number of independent units is

> **n_eff = (Σᵢ sᵢ)² / Σᵢ sᵢ²**  (inverse Simpson; sᵢ = pairs in component i)

which equals the component count when components are equal-sized and collapses toward 1 when one
dominates. The frozen test fold has **357 components but n_eff = 14.1**. Treating 4,638 pairs as
4,638 observations would overstate precision by more than two orders of magnitude.

### 4.2 The threshold investigation

Twelve RT × ncRNA identity-threshold combinations were evaluated **blind to any compatibility
result** — no embedding was loaded and no cross-modal similarity computed while thresholds were
being chosen (`results/embed_g2a_split_selection/`).

| RT id | nc id | components | giant | giant share | test n_eff | val n_eff | RT leak ≥0.5 |
|---|---|---|---|---|---|---|---|
| 0.30 | 0.80 | 156 | 27,572 | 89.2 % | 1.3 | 1.3 | — |
| 0.30 | 0.95 | 242 | 20,918 | 67.6 % | **4.0** | **1.0** | **1.7 %** |
| **0.50** | **0.80** | **1,075** | **5,711** | **18.5 %** | **14.1** | **14.2** | **55.2 %** |
| 0.50 | 0.90 | 1,242 | 5,561 | 18.0 % | 18.2 | 18.0 | 50.9 % |
| 0.70 | 0.90 | 5,859 | 822 | 2.7 % | 631 | 631 | 89.4 % |
| 0.90 | 0.95 | 9,533 | 783 | 2.5 % | 1,895 | 1,895 | — |

The trade-off is stark and unavoidable: **strict relatedness blocking and statistical power are
in direct opposition in this universe.** RT 0.30 blocks leakage superbly (1.7 % of held-out RTs
have a ≥0.50-identity training relative under the clustering's own coverage rule) and is
**unusable** — its validation fold is a *single* component (n_eff 1.0) and its test fold has
n_eff 4.0. RT 0.70 and above gives hundreds of effective units and ~90 % leakage, which would
make "held-out" almost meaningless.

Two measurements decided it, neither of which was in the original plan:

1. **The leakage instrument had to be independent of the clustering**, or it grades its own
   homework. An all-vs-all probe more sensitive than any threshold tested (mmseqs `-s 7.5
   --min-seq-id 0`, 8.71 M hits; blastn `-word_size 7`, 2.76 M hits) plus an **exact**
   held-out-vs-training-only search. The exact search mattered: the whole-universe probe keeps
   ≤300 hits per query, and at RT 0.30 **75–82 % of held-out RTs never reached a training
   sequence in the retained list**, so their leakage was a lower bound that systematically
   flattered the strict thresholds (4.9 % censored vs **15.7 %** exact).
2. **Component count is misleading; n_eff is the quantity that bounds inference.** This
   overturned the strict-blocking candidate.

### 4.3 The frozen split

| | |
|---|---|
| RT clustering | `mmseqs easy-cluster --min-seq-id 0.50 -c 0.8 --cov-mode 0` (mmseqs 18.8cc5c) |
| ncRNA clustering | `cd-hit-est -c 0.80 -aS 0.8 -n 8 -T 1` (CD-HIT 4.8.1) |
| RT coverage | **bidirectional** — both sequences ≥ 80 % covered |
| ncRNA coverage | **shorter-sequence** — shorter member ≥ 80 % aligned |
| split unit | **connected component of the bipartite RT-cluster ↔ ncRNA-cluster graph**, indivisible |
| fragment bridge | **none** (§4.6) |

The coverage rules differ deliberately: a protein pair aligning over 80 % of *both* is homologous
along its length, while ncRNAs at 34–395 nt are short enough that anchoring on the shorter member
avoids discarding a genuine relative over a length difference. `-T 1` because `cd-hit-est`'s
multithreaded path is **not order-deterministic** — measured, not assumed: a first rerun moved
component counts by up to 3 in ~6,000 before this was pinned.

**Why the component and not the cluster.** Splitting on RT clusters alone leaks through shared
ncRNAs (one ncRNA has 705 RT partners); splitting on ncRNA clusters leaks symmetrically. Only the
connected component of the bipartite graph is closed under both relations.

### 4.4 Deterministic allocation

Target 70/15/15 by pair count. Components sorted by (pairs desc, key asc); each assigned to the
fold with the largest remaining pair deficit; exact ties break train > val > test.
**No random seed, no RNG, no shuffling** — the assignment is a pure function of the component
sizes and keys.

| fold | pairs | % | components | **n_eff** | unique RT | unique ncRNA | T1 | T2 | T3 | T4 | T4 % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| train | 21,647 | 70.00 | 361 | 6.4 | — | — | 21,214 | 18,032 | 16,754 | 5,408 | 72.34 |
| validation | 4,639 | 15.00 | 357 | 14.2 | — | — | 4,499 | 3,719 | 3,496 | 1,077 | 14.41 |
| **test** | **4,638** | **15.00** | **357** | **14.1** | 4,469 | 2,756 | 4,574 | 3,922 | 3,430 | **991** | **13.26** |

Assignment sha256 (uncompressed) `78a9556378d4a7871a566fe914d3b7b7d52924b20149104339f8c1f62c77d376`.
The manifest was verified to reconstruct the exact split: **32/32 checks, 30,924/30,924 fold
labels agreeing**, with a seeded-bad run confirming the verifier can fail.

### 4.5 Measured leakage

Instrument independent of the clustering and more sensitive than it; held-out searched against a
**training-only** database so censoring is impossible. Held-out = test; training = train **+
validation**, because validation is inspected during development.

| modality | id ≥ 0.50, cov ≥ 0.50 | id ≥ 0.70, cov ≥ 0.50 | id ≥ 0.90, cov ≥ 0.30 |
|---|---|---|---|
| RT | 3,685 / 4,469 = 82.46 % | 57 / 4,469 = 1.28 % | **3 / 4,469 = 0.07 %** |
| ncRNA | 1,175 / 2,756 = 42.63 % | 1,122 / 2,756 = 40.71 % | **263 / 2,756 = 9.54 %** |

Three different coverage rules give three different numbers for the same identity threshold, and
the rule must always be quoted: at identity ≥ 0.50, RT leakage is **82.46 %** under
`max(qcov,tcov) ≥ 0.50`, **77.0 %** under query-coverage ≥ 0.50, and **55.2 %** under the
**bidirectional** rule that actually built the clusters.

- Held-out pairs reachable from training via either modality: **4,638 / 4,638 = 100 %**
- Held-out components with no detectable relationship to training: **0 / 357 = 0 %**

Both follow from all 29,192 sequences being reverse transcriptases — one protein family — so
*detectability* is saturated and uninformative. The identity-and-coverage tiers carry the
information.

⚠️ **Never quote unfiltered maximum ncRNA identity.** Every held-out ncRNA has a 100 %-identity
training match at < 30 % coverage: short conserved msr/msd motifs, not homology. The unfiltered
statistic is saturated at 1.0.

### 4.6 Near-duplicate sensitivity stratum, and why fragment bridges were rejected

The 80 % coverage requirement lets a near-identical **fragment** of a training sequence form its
own cluster and cross into the held-out fold. That channel was measured and priced.

A predeclared stratum was frozen: **local identity ≥ 0.90 AND aligned coverage ≥ 0.30**, with
**`aligned_coverage = max(query_coverage, target_coverage)`** — `max()` because a fragment must
count whichever way round it is; `min()` would miss both a short held-out sequence contained in a
long training one and the reverse. The stratum is a concrete frozen list of **3 RT + 263 ncRNA**
sequences. Excluding whole affected components (consistent with the component being the split
unit) leaves **1,525 pairs, 284 components, n_eff 24.5, T4 3.20 %**.

Structural remedies ("fragment bridges" merging near-identical sequences before splitting) were
evaluated and **rejected**:

| bridge | components | largest | train/val/test | test n_eff | val n_eff |
|---|---|---|---|---|---|
| **none (adopted)** | 1,075 | 18.5 % | 21,647 / 4,639 / 4,638 | **14.1** | **14.2** |
| id ≥ 0.90, cov ≥ 0.30 | 882 | 21.8 % | 21,647 / 4,639 / 4,638 | 13.3 | **2.6** |
| id ≥ 0.70, cov ≥ 0.50 | 480 | 34.1 % | 21,457 / 5,018 / 4,449 | 7.1 | **1.0** |
| id ≥ 0.50, cov ≥ 0.50 | 137 | 94.3 % | 29,163 / 881 / 880 | 1.6 | 1.2 |

Four reasons: (i) the motivating concern does not hold on the protein side — 3 of 4,469 held-out
RTs; (ii) the best variant was **verified, not assumed**, and closes the RT channel completely
(3 → 0) but only reduces ncRNA 263 → 54, because bridges come from a probe capped at 300 hits per
query; (iii) it costs **82 % of validation independence**; (iv) a surgical quarantine of the 73
affected test components was also priced and rejected (test → 1,525 pairs, T4 → 3.20 %).

**The ncRNA near-duplicate channel is accepted and reported, not eliminated.**

### 4.7 Why confirmatory inference is component-level

Pairs within a component share relatedness on both modalities and are not exchangeable. Every
interval in this report is a **bootstrap over components** (10,000 resamples), never over pairs,
and the permutation null is computed at component level. **n_eff = 14.1, not 4,638.**

### 4.8 Frozen interpretation

> The experiment evaluates generalization across the declared sequence-relatedness component
> split. It does not establish generalization to evolutionarily unrelated RT or ncRNA sequences.

---

## 5 · Retrieval task and terminology

### Terminology, used consistently

| term | meaning |
|---|---|
| **observed partner** | the ncRNA recorded with this RT in the corpus |
| **candidate partner** | any ncRNA offered to the model in a candidate set |
| **mismatched candidate** | a candidate that is not the observed partner |
| **retrieval decoy** | a mismatched candidate placed in a candidate set |
| **non-observed pairing** | an RT–ncRNA combination not seen in the corpus |
| **type-matched decoy** | a retrieval decoy sharing the query's retron type |

**A mismatched candidate is not an experimentally validated negative and not an incompatible
pair.** Non-observed RT–ncRNA combinations may well be biologically compatible; the corpus
records what was found, not what is possible. The retrieval task tests only whether the
**observed** association can be distinguished from controlled alternatives.

### Task definition

- **50-way retrieval**: 1 observed partner + **49 retrieval decoys**. Direction RT → ncRNA is
  primary; ncRNA → RT reported as secondary.
- **Chance MRR = 0.0900** (= (1/50)·Σ₁..₅₀ 1/i).
- **False-candidate exclusion**: any decoy that is an observed partner of the query RT
  *anywhere in the full 30,924-pair table* is removed and redrawn. Necessary because one ncRNA is
  observed with 705 RTs; without this, a "decoy" would frequently be a genuine observed partner.
- Decoys seeded (`PCG64(20260918)`), **identical candidate sets for every model**, so model
  comparisons are paired.
- Rungs report `UNDETERMINED` where the pool cannot supply enough independent components, rather
  than silently falling back to an easier pool.

### The candidate ladder

| rung | decoys drawn from |
|---|---|
| 0F failure control | pair assignment permuted within fold; must read chance |
| 1 | uniform over ncRNAs in the fold |
| 2 | length- and GC-matched (\|Δlen\|/len ≤ 0.10, \|ΔGC\| ≤ 0.05) |
| 3 | **same retron type** (`detection_model`) |
| 4 | same ncRNA identity cluster |
| 5 | ncRNAs observed with RTs in the same RT cluster |
| 6 | same `tax_species`, within one taxonomy system only |

---

## 6 · Models and baselines

All scorers see the identical candidate sets. Trivial baselines were run **first**, by design.

| id | scores a candidate by | role |
|---|---|---|
| `B-pop` | the candidate ncRNA's training frequency | **ncRNA-only marginal** |
| `B-len` | −\|len_nc − ridge(len_rt)\| | length |
| `B-gc` | −\|gc_nc − ridge(len_rt)\| | composition |
| `B-kmer` | cosine(ridge RT-dipeptide → ncRNA-4-mer, candidate 4-mer) | composition, **strongest trivial** |
| `B-model` | P(candidate's retron type \| RT embedding), multinomial logistic | **RT-only marginal / label shortcut** |
| `M-CCA` | cosine in a shared latent space from regularized CCA | **cross-modal compatibility probe** |

An RT-only score is constant across candidates and therefore exactly chance; the informative
RT-only baseline is the retron-type label shortcut, which is what `B-model` implements.

### M-CCA

Regularized CCA by symmetric whitening: `Cxx`, `Cyy` ridge-regularized by `α·trace(C)/dim`
(dimensionless, comparable across the 960-d and 1280-d spaces), then SVD of the whitened
cross-covariance. Score = cosine in the shared space.

- **Fit on training components only** (21,647 pairs).
- **Validation-selected grid**: `k ∈ {16, 32, 64} × α ∈ {1e-2, 1e-1, 1}` — 9 configurations, by
  the single predeclared rule *maximise validation rung-1 MRR*. Avoiding a broad search was
  deliberate given n_eff ≈ 14.
- **Selected `k = 32`, `α = 0.01`** (validation rung-1 MRR 0.4773).
- **Test opened once**, after that selection was frozen. No quantity was tuned afterwards.

### Why CCA before a contrastive model

CCA is the lowest-capacity cross-modal probe that can express "a linear subspace of the protein
space aligns with a linear subspace of the RNA space". It has a closed-form solution, no training
dynamics, two interpretable hyperparameters, and per-dimension diagnostics that can be read
against retron type and composition. A higher-capacity model would have been evaluated against
~14 independent units with no way to attribute its performance. The pre-registration made
escalation conditional on CCA clearing the trivial baselines — which is precisely the test that
decided the outcome.

---

## 7 · Primary quantitative results

Test fold, 4,638 pairs / 357 components, n_eff 14.1. Chance MRR 0.0900. Intervals are
component-level bootstraps.

### The ladder

| rung | matched on | `B-kmer` | **`M-CCA`** | 95 % CI | top-1 | top-5 | components | status |
|---|---|---|---|---|---|---|---|---|
| 1 | nothing (random) | 0.2265 | **0.4407** | [0.4039, 0.4772] | 0.1714 | 0.5164 | 357 | reported |
| 2 | length + GC | 0.1418 | **0.2262** | [0.1972, 0.2565] | 0.0457 | 0.1916 | 316 | reported |
| 3 | **retron type** | 0.1534 | **0.1832** | [0.1550, 0.2126] | 0.0299 | 0.1524 | 299 | reported |
| 4 | ncRNA cluster | 0.0764 | 0.0925 | degenerate | 0.0064 | 0.1314 | **1** | **UNDETERMINED** |
| 5 | RT cluster | 0.1050 | 0.0992 | [0.0867, 0.1127] | 0.0234 | 0.1299 | **10** | **UNDETERMINED** |
| 6 | species | 0.1111 | 0.2982 | [0.1904, 0.4262] | 0.0504 | 0.2605 | **22** | **UNDETERMINED** |

Other trivial baselines at rung 1: `B-len` 0.0669, `B-gc` 0.0697, `B-pop` 0.0200, `B-model`
0.0200. `B-pop` and `B-model` fall below chance as an artefact of tie-heavy scores under the
pre-registered pessimistic tie convention; under the standard expected-rank convention they move
to 0.0392, still below chance, and **no conclusion changes**. Both conventions are reported for
every cell.

### Reverse-direction retrieval

ncRNA → RT, random candidates: MRR **0.4738** [0.4380, 0.5104], top-1 0.1828. The effect is not
an artefact of direction.

### Permutation failure control (rung 0F)

Observed **0.4407** against null mean **0.0901** [0.0781, 0.1040] over 2,000 permutations,
**p = 0.0005**. The rung-1 effect is not a scoring artefact.

### Near-duplicate sensitivity

Frozen 1,525-pair / 284-component population: rung 1 **0.4329** [0.3910, 0.4751] — a change of
−0.008 from the full test fold. **The result is not driven by the residual near-duplicate
channel.**

### Strata (descriptive)

T1 0.4588 [0.4210, 0.4962] · T2 0.4912 [0.4477, 0.5332] · T3 0.5263 [0.4768, 0.5746] ·
T4 0.4732 [0.4053, 0.5437]. All intervals overlap; no stratum is distinguishable from another.

### The key comparison: M-CCA minus the k-mer baseline

Paired per-component difference, bootstrapped. The pre-registered rule required the difference
to exceed the 95 % CI half-width.

| rung | difference | 95 % CI | verdict |
|---|---|---|---|
| 1 random | **+0.2142** | [+0.1737, +0.2537] | **supported improvement** |
| 2 length + GC | **+0.0844** | [+0.0503, +0.1187] | **supported improvement** |
| 3 **retron type** | **+0.0298** | **[−0.0048, +0.0633]** | **not statistically distinguishable** |
| 4, 5, 6 | — | — | **UNDETERMINED** (1, 10, 22 components) |

⚠️ **Absence of a significant difference at rung 3 is not proof of equivalence.** The interval
[−0.0048, +0.0633] is consistent with a true difference of zero and also with a true improvement
of up to +0.063. With n_eff ≈ 14 this test has limited power, and the honest statement is that
the data do not distinguish the two.

---

## 8 · Embedding atlas and figures

All figures regenerate deterministically from the plotting tables via
`results/embed_g2c_atlas/scripts/a06_figures.py` alone — no embedding or model code re-runs.
Copies for this report live in `analysis/embedding_rt_ncrna/figures/`.

### Figure 1 — RT embedding atlas
`figures/fig1_rt_atlas.png` · data `results/embed_g2c_atlas/plotdata/atlas_rt.tsv` · script
`a05_atlas.py` (compute) + `a06_figures.py` (render)

> UMAP of frozen pooled ESM-C 300M representations for 8,000 RT sequences sampled from the pair
> universe, coloured by (a) retron type, (b) T1–T4 tier, (c) RT length, (d) major NCBI species.
> Grey = types outside the legend. **Descriptive only.**

### Figure 2 — ncRNA embedding atlas
`figures/fig2_ncrna_atlas.png` · data `plotdata/atlas_ncrna.tsv`

> UMAP of frozen pooled RiNALMo giga-v1 representations for 8,000 ncRNA sequences, coloured by
> (a) associated retron type, (b) T1–T4 tier, (c) ncRNA length, (d) major NCBI species.
> **Descriptive only.**

### Figure 3 — Shared CCA-space atlas
`figures/fig3_shared_cca_atlas.png` · data `plotdata/atlas_shared_cca.tsv`

> RT (circles, ESM-C) and ncRNA (triangles, RiNALMo) projected into the shared CCA latent space
> (k = 32, α = 0.01, fit on training components) and laid out by UMAP; 1,200 observed pairs
> sampled from the test fold. Colour = retron type. Right panel joins observed partners with
> light segments for a readable 150-pair subset. **Descriptive only** — a 30 k-segment rendering
> would be uninterpretable and is deliberately not produced.

### Figure 4 — Similarity, retrieval and neighbourhood
`figures/fig4_similarity_retrieval.png` · data `plotdata/similarity_long.tsv`,
`tables/g2a_neighbourhood.json`, `results/embed_g2_frozen_baseline/tables/g2_test_ladder.tsv`

> (a) Cross-modal cosine similarity for observed pairs and three decoy classes — **descriptive**.
> (b) Retrieval MRR across the candidate ladder with component-level 95 % CIs, chance line, and
> rungs 4–6 marked UNDETERMINED — **inferential**, and the panel that carries the result.
> (c) Neighbourhood composition in the open 2,756-candidate pool — **descriptive**.

### Figure 5 — Canonical dimensions and type encoding
`figures/fig5_cca_dimensions.png` · data `tables/g2a_cca_dimensions.tsv`,
`tables/g2a_type_encoding.tsv`

> (a) Canonical correlations across all 32 retained dimensions with cumulative share.
> (b) η² of retron type per dimension, separately for the RT and ncRNA sides.
> (c) Retron-type probe accuracy per modality against the majority-class rate.
> (a) and (b) **descriptive**; (c) is a probe fit on train and reported on test — explanatory,
> **not** an escalation gate.

### PCA variance

RT PC1–2 explain **69.1 %**; ncRNA PC1–2 explain **49.7 %**
(`tables/g2a_pca_variance_{rt,ncrna}.tsv`).

### On UMAP

**UMAP is visualization only.** It is a non-linear, non-distance-preserving projection whose
apparent clusters, gaps and relative sizes are artefacts of its hyperparameters as much as of the
data. No claim in this report rests on a UMAP panel. Discrete-looking islands are **not** evidence
of discrete biological classes.

---

## 9 · Shared-space organization

### Cross-modal similarity (descriptive)

| population | mean cosine | sd-pooled Cohen's *d* vs observed |
|---|---|---|
| **observed pair** | **+0.3771** | — |
| type-matched candidate | +0.3217 | **0.248** |
| length + GC-matched candidate | +0.2803 | 0.420 |
| random candidate | +0.0872 | **1.364** |

The separation between observed pairs and candidates **shrinks monotonically as candidates are
matched more closely on retron type**.

### Neighbourhood analysis

Open pool of **2,756** candidate ncRNAs (all distinct ncRNAs in the test fold), shared CCA space:

| quantity | value |
|---|---|
| observed partner is the nearest cross-modal neighbour | **0.56 %** |
| observed partner in top-5 / top-10 / top-20 | 2.63 % / 4.51 % / 7.91 % |
| **median rank of the observed partner** | **238** of 2,756 |
| nearest neighbour shares the query's retron type | **51.92 %** |
| top-5 / top-10 neighbours share retron type | 51.16 % / 50.03 % |
| retron-type prevalence in the pool | 9.40 % |
| **enrichment over prevalence** | **5.32×** |

### Conservative interpretation

> Local organization in the shared CCA space is substantially type-associated rather than
> demonstrably pair-specific.

The shared space places an RT among ncRNAs of its own retron type at 5.3× the background rate,
while the specific observed partner sits at median rank 238. Whatever the space encodes, it is
much more informative about *which kind of retron system* this is than about *which individual
ncRNA* this RT was observed with.

---

## 10 · Canonical dimensions and retron type

`tables/g2a_cca_dimensions.tsv`. Canonical correlations run **0.987 → 0.774** across the 32
retained dimensions.

| | dim 1 |
|---|---|
| canonical correlation | **0.9865** |
| η² of retron type, RT side | **0.809** |
| η² of retron type, ncRNA side | **0.724** |

The leading canonical dimension is **largely retron type**: retron-type membership accounts for
81 % of its variance on the protein side and 72 % on the RNA side. Correlation is spread rather
than concentrated — the top 5 dimensions carry **17.3 %** of the summed canonical correlation,
consistent with 32 dimensions of broadly similar strength rather than a few dominant axes.

### Modality-specific retron-type encoding

Multinomial logistic probe on frozen pooled embeddings, **fit on training components, reported on
test components**, 21 classes, majority-class rate **0.2693**:

| modality | test accuracy | above majority |
|---|---|---|
| ESM-C RT embeddings | **0.4978** | +0.229 |
| RiNALMo ncRNA embeddings | **0.6557** | +0.386 |

**Both modalities independently carry retron-type information.** This matters for interpretation:
it supplies a plausible and sufficient route by which *any* cross-modal alignment method — CCA
here, a contrastive encoder later — could align the two spaces and score observed pairs highly
**without learning anything about individual partner compatibility**. If an RT can be assigned to
a retron type from its own embedding, and an ncRNA likewise, then a model that simply maps both
onto a shared type axis will retrieve well against random and composition-matched candidates and
poorly against type-matched ones — which is exactly the pattern observed in §7.

This is an explanatory observation, not a demonstration that type is the *only* route.

---

## 11 · Main scientific interpretation

> **Frozen ESM-C and RiNALMo representations contain substantial shared structure associated with
> naturally occurring RT–ncRNA systems. This supports strong retrieval against random and
> length/GC-controlled candidate sets. However, the present experiment does not establish
> individual partner-specific compatibility beyond retron-type-associated structure: when
> candidate ncRNAs are restricted by retron type, the M-CCA improvement over the k-mer baseline
> is no longer statistically distinguishable.**

Stated explicitly, because each is a distinct and easily-confused claim:

1. **This does not prove that retron type explains all observed signal.** Rung 3 shows an absence
   of a *distinguishable* difference, not a demonstration of equivalence. The 95 % interval
   [−0.0048, +0.0633] admits a real improvement of up to +0.063.
2. **Rungs 4–6 are absence of sufficient measurement, not measured absence.** Their candidate
   pools draw on 1, 10 and 22 independent components — far below what component-level
   confirmatory inference requires. They are reported `UNDETERMINED` everywhere, including in
   Figure 4.
3. **Level 1 — shared RT–ncRNA organization at retron-type / system-class level — has evidence.**
   Strong retrieval against random (MRR 0.4407 vs 0.0900 chance, permutation p = 0.0005), 5.3×
   type enrichment in cross-modal neighbourhoods, and η² of type ≈ 0.8 on the leading canonical
   dimension all point the same way.
4. **Level 2 — individual RT–ncRNA partner specificity within that organization — is not
   established.** The observed partner is the nearest cross-modal neighbour for 0.56 % of queries
   at median rank 238/2,756, and the type-matched comparison does not separate the cross-modal
   probe from a k-mer baseline.

---

## B · Why contrastive escalation stopped

**No InfoNCE model, symmetric cosine contrastive model, dual encoder or cross-attention model was
trained after the `embed_g2` result.** None was started.

The pre-registered escalation condition (`LAUNCHER_03` §7) was that `embed_g2` beat **every**
trivial baseline on the held-out split by the declared margin. It does not: at rung 3 the
advantage over `B-kmer` is +0.0298, 95 % CI [−0.0048, +0.0633].

### The scientific concern

A high-capacity contrastive model trained with arbitrary mismatched candidates has a much easier
route to a high score than partner compatibility. §10 measured that route directly: retron type
is recoverable from each modality alone (0.498 / 0.656 against a 0.269 majority). A dual encoder
optimising InfoNCE over in-batch negatives would be rewarded for discovering exactly this,
because in a random batch the type-matched candidates are rare. It would then report excellent
retrieval while having learned system-class recognition — and with n_eff ≈ 14 independent test
units, there would be no way to tell the two apart after the fact.

This is not hypothetical in this project. An independent line of work
(`/home/borg/openCRISPR_for_retrons/`, §E) trained a protein-conditioned RNA generator on
retrons, ran leave-one-family-out evaluation, and reached the same conclusion from the other
direction: *"the model does FAMILY RECOGNITION, not partner recognition"*, with a row-matched
control attributing **78 % of the leave-one-family-out gap to family identity** and only 22 % to
training volume. Its contrastive arm raised the metric it optimised 43-fold while **degrading**
the rank statistic (row 2AFC 0.9532 → 0.9072, t = −21).

### The status of the decision

> **`NOT YET JUSTIFIED AS A CONFIRMATORY PARTNER-SPECIFIC TEST`** — not `METHOD REJECTED`.

InfoNCE, symmetric cosine contrastive learning, dual encoders and cross-attention compatibility
scoring are **preserved as future candidate methods**. Nothing measured here says they cannot
work; what was measured is that the current population cannot tell whether they worked. The
constraint is the evaluation, not the architecture.

---

## C · Within-type feasibility

Full table: `results/embed_g2c_atlas/tables/g2a_within_type_feasibility.tsv`; reading:
`results/embed_g2c_atlas/DOWNSTREAM_DECISION_NOTE.md`. **Audit only — nothing was trained.**

A within-type experiment restricts candidates to one retron type, removing type-associated
structure **by construction** rather than relying on it being controlled away afterwards. That
makes it the natural design for level 2.

Declared criteria, applied uniformly: `C1` usable candidate pool ≥ 50 · `C2` ≥ 30 relatedness
components · `C3` n_eff ≥ 10 · `C4` ≥ 100 T3 pairs. All four required.

**21 retron types evaluated. Two pass: `TypeIIIA3` and `TypeIB1`.**

| type | pairs | uniq RT | uniq ncRNA | components | **n_eff** | test comps | **test n_eff** | T3 | T4 | feasible |
|---|---|---|---|---|---|---|---|---|---|---|
| **TypeIIIA3** | 1,082 | 1,036 | 736 | 87 | **10.9** | 31 | **3.7** | 945 | 255 | **yes** |
| **TypeIB1** | 815 | 760 | 574 | 41 | **11.1** | 13 | **4.6** | 540 | 211 | **yes** |
| TypeIC1_IC2 | 6,277 | 6,139 | 2,034 | 144 | 1.2 | 42 | 9.2 | 5,319 | 2,012 | no (C3) |
| Ec107_like | 4,555 | 4,170 | 2,023 | 55 | 1.6 | 21 | 1.2 | 4,173 | 1,281 | no (C3) |
| OutgroupA | 4,359 | 4,302 | 3,319 | 230 | 1.6 | 82 | 20.1 | 3,597 | 964 | no (C3) |
| TypeIA_IIAI | 3,922 | 3,368 | 2,109 | 157 | 1.8 | 48 | 4.9 | 1,590 | 657 | no (C3) |

Combined feasible: **1,897 pairs, 128 components, 1,485 T3, 466 T4.**

**The blocking criterion for 19 of 21 types is `C3`, effective independent components.** Raw pair
counts are actively misleading: `TypeIC1_IC2` has **6,277 pairs but n_eff 1.2**; `Ec107_like` has
**4,555 pairs but n_eff 1.6**. Within a type, pairs collapse into a handful of relatedness
components.

**And the caveat that matters most**: even the two feasible types are feasible *overall*, not
*confirmatorily*. Under the frozen split their **test-fold** n_eff are **3.7** and **4.6** — a
held-out within-type readout would rest on roughly four independent units, below what `embed_g2`
already used and far below what would make a null result interpretable.

> **The current binding constraint for a confirmatory within-type compatibility test is
> independent relatedness components, not model capacity or raw pair count.**

### Connection to future data expansion

This is a data-acquisition and population-design problem. It would be materially changed by:

- **more genomes and loci that add independent components**, not merely more pairs from the same
  lineages;
- **recovery of currently missed ncRNAs.** The corpus's ncRNA calls come entirely from covariance
  models (`nc_source = 'infernal'` for every call). Retron ncRNAs that no existing CM detects are
  invisible to this population by construction — and those are disproportionately likely to sit
  in *divergent* lineages, i.e. exactly the ones that would add independent components rather
  than deepen existing ones. **Any advance in ncRNA recovery beyond CM-based approaches should
  trigger re-running this feasibility audit** (`a07_within_type_feasibility.py`), because it
  could change the answer for several types at once.

---

## D · OpenCRISPR as a methodological precedent

**Expanded into a standalone bounded comparison: `OPENCRISPR_METHOD_COMPARISON.md`.**
Architectural and methodological precedent only — not evidence for or against the retron
hypothesis, and OpenCRISPR performance is **not** used as a benchmark against the CCA result.
The biological tasks and validation endpoints differ.

### What could and could not be established

The published methods could **not** be read from this environment (Nature 303-redirects to
authentication; bioRxiv returns HTTP 429; Europe PMC 403). The comparison is therefore built on
the **released code and checkpoint**, which are locally available and were read directly, and
every item that could not be verified is recorded as *not determinable from available material*
— **never** as *not done*. In particular, **no absence of homology control is inferred from
silence.**

### Reconstructed from the released artifacts (high confidence)

| element | value |
|---|---|
| protein encoder | ESM2 `esm2_t6_8M_UR50D`, `d_s_protein = 320` |
| frozen? | **yes, by construction** — ESM2 is never instantiated inside the module; `forward` consumes a precomputed `protein_embs` tensor, so no gradient path exists |
| conditioning | `Linear(320 → 128)` + **1 bidirectional self-attention encoder layer**, 8 heads |
| decoder | **3 layers**, each RNA causal self-attention + **cross-attention to the protein**, 8 heads, `d_s = 128` |
| trainable parameters | **705,930** |
| objective | next-token cross-entropy on the RNA, padding and sentinels masked |
| optimizer | lr 2e-4, warmup 4,000, weight decay 0, `acc_batches` 2 |
| vocabulary | 10 tokens `a c g t 1 2 3 4 - _`; `1`/`2` bracket tracrRNA, `3`/`4` crRNA — **one protein conditioning two linked RNA segments, which maps directly onto retron msr/msd** |
| train/validation | a split existed: 3,120 train vs 388 validation batches per epoch (≈ 88.9 % / 11.1 %), 40 epochs, 62,400 optimizer steps. **No test-loop state in the checkpoint**; batch size unrecorded, so dataset size is not recoverable |
| negatives | **none in the released objective** — no contrastive or mismatch term anywhere in `forward` |

### Not determinable from available material

Training-set composition and size, the split *construction rule*, protein-side and RNA-side
homology control, whether grouping was joint, family composition across folds, evaluation
metrics, and whether generated gRNAs were validated independently of the protein. The checkpoint
*filename* carries the token `id90`, which is consistent with a 90 %-identity step, but nothing
inside the checkpoint corroborates it and a filename is not a method.

### The structural point that holds regardless

A protein-side identity control, at any threshold, does not by construction prevent RNA-side
family information from crossing a split boundary — the two are jointly controlled only if the
grouping is joint. In retron data that is not theoretical: **one ncRNA is observed with 705
distinct RTs** (and 17.72 % of ncRNAs have more than one RT partner), so a protein-only split
places near-identical RNAs on both sides.

**And the endpoint decides how much the split must carry.** A wet-lab functional endpoint
tolerates training-set homology — if a designed editor cuts DNA in cells, leakage cannot explain
the phenotype. A retrieval or partner-specificity endpoint does not, because leakage inflates the
statistic directly. This is why the two designs should not be scored against one another.

### Transfer verdict

**Transfers largely intact**: the frozen protein language-model encoder, the lightweight
trainable conditioning layer, the autoregressive RNA decoder with causal self-attention, the
cross-attention from decoder to protein representation, the two-segment sentinel vocabulary, and
the ~0.7 M-parameter budget.

**Cannot transfer without redesign**: split construction, definition of mismatched candidates,
evaluation of individual partner specificity, handling of multiple valid ncRNAs per RT or type
(3.15 % of RTs have >1 observed partner, max 176), and homology-aware inference.

A proposed non-executed architecture and its seven prerequisites are in
`OPENCRISPR_METHOD_COMPARISON.md` §6–§7.

## E · Historical model-work audit

See `HISTORICAL_MODEL_ASSET_AUDIT.md` for the full asset-by-asset table with paths, hashes,
architectures, splits, losses, negative construction, leakage control and reuse classification.

**Headline: substantial InfoNCE and protein-conditioned cross-attention infrastructure already
exists and does not need reimplementation.** Three prior lines of work are relevant, and **none
of them supersedes the frozen `embed_g2` result** — they are recorded as precedent and as
reusable engineering.

---

## G · Future triggers for reopening the modelling track

Explicit conditions. Any one is necessary; (2) or (5) is close to sufficient.

1. **Materially more RT–ncRNA associations** — a larger observed-pair universe.
2. **Especially more independent within-retron-type components** — the binding constraint. More
   pairs from the same lineages does not help.
3. **Recovery of ncRNAs missed by existing annotation / covariance-model approaches**, which
   would disproportionately add divergent, independent associations.
4. **Independent evidence allowing a harder compatibility evaluation** — biochemical,
   structural, or functional data that turns some non-observed pairings into assayed
   incompatible ones, which would convert the retrieval task into a genuine classification task
   with biologically meaningful negatives.
5. **A prospectively designed within-type split with sufficient component-level test support**
   — designed before any model is fit, with a declared minimum test n_eff.

Future candidate approaches, preserved and not authorised:

- regularized or deep CCA;
- InfoNCE dual encoders;
- symmetric cosine contrastive loss;
- cross-attention compatibility scoring;
- positive-pair alignment objectives;
- RT-conditioned autoregressive ncRNA generation in the OpenCRISPR mould.

**These are future hypotheses, not authorised current runs.**

---

## Appendix · Provenance summary

| artifact | commit | sha256 / identity |
|---|---|---|
| oriented ncRNA FASTA | `fe6e1a3` | `d04297a823e249061a320897233afac581bbfb0bf26b33942f5c0f6630258e35` |
| RT pair-universe FASTA | `fe6e1a3` | `db87de172ceff9df29bb635df13803500f73b9463c31e4926d7281d7f1b6cd2a` |
| frozen split assignment | `15e00b8` | `78a9556378d4a7871a566fe914d3b7b7d52924b20149104339f8c1f62c77d376` |
| near-duplicate stratum | `15e00b8` | `ebfa25e2421928859c14c20ff9662d284877f19b3a58340ca2399c6919e31d00` |
| RiNALMo weights | — | `cd93c3f21eb3e767373c9491192686b5846247bd1110693e453c1dd0f321c0db` |
| ESM-C weights | — | HF `EvolutionaryScale/esmc-300m-2024-12` |
| embedding caches | `2c9127b` | `manifests/{esmc300m_v1,rinalmo_giga_v1}.tsv` on Ibex |

Verification: `bash results/embed_g2b_frozen_split/verify.sh` — seeded-bad rejected, 32/32 passed.
