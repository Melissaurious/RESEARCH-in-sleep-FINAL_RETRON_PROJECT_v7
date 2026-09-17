# g4a REPAIRED — superseding predeclaration ADDENDUM 2

Written **before** any repair code was changed and before any table was regenerated. Registers the
rules the independent review found unregistered, and fixes the wording it found overstated.

Authority: independent review of the repaired g4a + UG5 gate, `FAIL/BLOCK` 5/10, recorded in
`review-stage/AUTO_REVIEW.md` and
`docs/decisions/2026-09-16_stage2_g4a_repair_ug5_review_outcome.md`. Operator authorisation
2026-09-16 for repairs 1–8 and for reworking the UG5 gate to per-sequence evaluation.

## 1 · Sequence-identifier handling (repair 1)

`mmseqs` normalises identifiers: an input id `sp|P23070.1_Retrons` is returned as
`P23070.1_Retrons`. The prefix is stripped, the hit never matches back, and the sequence becomes a
**phantom singleton component**.

**Registered rule:** before any `mmseqs` call, every sequence is renamed to an opaque surrogate id
`s<NNNNNN>`; results are mapped back through the surrogate table. **The pipeline then asserts exact
equality between the input id set and the id set recovered from the output, and fails closed on any
mismatch.**

Consequence already known: **Retrons is `93/1/1`, not `92/1/1/1`.**

## 2 · Directional vs unordered pair counts (repair 3)

`mmseqs` emits both directions of a pair. The previous tables reported **row** counts as if they
were pair counts.

**Registered rule:** cross-role relatedness is counted as **unordered pairs**. Both are landed:
`n_directional_rows_ge50pct` and `n_unordered_pairs_ge50pct`, never conflated.

## 3 · The 90%-dominance fragmentation criterion (repair 3)

Used in the previous run but never registered.

**Registered rule:** a family **fragments** when it has more than one separation component **and**
its largest component holds **≤ 90%** of eligible members. Otherwise it does not fragment, its
challenge set is `NON_INDEPENDENT_CHALLENGE`, and no transfer claim is made from it. The 90% figure
is a **declared implementation choice**, not a biological threshold.

## 4 · Full-consensus denominator (repair 2)

**Registered rule:** the full-consensus length is the HHM **`LENG`** field, parsed directly. The
previous code counted rows matching `^[A-Z]\s+\d+\s`, which undercounts — CRISPR 305 against
`LENG` 796. Both denominators remain reported: `pct_of_covered` and `pct_of_full_consensus`.

## 5 · `hhmake -M` (repair 4)

**Reclassified** from `algorithmic_default` to **`implementation_choice`**. HHmake's documented
default is `-M a2m`; `-M 50` is a deliberate selection that controls match states and therefore the
frozen frame.

**Registered sensitivity test:** the supported intersection is recomputed at `-M 50`, `-M 60` and
`-M a2m`, and the effect on the shared-core size is landed. **The value is not changed to improve
any result** — `-M 50` remains the primary setting regardless of what the sweep shows.

## 6 · Wording correction (repair 8)

**Withdrawn:** *"no independent within-family held-out set exists at any defensible separation
level."*

**Replacement:** *"no adequately sized independent within-family holdout exists **at the declared
0.30 / 0.50 rule**."* At identity 0.50 the families do fragment substantially (largest components
GII 98, DGRs 104, CRISPR 15, UG3 5, Retrons 6). Retaining 0.30 and refusing a post-outcome
threshold change remains the declared, conservative position.

## 7 · UG5 gate reworked to per-sequence (repair 5, operator-authorised)

The previous gate mapped an **aggregate profile** per UG5 subset. Monotone order and zero ambiguity
were therefore largely guaranteed by the one-to-one, order-preserving pairwise map — partly
tautological.

**Registered rules for the reworked gate:**

- **all 150 frozen anchor coordinates are landed**, not just their count and span;
- the frozen frame is projected onto **each UG5 sequence individually**;
- **every component is evaluated, including the singleton**;
- per sequence: anchors mapped, dyad inclusion, inter-anchor spacing, coordinate stability;
- **order is non-tautological**: measured against the sequence's own residue numbering, where a
  profile-to-sequence search *can* emit out-of-order or duplicated hits;
- **ambiguity is non-tautological**: counted as competing placements of the same anchor above the
  reporting threshold, not as two anchors sharing one column;
- **abstention is explicit**: a sequence or anchor with no supported placement is recorded as
  `NOT_PLACED`, never as a silent absence.

No UG5-derived object enters construction; the provenance audit is unchanged and still fails closed.

## 8 · Verifier and provenance (repairs 6, 7)

- a **UG5 verifier** is added, with the same semantics as the g4a one: enforce registered input
  hashes, run into a fresh temporary location, diff against frozen tables, non-zero on drift, never
  overwrite;
- `AUTHORED_TABLES.txt`, the parameter registry, the audit files and the narrative reports are
  **registered in `INPUTS.tsv`** so the authored-table list can no longer be edited to bypass
  comparison;
- the 24 UG5 construction inputs are hashed **at gate time** and re-verified, so the post-gate hash
  drift observed by the reviewer cannot recur silently.

## 9 · Stop condition

**If any repair materially changes the currently supported scientific conclusion — dyad 42/42,
correspondence 42/42, transitivity ~87%, shared core a minority, positive UG5 transfer — work stops
and returns to the operator before the review is requested.**
