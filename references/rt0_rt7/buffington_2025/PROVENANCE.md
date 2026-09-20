# BUFFINGTON2025_RETRON_CATALOGUE — provenance and identity record

**Acquired 2026-09-20.** Bounded asset ingestion only. **Not merged into any project
population**, not parsed into any analysis, and not used to infer anything.

---

## 1 · Identity

| field | value |
|---|---|
| **original filename** | `Discovery_and_engineering_of_retrons_supp.csv` |
| **untouched source path** | `/home/borg/Discovery_and_engineering_of_retrons_supp.csv` — left in place, unmodified |
| **project path** | `references/rt0_rt7/buffington_2025/Discovery_and_engineering_of_retrons_supp.csv` |
| **source paper** | Buffington J *et al.* **Discovery and engineering of retrons for precise genome editing.** *Nature Biotechnology* (2025) |
| **DOI** | `10.1038/s41587-025-02879-3` |
| **supplementary-table identity** | **Supplementary Table 1** |
| **sha256** | `d68366970378c05b5af9b00be886d76224a196a29b77171303f9353457cf4e62` |
| **bytes** | 87,392 |
| **rows** | **105** data rows (+1 header) |
| **columns** | 8 |
| **acquisition date** | 2026-09-20 |
| **copy verified** | ✅ byte-identical to the untouched source — `sha256sum` on both returns the same digest |
| **register entry** | `references/rt0_rt7/RESOURCE_REGISTER.tsv`, `asset_id = buffington2025_supp_T1_retron_catalogue` |

Stored under the **existing** `references/rt0_rt7/<source>_<year>/` hierarchy used for
`mestre_2020/`, `toro_2026/`, `myrt/` and `historical/`. No new hierarchy was created.

## 2 · Column schema, as published

| # | column | populated | note |
|---|---|---|---|
| 1 | `Accession Number` | 105/105 | ⚠️ **NOT unique** — 97 distinct; 7 accessions repeat, one appears 3× |
| 2 | `Organism` | 105/105 | free-text species/strain |
| 3 | `I.D.` | 105/105 | ✅ **the only 1:1 key** — `NRT-1` … `NRT-105`, 105 distinct |
| 4 | `Retron I.D.` | 105/105 | ⚠️ 104 distinct — `Retron-Kra1` appears twice |
| 5 | `Reverse Transcriptase (RT) sequence` | 105/105 | amino acid |
| 6 | `Name (RT)` | 105/105 | 104 distinct |
| 7 | `Putative native msr-msd` | 105/105 | nucleotide, lowercase `acgt` |
| 8 | `msr-msd with a 81nt RFP repair template (tcgggg…aggggg)` | 105/105 | **engineered construct**, not native |

**Join key for any downstream work is `I.D.`** — it is the only column that is unique.

## 3 · Measured properties of the sequences

Computed on ingestion so a downstream task does not have to rediscover them.

| property | value |
|---|---|
| RT length (stop character stripped) | min 104 · median 319 · max 617 |
| ⚠️ **RT sequences ending in `*`** | **104 of 105** |
| non-standard residues after stripping `*` | none |
| unique RT sequences (stop-stripped) | **101** of 105 — 4 recur |
| unique `Putative native msr-msd` | **89** of 105 — 16 recur |
| unique RT + msr-msd combinations | **103** of 105 |
| msr-msd length | min 112 · median 169 · max 363 |
| RT ≥ 250 aa (the frozen Stage-1 eligibility rule) | **91 of 105** — so **14 would be ineligible** |

⛔ **The trailing `*` is an exact-hash trap, and this project has already been caught by it.**
`docs/decisions/2026-09-16_stage2_scope_separation_errata.md` records a count that read as 10
instead of 4 *"requires stripping a trailing `*`, never disclosed."* Any exact-sequence-hash
comparison against `RT-EXACT-501561` **must state whether the stop character was stripped, and
report both counts.**

## 4 · ⛔ Scientific limitations — binding on every downstream use

1. **The table contains published bioinformatically identified / high-confidence retron systems.**
   That is a *computational* identification.
2. ⛔ **Presence in this table is NOT equivalent to experimental validation.** The table carries
   **no screening column and no activity column** — verified on ingestion, all 8 columns are listed
   above.
3. **Experimental screening / activity status must be joined separately**, from experimentally
   reported source data, and never inferred from membership here.
4. The `msr-msd` in column 7 is **putative and native**; column 8 is an **engineered RFP
   repair-template construct** and is not a natural sequence. They must never be pooled.
5. ⛔ **No cross-pair assay outcome may be inferred from this catalogue alone.** It reports systems,
   not combinations, and Stage 12 remains closed.

## 5 · Relationship to existing project work

This is the **`BUF2025` source** that `T-A23c` could not obtain. `A23c_uncertainties.tsv` records
`U1_7x7_every_cell_assayed` and `U2_six_nonfunctional_rows` as `NO_FULLTEXT` / *"NOT RESOLVABLE from
what could be retrieved"*, and those two questions carry **42 of the 56** rows in the `T-A23`
cross-pair curation.

⚠️ **This supplementary table is not the article.** It may or may not resolve `U1`/`U2`, which are
questions about a **7×7 heatmap caption** and about whether six non-functional rows are six measured
cross-pairs or one statement expanded six times. Supplementary Table 1 is a **systems catalogue**.
Whether it speaks to those two questions is for `T-A23d` to establish, not to assume.

## 6 · Status

- Registered, hashed, schema recorded. **Nothing computed from it.**
- ⛔ **NOT merged** into `RT-EXACT-501561`, `PAIR-ELIG-30924`, `RETRON-EXACT-78287` or `PANEL-175`.
- Reconciliation is a **proposed, unapproved** task: `T-X1-buffington-reconciliation`.
- Added as an **input candidate** to `T-A23d-primary-reference-resolution`.
- `programme/CANONICAL_DATASETS.tsv` → `BUFFINGTON2025_RETRON_CATALOGUE`,
  status **`CANONICAL_WITH_LIMITATION`**.

## 7 · ⚠️ One thing for the operator, before any push

The Mestre 2020 and Toro 2014 supplementary tables are **tracked in git**, so this file follows that
precedent. **The GitHub remote is public (verified).** `.gitignore` already excludes publisher PDFs
on redistribution grounds — *"the bytes are copyright-reserved and this repository has a remote"* —
and a 2025 supplementary table is a closer call than a 2014 one. **Committed here to match the
established convention; flagged so you can exclude it before pushing if you prefer.** See
`programme/GITHUB_READINESS.md`.
