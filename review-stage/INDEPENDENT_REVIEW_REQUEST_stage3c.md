# Independent review request — Stage 3C architecture integration

**Date:** 2026-09-19 · **Track:** `s3c` · **Bundle commit:** `34000ee` ·
**Bundle:** `analysis/stage3c_architecture_integration/`

**Reviewer independence (BS-15, WA-A.5).** The bundle was produced by Claude Opus 5 (1M context);
two subagents of the same family performed literature RETRIEVAL only. The reviewer must be
**disjoint** from that set. This request is routed to Codex (GPT-5.x), **read-only**: the reviewer
may read anything in the repository and must write nothing.

## What to review

`analysis/stage3c_architecture_integration/` — read `README.md` and `STAGE3C_DECISION_REPORT.md`
first, then the crosswalks, `CONTRADICTIONS_AND_UNCERTAINTY.tsv`, `CLAIM_EVIDENCE_MATRIX.tsv` and
the scripts under `scripts/`. The governing launcher is
`launchers/LAUNCHER_03C_architecture_integration.md`.

Stage 3C is **post-hoc and descriptive**. It must not change, re-tune or re-interpret Stage 2,
Stage 3A or Stage 3B, and it issues no merged verdict.

## Focus areas (the operator's list, in order)

1. **Correctness of the frozen joins** — residue-key joins onto the frozen Stage-3A partition
   (`rt_pdp_primary.residues.tsv`), the Stage-2 state-block join, and the literature/historical
   boundary joins. Are the keys, denominators and strata right? Is any row silently dropped?
2. **Dependence on the unresolved Stage-3B limitations** (see below).
3. **Interpretation of catalytic-site versus structural-unit stability** — is the claim that site
   *location* is more reproducible than the partition supported, or does it rest on a construction?
4. **RT0–RT7 crosswalk interpretation** — is the LtrA-local, sequence-level scope respected? Is
   anything said about RT0/RT1 that the frozen evidence does not support?
5. **Provenance of literature fingers/palm/thumb boundaries** — is the numbering verification
   sufficient? Are unverified sources properly excluded rather than quietly used?
6. **Region X/Y claims** — especially the Region-Y/ncRNA-specificity language.
7. **Termini/fusion interpretation** — the anchor-series truncation caveat and the two insertion
   measures.
8. **Whether any claim exceeds the available retron-specific evidence.** This is the operator's
   central worry. Comparison A contains **no retron chain**.

## Stage-3B issues raised by the project synthesis audit — reconcile explicitly

From `…_v7-synthesis/analysis/project_synthesis/PROJECT_EVIDENCE_MAP.md` §2.4 and concerns C-2, C-5,
C-6, and `OPEN_QUESTIONS.tsv` OQ-02 and OQ-11:

* **C-2 / OQ-02:** Stage 3B is labelled "CLOSED at PARTIAL" but terminated on a **fired kill
  criterion K5**; in the launcher, PARTIAL means a bounded-scope pass *on Tier B*, which was never
  evaluated. The audit calls the label a mislabel and asks for `STOPPED_ON_K5`.
* **Unreachable PASS branch:** Tier B contains 0 `HARD_PAIR` chains; its truth is single residues
  while a HIT requires both predicted residues in the truth set.
* **In-sample calibration:** `SEP_MIN` 75, `SEP_MAX` 115 and `D_MAX` 6.0 Å were set from the same
  Tier-A truth pairs the detector is then scored on, so every truth pair is admissible by
  construction. Out-of-sample LOCO is **12 HIT / 5 MISS / 2 ABSTAIN**, not 13/6/0.
* **Superseded statements locked in a landed bundle:** `cat3b_g2/README.md` still says "all 6 misses
  are adjacent-aspartate confusions" and "decoy pool 36"; both are superseded (corrected pool 19).
* **C-5:** the Stage-3A population was assembled by Stage 3B **for catalytic truth** (retron
  structures plus 9Z6Y added *because* they carry catalytic evidence), so Comparison A's
  concordance sits downstream of a selection made for that purpose.
* **C-6:** Tier B was partly inspected during Stage-3B design, so it is **not blind** for future use.
* **OQ-11** recommended running Comparison C only, dropping A and deferring B. The operator
  commissioned all five comparisons instead. Judge whether Stage 3C's bounding of A is adequate.

State, for each: does the Stage-3C bundle depend on the defective statement, and if so where, and
what is the minimum documentary repair?

## Tier-B question to rule on

Comparison A currently uses **Tier-A own-chain truth only** (19 chains, no retron). The operator has
asked whether a **clearly separate, descriptive, lower-confidence Tier-B retron appendix** would be
defensible — it may not change the primary verdict, may not be pooled with Tier A, and may not
re-tune any threshold. Given C-6 (Tier B inspected during design) and the unreachable-PASS issue,
say whether such an appendix is defensible **as a location description using the Tier-B truth
labels only** (not detector output), and under exactly what wording limits — or whether it should be
refused.

## Required output

A written review with:

1. **Verdict**: `PASS` / `PASS_WITH_REQUIRED_REPAIRS` / `FAIL_BLOCK`, plus a score out of 10.
2. **Blockers** (must fix before any promotion), each naming the file and line/row.
3. **Required repairs** (documentary), each with the exact superseded wording and the corrected
   wording you would accept.
4. **Advisory notes.**
5. **Per-focus-area findings** for all 8 areas above.
6. **Tier-B appendix ruling** as described.
7. **What you could not check**, explicitly.

Do not rewrite the bundle. Report only. Every criticism should name the artefact it is about; where
you verify a number, say how you verified it.
