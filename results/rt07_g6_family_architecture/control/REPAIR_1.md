# Repair cycle 1 of 1 — NULL-1 does not preserve the relevant nuisance structure

Invoked under `control/PREDECLARATION.md` §10 ("at most one bounded repair cycle, and only for
a genuine load-bearing defect"). **This is the only repair cycle this gate may use, and it is
now spent.**

## The defect

`PREDECLARATION.md` §7 declared **NULL-1** as a *sequence-level* label permutation within
`mapped_fraction` decile. Running it exposed a design error, not a data problem:

| measurement | value |
|---|---|
| clusters spanning **exactly one** family (identity 0.90) | **172,944 / 173,081 = 99.92 %** |
| NULL-1 (sequence-level) ρ | median **0.9833**, p99 **0.9906** |
| observed ρ | **0.9865** |

Family labels are **near-constant within a cluster**. A sequence-level permutation therefore
destroys a nuisance structure that is present in 99.92 % of the data: it scatters each
pseudo-family across all clusters, so the pseudo-family's two halves sample the *same*
underlying pool and replicate almost perfectly. A real family's two halves receive *different*
sequence swarms and replicate less easily.

The null is therefore **easier than the alternative**, and the test is biased **against**
finding structure. This is precisely what `PROJECT_ANALYSIS_PRINCIPLES.md` **Principle 12 —
"Controls must preserve the relevant nuisance structure"** forbids.

**The defect was diagnosed from a property of the data** — the 99.92 % cluster/family purity,
and the *a priori* predictable direction of the bias — **not from the fact that the repair
changes the answer.** The direction of the bias could have been stated before either number
existed, and is stated here in those terms.

## The repair

Add **NULL-2**: the same permutation performed at **cluster level** — whole clusters are
reassigned between pseudo-families, within `mapped_fraction` stratum. Pseudo-families are then
also built from whole related swarms, matching the alternative's nuisance structure.

Nothing else changes: the same ρ statistic, the same split, the same populations, the same
effect floor, the same controls.

## What is retained, unchanged

**NULL-1 is not deleted, not superseded and not hidden.** It lands in full, with its verdict,
in `tables/g6_between_family_null.tsv` and `tables/g6_within_retron_null.tsv`. A failed control
is evidence (`PROJECT_ANALYSIS_PRINCIPLES.md` Principle 24).

## The honest limitation of the repair — stated, not buried

**NULL-2 is not a perfect null either, and it errs in the opposite direction.**

* **NULL-1** breaks within-cluster label constancy → pseudo-families replicate too easily →
  **conservative** against the alternative.
* **NULL-2** preserves whole clusters but breaks the *between-cluster* relatedness that makes a
  real family a set of related clusters → pseudo-families replicate less easily than real
  families would on relatedness alone → **anti-conservative**.

Neither is the truth. The two therefore **bracket** it, and this gate reports **both** and
treats the interval between them as the result. A verdict is only called `SURVIVES` where it
holds under the conservative null; where the two nulls disagree, the disagreement **is** the
finding and is reported as such rather than resolved by preferring the convenient one.
