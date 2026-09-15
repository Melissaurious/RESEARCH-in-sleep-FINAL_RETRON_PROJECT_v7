# dbchar_g2b_rt_cds_recovery

STATUS: VERIFIED — `run.sh` was rerun from this assembled bundle and reproduced all 11 landed
tables and `MANIFEST.tsv` byte for byte (BS-3, WA-B.2). Log in §7.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **FULL**. A companion measurement to `dbchar_g2_canonical_units` (write-once, so this
lands as its own bundle): how the RT-anchored records with **no marked RT CDS** were recovered,
what independent evidence supports the reconstruction, and — for those that cannot be recovered
— whether the defect is a coordinate/window representation problem or genuinely truncated
biological context.

---

## 1 · What was measured

The 31,504 RT-anchored records that carry an `rt_gene` but no `cds_annotations[]` entry flagged
`is_rt_gene` (g1 and g2 counted them independently; this gate explains them), as a per-record
reusable table plus summaries.

### The recovery route, and why it is evidence

Every one of these records **already contains the RT protein**; what is missing is Prodigal's
ORF call. A record is **RECOVERED** when the window DNA, translated in the frame given by
`rt_gene.start/end/strand`, reproduces that protein. The DNA and the protein are different
fields written by different steps of the mining pipeline, so their agreement is evidence about
the coordinates rather than a restatement of them.

| recovery state | n records | what the record can still support |
|---|---:|---|
| **RECOVERED** | **14,188** | RT sequence **and** genomic coordinates (`elig_rt_coords = True`) |
| **SEQUENCE_ONLY** | **16,688** | RT sequence only; no defensible genomic context |
| **ILL_POSED** | **628** | sequence retained, coordinates flagged unverified |

All 31,504 keep `elig_exact_rt = True`: **no record is deleted**, and each carries its own
eligibility flags (`g2b_recovery_classes.tsv`, and per record in `rt_cds_recovery_v1.parquet`).

### Independent evidence for the reconstruction

1. **A different translation implementation.** `g2b_independent_translation_check.tsv`: on a
   seeded sample of 2,000 RECOVERED records, Biopython (table 11) plus the declared equivalence
   re-implemented in this gate reproduces the stored protein for **1,999/2,000 (99.95%)**; the
   same test on 2,000 records that *do* have an RT CDS gives **1,999/2,000**. The **negative
   control — the same comparison after a one-base frame shift — agrees 0 times** in both.
2. **What Prodigal did call.** `g2b_recovered_evidence.tsv`: of the RECOVERED records, 13,528
   13,535 have a CDS overlapping the RT interval **in the same reading frame and strand** but
   with different boundaries; 305 have no overlapping CDS at all; 18 share an exact end
   boundary. Prodigal therefore found coding sequence in the right frame at the right place in
   almost every recovered case — it simply did not call the RT ORF itself.
3. **Why the ORF call is missing at all.** 9,183 of the 14,188 have back-translation status
   `internal_stop_masked` — the stored protein carries in-frame stop codons written as `U`.
   An ORF containing internal stops is exactly what Prodigal will not call, so the missing CDS
   and the masked stops are the same phenomenon. This is a **PROPOSED** mechanism: the
   association is measured here, the causal claim is the operator's.

### The records that cannot be recovered — representation vs truncation

`g2b_representation_classes.tsv`. **All 16,688 SEQUENCE_ONLY records have
`clipped_at_contig_end = True` and a short window** (median span ≈ 4 kb against a full window of
20,001 bp), i.e. the context extractor hit the end of the contig it retrieved:

| class | n | median bp past the window end | max | reading |
|---|---:|---:|---:|---|
| `rt_beyond_a_contig_end_clipped_window` | **9,128** | 2,956 | 15,737 | the RT interval lies **wholly beyond** the retrieved contig: the RT was called against a longer sequence than the contig used for context — a **coordinate/representation mismatch between two pipeline steps**, not a biological truncation |
| `rt_crosses_a_contig_end_clipped_window` | **3,636** | 765 | 14,774 | the RT interval **straddles** the contig end: context genuinely truncated at a real boundary |
| `window_inverted_no_sequence_retrieved` | **3,924** | — | — | `actual_window.start > end` and an empty sequence: no context retrieved at all — a representation defect |

`g2b_sequence_only_by_database.tsv` shows these concentrate in the MAG catalogues
(mgnify_human_gut dominates), which is consistent with contig naming/versioning differing
between the protein source and the context source. That attribution is **PROPOSED**; this gate
measures the geometry, not the cause.

## 2 · Counts, including the ones that look bad (BS-5)

n_attempted: 31,504 records with no marked RT CDS
n_succeeded: 31,504 classified, with per-record eligibility preserved
n_dropped: 0

| | n |
|---|---:|
| RECOVERED / SEQUENCE_ONLY / ILL_POSED | 14,188 / 16,688 / 628 |
| records keeping a usable RT sequence | 31,504 (100%) |
| records with verified coordinates | 14,188 |
| independent-translation sample agreement (RECOVERED / control) | 1,999/2,000 / 1,999/2,000 |
| frame-shift negative control agreement | 0 / 0 |
| second-count comparisons / disagreements | 14 / **0** |
| positive controls / failed | 24 / 0; seeded-bad rejected |

The one mismatching record in each sample is retained and unexplained: at 0.05% it is inside
what a partial-codon or ambiguity edge case would produce, and it is not investigated here.

## 3 · The denominator's second count (WA-D.3)

`c02_second_count.sh` — one awk pass over the raw bytes recomputes the class split for lines
carrying no `"is_rt_gene": true`: 31,504 total, 14,816 with the RT inside its window (14,188
recovered + 628 ill-posed), 9,128 beyond the window end, 3,636 crossing an edge, 3,924 inverted,
0 before the window start. `g2b_second_counts.tsv`: **14 rows, 0 disagreements**, including
every class against the landed g2 bundle.

## 4 · Claims

No claim status proposed. Evidence for `C1`/`C2`: 45% of the records that look broken at the
annotation level are fully recoverable at the sequence-and-coordinate level, so "has an RT CDS"
and "has a usable RT" are different populations.

## 5 · The self-adversarial pass (BS-14)

**1 · Overstated words.** *"RECOVERED"* means the coordinates are consistent with the stored
protein — not that the RT gene model is correct; there is still no Prodigal call, so no
`partial` flag and no independent gene-boundary evidence. *"Representation mismatch"* is an
inference from geometry: measured is that the RT lies beyond the retrieved contig.

**2 · Alternative explanations.** The back-translation could be tautological if the protein were
derived from this window; for these records it demonstrably was not — Prodigal produced no call
here at all, and 65% of them carry in-frame stops that an ORF caller would refuse. The Biopython
check shares the *input* but not the implementation; the frame-shift control shows it can fail.

**3 · Could it have returned a negative?** It did: 628 records stay ILL_POSED, 16,688 keep no
defensible context, and the first version of the independent check returned 34.6% agreement.

**4 · Unit of every rate.** Records throughout; denominators named per table in `MANIFEST.tsv`.

**5 · Numbers with no producing script.** None in `tables/`. The 13,528 / 305 / 18 and 9,183
figures in §1 are sums over named columns of `g2b_recovered_evidence.tsv` and
`g2b_recovery_classes.tsv`.

**6 · What was withdrawn or weakened.**
- **Withdrawn:** the first independent-translation check, which scored 34.6% agreement because
  it compared under a stricter rule than g2's declared recoding classes (Biopython writes `*`
  where the corpus writes `U`/`W`). The harness was wrong, not the data; the corrected check
  re-implements the declared equivalence and reports 99.95%. The wrong number is recorded here
  rather than quietly replaced.
- **Withdrawn:** a first `representation_class` rule that used `anchor_center` to separate
  "beyond a contig end" from "crossing" it. A control caught it reading *crosses* for an RT
  lying wholly outside a window whose anchor sat inside. Replaced by a direct interval test.
- **Weakened:** the mechanism linking masked internal stops to the missing ORF call, from a
  conclusion to a `PROPOSED:` association.

## 6 · What changed from the plan

The gate was added after g2 landed, at the operator's request, because g2's classes were
reported in prose and needed a reusable per-record table. No g2 number changed.

## 7 · Reproduction log (BS-3, WA-B.2)

```
$ bash results/dbchar_g2b_rt_cds_recovery/run.sh
== c03 self-validation: the controls must reject a seeded-bad expectation
   rejected the seeded-bad case, as required
== c03 positive controls ...   c03: 24 controls, 0 failed
== r01 recovery classification + the independent Biopython translation check
== c02 independent second count (awk on the raw bytes)
== c04 reconcile ...           c04: 14 rows, 0 DISAGREE
== assemble ...                20 summary rows, 11 tables
  OK × 11 tables, OK MANIFEST.tsv
REPRODUCED: every landed table is byte-identical on rerun.
wall 37.8 s, exit 0
```

## 8 · Derived dataset

`rt_cds_recovery_v1.parquet` — 31,504 rows, one per record without a marked RT CDS, carrying the
recovery state, representation class, bp beyond the window, what Prodigal called around the RT,
and every g2 eligibility flag. Registered with hashes in `g2b_derived_registry.tsv` and
`data/README.md`.

## 9 · Acceptance

Open `INPUTS.tsv` and recognise the 46 inputs: 42 corpus files, two g2 derived datasets and two
landed g2 tables.
