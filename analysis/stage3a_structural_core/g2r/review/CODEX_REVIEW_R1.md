# Codex independent review — round 1 (g2r pre-registration, parser driver, provenance)

* Reviewer: Codex (MCP `codex`), read-only sandbox, cwd `analysis/stage3a_structural_core/g2r`
* Thread: `01a0b9a6-a790-7ec0-9434-ca94a39aa69f`
* Reviewed: `G2R_PREREGISTRATION.md` @ ee49f57e, `scripts/RunPDP.java`, `review/biojava_pdp_source/*`,
  `review/{g2_align.py,mkdssp_run.py,sse.py,ANTICIRCULARITY_CONTRACT.tsv}`
* Not shown: any fingers/palm/thumb boundary, `reference_boundaries.*`, motif coordinates, Stage 3B, RT0–RT7.
* Reviewer statement: "No files were modified, and I did not inspect any prohibited boundary source."
* **Verdict: PROCEED_WITH_FIXES (F1–F7).** Response: `G2R_AMENDMENT_1.md`.

Verbatim review text follows.

---

Bottom line: the PDP objective is non-degenerate, but the plan should not execute yet. There are fixable implementation, validation, and definition blockers.

## 1. C3 mathematics

**BLOCKING**

- The disclosed `size1t` expression is a real bug: Cut.java:72 adds `from-from+1`, so every preceding segment contributes 1 residue instead of its inclusive length. It affects recursive cutting of discontinuous domains, not the initial contiguous chain. It distorts both side sizes, the normalization denominator, the average-density normalization, and potentially the chosen cut or whether a cut occurs. Its direction is not uniformly conservative or liberal.
- Several additional reachable defects are presently undisclosed:
  - `to2` is assigned `getFrom()` at Cut.java:82, making that flank–flank contact loop empty.
  - Double-cut normalization uses `Math.max(MAXSIZE,size2)` rather than an apparent `Math.min` at Cut.java:360.
  - The large-domain double-cut adjustment writes `max_contacts[k]` instead of `[nc]` at Cut.java:370.
  - Multi-segment double-cut construction writes a middle segment at `dom1.nseg` instead of `dom2.nseg` at CutDomain.java:133. This can create an unused/null leading segment and potentially fail recursion.
  - Several inclusive segment calculations are paired with `< to` contact loops, causing endpoint omissions.
  - The merge code computes capped sizes but applies its powers to the uncapped variables at ClusterDomains.java:80.
- Running the library unchanged can be defensible only as "BioJava 7.1.4 PDP behavior," not as a verified faithful execution of published PDP. In the current plan it is not sufficient merely to disclose the first typo: the validation must explicitly exercise discontinuous-domain/double-cut behavior, or a separately preregistered corrected implementation must be used.

**NON-BLOCKING**

- The primary split normalization does use 1.3/3=0.43333, consistent with an approximate reported alpha=0.43, at Cut.java:134.
- The decision process is non-degenerate: candidate inter-part contact densities depend on contacts and sizes; the minimum is normalized by the domain's average candidate density; double cuts must improve the score and pass a second cutoff; the subsequent merge uses inter-domain contact density. It does not algebraically collapse like the voided objective.
- Merge normalization uses different exponents, 1.6/3 and 1.4/3, so "alpha 0.43" should be described specifically as the split normalization, not the entire parser.

## 2. Implementation and residue mapping

**BLOCKING**

- `RunPDP` calls the correct public parser entry point, but it does not enforce the promised single-chain invariant. `getRepresentativeAtomArray(s)` at RunPDP.java:22 aggregates representatives from the structure. Multiple chains or models would be treated as one index sequence, creating spurious contacts and chain-junction sequence adjacency. A preflight assertion of one model, one intended protein chain, and unique residue keys is required.
- The endpoint lookup at RunPDP.java:29 correctly interprets PDP segments as inclusive, zero-based atom-array indices. But endpoint author numbers alone are not a lossless assignment: author-number gaps must not be expanded arithmetically; insertion codes must remain part of the residue key; chain and model identity must be retained; each PDP segment means the ordered representative atoms between its indices, not every integer residue number between its displayed endpoints. Freeze and emit an explicit atom-index → (model, author chain, author sequence number, insertion code) map or complete per-residue domain assignments.
- The supplied source bundle omits `LocalProteinDomainParser` and its other helpers, so the top-level initialization, short-domain postprocessing, and exact source-to-jar correspondence cannot be independently checked. Include the exact 7.1.4 entry-point/helper sources or decompiled classes in the audit bundle.

**NON-BLOCKING**

- The g2 extraction selects model 1 and the registered chain, preserves author residue IDs, and removes ligands/waters at g2_align.py:20. This is suitable if its result is validated before PDP.
- The input is a representative-atom array, but PDP contacts are not strictly "Cα contacts." It retrieves real Cβ atoms and creates virtual Cβ atoms for recognized amino acids lacking Cβ at GetDistanceMatrix.java:159; Cα/representative atoms are only fallback cases.
- `ReducedChemCompProvider` does not move coordinates, but it can affect group classification, representative-atom inclusion, and whether virtual Cβ construction is available. "Residue lookup only" is too strong.
- Both g2 extraction and mkdssp reuse existing output files without input/hash validation. This is a provenance risk; cached files should be verified rather than assumed current.

## 3. Provenance

**BLOCKING**

- The method description is materially incomplete. The distance matrix adds another weight of 4 for sheet/helix-like neighboring-contact patterns at GetDistanceMatrix.java:109. In addition, the `|i-j|>4` restriction applies to the main single-cut loops but not uniformly to double-cut and merge calculations. Correct the current contact description (G2R_PREREGISTRATION.md:35).
- Because the primary PDP paper was not inspected and the port contains apparent translation errors, describe the instrument as the pinned BioJava implementation derived from PDP—not as demonstrated mathematical equivalence to the published implementation.
- "Failure indicates a broken pipeline, not a CATH-vs-PDP convention difference" is overclaimed. Lower thresholds than a published aggregate do not eliminate sample shift or classification-convention explanations. Failure supports `INSTRUMENT_LIMITED` for this use, which is the defensible conclusion.

**NON-BLOCKING**

- The alpha provenance is adequately transparent: direct code evidence plus DDOMAIN as secondary literature support. It does not independently validate PDP's other formulas or thresholds.
- The jar hashes are useful and version-specific.
- The driver's custom `<20` early return should be disclosed even if no eligible chain is that short.

## 4. Anti-circularity

**BLOCKING**

- The statement that C4–C7 were specified "before any C3r partition is seen" conflicts with the disclosed observation of `5HHJ_A` PDP output at lines 15–17. Correct the claim and designate that chain as design-exposed for primary scoring, unless a documented audit establishes that only execution—not the partition—was observed.
- Historical mkdssp assignments were available during criterion design. If their biological assignment contents were inspected rather than compared automatically, those chains were also not blinded for the C4/C5/C4b thresholds. This exposure must be stated and handled prospectively.
- `fused_or_accessory=YES/SUSPECTED` affects the primary verdict denominator. Its provenance and operational definition must be frozen and shown not to encode prohibited family labels, prior boundaries, or expected failure.
- No C4–C7 implementation was supplied, so the contract cannot presently prevent forbidden columns from entering those calculations. Freeze an explicit input-column allowlist and provenance manifest.

**NON-BLOCKING**

- The reviewed PDP driver itself consumes only coordinates and residue metadata.
- The g2 script reads the structure register but uses only source file, chain, and PDB identifier for extraction.
- CATH annotations are confined to external validation and do not prescribe RT boundaries.
- Biological groups are acceptable for replicate grouping and stratified reporting if they mean frozen same-protein/deposition groups rather than forbidden retron-family labels.

## 5. CATH external validation

**BLOCKING**

- "One chain per PDB" lacks a deterministic tie rule when several chains are eligible. The deduplication order must be specified.
- Specify what happens if a quota contains fewer eligible chains.
- Define the comparison universe as exact observed residue keys carrying both a representative coordinate and a CATH domain assignment. Unresolved residues, unassigned tails/linkers, insertion codes, and author/label chain-ID translation must be handled explicitly.
- Clarify whether "no fragments" excludes multi-segment/discontinuous CATH domains. The benchmark must contain a frozen discontinuous-domain stratum or another explicit double-cut test, because that is where the most consequential BioJava defects occur.
- PDB-ID and name-substring exclusions do not establish full independence from the RT population. Either exclude CATH homology/sequence clusters overlapping the RT set or weaken "independent" to "different-PDB, keyword-excluded."
- Optimal matching should be explicitly defined as maximizing the total residue intersection over all one-to-one domain permutations.

**NON-BLOCKING**

- A–D form a reasonable coarse non-degeneracy screen: A tests exact counts, B over-splitting, C collapse to one domain, and D partition quality.
- The quota-balanced sample is appropriate for an instrument stress test, but its overall accuracy is not a prevalence-weighted estimate of CATH performance.
- D is conditional on count-correct chains and the stated 0.85 "boundary-correct" statistic has no acceptance bar. That is acceptable if reported transparently, but it favors the easier subset.

## 6. Beta assignment

**BLOCKING**

- The pydssp route is not implemented in the reviewed files. sse.py contains DSSP-KS and P-SEA, not pydssp. Route B's exact coordinate extraction, chain-break handling, residue-key mapping, and 3-state conversion must be supplied and frozen.
- Define minimum common-residue coverage and behavior when κ, recall, or precision is undefined because one assignment contains no E residues.
- C4, C5, and C4b also use H fractions and helix counts, but the instrument gate validates only E. Either add a frozen H-concordance check or explicitly limit the claim to β reliability and separately justify the unvalidated H route.
- Missing-backbone residues and chain breaks must split sequential runs. Compacting them into adjacent array entries can create false helices/strands across unresolved gaps.

**NON-BLOCKING**

- pydssp is independent enough as a software implementation check, but not as an independent physical method: it implements DSSP-like hydrogen-bond logic. That is still useful for detecting invocation, mapping, and implementation failures.
- Combining κ with E precision and recall is sensible, and the per-chain κ plus unit-level E-recall gate is conservative once coverage and undefined cases are fixed.
- DSSP-KS/P-SEA issues are non-blocking if they remain record-only. Their insertion-code loss and gap compaction should nevertheless be corrected before reporting them as independent corroboration.

## 7. C4/C5/C4b/C6/C7 and verdict

**BLOCKING**

- Define whether strands/helices are built on the complete chain and then assigned to units, or independently within each unit. Also define what happens when a secondary-structure element crosses a PDP boundary, how coordinate gaps break runs, and the denominator for `frac_E`/`frac_H`.
- The C4b dependency is ambiguous: it excludes "the thumb-like unit" but requires only a C4 call. Specify behavior when C5 is `NO_CALL` or `AMBIGUOUS` and whether all C5 qualifiers are excluded.
- The stated hairpin rule is operationally testable but is only a proxy. If "hairpin" is retained as a structural claim, require de novo bridge pairing; otherwise call it "two same-sheet, sequence-near strands."
- C6 must specify: ordered versus unordered Foldseek comparisons and which TM normalization is used; whether unaligned X-unit residues count as recurrence failures; treatment of absent/ambiguous/instrument-limited Y calls; minimum alignment/unit coverage and empty comparison sets; aggregation across directions, chain pairs, and biological groups.
- The claim that author numbering removes the need for a mapping table is incorrect. Foldseek positions index ordered coordinate residues; gaps and insertion codes still require an explicit ordered-index map.
- C7 must define the common observed-residue universe, all-pairs versus group-level aggregation, missing/ambiguous calls, minimum evaluable replicate groups, and empty cases.
- The call-rate denominator must say whether chain-level instrument-limited cases count as failures or are excluded. Excluding them creates a selective-abstention loophole.
- There is an internal tension between excluding flagged chains from PASS at line 147 and saying flagged architectures are "never excluded" at line 138. Define primary and flagged-stratum verdicts unambiguously.

**NON-BLOCKING**

- The criteria do not force three domains, permit discontinuous units, and do not define fingers or thumb as residual flanks.
- Once metric eligibility is fixed, PASS/PARTIAL/FAIL is exhaustive and falsifiable.
- Raw counts of 20 inter-unit Cα contacts are size- and boundary-adjacency-sensitive. Because the threshold is frozen rather than fitted, this is a limitation to report rather than a mathematical blocker.
- The palm/thumb/fingers rules are heuristic "-like" classifiers, not validated biological annotations; interpretation should retain that wording.

Required fixes are: **F1** choose and fully disclose/validate the exact BioJava versus corrected-PDP instrument; **F2** enforce single-chain inputs and lossless residue mapping; **F3** correct method/provenance overclaims; **F4** close design-exposure and flagged-set anti-circularity routes; **F5** fully specify and extend the CATH benchmark to discontinuous cases; **F6** supply the pydssp route and complete secondary-structure gates; **F7** close C4–C7 eligibility, mapping, ambiguity, coverage, and aggregation definitions.

**OVERALL VERDICT: PROCEED_WITH_FIXES (F1–F7 above).**
