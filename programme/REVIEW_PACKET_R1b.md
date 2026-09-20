---
record: REVIEW_PACKET_R1b
date: 2026-09-20
purpose: final scientific review before spending PANEL-RTDNA-81
status: DRAFT — not frozen, not executed, PANEL-RTDNA-81 UNSPENT
---

# Review packet — T-R1b RT-DNA anchor mapping

⛔ **Nothing is frozen. Nothing is executed. `PANEL-RTDNA-81` is unspent.**
This is the packet for the decision that spends the project's strongest anchor.

## 1 · Files

`SYN = /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis` ·
`T = $SYN/programme/tasks/T-R1b-rtdna-anchor-mapping`

| artefact | path |
|---|---|
| **launcher** | `$T/TASK_LAUNCHER.md` |
| **implementation** | `$T/r1b_map.py` |
| **control table as drafted** | `$T/R1b_CONTROLS_AS_DRAFTED.tsv` |
| **threshold evidence** | `$T/R1b_THRESHOLD_EVIDENCE.tsv` |
| live control output | `$SYN/ARIS_OUTPUT/r1b_draft/tables/R1b_controls.tsv` *(gitignored)* |

⚠️ **There is no separate fixture generator or fixture manifest, by design.** Unlike `T-P1b`, whose
fixtures are drawn *from the catalogue* and therefore need a manifest to pin them, every R1b fixture
is **generated in-process from `random.Random(20260920)`** and uses **no project data at all**. The
fixtures are therefore fully specified by the seed and the code, both of which enter git in the
freeze commit. Pinning a file would add a hash without adding a guarantee.

## 2 · ⛔ Confirmation: no panel sequence has been inspected by the mapper

**Verified by instrumentation, not asserted.** `map_one` was wrapped to record every sequence it was
ever given, the control battery was run, and the log was compared against all 156 sequences
(RT-DNA + ncRNA) of the 81 anchors:

```
map_one invocations during the control run : 6
panel sequences available to leak          : 156  (from 81 anchors)
panel sequences passed to map_one          : 0
distinct subject sequences the mapper saw  : 2   (both synthetic)
```

**What the control run *does* touch in the panel**, stated precisely rather than glossed:

| access | what it reads | does it see a sequence? |
|---|---|---|
| `R1b_GATE_panel_sha256` | the file's **bytes**, for a digest | no semantic access |
| `R1b_GATE_panel_rows` | counts rows; tests `RTDNA_sequence` **non-empty** | presence only, never content |
| `R1b_GATE_anchors_have_ncrna` | tests `ncRNA_sequence` **non-empty** | presence only |

⛔ **No panel sequence is mapped, aligned, or used to derive any coordinate or threshold.** The
confirmatory endpoint is untouched.

## 3 · The exact mapping algorithm

For each anchor, against **its own** ncRNA, in this order:

1. **Exact substring search, forward.** `all_occurrences()` returns **every** start index, including
   overlapping ones — not the first, not the best.
2. **Exact substring search, reverse complement.** Always, never conditionally.
3. If either returns hits → **exact**; local alignment is never reached.
4. Only if both return nothing → **near-exact** (§4).

Coordinates are **1-based inclusive** on the ncRNA.

## 4 · The near-exact algorithm and its parameters

Biopython `Align.PairwiseAligner`, version **1.87**:

```
mode            = "local"        (Smith-Waterman)
match_score     = +2
mismatch_score  = -3
open_gap_score  = -5
extend_gap_score= -2
```

Run **twice** — once for the RT-DNA, once for its reverse complement — and the higher-scoring
orientation is taken. Mismatches, gaps, identity and coverage are counted from the aligned blocks,
not from the score.

## 5 · Justification for `coverage ≥ 0.90` **and** `identity ≥ 0.90`

**Declared before any panel sequence is seen.** The evidence is a **400-pair synthetic negative
sweep** at panel-realistic *lengths* (RT-DNA 55–189 nt inside ncRNA 88–293 nt — **lengths from the
schema, no sequence**), on seed `4242`, deliberately different from the task seed:

| | min | median | p95 | **max** |
|---|---|---|---|---|
| coverage | 0.0380 | 0.1034 | 0.2300 | **0.3875** |
| identity | 0.7619 | **0.9231** | 1.0000 | **1.0000** |

**400 of 400 unrelated pairs → `UNMAPPED`. Zero reached the floor.**
Worst-case coverage **0.3875** against a floor of **0.90** — a margin of **0.5125**.

⛔ **And the sweep shows why identity alone would be useless.** Unrelated noise reaches **median
identity 0.9231 and maximum 1.0000**, because a local aligner reports only the short best-scoring
island it can find. An identity-only criterion would admit **more than half** of pure noise.
**Coverage is the discriminating condition; identity guards against a long, poor alignment.** Both
are required, which is why the rule is a conjunction.

Full table: `$T/R1b_THRESHOLD_EVIDENCE.tsv`.

## 6 · The nine controls

| control | type | expectation | observed | state |
|---|---|---|---|---|
| `R1b_GATE_panel_sha256` | positive | `80b2f565…9577` | match | **PASS** |
| `R1b_GATE_panel_rows` | positive | 175 rows / 81 anchors | 175 / 81 | **PASS** |
| `R1b_GATE_anchors_have_ncrna` | positive | all 81 carry an ncRNA | 81 | **PASS** |
| `R1b_POS_planted_exact` | positive | planted at 41..130 → `EXACT_UNIQUE FORWARD 41..130`, n=1 | exact | **PASS** |
| `R1b_POS_planted_revcomp` | positive | its revcomp → `REVCOMP`, same span | exact | **PASS** |
| `R1b_POS_multiple_placements_reported` | positive | planted twice → n=2, **both** coordinates | `starts=41;171` | **PASS** |
| `R1b_NEG_unrelated_unmapped` | negative | unrelated, equal length → `UNMAPPED` | `cov=0.0778` | **PASS** |
| `R1b_POS_near_exact_detected` | positive | 3 substitutions → `NEAR_EXACT`, `n_mismatch=3` | `id=0.9667 cov=1.0` | **PASS** |
| `R1b_NEG_partial_not_forced` | negative | 20 nt real + 90 nt random → below floor | `UNMAPPED cov=0.2364` | **PASS** |

**9 blocking, 9 PASS.** Positives and negatives fail in **opposite** directions: a map-everything
procedure fails the two negatives; a map-nothing procedure fails the four positives.

⚠️ **A defect these controls caught during drafting**, recorded because it is the point of them:
`starts`/`ends` were a `';'`-joined **string** on the exact path and an **int** on the near-exact
path — a type trap for every consumer. **The implementation was fixed, not the assertion.**

## 7 · The four states, and how they differ

| state | trigger | coordinates | placements |
|---|---|---|---|
| `EXACT_UNIQUE` | exactly one exact substring hit | the one span | 1 |
| `EXACT_MULTIPLE` | ≥2 exact hits | ⛔ **all spans, `;`-joined** | n ≥ 2 |
| `NEAR_EXACT` | no exact hit, **and** coverage ≥ 0.90 **and** identity ≥ 0.90 | best alignment span | 1 |
| `UNMAPPED` | no exact hit **and** below either floor, or no alignment at all | **none** | 0 |
| `INPUT_MISSING` | a required sequence absent | none | 0 |

**`AMBIGUOUS` is not a state — it is a property**, carried on two axes so it is never collapsed:

- **`n_placements > 1`** — several equally valid positions;
- **`orientation = BOTH_AMBIGUOUS`** — the sequence matches forward **and** reverse-complement.

Both are surfaced again in `R1b_ambiguous_and_unmapped.tsv`.

⛔ **`EXACT` and `NEAR_EXACT` are never merged into "mapped".** They are different evidence and are
counted separately in the summary.

## 8 · Multiple placements and orientation

**Multiple placements.** `all_occurrences()` returns every index; the state becomes
`EXACT_MULTIPLE`; `n_placements` is the count; `ncrna_start` and `ncrna_end` are `;`-joined lists.
⛔ **There is no tie-break, no "best" placement, no first-hit shortcut. The number of equally valid
placements is itself a result.**

**Orientation.** Both strands are tested on **every** anchor, exact and near-exact alike. The
result is one of `FORWARD` · `REVCOMP` · `BOTH_AMBIGUOUS` · *(empty when unmapped)*, and **which
one matched is landed**. RT-DNA may legitimately be reported on either strand, so orientation is a
measurement, not an assumption.

## 9 · Output schema

**`R1b_anchor_coordinates.tsv`** — exactly 81 rows:

| column | type | notes |
|---|---|---|
| `terminal_id` | str | panel identifier |
| `retron_name`, `retron_sub` | str | as published |
| `rtdna_len`, `ncrna_len` | int | nt |
| `mapping_state` | enum | §7 |
| `orientation` | enum | `FORWARD`/`REVCOMP`/`BOTH_AMBIGUOUS`/empty |
| `n_placements` | int | **0 when unmapped**, ≥2 when ambiguous |
| `ncrna_start`, `ncrna_end` | **str** | 1-based inclusive; `;`-joined when multiple — **always a string, on every path** |
| `n_mismatch`, `n_gap` | int | 0 on the exact path |
| `pct_identity`, `pct_coverage` | float | 1.0 on the exact path |
| `align_score` | float | empty on the exact path |

Also: **`R1b_ambiguous_and_unmapped.tsv`** (the subset needing human attention, surfaced not
buried) · **`R1b_summary.tsv`** (counts by state and orientation) · **`R1b_controls.tsv`** ·
`logs/run_log.json`.

## 10 · STOP conditions

| condition | action |
|---|---|
| panel sha256 mismatch | **STOP** before any mapping |
| not exactly 175 rows / 81 anchors | **STOP** |
| an anchor lacking its own ncRNA | **STOP** |
| any blocking control fails | **STOP**, `TASK_STATE: VOID`, no primary table, escalate, **new task ID** |
| fewer than 81 rows would be written | **STOP** — ⛔ an anchor is never dropped; `UNMAPPED` and ambiguity are **states, not omissions** |
| a threshold would be changed after seeing a result | **STOP** — that is a new task |

## 11 · What you are being asked to approve

1. Spending **`PANEL-RTDNA-81`** — `NOT_YET_EXPOSED`, the project's strongest anchor, never a
   training target. **One authorisation, one task.**
2. That **`T-R1b` is the D7 merge** — `T-A5b1` and `T-R1` are the same task and must not both run.
3. The predeclared **0.90 / 0.90** floor, on the §5 evidence.
4. That exact and near-exact stay **separate**, and that ambiguity and non-mapping are **reported
   rather than resolved**.
