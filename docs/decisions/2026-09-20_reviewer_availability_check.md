# Reviewer availability — point-in-time check

**Date:** 2026-09-20 · **Checked by:** coordinating session · **Scope:** fact only, no decision taken

## Why this exists

A proposal in circulation would narrow the established independent reviewer to implementation
conformance and require a different adversarial reviewer for the scientific verdict. A concern was
raised that this could leave no available reviewer, because at the last recorded attempt
(`docs/decisions/2026-09-18_stage2_g7a_review_attempt_failed.md`) **both** failed: one on a usage
limit returning zero review content, the other on 503 then 429 quota exhaustion returning 0 of 7
sections.

That concern is checkable, so it was checked rather than argued.

## Result

| reviewer | status | serving model, self-reported |
|---|---|---|
| Codex | **AVAILABLE** | GPT-5.6-Codex |
| Gemini | **AVAILABLE** | Gemini 3.6 |

Both responded to a minimal availability probe. Codex was called read-only with approvals disabled
and read no files. **The pipeline does not currently stall for want of a reviewer.**

## What this does NOT settle

- **Availability is point-in-time.** Both were unavailable simultaneously once before. Re-check
  immediately before any dispatch; do not rely on this record.
- **It does not resolve the routing question.** Whether the established reviewer should be narrowed
  to implementation conformance, which would surrender model-disjointness precisely at the scientific
  verdict while retaining it where a same-vendor reviewer would suffice, is an operator decision and
  is untouched here.
- **It does not supersede anything.** A standing record states the established reviewer "is preferred
  and is used whenever available" as a binding constraint. Per `CLAUDE.md`, a settled decision is
  superseded by a new record naming it, never by silently rewriting history. Any narrowing must carry
  that explicit supersession clause, or two contradictory standing rules will coexist and a future
  session will obey whichever it reads first.

## Standing recommendation, unchanged

The author of a directive should not also return the verdict on the artifact that directive shaped.
That pattern is the failure `TASK_PROTOCOL.md` §4 records, where a repaired gate passed on retry and
independent review failed it because the first attempt's results had motivated the second attempt's
rule class.
