---
task_id: T-X1-buffington-reconciliation
governance_base: 9a793c9
base_commit: 0a220e3
base_branch: project-synthesis
stage_id: S00
title: Exact-sequence reconciliation of the Buffington 2025 retron catalogue against project populations
state: DRAFT_AWAITING_SCIENTIFIC_REVIEW
autonomy_tier: A
compute_class: CPU_SMALL
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-X1-buffington-reconciliation
branch: task/T-X1-buffington-reconciliation
output_directory: analysis/t_x1_buffington_reconciliation/
hard_dependencies: []
populations_touched: ["BUFFINGTON2025_RETRON_CATALOGUE :: EXTERNAL", "RT-EXACT-501561 :: READ-ONLY coverage check", "NCRNA-16458 :: READ-ONLY", "EXACT-BIPARTITE-COMPONENTS-14918 :: not used"]
population_state: EXTERNAL_COMPARISON_ONLY — merges nothing, spends no endpoint
confirmatory_spend: none
iteration_budget: 1
frozen: false
freeze_rule: WORKING_RULES §6b — NOT YET FROZEN
operator_authorisation: proposal approved 2026-09-20; drafting only; execution NOT authorised
---

# T-X1 · Buffington 2025 reconciliation

⛔ **DRAFT.** Not frozen, not dispatched, the primary reconciliation has **not** run. Only the
**controls** have executed — they touch no primary endpoint, and are reported in §7.

## 1 · The question

> Of the **105** retron systems published by Buffington *et al.* 2025, which RTs — and which
> RT + native msr-msd combinations — are **already present** in this project's resource, and which
> are **external to it**?

## 2 · ⛔ Interpretation ceiling

This is a **descriptive coverage check on our resource**. It is:

- **not biological validation, in either direction;**
- ⛔ **a published system absent from our catalogue is a MEASURED COVERAGE GAP IN OUR RESOURCE — it
  is not evidence that the publication is wrong;**
- ⛔ **a system present here is not thereby experimentally validated;**
- **not** a cross-pair compatibility or orthogonality inference of any kind — Stage 12 stays closed;
- **not** a merge. `BUFFINGTON2025_RETRON_CATALOGUE` remains an **external published catalogue** and
  is never merged into `RT-EXACT-501561`, `NCRNA-16458`, `PAIR-ELIG-30924` or `PANEL-175`.

⛔ **`PAIR-ELIG` is not consumed or reinterpreted as confirmatory pairing evidence.** The pair list
is read **only** to answer *"is this published combination already in our resource"* — a coverage
question about a file, not a claim that pairing works, was tested, or transfers.

## 3 · Inputs — all read-only

| input | path / hash | role |
|---|---|---|
| `BUFFINGTON2025_RETRON_CATALOGUE` | `references/rt0_rt7/buffington_2025/…_supp.csv`, `d6836697…4e62` | the 105 published systems |
| `RT-EXACT-501561` | `rt_exact_v1.faa`, `bcde6e9a…2655` | RT coverage target |
| `NCRNA-16458` | `rt_ncrna_oriented_v1.fna` | msr-msd coverage target |
| exact pair list | `rt_ncrna_exact_pairs_v1.parquet`, `b89df680…3dae` | ⚠️ combination-presence only, §2 |
| `RT-FAMILY-LABELS-613` | `rt_family_baseline_v1.parquet` | the `Retron` subset, 78,287 |

**Hash convention, verified at design time, not assumed:** the FASTA ids in both
`rt_exact_v1.faa` and `rt_ncrna_oriented_v1.fna` **are** `sha256(UPPERCASE sequence)`. Confirmed by
recomputation against the first record of each file.

## 4 · Axis A — sequence overlap

### 4a · ⛔ Raw and stop-stripped RT hashes are reported SEPARATELY

**104 of the 105 published RT sequences end in `*`.** The project catalogue has **zero** trailing
stops. Two hashes are therefore computed and **both are landed**:

| column | definition |
|---|---|
| `rt_raw_sha256` | `sha256(upper(sequence exactly as published))` |
| `rt_stopstripped_sha256` | `sha256(upper(sequence with trailing '*' removed))` |

⛔ **Neither silently substitutes for the other, and both counts appear in the summary.** This
project has already published a wrong count from exactly this — a 10 that was really a 4, because
*"10 requires stripping a trailing `*`, never disclosed."* Control `X1_POS_stop_strip_separation`
makes the distinction machine-checked.

### 4b · ⛔ Native msr-msd and the engineered construct stay separate

| published column | treatment |
|---|---|
| `Putative native msr-msd` | **the only sequence used for ncRNA matching** |
| `msr-msd with a 81nt RFP repair template (…)` | ⛔ **engineered construct. Hashed if at all, never matched, never pooled with the native sequence, and never counted toward coverage** |

### 4c · Orientation

The project ncRNA catalogue is **oriented**; a published msr-msd may be on either strand. Both
`sha256(upper(seq))` and `sha256(upper(revcomp(seq)))` are tested, and **which one matched is
landed** in `msr_orientation` ∈ {`FORWARD`, `REVCOMP`, `NO_MATCH`}.

### 4d · Classification, one per published row

| class | meaning |
|---|---|
| `PAIR_EXACT_PRESENT` | RT **and** its native msr-msd match, **and** that combination is already in our exact pair list |
| `RT_AND_NCRNA_PRESENT_PAIR_ABSENT` | both sequences present, the **combination** is not |
| `RT_PRESENT_NCRNA_DIFFERS` | RT matches, the native msr-msd does not |
| `EXTERNAL_NEW` | neither present — **a coverage gap in our resource** |

## 5 · Axis B — experimental status, a genuinely separate evidence axis

⛔ **Axis B is NOT computable from this catalogue, and the task will say so rather than guess.**
Verified on ingestion: Supplementary Table 1 has **8 columns, none of which is a screening or
activity column**. Membership in the table is a **bioinformatic identification**.

| value | meaning |
|---|---|
| `EXPERIMENTAL_SOURCE_TRACED` | an identifiable experimental **table / figure / citation** is recorded in `experimental_source` |
| `OPERATOR_NOMINATED_UNTRACED` | the operator named it; **no source traced yet; NOT labelled active** |
| `EXPERIMENTAL_STATUS_UNKNOWN` | default |

⛔ **Blocking gate `X1_GATE_no_untraced_active_claim`:** a row marked `EXPERIMENTAL_SOURCE_TRACED`
with an empty `experimental_source` **fails the task**. Tested against a three-row fixture: one
violating row is refused, one with a source and one `UNKNOWN` are accepted.

### 5a · The operator's seven named systems — resolved EXACTLY, and one is absent

Resolution is by **exact** match on `Retron I.D. == "Retron-<name>"` or `Name (RT) == "<name>-RT"`.

| nominated | resolves to |
|---|---|
| Vap1 | `NRT-36` |
| Psp1 | `NRT-39` |
| Vro1 | `NRT-42` |
| Cko1 | `NRT-45` |
| Efe1 | `NRT-49` |
| Mva1 | `NRT-83` |
| **Eco1** | ⛔ **NOT_IN_THIS_CATALOGUE** |

⚠️ **A substring test was tried at design time and is wrong.** `"Eco1"` is a substring of `Eco17`,
`Eco18`, `Eco10`–`Eco19`, and matched **ten rows, none of which is Eco1**. Under exact matching
Eco1 is absent from this table entirely — unsurprising if Supplementary Table 1 lists *newly
discovered* systems, and Eco1/Ec86 is the long-known one. **Naming is not identity**, and the
implementation uses exact matching for this reason.

⛔ **Eco1's absence is a property of the published table. It is not evidence that Eco1 is
inactive, does not exist, or is missing from our resource.** It is landed explicitly in
`X1_operator_nominations.tsv` rather than passed over in silence.

⛔ **None of the seven is labelled active by this task.** All six that resolve are recorded
`OPERATOR_NOMINATED_UNTRACED`. Tracing them needs an experimental source from elsewhere — that is
`T-A23d`'s shape of work, not this task's.

## 6 · Outputs

| file | contents |
|---|---|
| `X1_row_classification.tsv` | 105 rows: both axes, both RT hash hits, msr orientation, pair presence, `operator_nominated_as` |
| `X1_hashes.tsv` | 105 rows: **raw and stop-stripped RT sha256, forward and revcomp msr sha256** |
| `X1_operator_nominations.tsv` | the seven nominations and how each resolved, **including the unresolved one** |
| `X1_summary.tsv` | class counts; RT present by raw vs stop-stripped hash **separately**; msr forward vs revcomp; nominated vs traced |
| `X1_controls.tsv` | §7 |

## 7 · Controls — **10 blocking, 10 PASS, 0.8 s**, executed without touching the primary endpoint

| control | type | expectation | observed | state |
|---|---|---|---|---|
| `X1_GATE_sha256_buffington` | positive | `d6836697…4e62` | match | **PASS** |
| `X1_GATE_sha256_rt_exact_v1.faa` | positive | `bcde6e9a…2655` | match | **PASS** |
| `X1_GATE_sha256_…pairs_v1.parquet` | positive | `b89df680…3dae` | match | **PASS** |
| `X1_GATE_buffington_rows` | positive | 105 data rows | 105 | **PASS** |
| `X1_GATE_catalogue_counts` | positive | 501,561 RT / 16,458 ncRNA | match | **PASS** |
| `X1_POS_known_rt_found` | positive | a sequence taken **from** the catalogue is found | found | **PASS** |
| `X1_NEG_shuffled_absent` | negative | a composition-matched shuffle is **not** found | absent | **PASS** |
| `X1_POS_stop_strip_separation` | positive | `seq+"*"` **misses** raw, **hits** stop-stripped | `raw=False stripped=True` | **PASS** |
| `X1_POS_orientation_probe` | positive | forward matches; revcomp reported on its own axis | forward=True | **PASS** |
| `X1_GATE_no_untraced_active_claim` | positive | refuses 1 of 3 fixture rows | refused=1 | **PASS** |

**Why these could run now:** every control probes the *matcher* using sequences drawn from our own
catalogue or constructed synthetically. **None computes any Buffington × project overlap**, which
is the primary endpoint. The endpoint is untouched.

### 7a · On the primary run

| control | type | blocking |
|---|---|---|
| `X1_POS_populations_unchanged` | positive | **YES** — after the run the populations still count 501,561 / 16,458 / 30,924 / 78,287. **T-X1 merges nothing** |
| `X1_GATE_no_untraced_active_claim_primary` | positive | **YES** — no landed row is `TRACED` without a source |

## 8 · STOP conditions

| condition | action |
|---|---|
| any input hash mismatch | **STOP** before matching |
| any blocking control fails | **STOP**, `TASK_STATE: VOID`, no primary table, escalate, **new task ID** |
| a population count changes | **STOP** — something was written that should not have been |
| a row would be `TRACED` with no source | **STOP** — the gate refuses it |

## 9 · What this task may NOT conclude

Anything about orthogonality, compatibility, interchangeability or cross-pair function. Anything
about whether a published system works. Anything about whether our resource is *correct* — only
about what it **contains**.
