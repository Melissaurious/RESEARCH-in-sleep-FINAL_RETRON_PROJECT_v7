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
- 2026-09-15 · `dbchar_g4_family_baseline` landed: per-family RT/ncRNA baseline on exact-sequence views
  (V-RT-SINGLE 493,956 · V-RT-MULTI 7,593 · V-RT-CROSS 12); 36/44 prior family length baselines CONFIRMED
  exactly. MULTI labels shown to be near-tie HMM assignments (median margin 5.0 bits vs 81.7 in a
  98.1%-validated control); not resolved in Stage 1. 127/127 second counts agree.
- 2026-09-15 · `dbchar_g5_metadata_sampling` landed: catalogue join ~100% on all 8 databases (1 NCBI
  genome unjoined), but a completeness VALUE exists for only 412,261/1,653,827 genome entries (24.93%) —
  NCBI carries no CheckM columns. Taxonomy reported per schema (ncbi has no phylum by construction).
  Top-10 species fall from 66.2% of records to 19.0% of exact RTs (C8 evidence). 16/16 second counts agree.
- 2026-09-15 · `dbchar_g6_tool_calls` landed: tool matrix on 663,308 Retron records (myRT 92.8%, PADLOC
  68.4%, DefenseFinder 67.7%, all three 53.2%); system_subtypes split by the declared case rule with
  0 unclassifiable strings; agreement 43.85% where both tools speak (prior ~44.6% CONFIRMED).
  Extraction asymmetry: ncRNA carriage spans 13.5%-89.2% by tool combination. 11/11 second counts agree.
- 2026-09-15 · `dbchar_g7_stage1_report` landed: the Stage-1 closeout report over the seven landed
  gates. 70 declared values, each resolved from a landed table by an exact row selector (a selector
  matching != 1 row, or an undeclared placeholder, fails the build); every one traced in
  `g7_resolved_values.tsv`. Self-contained `REPORT.html` (8 sections, 5 base64-embedded figures)
  visually inspected at 1200 x 6946. The inspection found two landed figures that were numerically
  correct and unreadable (g3 fig01, g4 fig01); per REPORTING_STANDARDS they were re-plotted in THIS
  gate from their landed TSVs, leaving both landed bundles untouched (BS-6). It also found the
  closing text claiming 11 registered derived datasets where 16 exist - g4's three and g6's one are
  now registered in `data/README.md`, and the count is asserted against the bundle registries at
  build time. Retros written for g2, g2b, g3, g4, g5, g6, g7 (WA-S.2). No Stage-1 measurement has
  been promoted to a project claim; `human_input_audit` is PENDING for all eight bundles.
- 2026-09-15 · `dbchar_g7b_stage1_extended_report` landed: the extended Stage-1 scientific synthesis
  requested beside the g7 closeout report, built ONLY from landed Stage-1 data (14 registered derived
  datasets, 25 landed g2–g6 tables; raw JSONL never opened). 13 sections, 34 figures, 112 landed
  tables, 153 values resolved from landed tables by exact row selector. `c01_reconcile.py` compares
  294 re-derived quantities against the gates that published them and stops the build on any
  disagreement: 294/294 agree, with 2 declared definition differences landed rather than forced.
  An independent intervening-CDS recount from `rt_window_cds_v1` reproduces g3 on 5,000 sampled
  placements at 100%. New statements, none promoted to a claim: the 94.5%-upstream prior has a
  second mode that is one Salmonella protein re-deposited (118,275 placements → 1,908 exact pairs);
  the Retron zero-ncRNA class tracks available upstream window context (0.78% → 60.5%); PADLOC's own
  rules make part of the tool-carriage gradient definitional (retron_XII PROHIBITS an ncRNA), though
  subtype composition does not explain all of it; recurrent exact RTs keep the same ncRNA partner
  (87.8% at ≥100 loci); and GTDB prevalence with a catalogue denominator separates prevalence from
  burden. The older report's "retron_V is structurally distinct (67% downstream)" is re-derived as
  technical: 96.9% of those downstream placements sit in g3's contig-start-clipped mode. Nothing in
  g1–g7 was modified; `human_input_audit` PENDING. ⚠️ `REPORT.html` was NOT seen rendered — the only
  browser here is a snap that cannot run in this environment; all 34 figures were inspected as images.
