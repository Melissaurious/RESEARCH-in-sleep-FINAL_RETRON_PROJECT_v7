---
record: 2026-09-20_operator_ruling_exposure_freeze_controls
date: 2026-09-20
kind: DECISION RECORD — RECONSTRUCTED FROM CITATIONS, awaiting operator confirmation
status: PROVISIONAL
authority: the operator (Melissa Rios)
reconstructed_by: reconciliation session, 2026-09-20
supersedes: nothing
---

# Operator ruling of 2026-09-20 — exposure, freeze, controls, retrieval

## ⛔ Read this first: what kind of document this is

**This ruling is load-bearing and had no decision record.** It is cited by name — with section
numbers — in four task launchers, one executed script, one erratum and one escalation, and it is
the authority behind the exposure model now used across the programme. Until this file, it existed
**only in a chat transcript**.

That is the exact failure the handoff discipline exists to prevent: a governing decision reachable
only through a conversation nobody else can read.

**This document is reconstructed from the repository's own citations of the ruling, not from the
conversation.** Every clause below is quoted or paraphrased from a tracked file that cites it, and
each carries its source. **Sections 4–7 are not cited anywhere in the repository and are therefore
not reconstructed — their content is unknown.**

> **Operator action required:** confirm, correct or replace this record. Until confirmed it is
> `PROVISIONAL`. It is not a substitute for the ruling; it is the repository's best auditable
> reconstruction of it, written so no successor session has to ask the chat what the rules are.

---

## §1 · Exposure is tracked per endpoint, not per dataset

**Adopted rule:**

```
exposure = population_id + analysis_family/endpoint + exposure_state
```

A population marked `INSPECTED_FOR_THIS_ENDPOINT` **may** be used for:

- exploratory work;
- QC;
- asset construction;
- method development;
- unrelated preregistered endpoints with no plausible leakage.

It **may not** later be described as untouched confirmatory evidence *for that endpoint*.

**A rejected or VOID run still counts as an exposure.** `T-C1`, `T-N1` and `T-P1` all failed review,
and all three exposed their endpoints regardless.

**A population is not globally burned by one endpoint's exposure.** `RT-EXACT-501561` is
`INSPECTED_FOR_THIS_ENDPOINT` separately for profile detection, motif detection and identity
clustering, and `NOT_YET_EXPOSED` for everything else — so a preregistered confirmatory endpoint may
still be drawn there.

**Sources:** commit `c77adb9` message ¶2; `programme/EXPOSURE_BY_ENDPOINT.tsv`;
`programme/tasks/T-C1b-pf00078-envelope-census/TASK_LAUNCHER.md` L59–62 and L17;
`programme/tasks/T-N1b-neighbourhood-census/TASK_LAUNCHER.md` L17, L55;
`programme/tasks/T-N1c-neighbourhood-census/TASK_LAUNCHER.md` L18.

⚠️ **This ruling settles open decision #4** (`OVERNIGHT_RUN_REPORT` §10), which recorded that
`WORKING_RULES` §3 ("inspection depletes") and `POPULATION_LEDGER.tsv` ("inspection is not
consumption") could not both hold. §1 resolves it by making exposure endpoint-scoped rather than
dataset-scoped. **`WORKING_RULES` §3 and the ledger's pre-ruling rows have not yet been rewritten to
match**, and both still read as though exposure were dataset-wide.

## §2 · Freeze before execute

**The launcher and the implementation are committed together, in one commit, before the run. The
run records that commit id.**

Commit `c77adb9` is the first application: *"This commit is the pre-run freeze required by
WORKING_RULES section 6b and the operator ruling of 2026-09-20 section 2. Nothing here has been
run."* The three runs that followed each recorded `prerun_commit: c77adb96…`, and `T-N1c` recorded
`prerun_commit: b2701475…`.

**Sources:** commit `c77adb9` message ¶1; `WORKING_RULES` §6b;
`analysis/t_a23c_source_retrieval/logs/stdout.txt` (`"prerun_commit": "c77adb96…"`);
`programme/tasks/T-N1c-neighbourhood-census/ESCALATION_01_third_null_failed.md` frontmatter.

## §3 · Controls run on separate fixtures, and a failed control is a STOP

Two clauses, both cited:

1. **No control may touch the primary input.** *"Controls in all three run on separate fixture files
   and never touch the primary input, per operator ruling section 3."* This is the direct repair of
   `T-P1`, whose controls were appended to the primary input and changed the clustering they were
   meant to check.
2. **A failed blocking control is a STOP, and the threshold is not relaxed after seeing the
   number.** Applied twice, against the session's own interest: `T-N1b` at 0.070506 against a
   declared 0.05, and `T-N1c` at 0.284691 against a declared 0.25. Neither ceiling was raised.

**Sources:** commit `c77adb9` message, final paragraph;
`programme/tasks/T-C1b-pf00078-envelope-census/TASK_LAUNCHER.md` L80 and
`c1b_envelope_census.py` L21; `programme/tasks/T-N1c-neighbourhood-census/TASK_LAUNCHER.md` L29;
`ESCALATION_01_third_null_failed.md`.

## §4 – §7 · NOT RECONSTRUCTED

**No tracked file in this repository cites sections 4, 5, 6 or 7 of the ruling.** They may not
exist, or they may cover matters that never reached a launcher. **Their content is unknown and is
not guessed here.** If they exist and are load-bearing, the operator should add them.

## §8 · Bounded source retrieval authorised (T-A23c)

Retrieval was authorised, scoped to the six load-bearing uncertainties behind the `T-A23`
cross-pair curation, preferring primary sources, recording unavailability as a finding rather than
working around it, with two standing prohibitions carried in the launcher: **no unmeasured negative
pair is inferred**, and **no orthogonality modelling opens because rows were found**.

**Source:** `programme/tasks/T-A23c-source-retrieval/TASK_LAUNCHER.md` frontmatter
(`operator_authorisation: 2026-09-20 §8, bounded retrieval`) and §"Authorised by the operator,
2026-09-20 §8".

---

## What this record does not settle

- Whether `WORKING_RULES` §3 and `POPULATION_LEDGER.tsv` should now be rewritten to the §1 model,
  and by whom. They currently contradict it in wording while the programme operates under §1.
- The **control-design decision escalated by `T-N1c`** — whether a ceiling on the null rate is the
  right blocking criterion at all. §3 says a failed control stops the task; it does not say what the
  replacement criterion should be, and the escalation is explicit that choosing one is the
  operator's.
- Sections 4–7, above.
