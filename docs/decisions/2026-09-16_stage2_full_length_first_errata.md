# DECISION — Full-length-first review outcome: FAIL/BLOCK at 5/10, verified errata, forks returned

Date: 2026-09-16 · Track: `rt07` · Status: **stopped; returned to the operator**

**Corrects** `docs/decisions/2026-09-16_stage2_full_length_first.md` and the tables in
`results/rt07_pre_g4_full_length_design/`. Those are left **byte-unchanged** — their hashes are in
`review-stage/DESIGN_REVIEW_REQUEST_full_length_first.md` and they are the reviewed object.

Supersede this record by a new record, never by rewriting it.

    REVIEW_SCORE: 5     REVIEW_VERDICT: FAIL/BLOCK
    review_gate.py -> {"decision": "continue", "reason": "positive threshold not met"}

**NO FULL-CATALOGUE APPLICATION; g5 NOT STARTED.**

---

## 1 · Errata — refuted, and re-verified here before acceptance

| # | as landed | verified correct | how it happened |
|---|---|---|---|
| E1 | "1,835 source proteins" | **1,835 seed-fragment MAPPINGS; 1,831 unique parents.** The ≥80 aa fraction is 62.0% on both bases | a mapping count was described as a protein count |
| E2 | "80 aa is the size of the LtrA RT0 zone" | **the zone is LtrA 1–85 = 85 aa.** At ≥85 aa the figure is **1,090/1,835 = 59.4%**, not 62.0% | an off-by-five on an inclusive residue range, propagated into the headline statistic |
| E3 | "7.3× length spread" | **7.09×** — UG11 257.0 to UG10 1,821.5 aa | arithmetic not recomputed after the eligibility filter |
| E4 | "41 family directories, 32 UG/Abi labels" | **38 family directories** | a subagent's number passed through without verification — the same class of error as the round-2 `most_common(10)` truncation |
| E5 | Toro tree "tips are fig IDs" | only **6,884 of 9,141** are `fig\|` identifiers | overbroad generalisation from the head of the file |

**E2 is the one that matters.** It is the headline justification for full-length-first, and the
corrected figure is **59.4%**, not 62.0%. The direction still holds — a majority of proteins carry
enough discarded N-terminal sequence to contain an RT0-sized feature — but the number quoted in
support of it was wrong.

## 2 · Blocking findings accepted without argument

1. **The design still inherits the RVT_1 coordinate system.** Strategy A makes Pfam `RVT_1` the
   primary scaffold while Strategy C uses 46 myRT **seed-derived** Stockholm profiles in
   correspondence inference. That **contradicts the launcher amendment's own claim that the seed
   fragments are comparator-only**, and it means the product is a *Pfam-conditioned mapping study*,
   not broad architecture inference. This session flagged the risk to the reviewer; it is real.
2. **The collection is not established as full-length.** No per-protein completeness field, no build
   manifest, and at least seven eligible coordinate-named proteins touch a contig boundary. A 250 aa
   floor cannot establish intact termini, yet `T5` requires "not truncated".
3. **`F09` is epistemically wrong** — aligner agreement is neither necessary nor sufficient for
   homology.
4. **`T1`/`T2` overlap**, and `T2` conflates "absent" with "unlocatable" against `V12`.
5. **A held-out family is not held out** while its myRT profile survives, and **no withheld families
   or lineages are named**.
6. **The 90% anchor bar is post-hoc** — the same violation the round-2 reviewer found in `AC3`. And
   `ANCHOR_POOR`, used to declare later poor performance "not a finding", **pre-excuses failure**.
7. **`F10` requires `F02` AND `F06` together**, so either major premise can fail without killing the
   common-frame claim. `F01`/`F04`–`F06` shrink scope rather than stopping.
8. **`run.sh` is not a verification harness** — it `tee`s over the expected output instead of
   diffing against it, so it cannot detect drift. `INPUTS.tsv` omits the Stockholm profiles, Pfam
   and the structural inputs the proposed methods require.
9. **The retron 51 aa vs GII 88–110 aa difference is an operational length difference** measured
   against model-defined window starts. Calling it an "architectural difference" over-reads it.

## 3 · What survived, and is now independently reproduced

The reviewer executed `scripts/measure.py` and obtained a **byte-equivalent value stream**, then
recomputed the substantive results independently. Confirmed: the per-family N-terminal medians;
2,339/2,339/10/2,166; **2,165 of 2,166 non-redundant at 4-mer Jaccard 0.90, stable from 0.70 to
0.95**; dyad occupancy 94.9% overall and **95.4% on the eligible set**, 251 multi-hit, the same
seven sub-90% families; the per-label-cap failure at 76.5/3.3 → 73.2/4.4; the 486-member
hierarchical panel at 18.5% UG and 18.5% retron; and the Toro tree at **exactly 9,141 terminals
with no UG annotation**.

Adding a reproducible script was the right repair: it is what let the reviewer verify rather than
guess, and it is why this round's errata are five small numbers rather than six substantive ones.

## 4 · Forks returned

1. **Stop Stage 2 at 2A, or authorize only a bounded `g4a`/pilot as a myRT/Pfam-conditioned
   coordinate-methods study?** The reviewer: *"The present design does not justify g4b, g5 or g6."*
2. **Forced universal frame, or hierarchical class/family-first?** The reviewer judges the evidence
   supports **class/family-first construction followed by estimation of the supported intersection**
   — the reverse of this design's global-first order — and that "no shared retron frame" must be a
   permitted outcome.
3. **Is "broad RT architecture" worth acquiring external assets for** — a non-LTR/telomerase
   universe, independent retron depth, and the 2022 UG group assignments? Without them the
   permissible product is **operational callability and spacing on a limited bacterial/myRT
   reference universe**.

## 5 · Repairs recorded, not attempted

Per-protein completeness evidence replacing the 250 aa proxy; re-scan against a pinned hashed Pfam
`RVT_1`; name the withheld families and rebuild any profile whose ancestry overlaps them; define
the multi-dyad rule and measure all anchors before derivation; treat the 90% bar as exploratory;
make `T1`–`T3` mutually exclusive and rename `T4` to inter-anchor length; freeze alignment
algorithms, versions and parameters; rewrite `F01`–`F10` as claim-level stops with fixed
denominators; make reproduction non-destructive (`diff`, not `tee`) and hash every input the
methods need.
