# RESEARCH CONTRACT — [project]

_The **standing science**: what this project is trying to establish, and against what.
Stable across stages — you revise it when the science changes, not when a task changes.
The per-task document is `launchers/LAUNCHER_<track>.md`, which names which claims it settles._

Target length: **40–100 lines.** If it is longer, it has absorbed a launcher's job.

## The question

[One paragraph. What is not known, and why it matters. Not a method, not a plan.]

## Claims

Every claim is born `UNPROVEN`, before any gate runs. It reaches the paper only from
`SUPPORTED` with circularity `NONE` or `LOW` (`general/agreements/EVIDENCE_STANDARDS.md` §3).
**`REFUTED` is a result, not a failure** — a week with three REFUTED claims is a good week.

| id | claim | status | settled by | circularity |
|---|---|---|---|---|
| `C1` | `[one sentence, scoped to what will actually be examined]` | `UNPROVEN` | `[gate id, once it lands]` | `[NONE\|LOW\|MEDIUM\|HIGH]` |

⚠️ Scope every claim to what was audited — *"no X in the Y chain"*, never *"no X"*.
An overstated claim that later fails somewhere unexamined was avoidable at zero cost.

## Datasets

| name | path | what it is | trust |
|---|---|---|---|
| `[name]` | `[/abs/path]` | `[…]` | `[RAW\|FROZEN:<bundle>\|RE-DERIVE\|DO-NOT-USE:<why>]` |

Read-only, always. A schema document is a hypothesis about the data, not ground truth.

## Baselines and metrics

| claim | metric | baseline compared against | why that baseline can disagree |
|---|---|---|---|
| `C1` | `[metric, with unit and denominator]` | `[the honest comparator]` | `[shared dependency, if any]` |

⭐ The last column is the one that matters: two methods agreeing is evidence **only if they
could have disagreed** (§4). A baseline sharing a hidden dependency agrees whenever that
dependency is wrong.

## Kill criteria for the project

[What result would make you abandon this line entirely — not just this stage? Written now,
before any number exists, because this is the only moment it is honest.]

## Key decisions

| date | decision | why | supersedes |
|---|---|---|---|

Append-only. A superseded decision stays visible with its date — silent correction destroys
the audit trail that makes the rest trustworthy.

## Known-wrong

[Artefacts that exist and are WRONG, and what makes them untrustworthy. ⚠️ Absence is loud;
wrongness is quiet — a stale artefact reads as ready and nothing prompts a check.]
