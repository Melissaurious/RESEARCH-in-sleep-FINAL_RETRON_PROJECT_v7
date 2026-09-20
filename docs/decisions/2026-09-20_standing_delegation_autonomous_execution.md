---
record: 2026-09-20_standing_delegation_autonomous_execution
date: 2026-09-20
kind: DECISION RECORD — STANDING OPERATOR DELEGATION
status: ACTIVE
authority: the operator (Melissa Rios), stated explicitly on 2026-09-20
supersedes: >
  the per-task "operator review required" gate in programme/LAUNCHER_PROPOSALS_WAVE_02.md,
  and the READY_FOR_OPERATOR_REVIEW classification in its §0, for tasks inside the declared
  retron programme and its 12 scientific goals ONLY. Nothing else is superseded.
---

# Standing delegation of routine approval to the ARIS autonomous workflow

## 1 · The delegation, as given

> For tasks inside the already-declared retron programme and its 12 scientific goals, I delegate
> routine launcher approval, implementation review, execution routing, acceptance and dependency
> release to the ARIS autonomous workflow, **provided the task remains within its declared
> scientific scope.**

This removes routine operator approvals, backend choices and acceptance steps from the critical
path. It is a delegation of **routine judgment already bounded by a declared design**, not a grant
of scientific latitude.

## 2 · ⛔ What this delegation does NOT grant

- **It does not permit inventing scientific scope.** A task needing a genuinely new biological
  endpoint, threshold, population, feature-selection decision or interpretation is **outside** the
  delegation.
- **It does not permit the preparing agent to approve its own design.** The executor is never the
  approver — see §4.
- **It does not remove independent review.** It routes review to the *automatic* independent
  reviewer instead of to the operator. `WA-A.5` stands in full: reviewer independence, the score
  threshold and the stop/continue/escalate transition remain ARIS's, and are never weakened, never
  routed around, and never satisfied by a same-family reviewer.
- **It does not authorise a protected-population spend**, which still requires explicit
  authorisation per spend.
- **It does not make a parked task a global stop.** A task that cannot proceed is parked
  **individually**; every other eligible task continues. ⛔ **A single blocked task must never halt
  autonomous work.**

## 3 · Scope boundary — how "within declared scientific scope" is decided

A task is inside the delegation when its question, population, denominator, endpoint, controls and
interpretation ceiling are already fixed by a **tracked** source: the programme contract, a tracked
design packet (e.g. `programme/LAUNCHER_PROPOSALS_WAVE_02.md`), `programme/CANONICAL_DATASETS.tsv`,
an existing frozen launcher, or a prior decision record.

Ordinary scientific clarification that can be resolved from the contract, canonical datasets, the
prior-work inventory, the literature, existing task dependencies or reviewer feedback is **routine**
and is resolved autonomously. It is not an escalation.

If genuinely incompatible scientific interpretations survive adversarial review, that task is
parked and everything independent of it continues.

## 4 · The author ≠ approver pattern, restored

Every task follows, before any primary science runs:

```
DRAFT LAUNCHER (may be generated from a tracked design packet)
  → launcher lint / artefact-contract check
  → INDEPENDENT CROSS-MODEL ADVERSARIAL REVIEW  (ARIS auto-review-loop, Codex backend)
  → automatic repair of reviewer findings
  → re-review until the ARIS acceptance gate is met
  → FREEZE
  → EXECUTE
```

**The independent reviewer, not the executor, decides whether a launcher is ready.** The gate is
ARIS's own, taken verbatim from `skills/auto-review-loop/SKILL.md`:

> `POSITIVE_THRESHOLD: score >= 6/10 AND verdict ∈ {"ready", "almost"}` — **both** must hold;
> the verdict vocabulary is `{"ready", "almost", "not ready"}`; `MAX_ROUNDS = 4`.

A launcher that does not reach that gate within `MAX_ROUNDS` is **parked**, not frozen.

Autonomous launcher generation from a tracked design packet is permitted only when the packet is
cited, prior work is read first, and population/denominator/endpoint, controls and interpretation
ceiling are explicit. ⛔ **The prepare agent may never silently invent a missing endpoint at
execution time.**

## 5 · Acceptance — execution validity and scientific validity are different things

| gate | who decides | what it establishes |
|---|---|---|
| **execution validity** | deterministic verifier | frozen/input hashes, blocking controls, required artefacts, manifest, run log, report schema, no undeclared inputs, preregistered endpoint |
| **scientific validity** | independent cross-model reviewer, automatically invoked | whether the result is interpretable and meets its preregistered criterion |

A hard dependency is released **only after whatever acceptance the governed ARIS contract requires
has completed** — see `docs/BLOCKED.md` D20, which this record closes in favour of option (a).

Negative and null outcomes that satisfy their preregistered criterion are **valid consumable
results**, not failures.

## 6 · Resource planning is delegated

Backend and execution shape are **logistics, never science**. At each scheduling cycle the broker
inspects live BORG capacity (CPU, RAM, GPU, NVMe/I-O pressure, active workers) and live Ibex state
(reachability, partitions, queue depth, submitted project jobs) and may choose local, Ibex, both
concurrently, Slurm arrays for many small independent jobs, thread/memory/GPU counts, batching and
retry/resume mechanics.

⛔ **Ibex is not reserved for large jobs.** ⛔ **No backend choice may alter a frozen scientific
endpoint.**

## 7 · Failure handling

**Retried automatically** — transient network failures, scheduler failures, external HTTP 5xx,
recoverable staging failures, and mechanical traceability failures whose repair does not touch the
scientific design.

⛔ **Never rerun blindly** — a failed scientific control, a changed endpoint or population, an
exhausted protected population, or a genuine criterion failure. Those are recorded in their true
state, parked if necessary, and all unrelated work continues.

## 8 · Durability

The autonomous system recovers from a coordinator or session restart **entirely from repository and
runtime state**. It relies on no conversation memory, no in-memory status and no hand-editing of
task state. `WAVE_STATUS.tsv` is generated state and is never scientific authority.

## 9 · Consequences applied on this date

- `T-M1b-embedding-cache-reverification` and `T-S1b-structure-inventory-correction` move from
  `PARKED_LAUNCHER_REVIEW` into the autonomous path: their launchers are generated from the tracked
  §2 and §3 design packets, adversarially reviewed, repaired, re-reviewed and frozen under §4. They
  are **not** returned to the operator for separate approval.
- `programme/LAUNCHER_PROPOSALS_WAVE_02.md`'s "operator review required before any is written or
  dispatched" is replaced, for in-scope tasks, by the delegated independent-review gate of §4.
- `T-P1b-identity-partition` keeps its recorded procedural deviation. ⛔ **The expensive computation
  is NOT rerun to repair paperwork**, and no prospective authorisation is fabricated; the deviation
  is routed through this delegated governance mechanism as a recorded fact.
