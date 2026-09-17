# PROPOSED research-contract consequence — `C3` and `C9`

**NOT APPLIED.** `idea-stage/docs/research_contract.md` has not been edited. Changing claim
wording is an operator decision (launcher §9b: *"changing the project claim wording or the
scientific question"*), and the task instruction is explicit that a contract amendment must be
evaluated by the independent reviewer before it is applied.

Both claims stay `UNPROVEN`. Nothing here promotes a claim.

---

## `C3` — needs narrowing

**Current wording**

> `C3` — RT0–RT7 and related RT sequence/structural elements can be given reproducible
> operational definitions with explicit failure and uncertainty states across relevant RT
> families.

**Is it still scientifically supportable?** Partly, and the unsupportable part is load-bearing.

What the landed evidence says about each piece:

| piece of C3 | landed evidence | verdict |
|---|---|---|
| "reproducible operational definitions" | conserved-position membership reproduces across independent frames (81 vs 82) and collapses to 0 under a residue-shuffle null in 200/200 replicates | **supportable** |
| "explicit failure and uncertainty states" | the §7a call-state vocabulary and the declared perturbation ensemble | **supportable** |
| "across relevant RT families" | measurable as transferability, with failure to transfer an admissible result | **supportable as a measurement**, not as a presumption |
| "**RT0**–RT7" | g2 created no RT0 block; the defining cross-class claim is `NOT_TESTABLE_ON_SUBSTRATE`; g3 returned `OBJECT_MISMATCH`; `U01` open | **not supportable** — RT0 cannot be given an operational definition from available evidence |
| the **seven-way** reading of "RT0–RT7" | block count 5–16 across the sweep, 6 vs 7 across frames, never separates from a column-permutation null; RT5 and RT6 fall in one region | **not supportable** |

**Recommended amendment** — minimal, keeps the claim's shape, removes the two unsupportable
presumptions:

> `C3` — The conserved RT core can be given a **reproducible operational sequence coordinate
> system** with explicit failure and uncertainty states, and the historical RT0–RT7
> terminology maps onto it with **measured cardinality, including non-correspondence**. Status
> `UNPROVEN`.

**Alternative, if the operator prefers no wording change**: leave `C3` and record in the g4
bundle that the RT0 leg and the seven-way reading are `UNESTABLISHED` with their reasons. This
is defensible but weaker — it leaves the contract asserting a partition the evidence does not
support, and a later reader would have to find the bundle to learn that.

**Recommendation: amend.** The narrowed claim is the one the track can actually settle.

---

## `C9` — wording can stand; one baseline row needs a footnote

**Current wording**

> `C9` — Detection/localisation and boundary delimitation are separable measurable properties
> for ncRNAs, RT subdomains and operon boundaries.

**Current baselines-and-metrics row**

> | `C9` | localisation plus boundary error/coverage on known-boundary controls | independently
> known positive controls | finding an object and delimiting its edges are distinct
> measurements |

**The problem is in the metrics row, not the claim.** The row requires *known-boundary
controls* and *independently known positive controls*. For RT subdomains **these do not
exist** — that is exactly what `estimand_matrix.tsv` Q06–Q08 establish. So the row as written
specifies an instrument the RT-subdomain leg cannot supply.

**The claim itself survives, and is in fact strengthened.** `C9` asserts that detection/
localisation and boundary delimitation are *separable* properties. Stage 2's result is a direct
instance of that separability: localisation against the catalytic dyad is measurable (Q03),
ordering is measurable (Q02), stability is measurable (Q10) — while boundary delimitation
against truth is not available at all (Q08). **A demonstrated asymmetry between the two is
evidence for separability**, not evidence against `C9`.

**Recommended amendment** — one metrics row, no claim-wording change:

> | `C9` | localisation plus boundary **error where known-boundary controls exist**; where they
> do not, **demonstrated separability**: localisation and stability measurable while boundary
> delimitation against truth is unavailable | independently known positive controls **where
> they exist**; for RT subdomains, none exist and the leg is evidenced by separability | finding
> an object and delimiting its edges are distinct measurements — and for RT subdomains only the
> first is instrumented |

**Consequence for the launcher.** `C9` is `primary` on `rt07_g4`. Under this amendment `g4`
still settles `C9` — by demonstrating the asymmetry — rather than failing to settle it. The
ncRNA and operon legs are untouched and may still supply boundary-error evidence in their own
stages.

---

## What is NOT proposed

- No claim is promoted from `UNPROVEN`.
- No `circularity` grade is changed.
- The `Known-wrong` section is untouched, including the open ⛔ item that
  `VOID_DO_NOT_CITE.md` has not been consulted — `g3` established it does not exist on disk
  (`U10`), and that remains a contract-level item for the operator, not a Stage-2 edit.
