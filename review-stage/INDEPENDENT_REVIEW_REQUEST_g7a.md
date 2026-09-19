# INDEPENDENT REVIEW REQUEST — frozen g7a RT0–RT7 historical bridge — **GATE OPEN**

> **SUPERSEDED 2026-09-19 — the review this packet requested has now been COMPLETED.**
> Retry with this same packet, unchanged, against Codex (`gpt-5.6-sol`, read-only): **PASS_WITH_REQUIRED_REPAIRS, 7/10, 0 blockers**.
> Result and verbatim review: `review-stage/INDEPENDENT_REVIEW_RESULT_g7a.md`. The text below is the historical record of the
> failed 2026-09-18 attempt and is left exactly as it was.

**Status: OPEN. NO INDEPENDENT SCIENTIFIC REVIEW WAS COMPLETED.**

Object: `results/rt07_g7a_rt0_rt7_bridge/` — **frozen and unmodified throughout.**

This is the durable, git-tracked record of a failed review attempt. It exists because the
working copies live under `ARIS_OUTPUT/`, which is gitignored (`.gitignore:2`) and would not
survive a scratch clean or a fresh clone.

---

## 1 · Bottom line

**No independent adversarial review of the g7a RT0–RT7 bridge exists.** The preferred reviewer
and the authorised fallback both failed for external-capacity reasons. **No RT0–RT7 status has
been changed, and no correction has been implemented.**

**Failure is not tacit acceptance.** Every g7a proposition remains **untested**, not endorsed.

## 2 · The eight statuses — UNCHANGED and UNTESTED

| label | status |
|---|---|
| RT3 | ESTABLISHED OPERATIONAL CORRESPONDENCE |
| RT4 | ESTABLISHED OPERATIONAL CORRESPONDENCE |
| RT5 | ESTABLISHED OPERATIONAL CORRESPONDENCE |
| RT7 | ESTABLISHED OPERATIONAL CORRESPONDENCE |
| RT2 | PARTIAL / INTERPRETIVE |
| RT6 | PARTIAL / INTERPRETIVE (especially jointly with RT5) |
| RT0 | UNRESOLVED / NOT IDENTIFIABLE |
| RT1 | UNRESOLVED / NOT IDENTIFIABLE |

None of these was changed on the basis of this attempt, and none may be.

## 3 · Reviewer provenance

| field | value |
|---|---|
| **preferred reviewer** | **Codex** — remains preferred whenever available |
| **Codex status** | **UNAVAILABLE — external usage limit. ZERO scientific review content produced.** Verbatim: `You've hit your usage limit. … try again at Sep 19th, 2026 12:16 PM.` |
| **fallback provider** | **Google Gemini** (operator-authorised cross-provider fallback) |
| **configured MCP default model** | **`gemini-3.6-flash`** (`LLM_MODEL`; fallback also `gemini-3.6-flash`) |
| **serving model** | **UNCONFIRMED.** The MCP server returns assistant text only and never echoes a serving model. `gemini-3.6-flash` is the *configured default* and **must not** be described as the confirmed serving model. |
| API base URL | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| MCP server reported | `serverInfo {"name": "gemini", "version": "2.0.0"}`, tools `["chat"]` |
| invocation route | Direct stdio JSON-RPC to the configured `gemini` MCP server. Its tools were **not exposed to the Claude session** (only `codex` connected at startup; `ToolSearch` found no gemini tool), so the same server binary and env from `~/.claude.json` were driven directly. Same server, credentials and configured model; different invocation route. |

## 4 · Outcome of the Gemini attempt

| # | action | result |
|---|---|---|
| 1 | single call, full 102,429-char evidence document | **API 503 UNAVAILABLE** (high demand) |
| 2 | retry, same call | **partial — 555 chars, truncated mid-word** in section A/RT0 → `g7a_review_packet/INCOMPLETE_REVIEW_FRAGMENT.md` |
| 3 | transport probe (count 1→120) | **complete and correct** — transport healthy; the truncation was the model stopping early, not a transport fault |
| 4 | sectioned run, 7 sections × up to 5 attempts | **0 / 7 sections returned content.** A1, A2 → repeated **503**; A3, B, C, D, EF → repeated **429 quota exceeded** |

**Gemini produced no scientific review.** The only emitted content is the 555-character
fragment, labelled `INCOMPLETE_REVIEW_FRAGMENT — NOT SCIENTIFIC REVIEW`, which confirms and
refutes nothing.

## 5 · The preserved packet

`review-stage/g7a_review_packet/`

| file | what it is |
|---|---|
| `REVIEW_REQUEST_EXACT.md` | the **exact review request**, 102,429 chars, assembled **verbatim from the landed frozen tables** — not from summaries |
| `SECTION_INSTRUCTIONS_EXACT.md` | the exact per-call section instructions appended to it |
| `REVIEWER_PROVENANCE.json` | machine-readable provenance, per-call status, verbatim error payloads |
| `ARTIFACT_HASHES.tsv` | **SHA-256 of the reviewed frozen artifacts**, read from the bundle's landed `OUTPUTS.tsv` |
| `INCOMPLETE_REVIEW_FRAGMENT.md` | the truncated 555-char response, under its binding label |
| `FAILURE_LOG_RAW.md` | the raw sectioned result: 7 recorded failures with verbatim error payloads |

Infrastructure causes are recorded **separately**, in
`docs/INFRASTRUCTURE_INCIDENTS.md` — deliberately not mixed into this scientific-review record.

## 6 · Constraints on any retry

1. **Do not call Gemini during the exhausted quota window.** The reset time is not reported by
   the API.
2. **Codex is the preferred reviewer** and should be used whenever available.
3. **A future sectioned review must NOT resend the complete ~102 KB packet for every section.**
   Build **deterministic, hashed, section-specific packets** from the frozen evidence bundle, so
   each call carries **only the evidence its assigned RT0–RT7 section needs**, while preserving
   **the same frozen scientific questions** unchanged. The section instructions in
   `SECTION_INSTRUCTIONS_EXACT.md` are the questions to preserve; the evidence payload is what
   must be narrowed and hashed.
4. **A 429 must abort the whole run immediately** — never retry, never continue to later
   sections.
5. Note the server-side cap `max_tokens = 4096`: a full A–F audit of eight labels cannot fit in
   one response through this server regardless of quota, so sectioning remains necessary.

## 7 · State of the object under review

`results/rt07_g7a_rt0_rt7_bridge/` is **unmodified**: `git status --porcelain` on the path is
empty and the bundle's own `verify.sh` passes with **0 failures**. The bundle's
`PROVENANCE.md` already records that it has had **no adversarial pass**; this record does not
change that, it documents a failed attempt to obtain one.
