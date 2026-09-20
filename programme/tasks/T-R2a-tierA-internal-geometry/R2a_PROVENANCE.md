---
record: R2a_NCRNA_OBJECT_PROVENANCE
task_id: T-R2a-tierA-internal-geometry
date: 2026-09-20
kind: blocking provenance determination, recorded before freeze
verdict: RECONCILED — R2a may execute; interpretation is bound
---

# R2a · provenance of the ncRNA objects

## 1 · The question actually asked

The R2 adversarial pre-check raised a circularity risk: if the panel's ncRNA boundaries had been
drawn from the observed RT-DNA extent, then "the RT-DNA occupies ~58 % of its ncRNA" would be true
by construction and would carry no architectural information.

That **scientific** question is settled upstream and is not reopened here. The experimental census
study annotated the cognate ncRNAs bioinformatically **before** the natural RT-DNA sequences were
determined; RT-DNA was measured afterwards and aligned back onto those ncRNAs. RT-DNA did not define
these boundaries, so the feared circularity is not inherent to the source study.

What remained was the narrower **implementation** question, and it is the only thing this record
determines:

> Is the `ncRNA_sequence` R2a consumes the same sequence object carried in the experimental panel
> (`support.csv`) that `T-R1b` used, or has this project transformed or reconstructed it?

## 2 · What was checked, and what it showed

Instrument: `r2a_provenance_gate.py` (11 blocking checks, all 81 elements). Run 2026-09-20 against
the pinned panel and the accepted R1b table. **Result: 11/11 PASS, 81/81 elements, no mismatches.**

| finding | evidence |
|---|---|
| the panel is the registered, unmodified object | sha256 `80b2f565…9577`, matching the value pinned in `CANONICAL_DATASETS.tsv` (`PANEL-175`), in the R1b freeze, and in the R2a launcher §4 |
| the panel has not drifted anywhere on this workstation | six independent copies across five project trees are **byte-identical** at that sha256 |
| **no transformation occurred — not even case** | the only permitted normalisation, `strip()` + `upper()`, is a **no-op on all 81 rows**. The ingested sequences are byte-identical to the panel's |
| no reconstruction artefacts | alphabet is `ACGT` only across all 81; no ambiguity codes, no gaps |
| the object is internally consistent | the panel's own `ncRNA_length` column equals `len(ncRNA_sequence)` for all 81 — not truncated, not extended |
| **it is the same object R1b measured against** | R1b's landed `ncrna_len` equals `len(panel ncRNA_sequence)` for all 81 |
| **the R1b coordinates resolve on this object** | `revcomp(panel ncRNA[start:end]) == panel RTDNA` for all 81; all 81 `EXACT_UNIQUE` |

`R1b_anchor_coordinates.tsv` carries **coordinates and lengths only — no sequences**, so R2a
necessarily re-reads `ncRNA_sequence` from the pinned panel rather than from a derived intermediate.

## 3 · Determination

**RECONCILED.** R2a consumes exactly the `support.csv` ncRNA sequence objects already used by R1b.
No later boundary reconstruction or transformation occurred. This is **not** `REVIEW_REQUIRED`: that
verdict was reserved for the case where the sequences had been modified or rebuilt after ingestion,
and they were not.

The ncRNA boundaries are therefore **inherited from the source study's pre-RT-DNA bioinformatic ncRNA
annotation**.

## 4 · The interpretation this binds — mandatory

⛔ **Every RT-DNA/ncRNA fraction and every normalised coordinate R2a reports is a *fraction of the
published annotated ncRNA sequence*.**

It is **not** a fraction of an experimentally verified full-length transcript. The denominator is a
bioinformatic annotation, and no transcript end in this panel was measured. Any statement of a
fraction or normalised position must carry that reading.

Consequently: the observed tightness of the RT-DNA fraction, and its variation across subtypes, may
stand as **descriptive or hypothesis-generating** only. Random re-pairing statistics do not
demonstrate mechanism, and do not establish an ancestry-independent constraint.

## 5 · Recorded limitation — not resolved

The repository holds **no separate direct source-study supplementary file** from which `support.csv`
was built, so the panel could not be diffed against an upstream publication artefact. `support.csv`
lives outside this repository and is registered only as an ingested object pinned by sha256.

The registered `references/rt0_rt7/mestre_2020/` material is a **different source lineage** — a
classification/taxonomy reference carrying no sequence columns — and is **not** the origin of these
81 ncRNA sequences. Its contents are irrelevant to this determination and were not treated as
evidence either way.

This is a **source-file provenance limitation, recorded and carried**, not a defect in R2a and not a
reason to withhold execution. Closing it would require registering the experimental census study's
own supplementary distribution as a first-class resource under
`references/rt0_rt7/RESOURCE_REGISTER.tsv`.

## 6 · Scope

This record changes no R2a constraint, endpoint, population, threshold or control. The previously
approved R2a design stands unchanged; §4b adds a blocking gate and §10 binds the interpretation.
`PANEL-RTDNA-81` remains spent by R1b, with no new confirmatory spend.
