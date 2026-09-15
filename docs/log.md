# LOG

Notes that are not gates (WA-G.1).

- 2026-09-15 · `dbchar_g1_corpus_identity` landed (REPRODUCIBLE, input audit PENDING): 43 files,
  81,007,695,609 bytes, 3,358,182 records (RT-FAM 3,050,688 · MULTI 9,012 · ncRNA-anchored 298,482),
  0 parse failures, 450/450 second counts agree. g2 not started.
- 2026-09-15 · `general/` pin moved a0f4ded → cff9831 (upstream `$ROOT` fix); g1 re-validated
  without workaround. Stage-1 population rules recorded in
  `docs/decisions/2026-09-15_stage1_population_rules.md`.
- 2026-09-15 · `dbchar_g2_canonical_units` landed (REPRODUCIBLE): 3,059,700 RT-anchored records →
  2,847,312 loci → 2,475,684 physical loci → 501,561 exact RTs; back-translation verified 99.47%
  (99.54% on the frame-disambiguating stratum); 31,504 no-RT-CDS records classified (14,188
  recoverable); 371,628 twin pairs all evidence-supported; 58/58 second counts agree; prior exact-RT
  key set CONFIRMED identical. Derived datasets registered in data/README.md.
- 2026-09-15 · `dbchar_g2b_rt_cds_recovery` landed: the 31,504 no-RT-CDS records classified —
  14,188 RECOVERED (coordinates verified; Biopython cross-check 1,999/2,000, frame-shift control 0),
  16,688 SEQUENCE_ONLY (all contig-end-clipped; 9,128 wholly beyond the retrieved contig), 628 ILL_POSED.
- 2026-09-15 · `dbchar_g3_pair_geometry` landed: 346,722 placements → 344,154 canonical; 94.5% upstream,
  99.8% same strand, median gap 55 bp, 94.4% with 0 intervening CDS; 30,924 exact pairs (12,079 are 1:1);
  the ~2,682 bp downstream mode is a contig-start-clipping artefact; `position_relative_to_rt` is an index
  minus a coordinate (r=1.000 with -(RT window offset)); 10/10 second counts agree.
