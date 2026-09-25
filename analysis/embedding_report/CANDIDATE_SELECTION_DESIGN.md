# Candidate-pair prioritisation — PROSPECTIVE DESIGN, NOT EXECUTED

> **Nothing in this document has been run.** No RT–ncRNA pair has been scored, ranked or
> nominated. Figure F7 is a schematic with synthetic values. Every quantity defined here is a
> **predicted pairing / cross-reactivity score** — a hypothesis-generating device — and remains so
> until experimental validation. It is never evidence of orthogonality, incompatibility, binding
> or co-evolution.
>
> **X2 raises the bar for this framework rather than clearing it.** Its stop condition explicitly
> forbids converting a log-likelihood difference into a compatibility label, an interaction
> probability or a pair score, and its findings say why that prohibition is substantive: under the
> strictest counterfactual control the model favours the observed RT for only **52.5 % of pairs**,
> the raw pair-weighted mean at that tier is nominally negative, and about **78 %** of the
> RT-associated gain is explained at the homolog-lineage level rather than by the individual RT.
> Any future scoring work inherits the six binding requirements R1–R6 of `X2_HANDOFF.md`.

## 1 · The eventual objective

For a set of experimentally tractable RT–ncRNA systems, identify candidate sets such as

```
RT-A ↔ ncRNA-A          model supports the observed/native pairings
RT-B ↔ ncRNA-B
                        …while giving relatively weak conditional support to
RT-A ↔ ncRNA-B
RT-B ↔ ncRNA-A
```

so that a small number of pairs can be prioritised for laboratory testing of whether they behave
as a low-cross-reactivity set.

**What this is for.** Choosing which 4–8 combinations to build and assay first, out of a
combinatorially impossible space. That is the whole claim. The experiment adjudicates; the score
only orders the queue.

## 2 · The scoring object

For a candidate set of *n* RTs and their *n* observed ncRNAs, compute the full *n × n* matrix

> **S(i, j) = conditional log-likelihood of ncRNA_j given RT_i**, per nucleotide,
> under an authorised, out-of-fold model.

Two normalisations are mandatory before any comparison, because raw log-likelihoods are dominated
by properties of the RNA rather than of the pairing:

- **row-centre** (per RT): subtract that RT's mean score over the candidate ncRNAs — removes "this
  RT makes every RNA look likely";
- **column-centre** (per ncRNA): subtract that ncRNA's mean score over the candidate RTs — removes
  "this RNA is intrinsically easy", which is the dominant nuisance, since ncRNA length, GC and
  type-grammar drive absolute likelihood.

Report the double-centred matrix, **and** both singly-centred versions. A conclusion that survives
only one centring is not a conclusion.

## 3 · The selection statistic

For a candidate set *C*:

> **margin(C) = min over i of S̃(i, i) − max over i ≠ j of S̃(i, j)**

i.e. the worst native score minus the best cross score, on the centred scale. Selection maximises
`margin(C)` over candidate sets, **not** over individual pairs — because the object being proposed
to the laboratory is a *set* in which each RT should prefer its own ncRNA over the others in that
same set.

Report alongside every margin:

- the per-cell values and the full matrix, not just the summary;
- an uncertainty interval for the margin (§4);
- the number of independent relatedness components represented in the set;
- whether any two members of the set share a relatedness component — if they do, the set is not
  informative, because their "cross" pairing is a near-native pairing.

## 4 · Confidence — what it must be conditioned on

A margin alone is not a recommendation. Each candidate set carries a **confidence profile**, and a
set is only nominated when every gate passes. These are deliberately conjunctive: a large margin
does not buy its way past an out-of-distribution flag.

| factor | how it enters | gate |
|---|---|---|
| **model uncertainty** | refit under ≥ 3 seeds and evaluate each set under every out-of-fold model that legitimately covers it (X2_HANDOFF R3) | the margin's sign must be stable across all of them, and the across-seed spread must be reported beside the estimate — X2 found the specific-RT increment's sd as large as its point estimate |
| **replicate/seed consistency** | report the spread of `margin(C)` across seeds and folds, not the mean alone | spread must be smaller than the margin |
| **sequence relatedness of the RTs** | pairwise identity and coverage between set members, under the frozen bidirectional rule | members must not be near-identical (a cross pair between two 95 %-identical RTs tests nothing) |
| **retron type** | whether the set is within-type or across-type | report both; **within-type sets are the informative ones** for partner specificity, across-type sets mostly re-measure type grammar |
| **phylogenetic / lineage distance** | distance between set members, and their distance to the training distribution (X2_HANDOFF R5) | intermediate distance preferred — see the distance trap below. X2 measured the cost directly: in the quartile least similar to training RTs the effect's interval spans zero |
| **in-distribution status** | is each RT within the representation regime the model was trained on? flag `LEN_EXTRAPOLATED`, unusual length, rare type, low-coverage cluster | any member flagged out-of-distribution ⇒ the set is reported but **not** nominated |
| **native-vs-counterfactual margin** | the same quantity measured against the frozen counterfactual tiers (C1–C4) for each member (X2_HANDOFF R1) | each native pairing should also beat its **C3/C4** counterfactuals, not only the other set members and not merely same-type ones, which are ~10× easier and would inflate any headline |
| **lineage versus pairing** | the margin must be evaluated against `delta_R_minus_G` / `delta_logP_C4`, never `delta_R_minus_T` / `delta_logP_C1` (X2_HANDOFF R4) | a feature or a score correlated with RT lineage inherits the lineage signal, which X2 showed to be ~78 % of the effect |
| **component support** | number of independent components spanned | a set drawn from a single relatedness component is not evidence |

### The distance trap, stated explicitly

**Do not simply choose the most evolutionarily distant RTs.** Distance is confounded with
out-of-distribution prediction: a distant RT will receive low scores for *every* ncRNA, which
inflates the apparent margin while actually measuring the model's ignorance. The recommended
selection band is **intermediate**: RTs related enough to be inside the model's competence and
far enough apart that a cross pairing is a genuine alternative. This band must be declared before
scoring, not chosen after seeing the matrix.

## 5 · Prerequisites — none of which is satisfied today

1. **An authorised model.** Nothing currently authorises a scoring run: `embed_g3` was not
   escalated, X1 is a pilot, and X2 — although its frozen gate returned X2-A — closed with an
   explicit stop condition ("no log-likelihood difference is converted into a compatible/
   incompatible label, an interaction probability, or a pair score") and returned the work for
   operator review.
2. **A level-2 result that survives the stricter test — partially met, and instructive.** X2 did
   replicate the contrast and *did* resolve the T4 high-independence stratum (−0.02594 [−0.03508,
   −0.01731] over 247 components). What it did **not** deliver is a pair-specific effect of usable
   size: the residue beyond the 50 %-identity homolog group is −0.00551 with a factor-of-three
   spread across seeds, and the within-cluster counterfactual tier C4 is +0.00168 nats/nt. A
   selection margin built on quantities that small, against alternatives that close, would be
   dominated by model noise.
3. **Within-type component support.** Only `TypeIIIA3` and `TypeIB1` pass the population criteria,
   at test-fold n_eff 3.7 and 4.6. A cross-reactivity claim is inherently within-type.
4. **A named, experimentally tractable set** defined by the laboratory — expressible constructs,
   available assay, known positive control — not by the model.
5. **A pre-registered scoring protocol**: centring, margin definition, seeds, folds, gates and the
   selection band, all declared before any matrix is computed, with the number of sets to be
   nominated fixed in advance.
6. **A positive control that can fail**: a pairing the score should rank highly and a condition
   under which it demonstrably should not (e.g. a shuffled RT, a non-RT protein, a scrambled
   ncRNA). Without it, a ranked list is unfalsifiable.

## 6 · What the laboratory result would mean

| outcome | interpretation | what it licenses |
|---|---|---|
| native pairs active, cross pairs inactive | consistent with the prediction; **first genuine level-3 evidence** in this project, for that set | reporting a validated instance; calibrating the score on a handful of points, not a general compatibility claim |
| all combinations active | the RTs are promiscuous in this assay; the score does not predict function | the score is not a compatibility predictor; report the negative prominently |
| all combinations inactive | the assay or the constructs failed | uninformative about the score — the positive control decides whether the experiment ran at all |
| cross pairs active, native inactive | the score is anti-predictive for this set | a strong refutation; must be reported, not re-parameterised away |

**A single validated set does not establish a general predictor.** Calibration would need enough
independent sets to estimate a hit rate with an interval — which, as everywhere else in this
project, is a question of independent units, not of the number of assays run.

## 7 · Reporting discipline

- Call it a **predicted pairing score** or **predicted cross-reactivity score**, never a
  compatibility, orthogonality, specificity or interaction score.
- Never report an AUROC, precision or recall against non-observed pairings: they are not negatives.
- Always publish the full matrix and the failed candidate sets alongside the nominated ones.
- State the model, seeds, folds, centring and selection band with every ranked list; a ranked list
  without its protocol is not interpretable.
- If the experiment refutes the ranking, that result lands with the same prominence as a
  confirmation.
