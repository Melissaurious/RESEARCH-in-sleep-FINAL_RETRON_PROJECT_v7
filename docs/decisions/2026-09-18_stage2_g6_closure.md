# DECISION — `g6` family architecture is CLOSED; its headline is a bracket, not a number

Date: 2026-09-18 · Track: `rt07` · Status: **binding for downstream `rt07` work, the thesis
and any paper**

Producing bundle: **`results/rt07_g6_family_architecture/`** · Authority:
`launchers/LAUNCHER_02_rt0_rt7_definition.md` §7 (`g6` row) and
`results/rt07_g4b_production_mapper/docs/G6_ANALYSIS_PLAN.md`. **No new launcher was created.**

---

## A · The result

The question `g6` was run to answer:

> After accounting for mapper visibility, completeness and sequence relatedness, does the
> frozen conserved-state representation reveal **reproducible** organization of RT diversity
> between labelled families and within Retrons?

Measured as **split-half reproducibility** `ρ`: the between-group state-profile distance matrix
is rebuilt on two halves that **share no sequence cluster**, and `ρ` is the rank correlation
between them.

| arm | labelling | ρ | NULL-1 p99 | NULL-2 p99 | verdict |
|---|---|---|---|---|---|
| between-family | 36 of 42 families qualify | **0.9865** | 0.9906 ✗ | 0.9066 ✓ | `REPRODUCIBLE_UNDER_CLUSTER_NULL_ONLY` |
| within-Retron | DefenseFinder subtype, 10 strata | **0.8917** | 0.9814 ✗ | 0.8158 ✓ | `REPRODUCIBLE_UNDER_CLUSTER_NULL_ONLY` |
| within-Retron | PADLOC subtype, 14 strata | **0.9595** | 0.9782 ✗ | 0.6687 ✓ | `REPRODUCIBLE_UNDER_CLUSTER_NULL_ONLY` |
| within-Retron | label-free, 0.30 clusters | 0.8061 | — | — | `UNDERPOWERED` |

**The two nulls disagree, and the disagreement is the finding.** Neither is correct:

* **NULL-1** (declared) permutes labels at **sequence** level. It is **invalid here**: 99.92 %
  of clusters span exactly one family, so sequence-level permutation destroys a nuisance
  structure present in almost all the data and makes the null *easier than the alternative*
  — forbidden by `PROJECT_ANALYSIS_PRINCIPLES.md` Principle 12.
* **NULL-2** (the one permitted repair) permutes whole **clusters**. It preserves that
  structure but breaks the *between-cluster* relatedness that makes a real family a set of
  related clusters, so it errs **anti-conservatively**.

The truth lies between them. **Both are reported everywhere. NULL-1 is retained, not deleted.**

## B · The strongest statement the evidence supports

> **When mapper visibility — the confound NULL-1 was built to absorb — is controlled directly,
> the structure exceeds BOTH nulls.**

| control | ρ | NULL-1 p99 | NULL-2 p99 |
|---|---|---|---|
| `mapped_fraction` ∈ [0.0, 0.5) | 0.9399 | 0.8855 | 0.6808 |
| `mapped_fraction` ∈ [0.5, 0.8) | 0.9801 | 0.9671 | 0.6365 |
| `mapped_fraction` ∈ [0.8, 1.01) | 0.9885 | 0.9752 | 0.8426 |
| one representative per 0.90 cluster | 0.9959 | 0.9824 | 0.9832 |
| one representative per 0.50 cluster | 0.9855 | 0.9668 | 0.9655 |
| one representative per 0.30 cluster | 0.9915 | 0.9708 | 0.9664 |

All six exceed **both** nulls. Only the full, visibility-heterogeneous population fails NULL-1
— which is precisely where NULL-1's defect is strongest. So the between-family structure is
**not** an artefact of the GII-centred callability gradient, and **not** an artefact of
near-duplicate redundancy.

## C · What downstream work may and may not say

**May:**

* *"Per-family state-occupancy profiles in the frozen `state_id` space replicate on held-out
  sequence clusters (ρ = 0.9865 over 36 families), and the replication survives restriction to
  narrow mapper-visibility strata and collapse to one sequence per 30 %-identity cluster."*
* *"Retron subtype strata, as annotated by DefenseFinder (ρ = 0.8917) and, separately, by PADLOC
  (ρ = 0.9595), show reproducible differences in state-occupancy profile."* — the two tools are
  **named separately** and never pooled.
* *"The significance of this structure depends on the null: it exceeds a cluster-level
  permutation null but not a sequence-level one, and the sequence-level null is invalid for this
  labelling."* This sentence must travel with the headline.

**May not:**

1. **No accuracy claim of any kind** against a tool label — no sensitivity, specificity,
   precision, recall, F1 or ROC — and tool disagreement is never mapper error.
2. **No biological-absence claim.** `DELETED_STATE` is an alignment-path statement. A low
   MAPPED fraction in a family distant from GII is the **expected** behaviour of a GII-centred
   frame.
3. **No universal RT architecture claim**, and no claim beyond `-M 50`.
4. **No within-Retron claim from the label-free arm** — it is `UNDERPOWERED` (5 qualifying
   groups of 11,301 candidates; no permutation replicate reached the stratum threshold, so no
   null exists). The within-Retron result rests entirely on **tool annotations**, which are
   strata and not biology, and that limitation is load-bearing.
5. **No statement about an underpowered stratum.** 20 of 50 retron subtype strata are
   `UNDERPOWERED` (< 100 inspectable) and are reported but excluded from every distance matrix.
6. **No historical RT0–RT7 label.** Everything in `g6` is a bare `state_id`.

## D · Anti-circularity: `g7a` was sealed

`results/rt07_g7a_rt0_rt7_bridge/` was landed **before** `g6` ran, chronologically. It was
treated as though it did not exist:

* no g7a-derived RT0–RT7 assignment, boundary, structural interpretation or region influenced
  any `g6` feature, threshold, family, state, clustering rule or hypothesis;
* `INPUTS.tsv` names no g7a path, no script opens one, `seal.py` asserts it at run time, and
  `verify.sh` V1(a)(b)(c) and V2 check it mechanically.

**The g7a crosswalk may now be applied to `g6` results** — that is the interpretation step both
gates were designed to make possible, and it is legitimate only in this direction and only now
that `g6` is frozen. The permitted wording per historical label is
`results/rt07_g7a_rt0_rt7_bridge/tables/g7a_closure_decision.tsv`, which remains binding: only
RT3, RT4, RT5, RT7 (and RT2 partially, RT5+RT6 jointly) may be named at all, and RT0 and RT1 may
not be given any operational statement.

## E · The sequence-relatedness resource

No prior clustering resource was reusable; the audit is in
`tables/g6_clustering_reuse_audit.tsv` and found three independent disqualifiers — a different
input population (397,445 unique members), an identifier space that is **not** `rt_hash` with no
link recorded as existing, and **no pinned tool version**.

Built in `g6`, **label-blind** and minimal: `mmseqs 18.8cc5c easy-linclust`, exactly the 369,381
eligible sequences, `-c 0.8 --cov-mode 0`, identity 0.90 primary (**181,696 clusters**, a 51 %
collapse) with 0.50 and 0.30 as sensitivities. Registered for reuse.

## F · Limitations that travel with the result

1. **The halves are not perfectly independent, and this was measured rather than assumed**
   (Principle 7). PC-SPLIT: **11.22 % of cross-half hits are at ≥ 90 % identity**, because
   linclust is greedy and approximate. Leakage inflates ρ. The analysis least exposed to it —
   one representative per 30 %-identity cluster — still exceeds both nulls.
2. **The within-Retron arm rests on tool annotations.** The one labelling that used no tool was
   `UNDERPOWERED`.
3. **No adversarial pass.** Under BS-15 a reviewer must be on a model disjoint from
   `claude-opus-5`.
4. **An execution diagnosis was wrong and is recorded**, not hidden, in
   `results/rt07_g6_family_architecture/control/EXECUTION_INCIDENTS.md`. No number was affected.

## G · Scope not touched

Stage-2 mapper validation stays **CLOSED at Endpoint A**. The instrument, profile, anchors,
`CAT_STATE`, thresholds and all `g5` calls are unchanged and were read, never modified. `g7a`
is unchanged. `g7b` — the remaining structural and published-comparator campaign — is **NOT
STARTED** and is unaffected.

Supersede this record by a new record, never by rewriting it.
