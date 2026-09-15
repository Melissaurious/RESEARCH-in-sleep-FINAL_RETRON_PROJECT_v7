# `references/rt0_rt7/` — reference assets for the RT0–RT7 operational-definition stage

**Status: assets only. Stage 2 has NOT been executed.**
Assembled 2026-09-15; amended 2026-09-15 (operator amendments 1-6). This directory contains located, hashed and registered reference
material. It contains **no interpretation of RT0–RT7, no detector, no alignment built
here, no HMM built here, no RT0–RT7 calls and no catalogue analysis.**

Nothing outside this directory was created, moved, deleted or modified. Every asset was
brought in by copy only; all source originals are untouched and re-verified byte-identical
after copying.

---

## 1. Directory structure

```
references/rt0_rt7/
  README.md                     this file
  RESOURCE_REGISTER.tsv         retained assets + registered missing/external assets (27 rows)
  SOURCE_AUDIT.tsv              every discovered copy, incl. duplicates (121 rows)
  PRIOR_WORK_INVENTORY.tsv      prior RT0–RT7 work, inventory only (18 rows)

  literature/                   TIER1 (4 PDFs) + TIER1_STRUCTURAL (1 PDF)
  historical/                   TIER2 · Toro 2014 comparator assets
  mestre_2020/                  TIER2 · Mestre 2020 comparator assets
  myrt/                         TIER2 · myRT reference package + build script
  toro_2026/                    TIER2 · Toro 2026 preprint comparator assets

  _provenance/                  how this directory was built, and the raw evidence
    01_discover_and_hash.py     sweep + sha256 + duplicate grouping  -> SOURCE_AUDIT
    02_select_and_copy.py       canonical-copy selection + copy-in    -> selection.json
    03_build_registers.py       RESOURCE_REGISTER + SOURCE_AUDIT + validation
    04_prior_work_inventory.py  PRIOR_WORK_INVENTORY
    discovery.json              all 121 discovered copies with hashes
    selection.json              which source produced each project copy
    archive_listing_spire_hmms.txt     non-destructive `tar tzvf` listing
    archive_listing_spire_scripts.txt  non-destructive zip listing
```

The four `_provenance/` scripts re-derive all three TSVs from the source trees, so the
registers are reproducible rather than hand-maintained.

## 2. Evidence-tier policy

### TIER1 — derivational primary evidence
May be used to determine **what the historical RT0–RT7 framework actually means**.
`allowed_to_seed_rt07_definition = YES`.

Four sources, all located locally and all verified to be the primary papers (not reviews):

| asset | citation | what it literally provides |
|---|---|---|
| `literature/Poch_…_1989_…pdf` | Poch, Sauvaget, Delarue & Tordo 1989, EMBO J 8(12):3867–3874 | motif evidence and motif **A–F** terminology; consensus blocks; 2 explicit residue spans |
| `literature/Xiong_Eickbush_1990_…pdf` | Xiong & Eickbush 1990, EMBO J 9(10):3353–3362 | alignment blocks; YXDD-class anchors; cross-element transferability statements |
| `literature/Zimmerly_Hausner_Wu_2001_…pdf` | Zimmerly, Hausner & Wu 2001, NAR 29(5):1238–1250 | **the only retained Tier-1 source that numbers RT subdomains**: "subdomains 1–7" and "subdomain 0" / "domain 0"; palm/finger terminology; consensus blocks; 2 alignment figures |
| `literature/Simon_Zimmerly_2008_…pdf` | Simon & Zimmerly 2008, NAR 36(22):7219–7229 | bacterial RT class terminology and scope; alignment discussion; cross-class transferability statements |

**Do not assume a Tier-1 source defines exact sequence boundaries.** Recorded factually,
from string presence in the extracted text, in `RESOURCE_REGISTER.tsv`:

- **RT1–RT7 numbering appears in none of them** (the one regex hit in Zimmerly 2001 is the
  gene name `C.e.RT1`, not a subdomain label);
- **subdomain numbering appears only in Zimmerly 2001** (4 × "subdomain/domain 0",
  1 × "subdomains 1–7");
- **explicit residue-coordinate spans** appear only in Poch 1989, and only twice.

The `RT0` / `RT0–RT7` string result is stated once, below, so the two cannot drift apart.

#### Nomenclature observation (string census only)

Recorded because it shapes what Stage 2 has to reconstruct:

- the literal string **`RT0` was not found** in any of the four Tier-1 papers;
- the literal string **`RT0–RT7` was not found** in any of the four;
- **Zimmerly 2001 explicitly uses `subdomains 1–7` and `subdomain 0` / `domain 0`** — it is
  the only one of the four that numbers subdomains at all;
- by contrast the TIER1_STRUCTURAL paper (Blocker et al. 2005) **does** use the modern
  spelling: literal `RT0` 14×, `RT1`–`RT7` tokens 38×, one `RT0–RT7` composite, `RT1 to 7`
  once, alongside `domain X` 28×. It writes *motif RT0*, where Zimmerly 2001 writes
  *subdomain 0*.

> ⚠️ **Do not infer from this string census alone which earlier source originated each
> modern conceptual boundary.** A census over five locally held PDFs cannot establish
> priority: the spelling may appear in sources this project does not hold, a paper may use
> a boundary it does not name, and a later paper citing earlier work is not evidence that it
> coined the term. What the census does establish is that the modern `RT0–RT7` spelling and
> the subdomain numbering in the retained Tier-1 set are **not the same notation**, which is
> a reason to **reconstruct the terminology and its history** in
> `rt07_g1_history_and_definition` — not a finding about RT0–RT7 in itself.

These are counts of what is present in the text, not a reading of what the sources mean.
Establishing the meaning is Stage 2's job and has not been started.

### TIER1_STRUCTURAL — structural primary evidence
`allowed_to_seed_rt07_definition = **NO**`.

| asset | citation | role |
|---|---|---|
| `literature/Blocker_et_al_2005_…pdf` | Blocker, Mohr, Conlan, Qi, Belfort & Lambowitz 2005, RNA 11(1):14–28, doi:10.1261/rna.7181105 | **independent structural interpretation / validation**, and the basis for later structural-domain work |

This paper is primary and Tier-1-grade, but it is deliberately **not** allowed to seed the
historical **sequence** RT0–RT7 frame. Two reasons, both recorded in the register: its
contribution is a three-dimensional model and domain architecture rather than a sequence
block definition; and it is the one retained paper that already uses the modern block
spelling, so seeding a sequence frame from it would import the very convention the stage is
meant to audit. Use it to interpret and to check a frame built without it.

### TIER2 — published / reference comparators
May **test** an independently reconstructed frame; **must not define it**.
`allowed_to_seed_rt07_definition = NO` for all 20 Tier-2 assets.

- `historical/` — Toro 2014 RT0–RT7 block FASTA and Table S1.
- `mestre_2020/` — reference tree and three variants of the supplementary assignment table.
- `myrt/` — myRT reference package (profile, alignments, tree, mapping, phylo model, run
  log) plus the distribution's own model-build script.
- `toro_2026/` — EPA-ng reference phylogeny, per-type HMM archive, type XI local tree, and
  the mining pipeline scripts. **Toro 2026 is a preprint, not peer reviewed.**

### TIER3 — previous project-derived assets
Prior scripts, mappings, domain calls, alignments and results. **Not ground truth.** These
were inventoried in `PRIOR_WORK_INVENTORY.tsv` and deliberately **not copied** into this
directory: no Tier-3 asset is retained here, so no Tier-3 row appears in
`RESOURCE_REGISTER.tsv`. Reuse categories used: `REUSE_CODE` (4), `REUSE_REFERENCE` (11),
`REVERIFY_RESULT` (3).

## 3. Why comparators must not seed the RT0–RT7 operational definition

Every Tier-2 asset here already carries the RT0–RT7 convention, or a classification
derived under it. If the reconstructed frame were seeded from Toro's RT0–RT7 block FASTA,
from Mestre's clade assignments, or from the myRT/Toro-2026 reference alignments and
profiles, then the reconstruction would reproduce the convention **by construction**: it
would agree with the comparator whatever the data said, and the agreement would carry no
information. That is why the register separates "may determine what the framework means"
from "may be used to test a frame built without it", and why the seeding column is a
first-class field rather than a note.

The same reasoning applies across comparators. The Mestre 2020, myRT and Toro 2026 assets
are not four independent references: their published provenance chains overlap. Treating
their agreement as corroboration would be a second instance of the same error. Establishing
who inherits from whom is not part of this task and is not asserted here.

## 4. Provenance and checksum policy

- **Discovery is content-based, not name-based.** The four Tier-1 PDFs were found by
  extracting page 1–2 of **all 1,176 PDFs** under `/home/borg` and matching title/author
  strings, so a differently-named copy could not be missed.
- **Every discovered copy is recorded**, not just the selected one: `SOURCE_AUDIT.tsv` has
  all 121 copies with sha256, byte count, a `duplicate_group` label, and
  `selected_project_copy = YES/NO`. This is what proves later which local source produced
  each project copy.
- **One canonical copy per asset.** Selection policy, declared before running: a copy
  already inside this project first (per `CLAUDE.md`: reuse an existing `MELISSA_DATA`
  copy), then `RETRON-DB_V4`, then `RETRON-DB_V3`, then sorted path order. Because every
  multi-copy asset was verified byte-identical, selection changes provenance only, never
  content.
- **Copy only.** `shutil.copy2` / rsync semantics. No original was moved, deleted or edited.
- **Post-copy verification.** sha256 recomputed on every project copy and compared to the
  selected source; byte counts compared; each source re-hashed to confirm it did not change.
- **Archives are listed, never extracted in place.** Both archives were inspected with a
  non-destructive listing kept in `_provenance/`. Neither original archive was replaced and
  neither was unpacked into the project.

## 5. What is currently present

**25 retained assets**, 27 register rows. The two non-retained rows are a registered
*missing* external asset (`ALIGN_000044`) and a registered *external, not-copied* asset
(`RVT-All.hmm`), both §6. **26 MB** total — 26,359,236 bytes of registered on-disk payload;
neither non-retained row contributes bytes to that figure.

| directory | assets | contents |
|---|---|---|
| `literature/` | 5 | the four Tier-1 primary PDFs + the TIER1_STRUCTURAL paper (Blocker et al. 2005) |
| `historical/` | 2 | `toro_2014_Rt0-Rt7.FASTA`, `TableS1_Toro_2014.XLSX` |
| `mestre_2020/` | 4 | reference tree + three supplementary-table variants |
| `myrt/` | 10 | `RVT-ref.hmm`, `Suppl_Toro_Tree.txt`, `buildRVT.sh`, and the 7-file `myRT-FastTree2.refpkg` |
| `toro_2026/` | 4 | EPA-ng newick, type-specific HMM archive, type XI contree, pipeline scripts zip |

All nine assets that were already in the project before this task were re-hashed and
confirmed byte-correct; none was replaced.

**Newly discovered and added** (10, incl. the operator-amendment Blocker paper): `TableS1_Toro_2014.XLSX`,
`Mestre_supplementary_material.csv`, `RVT-ref.fst`, `RVT-ref.sto`, `RVT-ref.tre`,
`RVT-ref.log`, `Mapping`, `phylo_modeldyadg_ia.json`, `buildRVT.sh`,
`SPIRE_retron_pipeline_scripts.zip`,
`Blocker_et_al_2005_RNA_group_II_intron_RT_domain_structure_3D_model.pdf` — plus the 4
Tier-1 PDFs, which were absent (`literature/` was empty).

Archive contents, from the non-destructive listings:

- `SPIRE_retron_type_specific_HMMs.tar.gz` — 32 entries: 1 directory, **30 `.hmm` files**,
  and `calibration_thresholds.tsv` (876 B).
- `SPIRE_retron_pipeline_scripts.zip` — 12 entries: 8 pipeline scripts
  (`00_run_full_pipeline.sh` … `07_run_mlocarna_rscape.sh`), `README.md`,
  `requirements.txt`, `LICENSE.txt`.

## 6. What remains missing or unresolved

**Registered as missing — Zimmerly 2001's own alignment, `ALIGN_000044`.** This is the
highest-value absent asset and is now a **row in `RESOURCE_REGISTER.tsv`**
(`asset_id = zimmerly2001_align_000044`, `evidence_tier = TIER1_MISSING_EXTERNAL`,
`provenance_status = MISSING_NOT_ACQUIRED`, `project_path = NOT_ACQUIRED`) so it cannot be
overlooked by anything reading the register.

The paper's front page carries `DDBJ/EMBL/GenBank accession no. ALIGN_000044`, and its body
states *"the alignment has been submitted to the EMBL database (accession number
ALIGN_000044)"*. It is the primary-source alignment behind the **only** Tier-1 paper that
numbers RT subdomains, so having it would let the historical frame be read off the authors'
own alignment columns instead of inferred from printed figures and prose.

- **Not downloaded during reference assembly**, per the instruction in force then.
  `ALIGN_*` is a legacy EMBL alignment accession space.
- **Governed acquisition is now approved** — `docs/decisions/2026-09-15_stage2_operator_decisions.md`
  §A, to be performed during `rt07_g1_history_and_definition` and ideally before
  `rt07_g2_reference_reconstruction`. Reconstructing a reference frame while this is absent
  means the sole subdomain-numbering source is available to this project as figures and prose
  only. The register row stays `MISSING_NOT_ACQUIRED` until a `g1` acquisition row exists;
  acquired bytes land in `data/derived/rt07_external_assets/` and are **never** written into
  this directory. A failed or ambiguous retrieval lands `MISSING_PRIMARY_ASSET`, and no
  substitute is invented.

**Missing — all other Tier-1 supplementary material.** No supplementary file belonging to
Poch 1989, Xiong & Eickbush 1990, Zimmerly 2001 or Simon & Zimmerly 2008 exists anywhere
locally. Reported as MISSING rather than downloaded or substituted.

**The myRT reference package: identified, checksum unverified.** Preserved exactly as
observed; **nothing was repaired, regenerated or replaced.** The package ships its own
`CONTENTS.json` manifest with md5s for four files. Three distinct situations, kept separate
in the register's `provenance_status` column:

| case | files | `provenance_status` |
|---|---|---|
| in the manifest, observed checksum **matches** | `phylo_modeldyadg_ia.json` | `PROVENANCE_VERIFIED_AGAINST_MANIFEST` |
| in the manifest, observed checksum **disagrees** | `RVT-ref.fst`, `RVT-ref.tre`, `RVT-ref.log` | `PROVENANCE_IDENTIFIED_CHECKSUM_UNVERIFIED` |
| **not represented in the manifest at all** | `RVT-ref.hmm`, `RVT-ref.sto`, `Mapping` | `PROVENANCE_IDENTIFIED_NOT_IN_MANIFEST` |

Observed md5s for the disagreeing three: `RVT-ref.fst` manifest `925131942f89…` / observed
`97ea389857c5…`; `RVT-ref.tre` manifest `63da9234e67d…` / observed `d40ebda92b19…`;
`RVT-ref.log` manifest `8a6284d3f90a…` / observed `9fad8b74c381…`.

**This is not a corruption claim.** The files are *identified*: the content is attributable
to the myRT authors (the log's first line records
`Command: /home/fsharifi/Apps/FastTreeMP …`, matching the manifest author string
`fsharifi`), and the disagreement is not a line-ending or trailing-newline artifact — that
was tested and ruled out. The accurate statement is that **the manifest does not describe
these versions**, so no published checksum currently verifies them.

**All discovered local copies are byte-identical to one another** (6 copies of each refpkg
file; see `SOURCE_AUDIT.tsv` `duplicate_group`). The disagreement therefore predates every
local copy and is not a local-copy defect. Consequence for Stage 2: these assets are usable
as comparators, but **must not be described as the published, checksum-verified myRT
reference package.** `RVT-ref.hmm` — the one myRT asset already in the project before this
task — falls in the *not in manifest* row, so it has no published checksum at all.

**Registered external, not copied — `RVT-All.hmm`.** Added to the register 2026-09-15
(`asset_id = myrt_rvt_all_hmm_external`, `provenance_status =
PROVENANCE_IDENTIFIED_EXTERNAL_COPY_NOT_RETAINED`, `project_path = NOT_COPIED_EXTERNAL`) to
close a provenance gap: the correction of the prior dossier's myRT model counts was measured
on this file, which was not previously a register row. It lives at
`/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/HMM/RVT-All.hmm`,
3,892,396 bytes, sha256 `74556bd2…`; **measured 2026-09-15: 45 models and 1,988 summed
NSEQ**, matching the myRT publication's own statement of 45 HMM models for 41 RT classes
built from 1,988 RVT_1 sequences. It is **not copied in** — 3.9 MB, and large canonical data
stay in place — so identity is the recorded source path plus the observed sha256, which
`_provenance/03_build_registers.py` re-verifies on every run. The refpkg manifest does not
list it and **no published checksum is invented for it**. It was not part of the
content-based sweep, so it has no `SOURCE_AUDIT.tsv` row. TIER2: comparator and provenance
evidence only, `allowed_to_seed_rt07_definition = NO`.

**Three different Mestre 2020 supplementary CSVs.** They are not copies of one file: they
are three header variants of the same table, and their column *names* differ
(`Mestre_supplementary_material.csv` keeps the published footnote markers
`Nodea,RT/Cladea,Retron (sub)b,…`; the other two are sanitised to
`Node,RT_Clade,Retron_subtype,…` and `Node,Clade,Retron_subsystem,…`). All three are
retained so the derivation is visible. **Do not join them on header name.** For anything
provenance-bearing, prefer `Mestre_supplementary_material.csv` as the least-derived form.

**A misfiled comparator.** `myrt/Suppl_Toro_Tree.txt` is attributed by its filename to
Toro, not myRT, but sits under `myrt/`. Left in place rather than silently reorganised;
flagged in the register. Its year could not be established from the file itself.

**Resolved — the Blocker et al. Tier-1 candidate.** Previously flagged for a ruling; the
operator has ruled. It is now retained in `literature/` as `TIER1_STRUCTURAL` with
`allowed_to_seed_rt07_definition = NO` (see §2). `PRIOR_WORK_INVENTORY.tsv` records the
change from `FOUND_NOT_RETAINED` to `RETAINED_IN_RESOURCE_REGISTER`.

**Prior work carries no provenance records.** All six V4 `rt0_rt7_*` output trees contain
**0 `.prov.json` files**. Every prior number is therefore `REVERIFY_RESULT` and no prior
result may be carried into Stage 2 without recomputation.

## 7. What this directory does not authorise

Assembling these assets does not begin Stage 2. Not started, and not to be started from
this directory without the operator: literature interpretation, detector construction,
alignment building, HMM building, RT0–RT7 calling, catalogue analysis. No scientific
conclusion about RT0–RT7 is recorded here or anywhere under `references/rt0_rt7/`.

Once Stage 2 execution begins this directory is **read-only to the track**
(`launchers/LAUNCHER_02_rt0_rt7_definition.md` §9c). Externally acquired assets are written to
the governed acquisition cache `data/derived/rt07_external_assets/` and recorded in the
`rt07_g1_history_and_definition` acquisition and source-resolution register — never by adding
files to, or editing, this package.
