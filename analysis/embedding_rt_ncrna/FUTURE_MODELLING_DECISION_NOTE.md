# Future-modelling decision note

**Status of partner-specific contrastive modelling: `NOT YET JUSTIFIED AS A CONFIRMATORY
PARTNER-SPECIFIC TEST`.** Not `METHOD REJECTED`.

Nothing in this note authorises a run. It records what would have to be true first.

## What was decided, and why

`embed_g2`'s pre-registered escalation condition was that the cross-modal probe beat **every**
trivial baseline on the held-out split by the declared margin. At rung 3 (retron-type-matched
candidates) the advantage over the k-mer baseline is **+0.0298, 95 % CI [−0.0048, +0.0633]** —
not distinguishable. Escalation was therefore not authorised, and no InfoNCE, symmetric cosine
contrastive, dual-encoder or cross-attention model was trained.

The concern is specific and measurable, not stylistic: retron type is recoverable from **each
modality alone** (ESM-C 0.498, RiNALMo 0.656 against a 0.269 majority). Any cross-modal objective
using arbitrary mismatched candidates can therefore reach a high score by aligning the two spaces
on a type axis. With **n_eff = 14.1** independent test components, that outcome could not be
distinguished after the fact from genuine partner compatibility.

The prior generative attempt in this lab is the empirical precedent: its contrastive arm raised
the metric it optimised **43-fold while degrading the rank statistic** (2AFC 0.9532 → 0.9072,
t = −21), and its leave-one-family-out control attributed **78 %** of the effect to family
identity.

## Preserved as future candidate methods

- regularized or deep CCA
- InfoNCE dual encoders
- symmetric cosine contrastive loss
- cross-attention compatibility scoring
- positive-pair alignment objectives
- RT-conditioned autoregressive ncRNA generation (OpenCRISPR architecture)

## Reopening triggers

Any one of these is a reason to revisit; (2) and (5) are the ones that would actually change the
answer.

1. **Materially more RT–ncRNA associations.**
2. **More independent within-retron-type components.** This is the binding constraint. More pairs
   from the same lineages do not help.
3. **Recovery of ncRNAs missed by existing annotation / covariance-model approaches.** Every
   ncRNA call in the corpus has `nc_source = 'infernal'`; retron ncRNAs no CM detects are
   invisible by construction and sit disproportionately in divergent lineages. **Re-run
   `a07_within_type_feasibility.py` whenever ncRNA recovery improves** — it is one command and
   could change the verdict for several types at once.
4. **Independent evidence allowing a harder compatibility evaluation** — biochemical, structural
   or functional data that turns some non-observed pairings into *assayed* incompatible ones,
   converting retrieval into a classification task with biologically meaningful negatives.
5. **A prospectively designed within-type split with sufficient component-level test support**,
   designed before any model is fit, with a declared minimum test n_eff.

## If a run is authorised later, these are the standing requirements

Carried over from `embed_g2` and not renegotiable without a new decision record:

- **component-level inference**, never pair-level;
- **a declared negative/decoy ladder including a type-matched rung**, since that is the rung that
  decides;
- **false-candidate exclusion** — a decoy that is an observed partner of the query RT anywhere in
  the corpus is not a decoy;
- **a stop rule against trivial baselines declared before the readout**;
- **terminology discipline**: mismatched candidates are not negative or incompatible pairs;
- **a minimum test n_eff declared in advance**, with the run not starting if the split cannot
  supply it.

## Engineering that already exists

Do not reimplement. `HISTORICAL_MODEL_ASSET_AUDIT.md` has paths and hashes.

| component | source |
|---|---|
| InfoNCE objective | `openCRISPR_for_retrons/.../03_train.py` |
| memory-aware in-batch negatives (measured VRAM: k=15 OOM, k=4 21.87 GiB, k=2 15.19 GiB on 24 GiB) | `.../02_dataset.py` |
| cross-attention protein→RNA architecture | vendored Profluent `grna-modeling` |
| N×N scoring + 2AFC rank evaluation | `.../22_loco_eval.py` |
| treatment-vs-baseline Welch comparator | `.../27_struct_eval.py` |
| frozen embedding caches (ESM-C, RiNALMo) | `results/embed_g1_representations/`, Ibex |
| relatedness-aware bipartite component split | `results/embed_g2b_frozen_split/` |
| component-level bootstrap / permutation | `results/embed_g2_frozen_baseline/scripts/a02_engine.py` |
| negative ladder + false-candidate exclusion | same |

The historical work supplies the modelling machinery; `embed_g2` supplies the evaluation
discipline that would make its output interpretable. A future experiment should combine them
rather than start either from scratch.
