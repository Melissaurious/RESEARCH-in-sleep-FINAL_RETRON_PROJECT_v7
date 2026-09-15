# dbchar_g3_pair_geometry

STATUS: VERIFIED — `run.sh` was rerun from this assembled bundle and reproduced all 46 landed
tables and `MANIFEST.tsv` byte for byte (BS-3, WA-B.2). Log in §7.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **FULL** (launcher §7, the priority Stage-1 biological output). Population contract:
`docs/decisions/2026-09-15_stage1_population_rules.md`. Inputs: the g2 derived datasets over the
g1 corpus pin. The raw corpus is opened only by the independent second count.

---

## 1 · What was measured

The RT↔ncRNA association census, at **placement** grain (one record × one ncRNA call) and at
**exact-pair** grain, with geometry computed from coordinates by declared conventions.

### Populations — `g3_populations.tsv`

| population | rule | n placements |
|---|---|---:|
| `ALL` | every ncRNA call in an RT-anchored record | **346,722** |
| `ELIGIBLE` | record geometry-eligible, ncRNA inside the window, strand present, first copy | **345,313** |
| `CANONICAL` | eligible, not touching a window edge, not a within-record duplicate call | **344,154** |
| `ATYPICAL` | eligible but not canonical | **1,159** |

Ineligible (1,409): 1,303 byte-identical duplicate lines, 41 RT partly outside its window,
37 RT outside, 28 back-translation mismatch (`g3_ineligible_reasons.tsv`).

### The geometry conventions (declared in `g3lib.py` before any data was read)

- `gap_bp` = **bases strictly between** the two intervals — abutting = 0, overlapping = 0 with
  the overlap reported separately. (The prior project's `gap` was a coordinate difference, so
  abutting read 1; its distance bins are therefore not comparable at the boundary.)
- direction and signed distance are **transcription-relative to the RT strand**; contig-frame
  values are retained beside them.
- intervening CDS are counted from coordinates (CDS lying wholly in the gap), not from a
  gene-rank field whose upstream/downstream convention is unverifiable.

### The priors — `g3_direction.tsv`, `g3_distance_stats.tsv`, `g3_cds_between_explicit.tsv`

On **CANONICAL** placements:

| measure | value |
|---|---|
| upstream | **304,285 (94.5%)** — median gap **55 bp** (IQR 27–1,037) |
| overlapping the RT | 10,135 (3.1%) |
| downstream | 6,423 (2.0%) — median 2,682 bp, and **see §1 the downstream mode** |
| same strand as the RT | **99.8%** (upstream 303,759 of 304,285) |
| **0 CDS between** | **324,904 (94.41%)** |
| 1 CDS | 12,427 (3.61%) · 2 CDS 939 (0.27%) · 3 CDS 544 (0.16%) · >3 CDS 5,340 (1.55%) |

Figures: `fig01_distance_distribution` (signed spacing, canonical vs atypical),
`fig02_cds_between` (0/1/2/3/>3 with counts), `fig03_direction_by_family`. Each ships the TSV it
plots and stamps its unit and denominator; the figure script reads `tables/` and nothing else.

### The zero-ncRNA class is detector scope, not biology — `g3_zero_class_by_family.tsv`

| family label | loci | loci with ≥1 call | zero-ncRNA |
|---|---:|---:|---:|
| Retron | 632,688 | 333,838 | **47.24%** |
| RVT-GII | 1,525,893 | 120 | 99.99% |
| every other family | — | ≈0 | ≈100% |

⛔ The covariance models in this corpus are **retron ncRNA models**. The near-total absence of
calls outside Retron-labelled RTs measures **where the detector was pointed**, not whether an
ncRNA exists. No absence claim may be built on it.

### Retron-CM placements beside non-Retron RTs — kept as candidates

`g3_nonretron_cm_placements.tsv`, `rt_ncrna_nonretron_candidates_v1.parquet` (266 placements):

| population | n placements | % upstream | median |distance| bp | % same strand |
|---|---:|---:|---:|---:|
| CANONICAL Retron | 343,892 | 94.54 | 52 | 99.8 |
| eligible non-Retron single family | 260 | 57.69 | 2,665 | — |
| eligible MULTI stratum | 6 | 50.00 | 8,333 | — |

Their geometry does **not** look like the canonical Retron prior. They are retained as an
explicit atypical/candidate population and are one `pull.py` filter away for a later
divergent-retron hypothesis. **Stage 1 does not call them novel or divergent retrons.**

### Multiplicity, and what "duplicate" means — `g3_multiplicity_class.tsv`

Of eligible placements: 321,456 single call; **23,469 are the same call arriving from another
record of the same locus** (re-mining, usually a second source database); only **190 are a true
duplicate call inside one record**; 174 distinct sequences at one locus; 24 same sequence at
other coordinates. Conflating the first two would have inflated "duplicate calls" 123-fold.

### Pairing topology — `g3_topology_*.tsv`, `g3_pair_recurrence.tsv`

30,924 distinct exact (RT, ncRNA) pairs over 29,192 exact RTs and 16,458 exact ncRNA sequences:

- exact RTs with exactly one ncRNA sequence: **28,271 (96.8%)**; with more than one: 921 (3.2%,
  max 176).
- exact ncRNA sequences with exactly one RT: **13,542 (82.3%)**; with more than one: 2,916
  (17.7%, max 705).
- components: **12,079 are 1:1**, 179 are 1:many, 2,293 many:1, 367 many:many (largest: 706 RTs
  × 190 ncRNAs).
- recurrence of a repeated pair: 12,005 pairs occur once; 9,362 recur only as **copies of one
  physical locus in several databases**; 4,452 recur within one species; **5,056 recur across
  species** (the largest pair has 101,792 placements). Recurrence is therefore mostly
  redeposition, and the cross-species tail is the part worth a biological question.

⚠️ Declared caution: two exact ncRNA sequences differing only in where the CM cut the boundary
are two nodes here and one molecule in biology. `g3_ncrna_boundary_variants.tsv` measures it:
of 366 sequence pairs co-occurring at one locus, **all 366 have disjoint intervals** — none is a
boundary variant — but the caution stands for the corpus-wide node count.

### The shipped `position_relative_to_rt` — characterised, not merely rejected

- Present on only **14,825 of 346,722** placements (4.28%); null on 95.72%.
- **No coordinate reference frame explains it.** Twelve candidate frames were tested
  (`g3_shipped_field_semantics.tsv`): genomic vs transcription-relative, from either RT end, to
  either ncRNA end, signed and unsigned, against the anchor and the window. The best is
  `nc_start − rt_start` at **146/14,810 (0.99%)**; the transcription-relative signed distance
  matches 11.
- What it actually is (`g3_shipped_field_structure.tsv`): its correlation with
  **−(rt_start − win_start)** is **r = 1.000**, and the residual is a small integer in 0…19
  (20 distinct values) that equals the ncRNA's **intergenic-region index − 1** in 48.4% of cases.
  So the field is **an index minus a coordinate** — not a distance in any frame, and not a
  semantic/reference-frame mismatch.
- The coordinate-derived geometry is canonical; the shipped field is retained as provenance/QC.

### The downstream mode at ~2,682 bp is a TECHNICAL signature — `g3_downstream_mode_*.tsv`

6,761 canonical downstream placements, 77.4% within 150 bp of the median, IQR 97 bp. The audit:

- the dominant stratum (5,190 placements, ncbi_bacteria, Retron, CM `TypeV`) is **99.96%
  `true_start_clipped`** — the window begins at the contig start, so the RT sits at the window's
  left edge and any call is forced downstream;
- the mode contains only **18 distinct ncRNA sequences, 126 RTs, 15 species, 3 CMs**, and two
  sequences supply 5,187 of its 5,234 placements;
- `rt_start − win_start` has median **2** in this group against ~10,000 for a normal window.

**Labelled a suspicious technical/deposition mode. It is not offered as a biological prior.**

## 2 · Counts, including the ones that look bad (BS-5)

n_attempted: 346,722 ncRNA placements in RT-anchored records
n_succeeded: 346,722 placed and classified
n_dropped: 0 — 1,409 are geometry-ineligible with a reason and stay in the table

| | n |
|---|---:|
| atypical classes (overlapping RT / >5 kb / opposite strand / >2 CDS) | 12,259 / 557 / 3,095 / 5,903 |
| placements in clipped or contig-start-clipped windows | 57,571 / 59,510 |
| second-count comparisons / disagreements | 10 / **0** |
| positive controls / failed | 51 / 0; seeded-bad rejected |
| derived datasets | 4 (`g3_derived_registry.tsv`) |

## 3 · The denominator's second count (WA-D.3)

`c05_second_count.sh` re-implements the declared geometry **in awk over the raw bytes** — no
Python, no parquet, no `g3lib`. It agrees exactly: 346,722 placements; upstream 327,565;
downstream 6,819; overlapping 12,338; same strand 343,625; opposite 3,097; records carrying a
call 346,406 (`g3_second_counts.tsv`, 10 rows, 0 disagreements — the direction counts there are
on `ALL`, so they differ from the CANONICAL figures in §1 by the ineligible and edge cases).

**Positive controls** (`c04_positive_controls.tsv`, 51): a synthetic corpus with placements at a
known gap on both strands and both sides, abutting, overlapping, opposite-strand, with a known
number of intervening CDS, on a CDS, outside the window, with a missing strand, duplicated in
one record and duplicated across two records of one locus — pushed through the **landed g2
pipeline** and then this gate. The arithmetic helpers are checked on values whose answer is
arithmetic (abutting = 0 bases between, book-ended = 0 overlap, bin boundaries).

## 4 · Claims

No claim status proposed. Evidence for `C5`: on the canonical population the ncRNA sits upstream
of the RT, same strand, with no intervening CDS, at a median 55 bp — and the largest apparent
exception to that shape is explained by window clipping rather than biology.

Prior work (`g3_prior_reconciliation.tsv`): the prior finding that `position_relative_to_rt` is
unusable is **CONFIRMED** and strengthened; "no ncRNA sequence is called by more than one CM" is
**CONFIRMED** (0 of 16,458) with the prior's own caveat retained — one model per call is imposed
by the pipeline's selection step, so this is not evidence about CM specificity. The gap and
distance conventions are **CHANGED** by declaration.

## 5 · The self-adversarial pass (BS-14)

**1 · Overstated words.** *"CANONICAL"* is a declared filter, not a biological judgement.
*"upstream"* is transcription-relative and inherits the RT strand, which g2 verified for 99.5%
of records but not all. *"exact pair"* counts sequence identity, and boundary differences make
that a lower bound on "same molecule". *"technical mode"* for the downstream cluster is an
inference from clipping and low sequence diversity, not proof.

**2 · Alternative explanations.** The 94.5% upstream figure could be an artefact of the CM
models being trained on retron msr-msd, which sit upstream by construction — the number
describes *where this detector finds things*, and the non-Retron comparison (57.7% upstream) is
the only within-corpus contrast available. The 99.8% same-strand figure is partly circular for
the same reason. The 30,924 exact pairs would shrink if boundary variants were collapsed.

**3 · Could this have returned a negative?** It did: 1,409 ineligible placements, 3,095
opposite-strand, 5,903 with >2 CDS between, a downstream mode that failed its audit, and a
shipped field that failed all twelve candidate frames.

**4 · Unit of every rate.** Placements, loci, exact sequences or components — named per table in
`MANIFEST.tsv` and stamped on every figure.

**5 · Numbers with no producing script.** None in `tables/`. The percentages in §1 are ratios of
named columns.

**6 · What was withdrawn or weakened.**
- **Withdrawn:** a first multiplicity classification that folded "same call from another record
  of the same locus" into "duplicate call". It reported 23,659 duplicate calls where the
  detector-level number is 190.
- **Weakened:** the ~2,682 bp downstream mode, from a distribution feature to a labelled
  technical signature.
- **Weakened:** "the shipped field is wrong" to "the shipped field is an index minus a
  coordinate", after testing twelve reference frames.
- **Not claimed:** anything about the 266 non-Retron CM placements beyond their geometry.

## 6 · What changed from the plan

1. Items added at the operator's request before landing: the explicit 0/1/2/3/>3 CDS table and
   figures, the bipartite topology, the non-Retron candidate population, the shipped-field
   semantic audit and the downstream-mode audit.
2. `overlaps_rt_cds` was separated from `overlaps_any_cds`, because "inside the RT gene model"
   and "on some CDS" are different questions.

## 7 · Reproduction log (BS-3, WA-B.2)

```
$ bash results/dbchar_g3_pair_geometry/run.sh
== c04 self-validation: rejected the seeded-bad case, as required
== c04 positive controls ...     c04: 51 controls, 0 failed
== p01 ...                       346,722 placements, eligible 345,313, canonical 344,154
                                 30,924 distinct (exact RT, exact ncRNA) pairs
== a02 / a03 / a04 ...           priors, topology, three audits
== c05 independent second count (awk geometry on the raw bytes)
== c06 reconcile ...             10 rows, 0 DISAGREE; prior 4 rows
== figures ...                   fig01 / fig02 / fig03 (png + svg + sidecar TSV)
== assemble ...                  35 summary rows, 46 tables, 3 figures
  OK × 46 tables, OK MANIFEST.tsv
REPRODUCED: every landed table is byte-identical on rerun.
wall 101.3 s, peak RSS 13.3 GB, exit 0
```

Figures are verified through their sidecar TSVs: a PNG carries a renderer fingerprint that
changes with the matplotlib build without any number changing.

## 8 · Derived datasets

`rt_ncrna_pairs_v1.parquet` (346,722 placements, every field the launcher's geometry contract
names), `rt_ncrna_exact_pairs_v1.parquet` (30,924), `rt_ncrna_exact_pair_recurrence_v1.parquet`,
`rt_ncrna_nonretron_candidates_v1.parquet` (266). Hashes and content digests in
`g3_derived_registry.tsv`; registered in `data/README.md`.

## 9 · Acceptance

Open `INPUTS.tsv` and recognise the 47 inputs: 42 corpus files, three g2 derived datasets and
two landed g2 tables.
