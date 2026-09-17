# UG5 gate v3 — transfer summary

Rule frozen in `control/UG5_V3_PREDECLARATION.md` (sha256 `2dd7dd08608e3087…`) **before** any UG5
v3 evaluation, and derived from construction-family data only. v2 outputs are untouched; every v3
artefact carries the `ug5_v3_` prefix.

## 1 · The frozen rule, and where it came from

**An anchor is PLACED when a `hmmsearch` domain scores ≥ 8.0 bits and the anchor lies inside the
domain's *aligned* HMM span.** Highest-scoring domain wins.

Derived on **817 real + 817 decoy** construction sequences (GII HMM → the five other construction
families + their shuffles). **UG5 was never opened by the development scripts.**

| rule | real median | decoy max | decoy % placed |
|---|---|---|---|
| **envelope only — the v2 rule** | 150 | **150** | **21.7%** |
| score ≥ 5 | 150 | 9 | 0.12% |
| **score ≥ 8 — selected** | 150 | **0** | **0.00%** |

8.0 is the *smallest* threshold eliminating decoy placement entirely — the least aggressive filter
that achieves the goal. This also **independently confirms on non-UG5 data that the v2 rule was
broken.**

## 2 · Results

| quantity | result |
|---|---|
| sequences with ≥1 placed anchor | **65 of 67** |
| anchors placed | **median 83/150 = 55.3%** |
| **decoy placement** | **0 of 201 sequence-replicates = 0.00%** |
| catalytic dyad within placed span | **60 of 67** |
| abstentions | **2**, both `QUALIFYING_DOMAIN_COVERS_NO_ANCHOR` |
| ambiguous anchors | **0** |

Per component — heterogeneity is mild, contradicting v1's 90% vs 36% split:

| component | subset | n | median % placed | abstained | dyad placed |
|---|---|---|---|---|---|
| 0 | evaluation_reference | 42 | 55.0% | 1 | 38 |
| 1 | challenge | 21 | 53.3% | 1 | 18 |
| 2 | challenge | 3 | 66.7% | 0 | 3 |
| 3 | challenge (singleton) | 1 | 70.7% | 0 | 1 |

## 3 · The order statistic is NOT evidence — stated plainly

Kendall tau is **1.0000 for all 65** evaluable sequences, and monotonicity is 65/65.

**This carries no information.** Every one of the 65 sequences has **exactly one** qualifying
domain (0 sequences have more than one), and a single `hmmsearch` domain alignment is **inherently
colinear**. Order is therefore *structurally guaranteed*, exactly as it was — for a different
reason — in v1.

The v3 predeclaration anticipated that order could not be calibrated and demoted it to a
descriptive statistic before the run. **That demotion is what makes this reportable rather than a
second tautology presented as a pass.** No order claim is made from v3.

**What this does resolve:** v2's order failure (46.3% monotone) was an **artefact of the broken
envelope-only rule**, which admitted spurious low-scoring placements that scrambled the sequence
order. It was not evidence of genuine disorder in UG5. v2 nonetheless remains `FAILED` on its own
predeclared criterion — that disposition is not reopened.

## 4 · Verdict against the predeclared v3 criteria

| criterion | result |
|---|---|
| 1 · substantial fraction with ≥1 placed anchor | **MET** — 65/67 |
| 2 · separates from the decoy distribution | **MET** — 0.00% of 201 decoy replicates, against a decoy floor calibrated at 0.00% on 817 development decoys |
| 3 · dyad within placed span in a reported majority | **MET** — 60/67 |
| 4 · abstention and ambiguity explicitly represented | **MET** — 2 abstentions, 0 ambiguous, both landed |

**v3 SUCCEEDS on its declared criteria.** Order is reported, not claimed.

## 5 · Honest limits

- **Order is not evidence here** (§3). A future gate wanting evidential order needs sequences where
  multiple qualifying domains exist, or a different formulation.
- **The development population is saturated** — real placement was 150/150 median — because the
  anchors are `ALL_PARTNERS` positions defined to align across exactly those families. It calibrates
  the **decoy floor**, which is its purpose, but not real-side difficulty.
- **55.3% median placement** means roughly **half the frozen frame does not transfer** to a typical
  UG5 protein. That is the honest headline, not the 90% v1 reported.
- One family was withheld. **No universality, and no claim about unseen lineages.**
- No biological boundary, absence, or per-residue accuracy claim.
