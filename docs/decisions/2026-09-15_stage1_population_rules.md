# DECISION 2026-09-15 — Stage-1 analytical population rules

**Decided by:** operator (Melissa Rios), 2026-09-15, after `dbchar_g1_corpus_identity` landed.
**Scope:** every Stage-1 gate after g1 (`dbchar_g2` … `dbchar_g6`) and every view/dataset Stage 1
registers. **Supersedes:** nothing; makes explicit and tightens the corpus scope rule in
`data/README.md` and the MULTI / ncRNA-anchor conventions in `CLAUDE.md`.
**Evidence:** population counts from `results/dbchar_g1_corpus_identity/tables/s02_populations.tsv`
and `s02_validation_by_population.tsv` (record-manifest sha256 `8e9b7999…41d00`).

These are population rules, not deletions. Every record stays in the canonical representation
with the flags that place it; the rules decide which analyses and denominators it enters.

## Rule 1 — ncRNA-anchor-only records are outside the RT analytical population

The **298,482** `anchor_type == "ncRNA"` records (`POP-NCRNA`, all in
`master_ncRNA-anchored_merged.jsonl`) are **not** part of the RT analytical population. They are
excluded from:

- RT denominators of any kind;
- exact-RT statistics;
- RT-family statistics;
- RT–ncRNA geometry derived from RT-anchored loci.

They are retained, carry an explicit population flag, and may be analysed as their own population
(e.g. annotation-artefact vs undetected-divergent-RT questions) under their own declared
denominator.

## Rule 2 — MULTI RT-anchored records are a separate stratum

The **9,012** RT-anchored records in `master_MULTI_merged_oriented.jsonl` (`POP-RT-MULTI`) remain a
separate stratum.

- The basis of their multiple labels is to be investigated.
- They are **not** silently assigned to a single RT family.
- They are **not** included in single-family RT-family statistics unless a later, auditable
  resolution exists (a landed bundle stating the resolution rule and its per-record outcome).

The same principle applies to any multi-label record found outside the MULTI file: g1 found 20
such records (10 byte-identical pairs, `["<family>","Retron"]`) inside single-family files. They
are flagged as multi-label and must not be counted in two single families at once.

## Rule 3 — RT-anchored records lacking an RT CDS are classified, never dropped

The **31,504** RT-anchored records with no `cds_annotations[]` entry flagged `is_rt_gene`
(check V09a: 29,468 in `POP-RT-FAM`, 2,036 in `POP-RT-MULTI`) require g2 classification into
**recoverable** versus **ill-posed** cases.

- All records and the reason for each classification are preserved.
- A record lacking a defensible RT sequence or coordinate **after reconstruction** may be
  ineligible for analyses that require that quantity.
- Ineligible records remain represented with explicit eligibility/QC flags, and every analysis
  reports the denominator effect of its eligibility rule (n eligible, n ineligible, by reason).

## How to apply

- Views and pulls declare which of these populations they include; "all RT" means `POP-RT-FAM`
  with rule-3 eligibility stated, plus `POP-RT-MULTI` only when explicitly named.
- A gate README reporting an RT rate names the population and states the rule-3 eligibility
  count removed from its denominator.
- Changing any of these rules is an operator decision recorded as a new file here.
