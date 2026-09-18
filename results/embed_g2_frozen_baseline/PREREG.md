# embed_g2 — pre-registration

**Written before any validation or test number was computed.** Everything below follows from
`LAUNCHER_03` §7d/§7e/§7g and the frozen split `results/embed_g2b_frozen_split/` (commit
`15e00b8`). Nothing here is a new decision; where the launcher already fixed a choice, this
document only restates it so the run can be audited without cross-referencing.

## Immutable inputs (not re-derived, not re-examined)

RT/ncRNA clustering thresholds and coverage rules · component membership · train/val/test
assignment · primary test population (4,638 pairs, 357 components, n_eff 14.1) ·
near-duplicate sensitivity population (1,525 pairs, 284 components, n_eff 24.5) ·
component-level confirmatory inference · the frozen interpretation.

Representations: **frozen pooled only** — ESM-C 300M (960-d, 29,192 RT) and RiNALMo giga-v1
(1280-d, 16,458 ncRNA) from `embed_g1`. Token-level arrays are not touched; that stays `DEFER`.

## Primary metric — already declared, not chosen here

`LAUNCHER_03` §7 gate `embed_g2_frozen_baseline`:

> held-out-component retrieval MRR under the full control ladder, against the trivial baselines

**Task.** Given a held-out RT, rank a candidate set of ncRNAs; record the reciprocal rank of the
true partner. Candidate set = 1 true partner + **49 decoys** (50-way). Direction RT→ncRNA is
primary; ncRNA→RT is reported as secondary.

**Chance MRR for 50-way** = (1/50)·Σ_{i=1..50} 1/i = **0.0898**.

**False-negative exclusion.** Any decoy that is a true partner of the query RT *anywhere in the
full 30,924-pair table* is removed and redrawn. Naive in-batch negatives are biologically wrong
here — one ncRNA has 705 RT partners.

## Negative/control ladder — declared in §7e, restated

| rung | decoy pool |
|---|---|
| 0 positive control | boundary-trimmed variant of the true ncRNA at the same physical locus; must rank top |
| 0F failure control | pair assignment permuted within fold; must read chance |
| 1 | uniform over ncRNAs in the same fold |
| 2 | length- and GC-matched (\|Δlen\|/len ≤ 0.10 and \|ΔGC\| ≤ 0.05) |
| 3 | same `detection_model` (the retron-type label control) |
| 4 | same ncRNA identity cluster (`nc_id0.80`) |
| 5 | ncRNAs partnered with RTs in the same RT cluster (`rt_id0.50`) as the query |
| 6 | same `tax_species`, **within one taxonomy system only** |

A rung is reported as `INSUFFICIENT` where the pool cannot supply 49 admissible decoys for
enough queries, rather than silently falling back to an easier pool.

## Models — simplest first, per §7d

**Trivial / marginal baselines (deliverables 3 and 4), run FIRST:**

| id | scores a candidate by | marginal of |
|---|---|---|
| `B-pop` | the candidate ncRNA's training frequency | ncRNA-only |
| `B-len` | −\|len_nc − f(len_rt)\|, f a ridge fit on train | length |
| `B-gc` | −\|gc_nc − g(len_rt)\|, g a ridge fit on train | composition |
| `B-kmer` | cosine between ridge-predicted ncRNA 4-mer profile and the candidate's | composition |
| `B-model` | probability of the candidate's `detection_model` under a logistic model of RT embedding → model label | RT-only / label shortcut |

`B-pop` is the **ncRNA-only marginal**; `B-model` is the **RT-only marginal** in its strongest
usable form (an RT-only score is constant across candidates and therefore exactly chance, so
the informative RT-only baseline is the label shortcut).

**Cross-modal compatibility model (deliverable 5):**

`M-CCA` — regularized CCA between the two frozen pooled spaces, fit on **training pairs only**;
score = cosine similarity in the shared latent space. This is the `REQUIRED BASELINE` entry
"low-rank linear projection into a common latent space / regularized CCA". No higher-capacity
model is run in `embed_g2`.

## The only validation-selected quantity

A **small, predeclared** grid — 9 configurations, per "avoid broad hyperparameter searches":

- latent rank `k` ∈ {16, 32, 64}
- regularization `α` ∈ {1e-2, 1e-1, 1e0}

**Selection rule, fixed now:** the configuration maximizing **validation rung-1 MRR**. One
number, one rule, applied once. No other quantity is selected on validation. No negative-set
selection, no metric selection, no threshold selection.

## Component-level inference (deliverable 7) — the inference unit is immutable

Pair counts are **not** the sample size. For every reported metric:

1. per-component mean MRR over that component's pairs;
2. point estimate = mean over components (each component weighted equally);
3. **95 % CI by bootstrap over components**, 10,000 resamples;
4. **permutation test**: RT↔ncRNA assignment shuffled within the fold, 10,000 permutations,
   giving a null distribution of the component-mean MRR and a one-sided p-value;
5. n_eff reported beside every interval (14.1 primary, 24.5 sensitivity).

## Stop rule (§2 kill criterion) — declared before the readout

If any trivial baseline matches or exceeds `M-CCA` on the primary metric within the declared
tolerance, the track reports **no embedding-specific compatibility signal** and does **not**
escalate to `embed_g3`.

**Tolerance, fixed now:** `M-CCA` must exceed the best trivial baseline by more than the 95 %
bootstrap CI half-width of the *paired per-component difference* between them.

## Order of execution

1. assemble; 2. trivial baselines on train→validation; 3. `M-CCA` grid on train→validation;
4. select one configuration by the rule above and **freeze**; 5. run **once** on the primary
test population; 6. run once on the frozen near-duplicate-excluded sensitivity population;
7. strata and controls; 8. report.

Test is not read before step 5, and nothing is re-selected after it.

## Claim boundary

The strongest statement this gate can support is **compatibility signal in frozen pretrained
embeddings beyond the tested controls**, generalizing across the declared relatedness-component
split. Not co-evolution, not binding, not interaction, not generalization to evolutionarily
unrelated sequences.
