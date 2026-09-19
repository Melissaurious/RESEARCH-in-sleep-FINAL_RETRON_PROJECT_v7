# Stage 3A — failure modes encountered, recorded rather than repaired silently

## F1 · `mkdssp` 4.5.5 is unusable in this environment — INSTRUMENT SUBSTITUTED AND VALIDATED
Fails on valid mmCIF (`Is a directory` on a plain file) and on gemmi-written PDB (`does not seem to
be an mmCIF file`), with `LIBCIFPP_DATA_DIR` set and inputs local. Replaced by a direct Kabsch–Sander
implementation, validated against the 26 historical mkdssp outputs: median 3-state agreement 0.945,
helix recall 1.000, strand recall 0.701. The β conservatism is a stated limitation of every
downstream β-dependent criterion.

## F2 · Two join defects in my own validation, found and fixed
Both would have falsely condemned the instrument. (a) Historical `.dssp` files and backbone extracts
use different residue numbering — fixed by positional alignment. (b) The historical `.dssp` files
were computed on the **full deposition**, so residues from other chains collided on residue number —
fixed by honouring the chain column. Before the fixes, 11 of 26 chains scored 0.31–0.60; after, 25
of 26 score ≥ 0.92.

## F3 · The prospective structural-diversity split produced no held-out set
All 31 biological groups fall into **one** structural cluster at the declared TM ≥ 0.50 single-linkage
threshold. Group–group max TM: median 0.698, 93 % of the 465 pairs ≥ 0.50, 49 % ≥ 0.70. These
proteins are one fold. The pre-authorised fallback was taken: **leave-one-biological-group-out**,
31 folds, recorded in `CALIBRATION_SPLIT.tsv`. The threshold was **not** lowered to manufacture a
split.

## F4 · The contiguous-segmentation objective is degenerate — RUN VOID
Normalised cut increases monotonically with k and is 0 at k = 1, so it cannot select a number of
domains. Reported, not patched after seeing the output. See `DOMAIN_CRITERIA.md` C3.

## F5 · Structures that resist any simple three-domain representation
Independent of the criterion used, these carry large accessory content that the classical model has
no slot for: `9YFD_A` (DRT1 filament, 1,125 modelled residues), `9Z6Z_H`/`9Z6Y_H` (Drt3b, 626–628),
`24NC_A` (DRT4 hexamer, 520), `7KFT_C` (Cas6-RT-Cas1, 568), `9I2F_A`/`9I2G_B` (Ec67 RT–TOPRIM fusion,
578–580), `26CZ_A` (SUMO fusion, 640), `9WY8_A` (MBP fusion), `9HDO_A` (SUMO+MBP+ORF2p triple fusion).
1,300 residues are unmodelled inside chains across the population, in 37 of 62 chains.

## F6 · Not reached in this session
C4–C7, `REPLICATE_STABILITY.tsv`, `EXTERNAL_LITERATURE_COMPARISON.tsv`, `TRANSFER_READINESS.md`
beyond the audit already carried forward, and all figures. They depend on a working contiguous-domain
criterion, which F4 removed.
