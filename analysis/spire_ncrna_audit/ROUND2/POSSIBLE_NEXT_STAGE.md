# POSSIBLE NEXT STAGE — recorded 2026-09-19, NOT ACTIVE

Operator note, preserved verbatim in intent. It does **not** change the running Round-2 benchmark, and it
must not start before the Round-2 held-out gate has been evaluated. It opens only if that gate returns
`ROUND2_PASS_SMALL_UNRESOLVED_PILOT` and the operator then decides to proceed.

## Objective (if Round 2 validates the procedure)

Test a **Mestre-2020-style discovery strategy** on the project's much larger retron dataset: search
sufficiently deep, high-confidence retron RT homolog groups de novo in their local genomic neighbourhood
(about the available upstream / ±600 nt, or another prospectively justified window), **without relying on the
21 production CMs**. Discover conserved msr–msd-like RNA families and build new **experimental** covariance
models.

## Four outcomes, never merged

1. **Rediscovery** of known ncRNAs (production-CM-matched loci, coordinates hidden during discovery).
2. **Guided expansion** of known ncRNA families to unmatched homologs, reported separately from blind discovery.
3. **De novo discovery** of ncRNA families in groups with no production-CM call.
4. **Construction and held-out validation** of new CMs from those discoveries: new provenance IDs, kept apart
   from the 21 production models, scored on held-out matched and unmatched homologs, distal controls and CDS
   overlap (the Round-1 MIX_05_XIII lesson: propagating among matched members is not rescue of unmatched ones).

## Preconditions

- Round-2 held-out gate evaluated and passed; frozen Round-2 instrument reused unchanged, or any change
  re-validated on held-out data.
- The window justified prospectively (Round 2 compares W500/W700 on DEV only).
- Scale, groups and compute declared and approved by the operator before any run.
