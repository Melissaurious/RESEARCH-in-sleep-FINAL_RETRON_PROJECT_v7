# Stage 3A · g2r — AMENDMENT 1 (response to Codex review R1, F1–F7)

**Frozen before:** any CATH-benchmark PDP output, any β/H-concordance outcome on the RT chains, any C3r run on
the RT population, any C4–C7 score. It amends `G2R_PREREGISTRATION.md` (ee49f57e), which stays unedited as the
record of what was first frozen. Where the two differ, this document governs. Review text:
`review/CODEX_REVIEW_R1.md` (verdict PROCEED_WITH_FIXES).

Nothing below changes a PDP constant or a C4/C5/C4b threshold value. The changes define the instrument, the
residue mapping, eligibility, abstention and aggregation, and add gates. None of them was chosen by looking at an
RT outcome.

---

## 0 · Exposure ledger (F4)

| what was seen before this freeze | handling |
|---|---|
| PDP partition of **5HHJ_A** (runtime smoke test, pre-prereg) | **design-exposed**: excluded from the primary population; reported separately |
| Secondary structure of **all 62 RT chains**: DSSP-KS elements (g1, `STRUCTURAL_ELEMENTS.tsv`) and aggregate DSSP-KS/P-SEA vs historical-mkdssp recall/precision. The historical per-residue mkdssp strings were compared by script only. | Cannot be handled by exclusion without removing the population. **Disclosed limitation:** C4/C5/C4b thresholds were not blind to the population's SS content. They were taken from textbook fold descriptions and not fitted, and none has been changed since ee49f57e. |
| PDP + SS + C4–C7 **dry-run outputs on 12 CATH candidates that are NOT in the benchmark** (rank ≥ quota; synthetic groups), used to test the code end-to-end | Not RT and not benchmark chains; recorded here. The dry run exposed a mapping defect (below, §1.4), which was fixed. No threshold was touched. |

## 1 · C3r instrument (F1, F2, F3)

**1.1 Primary instrument: unmodified BioJava 7.1.4 PDP.** `LocalProteinDomainParser.suggestDomains(Atom[])`.
- Binary jar sha1 `bf7ef7eb…` equals the Maven Central `.sha1`.
- The sources jar (sha1 `0b9f0ffa…`, also equal to Maven Central) supplies the complete `domain/` and `domain/pdp/` source in
  `review/biojava_7.1.4_domain_src/`: entry point, CutSites, SegmentComparator, ShortSegmentRemover.
- The 9 files reviewed in R1 are byte-identical to it.

The instrument is described as **"BioJava 7.1.4's port of PDP"**. It is not claimed to be mathematically
equivalent to the published PDP program: the paper was not readable and the port contains defects.

**1.2 Known defects in the primary instrument** (reproduced, not patched in the primary):
- `Cut.java:73`: `size1t` adds `from−from+1`.
- `Cut.java:82`: `to2 = getFrom()`, which empties a flank–flank contact loop.
- `Cut.java:360`: `Math.max(MAXSIZE,size2)`.
- `Cut.java:370`: writes `max_contacts[k]` instead of `[nc]`.
- `CutDomain.java:133–134`: a middle segment is written at `dom1.nseg` instead of `dom2.nseg`.
- Inclusive segments are paired with `< to` loops.
- `ClusterDomains.java:80`: capped sizes are computed but not used.
- The driver's `< 20` representative-atom guard applies to no eligible chain.

**1.3 Sensitivity arm "BJ-p4" (frozen; can neither rescue nor veto).**
- `scripts/make_pdp_p4.py` applies exactly the four one-reading index/typo corrections: Cut 73, Cut 82, Cut 370, CutDomain 133–134. It asserts the original text before each edit.
- The ambiguous items (Cut 360, the `<to` loops, ClusterDomains 80) are left untouched.
- BJ-p4 is run on the benchmark and on the RT chains and reported next to the primary instrument.
- **Rule:** the external-validation verdict is decided by the primary instrument alone. If the primary fails, the stage is INSTRUMENT_LIMITED even when BJ-p4 passes.
- An RT chain whose BJ-p4 partition differs from the primary is flagged `IMPLEMENTATION_SENSITIVE`. It differs if the domain count differs, or if the Hungarian overlap between the two partitions is below 0.85.
- `IMPLEMENTATION_SENSITIVE` chains stay in every denominator. The number of them is reported.

**1.4 Input and residue mapping (F2).** `scripts/RunPDP.java` (rewritten):
- **Preflight:** exactly one model, exactly one chain carrying representative atoms, unique `(seqnum, icode)` keys. A violation gives `PREFLIGHT_FAIL`, no assignment, and counts as a failure.
- **Output:** a complete per-residue table: `idx, model, chain, resnum, icode, resname, domain` (0 = in no returned domain, e.g. removed by ShortSegmentRemover). Segments are expanded by atom-array index and never by author-number arithmetic.
- **Canonical index:** the canonical ordered index of a chain is *its residues carrying a CA in the extract*. This equals Foldseek's index space: qlen = CA count for 62/62 chains, asserted.
- **PDP_ABSENT residues:** residues BioJava omits from its representative-atom array are `PDP_ABSENT`. The dry run found HETATM-modified residues omitted under the ReducedChemCompProvider. These residues get label 0, belong to no unit, and are listed per chain. Their omission also means PDP sees a sequence gap there; this is disclosed.
- **Method wording corrected (F3):**
  - PDP contacts use real or virtual Cβ, with CA only as fallback. The distance matrix adds an extra +4 weight for sheet/helix-like neighbour patterns.
  - `|i−j|>4` applies to the single-cut loops but not uniformly to double-cut or merge.
  - α = 1.3/3 is the *split* normalisation exponent. The merge step uses 1.6/3 and 1.4/3.
  - `ReducedChemCompProvider` can change which residues are included and whether a virtual Cβ is built. It does not move coordinates.

**1.5 Cached inputs.** Every run recomputes from the hashed extracts: no step reuses a cached output file. RCSB mmCIF re-fetch logs were compared by hash: 100/100 of the first-fetched files are unchanged.

## 2 · External validation (F3, F5)

**2.1 Selection** (`scripts/cath_select.py`, `scripts/cath_screen.py`), CATH release files hashed in `tables/cath_release_sha256.txt`:
- **Eligibility:** as in the prereg. "F00" means *no CATH fragments*. Multi-segment (discontinuous) domains are **allowed**.
- **Tie rule:** CathDomall lines are read in lexicographic order and the first eligible chain of a PDB entry is kept.
- **Ordering and candidate pools:** each stratum is ordered by sha256(chain id), and a candidate pool of quota+40 is taken.
- **Independence screen:** a candidate is excluded if any hit against the 62 RT extracts (pinned foldseek, 3Di+AA, exhaustive) has e ≤ 1e-3 or max(qTM, tTM) ≥ 0.50.
- **Filling the quota:** the first `quota` survivors of each stratum are taken. A shortfall is reported and never filled from another stratum.
- **Result: 0/260 candidates excluded.** The strongest hit anywhere was e = 3.6e-3 with max TM 0.32. The final benchmark (`tables/cath_benchmark_final.tsv`, sha256 `3b4d8731…`) is therefore the original 100 chains: 30/30/25/15.
- **Discontinuous stratum:** **33** chains have ≥ 1 multi-segment CATH domain.
- **Wording:** the benchmark is described as *"different-PDB, keyword-excluded and structurally screened (no RT hit at e ≤ 1e-3 or TM ≥ 0.50)"*. It is not described as proven homology-independent.

**2.2 Comparison universe.**
- **U** = the ordered CA residues of the extract (keys `(seqnum, icode)`, author chain = CathDomall chain) that fall inside a CATH segment.
- A segment spans the ordered residues between its start and end keys. An unobserved endpoint resolves to the first observed residue at or after the start, or the last at or before the end, by sequence number; this is logged.
- Tails, linkers and CATH fragments lie outside U.
- PDP-unassigned and PDP_ABSENT residues stay in U and match nothing.
- **Overlap** = the maximum, over one-to-one (possibly partial) CATH↔PDP domain matchings, of the summed residue intersection ÷ |U|. It is computed by the Hungarian assignment.

**2.3 Acceptance — all six required; failing any → C3r INSTRUMENT_LIMITED.**

| gate | measure | bar |
|---|---|---|
| A | overall domain-count agreement | ≥ 0.60 |
| B | CATH single-domain chains parsed as 1 | ≥ 0.70 |
| C | CATH multi-domain chains parsed as ≥ 2 | ≥ 0.60 |
| D | median overlap among count-correct chains | ≥ 0.80 |
| **E1** | discontinuous stratum parsed as ≥ 2 | ≥ 0.60 |
| **E2** | median overlap over the whole discontinuous stratum | ≥ 0.70 |

- An empty stratum counts as a failed gate.
- Also reported: boundary-correct fraction (overlap ≥ 0.85), PDP outputs that contain a discontinuous domain, and the CATH→PDP count confusion matrix.
- The same metrics are reported for BJ-p4.
- The balanced sample is a stress test, not a prevalence-weighted estimate.
- A failure means the instrument is not validated for this use. It does **not** prove a broken pipeline; this corrects the prereg's §2 wording.

## 3 · Secondary structure (F6)

- **Input.** Both routes read the same atoms: model 1, the chain's polymer asym, altloc '.'/'A', from the original deposition.
- **Route A.** mkdssp 4.5.5 reads a text-level single-chain reduction of the deposition mmCIF; `pdbx_poly_seq_scheme` is kept because this build requires it. Classic output is mapped by `(seqnum, icode)`. Bridge partners are translated from DSSP serial numbers to the canonical index.
- **Route B.** pydssp 0.9.1 (numpy backend, env `opencrispr_retrons`) reads N/CA/C/O of the residues with a complete backbone, in canonical order.
  - The donor mask is 0 for Pro, for the first residue, and for any residue after a break. A break is C(i−1)–N(i) > 2.0 Å, or a missing previous residue or atom. This is because pydssp places the amide H from the previous C.
  - 3-state: pydssp helix = 3/4/5-turn helices and strand = any bridge, matching the mkdssp mapping {H,G,I}→H, {E,B}→E.
- **Scripts:** `scripts/ss_routes.py`, `scripts/pydssp_route.py`.
- **Route C** (DSSP-KS) remains record-only and is not used.

**Concordance** (`scripts/ss_concordance.py`), per chain, over residues carrying both a route-A and a route-B state:
- **Coverage** = common ÷ CA residues.
- **κ, recall and precision** are computed for E and for H.
- **Undefined values:**
  - κ is undefined only when both routes have none of that state. The chain is then "concordant-empty" for that state, which passes the chain gate.
  - Recall or precision is undefined when the reference or the test route has none of that state.
  - Undefined values are left out of the medians and counted.
- **Chain SS gate** (required for any C4/C5/C4b call): coverage ≥ 0.95, AND κ(E) ≥ 0.70 or concordant-empty, AND κ(H) ≥ 0.70 or concordant-empty.
- **Population gate:** for E **and H**, median κ ≥ 0.75, median recall ≥ 0.80 and median precision ≥ 0.80. H is added because C4/C5/C4b use frac_H and helix counts.
  - If either state fails, C4/C5/C4b are INSTRUMENT_LIMITED for the stage. (If the H gate alone fails, the report still states the E result.)
- **Palm route-B check:** ≥ 0.70 of the unit's route-A E residues must be E in route B. Otherwise the chain's C4 is INSTRUMENT_LIMITED.

**Element construction.**
- Elements are built on the **complete chain** from route A.
- Runs are split at breaks and at residues without a route-A state.
- A strand is an E run of ≥ 2; a counted helix is an H run of ≥ 8.
- An element that crosses a unit boundary is split into per-unit pieces. A piece counts only if it still meets the minimum length.
- The sheet of a strand piece is the majority mkdssp sheet label among its residues. No label means the piece belongs to no sheet.
- **frac_E / frac_H** = route-A E / H residues ÷ all residues of the unit.

## 4 · C4–C7 definitions (F7) — implementation `scripts/g2r_units.py` (input allowlist in its header)

**Input allowlist.**
- Read: the C3r per-residue table, the SS tables and gates, CA coordinates of the extracts, `tables/g2r_foldseek_ava.tsv`, and five register columns: pdb_id, chain, biological_group, fused_or_accessory, n_modelled_residues.
- Lineage/family columns are dropped when the register is read.
- Never read: motifs, catalytic coordinates, Stage 3B, RT0–RT7, historical boundaries.

**Units.** Units are primary-instrument PDP domains. Residues with label 0 or PDP_ABSENT are in no unit.

**C4 · palm-like.**
- Requires the chain SS gate. Candidates are units with ≥ 4 strand pieces sharing one sheet label, frac_E ≥ 0.20 and frac_H ≥ 0.15.
- The unit with the most same-sheet strand pieces is chosen. A tie gives `AMBIGUOUS`; no candidate gives `NO_CALL`.
- The chosen unit must pass the palm route-B check, else `INSTRUMENT_LIMITED`.

**C5 · thumb-like.**
- Evaluated only if C4 = CALL; otherwise `NOT_EVALUABLE`.
- Candidates are all units other than the palm with frac_H ≥ 0.60, frac_E ≤ 0.10, ≥ 3 helix pieces of ≥ 8, and ≥ 20 residue pairs with CA–CA ≤ 8 Å to the palm unit. Pairs are counted over unit × palm residues.
- Exactly one candidate gives CALL, more than one gives AMBIGUOUS, none gives NO_CALL.

**C4b · fingers-like.**
- Evaluated only if C4 = CALL.
- Candidates exclude the palm and **every unit that satisfies the C5 criteria**, whatever C5's outcome.
- A candidate needs a **β-hairpin**: two strand pieces in the unit with the same sheet label, sequence gap ≤ 8, and **directly bridge-paired** (a mkdssp bridge partner of one lies in the other). It also needs ≥ 1 helix piece of ≥ 8 and ≥ 20 CA-contact pairs with the palm.
- Exactly one candidate gives CALL, more than one gives AMBIGUOUS, none gives NO_CALL. A candidate is never taken as the residual of palm and thumb.

**Call rate.**
- Numerator: chains with CALL.
- Denominator: **all** chains of the population.
- NO_CALL, AMBIGUOUS, NOT_EVALUABLE, INSTRUMENT_LIMITED (chain-level) and PREFLIGHT_FAIL all count as *not called*, so abstaining cannot improve a rate.

**C6 · recurrence.**
- **Pairs:** ordered chain pairs (X, Y) with both chains in the population and from different biological groups, where the Foldseek row query=X, target=Y (both directions are rows) has **min(qTM, tTM) ≥ 0.50**.
- **Excluded pairs:** pairs whose qlen/tlen do not equal the CA counts (none at freeze).
- **Scoring:**
  - X must have a CALL for type T.
  - If Y lacks it, the pair is counted in `absent_in_Y` (reported) and not scored.
  - recurrence(X→Y) = |X-unit residues aligned to a residue of Y's T-unit| ÷ |X-unit|. Unaligned X residues count as failures.
- **Aggregation:** ordered-pair values are averaged within each unordered group pair; the median is taken across group pairs.
- **Outcome:** RECURRENT if the median ≥ 0.50 with ≥ 10 group pairs. Fewer than 10 group pairs gives UNDERPOWERED, which does not meet the bar.

**C7 · replicate stability.**
- **Pairs:** all chain pairs within a biological group in the population.
- **Numbering check:** the common universe is the shared `(seqnum, icode)` keys. The pair is excluded as numbering-incompatible if residue names agree at < 95 % of the shared keys (count reported).
- **Scoring:**
  - Jaccard of the T-unit residue sets, restricted to the common universe.
  - Called in one replicate only → 0.
  - Called in neither → not evaluable.
- **Aggregation:** the median over pairs within a group, then the median over groups.
- **Outcome:** STABLE if the median ≥ 0.70 with ≥ 5 evaluable groups. Otherwise UNDERPOWERED or NOT_STABLE; neither meets the bar.
- PDP domain-count agreement between replicates is also reported.

**EXTRA_DOMAIN.**
- A unit is EXTRA_DOMAIN if < 10 % of its residues are aligned to any chain of another biological group, over pairs with min-TM ≥ 0.50.
- The prereg wording was "no residue". The 10 % floor stops a single stray aligned residue from deciding the label.

## 5 · Populations and verdict (F4, F7)

- **Flagged.** Register `fused_or_accessory ∈ {YES, SUSPECTED}` or > 600 modelled residues.
  - Provenance: `scripts/g0_register.py` lines 49–50. YES means > 1 distinct UniProt accession mapped to the chain in the deposition's entity mapping. SUSPECTED means the construct length is > 1.6 × the modelled polymer length.
  - No family label, prior boundary or expected-failure input is involved.
- **Primary population** = all chains that are neither flagged nor design-exposed (5HHJ_A). **The stage verdict is computed on the primary population only.**
- **Flagged stratum:** flagged chains are never removed from the analysis. They get the identical metrics and a verdict-rule outcome of their own, reported as secondary. The prereg's "never excluded" means excluded from nothing but the primary denominator.
- **Also reported:** all non-exposed chains pooled, the design-exposed chain, and BJ-p4.

**Region bar.** A region meets its bar if its call rate is ≥ 0.70, C6 is RECURRENT and C7 is STABLE.

**Stage verdict.**
- **PASS:** all three regions meet their bars.
- **PARTIAL:** 1–2 regions meet their bars.
- **FAIL:** no region meets its bar.
- **INSTRUMENT_LIMITED:** the C3r external validation fails; or the population SS gate fails, in which case C4/C5/C4b are INSTRUMENT_LIMITED.

**LOGO.** An influence analysis: every primary summary and the verdict are recomputed with each biological group removed. The report gives ranges and the list of folds that flip a region's bar outcome.

**Interpretation.** "-like" classifiers are heuristics from textbook fold descriptions, not validated annotations. Raw CA-contact counts depend on unit size and adjacency; this is a stated limitation.

## 6 · Order of operations (unchanged in spirit)

1. Codex round-2 check of this amendment and the code, with no RT outcomes shown.
2. External CATH validation: primary and BJ-p4.
3. SS concordance on the 62 RT chains.
4. If both gates pass: C3r on the 62 RT chains (primary and BJ-p4). Hash and freeze the partition.
5. Run `g2r_units.py`.
6. External comparisons stay out of scope.
