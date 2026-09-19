# PROGRAM LAUNCHER — retron RT/ncRNA programme

**Status:** ACTIVE from 2026-09-20 · **Coordinating session:** this repository, branch `project-synthesis`
**Evidence basis:** `review-stage/INDEPENDENT_SCIENTIFIC_REVIEW_2026-09-20.md` (17 sections)
**Per-task duties:** `review-stage/TASK_PROTOCOL.md` · **Execution rules:** `programme/WORKING_RULES.md`

> This launcher says **what the programme is trying to establish and how its parts depend on each
> other**. It does not contain methods. It is short on purpose.

---

## 1 · The question

> What sequence, structural and genomic features define retron reverse transcriptases within
> bacterial RT diversity; how are those features related to their ncRNA partners through evolution;
> and to what extent does that relationship determine functional RT–ncRNA specificity?

**Claim authority remains `idea-stage/docs/research_contract.md`.** This launcher schedules work; it
does not promote claims.

## 2 · What this programme has already established, and must not re-litigate

These are settled by evidence and are inputs, not open questions. Re-opening any of them requires new
evidence named in advance.

| settled | on what |
|---|---|
| bacterial RT phylogeny **does not resolve** at this character economy | 312 trees, five preregistered routes, two independent reviews; 157 alignable characters for retrons, 1.39 taxa/character; signal real at ~660× chance and insufficient to carry a topology |
| de novo comparative ncRNA **discovery** loses to a fixed positional interval | 901 against 343 at IoU ≥ 0.5; per-type priors 969 |
| **placement** into the historical 11-clade system has no validated discriminator | shuffled queries confidently placed at 7.9% against a ≤1% limit |
| **re-inference** of the historical classification is not possible | the source alignment and extracts are not published and not on disk |
| neighbourhood is **not a retron detector** | retrons 27th of 41 families, inside a predeclared dead band |
| the three-way domain partition is **not operationally defined**, in this project's parser *and in the literature* | palm-like 0.565 against a 0.70 bar; literature fingers coincide 0/8; two 2026 papers publish incompatible partitions of the same protein |

## 3 · Stage graph

```
S00 CORRECTIONS · ASSET REGISTRATION · FREEZE          [open now]
      │
      ├── S01 RESOURCE + ANNOTATION LIMITS             [open now]
      │
      ├── S03a RELATEDNESS BACKBONE                    [the trunk]
      │        │
      │        ├── S04 RETRON RT FEATURES
      │        ├── S05 STRUCTURE (existing folds)
      │        ├── S06 GENOMIC ARCHITECTURE            [open now, architecture half]
      │        └── S07 ncRNA DISCOVERY, redesigned
      │
      ├── S03b RESOLVABILITY STUDY                     [optional branch, 1 arm]
      │        deliverable is the BOUND, not a tree
      │
      ├── S08 ncRNA INTERNAL ARCHITECTURE              [gated: prior-work audit]
      │        │
      │        └── S08b ARCHITECTURE-DEFINED PAIR EXPANSION
      │                 │
      │                 └── [lineage-count gate] ─── S09 ancestry-aware correspondence
      │
      └── S10 EMBEDDINGS / PAIRING BOUNDS              [open now, repair tasks]
               │
               └── S11 INTEGRATIVE MODEL               [must be decomposed before it opens]
                        │
                        └── S12 ORTHOGONALITY          [conditional, see §5]
```

**S03a is the trunk, not S03b.** Downstream stages take a hard dependency on the relatedness
backbone, which is cheap and robust, and **no** dependency on a resolved topology, which has been
measured not to exist.

## 4 · Dependency types

```yaml
hard:         # the orchestrator enforces; a task may not start
  - S04 requires S03a
  - S07 requires S03a
  - S08b requires S08
  - S09 requires S03a AND S08b
soft:         # benefits from, must not block
  - S05 benefits_from S03a
  - S06_functional_identity benefits_from S03a
conditional:  # opens only on a measured count, declared in advance
  - S09 opens_only_if independent_lineages_with_paired_data >= <floor declared before S08b runs>
  - S11 opens_only_if decomposed_into_per_prior_increments_with_declared_floors
  - S12 opens_only_if measured_cross_pair_functional_labels >= <floor declared by T-A23>
```

## 5 · Forbidden shortcuts

Each is here because it has already happened or has been explicitly attempted.

- No claim of biochemical **compatibility, orthogonality or interchangeability** without measured
  cross-pair labels. Unobserved pairings are **never** negatives.
- No **co-evolution** language. There is no ancestry null and none is currently obtainable.
- No **per-pair biological inference** from a likelihood difference. A counterfactual is a
  conditioning control, not a negative pair.
- No **n × n compatibility matrix**, and no laboratory candidate nomination from a sequence score.
- No **gate label used as a biological conclusion**.
- No statement that something is **absent** without a registry lookup and a positive control.
- No **retron-versus-non-retron** claim evaluated on held-out family: there is only one retron family.
- No number in prose that does not resolve to a canonical table cell.

## 6 · Claim promotion

`task → validation → stage synthesis → independent review → claim registry → promoted claim → thesis/paper`

No task promotes its own claim. Statuses are the single closed vocabulary in
`review-stage/INDEPENDENT_SCIENTIFIC_REVIEW_2026-09-20.md` §17 and the proposal's §12.

⚠️ **Nothing is promotable today.** `human_input_audit: DONE` appears nowhere in the repository
except the specification that defines it, and `BUNDLE_SPEC.md` makes it a precondition. This is an
operator decision, listed in §8.

## 7 · Autonomy tiers

| tier | covers | decided by |
|---|---|---|
| **A** fully autonomous | computation, validation, artifact generation, reporting a measured number with its unit and denominator | the task |
| **B** gated | status changes, opening a downstream stage, writing interpretation | task proposes, review disposes |
| **C** never autonomous | promoting a claim, changing a criterion, consuming a confirmatory population, waiving a control | the operator |

## 8 · Operator decisions this programme is waiting on

1. Accept withdrawal of the convergence claim.
2. Pre-commit to the verdict of the two cheap checks that decide the pairing paper.
3. How `human_input_audit` clears.
4. Whether the resource is released, and under what provenance.
5. The confirmatory-population freezing rule (Tier C; a task may not choose it).
6. **Back up the 88 MB Stage-1 workbench, which exists in no branch.**

## 9 · Completion

The programme is complete when: the resource paper is submittable with a released resource; the
pairing arm has reported its bound with absolute baselines and lineage-aware variance; the ncRNA
object exists or is closed with a bounded negative; the genomic architecture is described; and every
negative is preserved with its grade. **Orthogonality is not a completion condition.**
