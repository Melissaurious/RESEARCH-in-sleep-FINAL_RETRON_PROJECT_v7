# UG5 gate v3 — PREDECLARATION

Written **before** any UG5 v3 evaluation was run. Every rule below was derived from
**construction-family data only**; UG5 was not opened by either development script, and both assert
that.

Supersedes nothing in v2: v2 is closed as `FAILED on predeclared criterion 2`
(`docs/decisions/2026-09-16_stage2_ug5_v2_closed_failed.md`) and its outputs are frozen. All v3
artefacts carry the `ug5_v3_` prefix and overwrite nothing.

---

## 1 · The v3 question — unchanged

> Can a shared RT coordinate framework built entirely without UG5 information place homologous
> anchors in individual UG5 proteins with evidence distinguishable from decoys, and with coherent
> relative ordering?

Not a test of biological boundary accuracy. No universality claim.

## 2 · The frozen placement rule

**An anchor is PLACED in a sequence when a `hmmsearch` domain of the frozen reference HMM satisfies
both:**

1. **domain bit score ≥ 8.0**, and
2. the anchor's reference-HMM coordinate lies within the domain's **aligned** HMM span
   (`hmm from`–`hmm to`), **not** the looser envelope.

Where several qualifying domains cover one anchor, the **highest-scoring** domain supplies the
placement.

### How the threshold was derived — construction data only

`tables/placement_rule_development.tsv` and `placement_rule_sensitivity.tsv`. Development
population: the **GII reference HMM projected onto the five other construction families**
(`Retrons`, `DGRs`, `CRISPR`, `UG3`, `AbiA`) — a genuinely cross-family projection, exactly as UG5
would be — versus composition-preserving shuffles of the same sequences. **817 real + 817 decoy.**

| rule | real median | decoy max | decoy % with any placement |
|---|---|---|---|
| **envelope only (the v2 rule)** | 150 | **150** | **21.7%** |
| score ≥ 0 | 150 | 39 | 1.71% |
| score ≥ 5 | 150 | 9 | 0.12% |
| **score ≥ 8** | 150 | **0** | **0.00%** |
| score ≥ 10 | 150 | 0 | 0.00% |

**8.0 is the smallest threshold at which decoy placement is eliminated entirely on the development
population** — the least aggressive filter achieving the stated goal. `≥10` behaves identically
(real-with-any-placement 99.3% vs 99.4%) and is recorded as an equally defensible neighbour.

This measurement **independently confirms, on non-UG5 data, that the v2 envelope-only rule was
broken**: 21.7% of shuffled construction sequences received placements, with a maximum of all 150
anchors.

### Stated limitation of the development population

Real placement is **saturated** (median and max both 150/150). The anchors are `ALL_PARTNERS`
positions defined to align across exactly these families, so the development population is **easy by
construction**. It therefore calibrates the **decoy floor** — which is the threshold's purpose — but
it **cannot** tell us what a hard real case looks like. That is precisely what UG5 tests, and it is
why no real-side threshold is set.

## 3 · Abstention rule

A sequence with **no qualifying domain**, or with qualifying domains covering **no anchor**, is
recorded `ABSTAIN` with its reason. Abstention is an explicit reported state, never a silent zero.

## 4 · Ambiguity rule

An anchor is **AMBIGUOUS** when **two or more qualifying domains** (each score ≥ 8.0) cover it and
their implied sequence positions differ by **more than 10 residues**. This is non-tautological: a
per-sequence search can return multiple competing domains, unlike the one-to-one aggregate
profile-profile map that made v2's v1 predecessor vacuous.

## 5 · Order statistic — and an honest constraint

`tables/order_metric_development.tsv`. Five candidates — Kendall tau, ordered-pair fraction,
inversion fraction, longest-monotone-subsequence fraction, binary monotonicity — were evaluated on
812 real development sequences.

**Every one is saturated at 1.0000 — median *and* minimum.** Binary monotonicity holds for **100%**
of development sequences. **Zero** decoy sequences retain ≥3 anchors after the score filter, so
there is no decoy order distribution at all.

**Consequence, declared prospectively:** the construction-family data **cannot** discriminate among
these metrics, and **cannot** calibrate any order threshold. Selection on "behaviour on
development data" yields no signal. Therefore:

- **Primary order statistic: Kendall tau**, selected on **interpretability alone** — standard,
  bounded in [−1, 1], directly readable as the rescaled fraction of correctly ordered anchor pairs.
  The basis for the choice is stated rather than implied.
- **Kendall tau is reported DESCRIPTIVELY, with its full distribution. No pass/fail threshold is
  set on it**, because no non-UG5 evidence supports one and inventing a number now would be the
  outcome-driven tuning this cycle exists to eliminate.
- **Binary monotonicity is DEMOTED to a descriptive statistic for v3.** Prospective justification:
  it carries zero information on the development population (100% monotone), so its brittleness on
  divergent proteins is unmeasurable from non-UG5 data; retaining it as a hard pass/fail would
  import an untested assumption. **This does not alter v2, which remains FAILED on it.**

## 6 · v3 success and failure criteria

Because order cannot be thresholded from available evidence, the v3 gate decision rests on the
quantities that *can* be calibrated:

**v3 SUCCEEDS if all of:**
1. a substantial fraction of UG5 sequences receive ≥1 placed anchor under the frozen rule;
2. UG5 placement **separates from the decoy distribution** — the decoy floor is calibrated at
   0.00% on 817 development decoys, so any material UG5 placement is above it;
3. the catalytic dyad falls within the placed anchor span in a reported majority of dyad-bearing
   sequences;
4. abstention and ambiguity are explicitly represented.

**v3 FAILS if:** UG5 placement is indistinguishable from the decoy floor, or the rule cannot be
applied.

**v3 reports, without pass/fail:** the Kendall tau distribution, monotonicity rate, per-component
heterogeneity, and coordinate stability.

## 7 · Decoy design (repair 7)

Three composition-preserving shuffle replicates, seeds `20260916 + rep`. **Every decoy evaluation
is retained per sequence and per replicate** — sequence id, replicate, anchor id, score, placement
state, ambiguity, mapped coordinate. **No file is reused between replicates**, which was the v2
defect. A fully inspectable decoy table is landed.

## 8 · Frozen inputs, software, parameters

- reference HMM: `rt07_g4a_repaired/work/GII.deriv.hmm`; construction profiles for the six families
- frozen anchors: 150, in 11 contiguous runs, GII consensus coordinates, span 107–317 —
  **already landed in full** in `tables/ug5_frozen_anchor_coordinates.tsv`
- `hmmsearch --max -E 10 --domtblout`; `mafft --localpair --maxiterate 1000 --thread 1`;
  `hhmake -M 50`; `mmseqs easy-search -s 7.5`
- link rule for the UG5 split: identity ≥ 0.30 **and** min(coverage) ≥ 0.50
- placement: score ≥ 8.0, aligned HMM span; ambiguity window 10 residues; seed 20260916

## 9 · Provenance

UG5 remains excluded from all construction. The content-level provenance audit is re-run and
**fails closed** on any UG5 id or UG5 sequence appearing in a construction input.

## 10 · Stop condition

If the frozen rule cannot be applied, or if applying it reveals a defect in the rule itself, work
stops and returns to the operator rather than adjusting the rule against UG5 data.
