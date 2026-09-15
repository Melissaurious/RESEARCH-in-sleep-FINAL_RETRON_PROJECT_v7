# dbchar_g4_family_baseline

STATUS: VERIFIED — `run.sh` was rerun from this assembled bundle and reproduced all 23 landed
tables and `MANIFEST.tsv` byte for byte (BS-3, WA-B.2). Log in §7.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **FULL** (launcher §7). Population contract:
`docs/decisions/2026-09-15_stage1_population_rules.md`. Inputs: the g2/g3 derived datasets over
the g1 corpus pin, plus the myRT `RVT-All.hmm` profile library for the MULTI investigation.

---

## 1 · What was measured

The non-redundant per-family RT and ncRNA descriptive baseline, on declared views, plus the
**basis of the MULTI labels** using tool-specific evidence.

### Views — `g4_views.tsv`

| view | rule | exact RTs | median aa |
|---|---|---:|---:|
| `V-RT-SINGLE` | exact RTs whose occurrences all carry one family label | **493,956** | 385 |
| `V-RT-MULTI` | exact RTs in the MULTI file (unresolved stratum) | **7,593** | 283 |
| `V-RT-CROSS` | exact RTs spanning more than one family label | **12** | 485.5 |

One observation per **exact RT protein**: a protein at 900 loci counts once. `V-RT-CROSS` is
kept as its own stratum and never folded into a family (the prior project bucketed these and
then lost them to a `groupby` NaN drop).

### RT length by family — `g4_rt_length_by_family.tsv`, `fig01_rt_length_by_family`

| family | exact RTs | q25 | median | q75 |
|---|---:|---:|---:|---:|
| RVT-GII | 256,624 | 244 | **407** | 470 |
| Retron | 78,287 | 289 | **342** | 442 |
| RVT-DGRs | 76,111 | 316 | **359** | 404 |
| RVT-UG2 | 8,423 | 298 | 431 | 473 |
| RVT-UG8 | 7,261 | 352 | 606 | 669 |

Outliers use **Tukey k=1.5 within each family**, never a pooled distribution, and no family
below n=30 gets fences at all. Rates per family are in `g4_rt_length_outlier_rates.tsv`; the
individual sequences are **named** with their hashes and lengths in
`g4_rt_length_named_outliers.tsv` (e.g. RVT-AbiP2: 61 above the fence, median 1,019 aa, up to
2,129; 72 below, down to 42 aa).

### Completeness, three-state — `g4_completeness_by_family.tsv`

A **missing** Prodigal `partial` flag is `no_completeness_evidence`, never "partial" — the prior
project's c18 counted NULL as partial while its own c04 declared that it must not. Corpus-wide
(`g4_completeness_states_raw.tsv`): 339,474 exact RTs complete by Prodigal, 124,667 partial,
29,095 with no evidence, 708 mixed across their occurrences.

| family | all_complete | all_partial | mixed/codon evidence |
|---|---:|---:|---:|
| RVT-GII | 167,033 (median 434 aa) | 70,671 (median 276 aa) | 18,920 |
| Retron | 54,679 (median 366 aa) | 19,954 (median 255 aa) | 3,654 |

Partial RTs are markedly shorter, as expected if the flag tracks truncation — reported, not
interpreted.

### Why MULTI records carry several labels — `g4_multi_hmm_*`, `fig02_multi_label_margins`

The corpus stores the labels but not the evidence. This gate re-derives it by running the
**myRT `RVT-All.hmm` library (45 profiles)** over the RT proteins themselves.

**Positive control first.** On a seeded random sample of 2,000 single-family exact RTs, the
best-scoring profile family equals the file label for **1,962 (98.1%)**, with a median
best-vs-second margin of **81.7 bits** and only 2.3% under 10 bits. The instrument reproduces a
known label, so a tie on MULTI means something.

**The MULTI result.** For all 7,593 MULTI exact RTs:

| measure | value |
|---|---|
| best-scoring family is among the record's own labels | **7,586 (99.9%)** |
| second-best family also among those labels | 7,500 (98.8%) |
| median best-vs-second margin | **5.0 bits** (control: 81.7) |
| margin below 10 bits | **74.6%** (control: 6.7%) |

**PROPOSED:** the MULTI labels are not arbitrary — they name precisely the profiles that score,
and those profiles are within a few bits of each other. MULTI is an *ambiguity* stratum, not a
mislabelling. Stage 1 does **not** resolve it: assigning a family would need an auditable
resolution rule, which is the operator's to declare.

### ncRNA baseline — `g4_ncrna_length_by_model.tsv`, `g4_ncrna_structure_coverage.tsv`

16,458 exact ncRNA sequences, grouped by the covariance model that called them: `OutgroupA`
(3,319, median 129 nt), `TypeIA_IIAI` (2,109, median 159 nt), `TypeIC1_IC2` (2,034, median
134 nt), and so on. Only **1,251 (7.6%)** carry a structure annotation. **0** are called by more
than one model — which, as the prior project warned, reflects the pipeline's winner-take-all
model selection and is not evidence about CM specificity.

## 2 · Counts, including the ones that look bad (BS-5)

n_attempted: 501,561 exact RT sequences + 16,458 exact ncRNA sequences
n_succeeded: all assigned to a view and described
n_dropped: 0

| | n |
|---|---:|
| exact RTs with no completeness evidence | 29,095 |
| exact RTs whose occurrences disagree about completeness | 708 + 11 |
| families too small for fences (n < 30) | see `fences_declared` in `g4_rt_length_by_family.tsv` |
| MULTI exact RTs with no profile hit | 0 |
| control exact RTs with no profile hit | 18 of 2,000 |
| second-count comparisons / disagreements | 127 / **0** |
| positive controls / failed | 21 / 0; seeded-bad rejected |

## 3 · The denominator's second count (WA-D.3)

`c03_second_count.sh` slices the RT protein out of the raw bytes with awk and counts distinct
sequences per source file with `sort -u` — no Python, no parquet. All 127 comparisons agree
(per-label counts and min/max lengths for 42 labels, plus the total).

⚠️ The first version of this route piped all workers into one `sort`; an RT protein can exceed
the 4 KB pipe buffer, so concurrent writers interleaved **inside a line** and produced nonsense
labels. Fixed by giving each worker its own file. The failure is recorded because it would have
been invisible in a smaller corpus.

**Positive controls** (21): a synthetic corpus with known lengths, known family membership and
known completeness evidence through the landed g2 pipeline — including the case that must not
regress (a **missing** Prodigal flag must not read as "partial"), a family below `MIN_GROUP`
that must get no fences, two constructed length outliers that must be named, and h02's
profile→family mapping, domtbl parsing and margin arithmetic.

## 4 · Claims

No claim status proposed. Evidence for `C1` (supporting): family baselines computed on exact RTs
differ from record-level baselines by the redundancy factors g2 measured, and the MULTI stratum
is a genuine ambiguity class rather than noise.

### Prior work — `g4_prior_reconciliation.tsv`

Against the prior project's `c16_rt_length_stats_by_family`: **36 of 44 families CONFIRMED
exactly** (same n and same median, including RVT-GII 256,623/407 and Retron 78,287/342),
5 CHANGED by exactly one sequence (the `V-RT-CROSS` proteins, which the prior grain assigned to
a family), 3 UNRESOLVED (present in only one of the two tables). That is a strong independent
corroboration of the prior length baseline from a differently built corpus representation.

## 5 · The self-adversarial pass (BS-14)

**1 · Overstated words.** *"non-redundant"* means one observation per exact protein sequence —
not per gene, per locus or per organism, and a family sampled from one clonal outbreak still
dominates its own baseline. *"complete"* is an ORF property from Prodigal or from start/stop
codons, not a domain-level judgement. *"the profiles tie"* is a statement about this HMM library
at these settings.

**2 · Alternative explanations.** The MULTI tie could be an artefact of running *all* profiles
at a permissive E-value: a ~5-bit margin might simply be what any short or divergent protein
gives. The control rules that out for typical single-family RTs (81.7 bits), but MULTI proteins
are also shorter (median 283 aa vs 385), and length correlates with score — so part of the tie
may be a length effect rather than genuine family ambiguity. That is not separated here.
The family length medians could agree with the prior project because both inherit the same
upstream extraction, not because both are right.

**3 · Could this have returned a negative?** It did: 18 control sequences with no hit at all,
29,095 exact RTs with no completeness evidence, 5 families differing from the prior, and a first
HMM mapping whose control returned 33% — a failure that stopped the analysis until fixed.

**4 · Unit of every rate.** Exact RT sequences or exact ncRNA sequences, named per table in
`MANIFEST.tsv` and stamped on both figures.

**5 · Numbers with no producing script.** None in `tables/`.

**6 · What was withdrawn or weakened.**
- **Withdrawn:** the first profile→family mapping, a regex that silently failed on `RVT-GII-I`,
  `RVT-GII-II` and `RVT-Retrons`. Its positive control read 0/1,029 on RVT-GII and 0/294 on
  Retron — a 33% overall agreement that would have made the MULTI comparison meaningless.
  Replaced by an explicit declared mapping; the control then read 98.1%.
- **Withdrawn:** a per-label second-count table computed over first copies only, which
  disagreed with the awk route by 5 sequences. The comparison table now counts all records; the
  deduplicated counts live in the g2 ladder.
- **Weakened:** the MULTI conclusion, from "the labels are ties" to a `PROPOSED:` reading with
  the length confound stated.

## 6 · What changed from the plan

The MULTI investigation was specified in the population contract; the instrument (myRT HMM) and
its positive control were chosen here because the corpus carries no per-label tool evidence.

## 7 · Reproduction log (BS-3, WA-B.2)

```
$ bash results/dbchar_g4_family_baseline/run.sh
== c04 self-validation: rejected the seeded-bad case, as required
== c04 positive controls ...   c04: 21 controls, 0 failed
== b01 the per-family baseline on the declared views
== h02 MULTI HMM evidence + its positive control (9,593 proteins x 45 profiles)
== c03 independent second count (awk slice + sort -u)
== c05 reconcile ...           127 rows, 0 DISAGREE; prior 44 families, 36 CONFIRMED, 5 CHANGED
== figures ...                 fig01 / fig02 (png + svg + sidecar TSV)
== assemble ...                21 summary rows, 23 tables, 2 figures
  OK × 23 tables, OK MANIFEST.tsv
REPRODUCED: every landed table is byte-identical on rerun.
wall 116.8 s, exit 0
```

## 8 · Derived datasets

`rt_family_baseline_v1.parquet` (501,561 exact RTs with view, completeness class and per-family
context), `ncrna_family_baseline_v1.parquet` (16,458), `multi_hmm_evidence_v1.parquet` (7,593
MULTI proteins with their best/second profile, scores and margin). Registered with hashes in
`g4_derived_registry.tsv` and `data/README.md`.

## 9 · Acceptance

Open `INPUTS.tsv` and recognise the 47 inputs: 42 corpus files, three derived datasets, the myRT
HMM library and the prior length table compared against.
