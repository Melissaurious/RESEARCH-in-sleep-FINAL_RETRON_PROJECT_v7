# embed_x2 — PROVENANCE

## Parent state

| | |
|---|---|
| branch | `embeddings-g0` |
| parent commit | `8bf7207` (`embed_x1: RT-conditioned ncRNA generation pilot`) |
| X1 bundle (untouched) | `results/embed_x1_conditional_pilot/` |
| frozen split (untouched) | `results/embed_g2b_frozen_split/` |

X1 and the `embed_g2b` frozen split were **read only**. The X1 Outcome-C interpretation is
preserved verbatim in `DESIGN.md` section 2 and is not revised retrospectively.

## Binding inputs

`CROSSFIT_MANIFEST.tsv` sha256
`65228b34f7a1fec983c34d5d639a9c7029b5123e749e4797ead15412cc4a6a12`.

The manifest was hashed **before any training** (`y02_crossfit_manifest.py`) and rehashes to
the identical value in `HASHES.sha256` after all results were produced. The fold assignment,
population and split membership were therefore not altered in response to any model output.

Upstream frozen caches, used read-only and never fine-tuned:

- ESM-C 300M RT representations — 32 mean-pooled chunks x 960 (`embed_g1`)
- pooled RT ESM-C (`ARIS_OUTPUT/embed_g2_analysis/work/rt_pooled.npy`), used for the C3
  nearest-neighbour rule and the section-10 relatedness axis
- RiNALMo giga-v1 ncRNA representations (`embed_g1`)
- mmseqs `rt_id0.50` and cd-hit-est `nc_id0.80` clusters (`embed_g2b/inputs/`)
- canonical `data/derived/rt_ncrna_exact_pair_recurrence_v1.parquet` — joined 30,924/30,924
  pairs for the taxonomy and deposition strata

## Model

Architecture and hyperparameters imported unchanged from
`results/embed_x1_conditional_pilot/scripts/x03_model.py`. No architecture tuning, no added
capacity, no InfoNCE, no contrastive loss, no new RNA encoder, no hyperparameter search.
AdamW, lr 2e-4, 4,000-step warmup, wd 0, accum 2, batch 32, fp32, <=40 epochs, patience-5
lowest-validation-NLL stopping. Vendored Profluent `grna-modeling` `transformer.py`
sha256 `c1f2112b4b91e8424b173d49da43e7ff14fc1ec0bf39ddc0e419147a2b90af3f`.

## Compute

| run | where | detail |
|---|---|---|
| primary cross-fit, 25 cells (5 arms x 5 folds), seed 20260918 | local, 2 x RTX 4090 | re-run once after the incident in `EXECUTION_NOTES.md` |
| seed replicates, 30 cells (T/G/R x 5 folds x seeds 20260919, 20260920) | Ibex array `52095027`, account `pi-hohndor` | 30/30 COMPLETED, single submission 2026-09-19T15:46:42 |
| counterfactual tier selection C1-C4 | local CPU, 4 parallel processes | 946,174 forward passes sized in advance |
| counterfactual evaluation + analysis | local, 1 x RTX 4090 | `y04_analyse.py` |

## Environment

`/home/borg/miniconda3/envs/retron_esmc` — python 3.12.13, torch 2.5.1+cu121, numpy 2.5.2.

The recurrence-table join was extracted in `retron_tradicional` (the GPU env has no pyarrow)
to `work/recurrence_join.tsv.gz`, row-aligned to the split assignment and asserted as such.

## Script order

1. `y01_t4_audit.py` — T4 composition; confirms the 83-component X1 denominator
2. `y02_crossfit_manifest.py` — builds, asserts and **hashes** the 5-fold assignment
3. `y03_train_cv.py` — one (arm, fold) training cell; `y_run_local.sh` runs all 25
4. `y04a_tier_sizing.py` (+ `y04a_run_tiers.sh`) — frozen C1-C4 selection -> `cf_selection.npz`
5. `y04b_primary.py` — primary contrasts, strata, fold heterogeneity (no counterfactuals)
6. `y04_analyse.py` — full analysis including the counterfactual hierarchy
7. `y05_strata.py` — section-10 relatedness / taxonomy / deposition strata
8. `y06_seed_stability.py` — Amendment A optimization-variance check

`y04b_primary.py` is `y04_analyse.py` with section [5] removed, so the primary endpoint could
be computed while the tier selection was still building. Both produce identical values for
the contrasts they share.

## Ordering discipline

`DESIGN.md`, `COUNTERFACTUAL_RULES.md`, the cross-fit manifest and the six stratification
axes in `y05_strata.py` were all written and frozen **before any X2 effect estimate was
inspected**. `DESIGN.md` section 3 additionally records a prospective prediction (that T4
might remain unresolved) which the result contradicted — recorded rather than removed.

## Integrity

`HASHES.sha256` covers every file in this bundle. Quarantined outputs from the double-launch
incident are retained under `ARIS_OUTPUT/embed_x2_confirmation/work/QUARANTINE_double_run/`
and `logs/QUARANTINE_double_run/`; **none of them contributed to any reported number.**
