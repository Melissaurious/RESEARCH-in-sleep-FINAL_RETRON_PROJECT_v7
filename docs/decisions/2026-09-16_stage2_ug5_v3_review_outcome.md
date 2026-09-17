# DECISION — UG5 v3 reviewed: FAIL/BLOCK (5/10); v3 is a detection sub-gate, not a mapper gate

Date: 2026-09-16 · Track: `rt07` · Status: **stopped; returned to the operator**

Corrects `docs/decisions/2026-09-16_stage2_ug5_v3_placement_rule_and_gate.md` and
`results/rt07_ug5_holdout_gate/ug5_v3_transfer_summary.md`. Neither is rewritten.

Supersede this record by a new record, never by rewriting it.

    REVIEW_SCORE: 5   REVIEW_VERDICT: FAIL/BLOCK
    trend: 3 -> 4 -> 4 -> 5 -> 6 -> 5 -> 5

**MAPPER NOT FROZEN. g4b NOT BEGUN. g5 BLOCKED.**

---

## 1 · Errors in this session's work, each re-verified before acceptance

| as landed | verified correct |
|---|---|
| "8.0 is the SMALLEST threshold eliminating decoy placement" | **FALSE** - the candidate grid skipped 6 and 7. Max anchor-covering decoy-domain score is **6.1 bits**, so ~7 also zeroes decoys. 8 was merely the first grid value that worked |
| the `envelope_only_v2_rule` comparison row | **MISLABELLED** - it used the exact aligned HMM span; v2 used span +/-5. The true v2-style rate is **23.75%**, not the 21.7% reported |
| 2 abstentions, reason `QUALIFYING_DOMAIN_COVERS_NO_ANCHOR` | **WRONG** - both have **zero qualifying domains**, best scores **6.2** and **5.0**. The code counted all reported domains, not qualifying ones |
| "all five order metrics saturated at 1.0000" | **inversion fraction is 0.0000** |
| "UG5 was never opened by the development scripts" | **literally false** - both call `eligible_by_family()`, which reads the whole mixed collection. The threshold COMPUTATION is UG5-free and the reviewer accepts that, but the wording overstates it, and **human blinding is not established**: v2's UG5 results existed and motivated the rule class |
| `g4a_parameter_registry.tsv` | still calls `-M 50` `algorithmic_default` / "not sensitivity tested", contradicting ADDENDUM_2 |
| `control/EXECUTION_AUDIT.md` | still carries stale Retrons 92/95 and "any defensible level" |
| `g4a_repaired_comparison_report.md` line 24 | still carries the superseded **7.7-44.9%** |
| **`bash verify.sh`** | **ABORTS on hash drift** - three g4a scripts were edited after registration and never re-registered. The provenance layer is broken |

## 2 · The load-bearing finding

**v3 validates domain-level detection and span coverage only.** The reviewer: the linear endpoint
interpolation *"mathematically guarantees colinearity; it does not inspect the residue-level HMM
alignment or internal deletions"*, and zero ambiguity is guaranteed by the one-domain result.

So the 83 placed anchors are **correlated domain-span coverage calls, not 83 independently
supported residue mappings**. This session's own self-criticism about order was judged *"correct but
incomplete"* - I identified the one-domain tautology but not that the interpolation itself
guarantees the result.

**v3 is a scoped 8-bit domain-span screening heuristic, not a hierarchical coordinate mapper.**

## 3 · What survived

Repairs 1-3 mechanically sound and independently reconstructed: **93/1/1**, `LENG`-based
**7.5-27.5%**, separated directional/unordered counts. Repair 4 recomputes exactly. v3 numbers all
reproduced: 65/67, median 83/150, **0/201 decoy replicates**, 60/67 dyad. **v2's FAILED disposition
is genuinely preserved.** Declaring tau descriptive before the run was *"honest and avoids
presenting tautology as evidence."*

## 4 · Headline correction

Not *"roughly half the frame does not transfer"* but **"67 of 150 anchors are unplaced by this rule
in the median UG5 sequence"** - an operational statement about a screening rule, not biological
non-transfer.

## 5 · `-M a2m` is not reconciled

Under HHmake's documented default, DGRs and AbiA have **zero** source-oriented `ALL_PARTNERS`
positions. GII retains 115, so the **GII-centred frame survives**, but a **family-symmetric**
shared-core claim does not. The primary `-M 50` frame is implementation-dependent and must be
narrowed or prospectively justified.

## 6 · Required repairs

1. Non-rewriting erratum correcting: threshold minimality, the mislabelled v2-rule comparison,
   inversion wording, the dyad definition, and both abstention reasons.
2. Rebuild and externally anchor complete g4a **and** v3 registries - ADDENDUM_2, all development
   and v3 scripts, the sensitivity step, construction hashes, expected tables, fresh-directory
   verifier.
3. **Prospectively validate an actual HMM-state-to-residue mapper** that parses alignments and can
   falsify order and ambiguity, on non-UG5 development **and a fresh held-out lineage**. Do not
   reuse UG5 as a tuned confirmatory holdout.
4. Reconcile `-M a2m`: narrow to a GII-centred implementation-dependent frame, or justify `-M 50`
   prospectively.

## 7 · Why this session stops

Repairs 1, 2 and 4 are bounded. **Repair 3 is not**: it requires a *fresh held-out lineage* and a
genuinely alignment-resolved mapper - a new gate, and a scope decision. Three consecutive reviews
have now returned 5/10, each defeated by something structurally deeper than the last.
