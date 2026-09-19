# NCRNA METHOD — the SPIRE/Toro path from a retron RT to a proposed ncRNA

Reconstructed from `04_extract_flanking_upstream.py`, `07_run_mlocarna_rscape.sh`, `00` and the
README, and checked by executing `07` verbatim (`WORKFLOW_RECONSTRUCTION.md` §6). Where the scripts
are silent, the answer says so; a README sentence is not treated as code.

## 1 · The sixteen questions

| # | question | answer from the scripts |
|---|---|---|
| 1 | how the region is selected | a fixed-length window ending immediately 5′ of the RT start codon (`04`: `rec.seq[rt_atg-window:rt_atg]` on +; revcomp of `[rt_end:rt_end+window]` on −). The RT is found in a hand-annotated GenBank by a CDS whose note/gene contains `RT` |
| 2 | upstream only? | **yes**. Nothing downstream, nothing inside the RT, nothing on the other flank |
| 3 | window size | `04` default **270**; `07` usage and README **300**; "600" in `04`'s docstring. Not fixed by code — chosen per run |
| 4 | strand | output is in **RT sense**. Only that strand is aligned and folded; an antisense ncRNA is seen only as its reverse complement |
| 5 | CDS overlap allowed? | **yes, implicitly** — no masking; the window can contain the 3′ end of the upstream gene. Any ncRNA part inside the RT ORF is **cut off** because the window stops at the start codon |
| 6 | intervening CDS allowed? | not handled. An ncRNA separated from the RT by a gene lies outside a 270–300 nt window unless the gene is tiny |
| 7 | homolog groups before RNA discovery | per **"lineage"** = the `02` best-hit type-HMM group (novel lineages defined by manual tree inspection). **Not scripted** for the ncRNA step: `07` takes whatever FASTA it is given |
| 8 | grouping of upstream sequences | one FASTA per lineage; `04 --filter_ids` subsets by protein ID. `07` warns > 60 sequences and advises "filtering by motif presence" — a **label/motif-assisted, manual** choice |
| 9 | what mLocARNA optimises | progressive **global** sequence–structure (Sankoff-style) multiple alignment of the *whole* windows, with RNAplfold base-pair probabilities (`--plfold-span 400`, `--min-prob 0.03`), indel −4 / opening −400, max-diff 100, consensus by alifold (`--alifold-cons`). Nothing localises the RNA inside the window |
| 10 | what R-scape tests | the **one-set test**: all column pairs of the mLocARNA alignment, E-value target 0.05 (GTp statistic, phylogeny-aware null), reported against the alifold consensus as "given structure" plus a power analysis. No `-s` two-set test and no CaCoFold |
| 11 | sequence-count requirements | README "≤ 40"; `07` warns only above 60. **No minimum** |
| 12 | identity / diversity filtering | **none** scripted. `07` only warns if the mean gap fraction > 0.60 |
| 13 | thresholds | pair E < 0.05; README "ncRNA signal threshold obs/exp > 1.1×" — never computed by the scripts (bug: `07` greps `*.surv`) |
| 14 | how the ncRNA boundary is assigned | **by no script.** The outputs are a whole-window alignment, a consensus structure and a covariation list; the "next steps" are an R2R figure, a human judgement, then `cmbuild` |
| 15 | is one consensus transferred to homologs? | implied: `cmbuild model.cm result.stk && cmcalibrate` (printed suggestion). Searching homologs with that CM is **not scripted** |
| 16 | failures / abstentions | not represented. `set -e` aborts; the summary prints "No .cov file found" or (because of the parser bug) "0 significant pairs". No per-sequence output exists |

## 2 · Dependence on prior knowledge — label-assisted, not purely de novo

| prior | used? | where |
|---|---|---|
| retron subtype labels | **yes, for grouping** | lineage = type-HMM best hit (HMMs built from Mestre 2020 references) |
| RT phylogeny | yes, for defining *novel* lineages | manual EPA-ng placement; `06` phylo score is a manual placeholder |
| pre-existing msr/msd motifs | optional, manual | `07` advice "filtering by motif presence" |
| covariance models | **no**, for discovery; CM is the proposed *output* (`cmbuild`) | — |
| experimentally known ncRNAs | **no** | — |

**The structural evidence itself is de novo:** mLocARNA and R-scape see only the sequences.
**Which sequences are put together** is label- and judgement-assisted. So the method is a
de novo *detector* applied to label-defined (and possibly hand-filtered) groups. The labels do not
leak ncRNA coordinates, but they do decide whose windows get compared.

## 3 · The CM route under comparison is itself a product of this paradigm

The internal model names in `padlocdb.cm` are CMfinder motif names
(`GOOD_clade7_500_50msdna.fasta.motif.h2_6.h2_7.h2_8`, `seed1.fasta.motif.h1_2…`): Mestre et al.
built the retron CMs by **CMfinder de novo motif discovery on clade-grouped upstream windows**,
then calibrated them. SPIRE's `07` is the same paradigm with mLocARNA + R-scape in place of CMfinder.
Consequences:

- "Independent of the CM" means independent of the *models and their thresholds*, not of the
  *paradigm*: both find conserved structure in upstream windows of RT-defined groups.
- Where a group resembles the Mestre training clades, SPIRE-style rediscovery is expected and
  adds little. The informative cases are groups the CMs did not see: orphan clusters, fused-RT
  types, types with no CM (XI, XII, VI, VII, VIII, X lack a dedicated padlocdb model).
- Every CM call in the corpus is `location_type = intergenic` (best hit per intergenic region).
  The CM route therefore cannot report an ncRNA overlapping an annotated CDS. SPIRE's window
  ignores annotation — a real complementary property — but it is also truncated at the RT start
  codon, so it cannot report an ncRNA that overlaps the RT ORF.

## 4 · What this audit adds to make the method evaluable (declared, not SPIRE's)

SPIRE assigns no boundary and no grouping rule. To benchmark the *method* rather than a person's
judgement, `BENCHMARK_DESIGN.md` fixes, before any outcome: ncRNA-blind homolog sets (RT50 protein
clusters, RT90 de-duplication, 5–40 members); SPIRE's set-level signal criterion made explicit
(plus a declared sensitivity rule, Amendment 1); a boundary rule from R-scape's own helix
table (union extent of helices with ≥ 1 covarying pair, projected onto each member); and a
CaCoFold arm on the same sets and windows. Section 8 of the design is the part a reader must
not mistake for SPIRE's own method.

## 5 · R-scape vs CaCoFold — what each contributes

| | R-scape one-set test (SPIRE) | CaCoFold (`R-scape --cacofold`) |
|---|---|---|
| question | which pairs covary above phylogenetic expectation? | what is the best structure *consistent with* the significant covariation? |
| structure source | external (alifold consensus from mLocARNA) | internal: CYK fold forcing all significant pairs, forbidding powered-but-non-covarying pairs |
| output used for a boundary | helices of the given structure that contain a covarying pair | helices of the CaCoFold structure that contain a covarying pair |
| failure mode | a wrong alifold consensus hides real covariation (pairs not in the given structure are still reported, but not structured) | with few significant pairs, CaCoFold still returns a full thermodynamic fold; the helices lacking covariation carry no evolutionary support |
| same input? | yes — B-struct uses the identical mLocARNA alignment | B-seq uses a MAFFT alignment instead, to test alignment dependence |

The comparison is methodologically valid only as **A vs B-struct** (same alignment, different
structure inference) and **B-struct vs B-seq** (same structure inference, different alignment).
A vs B-seq changes two things at once and is reported only for completeness.
The two tools do not answer the same question. CaCoFold is not assumed better; its extra
helices without covariation are a fold, not evidence.
