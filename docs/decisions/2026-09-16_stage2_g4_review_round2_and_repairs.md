# DECISION — Stage-2 g4: round-2 review outcome, verified corrections, and the operator decisions that now gate the track

Date: 2026-09-16 · Track: `rt07` · Status: **stopped for operator decision**

**Supersedes** the specific statements of
`docs/decisions/2026-09-16_stage2_g4_identifiability_redesign.md` listed in §2 below.
That record is **not rewritten** and stays on disk as the reviewed object, with its hash
recorded in `review-stage/DESIGN_REVIEW_REQUEST_g4_round2.md`.

Supersede this record by a new record, never by rewriting it.

    round 2:  score 4 / 10,  verdict "not ready"   (threshold: score >= 6 AND verdict in {ready, almost})
    gate:     review_gate.py -> {"decision": "continue", "reason": "positive threshold not met"}

**`g4` NOT EXECUTED. `g5` NOT STARTED.**

---

## 1 · Why this session stopped instead of writing a round 3

`review_gate.py` returned `continue`, and the round budget permits rounds 3 and 4. The repairs
were not attempted anyway, for one reason:

**The three deepest blockers are scope decisions launcher §9b reserves to the operator.**

| blocker | why it is not this session's to settle |
|---|---|
| the portable object must be redefined as a **reference-coordinate projection**, because conserved-position membership has no external truth on a query sequence | launcher §9b — *"changing the project claim wording or the scientific question"* |
| `RVT-GII` is an **in-family** stratum, not family-novel; the transfer story of the whole track changes | changes what `g4`, `g5` and `g6` are measuring, and what the launcher's §7 gate rows assume |
| a **mandatory retron-transfer stop condition** is required: poor transfer may land as a result but must halt retron interpretation in `g5`/`g6` and trigger retron-specific re-planning | changes downstream stage scope |

Round 1 already recorded that repairs 2, 5, 6, 7, 12 and 13 *"change the scientific scope of
Stage 2 and require operator decisions before a round 2 design can be written."* That was not
acted on — a round-2 design was written anyway, and it is the round-2 design that just returned
4/10. Repeating the pattern a third time would be a process failure, not diligence.

Bounded specification repairs that are **not** scope decisions are listed in §3 and are ready to
apply the moment the scope questions are answered.

---

## 2 · Statements withdrawn from the round-2 record — verified, not conceded

Each was checked against the landed files in this session before being accepted. The reviewer
was right on all three, and the third finding is one the reviewer did not report.

### 2.1 `AC1` is mathematically unattainable — WITHDRAWN

`acceptance_criteria.tsv` AC1 required the catalytic `[YF]xDD` to fall inside the predicted
interval in **at least 95%** of 66 leave-one-out folds.

A literal motif scan of `results/rt07_g2_reference_reconstruction/reference/g2_reference_set.faa`
finds `[YF]xDD` in **56 of 66** proteins. The ceiling is **84.8%**, so AC1 could never pass
however good the instrument. The ten without the motif:
`S.t.nad1I4`, `P.a.ND5I4`, `M.p.atp9I1`, `E.g.psbCI4`, `L.b.psbCI4`, `A.l.orf456`,
`E.v.psbCI4`, `E.m.psbCI4`, `E.d.psbCI4`, `P.s.cpn60I`.

**Replacement (not yet applied):** the denominator becomes the **motif-positive** subset,
n = 56, declared as such; the 10 motif-negative proteins are reported separately as a distinct
population, never silently dropped. The 95% figure must be justified independently of the
observed 66 or replaced.

### 2.2 Rule `R-DYAD` is incoherent as written — WITHDRAWN

The rule stated that the catalytic motif may not enter derivation, scoring, features or
threshold selection, and that this is what makes Q03 and Q15 identifiable.

`g2_conserved_positions.tsv` columns **781–786 are all `conserved_strict = YES`** and all carry
`block_id_at_reported_point = 5`. The catalytic column **783 is itself one of the 81 derivation
labels.** M1 uses all 81 conserved positions; M2 uses the complete submitted alignment; M3 learns
conserved-column membership. **No proposed method can satisfy R-DYAD**, because the label set
contains the very columns the rule excludes.

**Replacement (not yet applied):** R-DYAD becomes an explicit **masking** rule — the motif
columns and a declared surrounding window are removed from the label set, from every profile and
embedding, and from threshold selection, with the masked window declared before execution.
Masking removes 6 of 81 labels from the most conserved region, so the masked instrument must be
re-derived, not patched. Until masking is specified and executed, **Q03 is not identifiable and
Q15 does not exist.**

### 2.3 The landmark is not unique per sequence — NEW, found while checking the review

**4 of 66** derivation proteins carry **two** `[YF]xDD` matches: `S.p.cox2I1`, `P.a.cox1I4`,
`M.p.SSUI1`, `P.li.co1I3`. Q03 specified no rule for multiple matches, so its estimand was
ill-posed on those four as well as undefined on the ten with none — 14 of 66 in total.

**Replacement (not yet applied):** a predeclared multiple-match rule, and reporting of
match multiplicity as a retained field.

### 2.4 "Every Stage-1 family is out-of-family by construction" — WITHDRAWN

Asserted in the round-2 record §4 and in `estimand_matrix.tsv` Q13,
`evaluation_arms.tsv` A4 and `bounded_sampling_plan.tsv`.

The 66 derivation proteins are group II intron ORFs; all 20 of the `bacterial` lineage group are
bacterial group II intron ORFs (`g2_reference_sequence_set.tsv`). Stage 1 contains **`RVT-GII` at
256,624 exact RTs** — its largest family. Absence of an attached Stage-1 metadata label does not
make group II intron RTs biologically out-of-family.

**Replacement (not yet applied):** `RVT-GII` is an **in-family / in-distribution** transfer
stratum. `Retron` and the other 40 labels are family-novel. Identity distance and family status
are reported **jointly**, never as one axis. The four g2 lineage groups additionally permit a
**leave-lineage-group-out** diagnostic that the round-2 design missed entirely.

**This session identified 2.4 independently, before the review returned.** It was not applied
then because the record was in flight.

### 2.5 "81 vs 82 across independent frames" as evidence of stable membership — NARROWED

`g2_second_frame.tsv` records `AGREE_IN_MAGNITUDE`, and `s05_second_frame.py` declares counts
agreeing whenever they differ by no more than 50%. That is **count** agreement. The reviewer's
own LtrA remapping gives **Jaccard 0.862, 75 shared positions of 87 in the union** — good, but
not the identity of membership the round-2 record implied, and **not landed anywhere**.

**Replacement (not yet applied):** land the homologous-position correspondence across frames as
a table, and state membership stability as that Jaccard, not as `81 vs 82`.

### 2.6 The derivational ensemble is too narrow — WITHDRAWN

The round-2 record treated the 150-setting sweep as the perturbation ensemble. The sweep varies
only `max_gap` and `min_conserved_positions` — the two **merge** parameters — which by
construction **cannot change which positions are conserved**. It does not vary the `>50%`
threshold, the `3 of 4 groups` rule, the lineage grouping, gap treatment, or strict-vs-similarity.
The last matters most: the same alignment yields **81 strict vs 157 similarity-defined**
positions (`g2_summary.tsv`).

**Replacement (not yet applied):** the ensemble must span the conservation criterion itself.
The round-2 target was one unexamined criterion setting presented as stable.

### 2.7 The `C9` separability argument — WITHDRAWN

`proposed/research_contract_C3_C9_amendment.md` argued that demonstrated asymmetry — localisation
measurable, delimitation unavailable — is itself evidence *for* `C9`'s separability claim.

The reviewer calls this a rescue and is right. Inability to measure one of two properties does
not demonstrate that both are "separable measurable properties"; it demonstrates that one is
partially instrumented and the other is unestablished. Changing the baseline row *after*
known-boundary controls proved unavailable, and then claiming `g4` still settles `C9`, is
reasoning backwards from a desired verdict.

**Replacement:** the **RT-subdomain leg of `C9` is `UNESTABLISHED`** in Stage 2. The ncRNA and
operon legs are untouched. The proposed C3 narrowing stands as written and remains unapplied.

### 2.8 Vocabulary still overclaiming — NARROWED

`claim_vocabulary.tsv` permits terms the design cannot support: `operational conserved-region
localization` (should be *predicted reference-coordinate projection*), `ordered-architecture
recovery rate` (*recovery* is unsupported when order can be enforced by the decoder),
`transferability` (only as instrument callability or dyad-localization transfer, never as
membership correctness). Prohibited concepts also return under synonyms — *clean*, *genuine
held-out check*, *untouched evaluation*, *stable conserved-position membership* — including in
the round-2 decision record's own prose.

### 2.9 `RULE-2` / `RULE-4` contradict each other — WITHDRAWN

`method_comparison_plan.tsv` RULE-4 selects the winner by which method *"transfers most stably"*,
while RULE-2 forbids any method from seeing the transfer arms during selection. The selection
criterion is unobservable at selection time.

---

## 3 · Repairs that are bounded specification work, ready to apply

Not applied, because applying them to a design whose object is still under operator review would
produce a fourth record describing an object that may itself change.

1. AC1 denominator → motif-positive n = 56; motif-negative 10 reported separately; multiple-match
   rule for the 4; AC1's bar justified independently of the observed 66.
2. R-DYAD → an executable masking rule with a declared window; re-derivation, not patching.
3. Ensemble → add conservation threshold, group count, lineage grouping, gap treatment,
   strict-vs-similarity; land cross-frame homologous-position correspondence.
4. Family logic → `RVT-GII` in-family; joint identity-distance × family-status reporting;
   leave-lineage-group-out diagnostic.
5. Nested, lineage- or taxonomy-blocked threshold selection; threshold-selection negatives
   separated from final negative controls.
6. Enumerate M1/M2/M3 grids; declare the common output→coordinate conversion; resolve RULE-2 /
   RULE-4.
7. AC3's 0.70 → descriptive operational cutoff only, never confirmatory; specify one-to-one
   ensemble region matching before any stability percentile.
8. Identity/coverage thresholds → sensitivity-tested, measured on the modelled core as well as
   whole protein, with taxonomic or phylogenetic clustering.
9. PDB arm → strictly comparator; resolve or exclude tagged constructs; cluster redundant
   structures; stop calling exact-disjoint sequences *clean* or *independent*.
10. Drop region-presence calibration, or redefine Q15 as calibration of the dyad-containment
    event with a named method, metric, clustered fitting split and untouched test population.
11. Instantiate the full claim registry with no placeholder frames, strata, units or denominators.
12. Hashed input and prohibited-asset manifests covering the actual labels, sequences, models,
    decoys and evaluation populations; `INPUTS.tsv` currently omits `g2_conserved_positions.tsv`,
    which is the target label table.
13. AC10 package tests → expected outcomes, fixtures and pass criteria, not category names.

---

## 4 · What now gates the track — operator decisions

Added to `docs/BLOCKED.md` on this date.

1. **Is a group-II-intron-derived coordinate system the right instrument for a retron-primary
   project?** The derivation substrate contains **zero retrons**. Retrons are `78,292` exact RTs
   and the contract's primary biological target. The alternatives are: proceed and measure
   transfer honestly, accepting that poor transfer is the likely and publishable outcome; or
   re-plan `g4` around a retron-inclusive derivation built clean-room, which is a larger change
   than this redesign.
2. **Does `g4` become a reference-coordinate projection** rather than a detector of an
   independently testable property?
3. **The retron-transfer stop condition** for `g5`/`g6`.
4. **`C9`** — accept that the RT-subdomain leg is `UNESTABLISHED`.
5. **The `docs/BLOCKED.md` compute-prohibition ruling**, still `OPEN` from 2026-09-16.
6. Carried and still open: `U01` RT0's primary source; `U08` the RT1 interpretation;
   `U11` the expression-tag offsets.

---

## 5 · What survives both reviews

Recorded so a later session does not re-derive it:

- **`BOUNDARY_ACCURACY = UNESTABLISHED`** and **`BOUNDARY_CALIBRATION = UNESTABLISHED`**. The
  reviewer endorsed this: *"The redesign correctly abandons boundary-accuracy claims."* No
  population supplies true region boundaries, and this is a property of the evidence, not of any
  method.
- **The seven-way partition is not recoverable**, and neither is a six-way one. Block count never
  separates from a column-permutation null.
- **No RT0 occupancy of any kind** (`AC8`, round-1 repair 10 — ADDRESSED).
- **RT1 is not rescued by tuning** (`AC9`, round-1 repair 9 — ADDRESSED).
- **The bounded Stage-1 sampling frame** (round-1 repair 12 — ADDRESSED): unit, frame,
  eligibility, allocation, ceiling 5,000, seed, derivation-neighbour exclusion and an excluded
  pilot, all declared before any draw. Its family logic needs the §2.4 correction; its structure
  stands.
- **"phylogeny-ready" is dead**; "candidate core substrate" replaces it (round-1 repair 15 —
  ADDRESSED).
- **The clean-room allowlist** is a real improvement and needs enforcement, not redesign.
