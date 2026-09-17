# rt07_pre_g4_scope_separation

**Scientific redesign and evidence inventory. No detector was built and no compute was spent on
the Stage-1 catalogue.**

Operator-directed reframing after two failed pre-g4 design reviews (3/10, then 4/10). The binding
record is `docs/decisions/2026-09-16_stage2_scope_separation.md`.

This is not a gate bundle: it has no `run.sh` and reproduces no gate number. Every measurement in
it is either a re-tabulation of a landed value, cited by source table, or a direct measurement of
a read-only external reference package, cited by path. Naming follows the precedent of
`results/rt07_pre_g4_seed_provenance/`.

## The finding, in one paragraph

Stage 2 asked one gate to be two instruments. `ALIGN_000044` — the g2 substrate — is **66 records
/ 65 unique sequences of a single RT class**: every one is a group II intron-encoded ORF, and the
four "lineage groups" are host compartments, not RT classes. That is the correct and only
substrate for reconstructing what RT0–RT7 historically meant, and it is the wrong substrate for a
general RT instrument, because a single-class panel cannot hold out a class and so class transfer
was untestable in principle. Broad material does exist locally — the myRT distribution carries
**1,988 family seeds across 45 families** and **2,339 full-length proteins across 38 labels** —
but its seeds are **Pfam `RVT_1` excisions** (`buildRVT.sh`: `cut -c $start-$stop`), so the
measured window on LtrA is **90–360** while Blocker's RT0 zone is **1–85**: no myRT-derived
substrate can address RT0, ever. myRT is valid derivation material (under 1% containment in the
old project seed) and invalid family-label validation (Stage-1's labels are its own output).

## Files

| file | what it is |
|---|---|
| `historical_vs_operational_scope.md` | the core document: what the g2 substrate is, what it legitimately answers, why it cannot carry a general instrument, and what a general reference set would have to be |
| `proposed_stage2_gate_restructure.md` | assessment of the 2A/2B/2C/2D decomposition — correct, with one modification and one addition — and the minimum launcher change |
| `tables/myrt_reference_inventory.tsv` | 47 rows: per-family models, `NSEQ`, FASTA records, uniqueness, length distribution, and the `NSEQ`-to-FASTA reconciliation |
| `tables/reference_source_inventory.tsv` | every candidate reference collection with `N`, sequence kind, RT classes, selection rule, and its **allowed derivation vs validation role** |
| `tables/reference_overlap_genealogy.tsv` | measured overlaps between every pair of reference sets, by exact sequence **and by containment** — the honest measure when one set holds fragments |
| `tables/candidate_reference_design.tsv` | the layered panel proposal L0–L4 with three binding rules; `N` deliberately left as rules rather than fixed numbers |
| `tables/estimand_matrix.tsv` | 14 quantities classified `ESTABLISHABLE` / `PARTIALLY_ESTABLISHABLE` / `UNESTABLISHED`, including the five-condition chain that must hold before the word *absent* is permitted |
| `tables/general_vs_retron_analysis_plan.tsv` | View A broad-RT architecture and View B retron-focal, on one shared coordinate frame, with the falsification condition that would justify a retron extension |
| `tables/structure_reference_inventory.tsv` | 39 distinct RT-bearing PDB entries by class, with tags, prior DSSP boundaries, and what each may be used for |
| `proposed/LAUNCHER_02_diff.md` | **not applied** — four proposed launcher edits |

## Status

**NO g4 DETECTOR EXECUTED; NO g5 CATALOGUE APPLICATION STARTED.**
