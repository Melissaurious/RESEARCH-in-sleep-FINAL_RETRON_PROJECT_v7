# BENCHMARK DESIGN — SPIRE/Toro de novo ncRNA method on the project's retron population

**Status: FROZEN before any benchmark or pilot outcome was produced** (2026-09-18).
The freeze is proven by `tables/FREEZE.tsv`: sha256 of this file, of the selection script and of
the selected-set manifests, written before the first `run_set` call. Nothing below was changed
after an outcome was seen; any later change is appended as a dated **Amendment** with its reason.

Exploratory analysis, not a governed gate (same status as `analysis/dbchar_rt_ncrna_workbench/`).
WA-A.4: counts are measured, interpretation is `PROPOSED:`. WA-G.5: null results land.

## 1 · Question

> Given RT systems already identified by our pipeline, can comparative sequence/structure
> analysis of homologous systems recover retron ncRNAs independently of the existing CM call —
> first where an ncRNA is already known (positive recovery benchmark), then in high-confidence
> retron systems where the CM route has no call (discovery pilot)?

SPIRE is evaluated **only as an ncRNA method**. Population, identifiers, system confidence,
genomic context, homolog grouping inputs and reference ncRNAs all come from the project's
registered derived data. No SPIRE RT HMM, classifier, enrichment or novelty step is run.

## 2 · Population (from `scripts/s01_master_table.py`)

Unit: **physical locus** with ≥ 1 first-copy `file_label = 'Retron'` record (563,701).
Three independent fields per row:

| field | values | source |
|---|---|---|
| `nc_status` | `A_T3`, `A_T2`, `A_T1`, `A_NONCANON`, `B_NO_CM_CALL` | best existing placement, workbench tier predicates verbatim |
| `evidence_stratum` | S1 system context, 2 tools · S2 system context, 1 tool · S3 fused-RT rule only · S4 PADLOC ncRNA-dependent rule only · S5 sequence only | `rt_tool_calls_v1` + the tools' own rule files |
| `suitability` | `OK` or a `C_*` reason | method requirements (§4) |

Evidence strata were derived from the rule files, not from outcomes:
DefenseFinder retron models never use an ncRNA; PADLOC `Ec107-like` and `outgroup` require
RT + ncRNA (min_total 2, ncRNA the only secondary gene), so S4 is **not independent of the CM
route** and is excluded from both cohorts; `I-C`, `VII-A1`, `XI`, `XII` fire on the RT
protein alone in both tools (S3); every other type needs RT + ≥ 1 accessory protein (S1/S2).

`B_NO_CM_CALL` means *no current ncRNA call* — never "negative".

## 3 · Blinding (anti-circularity)

The predictor receives only: the RT anchor (start codon, strand), the RT-relative window
definition of §4, and the homolog-set membership of §5. It never receives `ref_*` columns
(ncRNA coordinates, sequence, CM model, E-value) or `detection_model`.
Set formation uses protein clusters and tool type labels only. PADLOC labels that consume the
ncRNA (`Ec107-like`, `outgroup`) are excluded from type labels.
Reference ncRNAs are joined **after** all predictions are written and hashed
(`tables/PREDICTIONS_FROZEN.tsv`). Parameters are global; nothing is tuned per set or system.

Selection of *positive* sets does use `nc_status` (a positive benchmark must contain
positives). It does not use reference position, length or window coverage; those are
reported as strata only.

## 4 · Window (SPIRE-faithful)

SPIRE 04 extracts a fixed window immediately 5′ of the RT start codon, on the RT strand
(reverse-complemented for `-` RTs), with no CDS masking. 07's documented input is 300 bp
(04 defaults to 270, and 600 is mentioned). **Frozen: 300 nt, RT-relative positions −300…−1**
(position 0 = first base of the start codon).

`suitability = OK` requires valid RT coordinates, RT inside the record window, the full
window inside the stored record window, and an unambiguous RT/system identity. Loci failing
any of these are recorded as `C_*`, never dropped silently.

## 5 · Homolog sets (SPIRE step not scripted; rule declared here)

SPIRE groups upstream windows per "lineage" (its classification group) and hand-picks ≤ 40.
Our ncRNA-blind analogue, from protein sequence only (`s02`):

- homolog set key = **RT50 cluster** (mmseqs easy-cluster, ≥ 50 % id, ≥ 80 % cov, cov-mode 0)
  over the 78,287 exact RTs in the master table;
- within a set, **one locus per RT90 cluster** (≥ 90 % id) and **no identical windows**, so a
  set is not 40 copies of one strain variant;
- members ordered by `sha256("spire-bench-v1|" + physical_locus_key)`; first ≤ 40 kept;
- **minimum 5 members**; otherwise `C_INSUFFICIENT_HOMOLOGS`.

A set's type label is the modal member type label (descriptor only).

## 6 · Cohorts

### 6.1 Positive recovery benchmark (`POS`)
Member pool: `nc_status ∈ {A_T3, A_T2}`, `suitability = OK`, stratum ∈ {S1, S2, S3},
no type-label conflict. For each type label, up to **3** eligible RT50 sets in hash order.
Two additional descriptive sets from S5 (sequence-only) A loci, reported separately.

### 6.2 Discovery pilot (`PIL`) — run only after `POS` predictions are frozen
Member pool: `B_NO_CM_CALL`, `suitability = OK`. Strata, up to **5 sets each**, round-robin
over type labels in hash order:

| stratum | members | RT50 set also contains A loci? |
|---|---|---|
| `PIL_S12_HOMOLOG_HAS_CM` | S1/S2 | yes |
| `PIL_S12_ORPHAN` | S1/S2 | no |
| `PIL_S3_FUSED` | S3 | either |
| `PIL_S5_SEQONLY` | S5 | either |

Pilot sets contain **only B loci**; no A window enters a pilot alignment. For
`PIL_S12_HOMOLOG_HAS_CM`, where homologs' CM-call positions are revealed only after pilot
predictions are frozen, they serve as a positional-concordance check.

### 6.3 Controls (same pipeline, same parameters)

| control | windows | purpose |
|---|---|---|
| `CTRL_DISTAL` | RT-relative −1500…−1201, same POS members | positional specificity: is the signal RT-proximal? |
| `CTRL_INTRAGENIC` | +300…+599 (inside the RT CDS), same POS members | false-structure rate on coding sequence |
| `CTRL_NONRETRON` | −300…−1 of RVT-AbiK / RVT-AbiP2 loci, same set rules | homologous RT groups with no retron system evidence |

Deliberately **not** used: strand-reversed windows. Watson–Crick covariation is invariant
under reverse complement, so a reversed window keeps the covariation signal and would not
measure a false-positive rate for this method. Shuffled windows are also excluded:
R-scape's null already comes from phylogeny-aware simulation of the given alignment.

## 7 · Arms (same sets, same windows)

| arm | alignment | structure / test |
|---|---|---|
| **A** SPIRE reconstruction | mLocARNA 2.0.1, verbatim 07 flags | alifold consensus (`--alifold-cons`); R-scape 2.0.4.a one-set test `-E 0.05` |
| **B-struct** | *the same* mLocARNA alignment | R-scape `--cacofold -E 0.05` |
| **B-seq** | MAFFT 7.525 L-INS-i (`--localpair --maxiterate 1000`), no structure used | R-scape `--cacofold -E 0.05` |

A vs B-struct isolates structure inference; B-struct vs B-seq isolates the alignment.
B-seq exists because CaCoFold's covariation evidence should not depend on an alignment that
was itself built to maximise predicted base pairing.

## 8 · Prediction rule (declared; SPIRE assigns no boundary)

Per set and arm:

1. **Set signal** (SPIRE's criterion, made explicit): ≥ 1 significantly covarying pair
   (R-scape E < 0.05) **and** observed/expected covarying base pairs ≥ 1.1, both read from
   R-scape's stdout for the structure the arm tests.
2. **Power flag**: `LOW_POWER` when expected covarying pairs < 1 — too little sequence
   diversity for covariation to be observable. This is recorded; it does not change 1.
3. **Supported region**: the union extent (min left … max right alignment column) of R-scape
   helices (`.helixcov` RMs) with `nbp_cov ≥ 1`.
4. **Member prediction**: the ungapped span of that member inside the supported region,
   converted to RT-relative coordinates. No nucleotides in the region → member abstention.
5. Secondary, reported separately: `STRUCT_ONLY` span = extent of all consensus pairs,
   whatever their covariation (separates structure from evolutionary evidence).

Predicted strand = RT strand (the window is RT-oriented).

## 9 · Evaluation (reference revealed after freeze)

Frame: RT-relative, RT-sense orientation. Reference = the locus's existing best placement
(`ref_nc_start`/`ref_nc_end`) from the master table.

Metrics per member: nt overlap, IoU, Dice, 5′ error, 3′ error (signed, nt), predicted length
minus reference length, strand correctness, reference contained in prediction, prediction
contained in reference, reference fraction inside the window, set covariation support.

**Categories (mutually exclusive, never merged):**

| category | rule |
|---|---|
| `existing pair rediscovered` | call made, IoU ≥ 0.5 |
| `existing pair predicted with altered boundary` | call made, overlap ≥ 1 nt, IoU < 0.5 |
| `existing pair not rediscovered` | call made, zero overlap |
| `method abstention` | no set signal, or member has no nucleotide in the supported region |
| `system unsuitable for this method` | `C_*`, or reference entirely outside the window |
| `new candidate in previously ncRNA-negative system` | pilot only: call made in a `B` locus |

Three levels are reported separately and never collapsed:
**detection** (set signal), **region** (overlap ≥ 1 nt), **boundary** (IoU ≥ 0.5 and |5′|, |3′| ≤ 20 nt).

Baseline `P0_POSITIONAL`: one fixed RT-relative interval = median reference 5′ and 3′ of `A_T3`
loci that are in **no** benchmark set. It is a yardstick for "the ncRNA is usually just
upstream", not a method.

## 10 · Pilot candidate evidence (post-freeze)

For each pilot member call: conserved RT-relative position across the set's members; orientation;
recurrence across members; number of covarying pairs and R-scape E-values; power; helix
count; overlap with annotated CDS in the record (`rt_window_cds_v1`); Infernal `cmsearch`
of `padlocdb.cm` on the member window with reporting threshold E ≤ 10 (was the CM merely
sub-threshold?); RNAfold MFE of the member span; agreement across arms A / B-struct / B-seq;
and, for `PIL_S12_HOMOLOG_HAS_CM`, distance to homologs' CM positions.
Candidates are **computational candidates**, never "validated retron ncRNAs".

## 11 · Bounds

POS ≤ ~55 sets, PIL ≤ 20 sets, controls as above; all local; ≈ 25 s per mLocARNA set.
No catalogue-scale run. No change to CM annotations, the pair dataset, or embeddings.

---

## Amendment 1 — 2026-09-18, after harness testing on 2 sets, before any aggregate outcome

**Trigger.** While debugging the harness on `POS_IX_1` and `POS_XIII_1` (reference coordinates
not joined), `POS_XIII_1` Arm A showed 24 significantly covarying pairs with observed/expected
= 24 / 22.6 = 1.06. So SPIRE's "> 1.1×" criterion (§8.1) rejects a set whose covariation
roughly equals what R-scape's power analysis predicts for a real structure. In R-scape's own
reading, observed ≈ expected *supports* a structure; SPIRE's 1.1 demands more covariation than
power predicts.

**Change.** None to the primary rule, which stays SPIRE's. A **sensitivity rule `SENS_ANY_COV`**
is added and reported beside it, never in place of it: set signal = ≥ 1 significantly covarying
pair (E < 0.05), with no ratio requirement. Region, projection and categories are otherwise
identical. Both rules are applied to every cohort, controls included, so the sensitivity rule's
false-signal rate is measured on the same footing.

## Amendment 2 — 2026-09-18, before any CTRL_GII_HARD output existed

**Trigger.** The operator-named Rfam negative set (1,230 structured ncRNAs incl. Group-II intron)
was located (`docs/BLOCKED.md`, 2026-09-18) but carries no RT anchor, so it cannot enter an
RT-anchored comparative method. Its scientific purpose — structured RNA that is *not* a retron
ncRNA — can be served inside the method by RT-anchored group II intron loci.

**Change.** Add `CTRL_GII_HARD`: up to 3 sets from the project's `RVT-GII` loci (first 5,000
eligible physical loci in hash order, RT50/RT90 clustered, identical set rules and arms;
`scripts/s03b_gii_control.py`). Expected: real covariation. A signal here demonstrates that
R-scape/CaCoFold significance does not by itself identify a retron ncRNA. The Rfam set is not
used; no controls were dropped.

The 977-ncRNA set could not be located (see `docs/BLOCKED.md`); the positive reference is the
project's own `A_T3/A_T2` placements, with the subset matching the 175 published, experimentally
characterised retron ncRNAs (blastn ≥ 90 % identity over ≥ 80 % of the published length) tagged
`previously_validated` for evaluation only.
