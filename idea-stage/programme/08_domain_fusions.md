# Stage 8 · Analyse and characterize RT protein domain fusions

*(special focus on retrons?)*

## 0 · The point of this task

Domain fusions have only ever been treated here as a **confound to control for** — we cut
spans to reduce fusion bias, checked that our instrument was not secretly a fusion
detector, and moved on. Nobody has asked what fusions actually exist, at what rate, in
which families, or with which partner domains. So we cannot currently say whether retron
RTs fuse more or less than other RT families, or what they fuse to. Once this lands,
fusion becomes a **described property of the corpus** rather than a nuisance parameter,
and we can test whether the fused partners are the same objects the neighbourhood
annotation sees on the outside.

## 1 · Where this stands — 🟡 a confound, never an object

Everything on record treats fusion as something to *remove*:

| | finding |
|---|---|
| `D5` | Span-clustering cuts fusion bias **2.04× → 1.22×**; a **residual remains**. ⚠️ Do not claim it is removed |
| `A6` | Gate S is **not a fusion detector** — verdicts identical span-sliced (`O2` → `O3`) |
| `G82.1` | The label concordance is **not** a fused-domain artefact |
| `X05` | Dereplication clusters **on the span, not the protein** — precisely to stop fusion driving the clustering |

⛔ **CORRECTED 2026-09-13 — "there is no table of what fuses to what" was wrong.**
A fused effector–RT extraction already exists, built alongside the V3 neighbourhood
annotation:

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/cache/neighborhood_annotation/fused_effector_rt.faa
        ⭐ 14,778 sequences, 7.1 MB
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/cache/neighborhood_annotation/fused_effector_rt_clean.faa
        14,778 sequences
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/tables/fused_effector_residual.tsv
    producing scripts:
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/scripts/p3y_extract_neighborhood_proteins.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/scripts/p3z_annotate_neighborhood.sh
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/scripts/p3zz_summarise_effectors.py

**So the starting set is 14,778 proteins, not zero.** What remains genuinely new: the
**rate per family**, the **partner domain identity**, the **N-/C-terminal split**, the
**fusion boundary** (a delimitation problem — `/home/borg/RETRON_STAGES/A_delimitation.md`),
and the comparison against non-retron RT families.

⚠️ **It is retron-only.** The extraction ran over the 78,287 retron RTs, so it cannot say
whether a fusion is retron-specific or RT-general without
`/home/borg/RETRON_STAGES/I_non_retron_reference_set.md`. Full context:
`/home/borg/RETRON_STAGES/07_neighbourhood_and_operon.md` §8.1.

## 2 · What must be delivered

- **Fusion rate per RT family**, on a declared unit — with retrons placed among the 41
  families rather than described alone. (`x1` is the cautionary precedent: retrons turned
  out **27th of 41** on a modality everyone assumed was retron-like.)
- **Partner domain identity**, from stage 7's effector annotation, so that "fused to X" and
  "adjacent to X" are distinguishable and comparable.
- **Architecture, not just presence** — N-terminal vs C-terminal fusion, and whether the
  RT domain boundaries from stage 2 stay intact across the junction.
- **The retron-specific question stated as a comparison:** do retron RTs fuse at a
  different rate, or to different partners, than other RT families?

## 3 · Prerequisites and gates

- **Stage 1** — the population and the completeness flags.
- **Stage 2** — you cannot call something a fusion without a declared domain boundary. This
  is the hard dependency: `D5`'s "fusion bias" is only definable relative to a span.
- **Stage 7** — partner identity, and the ⚠️ **InterProScan stub-database blocker** must be
  cleared first (Pfam-A holds 3–4 profiles locally).

## 4 · Traps already paid for

- ⚠️ **`A6` cuts both ways.** Gate S being blind to fusion is what makes it a clean
  catalytic instrument — and also means it **cannot** be used to find fusions. A separate
  instrument is needed.
- ⚠️ **Span-slicing changes the object.** Full-length (`O2`) and span-sliced (`O3`/`O6`) are
  different populations with different structures on different machines. A fusion claim
  must name which.
- ⚠️ **Prodigal `partial` ≠ incomplete.** A contig-edge truncation can look like a missing
  fusion partner. Flag, never filter.

## 5 · Parked ideas that belong here

**Recombination detection at the RT/effector junction** — the mechanistic question behind
the descriptive one. Shared with stage 7.

---

# 6 · Refinements from `RETRON_RT_PROJECT_IDEAS.md` §10

## The question list, and what each needs

| question | prerequisite |
|---|---|
| Which domains are fused to retron RTs? | stage 7's annotation; ⚠️ the **InterProScan stub** must be cleared |
| How often? N- or C-terminal? | stage 2's boundaries — "terminal" is undefined without them |
| Where are the fusion **boundaries**? | ⭐ **stage A** — this is a delimitation problem, the fourth instance |
| Are fusion architectures **clade-specific**? | ⛔ gated by stage D — clade-specific means "beyond what descent explains", and the current null cannot move |
| Associated with ncRNA family / accessory / taxonomy / subtype / function? | ⛔ `E6` again: `msr_msd` nested inside `clade` makes the ncRNA-family arm confounded |
| ⭐ **Have similar fusions evolved independently multiple times?** | a tree or a stable grouping (6 / H). **This is the most interesting question in the section** and appears nowhere in prior work |
| Are the same domains fused to **non-retron** RTs? | ⛔ **stage I**, the non-retron reference set |

## ⭐ The three-way split this stage should deliver

The ideas document's potential extension is the sharpest framing available:

> distinguish **retron-specific fusions** from **RT-family-specific fusions** from
> **broadly common RT fusion patterns**.

That is exactly the general/family-specific decomposition `s4_motifs` achieved for motifs
(tetrad position 2 constrained in 40/40 families; the *residue* family-specific). Reusing
that design here is a known-good pattern — and `x1`'s warning applies: **retrons may well
land mid-table**, and that is a result, not a failure.

## Convergence, and how to avoid over-claiming it

*"Analyze convergent acquisition of fusion domains"* (parking lot §21). ⚠️ Convergence
requires a tree to be convergence rather than shared inheritance — and this project's tree
is a **confirmed negative**. So the claim must either wait for stage 6's structural route,
or be stated as **co-occurrence without a directional history**. Do not let "independently
acquired" enter a draft without a tree behind it.

## What this stage needs from stage 1

`MULTI` — the 9,012 loci carrying **more than one RT** — is adjacent but distinct: a
multi-RT locus is not a fusion. Keeping them separate is a stage-1 deliverable and a
precondition for a clean fusion rate.
