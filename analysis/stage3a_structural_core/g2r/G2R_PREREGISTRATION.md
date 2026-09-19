# Stage 3A · g2r — domain-parser repair gate · PRE-REGISTRATION

**Frozen before:** any external-benchmark outcome, any β-concordance outcome, any repaired-C3 run on
the RT population, and any C4–C7 score. Checkpoint of the state it repairs: commit
`03cf6f15b18a3c81bff929ee7095a56f6a345a77` (C3 VOID retained there, unmodified).

**Question.** Can a prospectively specified, sequence-aware structural-domain criterion recover
reproducible compact structural units in the experimental RT structures without using historical
RT0–RT7 boundaries, catalytic motifs, Stage 3B, or retron-family labels?

**Not the question.** Recovering three fingers/palm/thumb domains. k is never required to be 3 and
units are never required to be contiguous. The C1/C2 falsification results (natural k mostly ≠ 3;
spectral modules non-contiguous) stand and are not revisited here.

**Disclosure.** While getting the parser to run, one RT chain (`5HHJ_A`) was used as a runtime smoke
test and its PDP output was seen before this document was written. No parameter was set by us (all
PDP constants are the library's), so nothing could be tuned on it; it is disclosed anyway.

---

## 1 · Repaired C3 (C3r) — PDP, as implemented in BioJava

**Implementation.** `org.biojava.nbio.structure.domain.LocalProteinDomainParser.suggestDomains(Atom[])`,
BioJava **7.1.4** (Maven Central; jar sha256 in `tables/biojava_classpath_sha256.txt`), called by the
thin driver `scripts/RunPDP.java`. BioJava's PDP package is a translation of the original PDP C code
(Alexandrov & Shindyalov, Bioinformatics 2003;19:429–430, PMID 12584135). We do **not** re-implement PDP.

**Input.** `StructureTools.getRepresentativeAtomArray` (Cα) of the single-chain extract produced in g2
(author numbering preserved, ligands and waters removed). Chemical-component lookup uses BioJava's
offline `ReducedChemCompProvider`; this affects residue-type lookup only, never Cα coordinates.

**Constants — library defaults, unmodified** (`PDPParameters`): `MIN_DOMAIN_LENGTH 35`, `MAXSIZE 350`,
`ENDS 12`, `ENDSEND 9`, `RG 0`, `RG1 1`, `TD 25`, `TD1 40`, `DBL 0.05`, `CUT_OFF_VALUE 0.50` (cut),
`CUT_OFF_VALUE1 0.29` (combine), `CUT_OFF_VALUE2 0.44` (double cut), `CUT_OFF_VALUE1S 0.19`,
`CUT_OFF_VALUE1M 0.21`. Contacts are graded on Cβ–Cβ distance (<9, <8, <7, <6 Å → weights 1, 2, 4, 6;
Cα substitutes where Cβ is absent), counted only for |i−j| > 4.

**Size normalisation — α verified twice.**
1. Implementation: `Cut.java` normalises each side as `min(x^(1.3/3)+RG, x^(1.1/3)+TD^(1.3/3)+RG)`,
   with x capped at `MAXSIZE`; 1.3/3 = **0.4333**.
2. Literature: DDOMAIN (Zhou, Xue & Zhou, Protein Sci 2007;16:947–955, PMC2206635), Methods: *"This
   normalization is similar to the normalization of the number of interdomain contacts used in the
   PDP … As in PDP, we let α = 0.43."*
The PDP application note itself could not be read (publisher HTTP 403; not in PMC). The decision
thresholds above therefore rest on the implementation, not on the paper text, and are reported as such.

**Representation.** A domain is a **set of segments**. Discontinuous domains (PDP's double-cut) are
kept exactly as returned. Output per chain: domain count; per domain, its segments in author residue
numbers.

**Known implementation quirk, reproduced as-is and sent to review.** `Cut.java` computes
`size1t += getFrom() − getFrom() + 1` (the first term should presumably be `getTo()`). We run the library
unchanged; if review judges this blocking, the response is recorded here, not silently patched.

## 2 · External validation of C3r — frozen before running

**Source.** CATH release files dated 2025-01-13 (`download.cathdb.info/cath/releases/latest-release`):
`cath-domain-boundaries.txt` (CathDomall, author residue numbering), `cath-domain-list-S35.txt`
(S35 representatives, with resolution), `cath-names.txt`.

**Selection rule (deterministic, no RNG).** Chain eligible if: all its domains are listed in CathDomall
with no fragments; X-ray resolution ≤ 2.5 Å; chain length 80–700 residues; 1–4 domains; its first
domain is an S35 representative; its PDB ID is **not** in the Stage-3A RT population; **none** of its
domains belongs to a CATH superfamily whose name contains "reverse transcriptase", "polymerase",
"maturase" or "retron" (benchmark-side exclusion, to keep the test independent). One chain per PDB
entry. Order eligible chains by sha256(chain ID) and take the first **30 one-domain, 30 two-domain,
25 three-domain and 15 four-domain** chains (100 total). Structures fetched from RCSB as mmCIF,
hashed, logged.

**Metrics.** (i) exact domain-number agreement with CATH; (ii) for chains with the correct number, the
domain-overlap score = residues assigned to the same domain under the optimal one-to-one matching,
divided by residues present in both assignments; a chain is "boundary-correct" at overlap ≥ 0.85
(DDOMAIN's criterion).

**Acceptance — all four required.**
* **A** overall domain-number agreement ≥ **0.60**
* **B** CATH single-domain chains parsed as one domain ≥ **0.70** (not an over-splitter)
* **C** CATH multi-domain chains parsed into ≥ 2 domains ≥ **0.60** (not degenerate toward k = 1)
* **D** median overlap among count-correct chains ≥ **0.80**

These bars sit below PDP's published >80 % and DDOMAIN's reported 77–83 % method–database agreement,
so a failure indicates a broken pipeline, not a CATH-vs-PDP convention difference. **If C3r fails any of
A–D, it is INSTRUMENT_LIMITED and is not interpreted on the RT population.**

## 3 · Secondary structure for β-dependent criteria — frozen before running

**Route A (reference):** `mkdssp 4.5.5`, run with an explicit `--mmcif-dictionary`. Identity already
established: it reproduces the 26 historical mkdssp 4.5.5 outputs **identically** (26/26 files,
100 % of residues in 8-state). The broken default path is the dictionary lookup, not the algorithm.

**Route B (independent implementation):** `pydssp 0.9.1` (`opencrispr_retrons` env), 3-state.

**Route C (record only):** our DSSP-KS, reported for completeness; not used for any call.

**Concordance criterion (E vs not-E, per chain, over residues present in both):**
* population-level β is **reliable** if median Cohen's κ(E) ≥ **0.75** AND median E-recall(B vs A) ≥
  **0.80** AND median E-precision(B vs A) ≥ **0.80**;
* a chain's C4 call is made only if that chain's κ(E) ≥ **0.70**, else that chain is
  `INSTRUMENT_LIMITED` for C4;
* a palm-like call additionally requires ≥ **0.70** of the unit's route-A strand residues to be E in
  route B, else `INSTRUMENT_LIMITED`.
If population-level β is not reliable, C4 is `UNDERPOWERED/INSTRUMENT_LIMITED` for the whole stage.

## 4 · C4–C7 — amendment frozen here, before scoring

The earlier C4–C7 entries were titles only. They are specified now, before any C3r partition is seen.
Units are C3r (PDP) domains. Secondary structure from route A: 3-state, strands = maximal E runs ≥ 2,
helices = maximal H runs ≥ 8 (for helix counting), sheets = mkdssp sheet labels.

Textbook basis (right-hand polymerase fold): the palm is a mixed α/β unit built on a central β-sheet of
~4 strands flanked by helices; the thumb is predominantly α-helical; the fingers carry a β-hairpin
together with helices. Thresholds below encode those descriptions; none was derived from RT outcomes.

* **C4 · palm-like unit.** Unit containing ≥ **4** strands belonging to a single sheet label, with
  frac_E ≥ **0.20** and frac_H ≥ **0.15**. If several units qualify, the palm-like unit is the one with
  the most strands in one sheet; a tie → `AMBIGUOUS`. None → `NO_CALL` (abstention, not absence).
* **C5 · thumb-like unit.** A unit other than the palm-like unit with frac_H ≥ **0.60**, frac_E ≤ **0.10**,
  ≥ **3** helices of ≥ 8 residues, and ≥ **20** residue pairs (Cα–Cα ≤ 8 Å) with the palm-like unit.
  Exactly one qualifying unit → call; more than one → `AMBIGUOUS`; none → `NO_CALL`. Requires a C4 call.
* **C4b · fingers-like unit** *(new in this amendment — no fingers criterion existed)*. A unit other than
  the palm-like and thumb-like units containing ≥ **2** strands forming a hairpin (two strands in one
  sheet, separated by ≤ 8 residues) and ≥ **1** helix of ≥ 8 residues, with ≥ **20** Cα–Cα ≤ 8 Å pairs to
  the palm-like unit. Exactly one → call; more → `AMBIGUOUS`; none → `NO_CALL`. Requires a C4 call.
  **Never** the residual of palm and thumb.
* **C6 · recurrence across proteins.** For every pair of chains from different biological groups with
  alignment TM ≥ 0.50 in the pinned g2 all-vs-all (foldseek 10.941cd33), map chain X's called unit
  residues through the alignment into chain Y; recurrence(X→Y) = fraction landing in Y's unit of the
  same call type. A call type is **recurrent** if its median recurrence ≥ **0.50**.
* **C7 · replicate stability.** Within biological groups with ≥ 2 depositions (same protein, same author
  numbering), Jaccard of each called unit's residue set between replicate chains; **stable** if median
  Jaccard ≥ **0.70**. Also reported: PDP domain-count agreement between replicates.

**Leave-one-biological-group-out.** No C3r–C7 parameter is fitted to RT data, so LOGO has nothing to
refit; it is reported as an influence analysis — every population summary recomputed 31 times with one
group removed, and the range reported.

**Fusions / large architectures.** Flagged set: register `fused_or_accessory ∈ {YES, SUSPECTED}` or > 600
modelled residues. Reported separately and never excluded for disagreeing with a three-region model.
A C3r unit with no residue aligned (g2 all-vs-all, TM ≥ 0.50) to any chain of another biological group is
labelled `EXTRA_DOMAIN`.

## 5 · Stage-3A verdict rule — frozen

* **INSTRUMENT_LIMITED** — C3r fails its external acceptance (A–D), or β is unreliable (then at least
  C4/C5/C4b are instrument-limited).
* **PASS** — C3r and β pass, and palm-like, thumb-like and fingers-like are each called in ≥ **70 %** of
  eligible non-flagged chains, each is recurrent (C6) and stable (C7).
* **PARTIAL** — instruments pass; at least one of the three meets its call-rate, recurrence and
  stability bars, but not all three.
* **FAIL** — instruments pass and none of the three meets its bars.

## 6 · Order of operations

1. Independent review (Codex) of this document, the parser driver and the provenance. Blocking
   implementation or mathematical issues are addressed and recorded; nothing is tuned toward an answer.
2. External CATH validation of C3r → accept or INSTRUMENT_LIMITED.
3. β concordance (routes A vs B) on the 62 chains → reliable or not.
4. Only then: C3r on the 62 RT chains; freeze the partition (hash it).
5. Only then: C4, C5, C4b, C6, C7, LOGO, fusion analysis.
6. External comparisons (literature, historical boundaries, Stage 3B, RT0–RT7) are **out of scope for
   this gate** and happen only after operator review of the frozen assignments.
