# ERRATA — `g6` family architecture, from the independent BS-15 review

Date: 2026-09-19 · Track `rt07` · Status: **8 required repairs applied as errata · bundle UNCHANGED**

Review: `review-stage/INDEPENDENT_REVIEW_RESULT_g6.md` — Codex `gpt-5.6-sol`, thread
`01a0b99f`, `PASS_WITH_REQUIRED_REPAIRS`, 6/10, **0 blockers**.

**This record is additive.** `results/rt07_g6_family_architecture/` is frozen and sealed; no
file in it is edited, regenerated or re-sealed, and **no analysis is recomputed**. Where this
record and the bundle's own prose disagree, **this record governs interpretation**; the bundle's
numbers stand as landed. The bundle's `README.md`, `tables/g6_terminal_decision.tsv`, and the
decision records `2026-09-18_stage2_g6_closure.md` and
`2026-09-18_stage2_g6_bs15_open_and_bounded_use.md` are read through this erratum.

---

## E-g6-1 · What g6 supports: concordance, not discovery — REQUIRED

**Superseded framing:** "reproducible organization in the frozen conserved-state space";
"family architecture"; any wording implying independent discovery of RT family structure.

**Governing interpretation:**

> The between-family grouping in g6 is **essentially MyRT-derived**: on the eligible set,
> `stage1_collapsed_family` equals the raw MyRT label on **369,370 of 369,381** records (11
> `RVT-CRISPR|RVT-CRISPR-like` exceptions); **363,447** carry a direct `by_myRT` call; the
> **5,934** without one are all labelled `Retron`. g6 therefore supports **reproducibility and
> concordance of the mapper-derived conserved-state descriptor across MyRT-defined strata and
> related subtype groupings** (DefenseFinder and PADLOC retron subtypes, each a tool annotation
> with its own denominator). **It does not support independent discovery of biological RT
> family structure.**

Both the grouping (MyRT, an RVT profile-HMM search with similarity and phylogenetic placement)
and the measurement (occupancy under a GII-derived profile HMM) are sequence/profile-derived, so
the two share modality. The pure-sequence-partition counter-test (C2: 61 groups, ρ = 0.8689,
NULL-2 p99 = 0.8779) shows that beating NULL-2 is not automatic for every sequence partition;
it does **not** establish independence or remove partial circularity, and its p99 rests on only
40 permutations.

Required caption wording for any g6 figure: *"split-half concordance among predominantly
MyRT-derived family strata in a GII-HMM-derived occupancy space."*

## E-g6-2 · Withdraw "the truth is bracketed" and "the structure is real" — REQUIRED

**Superseded:** "the two bracket the truth" (bundle `README.md:98`; `CURRENT_PROJECT_STATE.md`);
"the headline is a BRACKET"; "`REPRODUCIBLE` — structure is real" under NULL-2
(`tables/g6_terminal_decision.tsv:2`).

**Governing interpretation:** the sequence-level null (NULL-1) and the cluster-level null
(NULL-2) are **two sensitivity analyses with opposite qualitative biases**. They are **not
proven bounds**: nothing shows that the correct null distribution, or biological truth, lies
between them. The honest statement is that the observed statistic **exceeds one imperfect
permutation distribution and not the other** for the full between-family arm.

The reporting practice of showing both nulls side by side is retained; only the "bracket" and
"real" language is withdrawn.

## E-g6-3 · Qualify "exceeds BOTH nulls" — REQUIRED

**Superseded:** "every visibility-restricted and every relatedness-collapsed analysis exceeds
BOTH nulls", read as 1 %-level significance.

**Governing interpretation:** the six rows are **numerically correct** — each observed ρ exceeds
the reported p99 of both nulls and in fact every one of the sampled replicates. But:

* **60 permutations cannot calibrate a 1 % tail.** The smallest ordinary Monte-Carlo p-value
  with 60 replicates is 1/61 ≈ **0.0164**.
* **No multiplicity control** was applied across the **13** analyses.

Permitted: *"the observed concordance exceeds every sampled replicate from both reported
permutation procedures on those six populations."*
**Not permitted:** "significant at 1 %", "significant across the family of analyses", or any
claim that the result is proof against all mapper-visibility artefacts.

## E-g6-4 · Subtype power: 26 of 50 strata excluded, not 20 — REQUIRED

**Superseded:** "20 of 50 retron subtype strata are `UNDERPOWERED`" (bundle `README.md:161`;
`2026-09-18_stage2_g6_closure.md:88`).

**Cause:** the strata table labels power by **≥ 100 inspectable in total**
(`scripts/s04_within_retron.py:121`), but the statistic requires **≥ 100 in each half**
(`scripts/arms.py:123`).

**Corrected count — verified in this erratum from landed tables only, nothing recomputed:**

| tool | marked `powered=YES` in `g6_retron_subtype_strata.tsv` | actually entered, per `g6_within_retron_rho.tsv` `n_groups` | marked powered but excluded |
|---|---|---|---|
| DefenseFinder | 12 | 10 | **2** — `Retron_VII_1` (152), `Retron_VII_2` (140) |
| PADLOC | 18 | 14 | **4** — `retron_IX` (201), `retron_VII-A2` (174), `retron_VII-A1` (125), `retron_X` (102) |

**20** marked underpowered + **6** marked powered but excluded = **26 of 50 strata did not
enter a distance matrix.** The within-Retron ρ values themselves are unaffected; only the
reported exclusion count was wrong.

## E-g6-5 · Report both leakage quantities — REQUIRED

**Superseded:** the single figure 11.2 % presented as the leakage rate.

**Governing interpretation — carry both, each with its unit:**

| quantity | value | unit | source |
|---|---|---|---|
| **fraction of retrieved hits** at identity ≥ 0.90 across halves | **11.2 %** (11.22 %, of 14,943 hits) | retrieved hit | bundle `tables/g6_controls.tsv:2` |
| **fraction of sampled queries** with at least one ≥ 0.90-identity opposite-half partner | **19.8 %** (595 / 3,000) | sampled half-A query | reviewer's read-only parse of the landed search output |

Limitations that travel with both: the search keeps at most **five targets per query**
(`--max-seqs 5`, `scripts/s05_controls.py:45`), and the 19.8 % is a **one-direction,
3,000-query sample**, not a full symmetric leakage rate over the dataset. Neither figure may be
quoted without its unit.

Related: a ≤ 30 %-identity **clustering** threshold does not guarantee that every cross-half
pair is ≤ 30 % identical. No claim of guaranteed ≤ 30 %-identity train/test separation is
permitted.

## E-g6-6 · Disclose the post-hoc procedural additions — REQUIRED

The predeclaration (`control/PREDECLARATION.md:134`) specifies NULL-1 and a single
significance rule. The following were **added after predeclaration** and are hereby disclosed
as post-hoc:

1. applying **both** nulls to **every** analysis (`scripts/s03_between_family.py:22`);
2. the **five-group** minimum for an analysis to report ρ (`scripts/s07_decision.py:23`);
3. the rule **"missing null → `UNDERPOWERED`"** (`scripts/s07_decision.py:32`).

The bundle's single `REPAIR_1.md` does not establish that only one analytic decision changed.
The exact chronology relative to observing the PRIMARY result cannot be reconstructed from the
single landed commit and is recorded as unknown.

## E-g6-7 · The rank statistic uses non-standard tie handling — REQUIRED, disclosed not re-run

* **The statistic g6 reports as Spearman ρ used non-standard tie handling.** `_spearman`
  (`scripts/arms.py:99`) ranks with `argsort(argsort())`, which assigns tied values distinct
  consecutive ranks instead of averaging them.
* **The standard tie-aware Spearman would differ slightly.** On the landed positive-control
  counts the reviewer obtained **0.9230** with the bundle's method against **0.9307** with
  standard tie-aware Spearman — same conclusion, different value.
* **The per-half distance vectors needed to recompute the headline ρ values under standard tie
  handling were not landed**, and the null replicates are summarised only as median/p99/max.
* **Therefore the original results remain frozen as reported**, and every g6 ρ must be read as
  *"a rank correlation with ordinal tie-breaking"*, not as standard Spearman where ties exist.
  **No re-run is authorised by this erratum.** A future task may authorise one explicitly.

## E-g6-8 · Narrow the visibility claim — REQUIRED

**Superseded:** "the structure is not an artefact of the mapper's visibility gradient"
(`CURRENT_PROJECT_STATE.md`).

**Governing interpretation:** the visibility control (CTRL-VIS) shows the concordance
**persists after conditioning on the scalar total MAPPED fraction**. It does **not** eliminate
state-specific GII-HMM callability effects or the shared sequence/profile modality in E-g6-1.
Full-profile distance correlates with the absolute difference in mean MAPPED fraction at
ρ = 0.5692 (C4) — a substantial association, **not** "56.92 % explained".

## Advisory notes (not required repairs)

* **Cold rerun.** `run.sh` does not clear scratch; clustering and PC-SPLIT reuse existing files
  (`scripts/s01_clustering.py:114`, `scripts/s05_controls.py:45`). A cold rerun was achieved,
  but `run.sh` is not intrinsically cold.
* **Sealing coverage.** Two `__pycache__` files sit inside the bundle and are deliberately
  excluded from sealing (`scripts/seal.py:95`). "Every file sealed" would be inaccurate.
* **Label-free underpowering (C9).** The reason every label-free NULL-2 replicate was discarded
  is not recoverable from the landed summary; NaN ρ can also arise from degeneracy.

## Bounded use — upheld, with the captions above

| use | status |
|---|---|
| g6 as a reproducible **descriptive** analysis | **CLOSED** |
| descriptive figures | **PERMITTED — only with E-g6-1, E-g6-3, E-g6-4, E-g6-5 captions**; not "as-is" |
| Stage-3 structural mapping on frozen `state_id`, with visibility/occupancy caveats | **PERMITTED** |
| thesis-level biological claims | **BLOCKED** — on the evidence, not merely pending review |
| classification reassessment | **BLOCKED** |
| any claim of independent validation | **BLOCKED** |
