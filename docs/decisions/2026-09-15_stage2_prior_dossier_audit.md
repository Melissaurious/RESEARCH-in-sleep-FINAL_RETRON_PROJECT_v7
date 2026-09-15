# DECISION — Stage-2 prior-dossier audit: what carries forward and in what role

Date: 2026-09-15 · Track: `rt07` · Status: **binding for `LAUNCHER_02_rt0_rt7_definition.md`**

Audits `general/RETRON_STAGES/02_rt0_rt7_definition.md` (963 lines), which is a **prior
scientific and design dossier, not established truth**. Supersede this record by a new
record, never by rewriting it.

> **Partially superseded, 2026-09-15 — `docs/decisions/2026-09-15_stage2_operator_decisions.md`.**
> That later record is the authority on the *decision status* of four items left open here:
> §G.1 (`ALIGN_000044` acquisition), §G.2 (inclusion rule for non-bacterial RT structures,
> which also supersedes the acquisition deferral in the §D non-LTR R2 row), §G.5 (Stage 04
> stays separate) and §G.6 (Xiong & Eickbush Fig. 1 digitisation). §G.3 and §G.4 remain
> deferred. Every **classification** in this record — `KEEP_AS_DESIGN`, `RE_DERIVE`,
> `USE_AS_PRIOR`, `COMPARATOR_ONLY`, `MOVE_TO_LATER_STAGE`, `REJECT/SUPERSEDED` — stands
> unchanged, as does every correction in §F. Nothing below is rewritten.

## Classification vocabulary

| class | meaning |
|---|---|
| `KEEP_AS_DESIGN` | the design reasoning is adopted; no prior number comes with it |
| `RE_DERIVE` | must be independently regenerated under Stage-1 inputs before any use |
| `USE_AS_PRIOR` | a prior reading or expectation, to be re-verified at its primary source |
| `COMPARATOR_ONLY` | may be compared against; may never seed the reconstructed frame |
| `MOVE_TO_LATER_STAGE` | in scope for the project, out of scope for `rt07` |
| `REJECT/SUPERSEDED` | withdrawn, mis-stated or measured wrong; must not re-enter |

**No prior numerical result is an acceptance criterion in `rt07`.** Every figure below that
carries a number carries it as something to reproduce or to refute, never as a target.

## A · The five registered prior claims

| item | prior content | class | why, and what `rt07` does instead |
|---|---|---|---|
| `D1` | a reproducible operational definition exists: landmarks at match states 146 (RT3) / 229, 99.91% held-out, 214–441× above a positional null, on frame `RT17_CORE` | `RE_DERIVE` | The design survives and is a genuine methods contribution; the numbers do not travel. Every one was computed on a frame and stratum that `g3` must re-establish, and the held-out figure is measured against a validation set now known to be 100% seed-overlapping. `g3` regenerates each figure with (frame, stratum, n) attached; `g4` re-derives the definition on the full-length set. |
| `D2` | RT1 fails its own declared ≥0.90 concordance bar, at 0.75 and 0.62 in a second frame | `RE_DERIVE` | A refuting result is a result (WA-G.5) and this one is scientifically interesting, but it inherits the same frame/stratum problem. `g3` re-measures. ⚠️ Whether this is reported as a limitation of the method or as an independent recovery of a weakness Xiong & Eickbush flagged in 1990 is an **operator decision** — the dossier is explicit that our 2026 concordance and their 1990 evidence caveat are different objects and must not be conflated. |
| `D4` | Toro's published span sits at approximately anchor −197 … +57, with 80 verbatim matches | `RE_DERIVE` | Small, clean and unpublished. Re-derive in `g7` as a comparator alignment, not as a boundary source. The associated never-executed step `PE8` — implement Toro's convention exactly and ask whether the published frame changes any surviving result — is `KEEP_AS_DESIGN` and belongs in `g7`. |
| `D6` | landmark enrichments of 2,657× / 4,936×, Region X as family-exclusive | `REJECT/SUPERSEDED` | Withdrawn **by the prior work itself**: regeneration gives 224× / 445×, roughly 12× apart, and Region X is weak rather than family-exclusive. Neither the original nor the regenerated values enter `rt07` as criteria. If an enrichment measurement is wanted it is a fresh `g6` measurement. |
| `D9` | the RT0 void is expected, because Zimmerly, Hausner & Wu 2001 define subdomain 0 as conserved only between group II intron and non-LTR RTs, and retrons are neither | `USE_AS_PRIOR` | **The single most load-bearing prior reading in the dossier**, and the reason the launcher forbids scoring RT0 on the same footing as RT1–RT7. It is quoted verbatim from p.1241, so it is checkable — and `g1` must check it at the PDF rather than inherit it. If it holds, "do retrons have RT0?" is malformed as posed, and the answerable question becomes whether conserved structure exists N-terminal to RT1 in retron RTs and whether it corresponds to the group II intron / non-LTR RT0. The `OUT_OF_FRAME` call state exists to report this honestly. |
| `D10` | a registered trap: do not cite Simon & Zimmerly 2008 as licensing a `LIV` criterion, because their "nearly always hydrophobic" is position 2 while the excluded class differs at position 1 | `USE_AS_PRIOR` | A trap already paid for. `g1` records it in the unresolved-definition register so it cannot be re-walked. |

## B · Frames, strata and validation sets

The dossier is emphatic that **three frames × four strata is the design**, and that any
number quoted without naming both frame and stratum is unattributable. `rt07` adopts that
discipline as a build failure condition, not a style preference.

| item | prior content | class | why |
|---|---|---|---|
| `RT17_CORE` | the frame carrying the `D1` and `D2` numbers | `RE_DERIVE` | A sequence-derived frame whose match states come from an alignment which comes from a seed set. It is not an independent coordinate system, so it cannot validate itself. `g2` rebuilds a frame from the derivational sources; `g3` maps prior results onto whatever `g2` produces. |
| `A_span17` | the 17-state span frame | `RE_DERIVE` | One of three distinct objects; retained as a named comparison frame only. |
| `B_full` | the full-length frame | `KEEP_AS_DESIGN` | This is the object the full-length derivation rule requires. The design carries forward into `g4` §7e; the prior numbers on it do not. |
| `anchors72` | used as the validation anchor set; "72/72 concordance" widely quoted | `REJECT/SUPERSEDED` **as a validation set**; `USE_AS_PRIOR` **as a contamination measurement** | Two separate findings. (1) "72/72" is the `n_anchor_rows` sample size, **not a concordance** — per-motif concordance ranges 0.75–1.00, so the quote reports the denominator as the result. (2) The prior audit measured **72 of 72 exact seed members, 100% overlap**, and only **26 of 72 have a structure at all**; the other 46 are sequence-propagated. Consequence: anchor concordance measured internal consistency of the frame, not out-of-sample validity. **The phrase "72 structure-validated anchors" is banned in `rt07` outputs.** `g4` re-measures the overlap and builds a new held-out design. |
| `gold175` / `gold175_uniq` | gold panel, 171 unique members | `RE_DERIVE` | Prior audit measured 44 of 171 exact seed members, 25.7%. Re-measure before any use; usable only as a stratum with its overlap stated. |
| "external" referee producers | 42 of 63 reported inside the `RT17_CORE` seed | `RE_DERIVE` | The externality of a referee set is a measurement, not a label. Re-measure in `g4`. |
| Khan experimental panel | reported to overlap the Mestre lineage strongly | `RE_DERIVE` | The most attractive candidate independent panel, so its overlap matters most. `g4` measures it before relying on it. |
| retron / nonretron occupancy strata | retron 78,287 · nonretron 423,274, selected unconditionally on `family` only | `RE_DERIVE` | The **design is exemplary and is kept**: exactly one selection criterion, no completeness, length, score or detection filter, explicitly to stop the profile reporting the selection instead of the population. The **counts** are superseded by Stage 1, whose exact-RT unit is 501,561 and whose family labels and eligibility predicates are landed and hashed. |

### The circularity that remains open one level up

The dossier states it plainly and `rt07` inherits the problem, not a solution: the occupancy
*measurement* was unconditioned, but the *stratification* was not — `family == 'Retron'`
came from PADLOC, DefenseFinder and myRT, which are the detection conventions being audited.

Classification: `RE_DERIVE`, and the prior scoped fix — validate the retron label
corpus-wide at a declared bit threshold — is `KEEP_AS_DESIGN`. In `rt07` this is handled by
taking family labels from Stage-1 `rt_tool_calls_v1`, where per-tool provenance is preserved
and not pooled, and by reporting every family-stratified result with the label's provenance
named. `C7` covers this and is declared `supporting` in the launcher.

## C · Prior design and code worth keeping

| item | class | why |
|---|---|---|
| `d1a_build_sets.py` unconditional-selection design | `KEEP_AS_DESIGN` | The one-criterion rule that fixed the previous attempt's voiding circularity. Adopt the rule; re-derive the sets. |
| `d20b_domain_methods.tsv` + `D2.0_METHOD_LANDSCAPE.md` | `KEEP_AS_DESIGN` | A method survey already carrying `can_define_RT0`, `circularity` and `what_it_CANNOT_do` columns. This is the natural starting row set for `g1`'s operational-evidence matrix, which makes `g1` cheaper than it looks. Rows are re-graded under `rt07`, not imported as verdicts. |
| `d21b_truncation_verdict.py` | `KEEP_AS_DESIGN` | A falsification test declared as a gate before running: is a structural negative at the N-terminus admissible? That is the RT0 region, and it is the closest thing on disk to an empirical test of whether N-terminal absence can be believed. Read before designing `g4`'s `NOT_DETECTED_INSPECTABLE` rule. |
| `d21c_sse_agreement.py` | `KEEP_AS_DESIGN` | Second declared falsification test: do two secondary-structure algorithms agree closely enough to set an edge? Directly constrains what an edge uncertainty interval may claim. |
| `d20a_capability_probe.py` | `KEEP_AS_DESIGN` | What each method *can* define. Feeds `g1`. |
| the full-length-before-HMM route | `KEEP_AS_DESIGN` | Recorded in the dossier as the publishable route and **never executed**. It is now launcher §7e and is the core of `g4`. |
| the per-family report table design | `KEEP_AS_DESIGN` | Concrete column set for `g6`. |
| `D_instrument` / `d_instrument_audit` / `M_models` scripts generally | `RE_DERIVE` | Code reusable after inspection; measurements independently regenerated. The audit arm is the more valuable of the two — it is what found the defects. |

## D · Structural material

| item | prior content | class | why |
|---|---|---|---|
| Simon & Zimmerly subdomain ↔ block mapping | RT domains 1–7 constitute the palm and finger domains and are generally alignable across RTs; domains 0 and 2a are shared among only a subset of RT classes; domain X corresponds to the thumb | `USE_AS_PRIOR` | The published mapping, quoted verbatim in the dossier. `rt07` **reports and tests** it and never assumes it. It is also the second independent line supporting `D9`. Consequence the launcher enforces: fingers/palm/thumb and RT0–RT7 are different partitions of the same protein and neither defines the other. |
| `d2j_boundary_crossval.tsv` structural transfer | Jaccard of derived match states against DSSP fingers/palm/thumb: fingers 0.74–0.84, palm 0.52–0.55, thumb 0.00–0.21 | `USE_AS_PRIOR` + `RE_DERIVE` | The gradient is exactly what the 2008 mapping predicts, which makes it a genuine two-line agreement and the answer to "I found the palm — is it where it should be?". Re-derive in `g7` under a pinned structural toolchain; report as comparator agreement, never as ground truth. |
| "structure cannot adjudicate a boundary, because it never set one" | prior arm's own finding | `KEEP_AS_DESIGN` | A **provenance** statement, not a claim that geometry is uninformative: the published conventions were never derived from structure, so structure cannot arbitrate between two conventions that both descend from sequence. This is why the launcher lets structure constrain and falsify but not manufacture the partition. |
| 25 crystals with boundaries extracted, including 6AR1 group II intron RT | on disk | `COMPARATOR_ONLY` | Usable as constraint in `g7`. The binding limit is that only 26 of 72 anchors have any structure, so a structure-first frame would be built on 26 proteins and propagated by sequence — the same transfer step one layer down. |
| ESMFold inside `D_instrument`, structural rescue pilot, full fingers/palm/thumb segmentation | prior arms | `MOVE_TO_LATER_STAGE` | Stage 04. `rt07` uses structure as validation and constraint only. |
| non-LTR R2-type RT structure | absent locally, needs network | `MOVE_TO_LATER_STAGE` | Blocks a full RT0-correspondence test. Acquisition is an operator decision; the launcher plans it and does not fetch it. ⚠️ **Acquisition status superseded 2026-09-15** by `2026-09-15_stage2_operator_decisions.md` §B: governed acquisition is now approved inside `rt07` under the predeclared inclusion rule. The classification is unchanged — the structure is a comparator that may constrain or falsify but not define the RT1–RT7 partition, and full structural segmentation stays Stage 04. |
| three foldseek installs, no agreed semantic version | tool-identity defect recorded by the prior stage | `RE_DERIVE` | One build must be pinned and recorded before any structural comparison. Graded `DO-NOT-USE` in launcher §4 until pinned. |

## E · Published comparators

| item | prior content | class |
|---|---|---|
| Simon & Zimmerly transferability measurement — retrons 157 alignable characters versus group II introns 177, DGRs 179, five other groups 126–167, and only 59 alignable across the entire set, being the 59 characters in RT domains 3–5 | the only published measurement of how far the RT1–RT7 frame transfers | `COMPARATOR_ONLY`, and the **primary external benchmark for `g6`** |
| Toro 2014 RT0–RT7 FASTA, 742 sequences (count verified 2026-09-15) | published RT0–RT7 block reference set | `COMPARATOR_ONLY` |
| Mestre 2020 tree and supplementary assignment table | published retron reference | `COMPARATOR_ONLY` |
| myRT reference profile, alignment, tree | closest published reusable RT profile | `COMPARATOR_ONLY` |
| Toro 2026 / SPIRE HMMs, phylogeny, pipeline | preprint comparator | `COMPARATOR_ONLY` |

⭐ The transferability numbers are the single most useful comparator in the dossier and the
thing a per-class occupancy matrix with n per block strictly improves on. They also say
**retrons are the hard case** — 157 against group II's 177 — which is the launcher's reason
for keeping retron a named stratum rather than a headline.

⚠️ The dossier records that this project's own register held only this paper's "20
groupings" claim and **never extracted the transferability numbers**, though the paper was on
disk throughout. `g1` extracts them.

## F · Items rejected or corrected

| item | class | correction |
|---|---|---|
| "72/72 concordance" | `REJECT/SUPERSEDED` | a sample size, not a concordance |
| "72 structure-validated anchors" | `REJECT/SUPERSEDED` | 26 of 72 have structures; 46 are sequence-propagated; all 72 are seeds |
| `D6` enrichment magnitudes | `REJECT/SUPERSEDED` | 224× / 445× on regeneration, not 2,657× / 4,936×; Region X weak, not family-exclusive |
| "domain-based phylogeny" for the prior tree | `REJECT/SUPERSEDED` | the tips were a 341-aa tetrad window, not the derived domain |
| the window cut as a settled parameter | `RE_DERIVE` | the load-bearing parameter's basis is a choice, and not this project's choice |
| `E4` motif basis | `RE_DERIVE` | the tree session built no HMM and re-derived no motif; the basis was inherited unverified from a previous project version |
| prior myRT model counts, roughly 2,051 seeds over 47 families | `REJECT/SUPERSEDED` | `RVT-All.hmm` measured 2026-09-15 holds **45 models and 1,988 summed NSEQ**, matching the myRT publication's own statement of 45 HMM models for 41 RT classes from 1,988 RVT_1 sequences |
| a Toro 2026 claim that retrons lack RT0 | `REJECT/SUPERSEDED` | the dossier itself retracted this on 2026-09-12 as a mis-attribution inherited from a summary and never checked against the source. It must not reappear |
| `rt_proteins.faa` registered at a V5 path | `USE_AS_PRIOR` | the file is in V3, 77,685 sequences; the register named the wrong tree. Verify at the point of use |

## G · Unresolved, and who decides

*As recorded on 2026-09-15 at the time of this audit. Items 1, 2, 5 and 6 were resolved later
the same day by `docs/decisions/2026-09-15_stage2_operator_decisions.md` (§A–§D); items 3 and 4
remain deferred and stay in launcher §9b. The text below is the historical statement of the
questions and is left as written.*

Carried into launcher §9b as stop-and-wait items:

1. **Acquire `ALIGN_000044`?** High value — the primary-source alignment behind the only
   Tier-1 paper that numbers subdomains. Registered `MISSING_NOT_ACQUIRED`. Resolve before
   or during `g1`, ideally before `g2`. Operator authorises the network fetch.
2. **Inclusion rule for non-bacterial RT structures**, to be written *before* any are added.
   `D9` implies that testing an RT0 claim needs group II intron, non-LTR, telomerase and
   viral RT structures, so the 25 crystals are a seed, not the population.
3. **Is the operational definition its own methods paper?** The prior `D6` debate.
4. **How is RT1's concordance failure reported** — limitation of this method, or independent
   recovery of a weakness the founding authors flagged? Defensibly the latter, and the
   dossier judges that the stronger paper, but it is a scientific-framing call.
5. **Does stage 04 come first or merge?** The dossier argues the crystals already supply
   fingers/palm/thumb boundaries, so RT0–RT7 landmarks might be anchored on that geometry
   rather than derived and reconciled afterwards. `rt07` as written does **not** merge them;
   changing that is an operator decision because it changes the anti-circularity design.
6. **Digitise Xiong & Eickbush Fig. 1?** The dossier notes the figure legend says "See text
   for a description of the criteria used in this assignment" and reports 42 conserved
   positions, so the familiar story that the 1990 boundaries were drawn by eye with no
   published criterion **may be false**. Digitising the figure converts the provenance chain
   from assertion into measurement. Scoped in `g1`; the effort is an operator call.
