# NOTE 2026-09-16 — response to the content-list review

Verdict on each reviewer point, with what was verified and what changed.

## Reviewer was RIGHT — corrected

| # | point | verified finding | action |
|---|---|---|---|
| 8 | "18 RNAs" is the mode, not all downstream | **All** canonical downstream = 6,761 placements / **230** exact ncRNAs. **The mode** (g3's own definition: ±150 bp of the 2,682 bp median) = **5,234 placements / 18 ncRNAs / 126 RTs / 15 species**, dominant stratum 99.96 % contig-start-clipped | D2 now reports four strata explicitly; Results R.9 and CONTEXT.md rewritten |
| 8 | separate the technical cluster from all downstream | **New finding**: the 1,041 downstream placements that are *not* clipped sit at a median **64 bp** over 149 ncRNAs — a near-range population the artefact was masking | surfaced in D2 and R.9 as its own population |
| 2 | redundancy multiplier is accession-loci, not physical | true; **but numerically identical within every database** (5.52 vs 5.52 etc.) because the `NZ_` twin collapse acts only *across* NCBI↔GTDB | A2 now computes both and states why they coincide |
| 3 | A4 mixes populations | true: panels 1–2 are `POP_RT`, panel 3 (database span, **45.23 %**) is the full-corpus exact-RT table | every panel now labelled on the figure and in text |
| 1 | geometry eligibility should not exclude proteins from sequence-only analyses | correct in principle and material in size: **16,008 exact RTs** are usable sequences with no defensible context | population split into `POP_RT_SEQ` (493,964 exact RTs) and `POP_RT_CTX` (477,956) |
| 14 | "single transcriptional unit" overreaches | correct | replaced with arrangement wording in D3, D6 and R.7; fusion / sampling / CM-cross-matching now explicitly marked as hypotheses |
| 7 | need a joint direction × strand × distance × CDS summary and a redundancy-weighted comparison | built as **D6** | see below — it changed a conclusion |
| 11 | pairing topology unimplemented | built as **F** (F0–F3) | |
| 13 | dataset inventory | built as **K** (K1 populated, K2 provisional) | |

## Reviewer was WRONG on one point

**#6 — "reconcile C2's representative-model summaries with C3's call-derived model assignments."**
There is nothing to reconcile: **`n_models > 1` for 0 of 16,458 exact ncRNA sequences**, and the
per-model counts sum to exactly 16,458. Every exact ncRNA is hit by exactly one covariance model, so
the two labellings are interchangeable. This is now asserted in the notebook rather than assumed.

**My own error, found while checking this:** `CONTEXT.md` previously claimed the opposite ("a
sequence called by more than one model appears under each — the columns therefore do not sum to
16,458"). That was wrong and is corrected.

**Outgroup models**: `OutgroupA` (10,910 calls / 3,319 sequences) and `OutgroupB` (2,018 / 338) are
part of the shipped CM library. Their intended role is **not determinable from the corpus** and must
be read from the myRT/PADLOC model documentation — recorded as a caveat, not guessed.

## Reviewer's concern valid, but the data already satisfies it

**#5 — zero/positive locus categories mutually exclusive.** The query as written did not guarantee
it. Verified: **0 of 2,847,312 loci** have mixed records (some reporting an ncRNA, some not). The
split is a true partition. Now asserted in C1 rather than left implicit.

## Found while implementing — not in the review

**The exact-pair view is built on ELIGIBLE placements, not CANONICAL.**
`rt_ncrna_exact_pairs_v1` = 30,924 pairs (eligible, 345,313 placements). Only **30,427** pairs are
derivable from canonical placements; **497 pairs are represented solely by placements removed during
de-duplication**. Section F (topology) uses the registered 30,924 so it matches g3; section D6
(geometry composition) must use the canonical-derived 30,427, because a geometry is only
attributable through a surviving placement. Documented in F0 and in the dataset inventory.

**D6 changed a conclusion.** The redundancy-weighting check does *not* show weighting-invariant
marginals, which is what I would have written before running it:

| combination | % of placements | % of exact pairs | |
|---|---|---|---|
| upstream · same · no CDS · **≤ 200 bp** | 55.22 % | **73.86 %** | strengthens |
| upstream · same · no CDS · **1–5 kb** | 32.83 % | **2.95 %** | collapses |

Physical-locus weighting barely moves anything (upstream 94.51 % → 94.91 %), but exact-pair
weighting drops `upstream` overall from 94.51 % to **88.10 %**, and the 1–5 kb band is revealed as
carried by a few pairs observed very many times. The defensible claim is narrower and better:
**close (≤ 200 bp) 5′ same-strand adjacency is dominant under every weighting and is the only band
that strengthens when redundancy is removed.**

## Still outstanding

- **Sections E, G, H** unimplemented (tool agreement / MULTI / taxonomy). E must be re-specified at
  **unique-protein** level, not record level, as the review notes.
- **K2 — the confident-association rule is unset.** Distance cut, overlapping in/out, CM hit
  quality, 1:1 requirement, recurrence requirement. Applied individually each criterion retains
  31–98 % of pairs; the intersection is deliberately not computed, because inventing a threshold
  here would make it the project's definition.
- **CM `score` / `evalue` are used nowhere** in this characterization. Either bring them in or state
  that detection confidence was not filtered.
- **Figures 4, 8, 15, 17** of the Results draft do not yet exist.
