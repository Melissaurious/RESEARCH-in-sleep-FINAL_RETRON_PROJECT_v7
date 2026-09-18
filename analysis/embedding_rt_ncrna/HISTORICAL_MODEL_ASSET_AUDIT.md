# Historical embedding / pairing-model asset audit

**Scope:** prior work in this user's project trees on RT–ncRNA embeddings, ESM / ESM-C / ESM-2 /
ESM-3, RiNALMo, EVA, contrastive learning, InfoNCE, symmetric cosine losses, dual encoders,
cross-attention, CNN pairing models, paired-vs-mismatched datasets, compatibility scoring and
co-evolution modelling.

> ⛔ **No historical result supersedes the frozen `embed_g2` experiment.** Everything below is
> recorded as *precedent* and as *reusable engineering*. Where a historical number disagrees with
> a frozen bundle, the frozen bundle wins and the disagreement is a finding about the history.

**Classification**: `GREEN` safe to reuse directly · `AMBER` inspect before reuse ·
`RED` do not inherit as truth · `DEAD ROUTE` tried and closed, keep as a negative record.

Roots searched: `openCRISPR_for_retrons`, `RESEARCH-in-sleep-RETRON-DB{,_V2,_V3,_V4,_V5}`,
`RESEARCH-retron-db`, `JUNE_RETRONS`, `RESEARCH-in-sleep-FINAL_RETRON_PROJECT{,_WORK,_v7}`,
`RESEARCH-in-sleep-GENERAL_v{1,2,3,5,6}`, `PhD_thesis_retrons_chatGPT`, plus paths referenced by
their documentation.

---

## ⭐ Headline finding of this audit

**A protein-conditioned RT→ncRNA model with a working InfoNCE arm already exists, was trained,
and reached the same conclusion as `embed_g2` from the opposite direction.**

`/home/borg/openCRISPR_for_retrons/` retargeted Profluent's `grna-modeling` (the OpenCRISPR
architecture of §D) from Cas9→gRNA to retron RT→ncRNA. Its own handoff states the finding
without hedging:

> **"The model does FAMILY RECOGNITION, not partner recognition."**

Leave-one-family-out, 4 families × 3 seeds, full N×N scoring on held-out rows:

| family | n | row 2AFC held-out | row-matched control | delta |
|---|---:|---:|---:|---:|
| TypeIB1 | 114 | 0.6017 | 0.7419 | −0.140 |
| TypeIIIA3 | 82 | 0.5363 | 0.6115 | −0.075 |
| TypeIV | 78 | **0.5020 (chance)** | 0.7136 | −0.212 |
| TypeXIII_Mx65 | 73 | 0.6474 | 0.7391 | −0.092 |

A row-matched control — removing exactly the same 454 rows chosen at random rather than by family
— decomposes the gap as **22 % training volume, 78 % family identity**, measured at 454-vs-454
rows so it is not a volume effect.

**Its contrastive arm is the cautionary result.** Adding an InfoNCE term raised the metric it
optimised 43-fold while making discrimination *worse*:

| statistic | baseline | contrastive | t |
|---|---|---|---|
| enrichment (MEAN gap) | +0.3692 | **+15.9562** | +7.45 |
| **row 2AFC (RANK)** | **0.9532** | **0.9072** | **−21.01** |
| col 2AFC norm | 0.9185 | 0.7991 | −12.64 |

Its own note: *"a project that had reported 'enrichment' alone would have called this a
spectacular success."* This is direct empirical support for the §B decision not to escalate to a
contrastive model on an evaluation that cannot separate type recognition from partner
recognition.

Its structure-supervision arm (1E) is a clean pre-registered null: an auxiliary secondary-structure
head that demonstrably learned its targets changed discrimination by **−0.0010 (t = −0.55)**.

**Its diagnosis of the ceiling matches ours**: *"12,720 pairs over ~3,400 independent groups,
where family identity nearly suffices to solve the training task"* — i.e. independent groups, not
pair count, is the binding constraint. `embed_g2` reached the same conclusion on a different
population (30,924 pairs, n_eff 14.1 in test) with a different method.

---

## Asset table

### 1 · `openCRISPR_for_retrons` — protein-conditioned RNA generation with InfoNCE

| | |
|---|---|
| root | `/home/borg/openCRISPR_for_retrons/ARIS_OUTPUT/` |
| env | `/home/borg/miniconda3/envs/opencrispr_retrons` |
| Ibex | `/ibex/project/c2366/RETRONS/opencrispr_ncrna/`, account `pi-hohndor` |

| asset | sha256 (16) | bytes | what it is | class |
|---|---|---|---|---|
| `stage3_train/scripts/03_train.py` | `409b43552a4e6f79` | 16,968 | **training harness incl. the InfoNCE term** (Profluent ships none). Flags `--contrastive`, `--contrastive-temp`, `--contrastive-negatives`, `--structure`, `--shuffle-pairing` | **GREEN** |
| `stage3_train/scripts/02_dataset.py` | `c1f75d91dc39f4e2` | 10,668 | dataset + **roll-based in-batch negative construction** (protein batch rolled by r; K shifts → K negatives per anchor at K extra forwards, avoiding B simultaneous autograd graphs) | **GREEN** |
| `stage3_train/scripts/22_loco_eval.py` | `d0e7b69b18d94e87` | 10,272 | **leave-one-family-out N×N scoring + 2AFC**. The instrument behind the headline table | **GREEN** |
| `stage3_train/scripts/24_structure_head.py` | `c561ea3e43800933` | 9,205 | auxiliary structure head with frame guard and pre-registered readouts | AMBER |
| `stage3_train/scripts/27_struct_eval.py` | `993e90717177decd` | 8,837 | treatment-vs-baseline comparison (Welch) | **GREEN** |
| `stage3_train/scripts/01_cache_embeddings.py` | `a134626b137a2ac2` | 6,103 | ESM-2 protein embedding cache for the conditioning pathway | **GREEN** |
| `stage2_data_contract/cache/pairs_extended.tsv` | `3eb00445afdbc6bc` | 7,937,616 | **12,720 RT–ncRNA pairs** | AMBER |
| `stage2_data_contract/cache/splits_extended.tsv` | `6cfd475842313042` | 549,111 | **union-find grouped splits** with `cm_family`, `blastn_cluster`, `uf_group` | AMBER |
| `stage3_train/cache/runs/` | — | 421 MB, 86 runs | trained checkpoints incl. `contrast_s*`, `loco_*`, `st_*`, `rand_*` | AMBER |

**Architecture**: frozen ESM-2 encoder → bidirectional transformer conditioning layer →
three-layer autoregressive RNA decoder with causal self-attention and cross-attention to the
protein; ~700k trainable parameters.
**Population**: 12,720 pairs, ~3,400 independent groups; ncRNA = the CM alignment span (owner
decision, not re-derived).
**Split**: union-find groups over `blastn_cluster`; leave-one-family-out for the decisive test.
**Loss**: autoregressive RNA LM + optional InfoNCE term + optional structure head.
**Negatives**: in-batch, roll-based. **Memory measured on 24 GiB**: k=all(15) OOM, k=4 21.87 GiB,
k=2 15.19 GiB, k=1 11.85 GiB.
**Leakage control**: yes — family-level (LOCO) and cluster-level (union-find). Stronger than
naive random splitting; *weaker* than `embed_g2`'s bipartite-component split, which blocks on
both modalities simultaneously.
**Scientific status**: family recognition established; partner recognition **not** established;
contrastive arm degraded the rank statistic; structure supervision a clean null.

> **Reusable components — the answer to "does InfoNCE infrastructure already exist?" is YES.**
> The InfoNCE objective, the memory-aware in-batch negative sampler with measured VRAM numbers,
> the N×N/2AFC evaluation harness, and the Welch treatment-vs-baseline comparator are all written,
> debugged and documented. A future contrastive experiment should **port these rather than
> reimplement**, replacing the population and split with the `embed_g2b` frozen component split.

⚠️ Two inherited cautions recorded in its own handoff: `src/`, `main.py`, `generate.py` are
read-only (import graph repaired at runtime by `oc_shim.py`); and never glob
`rt0_rt7_domain_test_v3/cache/s1a/`, where a merged file sits beside its parts and double-counts.

### 2 · `JUNE_RETRONS` — the earliest frozen dual-embedding attempt

| asset | sha256 (16) | bytes | what it is | class |
|---|---|---|---|---|
| `00_build_pairs_table.py` | `b66bfe1567c9a2c3` | 5,140 | builds RT + ncRNA FASTAs and a pairs table from PipelineData JSONL | AMBER |
| `01_extract_embeddings.py` | `f884b79ea419a1a2` | 6,887 | **frozen ESM-2 + RiNALMo embedding extraction and cache** — the direct conceptual ancestor of `embed_g1` | AMBER |
| `02_alignment_analysis.py` | `347e6042c9231804` | 5,496 | alignment analysis over the pair table | AMBER |
| `03_remove_gold_leakage.py` | `c6983499f4437c7b` | 4,790 | leakage removal against a gold set | AMBER |

Same two-modality frozen-embedding idea as this track, but ESM-2 rather than ESM-C, and with no
component-level split, no negative ladder and no component-level inference. **Superseded by
`embed_g1`/`embed_g2`**; retained as provenance for how the question was first posed. `RED` if
any of its numbers were ever to be quoted; `AMBER` as code.

### 3 · `RESEARCH-in-sleep-RETRON-DB_V4` — representation probes and caches

| asset | sha256 (16) | what it is | class |
|---|---|---|---|
| `ncrna_representation_probes/scripts/s14_embed_oriented.py` | `89e12543dd7f1cdb` | RiNALMo embedding script; source of the **bf16 batch-geometry** lesson and the orientation fix | **GREEN** (tooling) |
| `rt0_rt7_domain_test_v4_and_tree/scripts/s4n_embed_esmc.py` | `472498e2c7b4adbe` | ESM-C embedding script; BOS/EOS stripping convention | **GREEN** (tooling) |
| `ncrna_representation_probes/cache/emb_oriented/` | — (40 GB) | prior RiNALMo per-nucleotide cache | **RED as data** |
| `rt0_rt7_domain_test_v4_and_tree/cache/E7/emb_esmc.npz` | — | prior ESM-C pooled cache, 4,950 × 960 | **RED as data** |
| `M_models/` (+ 29 GB cache) | — | RiNALMo dependency maps; measured cost model `t = 6.539e-05·L^1.989`, r² 0.9992; Archive II positive control AUROC median 0.9993 | AMBER |

**Why the caches are RED as data, measured not assumed**: zero of the 16,458 registered ncRNA
hashes appear in any of the six V4 oriented sets (V4 median length 556 nt against 151 nt here —
a different extraction), and zero of the 4,950 ESM-C ids are registered RT hashes. They are a
different population. The *scripts* remain GREEN as tooling and were the basis for `embed_g1`.

⚠️ **The orientation lesson is the load-bearing one**: an earlier 21.4 GB cache was built on
**unoriented** sequence, so ~49.4 % of it was a language model's view of a reverse complement
that does not exist. This is why `embed_g0` re-verified orientation by hash round-trip.

### 4 · `DEAD ROUTE` register

| route | what was tried | outcome |
|---|---|---|
| **InfoNCE on the generative RT→ncRNA model** | `openCRISPR` 1C, in-batch negatives | **DEAD as run**: enrichment ×43, row 2AFC −0.046 (t = −21). Not the method's fault — the evaluation could not separate type from partner. Re-openable under a within-type design |
| **Structure supervision to force fold learning** | `openCRISPR` 1E, auxiliary structure head | **DEAD**: −0.0010 (t = −0.55) with both pre-registered escape hatches closed (targets were learnable; λ=1.0 learned them better and bought nothing) |
| **Unoriented RNA embedding caches** | V4 `M_models` 21.4 GB cache | **DEAD**: computed on reverse complements; superseded by `emb_oriented` and then by `embed_g1` |
| **Prior V4 embedding arrays as data for this track** | reuse attempt | **DEAD**: measured zero hash overlap with the registered universe |

### 5 · Not found

No evidence of ESM-3, EVA-based RT–ncRNA pairing models, CNN pairing models, or explicit
co-evolution/phylogenetic-congruence modelling in any searched tree. The `EVA` conda env exists
and imports (torch 2.5.1+cu124) but no RT–ncRNA analysis uses it.

---

## Summary for future reuse

| need | already exists? | where |
|---|---|---|
| InfoNCE objective | **yes** | `03_train.py` |
| memory-aware in-batch negatives + measured VRAM | **yes** | `02_dataset.py` |
| cross-attention protein→RNA architecture | **yes** (vendored Profluent) | `openCRISPR_for_retrons/src/` |
| frozen protein embedding cache pipeline | **yes** | `01_cache_embeddings.py`, `s4n_embed_esmc.py` |
| frozen RNA embedding cache pipeline | **yes** | `s14_embed_oriented.py`, `embed_g1` |
| N×N scoring + 2AFC rank evaluation | **yes** | `22_loco_eval.py` |
| treatment-vs-baseline statistics | **yes** | `27_struct_eval.py` |
| **relatedness-aware bipartite component split** | **only in `embed_g2b`** | `results/embed_g2b_frozen_split/` |
| **component-level bootstrap / permutation inference** | **only in `embed_g2`** | `results/embed_g2_frozen_baseline/scripts/a02_engine.py` |
| **negative/decoy ladder with false-candidate exclusion** | **only in `embed_g2`** | same |

The gap between the two halves of that table is the contribution of this track: the historical
work supplies the *modelling* machinery, and `embed_g2` supplies the *evaluation discipline* that
would make its output interpretable.
