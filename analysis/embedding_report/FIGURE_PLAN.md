# FIGURE PLAN

Seven figures are specified; **F1–F7 are generated and rendered now** from frozen bundles.
F8–F10 are specified but **cannot be produced yet** — each names exactly what it is waiting for.

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
| label | figure footer states PRELIMINARY: one pilot run, one seed per arm; X2 pending |

## F4 · Component-level R−T effect distribution — **GENERATED**

`figures/F4_component_effect_distribution.{png,pdf}`

| | |
|---|---|
| panels | **a** histogram of the 357 per-component R−T differences with the mean marked · **b** effect vs component size (marker area ∝ pairs) showing that every component carries equal weight and that the effect is not driven by the largest ones · **c** violin split by T4 content (descriptive) |
| data | `derived/x1_component_level.tsv` — re-aggregated from the frozen per-sequence held-out NLL arrays by `scripts/r01_x1_component_table.py`, **46/46 checks reproduce the frozen summary tables** |
| carries | that a supported mean shift is still a small shift of a wide distribution; 65 % of components favour R, so 35 % do not |
| thesis | §6.5 |
| note | this figure could not be drawn from the frozen bundle alone, which carries summaries only; no model output was recomputed to produce it |

## F5 · Observed RT versus same-type counterfactual conditioning — **GENERATED**

`figures/F5_counterfactual_control.{png,pdf}`

| | |
|---|---|
| panels | **a** schematic of the control (observed pair; M = 8 same-type alternatives; same arm-R model with only the conditioning RT swapped; Δ log P per nt) · **b** the frozen estimate with component-level CI, eligibility (4,630/4,638) and the fractions of pairs and components favouring the observed RT |
| data | `embed_x1/tables/x1_counterfactual.json` |
| carries | the strongest level-2-flavoured evidence in the frozen set, together with the statement that alternatives are controls and not biological negatives |
| thesis | §6.6 |
| limitation shown | per-pair values were not frozen, so only the component-level summary is plotted; stricter tiers C2–C4 are marked PENDING |

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

## Specified but NOT producible yet

### F8 · Cross-fitted R−T and the counterfactual tier ladder (C1 → C4) — **PENDING X2**

Planned panels: pooled out-of-fold R−T with between-fold heterogeneity; R−G and R−P beside it;
Δ log P per counterfactual tier C1→C4 with eligible pairs, components and `UNDETERMINED` shading
below 30 components. **Waiting on**: the X2 run to finish and land as a frozen bundle. Nothing
about its direction or magnitude may be drawn or implied before then.

### F9 · Within-type feasibility landscape — **producible, lower priority**

A per-type scatter of pairs versus n_eff with the four pre-declared criteria drawn as thresholds,
making visible that `TypeIC1_IC2` has 6,277 pairs at n_eff 1.2 while `TypeIIIA3` passes with 1,082
pairs. Data exist (`embed_g2c/tables/g2a_within_type_feasibility.tsv`). Recommended for §5.4 if
that section needs a figure rather than a table.

### F10 · Candidate-set decision plot with real scores — **BLOCKED**

The realised version of F7: real conditional scores for a named, experimentally tractable RT–ncRNA
set, with margins, seed/fold consistency and in-distribution flags. **Blocked by** an authorised
model and an authorised scoring run; neither exists, and the prerequisites in
`CANDIDATE_SELECTION_DESIGN.md` §5 are unmet. It must not be produced from X1 or X2 outputs
opportunistically.

---

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

`scripts/r01_x1_component_table.py` regenerates the derived table and **fails rather than writes**
if any of its 46 checks disagrees with the frozen bundle.
