# Stage F · Taxonomic and ecological distribution
**Proposed addition, smaller scope.**

## 0 · The point of this task

We do not know where retrons actually live — which phyla carry them, which environments,
and how much of any apparent pattern is simply what has been sequenced. The taxonomy field
in our source data is **two different schemas** depending on the source database, and most
of one schema has no phylum at all, so a naive breakdown silently degrades. Once this lands
we have a distribution corrected for database composition, and a clear statement of which
taxonomic claims the corpus can support. That also tells the diversity stage which
cross-family comparisons are biology and which are sampling artefacts.

## 1 · Where this stands

Partly inside `x1_neighbourhood` — which established that retrons rank **27th of 41** RT
families on Tier-A defence carriage, an inherently comparative, cross-family result — but
never as its own stage. `stage 1` (`r01`/`r02`) delivers the raw counts and the redundancy
ladder; this stage turns them into a distribution.

Prior work also recorded one live example of the schema trap: **a GTDB lineage string filed
under a column headed `ecosystem`** in the `gem_metadata.tsv` file — flagged as a testable
claim, not a fact.

## 2 · ⚠️ The schema trap, first

**`taxonomy.full_lineage` is two schemas keyed by `taxonomy_system`:**

| system | shape |
|---|---|
| `gtdb` | 7 fields — domain, phylum, class, order, family, genus, species |
| `ncbi` | 3 fields — **no phylum** |

**~61% of rows are ncbi 3-field.** A phylum- or genus-level breakdown therefore works on
gtdb rows and **silently degrades** on the majority. Count per system, never pooled.

Also on record: **`seq_id → rt_system_id` is not a function** — do not assume a one-to-one
join.

## 3 · The repair path

The D5 metadata files can restore the missing ncbi lineages:

    RESEARCH-in-sleep-/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/databases_metadata_files/
      gtdb_bacteria_metadata.tsv.gz          715,231 lines claimed
      gtdb_archaea_metadata.tsv.gz            17,426
      ncbi_bacteria_assembly_summary.txt   2,864,739
      ncbi_archaea_assembly_summary.txt       32,339
      mgnify_human_gut_metadata.tsv          289,232
      gem_metadata.tsv                        52,516   <- the mislabelled `ecosystem` column
      mgnify_marine_metadata.tsv              50,867
      mgnify_soil_metadata.tsv                20,909

⚠️ Each `source_database` value in the corpus maps to one of these files. The join is its
own row — it is **not** part of the census.

## 4 · What must be delivered

- **Distribution by domain / phylum / genus**, per RT family, **within each
  `taxonomy_system`**.
- **Environment breakdown** where the metadata supports it (`environment`, and the MGnify /
  GEM sources).
- **A database-composition correction** — the same organism can appear in GTDB *and* NCBI;
  say so before reporting any rate.
- **A statement of which taxonomic claims the corpus can support**, and which are
  unanswerable because the lineage is absent.
- **Archaeal retrons** as a specific question — a parked idea, and the first probed record
  in the corpus happens to be an archaeon (`d__Archaea; p__Halobacteriota`).

## 5 · Prerequisites

**Stage 1** (`r02`'s redundancy ladder). Serves **stage 9** — a diversity comparison
uncorrected for database composition measures sequencing effort.
