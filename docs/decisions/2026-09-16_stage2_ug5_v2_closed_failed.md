# DECISION — UG5 gate v2 CLOSED as FAILED on predeclared criterion 2

Date: 2026-09-16 · Track: `rt07` · Status: **closed; preserved as a valid falsifying result**

Operator decision 1 of 2026-09-16. Supersedes the UG5 portions of
`docs/decisions/2026-09-16_stage2_g4a_repair_and_ug5_gate.md` §4 and of
`results/rt07_ug5_holdout_gate/ug5_transfer_summary.md`. Neither is rewritten.

Supersede this record by a new record, never by rewriting it.

**Disposition: `FAILED on predeclared criterion 2: anchor order coherent`.**

**g4b NOT BEGUN. g5 BLOCKED.**

---

## 1 · The sequence of events, stated plainly

**v1 — aggregate profile — passed its own criteria.** One profile was built per UG5 subset and
projected onto the frozen frame. All six predeclared criteria were met: 135/150 anchors placed,
monotone order, 0% ambiguity, decisive decoy separation.

**The independent reviewer identified why that was not trustworthy.** Monotone order and zero
ambiguity were *"largely guaranteed by the one-to-one, order-preserving pairwise-alignment map"* —
an aggregate profile-to-profile alignment essentially cannot emit disorder, so the criterion could
not fail. The estimands were **partly tautological**.

**v2 — per sequence — made them falsifiable.** `hmmsearch` against an individual sequence *can*
emit out-of-order, duplicated or missing anchors.

**Made falsifiable, the criterion failed.**

    predeclared criterion 2:  anchor order is coherent
    observed:                 monotone for 31 of 67 sequences = 46.3%
                              36 sequences show 1-8 order inversions

## 2 · The criterion is NOT replaced

`anchor order coherent` is what was predeclared for v2, and it remains the criterion v2 is judged
against. It is **not** substituted — after the fact — with Spearman correlation, Kendall tau,
inversion count, ordered-pair fraction, longest monotone subsequence, local adjacency preservation,
or any other graded statistic. Doing so would change the success criterion after seeing the result.

**v2 remains FAILED on criterion 2.**

## 3 · A second, independent reason v2 does not support g4b

Even setting order aside, **v2's placement and callability numbers are not fully interpretable**.
The v2 placement rule was *envelope coverage only*: an anchor counted as placed if any hit envelope
spanned its HMM coordinate, **with no score criterion whatsoever**. A decoy envelope scoring
**−2.8** therefore "placed" every anchor it covered, which is why the shuffled-decoy maximum reaches
150 anchors while the decoy median is 0.

The defect is in the executing session's own rule, not in the data. It means v2's
`median 59.3% placed` cannot be read as a clean transfer rate.

## 4 · What v2 nevertheless establishes, and keeps

v2 is **preserved as a valid negative/falsifying result**, not discarded:

- the **holdout is genuine** — 24/24 construction inputs `UG5_GENEALOGY_PRESENT = FALSE`, audited
  by file content for UG5 ids and UG5 sequences;
- the **frozen frame is landed in full** — 150 anchors in 11 contiguous runs, span 107–317, in GII
  consensus coordinates;
- **every component was evaluated, including the singleton**, and the v1 claim that the 3-sequence
  component transferred poorly (36.0%) is **refuted**: per sequence, components 2 and 3 place
  *more* anchors (70.0%, 74.7%) than the large ones. That asymmetry was an aggregate-profile
  artefact;
- **0 sequences abstained**;
- the catalytic dyad falls within the placed span in **61 of 67** sequences;
- the decoy **median is 0%** across three replicates, so the central tendency does separate.

**The scientific value of v2 is that it falsified a claim v1 could not have falsified.** That is the
correct outcome of making an estimand honest.

## 5 · Versioning

v2 outputs are frozen at their existing paths under `results/rt07_ug5_holdout_gate/`:

    tables/ug5_per_sequence_mapping.tsv     tables/ug5_component_summary.tsv
    tables/ug5_abstention.tsv               tables/ug5_coordinate_stability.tsv
    tables/ug5_decoy_controls.tsv           tables/ug5_evaluation_split.tsv
    tables/ug5_split_pairwise_audit.tsv     tables/ug5_holdout_provenance_audit.tsv
    tables/ug5_frozen_anchor_coordinates.tsv
    scripts/ug5_gate.py (v1)                scripts/ug5_gate_v2.py
    control/ug5_holdout_predeclaration.md   control/UG5_V2_STOP_REPORT.md

**No v3 output may overwrite any of these.** Every v3 artefact carries an explicit `ug5_v3_`
prefix.

## 6 · Consequence

**v2 does not justify g4b.** The mapper is not frozen. Any future UG5 gate is **v3**, with its
placement rule and order statistic predeclared *before* execution and derived **without any UG5
information**, per operator decision 2.
