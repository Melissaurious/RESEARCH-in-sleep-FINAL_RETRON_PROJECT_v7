# DECISION — `g6` BS-15 independent review stays OPEN; bounded downstream use authorised

Date: 2026-09-18 · Track: `rt07` · Status: **binding**

**Decided by:** operator (Melissa Rios), 2026-09-18, immediately after the first independent-review
attempt failed on an external usage limit.

Bundle concerned: `results/rt07_g6_family_architecture/` — **unchanged by this record.**

---

## A · BS-15 is OPEN, and stays open

The g6 bundle and the subsequent self-audit were **both** produced by `claude-opus-5[1m]`
(`results/rt07_g6_family_architecture/PROVENANCE.md`, field `models:`). BS-15 requires an
adversarial pass to assert its own model is DISJOINT from that set. The self-audit therefore
does **not** satisfy the gate and is filed as a Layer-2 cheap preflight
(`docs/PROJECT_ANALYSIS_PRINCIPLES.md` Principle 19).

**No independent scientific review of `g6` exists.**

## B · What happened on attempt 1, and what it does and does not mean

| | |
|---|---|
| date | 2026-09-18 |
| reviewer routed to | `codex` MCP — cross-vendor, disjoint model |
| execution mode | `sandbox: read-only`, `approval-policy: never`, cwd the g6 worktree. **No write access to the bundle.** |
| outcome | **FAILED before producing any finding** |
| verbatim cause | `You've hit your usage limit. … try again at Sep 19th, 2026 12:16 PM.` |

**The failure was caused solely by an external account usage/credit limit.** It was **not** a
refusal, **not** a timeout, **not** a defect in the review packet, **not** an error in the
bundle, and **not** a scientific finding.

**Zero review content was produced** — no confirmation, no refutation, no verdict, not even a
partial result. Nothing from this attempt may be cited as review evidence in **either**
direction. In particular, the failure must never be read as tacit acceptance of the bundle.

## C · No Claude model may be substituted at this stage

A non-Opus Claude reviewer (Sonnet 5, Haiku 4.5) would satisfy BS-15 *as literally written* —
its model id is disjoint from `claude-opus-5[1m]`. The operator has nonetheless **ruled that
out for now**, because same-vendor, same-lineage independence is materially weaker than
cross-vendor independence, and the findings most in need of adversarial checking are precisely
those where a shared prior would be least visible.

**The same packet is rerun against `codex` after the limit resets.** Not a rewritten packet, and
not a different reviewer.

## D · The review packet is preserved, in two places

| copy | path | durability |
|---|---|---|
| working original, as named by the operator | `ARIS_OUTPUT/rt07_g6_review/CLAUDE_SELF_AUDIT.md` | **gitignored** (`.gitignore:2 ARIS_OUTPUT/`) — does not survive a scratch clean or a fresh clone |
| durable tracked copy | **`review-stage/INDEPENDENT_REVIEW_REQUEST_g6.md`** | tracked; carries the failure record and retry instructions, then the packet verbatim |

The tracked copy was added **because** the path the operator named is inside disposable scratch.
The scratch original was not moved, renamed or edited.

## E · Bounded status — what `g6` may and may not be used for, pending review

| use | status |
|---|---|
| `g6` as a **reproducible descriptive analysis** | **CLOSED.** `bundle_status: REPRODUCIBLE`, BS-1..BS-10 pass, 17/17 `verify.sh`, cold rerun reproduces every headline value |
| **descriptive figures** of family/subtype state architecture | **PERMITTED**, with the documented qualifications carried in the caption or text |
| **Stage-3 structural mapping** on the frozen `state_id` coordinate system | **PERMITTED**, with the visibility and occupancy caveats carried |
| **thesis-level biological claims** | **BLOCKED** pending independent review |
| **classification reassessment** | **BLOCKED** pending independent review |
| any claim of **independent validation** | **BLOCKED** pending independent review |

The qualifications that must travel with any permitted use, all already landed in the bundle
and in `docs/decisions/2026-09-18_stage2_g6_closure.md`:

1. `DELETED_STATE` is an alignment-path statement; non-detection is never biological absence.
2. A low MAPPED fraction in a family distant from GII is expected behaviour of a GII-centred
   frame, not a biological finding.
3. Every rate names its own denominator; INSPECTABLE (354,102) is the architecture denominator
   and the catalogue count (501,561) is never one.
4. The significance of the reproducibility result is **null-dependent** and is reported as a
   bracket; that bracket travels with the number.
5. MyRT / PADLOC / DefenseFinder labels are strata, never truth; no accuracy statement of any
   kind is computed against them.
6. Underpowered strata are reported, never compared.

## F · No further `g6` science

No additional `g6` analysis is performed while the gate is open, and **the bundle is not altered
to anticipate the reviewer**. Adjusting an artifact in advance of the review that is meant to
test it would defeat the review. Any correction arising from the self-audit's claims C1–C10
waits for the independent verdict and then lands as its own record.

Supersede this record by a new record, never by rewriting it.
