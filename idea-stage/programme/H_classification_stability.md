# Stage H · Classification stability
**Proposed addition. From `RETRON_RT_PROJECT_IDEAS.md` §15 — not previously a stage.**

## 0 · The point of this task

Any grouping we report — clades, clusters, subtypes, families — is the output of a chain of
arbitrary choices: a dereplication threshold, an alignment method, a trimming rule, a
substitution model, a sequence region. We have never asked which groups survive those
choices being changed, so we cannot currently distinguish a real biological group from an
artefact of one clustering parameter. Once this lands we know which groups are stable,
which collapse, which split, and which sequences move placement every time the method
moves. That last set is not noise — **unstable systems are the interesting ones**, and they
are the same population stage 12 finds by a different route.

## 1 · Why this is not optional here

Prior work already shows the classification moves when the knobs move, and each case was
discovered by accident rather than by design:

| | evidence |
|---|---|
| `C2` | The tree failure is **partly self-inflicted by cd-hit-50** — resolution goes **19.1 → 28.5%** once redundancy is restored. A dereplication threshold changed the headline result |
| `E3` | **Dereplication ENRICHES truncated tips** — 30.8% full-window before cd-hit-50, **24.1%** after. The same knob changes *what the tips are* |
| `B2` | Re-cutting the concordance axis with `NA..H` takes V from **0.511 → 0.588** (`NA..H` alone **0.689**). One character-class choice moves the flagship number by 15% |
| `polythetic` | ⛔ **0 of 24 cells** beat a shuffled axis at any floor — and every real axis fell **below** chance, meaning the axes group what sequence already groups. A de novo scheme **cannot** cover this population |
| `B4` | Mestre's **count is not algorithmically reproducible** — four different values for the reference-set size appear across sources |
| `D5` | Span-clustering cuts fusion bias **2.04× → 1.22×**; a **residual remains** |

## 2 · Perturbations to run

From the ideas document, with prior findings attached where they exist:

| perturbation | what is already known |
|---|---|
| exact deduplication vs clustering | the locus→unique-RT factor varies **1.74×–7.39× by family** |
| clustering threshold (c50 / c70 / c80 / c90) | `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/derep/` already holds c50, c70, c80, c90 and their draws |
| taxonomic balancing | ⚠️ **nearest-neighbour density IS pool size** — an 8× pool gap produced a whole false finding |
| excluding fragments | `E3` — exclusion is not neutral; it shifts the truncation profile |
| alignment method | ⛔ **Route 1 is already occupancy-trimmed** (`occ50` keeps 287 of ~2,100 columns; `-strict` leaves 68–115) |
| RT region | `D3` — window vs domain agree at only **Jaccard 0.736** |
| phylogenetic model | parked: PMSF / `C10`–`C60` site-heterogeneous mixtures |
| sequence vs structure | ⛔ the structural tree has **never been built as a tree** |

## 3 · What must be delivered

- **A stability table**: one row per group, one column per perturbation, showing whether
  the group survives.
- **The movers, named.** Which sequences change placement under which perturbation. This
  is the output that feeds stage 12 and stage J.
- **A declared reporting rule**: a group is only reported as a group if it survives a
  stated set of perturbations, and the set is fixed **before** scoring.
- ⚠️ **Report ranges honestly** — never verify a range by its endpoints; enumerate every
  pair and check both arms share a denominator and a threshold.

## 4 · Prerequisites and gates

- **Stage 1** for the population; **stage H depends on whatever stage produced the grouping**
  — it is a post-hoc test applied to stages 5, 6 and 12.
- ⛔ **Stage C, a positive control.** A stability test that cannot detect instability proves
  nothing. `PE0` applies: report the null's **sd**, **z**, and an injected-perturbation
  power curve.
- ⚠️ **Rarefaction needs replicates** — one draw left a family rank uncertain by **±5
  places**. Every perturbation needs replicates, not a single run.

## 5 · The connection worth exploiting

**Unstable systems and disagreement systems may be the same set.** Stage 12 finds loci
where the three annotation tools disagree; this stage finds sequences that move placement
when the method moves. If those two sets overlap, that is a strong, cheap result: *the
things our methods cannot place are the things our tools cannot agree on* — and it points
at exactly the biology the field cannot see.
