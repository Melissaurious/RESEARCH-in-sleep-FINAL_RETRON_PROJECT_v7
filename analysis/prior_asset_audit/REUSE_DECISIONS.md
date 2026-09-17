# PRIOR ASSET AUDIT — RT fingers/palm/thumb + catalytic-site geometry

**Scope:** asset and evidence audit only. No new biological analysis was run, no structure was
predicted, no expensive product was recomputed, and no Stage-3 launcher is written here.

**Date:** 2026-09-18 · **Worktree:** `RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit`,
branch `prior-asset-audit`. No historical directory was modified.

**Companions:** `ASSET_REGISTER.tsv` (79 rows, one per asset or dead route) ·
`PATH_REGISTER.tsv` (23 absolute paths with size and hash state).

**Governing principle applied throughout:** *reuse immutable expensive assets where identity and
provenance can be established; re-derive scientific claims.* An old conclusion being wrong does
not condemn the coordinates it was computed from.

Everything below was measured in this session unless it is explicitly attributed to a prior
document. Where a prior document and the filesystem disagree, the filesystem wins and the
disagreement is recorded.

---

## 1 · Grade summary

| grade | count | meaning |
|---|---:|---|
| **GREEN** | 40 | identity and provenance sufficient, no relevant known defect |
| **AMBER** | 22 | reusable after a bounded verification or re-derivation |
| **RED** | 18 | not reusable as scientific evidence or data |

Of the 18 RED, **9 are dead routes** recorded so Stage 3 does not repeat them. Of the other 9,
seven are *claims or summary tables* rather than data; only `tm.npy` and the foldseek `ava.*`
shards are RED **data**, and both are cheap to regenerate.

---

## 2 · What is actually on disk — corrections to the inherited picture

Five statements carried by prior summary documents are **false as measured today**. They matter
because each one either hides an asset or misdescribes a denominator.

| inherited statement | measured reality |
|---|---|
| "the span-sliced structures are on Ibex and are **not present on borg**" | `cache/fm/span_pdb/` on borg holds **5,256 real span-sliced `.pdb` files, 1,012 MB** |
| "the foldseek all-vs-all is **the 1,919-protein TM matrix**" | `tm.npy` is **float32 (5256, 5256)**; `tm.ids` has 5,256 ids. It is over the **span-sliced** set |
| "the id map is **9,965 sha1-verified**" | **7,875** rows verify; **2,090** (`mestre` 1,919 + `khan171` 171) use the `named` scheme and carry **no hash check**. The prior table lists `v4t_mestre` as `SHA1_VERIFIED`; it is not |
| "**ZERO** non-LTR / R2-type structures are available locally" (landed `structure_reference_inventory.tsv`, echoed by `G7_STRUCTURE_PLAN.md`) | **9 non-LTR RT structures** are on disk with a logged, hashed RCSB fetch: LINE-1 ORF2p `8C8J 8SXT 8UW3 9HDO 9K6G` and R2 `8GH6 9DOU 9NL2 9NL3` |
| "the acquisition script was **not found**; nothing on borg pulls these" | **two** working acquisition routes exist: `a1_fetch_log.tsv` (325 fetches, all HTTP 200, **sha256 per file**) and `c2_structure_reference.fetch_cif` |

A sixth: `structure_reference_inventory.tsv` marks 14 accessions `has_local_coordinate_file = NO`
(`23OR 26CZ 7KFT 7R06 7R08 8BGJ 8OZ7 8UB7 9D4S 9I2F 9IOA 9L7P 9LJE 9N69`). **All 14 are local**, as
mmCIF, in the stage2b columns cif cache.

One user-supplied identifier does not exist: **`9Z6Y`**. The file on disk is **`9Z6Z`**
(EcDRT3), and `9Z6Z` is the entry that contains *two* distinct RTs.

---

## 3 · The experimental structural reference set

### 3.1 The 25-entry set — GREEN as coordinates, AMBER as a *set*

`/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/`, 54 MB, 21 `.pdb` +
4 `.cif`. **Filename matches the in-file `HEADER`/`data_` accession for 25/25** (verified this
session); `TITLE`, `COMPND`/`_entity` and `SOURCE` were read for every entry; sha256 recorded per
file in `ASSET_REGISTER.tsv`.

The coordinates are reusable. The **set** is not a designed reference set:

* **`5VBS` is Moloney MLV RT** — a retroviral enzyme, recorded elsewhere in this project as a
  known non-member at 23.2 bits. It is an outgroup, not a member.
* **`9WY8` is an MBP fusion** (His6 + thrombin + PreScission + MBP). Measured frame offset **+398**.
  Any residue number read off that file uncorrected is wrong by 398.
* **`9Z6Z` contains two different RTs** — Drt3a (`RVT-UG3`, chain A) and Drt3b (`RVT-UG8`, chain H).
  The prior extraction used chain H only and never recorded chain A.
* **`9YFD` is a 1,229-residue DRT1 filament** and `24NC` a 540-residue DRT4 hexamer — multi-domain
  assemblies, not bare RT cores.
* **Four entries are the same Ec86 protein** (`7V9U 7V9X 7XJG 8QBM`), and `5HHJ`/`5HHK` are the same
  Roseburia protein (native + SeMet). Counting 25 as 25 independent structures overstates *n*
  roughly twofold.
* **`5HHJ` is a group II intron maturase RT** (Roseburia intestinalis, D4L313) — the prior
  `reference_boundaries.py` labels it `family=RVT-Retrons`, which is simply wrong, and it was the
  **hardcoded anchor** from which every other structure's boundaries were transferred.
* `Family:` is `unknown` for 24 of 25 in the extraction report, so **nothing in that product
  asserts the set is RT-only**.

### 3.2 A second, larger and better-provenanced structure set exists

| set | path | n | provenance |
|---|---|---:|---|
| stage2b anchor mmCIF | `stage2b_assessor_redesign/columns/cache/cif/` | 25 | in-script RCSB fetch, **no hash at fetch** |
| rtelem RCSB mmCIF | `rtelem-g2-panels/cache/rcsb_cif/` | 38 | **`a1_fetch_log.tsv`: url + HTTP 200 + bytes + sha256 for all 325 fetches** |
| HIV-1 RT outgroup | `columns_rt17/cache/cif/1RTD.cif` | 1 | same in-script route |
| RCSB entry FASTA | `rtelem-g2-panels/cache/rcsb_fasta/` | 287 | same logged fetch |

Union of distinct RT-bearing entries across all caches: **~48**, against the 25 that every prior
document treats as "the set".

The rtelem cache is the single most consequential find. Its 38 entries include:

* **the non-LTR / R2 comparison class the launcher declares absent** — `8C8J 8SXT 8UW3 9HDO 9K6G`
  (LINE-1 ORF2p RT) and `8GH6 9DOU 9NL2 9NL3` (R2 retrotransposon RT), all carrying `FADD`,
  confirmed by parsing the files this session;
* `7UIM` (group II intron apo) and `9D4S` (G2L4 + snapback substrate), neither in the 25;
* **a ready-made negative control set**: `1R7M 3OOL 3OOR 5A0M` (I-SceI homing endonuclease) and
  `3UVF` (LAGLIDADG variant) contain `FMDD`/`YSDD` — they **match `[YFWH].DD` and are not RTs**.
  Five non-RT proteins with a tetrad-shaped motif, already on disk, is exactly the specificity
  control a YXDD stage needs;
* keyword-search noise that must be excluded **by name**: HydE (`3CIW 3CIX 5FEP 5FEW 7O1O 7O1P
  8QMK`), terminase (`4BIJ`), nitrogenase (`7BI7 4JY8`), ribosome (`6TPQ`), endonuclease-only
  domains (`1VYB 8SP5 2EI9`).

**Decision.** Register all three caches. Re-download nothing. Hash the stage2b cache (open VERIFY).
Write the inclusion rule *before* deciding which of the ~48 enter Stage 3.

---

## 4 · Prior fingers / palm / thumb information — and how far it can be trusted

### 4.1 `reference_boundaries.{tsv,json,py}` — **RED, RE-DERIVE**

This is the file three prior documents call *"the ground truth"* and *"exactly this stage's ground
truth, and nobody has used it as such."* It is not ground truth. Reading `run_log.txt` line by line
shows the actual method:

1. **`5HHJ` chain A is the anchor**, with boundaries **hardcoded** as `(12,130)/(131,260)/(261,305)`.
   The source of those three numbers is recorded nowhere.
2. Every other structure is aligned pairwise to `5HHJ` and the boundaries transferred.
3. DSSP then refines the **palm** only: the strand containing the YXDD, the next strand, the first
   long following helix, and any block within 20 residues of it.
4. **`fingers` = everything before the palm. `thumb` = everything after the palm.**

Step 4 is the defect. The thumb and the fingers are **residuals, not measurements**. For a
multi-domain protein the "thumb" swallows every downstream domain: `24NC` thumb 287–536,
`9Z6Z` 336–649, `9YFD` **379–1229** (850 residues). The prior `d2j` cross-validation reports thumb
Jaccard **0.0** for `24NC`, `9WY8`, `9YFD`, `9Z6Z` and `5G2X` — that zero measures this defect, not
a biological absence, and must not be reported as a structural finding.

The product refutes itself in four further ways, all already on disk:

* its own report logs **"DSSP vs alignment boundaries disagree"** for **24 of 25** structures, up to
  **886 residues** (`9YFD`), and **"low alignment coverage to anchor"** down to **25.5 %** — and
  **neither warning gates anything**;
* **`5G2X`: palm 139–240 does not contain its own catalytic dyad at 308.** A later step
  (`c6_boundary_donors_dropped.tsv`) dropped it for exactly this reason;
* **`9Z6Z` chain A**: boundary falls outside the sequence, offset −94; also dropped by `c6`;
* **`7XJG`/`8QBM` give fingers 3–190 / palm 191–245 while `7V9U`/`7V9X` give 3–113 / 114–245 for the
  same Ec86 protein** — a 77-residue disagreement produced by the method on identical input;
* `5HHJ`'s `yadd_motif` cell is **empty** while its `yadd_start/end` are populated.

**Verdict.** The boundary numbers are RED. The `run_log.txt`, which makes all of this auditable, is
GREEN and should be kept as evidence.

### 4.2 What *is* trustworthy about prior boundary work

| asset | grade | why |
|---|---|---|
| `c6_boundary_donors.tsv` + `_dropped.tsv` | AMBER / **GREEN for the drop log** | the **frame-calibration method** (calibrate on the motif-C tyrosine, check against `(L/I)PQG`, drop failures with a stated reason) is sound and applied the **+398** `9WY8` correction. Only the inherited boundary *values* are bad |
| `d21b_per_chain_nterm.tsv` | **GREEN** | per-chain UniProt accession, construct length, modelled span, N-terminal unmodelled residues and disorder gaps for all 26 anchors. This **is** the tagged-construct offset record the launcher demands |
| `d21c_edge_disagreement.tsv` + `d21c_sse_agreement.tsv` | **GREEN** | DSSP vs P-SEA per-block start/end deltas, 605 matched elements: median delta **1**, p90 **3**, **89.75 %** of edges within a *pre-declared* 2-residue tolerance. **This is the boundary uncertainty model; it does not need inventing** |
| `d2j_boundary_crossval.tsv` | AMBER | the design is right — subdomain vs derived-region Jaccard per structure, with the Simon & Zimmerly 2008 expectation (RT1–7 ≈ fingers+palm, domain X ≈ thumb) as a predeclared reading. Covers **11 of 25**, and is computed against the RED boundaries |
| `a4_dyad_per_crystal.tsv` | AMBER | DSSP *and* P-SEA state at each RT1–RT7 landmark for 26 anchors. Its real content is a negative: **RT4–RT7 are coil in both algorithms almost everywhere** — the later landmarks have no secondary-structure signature |

**Both falsification gates the launcher requires have already been declared and run**, with
thresholds fixed before scoring:

* *Test 1 — is an N-terminal structural negative admissible?* → **ADMISSIBLE** (0/26 constructs
  N-terminally truncated against declared threshold 0.25; 8/26 with N-terminal disorder; median 3
  unmodelled residues, max 398).
* *Test 2 — do two SSE algorithms agree closely enough to set an edge?* → **ADMISSIBLE — "the pair
  may set boundaries"**.

Caveat worth carrying: P-SEA finds far fewer strands than DSSP (21 vs 9 for `23OR`), so the
agreement is carried by helices. A boundary set at a **strand** edge is less well supported than
the headline 89.75 % suggests.

---

## 5 · Prior YXDD / catalytic-geometry information

Three independent instruments exist. They are of very different quality.

### 5.1 `c2_dyad_env.tsv` — **GREEN, the best catalytic asset on disk**

Asp carboxylate atoms (`OD1`/`OD2`/`CG` only — no CA fallback) within **12 Å** of the catalytic
dyad, per crystal anchor, **expressed in entity coordinates**, 99 rows. The recurring pattern is
the real triad: an Asp at **offset +1** at ≈5–6 Å (the second D of YXDD) and an Asp at **offset −85
to −92** at ≈3–5 Å (the motif-A aspartate). This is a *measurement*, reproducible without foldseek,
and its numbering maps back to the biological sequence.

Its one dependency is the dyad call, which for some anchors is `column_resolved` (alignment-derived)
rather than `structure`. Those rows need structural re-derivation before the product is used to
validate an alignment-derived catalytic column — otherwise the loop closes on itself.

### 5.2 `c1_answer_key.tsv` / `c4_resolved_dyads.tsv` — **GREEN / AMBER**

The answer key is worth reusing chiefly as **method**. It records `n_occurrences` and
`occurrence_positions` per anchor and refuses to name a dyad when there is more than one candidate:
`8OZ7` carries `YLDD@316` and `YVDD@342`; `7R08` carries `YRDD@284` and `YGDD@425`. **A first-match
rule would have chosen wrongly.** That discipline is directly transferable — and it condemns every
prior product that uses the first regex hit.

### 5.3 Gate S (`s6d_gateS_f14_exact.py`) — **AMBER as code, RED as "catalytic-site geometry"**

The criterion: from the second D of the first `[YFWH].DD` (else `[LIV].DD`) match, is there *any*
Asp at least 20 residues away in sequence whose side chain is within **8 Å**? Sidechain atom is
`CG → CB → CA` by fallback.

It is a well-controlled instrument — a matched random-Asp null, a coupled denominator, a documented
threshold plateau ≥7 Å, and a documented correction of an earlier buggy version — and it has
survived four attacks. But it is **a proxy, not catalytic-site geometry**: "any distant Asp within
8 Å" is not the triad; a CA fallback silently changes the measured quantity; and first-match motif
selection is wrong for multi-YXDD proteins. Reuse as a **comparator baseline**; do not present it
as a geometric definition of the active site.

Two Gate S products are worth keeping: `s7u_gateS_span_vs_full.tsv` (verdicts identical on
full-length and span-sliced structures across 4 clusters — this is what licenses working on span
structures) and `s7q`/`s7s` (geometry tracks global structural separation; z = 16.69).

### 5.4 The catalytic column

`c5_framework_defs.tsv` records catalytic column **1038** (D2 at 1039) in a 2,208-column
`mafft_linsi` MSA, with **65/65** definer convergence, motif-A column 809, motif-B column 940, and
**26/26** structures placing the structural triad on that column. That last number is measured over
the anchor set that also *defined* the column. The **non-LTR entries in the rtelem cache are the
natural out-of-set test** and cost nothing to acquire.

---

## 6 · The 18-versus-25 discrepancy — resolved

Three prior documents carry this as an open item (*"which 18, and why 7 were dropped, is
unrecorded"*). It is a **software artefact with no biological content**.

`s7z_gateS_crystals.py` parses each file with a helper whose docstring says
*"→ … for the **first chain**"*, implemented as `ch0 = order[0][0]` — the chain of the first `ATOM`
record. The tetrad regex then runs on that chain only.

For seven entries the first chain is **not the RT**:

| entry | first chain is | length seen by `s7z` | RT chain actually is |
|---|---|---:|---|
| `5G2X` | group II intron RNA | 692 | C |
| `6ME0` | T.el4h RNA | 829 | C |
| `6MEC` | T.el4h RNA | 818 | C |
| `7UIN` | E.r IIC intron RNA | 541 | D |
| `8FLI` | group II intron RNA | 828 | B |
| `9E8Z` | retron Ec83 ATPase | 534 | H |
| `9NNB` | retron I-A PtuA | 550 | B |

**25 − 7 = 18.** Every one of the seven prints `none` in the run log, and the script's own counter
`tot` only ever sees 18.

Two further numbers in the same product are wrong and should never be quoted: the script docstring
says *"**30** experimental structures are already on disk"* and the landed
`s7z_gateS_crystals.tsv` records `n_structures = 30`. The directory holds **25**. The landed
`s1g_structure_inventory.tsv` independently records **25**.

**Consequences.**
* "Gate S fires on **18/18** experimental RT chains carrying a tetrad = 100 %" has a denominator
  defined by a chain-selection bug, not by biology.
* Claim `A9` was killed for a *different* reason (`YIDD` matches `[YFWH].DD`, so 0 of 18 were of the
  excluded class). The chain-selection defect was never found.
* **Claim `E5` still quotes "18/18 crystals" and has not been corrected.** It should be.
* The distances themselves (4.11–7.26 Å, median 4.99) are real measurements on real RT chains and
  survive as data.

The fix is cheap: an explicit, recorded chain-selection rule (entity description or UniProt, never
file order) and a re-run over all 25 — and over the two larger caches.

---

## 7 · Predicted structures — what is reusable without recomputation

| set | n | grade | condition |
|---|---:|---|---|
| ESMFold v1 full-length (`cache/fold/pdb/`) | 5,109 | **AMBER → GREEN for 5,067** | exclude or re-fold the **42** inputs longer than 1,000 aa |
| span-sliced (`cache/fm/span_pdb/`) | 5,256 | **AMBER** | land the span→parent offset table (deterministic, no GPU) |
| `ldd557` / `ldd_pdb` | 1,060 / 506 | AMBER | `sha1_16` ids verify; confirm the set's selection rule |
| `mestre` / `khan171` | 1,919 / 171 | AMBER | `named` ids, **no hash check possible** |

**New defect found in this audit.** `s5a_fold_esmfold.py` folds `s[:MAXLEN]` with `MAXLEN = 1000`.
**42 of the 5,292 input sequences exceed 1,000 aa (max 2,225)** and were silently truncated, while
the `.pdb` filename remains `sha1(full_sequence)[:16]`. Spot-checked: `aed1f66d78b74d40` — 1,195 aa
input, **1,000 residues modelled**; `8505fd14d60c6717` — 1,018 aa input, 1,000 modelled;
`313445a10a19b083` — 1,165 aa input, **only 209 residues written**, unexplained.

So the celebrated "self-verifying id" **verifies the input sequence, not the modelled object**, for
those 42. Every other structure is genuinely self-verifying, which is a real and unusual strength:
`7,875/7,875` `sha1_16` ids reproduce `sha1(sequence)[:16]` exactly, and all 9,965 `pdb_path`
entries exist on disk (re-verified this session).

Span structures are **renumbered 1..N** and the offset is stored nowhere. It is exactly recoverable
by re-running the anchor search (`s6g`: first `[YFWH].DD` else `[LIV].DD`, window −220…+120) on the
parent, which still exists. That re-derivation is the whole cost of making 1 GB of span structures
reusable — and it should also record, per structure, **whether the anchor used was the catalytic
YXDD or merely the first match**.

**Not present, not needed yet:** no AlphaFold or AF3 product exists anywhere in this project. AF3
databases exist on Ibex (`/ibex/reference/KSL/alphafold/3.0.0/`, including three RNA databases) but
**no `params/` was ever observed**, so AF3 weights are unconfirmed. Nothing in a fingers/palm/thumb
stage requires AF3.

---

## 8 · Foldseek / FoldMason / HHsearch / structural-alignment products

| product | grade | reason |
|---|---|---|
| `c2_resmap.tsv` (12,002 rows) | **GREEN** | struct_idx ↔ entity_idx for 26 chains, **frame-validated at ≥90 % against the entity sequence before acceptance**. This is the numbering bridge |
| `c2_struct_pairs.tsv` (92,082 residue correspondences) | **AMBER** | already in entity coordinates; the single best boundary-transfer substrate. Needs only a pinned foldseek |
| `c2_pair_summary.tsv` (325 pairwise TM + LDDT) | **AMBER** | same condition |
| `c2_foldseek_aln.tsv` | **AMBER** | parameters fully visible in source (`--alignment-type 1 -e inf --exhaustive-search 1 --tmscore-threshold 0.0`); only the **binary version** is missing |
| `tm.npy` 5256×5256 | **RED** | **no producing script exists** among the 60 in that arm — only consumers. No parameters, no binary version, and the object it covers was mis-described in every prior summary |
| `cache/fs_mestre/`, `cache/fs557/` (535 MB of `ava.*` shards) | **RED** | raw shards, no command line, no version, no run log |
| **FoldMason structural MSAs** | **GREEN** | **four complete runs**, each emitting the amino-acid *and* 3Di alphabet on identical taxa and columns plus a guide tree: `rtspan_*` **5,256 × 4,132** (span-sliced, the repaired object), `rt90_*` **3,947 × 2,564**, `rt_*` **5,257 × 9,067** (full-length, known-defective), `smoke_*` 127. **Version `4.dd3c235` and the exact `easy-msa` command line are recorded in `logs/fm_{all,span,90,smoke}.log`** with matching `.time` files. This is the best-provenanced expensive structural product in the whole audit |
| HHsearch / HHblits | **GREEN** | 210 `.hhr` + 21 `.hhm`/`.hmm`/`.sto` inside the landed v7 `rt07_g4a_frame_recovery` bundle, with reversed and shuffled negative controls. HH-suite capability is established in-project. These are **sequence** products and say nothing about structure |

**The single highest-leverage cheap action in this whole audit:** the local
`/home/borg/foldseek/bin/foldseek` reports **only** commit `d609cff8ca9250b9994a96207fb22a1585e7964e`
and no semantic version — which is why the launcher grades all three installs `DO-NOT-USE`. The
`esmologs` build and the Ibex module both report **`10.941cd33`**. Pinning that one build and
recording it promotes `c2_foldseek_aln` / `c2_struct_pairs` / `c2_pair_summary` from AMBER to
GREEN-eligible in a single step.

---

## 9 · Routes that must NOT be rerun

Recorded so a Stage-3 launcher does not spend compute rediscovering them. **None were repaired or
rerun during this audit.**

1. **`s6b_gateS_LDD.py`** — buggy first-pass Gate S. Three defects, all inflating the null: CA-only
   distance instead of sidechain carboxyl; no exclusion of Asps within 3 of the anchor (so a
   "random" Asp could land *on* the catalytic DD); a control drawn for every model rather than only
   motif-positive ones. Use `s6d_gateS_f14_exact.py`.
2. **Structural-MSA phylogeny.** Every column-based method — sequence MSA, structural MSA and 3Di
   alike — plateaus at ~18 % trustworthy splits. The reference lab reported the same failure in
   print (Toro 2018).
3. **TM-distance NJ trees.** The last tree route tried, with the declared reading *"RF high → no
   route we have tried produces a tree."* Do not re-attempt a structural phylogeny in this stage.
4. **PSSM-based admission.** Collapsed: masking the tetrad columns to remove bias destroyed family
   discrimination (Retron PSSM then passes `RVT-UG2` at 95.0 %, GII at 83.7 %). The masked columns
   *were* the discrimination.
5. **The phrase "domain-based phylogeny."** Withdrawn by the prior work itself and banned by the v7
   g3 audit — the tips were a 341-aa tetrad window, Jaccard 0.732 against the published window.
6. **Claim `A9` ("18/18 including one the standard criterion excludes").** Killed. `YIDD` matches
   `[YFWH].DD`. Do not resurrect it; and see §6 for the second, undiscovered defect.
7. **Claim `A10` ("`[YFWH].DD` is the criterion the field uses").** Killed — it is this project's own
   invention; published tools admit by HMM bit score. Open item `PE15` (where `W` and `H` came from)
   was never run. Any Stage-3 motif definition must **source its character class or declare it as
   ours**.
8. **The phrase "72 structure-validated anchors."** Banned. 72/72 are in the model seed, only **26**
   have a structure at all, 46/72 are members of the population they score, 7 carry His6 and one
   SUMO. Say "26 with structure + 46 sequence-propagated".
9. **Claim `D6`** (Region X family-exclusivity). Withdrawn by the prior work: 224× / 445×, not
   2,657× / 4,936×, and Region X is weak rather than family-exclusive.

---

## 10 · Expensive compute already saved

Reusable now, or after a bounded check, without repeating the original cost.

| saved | scale | condition |
|---|---|---|
| ESMFold v1 predictions | **8,765 models**, ~2.1 GB, GPU-hours | 42 over-length exclusions |
| span-sliced structures | **5,256**, 1,012 MB | emit the offset table (CPU-minutes) |
| experimental structure downloads | **~48 distinct RT-bearing entries** across three caches, 175 MB | hash the stage2b cache |
| RCSB acquisition provenance | **325 logged fetches with sha256** | none — GREEN |
| **FoldMason structural MSAs** | **4 runs**, up to 5,257 taxa × 9,067 columns, aa + 3Di + guide trees | **none — version and command line logged** |
| foldseek all-vs-all on crystal anchors | 325 pairs, 92,082 residue correspondences | pin the binary |
| DSSP + P-SEA | **26 chains, both algorithms**, plus per-block deltas | recompute (seconds) with a recorded version |
| catalytic-geometry extraction | 99 measured Asp-carboxylate contacts in entity coordinates | re-derive the `column_resolved` dyad calls |
| structure↔UniProt numbering | 26 chains with construct/modelled/offset | none — GREEN |
| structure id ↔ sequence map | **7,875 sha1-verified** of 9,965 | re-run the producer inside a bundle |
| HH-suite profile products | 210 `.hhr` with negative controls | none — landed and GREEN |
| **both falsification gates** the launcher requires | declared thresholds, run, ADMISSIBLE | re-derive as claims; the instruments stand |

**What genuinely must be recomputed:** `tm.npy` (no producer, no provenance) and the foldseek
`ava.*` shards (same). Both are cheap to regenerate from structures that already exist, once a
binary is pinned. Nothing in this audit requires new GPU work.

---

## 11 · Minimum new work before a rigorous stage can be defined

Ordered; none of it is a biological analysis and none needs a GPU.

1. **Pin one foldseek build** (`10.941cd33`) and record its identity. Unblocks four AMBER assets and
   lifts a standing `DO-NOT-USE`.
2. **Write the structure inclusion rule before touching the structures**, then build **one**
   structure register over all three caches — accession, chain, entity, UniProt, method,
   resolution, tag, construct offset, near-duplicate cluster, allowed role. Extend the existing
   `structure_reference_inventory.tsv`; correct its two stale rows.
3. **Fix the chain-selection rule** and re-measure the tetrad and its geometry over every RT chain
   in the register, replacing the 18/18 denominator. Report the **7 previously dropped entries
   explicitly**.
4. **Hash the stage2b cif cache**; re-verify every accession against its in-file identity as was done
   here for the 25.
5. **Emit the span→parent offset table** and flag, per structure, whether the span anchor was the
   catalytic YXDD or merely the first match.
6. **Exclude or re-fold the 42 over-length ESMFold models**, and audit short writes.
7. **Re-derive the fingers/palm/thumb boundaries from scratch**, with a *positive* criterion for all
   three subdomains rather than a palm plus two residuals, and with the multi-domain cases
   (`9YFD 24NC 9Z6Z 9WY8 8QBM`) delimited to their RT core first.
8. **Carry the two falsification gates forward** as re-derived claims — `d21b` (N-terminal
   admissibility) and `d21c` (SSE edge agreement) — rather than re-inventing an uncertainty model.
9. **Register the non-LTR/R2 set and the 5 non-RT YXDD decoys** as first-class Stage-3 assets. The
   RT0 question requires the non-LTR class, and it is already on disk.

Two questions that must be **answered in writing before any method is chosen**, because both have
already destroyed claims in this project:

* **Where does the `[YFWH].DD` character class come from?** (`A10` killed, `PE15` never run.)
* **Which chain, and which occurrence, is "the" catalytic tetrad?** (`8OZ7` and `7R08` each carry
  two; the prior span slicer and Gate S both take the first match.)

---

## 12 · Recommendation — one gate or two?

### Two gates, with a third, explicitly a join.

The evidence in this audit points one way. **Boundaries and catalytic geometry fail differently,
fail at different rates, and rest on different assets.**

* **The catalytic side is close to ready.** The dyad has a resolved position per anchor with a
  stated basis, an explicit ambiguity policy, a measured Asp-carboxylate environment in entity
  coordinates, an MSA column with 65/65 convergence, a controlled geometric criterion with a null
  and a threshold plateau, and an out-of-set test class (non-LTR) already on disk. What it needs is
  a chain-selection fix, an occurrence-selection rule and a sourced character class.
* **The boundary side is close to empty.** Every inherited boundary number is RED. The thumb has
  never been *measured* in this project — it has only ever been "whatever follows the palm". The
  work required is a genuine re-derivation, not a verification.

Merging them would let the mature half carry the immature half. Worse, it would make the field's
central expectation — *the YXDD sits inside the palm* — **unfalsifiable by construction**, because
the prior palm was grown *outward from the YXDD strand*. A palm defined from the tetrad cannot then
be used to test whether the tetrad is in the palm. The two objects must be derived **independently**
before they are joined.

The prior stage brief reached the same conclusion from a different direction
(`RETRON_STAGES/04`, §7: *"§4 is palm/fingers/thumb detection; §5 is YXDD motif analysis. Keeping
them separate is better than the merge in this document, because they fail differently"*). The
launcher's own framing agrees: the **RT0–RT7 sequence framework** and the **fingers/palm/thumb
structural partition** are *"kept distinct throughout and neither is substituted for the other."*

**Proposed shape — three gates, not two:**

| gate | object | readiness |
|---|---|---|
| **A · structural core boundaries** | fingers / palm / thumb, positively defined, with the `d21c` uncertainty model and multi-domain cases delimited first | **needs real new derivation** |
| **B · catalytic site** | tetrad identity, occurrence selection, triad geometry in entity coordinates, with the non-RT decoys as the specificity control | **mostly assembled; needs fixes, not invention** |
| **C · the join** | is the tetrad inside the independently derived palm, and **where is it not** | **only meaningful if A and B are independent** |

Gate B can start first and does not block on Gate A. Gate C must not start before both.

A separate opportunity the prior work identified and never ran, which this asset base supports
directly: **is catalytic-site geometry more conserved than the motif sequence?** The asymmetry is
already on record — the geometric validation survived the `A9`/`A10` kills while the sequence-based
admission validation did not.

---

## 13 · Open items this audit could not close

1. **Ibex was not reachable** from this session, so `/ibex/project/c2366/RETRONS/` (11 GB),
   `esmfold_khan171/`, `rt_reference_search/structures` and
   `JULY_2026_RETRONS_TEST/stratum3_esmfold/structures/` were **not inventoried**. Prior documents
   record borg/Ibex counts differing on **every** shared set; they are not verified mirrors.
2. **No RCSB re-verification of accession → entry was performed** (no network). In-file
   `HEADER`/`data_`/`TITLE`/`COMPND` identity was verified for 25/25 instead, which is strong but
   not the same thing.
3. **Expression tags in `structure_reference_inventory.tsv` are regex inferences**, not recorded
   annotations, for every entry except `26CZ`. That file says so itself; the item stays open.
4. **AF3 weights on Ibex remain unconfirmed** (databases present, no `params/` observed).
5. **`tm.npy`'s producing command was not found.** It may exist on Ibex; on borg it does not.
6. **The `id → rt_system_id → genome` link still does not exist.** The id map reaches the *sequence*
   and stops. Any statement tying a predicted structure to a genomic locus is currently unsupported.
