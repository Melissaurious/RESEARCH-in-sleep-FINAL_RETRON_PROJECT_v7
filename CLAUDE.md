# CLAUDE.md — <project>

<One sentence: what this project measures, in what units, so that every downstream number
has a denominator that can be named.>

> ⚠ The sentence above is the only project-specific claim in this file. The operator owns
> it — rewrite it when the scope settles.

**One repo; git holds versions. Never create a version-numbered sibling directory.**

## Governed by

`general/` — the governance layer, a submodule pinned by sha. If it is empty this checkout
is not governed and no gate may start:

    git submodule update --init --recursive
    bash general/checks/specs_exist.sh      # must print OK

Read `general/CLAUDE.md` at session start. Every rule, every check and every template lives
there; nothing is restated here. The revision this project runs under:

    bash general/tools/general_sha.sh       # recorded in every bundle (BS-10)

Moving the pin is a deliberate commit with a decision record in `docs/decisions/`.

## Read before acting

- `<project>/idea-stage/docs/research_contract.md` — **the single claim authority.** The question,
  the claims and their status. ARIS creates and consumes this path.
  ⛔ There is no `GOALS.md`, no `CLAIMS.md`, no `ROADMAP.md`. A launcher *references* claims
  ("this task tests C2 and C4"); it never restates them. Three claim ledgers disagree
  within a week.
- `launchers/LAUNCHER_<track>.md` — the active track. The authority on scope (WA-L.1).
- `docs/decisions/` — settled decisions, numbered. Not re-argued in a session; superseded
  by a new record or not at all.
- `data/README.md` — the input register, and the inherited-baseline rows (WA-L.3)

Read when the situation applies:
- `IDEAS.md` — deferred work. A session may propose promotion; it may never promote.
- `sidework/README.md` — before opening or reading a side investigation
- `docs/BLOCKED.md` — the open questions, with their recommended defaults

## Environment

- **Env:** `<env-name>` (never base).
  Local `<local env path>`; cluster `<cluster env path>`.
- **Root:** `<project root>`

## Project conventions

<Only genuine overrides. Each names the rule it overrides and why. Delete this section if
there are none — an empty conventions list is better than an invented one.>

- **OVERRIDE — script length ≤ N lines** (default 200). <why>

## File safety

- Source data is read-only, enforced by file mode (WA-D.1).
- Writes are confined to the paths declared in `.claude/settings.json` (WA-D.1) — and
  `.claude/settings.json`.
- All scratch goes to `ARIS_OUTPUT/` — gitignored, disposable, allowed to be messy.
- Numbers go to `results/<GATE>/` and nowhere else (WA-B.1).

## Before any negative or absence claim

A count of zero needs a positive control that the same code returns non-zero on a case known
to be present (EVIDENCE_STANDARDS §6). This project inherits none — every gate supplies its
own.

---

## ARIS pipeline state

_ARIS reads this file for research context and pipeline state. Keep these fields — its
skills consume them, and an empty one is read as "not set", not as "not applicable"._

| | |
|---|---|
| Research direction | `[the problem statement, one paragraph]` |
| Current stage | `[idea-discovery \| contract \| experiment-plan \| running \| review \| narrative \| paper]` |
| Target venue | `[journal or conference, or "thesis chapter N"]` |
| `AUTO_PROCEED` | `true` — this **is** `/research-pipeline`'s default; stated here explicitly because this project is meant to run unattended. When true, every selection checkpoint is informational: report the choice and continue. |
| Executor / reviewer | `[Opus 5 High]` / `[codex gpt-5.6-sol]` — `claude_profile.json` |
| Compute budget | see `launchers/LAUNCHER_<track>.md` §9 |
| Effort levels | `[skill:effort pairs, if you override defaults]` |

## Governance

This project is governed by `general/` — the working agreements constrain **how** ARIS
works; they do not replace **what** ARIS does. ARIS owns the pipeline, its artifacts
(`.aris/`, `research-wiki/`, `paper/`, `EXPERIMENT_PLAN.md`, `EXPERIMENT_LOG.md`) and its
loops. `general/` owns data integrity, evidence standards, report quality, compute policy,
Ibex usage, and which decisions are reserved for Melissa.

    bash general/checks/specs_exist.sh      # must print OK before any gate
    python3 general/tools/check_launcher.py launchers/LAUNCHER_<track>.md
