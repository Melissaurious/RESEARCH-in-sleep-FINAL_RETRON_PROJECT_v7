# dbchar_g1_corpus_identity

STATUS: VERIFIED — `run.sh` was rerun from this assembled bundle and reproduced all 24 landed
tables and `MANIFEST.tsv` byte for byte (BS-3, WA-B.2); log in §7.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **LIGHT** (launcher §7) — a provenance skeleton for the corpus; it may not enter a
claim, figure or paper by itself (WA-B.3). Plan written before the census:
`ARIS_OUTPUT/01_database_characterization/dbchar_g1_corpus_identity/PLAN.md`.

---

## 1 · What was measured

The exact inventory of the registered raw corpus root
`/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june/` — every entry,
every line, every record — as a census (WA-D.2), stratified by declared anchor population.

### The corpus, identity-pinned

| quantity | value | table |
|---|---:|---|
| entries in the corpus root | 43, all regular `.jsonl` files, none other | `s01_corpus_root.tsv` |
| bytes | 81,007,695,609 | `s01_corpus_root.tsv` |
| per-file sha256 | 43 rows, all mode `-r--r--r--` | `s01_file_identity.tsv` (also `INPUTS.tsv`) |
| lines (= newlines; every file ends in `\n`, 0 CRLF) | 3,358,182 | `s01_corpus_root.tsv`, `s02_populations.tsv` |
| **record-manifest sha256** | `8e9b7999954b460d2bdfc558c605d26610d58e6901788f61720e11eafdc41d00` | `s02_record_manifest_digest.tsv` |
| schema document, project copy = V5 copy | identical, sha256 `7aa458fa…0873cc` | `s01_schema_identity.tsv` |

The record-manifest digest is sha256 over `source_file \t line_no \t byte_offset \t byte_len \t
sha256(raw line)` for every line in file/line order. It names the exact record set analysed:
any later gate that regenerates the manifest (s02 writes it to
`ARIS_OUTPUT/rerun-dbchar_g1_corpus_identity/cache/record_manifest.parquet`) and gets this digest is
reading the same records.

### Anchor populations — `s02_populations.tsv`

| id | the population, in words | lines | files |
|---|---|---:|---:|
| `POP-RT-FAM` | parsed records, `anchor_type == "RT"`, in the 41 single-RT-family files | **3,050,688** | 41 |
| `POP-RT-MULTI` | parsed records, `anchor_type == "RT"`, in `master_MULTI_merged_oriented.jsonl` | **9,012** | 1 |
| `POP-NCRNA` | parsed records, `anchor_type == "ncRNA"` (any file) | **298,482** | 1 |
| `POP-OTHER` | any other/missing `anchor_type`, or RT in a file of another role | **0** | 0 |
| `POP-UNPARSED` | blank, bad UTF-8, bad JSON, or non-object lines | **0** | 0 |
| **ALL** | every line of the 43 files | **3,358,182** | 43 |

The anchor populations are **file-pure**: every `ncRNA` record is in `master_ncRNA-anchored`, and
that file contains nothing else (`s05_prior_reconciliation.tsv`, last two rows). RT-anchored
records = 3,059,700.

### Source-database composition — `s02_source_database.tsv`

| `source_database` | POP-RT-FAM | POP-RT-MULTI | POP-NCRNA |
|---|---:|---:|---:|
| ncbi_bacteria | 2,256,718 | 3,098 | 180,562 |
| gtdb_bacteria | 600,156 | 399 | 83,564 |
| mgnify_human_gut | 139,494 | 2,692 | 21,650 |
| gem | 22,261 | 10 | 4,605 |
| mgnify_soil | 14,141 | 1,517 | 4,356 |
| mgnify_marine | 7,751 | 201 | 1,875 |
| ncbi_archaea | 7,074 | 841 | 1,253 |
| gtdb_archaea | 3,093 | 254 | 617 |

Unit: records (raw lines), not loci — the same locus mined from two databases is two records
here (redundancy is g2's). Per file × anchor × database: `s02_source_database_by_file.tsv`.

### MULTI and multi-label — `s02_multilabel_by_file.tsv`, `s02_multilabel_sets.tsv`

- `POP-RT-MULTI`: 9,012 records, **all** multi-label (0 single-label records in the MULTI file);
  568 order-normalised type sets (6,097 records with 2 tokens, 2,915 with 3); 221 of those sets
  occur under more than one raw spelling, covering 8,465 records (sums over
  `s02_multilabel_sets.tsv`). `metadata.detected_by` is `myRT` alone for all 9,012; all have
  empty `system_subtypes`.
- **20 multi-label records sit inside single-family files**, as 10 byte-identical pairs: each
  record is filed once in `master_Retron` and once in `RVT-UG2` (4), `RVT-UG10` (3), `RVT-UG11`
  (2) or `RVT-GII` (1), with a genuine two-element `system_types` list (`["RVT-UG2","Retron"]`).
  They are **not** in the MULTI file, so a family-by-file analysis pools them into two single
  families at once. Flagged; not removed.

### Parse and validation — `s02_parse_census.tsv`, `s02_validation_by_population.tsv`

Parse failures: **0** in every class over all 3,358,182 lines, with a strict decoder (the prior
g0 parser used `errors="replace"` and skipped blank lines, so it could not have counted either).

Declared checks that fired (flags only; nothing dropped):

| check | POP-RT-FAM (n=3,050,688) | POP-RT-MULTI (n=9,012) | POP-NCRNA (n=298,482) |
|---|---:|---:|---:|
| V09a RT record with no `cds_annotations[]` flagged `is_rt_gene` | 29,468 | 2,036 | — |
| V12 `metadata.total_ncrnas` ≠ `len(ncrnas)` | 9,799 (all metadata > array) | 0 | 69,719 (67,617 metadata < array; 2,102 >) |
| V16 `actual_window.start > actual_window.end` | 3,661 | 263 | 0 |
| V17 `has_ncrna` true somewhere while `ncrnas[]` empty | 9,694 | 0 | 0 |
| V20b `taxonomy_system` outside the schema-documented set | 2,286,053 | 3,949 | 186,420 |

Every other declared check (V01–V08, V09b, V10, V11, V13–V15, V18, V19, V20a, V21a, V21b) is
**0** in every population, and each has a positive control that fires on the fixture (§3).

### Byte-identical record lines — `s02_byte_identical_records.tsv`

8,452 extra copies within one RT-family file, 49 within the ncRNA-anchored file, and 10 across
files (the multi-label pairs above). Unit: raw lines with an identical sha256. This is exact
byte identity only; semantic redundancy (same locus, different bytes) is g2's.

### Observed structure vs the schema — `s02_schema_paths.tsv`

Per population, every key path observed, whether the schema documents it, records carrying it,
occurrences, nulls, observed types. Discrepancies that matter downstream:

1. **`master_ncRNA-anchored` has its own ncRNA element schema, split in two.** No element has
   `sequence_oriented` or `orientation_corrected` (both documented); 226,741 elements carry an
   undocumented `sequence` plus `length`, `location_type`, `gc_content`, `selection_reason`;
   71,867 elements carry an undocumented `rfam_family_id` (always null) and a null
   `structure_annotation`, and lack those fields. 226,615 + 71,867 records = 298,482 (the
   population), consistent with a record-level partition — disjointness was not tested.
2. **`ncrnas[].structure_annotation`** — the schema's "canonical" structure source — is present
   on 4,743 of 346,716 ncRNA elements in POP-RT-FAM (4 of 6 in POP-RT-MULTI), and on 8,414 of
   298,608 in POP-NCRNA (null on 71,867).
3. **`cds_annotations[].sequence`** occurs exactly once in 3,021,220 RT-FAM records and never
   in ncRNA-anchored records; 3,021,220 = records with an `is_rt_gene` CDS. Consistent with
   **only the RT CDS carrying a protein sequence** — neighbour proteins would then have to be
   re-translated from `full_sequence`. Which CDS carries it was **not** checked here.
4. 3,700 RT-FAM, 264 MULTI and 293 ncRNA-anchored records have **no CDS at all**; 10,429 RT-FAM
   records have no intergenic regions.
5. `taxonomy_system` values are `gtdb`, `ncbi`, `unknown`; the documented `mmseqs2_inferred` occurs
   0 times (a census over all observed values, `s02_taxonomy_system.tsv`). `gem` is `unknown`
   for all its records; 6 `ncbi_bacteria` records are `unknown`.
6. `ncrnas[].position_relative_to_rt` in RT records: int 14,825, null 331,897.
7. `rt_gene` and `anchor_gene_id` are `null` for all 298,482 ncRNA-anchored records (V08 = 0
   confirms no ncRNA-anchored record carries an RT).

## 2 · Counts, including the ones that look bad (BS-5)

n_attempted: 43 corpus files / 3,358,182 lines
n_succeeded: 43 files hashed / 3,358,182 lines parsed as JSON objects
n_dropped: 0 — nothing is dropped by design; anomalies are flags

| | n |
|---|---:|
| corpus-root entries attempted / hashed | 43 / 43 |
| lines attempted / parsed as JSON objects | 3,358,182 / 3,358,182 |
| lines dropped | **0** — nothing is dropped by design; every anomaly is a flag |
| schema documents pinned | 2 (identical) |
| inputs hashed in `INPUTS.tsv` | 50 (43 corpus, 2 schema, 4 prior-g0 files, 1 stage brief) |
| second-count comparisons / disagreements | 450 / **0** |
| prior-assumption comparisons / differences | 231 / **2** (§4) |
| positive controls / failed | 107 / 0; seeded-bad run rejected, as required |
| figures | 0 (LIGHT gate) |

The ugly counts are in §1: 31,504 RT records with no RT CDS; 3,924 inverted windows; 79,518
records whose metadata ncRNA total disagrees with the array; 20 multi-label records hidden in
family files; 8,511 byte-identical extra lines.

## 3 · The denominator's second count (WA-D.3) and positive controls

**Independent route** (`s03_second_count.sh`): coreutils `wc -l` per file, and `LC_ALL=C grep -no`
extraction of the serialised `"anchor_type"` and `"source_database"` tokens, paired per line in
awk. No Python, no JSON parser, no shared code with s02. `s05_second_counts.tsv`, **450 rows, 0
disagreements**:

| population | route A (s02, `json.loads`) | route B (s03) | rows |
|---|---|---|---:|
| newlines per file | s01 Python byte count | `wc -l` | 43 |
| lines per file | s02 line split | `wc -l` + unterminated tail | 43 |
| records per file × anchor × database | s02 census | grep token pairs | 317 |
| records per file (any anchor/database) | s02 parsed objects | lines with a token pair | 43 |
| POP-RT-FAM, POP-RT-MULTI, POP-NCRNA totals | s02 | grep, same definition | 3 |
| all lines | s02 | `wc -l` | 1 |

**Positive controls** (`s04_positive_controls.tsv`, EVIDENCE_STANDARDS §6). The fixture base is
the schema document's own worked example record, placed in `master_Retron`, so its expected flag
set is empty *by documentation*. 34 fixture lines (plus a CRLF line and an unterminated final
line) each carry a hand-written expected result;
every parse class, every one of the 24 checks, byte-identical duplicate detection (within and
across files), CRLF and unterminated-tail detection, newline-aligned chunk tiling, and the grep
joint count all fire exactly as expected. The shipped s01, s02, s03 and s05 run end to end on
it as subprocesses, and **s05 must report exactly the four disagreements seeded into it** (two
lines grep can read but JSON cannot). `run.sh` first runs the controls with a corrupted
expectation (`--seed-bad`) and aborts unless they **fail**.

## 4 · Claims

LIGHT gate: **no claim status is proposed.** The launcher lists this gate as `C1` supporting.
Evidence recorded for whoever settles `C1`/`C2`: the corpus is 3,358,182 records in three anchor
populations; RT-anchored record counts are strongly non-uniform across source databases
(ncbi_bacteria 2,259,816 of 3,059,700 RT-anchored records, 73.86%); and 8,511 lines are byte-identical copies — a lower bound on
record-level redundancy.

### Prior assumptions — `s05_prior_reconciliation.tsv` (231 rows)

Prior values were in context before the census (read during the reuse audit), so this is
**reconciliation, not blind re-derivation**. None enters any count.

- **AGREE (229):** all 42 prior-g0 per-file sha256, bytes, record counts and 0 unparseable lines;
  prior-g0 P-REC 3,059,700; all 8 prior per-database record counts; the schema document's
  `wc -l` listing for all 43 files; the stage brief's 3,358,182; prior-g0 MULTI facts (9,012
  records; 9,009 one-element lists; 23 two-element lists over 42 files; 0 non-empty subtypes);
  the schema note's observed taxonomy set `gtdb|ncbi|unknown`; and both file-purity scope rules.
- **DIFFER (2):** (a) `master_ncRNA-anchored` is in scope here and was never opened by prior g0 —
  scope, not a count error; (b) the schema field list's documented `taxonomy_system` values
  (`gtdb|mmseqs2_inferred`) vs observed (`gtdb|ncbi|unknown`) — already noted in the schema's own
  appendix, still wrong in its field list.
- Not reconciled because the unit differs: prior g0's "9 loci in more than one file" is a locus
  count; this gate's 10 cross-file byte-identical pairs is a line count. g2 owns the locus unit.

## 5 · The self-adversarial pass (BS-14)

**1 · Where is a headline overstated? Name the word.**
- *"identity-pinned"* — pinned to **this path at these hashes on borg**. The Ibex mirror was not
  located or compared and remains `DO-NOT-USE`.
- *"0 parse failures"* — against the declared classes. A line that is valid JSON but semantically
  corrupt (e.g. a truncated sequence string) parses `ok`; that is g2's integrity test.
- *"only the RT CDS carries a sequence"* — the word is **only**. Measured: one occurrence per record
  and a count equal to records with an RT CDS. Which CDS carries it was not tested.
- *"file-pure anchor populations"* — true of `anchor_type`; says nothing about whether an
  ncRNA-anchored locus overlaps an RT-anchored locus in another file (g2).

**2 · What alternative explanation produces this exact number?**
- *0 disagreements in 450 rows* — both routes could share a blind spot if a key were serialised
  differently. Excluded by construction: s02 reads parsed keys, s03 bytes; a record with the key
  absent, null, doubled or unparseable lands in a distinct token class and would disagree, and
  the fixture proves s05 reports such cases.
- *All 229 prior agreements* — a shared input guarantees agreement on hashes and line counts;
  that is what they test. Record counts could agree while both parsers drop the same lines; the
  strict decoder and `wc -l` route rule that out (0 blanks, lines = newlines).
- *V20b 2.47 M* — measures the schema's documentation, not the data; read it as a doc defect.

**3 · Could this test have returned a negative?** Yes. It returned anomalies from 263 to 69,719
records (V09a, V12, V16, V17), a sub-schema split, 20 misfiled multi-label records and 2 prior
differences. Every zero has a positive control that returned non-zero on the fixture; the
controls themselves were watched failing on a seeded-bad expectation.

**4 · Unit of every rate.** Lines or records throughout (named per table in `MANIFEST.tsv`); key
occurrences only in `s02_schema_paths.tsv`, labelled. No locus, genome or sequence unit appears.

**5 · Numbers with no producing script.** None in `tables/`. In this README: 73.86% (2,259,816 /
3,059,700, from `s02_source_database.tsv`), 31,504, 79,518, 8,511 and the MULTI 568/221/8,465 are sums or ratios over named table
columns; the run timings in §7 are stdout, deliberately not in any table.

**6 · What was withdrawn or weakened.**
- **Withdrawn during development:** the first path census flagged `genomic_context`, `metadata`,
  `rt_gene`, etc. as "undocumented". That was my parser reading only leaf paths from the schema;
  fixed (containers of documented leaves are documented) before landing.
- **Weakened:** the CDS-sequence observation, from "neighbour proteins are absent" to "consistent
  with only the RT CDS carrying a sequence"; and the ncRNA sub-schema, from "partition" to
  "consistent with a partition".
- **Not claimed:** any interpretation of V16 inverted windows or V12 direction — flagged for g2/g3.

## 6 · What changed from the plan

1. **V12–V14 got a direction table** (`s02_metadata_count_mismatch_direction.tsv`), added after
   V12 fired, to show metadata > array vs < array. Additive; no declared check changed.
2. **`source_database`/`anchor_type` labels keep absent vs null distinct** (`<absent>`, `<null>`),
   so s05 can pair them with grep's token classes exactly. Added before the landed run.
3. **Documented-path parsing fixed** (§5, question 6).
4. **Scratch driver** `logs/dev_full_pass.sh` ran the pipeline in the scratch layout; the
   landed tables come from that run and were then reproduced by this bundle's `run.sh`.
5. Throughput smoke used a seeded, size-stratified chunk sample (10 chunks, 550 MB): 67.8 MB per
   worker-second; the full pass measured 49.5 (contention), inside the 2× band.

## 7 · Reproduction log (BS-3, WA-B.2)

```
$ bash results/dbchar_g1_corpus_identity/run.sh
== s04 self-validation: controls must reject a seeded-bad expectation
   rejected the seeded-bad case, as required
== s04 positive controls ...            s04: 107 controls, 0 failed
== s02 record census ...                s02 pass wall 41.6 s, 1,635.8 worker-s, 3,358,182 records
== s01 file identity ...                ~55 s
== s03 independent second count ...     ~60 s
== s05 reconcile ...                    second counts 450 rows, 0 DISAGREE; prior 231 rows, 2 DIFFER
== assemble ...                         28 summary rows, 24 tables in MANIFEST
  OK × 24 tables, OK MANIFEST.tsv
REPRODUCED: every landed table is byte-identical on rerun.
run.sh wall=169.87s exit=0
```

Second rerun under `/usr/bin/time -v` (also REPRODUCED): wall 2:49.8, user 1,828.3 s + system
154.2 s = **0.55 CPU-h**, peak RSS of the largest process 3.36 GB (borg, 48 cores, corpus ~95%
page-cached per `fincore`). A cold page cache adds NVMe read time for 81 GB; not measured.

## 8 · Handoff to g2 (not started)

g2 can proceed on this pin. Carry forward as flags, not filters: the 20 multi-label records in
family files; 8,511 byte-identical lines; 31,504 RT records without an RT CDS; 3,924 inverted
windows (V16 — the coordinate-frame test must define `x − actual_window.start` for them); CDS-less
records; the ncRNA-anchored sub-schema split and missing `sequence_oriented`; the CDS-sequence
question (§1, item 3).

## 9 · Acceptance — the half that is not automatable

`bundle_valid.sh` passing is not acceptance. Open `INPUTS.tsv` and recognise the 50 inputs.
