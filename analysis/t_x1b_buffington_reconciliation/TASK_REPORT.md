# TASK REPORT — T-X1b-buffington-reconciliation

TASK_STATE: PASS
SCIENTIFIC_OUTCOME: DESCRIPTIVE
CRITERION: "Of the 105 retron systems published by Buffington et al. 2025, which RTs — and which RT + native msr-msd combinations — are already present in this project's resource, and which are external to it?"
MET: yes — 105/105 classified, 14/14 blocking controls PASS, every population unchanged.

## Consumable outputs

`tables/X1_row_classification.tsv` · `tables/X1_hashes.tsv` ·
`tables/X1_operator_nominations.tsv` · `tables/X1_summary.tsv` · `tables/X1_controls.tsv` ·
`logs/run_log.json` · `OUTPUT_MANIFEST.sha256`

⚠️ **With the labelling caveat in §Limitations, which a consumer must read before using
`overlap_class`.**

---

## Methods-ready summary

**Population / inference unit.** `BUFFINGTON2025_RETRON_CATALOGUE` — **105 published systems**,
Supplementary Table 1 of `doi:10.1038/s41587-025-02879-3`. **Unit: one published retron system.**
The project populations are read-only comparison targets, never merged.

**Software.** Python 3.12.12 (`retron_tradicional`), stdlib `hashlib`/`csv`, `pyarrow`. Local
workstation, ≤2 threads, `nice -n 10`, concurrent with the `T-P1b` full run and non-contending.

**Parameters, fixed at freeze `3d35167`.** Hash convention `sha256(UPPERCASE sequence)` — verified,
not assumed: the FASTA ids in `rt_exact_v1.faa` and `rt_ncrna_oriented_v1.fna` **are** that digest.
RT matched on **two** hashes, raw and terminal-`*`-stripped, reported separately. Native msr-msd
matched **forward and reverse-complement**. Family join bound **explicitly** to `family_label`.

**Controls — 14 blocking, 14 PASS.** Three input hashes; row and catalogue counts; a known-present
positive; a composition-matched shuffled negative; the stop-strip separation probe; the orientation
probe; ⛔ **`X1b_GATE_family_join_retron_count` → 78,287** and **`X1b_GATE_family_vocabulary_size` →
42** (the gates whose absence voided `T-X1`); the untraced-active-claim gate; and two post-run
gates — populations unchanged, and no `TRACED` row without a source.

**Analysis method.** Exact set membership on sha256 digests. **No alignment, no model, no
statistics.**

---

## Results-ready summary

**Denominator: 105 published systems.**

### Principal measurements

| quantity | value | denominator |
|---|---|---|
| RT present by **stop-stripped** hash | **56** | 105 |
| ⛔ RT present by **raw** hash | **0** | 105 |
| `PAIR_EXACT_PRESENT` (RT **and** native msr-msd **and** the combination) | **5** | 105 |
| `RT_PRESENT_NCRNA_DIFFERS` | **51** | 105 |
| `EXTERNAL_NEW` *(see the caveat)* | **49** | 105 |
| native msr-msd present, **forward** | **11** | 105 |
| native msr-msd present, **revcomp** | **0** | 105 |
| operator nominations, untraced | **6** | 105 |
| ⛔ experimental sources **traced** | **0** | 105 |

### ⭐ The headline is the one that nearly wasn't measurable

**0 of 105 RTs match on the raw published sequence. 56 of 105 match once the trailing `*` is
stripped.**

104 of the 105 published RTs end in `*`; the project catalogue has none. **A raw-hash-only
implementation would have reported "0 of 105 present" — a completely false coverage gap**, and a
plausible-sounding one. This project has already published a wrong count from exactly this trap: a
10 that was really a 4, *"because 10 requires stripping a trailing `*`, never disclosed."*
Reporting both hashes separately was the whole point, and it is what makes the 56 trustworthy.

**All 56 RT matches carry `family_label == "Retron"`** — 56 of 56. The published RTs that our
resource contains are labelled retrons in it.

### Coverage, stated as what it is

Our resource already contains **56 of 105 (53.3%)** of these published RT sequences exactly, but
only **5 of 105 (4.8%)** of the full RT + native-msr-msd combinations. **51 systems share an RT with
our resource while their native msr-msd differs from anything we hold.**

⛔ **This is a measured property of our resource, not of the publication.** A system absent here is
a **coverage gap in our catalogue**; it is not evidence that the publication is wrong, and a system
present is **not** thereby experimentally validated.

### Uncertainty

Not applicable — exact digest matching. No estimate, no interval.

### Limitations

⛔ **`EXTERNAL_NEW` is imprecise for 6 of its 49 rows.** The launcher defines it as *"neither
present"*, but the implementation assigns it whenever the **RT** is absent, regardless of the
ncRNA. **Six systems — `NRT-71`, `NRT-72`, `NRT-79`, `NRT-81`, `NRT-93`, `NRT-95` — have their
native msr-msd present in our resource while their RT is absent**, and are labelled `EXTERNAL_NEW`.

- **The underlying data is correct and landed.** `msr_forward_hit = True` and
  `rt_stopstripped_hash_hit = False` on those rows, so the true state is recoverable from
  `X1_row_classification.tsv` with no rerun.
- **The defect is the class name, not the measurement.** A consumer reading `overlap_class` alone
  would wrongly conclude our resource holds nothing for those six.
- **Correctly stated: 43 of 105 systems have neither sequence present; 6 have the ncRNA only.**
- Adding an `NCRNA_PRESENT_RT_ABSENT` class would be a **classification change, i.e. a new task**.
  It is not proposed, because the data is already there.

Other limitations: **n = 105** from one publication, not a sample of retrons · the engineered
RFP-repair-template construct was **never matched** and contributes nothing · `msr_present_revcomp
= 0` means the published native msr-msd is stored in the **same** orientation as our oriented
catalogue — the opposite of `T-R1b`'s RT-DNA, which was 81/81 reverse-complement, and consistent
with one being RNA-sense and the other its cDNA.

### ⛔ Interpretation ceiling

Coverage of **our** resource against **one** published catalogue. **Not** biological validation in
either direction. **Not** experimental activity — see below. **No** compatibility or orthogonality
inference; Stage 12 stays closed. **Nothing was merged** into any project population.

---

## ⛔ Experimental activity is not inferred

Supplementary Table 1 has **8 columns and none is a screening or activity column**.
`experimental_source` is **empty on all 105 rows**, and `experimental_source_traced = 0`.

| nomination | resolution |
|---|---|
| Vap1 · Psp1 · Vro1 · Cko1 · Efe1 · Mva1 | `NRT-36` · `39` · `42` · `45` · `49` · `83` — **`OPERATOR_NOMINATED_UNTRACED`, none labelled active** |
| **Eco1** | ⛔ **`NOT_IN_THIS_CATALOGUE`** — external to these 105, landed as its own row |

A substring match would have wrongly attached Eco1 to Eco17; exact matching is used.

## Populations touched

`BUFFINGTON2025_RETRON_CATALOGUE` (external) · `RT-EXACT-501561`, `NCRNA-16458`,
`RT-FAMILY-LABELS-613`, exact-pair list — **all read-only**. ⛔ **No endpoint spent.**
`X1_POS_populations_unchanged` re-verified **501,561 / 16,458 / 30,924 / 78,287** after the run.

## Outputs

| file | rows | sha256 (16) |
|---|---|---|
| `X1_row_classification.tsv` | 105 | `3a0b7fa73f789690` |
| `X1_hashes.tsv` | 105 | `c9cf795d03ecccc8` |
| `X1_operator_nominations.tsv` | 7 | `512f5e21f9d52d4b` |
| `X1_summary.tsv` | 9 | `7ba85e9db210bb3e` |
| `X1_controls.tsv` | 14 | `629c6a6c7acfe34d` |

## Provenance

| | |
|---|---|
| freeze commit | **`3d35167`** — launcher + implementation + controls, **before** this run |
| supersedes | `T-X1` (**VOID**), record `VOID_01_family_join_defect.md`. **Nothing inherited** |
| base | `project-synthesis@0a220e3` |
| inputs | Buffington `d6836697…4e62` · `rt_exact_v1.faa` `bcde6e9a…2655` · pairs `b89df680…3dae` |
| software | Python 3.12.12, pyarrow |
| backend | local workstation, ≤2 threads |
| elapsed | ~4 s |

⚠️ **Disclosure, `WORKING_RULES` §1.** Executed by the coordinating session under the operator's
standing authorisation, with `D4` unresolved. Role separation not achieved.

## Iterations

1 of 1. No criterion changed. The four corrections to `T-X1` were made **before** this task's
freeze, under a **new task identity**, never as a v2 in place.

## Nominations

1. **`EXTERNAL_NEW` should be split** — `NCRNA_PRESENT_RT_ABSENT` for the six. A new task if wanted.
2. **51 systems share an RT with our resource but not its native msr-msd.** Whether that is
   biological divergence or our ncRNA ascertainment is **not answerable here** — a candidate
   question for `T-R2`.
3. **All 56 RT matches are `family_label == "Retron"`.** Worth noting; not tested for significance.

## What this does not show

Nothing about experimental activity. Nothing about whether any published system works. Nothing
about compatibility, orthogonality or interchangeability. Nothing about whether our resource is
*correct* — only about what it **contains**. And nothing about the unresolved **613** vocabulary,
which was deliberately not consumed, interpreted or reconciled.
