# OpenCRISPR as a methodological precedent — what was borrowed, what was not, and why

**This work is not a replication of OpenCRISPR.** No analysis here reproduces any OpenCRISPR
experiment, and no OpenCRISPR result is used as a benchmark against ours: the biological tasks,
the populations and above all the validation endpoints differ, and the numbers are not
commensurable. What was borrowed is an **architecture and a training idea**. What was not borrowed
is the **evaluation**, and that distinction is the point of this document.

This file re-states and extends the bounded comparison already landed at
`analysis/embedding_rt_ncrna/OPENCRISPR_METHOD_COMPARISON.md` (@ `4f56519`); it does not re-derive
it. Where the two disagree, the landed bundle wins and the disagreement is a finding.

---

## 0 · Evidence status of everything below

The published methods **could not be read from this environment**: Nature 303-redirects to
authentication, bioRxiv returns HTTP 429, Europe PMC 403. The comparison is therefore built on the
**released code and checkpoint**, which are locally available and were read directly.

| tier | meaning |
|---|---|
| **A** | explicitly reported by the authors (requires the paper; only weak, secondary-summary items reach this tier here) |
| **B** | reconstructable from released code / checkpoint — asserted against file contents |
| **C** | **not determinable from available material** |

> ⚠️ Tier C is **not** a claim of absence. Every item we could not verify is recorded as *not
> determinable*, never as *not done*. In particular, **no absence of homology control is inferred
> from silence.**

## 1 · The methodological idea that motivated our conditional model

One sentence: **a frozen protein language model can condition a small autoregressive RNA decoder
through cross-attention, and that decoder can be made to depend genuinely on its protein input.**

Three specific design commitments follow from it, and all three were adopted:

1. **Freeze the protein encoder and precompute its representations.** In the released model, ESM2
   is never instantiated inside the trainable module — `forward` consumes a precomputed
   `protein_embs` tensor, so no gradient path to it exists. Frozen **by construction**, not by a
   flag (tier B).
2. **Keep the trainable head small.** 705,930 trainable parameters: a linear projection
   `320 → 128`, one bidirectional self-attention encoder layer over the protein, and three decoder
   layers each combining causal RNA self-attention with cross-attention to the protein
   representation (tier B).
3. **Model one protein conditioning two linked RNA segments.** The 10-token vocabulary
   `a c g t 1 2 3 4 - _` brackets the tracrRNA with `1`/`2` and the crRNA with `3`/`4` (tier B).
   This maps structurally onto retron **msr/msd** and is the single most transferable
   representational choice.

Local verification of the conditioning pathway (this lab's own reproduction, tier B): the
checkpoint loads with all 85 tensors byte-identical; conditioned on SpCas9 it emits the verbatim
canonical direct repeat `gttttagagctatgctgttttg` and the `ggcaccgagtcggtgc` terminator hairpin
(16/16 well-formed); conditioned on *E. coli* MalE it produces **0/64** well-formed outputs. The
protein input is therefore doing real work — which is precisely the property a retron model needs.

## 2 · What was actually reused

| component | reuse | detail |
|---|---|---|
| `transformer.py` from the vendored `grna-modeling` release | **imported read-only at a pinned hash** | sha256 `c1f2112b4b91e8424b173d49da43e7ff14fc1ec0bf39ddc0e419147a2b90af3f`; supplies `EncoderLayer` and `CrossDecoderLayer` |
| architecture shape | **adopted** | Linear → 1 bidirectional encoder layer → 3 cross-attention decoder layers → LM head |
| capacity class | **adopted** | 665 k–788 k parameters per arm, deliberately the same order as the released 705,930 |
| objective | **adopted** | conditional next-token cross-entropy on the RNA, padding and sentinels masked |
| optimiser settings | **adopted** | AdamW, lr 2e-4, 4,000-step warmup, weight decay 0, accumulation 2 |
| frozen-encoder + precomputed-embedding pattern | **adopted** | ESM-C 300M cache built once in `embed_g1` |

## 3 · What was NOT reused, and why

| component | status | reason |
|---|---|---|
| `gRNAModel.py` | **not used** | its batch plumbing requires the unpublished `profluent.*` namespace |
| the released checkpoint weights | **not used** as initialisation | trained on CRISPR effectors and guide RNAs; a retron model must not inherit that prior |
| any OpenCRISPR sequence | **never added** to the retron dataset | populations are kept strictly separate |
| ESM2 8M as the protein encoder | **replaced** | ESM-C 300M, already cached and verified for this exact RT population |
| the two-segment sentinel vocabulary | **not yet used** | it requires msr/msd boundary annotations, which are not independently established in this project; our vocabulary tokenises the undifferentiated oriented ncRNA span plus the four IUPAC codes present in the corpus |
| the 88.9/11.1 train/validation arrangement | **replaced** | see §4 |
| any evaluation harness | **none existed to reuse** | the released code has no `training_step`, no dataset, no metric code (tier C for their actual evaluation) |

## 4 · Dataset, split and evaluation differences

| axis | OpenCRISPR gRNA model | this work |
|---|---|---|
| protein population | 112,212 type II effectors (**tier A-weak**, unverified against the methods text) | 29,192 unique exact RTs across 21 retron types |
| RNA population | not determinable (tier C) | 16,458 unique oriented ncRNAs, 34–395 nt |
| association definition | one protein → two sentinel-bracketed RNA segments | one RT ↔ one exact ncRNA co-observed at a genomic locus |
| split existence | train/validation existed: 3,120 vs 388 batches per epoch ≈ 88.9 / 11.1 by batch count, 40 epochs, 62,400 steps (**tier B**) | deterministic 70/15/15 by pair count over indivisible bipartite components |
| split construction rule | **not determinable** (tier C); the checkpoint *filename* carries `id90`, which is consistent with a 90 %-identity step but is corroborated nowhere inside the checkpoint — a filename is not a method | mmseqs 0.50 bidirectional-80 % RT clusters × cd-hit-est 0.80 ncRNA clusters → connected components; frozen, hashed, verified 32/32 |
| test set | **no test-loop state in the checkpoint** (tier C) | a held-out fold opened **once** |
| joint protein+RNA grouping | not determinable (tier C) | **yes, by construction** |
| negatives / mismatched candidates | **none in the released objective** (tier B) | a 6-rung declared ladder with false-candidate exclusion, plus counterfactual conditioning tiers C1–C4 |
| inference unit | not determinable (tier C) | the relatedness component; test n_eff = 14.1, not 4,638 pairs |
| endpoint | ultimately **wet-lab editing activity** | a **statistical** endpoint: held-out likelihood and retrieval |

### Why our leakage-aware connected-component split was retained

Not because the alternative is known to be weaker — we cannot know that — but because of two
structural facts measured **in our own data**:

1. **A protein-side identity control, at any threshold, does not by construction prevent RNA-side
   family information from crossing a split boundary**, and vice versa. The two are jointly
   controlled only if the grouping is joint. In retron data this is not theoretical: **one ncRNA is
   observed with 705 distinct RTs**, and 17.72 % of ncRNAs have more than one RT partner, so a
   protein-only split places near-identical RNAs on both sides.
2. **A 90 %-identity threshold, if that is what `id90` denotes, is a de-duplication threshold, not
   a family-level control.** Members of one protein family routinely sit far below 90 % identity.
   We measured the consequence directly: at RT 0.70 clustering, **89.4 %** of held-out RTs still
   had a ≥ 0.50-identity training relative; only at RT 0.50 with bidirectional coverage did that
   fall to **55.2 %**, and reaching 1.7 % required RT 0.30, which destroyed the usable sample
   (validation n_eff 1.0).

**And the endpoint decides how much the split must carry.** A wet-lab functional endpoint tolerates
training-set homology — if a designed editor cuts DNA in cells, leakage cannot explain the
phenotype. A retrieval or partner-specificity endpoint does not, because leakage inflates the
statistic directly. This is why the two designs should not be scored against one another, and why
the comparison is **not** "OpenCRISPR used a weaker split".

## 5 · Which parts of their compatibility / exchangeability analysis could later be adapted

The released artifacts contain no evaluation harness, so what follows is adapted from the *idea* of
protein–RNA exchangeability, not from their code.

| adaptable idea | retron form | prerequisite |
|---|---|---|
| condition on a **non-cognate protein** and require degradation | the MalE-style control: condition on a non-RT protein and on a shuffled RT; the model must get **worse** | none — this is a cheap, informative control and should be added whenever the model is next run |
| condition on a **different effector of the same family** | our counterfactual tiers C1–C4, ending at the same 50 %-identity RT homolog cluster | already specified in X2; tiers below 30 components report `UNDETERMINED` |
| **exchange** RNA between two proteins and compare outcomes | the RT × ncRNA score matrix and its native-minus-cross margin (`CANDIDATE_SELECTION_DESIGN.md`) | an authorised model and an experimentally tractable named set |
| validate designs **functionally** | a retron activity assay for a nominated candidate pair | a laboratory collaboration; nothing computational substitutes for it |
| the two-segment sentinel vocabulary as an interpretability handle (which segment changes when the protein changes?) | msr vs msd segments treated separately | msr/msd boundary annotations, currently absent |

## 6 · What cannot currently be reproduced, and why

**We lack experimental RT–ncRNA exchangeability labels.** OpenCRISPR's decisive evidence is
functional: a generated system either edits in cells or does not. We have no equivalent. For
retrons there is, in this project, no assayed set of RT–ncRNA combinations labelled compatible or
incompatible. Consequences, stated plainly:

- We cannot compute a true classification metric (AUROC, precision/recall) against biologically
  meaningful negatives, because **we have no negatives** — only non-observed pairings, which may
  well be compatible.
- We cannot calibrate any score into a probability of function.
- We cannot validate a generated ncRNA. No generated sequence in this work is claimed functional or
  ranked by compatibility.
- We therefore cannot inherit the tolerance for training-set homology that a functional endpoint
  earns; our endpoint is statistical, so the split must carry the full weight (§4).

This is the single most important asymmetry between the two projects, and it is why a retron
generative model would need a functional or otherwise orthogonal endpoint before its output could
be read as being about compatibility rather than about retron-type grammar.

## 7 · The evaluation our architecture would still need

If and when a retron generative model is authorised, three things must be reported **separately**,
never as one headline — because (1) and (2) will absorb most of the achievable likelihood while
only (3) bears on partner specificity:

1. **retron-type RNA grammar** — is the output the right *kind* of ncRNA? (against a
   type-conditioned, RT-agnostic baseline: our arm T)
2. **general ncRNA plausibility** — would this output appear for *any* protein? (the MalE-style
   non-cognate and shuffled-RT controls)
3. **individual RT-conditioned specificity** — does the identity of *this* RT change the output
   relative to another RT **of the same retron type**? (our counterfactual tiers, and arms G and P)

Seven prerequisites for training that architecture are recorded in the landed comparison
(`OPENCRISPR_METHOD_COMPARISON.md` §7); the binding one is **a within-type split with sufficient
component-level test support**, which today only two of 21 retron types approach, and both at
test-fold n_eff below 5.

## 8 · One-line summary for the thesis

> The conditional model in this chapter borrows OpenCRISPR's architecture — a frozen protein
> language model, a small trainable conditioning layer, and an autoregressive RNA decoder that
> cross-attends to the protein — and deliberately does not borrow its evaluation, because a
> statistical partner-specificity endpoint places far more weight on split construction and
> control design than a functional editing endpoint does. This is a methodological adaptation, not
> a replication.
