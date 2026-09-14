# LAUNCHER — rt_ncrna_pairing_census

> A filled, passing launcher. Copy the *shape*, not the content.
> `python general/tools/check_launcher.py` exits 0 on this file — it is the validator's
> positive fixture, so it is verified in both directions (WA-A.3).

## 1. Objective and success criterion

**Objective.** An exact census of RT–ncRNA pairing in the retron JSONL corpus: how many
records carry both an RT call and an ncRNA call, how many carry exactly one, and how many
carry neither.

**Success criterion.** Four counts summing to the corpus total, that total agreeing with an
independent `wc -l` over the same files, and `run.sh` reproducing all four from the hashed
inputs on a second run.

## 2. Kill criteria

Abandon the pairing line if fewer than 500 records carry both calls — below that the
downstream covariation analysis has no population and no amount of method work fixes it.

Stop regardless of result at 2× the compute estimate, and report.

## 3. Non-goals — out of scope

No covariation analysis. No alignment. No phylogeny. No filtering of the corpus on any
quality criterion — this gate measures the population unconditionally and stratifies later
(EVIDENCE_STANDARDS §3). Do not re-derive the RT or ncRNA calls themselves; this gate counts
what the records assert, and says so.

## 4. Inputs

| path | what it is | trust grade |
|---|---|---|
| `/home/borg/RESEARCH-in-sleep-RETRON-DB/MELISSA_DATA/json_files_input_june/` | the JSONL corpus | RAW |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB/MELISSA_DATA/gem_metadata.tsv` | per-record metadata | RAW |

⛔ Read-only. `input_format.md` is a hypothesis about these files, not ground truth — probe
real values before counting anything (WA-D.4). A prior stage found a lineage string filed
under an `ecosystem` column and a "direction" field that was 97.7% null and not a direction.

## 5. What might already exist

`ARIS_OUTPUT/stage1_db_analysis/` in RETRON-DB_V3 holds field-completeness tables that may
already carry these counts. **Treat them as untrustworthy until checked:** they predate the
schema correction above, and nothing records whether they were computed before or after it.
If they agree with a fresh count, say so and cite both. If they disagree, the fresh count
wins and the disagreement is the finding.

## 6. Claims this task tests

| id | role in this task |
|---|---|
| C1 | primary |
| C2 | primary |

⛔ **Ids and roles only — never a paraphrase.** The wording and status live in
`<project>/idea-stage/docs/research_contract.md`, which ARIS creates and consumes. A
restated claim drifts from the canonical one within a week, and then two sentences both
claim to be C1. `REFUTED` is a result, not a failure.

## 7. Gates

| gate id | the ONE measurement | weight | settles | stop condition |
|---|---|---|---|---|
| g1_pairing_census | the four-way count of RT×ncRNA call presence over all records | FULL | C1, C2 | done when results/g1_pairing_census/ exists and run.sh reproduces the four counts from the hashed inputs |

FULL, not LIGHT: both counts become claims, so the denominator needs its independent second
count (WA-D.3) and the zero cells need a positive control (EVIDENCE_STANDARDS §6).

## 8. Compute

- Expected: borg, CPU only, streamed record-by-record. Estimated 25 min.
- Hard stop at 2× the estimate — report, do not push through.
- No GPU, no Ibex: this is a streaming pass, well under the escalation thresholds in
  `general/site/COMPUTE.md`. If the corpus turns out not to fit in RAM, stream it — never
  downgrade a census to a sample to stay local (WA-D.2).

## 9. Autonomy

**Decide alone and continue** (log in `docs/BLOCKED.md`): field-name mismatches and how they
were resolved; which JSONL files are malformed and were counted as such; the exact predicate
used for "carries an RT call"; anything reversible and inside the gate's scratch.

**Stop and wait**: any write outside `ARIS_OUTPUT/g1_pairing_census/` and
`results/g1_pairing_census/`; any run exceeding 50 min; any change to a spec; a corpus total
that disagrees with `wc -l` by more than 0 records.

**Review rounds before halting:** 3. A budget-halt is reported as a budget-halt, never as a
pass (WA-A.3).

---
_Rules quoted inline, with their ids, per LAUNCHER_SPEC:_
**WA-A.4** measure and report counts; do not conclude — interpretation lands as `PROPOSED:`.
**WA-G.5** a null or refuting measurement is a result and lands like any other.
**WA-S.1** never guess silently and never stall; LOW-STAKES takes the default and continues.
