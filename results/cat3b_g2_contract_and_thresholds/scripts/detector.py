#!/usr/bin/env python3
"""Stage 3B catalytic-site detector — FROZEN at g2, calibrated on Tier A only.

ALLOWED INPUTS (anti-circularity contract): Asp side-chain carboxylate coordinates; pairwise
carboxylate distances; |i-j| sequence separation between the two candidate residues (window
calibrated on Tier A only and frozen here).
NOT USED, anywhere in this module: motif identity or any regex; RT5/state coordinates;
fingers/palm/thumb boundaries; family labels; Gate S; expected normalised position; metal or
ligand positions; Tier B.

CANDIDATE GENERATION
  every unordered pair (i<j) of Asp residues with modelled OD1/OD2, such that
  SEP_MIN <= |i-j| <= SEP_MAX  and  min carboxylate O-O distance <= D_MAX.
SCORE           min carboxylate O-O distance, ascending (pure geometry).
PREDICTION      the single best-scoring candidate.
AMBIGUITY RULE  AMBIGUOUS if |d(best) - d(second)| < DELTA_TIE.
ABSTENTION RULE ABSTAIN if no candidate is admissible. Abstention is reported separately from
                failure and is never counted as a miss.

FROZEN PARAMETERS
  SEP_MIN, SEP_MAX  outward rounding to the nearest 5 of the observed Tier A truth-pair range
                    (75..113 observed -> 75..115). Declared rule, not optimised.
  D_MAX             ceiling to the nearest 0.5 A of the largest Tier A truth-pair distance
                    (5.65 -> 6.0). Declared rule, not optimised.
  DELTA_TIE         0.25 A, declared on the ground that it lies below the coordinate precision of
                    a 3.5 A cryo-EM map. NOT derived from any outcome.
  RES_MAX           3.5 A eligibility cut (see g1). Chains above it are NOT SCOREABLE.
"""
SEP_MIN, SEP_MAX, D_MAX, DELTA_TIE, RES_MAX = 75, 115, 6.0, 0.25, 3.5
DETECTOR_VERSION = "stage3b-detector-1.0"

def candidates(asp_carboxyl):
    """asp_carboxyl: {resnum: [gemmi.Position, ...]} -> sorted list of (dist, i, j)."""
    import itertools
    out=[]
    for i, j in itertools.combinations(sorted(asp_carboxyl), 2):
        if not (SEP_MIN <= abs(i-j) <= SEP_MAX): continue
        d = min(p.dist(q) for p in asp_carboxyl[i] for q in asp_carboxyl[j])
        if d <= D_MAX: out.append((round(d,3), i, j))
    return sorted(out)

def predict(asp_carboxyl):
    """-> (verdict, pair_or_None, candidates). verdict in {PREDICT, AMBIGUOUS, ABSTAIN}."""
    c = candidates(asp_carboxyl)
    if not c: return "ABSTAIN", None, c
    if len(c) > 1 and abs(c[0][0] - c[1][0]) < DELTA_TIE: return "AMBIGUOUS", (c[0][1], c[0][2]), c
    return "PREDICT", (c[0][1], c[0][2]), c
