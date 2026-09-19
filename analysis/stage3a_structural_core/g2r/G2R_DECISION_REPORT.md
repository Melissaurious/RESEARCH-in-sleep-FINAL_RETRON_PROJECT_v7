# Stage 3A · g2r — DECISION REPORT (domain-parser repair gate)

**Stage-3A g2r status: FAIL** under the frozen verdict rule. Both instrument gates passed, so this is not
INSTRUMENT_LIMITED. The palm-like region is recurrent and replicate-stable but is called in only 0.565 of
primary chains, against a bar of 0.70. Thumb-like and fingers-like are rare and unstable. No threshold, constant
or rule was changed after any outcome.

## Commit chain

| commit | content |
|---|---|
| `03cf6f15` | checkpoint g0–g2 as obtained (C3 VOID retained) |
| `ee49f57e` | g2r pre-registration |
| `4aeb2181` | amendment 1: Codex R1, F1–F7 |
| `efb1eadf` | amendment 2: Codex R2, B1–B8. Codex R3 then returned CLEARED_TO_RUN |
| `6f37711e` | instrument gates |
| `76526444` | RT C3r partition frozen (`results/RT_PARTITION_FREEZE_sha256.txt`) before any C4–C7 score |

## Instruments

- **C3r external validation** on 100 CATH chains (30/30/25/15; 33 discontinuous), primary BioJava 7.1.4. **ACCEPT**:

  | gate | value | bar |
  |---|---|---|
  | A | 0.610 | 0.60 |
  | B | 0.733 | 0.70 |
  | C | 0.886 | 0.60 |
  | D | 0.993 (n=61) | 0.80 |
  | E1 | 0.939 | 0.60 |
  | E2 | 0.849 | 0.70 |

  - A and B pass narrowly. The parser both over-splits (8/30 single-domain chains) and under-splits.
  - BJ-p4 gives the same outcome; C drops to 0.871 and E1 to 0.909.
- **Secondary structure (routes A vs B, 62 chains):** **RELIABLE**.

  | state | median κ | recall | precision |
  |---|---|---|---|
  | E | 0.986 | 0.986 | 1.000 |
  | H | 0.981 | 0.994 | 0.993 |

  - 62/62 chains pass the chain gate, with coverage 1.000.
  - The g1 strand recall of 0.701 belonged to the self-written DSSP-KS, not to DSSP.

## RT structural units (primary instrument)

- **Domain counts (all 62 chains):** 1–8 per chain. In the primary population (n = 46), the counts are 1:2, 2:12, 3:18, 4:11, 5:3.
- **Discontinuity:** 48/139 primary units are discontinuous, and 19/26 palm-like units have more than one segment.
- **Replicate domain-count agreement:** 0.385 over 52 primary pairs. The PDP partition count is itself not replicate-stable.
- **PDP_ABSENT residues:** 7R06_A 44 PTR; 8C8J_A 661 CSX; 9Z6Y_H and 9Z6Z_H 650 PTR.
- **IMPLEMENTATION_SENSITIVE (primary ≠ BJ-p4):** 5/62. Of these, 9C0I_A and 9N69_E are primary chains; 7KFT_C, 8UW3_A and 9Z6Z_H are flagged. They stay in every denominator.

## C4–C7 (primary population n = 46: excludes 15 flagged chains and design-exposed 5HHJ_A)

| region | call rate | C6 recurrence | C7 replicate Jaccard | meets bar |
|---|---|---|---|---|
| palm-like (C4) | **0.565** (26 CALL / 19 NO_CALL / 1 AMBIGUOUS) | RECURRENT, median 0.798 over 35 group pairs | STABLE, median 0.798 over 8 groups | no (call rate) |
| thumb-like (C5) | 0.130 | UNDERPOWERED, 0.000 over 7 group pairs | NOT_STABLE, 0.000 over 5 groups | no |
| fingers-like (C4b) | 0.304 | UNDERPOWERED, 0.721 over 8 group pairs | NOT_STABLE, 0.000 over 5 groups | no |

- **C4 NO_CALL diagnosis** (descriptive, post-freeze, not acted on): in 17/19 NO_CALL chains, a unit carrying ≥ 4 same-sheet strands exists but has frac_E < 0.20. The sheet is present, but the PDP unit containing it is too large and helix/coil-rich to qualify. In 2/19 no unit holds 4 same-sheet strands.
- **Instrument limits:** no chain was INSTRUMENT_LIMITED at chain level. C5 and C4b are NOT_EVALUABLE in the 20 primary chains without a palm call.

## Stability, LOGO, fusions

- **LOGO** (22 primary groups):
  - Every fold gives FAIL, and no fold flips any region's bar outcome.
  - Palm call rate ranges 0.500–0.650, so no fold reaches 0.70.
  - Palm C6 ranges 0.778–0.831 and palm C7 ranges 0.628–0.968.
- **BJ-p4 sensitivity:** the primary-population numbers and verdict are identical.
- **Flagged stratum** (15 chains; fused YES/SUSPECTED or > 600 residues):
  - Verdict-rule outcome FAIL.
  - Palm call rate 0.467; recurrence and stability UNDERPOWERED.
  - Replicate domain-count agreement 0/12.
- **EXTRA_DOMAIN units:** 26/219, of which 18 are in flagged chains. These are units < 10 % aligned to any other group at min-TM ≥ 0.50.
- **All non-exposed chains pooled (61):** FAIL. Palm call rate 0.541. C4b becomes RECURRENT (0.695 over 11 group pairs), but it is not stable.
- **Design-exposed 5HHJ_A:** 2 units; palm CALL, thumb NO_CALL, fingers CALL. It is reported only and not scored.

## Supported statement

In 46 experimental RT chains, a size-normalised structural-domain parser was validated externally on CATH but only narrowly. With it and without any retron boundary, motif or family input:

- The chains do **not** decompose reproducibly into three conventional units.
- A palm-like β-sheet unit is recovered in about half of the chains (0.565). Where it is recovered, it recurs across proteins (0.80) and is stable across replicates (0.80).
- Thumb-like and fingers-like units are neither frequent nor stable under this parser.

The parser's own domain count agrees between replicates of the same protein only 38.5 % of the time. This limits any unit-level claim beyond the palm.

## Not done (out of scope, per instructions)

- No redesign after outcomes.
- No transfer to predicted structures.
- No comparison with literature boundaries, historical boundaries, Stage 3B or RT0–RT7.
