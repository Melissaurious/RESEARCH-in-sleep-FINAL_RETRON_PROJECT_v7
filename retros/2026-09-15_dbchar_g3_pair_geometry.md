# Retro — dbchar_g3_pair_geometry (2026-09-15)

Bundle: `results/dbchar_g3_pair_geometry/` — REPRODUCIBLE, human_input_audit PENDING.
46 tables, 3 figures, rerun 101.3 s.

## What happened

- The priority Stage-1 output: 346,722 RT↔ncRNA placements reduced to 344,154 canonical ones,
  with a reusable placement-level table rather than only summaries. Priors: 94.5% upstream,
  99.8% same strand, median gap 55 bp, 94.41% with zero intervening CDS, and the 0/1/2/3/>3
  intervening-CDS counts landed explicitly rather than as a mean.
- Two shipped signals were shown to be **technical, not biological**, which is the gate's most
  useful result:
  - the ~2,682 bp downstream cluster contains only 18 distinct ncRNA sequences and 99.96% of its
    dominant stratum is contig-start-clipped — the window begins at the contig start, so any call
    is forced downstream;
  - `position_relative_to_rt` matches no coordinate frame. Twelve candidate frames were tested;
    the best reproduces 146 of 14,810 values. Its variation is **−(RT offset into the window) plus
    the ncRNA's intergenic-region index** (r = 1.000) — an index minus a coordinate. The
    coordinate-derived geometry is canonical; the shipped field is retained as provenance.
- The retron-CM-beside-non-Retron-RT population (260 placements) is preserved and characterised
  separately, explicitly **not** called novel retrons, per the operator's instruction.

## What went wrong

- **Multiplicity conflated two different things**: a detector emitting the same call twice inside
  one record, and the same locus being re-mined from another record. The first measure read 23,659
  where the real cross-record number is **190**. Split into
  `duplicate_call_within_one_record` / `same_call_from_another_record_of_the_same_locus`.
  A "duplicate" is meaningless until the unit it duplicates within is named.
- **`same_strand` was an object-dtype column** and broke the parquet write. Nullable `boolean`.
- **Sandbox placeholder char-devices were swept into `OUTPUTS.tsv`** and `clone_safe.sh` refused
  the bundle. Resealed outside the sandbox and added `results/**/.claude/` and
  `results/**/.mcp.json` to `.gitignore`.

## Proposal (not an amendment — WA-S.2)

**`bundle_valid.sh --write-outputs` should refuse to seal a non-regular file.** A char device, a
socket or a fifo in a bundle is never a legitimate output, and sealing one produces an
`OUTPUTS.tsv` that `clone_safe.sh` then rejects — one check creating work for another.
- *Would have caught:* this gate's seal, which recorded two sandbox placeholder devices and had to
  be redone outside the sandbox.
- *Would wrongly reject:* a bundle that deliberately ships a named pipe as a fixture, which no
  bundle in this project does and which could declare itself by shipping the fixture as a regular
  file plus a script that creates the pipe.

## Carried into later gates

The canonical placement table and the exact-pair view are the substrate for the g7 report's
section 4; the contig-clipping finding is why g4's geometry stratification excludes clipped
windows by flag rather than by filter.
