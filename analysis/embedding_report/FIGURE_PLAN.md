# FIGURE PLAN

Ten figures are specified, and **all ten are generated and rendered** from frozen bundles: F1–F7
from the dataset/baseline/pilot work, F8–F10 from the landed X2 confirmation. Two further figures
(F11, F12) are specified but not produced; each names what it is waiting for.

**Numbering note (2026-09-19).** The slot previously reserved for the pending X2 figure is now
F8, and the counterfactual and bounding figures took F9 and F10. The earlier placeholders
"F9 within-type feasibility" and "F10 candidate-set decision plot" have moved to **F11** and
**F12**.

All figures render deterministically via

```bash
LD_LIBRARY_PATH=$CONDA_PREFIX/lib python scripts/f_figures.py          # all
LD_LIBRARY_PATH=$CONDA_PREFIX/lib python scripts/f_figures.py --only F4
```

with `$CONDA_PREFIX = /home/borg/miniconda3/envs/retron_tradicional`. No embedding is loaded, no
model is run, and nothing in the source worktree is written. PNG (300 dpi) and PDF (vector) are
emitted for every panel.

**Design rules applied throughout**

- Every panel that carries an inference shows its **denominator and its uncertainty**: number of
  components, n_eff, and a component-level 95 % CI — never a bare summary bar.
- Under-supported rungs and strata are drawn as `UNDETERMINED`, never as a null.
- Captions use *observed pair*, *candidate*, *counterfactual conditioning control*, *non-observed
  pairing*. Never *negative pair*, never *incompatible pair*.
- Descriptive panels are labelled descriptive; inferential panels are labelled as such.
- Colour palette is Okabe–Ito (colour-blind safe). Schematic text auto-shrinks to fit its box, so
  panels never overflow at print size.

---

## F1 · Dataset construction and the leakage-aware split — **GENERATED**

`figures/F1_dataset_split_schematic.{png,pdf}`

| | |
|---|---|
| panels | **a** flow: PAIR-ELIG → RT/ncRNA clustering → bipartite connected components → deterministic 70/15/15 · **b** component-size distribution (log–log) · **c** components vs n_eff per fold · **d** blocking-versus-power trade-off across the 12 evaluated threshold combinations |
| data | `embed_g2b/tables/split_components.tsv`; `embed_g2a/tables/g2_decision_table.tsv` |
| carries | why the component is the split unit (one ncRNA has 705 RT partners); why 4,638 test pairs are 14.1 effective units |
| thesis | §2 |
| caveat in caption | panel d's leakage column is the censored whole-universe probe; the exact held-out-vs-training search gives higher values |

## F2 · Conceptual U / T / R model and the three claim levels — **GENERATED**

`figures/F2_conditioning_concept.{png,pdf}`

| | |
|---|---|
| panels | **a** one byte-identical decoder, three conditioning inputs (constant vector / 21-type embedding / frozen ESM-C of *this* RT) → held-out likelihood · **b** the three-level claim ladder with an explicit "no automatic inference" barrier between level 2 and level 3 |
| data | architecture constants from `embed_x1/README.md` (no computation) |
| carries | that T − U isolates broad type information and R − T isolates individual-RT information; that level 3 is not reachable from levels 1–2 |
| thesis | §1.2, §6.1 |

## F3 · X1 held-out NLL / perplexity with component-level uncertainty — **GENERATED**

`figures/F3_x1_nll_comparison.{png,pdf}`

| | |
|---|---|
| panels | **a** component-mean test NLL per arm with 95 % CI and perplexity · **b** paired per-component differences (T−U, R−U, R−T) with the fraction of components favouring the first arm · **c** R−T across the full fold, the near-duplicate-excluded population, and T4 (interval includes zero, marked) |
| data | `embed_x1/tables/x1_arms.tsv`, `x1_comparisons.tsv`, `x1_sensitivity.tsv`, `x1_strata.tsv` |
| carries | the primary X1 result **and its smallness**, next to the type effect that is twice as large |
| thesis | §6.4, §6.7 |
| label | figure footer states PRELIMINARY: one pilot run, one seed per arm, single fold, and points to F8 for the cross-fitted confirmation |

## F4 · Component-level R−T effect distribution — **GENERATED**

`figures/F4_component_effect_distribution.{png,pdf}`

| | |
|---|---|
| panels | **a** histogram of the 357 per-component R−T differences with the mean marked · **b** effect vs component size (marker area ∝ pairs) showing that every component carries equal weight and that the effect is not driven by the largest ones · **c** violin split by T4 content (descriptive) |
| data | `derived/x1_component_level.tsv` — re-aggregated from the frozen per-sequence held-out NLL arrays by `scripts/r01_x1_component_table.py`, **46/46 checks reproduce the frozen summary tables** |
| carries | that a supported mean shift is still a small shift of a wide distribution; 65 % of components favour R, so 35 % do not |
| thesis | §6.5 |
| note | this figure could not be drawn from the frozen bundle alone, which carries summaries only; no model output was recomputed to produce it |

## F5 · Observed RT versus same-type counterfactual conditioning (pilot) — **GENERATED**

`figures/F5_counterfactual_control.{png,pdf}`

| | |
|---|---|
| panels | **a** schematic of the control (observed pair; M = 8 same-type alternatives; same arm-R model with only the conditioning RT swapped; Δ log P per nt) · **b** the frozen estimate with component-level CI, eligibility (4,630/4,638) and the fractions of pairs and components favouring the observed RT |
| data | `embed_x1/tables/x1_counterfactual.json` |
| carries | the strongest level-2-flavoured evidence in the frozen set, together with the statement that alternatives are controls and not biological negatives |
| thesis | §6.6 |
| limitation shown | per-pair values were not frozen in X1, so only the component-level summary is plotted; the panel now points forward to F9, where the stricter X2 tiers show a ~10-fold decay |

## F6 · Shared-representation evidence (atlas panels that carry the narrative) — **GENERATED**

`figures/F6_shared_space_evidence.{png,pdf}`

| | |
|---|---|
| panels | **a** cross-modal cosine by candidate class — separation shrinks monotonically as candidates are matched on type (descriptive) · **b** the retrieval ladder, M-CCA vs the strongest trivial baseline, with component counts on the axis, the chance line, and rungs 4–6 shaded `UNDETERMINED` (**inferential — this is the panel that carries the result**) · **c** type enrichment (5.32×) against the observed partner's median rank (238 of 2,756) |
| data | `embed_g2c/plotdata/similarity_long.tsv`, `tables/g2a_neighbourhood.json`; `embed_g2/tables/g2_test_ladder.tsv` |
| carries | level 1 supported, level 2 not established by retrieval |
| thesis | §4.2–4.5, §5.1 |

**On the existing UMAP atlas figures.** `embed_g2c/figures/fig1…fig5` (RT atlas, ncRNA atlas,
shared CCA atlas, similarity/retrieval, canonical dimensions) remain valid and are referenced, not
regenerated. In the thesis, **only fig5 (canonical correlations + η² of retron type per dimension
+ per-modality type-probe accuracy) is recommended for the main text**, because it carries the
mechanism behind the rung-3 boundary. The three UMAP panels belong in a supplementary figure with
an explicit caption that UMAP is visualisation only: it is non-distance-preserving, its apparent
clusters and gaps are artefacts of its hyperparameters as much as of the data, and **no claim in
this chapter rests on a UMAP panel**. Decorative UMAPs in the main text would imply discrete
biological classes that were never tested.

## F7 · Prospective candidate-selection matrix — **GENERATED (schematic, not a result)**

`figures/F7_candidate_selection_schematic.{png,pdf}`

| | |
|---|---|
| panels | **a** an illustrative RT × ncRNA conditional score matrix with a candidate set (native high, cross low) outlined in blue and a high-cross-score pair marked and deprioritised in orange · **b** the selection rule and the native-minus-cross margin · **c** the seven factors confidence must be conditioned on, including the warning that the most evolutionarily distant RTs are not automatically the best candidates because distance itself produces out-of-distribution scores |
| data | **synthetic** — no retron score has been computed |
| carries | the eventual laboratory-prioritisation endpoint, as METHODS/PROSPECTIVE |
| thesis | §8.2–8.3 |
| mandatory label | figure footer states: PROSPECTIVE METHODS SCHEMATIC; values are synthetic; no retron RT–ncRNA cross-reactivity has been predicted, scored or tested |

---

## F8 · X2 cross-fitted confirmation and decomposition — **GENERATED**

`figures/F8_x2_crossfitted_confirmation.{png,pdf}`

| | |
|---|---|
| panels | **a** out-of-fold decomposition: R−U, G−U, T−U, G−T, **R−T (primary)**, **R−G**, P−T, each with component-level CI · **b** replication against the X1 pilot plus the T4, T3 and near-duplicate-excluded strata · **c** all five cross-fit folds with their component counts |
| data | `embed_x2/tables/COMPONENT_LEVEL_EFFECTS.tsv`, `FOLD_HETEROGENEITY.tsv` |
| carries | the primary result **and** the fact that G−T is most of R−T; T4 resolving; the effect not being carried by one fold |
| thesis | §7.3, §7.4 |
| label | footer states INTERNAL cross-fitted confirmation, not external validation |

## F9 · Counterfactual decay C1 → C4, and the weighting that forbids a per-pair reading — **GENERATED**

`figures/F9_counterfactual_decay.{png,pdf}`

| | |
|---|---|
| panels | **a** Δ log P per nt by tier with component-level CIs and component counts, annotated with the ~10× decay · **b** % of components and of **pairs** favouring the observed RT against the 50 % chance line, with C3 at 52.5 % · **c** component-level versus raw pair-weighted means, showing the **sign difference at C3** |
| data | `embed_x2/tables/COUNTERFACTUAL_EFFECTS.tsv` + the reconciliation table in `X2_HANDOFF.md` |
| carries | the single most important bound on the level-2 claim, and the evidence for why no per-pair biological inference is supported |
| thesis | §7.5 |
| terminology | captions say *conditioning controls*, never negative or incompatible pairs |

## F10 · What bounds the result: lineage, seeds, relatedness — **GENERATED**

`figures/F10_bounds_lineage_seeds_relatedness.{png,pdf}`

| | |
|---|---|
| panels | **a** R−T decomposed into G−T (78 %) and R−G (22 %) · **b** R−T and R−G across three optimization seeds, showing R−G's factor-of-three spread against a stable sign · **c** R−T and R−G by nearest-training-RT cosine quartile, with Q1's interval spanning zero shaded |
| data | `embed_x2/tables/COMPONENT_LEVEL_EFFECTS.tsv`, `SEED_STABILITY.tsv`, `SENSITIVITY_STRATA.tsv` |
| carries | the three qualifications (Q1–Q3 of the closure record) in one figure |
| thesis | §7.4, §7.6 |
| note | panel c also shows R−G is flat across quartiles, which localises the gradient to the T arm |

---

## Specified but NOT producible yet

### F11 · Within-type feasibility landscape — **producible, lower priority** *(formerly F9)*

A per-type scatter of pairs versus n_eff with the four pre-declared criteria drawn as thresholds,
making visible that `TypeIC1_IC2` has 6,277 pairs at n_eff 1.2 while `TypeIIIA3` passes with 1,082.
Data exist (`embed_g2c/tables/g2a_within_type_feasibility.tsv`). Recommended for §5.4 if that
section needs a figure rather than a table.

### F12 · Candidate-set decision plot with real scores — **BLOCKED** *(formerly F10)*

The realised version of F7: real conditional scores for a named, experimentally tractable RT–ncRNA
set, with margins, seed/fold consistency and in-distribution flags. **Blocked by** an authorised
model and an authorised scoring run; neither exists, X2's stop condition forbids converting a
likelihood difference into a pair score, and the prerequisites in `CANDIDATE_SELECTION_DESIGN.md`
§5 are unmet. It must not be produced opportunistically from the X1 or X2 outputs.

## Reproduction and provenance

| figure | script | inputs | recomputes a result? |
|---|---|---|---|
| F1 | `scripts/f_figures.py:f1` | embed_g2a, embed_g2b tables | no |
| F2 | `:f2` | architecture constants | no |
| F3 | `:f3` | embed_x1 tables | no |
| F4 | `:f4` | `derived/x1_component_level.tsv` (verified) | no — re-aggregation only |
| F5 | `:f5` | embed_x1 counterfactual json | no |
| F6 | `:f6` | embed_g2, embed_g2c tables/plotdata | no |
| F7 | `:f7` | synthetic | no |
| F8 | `:f8` | embed_x2 component-level and fold tables | no |
| F9 | `:f9` | embed_x2 counterfactual table + handoff reconciliation | no |
| F10 | `:f10` | embed_x2 effects, seed-stability and strata tables | no |

`scripts/r01_x1_component_table.py` regenerates the derived X1 component table and **fails rather
than writes** if any of its 46 checks disagrees with the frozen bundle.
`scripts/r02_multiplicity.py` re-derives the partner-multiplicity percentages from two independent
frozen tables and fails if they disagree or if the population totals drift.
