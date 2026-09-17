# DECISION — UG5 v3: placement rule derived without UG5, gate succeeds, order remains non-evidential

Date: 2026-09-16 · Track: `rt07` · Status: **executed; pending independent review**

Implements operator decisions 1 and 2 of 2026-09-16. Follows
`docs/decisions/2026-09-16_stage2_ug5_v2_closed_failed.md`, which is not reopened.

Supersede this record by a new record, never by rewriting it.

**g4b NOT BEGUN. g5 BLOCKED.**

---

## 1 · v2 disposition preserved

`FAILED on predeclared criterion 2: anchor order coherent` (31/67 = 46.3% monotone). The criterion
was **not** replaced after the fact. All v2 outputs are frozen at their existing paths; every v3
artefact carries the `ug5_v3_` prefix and overwrites nothing.

## 2 · The placement rule, and how it was derived

**Frozen rule:** an anchor is PLACED when a `hmmsearch` domain scores **>= 8.0 bits** and the anchor
lies inside that domain's **aligned** HMM span; the highest-scoring domain wins.

Derived on **817 real + 817 decoy** construction sequences - the GII reference HMM projected onto
the five other construction families, versus composition-preserving shuffles. **Neither development
script opened any UG5 file, and both assert it.** No UG5 sequence, profile, decoy, score
distribution or threshold informed the choice.

8.0 is the smallest threshold at which decoy placement is eliminated entirely (decoy max 0, 0.00%
with any placement, real-with-any-placement 99.4%). `>=10` is recorded as an equally defensible
neighbour.

**The development data independently confirmed the v2 rule was broken**: envelope-only placement
gave 21.7% of shuffled construction sequences a placement, with a maximum of all 150 anchors.

## 3 · The order statistic could not be calibrated - declared prospectively

All five candidate order metrics - Kendall tau, ordered-pair fraction, inversion fraction,
longest-monotone-subsequence fraction, binary monotonicity - are **saturated at 1.0000, median and
minimum**, across 812 development sequences, and **zero decoys retain >=3 anchors** after the score
filter. The construction data therefore **cannot discriminate among them, nor calibrate any
threshold**.

Consequently, and **before the v3 run**: Kendall tau was selected on **interpretability alone**,
declared **descriptive with no pass/fail threshold**, and binary monotonicity was **demoted to a
descriptive statistic** with the reason stated. v2's disposition was unaffected.

## 4 · v3 results

| quantity | result |
|---|---|
| sequences with >=1 placed anchor | **65 of 67** |
| anchors placed | **median 83/150 = 55.3%** |
| decoy placement | **0 of 201 sequence-replicates = 0.00%** |
| dyad within placed span | **60 of 67** |
| abstentions | **2**, both `QUALIFYING_DOMAIN_COVERS_NO_ANCHOR` |
| ambiguous anchors | **0** |
| component median placement | 55.0 / 53.3 / 66.7 / 70.7% |

**All four predeclared v3 criteria are MET. v3 SUCCEEDS.**

## 5 · The order result is still not evidence, and is reported as such

Kendall tau is 1.0000 for all 65 evaluable sequences. **This carries no information**: every one of
those sequences has **exactly one** qualifying domain, and a single `hmmsearch` domain alignment is
inherently colinear. Order is structurally guaranteed - a second tautology, arrived at differently
from v1's.

It is reported and **not claimed**, which is only possible because the predeclaration demoted it
before the run rather than after.

**What v3 does resolve:** v2's 46.3% monotone rate was an **artefact of the broken envelope-only
rule** admitting spurious low-scoring placements, not genuine disorder in UG5. v2's FAILED
disposition stands regardless.

## 6 · Supportable claims

**Supported:** a coordinate frame built entirely without UG5 information places a **median 55.3%**
of its 150 anchors in individual UG5 proteins, with the catalytic dyad inside the placed span in
**60 of 67**, against a decoy rate of **0.00% over 201 sequence-replicates** with a floor calibrated
on 817 independent development decoys.

**Not supported:** any order claim from v3 · universality · transfer to unseen lineages · biological
boundaries · per-residue accuracy. Roughly **half the frozen frame does not transfer** to a typical
UG5 protein.

## 7 · Next

Independent non-Claude-family review of the frozen v3 gate. **g4b does not begin on this session's
judgement.**
