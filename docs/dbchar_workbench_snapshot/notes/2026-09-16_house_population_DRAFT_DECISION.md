# DRAFT DECISION 2026-09-16 — the house RT analytical population (`POP_RT`)

**Status: DRAFT, not landed.** Written in the workbench because the operator stated the rule in
session. It is formatted to be promoted to `docs/decisions/` unchanged if she accepts it. Until
then it binds only `ARIS_OUTPUT/dbchar_workbench/`.

**Decided by:** operator (Melissa Rios), 2026-09-16, in the dbchar workbench session.
**Scope:** default RT-level denominator for workbench analyses.
**Supersedes:** nothing. It *composes with* `docs/decisions/2026-09-15_stage1_population_rules.md`
and does not restate or weaken it.

## The rule

```sql
POP_RT :=  is_first_copy
       AND file_label <> 'MULTI'
       AND NOT multilabel
       AND elig_geometry
```

Applied to `rt_records_v1`, which already excludes the 298,482 ncRNA-anchor-only records
(Rule 1 of the 2026-09-15 decision).

## What it costs, exactly

| step | population | n | removed here |
|---|---|---|---|
| 1 | all raw records | 3,059,700 | — |
| 2 | `+ is_first_copy` | 3,051,238 | 8,462 |
| 3 | `+ drop the MULTI file` | 3,042,226 | 9,012 |
| 4 | `+ drop multilabel records` | 3,042,216 | 10 |
| 5 | `+ elig_geometry` = **`POP_RT`** | **3,026,000** | 16,216 |

**Total cost: 33,700 records, 1.10 % of the raw corpus.**

Units yielded: 3,026,000 records · 2,822,547 loci · 2,451,078 physical loci · **477,956 exact RT
proteins** · 1,535,827 genomes.

## Why `elig_geometry` is the right predicate for "ill-posed + off-contig"

The operator asked to exclude MULTI and "ill-posed RT systems that had off contig issues". The g2b
recovery states map onto `elig_geometry` **one-to-one** — verified in the notebook by assertion,
not assumed:

| recovery state | n | `elig_geometry` | what it is |
|---|---|---|---|
| `RECOVERED` | 14,188 | **True** | RT CDS reconstructed and verified; full genomic context |
| `SEQUENCE_ONLY` | 16,688 | False | 9,128 RT wholly outside the retrieved contig · 3,924 inverted window · 3,636 RT crossing a contig end |
| `ILL_POSED` | 628 | False | ill-posed |

So `elig_geometry` drops every ill-posed and every off-contig/inverted record and keeps the 14,188
successfully recovered ones. No new predicate is defined; the flag already exists in the canonical
tables.

## What `POP_RT` deliberately does NOT exclude

**Contig clipping is a stratification flag, not an exclusion.** 1,249,012 distinct records carry
`true_start_clipped` and 1,270,225 carry `clipped_end_flag` — roughly 41 % of the corpus each.
Those windows hold a *verified* RT with defensible coordinates; only the window's extent is
truncated. Excluding them would discard 41 % of the corpus to fix a problem that affects one
measurement (the forced-downstream distance mode), and that measurement is correctly handled by
stratifying — as notebook section D2 does. Partial ORFs (B3) and atypical geometry (I) likewise
stay in and are reported.

**If the operator does want clipped windows excluded**, that is a *different* and much more
expensive rule and should be its own decision record, with the 41 % denominator cost stated.

## Interaction with the canonical Stage-1 numbers

Sections A1–A3 of the notebook reproduce the landed g2 unit ladder and therefore run on the
**unfiltered** population; their numbers are the canonical Stage-1 ones and do not equal the
`POP_RT` numbers. This is intended: the two answer different questions ("what did the corpus
contain" vs "what will we measure on"). Every cell states which it used.

`POP_RT` is a *workbench reporting default*. It does not re-open, re-derive or contradict any
landed g1–g7 measurement.

## Open

Whether to promote this file to `docs/decisions/2026-09-16_house_analytical_population.md`. That
is an operator action; this workbench does not write to `docs/`.
