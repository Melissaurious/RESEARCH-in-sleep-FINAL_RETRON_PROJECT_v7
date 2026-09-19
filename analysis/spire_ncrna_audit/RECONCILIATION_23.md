# Reconciliation — the 23 pilot "existing-CM rescues" vs the canonical records

**Status:** data-representation reconciliation, 2026-09-18. No CM was rerun globally; the only
Infernal output involved is the pilot's own 219-window search (`ARIS_OUTPUT/.../pilot_cm/`).
This supersedes the earlier wording in `README.md`/`NEXT_SCALE_PLAN.md` ("a global search-space
bug", "Run 1: rescan everything"); both are withdrawn below.

Canonical reference: Z6 (`dbchar-workbench` commit `12ea561a5565aca29eeaacbfe8863dc244838fa3`,
row-level parquet sha256 `92dc8f2a…`, five population checks reproduced exactly), plus the
registered `rt_ncrna_calls_v1` / `rt_records_v1` and the pinned raw corpus.

## Hypotheses tested

| hypothesis | test | result |
|---|---|---|
| wrong / intermediate population | join to Z6 by `physical_locus_key` | all 23 present in Z6 as `NO_NCRNA_CALL_IN_RETAINED_WINDOW` (29 Z6 rows: 6 physical loci map to 2 `locus_key`s — a unit difference, not a status disagreement) |
| canonical call already present at the locus | `rt_ncrna_calls_v1` over every record of the 23 physical loci | **0 calls** |
| coordinate translation | RT start/end/strand/hash vs Z6; start codon at RT-relative 0 | 29/29 rows agree; 23/23 start codons |
| different retained context | Z6 `bp_available_upstream`, `win_len_retained` | 22/23 have ≥ 2.0 kb upstream retained (most 5–12 kb); minimum 563 bp. The hit lies inside the retained window in all 23 |
| different acceptance threshold | pilot E-values vs producer rule (`!` inclusion) | E = 1e-15 … 8e-6 on 65.7 kb searched; even ×100 for genome-scale search space keeps all 23 far inside `!`. Threshold alone does not explain them |
| different CM library version | two local `padlocdb.cm` files (`09449bdf…`, `12dbc1bb…`) | the same 42 model blocks, reordered — search-equivalent. Not the explanation |
| call registered under a different record (duplicate/multi-system representation) | calls on the same contig overlapping the hit, any record, any file label; ncRNA-anchored file | **4 of 23**: the same ncRNA is registered under another `Retron` record on that contig; 0 in the ncRNA-anchored file |
| historical intergenic-only assignment | producer code + canonical outputs + each record's own intergenic regions | see R1 |

## Result — three classes (`tables/RECON_23_intergenic_test.tsv`, `tables/RECON_23_hits.tsv`)

| class | n | what the canonical data show |
|---|---|---|
| **R1** hit overlaps no intergenic region of the record | **12** | the hit (e.g. −134…−2, TypeIX, E 1e-15) lies entirely inside an annotated non-RT ORF (e.g. −164…+3) that abuts the RT start codon; the record's `intergenic_regions` contain nothing overlapping it |
| **R2** call present under a different Retron record on the same contig | **4** | e.g. TypeIIIA3 2,161,069–2,161,326 (E 1.4e-11) is attached to a neighbouring RT system's record. Consistent with the enricher's `fix_ncrna_assignments` (a shared ncRNA is kept only in the closest system) |
| **R3** hit overlaps an intergenic region, no call anywhere | **7** | bit scores 31.4–69.2. Not explained by any locally testable hypothesis |

### What is and is not established about R1

Established against canonical outputs: every one of the 346,722 registered calls carries an
`intergenic_region_id` (0 null), and 1,999/1,999 sampled calls overlap the intergenic region they
name in their own raw record. Every R1 hit overlaps none.

Consistent with, but **not proven for the June production run**: the local producer code
(`RETRONS_january_2026/the-retron-project/pipeline_for_negative_dataset_with_deleting/rt_integration_corrected.py`,
`assign_ncrnas_to_intergenic_regions`) keeps an Infernal hit only if it overlaps a gap between
Prodigal genes. Several copies/versions of this file exist locally; which one produced
`json_files_input_june` is not recorded here. The enricher (`FINAL_REPORT/final_enricher_script*.py`)
only removes duplicate assignments and never adds calls.

**Not claimed:** a global search-space bug, or any population-wide count of affected loci. The earlier
census (`tables/SCALE_upstream_cds_cover.tsv`: RT-proximal upstream ≥ 60 nt CDS-covered in 38–40 % of
high-confidence unmatched loci vs 0.6 % of matched) describes **exposure** to R1-type
representation, not confirmed misses, and it was computed on the superseded physical-locus table.

## What would close R1 and R3 (operator / dbchar session)

1. The exact producer version and its per-genome Infernal `tblout` for the June corpus (likely on
   Ibex). With those, R1 becomes a lookup: was the hit in the tblout and dropped at assignment? R3
   likewise: was it absent from the tblout, or present and dropped by overlap resolution / best-per-region?
2. For R2: Z6 may want a flag for loci whose only nearby call was reassigned to a neighbouring system.
   That is a Z6 design question and is left to the dbchar session.

Withdrawn: `NEXT_SCALE_PLAN.md` "Run 1 — annotation-independent Infernal rescan". The existing detector
result is registered; this task does not rerun the production CMs.
