# DECISION — `g7a` independent review stays OPEN; the failed attempt is made durable

Date: 2026-09-18 · Track: `rt07` · Status: **binding**

**Decided by:** operator (Melissa Rios), 2026-09-18, after the Gemini fallback attempt failed.

Object concerned: `results/rt07_g7a_rt0_rt7_bridge/` — **not modified by this record.**

---

## A · No independent scientific review was completed

Both reviewers failed for external-capacity reasons and **produced no scientific review**:

| reviewer | role | outcome |
|---|---|---|
| **Codex** | **preferred** | **UNAVAILABLE** — external usage limit. `You've hit your usage limit. … try again at Sep 19th, 2026 12:16 PM.` **Zero scientific review content.** |
| **Google Gemini** | authorised cross-provider fallback | **FAILED** — transient **503** then **429 quota exhaustion**. **0 of 7 sections returned content.** |

**Codex remains the preferred reviewer whenever available.**

## B · The 555-character fragment is not a review

The only text Gemini emitted is preserved as
`review-stage/g7a_review_packet/INCOMPLETE_REVIEW_FRAGMENT.md` under the binding label:

```
INCOMPLETE_REVIEW_FRAGMENT — NOT SCIENTIFIC REVIEW
```

It stops mid-word inside section A/RT0, reaches no verdict, completes no label, and never
reaches sections B–F. **It confirms or refutes no RT0–RT7 proposition.** It was restating the
project's own evidence register when it terminated; restating inputs is not agreement with
conclusions.

## C · The gate is OPEN and the eight statuses are unchanged

**The g7a independent-review gate remains OPEN.** The bundle's own `PROVENANCE.md` already
records that it has had no adversarial pass; this record documents a failed attempt to obtain
one, and changes nothing else.

| label | status — **UNCHANGED and UNTESTED** |
|---|---|
| RT3, RT4, RT5, RT7 | ESTABLISHED OPERATIONAL CORRESPONDENCE |
| RT2 | PARTIAL / INTERPRETIVE |
| RT6 | PARTIAL / INTERPRETIVE (jointly with RT5) |
| RT0, RT1 | UNRESOLVED / NOT IDENTIFIABLE |

**No status was changed on the basis of this attempt, and none may be.** **Failure is not
tacit acceptance** — every proposition remains untested, not endorsed.

## D · The attempt is durable, in tracked provenance

Moved out of gitignored scratch (`ARIS_OUTPUT/`, `.gitignore:2`) into tracked review
provenance:

* **`review-stage/INDEPENDENT_REVIEW_REQUEST_g7a.md`** — the status record;
* **`review-stage/g7a_review_packet/`** —
  `REVIEW_REQUEST_EXACT.md` (the exact 102,429-char request, assembled verbatim from the landed
  frozen tables), `SECTION_INSTRUCTIONS_EXACT.md`, `REVIEWER_PROVENANCE.json`,
  `ARTIFACT_HASHES.tsv` (SHA-256 of the reviewed frozen artifacts),
  `INCOMPLETE_REVIEW_FRAGMENT.md`, `FAILURE_LOG_RAW.md`.

The scratch originals were **copied, not moved** — nothing was deleted.

## E · Infrastructure causes are recorded SEPARATELY

`docs/INFRASTRUCTURE_INCIDENTS.md`, entry **INF-1**. Kept apart from this scientific record so
a tooling fault is never mistaken for scientific evidence. It records: the server-side
`max_tokens = 4096` cap; the transient 503s; the subsequent 429 exhaustion; and the executor's
**retry storm as an orchestration error** — up to 35 calls, each carrying the full ~102 KB
payload, with only 20–80 s backoff, which probably consumed the remaining quota.

## F · Binding constraints on any retry

1. **Do not call Gemini during the exhausted quota window.** The reset time is not reported by
   the API.
2. **Codex is preferred** and is used whenever available.
3. **A 429 must abort the entire run immediately** — never retried, never carried into later
   sections.
4. **A future sectioned review must not resend the complete ~102 KB packet for every section.**
   Build **deterministic, hashed, section-specific packets** from the frozen evidence bundle so
   each call carries **only the evidence its assigned RT0–RT7 section requires**, while
   **preserving the same frozen scientific questions** unchanged. The questions to preserve are
   in `SECTION_INSTRUCTIONS_EXACT.md`; it is the evidence payload that must be narrowed and
   hashed, never the questions.
5. Sectioning remains structurally necessary through this server regardless of quota, because a
   full A–F audit of eight labels cannot fit in a 4096-token response.

## G · Scope not touched

`results/rt07_g7a_rt0_rt7_bridge/` is unmodified — `git status --porcelain` on the path is
empty and its `verify.sh` passes with 0 failures. No correction arising from any earlier
self-audit has been implemented; corrections wait for an actual independent verdict. The
frozen Stage-2 instrument, `g4b`, `g5` and `g6` are untouched. `g7b` is not started.

Supersede this record by a new record, never by rewriting it.
