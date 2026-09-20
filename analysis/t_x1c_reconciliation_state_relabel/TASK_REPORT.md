# TASK REPORT — T-X1c-reconciliation-state-relabel

TASK_STATE: PASS
SCIENTIFIC_OUTCOME: DESCRIPTIVE
CRITERION: "Consume the landed X1b Boolean measurements and derive exactly four mutually exclusive states, reproducing the predeclared counts 5 / 51 / 6 / 43, without rerunning sequence matching."
MET: yes — all four counts reproduced exactly; 8/8 blocking controls PASS; no sequence matching performed.

## Consumable outputs

`tables/X1c_reconciliation_states.tsv` — **the authoritative reconciliation state per published
system.** · `tables/X1c_state_counts.tsv` · `tables/X1c_controls.tsv` · `logs/run_log.json`

⛔ **These supersede `T-X1b`'s `overlap_class`, which is RETRACTED as an authoritative state
label.** It is carried alongside in the output, marked retracted, for traceability only.

---

## Methods-ready summary

**Population / inference unit.** One published retron system; 105 of them. ⛔ **No biological
population is opened.** The sole input is `T-X1b`'s landed `X1_row_classification.tsv`, pinned by
sha256 `3a0b7fa73f789690b1bc383c1717c33c3354d82b5e8bb3715fc0ddd0977cc0ce`.

**Software.** Python 3.12.12, stdlib only. Local, 1 thread, `nice -n 10`, concurrent with the
`T-P1b` full run and non-contending.

**Parameters.** None. `state_of(rt, ncrna)` is a total function on two Booleans.

**Controls — 8 blocking, 8 PASS.** Source sha256 (**asserting**, with a negative test proving it
returns `VOID` on a wrong hash) · 105 source rows · the four states sum to 105 · **each of the four
predeclared counts** · both axis totals carried through unchanged.

**Analysis method.** A two-way Boolean cross-tabulation. No alignment, no hashing of sequences, no
model, no statistics.

---

## Results-ready summary

**Denominator: 105 published systems.**

| RT exact | native msr-msd exact | state | n |
|---|---|---|---|
| 1 | 1 | `PAIR_EXACT_PRESENT` | **5** |
| 1 | 0 | `RT_ONLY_EXACT_PRESENT` | **51** |
| 0 | 1 | `NCRNA_ONLY_EXACT_PRESENT` | **6** |
| 0 | 0 | `NEITHER_EXACT_PRESENT` | **43** |

Axis totals: **exact RT present 56/105 · exact native msr-msd present 11/105 · exact pair 5/105.**

**The four states are mutually exclusive and exhaustive**, and every predeclared count was
reproduced exactly.

### What changed, and what did not

**Nothing was re-measured.** The two Boolean axes are `T-X1b`'s, carried through unchanged. What
changed is that six systems previously labelled `EXTERNAL_NEW` — NRT-71, 72, 79, 81, 93, 95 — now
carry `NCRNA_ONLY_EXACT_PRESENT`, which is what they always were in the data.

### Uncertainty

Not applicable. A deterministic relabel of exact Boolean measurements.

### Limitations

⛔ **`ncRNA = 0` means "no exact native-msr-msd sequence match in the project ncRNA catalogue".**
It does **not** mean biological incompatibility, a failed pairing, or an absent ncRNA in nature.
An exact-sequence miss is a statement about **our catalogue's contents**, nothing more.

- `RT_ONLY_EXACT_PRESENT = 51` is the largest class. Whether those native msr-msd sequences are
  genuinely divergent or simply absent from our ascertainment is **not answerable here**.
- The RT axis is the **stop-stripped** hash. The raw hash matched **0 of 105**, so a raw-only
  reconciliation would have placed all 105 in `NEITHER_EXACT_PRESENT`.
- `T-X1b`'s own limitations carry over unchanged.

### ⛔ Interpretation ceiling

Coverage of **our** resource against **one** published catalogue. Not validation in either
direction. No experimental activity — `T-X1b` traced **0** sources. No compatibility or
orthogonality inference. Nothing merged into any population.

---

## Populations touched

**None.** No FASTA, parquet, catalogue or panel was opened.

## Provenance

| | |
|---|---|
| freeze commit | **`b8f75d1`** — launcher + implementation, before this run |
| source | `T-X1b` `X1_row_classification.tsv`, sha256 `3a0b7fa7…c0ce`, asserted by a blocking gate |
| software | Python 3.12.12, stdlib |
| backend | local, 1 thread |
| elapsed | < 0.1 s |
| `reran_sequence_matching` | **false**, recorded in `run_log.json` |

⚠️ **Disclosure, `WORKING_RULES` §1.** Coordinating-session execution under the operator's standing
authorisation; `D4` unresolved.

## Iterations

1 of 1. No criterion changed. The counts were **predeclared from the exposed X1b measurements
before this run** and are reproduced, not fitted.

## Nominations

1. **51 of 105 share an RT with our resource but not its native msr-msd.** A candidate question for
   `T-R2`, framed as ascertainment vs divergence — not resolvable from exact matching.
2. **6 systems have the ncRNA but not the RT.** Worth a look at whether their RTs are near-matches
   below exact identity; that would be a new task with a declared threshold.

## What this does not show

Nothing about experimental activity, function, compatibility or orthogonality. Nothing about
whether our resource is correct — only what it contains. Nothing about the unresolved 613
vocabulary, which was not consumed.
