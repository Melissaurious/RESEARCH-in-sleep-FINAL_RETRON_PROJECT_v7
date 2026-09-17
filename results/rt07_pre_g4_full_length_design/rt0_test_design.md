# RT0 test design

**RT0 is a test case, not a required region.** The point of full-length-first is to stop deleting
the sequence space in which such a feature could be tested — not to assume the feature exists.

## 1 · Why the region was previously unobservable

`buildRVT.sh` excises every myRT seed to the Pfam `RVT_1` hit (`cut -c $start-$stop`). Measured on
LtrA from the seed header `L.l.I1|ML|IIA1|Lactococcus_90_360_GII-II`:

    myRT RVT_1 window on LtrA      90 – 360
    Blocker 2005 RT0 zone           1 –  85     entirely outside
    g2 region 1 (the RT0-zone region) 39 – 61    entirely outside

A fragment-only design therefore cannot see the region **by construction**, and a non-detection
there would be an artefact of the substrate, not a finding.

## 2 · What full-length-first restores — measured

Mapping all 1,988 seeds back onto their full-length parents (1,835 mapped):

| quantity | measured |
|---|---|
| N-terminal sequence discarded per protein | median **97 aa**, mean 112.3, max **631** |
| proteins with ≥80 aa N-terminal of the window | **1,138 of 1,835 — 62.0%** |

80 aa is the size of the LtrA RT0 zone, so for **62% of proteins there is enough discarded
N-terminal sequence to contain an RT0-sized feature.** That space is now observable.

### The measurement that makes RT0 a real question

Median N-terminal extension, by family — the sequence space where an RT0-like feature would lie:

| family | median N-ext (aa) | max |
|---|---|---|
| UG10 | 468 | 537 |
| UG25 | 458 | 631 |
| CRISPR-G2 | 358 | 401 |
| UG1 | 205 | 280 |
| **GII-I** | **110** | 148 |
| **GII-II** | **88** | 250 |
| DGRs | 72 | 258 |
| **Retrons** | **51** | 206 |

**Group II intron RTs carry 88–110 aa N-terminal of the core; retrons carry 51 aa.** Both GII
medians comfortably exceed the 85 aa LtrA RT0 zone; the retron median does not.

This is a **measured architectural difference in the right place to matter**, and it is exactly
why the question is now askable. It is **not** evidence that retrons lack RT0. It is evidence that
the sequence space differs, measured relative to a model-defined window, on a reference panel of
95 retrons.

## 3 · The questions, and what would answer each

| question | testable now | what it needs |
|---|---|---|
| Is there a conserved N-terminal feature in GII RTs, outside `RVT_1`? | **YES** — full-length GII proteins retain 88–110 aa there | conservation analysis on the N-terminal extensions of the GII panel, with a shuffle null |
| Does that feature transfer to other RT classes? | **YES, as callability** | the frozen anchors applied to other lineages' N-terminal extensions |
| Is there sequence evidence for an orthologous feature in retrons? | **PARTIALLY** | retrons have 51 aa median — inspectable but short. Per-protein inspectability must be reported, not pooled |
| If not detected, was the sequence inspectable? | **YES** — this is the whole gain | N-terminal extension length per protein is a retained field; a protein with 10 aa there is `UNINSPECTABLE`, not negative |
| Is the region replaced or diverged rather than absent? | **NO** | needs structure, and there are **zero** local non-LTR structures |
| Is historical RT0 restricted to a narrower lineage? | **NO, not yet** | RT0's defining claim is cross-class between group II intron **and non-LTR** RTs. **No non-LTR sequence set is registered in this project and no non-LTR structure is held locally.** Without a non-LTR comparison class the defining claim stays `NOT_TESTABLE_ON_SUBSTRATE`, exactly as g2 found |

## 4 · Admissible outcomes, declared in advance

`TRANSFERABLE` · `LINEAGE_RESTRICTED` · `STRUCTURALLY_ANALOGOUS_NOT_SEQUENCE_HOMOLOGOUS` ·
`UNRESOLVED` · `NOT_DETECTABLE_ON_INSPECTABLE_SEQUENCE`

No outcome is preferred, and none licenses the word *absent* without the `V12` chain — which
remains `UNESTABLISHED`.

## 5 · Binding constraints

1. **`RT0 = region 0` is not encoded in the instrument.** The general frame emits anchors and
   intervals; the historical RT0 label is applied afterwards in the crosswalk, if at all.
2. **RT0 is not scored on the same footing as other features** (launcher §1), and
   `OUT_OF_FRAME` remains its state outside admissible classes.
3. **No RT0 occupancy number may be produced** — g3 returned `OBJECT_MISMATCH` and that stands.
4. **The blocking gap is the non-LTR comparison class.** Acquiring a non-LTR/R2-type RT reference
   set is the single highest-value acquisition for this question, and it is an operator decision
   under launcher §9a/§9b. Until then RT0 remains a *scoped* question: *is there a conserved
   N-terminal feature in these lineages*, not *is this RT0*.
5. **The N-terminal extension is measured relative to a Pfam-defined window**, so it is an
   operational quantity, not a biological boundary. `U01` — RT0's primary definitional source,
   Malik et al. 1999 — is still unheld.
