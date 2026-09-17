# rt07_g3_prior_method_replication

_What survives the prior work, and what was never the object it was named for_

Every number below resolves to a landed table via `tables/g3_resolved_values.tsv`. This document computes nothing.

## 1 · The audit

**13** prior claims were audited on object identity, frame identity, seed dependence, conditioning and reproducibility. Verdicts: **2** reproduced in the same object and frame, **1** partially reproduced, **3** circular or seed-dependent, **2** object mismatches, **1** frame mismatch, **2** already withdrawn by the prior work, **2** not testable here. **4** of 4 controls pass.

> No prior number became an acceptance criterion, including the ones that reproduced exactly.

Tables: `tables/g3_prior_claim_verdicts.tsv`, `tables/g3_controls.tsv`

## 2 · Independence: the anchors are the seed

Re-measured by exact sequence identity, not by identifier: **100.00**% of the 72 anchors are members of the model seed, and **63.89**% are also members of the retron population they score. Only **26** of 72 carry a PDB identifier. New here: **7** carry a His6 expression tag and one carries a SUMO tag, so their residue numbering includes vector-derived sequence. The gold panel is **25.73**% seed, leaving **127** members genuinely outside it.

> These reproduce the prior audit's own figures exactly, from the files rather than from its report - which is what makes them usable.

Tables: `tables/g3_set_overlap.tsv`, `tables/g3_anchor_composition.tsv`

## 3 · Frames: four coordinate systems, one landmark set

The primary frame ships as RT17_CORE.hmm but declares NAME **B_span17**, **305** match states, and is byte-identical to B_span17.hmm. Carried onto shared LtrA residues, **27/28** prior landmark placements fall inside an independently reconstructed g2 region, and six of seven landmarks sit at the IDENTICAL LtrA residue in every prior frame.

> PROPOSED: the four frames are not four independent determinations of the landmarks. They are four coordinate systems over one anchor-derived landmark set, so agreement between them prices transfer consistency, not replication.

Tables: `tables/g3_frame_identity.tsv`, `tables/g3_prior_region_correspondence.tsv`

## 4 · The seven-way partition does not survive reconciliation

Only **4/29** prior frame blocks are fixed by a published motif; the rest are order-interpolated. The seven prior labels collapse onto SIX g2 regions, because **RT5 and RT6** both fall inside g2 block **5**.

> No old seven-block result is defensible AS a seven-way partition after frame reconciliation. The landmarks and their ORDER survive; the seventh boundary does not.

Tables: `tables/g3_prior_frame_correspondence.tsv`

## 5 · RT0 was never measured on the RT0 region

Verdict: **OBJECT_MISMATCH**. The prior frame spans LtrA **53-361** and does not cover the conserved RT0 alanine at LtrA **39** (covered by the prior frame: **NO**); the independently reconstructed g2 region **1** does cover it. The prior RT0 occupancy contrast is real and was measured with a declared positive control that passed - but on interpolated N-terminal blocks that exclude the only specific RT0 landmark available.

> U01 stays open and the g2 scope limit stands: the claim that defines RT0 is cross-class and remains untestable on the available substrate. No RT0 occupancy value may be carried forward as an RT0 number.

Tables: `tables/g3_rt0_object_audit.tsv`

## 6 · RT1, measured and not interpreted

RT1 is the only landmark that moves between prior frames, and its prior concordance is 0.75 against a declared 0.90 bar. In shared coordinates it falls at LtrA **49**, inside g2 block **1** - which lies in the region Blocker 2005 assigns to RT0, not RT1.

> The INTERPRETATION of the RT1 failure is not settled here. Whether it is a limitation of the method or an independent recovery of a weakness the founding authors flagged remains an operator decision; g3 adds one measured fact to it.

Tables: `tables/g3_prior_claim_verdicts.tsv`, `tables/g3_handoff_to_g4.tsv`
