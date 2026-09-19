# cat3b_g2 — contract, thresholds and frozen detector

Calibrated on **Tier A only**. Tier B was never read; `evaluate_tierA.py` asserts it.

**Frozen detector** `stage3b-detector-1.0`: candidate = unordered Asp pair with modelled
carboxylates, `SEP_MIN <= |i-j| <= SEP_MAX`, min carboxylate O-O distance `<= D_MAX`; score = that
distance ascending; prediction = best candidate; AMBIGUOUS if the top two differ by `< DELTA_TIE`;
ABSTAIN if no admissible candidate. Parameters: `SEP 75..115`, `D_MAX 6.0 A`, `DELTA_TIE 0.25 A`,
`RES_MAX 3.5 A`.

**Tier A calibration (declared residue-exact metric):** 13 HIT / 6 MISS / 0 ABSTAIN over 19
truth-bearing chains = **0.684**. 6 AMBIGUOUS verdicts. 4 chains NOT_SCOREABLE at 3.5 A.
Decoy pool inside the detector's candidate space: **36** admissible non-truth pairs across 23 chains.

**Diagnostic, not the declared criterion and used for no threshold:** all 6 misses are
adjacent-aspartate confusions inside the correct site; site-level overlap is 19/19.

**PASS bar is deliberately NOT set** — the launcher predeclares PARTIAL and requires Tier B to be
enlarged before a PASS is available. Named PARTIAL scope is in `tables/g2_frozen_parameters.tsv`.

STATUS: VERIFIED

n_attempted: 19
n_succeeded: 13
n_dropped: 6
n_attempted/n_succeeded/n_dropped are the Tier A truth-bearing chains, hits and misses; abstentions among them are 0.
