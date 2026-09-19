# ROUND 2 — DESIGN (written before any development run; hashes in `tables/FREEZE.tsv`)

Exploratory, not a gate. Round 1 is frozen at commit `bcb6cee0c0c9aef6e6183c9fe2f6b80fc809e52e`
(`../ROUND1_FREEZE.md`). Population: Z6 at `dbchar-workbench@12ea561a5565aca29eeaacbfe8863dc244838fa3`.
Nothing here scales to the 509 groups, runs across unmatched loci, reruns production CMs, or promotes a CM.

## 0 · Question

> Can a de novo comparative procedure localise retron ncRNAs reproducibly in homolog groups, above matched
> distal controls, using evidence that stays useful when formal covariation is underpowered?

Round 2 builds and tests an **instrument on known systems**. Unresolved groups are touched only if the
held-out gate passes (§8), and then only as a very small pilot.

## 1 · Units and population

Locus / exact RT / RT homolog group (RT50) are kept separate; **the evaluation unit is the group**.
Universe: the 173 `POS_FEASIBLE` groups (≥ 6 RT90 matched-local-adequate S1–S3 loci).
Members: one locus per RT90, ≤ 20, `bp_available_upstream ≥ 1900` so each member has both its real and its
distal-control window (`scripts/r01_split_and_sets.py`). Per group, raw loci, exact RTs, RT90 and RT70 counts
are carried (`tables/SPLIT_MANIFEST.tsv`), so no strength claim rests on redundant depositions.

## 2 · Split (frozen before any Round-2 run)

`tables/SPLIT_MANIFEST.tsv`, algorithm in r01's docstring: Round-1-exposed groups → DEV; the rest stratified
by modal type × depth bin, hash-ranked, `r % 5 ∈ {0,2}` → DEV. Result: **DEV 88 groups (83 evaluable, 48
stability-testable), HELDOUT 85 (81 evaluable, 40 testable)**. All 9 types appear on both sides; IV (4/1),
V (3/1) and IX (5/2) are thin on the held-out side. Balance on divergence, deposition, ncRNA length, distance
and topology is reported in `tables/SPLIT_BALANCE.tsv`. Reference-derived summaries are sealed
(`GROUP_REFSTATS_SEALED.tsv`) and read by no discovery script.

## 3 · Blinding

Discovery scripts read only member FASTAs and member record annotation (CDS positions). Reference ncRNA
coordinates, production CM hits and `detection_model` are never features. DEV references are revealed only in
`r03_dev_calibrate.py`; HELDOUT references only in `r05_heldout_eval.py`, which refuses to run unless the held-out
predictions' hashes are recorded in `tables/PREDICTIONS_FROZEN.tsv` **and** `FROZEN_RULE.md` is hashed in `FREEZE.tsv`.

## 4 · Configuration space (DEV only; finite, declared)

| knob | values | origin |
|---|---|---|
| CMfinder span (`-maxspan1 = -maxspan2`) | **100** (Round-1 default), **170** (≈ DEV median ncRNA length 163), **260** (≈ DEV p90 254) | DEV-only length prior: p10 129 · p25 139 · p50 163 · p75 217 · p90 254 nt (1,224 references) |
| window | **W700** −600…+100 (control −1900…−1201) · **W500** −400…+100 (control −1500…−1001) | Round 1 / tighter background |
| alignment | CMfinder's own EM motif alignment (fixed). mLocARNA is retired (non-specific in both Round-1 benchmarks); Q-INS-i is not carried forward | Round 1 |
| motif ranking | **R_A** highest summed member score (Round-1 rule) · **R_B** highest coverage × mean member score among motifs passing the non-coding criterion | declared |

Interface note (disclosed): CMfinder 0.4.1.9's help lists `-M/-m`, but the parser only accepts
`-maxspan1/-maxspan2` (both default 100 — why Round-1 motifs were ≤ 100 nt). Four timing runs on one DEV group
(`0a04ed3a…`, W500/W700 × span 170/260) were made to size compute; only runtime and motif count were read
(257–434 s, 10 motifs each, ≤ 0.26 GB). No reference was joined.

## 5 · Evidence per motif (computed without references; `scripts/r02_discover.py`)

| family | feature |
|---|---|
| localisation | coverage (members with an instance / members); centre SD and median (RT-relative) |
| cross-homolog reproducibility | instances across distinct RT90 (by construction) and **half-split concordance** (§7) |
| sequence/alignment | mean and summed CMfinder member score; R-scape `avgid` of the motif alignment |
| structure | base pairs in the motif consensus structure (`SS_cons`); CaCoFold pairs |
| covariation | R-scape one-set test: significant pairs (E < 0.05), expected covarying pairs (power). State: `SUPPORTED` (≥ 2 significant) · `POWERED_ABSENT` (expected ≥ 2, 0 significant) · `UNDERPOWERED` |
| genomic context | `coding_frac` = mean share of instance nucleotides inside an annotated non-RT CDS or inside the RT ORF beyond +50 (msd/start overlap is allowed) |

## 6 · Candidate rule — family fixed now, thresholds chosen on DEV

A set passes if its ranked candidate satisfies all of:
coverage ≥ **c** · centre SD ≤ **s** · coding_frac ≤ **k** · mean member score ≥ **b** · covariation state ≠
`POWERED_ABSENT` · and, where testable, half-split concordance.

Grid (declared): c ∈ {0.5, 0.7}, s ∈ {30, 50}, k ∈ {0.3, 0.5}, b ∈ {0, 20, 40} bits, ranking ∈ {R_A, R_B},
× 6 configurations.

**Calibration objective (DEV only):** maximise J = P(real set passes **and** candidate is correct) −
P(control set passes), subject to control pass rate ≤ 0.05. "Correct" = the candidate's instances overlap the
hidden reference (≥ 1 nt) in ≥ 50 % of members with a reference. Ties → fewer / looser constraints, then shorter
runtime.

## 7 · Stability / falsification

For groups with ≥ 12 members, the two frozen halves (A = even hash ranks, B = odd) are run independently with
the chosen configuration. Concordant = in **each** half, the top-ranked motif passing the rule minus stability has
its centre within 50 nt of the full-set candidate centre. Recorded: resamples (2 disjoint halves),
concordance, boundary dispersion (SD of candidate start/end across full + halves), and survival when every
member of the most redundant RT70 cluster is removed (one leave-cluster-out rerun per testable group).

## 8 · Held-out gate (structure fixed now; numbers written to `FROZEN_RULE.md` from DEV only, before held-out runs)

`ROUND2_PASS` requires every one of:

- **G1 enrichment:** member-level rediscovery (IoU ≥ 0.5) ≥ 3× the chance expectation, one-sided permutation p < 0.01.
- **G2 discrimination:** held-out real pass rate − held-out control pass rate ≥ DEV value × 0.5, and control pass ≤ 0.10.
- **G3 precision:** among passing held-out groups, correct candidates ≥ max(0.6, DEV precision − 0.15).
- **G4 stability:** concordant in ≥ 60 % of testable passing groups.
- **G5 abstention:** held-out abstention ≤ DEV abstention + 0.15.
- **G6 coding artefact:** candidates with coding_frac > 0.5 are ≤ 10 % of held-out passes.

Failing any → `ROUND2_FAIL_STOP` (preserved; no unresolved-group work). Fewer than 20 evaluable held-out passes
or controls, or a G1 permutation that cannot reach p < 0.01 → `UNDERPOWERED/INCONCLUSIVE`.

## 9 · Metrics (held-out, reported per group and per member; references revealed after freeze)

Overlap ≥ 50 % (IoU ≥ 0.5) · any overlap · start error · end error · both ends within ±20 nt · length error ·
abstention · paired-control false-positive rate · chance localisation (same calculation as Round 1) ·
coding-overlap failures. "Region recovered" is never reported as "boundary solved".

Failure analysis by: ncRNA length, homolog depth, RT divergence (RT70/RT90), type, topology, context,
deposition size. **Topology** per member reference: `upstream` · `overlaps_RT_start` · `intragenic_RT` ·
`overlapping_adjacent_CDS` · `downstream` · `other_uncertain`. Primary calibration remains upstream-dominated;
atypical systems are reported, never counted as failures of biology.

## 10 · Supplementary controls (evaluation only)

Non-retron comparative groups (RVT-AbiK / RVT-AbiP2, as in Round 1) run with the frozen rule at the frozen
window; reported beside the distal controls; not used for tuning.

## 11 · If and only if `ROUND2_PASS`

A very small unresolved pilot (≤ 3 mixed + ≤ 3 fully unresolved groups, selected by declared hash order),
with blind discovery first and any guided expansion reported separately; seeded experimental CMs get new
provenance IDs, stay apart from the 21 production models, and are scored on held-out matched **and**
unmatched homologs, distal controls, and CDS overlap. Then stop.

## Amendment 2 — 2026-09-19, after DEV calibration, before any HELDOUT run

**Trigger (DEV only; `tables/DEV_CONFIG_VS_POSITIONAL_BASELINE.tsv`).** The J-optimal, tie-broken rule
(W500, span 100) localises the hidden ncRNA at IoU ≥ 0.5 in 157/1,125 DEV members, whereas a fixed
positional interval (−193…−24, the DEV median reference extent, no discovery at all) does so in 906/1,125
(both ends ±20 nt: 28 vs 93). Every configuration stays far below it (best: W500 span 260, 373/1,125).
CMfinder motifs stay ~90 nt even with span 260, i.e. a conserved sub-motif rather than the whole ncRNA.
Against uniform chance alone (G1), a method weaker than "ncRNAs sit just upstream" could pass.

**Changes.**
1. *Configuration selection:* among combinations with control pass ≤ 0.05 and J ≥ best J − 0.02, choose the
   one with most DEV IoU ≥ 0.5 rediscoveries (boundary accuracy is a required metric); then the declared
   looseness tie-break. Result: **W500, span 260, R_B, c 0.5, s 50, k 0.5, b 0** (DEV J 0.827, real 86.4 %,
   control 0/83, precision 95.7 %).
2. *New gate G7 (positional-prior test):* on the same held-out in-window members, IoU ≥ 0.5 rediscoveries of the
   method (abstentions count as misses) must be ≥ those of the DEV-derived fixed interval P0 = −193…−24.
   The decision is reported both on the pre-declared G1–G6 and on G1–G7, so the effect of this addition is visible.
3. *Named separately:* discrimination of real vs control windows (G2) is **existence** evidence;
   G1/G3/G7 are **localisation** evidence. They are reported as different questions.
4. *Runner change logged:* `r02_discover.py` gained loading of `NONRETRON_MEMBERS.tsv` (supplementary controls
   only); no DEV/HELDOUT retron run is affected.
