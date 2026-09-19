# Z6 de novo experiment — RESULTS (bounded benchmark; nothing scaled)

Exploratory, not a gate. Design frozen before any method ran (`DESIGN.md`, `tables/FREEZE.tsv`,
Amendment 1 logged before the benchmark run). Predictions were hashed before any reference was
joined (`tables/PREDICTIONS_FROZEN.tsv`, 2026-09-18T16:20Z). Counts are measured; readings are `PROPOSED:`.
Canonical population: Z6 at `dbchar-workbench@12ea561a5565aca29eeaacbfe8863dc244838fa3`, all five
checks reproduced (`tables/Z6_CHECKS.tsv`).

## 1 · Population and homolog groups (`tables/LOCUS_CLASSES.tsv`, `GROUPS*.tsv`)

| locus class | loci | exact RTs | RT90 |
|---|---|---|---|
| matched, local reference (T2/T3), ≥ 1 kb upstream | 187,160 | 23,563 | 10,373 |
| matched, T1 only (reference usually > 200 bp away), adequate | 133,543 | 4,027 | 2,417 |
| **unmatched, ≥ 1 kb upstream** | **241,077** | **34,070** | **19,850** |
| unmatched, 200–999 bp upstream | 18,461 | 4,702 | 2,995 |
| unmatched, < 200 bp upstream | 38,434 | 13,039 | 5,359 |

Remaining classes (matched with limited context: 12,066 loci) are in the table.
10,925 RT50 homolog groups in total. With ≥ 6 near-identical-collapsed (RT90) members:

| group class | groups | loci | unmatched-adequate loci |
|---|---|---|---|
| positive-rediscovery feasible | 173 | 279,943 | 13,066 |
| **mixed** (≥ 4 RT90 matched-local + ≥ 4 RT90 unmatched, S1/S2) | **57** | 167,814 | 12,578 |
| **de novo feasible, S1/S2** (no matched locus of any tier) | **186** | 79,396 | 74,055 |
| de novo feasible, S3 fused-RT | 93 | 24,306 | 22,630 |

Of 150,188 unmatched, adequate-context, high-confidence (S1/S2) loci: **71,757** sit in groups with
no matched member and depth ≥ 6 (the genuinely de novo stratum; types VI, XII, III-A, XI dominate);
21,858 in groups that also contain matched loci; **56,573** in groups too shallow for comparative
analysis. Deposition redundancy is extreme but concentrated: the median group has 1 locus per RT90,
yet the loci-weighted median is 782 loci per RT90, and 62 groups with > 100 loci per RT90 hold 423,442
of the 630,741 loci. Locus counts therefore say almost nothing about independent evidence.

## 2 · Bounded benchmark

24 sets (10 `POS_BLIND`, 6 `MIXED`, 5 `DENOVO_S12`, 3 `DENOVO_S3`) + 24 matched distal controls;
700-nt window −600…+100; 6–16 members, one per RT90. 144 arm-runs, 0 run failures (6 CMfinder runs
produced no motif — recorded as an outcome; the tool check shows CMfinder does find motifs in known ncRNAs).

### 2a · Rediscovering hidden known ncRNAs (`tables/Z6_REDISCOVERY_SUMMARY.tsv`, `figures/zfig1`)

| cohort · arm | hidden refs | region overlap | rediscovered IoU ≥ .5 | chance-expected | boundary ±20 nt both ends | unsuitable |
|---|---|---|---|---|---|---|
| POS · **CMfinder** top motif | 120 | **76.7 %** | **62** | 8.1 | 0 % | 8 |
| POS · mLocARNA + CaCoFold | 120 | 33.3 % | 10 | 7.6 | 0 % | 8 |
| POS · Q-INS-i + CaCoFold | 120 | 26.7 % | 6 | 0.8 | 0 % | 8 |
| MIXED · CMfinder | 48 | 72.9 % | 5 | 0.6 | 0 % | 8 |
| MIXED · mLocARNA | 48 | 50.0 % | 10 | 4.0 | 0 % | 8 |
| MIXED · Q-INS-i | 48 | 16.7 % | 0 | 0.0 | 0 % | 8 |

- **CMfinder localises hidden retron ncRNAs far above chance** (62 vs 8.1; median IoU 0.51),
  with no reference information. It does so under its default 100-nt candidate cap, so
  boundaries describe the motif (one stem-loop region), not the whole ncRNA: 0 % within ±20 nt at both ends.
- mLocARNA's covariation-supported region is at chance on positives (10 vs 7.6); 65/120 calls miss.
- The 8 "unsuitable" per cohort are one III-A group (`24c1a888…`) whose T3 references lie **inside
  the RT ORF** (+1,162…+1,424, `direction = overlapping`): atypical architecture, recorded, outside W by construction.

### 2b · Set-level candidate rule after the matched control (`tables/Z6_SET_OUTCOMES.tsv`, `figures/zfig2`, `zfig3`)

Sets passing the localisation + covariation criteria (§8.1–3), top motif/region:

| arm | benchmark windows | distal control windows |
|---|---|---|
| CMfinder | 1 / 24 | 0 / 24 |
| **mLocARNA + CaCoFold** | 13 / 24 | **16 / 24** |
| Q-INS-i + CaCoFold | 1 / 24 | 0 / 24 |

- **mLocARNA covariation is again non-specific**: it "passes" more often on distal windows than on
  real ones (replicates the first benchmark on a new population and window).
- CMfinder and Q-INS-i are specific (0/24 controls) but **almost never reach covariation with power**:
  CMfinder's top motif is `LOW_POWER` in 12/24 sets (expected covarying pairs < 1 — motif columns too
  conserved across 6–16 near-related homologs), `NOT_LOCALISED` or `NO_COVARIATION` in most others.
- Positive-control sensitivity of the full rule: **3/10 POS sets** give `CANDIDATE` in some arm
  (CMF POS_05_II-A; MLOC POS_06_XIII; QINSI POS_08_I-A). A rule that recovers 3 of 10 known ncRNA
  families cannot turn a null in unresolved groups into evidence of absence.

### 2c · Discovery cohorts (`tables/Z6_MIXED_EXPANSION.tsv`, `Z6_CM_SEED.tsv`, `Z6_CANDIDATE_SPANS.tsv`)

Two sets reached `CANDIDATE`, both in the mLocARNA arm; both were followed up and **neither is credible**:

| set | what the follow-up shows |
|---|---|
| `MIX_05_XIII` (8 matched + 8 unmatched) | Region rediscovers the matched members' TypeXIIIB ncRNA (8/8 overlap, IoU ≈ 0.42–0.51; region ~450–550 nt contains the reference). Seeded experimental CM: **30/32 held-out matched** homologs, **0/8 held-out unmatched**, 1/38 distal. In 6/8 in-set unmatched members the aligned span is 56–100 % annotated non-RT CDS. `PROPOSED:` unmatched members of this group carry a different local architecture (a gene where matched members carry the ncRNA), not a missed ncRNA. 0 expansion pairs credible. |
| `DN3_01_VII-A1` (7 unmatched, fused-RT stratum) | ~280-nt region at −560…−200; 84–100 % inside annotated CDS in 4/7 members; group too small (4 held-out homologs: 2 hits in W, 0/3 distal). Not credible. |

No `DENOVO_S12` set produced a candidate in any arm (CMfinder: 3 LOW_POWER, 2 NOT_LOCALISED;
mLocARNA: 2 SIGNAL_FAILS_CONTROL, 3 NOT_LOCALISED; Q-INS-i: 5 NOT_LOCALISED).

**`PROPOSED:` Bottom line.** Comparative de novo discovery **can localise** known retron ncRNAs without
reference information (CMfinder, 7.6× chance), so the approach is not hopeless. But in its current form
it **cannot supply evolutionary covariation evidence** for most groups (power), and the one arm that
produces covariation readily (mLocARNA) produces it equally in control windows. The bounded experiment
found **no credible new RT–ncRNA association** and **no new independent RT or ncRNA component**. The unmatched
state of these loci remains `NO_NCRNA_CALL_IN_RETAINED_WINDOW` — not evidence of absence.

## 3 · Proposed next step — a second bounded round, not a scale-up

Scaling the current rule would multiply a 3/10-sensitivity, power-limited instrument. What the data
point to, prospectively declared here for operator review:

1. **CMfinder as the discovery engine, with its candidate length raised to whole-ncRNA size**
   (`-M 250`, `-m 30`) so boundaries can be tested; mLocARNA retained only as a documented negative control arm.
2. **Evidence hierarchy that does not demand covariation where power is absent:** positional consistency
   (SD ≤ 50 nt) + structural conservation + recurrence across RT90s as the primary gate; covariation
   reported with power and required only where expected covarying pairs ≥ 2. Calibrate the
   specificity of this gate on the distal controls before it is applied to any unresolved group.
3. **More diverse sets:** up to 40 RT90 members per set (current cap 16) and, where a group is shallow,
   pooling RT50 groups of the same type label that share a CM family; diversity reported per set.
4. **Calibrate on all 173 positive-feasible groups first** (sensitivity with confidence interval), and only
   then run the 57 mixed and 186 + 93 de novo groups.

## 4 · Proposed scale-up population and compute (for the operator decision; nothing launched)

| population | groups | sets (incl. distal control) | notes |
|---|---|---|---|
| calibration: positive-feasible | 173 | 346 | hidden references; sensitivity per type |
| mixed (family expansion) | 57 | 114 | status hidden; follow-up by seeded CM on held-out homologs |
| de novo S1/S2 | 186 | 372 | primary genuinely de novo stratum |
| de novo S3 (fused-RT) | 93 | 186 | separate stratum; XII flagged (PADLOC rule prohibits an ncRNA) |
| **total** | **509** | **1,018** | never all 297,972 unmatched loci; ≤ 40 loci per set, one per RT90 |

Measured cost (16 members × 700 nt, 4 threads): CMfinder 115–118 s; Q-INS-i + CaCoFold 164–193 s;
mLocARNA + CaCoFold 321–468 s; this benchmark's 48 sets × 3 arms took **57 min wall on 12 workers**.
CM seeding is the expensive step: **~33 min per candidate on 8 cores**, dominated by `cmcalibrate`.

Estimate for the table above with CMfinder + Q-INS-i only, sets of up to 40 members (≈ 2.5× the per-set cost):
1,018 sets × ~12 min × 4 threads ≈ **815 core-h** (≈ 17 h on 48 local cores; or an Ibex array of 1,018 × 4-CPU
jobs, 30 min wall each, ≈ 1 GB RAM, ≈ 3 GB output). Seeding adds ≈ 4.4 core-h per candidate. Caching: one directory per set,
skip-if-output-exists (as here); a `DONE` sidecar with input/output hashes before any Ibex submission.
Success criteria to fix before launch: calibration sensitivity with a lower 95 % bound above an agreed floor,
control false-candidate rate ≤ 5 %, and for any de novo candidate: seeded-CM hit rate on held-out homologs
significantly above distal, at a consistent RT-relative position, in non-coding sequence.

## Files

`DESIGN.md` · `RESULTS.md` · `tables/` (Z6 checks, locus classes, groups, mixed/de novo group lists, sets,
members, freeze and prediction hashes, set outcomes, member evaluation, rediscovery summary, mixed
expansion, candidate spans, CM seeding) · `figures/` (+ `figures/data/`) · `scripts/z01–z06`.
Scratch: `ARIS_OUTPUT/spire_ncrna_audit/z6/` (sets 86 MB, seeds, loci parquet).
