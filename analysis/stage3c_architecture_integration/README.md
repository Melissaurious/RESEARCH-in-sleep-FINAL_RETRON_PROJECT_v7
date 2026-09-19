# Stage 3C — post-hoc integration of independently frozen RT architecture analyses

STATUS: VERIFIED — `run.sh` was rerun end to end from this assembled layout and reproduced every
product byte-identically, except `tables/mapper/s3c.provenance.tsv` (and therefore `OUTPUTS.tsv`,
which seals it); both are declared below.

**COMPLETE for experimental structures · no verdict issued, none merged.**

    bundle_status:     REPRODUCIBLE   (run.sh reruns and reproduces every product byte-identically,
                                       except tables/mapper/s3c.provenance.tsv, declared below)
    human_input_audit: PENDING        (required before any number here becomes a thesis claim)

Governed by `launchers/LAUNCHER_03C_architecture_integration.md`. Read
**`STAGE3C_DECISION_REPORT.md`** first; this file is the packaging record.

    n_attempted:  62 experimental RT chains, 31 biological groups
    n_succeeded:  62 joined to the frozen Stage-3A units on author residue keys
    n_dropped:     0 chains dropped — but coverage differs per comparison, and that is the point:
                     A  19/62 chains (Stage-3B Tier-A truth-bearing; NONE is a retron)
                     B  59/62 mapped, 1 ABSTAIN, 2 below the instrument's 250-aa minimum
                     C  8/62 chains carry a usable literature boundary (17 statements)
                     D  62/62 scanned; Region X definable in 33, Region Y in 19
                     E  62/62 described; terminal extensions interpretable in 20

## The counts that look bad, stated here rather than footnoted

* **Comparison A says nothing about retrons.** Every retron chain is Tier B or Tier C in Stage 3B,
  which closed with Tier B never opened. Excluding them is the default taken in `docs/BLOCKED.md`;
  admitting Tier-B truth labels descriptively is an operator decision.
* **The catalytic site is outside the called palm-like unit in 4 of 9 palm-CALL chains**, and in
  `9NL3_A` it lies in the fingers-like unit.
* **Region X is undefined in 13 of 21 retron chains** — the GII-centred mapper does not reach block
  SB2p there. That is the instrument, not biology.
* **All six Retron-Eco8 chains carry no VTG-like triplet**; VTG is also present in four non-retron
  chains. The motif is neither universal nor exclusive in this population.
* **The declared gap-based insertion rule found nothing** (max excess 19 against a 20-residue bar)
  while the instrument's own insertion runs reach 774 residues. Both numbers are reported.
* **21 literature sources could not be retrieved** (paywall/403); Comparison C is a sample of the
  literature, not a census.
* **3 of 143 states disagree** in the LtrA positive control (0.979 against the declared 0.95 bar),
  explained by an unmodelled gap at 251→302 in 5G2X_C.
* The Stage-3B bundles seal three `__pycache__/*.pyc` paths that git never tracked (BS-16 defect in
  those bundles); every scientific file of both matched.

## Layout

| path | what it is |
|---|---|
| `STAGE3C_DECISION_REPORT.md` | the findings, per comparison, with `PROPOSED:` interpretation |
| `INPUT_PROVENANCE.tsv` | 244 inputs hashed against their frozen records (K1/K2/K4) |
| `STRUCTURE_STAGE3B_CROSSWALK.tsv` | Comparison A join (chain × partition arm) |
| `STRUCTURE_STAGE2_CROSSWALK.tsv` | Comparison B join (chain × state block × arm) |
| `LITERATURE_BOUNDARY_AUDIT.tsv` | Comparison C provenance audit, 94 rows |
| `XY_REGION_EVIDENCE.tsv` | Comparison D literature audit, 41 statements / 30 sources |
| `XY_REGION_ANNOTATIONS.tsv` | Comparison D operational annotation, joinable by `rt_hash` |
| `TERMINI_FUSION_SUMMARY.tsv` | Comparison E |
| `CONTRADICTIONS_AND_UNCERTAINTY.tsv` | 22 recorded contradictions and limits |
| `CLAIM_EVIDENCE_MATRIX.tsv` | 22 statements → evidence file, script, commit, falsifier |
| `tables/`, `figures/` | supporting tables; 5 figures (PNG + SVG, each with its data TSV) |
| `inputs/stage2_94a1a788/` | Stage-2 closed-state tables, copied from git and hash-verified |
| `run.sh`, `scripts/`, `env.lock` | entry point, producing scripts, environment |

## Reproducibility

`bash run.sh` regenerates everything from the hashed frozen inputs (about 30 s, CPU only).
Verified: a full rerun reproduces every table, figure and figure data table **byte-identically**.

Two declared exceptions, neither carrying a scientific number:
* `tables/mapper/s3c.provenance.tsv` — written by the frozen instrument; host, paths, timestamps.
  **Consequence, stated rather than hidden:** `OUTPUTS.tsv` seals that file too (BS-11 is
  exhaustive), so `OUTPUTS.tsv`'s own hash changes between runs as well. Every other one of the
  87 sealed artefacts is byte-identical across reruns.
* The literature retrieval was a **one-time audited acquisition** over the network. Its products are
  landed and read from disk; `run.sh` never re-fetches. Cached source texts stay in disposable
  scratch and are hashed in `tables/D_source_cache_hashes.tsv`.

## The six adversarial questions (BS-14)

1. **Where is a headline claim overstated?** The word to watch is *"agree"* in Comparison A. Stage 3A
   and Stage 3B describe the same fold core, and the catalytic site is inside that core by
   definition; the `size_expected_fraction` column (median 0.309) prices how much agreement is
   structural inevitability. Also *"enriched"* in Comparison D: 1.34× the length-proportional share
   is modest, varies 0.59–1.86, and is computed on whatever nucleic acid each entry contains.
2. **What alternative explanation produces these exact numbers?** For Comparison B, that the state
   blocks land in one unit simply because the RT core *is* one PDP unit in most chains — which is the
   interpretation offered, not a rival to it. For the historical product's high thumb agreement, the
   residual construction, which is confirmed on file (25/25 rows).
3. **Could this have returned a negative?** Yes, and parts did: 0/11 literature fingers regions
   coincide with a unit; the gap-based insertion rule returned nothing; Region X is undefined in most
   retron chains; 4/9 palm-CALL chains put the catalytic site elsewhere.
4. **The unit of every rate** is a column in every table, with its denominator; `MANIFEST.tsv`
   carries both per artefact.
5. **Which numbers have no producing script?** `XY_REGION_EVIDENCE.tsv`,
   `tables/C_literature_boundaries_retrieved.tsv`, the two `*_sources.tsv` and the two
   `*_audit_notes.md` come from the one-time literature retrieval; the report, the contradictions
   register and the claim–evidence matrix are authored. All are marked as such in `MANIFEST.tsv`.
6. **What was withdrawn or weakened?** Three things were changed after they were tried, each
   recorded rather than silently fixed: the YxDD control initially anchored on the *motif-A*
   aspartate and tested the wrong window (2/19 → 19/19 once corrected); the 5G2X numbering check used
   306–309 only after 305–308 failed — the error was in my check, not in any source; and the
   Comparison-E "terminal extension" measure was withdrawn for 39 chains once it emerged that a
   truncated anchor series was being read as architecture. A retrieval claim that these chains carry
   negative author numbering was **not reproduced** and was not adopted (`X05`).

## What this stage did not touch

Stage 2, Stage 3A and Stage 3B outputs, thresholds and verdicts — all 236 hash-checked frozen inputs
matched. No predicted-structure transfer, no catalogue-wide scan, no ncRNA model training. RT0 and
RT1 receive no interval anywhere, on any structure.
