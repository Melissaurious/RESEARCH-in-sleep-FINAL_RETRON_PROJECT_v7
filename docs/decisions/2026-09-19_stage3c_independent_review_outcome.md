# DECISION — Stage 3C independent review outcome: NOT PROMOTABLE; bundle frozen pending repairs

Date: 2026-09-19 · Track `s3c` · Status: **FAIL_BLOCK upheld · no promotion · re-runs unauthorised**

Supersede by a new record, never by rewriting.

*(This is the first `docs/decisions/` record for a Stage-3 ruling. The synthesis audit noted that
Stage-3 operator rulings had lived only inside analysis markdown, contrary to the project's
supersession rule; this record starts closing that gap for Stage 3C.)*

---

## 1 · What was done

The completed Stage-3C bundle (`analysis/stage3c_architecture_integration/`, commit `34000ee`) was
routed to an **independent, model-disjoint, read-only reviewer** — Codex (GPT-5.x) — as BS-15 and
WA-A.5 require: the bundle was produced by Claude Opus 5, and two subagents of that same family did
the literature retrieval, so the reviewer had to be outside that set.

* Request: `review-stage/INDEPENDENT_REVIEW_REQUEST_stage3c.md`
* Result, verbatim: `review-stage/INDEPENDENT_REVIEW_RESULT_stage3c.md`
* Verdict: **`FAIL_BLOCK`, 4.5/10, 5 blockers, 10 required repairs**
* Errata: `docs/errata/2026-09-19_stage3c_review_errata.md`
* Tier-B proposal: `review-stage/TIERB_APPENDIX_PROPOSAL_stage3c.md`

## 2 · The ruling

**All five blockers are upheld.** The author independently re-derived every contested number from the
landed tables before accepting it; the verification is tabulated in the errata §1. Two blockers
(B1, B4) are the serious ones: a **primary Stage-3C number was computed under a rule the governing
launcher does not declare** —

* the `13/14` replicate Jaccard mixes 7 truth-based and 7 detector-based pairs and is not computed
  over the same pairs as the `3/18` unit-count figure. Under the declared truth-bearing scope the
  result is **7/7 (median 0.882) versus 0/7**, from only **two** biological groups;
* every reported Region-X motif hit comes from an **undeclared wide-window fallback**. Under the
  launcher's own two-block rule, Region X is defined in **24/62** chains (3/21 retron) and **none of
  those 24 intervals contains NAXXH or AXXH**.

This is a process failure of Stage 3C, not of any upstream stage.

## 3 · Consequences, in force now

1. **Nothing from Stage 3C may be promoted to a thesis or paper claim.**
2. `CLAIM_EVIDENCE_MATRIX.tsv` rows **S05, S11, S12 and the Region-X part of S16 are WITHDRAWN**.
   S17 stands only as corrected by errata E-3C-7. The remaining rows are unaffected by the blockers.
3. **`STAGE3C_DECISION_REPORT.md` and `README.md` may not be read or cited without the errata.** The
   bundle is frozen and was not edited: no file in it has been changed or re-sealed.
4. The five required re-runs (R1–R5 in the errata §3) are **specified but not authorised and not
   performed**, per the operator's instruction that Stage 3C remains frozen.

## 4 · Stage-3B dependencies, reconciled

The synthesis audit's Stage-3B findings were checked against Stage-3C's prose:

| audit finding | does Stage 3C depend on it? | disposition |
|---|---|---|
| C-2 / OQ-02 — "CLOSED at PARTIAL" is a mislabel for a K5 stop | **yes**, inherited verbatim | superseded by E-3C-1 |
| in-sample calibration of `SEP_MIN`/`SEP_MAX`/`D_MAX` on the same 19 truth pairs | **yes**, the caveat was absent | superseded by E-3C-3; LOCO **12/5/2** now stated |
| stale "decoy pool 36" and "all six misses are adjacent-aspartate confusions" | **no** — neither string occurs anywhere in the bundle (re-checked) | no repair needed |
| C-5 — the 62-chain register was assembled downstream of Stage-3B catalytic-evidence collection | **yes**, unreported | added by E-3C-2 |
| C-6 — Tier B was inspected during 3B design | not in the primary rows (Tier B excluded) | constrains the Tier-B appendix only |
| OQ-11 — recommended dropping Comparison A | partially | A is retained but must carry E-3C-3 and E-3C-9; the reviewer judged the current bounding inadequate |

**No Stage-2, Stage-3A or Stage-3B output, threshold or verdict was altered by this stage or by this
record.**

## 5 · Operator decisions now open

| # | decision | recommended default |
|---|---|---|
| D1 | authorise re-runs R1–R5 to repair the blockers | **authorise** — until then Stage 3C cannot be promoted at all |
| D2 | Tier-B appendix: option A (build, 5 chains / 3 retron, exploratory), B (do not build; record retron architecture as untested), or C (wider population — not recommended) | **A**, after R1–R5 |
| D3 | whether to add a one-line pointer to this erratum at the top of the frozen bundle's `README.md` and report (requires re-sealing `MANIFEST`/`OUTPUTS`) | **yes** — a frozen report that cannot be read safely without an external document is a trap for the next reader |
| D4 | whether Stage 3B's own `PARTIAL` label should be erratum'd at source (synthesis audit OQ-02) — **a Stage-3B decision, not Stage 3C's to take** | refer to the Stage-3B owner |

## 6 · What this record does not do

It does not re-run anything, does not edit the frozen bundle, does not promote or retire any
upstream claim, and does not start downstream Stage-3 work. `human_input_audit` remains `PENDING`.
