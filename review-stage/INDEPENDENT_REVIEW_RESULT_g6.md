# INDEPENDENT REVIEW RESULT — g6 family architecture (BS-15) — **COMPLETED**

**This is the first independent adversarial review of this bundle to produce content.** The
2026-09-18 attempt failed on external capacity limits and produced no review; that failure is
recorded in `review-stage/INDEPENDENT_REVIEW_REQUEST_g6.md` and was never treated as acceptance.

## Provenance

| field | value |
|---|---|
| object under review | `results/rt07_g6_family_architecture/` — frozen; **not modified, regenerated or recomputed** |
| review packet used | `review-stage/INDEPENDENT_REVIEW_REQUEST_g6.md` — **unchanged** from the landed version |
| reviewer | **OpenAI Codex** via the `codex` MCP server |
| serving model | **`gpt-5.6-sol`**, reasoning effort `xhigh` — read from the session log's `turn_context`, not assumed |
| producer of the bundle | `claude-opus-5[1m]` — **vendor- and model-disjoint** from the reviewer |
| sandbox | `read-only`, `approval-policy: never` — the reviewer had no write access |
| working directory | the `rt07-g7a-bridge` worktree |
| thread id | `01a0b99f-4837-7ce1-9ddd-9d0138441c55` |
| started / finished (UTC) | `2026-09-19T12:23:38.891Z` / `2026-09-19T12:33:59.905Z` |
| session log | `~/.codex/sessions/2026/09/19/rollout-2026-09-19T15-23-38-01a0b99f-4837-7ce1-9ddd-9d0138441c55.jsonl` (local, not in git) |
| session log sha256 | `9c2bd8b3a1f63dc273bbe2c56c00a8e4e405771d534c1539f4eca42424dfa15e` |
| review text sha256 | `467a023203d1d9e23714c4c17db95852ef29725413380807db9fcaba9e2f5ffc` — the verbatim text below |

## Outcome

| | |
|---|---|
| **verdict** | **`PASS_WITH_REQUIRED_REPAIRS`** |
| **score** | **6/10** |
| **blockers** | **0** |
| required repairs | 8 — all addressed as additive errata; see the errata record |

**Bounded-use table: UPHELD, no row moves.** Descriptive figures remain PERMITTED only with the fuller captions required below; thesis-level biological claims, classification reassessment and independent-validation claims remain BLOCKED — now because g6 itself does not support them, not merely because review was pending.

## Scientific status vs workflow closure

These are different things and must not be conflated:

* **Scientific status** is what the frozen evidence supports, label by label or claim by claim.
  The review upheld it and bounded it; it did not extend it.
* **Workflow closure** means this project will do no further work on this question with the
  **current instrument and evidence set**. It is a stopping decision, not a claim that the
  question is fully answered. In particular, **`TERMINAL` for g7a means workflow closure for the
  current instrument and evidence set — not complete historical recovery of RT0–RT7.**

Required repairs are applied in the errata record; the frozen bundle is untouched.

---

## Verbatim review text

The text below is reproduced **exactly** as the reviewer returned it, extracted
programmatically from the session log (sha256 above). It has not been edited, reordered or
summarised. File links inside it point to paths as they existed in the worktree at review time.

---

# Independent BS-15 review

**VERDICT: PASS_WITH_REQUIRED_REPAIRS**

**SCORE: 6/10**

The frozen numerical evidence supports a reproducible descriptive measurement of concordance among sequence-derived annotation strata. It does not support independent validation, biological family structure, or classification reassessment. No blocker invalidates the narrow descriptive tables, but several interpretations and reporting details require an additive erratum or downstream correction. The frozen bundle itself should remain unchanged.

## C1–C10 determinations

| Claim | Determination | Evidence |
|---|---|---|
| **C1** | **CONFIRMED** | The provenance trace is correct: exact-RT `family_label` is `file_label.first()` in [b01_baseline.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/dbchar_g4_family_baseline/scripts/b01_baseline.py:59); `file_label` comes from the input filename in [e01_extract.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/dbchar_g2_canonical_units/scripts/e01_extract.py:203) and [g2lib.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/dbchar_g2_canonical_units/scripts/g2lib.py:68). Read-only counting of [g5_metadata_crosswalk.parquet](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt07_g5/g5_metadata_crosswalk.parquet) reproduced 369,370/369,381 matches, 11 `RVT-CRISPR|RVT-CRISPR-like` exceptions, 363,447 `by_myRT`, and 5,934 non-myRT records—all labelled `Retron`. Counter-direction qualification: 1.61% were not directly detected by myRT, so “effectively MyRT-derived” is correct; “every label is a direct myRT call” would not be. |
| **C2** | **CONFIRMED** | myRT uses an RVT profile-HMM search ([myRT-local-py3.py](/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/myRT-local-py3.py:66), [line 256](/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/myRT-local-py3.py:256)), supplemented by sequence similarity and phylogenetic placement ([line 309](/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/myRT-local-py3.py:309)). Thus the grouping and GII-HMM-derived occupancy measurement share sequence/profile modality. The counter-test in [diagnostic.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/ARIS_OUTPUT/rt07_g6_review/diagnostic.py:32) reproduced exactly: 61 groups, ρ=0.8689, NULL-2 p99=0.8779, versus family ρ=0.9865. It proves that beating NULL-2 is not automatic for every sequence partition. It does not establish independence or remove partial circularity. Moreover its p99 uses only 40 permutations ([diagnostic.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/ARIS_OUTPUT/rt07_g6_review/diagnostic.py:43)), inadequate to calibrate a 1% tail. |
| **C3** | **PARTIALLY CONFIRMED** | Read-only counting confirmed all 61,395 eligible Retrons have both `raw_myrt_family_label_set == Retron` and `system_types == Retron`; myRT supplies no subtype resolution. The bundle properly keeps DefenseFinder and PADLOC separate and calls them annotations, not truth ([PREDECLARATION.md](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/control/PREDECLARATION.md:115), [terminal table](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/tables/g6_terminal_decision.tsv:3)). Their exact internal RT-profile dependencies are not documented in the frozen g6 evidence, so that algorithmic subclaim was not fully independently established here. The safe conclusion is still comparator concordance, not validation. |
| **C4** | **CONFIRMED** | The read-only diagnostic reproduced ρ=0.5692 between full profile distance and absolute mean-MAPPED-fraction difference ([diagnostic.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/ARIS_OUTPUT/rt07_g6_review/diagnostic.py:49)). This is substantial association, but it is not “56.92% explained.” |
| **C5** | **PARTIALLY CONFIRMED** | The bundle accurately labels its number as hit-level: 14,943 retrieved hits, 11.22% at identity ≥0.90 ([g6_controls.tsv](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/tables/g6_controls.tsv:2)). A read-only parse reproduced 595/3,000=19.83% of sampled half-A queries with a ≥0.90 partner and 2,995/3,000 with any hit. The search is truncated at five targets per query ([s05_controls.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/scripts/s05_controls.py:45)). Thus 11.22% is not numerically wrong as a hit statistic, but it is the wrong/inadequate quantity if presented as prevalence of sequence-level leakage. The 19.83% is itself a one-direction, 3,000-query sample—not a full-dataset symmetric leakage rate. |
| **C6** | **PARTIALLY CONFIRMED** | Implementation is as claimed: NULL-1 shuffles sequences within mapped-fraction deciles ([arms.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/scripts/arms.py:133)); NULL-2 shuffles cluster labels within rounded cluster-mean strata ([arms.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/scripts/arms.py:152)). The 172,944/173,081 purity measurement is landed ([g6_cluster_family_purity.tsv](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/tables/g6_cluster_family_purity.tsv:2)). The exchangeability criticism is correct: NULL-2 preserves cluster counts, not sequence counts, and can change which groups qualify. However, opposite qualitative biases do not mathematically prove that “truth lies between” the two null distributions. They are sensitivity analyses, not demonstrated bounds. |
| **C7** | **PARTIALLY CONFIRMED** | The predeclaration specifies NULL-1 and a single significance rule ([PREDECLARATION.md](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/control/PREDECLARATION.md:134)); current code applies both nulls to all analyses ([s03_between_family.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/scripts/s03_between_family.py:22)). The five-group and NaN-null rules appear only in decision code ([s07_decision.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/scripts/s07_decision.py:23)), while V5 merely counts repair files ([verify.sh](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/verify.sh:57)). The lack of disclosure is confirmed. The exact chronology—specifically that expansion was decided only after observing PRIMARY’s result—cannot be independently reconstructed from the single landed commit. |
| **C8** | **CONFIRMED** | The incident is candidly recorded ([EXECUTION_INCIDENTS.md](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/control/EXECUTION_INCIDENTS.md:15)). `rt07_g6_prev` and the retained scratch have the same eligible FASTA SHA-256 and identical cluster-pair sets after sorting at all three identities; the landed counts are 181,696/97,659/88,642 ([g6_clustering_resource.tsv](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/tables/g6_clustering_resource.tsv:2)). This is adequate evidence that the duplicate-process incident did not select a scientific result. Caveat: the default rerun is not intrinsically cold—clustering and PC-SPLIT reuse existing files ([s01_clustering.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/scripts/s01_clustering.py:114), [s05_controls.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/scripts/s05_controls.py:45)). |
| **C9** | **PARTIALLY CONFIRMED** | Read-only counting reproduced 11,301 candidate 0.30 clusters, five qualifying groups, and 1,770 sequences in those groups. The landed null table contains zero usable NULL-2 replicates and NA p99 ([g6_within_retron_null.tsv](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/tables/g6_within_retron_null.tsv:6)); `UNDERPOWERED` is therefore preferable to a negative result ([s07_decision.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/scripts/s07_decision.py:32)). The stronger assertion that every replicate failed specifically because of the per-half threshold is not recoverable from the summary: NULL results are discarded whenever `rho` is NaN, which can also arise from degeneracy. No tool-independent corroboration exists. |
| **C10** | **PARTIALLY CONFIRMED** | No issue found invalidates the narrow descriptive measurement, so `FAIL_BLOCK` is not warranted. But “descriptive figures supported as-is” is too strong given the required provenance, leakage, power, null, and rank-statistic corrections. A ≤30%-identity clustering threshold also does not guarantee all cross-half pairs are ≤30% identical—PC-SPLIT already demonstrates why a greedy clustering threshold is not a pairwise independence guarantee. Biological claims, classification reassessment, and independent-validation claims remain blocked under the existing table ([bounded-use decision](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/docs/decisions/2026-09-18_stage2_g6_bs15_open_and_bounded_use.md:61)). |

## Findings, most severe first

- **BLOCKER — none.** The narrow descriptive tables remain usable.

- **REQUIRED — Reframe the result as comparator concordance.** The between-family grouping is overwhelmingly inherited from MyRT-labelled source-file categories. Required wording should say “split-half concordance among predominantly MyRT-derived family strata in a GII-HMM-derived occupancy space,” not independent validation or biological organization.

- **REQUIRED — Withdraw the literal “truth is bracketed” and “structure is real” language.** The bundle honestly reports null disagreement, but the nulls are not proven bounds. In particular, [g6_terminal_decision.tsv](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/tables/g6_terminal_decision.tsv:2) says structure is “real” under NULL-2; the evidence only says the observed statistic exceeds that particular imperfect permutation distribution.

- **REQUIRED — Qualify the “exceeds BOTH nulls” claim.** The literal six comparisons hold: all three visibility rows and all three relatedness rows exceed both reported p99 values, and in fact exceed the maxima of all 60 sampled replicates. But 60 permutations cannot calibrate a 1% tail—the smallest ordinary Monte Carlo p-value is 1/61≈0.0164—and there is no multiplicity control across 13 analyses. “Exceeds the reported empirical thresholds” is supported; “significant at 1% across the family of analyses” is not.

- **REQUIRED — Correct subtype power reporting.** The statistic requires ≥100 sequences in each half ([arms.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/scripts/arms.py:123)), but the strata table labels power using ≥100 total ([s04_within_retron.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/scripts/s04_within_retron.py:121)). Six strata are consequently marked powered but excluded: DF `Retron_VII_1`, `Retron_VII_2`; PADLOC `retron_IX`, `retron_VII-A2`, `retron_VII-A1`, `retron_X`. Twenty-six of 50, not 20, fail to enter a distance matrix.

- **REQUIRED — Report both leakage units.** Preserve 11.22% as “fraction of retrieved hits,” but add 595/3,000=19.83% as “sampled queries with at least one ≥90%-identity opposite-half partner,” including the sampling and `--max-seqs 5` limitations.

- **REQUIRED — Disclose the post-hoc procedural additions.** Record expansion of both nulls to every analysis, the five-group rule, and “missing null → UNDERPOWERED” as post-hoc rules. Counting one `REPAIR_*.md` file does not establish that only one analytic decision changed.

- **REQUIRED — Correct or relabel the rank statistic.** `_spearman` uses `argsort(argsort())`, which does not average tied ranks ([arms.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/scripts/arms.py:99)). On the landed positive-control counts it gives 0.9230, while standard tie-aware Spearman is 0.9307; the conclusion remains positive, but the reported statistic is not standard Spearman when ties exist. Half-distance vectors were not landed, so headline sensitivity to ties cannot be audited.

- **REQUIRED — Narrow visibility language.** CTRL-VIS shows persistence after conditioning on the scalar total MAPPED fraction. It does not eliminate state-specific GII-HMM callability or shared sequence/profile modality. Therefore “not an artefact of the GII-centred callability gradient” is too broad.

- **ADVISORY — Packaging/reproduction language.** The cold rerun is supported, but `run.sh` itself does not clear scratch. Also, two `__pycache__` files exist inside the bundle and are deliberately excluded from sealing ([seal.py](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/scripts/seal.py:95)). Their mtimes predate the freeze and no scientific effect was found, but “every file sealed” would be inaccurate.

## Bracket headline and “exceeds both”

The headline is honest insofar as it prominently reports that sequence-level and cluster-level permutations disagree. It is not honest as a mathematical bracket: no result proves the target null distribution or biological truth lies between them.

The six advertised “exceeds both” rows are numerically correct. Their defensible interpretation is:

> The observed concordances exceed every sampled replicate from both reported permutation procedures on those six populations.

They should not be promoted to globally calibrated 1% significance, proof against all mapper-visibility artefacts, or biological family structure.

## Bounded-use table

No existing row should move from PERMITTED to BLOCKED, provided permitted descriptive use carries the additional repairs above.

- Descriptive figures: remain **PERMITTED**, but not “as-is.” Captions must disclose MyRT-derived family provenance, tool-stratum status, both leakage denominators, null limitations, and corrected subtype power counts.
- Stage-3 mapping on frozen `state_id`: remains **PERMITTED** with existing visibility/occupancy caveats.
- Thesis-level biological claims: remain **BLOCKED**, now because g6 itself does not support them—not merely because review was pending.
- Classification reassessment: remain **BLOCKED**.
- Independent-validation claims: remain **BLOCKED**.

A claim of a guaranteed ≤30%-identity train/test separation should not be added to PERMITTED use.

I found no place where PADLOC or DefenseFinder is explicitly treated as truth; the tables repeatedly identify them as tool annotations. The main concern is that generic “family organization” rhetoric obscures the MyRT provenance of the between-family labels.

## Additional checks

- PRIMARY `n_sequences=353,248` is confirmed in [g6_between_family_rho.tsv](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g6_family_architecture/tables/g6_between_family_rho.tsv:2); 36 of 42 families qualify.
- No multiplicity adjustment was found.
- I independently ran the static verifier: 17/17 PASS.
- I independently ran `bundle_valid.sh`: BS-1..BS-10 PASS, `bundle_status: REPRODUCIBLE`; it additionally reports `human_input_audit: PENDING`.
- Input SHA-256 values match `INPUTS.tsv`.
- The worktree remained clean; nothing was modified.

## Could not verify

- The exact C7 decision chronology before the single landed commit.
- Headline sensitivity to standard tie-aware Spearman, because half-specific distance vectors and null replicates are not landed and I did not recompute the frozen analysis.
- Individual permutation distributions beyond their landed median/p99/max summaries.
- The precise failure mechanism of every label-free NULL-2 replicate.
- Full DefenseFinder/PADLOC model internals from the frozen packet.
- Mapper universality or transfer, intentionally outside scope.

## Reviewer identity

**OpenAI Codex, GPT-5-family model.** The exact deployed checkpoint identifier is not exposed to me. This is vendor/model-lineage disjoint from the recorded producer, `claude-opus-5[1m]`.
