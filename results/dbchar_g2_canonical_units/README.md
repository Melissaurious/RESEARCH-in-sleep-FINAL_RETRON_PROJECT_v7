# dbchar_g2_canonical_units

STATUS: VERIFIED — `run.sh` was rerun from this assembled bundle and reproduced all 28 landed
tables and `MANIFEST.tsv` byte for byte (BS-3, WA-B.2). Log in §7.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **FULL** (launcher §7). Plan: `ARIS_OUTPUT/01_database_characterization/dbchar_g2_canonical_units/PLAN.md`.
Population contract: `docs/decisions/2026-09-15_stage1_population_rules.md`.
Corpus: the g1 pin (`results/dbchar_g1_corpus_identity/`, record manifest `8e9b7999…41d00`).

---

## 1 · What was measured

The redundancy/identity mapping among the declared analytical units of the **RT-anchored**
population (3,059,700 records; the 298,482 ncRNA-anchor-only records are outside it and their
file was never opened), plus the coordinate/sequence integrity rules and the eligibility flags
that decide which record can support which downstream measurement.

### The unit ladder — `g2_unit_ladder.tsv`

| unit | definition | n |
|---|---|---:|
| raw record | one line of an RT-anchored file | **3,059,700** |
| distinct raw record | after byte-identical duplicate lines collapse | **3,051,238** |
| `rt_system_id` | distinct id string (**not a key** — it encodes contig + RT start) | 2,917,865 |
| attribution | distinct (id, source_database, genome_id) | 3,051,238 |
| **locus** | distinct (contig, RT start, RT end, RT strand) | **2,847,312** |
| **physical locus** | locus after `NZ_` contig-prefix normalisation | **2,475,684** |
| physical locus, collapse supported by evidence | window DNA + RT + coordinates + strand agree | **2,475,684** |
| **exact RT** | sha256 of the RT protein, one trailing `*` removed | **501,561** |
| exact RT, coordinate-verified | ≥1 record whose DNA back-translates to it | 484,360 |
| genome | distinct `genome_id` without the GTDB `RS_`/`GB_` prefix | 1,542,433 |
| contig | distinct contig accession (`NZ_` normalised) | 2,182,435 |
| RT taxonomic occurrence | distinct (exact RT, genome) | 2,737,189 |
| RT species occurrence | distinct (exact RT, taxonomy system, species) | 818,961 |
| window DNA | distinct window sequence hash (empty excluded) | 1,262,241 |

**No two units convert by a constant** — `g2_ladder_by_source_database.tsv`: loci per exact RT
runs from **1.11** (mgnify_soil) to **5.49** (ncbi_bacteria), and records per locus is 1.00 in
every database because the same locus mined twice differs by database, not by record
duplication. This is the evidence `C1`/`C2` asked for; the claim statuses stay the operator's.

### Coordinate and sequence integrity — `g2_bt_status.tsv`

The RT interval is translated from the window DNA (table 11, strand-aware) and compared with the
stored protein:

| verdict | POP-RT-FAM | POP-RT-MULTI |
|---|---:|---:|
| `exact` | 2,532,006 | 5,290 |
| `alt_start` (alternative start codon read as M) | 491,051 | 1,365 |
| `code4_tga_trp` (TGA read as W — translation table 4) | 2,716 | 394 |
| `internal_stop_masked` (internal stop written `U`) | 8,699 | 758 |
| **`mismatch`** | **618** | **51** |
| `matches_opposite_strand` | **0** | **0** |
| not testable (RT outside/partly outside window, inverted window) | 15,598 | 1,154 |
| **verified total** | **3,034,472 (99.47%)** | **7,807 (86.63%)** |

Where `actual_window.start == 1` the absolute and window-relative frames coincide, so a pass
there cannot discriminate them. On the **frame-disambiguating** stratum alone (window start > 1,
1,799,424 records) the verified rate is **99.54%** — the check is not carried by the coinciding
cases.

The recoding classes are real properties of the corpus, not failures: Prodigal was run without a
declared genetic code, so table-4 organisms and proteins whose internal stops were written `U`
appear. They are named classes, never folded into `exact`.

### RT records with no RT CDS — `g2_rt_cds_classes.tsv`

All **31,504** (29,468 + 2,036; identical to g1's independent count) are classified, none dropped:

| class | n | recoverable? |
|---|---:|---|
| `no_prodigal_call_bt_verified_overlapping_cds` | 14,026 | **yes** — sequence and coordinates verified; Prodigal called a different ORF |
| `no_prodigal_call_bt_verified_no_overlapping_cds` | 162 | **yes** — verified; no ORF called there at all |
| `rt_outside_window` | 9,128 | sequence only; the context contig is shorter than the RT coordinates |
| `rt_partially_outside_window` | 3,636 | sequence only |
| `context_absent_window_inverted` | 3,924 | sequence only; window empty |
| `no_prodigal_call_bt_mismatch` | 628 | **no** — ill-posed |

**14,188 are fully recoverable** (RT sequence *and* coordinates), 16,688 keep a usable sequence
but no defensible genomic context, and 628 are ill-posed. In every record the protein is present:
`elig_exact_rt` is **100%**.

`g2_cds_sequence_carrier.tsv` settles g1's open question: a CDS protein sequence occurs only on
the `is_rt_gene` CDS (one per record wherever an RT CDS exists). **Neighbour proteins are not in
the corpus** and must be re-translated from `full_sequence` by any later neighbourhood analysis.

### Eligibility denominators — `g2_eligibility.tsv`, `g2_eligible_unit_counts.tsv`

| flag | distinct records | loci | physical loci | exact RTs |
|---|---:|---:|---:|---:|
| `elig_exact_rt` / `elig_rt_length` | 3,051,238 (100%) | 2,847,312 | 2,475,684 | 501,561 |
| `elig_rt_coords` / `elig_geometry` / `elig_rt_completeness` | 3,033,817 (99.43%) | 2,829,894 | 2,458,268 | 484,360 |

Geometry-ineligible records are named by reason (RT outside window 9,128; partly outside 3,636;
inverted window 3,924; mismatch 669). g3 must report this denominator effect, not silently drop.

### Twins, duplicates and conflicts

- **371,628 RefSeq/GenBank twin pairs** (743,256 loci) — **every one** has identical window DNA,
  RT protein, window coordinates and strand (`g2_twin_evidence.tsv`); **0** disagree and **0**
  are non-evaluable. Collapsing them is evidence-supported, and both spellings are retained.
- **8,462 byte-identical duplicate line groups**, each counted once; **10** span two family files
  and touch **9 loci**.
- **0 loci carry more than one exact RT.** 203,921 loci appear under more than one
  `source_database`, 70,553 carry more than one `rt_system_id`, 57 more than one `genome_id`.

### The canonical ncRNA count — `g2_ncrna_count_source.tsv`

Declared: **`len(ncrnas[])`** is the canonical count; `metadata.total_ncrnas` and
`intergenic_regions[].has_ncrna` are QC fields. Of 9,799 RT-FAM records where metadata exceeds
the array, **all 9,799** reference ncRNA ids that are absent from the array, and 9,694 records
carry `has_ncrna == true` with an empty array. The array holds 346,722 calls corpus-wide.

### MULTI — `g2_multi_stratum.tsv`

9,012 records, **all** multi-label, 568 order-normalised label sets, resolved state: **none**.
Separately, **20 records at 9 loci inside single-family files carry a genuine two-element label**
(`["RVT-UG2","Retron"]` and similar). They are flagged `multilabel` and must not enter two
single-family denominators. Why MULTI carries several labels is investigated in g4.

## 2 · Counts, including the ones that look bad (BS-5)

n_attempted: 3,059,700 records in 42 files
n_succeeded: 3,059,700 parsed, projected and classified
n_dropped: 0 — nothing is dropped; 669 mismatches, 16,688 context-mismatched and 628 ill-posed
records are flagged and retained

| | n |
|---|---:|
| derived datasets written | 7 (`g2_derived_registry.tsv`, hashes + content digests) |
| ncRNA calls / window CDS rows | 346,722 / 44,310,231 |
| second-count comparisons / disagreements | 58 / **0** |
| prior-work rows compared | 7 (2 CONFIRMED, 5 CHANGED-with-reason) |
| positive controls / failed | 78 / 0; seeded-bad rejected |

## 3 · The denominator's second count (WA-D.3)

`c03_second_count.sh` — awk slices the `rt_gene` and `actual_window` blocks out of raw bytes,
`sort -u` counts distinct keys. No Python, no JSON parser, no `g2lib`. Plus the landed **g1
bundle** as a third route. `g2_second_counts.tsv`: **58 rows, 0 disagreements**, including
records (3,059,700), `rt_system_id` (2,917,865), locus keys (2,847,312), exact-RT sequences
(501,561), records without an RT CDS (31,504), inverted windows (3,924), RT-not-inside-window
(16,752), and per-file record counts for all 42 files.

⚠️ The locus key and `rt_system_id` are **not independent** — the id encodes contig and RT start.
What the two routes test is the parser and the arithmetic, not two independent definitions.

## 4 · Claims

No claim status is proposed (the ledger is the operator's). Evidence recorded for `C1`/`C2`:
the five units above differ by factors that are themselves database-dependent (1.11–5.49 loci per
exact RT), so a raw-record count describes a different population from a locus or exact-RT count.

### Prior work — `g2_prior_reconciliation.tsv` (read only after the g2 values existed)

| quantity | verdict | detail |
|---|---|---|
| exact RT set | **CONFIRMED** | 501,561 keys, and the **key sets are identical** — 0 keys only in prior, 0 only in g2 |
| loci in more than one source file | **CONFIRMED** | 9, re-derived over all records |
| locus count | **CHANGED** | prior 2,663,087 vs g2 2,475,684 (physical) / 2,847,312 (locus) |
| twin pairs folded | **CHANGED** | prior 254,778 (id-string pairs) vs g2 371,628 (coordinate pairs) |
| loci carrying >1 `rt_system_id` | **CHANGED** | 70,553 — invisible at the prior id grain |

The locus difference decomposes exactly: prior grain is the `rt_system_id`
(2,917,865 − 254,778 = 2,663,087); g2's grain is the RT coordinate interval
(2,847,312 − 371,628 = 2,475,684). g2 sees 116,850 more twin pairs because a twin whose id
suffix differs is still a coordinate pair, which an id-string test cannot see.

## 5 · The self-adversarial pass (BS-14)

**1 · Where is a headline overstated? Name the word.**
- *"verified coordinates"* — **verified** means the DNA at those coordinates translates to the
  stored protein: an internal consistency check between two fields of one record, not external
  truth. Both fields can be wrong together if the pipeline wrote them from the same wrong place.
- *"collapse supported"* — **supported**, not proven: identical window DNA plus identical RT is
  strong evidence two entries are one physical locus, but assembly-level identity is not tested.
- *"canonical locus"* — the key is a coordinate interval on a contig accession; two different
  assembly versions of one contig are two loci here.
- *"recoverable"* for the 14,188 — recoverable **as sequence and coordinates**; the missing
  Prodigal call means no `partial` flag, so completeness for them rests on derived codons.

**2 · What alternative explanation produces this exact number?**
- *99.47% back-translation.* The obvious alternative is that it is **near-tautological**: where
  the pipeline called the ORF with Prodigal on this very window, the protein is by construction
  the translation of those coordinates. That is why the number is reported with its failures:
  the check demonstrably fires (669 mismatches, and on the fixture a one-base frameshift and a
  flipped strand are both caught). Its real power is over the records whose protein came from
  elsewhere — the MAG catalogues, where the mismatches and `U`-masked stops concentrate.
- *371,628 twins all agreeing.* Alternative: the window DNA hash is trivially equal because both
  entries were extracted from the same file. Not excludable from inside the corpus; what is
  measured is that no twin pair contradicts itself.
- *0 loci with two exact RTs.* Alternative: the locus key contains the RT interval, and a
  different protein at the same interval is rare by construction. True — the fixture shows the
  conflict class does fire when it exists.

**3 · Could this test have returned a negative?** It did: 669 mismatches, 16,752 RT-outside-window
records, 3,924 inverted windows, 628 ill-posed records, and 5 prior quantities that CHANGED.

**4 · Unit of every rate.** Named per table in `MANIFEST.tsv`; records, loci, physical loci,
exact RTs, genomes or controls — never mixed inside one table.

**5 · Numbers with no producing script.** None in `tables/`. In this README the percentages are
ratios of two named columns of a landed table.

**6 · What was withdrawn or weakened.**
- **Withdrawn:** "loci in more than one source file = 0". That was an artefact of counting only
  first copies of byte-identical lines; the honest number over all records is 9, which also
  re-confirms the prior project's finding. The corrected measure is landed.
- **Withdrawn:** the first merge design (per-group Python aggregations over ~3M groups). It was
  replaced by a vectorised merge in its own process; no number depended on the discarded code.
- **Weakened:** the exact-RT count was going to be compared with the prior by row count; the
  prior file's comment lines made that read 501,570. Replaced by a set comparison.
- **Not weakened but stated:** determinism of the derived parquet files was **tested** (an
  independent merge rerun reproduced all six byte-identically), not assumed.

## 6 · What changed from the plan

1. **The pass and the merge are two scripts** (`e01` then `m02`). The first version did both in
   one process; the merge was replaced wholesale after it proved slow and memory-hungry.
2. **`matches_opposite_strand` and `frame_disambiguating`** were added after the prior-work audit
   and before the census pass, so a strand-convention error cannot hide inside `mismatch` and the
   coinciding-frame records cannot inflate the verification rate.
3. **The recoding classes** (`code4_tga_trp`, `internal_stop_masked`) were designed after probing
   real records and before the census (WA-D.4), because the corpus contains both.
4. **PLAN.md was written alongside the code**, not before it; the rules it states were fixed in
   `g2lib.py` before the census pass and were not changed after seeing results.

## 7 · Reproduction log (BS-3, WA-B.2)

```
$ bash results/dbchar_g2_canonical_units/run.sh
== c04 self-validation: the controls must reject a seeded-bad expectation
   rejected the seeded-bad case, as required
== c04 positive controls ...        c04: 78 controls, 0 failed
== e01 extraction pass ...          47 s wall, 1,790 worker-s, 3,059,700 records
== m02 build the derived tables ... records=3,059,700 exact_rt=501,561 loci=2,847,312
                                    physical_loci=2,475,684 ncRNA calls=346,722 CDS=44,310,231
== a02 unit ladder, QC, eligibility
== c03 independent second count ... 2 min
== c05 reconcile ...                58 rows, 0 DISAGREE; prior 7 rows
== assemble ...                     40 summary rows, 28 tables, 7 derived datasets
  OK × 28 tables, OK MANIFEST.tsv
REPRODUCED: every landed table is byte-identical on rerun.
wall 13:01.86, peak RSS 27.8 GB, exit 0
```

Derived-dataset determinism was tested separately: an independent merge rerun from the same
shards reproduced all six parquet files and the FASTA **byte-identically**, which is what makes
the sha256 column of `g2_derived_registry.tsv` meaningful on a rerun.

## 8 · Derived datasets

`g2_derived_registry.tsv` records bytes, sha256 and a writer-independent content digest for
`rt_records_v1`, `rt_loci_v1`, `rt_physical_loci_v1`, `rt_exact_v1` (+`.faa`),
`rt_ncrna_calls_v1` and `rt_window_cds_v1`. They are registered in `data/README.md` and live in
`data/derived/`, not in this bundle: they re-derive from `run.sh` in ~15 minutes.
`VIEWS.md` + `scripts/pull.py` define and run the declared views over them.

## 9 · Acceptance — the half that is not automatable

Open `INPUTS.tsv` and recognise the 48 inputs: 42 corpus files, the two prior derived artifacts
compared against, and four files of the landed g1 bundle.
