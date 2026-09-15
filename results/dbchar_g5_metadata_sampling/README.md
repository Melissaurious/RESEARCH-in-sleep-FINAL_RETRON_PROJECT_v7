# dbchar_g5_metadata_sampling

STATUS: VERIFIED — `run.sh` was rerun from this assembled bundle and reproduced all 16 landed
tables and `MANIFEST.tsv` byte for byte (BS-3, WA-B.2). Log in §7.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **FULL** (launcher §7). Inputs: the g2 record table over the g1 corpus pin, plus the nine
registered metadata catalogues.

---

## 1 · What was measured

Metadata/taxonomy/source-database coverage and overrepresentation on **schema-specific**
populations — never pooled across taxonomy systems, and never across catalogues.

### The join, per database — `g5_join_coverage.tsv`, `g5_catalogue_shape.tsv`

Each catalogue is joined on the key its own database names, with `RS_`/`GB_` normalised on
**both** sides:

| source_database | genomes | % genomes joined | catalogue rows |
|---|---:|---:|---:|
| gtdb_bacteria | 299,306 | 100.0 | 715,230 |
| gtdb_archaea | 1,806 | 100.0 | 17,245 |
| gem | 13,645 | 100.0 | 52,515 |
| mgnify_human_gut | 87,226 | 100.0 | 289,232 |
| mgnify_marine | 4,817 | 100.0 | 50,866 |
| mgnify_soil | 5,461 | 100.0 | 20,908 |
| ncbi_archaea | 4,047 | 100.0 | 32,837 |
| ncbi_bacteria | 1,237,519 | **99.9999** | 2,864,737 |

**One NCBI genome does not join.** It is named in `g5_unjoined_examples.tsv`, not rounded away.

⚠️ This is the weakest number in the gate, and it is a **description, not a test**: a corpus
whose `genome_id` values were harvested *from* these catalogues will resolve into them by
construction. It says a row exists — not that the row is the right genome.

### What a quality filter can actually speak for — `g5_quality_availability.tsv`

A join that resolves a *row* is not a join that resolves a *value*:

| concept | GTDB (both) | GEM | MGnify (all three) | NCBI (both) |
|---|---|---|---|---|
| completeness | 100% | 100% | 100% | **no such column** |
| contamination | 100% | 100% | 100% | **no such column** |
| N50 | 100% | 100% | 100% | **no such column** |

The NCBI assembly summaries carry no CheckM-style columns at all, so **a completeness filter can
speak for 412,261 of 1,653,827 genome entries (24.93%)** — the other **1,241,566 (75.07%)** have
no such value to filter on. Any quality-filtered view must name the databases it covers.
(The denominator sums genomes per source database, so a genome deposited in two databases counts
once per database.)

### Taxonomy, per schema — `g5_rank_coverage_by_system.tsv`

The corpus carries three systems and they are **different schemas**:

| system | records | domain | phylum | genus | species |
|---|---:|---:|---:|---:|---:|
| `gtdb` | 769,693 | 100% | **100%** | 99.78% | 98.12% |
| `ncbi` | 2,259,269 | 100% | **0%** | 99.66% | 99.66% |
| `unknown` | 22,276 | 0% | 0% | 0% | 0% |

The NCBI block has **no phylum by construction** — a pooled "phylum coverage" would report ~34%
and mean nothing. `unknown` is entirely GEM (22,271 records) plus 5 NCBI records; GEM's GTDB
lineage lives in the column headed `ecosystem`, which this gate **verified** rather than assumed:
4,998 of the first 5,000 rows start with `d__` (`g5_gem_ecosystem_column.tsv`).

### Overrepresentation, and what redundancy correction does to it — `g5_redundancy_correction.tsv`

| taxonomy system | top species | % of **records** | % of **exact RTs** | top-10 % of records | top-10 % of exact RTs |
|---|---|---:|---:|---:|---:|
| `ncbi` | *Escherichia coli* | **19.97** | **6.09** | 66.21 | 18.95 |
| `gtdb` | *Escherichia_coli* | 8.57 | 2.21 | 26.86 | 9.85 |

This is the `C8` evidence in one line: the apparent taxonomic concentration of the corpus falls
by roughly **3×** when the unit changes from raw records to exact RT sequences. Per-species and
per-genus tables at all three units are in `g5_overrepresentation_species.tsv` / `_genus.tsv`.

## 2 · Counts, including the ones that look bad (BS-5)

n_attempted: 3,051,238 distinct raw records / 1,653,827 genomes / 9 catalogues
n_succeeded: all joined or explicitly reported as unjoined
n_dropped: 0

| | n |
|---|---:|
| genomes that do not join | 1 (ncbi_bacteria) |
| genomes with no completeness value available | 1,241,566 (75.1%) |
| records whose taxonomy system is `unknown` | 22,276 |
| records with a family-level fallback genus (`[family:…]`) | see `n_family_level_fallback_brackets` |
| second-count comparisons / disagreements | 16 / **0** |
| positive controls / failed | 41 / 0; seeded-bad rejected |

## 3 · The denominator's second count (WA-D.3)

`c03_second_count.sh` recounts, by awk + `sort -u` over the raw corpus bytes and the catalogue
files, the distinct genomes per source database and the distinct key count of every catalogue.
All 16 comparisons agree.

**Positive controls** (41, `c02_positive_controls.tsv`) — required here because an all-100% join
is exactly the shape a broken key produces:
- a key **taken from** each of the 8 catalogues joins (the search can return non-zero);
- a fabricated accession joins **nowhere** (it can return zero);
- a catalogue whose header sits behind a comment line is still read;
- `RS_`/`GB_` normalise on both sides;
- a constructed redundant species must dominate on records and stop dominating on exact RTs.

## 4 · Claims

No claim status proposed. `C8` (supporting): the top-10 species share falls from 66.2% of records
to 19.0% of exact RTs under `ncbi`, so diversity and distribution statements change materially
with the unit.

### Prior work — `g5_prior_reconciliation.tsv`

Reading A (a catalogue row resolves) is **CONFIRMED** at 100% for all eight databases against the
prior g0 bundle. Reading B (a quality *value* is obtainable) is **CHANGED by route**: g5 measures
**native** availability only and reports 0% for NCBI, where the prior reached 25.5%/42.8% through
a GTDB `ncbi_genbank_assembly_accession` bridge that g5 does not implement. Neither number is
wrong; they answer different questions, and the bridge remains available for a later gate.

## 5 · The self-adversarial pass (BS-14)

**1 · Overstated words.** *"100% joined"* — see the circularity note in §1; the word doing
unearned work is **joined**. *"coverage"* for a taxonomy rank means a non-empty string, not a
correct assignment. *"overrepresentation"* is measured against the corpus itself, not against any
external expectation of how common a species should be.

**2 · Alternative explanations.** The 3× drop in species concentration could reflect sequencing
effort rather than biology — heavily sequenced species contribute many near-identical genomes;
that is precisely why the exact-RT unit is reported beside the record unit rather than instead of
it. The `unknown` taxonomy block is entirely GEM, so "unknown" is a catalogue property here, not
a property of the organisms.

**3 · Could this have returned a negative?** It did, twice, and both were my own defects caught by
the controls: the first run reported **0%** join for GTDB (prefix stripped on one side only) and
"key column absent" for both NCBI catalogues (a comment line before the header). Both were fixed
before any number was landed, and the two-sided join controls now exist to catch a recurrence.

**4 · Unit of every rate.** Genomes, records, loci or exact RTs — named per table in
`MANIFEST.tsv`.

**5 · Numbers with no producing script.** None in `tables/`. The 24.9% / 74.8% figures in §1 are
sums over `g5_quality_availability.tsv`.

**6 · What was withdrawn or weakened.**
- **Withdrawn:** the first join implementation and its 0% GTDB / absent-NCBI result.
- **Weakened:** reading B against the prior, from a comparison to a route difference.
- **Weakened:** the lineage-slot table is an estimate on a seeded 200k sample, labelled as such;
  every other number in the gate is a census.

## 6 · What changed from the plan

The quality-availability table was added after the join came back at ~100%: a join rate alone
would have implied metadata that NCBI does not carry.

## 7 · Reproduction log (BS-3, WA-B.2)

```
$ bash results/dbchar_g5_metadata_sampling/run.sh
== c02 self-validation: rejected the seeded-bad case, as required
== c02 positive controls ...  c02: 41 controls, 0 failed
== j01 join coverage, taxonomy schemas, quality availability, overrepresentation
== c03 independent second count (awk + sort -u over corpus and catalogues)
== c04 reconcile ...          16 rows, 0 DISAGREE; prior 16 rows
== assemble ...               33 summary rows, 16 tables
  OK × 16 tables, OK MANIFEST.tsv
REPRODUCED: every landed table is byte-identical on rerun.
wall 200.9 s, exit 0
```

## 8 · Acceptance

Open `INPUTS.tsv` and recognise the 53 inputs: 42 corpus files, the g2 record table, nine
metadata catalogues and the prior join-rate table.
