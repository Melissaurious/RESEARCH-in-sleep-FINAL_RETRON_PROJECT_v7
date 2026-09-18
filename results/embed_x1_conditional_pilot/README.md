# embed_x1 — RT-conditioned ncRNA generation pilot

> **Separate namespace. The frozen `embed_g2` bundles were not modified and are not reopened or
> reinterpreted.** This is a **new exploratory task**, not `embed_g3` and not a continuation of
> the closed partner-specific escalation gate.

Pre-registration: `PREREG.md`, written before any model was built or any metric read.
Split: `results/embed_g2b_frozen_split/` (commit `15e00b8`), consumed unchanged and verified.

## Question

> Does conditioning an RNA sequence model on the **specific retron RT representation** improve
> prediction of the observed ncRNA beyond RNA sequence regularities and **retron-type
> information alone**?

Primary comparison **R vs T**, not R vs U.

## Result: **Outcome C**, at a small effect size

All three prospectively-stated conditions for Outcome C are met.

| | |
|---|---|
| R beats T with component-level support | **ΔNLL = −0.01778** [−0.02428, −0.01052] nats/nt, 65.0 % of 355 components favour R |
| survives the frozen sensitivity population | **−0.01809** [−0.02530, −0.00992] — essentially unchanged |
| observed-RT beats same-type counterfactual | **Δ log P = +0.013512/nt** [+0.006820, +0.018813], 71.0 % of pairs favour the observed RT |

> **Preliminary evidence that specific RT sequence representations contain information
> predictive of their observed ncRNA beyond retron type.**
>
> This is **not** proof of co-evolution, physical interaction or biochemical compatibility.

## Models

Adapted — not reimplemented — from the vendored Profluent `grna-modeling` release.
`transformer.py` (sha256 `c1f2112b4b91e8424b173d49da43e7ff14fc1ec0bf39ddc0e419147a2b90af3f`) is
self-contained and supplies `EncoderLayer` and `CrossDecoderLayer`; it is imported **read-only**
at a pinned hash. `gRNAModel.py` is **not** used — its batch plumbing needs the unpublished
`profluent.*` namespace.

```
conditioning → Linear(d_in→128) → 1 bidirectional EncoderLayer
             → 3 × CrossDecoderLayer (causal RNA self-attn + cross-attn to conditioning, RoPE)
             → LayerNorm → LM head over 11 tokens
d_s 128 · d_hidden 16 (per head) · 8 heads · dropout 0.1
```

| arm | conditioning | total params | shared decoder | conditioning path |
|---|---|---|---|---|
| **U** RNA-only | one learned constant vector | 665,483 | **665,355** | 128 |
| **T** type-conditioned | learned embedding of 21 retron types | 668,043 | **665,355** | 2,688 |
| **R** RT-conditioned | frozen ESM-C 300M, 32×960 chunks → Linear | 788,363 | **665,355** | 123,008 |

The **decoder is byte-identical across arms**; only the conditioning input path differs, which
is unavoidable and is reported exactly. All three sit inside the declared 0.5–1.0 M budget.

**RT conditioning representation**: the verified per-residue ESM-C cache reduced on Ibex to
K = 32 equal-width mean-pooled chunks (declared in PREREG before any model existed), giving
(32, 960) per RT; 1 RT of 29,192 is shorter than K and has masked-out empty chunks.
`rt_chunks.npy` sha256 `740dd0596732db3038e483037ea743f11bd3d46a9525cb8b8edcbb292da50b4f`,
verified identical after transfer. **ESM-C was not fine-tuned.**

**Vocabulary** (declared prospectively): `<pad> <bos> <eos> A C G T K N R Y` — the four IUPAC
codes present in the corpus are **kept as tokens**, not substituted and not filtered.
**No sequence was removed from any fold at any point.**

## Training and the one validation-selected quantity

AdamW, lr 2e-4, 4,000-step warmup, wd 0, accum 2, batch 32, fp32, seed 20260918, max 40 epochs.
Validation was used for **exactly one thing**: selecting the lowest-validation-NLL checkpoint
(patience 5), applied identically to each arm. **Test opened once**, afterwards.

| arm | best epoch | val NLL | note |
|---|---|---|---|
| U | 0 | 1.41268 | overfits immediately — train NLL falls 1.469→1.212 while validation rises |
| T | 15 | 1.39220 | |
| R | 12 | 1.38878 | |

## Held-out results (test fold, 4,638 pairs / 357 components, n_eff 14.1)

| arm | test NLL (component mean) | 95 % CI | perplexity |
|---|---|---|---|
| U | 1.41097 | [1.40847, 1.41347] | 4.0999 |
| T | 1.37513 | [1.36748, 1.38273] | 3.9556 |
| **R** | **1.35734** | [1.34787, 1.36710] | **3.8859** |

Paired per-component differences (negative = first arm better):

| comparison | Δ | 95 % CI | components favouring first arm |
|---|---|---|---|
| T − U | −0.03585 | [−0.04262, −0.02924] | 80.7 % |
| R − U | −0.05363 | [−0.06224, −0.04454] | 82.9 % |
| **R − T** | **−0.01778** | **[−0.02428, −0.01052]** | **65.0 %** |

**Component-level throughout**: per-sequence NLL → per-component token-weighted mean → bootstrap
over components (10,000 resamples). Pair count is never the inferential sample size.

## Same-type counterfactual conditioning control (evaluation only)

Sampling rule fixed in PREREG before the result was read: **M = 8** alternative RTs drawn
uniformly without replacement from the **same retron type in the test fold**, excluding the
observed RT and any RT observed with that ncRNA; a type needs ≥ 9 distinct test RTs.
**4,630 / 4,638 pairs eligible (99.8 %)**; the 8 ineligible are reported, not dropped silently.

> Δ log P per nt = **+0.013512** [+0.006820, +0.018813] over **355 components**
> **71.0 %** of pairs favour their observed RT.

These alternatives are **counterfactual same-type conditioning controls** — *not* biological
negatives, *not* incompatible pairs, and never used as training labels.

## Strata (descriptive only, never confirmatory)

| stratum | n | R − T | 95 % CI | components |
|---|---|---|---|---|
| T1 | 4,574 | −0.02070 | [−0.02744, −0.01359] | 339 |
| T2 | 3,922 | −0.02298 | [−0.02904, −0.01720] | 265 |
| T3 | 3,430 | −0.02168 | [−0.02854, −0.01502] | 200 |
| **T4** | 991 | **−0.00776** | **[−0.01761, +0.00169]** | 83 |

⚠️ **T4 — the independently recurrent tier — does not show the effect.** Its interval includes
zero. This is descriptive and under-powered (83 components), and is **not** converted into a
confirmatory test, but it is the single most important caveat on Outcome C: the tier in which a
repeated observation is a repeated *event* is the one where the advantage is not resolved.

## Generation analysis (descriptive; run only after likelihoods were frozen)

200 test RTs × 4 samples, temperature 1.0.

| arm | median length | GC | 3-mer JSD vs real test | median MFE |
|---|---|---|---|---|
| U | 122 | 0.483 | 0.02812 | −24.75 |
| T | 155 | 0.485 | **0.00256** | −39.40 |
| R | 178 | 0.464 | 0.00428 | −42.65 |
| **real test ncRNA** | **156** | **0.485** | 0 | **−58.70** |

Between arms (3-mer JSD): R vs T **0.00262**, R vs U 0.02782, T vs U 0.02651.

**Read conservatively.** Type conditioning transforms generation realism (U→T reduces JSD ~11×);
**RT conditioning does not further improve marginal composition** — R's JSD vs real (0.00428) is
slightly *worse* than T's (0.00256), and R over-generates length (178 vs 156). So the likelihood
advantage of R does **not** show up as a better marginal sequence distribution. All arms produce
markedly less structured RNA than real ncRNA (MFE −25/−39/−43 vs −58.7). The 100 % "novelty" is
an artefact of temperature-1.0 sampling and carries no biological meaning.

**No generated RNA is claimed to be functional, and none is ranked as biologically compatible.**

## Compute gate (all passed before the full run)

Data loader correctness · **no component leakage** (train∩val, train∩test, val∩test all empty) ·
masking correctness (target count = len−1; loss invariant to appended padding) · **RT
conditioning provably reaches the decoder** · determinism on identical batches · parameter budget
· loss decreases. Measured 1.57 ms/pair/epoch → ~23 min per arm on one RTX 4090; the run stayed
on the workstation and needed no Ibex escalation.

> **A finding from the gate worth carrying forward.** The vendored layers zero-initialise their
> residual output projections (`AttentionLayer.linear_out`, `Transition.linear_3`), so at step 0
> the cross-attention branch contributes **exactly zero** and no gradient reaches the
> conditioning projection. An init-time "is conditioning wired up?" check therefore returns a
> **false negative**. The check was moved to after 30 optimizer steps, where |grad| = 3.9 and
> perturbing the RT changes the loss by 9e-2. Had this not been checked, arm R could have been
> arm U with unused parameters and R ≈ T would have been reported as a finding.

## Claims supported

- Conditioning on the specific RT representation gives a **small but component-level-supported**
  improvement in held-out ncRNA likelihood over conditioning on retron type alone
  (−0.018 nats/nt, ~1.3 % relative), which survives the frozen near-duplicate sensitivity
  population.
- Conditioning on the **observed** RT gives higher likelihood than conditioning on same-type
  alternative RTs (+0.0135 nats/nt, 71 % of pairs).
- Retron-type conditioning itself gives a larger improvement over no conditioning (−0.036) than
  RT conditioning gives over type conditioning (−0.018): **type remains the dominant signal.**

## Claims NOT supported

- **Not** co-evolution, physical interaction, binding, or biochemical compatibility.
- **Not** that mismatched or non-observed RT–ncRNA combinations are incompatible — they are
  non-observed, nothing more.
- **Not** that generated ncRNAs are functional or rankable by compatibility.
- **Not** established in T4, the independently recurrent tier (interval includes zero).
- **Not** a reopening or reinterpretation of `embed_g2`, whose retrieval result stands unchanged.
- **Not** a per-pair claim: 4,638 test pairs carry n_eff 14.1.

## Reproducing

```bash
python scripts/x02_dataset.py       # frozen split -> dataset.npz
python scripts/x05_smoke.py         # the compute gate; must pass before training
python scripts/x04_train.py --arm U   # and T, R
python scripts/x06_eval.py          # opens test once
python scripts/x07_generate.py      # descriptive generation
python scripts/x08_figures.py
```

`scripts/x01_rt_chunks_ibex.py` runs on Ibex against the verified `embed_g1` token cache and
produces the RT conditioning array. Seeds fixed at 20260918 throughout.

**Stopped here.** No InfoNCE, symmetric cosine contrastive loss, dual encoder or other model
family was started after seeing this result.
