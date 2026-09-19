# SPIRE/Toro 2026 ncRNA-discovery audit + bounded benchmark

> **⚠️ Superseded in part (2026-09-18, after the Z6 handover).** Population definitions below come from a
> locally reconstructed physical-locus table; the canonical population is now Z6 (`dbchar-workbench` @ `12ea561`).
> The "annotation-independent Infernal rescan" recommendation and any "global search-space bug" reading are
> **withdrawn**: see `RECONCILIATION_23.md` (12 R1 / 4 R2 / 7 R3; no global claim) and `Z6_DENOVO/`.
> The negative result on the released SPIRE rule stands.
> **Closed (2026-09-19):** Round 2 `ROUND2_FAIL_STOP` (`ROUND2/RESULTS.md`); post-mortem label
> `RETRON_ENRICHED_NCRNA_SUBMOTIF` (`POSTMORTEM/RESULTS.md`). SPIRE de novo discovery branch closed.
> **Earlier results:** `Z6_DENOVO/RESULTS.md` (Z6 population, homolog groups, CMfinder / mLocARNA / Q-INS-i
> benchmark with distal controls and CM seeding; no credible new RT–ncRNA association; second bounded round proposed).


> **Exploratory analysis, not a governed gate** (same status as `analysis/dbchar_rt_ncrna_workbench/`).
> No `MANIFEST.tsv`, no independent review, no operator acceptance. Every number is exploratory.
> Nothing here changes CM annotations, the canonical RT–ncRNA pair dataset, or embeddings.
> Computational candidates are **not** validated retron ncRNAs. Interpretations are `PROPOSED:` (WA-A.4).
> Branch `worktree-spire-ncrna`, 2026-09-18.

## Question

Given RT systems already identified by our pipeline, can comparative sequence/structure analysis
(the Toro/SPIRE mLocARNA + R-scape strategy, plus a CaCoFold arm) recover retron ncRNAs
independently of the existing CM call — first where the ncRNA is known, then where the CM route
has no call?

## Answer in five lines

1. **The released package is not runnable from raw inputs.** The ncRNA step (`07`) is a thin wrapper
   over a hand-assembled FASTA. It assigns no boundary and has a parser bug that always prints
   0 significant pairs. It runs verbatim after two environment shims (`WORKFLOW_RECONSTRUCTION.md`).
2. **On 377 blinded CM-positive systems, SPIRE's own rule abstains on 94 % and performs at chance**
   (12 rediscovered; 12.2 expected for random intervals of the same length).
3. **Covariation signal on mLocARNA alignments is not specific:** it appears in 88 % of distal
   windows, 75 % of non-retron RT windows and 3/3 group II intron sets, against 74 % of true
   positive sets. Only the MAFFT + CaCoFold arm separates positives from controls, and it has low
   sensitivity.
4. **In the CM-negative pilot, no credible de novo-only ncRNA was found.** What *was* found: 23/219
   "CM-negative" systems carry a strong padlocdb.cm hit (E ≤ 1e-5) the corpus route never
   searched. It reports intergenic hits only, and a small annotated ORF covers the msr/msd region.
   That affects 38–40 % of high-confidence CM-negative loci.
5. **Recommendation:** do not scale SPIRE. Run an annotation-independent Infernal rescan first
   (`NEXT_SCALE_PLAN.md`, Run 1). It adds depth, not independent components (0 new RT components
   in the pilot). De novo discovery only for CM-less types, behind a control gate (Run 2).

## Population (from our registered data — SPIRE defines nothing)

`scripts/s01_master_table.py` → `ARIS_OUTPUT/spire_ncrna_audit/master/master_rt_system.parquet`
(563,701 physical loci, sha256 `c806d55c…`; summaries `tables/M0–M3`). Canonical inputs are read
from the main checkout's `data/derived/` (external project asset, read-only; this worktree's
`data/` holds only the README) and window DNA from the pinned raw corpus by byte offset.

| field | values (physical loci) |
|---|---|
| `nc_status` | A_T3 161,154 · A_T2 4,524 · A_T1 131,930 · A_NONCANON 926 · **B_NO_CM_CALL 265,167** |
| `evidence_stratum` | S1 system context, 2 tools 251,697 · S2 1 tool 86,186 · S3 fused-RT rule 85,048 · S4 PADLOC rule needs the ncRNA 36,169 · S5 sequence only 104,601 |
| `suitability` | OK 514,867 · C_CONTIG_EDGE_TRUNCATED_UPSTREAM 46,887 · C_RT_COORDINATES_INVALID 1,947 |

S4 is excluded from both cohorts: PADLOC's `Ec107-like`/`outgroup` rules require the ncRNA, so
they are not independent of the CM route. DefenseFinder retron models never use an ncRNA.
⚠️ Found after the freeze, from the rule files: PADLOC `retron_XII` lists `ncRNA` as a
**prohibited** gene. For PADLOC-labelled XII systems, "no ncRNA" is part of the tool's
definition, not a CM miss. The strata are unchanged (XII is an RT-only rule in both tools), but
CM-negative XII loci (21,866) must not be read as "missed ncRNAs". The one XII de novo
candidate sits in exactly this class.

## Benchmark (design frozen before outcomes — `BENCHMARK_DESIGN.md`, `tables/FREEZE.tsv`)

Sets: RT50 protein clusters, one locus per RT90, 5–40 members, 300 nt 5′ of the RT start codon.
Reference coordinates were joined only after predictions were hashed (`tables/PREDICTIONS_FROZEN.tsv`).
Two amendments, each logged before the outcome it concerns: a sensitivity rule (any covarying
pair), and a group II intron hard-negative control.

### Positive recovery — 27 sets, 377 CM-positive loci, 9 retron types (`BENCHMARK_RESULTS.tsv`, `tables/BENCHMARK_SUMMARY.tsv`)

| arm · rule | rediscovered (IoU ≥ .5) | altered boundary | not rediscovered | abstention | unsuitable | chance-expected rediscovered | boundary ±20 nt |
|---|---|---|---|---|---|---|---|
| A SPIRE · SPIRE rule | 12 | 10 | 0 | 354 | 1 | 12.2 | 1.6 % |
| A SPIRE · any covarying pair | 152 | 127 | 40 | 57 | 1 | 126.4 | 17.5 % |
| B-struct CaCoFold · SPIRE rule | 19 | 30 | 8 | 319 | 1 | 23.5 | 1.6 % |
| B-struct CaCoFold · any cov. pair | 153 | 126 | 40 | 57 | 1 | 126.4 | 17.5 % |
| B-seq MAFFT+CaCoFold · SPIRE rule | 0 | 0 | 5 | 371 | 1 | 1.3 | 0 % |
| B-seq MAFFT+CaCoFold · any cov. pair | 116 | 40 | 13 | 207 | 1 | 68.0 | 10.9 % |
| P0 fixed positional baseline (−166…−32) | 232 | 134 | 11 | 0 | 0 | — | 7.4 % |

Detection, region and boundary levels are reported separately in `tables/BENCHMARK_SUMMARY.tsv`.
Strand is correct for every call; the window is RT-oriented and all T2/T3 references are
same-strand by definition, so strand is not an informative test here. 14 loci match a published,
experimentally characterised ncRNA. No comparative arm placed a boundary within ±20 nt on any of
them (`tables/BENCHMARK_previously_validated_subset.tsv`).

### Controls — set-level signal (`tables/EVAL_set_level.tsv`, `figures/fig4`)

| cohort | sets | A · SPIRE rule | A · any cov. pair | B-seq · any cov. pair |
|---|---|---|---|---|
| POS (real retron windows) | 27 | 15 % | 74 % | 33 % |
| distal −1500…−1201 | 24 | 21 % | 88 % | 8 % |
| intragenic +300…+599 | 26 | 0 % | 46 % | 19 % |
| non-retron RT (AbiK, AbiP2) | 4 | 50 % | 75 % | 0 % |
| group II intron (hard negative) | 3 | 0 % | 100 % | 33 % |

### CM-negative pilot — 20 sets, 219 loci (`CM_MISSED_PILOT.tsv`, `CANDIDATE_EVIDENCE.tsv`)

| stratum | loci | A · SPIRE-rule calls | windowed CM hit E ≤ 1e-5 |
|---|---|---|---|
| S1/S2, RT homolog has a CM call | 53 | 0 | **20** |
| S1/S2, orphan component | 64 | 20 (one set; region = the upstream CDS, 21 % identity) | 0 |
| S3 fused-RT rule | 74 | 7 (one set; 2 covarying pairs) | 2 |
| S5 sequence only | 28 | 10 | 1 |

Every de novo call was checked for independent support: cross-arm agreement, CDS overlap,
sub-threshold CM, homolog CM position, covariation versus power, positional spread and RNAfold.
No call has covariation at or above power *and* agreement with a CM hit or a homolog's CM
position beyond noise. Only two calls touch a relaxed CM hit at all (`PIL_S3_FUSED_3` m04:
TypeV, E = 6.9, 2 nt overlap; m06: TypeIA_IIAI, E = 0.49, 9–10 nt overlap, span 100 % CDS), and
both rest on 2 covarying pairs. `PAIR_POPULATION_IMPACT.tsv`: CM-window rescues 23 loci, 8 types,
**0 new RT components**, 4 new ncRNA components. Weak de novo candidates: 8 loci, 2 new RT
components (one type XII), not credible yet.

## Files

| file | content |
|---|---|
| `ASSET_REGISTER.tsv` | every ZIP/tarball member and tool: role, inputs, outputs, parameters, versions, executability, defects |
| `WORKFLOW_RECONSTRUCTION.md` | which of the 7 claimed workflows exist, execution order, versions, six defects found by execution |
| `NCRNA_METHOD.md` | the 16 method questions, label-assisted vs de novo, CM-route lineage, R-scape vs CaCoFold |
| `METHOD_COMPARISON.tsv` | method × input / prior knowledge / structural evidence / boundary / failure mode / CM independence |
| `BENCHMARK_DESIGN.md` | frozen design + Amendments 1–2 |
| `BENCHMARK_RESULTS.tsv` | member × arm × rule, positive cohorts, all metrics and categories |
| `CM_MISSED_PILOT.tsv` | every pilot locus, every arm × rule category, windowed CM hit |
| `CANDIDATE_EVIDENCE.tsv` | every pilot call with its independent-support columns |
| `PAIR_POPULATION_IMPACT.tsv` | newly paired RTs/ncRNAs/types; new RT and ncRNA components; within-type components; ceilings |
| `NEXT_SCALE_PLAN.md` | proposal only: population and homolog-set census, two runs with commands/compute/criteria |
| `tables/` | freeze and prediction hashes, set manifests, evaluation tables, census tables |
| `figures/` + `figures/data/` | six figures and the exact data behind each |
| `scripts/` | `s01`–`s11`, `common.py`, `windows.py` — regenerate everything; `s10_spire_hmm_grouping.sh`/`s10a_*` are **withdrawn stubs** (operator ruled SPIRE RT classification out of scope before they ran) — safe to delete |

Scratch (gitignored, disposable): `ARIS_OUTPUT/spire_ncrna_audit/` — unpacked archive, smoke tests,
106 set directories with every mLocARNA/R-scape/CaCoFold output (142 MB), master parquet,
clusters, predictions, CM rescan. Reproducibility: mLocARNA and R-scape (seed 42) reruns are
byte-identical (checked on `POS_XIII_2`).

## Regenerate

```bash
P=<python with duckdb, pandas, networkx, matplotlib>   # used: dbchar-workbench .venv
cd analysis/spire_ncrna_audit/scripts
$P s01_master_table.py && bash s02_rt_homolog_clusters.sh && $P s03_select_sets.py && $P s03b_gii_control.py
$P s04_run_sets.py 'POS|POS_S5|CTRL_DISTAL|CTRL_INTRAGENIC|CTRL_NONRETRON' 11
# record sha256 in tables/PREDICTIONS_FROZEN.tsv before the next line (s05 refuses otherwise)
$P s04_run_sets.py 'PIL|CTRL_GII_HARD' 12
$P s05_evaluate.py <both prediction files> && $P s08_candidate_evidence.py && $P s09_upstream_cds_census.py
$P s07_scale_census.py && $P s10_pair_impact.py && $P s11_results_tables.py && $P s06_figures.py
```

Open items: the operator's 977-ncRNA boundary set was not found on this machine (`docs/BLOCKED.md`,
2026-09-18). Predictions are frozen, so it can be mapped in and evaluated without rerunning anything.
