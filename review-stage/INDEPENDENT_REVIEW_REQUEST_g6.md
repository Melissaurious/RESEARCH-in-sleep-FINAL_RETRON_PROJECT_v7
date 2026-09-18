# INDEPENDENT REVIEW REQUEST — `rt07_g6_family_architecture` (BS-15) — **OPEN**

**Status: OPEN. No independent scientific review has been produced.**

This is the durable, git-tracked copy of the review packet. The working original the operator
named is `ARIS_OUTPUT/rt07_g6_review/CLAUDE_SELF_AUDIT.md`, which sits under the gitignored
scratch tree (`.gitignore:2  ARIS_OUTPUT/`) and would not survive a scratch clean or a fresh
clone. This copy exists so the packet is not lost. The scratch original is unchanged.

## Why this gate is open

The g6 bundle **and** the self-audit reproduced below were both produced by
`claude-opus-5[1m]` (`results/rt07_g6_family_architecture/PROVENANCE.md`, field `models:`).
BS-15 requires an adversarial pass to assert its own model is DISJOINT from that set, so the
self-audit does **not** satisfy the gate. It was filed as a Layer-2 cheap preflight
(`docs/PROJECT_ANALYSIS_PRINCIPLES.md` Principle 19), not as the independent review.

## Attempt 1 — 2026-09-18 — FAILED, external cause, no review produced

* Routed to the `codex` MCP server: cross-vendor, disjoint model, `sandbox: read-only`,
  `approval-policy: never`, cwd the g6 worktree. It had **no write access** to the bundle and
  could not have altered it.
* Outcome: **failed before producing any finding.** Verbatim cause returned by the tool:
  `You've hit your usage limit. … try again at Sep 19th, 2026 12:16 PM.`
* **The failure was solely an external account usage/credit limit.** It was not a refusal, not
  a timeout, not a defect in this packet, not an error in the bundle, and **not a scientific
  finding of any kind**.
* **Zero review content was produced** — no confirmation, no refutation, no verdict, no partial
  output. Nothing from this attempt may be cited as review evidence, in either direction.
* Operator decision, same day: do **not** substitute another Claude model at this stage; keep
  BS-15 **explicitly OPEN**; rerun **this same packet** after the limit resets.

## Retry instructions

Rerun unchanged against the same bundle, from the g6 worktree, read-only. The document below is
what is under review: propositions **C1–C10**, each stated so it can be confirmed or refuted
individually against file/line/number evidence. Two of them warrant extra scrutiny because they
cut in opposite directions:

* **C2** contains the one counter-test whose result *favours* the bundle (a pure sequence
  partition, ρ = 0.8689, failing its own NULL-2 p99 = 0.8779). An exculpation produced by the
  same model that produced the bundle deserves the hardest check.
* **C1 / C5** are criticisms of the bundle (myRT label provenance; leakage denominator
  19.8 % vs the reported 11.2 %). These may equally be wrong in the bundle's favour.

The reviewer should report both directions with equal prominence.

---

# Claude Opus self-audit of g6 — the document under independent review

Produced by `claude-opus-5[1m]`, which ALSO produced the g6 bundle. It therefore fails the
BS-15 independence gate and was filed as a self-audit, not the independent adversarial review.
An independent reviewer is asked to confirm or refute each numbered claim below.

## Claims made by the self-audit

### C1 · The 36-family grouping variable is effectively MyRT-derived
Trace asserted:
`stage1_collapsed_family` (in `data/derived/rt07_g5/g5_metadata_crosswalk.parquet`)
 ← `family_label` = `file_label.first()` in
   `results/dbchar_g4_family_baseline/scripts/b01_baseline.py` line ~66
 ← `file_label` assigned by `g2lib.file_label(fname)` in
   `results/dbchar_g2_canonical_units/scripts/e01_extract.py` line ~208
 ← source corpus filename `master_<LABEL>_merged_oriented.jsonl`
   (corpus at `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june/`)

Measured claim: `stage1_collapsed_family == raw_myrt_family_label_set` for
**369,370 / 369,381 = 99.997 %** of eligible RTs; the 11 exceptions are CRISPR/CRISPR-like
multi-label collapses. Also claimed: 363,447 / 369,381 eligible RTs have `by_myRT = true`, and
the 5,934 that do not are **all** labelled `Retron`.

### C2 · Therefore g6 is comparator concordance, not independent validation
Claim: myRT assigns family by profile-HMM scoring of the RT domain, and g6 measures
state-occupancy against a GII-derived profile HMM, so the grouping variable and the measurement
share a modality. Labelled "partially circular annotation".

**Counter-test the self-audit ran (and reports as exculpatory):** a pure sequence partition
(0.30-identity clusters, 61 qualifying groups, same INSPECTABLE population, same halves, same
statistic) gives rho = 0.8689 and does **NOT** exceed its own NULL-2 (p99 = 0.8779), whereas the
family labelling rho = 0.9865 exceeds its NULL-2 (0.9066). Conclusion drawn: exceeding NULL-2 is
not automatic for sequence-tracking labels, so the circularity objection bounds but does not
void the result.

### C3 · DefenseFinder/PADLOC subtype labels are external but not independent
Claim: they are defense-system detectors whose retron subtype models use RT profile similarity
among other components, so they are "external but not independent" — comparator agreement, not
validation. Supporting fact claimed: myRT does not resolve retron subtype at all
(`raw_myrt_family_label_set` and `system_types` are the single string `Retron` for all 61,395
eligible retrons), which is why DF/PADLOC were used instead.

### C4 · Mapper visibility contributes substantially to the distance structure
Measured claim: Spearman between (a) the upper triangle of the full 150-dimensional
between-family correlation-distance matrix and (b) |difference in each family's overall mean
MAPPED fraction| = **0.5692**.

### C5 · The cross-half leakage figure is quoted on the wrong denominator
The bundle reports "11.22 % of hits at identity >= 0.90". The self-audit claims the
scientifically meaningful quantity is sequence-level: **595 / 3,000 = 19.83 %** of sampled
half-A sequences have a >= 90 %-identity partner in half B, and that the hit-level figure is
partly an artefact of `mmseqs easy-search --max-seqs 5`. Total cross-half hits 14,943; queries
with any cross-half hit 2,995 / 3,000.

### C6 · NULL-1 / NULL-2 implementation and interpretation
Claim: both are implemented in `results/rt07_g6_family_architecture/scripts/arms.py`
(`permuted_null`, `cluster_permuted_null`), NULL-1 permutes labels among SEQUENCES within a
`mapped_fraction` decile, NULL-2 permutes labels among whole CLUSTERS within the same stratum.
The repair (`control/REPAIR_1.md`) argues NULL-1 is invalid because 99.92 % of clusters span
exactly one family. The self-audit accepts the bracket framing as justified but flags residual
exchangeability gaps: NULL-2 preserves each label's CLUSTER count but not its SEQUENCE count,
and family sizes span 175,588 (RVT-GII) down to ~100.

### C7 · The outcome-triggered expansion to both nulls was NOT disclosed
Claim: the decision to compute NULL-1 for every analysis (not only PRIMARY) was taken AFTER
observing that PRIMARY failed NULL-1. It was applied non-selectively, but the trigger was
outcome-dependent and appears nowhere in `control/` or the decision record. Two other post-hoc
rules (the `MIN_GROUPS_FOR_A_VERDICT = 5` guard, and "NaN null -> UNDERPOWERED") ARE disclosed,
but only in `README.md` section 6, not in `control/`. `verify.sh` check V5 counts
`control/REPAIR_*.md` files and reports "1 repair cycle used", which the self-audit calls false
assurance.

### C8 · The cleared-scratch rerun neutralises the execution incident
Claim: `control/EXECUTION_INCIDENTS.md` records that a step was wrongly declared dead from a
namespace-limited `ps` check and a duplicate process was launched; the step had never stopped.
The self-audit claims the subsequent cold rerun (scratch directory moved aside, mmseqs genuinely
re-executed, identical cluster counts 181,696 / 97,659 / 88,642 from the same input sha256)
eliminates any concern about contaminated outputs. It also flags that `s01_clustering.py:119`
and `s05_controls.py:46` contain cache-skip branches, so a rerun WITHOUT clearing scratch would
silently reuse cached intermediates, and `run.sh` does not clear scratch itself.

### C9 · The label-free arm is underpowered rather than a negative result
Claim: 5 qualifying groups out of 11,301 candidate 0.30-clusters; every NULL-2 permutation
replicate fell below the >= 100-in-both-halves stratum threshold, so no null could be computed
(p99 = NaN). The self-audit argues non-reproducibility cannot be asserted against a null that
does not exist, so `UNDERPOWERED` is correct and the within-Retron result consequently has no
tool-independent corroboration.

### C10 · No fatal issue
Claim: nothing invalidates the DESCRIPTIVE conclusion; the gate is a reproducible descriptive
measurement. Thesis biological claim and classification reassessment were marked
`NOT YET SUPPORTED`; descriptive figures `SUPPORTED AS-IS`; train/test stratification
`SUPPORTED WITH QUALIFICATION` but at <= 30 % identity rather than 90 %.

## Other self-audit assertions worth checking
* PRIMARY `n_sequences` = 353,248, not 354,102, because 6 of 42 families do not qualify.
* No multiplicity control across the 13 analyses; each tested at its own p99.
* The bundle passes 17/17 `verify.sh` checks and `bundle_valid.sh` BS-1..BS-10,
  `bundle_status: REPRODUCIBLE`.
