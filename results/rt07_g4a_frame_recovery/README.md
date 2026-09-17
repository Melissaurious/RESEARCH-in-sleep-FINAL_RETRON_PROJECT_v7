# rt07_g4a_frame_recovery

**Bounded g4a methods study, executed.** Binding record:
`docs/decisions/2026-09-16_stage2_g4a_frame_recovery.md`.

No g4b. No g5. No Stage-1 catalogue access — the sole sequence input is myRT's
`RTs-collection.faa`, and the derivation steps read **no** myRT or Pfam profile of any kind.

## The question

> Starting from complete RT proteins, what conserved ordered sequence structure can be recovered
> within RT families, and what portion is demonstrably homologous across families — **without**
> using the myRT/Pfam seed profiles as the defining ruler?

## The answer

**A shared core exists and is recoverable de novo, but it is a minority of each family's
sequence.** Seven families, predeclared before any alignment:
`Retrons · GII · DGRs · CRISPR · UG3 · UG5 · AbiA`.

| result | value |
|---|---|
| between-family profile correspondence | **42/42** ordered pairs; hhalign probability **74.2–100.0** |
| catalytic dyad correspondence | **42/42** `DYAD_CORRESPONDS`, offset 0 |
| transitive consistency | **210** triples, mean **88.2%**, **83%** at ≥80% |
| globally supported positions | **68–160** per family — **18.9%** (UG5) to **57.3%** (CRISPR) of covered |
| global-or-class | **69.1%** to **99.6%** |
| transfer, as a score | SELF **424.1** vs CROSS **32.6** median bit score (**13.0×**) |
| reproducibility | `./verify.sh` → byte-identical, non-zero on drift |

**Outcome: `g4a PARTIAL`** — class/family frames are supported with a smaller shared global
intersection. A single universal frame is **not** justified by these data.

## Layout

| path | what |
|---|---|
| `control/PREDECLARATION.md` | families, splits, methods and the no-threshold rule, fixed **before** any alignment ran |
| `control/ERRATA.md` | **four errors made and corrected during execution**, two of which produced plausible false negatives |
| `scripts/g4a_pipeline.py` | Phase A — selection, cluster holdout, alignments, de novo profiles |
| `scripts/g4a_correspondence.py` | Phase B — pairwise `hhalign` |
| `scripts/g4a_dyad_check.py` | dyad correspondence, read from the alignment text |
| `scripts/g4a_intersection.py` | Phase C — transitivity and supported intersection |
| `scripts/g4a_transfer.py` | transfer, reported as a score distribution |
| `verify.sh` | **repaired** harness: reproduces into a temp dir, diffs, exits non-zero on drift |
| `tables/` | 12 landed tables |
| `g4a_method_and_failure_modes.md` | method as executed, and nine remaining failure modes |
| `stage1_retron_augmentation_design.md` | design only; no Stage-1 sample drawn |

## Honest limits, stated here rather than buried

- **No family was held out** — all seven contribute a profile, so family-level generalisation is
  untested by design.
- **The detection-rate transfer test cannot fail** at `--max -E 10` and is flagged
  `NON_DISCRIMINATING` in its own table.
- **The intersection depends on the seven families chosen**; a different admissible set was not
  tried.
- **UG5 and GII are the weak corners** — lowest global fractions and the worst transfers.

**NO FULL-CATALOGUE APPLICATION; g5 NOT STARTED.**
