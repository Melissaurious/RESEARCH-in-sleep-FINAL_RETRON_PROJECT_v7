# rt07_g2_reference_reconstruction

_The landmarks reconstruct. The seven-way partition does not._

Every number below resolves to a landed table via `tables/g2_resolved_values.tsv`. This document computes nothing.

## 1 · What was reconstructed, and on what

The substrate is ALIGN_000044 itself - the alignment Zimmerly 2001 adjusted its inherited subdomain labels against, acquired and hash-verified in g1. **66** proteins in **4** lineage groups, assigned by declared keyword rules over the record's own description lines. Applying the Xiong & Eickbush criterion verbatim - a residue present in over 50% of the elements of at least three of four groups - yields **81** conserved positions in the stated RT domain (**157** under the chemically-similar reading).

> No comparator was read. No Toro, Mestre, myRT, SPIRE, prior HMM, prior boundary or prior anchor set touched this reconstruction; those belong to g3.

Tables: `tables/g2_reference_sequence_set.tsv`, `tables/g2_conserved_positions.tsv`

## 2 · The conserved positions are real

Shuffling residues within each sequence destroys the signal completely: across 200 replicates the null never produced a single conserved column, against **81** observed (empirical p=**0.0050**). The largest gap between consecutive conserved positions also exceeds every replicate (p=**0.0050**), so the conserved positions are not scattered evenly - they leave one long empty stretch.

> **3** of the declared controls pass and **1** fails. The failure is reported in section 4 and it is the most important number in this bundle.

Tables: `tables/g2_null_model.tsv`, `tables/g2_null_spatial_statistics.tsv`

## 3 · The landmarks recover

Of the declared historical statements, **2** recover outright, **5** recover partially, **2** do not, and **2** are not testable on this substrate. The catalytic motif lands exactly where Zimmerly 2001 says it does: **the catalytic Y/FxDD lies in reconstructed block 5 of 6 (alignment column 783, LtrA residue 306)**. The widest inter-block gap is the one the source describes as the variable insertion site: **widest inter-block gap is 4/5 at 190 columns, 5-185 residues across sequences**. Within-group conservation is close to the authors' own figures - **100** conserved columns for the bacterial group against their published 94.

> Kill criterion: **NOT TRIGGERED**. The landmarks do recover on the substrate they came from, so the reconstruction arm continues.

Tables: `tables/g2_landmark_recovery.tsv`, `tables/g2_interblock_spacers.tsv`, `tables/g2_per_group_conservation.tsv`

## 4 · The block COUNT does not

At the reporting point declared before any block was counted, the criterion returns **6** blocks, not seven. Re-aligning the same **66** sequences independently with MAFFT returns **7**. Seven blocks recovered in frame one: **NO**; in frame two: **YES**. And the count never separates from a column-permutation null at any gap in the declared sweep (p=**0.6965** at the reporting point) - scattering the same conserved positions at random produces just as many blocks.

> **NOT ESTABLISHED**: what propagates to later gates is a set of positionally reproducible conserved regions with interval uncertainty, NOT an RT1-RT7 partition. No block was split or merged to make seven.

Tables: `tables/g2_parameter_sweep.tsv`, `tables/g2_null_by_gap.tsv`, `tables/g2_second_frame.tsv`

## 5 · Positions agree across frames even where the count does not

Matched on shared LtrA residues rather than on block index, **5** of the frame-one blocks have a one-to-one counterpart in the independent re-alignment, at a median Jaccard of **0.955**. The single disagreement is one conserved region that frame one treats as a single block and frame two splits. Conserved positions themselves are stable: **81** against **82**.

> PROPOSED: the reconstruction is stable in WHERE the conserved regions are and unstable in HOW MANY blocks they are cut into. That distinction is the finding, and it is what a later occupancy analysis has to respect.

Tables: `tables/g2_frame_correspondence.tsv`, `tables/g2_second_frame_blocks.tsv`

## 6 · RT0 was not created

RT0 block created: **NO**. Block **1** falls inside the LtrA region Blocker 2005 assigns to RT0, and that region is conserved here - which is what Zimmerly's statement predicts for group II intron RTs. But the claim that DEFINES subdomain 0 is that it is conserved only between group II intron and non-LTR RTs, and this substrate has no non-LTR class. The claim is untestable here and no block was created because later literature uses the name.

> Uncertainty is carried as intervals, not edges: the widest block start interval across the declared sweep is **58** columns and the widest end interval **72**. The sources state a procedure and no residue edges, so no single-column boundary is claimed.

Tables: `tables/g2_nterminal_region.tsv`, `tables/g2_block_uncertainty.tsv`, `tables/g2_unresolved_carried_forward.tsv`
