# COORDINATION STATE

**As of 2026-09-20.** One page. Everything a coordinating session needs to take over, or to resume
after a gap. Written to be useful whether coordination stays here or moves.

---

## 1 · Urgent, not scientific

**A live API key is in plaintext in the user's Claude configuration, in an MCP environment block, and
was printed into a session transcript.** Rotate it. Reported by a task session; deliberately not
inspected further by this session, because inspecting it repeats the exposure rather than fixing it.

**The 88 MB Stage-1 workbench is backed up** at
`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7_SEPTEMBER/backups/`, sha256
`140a0062…d39b25`, verified on read-back, manifest at `docs/BACKUP_MANIFEST.tsv`. Previously it
existed in no branch at all.

## 2 · Where the work is

| tier | branch | tip |
|---|---|---|
| index, governance, review | `project-synthesis` | `d391220`, **9 commits unpushed** |
| promoted state | `main` | `94a1a78` |
| evidence | eight task branches | unchanged |
| Batch One artifacts | five `task/*` branches | pinned, §4 |

**The GitHub remote is public.** Verified by unauthenticated probe, HTTP 200, `"private": false`.
Ten branches are already pushed, including one whose commit message records an independent review
returning a blocking failure. Disclosure was decided some time ago; the unpushed commits add candour
to a repository that already carries a great deal of it.

## 3 · Board

| state | n |
|---|---|
| PASS, Batch One complete | 5 |
| HELD, dependency unmet | 6 |
| DRAFTED, launcher not written | 3 |
| AWAITING_SPECIFICATION | 2 |
| AWAITING_ADOPTION | 1 |
| CLOSED_CURRENT_EVIDENCE / _DESIGN | 2 |

Machine-checkable status: `programme/PREFLIGHT_STATUS.tsv`. Gate tests: `PREFLIGHT_TESTS.tsv`,
10 of 10 pass, including the one that must **allow** a valid negative through.

## 4 · Batch One, pinned

| task | commit | outcome |
|---|---|---|
| T-REG-asset-registration | `9052ccb` | DESCRIPTIVE |
| T-LINT-prose-numbers | `82059df` | SUPPORTS_H1 |
| T-A0-lineage-variance | `c724df7` | **BOUND** |
| T-A2-ladder-population | `a1b76d1` | SUPPORTS_H1 |
| T-A23-crosspair-curation | `98f3125` | DESCRIPTIVE |

All five gate-verified by the coordinating session independently of their own reports. The
criterion-bearing interval was re-bootstrapped here and reproduced.
Synthesis: `programme/BATCH_ONE_SYNTHESIS.md`.

⛔ **THE REVIEW IS DONE AND IT RETURNED FAIL.** A handoff from a terminating task session states the
Batch One review is "still outstanding". **That is stale and must not be acted on.** It ran on
2026-09-20 in fresh thread `01a0bc53`, read-only, and returned **FAIL**: three tasks FAIL, two
ACCEPT_WITH_CHANGES. Verdict verbatim at `review-stage/BATCH_ONE_INDEPENDENT_REVIEW_VERDICT.md`.
**Do not re-dispatch it.** Nothing was promoted at any point.

## 5 · Open decisions, operator only

1. **Rotate the exposed key.**
2. **Push or do not.** Nine commits, tag `programme-prelaunch-v1`. Remote is public.
3. **Reviewer routing.** Both reviewers probed available today. A proposal would narrow the
   established one to implementation conformance; it must carry an explicit supersession clause or
   two contradictory standing rules will coexist. The better replacement is role separation: an
   invocation may not adjudicate work it authored, repaired or advised on.
4. **Adopt the confirmatory rule**, including the far-confirmation minimum. No number was invented.
5. **Clear `human_input_audit`.** It appears nowhere but the spec defining it, so nothing is
   promotable under the project's own governance. Spec at `programme/HUMAN_INPUT_AUDIT_SPEC.md`.
6. **Fix the sandbox.** Task sessions cannot write into their own worktrees; four of five worked
   around it. This should be fixed, not worked around again.
7. **Resolve dual coordination.** Four documents shaping this programme have never been seen by this
   session: a prior-work lookup rule, a batch-two candidates file, a reviewer narrowing, and a
   drafted decision record.

## 6 · Findings that outlive Batch One

| # | finding |
|---|---|
| 1 | The interval generator behind the landed pairing results has **~65% coverage against a nominal 95%**. Bears on every interval those scripts produced; none examined. |
| 2 | Effective sample size settled three ways: 12.5 is a Kish count over pair weights, 1075 is a formula defect, **≈463** is the estimator's actual effective n. |
| 3 | **No interval at the 50%-identity lineage level exists.** Homolog groups nest inside components, so that blocking is degenerate. |
| 4 | Only **0.217%** of asset collections are named exactly by any registry; 86.9% of bytes named at no depth. |
| 5 | Published cross-pair evidence: 56 rows, but **42 rest on one caption-expansion decision** and 6 more on a single sentence. Defensible floor is single digits. Zero numeric values. |
| 6 | Five review conclusions were reversed by looking outside the nine declared worktrees. The cause was scope, every time. |

## 7 · Standing rules a successor must not relax

- Controls are tasks, they run first, and they block.
- Task validity is not hypothesis truth. A refuted hypothesis is a **successful task**.
- A biological contrast may not be a blocking control unless independently established.
- Populations deplete. The pairing holdout is already spent and cannot be recovered.
- No number in prose without a table cell behind it.
- Prior work supplies assets and bounded negatives. Its numbers are unverified until re-derived.
- Fail closed. If a reviewer is unavailable, record it and stop; never substitute silently.
