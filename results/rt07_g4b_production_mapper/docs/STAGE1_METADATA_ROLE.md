# Stage-1 labels are metadata and strata — never validation truth

The **501,561** Stage-1 exact RT proteins (`data/derived/rt_exact_v1.faa` /
`rt_exact_v1.parquet`; unit `exact_rt`, `results/dbchar_g2_canonical_units`) are the
application population for g5. They are **not** a validation set, and nothing in g5 or g6
may treat them as one.

## What is retained, and what each thing is for

| variable | source | role in g5/g6 |
|---|---|---|
| raw MyRT family | Stage-1 `rt_family_baseline_v1` | grouping / stratification |
| Stage-1 collapsed family | `dbchar_g4_family_baseline` | grouping / stratification |
| `MULTI` multi-label population | Stage-1 | **its own population**, never folded into a single family |
| PADLOC support | `rt_tool_calls_v1` | robustness stratum |
| DefenseFinder support | `rt_tool_calls_v1` | robustness stratum |
| source database | Stage-1 record provenance | robustness stratum |
| taxonomy | Stage-1 taxonomic occurrence | grouping; the denominator is the taxonomic-occurrence unit, not the exact-RT unit |
| system context / accessory genes | `rt_loci_v1`, `rt_window_cds_v1` | interpretation in g6 |
| ncRNA association | `rt_ncrna_exact_pairs_v1` | interpretation in g6 |
| completeness / contig-edge state | Stage-1 | **retained and reported**, never a silent filter |

## The rule

**Tool agreement is not biological ground truth.** MyRT, PADLOC and DefenseFinder are
annotation instruments with their own models, thresholds and blind spots. They were not
used to derive the mapper and they cannot validate it.

Concretely, the following are all forbidden in g5 and g6:

* computing a sensitivity, specificity, precision, recall, accuracy, F1 or ROC of the mapper
  **against** any tool label;
* calling a mapper output "correct" or "incorrect" because a tool agrees or disagrees;
* filtering the application population to tool-supported records before measuring;
* treating "MyRT says Retron" as establishing that a protein is a retron RT;
* treating tool disagreement as mapper error.

What *is* allowed, and is the point of carrying them:

* reporting mapper behaviour **within** each stratum, with that stratum's own denominator;
* reporting whether mapper behaviour is stable across strata — a robustness statement about
  the instrument, not an accuracy statement;
* reporting tool-discordant records as their own stratum, retained rather than filtered.

## Denominator discipline

Every g5/g6 number names its analytical unit and its denominator. The units are the
project's registered ones: raw record, genomic locus, exact RT, taxonomic occurrence,
RT–ncRNA pair. The mapper operates on the **exact RT** unit; a per-locus or per-taxon
statement requires an explicit re-aggregation with its own denominator, never a reuse of the
exact-RT count.

`MULTI` remains its own multi-label population and is never appended to a single RT family.

RT analyses do not silently mix ncRNA-anchor-only records into their denominator.

## Eligibility is a separate, declared filter

The instrument's inherited eligibility rule (≥ 250 aa, standard residues only) will exclude
part of the Stage-1 catalogue — the landed length distribution shows substantial mass below
250 aa in several families. Those records are **`INPUT_INVALID`, not absent RTs**, they are
counted and reported, and g5's first step is an eligibility census that establishes the
real denominator before any mapping runs. See `G5_EXECUTION_PLAN.md` §2.
