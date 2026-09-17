# G2L held-out gate — frozen success criterion

Date: 2026-09-17. Written **before** any G2L sequence was mapped. Thresholds come from
construction/development evidence only; none is derived from G2L.

## Frozen inputs
Mapper, parser, score rule, abstention logic, ambiguity logic, anchor list (150 states), HMM
construction and decoy logic are frozen as of `control/FRESH_LINEAGE_RULE_V2.md` §6.

## Independence test population
The two qualifying components: **component 0 (n=40)** and **component 1 (n=9)**. The two singleton
components are reported **descriptively only** and take no part in the pass/fail test.

## Success requires ALL of
1. **multiple** frozen conserved states are callable in **both** non-trivial components;
2. state→residue mappings are supported under the frozen score rule;
3. the catalytic landmark maps via the actual alignment path where a dyad is present;
4. mapping does **not** collapse to one component — both components show callability of the same
   order, judged against the construction spread already measured (0.713–0.953 median callability
   across six families);
5. abstention and ambiguity are explicitly represented;
6. real sequences separate from decoys under the identical mapper;
7. **no G2L-specific tuning** is applied.

## Not required
Universal or complete mapping. No numeric threshold is invented from held-out results.

## Explicitly NOT evidence
**Monotone state order.** `hmmalign` is globally colinear by construction, so order is an
`IMPLEMENTATION_INVARIANT` and is reported descriptively only. It is not reinstated as a criterion.

## Stop
One run. No iteration or tuning after results are visible.
