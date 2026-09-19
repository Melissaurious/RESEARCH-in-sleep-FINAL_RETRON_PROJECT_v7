# DECISION — independent reviews of `g6` and `g7a` COMPLETED; both PASS_WITH_REQUIRED_REPAIRS

Date: 2026-09-19 · Track `rt07` · Status: **both review gates CLOSED; repairs recorded as errata**

Supersede by a new record, never by rewriting. This record supersedes the OPEN review status in
`2026-09-18_stage2_g6_bs15_open_and_bounded_use.md` and
`2026-09-18_stage2_g7a_review_attempt_failed.md`. Those records are left as written.

---

## 1 · What was run

The retry both earlier records specified: **the same landed packet, unchanged, against the
same preferred reviewer**, after the usage-limit reset (2026-09-19 12:16).

| | g6 | g7a |
|---|---|---|
| packet | `review-stage/INDEPENDENT_REVIEW_REQUEST_g6.md` | `review-stage/g7a_review_packet/REVIEW_REQUEST_EXACT.md` + `SECTION_INSTRUCTIONS_EXACT.md` |
| reviewer | Codex, `gpt-5.6-sol`, `xhigh` | Codex, `gpt-5.6-sol`, `xhigh` |
| sandbox | read-only, `approval-policy: never` | read-only, `approval-policy: never` |
| thread | `01a0b99f-4837-7ce1-9ddd-9d0138441c55` | `01a0b9a1-1d76-7193-9d7b-89cb6a41e875` |
| result record | `review-stage/INDEPENDENT_REVIEW_RESULT_g6.md` | `review-stage/INDEPENDENT_REVIEW_RESULT_g7a.md` |

The serving model is read from each session log's `turn_context`, not assumed. The reviewer
is vendor- and model-disjoint from the producer `claude-opus-5[1m]`, so **BS-15 is satisfied**
for both bundles.

Pre-review integrity, verified in this session without recomputing anything: both bundles pass
`bundle_valid.sh` BS-1..BS-10; 37/37 g6 and 34/34 g7a outputs match `OUTPUTS.tsv`; 25/25
g7a packet artefacts match `ARTIFACT_HASHES.tsv`.

## 2 · Outcomes

| | g6 | g7a |
|---|---|---|
| **verdict** | **`PASS_WITH_REQUIRED_REPAIRS`** | **`PASS_WITH_REQUIRED_REPAIRS`** |
| **score** | **6/10** | **7/10** |
| **blockers** | **0** | **0** |
| required repairs | 8 | 5 |

**g6.** C1–C10: 4 CONFIRMED, 6 PARTIALLY CONFIRMED, 0 REFUTED. The narrow descriptive tables
stand. The bounded-use table is **upheld with no row moving**.

**g7a.** All eight label statuses **UPHELD**; none downgraded, none upgraded.

## 3 · RT0 and RT1 remain UNRESOLVED

**The independent reviewer upheld RT0 = `UNRESOLVED / NOT IDENTIFIABLE` and RT1 =
`UNRESOLVED / NOT IDENTIFIABLE`**, for reason *C — both*:

* **historical:** no held source states RT0's C-terminal edge; the defining source, Malik, Burke
  & Eickbush 1999, is **not held**; the Blocker transcription places R85 *inside* RT1 and states
  no RT0|RT1 boundary;
* **instrumental:** the frozen anchors begin at LtrA 97; RT0 evidence lies at or before 85 and
  reconstructed block 1 at 39–61.

No inferential, analogical, interpolated or structural resolution was attempted, and none is
permitted. **Only primary historical evidence could change either status.** Non-observability
is a statement about the instrument and the sources, **not about biology**.

## 4 · Scientific status vs workflow closure

* **Scientific status** — what the frozen evidence supports. The reviews upheld it and bounded
  it; they extended nothing.
* **Workflow closure** — a decision to stop working on a question with the current instrument
  and evidence set. It is not a claim that the question is answered.

**`TERMINAL`**, wherever it describes g7a, means **workflow closure for the current instrument
and evidence set — not complete historical recovery of RT0–RT7.**

## 5 · Repairs

All 13 required repairs are applied as **additive errata and interpretive corrections only**:
`docs/decisions/2026-09-19_stage2_g6_review_errata.md` and
`docs/decisions/2026-09-19_stage2_g7a_review_errata.md`. **No frozen computational output is
altered**, and neither bundle is re-sealed.
