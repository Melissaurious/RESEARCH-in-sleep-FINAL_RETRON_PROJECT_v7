# DECISION — g4a executed: a shared RT core is recoverable de novo, but a universal frame is not supported

Date: 2026-09-16 · Track: `rt07` · Status: **executed; pending independent review**

Follows `docs/decisions/2026-09-16_stage2_full_length_first.md` and its errata, and answers the
load-bearing blocker the fourth independent review raised: that the previous design still used
myRT/Pfam seed-derived profiles to infer the coordinate system while calling those fragments
comparator-only.

Supersede this record by a new record, never by rewriting it.

Bundle: `results/rt07_g4a_frame_recovery/`.

**NO FULL-CATALOGUE APPLICATION; g5 NOT STARTED.**

---

## 1 · The leakage is closed, and it is checkable

The derivation pipeline's **sole sequence input** is `RTs-collection.faa`. It opens no `.fst`, no
`.hmm`, no `.sto`, no Pfam. Every profile it uses it builds itself, with `hmmbuild` and `hhmake`,
from its own MAFFT alignments of derivation-only sequences.

This is verifiable rather than asserted: `INPUTS.tsv` hashes the one sequence input, all five
scripts, the harness, the predeclaration and all eight tool binaries, and a grep of the scripts for
every prohibited asset name returns hits only in comments.

myRT **family labels** are used to stratify the collection into families. A label names a stratum;
no coordinate, alignment, profile or match state comes from myRT.

## 2 · Predeclared before any alignment ran

`control/PREDECLARATION.md` fixed the seven families, the split rule, the cluster-holdout
procedure, the aligners and — the point the last two reviews turned on — **the absence of any
anchor threshold**. The previous round's 90% occupancy bar was chosen after seeing the
distribution and was correctly rejected. g4a ranks candidate anchors continuously on predeclared
quantities and declares **no PASS cut-off at all**.

Families: `Retrons` (focal) · `GII` · `DGRs` · `CRISPR` · `UG3` · `UG5` · `AbiA`, chosen on
lineage coverage, N and median length — never on how they align.

## 3 · What was measured

| result | value |
|---|---|
| between-family profile correspondence | **42 of 42** ordered pairs; hhalign probability **74.2–100.0**; best E-value **4.8e-42** |
| catalytic dyad correspondence | **42 of 42** `DYAD_CORRESPONDS` at offset 0; exactly one dyad per consensus |
| transitive order consistency | **210** triples; mean **88.2%** within ±2; **174/210 (83%)** at ≥80%; median offset 0 |
| globally supported positions | **68–160** per family; **18.9%** (UG5) – **57.3%** (CRISPR) of covered positions |
| global-or-class | **69.1%** (UG3) – **99.6%** (CRISPR) |
| global core extent | **94–201** consensus positions; **64.2–87.3%** of each span global |
| transfer, as a score | SELF median bit score **424.1** vs CROSS **32.6** — **13.0×** |
| reproducibility | byte-identical from registered inputs |

**Sequence-level holdout is genuine.** Whole cd-hit clusters at 0.50 were dealt to roles, so no
challenge sequence has a ≥50% identity relative inside derivation — and because every profile is
built here, there is no external profile that could leak, which was the reviewer's specific
objection.

## 4 · The verdict on the science

**`g4a PARTIAL` — class/family frames are supported, a universal frame is not.**

A shared core is real: every family pair corresponds, the catalytic dyad corresponds in all 42
ordered pairs, and the pairwise correspondences are transitively coherent in 83% of triples. But
that shared core is a **minority of each family's sequence** — as little as 18.9% of UG5's covered
positions and 19.0% of GII's. Most conserved structure is class-level or family-level, not global.

This is the hierarchical outcome the fourth reviewer argued the evidence would support, and it
emerged from the data: no target number of regions was set, and none is reported.

## 5 · Four errors made during execution, all corrected and recorded

`control/ERRATA.md`. Two produced plausible **negative** results that would have been serious
false findings:

1. **`hhsearch -d` failed silently** — `-d` needs an ffindex database, and the return code was not
   checked. It landed an **empty correspondence table** that reads as *no between-family
   correspondence*. Fixed with `hhalign`, the correct pairwise tool.
2. **A reimplementation of `hhmake`'s match-state numbering** gave **0 of 42** dyad
   correspondences — i.e. *the catalytic dyad does not correspond across RT families*, which is
   biologically implausible. The raw alignment showed `YADD` aligned to `YADD`. Fixed by reading
   the alignment text and reimplementing nothing.
3. The transitivity table inherited that broken map and was **all zeros**.
4. **MAFFT `--thread 4` is non-deterministic** — caught only because the harness was repaired.
   Conclusions were stable across runs (dyad 42/42 both times, `pct_global` moved ≤2.3 points) but
   tables were not byte-reproducible until MAFFT was pinned to `--thread 1`.

Rule adopted: **do not reimplement a tool's internal coordinate system to interrogate its output.
Read the output.**

## 6 · The harness is repaired

The previous bundle's `run.sh` piped `measure.py | tee tables/…`, overwriting the expected output
with the reproduction, so it could never detect drift. `verify.sh` now runs from registered
inputs into a temporary directory, diffs against the landed tables, exits non-zero on any
difference, and never writes into `tables/`. It found error 4 on its first use.

## 7 · What g4a did not establish

**No family was held out** — all seven contribute a profile, so family-level generalisation is
untested by design. **The detection-rate transfer test cannot fail** at `--max -E 10` and is
flagged `NON_DISCRIMINATING` in its own table; the bit-score distribution is the informative
quantity. **The intersection depends on the seven families chosen**, and a different admissible
set was not tried. Biological absence, exact boundaries, family-assignment accuracy and
phylogenetic eligibility all remain **UNESTABLISHED**, unchanged across five reviews.

No external asset was acquired and none was needed: nothing is classified `REQUIRED_FOR_G4A`.

## 8 · Reviewer verdict

Routed through ARIS's governed reviewer mechanism. Verdict recorded in
`review-stage/AUTO_REVIEW.md` and appended at §8a. **No success criterion in this record may be
weakened to obtain a pass** (`WA-A.5`). The launcher and research contract are **not** amended;
`§22` of the task reserves that until review approves the new scope.
