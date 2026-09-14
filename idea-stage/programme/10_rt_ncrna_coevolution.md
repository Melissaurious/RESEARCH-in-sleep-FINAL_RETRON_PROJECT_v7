# Stage 10 · RT–ncRNA co-evolution

## 0 · The point of this task

This is the question the project is named for, and it has never actually been done. What
looked like prior work was a detector's **input** table, not the RT–ncRNA pair set, and
the one co-variation result we hold is confounded: the ncRNA families are **nested inside**
the RT clades, so the association is 1.0 by construction rather than by biology. We also
do not know how many retron loci carry **no ncRNA at all** — a biased sample suggests it
could be near half, which would mean "retron locus" and "retron system" are different
populations. Once this lands we have a real paired table and a test of whether RT and
ncRNA evolve together beyond what shared ancestry explains. AF3 with its RNA databases
makes structural modelling of the complex possible here for the first time.

## 1 · ⛔ Why the existing evidence does not count

- **The pair set was never built.** `V_verify/cache/v1b_collapsed_RTxncRNA.parquet` was an
  input to a detector for **misannotated** ncRNAs. Numbers computed off it were
  arithmetically correct and completely irrelevant.
- `E6` ⛔⛔ **`msr_msd` is NESTED inside `clade`** — all 21 ncRNA families lie in exactly
  one clade, so **V = 1.0000 by construction**. **The axis count is TWO, not four.** Only
  **8 of 12** clades carry any ncRNA label.
- `E2` ⛔⛔ **`msr_msd_family` is 44.4% the literal string `nan`, scored as a category**
  (the guard tested for empty string; `nan` is truthy), and `landmark` is 48.3% `NEITHER`.
  **The largest cell of the flagship table is "neither instrument detected anything."**
- `E7` ⛔ The relatedness null on the pair that matters is **mathematically invariant**
  (sd = 0.000000).

## 2 · What must be delivered

- **The paired RT–ncRNA table** — one row per (locus, RT, ncRNA), both sequences,
  coordinates in a **declared** frame, and the multiplicity class. This is `r03`.
- **The zero-ncRNA class size**, exactly. It decides whether the population for this stage
  is "retron loci" or "retron systems".
- **The multiplicity resolution**, chosen *after* the distribution is seen: nested or
  overlapping predictions of one molecule (collapse by coordinate overlap — a merge, not a
  choice); genuinely disjoint ncRNAs (keep both, flag the locus); a **multi-RT window**
  (that is a `MULTI` locus, not a multi-ncRNA system).
- **A co-evolution test with a control that can move** — see stage D. Without it the result
  is not reportable in either direction.
- Cases where **one ncRNA spans several RTs** and **one RT carries different ncRNAs**,
  explained rather than deduplicated away (also required by stage 1).

## 3 · ⭐ The new capability

`/ibex/reference/KSL/alphafold/3.0.0/` is a genuine **AlphaFold-3** database set and
carries the three RNA references AF2 sets lack:

    nt_rna_2023_02_23_clust_seq_id_90_cov_80_rep_seq.fasta
    rfam_14_9_clust_seq_id_90_cov_80_rep_seq.fasta
    rnacentral_active_seq_id_90_cov_80_linclust.fasta

**AF3 can model protein–RNA complexes; AF2 cannot.** This is the one stage in the project
where AF3 buys something no earlier tool could.
⚠️ No `params/` directory was seen — **confirm licensed weights exist** before planning any
run. No `alphafold` module was confirmed on Ibex (the probe timed out); treat that as
unchecked, not absent.

## 4 · Prerequisites and gates

| gate | why |
|---|---|
| ⛔ **`r03` paired table** | there is no pair set today |
| ⛔ **Stage D relatedness control** | `E7` — the existing null cannot move |
| ⛔ **Frame verification by RT back-translation** | the pair table cannot be written until it passes; report attempted / verified / dropped |
| ⚠️ **Stage A delimitation** | the msr-msd **boundary** is the open problem: CMfinder localises at 12/17 (70.6%) and covers ~24% |

## 5 · Traps already paid for

- ⛔ **Ask which artefact is the corpus.** A stage directory named after a data type is
  often detector/tooling development. This exact stage has already been answered off the
  wrong file once.
- ⛔ **Coordinates are contig-based**; 1 in 6 records has `actual_window.start == 1` where
  both frames coincide and every check passes.
- ⚠️ **Identity tests are blind to degradation** — `difflib` scores two identical 400-nt
  sequences 1.0 and a single-base mismatch 0.50. Probe with **nearly** identical
  sequences, never identical ones.
- ⚠️ **All 21 retron ncRNA covariance models are Mestre's**, so CM-based ncRNA calls cannot
  corroborate a Mestre-derived clade assignment.

## 6 · Parked ideas that belong here

**msd diversification** (msd/RT divergence ratio) · **a1/a2 inverted repeats** ·
**CMcompare + R-scape on the existing 21 covariance models** · an equivalent of SPIRE's
`07_run_mlocarna_rscape.sh`, which we have never run.

---

# 7 · Refinements from `RETRON_RT_PROJECT_IDEAS.md` §12

## ⭐ The control ladder — adopt this in full

The ideas document specifies five controls, and they form a proper ladder from weakest to
strongest:

    1. random mismatches
    2. within-clade mismatches
    3. within-genus mismatches
    4. phylogenetically matched mismatches
    5. taxonomy-only baseline

⭐ **This is precisely the fix for `E7`.** The null that failed was invariant because the
c50 clusters were nested inside the clades — a single shuffle unit, chosen once. A ladder
makes the shuffle unit an **axis** instead: the depth at which the signal disappears is
itself the answer, and it satisfies the standing rule that an invariant null diagnoses the
**shuffle unit**, not the claim.

**Report the whole ladder, not the rung that works.** Each rung needs its own **sd** and
**z** (`PE0`), and rung 1 with `sd = 0` is a diagnostic, not a result.

## ⛔ One correction — do NOT use Mantel tests

The ideas document lists **Mantel tests** among the possible analyses. Prior work already
rejected this, with sources:

> `PE1`, re-specified after reading the literature index: *"My first proposal — use the
> foldseek TM matrix as a continuous relatedness covariate — **is a Mantel test**, and
> **Harmon & Glor 2010** report inflated type-I error for exactly that, naming **Lapointe &
> Garland's PP** as the alternative."*
> ⚠️ **Guillot & Rousset 2013** argues the other side; the index's rule is **cite both or
> neither**.

**Use a PP-style block-constrained permutation** — compare observed V against the
distribution under permutation within relatedness blocks, **not** a distance-matrix
correlation. Same data, defensible statistic.

Also ⛔ **`E9`: Pagel's λ is not available** — binary-only, requires a resolved tree; our
labels are multi-state and no tree is resolved. It was pre-registered and was never
executable.

## The dataset requirements, checked against reality

| requirement | status |
|---|---|
| high-confidence RT–ncRNA pairs | ⛔ **does not exist** — this is `r03` |
| deduplicated systems | stage 1's ladder |
| **reliable ncRNA boundaries** | ⛔⛔ **this is the open problem** — CMfinder localises at 12/17 (70.6%) and covers ~24%. See stage A. *Co-evolution on unreliable boundaries measures the boundary, not the biology* |
| reliable RT family / classification | ⚠️ `system_subtypes` is two tools pooled; the `Retron` label itself is unvalidated corpus-wide (one `hmmsearch`) |
| phylogenetic information | ⛔ no resolved tree exists |

⭐ **Three of five requirements are currently unmet, and one of them (boundaries) is stage
A.** That ordering is the honest reading: this stage is downstream of more than `r03`.

## The regional questions — new, and worth keeping

*Which RT regions contribute most? Which ncRNA regions contribute most?* These need stage 2
(RT0–RT7 blocks) and reliable ncRNA delimitation respectively. ⭐ A per-region co-evolution
decomposition is a genuinely novel analysis and appears nowhere in the record — but it is
the *last* thing in the chain, not the first.

*Does accessory architecture correlate with stronger or weaker RT–ncRNA coupling?* — needs
stage 7's architecture alphabet.
