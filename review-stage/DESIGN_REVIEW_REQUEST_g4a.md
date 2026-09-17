# Independent adversarial review — g4a frame recovery (EXECUTED), request record

The first reviewed object in this track that is an **executed methods study** rather than a
design. Four prior reviews of earlier formulations failed: 3/10, 4/10, 4/10, 5/10.

    backend:            codex (mcp__codex__codex, new thread)
    reviewer_model:     gpt-5.6-sol, model_reasoning_effort xhigh
    executor_model:     claude-opus-5[1m]
    sandbox:            read-only, cwd = the project root
    date:               2026-09-16
    verdict vocabulary: PASS | PASS_WITH_REQUIRED_REPAIRS | FAIL/BLOCK

## Reviewed object

    docs/decisions/2026-09-16_stage2_g4a_frame_recovery.md            b326089324776968
    results/rt07_g4a_frame_recovery/
      control/PREDECLARATION.md                                       ee5bfa9197e42411
      control/ERRATA.md                                               7396e2b3e44bb2b7
      verify.sh                                                       ec1951fee929f749
      README.md                                                       c501f2b7e4e2751d
      g4a_method_and_failure_modes.md                                 ed05a3fa55fd42a1
      stage1_retron_augmentation_design.md                            d93ece3f55553a63
      tables/  (12 tables, hashes in the bundle)
      scripts/ (5), INPUTS.tsv (16 rows: the one sequence input, 5 scripts,
               the harness, the predeclaration, and all 8 tool binaries)

## What was asked

The operator's twelve questions, plus these, added by the executing session because they are the
places this study is most likely to be wrong:

- **is `42/42 DYAD_CORRESPONDS` trivially true?** If each consensus carries exactly one `[YF]xDD`
  and the profiles align well, finding them aligned may be near-inevitable rather than
  informative;
- **is hhalign probability 74.2–100.0 impressive or expected?** All RTs are homologous.
  **There is no negative control — no non-RT profile was tested** — and the reviewer was told so
  explicitly;
- **is SELF 424.1 vs CROSS 32.6 informative or near-tautological?** ("a family profile matches its
  own family best");
- **which thresholds are predeclared and which crept in post-hoc** — cd-hit 0.50, `hmmsearch -E 10`,
  the ±2 transitivity tolerance, the ≥20-position triple filter, the 250 aa floor;
- **is "aligned to all 6 partners" a meaningful definition of global**, or an artefact of choosing
  exactly seven families;
- **can the harness be gamed**, given it has a `--regenerate` mode;
- **are there further errors of the same class as the self-reported ERRATA?** Two of the four
  produced plausible *false negatives*; the reviewer was asked to independently re-derive the dyad
  correspondence and the transitivity;
- whether `g4a PARTIAL` is the right verdict, or the evidence supports something stronger or
  weaker.

The reviewer was asked to **run `verify.sh` itself** and report what it actually did. Note: the
reviewer's sandbox is read-only, so the harness may be unable to create its temporary reproduction
directory; if it reports that, the failure is the sandbox, not the harness, and the executing
session's own run is recorded in this bundle.

The reviewer was told not to inflate, and explicitly: *"four prior rounds failed; do NOT fail this
one from momentum if it genuinely fixed the defects, and do NOT pass it from fatigue if it has
not. A study that correctly reports a PARTIAL result with honest limits is not thereby
defective."*

## Outcome

Recorded in `review-stage/AUTO_REVIEW.md` after the round completes.

---

## Submission log

The reviewed object is a **frozen snapshot**. It has not been modified between submissions.
Manifest: 31 files (excluding `work/`), 16 tables, 7 scripts. Selected hashes:

    control/PREDECLARATION.md                        ee5bfa9197e42411
    control/ERRATA.md                                7396e2b3e44bb2b7
    verify.sh                                        c1ae6d306112f5f4
    tables/g4a_between_family_correspondence.tsv     b96bfbf0eca10994
    tables/g4a_dyad_anchor_correspondence.tsv        65d0d54b23786b71
    tables/g4a_supported_intersection.tsv            c55ad4ed6bc8e67c
    tables/g4a_negative_control.tsv                  5822b684e9754f33
    tables/g4a_transitivity.tsv                      f4e8eba80780ea41

| attempt | time | outcome |
|---|---|---|
| 1 | 2026-09-16 ~14:0x | ran ~4 min, then terminated: *"You've hit your usage limit … try again at 4:38 PM."* **No score, no verdict, no findings.** |
| 2 | 2026-09-16 14:42 | refused immediately, same quota message. Not submitted. |
| 3 | 2026-09-16 16:40 | **submitted and running.** Bundle integrity re-verified against the frozen manifest immediately before submission: all hashes match. Identical prompt, identical snapshot. |

**Attempt 2 carried the operator's sixteen explicit questions**, including the load-bearing one:
whether the absence of a completely held-out RT family is a blocker for `g4b`, to be classified as
`A` (cluster-level challenge sufficient), `B` (whole-family holdout required) or `C` (not
identifiable/necessary) — explicitly not as "nice to have".

### Alternative backends were checked and none is admissible

- `copilot` resolves to a **stub that is not installed** — it offers to download GitHub Copilot
  CLI. Installing and authenticating a new external tool needs operator approval under launcher
  §9b (credentials/permissions not already available), so it was not pursued.
- The only MCP reviewer server configured in this session is `codex`.
- Every model available through the executing session's own Agent tool is **Claude-family**, and
  the executor is `claude-opus-5`. `WA-A.5` forbids a same-family reviewer, and `review_gate.py`
  fails closed on same-family executor/reviewer pairs. **Self-review was not performed and is not
  admissible.**

### State

`rt07_g4a_frame_recovery` remains **EXECUTED, REPRODUCIBLE and UNREVIEWED**. No gate call has been
made for it, because `review_gate.py` requires a score and a verdict and neither exists. The
bundle is unchanged and this request can be re-submitted verbatim once the quota resets.
