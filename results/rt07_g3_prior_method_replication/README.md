# rt07_g3_prior_method_replication

STATUS: VERIFIED — `run.sh` was rerun from this assembled bundle and reproduced every landed table, both reports and `MANIFEST.tsv` byte-for-byte.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **FULL** (launcher §7). Settles `C3` supporting, `C7` supporting. No claim is promoted.

**Headline: the prior landmarks are real positions in conserved regions. The prior *seven-way partition*, the "external" validation, and the RT0 number are not what they were named.**

---

## 1 · What was measured

13 prior claims, audited on the five dimensions the launcher requires — object identity, frame identity, seed dependence, conditioning, reproducibility — plus positional correspondence against the g2 regions.

| verdict | n | claims |
|---|---|---|
| `REPRODUCED_SAME_OBJECT_SAME_FRAME` | 2 | D2 (RT1 instability), RT0_FRAME_GAP |
| `PARTIALLY_REPRODUCED` | 1 | D1 (landmark positions reproduce; the 99.91% is misnamed) |
| `CIRCULAR_OR_SEED_DEPENDENT` | 3 | A72_EXTERNAL, GOLD175, PRODUCERS |
| `OBJECT_MISMATCH` | 2 | C72 ("72/72"), RT0_VOID |
| `FRAME_MISMATCH` | 1 | SEVEN_BLOCKS |
| `WITHDRAWN_BY_PRIOR_WORK` | 2 | D6, DOMAIN_PHYLO |
| `NOT_TESTABLE` | 2 | D4 (comparator, → g7), VOID_FILE |

**No prior number became an acceptance criterion**, including the ones that reproduced exactly.

## 2 · Independence, re-measured from the files

By exact sequence identity (sha256 over residues — identifiers were reassigned between project versions and cannot be joined on):

| set | in the model seed | prior audit reported | g3 |
|---|---|---|---|
| `anchors72` | **72/72 = 100.00%** | 72/72, 100% | reproduced exactly |
| `gold175_uniq` | **44/171 = 25.73%** | 44/171, 25.731% | reproduced exactly |
| `retron` | 49/78,287 = 0.06% | 0.0626% | reproduced exactly |
| `nonretron` | 97/423,274 = 0.02% | 0.0229% | reproduced exactly |

New in g3:
- **46 of 72 anchors (63.89%) are also members of the retron population they score** — the anchors are not outside the corpus they validate.
- **26 of 72 carry a PDB id**; the other 46 are sequence-propagated.
- **7 anchors carry a His6 expression tag and 1 carries a SUMO tag.** A purification tag is vector-derived sequence, so residue numbering taken from those constructs is offset unless the tag was stripped — and the prior work does not record whether it was (`U11`, new).
- The gold panel's seed overlap is **entirely** its overlap with `anchors72` (the same 44 sequences).
- **127 gold-panel members are genuinely outside the seed** — the only held-out population g4 can build from prior assets.

## 3 · Frames: four coordinate systems over one landmark set

The primary frame ships as `RT17_CORE.hmm` but declares `NAME B_span17`, 305 match states, and is **byte-identical to `B_span17.hmm`**. Every number quoted "on RT17_CORE" is a number on B_span17.

Carried onto shared LtrA residues via `hmmalign` against the g2 reference set:

| prior landmark | match state | LtrA residue | falls in |
|---|---|---|---|
| RT1 | 42 | 49 | g2 block 1 — **which is in Blocker's RT0 zone** |
| RT2 | 87 | 102 | g2 block 2 |
| RT3 | 146 | 160 | g2 block 3 |
| RT4 | 193 | 213 | g2 block 4 |
| RT5 | 229 | 308 | g2 block 5 — the catalytic region |
| RT6 | 263 | 344 | g2 block 5 — **the same region** |
| RT7 | 276 | 357 | g2 block 6 |

**27 of 28 landmark placements across four frames fall inside an independently reconstructed g2 region, and 6 of 7 landmarks sit at the identical LtrA residue in every frame.**

> `PROPOSED:` the four frames are not four independent determinations. They are four coordinate systems over one anchor-derived landmark set, so agreement between them prices transfer consistency, not replication. The prior claim that the states "replicate in four independently built frames" is true as transfer and misleading as replication.

## 4 · The seven-way partition does not survive reconciliation

- Only **4 of 28** mappable prior frame blocks are fixed by a published motif; the other 24 are `order_interpolated`.
- The seven prior labels collapse onto **six** g2 regions: **RT5 (LtrA 308) and RT6 (LtrA 344) both fall inside g2 block 5**.

**No old seven-block result is defensible as a seven-way partition after frame reconciliation.** What survives is the landmarks and their order.

## 5 · RT0 was never measured on the RT0 region

Verdict: **`OBJECT_MISMATCH`**.

- The prior frame spans **LtrA 53–361** and every block in its "RT0-proximal" region is `order_interpolated`.
- It does **not** cover the conserved RT0 alanine at **LtrA 39** — it begins **14 residues downstream of it**.
- The independently reconstructed **g2 region 1 (LtrA 39–61) does cover it.**

The prior occupancy contrast is real and carried a declared positive control that passed (group II introns 0.8999 vs retrons 0.105, same columns). But it measures interpolated N-terminal blocks that exclude the only specific RT0 landmark available, so **it is not an RT0 number**. `U01` stays open; the g2 scope limit stands.

## 6 · RT1 — measured, not interpreted

RT1 is the **only** landmark that moves between prior frames, and its prior concordance is 0.75 against a bar of 0.90 declared in the prior code. In shared coordinates it falls at LtrA 49 — inside the region Blocker assigns to RT0.

> **The interpretation is not settled here.** Whether this is a limitation of the method or an independent recovery of a weakness the founding authors flagged remains an operator decision (launcher §9b). g3 adds one measured fact to that decision and stops.

## 7 · Counts, including the ugly ones (BS-5)

    n_attempted:  13 prior claims; 6 prior sets; 5 prior frames; 29 prior frame blocks;
                  28 landmark placements; 8 set-overlap pairs
    n_succeeded:  13 verdicts landed; 4/4 controls pass; 21 inputs hashed;
                  27/28 landmark placements mapped into g2 regions
    n_dropped:    0 — nothing discarded. 2 claims are NOT_TESTABLE and 1 prior block could
                  not be mapped (no usable LtrA coordinate); all are landed as their states.

Ugly counts kept in view: **3 of 13 claims are circular or seed-dependent**; **24 of 28 prior blocks were interpolated, not anchored**; **1 prior frame block has no usable coordinate**; and the file the project's own contract says to consult before quoting any prior figure — `VOID_DO_NOT_CITE.md` — **does not exist on disk**.

## 8 · Controls

| control | kind | result |
|---|---|---|
| C1 the frame carrier places prior RT5 on the catalytic region g2 found independently | POSITIVE | **PASS** |
| C2 seed overlaps reproduce the prior audit's published values from the files | POSITIVE | **PASS** |
| C3 the identity measure collapses to 0 on shuffled residues | NULL | **PASS** |
| C4 frames the prior work named separately are one file by hash | POSITIVE | **PASS** |

**Seeded-bad guard:** `run.sh` first switches identity matching from residues to identifiers — the exact defect the prior audit avoided — and aborts if the controls still pass. They fail, as required.

## 9 · Self-adversarial pass (BS-14)

1. **Is judging prior work against g2 circular?** No — g2 established regions and explicitly did *not* establish a partition. Claims are judged on what they measured, on what frame, and on how much of their validation was their own seed.
2. **Could the LtrA carrier manufacture agreement?** It could have placed prior landmarks anywhere; C1 shows it lands RT5 on the catalytic region located independently, and one landmark (RT1) does move between frames.
3. **Are the contamination figures just the prior audit's?** They are recomputed from the FASTA files; agreement with the prior report is the control, not the source.
4. **Is "46 sequence-propagated" inherited?** No. The prior arm never computed it. g3 measures 26 PDB + 42 RETRON + 4 UNIPROT directly.
5. **Did a comparator leak in?** No Toro, Mestre, myRT or SPIRE asset was read. The prior project's Toro-derived HMMs were registered, not used.
6. **Was any prior number promoted?** No. Every figure here was re-measured, and the verdict table records that explicitly per row.

## 10 · What g3 changes for g4

Landed in `tables/g3_handoff_to_g4.tsv`:

1. **Held-out design**: only the **127** non-seed gold-panel members are available; that n must be stated. `anchors72` is unusable as validation (100% seed).
2. **No seven-way partition to inherit**: g4's per-block model must be built on regions with interval uncertainty, and any block count needs its own null.
3. **Name frames by content**: record each frame's sha256, or the RT17_CORE/B_span17 confusion recurs.
4. **No RT0 occupancy** may be reported.
5. **RT1 is a declared uncertainty**, carried without interpretation.
6. **Tagged anchors**: any residue coordinate from the 7 tagged constructs needs its tag offset resolved first (`U11`).

## 11 · Reproduction log (BS-3, WA-B.2)

    $ bash results/rt07_g3_prior_method_replication/run.sh
    == 1. independence and contamination, re-measured by exact sequence identity
       anchors72 in seed_all167  72/72 = 100.00%  SEED_CONTAMINATED
    == 2. frame correspondence: prior frames carried onto shared LtrA residues
       frames aligned: 5/5; prior regions mapped: 28; inside a g2 region: 27
       landmarks placing at the SAME LtrA residue in every frame: 6/7
    == 3. the prior RT0-RT7 frame table, and the RT0 object audit
       26 of 28 blocks inside a g2 region; 4/28 fixed by a published motif
       Blocker RT0 alanine 39 covered by prior frame: NO; by g2 region(s): [1]
    == 4-6. verdicts, seeded-bad guard, controls (4/4 PASS)
    == 7-9. report, manifest, byte comparison
    REPRODUCED: every landed table, report and manifest is byte-identical on rerun.

`REPORT.html` is self-contained and placeholder-free; the visual inspection required by launcher §9d is the operator's.

## 12 · Acceptance

- Prior trees were read **read-only**; nothing outside this bundle was written.
- Every prior figure quoted was re-measured; none is an acceptance criterion.
- The RT1 interpretation and `U01` remain open and are recorded as such.
