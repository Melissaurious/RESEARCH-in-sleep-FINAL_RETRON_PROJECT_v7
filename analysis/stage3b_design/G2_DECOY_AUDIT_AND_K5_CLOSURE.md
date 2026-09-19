# Stage 3B — bounded decoy-sufficiency audit; K5 terminally fired; Stage 3B closed at PARTIAL

**Tier B was not opened.** No threshold, candidate rule, score, truth label, resolution criterion or
tier assignment was altered. Nothing in this audit used Tier B structures, labels, outcomes or
candidate distributions.

---

## Q1 · Were admissible Tier A decoys omitted through implementation, deduplication, chain-selection
or bookkeeping error?

**No omission was found. One over-count was found, and it runs against K5, not for it.**

* **Insertion codes / dict-key collisions:** 0 aspartates in Tier A carry an insertion code, so the
  `{seqid: carboxylate}` keying loses nothing.
* **Alternative conformations:** removed before enumeration, consistently, in every path.
* **Unmodelled carboxylates:** aspartates without OD1/OD2 are excluded because they have no
  coordinates to measure — required by the detector's own precondition, not an omission.
* **Glutamate:** the detector and the truth labels are aspartate-only by frozen definition.
* **NOT_SCOREABLE chains:** the 4 chains above 3.5 Å are correctly excluded along with their
  candidates.

**The over-count.** The figure of **36** reported at the g2 freeze was computed over *all* eligible
Tier A chains, so on the 11 chains that carry **no** catalytic truth it counted **every** admissible
candidate as a decoy. That is exactly the rule this audit forbids — "not currently labelled truth" is
not evidence of being a negative. Applying the operator's definition, decoys may be counted only on
chains that have truth:

| count | value |
|---|---:|
| as reported at the g2 freeze (all eligible chains) | 36 |
| **under the operator's definition (truth-bearing chains only)** | **19** |
| difference: candidates on 11 no-truth chains | 17 |

**The corrected Tier A decoy pool is 19, not 36.** K5 fires more decisively than the ruling assumed.

### Q1(b) · NCS and oligomer copies

The register keeps one representative chain per entity. The additional copies are real coordinates:
29 further chains across 7 truth-bearing entries, carrying 18 further admissible non-truth pairs
(`1RTD` C; `8BGJ` C; `9Z6Y` B–F and I–M; `9Z6Z` I–M; `24NC` B–F and `9YFD` B–H contribute none).

They are **crystallographic/NCS copies of proteins already in the pool**. Counting them would be
pseudo-replication — more observations of the same negatives, not additional independent negatives.
They are quantified here and **not** added to the legitimate pool.

---

## Q2 · Do predeclared external controls supply legitimate detector-space decoys?

Only the controls named in `CONTROLS.tsv` rows **C3** (motif-positive non-RT proteins) and **C3b**
(HIV-1 RT p51) were used. Each is independently known not to be an RT polymerase catalytic pair on
grounds other than absent annotation. Evaluated under the **unchanged** frozen rule
(SEP 75–115, D_MAX 6.0 Å, RES_MAX 3.5 Å).

| structure / chain | candidate Asp | admissible? why | why independently NOT the target RT-polymerase pair | predeclared control | why previously omitted |
|---|---|---|---|---|---|
| `1R7M_A` 2.25 Å | D44–D145 (3.16 Å), D44–D144 (3.98 Å) | sep 101/100, dist ≤6.0, res ≤3.5 | I-SceI is a LAGLIDADG **homing endonuclease**, not a reverse transcriptase; it has no polymerase active site | **C3** | control inventory was never registered as chains in the 62-chain RT register |
| `3OOL_A` 2.30 Å | D44–D145 (3.03), D44–D144 (4.38) | same | same protein P03882 | **C3** | same |
| `3OOR_A` 2.50 Å | D44–D145 (3.00), D44–D144 (4.41) | same | same protein P03882 | **C3** | same |
| `5A0M_A` 2.90 Å | D344–D445 (2.81), D344–D444 (3.48) | same | same protein P03882, +300 numbering offset | **C3** | same |
| `5A0M_B` 2.90 Å | D344–D445 (2.93), D344–D444 (4.23) | same | same protein P03882 | **C3** | same |
| `3UVF_A` 3.00 Å | — | **no admissible pair** | I-HjeMI endonuclease | C3 | n/a |
| `9N69_A` 3.13 Å | — | **no admissible pair** | AAA-family ATPase | C3 | n/a |
| `9N69_F` 3.13 Å | — | **no admissible pair** | TIGR02646 protein | C3 | n/a |
| `1RTD_B` 3.20 Å | D110–D186 (3.52), D110–D185 (4.63) | sep 76/75, dist ≤6.0 | **p51** — the same polypeptide as p66 in a conformation with no functional polymerase site; the deposition's own `_struct_biol.details` names p66 and p51 as distinct subunits, and only p66 carries the dNTP and Mg sites | **C3b** | the register holds one chain per entity; p51 is a separate entity and was catalogued as a control, never as a scored chain |

**12 admissible pairs across 9 eligible control chains — but only 2 unique proteins contribute.**
I-SceI's 10 pairs are 5 near-identical copies of the same 2 pairs; de-duplicated to unique protein the
controls yield **4** independent decoy pairs.

The RNase H pair `D443–D549` (sep 106, 3.27 Å) in `1RTD_A` and the TOPRIM pairs in `9I2G_B`/`9S1F_B`
were checked: the RNase H pair is **already inside** the 19 (it is an admissible non-truth candidate
on a truth-bearing chain), and the TOPRIM pairs are `|i−j| = 2`, far below `SEP_MIN`, so not
admissible. No double counting.

---

## Q3 · Can the legitimate pool reach 60?

| pool | count | ≥ 60? |
|---|---:|---|
| (i) strict Tier A decoys, truth-bearing chains only | **19** | no |
| (ii) predeclared control decoys, de-duplicated to unique protein | **4** | — |
| **(i) + (ii) — the legitimate pool** | **23** | **NO** |
| (i) + control decoys counted per chain copy | 31 | no |
| the above **plus** all 18 pseudo-replicate NCS decoys — the most permissive count available | **49** | **NO** |

**No admissible construction reaches 60**, including one that deliberately over-counts by admitting
pseudo-replicates. The shortfall is structural, not clerical: the frozen sequence-separation window of
75–115 residues is narrow, so a typical RT chain contributes 1–4 admissible candidates in total.

---

## K5 — recorded as TERMINALLY FIRED

> *K5 — the within-protein decoy pool falls below 60 pairs after eligibility filtering → stop;
> specificity cannot be measured on this set.*

Legitimate pool **23** (or 31 per chain copy; 49 at maximum permissiveness) against a threshold of 60.
**Stage 3B is closed at the PARTIAL calibration stage under `LAUNCHER_03B`. Tier B is not opened.**

The g1 and g2 bundles remain valid, reproducible and unaltered. What they establish is calibration
evidence, not a validated detector.

---

## The strongest statement the evidence now supports

> The frozen motif-blind structural detector localises the independently defined RT-polymerase
> catalytic site consistently across Tier-A calibration structures — **19/19 diagnostic site-level
> overlap** — but **exact catalytic-residue recovery is 13/19 (0.684)**, and the predeclared
> false-positive / decoy-sufficiency criterion **is not met**.

The 19/19 figure is **diagnostic and post hoc**. It is not a success criterion, it set no threshold,
and it may not be substituted for the declared residue-exact metric.

**A correction to the characterisation of the misses.** The earlier phrasing "all six misses are
adjacent-aspartate confusions" is **not exactly supported**. Measured:

| characterisation | supported |
|---|---:|
| predicted pair contains ≥1 independently evidenced catalytic residue of the same site | **6/6** |
| off-target residue is adjacent (≤2 residues) to a truth residue | **4/6** (`1RTD_A` D186, `8SXT_A` D703, `8UB7_A` D216, `9Z6Y_A` D198) |
| off-target residue is itself truth in a replicate of the same protein | 1/6 (`9Z6Z_H` D192 — truth in `9Z6Y_H`) |
| neither adjacent nor replicate-truth | 1/6 (`9NL3_A` D556) |

**Operator ruling, 2026-09-18 — this four-part breakdown is the only supported characterisation of
the misses, and the phrase "all six exact-residue misses are adjacent-Asp confusions" may not be
used:** 6/6 predictions retain at least one independently evidenced catalytic residue; 4/6 have an
off-target Asp within two residues of a truth residue; 1/6 uses a residue independently supported in
a replicate of the same protein; 1/6 meets neither of those narrower descriptions.

---

## Preserved verbatim from the g2 freeze

* residue-exact: **13 HIT / 6 MISS / 0 ABSTAIN** among 19 truth-bearing Tier A chains = **0.684**
* **6** AMBIGUOUS predictions · **4** NOT_SCOREABLE (3.5 Å criterion) · **0** truth-bearing abstentions
* the 2 abstentions in Tier A are both on no-truth chains (`7KFT_C`, `9K6G_A`), cause "no admissible
  candidate"
* cross-state diagnostic: `9Z6Z_A`, which carries no truth of its own, predicts `[115, 197]` —
  exactly the independently evidenced catalytic pair of `9Z6Y_A`, the same protein in the elongating
  state
* all Tier-A-only sensitivity results in `G2_SENSITIVITY_TIERA.tsv` stand unchanged: leave-one-cluster-out
  1.0 (×6), 0.667 (×2), 0.0 (×3, each n=1); `D_MAX` 5.0–7.0 → 0.684–0.722; `SEP` stable to [65,125],
  0.632 at [55,135]; resolution bands 1.0 / 0.6 / 0.6; excluding transferred truth 0.684 unchanged;
  one chain per replicate group 0.833

---

## What a future Tier-B test requires

A **new, explicitly approved validation design** — not an amendment to this launcher made after seeing
Tier-A calibration. Any such design has to solve the decoy-sufficiency problem at its root, which on
this evidence means enlarging the population or widening the candidate space by a rule declared in
advance, not adjusting the present one. Tier B remains unopened and uninspected.
