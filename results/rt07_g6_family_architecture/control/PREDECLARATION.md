# g6 predeclaration — written BEFORE any g6 statistic was computed

Gate: `rt07_g6_family_architecture` · Authority: `launchers/LAUNCHER_02_rt0_rt7_definition.md`
§7 (`g6` row) and `results/rt07_g4b_production_mapper/docs/G6_ANALYSIS_PLAN.md`.
No new launcher is created; this file is the gate's predeclaration, and `run.sh` records that
it was written first.

---

## 0 · Sealed external context — the anti-circularity rule that binds this gate

**`results/rt07_g7a_rt0_rt7_bridge/` is sealed external context and is NOT read by this gate.**

The historical RT0–RT7 bridge was landed before this gate ran, chronologically. It is
nonetheless treated as though it does not exist:

* no g7a-derived RT0–RT7 assignment, boundary, structural interpretation or "interesting
  region" may influence **any** g6 feature, threshold, family selection, state selection,
  clustering rule or hypothesis;
* g6 operates **entirely in frozen `state_id` space** on the pre-existing g5 products;
* `INPUTS.tsv` names no g7a path, no script reads one, and `verify.sh` asserts this
  mechanically — the same construction g7a used to exclude g5/g6 from itself, applied in the
  opposite direction.

g7a may be used **only after g6 is frozen**, for interpretation and crosswalk. Every state
reported by this gate is a bare `state_id`.

This ordering is honest but unusual, so it is recorded rather than glossed: the two gates are
independent by construction, and the mechanical check is what makes that claim auditable
rather than a promise.

## 1 · The question, and what would answer it

> **After accounting for mapper visibility, completeness and sequence relatedness, does the
> frozen conserved-state representation reveal reproducible organization of RT diversity
> between labelled families and within Retrons?**

The operative word is **reproducible**. A pattern that is merely *present* is not an answer:
the instrument has a known family-callability gradient that would produce apparent structure
on its own. So the gate measures whether structure **replicates on data the first half never
saw**, and whether it **survives** three controls plus a null.

## 2 · Populations and denominators

| name | n | role |
|---|---|---|
| CATALOGUE | 501,561 | context only. **Never a denominator.** |
| ELIGIBLE (`G5_ELIGIBLE_N`) | 369,381 | eligibility and visibility statements |
| **INSPECTABLE** (`verdict == MAPPED`) | **354,102** | **every architecture statement.** Only these carry a committed state assignment |
| Retron eligible / inspectable | 61,395 / 53,722 | the within-Retron arm |
| MULTI | 2,824 | its own population, never folded into a single family |

Each family carries **its own** eligible and inspectable counts. A between-family number
computed on a pooled denominator is a defect.

## 3 · The representation — frozen `state_id` space only

Per inspectable exact RT, the **state-call profile**: a 150-length vector over the frozen
anchor states, each entry one of `MAPPED` / `AMBIGUOUS` / `UNSUPPORTED` / `DELETED_STATE`.
Read directly from `g5_states.parquet`. Nothing is re-mapped, re-fitted or re-thresholded.

The primary derived quantity is the **per-state MAPPED indicator** (1 if `MAPPED`, else 0),
because `MAPPED` is the frozen rule's only positive evidence. `AMBIGUOUS`, `UNSUPPORTED` and
`DELETED_STATE` are reported in their own right and are never collapsed into "absent".

`CAT_STATE` 262 is **not** one of the 150 anchors and is never pooled with them.

## 4 · The falsifiable core — split-half reproducibility

1. **Split by cluster, not by sequence.** Every eligible exact RT is assigned a cluster
   (§5). Clusters are partitioned into half A and half B by a deterministic, **label-blind**
   rule: `sha256(cluster_representative_hash)` parity. Because the split is by cluster, the
   two halves **share no near-duplicate sequences** — which is precisely the leak that a
   sequence-level split would allow (Principle 7: a cluster split is not automatically an
   independent split, so the split is *measured* in §7, not assumed).
2. **Per family, per half**, compute the mean per-state MAPPED fraction — a 150-length
   profile on that half's own denominator.
3. Build the between-family **distance matrix** in each half (correlation distance over the
   150-length profiles), restricted to families with ≥ 100 inspectable sequences in **both**
   halves.
4. **Reproducibility statistic `ρ`** = Spearman correlation between the upper triangles of the
   half-A and half-B distance matrices.

The same construction is applied within Retrons, with the tool-subtype strata of §6 in place
of families, each tool kept on its own denominator.

## 5 · The clustering resource — minimum, clean, label-blind

No existing clustering resource is reusable. The candidate
(`…RETRON-DB_V3/MELISSA_SCRIPTS/clustering_experiments/cluster_work/full_id*.tsv`) was audited
and is `DO-NOT-USE` on three independent grounds, recorded in
`tables/g6_clustering_reuse_audit.tsv`: a different input population (397,445 unique members),
an identifier space that is **not** `rt_hash` and for which the project records that no link
exists, and no pinned tool version.

Built here instead, and nothing more:

```
mmseqs easy-linclust <eligible.faa> --min-seq-id 0.90 -c 0.8 --cov-mode 0   # PRIMARY
                                    --min-seq-id 0.50 -c 0.8 --cov-mode 0   # sensitivity
                                    --min-seq-id 0.30 -c 0.8 --cov-mode 0   # sensitivity
```

* input: **exactly** the 369,381 eligible amino-acid sequences, keyed by `rt_hash`, written
  from `data/derived/rt_exact_v1.faa` and hashed into `INPUTS.tsv`;
* **label-blind**: no family label, tool label, taxonomy or state call is an input to
  clustering;
* `--cov-mode 0` (bidirectional coverage) is the primary because it is the stricter
  redundancy criterion; the prior work's `--cov-mode 1` is not inherited;
* tool version **pinned and recorded**: `mmseqs 18.8cc5c`;
* 0.90 is declared as the **near-duplicate** threshold for the primary split. It is not tuned:
  the two sensitivity thresholds are run regardless of what 0.90 shows, and all three are
  reported.

## 6 · Within-Retron strata — metadata, never truth

`system_types` does not resolve retron subtype (a single undifferentiated string over all
61,395). `rt_tool_calls_v1` does, and joins to `rt_hash` at 369,381/369,381. Used as strata:

* `subtypes_defensefinder` — 33,769 retron exact RTs resolved;
* `subtypes_padloc` — 32,290 resolved;
* **never pooled with each other**, each on its own denominator, capital-initial vs lowercase
  provenance preserved (the two tools agree on only 44.6 % of `system_subtypes`).

A stratum with < 100 inspectable sequences is reported `UNDERPOWERED` and is **not** entered
into a distance matrix. A subtype label is a **tool annotation**: no accuracy, sensitivity,
specificity, precision, recall, F1 or ROC is computed against one, ever, and tool disagreement
is never called mapper error.

Retrons additionally carry an unsupervised, **label-free** arm: the same split-half statistic
over cluster-derived groups, so the within-Retron question can be answered even where no tool
assigns a subtype.

## 7 · Controls — declared now, reported whatever they show

| id | control | what it tests | what failure means |
|---|---|---|---|
| **NULL-1** | **label permutation**: family labels shuffled **within `mapped_fraction` decile**, 200 replicates, ρ recomputed each time | whether ρ is achievable without real family structure, *holding visibility fixed* | if observed ρ sits inside the null, there is **no reproducible organization** — a terminal negative |
| **CTRL-VIS** | repeat within narrow `mapped_fraction` strata, and report ρ against the family callability gradient | whether structure is just the GII-centred visibility gradient | if ρ collapses, the answer is `EXPLAINED_BY_VISIBILITY` |
| **CTRL-REL** | repeat cluster-collapsed (one sequence per cluster) at all three identities | whether structure is driven by near-duplicate swarms | if ρ collapses, the answer is `EXPLAINED_BY_REDUNDANCY` |
| **CTRL-COMP** | repeat on full-length-only (`completeness_class`) | whether structure is a truncation artefact | if ρ collapses, the answer is `EXPLAINED_BY_COMPLETENESS` |
| **PC-SPLIT** | measure cross-half sequence identity leakage directly | Principle 7 — independence is **measured**, not inferred from cluster ids | a leaking split invalidates ρ and is reported |
| **PC-POS** | a positive control: `CAT_STATE` 262 concordance, which is known-present, recovers across halves | that the instrument has power on this substrate | if it fails, no absence statement may be made |

## 8 · Terminal decision — declared before the statistic exists

`ρ` is reported **continuously**. The verdict per arm uses two conditions, both required:

* **significance**: observed ρ exceeds the **99th percentile of the NULL-1 permuted null**
  (a data-derived criterion, not a hand-picked cutoff);
* **effect floor**: observed ρ ≥ **0.50**, so a statistically detectable but negligible
  structure is not reported as organization.

| verdict | when |
|---|---|
| `REPRODUCIBLE_AND_SURVIVES_CONTROLS` | both conditions met, and ρ survives CTRL-VIS, CTRL-REL and CTRL-COMP |
| `REPRODUCIBLE_BUT_EXPLAINED_BY_<control>` | both conditions met in the primary, but ρ collapses under a named control |
| `NOT_REPRODUCIBLE` | either condition fails |
| `UNDERPOWERED` | too few qualifying strata to build a distance matrix |

Verdicts are issued **separately** for the between-family arm and the within-Retron arm. A
negative, or an answer that holds for one arm and not the other, is a **valid terminal
outcome** and the gate stops there. The gate does not try further methods to convert a
negative into a positive.

## 9 · Binding interpretation rules

1. `DELETED_STATE` is an **alignment-path** statement. "This family lacks this region" is a
   different claim and is not derived from occupancy.
2. `NO_SUPPORTED_MAPPING` / abstention is **not** biological absence and **not** failure.
3. A low MAPPED fraction in a family distant from GII is the **expected** behaviour of a
   GII-centred frame, not a biological finding.
4. MyRT / PADLOC / DefenseFinder labels are **strata, never truth**.
5. `MULTI` is its own population.
6. Tool-specific fields are never pooled across tools.
7. Atypical biology is **flagged before it is filtered**.
8. **No historical RT0–RT7 label appears anywhere in this gate**, and the crosswalk is not
   consulted (§0).
9. Scope is `-M 50` only. No `-M 60` or `-M a2m` claim.
10. No accuracy claim, no universal-RT-architecture claim, no re-running or re-tuning of the
    mapper, no structural data, no phylogeny, no motif discovery, no ncRNA, no embeddings, no
    co-evolution.

## 10 · Stopping condition

The gate stops when both arms carry a verdict from §8 with their controls reported. **At most
one bounded repair cycle** is permitted, and only for a genuine load-bearing defect. "The
result is negative" is not a defect.
