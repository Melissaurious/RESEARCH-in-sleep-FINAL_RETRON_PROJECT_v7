# embed_x1 — RT-conditioned ncRNA generation pilot · PRE-REGISTRATION

**Written before any model was built, any loss computed, or any metric read.**

> This is a **new exploratory task**, not `embed_g3` and not a continuation of the closed
> partner-specific escalation gate. `results/embed_g2_frozen_baseline/` (commit `2c9127b`)
> remains **CLOSED** and is neither reopened nor reinterpreted here.

## Question

> Does conditioning an RNA sequence model on the **specific retron RT representation** improve
> prediction of the observed ncRNA beyond RNA sequence regularities and **retron-type information
> alone**?

The primary comparison is **R versus T**, not R versus U.

## Terminology (binding)

observed / natural pair · candidate partner · mismatched candidate · **counterfactual same-type
conditioning control** · non-observed pairing. Mismatched RT–ncRNA combinations are **never**
used as biological negatives, and none is used as a training label.

## Binding split — inherited unchanged

`results/embed_g2b_frozen_split/` (commit `15e00b8`). Component definitions, train/val/test
membership, relatedness thresholds, the near-duplicate sensitivity population and the
**component-level inference unit** are all immutable here. Train uses train components only.
Validation is used only for the predeclared stopping rule below. **Test is opened once**, after
the final configuration is fixed.

train 21,647 · val 4,639 · test 4,638 pairs · test n_eff **14.1** · sensitivity population
1,525 pairs / n_eff 24.5.

## Inputs, declared prospectively

**RT conditioning representation.** Frozen ESM-C 300M, **not fine-tuned**. The per-residue cache
(21.6 GB, `embed_g1`, verified) is reduced to a fixed-width conditioning array of
**K = 32 equal-width mean-pooled chunks** of the per-residue representation, giving
`(32, 960)` per RT.

*Declared rationale, before any result*: the full per-residue cache is 21.6 GB and transfers at
~12 MB/s from Ibex, so the reduction is computed **on Ibex from the verified cache** and only the
1.8 GB derived array is moved. 32 chunks preserves regional (N→C) structure for cross-attention
while keeping the conditioning array tractable for a 0.5–1.0 M-parameter decoder. RTs shorter
than 32 residues are chunked with empty chunks masked out. Full-token conditioning is recorded
as a future variant and is **not** run here.

**RNA target.** The canonical oriented ncRNA population `data/derived/rt_ncrna_oriented_v1.fna`
(16,458 sequences, hash-verified 16,458/16,458).

**Vocabulary, declared prospectively:** `A C G T` + `N R Y K` (the four IUPAC codes actually
present in the corpus) + `<bos> <eos> <pad>`. 11 tokens. IUPAC characters are **kept as tokens**,
not substituted and not filtered. Loss is masked at `<pad>` and at `<bos>`. **No sequence is
removed from any fold for any reason, at any point.** In particular nothing is removed after
looking at model performance.

## Model family — fixed, no architecture search

One OpenCRISPR-inspired conditional decoder, **adapted** from the vendored Profluent
`grna-modeling` release rather than reimplemented (see §0 audit): `transformer.py`
sha256 `c1f2112b4b91e8424b173d49da43e7ff14fc1ec0bf39ddc0e419147a2b90af3f`, whose
`EncoderLayer` and `CrossDecoderLayer` are self-contained (only `torch` + `einops`). The broken
`profluent.*` batch plumbing in `gRNAModel.py` is **not** used.

```
conditioning source → Linear(d_in → d_s)
                    → 1 bidirectional EncoderLayer (lightweight conditioning layer)
                    → 3 × CrossDecoderLayer  (causal RNA self-attention + cross-attention)
                    → LM head over 11 tokens
```

`d_s = 128`, `d_hidden = 256`, `n_heads = 8`, `n_dec_layers = 3`, `n_enc_layers = 1`, dropout 0.1
— the released checkpoint's shape, which lands in the declared 0.5–1.0 M budget. **Exact
parameter counts are reported per arm.**

## The three arms — identical decoder, conditioning differs only at the input

| arm | conditioning source | what it tests |
|---|---|---|
| **U** | a single **learned constant** vector (no RT, no type) | ncRNA grammar with no protein information |
| **T** | a learned embedding of the **retron-type label** (21 types) | level-1 system/type organization |
| **R** | the frozen ESM-C RT conditioning array (32 × 960) | **the primary exploratory model** |

The decoder, its parameter count and all hyperparameters are **identical** across arms; only the
conditioning input path differs, which is unavoidable and is reported exactly. No fourth
high-capacity model is trained.

## Training and the stopping rule — declared now

AdamW, lr 2e-4, 4,000-step linear warmup, weight decay 0, gradient accumulation 2, batch 32,
fp32, seed 20260918 — the released checkpoint's schedule where applicable.

**Stopping rule:** train up to 40 epochs; select the checkpoint with the **lowest validation
per-nucleotide NLL**, patience 5 epochs. This is the **only** use of validation. Applied
identically and independently to each arm. No other quantity is selected on validation.

## Primary metric

Held-out **per-nucleotide negative log-likelihood** (natural log) and perplexity, computed per
sequence, then aggregated **at the frozen component level**. Point estimate = mean over
components; 95 % CI = bootstrap over components, 10,000 resamples. **Pair count is not the
inferential sample size.**

Reported: **U vs T**, **U vs R**, and the primary **T vs R**, each as a paired per-component
difference with a bootstrap CI.

## Same-type counterfactual conditioning control — sampling rule declared now

Evaluation only; **never trained on**. For each eligible held-out observed pair
(RT_A → ncRNA_A), draw **M = 8** alternative RT representations uniformly without replacement
from RTs of the **same retron type** in the **test fold**, excluding RT_A itself and excluding
any RT that is an observed partner of ncRNA_A. A pair is **eligible** if its type has ≥ 9
distinct test RTs; ineligible pairs are reported as such, not dropped silently.

Report the distribution of

> Δ log P = log P(ncRNA_A | observed RT_A) − log P(ncRNA_A | same-type alternative RT)

per nucleotide, with component-level uncertainty. These alternatives are **counterfactual
same-type conditioning controls**, not biological negatives or incompatible pairs.

## Additional controls

Descriptive stratification by T1/T2/T3/T4, retron type, ncRNA length and RT length where sample
size permits. **Small strata are descriptive only and are never converted into confirmatory
tests.** The primary R-vs-T comparison is repeated on the frozen near-duplicate-excluded
sensitivity population.

## Generation analysis — only after likelihoods are frozen

Sample from U, T and R for a bounded representative RT set. Descriptive only: length, GC,
nucleotide and k-mer composition, novelty against training ncRNAs, gross structural plausibility
if inexpensive, and retron-type consistency. **No claim of function. No ranking of generated RNA
as biologically compatible.**

## Outcomes, stated prospectively

- **Outcome A — R ≈ T.** Specific RT conditioning gives no detectable improvement beyond retron
  type under this population and design. The measurable signal remains predominantly type-level.
- **Outcome B — R > T, but the advantage disappears in the near-duplicate sensitivity set or is
  concentrated in a few components.** Suggestive, not robust.
- **Outcome C — R > T with component-level support, surviving the sensitivity population, and
  observed-RT conditioning outperforming same-type counterfactual conditioning.** Preliminary
  evidence that specific RT representations carry information predictive of their observed ncRNA
  beyond retron type.

**Outcome C is not proof of co-evolution, physical interaction or biochemical compatibility.**

## Relationship to OpenCRISPR

Architectural precedent only; **no OpenCRISPR sequence is used**. Inherited: frozen protein-LM
conditioning, a lightweight trainable conditioning layer, an autoregressive RNA decoder, causal
self-attention, protein→RNA cross-attention, and a next-token objective.

**The critical difference**: this experiment includes a **retron-type-conditioned baseline (T)**
and a **component-aware relatedness split**, because `embed_g2` demonstrated strong retron-type
shared structure that a type-agnostic design would silently absorb.

## Stop condition

This is a single exploratory pilot. **No InfoNCE, symmetric cosine contrastive loss, dual
encoder or other model family is started after seeing the result.**
