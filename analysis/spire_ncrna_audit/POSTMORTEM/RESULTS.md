# SPIRE post-mortem — RESULTS · label **`RETRON_ENRICHED_NCRNA_SUBMOTIF`** · SPIRE discovery branch CLOSED

Bounded and descriptive (`DESIGN.md`, frozen before any run; `tables/FREEZE.tsv`). `ROUND2_FAIL_STOP` stands. The frozen
Round-2 rule and runner were reused unchanged. No discovery was reopened, no CM was seeded or built, nothing was scaled.
Conservation is not read as function.

## 1 · What the motif is, in retrons (`tables/MOTIF_INSTANCES.tsv`, `MOTIF_CHARACTERISATION_BY_CLASS.tsv`)

1,793 motif instances from 140 passing retron groups (DEV + HELDOUT):

| property | value |
|---|---|
| centre (RT-relative) | median **−116 nt**, IQR 77 nt; set-level centre SD median 18 nt (consistent across homologs) |
| length | median 88 nt (reference ncRNAs: median 133–253 nt by type) |
| strand | RT strand (by construction of the RT-oriented window) |
| overlaps the locus's own registered ncRNA | **97.9 %** |
| overlaps any registered ncRNA call (all are production-CM calls) | 97.9 % |
| overlaps a non-RT CDS | 3.3 % of nucleotides |
| overlaps the RT ORF (≥ 1 nt) | 10.8 % · overlaps the RBS region −20…−1: 22.8 % |
| consensus base pairs (median) | 25 · covariation `SUPPORTED` in 40 % of instances |

Distance to the RT end is uninformative (window stops at +100). In retrons, **the conserved motif is a sub-element of the known ncRNA**;
it overlaps the ncRNA but does not delimit it.

## 2 · Type III-A (`tables/IIIA_INSTANCES.tsv`, `IIIA_GROUPS.tsv`)

| class | instances | groups (modal) |
|---|---|---|
| the reference ncRNA itself (overlap) | **385** | 32 |
| leader / UTR / RBS region | 3 | 1 |
| unresolved conserved element | 4 | 1 |
| other annotated ncRNA · repeat element · neighbouring CDS | 0 | 0 |

**Correction to the Round-2 reading.** III-A was not "a different element": the motif sits *inside* the III-A ncRNA in 32/34 groups.
III-A references are long (held-out median 253 nt) and mostly run across the RT start (`overlaps_RT_start`, ~−245…+21), so a ~90-nt motif
cannot reach IoU ≥ 0.5 — a boundary failure, not a localisation failure (held-out any-overlap 58.7 %, IoU ≥ 0.5 0.4 %). The two exceptions are
the groups whose registered ncRNA lies inside the RT gene (+1,100…+1,470); there the motif sits at −44 / +21 and stays
`LEADER_UTR_OR_RBS_REGION` / `UNRESOLVED_CONSERVED_ELEMENT` — not called an ncRNA.

## 3 · Specificity panel (`tables/PANEL_GROUPS.tsv`, `SPECIFICITY_BY_CLASS.tsv`, `figures/pmfig1_motif_centre_by_class.png`)

10 non-retron RT classes × 8 independent homolog groups (AbiA: 0 groups — 46 loci, too few). Same member rules as the retron sets (one
locus per RT90, 6–20 members, ≥ 1,900 bp upstream, W500 + paired distal control). Frozen rule, rule pass (no half-splits).

| class | real pass | distal pass | where the motif sits (median centre) |
|---|---|---|---|
| **Retron** | **140/164 (85 %)** | 2/164 | **−116, inside the known ncRNA** |
| UG5 | 8/8 | 2/8 | +31 — RT start / RBS |
| DGRs | 6/8 | 1/8 | −221, spread |
| CRISPR-like | 5/8 | 0/8 | −23, spread |
| UG2 | 5/8 | 0/8 | −172; covariation-supported in 61 % |
| UG3 | 5/8 | 1/8 | +37 — RT start |
| AbiK | 4/8 | 0/8 | +10 — RT start / RBS |
| GII | 4/8 | 0/8 | −142; covariation-supported in 100 % (intron-RNA-like) |
| UG8 | 3/8 | 0/8 | +17 — RT start / RBS |
| AbiP2 | 1/8 | 0/8 | +36 |
| CRISPR | 1/8 | 0/8 | +35 |
| **all panel** | **42/80 (52.5 %)** | 4/80 | — |

Retron vs pooled panel: **Fisher p = 1.0e-7, odds ratio 5.3** → retron-enriched. But what passes elsewhere is mostly a *different* element:
in AbiK, AbiP2, CRISPR, UG3, UG5 and UG8 it straddles the RT start codon and RBS. This exposes a design leak in the Round-2 rule: the coding
filter exempted the first 50 nt of the RT ORF (to allow msd–start overlap), which is exactly where the non-retron motifs sit. GII passes with
fully covariation-supported upstream structure, consistent with group II intron RNA. None of these panel motifs overlaps a registered
ncRNA call (the registered calls are retron CMs; this measures detector scope, not absence). Panel GC ranges 0.29–0.57 (reported, not matched).

## 4 · How much of the useful signal is positional (`tables/POSITIONAL_BY_TYPE.tsv`, `POSITIONAL_PRIORS_DEV_BY_TYPE.tsv`)

Held-out, 1,051 in-window members; priors derived on DEV only:

| predictor | IoU ≥ 0.5 |
|---|---|
| frozen CMfinder rule | 343 (32.6 %) |
| global fixed interval −193…−24 | 901 (85.7 %) |
| **per-type DEV median interval** | **969 (92.2 %)** |

Reference positions are tight: start SD 57 nt (IQR 89), end SD 42 nt (IQR 39); per type as low as 4 nt (IX) to ~60 nt (I-B).
Of the method's 343 IoU ≥ 0.5 hits, 234 lie within P0 ± 20 nt anyway. `PROPOSED:` for the future ncRNA-boundary project, RT-relative
position conditioned on retron type is a very strong prior (≈ 92 % IoU ≥ 0.5 before any sequence model), and the conserved sub-motif found here
is a candidate *anchor* inside the ncRNA, not a boundary predictor. That is an input to the boundary project, not a new SPIRE question.

## 5 · Erratum found during the post-mortem (`tables/ERRATUM_NAN_OVERLAP.tsv`, `scripts/pm04_erratum_nan_overlap.py`)

`np.fmin/np.fmax` ignore NaN, so in Round-2 `r03`/`r05` a member **without** a motif instance was scored as overlapping its reference when
computing group "correctness" (DEV J, precision; held-out G3). Recomputed NaN-safely: group-level precision is unchanged (DEV 67/71,
HELDOUT 67/69 rule passes), so DEV selection and G3 are unaffected. G1 and G7 were already masked by the call flag. The Round-2 decision
`ROUND2_FAIL_STOP` is unchanged. The same pattern in this post-mortem's panel table was fixed before the numbers above were written.

## 6 · Open items

- **977-ncRNA set:** provenance still open. If found, score the hashed Round-1 (`tables/PREDICTIONS_FROZEN.tsv`,
  `Z6_DENOVO/tables/PREDICTIONS_FROZEN.tsv`) and Round-2 (`ROUND2/tables/PREDICTIONS_FROZEN.tsv`) predictions without rerunning.
- **7 R3 pilot cases:** unresolved pending the June per-genome production outputs.

## 7 · Closing interpretation

**`RETRON_ENRICHED_NCRNA_SUBMOTIF`.** The element CMfinder reproducibly detects near retron RTs is a conserved ~90-nt sub-element of the
registered retron ncRNA (97.9 % overlap), strongly enriched in retron groups over other RT classes (85 % vs 52.5 %, p = 1e-7). It is **not**
a general RT-neighbourhood motif in retrons. The rule also passes many non-retron groups, usually on a different element (RT start/RBS, or
intron-like upstream structure), so pass/fail alone is not retron-specific. No new ncRNA family is inferred. The SPIRE de novo discovery
branch is **closed**: no clearly justified new *discovery* question emerged. The positional finding is handed to the boundary project.
