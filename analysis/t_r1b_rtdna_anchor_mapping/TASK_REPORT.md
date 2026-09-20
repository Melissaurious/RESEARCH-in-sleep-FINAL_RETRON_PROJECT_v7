# TASK REPORT — T-R1b-rtdna-anchor-mapping

TASK_STATE: PASS
SCIENTIFIC_OUTCOME: DESCRIPTIVE
CRITERION: "For each of the 81 anchors, map the measured RTDNA_sequence against its own ncRNA_sequence; test both orientations; report exact vs near-exact separately; record coordinates, orientation, number of equally valid placements, mismatches/indels; and report an explicit unmapped/ambiguous state rather than forcing a result."
MET: yes — 81/81 mapped EXACT_UNIQUE, 10/10 blocking controls PASS, 0 forced results.

## Consumable outputs

- `tables/R1b_anchor_coordinates.tsv` — **the experimentally anchored RT-DNA→ncRNA coordinate
  table for the 81 elements. This is the deliverable, and it is what `T-R2` may consume.**
- `tables/R1b_summary.tsv`, `tables/R1b_controls.tsv`, `tables/R1b_ambiguous_and_unmapped.tsv`
  (0 rows), `logs/run_log.json`

---

## Methods-ready summary

**Population / inference unit.** `PANEL-RTDNA-81` — the 81 elements of the 175-element experimental
panel carrying a measured `RTDNA_sequence`. **Unit: one assayed retron element. n = 81 is the whole
population, not a sample.**

**Software.** Python 3.12.12 (`retron_tradicional`); Biopython **1.87** `Align.PairwiseAligner`.
Backend: local workstation, ≤2 threads, `nice -n 10`, non-contending with the concurrent `T-P1b`
run.

**Parameters, all fixed at freeze `7e7f598`.** Exact substring search first, returning **every**
occurrence. Both orientations always tested. Local alignment reached **only** if exact fails:
`mode="local"`, match `+2`, mismatch `−3`, gap open `−5`, gap extend `−2`. Near-exact floor
**coverage ≥ 0.90 AND identity ≥ 0.90** — a **predeclared conservative rescue criterion**, not a
claim that 0.90 is a biologically optimal boundary. Below either → `UNMAPPED`. Seed `20260920`
(fixtures only; the mapping is deterministic).

**Controls — 10 blocking, 10 PASS.** Three input gates (panel sha256; 175 rows / 81 anchors; all 81
carry an ncRNA), four synthetic positives (planted fragment recovered at exact coordinates; its
reverse complement recovered as `REVCOMP`; a fragment planted twice reported as **two** placements
with both coordinate sets; three planted substitutions detected as `NEAR_EXACT` with
`n_mismatch=3`), two synthetic negatives (an unrelated equal-length sequence → `UNMAPPED`; a
20 nt-real + 90 nt-random chimera → `UNMAPPED`), and one output gate (all 81 reported).

⛔ **No panel sequence reached the mapper during the control run** — verified by instrumenting
`map_one`: 6 invocations, 0 panel sequences, 2 synthetic subjects.

**Threshold justification.** A 400-pair synthetic negative sweep at panel-realistic lengths: **400
of 400 unrelated pairs `UNMAPPED`**, worst-case coverage **0.3875** against the 0.90 floor.
Unrelated noise reached **median identity 0.9231 and maximum 1.0000**, so an identity-only
criterion would admit most noise — which is why the rule is a conjunction.

**Analysis method.** Deterministic string matching and, where needed, Smith–Waterman local
alignment. **No statistical model, no training, no classifier, no tie-breaking.**

---

## Results-ready summary

**Denominator: 81 assayed retron elements** (of a 175-element panel; 103 of which carry a measured
production value — not used here).

### Principal measurements

| quantity | value | denominator |
|---|---|---|
| `EXACT_UNIQUE` | **81** | 81 |
| `NEAR_EXACT` | 0 | 81 |
| `UNMAPPED` | **0** | 81 |
| orientation `REVCOMP` | **81** | 81 |
| orientation `FORWARD` | **0** | 81 |
| orientation `BOTH_AMBIGUOUS` | 0 | 81 |
| multiple placements | **0** | 81 |

**Every one of the 81 measured RT-DNA sequences maps exactly, uniquely and unambiguously onto its
own ncRNA.** No rescue alignment was needed; no placement was ambiguous; nothing was forced.

⭐ **All 81 map in reverse-complement orientation, and none maps forward.** This is a fact about how
the panel represents the molecule — RT-DNA is reverse-transcribed from the msd and is therefore
complementary to the ncRNA as catalogued. ⚠️ **A forward-only implementation would have mapped
0 of 81** and could have been reported as a total failure of the anchor set. Testing both
orientations was not a formality.

### Descriptive coordinate geometry

| quantity | min | median | max |
|---|---|---|---|
| RT-DNA length / ncRNA length | 0.188 | 0.545 | 2.148 |
| nucleotides 5′ of the RT-DNA | 0 | 55 | 126 |
| nucleotides 3′ of the RT-DNA | 3 | 17 | 110 |

The RT-DNA occupies roughly **half** its ncRNA at the median, sits **internally** in all but one
case (one element is flush to the 5′ end; **none** is flush to the 3′ end), and always leaves at
least **3 nt** of 3′ ncRNA beyond it.

### Uncertainty

Not applicable. These are **exact string coordinates**, identity 1.0000 and coverage 1.0000 on all
81. There is no estimate and therefore no interval.

### Limitations

- **n = 81.** Counts only. No rate on a small base, and the panel is **not** a random sample of
  retrons.
- The ratio above 1.0 (max 2.148) means some RT-DNA is **longer** than the ncRNA field it maps
  into; as an exact substring match this reflects how the panel stores the two fields, and is
  **not** interpreted here.
- The uniform `REVCOMP` result is a **representational** fact about this panel. It is not evidence
  about any retron outside it.
- `pct_identity` and `pct_coverage` are 1.0 by construction on the exact path; they carry no
  information here.

### ⛔ Interpretation ceiling

**This is a lookup, not a model.** It establishes where 81 measured molecules lie on their own
ncRNAs. It infers **no general msr/msd boundary**, says **nothing** about the 16,458-sequence ncRNA
catalogue, and says **nothing** about retron function, activity, compatibility or orthogonality.
Generalisation is `T-R2`, which does not exist. **No machine learning was used and none is
licensed by this table.**

---

## Populations touched

`PANEL-RTDNA-81` · `analysis_family = rtdna_anchor_mapping` · ⛔ **SPENT.** Previously
`NOT_YET_EXPOSED`; now exposed for this endpoint. One authorisation, one task — this task is the
**D7 merge** of `T-A5b1` and `T-R1`, so the anchor set was spent **once**, not twice.

⚠️ **62 of these 81 are also `PANEL-PRODUCERS-67-36` positives.** `T-A22`'s feature set was frozen
**before** this run and its whitelist machine-refuses every anchor- and RT-DNA-derived column, so
this exposure cannot contaminate that comparison if it is ever reactivated.

## Outputs

| file | rows | sha256 (16) |
|---|---|---|
| `tables/R1b_anchor_coordinates.tsv` | 81 | `713237accf27e727` |
| `tables/R1b_summary.tsv` | 5 | `445c81293c179ca1` |
| `tables/R1b_controls.tsv` | 10 | `c1af6a7a27255760` |
| `tables/R1b_ambiguous_and_unmapped.tsv` | 0 | `c8a5985bf0b1b723` |

## Provenance

| | |
|---|---|
| freeze / preregistration commit | **`7e7f598`** — launcher + implementation + controls, **before** this run |
| base | `project-synthesis@0a220e3`; branch `task/T-R1b-rtdna-anchor-mapping` cut from `7e7f598` |
| input | `support.csv`, sha256 `80b2f565515c96bb1b9b0082c261dd6184c67672e29bb96c813cf6abdd9d9577` |
| software | Python 3.12.12, Biopython 1.87 |
| parameters | match +2 / mismatch −3 / gap −5,−2; `near_cov_min` 0.90; `near_id_min` 0.90 |
| backend | local workstation, ≤2 threads |
| elapsed | **0.1 s** |
| seed | 20260920 |

⚠️ **Disclosure, `WORKING_RULES` §1.** Executed by the **coordinating session**, not an independent
task session — `D4` unresolved, operator-authorised under mandatory disclosure. Role separation was
not achieved for this run.

## Iterations

1 of 1. **No criterion was changed at any point**, before or after seeing any result.

## Nominations

1. **All 81 in `REVCOMP`** — worth confirming against the panel's own documentation that this is
   the intended storage convention rather than an artefact of how the columns were assembled.
2. **Some RT-DNA exceeds its ncRNA field length** (ratio to 2.148) while still matching exactly —
   the two columns may not describe the same coordinate frame. For `T-R2`, not here.
3. **None of the 81 is flush to the ncRNA 3′ end**, minimum 3 nt remaining. A candidate landmark
   for `T-R2` to test, **not** a finding here.

## What this does not show

- Nothing about any retron outside these 81.
- **No msr/msd/a1/a2 boundary.** The RT-DNA extent is one piece of evidence toward architecture, at
  Tier A, and architecture is `T-R2`'s question.
- Nothing about function, activity or production — those columns exist in the panel and were **not
  read**.
- Nothing about the ncRNA catalogue, the exact-RT catalogue, or any pairing.
- The geometry in §Results is **descriptive of these 81 coordinate pairs**. It is not a model of
  retron ncRNA architecture and must not be read as one.
