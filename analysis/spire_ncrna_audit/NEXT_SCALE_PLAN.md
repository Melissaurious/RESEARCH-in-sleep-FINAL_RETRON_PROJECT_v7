# NEXT SCALE PLAN — proposal only; nothing here has been run

> **⚠️ Superseded in part (2026-09-18, after the Z6 handover).** Population definitions below come from a
> locally reconstructed physical-locus table; the canonical population is now Z6 (`dbchar-workbench` @ `12ea561`).
> The "annotation-independent Infernal rescan" recommendation and any "global search-space bug" reading are
> **withdrawn**: see `RECONCILIATION_23.md` (12 R1 / 4 R2 / 7 R3; no global claim) and `Z6_DENOVO/`.
> The negative result on the released SPIRE rule stands.


**Operator decision required before any of this executes.** Recommendation first, then the
numbers the operator asked for, then the exact runs being proposed.

## 0 · Recommendation

`PROPOSED:` **Do not scale the SPIRE/Toro de novo method (Arm A) across the catalogue.**
The bounded benchmark does not justify interpreting its output in CM-negative systems:

1. Under SPIRE's own criterion it abstains on 354/377 positives and rediscovers 12 — exactly the
   12.2 expected by chance for intervals of the same length (`tables/BENCHMARK_SUMMARY.tsv`).
2. Its covariation signal is not specific. Sets signalled (any covarying pair) in 74 % of
   positive sets, **88 % of distal windows**, 75 % of non-retron RT windows and 3/3 group II
   intron sets (`tables/EVAL_set_level.tsv`). On mLocARNA alignments of divergent windows
   (median identity 25–51 %), covariation appears whether or not a retron ncRNA is present.
3. A fixed positional guess (P0, −166…−32) rediscovers 232/377 at IoU ≥ 0.5, against 152 for
   the best comparative rule.

`PROPOSED:` **The recoverable pairs the pilot found come from annotation, not from de novo
structure.** In the pilot, **23 of 219 CM-negative systems** carry a padlocdb.cm hit at
E ≤ 1e-5 inside the 300-nt upstream window. The corpus CM route never searched there: it
reports best-per-*intergenic-region* hits only, and in those loci a small annotated ORF
(e.g. −164…+3) covers the msr/msd region. The same situation (≥ 60 of the 120 nt 5′ of the RT
covered by a non-RT CDS) holds for 38 % of S1 and 40 % of S2 CM-negative loci, against 0.6 % of
S1 CM-positive loci (`tables/SCALE_upstream_cds_cover.tsv`).

So the next step with evidence behind it is **Run 1** (annotation-independent Infernal rescan).
It is cheap, fully local, and has a built-in positive control. It adds **depth, not
independence**: in the pilot, all 23 rescues fell in RT50 components that already contain
CM-positive systems (0 new RT components; `PAIR_POPULATION_IMPACT.tsv`).

**Run 2** (de novo, restricted, B-seq arm) is justified only as a separate, small, controlled
experiment. It targets the types with **no retron CM at all** (VI, XI, XII, VII-A1, VIII, X —
roughly 58,000 CM-negative loci, `tables/M3_type_coverage.tsv`), which are the only place new
independent components can come from, and it has a specificity gate. It is not a catalogue run.

## 1 · Population for any scale-up (all eligible A + B; from `tables/SCALE_*.tsv`)

| quantity | value |
|---|---|
| total retron RT systems (physical loci, ≥ 1 first-copy `Retron` record) | **563,701** |
| — with an existing ncRNA placement (A, any tier) | 298,534 (T3 161,154 · T2 4,524 · T1 131,930 · non-canonical 926) |
| — without a current ncRNA call (B) | **265,167** |
| suitable for a 300-nt upstream window (`suitability = OK`) | 514,867 |
| unsuitable: upstream truncated at a contig edge | 46,887 |
| unsuitable: RT coordinates invalid | 1,947 |
| excluded from the discovery cohort: PADLOC rule consumes the ncRNA (S4) | 36,169 loci (672 of them B + suitable) |
| exact RTs in the master table | 78,287 → 11,860 RT50 components, 36,866 RT90 clusters |

A_T1 (131,930 loci) is its own class: 114,413 have a same-strand upstream CM call more than
200 bp away, and in 99.4 % of S1 loci of this class (A_T1 + non-canonical) an annotated CDS
covers the proximal upstream. Their
existing reference lies outside the 300-nt window, so they cannot serve as positives for this
method (reported, not dropped).

### Homolog sets suitable for comparative analysis (≥ 5 distinct RT90 members per RT50 component; upper bound)

| cohort | stratum | RT50 components | eligible sets | loci in eligible sets | loci with < 5 homologs | windows (≤ 40 per set) |
|---|---|---|---|---|---|---|
| A local (T2/T3) | S1 | 351 | 98 | 50,745 | 8,960 | 1,588 |
| A local | S2 | 423 | 79 | 8,104 | 1,868 | 1,066 |
| A local | S3 | 243 | 61 | 47,547 | 1,588 | 933 |
| A local | S5 | 1,051 | 108 | 8,058 | 3,359 | 1,079 |
| B | S1 | 877 | 154 | 57,289 | 11,803 | 1,798 |
| B | S2 | 1,903 | 229 | 33,736 | 31,015 | 2,456 |
| B | S3 | 1,208 | 141 | 24,053 | 6,448 | 1,946 |
| B | S5 | 4,786 | 292 | 44,021 | 14,259 | 3,144 |

About 1,160 eligible sets and ~14,000 windows over A-local + B (excluding S4 and A_T1).
Homolog depth is the binding constraint, not compute: after RT90 de-duplication, **63,525 suitable B
loci (S1–S3, S5) sit in components with fewer than 5 distinct homologs** (`C_INSUFFICIENT_HOMOLOGS`).

## 2 · Run 1 — annotation-independent Infernal rescan (recommended; needs operator approval)

| | |
|---|---|
| question | how many B systems carry a padlocdb.cm hit inside a fixed RT-anchored window that the intergenic-only route never searched? |
| window | RT-relative **−400…+100** on the RT strand (declared now: covers the 300-nt SPIRE window plus msr/msd that overlap the RT start codon) |
| systems | all `suitability = OK` loci: B 223,296 + A-local 164,871 (A as the positive control); de-duplicated by exact window sequence before search |
| grouping | none (per-sequence method) |
| command | `cmsearch --cpu 8 -E 10 --tblout <shard>.tbl -o /dev/null padlocdb.cm <shard>.fa` per 2,000-window shard; call = best + strand hit, E ≤ 1e-5 (the corpus threshold, T3) |
| environment | `/home/borg/miniconda3/envs/retron_tradicional` (Infernal 1.1.5); padlocdb.cm sha256 `09449bdf…` |
| compute | measured 57 s / 219 windows on 8 cores ≈ 2 core-s per window → ≤ 388,000 windows ≈ **215 core-h upper bound before de-duplication**; ~4.5 h on 48 local cores; RAM < 1 GB per process. Local; no Ibex needed |
| output | ≤ 60 MB of tblout + one parquet per window (hash → hits) |
| caching / restart | shards keyed by the sha256 of their FASTA; a `DONE` sidecar with input and output hashes; reruns skip DONE shards |
| positive control (must pass first) | on A-local loci the rescan must return the existing call at the same model and ≥ 50 % reciprocal overlap for **≥ 95 %** of A_T3 references inside the window; otherwise stop |
| success | rescued B count reported per evidence stratum and type, with RT50/ncRNA component counts; nothing enters the pair dataset without a new operator decision |
| failure | positive control < 95 %, or rescues concentrated in S5 only (would indicate CM promiscuity on sequence-only calls) |

## 3 · Run 2 — de novo discovery restricted to CM-less types (conditional)

Only if the operator wants de novo evidence where no CM exists. Arm **B-seq** (MAFFT L-INS-i →
CaCoFold) is proposed over Arm A: it was the only arm whose signal rate separated positives
(33 % of sets) from distal (8 %), intragenic (19 %) and non-retron (0 %) controls, and its
calls were 1.7× above chance at IoU ≥ 0.5 (116 vs 68.0 expected). Its weaknesses are low
sensitivity (abstains on 207/377 positives) and a group II intron set it still signals on.

| | |
|---|---|
| systems | B loci of types VI, XI, XII, VII-A1, VIII, X with `suitability = OK`, S1–S3 only. XII is reported as a separate stratum: PADLOC's `retron_XII` rule *prohibits* an ncRNA, so a PADLOC-labelled XII system is ncRNA-less by the tool's definition, and a candidate there tests that definition rather than filling a CM gap |
| grouping | RT50 component; one locus per RT90; 5–40 members (unchanged rules) |
| mandatory per-set controls | the same members' distal (−1500…−1201) and intragenic (+300…+599) windows through the identical pipeline; a set counts only if its upstream window signals and **both** controls do not |
| candidate rule (declared before the run) | covarying helix supported in B-seq **and** B-struct; < 50 % CDS overlap; RT-relative position SD < 30 nt across calling members; ≥ 2 covarying pairs |
| positive control | cannot be in-type (no CMs exist). Proxy: rerun the 27 POS sets under the new set-level rule and report the recovery achieved |
| compute | ≈ 25 s mLocARNA + < 30 s MAFFT/R-scape per set × 3 windows per set; for ≤ 300 sets ≈ 1–2 h on 48 local cores; ≈ 1.3 MB per set |
| success / failure | report candidates and their independent RT/ncRNA components. If the per-set control gate removes > 90 % of signals, stop: the method is not separable from background on these data |

## 4 · Not proposed

- Arm A (SPIRE verbatim) at scale — see §0.
- Any catalogue-wide run outside the retron population (all RT families).
- Training the boundary detector or the embedding model on any candidate from this audit.
- Any change to CM annotations or the canonical pair dataset.
