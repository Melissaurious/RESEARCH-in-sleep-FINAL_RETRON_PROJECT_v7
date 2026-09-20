---
task_id: T-P1b-identity-partition
supersedes: T-P1-relatedness-backbone (VOID, preserved exactly as executed, nothing inherited)
governance_base: 9a793c9
base_commit: 0a220e3
base_branch: project-synthesis
base_rationale: |
  The authoritative scientific state is project-synthesis, NOT main. main is 94a1a78 plus
  ba3154a and predates the canonical dataset registry, the exposure ruling, the reconciliation
  and every Batch-02 outcome. A task frozen from main would inherit a state in which T-P1 is
  not yet VOID. The worktree branch is cut from the freeze commit itself, which descends from
  0a220e3.
stage_id: S03a
title: Cascaded sequence-identity partition of the exact-RT catalogue, label-blind and gated
state: AUTHORIZED
autonomy_tier: A
compute_class: CPU_MEDIUM (pilot) / CPU_HIGH (full)
preferred_backend: workstation (pilot) / ibex (full)
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-P1b-identity-partition
branch: task/T-P1b-identity-partition
output_directory: analysis/t_p1b_identity_partition/
hard_dependencies: []
populations_touched: ["RT-EXACT-501561 :: analysis_family=rt_identity_clustering :: INSPECTED_FOR_THIS_ENDPOINT"]
population_state: INSPECTED_FOR_ENDPOINT (operator ruling 2026-09-20 §1)
confirmatory_spend: none — the endpoint was already spent by T-P1, which is VOID
iteration_budget: 1
frozen: true
freeze_rule: WORKING_RULES §6b — launcher, implementation and fixtures frozen in ONE commit BEFORE execution
operator_authorisation: |
  D12 resolved 2026-09-20. Scientific review returned APPROVED WITH FOUR CORRECTIONS, all
  applied: (1) base is project-synthesis@0a220e3, not main; (2) the component input is the
  separately registered EXACT-BIPARTITE-COMPONENTS-14918, not PAIR-ELIG-30924; (3) duplicate
  control wording corrected; (4) catalogue monotonicity framed as an algorithm-dataset
  diagnostic. PILOT AUTHORISED. The full 501,561 run is NOT authorised and needs a separate
  decision after the pilot report.
---

# T-P1b · sequence-identity partition of the exact-RT catalogue

✅ **FROZEN.** This launcher, `p1b_identity_partition.py`, `p1b_fixtures.py` and
`FIXTURE_MANIFEST.tsv` entered git together, in one commit, **before** any run — `WORKING_RULES`
§6b. The run records that commit id.

**Authorised: the 10,000-sequence pilot only.** ⛔ The full 501,561-sequence catalogue run is **not**
authorised and requires a separate decision after the pilot report.

## 1 · The question

> **Can the exact-RT catalogue provide reproducible sequence-relatedness partitions at several
> resolutions that are useful for controlling shared RT ancestry in downstream comparisons?**

## 2 · ⛔ Interpretation ceiling — binding on every output

This task establishes **sequence-relatedness structure only**. It is:

- **not** a phylogeny;
- **not** evolutionary lineage truth;
- **not** a system of biological clades;
- **not** a replacement RT classification;
- **not** a designation of any threshold as "the lineage boundary".

The deep RT tree has been measured **not to resolve** — 312 trees, 157 alignable characters,
1.39 taxa/character — and nothing here changes that. Clusters are a **nuisance / blocking /
sensitivity structure** for controlling shared ancestry in downstream comparisons. A downstream
task may use them to separate retron-associated features from shared ancestry; it may **not** call
them clades.

## 3 · Population and exposure

| | |
|---|---|
| population | `RT-EXACT-501561` — all 501,561 exact RT sequences |
| analysis family | `rt_identity_clustering` |
| exposure | **`INSPECTED_FOR_THIS_ENDPOINT`** — already spent by `T-P1`, which is VOID. A VOID run still spends its endpoint (operator ruling §1) |
| confirmatory spend | **none** |
| inference unit | exact RT sequence in; **cluster** out |

## 4 · Inputs, and the gate that runs before anything else

| input | path | role |
|---|---|---|
| exact-RT catalogue | `…_v7/data/derived/rt_exact_v1.faa` | **the only input to cluster formation** |
| **`EXACT-BIPARTITE-COMPONENTS-14918`** | derived from `…_v7/data/derived/rt_ncrna_exact_pairs_v1.parquet`, sha256 `b89df680…3dae` | component derivation — **registered separately, see §4b** |
| landed component summary | `…_v7/results/dbchar_g3_pair_geometry/tables/g3_topology_components.tsv`, sha256 `aaf0fe7f…8674` | reproduction target |
| family baseline | `…_v7/data/derived/rt_family_baseline_v1.parquet` | ⚠️ **post-hoc description ONLY**, opened after every cluster file is written |

### 4b · ⛔ The component input is a separately registered asset, not `PAIR-ELIG`

`rt_ncrna_exact_pairs_v1.parquet` is the source file behind **`PAIR-ELIG-30924`**, which is
**`EXPLORATORY_ONLY`** — permanently exhausted for pairing inference. `WORKING_RULES` §8 permits a
task to consume only `CANONICAL` or `CANONICAL_WITH_LIMITATION`. **That conflict is resolved by
registration, not by bypass.**

The object this task consumes is **`EXACT-BIPARTITE-COMPONENTS-14918`**, registered in
`programme/CANONICAL_DATASETS.tsv` as `CANONICAL_WITH_LIMITATION`, with its own source hash
(`b89df680…3dae`, computed for this purpose — it was not previously recorded anywhere), its
derivation rule, and its reproduction target.

> **The distinction is the object, not the file.** `PAIR-ELIG-30924` is the *pairing endpoint* —
> does RT *x* go with ncRNA *y*. `EXACT-BIPARTITE-COMPONENTS-14918` is the *graph topology* — who
> shares an exact sequence with whom. Union–find over exact-identity edges spends no pairing
> endpoint, because it asks no pairing question and produces no pairing answer.

⛔ **The limitation is binding and is carried in the registry:** any use of this topology that
makes, supports or weakens a claim about **pairing** *is* a pairing endpoint, and is forbidden
under `PAIR-ELIG`'s permanent exhaustion. `T-P1b` uses it only to ask whether an identity partition
crosses exact-sequence-sharing boundaries.

⚠️ **Skew, declared in advance:** 12,079 of the 14,918 components are 1:1 singletons and the largest
holds **706** RTs. Component-level statistics are dominated by a handful of components, and the
incidence distribution is reported in full rather than summarised to a mean.

### 4a · ⛔ GATE 0 — input identity, before any clustering

```
sha256(rt_exact_v1.faa) == bcde6e9a64de90e6e791256f79c87799a00a95f0d1730f3460301220379e2655
record count            == 501,561
```

**Either mismatch is a STOP before clustering.** `T-P1` ran on **501,861** sequences after a
mid-run scope change. This gate makes that impossible rather than discoverable afterwards.

## 5 · Label-blind by construction

**`cluster()` takes exactly one data input: a FASTA path.** No family label, no MyRT / PADLOC /
DefenseFinder call, no ncRNA call and no taxonomy is an input to cluster formation, threshold
selection or acceptance — at any level.

Stated precisely, because a reviewer will check it:

| file | opened where | relative to clustering | can it influence a cluster? |
|---|---|---|---|
| `rt_exact_v1.faa` | `cluster()` | **the only clustering input** | — |
| `rt_family_baseline_v1.parquet` | `describe()` **only** | **after** every cluster file is written | **no** |
| `EXACT-BIPARTITE-COMPONENTS-14918` (from `rt_ncrna_exact_pairs_v1.parquet`) | control `C5`; then incidence | `C5` runs before clustering; incidence **after** the loop | **no** — `C5`'s expected value (14,918) is fixed in advance and independent of any clustering, and neither call feeds `cluster()` |

Enforced by ordering, not merely asserted: in `run_primary()` the clustering loop completes before
`derive_components()` and `describe()` are called.

**Labels appear only in** `P1b_cluster_family_composition.tsv` and `P1b_cross_family_clusters.tsv`,
as post-hoc description.

## 6 · The declared MMseqs2 procedure, fixed in this commit

```
mmseqs easy-cluster <in.faa> <prefix> <tmp>
    --min-seq-id   {0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95}
    -c             0.80
    --cov-mode     0        # bidirectional coverage
    --cluster-mode 0        # greedy set cover
    -s             7.5      # sensitivity, raised from default
    --max-seqs     1000     # prefilter depth, raised from default 300
    --threads      <N>
    -v 1
```

**Version:** MMseqs2 `18.8cc5c`, at `/home/borg/miniconda3/envs/retron_tradicional/bin/mmseqs`,
in the project's primary environment. Recorded in `logs/run_log.json` at run time.

**Seed:** `20260920`, used only for fixture construction and pilot sampling. Clustering itself is
deterministic given the input and these parameters.

### 6a · Ladder and monotonicity — direction stated, nesting NOT claimed

Ladder: **40, 50, 60, 70, 80, 90, 95 %**. ⛔ **No level is designated the lineage threshold.**

> **Declared monotonicity.** Traversing the ladder **40 % → 95 %**, i.e. as the minimum identity
> threshold becomes **stricter**, the number of clusters is expected to be **non-decreasing**.

⚠️ **Cluster-count monotonicity and partition nesting are different properties, and only the first
is asserted.** Cascaded MMseqs2 clustering does not mathematically guarantee that the partition at
90 % refines the partition at 80 %, so no nesting requirement is imposed.

> **Nomination, not a finding.** `T-P1`'s landed `P1_level_summary.tsv` reads 53,289 → 68,233 →
> 116,186 → 150,268 → 189,780 → 234,722 → 266,964 — **strictly increasing at every adjacent pair**,
> in the direction declared above. Its review nonetheless recorded *"monotonicity fails at every
> adjacent pair"*, which is inconsistent with its own landed table and suggests the check tested the
> inverted direction. **This is recorded as an erratum candidate and nothing more. `T-P1` is not
> reopened and is not rehabilitated** — controls that never gated, two that never ran, a duplicate
> control that failed and was reported as a pass, and controls appended to the primary input remain
> independently sufficient for VOID.

## 7 · Sequence-content policy — declared in advance, flag before filtering

**No sequence is filtered. The denominator is never silently reduced.**

Measured during design review and **to be re-derived by the task rather than inherited**:

| property | measured at design time |
|---|---|
| sequences | 501,561 |
| trailing `*` | **0** |
| contain `U` (selenocysteine) | 22,263 |
| contain `X` (unknown) | 5,539 |
| length min / median / max | 20 / 384 / 10,449 aa |
| length < 250 aa | 108,439 (21.62 %) |

**How MMseqs2 handles each, verified empirically at design time, not assumed:**

| case | behaviour | policy |
|---|---|---|
| `U` | accepted; clusters normally | retained, unmodified |
| `X` | accepted; clusters normally | retained, unmodified |
| very short (20 aa) | accepted; forms a singleton under `-c 0.8` | retained; singleton status is a **result**, not an error |
| very long (10,449 aa) | accepted | retained |
| unprocessable, if any | — | ⛔ **retained in `P1b_exclusions.tsv` with an explicit reason.** Never dropped |

⚠️ **22,263 sequences carrying `U` is high for selenoproteins and may indicate a translation-table
or provenance artefact. That is a NOMINATION, not a conclusion, and not this task's scope.**

## 8 · Components — the threshold-free definition, pinned

The incidence output uses the **exact RT–ncRNA bipartite connected components**:

| | |
|---|---|
| source | `results/dbchar_g3_pair_geometry/tables/g3_topology_components.tsv` |
| sha256 | `aaf0fe7f9100886b40d59eb026360fbdd640760e75263732a50576112d3a8674` |
| expected count | **14,918** |
| shape breakdown | 1:1 12,079 · 1:many 179 · many:1 2,293 · many:many 367 = **14,918** |
| RT / ncRNA covered | 29,192 / 16,458 |

⛔ **NOT the 1,075 components in `CROSSFIT_META.json`.** That file states its own reason:
`G_arm = ESM-C representation of the frozen rt_id0.50 cluster representative`. Those components
**already embed a 50 %-identity clustering**, so comparing a new identity partition against them
would be partly circular. The 14,918 are threshold-free and label-free.

The task **derives** the components itself by union–find over the bipartite graph and must
reproduce **14,918** against the landed summary — an implementation-reproduction control that
consumes **no** `T-P1` output.

> ⚠️ **Multiple relatedness groups inside one component are an EXPECTED MEASURABLE OUTCOME, not a
> task failure.** Quantifying that distribution is a deliverable.

## 9 · Controls — all blocking, all on separate fixtures, **already verified attainable**

⛔ **No control sequence is appended to, mixed with, or modifies the primary catalogue.** Each runs
on its own file in its own MMseqs2 invocation. That is the defect that voided `T-P1`.

### 9a · The duplicate criterion and its independent justification

**Declared expectation: 100/100 at every level.**

**The justification is the algorithm, not the observation.** Two identical sequences align to **each
other** at identity 1.0 and coverage 1.0 — the maximum attainable — so each is the other's
top-scoring hit, and no third sequence can outscore it. (They also have *identical* scores to every
other sequence, since they are the same string; that is what makes their prefilter lists
interchangeable, but it is not itself the argument.) The only mechanism by which they can fail to
co-cluster is therefore **prefilter saturation** — the prefilter retaining only the top `--max-seqs`
hits, and the twin falling outside that list in a dense neighbourhood.
The fixture is **200 sequences against `--max-seqs 1000`**, so saturation **cannot occur at this
size**. 100/100 therefore follows from the declared procedure.

This is also the concrete explanation for `T-P1`'s **98/100**: its duplicates were injected **into
the 501,861-sequence primary input**, where saturation is possible. Running the fixture standalone
removes the mechanism rather than tolerating it. ⛔ **98/100 is not inherited as a threshold.**

⚠️ **Declared limitation.** A fixture control shows the procedure co-clusters identical sequences;
it does **not** show that prefilter saturation never occurs at catalogue scale. That is why
`--max-seqs` is raised to 1000 and `-s` to 7.5, and why a **non-blocking diagnostic** reports
catalogue-scale monotonicity separately (§9c).

### 9b · The control table, as executed on fixtures 2026-09-20

| control | type | blocking | expectation | observed | state |
|---|---|---|---|---|---|
| `P1b_GATE_input_sha256` | positive | **YES** | catalogue sha256 matches | `bcde6e9a…2655` | **PASS** |
| `P1b_GATE_input_records` | positive | **YES** | exactly 501,561 records | 501,561 | **PASS** |
| `P1b_GATE_component_source_sha256` | positive | **YES** | component source sha256 matches | `b89df680…3dae` | **PASS** |
| `P1b_POS_duplicate_id{40…95}` | positive | **YES** | 100 duplicate pairs co-cluster, each level | **100/100 × 7** | **PASS** |
| `P1b_NEG_shuffled_id{40…95}` | negative | **YES** | 0 composition-matched shuffles co-cluster | **0/100 × 7** | **PASS** |
| `P1b_POS_monotonic_40_to_95` | positive | **YES** | cluster count non-decreasing 40→95 | 61 ≤ 77 ≤ 91 ≤ 94 ≤ 98 ≤ 98 ≤ 98 | **PASS** |
| `P1b_POS_edgecase_completeness` | positive | **YES** | U, X, all-U, 20 aa, 12×-long, unrelated all assigned | 7/7 | **PASS** |
| `P1b_POS_reproduce_components` | positive | **YES** | components derived == 14,918 | derived 14,918, g3 sha256 match | **PASS** |

**20 blocking controls, 20 PASS.** Positive and negative fail in **opposite** directions: a
cluster-everything procedure fails the shuffled negative, a cluster-nothing procedure fails the
duplicate positive.

### 9c · On the primary input

| control | type | blocking |
|---|---|---|
| `P1b_POS_primary_completeness` | positive | **YES** — every input sequence assigned at every level; any exception retained in `P1b_exclusions.tsv` |
| `P1b_DIAG_primary_monotonic` | **diagnostic** | **NO** — catalogue-scale cluster-count monotonicity is **reported, not gated** |

⚠️ **§9c's second row is deliberate.** `WORKING_RULES` §6a: a control exists to show the
*implementation* works. Demanding a shape of the real catalogue is what killed three successive
`T-N1` null designs. The blocking monotonicity check runs on the fixture; the catalogue-scale
number is a measurement.

⛔ **What the catalogue-scale number is, and is not.** It is an **algorithm–dataset diagnostic**:
the behaviour of *this* MMseqs2 procedure, at *these* parameters, on *this* catalogue. It is a
joint property of the instrument and the data. It is **not** a biological property of reverse
transcriptases, and a non-monotone result would say something about cascaded clustering on a
corpus with this length and redundancy structure — **not** about RT evolution.

## 10 · Pilot — 10,000 sequences, deterministic, label-blind

**Sampling rule, fixed in this commit and in `pilot_selection()`:**

1. Sort all `rt_id` lexicographically, so the sample does not depend on file order.
2. Take four **edge-case strata of 100 each**, by **sequence property only**: the 100 shortest,
   the 100 longest, 100 containing `U`, 100 containing `X`.
3. Fill the remainder to 10,000 from a `random.Random(20260920)` shuffle of everything not already
   taken.
4. Emit sorted.

⛔ **No family, tool, taxonomy or ncRNA label is read at any point in the selection.** Every
criterion is a property of the sequence itself.

**Pilot PASS concerns implementation only:** correct input handling · control behaviour · complete
and reported assignment · correct output schema · computational feasibility.

⛔ **Unexpected biological cluster composition is NOT a pilot failure.**

## 11 · Full run — separate authorisation

⛔ **The 501,561-sequence run does NOT follow automatically from a passing pilot.** It requires a
separate operator authorisation after the pilot report is reviewed.

Backend: Ibex, `CPU_HIGH`, ~32 CPU / 120 GB. ⚠️ `batch` showed **7 idle nodes** at design time —
expect to queue. Staging the catalogue is local `IO_MEDIUM` and is declared here rather than
discovered.

## 12 · Outputs

| file | unit | contents |
|---|---|---|
| `P1b_clusters_id{40,50,60,70,80,90,95}.tsv` | exact RT | `rt_id`, `cluster_rep`, `cluster_id` |
| `P1b_level_summary.tsv` | level | `n_input`, `n_assigned`, `n_unassigned`, `n_clusters`, `largest_cluster`, `median_cluster_size`, `n_singletons` |
| `P1b_cluster_family_composition.tsv` | cluster | **post hoc**: `n_members`, `n_distinct_families`, `dominant_family`, `dominant_family_fraction` |
| `P1b_cross_family_clusters.tsv` | level | `n_clusters`, `n_clusters_multi_family`, `fraction_multi_family` |
| `P1b_component_incidence.tsv` | level × component | `n_distinct_clusters` per exact bipartite component |
| `P1b_component_multimembership.tsv` | level | distribution of distinct clusters per component |
| `P1b_exclusions.tsv` | level × RT | any unassigned sequence, **retained with a reason** |
| `P1b_controls.tsv` | control | the table in §9b |
| `logs/run_log.json` | — | mmseqs version, parameters, seed, input hashes, elapsed, blocking failures |
| `TASK_REPORT.md` | — | `WORKING_RULES` §5 contract |

## 13 · STOP conditions

| condition | action |
|---|---|
| catalogue sha256 or record count mismatch | **STOP before clustering.** No table written |
| any blocking control fails | **STOP.** `TASK_STATE: VOID`, no primary table, escalate, **new task ID** |
| a control failure after freeze | **STOP.** ⛔ **No threshold is modified after seeing a result** |
| a sequence cannot be processed | retained in `P1b_exclusions.tsv`; denominator unchanged |
| iteration budget (1) exhausted | escalate to the operator |

## 14 · Downstream scope

`T-P1b` produces the **relatedness representation and the incidence structure**. It does **not**
solve the downstream multi-membership statistical problem — `T-A0b` decides later how to model
components containing multiple relatedness groups.

## 15 · What this task may NOT conclude

Anything about phylogeny, lineage, clades, RT classification, or which identity threshold is
biologically meaningful. It reports that a partition is what it is.

## 16 · Nothing inherited from T-P1

⛔ No table, count, threshold, clustering assignment or claimed result from `T-P1` is consumed.
`T-P1` informs redesign and history only, and remains **VOID**.

## 17 · Dispatch

⚠️ **D4 is unresolved.** When execution is authorised, use only the currently authorised route —
manual `bash programme/launch_task.sh T-P1b-identity-partition`, or coordinator execution with
mandatory disclosure in the report. **Do not assume autonomous dispatch works.**
