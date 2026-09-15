# Retro — dbchar_g5_metadata_sampling (2026-09-15)

Bundle: `results/dbchar_g5_metadata_sampling/` — REPRODUCIBLE, human_input_audit PENDING.
16 tables, rerun 200.9 s.

## What happened

- Catalogue joins resolve for ~100% of genomes across all eight databases (one NCBI genome does
  not, and it is named rather than rounded away). The gate then says plainly that this is a
  **description, not a test**: a corpus whose `genome_id` values were harvested *from* these
  catalogues resolves into them by construction.
- The number that matters is the one the join rate hides: a completeness **value** exists for only
  412,261 of 1,653,827 genome entries (**24.93%**), because the NCBI assembly summaries carry no
  CheckM-style columns at all. Any quality-filtered view must name the databases it can speak for.
- Taxonomy is reported **per schema**, never pooled: the NCBI block has no phylum by construction,
  so a pooled "phylum coverage" would read ~34% and mean nothing.
- Redundancy correction is the `C8` evidence in one line: *E. coli* is 19.97% of NCBI records and
  6.09% of exact RTs; top-10 species fall from 66.21% of records to 18.95% of exact RTs.

## What went wrong

- **The first join read 0% for GTDB** (the `RS_`/`GB_` prefix was stripped on one side only) and
  **"key column absent" for both NCBI catalogues** (a comment line sits before the header). Both
  were my defects, both were caught before any number was landed, and both are now covered by
  two-sided join controls and a header-searching reader.
- This is the gate where an **all-100% result was the warning sign**, not the reassurance: 41
  positive controls exist here precisely because a broken key produces exactly that shape. A key
  taken from each catalogue must join; a fabricated accession must join nowhere.
- Against the prior work, reading B (a quality *value* is obtainable) is **CHANGED by route**, not
  refuted: the prior reached 25.5%/42.8% for NCBI through a GTDB `ncbi_genbank_assembly_accession`
  bridge that this gate does not implement. Neither number is wrong; they answer different
  questions, and the bridge is available to a later gate.

## Proposal (not an amendment — WA-S.2)

**A rate at or near 100% requires a negative control in the same table.** The controls that saved
this gate were added because the result looked too clean; the agreement should not depend on a
session noticing. `EVIDENCE_STANDARDS` §6 already requires a positive control for a zero — the
symmetric case is a one.
- *Would have caught:* this gate's first join, which read 0% and 100% for the same reason (a key
  normalisation applied on one side), and which no existing rule required a control for.
- *Would wrongly reject:* a census where 100% is definitionally true — e.g. "every record has a
  source file" — which would have to declare `n/a - true by construction` and say why.

## Carried into later gates

The per-schema taxonomy tables and the quality-availability table are what any downstream
"high-quality genomes only" view must be built on; the 75.07%-without-a-value figure is the
denominator effect that view inherits.
