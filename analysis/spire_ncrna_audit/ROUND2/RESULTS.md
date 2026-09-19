# ROUND 2 — RESULTS · decision **`ROUND2_FAIL_STOP`**

Exploratory, not a gate. Round 1 frozen at `bcb6cee0c0c9aef6e6183c9fe2f6b80fc809e52e`. Population: Z6 at
`dbchar-workbench@12ea561a5565aca29eeaacbfe8863dc244838fa3`. Design `DESIGN.md` (+ Amendments 1–2); all
freezes and hashes in `tables/FREEZE.tsv`; held-out predictions hashed before any reference was revealed
(`tables/PREDICTIONS_FROZEN.tsv`, 2026-09-19T13:21Z). The held-out gate failed, so **no unresolved-group work
was run** and the 509-group scale-up stays inactive.

## 1 · Reconciliation of the 23 pilot cases (`tables/RECON_23_PROVENANCE.tsv`)

| status | n | basis |
|---|---|---|
| `RECONCILED_R1` hit outside any retained intergenic region | 12 | record's own intergenic regions; producer code copies (June producer version unrecorded → provenance uncertainty) |
| `RECONCILED_R2` call registered under a neighbouring Retron record | 4 | `rt_ncrna_calls_v1` on the same contig |
| `UNRESOLVED_R3` | 7 | production per-genome Infernal output not located (Ibex `/ibex/project/c2366/RETRONS` listed read-only: no June per-genome outputs) |

No production CM was rerun. No global search-space claim is made.

## 2 · Split (`tables/SPLIT_MANIFEST.tsv`, `SPLIT_BALANCE.tsv`)

173 rediscovery-feasible RT homolog groups, split by group before any Round-2 run: **DEV 88 (83 evaluable,
48 stability-testable, incl. all 14 Round-1-exposed groups)**, **HELDOUT 85 (81 evaluable, 40 testable)**.
Allocation: Round-1-exposed → DEV; others stratified by modal type × depth bin, hash-ranked, `r % 5 ∈ {0,2}` → DEV.
All 9 types on both sides; IV, V, IX have only 1–2 held-out groups (stated, not rebalanced).

## 3 · Frozen method and rule (`FROZEN_RULE.json`)

CMfinder 0.4.1.9, `-maxspan1 = -maxspan2 = 260`, window **W500** (−400…+100; paired distal control
−1500…−1001), motif ranking R_B (coverage × mean score among motifs with coding_frac ≤ 0.5).
A set passes if coverage ≥ 0.5, centre SD ≤ 50 nt, coding_frac ≤ 0.5, covariation not `POWERED_ABSENT`, and
(where ≥ 12 members) both frozen halves reproduce the candidate centre within 50 nt.
Covariation is supporting evidence only. No production CM hit or reference coordinate is a feature.
Selection followed Amendment 2 (J within 0.02 of the best, then most DEV IoU ≥ 0.5 rediscoveries); the purely
J-optimal tie-break had picked span 100.

## 4 · DEV calibration (real vs control)

Grid: 3 spans × 2 windows × 2 rankings × 24 thresholds, 996 CMfinder runs, 0 failures (160 runs no motif).
Chosen rule on DEV, stability included: real pass **69.1 %**, distal-control pass **0 %**, precision 93.0 %,
half-split stability 64.1 %, leave-cluster-out survival 79.5 %, abstention 30.9 %, coding artefacts 0 %.
**DEV already showed the core weakness** (`tables/DEV_CONFIG_VS_POSITIONAL_BASELINE.tsv`): at IoU ≥ 0.5 every
configuration (best 373/1,125) stayed far below a fixed positional interval −193…−24 (906/1,125).

## 5 · Untouched held-out evaluation (`tables/HELDOUT_DECISION.json`)

81 groups, 80 with a reference inside W, 1,051 in-window members.

| gate | held-out | threshold | |
|---|---|---|---|
| G1 enrichment | 343 IoU ≥ 0.5 vs 118.9 chance = **2.88×**, p = 5e-5 | ≥ 3×, p < 0.01 | **FAIL** |
| G2 discrimination (existence) | real 73.8 % vs distal control 2.5 % | Δ ≥ 0.346, ctrl ≤ 0.10 | pass |
| G3 precision | 96.7 % of 60 passing groups | ≥ 0.780 | pass |
| G4 stability | 28/37 = 75.7 % | ≥ 0.60 | pass |
| G5 abstention | 26.2 % | ≤ 0.459 | pass |
| G6 coding artefact | 0 % | ≤ 0.10 | pass |
| G7 positional prior (Amendment 2) | method 343 vs **P0 901** at IoU ≥ 0.5; both ends ±20 nt 60 vs 87 | method ≥ P0 | **FAIL** |

Decision on the pre-declared G1–G6: **`ROUND2_FAIL_STOP`**. With G7: **`ROUND2_FAIL_STOP`**.

Member metrics (held-out, in window): any overlap 724/1,051 · IoU ≥ 0.5 343 · both ends ±20 nt 60 ·
median |5′ error| 29.5 nt · median |3′ error| 37 nt · median length error −69.5 nt (motifs shorter than the ncRNA).
Supplementary non-retron RT controls: **2/4 pass** (AbiP2 2/2, AbiK 0/2): distal-window discrimination does not
fully carry over to other RT families' upstream regions.

## 6 · Stability (`tables/HELDOUT_STABILITY.tsv`)

2 disjoint halves + 1 leave-most-redundant-RT70-cluster-out per testable group. Among 37 testable rule-passing groups:
halves concordant **28**, leave-cluster-out survival **31/36**, median boundary SD across full + halves **9.7 nt (5′) /
7.0 nt (3′)**. The candidate is reproducible; it is simply not the whole ncRNA.

## 7 · Failure analysis (`tables/HELDOUT_FAILURE_ANALYSIS.tsv`, `HELDOUT_GROUP_BY_TYPE.tsv`)

| stratum | method IoU ≥ .5 | positional prior IoU ≥ .5 |
|---|---|---|
| RT divergence low (RT70/RT90 ≤ 0.34; 7 groups) | **74.5 %** | 76.4 % |
| divergence mid / high | 32.0 % / 18.3 % | 85.6 % / 89.3 % |
| ncRNA length 170–220 nt | 60.7 % | 75.0 % |
| ncRNA length ≤ 140 / > 220 nt | 24.0 % / 29.6 % | 86.3 % / 84.7 % |
| type III-A (20 groups) | **0.4 %** (groups pass 71 %) | 87.8 % |
| type XIII / I-A | 62.6 % / 76.5 % | 74.3 % / 95.6 % |
| topology upstream / overlaps RT start / overlaps adjacent CDS | 38.4 / 20.5 / 21.0 % | 86.4 / 81.3 / 89.5 % |
| deposition > 1,000 loci (7 groups) | 61.2 % | 87.6 % |

`PROPOSED:` The procedure detects a **reproducible, non-coding, conserved motif near the RT start** far better than
distal windows (existence evidence), but it localises a sub-element (~90 nt) rather than the ncRNA, and in III-A
groups a different element entirely. It never beats "the ncRNA sits at −193…−24" except in low-divergence groups,
where the two tie. Atypical topologies (`overlaps_RT_start`, `overlapping_adjacent_CDS`) were reported, not scored
as biological failures; the intragenic III-A group is in DEV.

## 8 · Decision

**`ROUND2_FAIL_STOP`.** No unresolved-group pilot, no CM seeding, no new CM. The 509-group / ~815-core-hour
scale-up remains **inactive**, and the Mestre-style stage (`POSSIBLE_NEXT_STAGE.md`) does **not** open.
