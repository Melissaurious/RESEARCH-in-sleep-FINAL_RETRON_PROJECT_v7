# HUMAN_INPUT_AUDIT — specification

**Status: SPECIFIED, NOT MASS-APPLIED.** This defines what `human_input_audit: DONE` means. It is a
**promotion gate only**. It does not block Batch One, and historical bundles are not audited
retrospectively as a batch.

**Why it exists.** `BUNDLE_SPEC.md` makes `human_input_audit: DONE` a precondition for promoting any
number to a paper or thesis claim. Across every worktree the string appears in exactly one file: the
specification that defines it. Twelve of twenty-nine result bundles omit the field entirely, including
both bundles carrying the terminal Stage-2 claims and both carrying the instrument freeze and its
confirmatory run. **So no number in this project is currently promotable under its own governance.**
That is a real gate, not a formality, and it has never once been exercised.

---

## 1 · Scope, deliberately narrow

Audit **only** bundles that are candidates for a thesis chapter or a manuscript. Do not audit for
completeness, do not audit to clear a backlog, and do not treat an unaudited bundle as suspect. An
unaudited bundle is simply not yet promotable.

A bundle enters the queue when a stage synthesis proposes one of its numbers for promotion.

## 2 · The nine checks

A human, not a model, confirms each. `DONE` requires all nine, or an explicit recorded exception.

| # | check | what failure looks like here, from this project's own history |
|---|---|---|
| 1 | **inputs** — the exact input population, hashes and versions are the intended ones | an anchor table living inside a bundle whose own gate failed |
| 2 | **unit and denominator** — the analytical unit and denominator are correct **for the proposed claim** | a rate computed on records in a project whose governance says records are not a biological unit; a 6.6-fold spread compared across tool-defined subsets rather than a fixed locus set |
| 3 | **controls** — every required control ran and passed | a placement positive control commented out in its runner; an acceptance criterion with an 84.8% ceiling against a required 95%, never run, instrument frozen anyway |
| 4 | **ordering** — the criterion and falsification rule preceded execution | a selection cutoff landing exactly at the winner-flip point of its own sweep |
| 5 | **forbidden inputs** — none was consumed | a prohibited reconstruction set reintroduced into a derivation |
| 6 | **numeric provenance** — every promoted number resolves to a canonical table cell | a same-strand figure wrong by 0.7 points, hardcoded as a string literal in a producing script, propagated into four index documents |
| 7 | **completeness of the record** — known errata, negative results and limitations are represented | a frozen report containing zero references to its own binding errata |
| 8 | **wording** — the proposed claim does not exceed the task and stage evidence | a gate label read as a biological conclusion |
| 9 | **immutability** — the exact audited bundle and git commit are identified and unchanged | a superseded statistic still in print in two files |

## 3 · The record

One row per audit, appended to `docs/HUMAN_INPUT_AUDIT.tsv`, never edited in place.

```
auditor · date · bundle · git_commit · scope · status · exceptions_or_notes
```

- `status` is `DONE`, `DONE_WITH_EXCEPTIONS`, or `REFUSED`.
- `scope` names **which claims** were audited. A bundle is rarely audited whole; auditing three
  numbers does not certify the other forty.
- `exceptions_or_notes` is mandatory for `DONE_WITH_EXCEPTIONS` and names each exception and why it
  is acceptable for the specific claim being promoted.
- `git_commit` pins the audited state. A later commit to that bundle voids the audit.

## 4 · What the audit is not

- **Not a review.** Independent scientific review is a separate step and happens before this one.
- **Not automatable.** Checks 2, 8 and 7 are judgement. A model may prepare the evidence; a human
  signs.
- **Not transitive.** Auditing a bundle does not audit what it cites.
- **Not a blocker on analysis.** Tasks run, stages synthesise, reviews happen. Only **promotion**
  waits.

## 5 · Relationship to the task machinery

`TASK_STATE=PASS` means the task executed validly. `SCIENTIFIC_OUTCOME` says what it found. Neither
is promotion. The full path stays:

```
task -> validation -> stage synthesis -> independent review -> human_input_audit -> claim registry -> thesis/paper
```

Batch One produces none of these. Its outputs are consumable by downstream tasks and are not claims.
