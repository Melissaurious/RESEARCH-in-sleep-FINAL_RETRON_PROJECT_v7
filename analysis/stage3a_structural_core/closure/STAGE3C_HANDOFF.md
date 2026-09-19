# Stage 3C handoff — post-hoc comparison of frozen Stage-3A units (one page)

**Stage 3A is CLOSED at FAIL** (`closure/STAGE3A_CLOSURE.md`). Stage 3C may *read* its frozen assignments
and compare them with external annotations. It may **not** change them.

**Frozen inputs** (verify hashes before any use):
- `g2r/results/rt_pdp_primary.residues.tsv`: the per-residue PDP unit, keyed `(chain, resnum, icode)`.
- `rt_units.units.tsv` and `rt_units.calls.tsv`: unit features, palm/thumb/fingers-like roles and call status.
- `RT_PARTITION_FREEZE_sha256.txt`.
- Commits: partition `76526444`, results `891036e5`.

## Rules carried forward

1. **3A is read-only.** Do not re-parse, re-threshold, re-classify, or run another decomposition to "recover"
   three domains. A disagreement found in 3C is a 3C finding, not a 3A revision.
2. **3C is descriptive and post hoc.** Any statistical test must be named in a 3C launcher before the external
   labels are joined to the 3A table. The external label sets are 3B sites, RT0–RT7 states and literature
   boundaries.
3. **Keep the strata.** Report primary (46), flagged (15) and design-exposed (5HHJ_A) separately. Carry
   `IMPLEMENTATION_SENSITIVE` (5 chains) and the PDP_ABSENT residues.
4. **No verdict merging.** 3A (FAIL), 3B (CLOSED at PARTIAL) and 3C each keep their own verdict. No combined
   "structural model" verdict is issued.
5. **Out of scope.** No predicted-structure transfer, and no Tier-B inference from 3B.
6. **Order of joins.** Label columns join the 3A table last, one comparison at a time, and each join is
   committed before its analysis.

## Comparison A — Stage 3B catalytic architecture

*Question:* where do the Stage-3B catalytic-site residues sit relative to the 3A units?

- **Input:** only the frozen 3B bundles, `results/cat3b_g1_population_freeze` and
  `results/cat3b_g2_contract_and_thresholds`. Use their supported-statement scope: CLOSED at PARTIAL, with the
  documented miss breakdown of 6/6 overlap, 4/6 adjacent, 1/6 replicate-supported and 1/6 neither.
- **Join:** match chains by PDB chain and residues by author `(resnum, icode)`. Report the chain overlap
  between the 3B population and the 62 3A chains first.
- **Measures:**
  - For each chain, the fraction of 3B site residues inside (i) the palm-like unit when one is called, and (ii)
    the unit holding the most same-sheet strands when palm is NO_CALL. The second case covers the 17/19 chains
    diagnosed post hoc.
  - Whether the site falls in one unit or is split across units, and whether it sits in a discontinuous unit.
- **Caveat:** the site location cannot validate the palm call. Both describe the same fold core, and 3A was
  blind to 3B by design; the comparison is a concordance description only.

## Comparison B — Stage 2 RT0–RT7 states

*Question:* do unit count, discontinuity or palm/thumb/fingers call status vary with RT0–RT7 state?

- **Input:** frozen RT0–RT7 assignments from the `results/rt07_*` bundles. Use the landed production mapper
  and catalogue application, not re-derivation.
- **Join:** map each 3A chain to a state through its sequence and the frozen mapper. Chains the mapper cannot
  place stay `UNMAPPED`; they are not imputed.
- **Measures:** a per-state table of chains, groups, units per chain, discontinuous fraction, palm, thumb and
  fingers call rates, and replicate count agreement.
- **Statistics:** per-state n will be small (31 groups in total), so the tables are descriptive. Any test is
  at the group level and prespecified.
- **Caveat:** family and lineage labels enter the analysis here for the first time. Record that transition.

## Comparison C — historical and literature fingers/palm/thumb annotations

*Question:* do conventional F/P/T boundaries coincide with, cut across, or merge the 3A units?

- **Input:**
  - Literature annotations with citations, for example HIV-1 RT (1RTD) and group-II intron/retron RT structure
    papers.
  - Historical `reference_boundaries.*`, e.g. `RETRON-DB_V3/MELISSA_DATA/crystal_structures/`. These were
    never opened in 3A. They are treated as sources to audit, not as truth: record their provenance and
    derivation before use.
- **Measures:**
  - For each annotated chain and each literature region, the best-matching PDP unit and its Jaccard overlap.
  - The number of PDP units each literature region spans, and the number of literature regions each unit
    spans.
  - Whether the literature palm corresponds to the 3A palm-like unit.
  - Whether literature fingers and thumb are split, merged, or absorbed into mixed units.
- **Expected value:** this is where the narrow 3A conclusion can be interpreted. It tests whether the
  conventional regions are real but not compact contact-density units, which is not what 3A measured.

## Deliverables for 3C

- A launcher with the three questions and any prespecified tests.
- One join commit per comparison, before analysis.
- Descriptive tables per comparison.
- A claim–evidence matrix citing both the 3A frozen files and each external source's provenance.

No 3C work has been started.
