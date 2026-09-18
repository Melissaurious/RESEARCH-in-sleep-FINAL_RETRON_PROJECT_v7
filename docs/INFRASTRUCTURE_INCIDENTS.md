# INFRASTRUCTURE INCIDENTS

Tooling, transport and orchestration failures. **Deliberately separate from scientific
records**, so an infrastructure fault is never mistaken for scientific evidence and never
allowed to imply anything about a bundle under review.

---

## INF-1 · 2026-09-18 · g7a independent review — reviewer infrastructure failed; no review produced

Context: an independent adversarial review of the frozen
`results/rt07_g7a_rt0_rt7_bridge/` bundle. The scientific record of the failed attempt is
`review-stage/INDEPENDENT_REVIEW_REQUEST_g7a.md`. **This entry is about the infrastructure
only.** No conclusion about the bundle may be drawn from anything here.

### 1 · Preferred reviewer unavailable

**Codex** — external account usage limit. Verbatim:

```
You've hit your usage limit. … try again at Sep 19th, 2026 12:16 PM.
```

Zero scientific review content produced. Not a refusal, not a timeout, not a defect in the
packet or the bundle.

### 2 · MCP/server output limit — `max_tokens = 4096`

The `gemini` MCP server hardcodes the output cap:

```
/home/borg/aris_repo/mcp-servers/llm-chat/server.py:111
    payload = { ..., "max_tokens": 4096 }
```

**Consequence, independent of quota:** a complete A–F audit of eight historical labels cannot
be returned in one response through this server. The first single-call attempt returned **555
characters and stopped mid-word** inside section A/RT0. Sectioning is therefore *structurally
required* for any review routed through this server, not a stylistic choice.

A transport probe (count 1→120, ending in a sentinel) returned **complete and correct**,
confirming the truncation was the model stopping early against the cap and **not** a transport
or framing fault.

### 3 · Transient 503 responses

Initial calls returned:

```
API error 503: "This model is currently experiencing high demand. Spikes in demand are
usually temporary. Please try again later." status: UNAVAILABLE
```

Sections A1 and A2 failed this way across all their attempts. 503 is a **transient capacity**
signal and is legitimately retryable — but with far longer backoff than was used.

### 4 · Subsequent 429 quota exhaustion

From section A3 onward, every call returned:

```
API error 429: "You exceeded your current quota, please check your plan and billing details."
```

429 is a **terminal budget** signal, not a transient one. **The API does not report the reset
time**, so the window's end is unknown from the error alone.

### 5 · Retry storm — an ORCHESTRATION ERROR by the executor

The sectioned run issued **up to 35 calls (7 sections × 5 attempts), each carrying the full
~102 KB evidence document**, with only 20–80 s backoff.

Evidence that this consumed the remaining quota:

* quota demonstrably existed beforehand — the earlier single call partially succeeded (555
  chars returned);
* the error signature moved **503 → 429** partway through the run and never moved back;
* every section after A2 failed identically with 429, including its four retries.

**This was an executor design error, not a property of the bundle, the review packet, or the
reviewer.** It is recorded here so it is not re-derived from error codes later, and so the
cost — probable loss of the Gemini fallback for an unknown window — is attributed correctly.

### 6 · Binding rules for future reviewer orchestration

1. **A 429 MUST abort the entire run immediately.** Never retry a 429; never continue to
   subsequent sections after one.
2. **A future sectioned review MUST NOT resend the complete ~102 KB packet for every section.**
   Build **deterministic, hashed, section-specific packets** from the frozen evidence bundle so
   each call carries **only the evidence required for its assigned RT0–RT7 section**, while
   **preserving the same frozen scientific questions** unchanged. Hash each section packet so
   the reviewer's inputs are reproducible and auditable per call.
3. **Retry caps must scale with payload.** A ~102 KB request is not a cheap retry; 5 attempts
   per section against a large payload is not acceptable backoff discipline.
4. **503 backoff must be substantially longer** than the 20–80 s used here.
5. **Do not call Gemini during an exhausted quota window.** Reset time is unreported; wait for
   an explicit signal or operator instruction.
6. **Codex remains the preferred reviewer** whenever available; Gemini is the authorised
   cross-provider fallback only.
7. **Probe before a large run.** The cheap transport probe used here (a bounded counting task
   with a sentinel) correctly distinguished "transport healthy, model stopped early" from
   "transport broken" and cost almost nothing. Run it first.

### 7 · What this incident does NOT mean

* It says **nothing** about the correctness of `results/rt07_g7a_rt0_rt7_bridge/`.
* It is **not** tacit acceptance of any RT0–RT7 status.
* The 555-character fragment it produced is labelled
  `INCOMPLETE_REVIEW_FRAGMENT — NOT SCIENTIFIC REVIEW` and confirms or refutes **no**
  proposition.
* The g7a independent-review gate remains **OPEN**.
