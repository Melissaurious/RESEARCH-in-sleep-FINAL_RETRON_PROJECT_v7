# Alignment / mapping strategy comparison

No algorithm is precommitted. Four strategies are assessed against the measured properties of the
full-length substrate, and the recommendation is a staged combination, not a single method.

## What the substrate actually looks like

These measurements constrain every strategy below.

| property | measured |
|---|---|
| eligible full-length proteins | **2,166** of 2,339 records, after excluding `NotUsed` (136), `UNC` (1), 10 non-standard-residue sequences and sub-250 aa fragments |
| redundancy | **essentially none** — greedy clustering at 4-mer Jaccard 0.90 yields 2,165 representatives from 2,166; median within-family pairwise 4-mer Jaccard 0.007–0.177 |
| length range | **50–1,879 aa**, median 461; per family, medians range from UG11 257 aa to UG10 1,821 aa |
| N-terminal sequence discarded by RVT_1 excision | median **97 aa**, mean 112.3, max **631**; 62.0% of proteins carry ≥80 aa there |
| primary anchor occupancy | `[YF]xDD` in **94.9%** (2,090/2,202), but **7 families below 90%**, lowest UG13 at **52.0%** |
| anchor multiplicity | **251 proteins (11.4%)** carry more than one `[YF]xDD` |

Two of these are decisive for method choice. **Redundancy reduction is not needed** — the
collection is already dereplicated, so a strategy whose main virtue is clustering buys nothing.
And the **7.3× length spread** (median 257 to 1,821 aa across families) means any global
alignment will be dominated by gap placement rather than by homology.

---

## Strategy A — profile-anchored full-length mapping

Locate homologous core coordinates inside each full-length protein using existing RT profiles,
then align only the homologous core while retaining flanking and intervening sequence as
architecture.

**For.** It is the only strategy that directly matches the operator's required decomposition —
identify anchors, establish order, align core, retain the rest. It is robust to the length spread
because it never asks a global aligner to reconcile a 257 aa protein with an 1,821 aa one. The
Pfam `RVT_1` profile is available locally in `cdd-pfamA` and is **external to every project
artefact**, which is the strongest independence any scaffold candidate has.

**Against.** The scaffold inherits Pfam `RVT_1`'s scope. Anything the profile does not cover is
outside the coordinate system by construction — which is precisely the defect that motivated this
whole task. **Mitigation, and it is the crux of the design:** the scaffold defines where
*coordinates* exist; it does not define where *sequence is retained*. Full-length sequence is kept
and measured relative to the anchors (`T4`, `T5`), so the N-terminal region remains observable
even though it is not initially coordinatised.

**Verdict: PRIMARY.**

## Strategy B — representative full-length alignment

Reduce redundancy, align family representatives with a standard protein MSA method, assess
whether cross-family anchors are stable.

**For.** Model-free; it can discover correspondence the profiles miss, including in the
N-terminal region no profile covers.

**Against.** Its premise is already refuted: **there is no redundancy to reduce**. And at this
length spread and divergence — median within-family 4-mer Jaccard below 0.02 for most families —
a progressive aligner will emit columns that are gap-placement artefacts. `F09` exists precisely
for this: *a column is non-homologous unless stable across alignment methods.*

**Verdict: SECONDARY, as the source of the `V04` alignment-stability ensemble rather than as a
frame builder.** It is more useful as a way to falsify columns than to create them.

## Strategy C — profile-profile and structure-assisted correspondence

Use profile-profile comparison, or structure, as an independent correspondence test.

**For.** Profile-profile is the natural way to test whether two family-specific cores correspond —
the actual hard problem, since myRT ships **46 per-family Stockholm alignments carrying `#=GC RF`
match-state lines**, which are ready-made per-family profiles.

**Against, and it is a hard constraint.** Structure may not define sequence correspondence and
then be presented as independent validation of it. Coverage also forbids leaning on it: **21 of 38
families have no experimental structure**, prior sequence-to-structure cross-validation covers
only **11 of 25** structures with **thumb Jaccard 0.0 for five**, and LtrA/5G2X is excluded as the
historical coordinate carrier.

**Verdict: profile-profile is a STRONG SECONDARY for cross-family anchor correspondence.
Structure is POST-FREEZE ONLY.**

## Strategy D — frozen protein-LM embeddings

Residue-level representations from a frozen protein language model as a correspondence challenger.

**For.** Genuinely independent of Pfam and myRT, which no other strategy here is. It could reach
the divergent families where `F01` says the dyad anchor fails — UG13 at 52% is exactly the case
that profile methods are least likely to rescue.

**Against.** A pretrained model's training corpus is unknown and may contain these very proteins,
so "independent" needs qualifying, not asserting. Sophistication is not identifiability: an
embedding will always emit a nearest neighbour, and a confident wrong correspondence is worse than
a declared failure.

**Verdict: CHALLENGER, run only if a pinned local model already exists and a bounded pilot is
affordable. Inability to run it is recorded, not fatal.**

---

## Recommended staged design

1. **Anchor location** — A_DYAD by direct motif search (masked from any derivation), plus
   `RVT_1` match states, plus the Poch et al. 1989 motifs once their occupancy is measured. `F02`
   requires **at least two anchors in ≥90% of panel proteins**; a single-anchor frame is refused.
2. **Order and correspondence** — establish ordered anchor correspondence per family, then test
   cross-family correspondence by profile-profile (Strategy C) against the 46 `.sto` profiles.
3. **Core alignment** — align only between corresponding anchors; mask columns failing `F09`.
4. **Architecture retention** — inter-anchor spacing (`T4`) and terminal extensions (`T5`) measured
   on full-length coordinates, with every transform reversible.
5. **Challenge** — Strategy D and the structural arm, both post-freeze.

## Bounded pilot, if one is run

Declared before execution: **N = 120, family-balanced at ~3 per label across the 38 eligible
labels**, drawn with seed `20260916` and permanently excluded from any later evaluation draw. Its
only question is whether cross-family anchor correspondence is technically obtainable at all. It
sets no threshold, tunes nothing, and is not validation. **No Stage-1 catalogue access.**

## The unresolved method question

Nothing here settles whether **UG is one lineage or 29** (`UG_OPTION_A`/`B`/`C`). That choice
changes the panel, and `V09`/`F08` are the mechanism that makes it auditable rather than hidden —
the frame is rebuilt under both allocations and the movement is measured. The question itself is
returned to the operator.
