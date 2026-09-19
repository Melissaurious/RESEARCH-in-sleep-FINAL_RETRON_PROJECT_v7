# DECISION — STAGE 2 CLOSED, with explicit residual limitations

Date: 2026-09-19 · Track `rt07` · Status: **Stage 2 CLOSED · no further Stage-2 analysis**

Supersede by a new record, never by rewriting.

---

## 1 · Closure statement

> **Stage 2 (RT0–RT7 definition and the conserved-state mapper) is CLOSED.**
>
> The mapper `rtmap-1.0.0/53a1e738a19b3896` is validated within its stated scope (UG25
> confirmatory transfer, Endpoint A), frozen (`g4b`), and applied to the censused eligible
> Stage-1 catalogue (`g5`: 369,381 eligible, 354,102 inspectable). `g6` and `g7a` are landed
> and have each passed an independent, vendor-disjoint review with **zero blockers**; all
> required repairs are recorded as additive errata and no frozen output was altered.
>
> Stage 2 closes with these **explicit residual limitations**, which are part of the closed
> record and may not be silently dropped downstream:
>
> 1. **RT0 is UNRESOLVED / NOT IDENTIFIABLE.**
> 2. **RT1 is UNRESOLVED / NOT IDENTIFIABLE.**
> 3. **RT2 is PARTIAL** — only LtrA 97–123 of the reconstructed interval is observed.
> 4. **RT6 is separable only jointly with RT5** — the evidence supports the joint RT5+RT6
>    region, never RT6 alone.
> 5. **g6 is limited to descriptive concordance and bounded-use evidence** — reproducibility of
>    the mapper-derived descriptor across MyRT-defined strata, not independent discovery of
>    biological RT family structure.
> 6. **Stage 3 remains independent and untouched.** Nothing in Stage 2 defines, constrains or
>    pre-empts Stage-3 structural definitions.
>
> **Closure is workflow closure, not complete recovery.** It records that Stage 2's questions
> have been answered as far as the current instrument and evidence set allow. It does not claim
> that RT0–RT7 are historically recovered, that the unresolved labels are biologically absent, or
> that future primary evidence could not change an `UNRESOLVED` or `PARTIAL` status.

## 2 · What each closed component establishes — and only that

| component | closed as | governing records |
|---|---|---|
| mapper validation | Endpoint A: transfer to one fresh lineage (UG25) under `hhmake -M 50` | `2026-09-17_stage2_ug25_confirmatory_closed.md` |
| `g4b` production freeze | versioned instrument, packaging-reviewed 9/10 | `2026-09-17_stage2_g4b_production_packaging.md` |
| `g5a` + `g5` | censused denominator 369,381; canonical mapped dataset | `results/rt07_g5a_eligibility_census/`, `results/rt07_g5_catalogue_application/` |
| `g6` | descriptive concordance; independent review `PASS_WITH_REQUIRED_REPAIRS` 6/10, 0 blockers | `2026-09-18_stage2_g6_closure.md` read through `2026-09-19_stage2_g6_review_errata.md` |
| `g7a` | historical bridge, 4 ESTABLISHED / 2 PARTIAL / 2 UNRESOLVED; independent review `PASS_WITH_REQUIRED_REPAIRS` 7/10, 0 blockers | `2026-09-18_stage2_g7a_rt0_rt7_closure.md` read through `2026-09-19_stage2_g7a_review_errata.md` |

Final RT0–RT7 statuses, **unchanged by review**:

| label | status |
|---|---|
| RT0 | **UNRESOLVED / NOT IDENTIFIABLE** |
| RT1 | **UNRESOLVED / NOT IDENTIFIABLE** |
| RT2 | PARTIAL / INTERPRETIVE |
| RT3 | ESTABLISHED OPERATIONAL CORRESPONDENCE — with qualification |
| RT4 | ESTABLISHED OPERATIONAL CORRESPONDENCE — with frame-instability qualification |
| RT5 | ESTABLISHED OPERATIONAL CORRESPONDENCE — named jointly as RT5+RT6 |
| RT6 | PARTIAL / INTERPRETIVE — jointly with RT5 only |
| RT7 | ESTABLISHED OPERATIONAL CORRESPONDENCE — with narrowed wording |

All are **LtrA-local interpretation-layer correspondences**. Production emits `state_id` only;
the production crosswalk stays `UNRESOLVED` in all eight rows.

## 3 · Not established, and not claimable from Stage 2

Universal RT architecture · universal RT0–RT7 domains · residue-level accuracy against external
truth · transfer beyond UG25 · specificity against unrelated natural proteins · robustness under
`-M a2m` · equivalence under `-M 60` · independent discovery of RT family structure · any
accuracy of the mapper against MyRT / PADLOC / DefenseFinder labels · biological absence of any
region the instrument cannot see.

## 4 · Carried forward, deliberately open — not blockers

* **RT0/RT1 resolution** requires primary historical evidence (the defining source, Malik,
  Burke & Eickbush 1999, is not held). No inferential resolution is permitted.
* **g6 rank statistic** uses non-standard tie handling; standard Spearman would differ slightly;
  the per-half vectors were not landed. Frozen as reported; a re-run needs explicit
  authorisation.
* `human_input_audit: PENDING` on the landed bundles — required before any number becomes a
  thesis claim, per the governance layer.

## 5 · What happens next

* **No new Stage-2 analysis.** Any change to a closed Stage-2 result requires a new decision
  record and a new task.
* `g7b` (structural and published comparators) was split from `g7` and is **not started**; it
  is not a condition of this closure.
* **Stage 3A proceeds independently** and must freeze its own structural definitions. It may
  use the g7a bridge and the frozen `state_id` system **descriptively**, but **must not be
  presented as resolving RT0, RT1 or any other historical label.**
