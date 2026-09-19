# INDEPENDENT REVIEW RESULT — g7a historical RT0–RT7 bridge — **COMPLETED**

**This is the first independent adversarial review of this bundle to produce content.** The
2026-09-18 attempt failed on external capacity limits and produced no review; that failure is
recorded in `review-stage/g7a_review_packet/REVIEW_REQUEST_EXACT.md` and was never treated as acceptance.

## Provenance

| field | value |
|---|---|
| object under review | `results/rt07_g7a_rt0_rt7_bridge/` — frozen; **not modified, regenerated or recomputed** |
| review packet used | `review-stage/g7a_review_packet/REVIEW_REQUEST_EXACT.md + SECTION_INSTRUCTIONS_EXACT.md` — **unchanged** from the landed version |
| reviewer | **OpenAI Codex** via the `codex` MCP server |
| serving model | **`gpt-5.6-sol`**, reasoning effort `xhigh` — read from the session log's `turn_context`, not assumed |
| producer of the bundle | `claude-opus-5[1m]` — **vendor- and model-disjoint** from the reviewer |
| sandbox | `read-only`, `approval-policy: never` — the reviewer had no write access |
| working directory | the `rt07-g7a-bridge` worktree |
| thread id | `01a0b9a1-1d76-7193-9d7b-89cb6a41e875` |
| started / finished (UTC) | `2026-09-19T12:25:39.027Z` / `2026-09-19T12:35:08.850Z` |
| session log | `~/.codex/sessions/2026/09/19/rollout-2026-09-19T15-25-38-01a0b9a1-1d76-7193-9d7b-89cb6a41e875.jsonl` (local, not in git) |
| session log sha256 | `d1406ea155eb5c26525cb77aa3a7c4bcb190eaf0cc0ff840c8ace62f6f1471ed` |
| review text sha256 | `1c1ccb4e74dcba2afac4883a161ed5b79826c6edd51fbbf2cd16faad23eb1a38` — the verbatim text below |

## Outcome

| | |
|---|---|
| **verdict** | **`PASS_WITH_REQUIRED_REPAIRS`** |
| **score** | **7/10** |
| **blockers** | **0** |
| required repairs | 5 — all addressed as additive errata; see the errata record |

**All eight label statuses UPHELD; none downgraded, none upgraded.** **RT0 = UNRESOLVED / NOT IDENTIFIABLE and RT1 = UNRESOLVED / NOT IDENTIFIABLE were independently upheld.** The reviewer attempted no inferential resolution of either, and confirmed the bundle frames them as limits of the historical sources and of the instrument's reach (anchors from LtrA 97), not as biological absence.

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

### A. Evidence audit

**VERDICT: PASS_WITH_REQUIRED_REPAIRS**

**SCORE: 7/10**

All 25 packet-listed artifacts match their declared SHA-256 and byte counts. The following label judgments concern the scientific interpretation, not bundle integrity.

**RT0**

- **Historical definition/evidence:** Blocker is transcribed as describing M1–R85 as a fragment *containing* RT0 and A39 as internal to RT0. It does not define the RT0 C-terminal edge; Malik et al. 1999, the defining source, is missing ([evidence register](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g7a_rt0_rt7_bridge/tables/g7a_historical_evidence_register.tsv:2)).
- **Frozen-instrument observability:** None. Anchors begin at LtrA 97; RT0 evidence lies at or before 85.
- **Correspondence evidence:** Zero supporting states ([crosswalk](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g7a_rt0_rt7_bridge/tables/g7a_crosswalk_resolved.tsv:2)).
- **Limitation:** Both the historical definition and instrumental reach are insufficient—reason **C, both**. This says nothing about biological absence.
- **Final evidential status:** **UPHELD — UNRESOLVED / NOT IDENTIFIABLE.**

**RT1**

- **Historical definition/evidence:** The Blocker transcription places R85 *inside* RT1, not at its boundary. Xiong’s domain 1 is also reported as the only founding block not independently confirmed ([register](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g7a_rt0_rt7_bridge/tables/g7a_historical_evidence_register.tsv:7)).
- **Frozen-instrument observability:** None for reconstructed block 1, LtrA 39–61; the nearest mapped anchor is 48 residues away.
- **Correspondence evidence:** Zero supporting states; the proposed 39–61 interval also cannot represent the complete RT1 because R85 is stated to be internal to RT1 ([crosswalk](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g7a_rt0_rt7_bridge/tables/g7a_crosswalk_resolved.tsv:3)).
- **Limitation:** Again **C, both** historical-boundary insufficiency and lack of observability.
- **Final evidential status:** **UPHELD — UNRESOLVED / NOT IDENTIFIABLE.**

**RT2**

- **Historical definition/evidence:** Primary-source transcriptions support a second conserved block and a reconstruction procedure, but no LtrA residue boundaries ([register](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g7a_rt0_rt7_bridge/tables/g7a_historical_evidence_register.tsv:11)).
- **Frozen-instrument observability:** Seventeen anchors cover only LtrA 97–123 of reconstructed interval 79–123.
- **Correspondence evidence:** The RT2 assignment and its 79–123 interval are project-derived by ordinal propagation and comparator-point agreement; only the 97–123 portion is observed ([crosswalk](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g7a_rt0_rt7_bridge/tables/g7a_crosswalk_resolved.tsv:4)).
- **Limitation:** Residues 79–96 are outside the anchor span, and 79–85 conflicts with the source-described RT1 interior point at R85.
- **Final evidential status:** **UPHELD — PARTIAL / INTERPRETIVE.**

**RT3**

- **Historical definition/evidence:** The transcribed Xiong evidence says Poch motifs a–e correspond to domains 3–7 and Webster blocks correspond to domains 2–5 ([g1 quotes](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g1_history_and_definition/tables/g1_evidence_quotes.tsv:6)). No primary LtrA boundaries are stated.
- **Frozen-instrument observability:** Twenty-two anchors map within LtrA 126–166.
- **Correspondence evidence:** Reconstructed block 3 is cross-frame stable at Jaccard 0.911, and the comparator point is LtrA 160 ([coordinate carriage](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g7a_rt0_rt7_bridge/tables/g7a_coordinate_carriage.tsv:9)).
- **Limitation:** The LtrA interval and label attachment remain project inference. Route C is computationally distinct from Route P, but it is not an independent primary historical determination: the upstream audit calls the four frames coordinate transfers over one landmark set, not replication ([g3 README](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g3_prior_method_replication/README.md:64)).
- **Final evidential status:** **UPHELD — ESTABLISHED OPERATIONAL CORRESPONDENCE**, only with the existing LtrA-local “overlaps a portion” wording.

**RT4**

- **Historical definition/evidence:** Besides the general motif correspondences, Zimmerly directly identifies a 4/5 spacer ([g1 quotes](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g1_history_and_definition/tables/g1_evidence_quotes.tsv:17)).
- **Frozen-instrument observability:** Forty-two anchors map within LtrA 170–230.
- **Correspondence evidence:** The comparator point is LtrA 213, and the widest reconstructed gap supplies additional relative support.
- **Limitation:** The claimed `SUPPORTED_1_TO_1` class is too clean: block 4 splits into three in the independent alignment frame, with Jaccard 0.410 ([frame comparison](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g2_reference_reconstruction/tables/g2_frame_correspondence.tsv:5)). That uncertainty is absent from the closure wording.
- **Final evidential status:** **UPHELD — ESTABLISHED OPERATIONAL CORRESPONDENCE**, but its unqualified 1:1 cardinality requires repair.

**RT5**

- **Historical definition/evidence:** The catalytic YxDD motif is directly transcribed as lying in subdomain 5 ([register](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g7a_rt0_rt7_bridge/tables/g7a_historical_evidence_register.tsv:27)).
- **Frozen-instrument observability:** `CAT_STATE` 262 separately maps to LtrA 306/YADD, inside block 5; 34 anchor states cover LtrA 311–347. These denominators were not pooled.
- **Correspondence evidence:** This is the best direct feature-to-label anchor. Block 5 is stable across frames at Jaccard 0.955.
- **Limitation:** RT5 and RT6 are not separable in the frozen representation. The permitted statement correctly requires “joint RT5+RT6 region,” not RT5 alone ([closure table](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g7a_rt0_rt7_bridge/tables/g7a_closure_decision.tsv:7)).
- **Final evidential status:** **UPHELD — ESTABLISHED OPERATIONAL CORRESPONDENCE**, strictly many-to-one and joint with RT6.

**RT6**

- **Historical definition/evidence:** The source transcriptions support domain 6 and its correspondence to the fourth Poch motif, but supply no LtrA coordinate. They also report domain 6 as incomplete in some historical classes ([g1 quotes](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g1_history_and_definition/tables/g1_evidence_quotes.tsv:9)).
- **Frozen-instrument observability:** The same 34 anchors covering block 5 are observable.
- **Correspondence evidence:** RT6’s comparator point is 344, inside block 5, but its upstream blocks were order-interpolated and there is no independently mapped RT6-specific feature.
- **Limitation:** Nothing separates RT6 from RT5 in the frozen representation; the evidence supports only the joint RT5+RT6 interpretation ([crosswalk](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g7a_rt0_rt7_bridge/tables/g7a_crosswalk_resolved.tsv:8)).
- **Final evidential status:** **UPHELD — PARTIAL / INTERPRETIVE, jointly with RT5 only.**

**RT7**

- **Historical definition/evidence:** Blocker is transcribed as locating a proteolytic cleavage site “between RT7 and domain X” at R364/R365; Zimmerly names a 7/X spacer ([register](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g7a_rt0_rt7_bridge/tables/g7a_historical_evidence_register.tsv:32)).
- **Frozen-instrument observability:** Six anchors cover reconstructed block 6 at LtrA 356–361; the Route-C point is 357.
- **Correspondence evidence:** Block 6 is perfectly positionally reproduced across the two alignment frames, and it lies immediately N-terminal to the source-described cleavage landmark.
- **Limitation:** R364/R365 is first a proteolytic landmark described as lying between named regions. The source-described location is strong, but coincidence of a sequence-domain edge with the cleavage site is still an inference. The anchor endpoint at 363 is mere numerical proximity and is not a third independent validation route.
- **Final evidential status:** **UPHELD — ESTABLISHED OPERATIONAL CORRESPONDENCE**, without the endpoint-based “three independent routes” claim.

### B. Proposition audit

| Proposition | Judgment | Reason |
|---|---|---|
| RT0 unresolved | **CONFIRMED** | Both definition and observability fail; no biological-absence inference. |
| RT1 unresolved | **CONFIRMED** | R85 is internal, no edge is stated, and anchors start at 97. |
| RT2 partial | **CONFIRMED** | Only 97–123 of inferred 79–123 is observed, with an N-terminal source conflict. |
| RT3 established | **CONFIRMED WITH QUALIFICATION** | Stable reconstructed region plus comparator agreement, but not independent historical replication. |
| RT4 established | **CONFIRMED WITH QUALIFICATION** | Localization is defensible; unqualified `1_TO_1` is not, because block 4 splits across frames. |
| RT5 established | **CONFIRMED WITH QUALIFICATION** | Direct YxDD anchor; only a joint RT5+RT6 region may be named. |
| RT6 partial | **CONFIRMED** | No RT6-specific operational separation exists. |
| RT7 established | **CONFIRMED WITH QUALIFICATION** | Supported by block 6, point 357 and the source-described C-terminal landmark—not by the anchor endpoint itself. |
| Withdrawal of “RT0=M1–R85; RT1/7=R86–R364” | **CONFIRMED WITH QUALIFICATION** | Correct against the landed transcription; PDF wording was not independently inspected. |
| R85 lies inside RT1 | **CONFIRMED WITH QUALIFICATION** | Explicit in the landed Blocker transcription; not independently checked against the article. |
| RT5 anchored by YxDD | **CONFIRMED WITH QUALIFICATION** | The transcription and LtrA measurement agree; the 34 anchor states begin at residue 311 while `CAT_STATE` separately reports residue 306. |
| RT7 is the single “strongest correspondence” | **NOT ESTABLISHED** | RT7 has the strongest LtrA-local terminal coordinate; RT5 has the strongest transferable feature anchor. No common ranking makes one unconditionally strongest. |
| 5G2X is LtrA; 6AR1 is GsI-IIC | **CONFIRMED** | Verified directly from deposited CIF metadata. It changes comparator identity, not any RT0–RT7 inference. |
| Production remains label-free | **CONFIRMED** | All eight frozen production crosswalk rows remain `UNRESOLVED` ([production table](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g4b_production_mapper/control/CROSSWALK_RT0_RT7.tsv:7)); production schemas explicitly exclude historical labels ([schema](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g4b_production_mapper/code/rtmap/schema.py:28)). |
| Instrumental non-observability is not biology | **CONFIRMED** | The distinction is explicit in crosswalk and downstream-prohibition columns. |
| Historical track is “TERMINAL” | **CONFIRMED WITH QUALIFICATION** | Justified as a stopping rule for this frozen instrument and evidence set, after the repairs below. It is not justified as scientific finality: Malik 1999 is missing and historical-source ambiguities remain. |

### C. Source audit

- **Directly verified:** All packet hashes and byte counts; the 150-row bridge with 143 `MAPPED` anchors spanning LtrA 97–363; separate catalytic residue 306; unchanged production isolation.
- **Structural direct sources:** 5G2X identifies entity 3 as “GROUP II INTRON-ENCODED PROTEIN LTRA” and accession P0A3U0 ([5G2X CIF](/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/5G2X.cif:141)). 6AR1 identifies GsI-IIC RT from *Geobacillus stearothermophilus* and contains an eight-histidine expression tag ([6AR1 CIF](/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/6AR1.cif:112)).
- **Historical-source claims:** Per the binding packet, I treated all article quotations as project transcriptions and did not independently inspect the PDFs. The Blocker PDF’s SHA-256 matches the registered input, but that verifies file identity, not transcription accuracy.
- **Inaccessible source:** Malik, Burke & Eickbush 1999 is not held; it supports no finding in this review.
- **Source ambiguity:** The landed g1 transcription says Xiong directly mapped Poch motifs a–e to domains 3–7 and Webster blocks to domains 2–5. The g7a register instead marks several Poch-to-domain relations `project_inferred` and omits motif E/Webster evidence. That discrepancy requires correction.
- **Could not verify:** Printed Xiong/Blocker figure extents, exact article page typography, the Malik definition, and the claimed chronology that Amendment 1 preceded bridge execution beyond the bundle’s own provenance assertion.

### D. Additional findings

No **BLOCKER** was found.

- **REQUIRED — Route-C independence is overstated.** Assignment rule A4 calls the convergence categorically non-circular, while g3 says the four frames are coordinate systems over one anchor-derived landmark set, not independent determinations ([assignment rule](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/results/rt07_g7a_rt0_rt7_bridge/control/ASSIGNMENT_RULE.md:58)). State computational independence from Route P, but not independent replication of historical semantics.

- **REQUIRED — Correct the primary-evidence register.** The claim that RT5/YxDD is the only source-stated feature-to-number relationship conflicts with transcribed Xiong statements X05 and X06. Poch a–e/domain 3–7 and Webster/domain 2–5 must be represented as source-stated correspondences, with their coordinate limitations retained.

- **REQUIRED — Carry RT4’s instability into the crosswalk and downstream wording.** `SUPPORTED_1_TO_1` omits the independent-frame `SPLIT_INTO_3`, Jaccard 0.410 result. The terminal status may remain established, but the cardinality and uncertainty cannot remain unqualified.

- **REQUIRED — Narrow the RT7 claim.** Replace “stated domain junction” with “source-described between-domain proteolytic landmark,” acknowledging that edge coincidence is inferred. Do not count the frozen endpoint 363 as independent validation or use it to rank RT7 unequivocally above RT5.

- **REQUIRED — Supersede the stale launcher text.** The launcher still states the withdrawn “RT0=M1–R85; RT1/7=R86–R364” interpretation ([launcher](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/.claude/worktrees/rt07-g7a-bridge/launchers/LAUNCHER_03_rt0_rt7_closure.md:318)). Amendment 1 corrected execution, but the governing record remains internally inconsistent.

- **ADVISORY — D1 was not in the predeclared assignment control.** The RT6 downgrade called “declared rule D1” appears in `s07_closure.py`, not `ASSIGNMENT_RULE.md`. It is conservative and scientifically appropriate, but its provenance should be described accurately.

- **ADVISORY — Hash coverage.** All 25 review-packet hashes pass, but that packet omits the generator scripts that the bundle’s larger `OUTPUTS.tsv` hashes. This limits the packet-level integrity assertion; it did not prevent read-only inspection of the relevant logic.

The overclaims are therefore “genuine convergence, not circularity,” RT4’s unqualified 1:1 class, RT7’s “three routes/strongest” framing, and the assertion that RT5 is the only source-stated feature relationship.

### E. Strongest defensible statement

On LtrA, the frozen conserved-state system supports observable portions of project-reconstructed intervals corresponding operationally to RT3, RT4, the joint RT5+RT6 region, and RT7; RT5 has a direct catalytic-feature anchor, while RT7 has a strong source-described C-terminal proteolytic landmark. RT2 is only partial. RT0 and RT1 remain unresolved because both their recoverable historical boundaries and the frozen instrument’s N-terminal reach are insufficient.

These are LtrA-local interpretation-layer correspondences. They neither define universal biological domains nor validate the mapper, and they do not license absence claims.

“Historical track is TERMINAL” is defensible only as project workflow closure under the frozen evidence and instrument. It is not a claim that the historical literature is completely recovered or that future primary evidence could not change an unresolved status.

### F. Downstream-use assessment

- **Historical terminology in the thesis:** Permissible after the required source and wording corrections, with statuses and LtrA-local scope explicit.
- **Figure annotation:** Permissible for LtrA; show RT0/RT1 as unresolved, RT2 as partial, RT5/RT6 jointly, and RT4’s frame instability.
- **Descriptive comparison with Stage-2 states:** Permissible through the g7a interpretation table only. Production must continue emitting `state_id`, not historical labels.
- **Stage-3 structural interpretation:** May use the bridge descriptively but must remain independent and must not be presented as a way to resolve any label.
- **Classification reassessment:** Not supported.
- **Treating RT0–RT7 as universal domains:** Not supported.

**Reviewer model identity:** OpenAI Codex, GPT-5-family, as best exposed to me; the exact serving checkpoint is not available. This is disjoint from the bundle producer recorded as Claude Opus 5.
