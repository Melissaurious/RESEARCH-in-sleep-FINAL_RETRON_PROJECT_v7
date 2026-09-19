# LAUNCHER — m2_historical_classification_expansion  (PROPOSED rev-3 — M2a–c APPROVED, PAUSED)

> ⛔ **Status: revision 3 (2026-09-19).**
> - The operator approved **M2a–c** within ≤ 60 CPU-h on 2026-09-19. **M2d is NOT approved.**
> - Execution is **PAUSED**, under the operator's own rule: the Toro 2014 source audit (M1
>   report §14–17) materially changes the historical-core definition. The operator must
>   choose the extraction contract in §4a (**MCC-v3**, recommended, or MCC-v2 required-core)
>   before anything is frozen.
> - After that choice, this file is copied to `launchers/` with the decision recorded.
> - **M2c ends in a mandatory independent (Codex) review and operator stop.**

### Three things this track keeps apart

1. **Exact historical reproduction.** Impossible: Mestre's RT0–RT7 extraction and MSA are
   unrecoverable (M1).
2. **Historical reconstruction.** The primary task (M2a): rebuild the classification as
   faithfully as the recoverable evidence allows, then test whether historical clade
   membership can be recovered **without the clade label constructing the placement**.
3. **Modern classification-space placement.** Downstream (M2b–c now; M2d later, if approved),
   only once item 2 passes validation.
>
> **Title:** *Historical-classification expansion and placement test.*
> **Question:** how does **modern retron / retron-like RT** diversity relate to the Mestre 2020
> retron classification when both are represented on a reproducible, Mestre-comparable
> RT0–RT7 core? The full 501,561-RT catalogue is the **source and denominator only**. It is
> not the placement population.
>
> Evidence for every design number below: `analysis/mestre_audit/REPORT.md` §9–§12 and
> `analysis/mestre_audit/m2_design/`.

### Changes from revision 1

| rev-1 | rev-2 |
|---|---|
| place representatives of all 501,561 RTs | only the prospectively frozen **retron / retron-like query universe** (M2b); non-retron RTs are controls only |
| cut "the RT0–7 region" with the Stage-2 mapper | Stage-2's 150-anchor instrument does **not** observe the RT0/RT1 N-terminus. The region is now **MCC-v2**, a Mestre-comparable core defined on the published Toro 2014 RT0–RT7 extraction frame (§4a) |
| five identity scales in parallel | **one primary** representative scheme (85 % on the MCC); 95 % and 70 % are sensitivity only |
| one gate sequence ending in catalogue placement | M2a reference reconstruction → M2b query freeze → M2c smoke + **operator stop** → M2d scale |
| Ibex root "unreachable" | audited 2026-09-19 (M1 §9): V4 alignments found, no Mestre RT0–RT7 material; K0 fired and awaits the operator's disposition |

## 1. Objective and success criterion

**Objective.** Deliver four things, in this order: (a) a validated, frozen reference package
(MCC-v2 extracts of clean published-accession Mestre proteins, reference alignment, pruned
published topology, fitted model); (b) a frozen, tiered query-population table for modern
retron / retron-like RTs; (c) a smoke test of placement behaviour, stopped for review;
(d) after approval, placement of frozen representatives with expansion and accumulation
measures on the retron population.

**Success criterion.**
1. **M2a:** every one of the 1,928 published tips has exactly one reference status
   (`IN_REFERENCE` / `NO_PUBLISHED_PROTEIN` / `NO_EXTRACTABLE_CORE` / `DUPLICATE_COLLAPSED`),
   and the counts sum to 1,928. Held-out genuine Mestre sequences return to their published
   clade at the level fixed in §7a, **on evaluation replicates not used to set thresholds**.
2. **M2b:** every exact RT in the 501,561 catalogue carries a stratum and, if it is in the
   query universe, an inclusion or exclusion reason. The table is hashed and recorded in a
   decision record **before** any M2c placement output exists.
3. **M2c:** every smoke stratum and control behaves as declared in §7c, or the deviation is
   reported. The run stops.
4. **M2d:** every retron query exact RT maps to exactly one primary representative, and
   every representative to exactly one status. Categories 4 and 5 (§6b) are never merged.

## 2. Kill criteria

Declared before any M2 number exists.

- **K0 — Ibex changes the reference.** If the Ibex audit finds an original Mestre-lineage
  RT0–RT7 extract set, extraction coordinates or the pre-trim alignment behind the V4
  re-inferences, M2a stops. MCC-v2 is re-examined against that asset first, by operator
  decision.
  **Status 2026-09-19: `K0_FIRED_RESOLVED_COMPARATOR_ONLY`** (operator decision,
  `docs/decisions/2026-09-19_m1_mestre_audit_and_k0_disposition.md`). The
  audit (M1 report §9) found the V4 pre-trim and `_occ50` alignments. They are fixed
  YxDD-window alignments of the 1,843-protein set carrying 91 substitutes, cut on borg by
  V4's `s7h`. They are not Mestre-lineage RT0–RT7 extracts, and no extraction coordinates or
  Mestre alignment exist on Ibex. **Recommended disposition:** MCC-v2 is unchanged; the V4
  alignments become `DO-NOT-USE` as reference and comparator-only in M2a step 3. Recording
  this is an operator decision.
- **K1 — reference not reconstructable.** M2a stops, and there is **no placement at all**, if
  any of the following holds:
  - after pruning to `IN_REFERENCE` tips, fewer than 9 of the 10 published
    unrooted-monophyletic clades stay unrooted-monophyletic;
  - the published topology is rejected against the unconstrained ML tree on the same
    alignment (AU test, p < 0.01). This is reported, and alone it is not fatal only if every
    other K1 item passes; the operator decides;
  - fewer than 90 % of clean published-accession proteins yield an extractable MCC-v2 core
    (the feasibility probe measured 95.3 %).
- **K2 — held-out recovery fails.** On the evaluation replicates, fewer than 80 % of held-out
  tips from the 10 monophyletic clades are `CONFIDENTLY_PLACED` into their published clade, or
  more than 2 % are confidently placed into a **wrong** clade. The consequence is **STOP.**
  "EPA-ng accepted the files" is not a pass.
- **K3 — controls fail.** Any of these is **STOP**:
  - more than 5 % of the non-retron negative panel is `CONFIDENTLY_PLACED`;
  - more than 1 % of column-shuffled held-out queries are `CONFIDENTLY_PLACED`;
  - any of the 15 RNA-polymerase substitutes reaches placement at all.
- **Cost stop.** More than 2× the estimate measured in M2c: stop and report.

## 3. Non-goals — out of scope

- ⛔ Placing non-retron RTs as targets. Group II, DGR, CRISPR-RT, UG*, Abi*, G2L* and
  unlabelled RTs enter only as declared **negative/outgroup controls**, and their failure to
  place is never called expansion.
- ⛔ Any de novo tree of the catalogue or of the representatives. No rebuilding of the
  historical tree around modern sequences.
- ⛔ MyRT, DefenseFinder or PADLOC labels as biological truth. They define **evidence
  tiers** (§4b), which is a statement about the detection route, not about the biology. They
  never decide a clade.
- ⛔ Calling any MCC-v2 extract "the Mestre alignment" or "Mestre's RT0–RT7". The published
  alignment is unrecoverable (M1). The operational object is always named **MCC-v2**.
- ⛔ Using the Stage-2 frozen 150-anchor mapper (`rtmap-1.0.0`) as the extractor. It does not
  observe the RT0/RT1 N-terminus. It may appear only as a reported cross-check column.
- ⛔ Substituting a protein for any of the 114 tips whose published protein is not held
  (112 rescued substitutes, including 15 RNA-polymerase subunits, plus terminals 461 and 1774).
- ⛔ "New family", "novel clade" or "Mestre is wrong" statements. §6b categories are
  descriptive.
- ⛔ ncRNA co-evolution, fold space, Stage-D relatedness controls.
- Anything else is logged in `docs/BLOCKED.md` with a default and not built.

## 4. Inputs

| path | what it is | trust grade |
|---|---|---|
| `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material/Supplementary_mestre_Tree.nwk` | published tree, 1,928 tips | `RAW` |
| `…/supplementary_material/Supp_material_T1_R1_systematic_prediction.csv` | published per-tip clade/type table | `RAW` |
| `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references/rt0_rt7/historical/toro_2014_Rt0-Rt7.FASTA` + `TableS1_Toro_2014.XLSX` | published Toro & Nisa-Martínez 2014 RT0–RT7 **extraction** alignment (742 × 1,466). The MCC-v2 frame and the non-retron negative panel | `RAW` |
| `/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences/terminal_*/protein_aminoacid.fasta` | historical proteins; **only headers without `\|rescued`** (1,814) | `RE-DERIVE` |
| `analysis/mestre_audit/subaudits/v2_v3_v5/v235_rnap_substitutes.tsv` | 15 RNA-polymerase substitutes | `FROZEN:M1` — exclusion control |
| `analysis/mestre_audit/scripts/m07_mcc_v2_feasibility.py` | the MCC-v2 extraction rule, verbatim | `FROZEN:M1` — M2a re-freezes it by sha256 |
| `analysis/mestre_audit/scripts/m04_query_population_census.py` | the M2b tier rules, verbatim | `FROZEN:M1` — M2b re-freezes it by sha256 |
| `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_exact_v1.{faa,parquet}` | 501,561 exact RTs | `FROZEN:dbchar_g2` — source catalogue / denominator |
| `…/data/derived/rt_tool_calls_v1.parquet` | per-record DF / PADLOC / myRT calls | `FROZEN:dbchar_g6` — evidence tiers only |
| `…/data/derived/rt_ncrna_pairs_v1.parquet` | canonical, geometry-eligible RT–ncRNA pairs | `FROZEN:dbchar_g3` — evidence tiers only |
| `…/data/derived/rt_records_v1.parquet` | record → genome, database, taxonomy | `FROZEN:dbchar_g2` — sampling units for M2d |
| `…/data/derived/rt07_g5a/g5a_eligibility_partition.tsv.gz` | Stage-2 eligibility | `FROZEN:rt07_g5a` — reported column, **not** a filter |
| `/home/borg/RESEARCH-retron-db/results/stage1_mestre_replication_and_insights/tables/{protein_substitution_audit,clade_recovery}.tsv` | substitution flags; unrooted monophyly | `FROZEN:` retron-db 76ad2af, rerun-verified by M1 |
| `/home/borg/RESEARCH-retron-db/results/stage3_placement_toolkit/scripts/place.py` | prior placement tooling | `RE-DERIVE` (design reuse; smoke-only precedent) |
| V4 `mestre_trees/`, V4 `refbuild/`, retron-db `reference_msa_v1.afa`, V3/V4 Mestre FASTA/STO | prior trees and alignments | `DO-NOT-USE` as reference: all contain substitutes. Comparator only, after M2a freezes |
| `/ibex/project/c2366/RETRONS/Mestre_replication/` | Ibex detector-pipeline root. Audited 2026-09-19: 128,701 files; proteins byte-identical to the borg benchmark | `DO-NOT-USE:` holds no reference material. Per-file identity in `analysis/mestre_audit/ibex_audit/results/mestre_replication/` |
| `/ibex/project/c2366/RETRONS/rt0_rt7_domain_test_v4_and_tree/mestre/out/*.afa` | V4 re-inference alignments (Ibex-only; 1,843 taxa incl. 91 substitutes) | `DO-NOT-USE:` as reference. Comparator only after M2a freezes; K0 disposition above |

⛔ Read-only, always. Probe real values (WA-D.4).

### 4a. The operational interval — ⛔ PENDING OPERATOR CHOICE: MCC-v3 (recommended) or MCC-v2

**Why this is open.** The Toro 2014 source audit (M1 §14–17) found **source-stated RT0–RT7
boundaries on 76 clean Mestre proteins**: Toro 2014 retron extracts occurring verbatim, or
at ≥ 0.95 identity, inside them. Scored against those boundaries, with no Mestre label:

| | extracted of 76 | start / end within 5 aa | median error start / end | clean historical extracted | RNAP control |
|---|---:|---|---|---:|---:|
| **MCC-v3 boundaries = Toro-template extraction (TTE, `m09`)** | **76** | **0.658 / 0.816** | **0 / 0 aa** | **1,814 / 1,814** | 0 / 15 |
| MCC-v2 window | 71 | 0.225 / 0.718 | 11 / 2 aa | 1,729 / 1,814 | 0 / 15 |
| MCC-v2 required core (the approved primary) | 71 | 0.000 / 0.127 | 29 / 10 aa | 1,729 / 1,814 | 0 / 15 |

**The MCC-v3 contract (proposed):**
- **Primary edges:** TTE. The templates are the 102 Table S1 "Retrons" extracts; take the best
  bitscore template covering ≥ 0.80 of itself. Leave-near-self-out (< 0.90 identity) applies
  in historical validation only; for modern queries every template is eligible and the
  template identity is recorded.
- **Core QC:** the MCC-v2 hmmalign route must place ≥ 70 % of required-core states
  (blocks 4–28) inside the TTE interval; otherwise the status is
  `UNABLE_TO_EXTRACT_MCC_RELIABLY`.
- **Primary alignment input:** the full TTE interval. **Sensitivity:** the MCC-v2
  required-core columns, reported beside every primary number.

The difference is provenance-driven: it was measured on source-stated ground truth before any
tree, placement or clade evaluation, and run once with rules declared in `m09`.
**If the operator keeps MCC-v2**, the text below stands unchanged and TTE becomes a sensitivity
analysis.

*MCC-v2 specification (unchanged; under MCC-v3 it becomes the core-QC route):*

- **Name and meaning.** MCC-v2, the *Mestre-comparable core, version 2*. It is **not**
  Mestre's RT0–RT7: that alignment was never published, and no historical asset preserves it
  (M1, `subaudits/rt07/rt07_findings.md`). It is the closest reproducible operational
  equivalent.
- **Frame.** The published Toro 2014 RT0–RT7 *extraction* alignment, from the Toro lab
  (Mestre's lineage) and built without Mestre clades. Profile:
  `hmmbuild --amino --fragthresh 0`, 230 match states, all within frame columns 68–1305.
  The default fragthresh gives 465 states, 228 of them artefact flank states.
- **Window.** Frame columns 68 (modal Toro start) to 1305 (modal Toro end = RT7 C-terminus).
- **Required core.** Frame blocks 4 → 28 (columns 224–1247, 182 states). These are the first
  and last blocks occupied by **≥ 95 % of the 102 Toro-2014 retrons**. That criterion uses
  Toro retrons only; no Mestre clade and no Mestre sequence was used.
- **Optional flanks.** The RT0 zone (columns 68–223) and the RT7 tail (block 29, 1297–1305)
  are kept whenever residues align there, and are never required. Toro's own retron extracts
  leave RT0 blocks 1–2 at 0.47 / 0.00 occupancy (group II ≈ 0.9), and the terminal 9-state
  block is an alignment-edge artefact (v1: 554 false C-truncations with core occupancy 0.90).
- **Extractability rules E1–E5 and the MULTI_CORE flag:** exactly as in `m07`. Two
  independent routes, `hmmalign` into the profile and `mafft --add --keeplength --mapout`
  into the frame, must agree on core bounds within 5 residues.
- **Historical evidence (feasibility, not the gate).** Clean published-accession proteins:
  - **1,729 / 1,814 extractable (95.3 %)**; failures are 54 C-truncated, 30 N-truncated,
    1 non-standard; 1 is MULTI_CORE;
  - route concordance: **99.1 % of core starts and 99.5 % of core ends within 5 residues**;
    interior block starts agree within 2 residues for a median 0.917 of blocks per sequence,
    but only 51.7 % of sequences have ≥ 90 % of blocks agreeing, so interior column
    assignment carries real uncertainty and M2a must quantify it;
  - **15 / 15 RNA-polymerase substitutes: `NO_HIT`**;
  - median extract 217 aa (IQR 206–225).
  MCC-v1 (≥ 50 % anchors) failed the same probe (64 % extractable) and is recorded, not
  hidden.

### 4b. The query universe (M2b) — tiers, measured pre-activation

Unit: exact RT. Evidence is assessed per record, because system evidence has to co-occur at
one locus. Lines: **DF** (DefenseFinder retron system), **PAD** (PADLOC retron system),
**NC** (canonical, geometry-eligible RT–ncRNA pair), **PROF** (myRT Retron family).

| stratum | rule | exact RTs | records | g5a-eligible | identical to a clean Mestre protein |
|---|---|---:|---:|---:|---:|
| **A — high-confidence retron system** | a Retron record with ≥ 2 of {DF, PAD, NC} | **33,670** | 483,848 | 31,952 | 1,289 |
| **B1 — single system line** | a Retron record with exactly 1 of {DF, PAD, NC} | **20,451** | 96,624 | 16,130 | 227 |
| **B0 — profile only** | a Retron record with PROF alone | **24,166** | 82,836 | 13,313 | 87 |
| M — MULTI / mixed-family | stage-1 rule 2 | 7,593 | 9,012 | 2,824 | 0 |
| D — discordant | DF/PAD retron call on a non-Retron record | 5 | 11 | 1 | 0 |
| X — no retron evidence | everything else | 415,676 | 2,378,907 | 305,161 | 0 |

- **Primary query universe: A ∪ B1 ∪ B0 = 78,287 exact RTs.** A and B are **never pooled** in
  any summary.
- M and D are separate, separately reported strata and are not in the primary universe.
- X is not a query; a declared random sample of it supplies negative controls.
- ⚠️ **Circularity.** DF and PAD models descend from the Mestre/Toro reference, and all 21
  ncRNA CMs are Mestre-authored. Tier A is "strong system context". It is **not** evidence
  independent of Mestre, and every A-stratum placement summary carries that flag. Sensitivity
  variant **A-nc**: tier-A RTs with an A-record carrying the NC line (23,556).
- M1 also found that 1,603 of the 1,813 distinct clean Mestre sequences occur verbatim in the
  catalogue. They are reference-identity controls, not discoveries.

## 5. What might already exist

- **M1 audit** (`analysis/mestre_audit/`): the substitution defect, V4 re-inference
  limitations, and the retron-db rerun. The MCC and census probes are the starting point.
- **retron-db `stage3_placement_toolkit`:** its lessons are fixed here. The LWR floor must come
  from a shuffled control (0.50 admitted 3 of 20 shuffled queries; 0.80 admitted none); a
  single-profile discovery filter misses its own references; EPA-ng output order is
  thread-dependent; and caches must be keyed on their inputs.
- **V4 `rt0_rt7_domain_test/s09,s10,s14`:** the prior Toro-frame projection, reproduced
  byte-identically by M1. It used the default-fragthresh profile and the substitute-
  contaminated set, so it is a comparator only.
- **Ibex root:** uninspected. It may hold the lost `*_occ50.afa` inputs and pre-trim alignments
  behind the V4 trees; those derive from the same contaminated protein set.

What would make any of these untrustworthy: a `|rescued` terminal inside; a missing producing
command; an HMM built with default fragthresh on the Toro extracts.

## 6. Claims this task tests

| id | role in this task |
|---|---|
| `C8` | primary |
| `C3` | supporting |
| `C7` | supporting |

⚠️ No contract claim states "the historical classification represents modern retron
diversity". Adding one is an operator decision; until then those results are descriptive.

### 6b. Interpretation categories — declared before any placement; never merged

1. **Close representatives of known diversity:** `CONFIDENTLY_PLACED`, with pendant length at
   or below the clade's reference-only leave-out distribution (≤ its 95th percentile).
2. **Deeper expansion within a historical clade:** `CONFIDENTLY_PLACED`, pendant length above
   that percentile.
3. **Ambiguous among historical clades:** `AMBIGUOUS`.
4. **Retron sequence space not confidently represented by the historical reference:**
   `OUTSIDE_WELL_SUPPORTED_HISTORICAL_CLADE_SPACE`.
5. **Comparable core not extractable / not alignable:** an M2b exclusion reason, or
   `UNABLE_TO_ALIGN_OR_PLACE_RELIABLY`.

Neither 4 nor 5 is a "new retron family", and neither is evidence that Mestre 2020 is wrong.

## 7. Gates

| gate id | the ONE measurement | weight | settles | stop condition |
|---|---|---|---|---|
| `m2_g0_ibex_reconcile` | identity classes of every Ibex Mestre-root file against borg (`m05` over the Ibex inventory) — **measurement already made in M1 (2026-09-19, three roots, 141,327 files); g0 only packages it as a bundle** | LIGHT | — | done when results/m2_g0_ibex_reconcile/ exists and run.sh reproduces the number; K0 evaluated |
| `m2a_reference_reconstruction` | held-out clade-recovery rate on evaluation replicates (§7a), with K1–K3 | FULL | C3 (support) | done when results/m2a_reference_reconstruction/ exists and run.sh reproduces the number; reference package frozen by sha256, or STOP recorded |
| `m2b_query_freeze` | per-exact-RT stratum, MCC-v2 extractability and inclusion reason for all 501,561 | FULL | C8 (support) | done when results/m2b_query_freeze/ exists and run.sh reproduces the number; table sha256 in a decision record before M2c |
| `m2c_placement_smoke` | per-stratum status distribution on the §7c smoke set | FULL | C7 (support) | done when results/m2c_placement_smoke/ exists and run.sh reproduces the number; then **STOP for operator review** |
| `m2d_expansion_and_accumulation` | §7d expansion table and accumulation curves on the retron population | FULL | C8 | done when results/m2d_expansion_and_accumulation/ exists and run.sh reproduces the number; separate operator approval required to start |

### 7a. M2a — historical RT0–RT7-comparable reference reconstruction

0. **Denominator ledger, reported at every step:**
   - source entries (1,928 tips, 1,927 clade-labelled + 1 Orphan);
   - clean proteins (1,814 terminals, 1,813 distinct);
   - extractable under the chosen contract;
   - unsuitable or excluded, with the reason.
   `UNABLE_TO_EXTRACT_MCC_RELIABLY` is an extraction status, not evidence of a non-retron.
1. **Clean accession set.** Published tips whose held protein carries the published accession
   (1,814 terminals; 1,813 distinct sequences). The 114 others are `NO_PUBLISHED_PROTEIN`.
   Reuse the existing verified download; nothing is re-downloaded.
2. **Extraction.** The contract chosen in §4a (MCC-v3 = `m09` TTE + `m07` core QC, or MCC-v2 =
   `m07`), frozen by sha256. Output: extracted sequences and a
   full-length ↔ extract coordinate table (protein start and end, per-block residue
   positions from both routes, RT0-zone and RT7-tail residue counts, status). Non-extractable
   tips are `NO_EXTRACTABLE_CORE` and are pruned. Identical extracts are collapsed to one
   reference taxon, and every tip mapping is kept.
3. **Reference alignment**, the closest published methodology. Mestre: MAFFT, "progressive
   methods", RT0–7 domain, IQ-TREE 1.6.12, LG+F+R10.
   - **Primary:** `mafft --retree 2` (FFT-NS-2, progressive), untrimmed.
   - **Comparators:** L-INS-i, and the Toro-frame `hmmalign` projection.
   - **Quality measures:** column occupancy profile, and pairwise-column agreement between
     primary and each comparator (fraction of residue pairs aligned identically). The
     primary is kept unless it fails K1/K2 while a comparator passes; any switch needs a
     decision record.
4. **Tip mapping.** The published newick pruned to reference taxa; the topology is never
   re-estimated.
5. **Model fit.** `iqtree -te <pruned> -m LG+F+R10` gives lnL, BIC and branch lengths.
   RAxML-NG `--evaluate` finds the closest EPA-ng-representable model; ΔlnL and ΔBIC are
   reported against LG+F+R10. The AU test uses one unconstrained IQ-TREE ML search on the
   same alignment.
5b. **Historical-tree comparison.** Infer one **clean** ML tree from the reference alignment
   with `LG+F+R10` (IQ-TREE 3.1.3 in `retron_tradicional`; the version difference from Mestre's
   IQ-TREE 1.6.12 is recorded, and the 546-model ModelFinder step is not repeated). Compare
   three trees:
   - the **published** tree;
   - the **recovered contaminated V4** trees. Their Ibex products are reused as comparator
     assets per `K0_FIRED_RESOLVED_COMPARATOR_ONLY` and are **not recomputed**;
   - the **clean reconstruction**.
   For each of the 11 clades, report whether it is recovered (unrooted split; purity; UFBoot
   support). The reconciliation table states the exact denominator behind every historical
   statement:
   - `10/11`: unrooted monophyly on the published tree, 11 clades;
   - `9/10`: the K1 criterion, 10 monophyletic clades after pruning;
   - `≤3/11`: V4 support-based clade count on 1,843-taxon trees;
   - V4 purity-only `4–6/11`.
   The aim is to quantify which clades are reproducible, not to force the topology.
6. **Leave-out placement — PRIMARY: relatedness-blocked.**
   - Cluster the reference extracts at the frozen **85 % identity** rule (MMseqs2,
     `--min-seq-id 0.85 -c 0.8`). Every member of an 85 % group stays on the same side of a
     split.
   - **10 replicates**, each withholding about 10 % of **groups**, stratified by clade. Per
     replicate: prune the withheld taxa, re-fit branch lengths on the fixed published
     topology, align the withheld sequences by the **same query route used for modern RTs**,
     then run EPA-ng.
   - Historical labels are revealed **only after** each replicate's placements are fixed.
   - Replicates 1–5 **calibrate** τ_LWR (clade-level LWR), τ_EDPL and τ_pend(clade).
     Replicates 6–10 **evaluate** K2.
   - **Secondary comparison only:** sequence-level random 10 % holdout, reported beside the
     primary.
   - **Per clade, never pooled:** reference sequence count, independent 85 % group count,
     withheld count, `CONFIDENTLY_PLACED` correct, `AMBIGUOUS`, confident wrong placement,
     `UNABLE_TO_ALIGN_OR_PLACE_RELIABLY`, and an underpowered flag (< 5 independent groups).
     Clade 10 (paraphyletic w.r.t. clade 11) is reported separately and does not count toward
     K2. The K1–K3 stop criteria are unchanged.
7. **Controls.**
   - the 15 RNA-polymerase substitutes (must fail extraction; must never be placed);
   - the other 97 substitutes (reported separately; never in the reference);
   - column-shuffled held-outs;
   - the non-retron negative panel: Toro-2014 non-retron extracts (group II, DGR, CRISPR-RT,
     UG/G2L, Abi), plus a declared random 500 from catalogue stratum X, sampled with seed 2026;
   - K3 thresholds apply to all of these.
8. **Outputs:** clean accession set, extracts, coordinate table, reference alignment(s),
   tip-mapping table, model-fit table, leave-out table, failure/abstention table and the
   frozen reference package.

### 7b. M2b — modern retron query freeze

One row per exact RT, 501,561 rows, with:
- `rt_seq_hash`, record/system IDs and counts;
- stratum (A / B1 / B0 / M / D / X, rules of `m04`);
- evidence lines per record (DF, PAD, NC, PROF) and tool provenance;
- ncRNA status (n canonical pairs, CM model names);
- protein length and non-standard fraction;
- MCC-v2 status, extract length, flank residue counts, MULTI_CORE;
- g5a eligibility (reported, not a filter);
- inclusion/exclusion reason.

Exclusions, applied only to A/B/M/D:

| reason | rule |
|---|---|
| `NOT_QUERY` | stratum X |
| `NO_HIT` / `N_TRUNCATED` / `C_TRUNCATED` / `LOW_CORE_OCCUPANCY` | MCC-v2 E1–E4 |
| `NONSTANDARD` | E5 (> 1 % non-standard residues in the extract) |
| `MULTI_CORE` | fusion / tandem RT whose core cannot be isolated to one copy |
| `CORE_LENGTH_OUTLIER` | extract > 2× the historical median (> 434 aa); flagged, and excluded from primary |

The excluded fraction is reported **per stratum**, as a result.

### 7c. M2c — placement smoke (then STOP)

Stratified, **seed 2026**, drawn from the frozen M2b table after M2a passes:

Nearest-reference identity is measured by MMseqs2 on the extracted core against the frozen
reference. The bins are half-open and cover the full range: `[0.90, 1.00)`, `[0.70, 0.90)`,
`[0.50, 0.70)`, `[0, 0.50)`, plus the separate identical class `1.00`. A bin with fewer
available sequences than its quota takes all of them, and the shortfall is reported, never
back-filled from another bin.

| stratum | identity bins | n per bin | n | expectation declared now |
|---|---|---:|---:|---|
| A, identical to a clean Mestre protein | 1.00 | — | 40 | `CONFIDENTLY_PLACED` into its own published clade (positive control) |
| A | the four bins above | 30 | 120 | no expectation stated for the lower bins; behaviour reported |
| B1 | the four bins above | 15 | 60 | reported separately from A |
| B0 | the four bins above | 15 | 60 | reported separately from A |
| M (MULTI / mixed) | unbinned | — | 20 | separate stratum |
| 15 RNA-polymerase substitutes | — | — | 15 | never reach placement |
| column-shuffled A queries | — | — | 40 | ≤ 1 % confident |
| non-retron panel: Toro-2014 non-retron extracts + stratum-X sample | — | — | 60 (30 + 30) | ≤ 5 % confident |
| **total** | | | **415** | |

Arithmetic check: 40 + 120 + 60 + 60 + 20 + 15 + 40 + 60 = **415**. The rev-2 table summed to
375 while the text said about 415, and it omitted the 70–90 % range; both are corrected here.

- **Query route:** identical to M2a step 6.
- **Status rules:** the τ values frozen in M2a.
- **Deliverables:** per-stratum status counts, EPA-ng runtime per query (it sizes M2d), and
  any rule that behaved unexpectedly. The purpose is to check that the rules behave as
  declared, **not to discover new clades**; `OUTSIDE_WELL_SUPPORTED_HISTORICAL_CLADE_SPACE` is
  never renamed as a family or clade.
- **Carried identifiers, never used to place:** every query and reference row keeps its keys
  to ncRNA family, accessory architecture, current system/type calls, taxonomy, and RT
  structural/sequence architecture. They are for later **independent** tests of whether the
  historical classification tracks other biology.
- **Independent review (mandatory, before the stop).** Codex receives the bundle paths and
  the neutral review questions only; no desired conclusion is stated. It reviews:
  historical-reference cleaning, the extraction contract's anti-circularity, the blocked
  validation, the recovered-V4 comparator interpretation, the placement confidence rule,
  control behaviour, and whether any claim exceeds the evidence. Its verdict is recorded
  verbatim. **The run then stops for operator review.**

### 7d. M2d — scale, only after M2a–c pass and a second approval

- **Primary representative scheme.** MMseqs2 clustering of **MCC-v2 extracts** of the
  included A ∪ B1 ∪ B0 exact RTs:
  - settings: `--min-seq-id 0.85 -c 0.8 --cov-mode 0`, seed-fixed, one clustering over the
    union, with each member's tier kept;
  - why 85 %: it is the redundancy scale of Mestre's own source dataset (Toro: 9,141
    representatives at 85 % identity), so one representative is roughly one historical
    reference unit;
  - **95 % and 70 %** are sensitivity analyses only; they never replace the primary in a
    headline;
  - M is clustered and reported separately.
- **Per representative:** cluster size, member exact RTs and systems, taxonomy (per member),
  tier composition, ncRNA status, full sequence and MCC extract, placement status, LWR, EDPL
  and pendant length. Members inherit their representative's placement, and summaries are
  stratified **by member tier**.
- **Expansion measures, per historical clade and for "none":**
  - retron systems / exact RTs / representatives per clade;
  - new clusters (clusters with no historical member) per clade;
  - nearest-reference identity and pendant-length distributions;
  - fractions in categories 3, 4 and 5, each reported separately;
  - clade occupancy across taxonomy (phylum → genus) and source database;
  - expansion asymmetry (share of new clusters ÷ share of historical tips), with a
    genome-bootstrap CI.
  Every measure is reported separately for A, B1 and B0, and for A-nc.
- **Accumulation / saturation, on the retron query population only.** Curves of:
  - retron systems sampled;
  - unique retron exact RTs;
  - primary-scheme clusters;
  - historical clades confidently represented;
  - clusters lacking confident historical-clade representation;
  - marginal discovery rate.
  All are plotted against genomes sampled, using:
  - ≥ 100-permutation random rarefaction;
  - per-species and per-genus capped rarefaction;
  - database-balanced resampling, plus leave-one-database-out;
  - RefSeq/GenBank twins collapsed first.
  Raw acquisition order appears only as a labelled comparison.

## 8. Compute

- **M2a–c:** borg (48 cores). The unconstrained IQ-TREE ML search for the AU test on about
  1,730 × about 220 aa is the dominant cost (≤ 40 CPU-h). Fixed-topology fits and 10 leave-out
  replicates take ≤ 15 CPU-h; the smoke run is under 1 CPU-h. **Planning total: ≤ 60 CPU-h.**
- **M2d only (the revised budget):** expected **≈ 40 CPU-h**, budget **100 CPU-h**,
  **0 GPU-h**, max single job **8 h**; borg is sufficient.
  - Components: MCC extraction of ≤ 86 k RTs (≈ 2 CPU-h); MMseqs2 clustering at three scales
    (< 2 CPU-h); query alignment plus EPA-ng for primary representatives (estimated 10–20 k
    representatives, ≤ 10 CPU-h); sensitivity scales (≤ 15 CPU-h); rarefaction and bootstraps
    (≤ 15 CPU-h).
  - This replaces rev-1's 250 CPU-h. The EPA-ng per-query cost measured in M2c re-sizes it
    before M2d starts. Ibex is used only if the M2c measurement crosses the WA-K.1 thresholds.
- Hard stop at 2× the M2c-measured estimate.

## 9. Autonomy envelope

**Auto-proceed:** `false` until activation. After activation it is `true` **within M2a →
M2c only**; M2c ends in a mandatory stop.

| | budget (proposed) |
|---|---|
| CPU-hours | 60 for M2a–c; 100 for M2d (separate approval) |
| GPU-hours | 0 |
| max single job | 8 hr |
| review rounds per gate | 3 |

**Human gate — stop and wait:**
- activation of this launcher;
- the Ibex audit result if K0 fires;
- any K1–K3 stop;
- the M2c review;
- M2d start;
- any change to MCC-v2, the tier rules, the primary representative scheme or the τ values
  after they are frozen;
- promoting a category 4 or 5 result to a "novel family" or "classification error"
  statement;
- adding a contract claim;
- anything published or sent outside this machine.
