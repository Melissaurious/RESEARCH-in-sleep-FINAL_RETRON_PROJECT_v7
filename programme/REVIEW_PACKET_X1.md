---
record: REVIEW_PACKET_X1
date: 2026-09-20
purpose: manual scientific review of T-X1 before freeze
status: DRAFT — not frozen, not executed, primary endpoint untouched
---

# Review packet — T-X1 Buffington reconciliation

## 1 · Paths

`SYN = /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis`

| artefact | path |
|---|---|
| launcher | `$SYN/programme/tasks/T-X1-buffington-reconciliation/TASK_LAUNCHER.md` |
| implementation | `$SYN/programme/tasks/T-X1-buffington-reconciliation/x1_reconcile.py` |
| control results | `$SYN/ARIS_OUTPUT/x1_draft/tables/X1_controls.tsv` *(gitignored scratch)* |
| the source asset | `$SYN/references/rt0_rt7/buffington_2025/Discovery_and_engineering_of_retrons_supp.csv` |
| its provenance | `$SYN/references/rt0_rt7/buffington_2025/PROVENANCE.md` |
| registry row | `$SYN/programme/CANONICAL_DATASETS.tsv`, `BUFFINGTON2025_RETRON_CATALOGUE` |

**Nothing is frozen.** No commit pins this task yet, by design.

## 2 · What the catalogue is

105 rows · 8 columns · sha256 `d6836697…4e62` · Supplementary Table 1 of
`doi:10.1038/s41587-025-02879-3`. It contains **105 bioinformatically identified retron systems**,
each with an RT sequence, a **putative native msr-msd**, and a **modified msr-msd carrying the RFP
repair template**.

⛔ **It has no screening column and no activity column.** Membership is a computational
identification. **Experimental activity cannot be inferred from it.**

## 3 · Controls — 10 blocking, 10 PASS, 0.8 s

| control | expectation | observed |
|---|---|---|
| `X1_GATE_sha256_buffington` | `d6836697…4e62` | match |
| `X1_GATE_sha256_rt_exact_v1.faa` | `bcde6e9a…2655` | match |
| `X1_GATE_sha256_…pairs_v1.parquet` | `b89df680…3dae` | match |
| `X1_GATE_buffington_rows` | 105 | 105 |
| `X1_GATE_catalogue_counts` | 501,561 / 16,458 | match |
| `X1_POS_known_rt_found` | a catalogue sequence is found | found |
| `X1_NEG_shuffled_absent` | a composition-matched shuffle is not | absent |
| `X1_POS_stop_strip_separation` | `seq+"*"` **misses** raw, **hits** stripped | `raw=False stripped=True` |
| `X1_POS_orientation_probe` | forward matches; revcomp on its own axis | forward=True |
| `X1_GATE_no_untraced_active_claim` | refuses 1 of 3 fixture rows | refused=1 |

⛔ **None of these computes any Buffington × project overlap.** They probe the matcher with
sequences drawn from our own catalogue or built synthetically, so **the primary endpoint is
untouched** and remains available for the frozen run.

## 4 · The two design facts that shaped it

**Hash convention, verified not assumed.** The FASTA ids in `rt_exact_v1.faa` and
`rt_ncrna_oriented_v1.fna` **are** `sha256(UPPERCASE sequence)`. The ncRNA catalogue is stored
uppercase and **oriented**; the published msr-msd is lowercase and may be on either strand. Both
the sequence and its reverse complement are tested and **which one matched is landed**.

⛔ **A substring match on the nominated systems is wrong, and was caught in the draft.** `"Eco1"` is
a substring of `Eco17`, `Eco18`, `Eco10`–`Eco19` and matched **ten rows, none of them Eco1**. Under
exact matching on `Retron-<name>` / `<name>-RT`:

| Vap1 | Psp1 | Vro1 | Cko1 | Efe1 | Mva1 | **Eco1** |
|---|---|---|---|---|---|---|
| NRT-36 | NRT-39 | NRT-42 | NRT-45 | NRT-49 | NRT-83 | ⛔ **not in this 105-row catalogue** |

**Eco1 stays external** rather than being forced in. Its absence is a property of the published
table — unsurprising for a table of newly discovered systems when Eco1/Ec86 is the long-known one —
and it is **not** evidence that Eco1 is inactive or missing from our resource. It is landed in
`X1_operator_nominations.tsv`.

## 5 · The constraints, and where each is enforced

| constraint | enforcement |
|---|---|
| never merged into canonical populations | `X1_POS_populations_unchanged` re-counts 501,561 / 16,458 / 30,924 / 78,287 after the run |
| overlap is coverage, not validation | launcher §2, repeated in the implementation docstring |
| raw **and** stop-stripped RT hashes reported separately | two columns, two summary rows, plus `X1_POS_stop_strip_separation` |
| native vs engineered construct kept apart | only `Putative native msr-msd` is ever matched |
| absence = coverage gap in **our** resource | launcher §2, stated as a definition |
| experimental status is a separate axis from a traced source | `X1_GATE_no_untraced_active_claim`, blocking, fixture-tested |
| Vap1…Mva1 remain nominations | `OPERATOR_NOMINATED_UNTRACED`; cannot become `TRACED` without a source |
| `PAIR-ELIG` not reinterpreted as pairing evidence | read only for combination presence; stated in §2 |
| no cross-pair / orthogonality inference | launcher §9 |

## 6 · What this asks you to decide

1. Is the four-way overlap classification the right cut, or should
   `RT_AND_NCRNA_PRESENT_PAIR_ABSENT` collapse into `RT_PRESENT_NCRNA_DIFFERS`?
2. Is reading the exact-pair list for **combination presence** acceptable, given `PAIR-ELIG` is
   exhausted for pairing *inference*?
3. ⚠️ **Axis B cannot be populated from this catalogue at all.** Should X1 still carry the column —
   recording six nominations as untraced and Eco1 as external — or should Axis B be deferred
   entirely to a source-tracing task?
4. Freeze and run?

## 7 · Implementation summary

`x1_reconcile.py`, ~380 lines, two modes (`--mode controls` / `--mode primary`).

| step | what it does |
|---|---|
| gates | sha256 of the Buffington CSV, `rt_exact_v1.faa` and the pair parquet; 105 rows; 501,561 / 16,458 counts |
| **Axis A** | per published row: `sha256(UPPER(RT as published))` **and** `sha256(UPPER(RT minus trailing '*'))`; `sha256(UPPER(native msr-msd))` **and** `sha256(UPPER(revcomp(native msr-msd)))`; membership tested against the catalogue id sets and the exact-pair set |
| classification | `PAIR_EXACT_PRESENT` · `RT_AND_NCRNA_PRESENT_PAIR_ABSENT` · `RT_PRESENT_NCRNA_DIFFERS` · `EXTERNAL_NEW` |
| **Axis B** | exact-name resolution of the seven nominations; everything else `EXPERIMENTAL_STATUS_UNKNOWN`; `experimental_source` is written **empty**, because this catalogue supplies none |
| post-run | re-counts every population to prove nothing was written |

**Hash convention** is the project's own, verified by recomputation: the FASTA ids in
`rt_exact_v1.faa` and `rt_ncrna_oriented_v1.fna` **are** `sha256(UPPERCASE sequence)`.

### 7a · Raw vs terminal-stop-stripped RT matching

**104 of 105** published RTs end in `*`; the project catalogue has **zero**. Both hashes are
computed, **both are landed as separate columns**, and **both appear as separate summary rows**
(`rt_present_by_RAW_hash`, `rt_present_by_stopstripped_hash`). Neither silently substitutes for the
other. `X1_POS_stop_strip_separation` proves the distinction is live: `seq+"*"` **misses** the raw
hash and **hits** the stripped one.

### 7b · Native msr-msd orientation matching

The project ncRNA catalogue is stored **uppercase and oriented**; the published msr-msd is
**lowercase and may be on either strand**. Both `sha256(UPPER(seq))` and
`sha256(UPPER(revcomp(seq)))` are tested, and **which one matched is landed** in `msr_orientation`
∈ `FORWARD` · `REVCOMP` · `NO_MATCH`.

### 7c · ⛔ The engineered construct is handled separately

| published column | treatment |
|---|---|
| `Putative native msr-msd` | **the only sequence ever matched** |
| `msr-msd with a 81nt RFP repair template (…)` | ⛔ **never matched, never pooled, never counted toward coverage** |

The difference between the two is an **`ENGINEERED_DELTA`** and is out of scope for X1 entirely —
it belongs to `T-R2`, and only after the construct design is verified.

## 8 · Expected outputs

| file | rows | contents |
|---|---|---|
| `X1_row_classification.tsv` | **105** | both axes: overlap class, `rt_raw_hash_hit`, `rt_stopstripped_hash_hit`, `rt_is_retron_family`, `msr_forward_hit`, `msr_revcomp_hit`, `msr_orientation`, `pair_exact_present`, `experimental_status`, `experimental_source`, `operator_nominated_as` |
| `X1_hashes.tsv` | **105** | `rt_raw_sha256`, `rt_stopstripped_sha256`, `msr_forward_sha256`, `msr_revcomp_sha256`, lengths |
| `X1_operator_nominations.tsv` | **7** | how each of Vap1/Psp1/Vro1/Cko1/Efe1/Mva1/**Eco1** resolved, **including the one that resolves to nothing** |
| `X1_summary.tsv` | ~12 | class counts; RT present by raw **vs** stop-stripped **separately**; msr forward vs revcomp; nominated vs traced |
| `X1_controls.tsv` | 12 | 10 pre-run + 2 post-run |

## 9 · STOP conditions

| condition | action |
|---|---|
| any input sha256 mismatch | **STOP** before matching |
| not exactly 105 Buffington rows | **STOP** |
| catalogue counts ≠ 501,561 / 16,458 | **STOP** |
| any blocking control fails | **STOP**, `TASK_STATE: VOID`, no primary table, escalate, **new task ID** |
| a population count changes after the run | **STOP** — something was written that should not have been |
| a row would be `EXPERIMENTAL_SOURCE_TRACED` with an empty source | **STOP** — the gate refuses it |

## 10 · ⛔ Explicit confirmation: experimental activity is NOT inferred

**Supplementary Table 1 has 8 columns and none is a screening or activity column** — verified on
ingestion, listed in `PROVENANCE.md`. Membership is a **bioinformatic identification**.

- `experimental_source` is written **empty for all 105 rows**, because the catalogue supplies none.
- `X1_GATE_no_untraced_active_claim` **refuses** any row marked `EXPERIMENTAL_SOURCE_TRACED` with an
  empty source — blocking, fixture-tested, refusing 1 of 3 fixture rows.
- **Vap1 · Psp1 · Vro1 · Cko1 · Efe1 · Mva1** → `OPERATOR_NOMINATED_UNTRACED`. Resolved by **exact**
  name match to NRT-36, 39, 42, 45, 49, 83. **None is labelled active.**
- **Eco1** → ⛔ **`NOT_IN_THIS_CATALOGUE`**, landed as its own row. It stays **external to the 105**
  rather than being forced in. A substring match would have wrongly attached it to Eco17 — it
  matched **ten** rows, none of them Eco1.
