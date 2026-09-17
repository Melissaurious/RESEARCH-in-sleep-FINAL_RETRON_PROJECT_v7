# g6 — downstream architecture analysis. PLAN ONLY.

`rt07_g6_family_architecture`. Runs after g5 and only on g5's landed products. It re-runs no
mapping and changes no instrument.

Every measurement below names its analytical unit (**exact RT**, unless stated) and its
denominator (the **censused eligible** population, not 501,561). Every one reports all four
call states. None of them is an accuracy statement.

---

## A · Broad RT architecture

| target | measurement | denominator |
|---|---|---|
| MAPPED fraction by RT family | median, IQR, full distribution of `mapped_fraction` | eligible exact RTs in that family stratum |
| state occupancy by family | per `state_id`, the share of sequences with each of the four call states | eligible exact RTs in that stratum |
| catalytic-state mapping | `cat_call_state` and `cat_motif_class` distribution; `[YF].DD` concordance among `CAT_STATE`-`MAPPED` sequences | **two separate denominators**: all eligible sequences, and `CAT_STATE`-MAPPED sequences |
| deletion / state-loss patterns | `DELETED_STATE` runs — which states, which contiguous blocks, which co-occurrence patterns | eligible exact RTs |
| family-specific insertions / extensions | `n_insertion_runs`, `total_inserted_residues`, `max_insertion_run`, and insertion position relative to the profile | eligible exact RTs |
| mapping uncertainty | `AMBIGUOUS` + `UNSUPPORTED` share per state and per sequence; the posterior distribution | anchor calls |
| failure-to-map rates | `inspectability_status` distribution, and `failures.tsv` reason codes | eligible exact RTs, and all input records |

**Interpretation rules, binding:**

* A `DELETED_STATE` is an alignment-path statement. "This family lacks this region" is a
  *different* claim and may not be derived from occupancy alone.
* Low MAPPED fraction in a family distant from GII is the **expected** behaviour of a
  GII-centred frame, not a biological finding. Construction medians ran GII 0.950 →
  Retrons 0.473 with no biology in between.
* The seven-way RT0–RT7 partition is not used. States are reported as `state_id`.
* Every reported difference between families needs a stated denominator and an explicit
  statement of whether it survives the callability gradient. The mapper's own family
  gradient is a confound for every between-family architecture comparison and must be
  carried in the reporting, not assumed away.

---

## B · Retron-focused architecture

| target | measurement |
|---|---|
| retron state occupancy | per-state call-state distribution over Retron-labelled eligible exact RTs |
| retron-specific missing / non-detected states | states with elevated `DELETED_STATE` / `UNSUPPORTED` in retrons relative to other families — reported as **detection behaviour**, with the callability gradient stated |
| N/C-terminal architecture | `sequence_length` against first and last MAPPED `state_id`; residues before the first and after the last mapped state |
| catalytic-state behaviour | `cat_motif_class` distribution in retrons; `n_dyad_motifs_in_sequence` where `CAT_STATE` is `SUBSTITUTED` |
| subtype differences | only where the subtype stratum is large enough to support it; otherwise reported as under-powered and left descriptive |
| accessory / system context | joins to `rt_loci_v1`, `rt_window_cds_v1`, `rt_ncrna_exact_pairs_v1` — interpretation, on the pair/locus unit with its own denominator |

Atypical biology is **flagged before it is filtered**: unusual distance, orientation, missing
ncRNA, multiplicity, contig-edge state, tool disagreement and unusual architecture are all
retained and reported.

---

## C · Tool-stratified robustness

Strata: multi-tool-supported · MyRT-only · PADLOC-supported · DefenseFinder-supported ·
tool-discordant.

Reported per stratum: `inspectability_status` distribution, `mapped_fraction` distribution,
state occupancy, catalytic behaviour.

**Tool agreement is not biological ground truth.** This section reports whether mapper
behaviour is *stable across strata* — a robustness statement about the instrument. It is
never an accuracy, sensitivity, specificity, precision, recall or ROC measurement against a
tool label, and a tool-discordant record is never called a mapper error. See
`STAGE1_METADATA_ROLE.md`.

`MULTI` is its own multi-label population throughout and is never appended to a single
family. Tool-specific fields are never pooled across tools whose provenance differs; the
original tool call is preserved.

---

## D · Negative and absence discipline

No zero or absence claim is made without a positive control showing the same instrument
recovers a known-present case on an appropriate substrate. Null and refuting results are
retained and reported.

## E · What g6 must not do

* No accuracy claim of any kind.
* No universal-RT-architecture claim.
* No RT0–RT7 renaming, and no historical label except through the crosswalk, which is
  currently `UNRESOLVED` everywhere.
* No claim about `-M 60` or `-M a2m` behaviour.
* No re-running, re-tuning or re-validating of the mapper.
* No structural data — that is g7.
