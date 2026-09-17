# g4a PREDECLARATION — written before any alignment was run

Timestamp of writing: 2026-09-16, before `scripts/g4a_pipeline.py` was executed for the first time.
Nothing in this file was chosen after inspecting an alignment, a conservation profile, a
correspondence score, or any pilot output.

## 1 · Prohibited derivation inputs (hard)

The following are `DERIVATION_PROHIBITED` / `POST_HOC_COMPARATOR_ALLOWED` and are **not read by
the derivation pipeline at all**. The pipeline's only sequence input is
`RTs-collection.faa`.

- the 1,988 RVT_1 seed fragments (`Models/HMM/*.fst`)
- the 45 `RVT-All.hmm` models and every per-family `.hmm`
- the 46 seed-derived Stockholm alignments (`Models/HMM/*.sto`)
- Pfam / `cdd-pfamA`, including `RVT_1`
- all 488 prior project HMMs, prior boundary tables, prior frames
- `all167`, `anchors72`, CAND95, GOLD171
- `ALIGN_000044` and the g2 reconstruction
- every structure and every structure-derived boundary product

myRT **family labels** are used only to stratify the collection into families. A label is a
stratum name; no coordinate, profile, alignment or match state derives from myRT.

## 2 · Family selection rule — declared before selection

Families are selected to satisfy, in this order:

1. **lineage coverage** — at least one family from each of: Retron (focal), GII-like, DGR,
   CRISPR-associated, UG, Abi;
2. **adequate N** — `N_eligible >= 40` for a full three-way split;
   `12 <= N_eligible < 40` admitted as `SMALL_FAMILY` with derivation + challenge only;
3. **architecture variation** — the set must span the length range, so at least one family with
   median length < 400 aa and at least one with median > 900 aa;
4. where a lineage offers several qualifying families, take the one with the largest
   `N_eligible`, except that the UG lineage contributes **two** families chosen to be the largest
   qualifying UG family and the largest qualifying UG family with median length > 900 aa.

No family is selected or dropped because of how it aligns. Selection uses only `N_eligible`,
lineage and median length — all measured in the previous bundle and reproduced by
`scripts/measure.py` there.

### The resulting seven families, fixed here

| family | lineage | N_eligible | median aa | role in the set |
|---|---|---|---|---|
| `Retrons` | Retron | 95 | 381 | focal |
| `GII` | GII_like | 496 | 475 | historical link to the g2 arm |
| `DGRs` | DGR | 488 | 365 | major distinct lineage; shortest median |
| `CRISPR` | CRISPR | 129 | 657 | CRISPR-associated |
| `UG3` | UG | 86 | 422 | largest qualifying UG family |
| `UG5` | UG | 67 | 1000 | largest qualifying long UG family (median > 900) |
| `AbiA` | Abi | 19 | 630 | `SMALL_FAMILY` exception — the Abi lineage cannot reach N >= 40 (max is AbiA at 19) |

## 3 · Pilot sizes — declared before drawing

    N_eligible >= 90   ->  pilot_N = 90
    40 <= N < 90       ->  pilot_N = N_eligible
    N < 40             ->  pilot_N = N_eligible  (SMALL_FAMILY)

Split proportions, applied to whole clusters (§4):

    derivation  ~55%      development  ~15%      challenge  ~30%
    SMALL_FAMILY:  derivation ~60%, challenge ~40%, no development set

## 4 · Sequence roles are assigned by CLUSTER, not at random

Within each family, sequences are clustered with `cd-hit -c 0.50 -n 3`. **Whole clusters** are
assigned to derivation, development or challenge, so a challenge sequence never has a
near-relative inside derivation. Clusters are ordered by size (descending), then by
representative id, and dealt to roles to meet the target proportions. Seed `20260916` breaks ties
only.

If clustering at 0.50 yields all singletons, cluster-holdout degenerates to sequence-holdout; that
outcome is **reported**, not concealed.

## 5 · Methods — fixed before execution

- **primary aligner**: MAFFT L-INS-i (`--localpair --maxiterate 1000`), or `--auto` where the
  family exceeds 200 sequences (none does at these pilot sizes);
- **sensitivity aligner**: MUSCLE v5;
- **de novo profiles**: `hmmbuild` on the derivation-only MAFFT alignment of each family;
- **between-family correspondence**: `hhmake` + `hhsearch`, profiles built **only** from g4a
  derivation alignments;
- **transfer test**: each family's de novo profile searched against its own **challenge** sequences
  and against other families' challenge sequences with `hmmsearch`.

No profile, alignment or model from myRT, Pfam or any prior project enters any of these steps.

## 6 · Anchor evidence — NO post-hoc cut-off

The previous round's 90% occupancy bar was chosen after seeing the distribution and was correctly
rejected. **g4a declares no PASS threshold for anchor admission.**

Candidate anchors are reported **continuously and ranked**, on these predeclared quantities,
computed per alignment column:

- `gap_fraction` — fraction of derivation sequences with a gap
- `shannon_entropy` — over the 20 residues, non-gap
- `max_residue_fraction` — modal residue share among non-gap
- `col_stability` — whether the same residue set co-occurs in the MUSCLE alignment (sensitivity)
- `context_conservation` — mean entropy of the +/-3 column window

A column's **anchor evidence rank** is its rank on the composite ordering
(`gap_fraction` ascending, then `shannon_entropy` ascending). Ranks are descriptive. A later,
clearly separated development phase may choose thresholds; g4a does not.

## 7 · `[YF]xDD` is a candidate landmark, not the coordinate system

It is **not** required for admission to anything. For each family the pipeline records: whether a
hit exists, how many, which alignment column the first and last hit occupy, and whether hits
concentrate in one column. Multiplicity is reported, never silently resolved.

## 8 · Declared possible outcomes

`ONE_BROAD_SHARED_FRAME` · `CLASS_LEVEL_FRAMES_WITH_SMALLER_GLOBAL_INTERSECTION` ·
`FAMILY_SPECIFIC_FRAMES_LITTLE_TRANSFER` · `INSUFFICIENT_EVIDENCE`

None is preferred. The pipeline cannot be re-run with different families to obtain a different one.

## 9 · What g4a may not claim

No biological boundary accuracy · no complete RT architecture truth · no biological absence from
non-detection · no universal RT0–RT7 boundaries · no RT0 label on retron N-terminal sequence ·
no claim that similar normalized position implies correspondence.
