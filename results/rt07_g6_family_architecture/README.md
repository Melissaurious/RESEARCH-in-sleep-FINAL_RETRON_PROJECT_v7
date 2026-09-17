# rt07_g6_family_architecture — reproducible organization in the frozen conserved-state space

STATUS: VERIFIED — `run.sh` reruns end to end from the landed g5 products and reproduces every
number below.

**Terminal. Both arms carry a verdict. The headline is a BRACKET, not a single number, because
neither null is correct and they err in opposite directions.**

```
n_attempted: 13     analyses (1 primary + 9 between-family controls + 3 within-Retron labellings)
n_succeeded: 12     analyses that produced a rho and a computable null
n_dropped:   0      nothing was dropped; 1 analysis is reported UNDERPOWERED, not removed
```

Authority: `launchers/LAUNCHER_02_rt0_rt7_definition.md` §7 (`g6` row) and
`results/rt07_g4b_production_mapper/docs/G6_ANALYSIS_PLAN.md`. No new launcher was created.
Predeclaration: `control/PREDECLARATION.md`, written before any statistic existed.

---

## The question, and the answer

> After accounting for mapper visibility, completeness and sequence relatedness, does the
> frozen conserved-state representation reveal **reproducible** organization of RT diversity
> between labelled families and within Retrons?

**Yes under the cluster-level null, no under the sequence-level null, in both arms** — and the
disagreement between those two nulls *is* the result. The strongest single statement the
evidence supports:

> **When the confound the sequence-level null was built to absorb — mapper visibility — is
> controlled directly, the structure exceeds BOTH nulls.** All three visibility-restricted
> analyses and all three relatedness-collapsed analyses exceed both. Only the full,
> visibility-heterogeneous population fails the sequence-level null, which is exactly where
> that null's known defect bites hardest.

## Terminal verdicts

| arm | labelling | ρ | NULL-1 p99 | NULL-2 p99 | verdict |
|---|---|---|---|---|---|
| between-family | 42 families, 36 qualifying | **0.9865** | 0.9906 ✗ | 0.9066 ✓ | `REPRODUCIBLE_UNDER_CLUSTER_NULL_ONLY` |
| within-Retron | DefenseFinder subtype (10 strata) | **0.8917** | 0.9814 ✗ | 0.8158 ✓ | `REPRODUCIBLE_UNDER_CLUSTER_NULL_ONLY` |
| within-Retron | PADLOC subtype (14 strata) | **0.9595** | 0.9782 ✗ | 0.6687 ✓ | `REPRODUCIBLE_UNDER_CLUSTER_NULL_ONLY` |
| within-Retron | label-free, 0.30 clusters (5 groups) | 0.8061 | 0.9657 ✗ | — | `UNDERPOWERED` |

The between-family controls, each against its own null on its own population:

| control | ρ | NULL-1 p99 | NULL-2 p99 | exceeds |
|---|---|---|---|---|
| CTRL-VIS mapped_fraction [0.0,0.5) | 0.9399 | 0.8855 | 0.6808 | **both** |
| CTRL-VIS [0.5,0.8) | 0.9801 | 0.9671 | 0.6365 | **both** |
| CTRL-VIS [0.8,1.01) | 0.9885 | 0.9752 | 0.8426 | **both** |
| CTRL-REL one rep / 0.90 cluster | 0.9959 | 0.9824 | 0.9832 | **both** |
| CTRL-REL one rep / 0.50 cluster | 0.9855 | 0.9668 | 0.9655 | **both** |
| CTRL-REL one rep / 0.30 cluster | 0.9915 | 0.9708 | 0.9664 | **both** |
| CTRL-COMP all_complete | 0.9819 | 0.9906 | 0.9113 | NULL-2 only |
| CTRL-COMP all_partial | 0.9456 | 0.9839 | 0.9043 | NULL-2 only |
| CTRL-COMP mixed_or_codon_evidence | 1.0000 | 1.0000 | 1.0000 | `UNDERPOWERED` — 3 groups |

## Populations

| | n | role |
|---|---|---|
| CATALOGUE | 501,561 | context only. **Never a denominator here.** |
| ELIGIBLE (`G5_ELIGIBLE_N`) | 369,381 | clustering input; visibility statements |
| **INSPECTABLE** (`verdict == MAPPED`) | **354,102** | **every architecture number** |
| Retron eligible / inspectable | 61,395 / 53,722 | the within-Retron arm |

Call-state totals over 55,407,150 state calls: MAPPED 40,217,506 (0.7259) · AMBIGUOUS 2,685,768
(0.0485) · UNSUPPORTED 2,559,452 (0.0462) · DELETED_STATE 9,944,424 (0.1795). The mean MAPPED
fraction 0.7259 **independently reproduces** `G6_READINESS.md` §5, which was computed by a
different gate from the same dataset.

## The sequence-relatedness resource

No existing clustering resource was reusable. The best candidate
(`…RETRON-DB_V3/…/cluster_work/full_id*.tsv`) fails on **three independent grounds** recorded in
`tables/g6_clustering_reuse_audit.tsv`: a different input population (397,445 unique members,
not 369,381), an identifier space that is **contig/locus IDs rather than `rt_hash`** — and the
research contract records that no `rt_hash → locus` link exists — and **no pinned tool
version**. Audit bounded to exactly what reuse required; nothing further was inspected.

Built instead, **label-blind** (amino-acid sequence is the only input; no family label, tool
label, taxonomy or state call participates): `mmseqs 18.8cc5c easy-linclust` over exactly the
369,381 eligible sequences, `-c 0.8 --cov-mode 0`, at identity 0.90 (primary, **181,696
clusters** — a 51 % collapse, so redundancy is substantial and the control matters), plus 0.50
and 0.30 as sensitivities.

## The repair — one cycle, spent

`control/REPAIR_1.md`. The declared NULL-1 permutes labels at **sequence** level. Measurement
showed **99.92 % of clusters span exactly one family**, so that permutation destroys a nuisance
structure present in almost all the data and makes the null *easier than the alternative* —
forbidden by Principle 12. NULL-2 permutes whole **clusters** instead.

**NULL-1 is retained in full, not deleted.** And NULL-2 is not correct either: it breaks the
*between-cluster* relatedness that makes a real family a set of related clusters, so it errs
anti-conservatively. The two bracket the truth and both are reported everywhere.

## Controls

| control | result | observed |
|---|---|---|
| PC-POS — known-present signal recovers | **PASS** | catalytic (`CAT_STATE` 262, `CATALYTIC_CONFIRMED`) cross-half Spearman **0.9230** over 36 families |
| PC-SPLIT — half independence, **measured** | **MEASURED** | 3,000 vs 3,000 sequences, 14,943 hits: median identity 0.5620, p95 0.9890, **11.22 % of hits at ≥ 0.90** |

## The six adversarial questions (BS-14)

**1 · Where is each headline claim overstated — name the word.**
The word is **"organization"**. ρ measures whether a *between-group distance matrix* replicates
on held-out clusters. It does **not** show that the groups are biologically distinct, that the
distances are meaningful, or that any particular state drives them. The second word is
**"reproducible"** — reproducible *across halves of this dataset under this instrument*, not
across instruments, alignments, or `-M` settings. The third is **"within Retrons"**: what
replicates is structure across **tool-assigned subtype strata**, which are annotations, not
biology, and the one labelling that used no tool at all came back `UNDERPOWERED`.

**2 · What specific alternative explanation produces this exact number?**
**Residual cross-half sequence identity.** PC-SPLIT measured it rather than assuming it away:
11.22 % of cross-half hits are at ≥ 90 % identity, because linclust is greedy and approximate,
so some near-identical pairs land in different clusters and therefore different halves. Leakage
inflates ρ. It inflates the nulls too, so it partly cancels in the comparison — but not
symmetrically, because real families concentrate their near-duplicates within a family while
permuted labels scatter them. The mitigation is already in the table and was not invented
afterwards: **CTRL-REL@0.30**, one representative per 30 %-identity cluster, is the analysis
least exposed to this, and it still exceeds **both** nulls (0.9915 vs 0.9708 / 0.9664).
A second alternative for the primary: the whole effect is visibility composition. **CTRL-VIS
refutes that specifically** — within narrow `mapped_fraction` bands, where visibility is nearly
constant, ρ stays 0.94–0.99 against nulls of 0.64–0.88.

**3 · Could this test have returned a negative?**
Yes, and part of it did: `LABEL_FREE` returned `UNDERPOWERED`, and the *declared* primary test
against the *declared* NULL-1 **failed** — that failure is what triggered the repair rather
than being quietly dropped. Four ways to fail were fixed in advance: ρ below the 0.50 effect
floor, ρ inside the null, no computable null, and fewer than 5 qualifying groups. Three of the
four actually fired somewhere in the table.

**4 · The unit of every rate.**
ρ is a Spearman correlation between the upper triangles of two between-group correlation-distance
matrices — **unitless**, denominator = the number of group pairs, which is `n_groups × (n_groups
− 1) / 2` and is stated per row. MAPPED fraction = MAPPED anchor calls ÷ **150 frozen anchor
states**, per sequence. Per-family profiles use **that family's own inspectable count**, never a
pooled one. Catalytic numbers use `CAT_STATE`-MAPPED as their denominator and are never pooled
with the 150 anchors. Cluster collapse ratio = clusters ÷ 369,381 eligible.

**5 · Which numbers have no producing script?**
None in `tables/`. Every artifact names its producing script in `MANIFEST.tsv`. The only
figures quoted here that this gate did not compute are the g5 population constants (501,561 /
369,381 / 354,102), which come from the landed g5 bundle and are re-verified by `run.sh` calling
`results/rt07_g5_catalogue_application/verify.sh` before any analysis runs.

**6 · What was withdrawn or weakened?**
- **The declared NULL-1 was found invalid and replaced** (`REPAIR_1.md`) — the one permitted
  repair cycle, now spent. NULL-1 is retained and reported everywhere, and the headline is a
  bracket rather than the convenient endpoint.
- **`LABEL_FREE` was downgraded to `UNDERPOWERED`**: only 5 of 11,301 candidate groups
  qualified, and every permutation replicate fell below the stratum threshold, so no null
  exists. "Not reproducible" cannot be asserted against a null that does not exist.
- **`CTRL-COMP[mixed_or_codon_evidence]` was downgraded to `UNDERPOWERED`** despite ρ = 1.0000:
  3 groups give 3 pairwise distances and ρ saturates trivially.
- **20 of 50 retron subtype strata are `UNDERPOWERED`** (< 100 inspectable) and are excluded
  from the distance matrices while still being reported.
- **A diagnosis was wrong and is recorded, not hidden** (`control/EXECUTION_INCIDENTS.md`): an
  analysis step was declared dead on the basis of a `ps` check that is namespace-limited in this
  sandbox and could not have seen it, and an unevidenced "memory contention" cause was asserted
  while 230 GB of 251 GB was free. The step had never stopped. No number was affected.

## What this gate did NOT do

No historical RT0–RT7 label appears anywhere; states are bare `state_id`. **`results/rt07_g7a_rt0_rt7_bridge/`
is sealed external context and was not read** — not by any script, not as an input — enforced by
`verify.sh` V1/V2 and asserted in `seal.py`. The g7a crosswalk may be applied to these results
only *after* this gate is frozen.

No mapper re-running, re-tuning or re-validation. No accuracy claim against any tool label. No
universal-RT-architecture claim. No absence claim: `DELETED_STATE` is an alignment-path
statement and is never read as "this family lacks this region". No palm/fingers/thumb, motif
discovery, phylogeny, ncRNA, embeddings or co-evolution. Scope is `-M 50` only.

## Claims

`C4` primary, `C3` supporting. **No claim is promoted by this bundle.** Status lives only in
`idea-stage/docs/research_contract.md`, where both remain `UNPROVEN`.
