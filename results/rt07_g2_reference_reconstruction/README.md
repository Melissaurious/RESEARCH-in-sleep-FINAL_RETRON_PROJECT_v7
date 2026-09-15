# rt07_g2_reference_reconstruction

STATUS: VERIFIED — `run.sh` was rerun from this assembled bundle and reproduced every landed table, both sequence products, both reports and `MANIFEST.tsv` byte-for-byte.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **FULL** (launcher §7). Settles `C3` supporting. No claim is promoted here.

**Headline: the historical landmarks reconstruct on their own substrate. The seven-way partition does not.**

---

## 1 · What was measured

**One measurement:** the recovery rate of the historical landmarks on the sequences and
reference alignment from which they were derived, before any Toro, Mestre or myRT convention
is consulted.

Substrate: `ALIGN_000044` itself — the alignment Zimmerly 2001 states it adjusted its
inherited subdomain labels against — acquired and hash-verified in `g1`. 66 proteins, 1,441
columns, four lineage groups (mitochondrial 29, bacterial 20, algal/chloroplast 11, euglenoid
6) assigned by declared keyword rules over the record's own description lines; 0 unassigned.

Procedure: the **Xiong & Eickbush criterion verbatim**, as recovered in `g1` — a position is
conserved when, in ≥3 of 4 groups, >50% of that group's sequences carry the group's modal
residue. Both free parameters (merge gap, minimum block size) were swept over their whole
declared range, and the reporting point was fixed **before any block was counted**: the
midpoint of the widest plateau in block count. Not "the parameters that give seven".

### What reconstructed

| landmark | published | observed | verdict |
|---|---|---|---|
| catalytic Y/FxDD in subdomain 5 | Zimmerly 2001 | block **5 of 6**, column 783, LtrA residue 306 | `RECOVERED` |
| the 4/5 spacer is the variable insertion site, 1–179 aa | Zimmerly 2001 | widest inter-block gap is **4/5**, 190 columns, **5–185 residues** across sequences | `RECOVERED` |
| within-group conservation, subdomains 0–7 | 90 (mito) / 94 (bacterial) | 116 / **100** columns | `PARTIALLY_RECOVERED` |
| total conserved extent | 178 aa across all RT classes | 254 columns spanned, 81 conserved positions | `PARTIALLY_RECOVERED` |
| LtrA coordinates | RT1–RT7 = R86–R364 (Blocker 2005) | blocks span LtrA **39–361**; last block ends at 361 against R364 | `PARTIALLY_RECOVERED` |

Conserved positions are real: shuffling residues within each sequence produced **zero**
conserved columns in all 200 replicates against 81 observed (p = 0.0050), and the largest gap
between consecutive conserved positions exceeds every replicate (p = 0.0050).

### What did not reconstruct

**The block count.** At the declared reporting point the criterion returns **6 blocks**, not
seven. Seven appears at exactly 1 of 30 gap values at `min_size=2` (and 4 of 30 at
`min_size=3`) — isolated settings, not a plateau. Re-aligning the same 66 sequences
independently with MAFFT returns **7**. And the count **never separates from a
column-permutation null at any gap in the sweep** (p = 0.6965 at the reporting point):
scattering the same conserved positions at random yields just as many blocks.

> `PROPOSED:` the reconstruction is **stable in where the conserved regions are and unstable
> in how many blocks they are cut into.** Matched on shared LtrA residues rather than block
> index, **5 of 6** frame-one blocks have a one-to-one counterpart in the independent
> re-alignment at a **median Jaccard of 0.955**; the single disagreement is one region that
> frame one keeps whole and frame two splits (LtrA ~170–230).
>
> Would be wrong if: the column-permutation null is too generous — it preserves the number of
> conserved columns and only destroys their order, which may be an unfairly strong null for a
> region-count statistic. The two spatial statistics that *do* separate (largest gap, gap
> CV) are reported beside it.
> → `scripts/s04_controls.py` · `tables/g2_null_by_gap.tsv` · `tables/g2_frame_correspondence.tsv`

### RT0

**No RT0 block was created.** One reconstructed block (LtrA 39–61) falls wholly inside the
region Blocker 2005 assigns to RT0, and that region *is* conserved here — which is what
Zimmerly's statement predicts for group II intron RTs. But the claim that *defines* subdomain
0 is that it is conserved **only** between group II intron and non-LTR RTs, and this substrate
has no non-LTR class. The claim is `NOT_TESTABLE_ON_SUBSTRATE`; the region is reported as
N-terminal conservation in this class, not as RT0.

Consequence for the numbering: of 6 blocks, 1 lies in the RT0 zone and 1 straddles its edge,
so **within the RT1–RT7 region proper this substrate yields 5 blocks, not seven.**

### Uncertainty

No residue edge is claimed. Every block carries a start and end **interval** across the whole
declared sweep (start uncertainty 5–58 columns, end uncertainty 3–72). The sources state a
procedure and no coordinates; a single-column edge would be false precision.

## 2 · Counts, including the ones that look bad (BS-5)

    n_attempted:  11 historical statements; 66 proteins; 1,441 columns; 150 parameter
                  settings; 200 null replicates x 2 null models; 2 alignment frames
    n_succeeded:  2 landmarks recovered, 5 partially recovered; 66/66 sequences grouped;
                  3 of 4 declared controls pass; both frames reconstructed
    n_dropped:    0 — nothing discarded. 2 statements are NOT_RECOVERED and 2 are
                  NOT_TESTABLE_ON_SUBSTRATE, and all four are landed as their own states.

Ugly counts kept in view: **1 of 4 declared controls FAILS** (C4, block clustering vs the
permutation null); **the seven-way partition is not recovered**; the two frames **disagree on
block count** (6 vs 7); and the similarity reading of the criterion gives **157** conserved
positions against 81 strict — nearly double, on the same data.

## 3 · Controls and the second frame

| control | kind | result |
|---|---|---|
| C1 catalytic Y/FxDD column is conserved | POSITIVE | **PASS** |
| C2 the Y/FxDD block is the fifth | POSITIVE | **PASS** |
| C3 conserved positions collapse under residue shuffling | NULL | **PASS** (p = 0.0050) |
| C4 block clustering beats column permutation | NULL | **FAIL** (p = 0.6965) |

**Seeded-bad guard.** `run.sh` first runs the criterion with the group threshold set to 0 — so
every column counts as conserved — and aborts if the null controls still pass. They fail, as
required.

**Second frame.** MAFFT FFT-NS-2, one thread, no iterative refinement, on the same 66 ungapped
sequences, with both frames restricted to the same LtrA residue window (36–362) so the
comparison is not between a window and a whole protein. Conserved positions: 81 vs 82.

## 4 · Claims

| id | role | contribution | status |
|---|---|---|---|
| `C3` | supporting | Operational definitions for the RT regions are partly supportable: the landmarks and the positions of conserved regions reproduce, while the seven-way partition does not survive its own criterion on its own substrate. | `UNPROVEN` |

## 5 · The self-adversarial pass (BS-14)

1. **Was the reporting rule chosen to avoid seven?** It was declared in
   `control/reconstruction_parameters.tsv` before any block was counted, and it selects the
   widest plateau. Had seven held a plateau, the rule would have selected it — in frame two it
   does select seven.
2. **Is the criterion faithfully implemented?** It is the quoted sentence, with the four groups
   of *this* substrate substituted for Xiong's four cross-class groups. That substitution is
   recorded as a deviation: it tests within-class conservation, not cross-class.
3. **Did a comparator leak in?** No Tier-2 asset appears in `INPUTS.tsv`, in any script, or in
   any path. The only external coordinates used are Blocker's LtrA residues, used to *test*.
4. **Could the 6 vs 7 difference be a MAFFT artefact?** Possibly — which is why neither frame
   is privileged. Both are landed, and the finding is the disagreement.
5. **Is "not separable from the null" too strong?** It is one statistic (block count) under one
   null (column permutation). Two other statistics separate cleanly. Reported side by side.
6. **Would a failed reconstruction have been forced into a boundary?** No block was split,
   merged, extended or dropped to reach any target number, and the kill criterion was assessed
   from the landed recovery rate rather than from prose.

## 6 · What surprised me

- **The catalytic motif lands in block 5 of 6.** Zimmerly says subdomain 5; an independent
  reconstruction that never read a modern boundary put it there.
- **The widest gap is exactly where the source says the spacer is**, and its measured range
  (5–185 residues) brackets the published 1–179.
- **The seven-way count is the fragile part, not the boundaries.** The blocks themselves
  reproduce across independent alignments at median Jaccard 0.955; only the cut count moves.
- **One conserved block sits in the RT0 zone** — in the one class where Zimmerly's statement
  says it should.

## 7 · What I could NOT check

- **Malik et al. 1999** — still unheld, so RT0's definitional source remains unread (`U01`).
- **The cross-class RT0 claim** — needs non-LTR, telomerase and viral RT sequences this
  substrate does not contain.
- **Xiong's own 1990 sequence set** — no accession is cited in that paper, so the criterion
  could not be run on the elements it was derived from, only on the closest held substrate.
- **Figure 1 extents** — digitisation was *not* required and was not done: the binding
  constraint turned out to be the block count, not the printed edges (`U03` closed as not
  needed).
- **Domain X and the 7/X spacer** — out of this gate's scope.

## 8 · Reproduction log (BS-3, WA-B.2)

    $ bash results/rt07_g2_reference_reconstruction/run.sh
    == 1. curated reference set (identity verified against the g1 acquisition record)
    reference set: 66 proteins, 1441 columns
    == 2. reconstruct blocks by the Xiong & Eickbush criterion, over the declared sweep
    conserved columns (strict, RT domain): 81  (similarity reading: 157)
    reporting point: max_gap=26 (widest plateau, width 9), min_size=2 -> 6 blocks
    == 3. seeded-bad guard: a criterion that calls everything conserved MUST fail its nulls
    SEEDED-BAD GUARD PASSED (the broken criterion failed its null controls, as required)
    == 4. landmarks, LtrA test, spacers, N-terminal region, recovery table
    YxDD at column 783 (LtrA residue 306) -> block 5 of 6
    widest inter-block gap: 4/5 (190 cols)
    == 5. controls and null models
    PASS C1, PASS C2, PASS C3, FAIL C4 (landed as a result)
    == 6. second alignment frame (MAFFT FFT-NS-2), frame-independence
    second frame: 82 conserved positions, 7 blocks; median cross-frame Jaccard 0.955
    == 7. summary, kill-criterion assessment, unresolved carried forward
    kill criterion: NOT TRIGGERED; seven-way partition: NOT ESTABLISHED
    == 8-10. report, manifest, byte comparison
    REPRODUCED: every landed table, sequence product, report and manifest is byte-identical on rerun.

`REPORT.html` is self-contained and placeholder-free; the visual inspection required by
launcher §9d is the operator's.

## 9 · Kill criterion, assessed from the landed numbers

- **Launcher g2 kill — NOT TRIGGERED.** 2 recovered + 5 partially recovered of 9 testable
  statements (78%). The landmarks do recover on the substrate they came from, so the
  reconstruction arm continues.
- **The seven-way partition — NOT ESTABLISHED.** What propagates to later gates is a set of
  **positionally reproducible conserved regions with interval uncertainty**, explicitly *not*
  an RT1–RT7 partition.
- **RT0 — OUT_OF_FRAME**, and no block was created.

## 10 · Handoff to g3

`g3` replicates prior methods under Stage-1 inputs. Three things from this gate change its
design, and they are landed in `tables/g2_unresolved_carried_forward.tsv`:

1. **A prior result that reports per-block occupancy inherits an unestablished partition.**
   `U09` (new): the block *count* matches a permutation null at every gap tested. Any prior
   number keyed to "RT1–RT7" must be reconciled against regions, not against seven boxes.
2. **Frame identity is now measurable.** The cross-frame correspondence method
   (`g2_frame_correspondence.tsv`, Jaccard on shared LtrA residues) is the instrument `g3`
   should use to ask whether a prior frame is the same object as this one.
3. **RT0 stays out.** No prior RT0 occupancy number can be replicated *as an RT0 number* on a
   substrate that cannot test the defining claim.
