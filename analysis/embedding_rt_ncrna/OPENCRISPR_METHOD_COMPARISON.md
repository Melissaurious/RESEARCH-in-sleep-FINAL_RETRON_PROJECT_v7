# OpenCRISPR ↔ retron RT–ncRNA: bounded methodological comparison

**Purpose.** Compare *design*, not performance, between Profluent's protein-conditioned guide-RNA
model and the present retron RT–ncRNA embedding experiment, in order to identify which design
elements could transfer to a future retron model and which cannot transfer without redesign.

**Hard boundaries observed.** No model was trained. No OpenCRISPR sequence was added to, or used
in, the retron dataset. OpenCRISPR performance is **not** used as a benchmark against the CCA
result — the biological tasks and validation endpoints differ and the numbers are not
commensurable.

---

## 0 · Sources consulted, and what could not be obtained

| source | status |
|---|---|
| vendored release `src/grna-modeling/` (model code, vocabulary, transformer) | **read** |
| released checkpoint `…grna-model-esm8m-id90…epoch=39-step=62400.ckpt` (8.6 MB) | **read**, incl. `hyper_parameters`, Lightning loop state, optimizer/scheduler state |
| vendored `src/opencrispr_repro/` (ProGen2 protein side) | inspected; **not** the gRNA model |
| local reproduction record `ARIS_OUTPUT/stage1_repro_feasibility/FINDINGS.md` | **read** |
| Nature 2025, *Design of highly functional genome editors by modelling CRISPR–Cas sequences* | **NOT OBTAINED** — 303 redirect to `idp.nature.com` authentication |
| bioRxiv preprint `10.1101/2024.04.22.590591` | **NOT OBTAINED** — HTTP 429 from this environment on every attempt (WebFetch and direct) |
| Europe PMC record `MED/40739342` | **NOT OBTAINED** — HTTP 403 |
| GitHub `Profluent-AI/OpenCRISPR` README | read; states nothing about gRNA-model training methodology |

> ⚠️ **Consequence, stated plainly.** I was unable to read the published methods or supplementary
> methods from this environment. Therefore **tier A below is almost empty**, and that is a
> limitation of my access, **not** evidence that the authors omitted anything. Every item I could
> not verify is recorded as *not determinable from available material* — never as *not done*.

---

## 1 · Evidence tiers

- **A — explicitly reported by the authors.** Requires the paper. Only one item reaches this
  tier, and only through a search-engine summary rather than a read of the methods; it is
  flagged accordingly and should be re-checked against the paper before being cited.
- **B — reconstructable from released code / checkpoint.** High confidence; asserted against
  file contents.
- **C — not determinable from available material.** Explicitly *not* a claim of absence.

## 2 · Fact table

| # | design element | finding | tier |
|---|---|---|---|
| 1 | protein sequence population | A secondary summary states **112,212 type II effector proteins** from the CRISPR–Cas Atlas were used to train a sequence-to-sequence gRNA model. **Unverified against the methods text**; treat as provisional | A(weak) |
| 2 | RNA population | not determinable | C |
| 3 | definition of a protein–RNA association | **Structurally**: one protein conditions **two linked RNA segments**, sentinel-bracketed in a 10-token vocabulary `a c g t 1 2 3 4 - _`, where `1`/`2` bracket the tracrRNA and `3`/`4` the crRNA (`utility/vocabulary.py`). How a (protein, tracrRNA, crRNA) triple was *assembled from genomic data* is not determinable | B (representation) / C (curation) |
| 4 | train/validation/test construction | Lightning loop state proves a **train/validation split existed**: 3,120 training minibatches and 388 validation batches per epoch (≈ **88.9 % / 11.1 %** by batch count), 40 epochs, 62,400 optimizer steps at `acc_batches=2`. **No test-loop state is present in the checkpoint.** Batch size is not recorded, so absolute dataset size is **not** recoverable (dataset ≈ 3,120 × batch_size) | B (existence and proportion) / C (construction rule, absolute size, test set) |
| 5 | protein-side identity/homology control across splits | **Not determinable.** The checkpoint *filename* contains the token **`id90`**, which is consistent with a 90 %-identity clustering or de-duplication step — but **no field inside the checkpoint corroborates it**, and a filename token is not a method. Recorded as a hypothesis to check against the paper, **not** as a finding | C |
| 6 | RNA-side identity/homology control | not determinable | C |
| 7 | joint protein+RNA grouping when splitting | not determinable | C |
| 8 | family/type composition across folds | not determinable | C |
| 9 | candidate / negative / mismatch construction | **None exists in the released model.** The objective is a conditional language-model loss over the RNA given the protein; there is no negative, decoy or contrastive term anywhere in `gRNAModel.forward`. Whether any was used in training is not determinable | B (released model) / C (training) |
| 10 | protein encoder | **ESM2 `esm2_t6_8M_UR50D`** — the 8M-parameter model (`hyper_parameters.config.esm_model`), `d_s_protein = 320` | B |
| 11 | frozen vs trainable weights | **ESM2 is outside the trainable module entirely.** `gRNAModel.forward` consumes a precomputed `protein_embs` tensor; ESM2 is never instantiated inside the module, so there is no gradient path to it. Trainable parameter count **705,930** — consistent with ESM2 excluded. Frozen **by construction**, not by a freeze flag | B |
| 12 | conditioning mechanism | `nn.Linear(320 → 128)` projection of the ESM2 embedding, then **1 bidirectional self-attention encoder layer** over the protein (`n_enc_layers = 1`, 8 heads), giving the representation the decoder attends to | B |
| 13 | RNA decoder | **3 decoder layers** (`n_dec_layers = 3`), each with RNA self-attention **and cross-attention to the protein representation** (8 heads each), then an LM head over the 10-token vocabulary. `d_s = 128` | B |
| 14 | objective / loss | Token-level **cross-entropy on next-token RNA prediction**, computed inside `forward` when `S_label` is supplied: labels shifted by one, padding and sentinel positions masked, mean over unmasked positions. Optimizer state: `initial_lr 2e-4`, `warmup 4000`, `weight_decay 0`, `acc_batches 2` | B |
| 15 | generation / retrieval metrics | not determinable. The released code has **no evaluation harness** — no `training_step`, no `configure_optimizers`, no dataset, no metric code | C |
| 16 | experimental / external validation | A secondary summary indicates the **OpenCRISPR-1 system (protein + gRNA)** was experimentally validated as a functional gene editor. Whether *generated gRNAs specifically* were validated independently of the protein is not determinable from available material | A(weak) / C |

**Local reproduction evidence (tier B, from this lab's own verification).** The checkpoint loads
with all 85 tensors byte-identical; conditioned on SpCas9 it emits the verbatim canonical direct
repeat `gttttagagctatgctgttttg` and the `ggcaccgagtcggtgc` terminator hairpin, 16/16 well-formed;
conditioned on *E. coli* MalE it produces **0/64** well-formed outputs. The conditioning pathway
is therefore real and strong — which is itself a design fact worth carrying: a protein-conditioned
RNA decoder *can* be made to depend genuinely on its protein input.

---

## 3 · Comparison table

| design axis | OpenCRISPR gRNA model | current retron baseline (`embed_g2`) | implication for a future retron model |
|---|---|---|---|
| **scientific endpoint** | generate a functional gRNA for a given effector; endpoint ultimately **wet-lab editing activity** | *discriminate* the observed ncRNA partner from controlled candidates; endpoint a **retrieval statistic** | The endpoints are not comparable. A functional endpoint tolerates training-set homology leakage — if the designed editor works in cells, leakage cannot explain it. A retrieval endpoint does **not** tolerate it, because leakage directly inflates the statistic. **A retron generative model would need a functional or at least an orthogonal endpoint to inherit that tolerance.** |
| **protein population** | 112,212 type II effectors (provisional, tier A-weak) | 29,192 unique exact RTs across 21 retron types | Comparable order of magnitude on the protein side; the retron constraint is not raw count. |
| **RNA population** | not determinable | 16,458 unique oriented ncRNAs | — |
| **association definition** | one protein → two sentinel-bracketed RNA segments (tracrRNA, crRNA) | one RT ↔ one exact ncRNA, as co-observed in a genomic locus | **The two-segment sentinel vocabulary maps directly onto retron msr/msd** and is the single most transferable representational choice. |
| **split construction** | train/val ≈ 88.9/11.1 by batch; rule not determinable; no test-loop state in checkpoint | **connected components of a bipartite RT-cluster ↔ ncRNA-cluster graph**, deterministic 70/15/15, frozen and hash-verified | Not transferable in either direction as-is; see §4. |
| **protein homology control** | not determinable (`id90` filename token only) | mmseqs 0.50 min-seq-id, **bidirectional 80 % coverage** | — |
| **RNA homology control** | not determinable | cd-hit-est 0.80, shorter-sequence 80 % coverage | — |
| **joint grouping** | not determinable | **yes — joint by construction**; the component is closed under both relations | The retron experiment *measured* that this is necessary: one ncRNA is observed with **705** distinct RTs, so protein-side clustering alone cannot prevent RNA-side crossing. |
| **inference unit** | not determinable | **relatedness component**; test n_eff = **14.1**, not 4,638 pairs | Any retron model's evaluation must inherit this or its intervals are meaningless. |
| **negatives / mismatched candidates** | none in the released objective | **6-rung declared ladder** with false-candidate exclusion; the type-matched rung is decisive | A generative objective needs no negatives; a *discriminative claim about partner specificity* does. |
| **encoder** | ESM2 8M, frozen by construction (outside the module) | ESM-C 300M + RiNALMo giga-v1, both frozen | **Directly transferable**, and the retron track already has both caches built and verified. |
| **trainable capacity** | **705,930 parameters** | 0 trained parameters (closed-form CCA) | A ~0.7M-parameter head is a plausible next rung — large enough to be expressive, small enough to be defensible against n_eff ≈ 14. |
| **objective** | conditional next-token cross-entropy on the RNA | cosine in a shared CCA space | Different questions: *does the RT change the RNA distribution* vs *can the observed partner be ranked first*. |

---

## 4 · The split-crossing question, treated carefully

The current retron experiment identified retron-type structure as a **major shared signal**:
retron type is recoverable from each modality alone (ESM-C 0.498, RiNALMo 0.656 against 0.269
majority), the leading canonical dimension carries η² of type 0.81/0.72, and 50 % of top-10
cross-modal neighbours share the query's type against 9.4 % prevalence. So the question of
whether family information can cross a split boundary is, for retrons, load-bearing.

**What I can say about OpenCRISPR's split: nothing determinative.** The construction rule is not
in the released artifacts and I could not read the methods. The `id90` filename token is
suggestive of a 90 %-identity step but is not corroborated anywhere inside the checkpoint, and I
will not convert a filename into a method.

**What I can say structurally, and which holds regardless of what OpenCRISPR did:**

1. **A protein-side identity control, at any threshold, does not by construction prevent
   RNA-side family information from crossing**, and vice versa. The two are only jointly
   controlled if the grouping is joint. In the retron data this is not a theoretical concern —
   one ncRNA is observed with 705 distinct RTs, so a protein-only split will place near-identical
   RNAs on both sides.
2. **A 90 %-identity threshold, if that is what `id90` denotes, is a de-duplication threshold,
   not a family-level control.** Members of one protein family routinely sit far below 90 %
   identity to one another. The retron experiment measured the consequence directly: at RT 0.70
   clustering, **89.4 %** of held-out RTs still had a ≥0.50-identity training relative; only at
   RT 0.50 with bidirectional coverage did that fall to 55.2 %, and reaching 1.7 % required RT
   0.30, which destroyed the usable sample.
3. **For a generative endpoint validated in the wet lab, (1) and (2) may not matter.** If a
   designed editor cuts DNA in cells, homology between training and validation sequences does not
   explain the phenotype. **For a retrieval or discrimination endpoint they matter completely.**
   This is the crux of why the two designs should not be evaluated against one another.

> The comparison is therefore **not** "OpenCRISPR used a weaker split". It is: *the endpoint
> determines how much the split has to carry, and a retron partner-specificity claim puts far
> more weight on the split than a functional-editing claim does.*

---

## 5 · What transfers, and what does not

### Transferable with little or no redesign

| element | why it transfers | status in this project |
|---|---|---|
| **frozen protein language-model encoder** | no gradient path needed; embeddings precomputable once | ESM-C 300M cache **already built and verified** (`embed_g1`) |
| **lightweight trainable conditioning layer** | a linear projection + 1 bidirectional self-attention layer is ~0.1M parameters and defensible at small n_eff | to be written |
| **autoregressive RNA decoder with causal self-attention** | retron ncRNA is a short sequence (34–395 nt) well inside decoder range | architecture exists in the vendored tree |
| **cross-attention from RNA decoder to protein representation** | the mechanism by which the RT can influence the RNA at all | exists; verified functional (SpCas9 0/64 MalE control) |
| **two-segment sentinel vocabulary** | `1`/`2` and `3`/`4` bracket two linked RNA segments — **structurally identical to msr/msd** | directly reusable |
| **precomputing and caching frozen embeddings** | the encoder is frozen, so recomputation per epoch is waste | already the `embed_g1` design |
| **small trainable parameter budget (~0.7M)** | matches the evidence available | — |

### Not transferable without redesign

| element | why not | what redesign requires |
|---|---|---|
| **split construction** | a protein-only or identity-only split cannot control a bipartite relation where one ncRNA has 705 RT partners | reuse the **frozen bipartite component split** (`embed_g2b`), or derive a new one under the same discipline |
| **definition of mismatched candidates** | the released objective has none; a partner-specificity claim needs them, and arbitrary mismatches are solvable by type recognition | the **declared ladder with a type-matched rung** and false-candidate exclusion |
| **evaluation of individual partner specificity** | likelihood of the observed RNA does not separate *type grammar* from *partner identity*; a model can score well by producing plausible retron ncRNA in general | an evaluation that explicitly decomposes retron-type RNA grammar, general ncRNA plausibility, and RT-conditioned specificity — **all three, reported separately** |
| **handling multiple valid ncRNAs per RT/type** | 3.15 % of RTs have >1 observed partner (max 176) and 17.7 % of ncRNAs have >1 RT partner (max 705); a single-target likelihood treats co-observed alternatives as errors | a set-valued or multi-reference objective, or explicit exclusion of multi-partner RTs with the exclusion reported |
| **homology-aware inference** | pair-level statistics overstate precision by two orders of magnitude here | **component-level** bootstrap and permutation, with a declared minimum test n_eff |
| **absolute dataset scale** | OpenCRISPR's gRNA training-set size is not recoverable (batch size unrecorded); retron within-type components are the binding constraint | the feasibility audit, re-run when ncRNA recovery improves |

---

## 6 · Proposed architecture for a future retron experiment — **NOT EXECUTED**

```
   RT amino-acid sequence
            │
            ▼
   ┌────────────────────────┐
   │  FROZEN protein LM     │   ESM-C 300M (already cached, embed_g1)
   │  no gradient path      │   per-residue tokens, BOS/EOS stripped
   └────────────┬───────────┘
                │  (L_RT × 960)
                ▼
   ┌────────────────────────┐
   │ trainable conditioning │   Linear(960 → d_s) + 1 bidirectional
   │  ~0.1 M parameters     │   self-attention layer, 8 heads
   └────────────┬───────────┘
                │  protein representation (L_RT × d_s)
                ▼
   ┌─────────────────────────────────────────────┐
   │  autoregressive ncRNA decoder, 3 layers     │   causal self-attention over ncRNA
   │  each: causal self-attn → cross-attn → FFN  │   + cross-attention to the protein
   │  ~0.6 M parameters                          │   LM head over {a,c,g,t} + msr/msd
   └─────────────────────────────────────────────┘   sentinels + pad
                │
                ▼
   msr segment ⟨1 … 2⟩   msd segment ⟨3 … 4⟩      (two-segment sentinel design,
                                                    inherited directly)
```

**Total trainable ≈ 0.7 M parameters**, encoder frozen. Deliberately the same capacity class as
the released model: large enough to express RT-conditioned structure, small enough to be
assessable against a small number of independent components.

**Objective**: conditional next-token cross-entropy on the ncRNA given the RT, with padding and
sentinel positions masked — as in the released model. **No contrastive term in the first
version**, because the `embed_g2` result and the prior in-lab contrastive arm both indicate that
an arbitrary-mismatch contrastive objective is solvable by type recognition.

**Evaluation must decompose three things and report all three separately**, never a single
headline:

1. **retron-type RNA grammar** — is the output the right *type* of ncRNA? (compare against a
   type-conditioned, RT-agnostic baseline)
2. **general ncRNA plausibility** — would this output be produced for *any* RT? (the MalE-style
   control: condition on an unrelated protein and on a shuffled RT, and require degradation)
3. **individual RT-conditioned specificity** — does the identity of *this* RT change the output
   relative to another RT **of the same retron type**? (the type-matched control, which is the
   only one that addresses level 2)

Only (3) bears on partner specificity, and (1) and (2) will absorb most of the achievable
likelihood.

---

## 7 · Prerequisites before this architecture is trained

None of these is satisfied today. All are measurable, and the first is the binding one.

1. **A within-type split with sufficient component-level test support.** Currently only
   `TypeIIIA3` and `TypeIB1` pass the population criteria, with **test-fold n_eff of 3.7 and
   4.6**. A declared minimum test n_eff must be set *before* training and the run must not start
   if the split cannot supply it.
2. **More independent relatedness components**, not more pairs. `TypeIC1_IC2` has 6,277 pairs at
   n_eff 1.2 — raw counts are actively misleading.
3. **ncRNA recovery beyond covariance models.** Every ncRNA call in the corpus is
   `nc_source = 'infernal'`; ncRNAs no CM detects are invisible by construction and sit
   disproportionately in divergent lineages — exactly the ones that add independent components.
   Re-run `a07_within_type_feasibility.py` whenever recovery improves.
4. **A declared policy for multi-partner RTs and multi-RT ncRNAs**, since a single-target
   likelihood mistreats co-observed alternatives.
5. **A pre-registered three-way evaluation decomposition** (§6) with its controls, written before
   any training run.
6. **msr/msd boundary annotations**, if the two-segment sentinel design is to be used as intended
   rather than on an undifferentiated CM alignment span.
7. **A positive control that can fail** — an RT–ncRNA relationship the model should recover, and
   a condition under which it demonstrably should not.

Prerequisite 1 is the gate. Until it is met, a generative retron model can be built and will
produce plausible ncRNA, but its output could not be attributed to partner specificity rather
than retron-type grammar — which is precisely the ambiguity `embed_g2` was designed to expose.
