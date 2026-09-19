# Historical asset cross-check — `RETRON_STAGES/04` and the MAY scripts

**Scope:** provenance and completeness only. Nothing was recomputed. Stage 3B, its launcher, truth
set, detector design and anti-circularity contract were **not touched**. Ibex is unreachable from
this session (no `/ibex` mount; DNS resolution fails), so MAY originals could not be hashed; identity
was established from local copies, from embedded invocations, and from content comparison.

**Register changes:** `ASSET_REGISTER.tsv` 80 → **90 rows** (10 added, 2 amended);
`PATH_REGISTER.tsv` 25 → **30 rows**. Grades now GREEN 41 / AMBER 29 / RED 20.

---

## Mapping table

| historical object | original path | audited counterpart | identity evidence | same/earlier/later/new | status | Stage 3A relevance | Stage 3B relevance |
|---|---|---|---|---|---|---|---|
| stage brief | `/home/borg/RETRON_STAGES/04_palm_fingers_thumb_yxdd.md` | **none until now** — read in the audit, cited once in prose, absent from both registers | sha256 `55480258…`; grep of the audit deliverables returns 1 prose hit, 0 register rows | **new registration of an already-read document** | **AMBER** `STAGE_DOC_04_PALM` | high — it is the prose plan for 3A | low — 4 of its factual claims are refuted by the audit |
| `pdb_database_test.py` | `…/MAY/FINAL_SCRIPTS_FOR_DOCUMENTATION/` | **none** | 3 byte-identical local copies, sha256 `4627ec6a…`; internal docstring name `find_rt_references.py`; a pruned 766-line variant `ee19bf09…` also exists | **genuinely unaudited** | **GREEN** `MAY_FIND_RT_REFERENCES` | **high** — it is the inclusion rule | medium — its 3.5 Å cutoff corroborates the declared eligibility cut |
| `extract_reference_boundaries_v5.py` | `…/MAY/FINAL_SCRIPTS_FOR_DOCUMENTATION/` | `REFBOUND_TSV` / `BOUNDARY_RUNLOG` (audited) | the local `custom_and_hmm_analysis` copy (`d804ebec…`, 1791 L) carries the **exact MAY invocation** in a trailing docstring, and its `--struct_dir` matches `run_log.txt` verbatim | **later/annotated version of the audited producer** (earlier pruned copy = `06a692e7…`, 1684 L) | **AMBER** `MAY_EXTRACT_BOUNDARIES_LATER`; its output stays **RED** | **high** | low |
| `hhblits_create_bd_.sh` | `…/MAY/FINAL_SCRIPTS_FOR_DOCUMENTATION/` | **none** | single local copy, sha256 `f250d6ed…`; internal name `build_hhblits_db.sh` | **genuinely unaudited** | **AMBER** `MAY_HHBLITS_DB_BUILD` | medium | none |
| `annotate_rt_domains_v5_.py` | `…/MAY/FINAL_SCRIPTS_FOR_DOCUMENTATION/` | **none** | 3 identical copies, sha256 `5f2229d1…`; pruned variant `e488d6d5…` with InterProScan removed | **genuinely unaudited** | **AMBER** `MAY_ANNOTATE_RT_DOMAINS` | **high** — it is the historical boundary-transfer engine | medium — a third Foldseek line, and a mixed predicted/experimental reference DB |
| `build_subdomain_hmms.sh` | `…/MAY/VIABILITY_and_TASK_eval_progen/` | **none** | local `build_subdomain_hmms2.sh`, 5 byte-identical copies, sha256 `5c589833…`, is its successor | **earlier version of a local later file** | **AMBER** `MAY_FAMILY_ANNOTATION_DRIVER` | medium | none |
| `run_family_annotation.sh` | `…/MAY/VIABILITY_and_TASK_eval_progen/` | **none** | single local copy, sha256 `e4c9236b…`; header lines 1–14 **identical** to `build_subdomain_hmms2.sh`, loop truncated at line 24 | **earlier/truncated variant of the same driver** | **AMBER** (same row) | medium | none |
| `split_domain_annotation.sh` | `…/MAY/VIABILITY_and_TASK_eval_progen/` | **none** | exhaustive name and content search over `/home/borg` returns nothing | **genuinely unaudited and absent** | **RED** `MAY_SCRIPTS_ABSENT` | unknown | none |
| `diagnose_find_yadd.py` | `…/MAY/VIABILITY_and_TASK_eval_progen/` | **none** | same — no file, no product, no reference | **genuinely unaudited and absent** | **RED** (same row) | **high** — the only YADD-detection diagnostic named anywhere | medium |
| `build_active_site_matrix.py` | `…/MAY/VIABILITY_and_TASK_eval_progen/` | **none** — but its **output** survives | script absent; `family_active_site_matrix.json` and `…_v7.json` found in 4 local places | **documentation-by-product: output preserved, code not** | script **RED**; product **AMBER** `FAMILY_ACTIVE_SITE_MATRIX` | medium | medium — an unaudited per-family active-site definition |
| `reference_boundaries_24_116.json` | `…/MAY/FINAL_SCRIPTS_FOR_DOCUMENTATION/annotate_rt_domains_new/` | **none** — and it is **not** the audited `reference_boundaries.json` | named by both drivers; no local copy | **genuinely new and absent** | **RED** `MAY_REF_BOUNDARIES_24_116` | **high** | none |
| `9Z6Y` | MAY `reference_structure_table1.tsv` | **none** — the local set holds `9Z6Z` | both are live RCSB entries; `9Z6Z` = *resting* EcDRT3, `9Z6Y` = *elongating* EcDRT3, 2.6 Å, bound `MG` + `POP` | **genuinely new and never acquired** | **AMBER** `PDB_9Z6Y_ELONGATING` | medium | **high — see §6** |

---

## Answers

### 1. Was `04_palm_fingers_thumb_yxdd.md` incorporated into the previous audit?

**Read in full, but not registered.** It was `cat`-ed during the audit and is cited once in
`REUSE_DECISIONS.md` §12 (the one-gate-or-two argument). It appears **zero times** in
`ASSET_REGISTER.tsv` and `PATH_REGISTER.tsv`. That is a real gap in the audit's own bookkeeping and is
now closed by the row `STAGE_DOC_04_PALM`.

Substantively, nothing was missed: every method and resource it describes was independently located
and registered by the audit, and every one of its §8 pointers (`d2j_boundary_crossval`, `d21b`, `d21c`,
the 26+46 anchor correction, the three foldseek installs, foldmason, mkdssp) already has a row. Four
of its factual statements are **refuted** by the audit's measurements: span structures *are* on borg;
the TM matrix is 5256×5256, not 1,919; the id map is 7,875 sha1-verified, not 9,965; and "nothing on
borg pulls these crystals" is false.

**Its documentation of the twelve named topics maps as follows.** PDB acquisition/curation → §3 TODO
item 5, which says the script was *not found*; now `MAY_FIND_RT_REFERENCES`. Experimental inventory →
`XTAL_SET_25` + the 25 per-structure rows. DSSP/P-SEA → `DSSP_CACHE_26`, `D21C_SSE_AGREEMENT`.
Foldseek → `FOLDSEEK_BUILDS`, `TM_MATRIX_5256`, `C2_FOLDSEEK_ALN`, now also `MAY_ANNOTATE_RT_DOMAINS`.
FoldMason → `FOLDMASON_BUILD`, `FOLDMASON_MSA`. HHblits/HHsearch → `V7_HHR_PRODUCTS`, now also
`MAY_HHBLITS_DB_BUILD`. Subdomain HMMs → not covered by the document at all; now
`MAY_FAMILY_ANNOTATION_DRIVER`. Boundary transfer → `REFBOUND_TSV` (RED), `C6_BOUNDARY_DONORS`.
YXDD detection → `GATE_S_INSTRUMENT`, `C1_ANSWER_KEY`. Catalytic site → `C2_DYAD_ENV`,
`C5_TRIAD_PROBE`. ESMFold → `ESMFOLD_*`, `STRUCTURE_ID_MAP`. Sequence-to-structure numbering →
`C2_RESMAP`, `D21B_NTERM`. Family/domain annotation → previously unrepresented; now
`MAY_ANNOTATE_RT_DOMAINS`.

### 2. Were the MAY scripts already audited under other paths?

**No. None of the nine was in the audit.** Five have local counterparts under
`MELISSA_SCRIPTS/` — and the audit had touched only *one* of them, `extract_reference_boundaries_v5.py`,
and then only as the named producer of a RED table, without hashing it or reading its later version.

The local tree holds **two distinct versions of three scripts**. `custom_and_hmm_analysis/` carries the
later, annotated copies (which retain commented-out blocks and, in one case, the literal MAY command
line); `RT_domain_characterization/` carries earlier pruned copies. Operative parameters are identical
where both exist (`-e 0.001` in both `annotate_rt_domains_v5_.py` versions).

### 3. Which genuinely new assets were missed?

Six, in descending order of consequence:

1. **`MAY_FIND_RT_REFERENCES`** — the acquisition/curation script, whose absence three documents and
   the audit itself recorded as an open item. It is **GREEN**.
2. **`MAY_ANNOTATE_RT_DOMAINS`** — a third Foldseek product line plus the historical boundary-transfer
   engine, with full parameters (§4).
3. **`MAY_HHBLITS_DB_BUILD`** — HHblits database construction, single local copy.
4. **`reference_boundaries_24_116.json`** — a *different, larger* boundary file that the production
   annotation actually consumed. Absent locally. Anything said about boundaries transferred onto
   predicted structures is unverifiable without it.
5. **`9Z6Y`** — a set member that was curated but never downloaded (§6).
6. **`diagnose_find_yadd.py`, `split_domain_annotation.sh`, `build_active_site_matrix.py`** — absent;
   only the last one's output survives.

### 4. Does the historical document recover missing Foldseek / HHblits / HMM parameters?

**The document: no. The scripts: yes, substantially.**

`04_palm…` mentions Foldseek exactly four times and gives **no command, no database construction, no
sensitivity, no E-value, no coverage, no cov-mode and no post-processing** — only the three install
paths (which the audit already had) and the incorrect "1,919-protein TM matrix".

The scripts recover this, for a **Foldseek line the audit had not seen at all**:

| parameter | `annotate_rt_domains_v5_.py`, call 1 (general PDB DB) | call 2 (curated retron RT DB) |
|---|---|---|
| version / commit | **not recorded** | **not recorded** |
| database construction | prebuilt, path only (`reference_foldseek_db_expanded/retron_ref_db`) | same |
| query / target | one query `.pdb` (tail region) vs general PDB DB | one query `.pdb` vs "171 validated RTs" DB |
| command | `foldseek easy-search <q> <db> <out> <tmp>` | `foldseek easy-search <q> <db> <raw.tsv> <tmp>` |
| sensitivity `-s` | **absent — default** | **absent — default** |
| E-value | **absent — default** | **`-e 0.001`** |
| coverage `-c` / `--cov-mode` | **absent — default** | **absent — default** |
| alignment type / TM-score | **not requested** | **not requested** |
| output columns | `query,target,evalue,fident,alnlen,taxname`, `--max-seqs 3` | 18 columns incl. `qaln,taln,tca,tseq`; `--num-iterations 1` |
| post-processing | top hit | self-hit exclusion at `fident ≥ 0.99` |

**Compared with the two Foldseek products already classified:** `C2_FOLDSEEK_ALN` (AMBER) used
`--alignment-type 1` TM-align mode with `-e inf --exhaustive-search 1 --tmscore-threshold 0.0` over 26
crystal chains and **did** produce TM-scores; `TM_MATRIX_5256` (RED) has no producer at all. This new
line is a **third object**: E-value/identity alignments over predicted structures, no TM-scores, and a
reference DB that mixes 164 predicted models with 7 crystal structures. It does not rehabilitate
`TM_MATRIX_5256` and it does not supply the missing binary version for any of the three.

**HHblits — fully recovered:** `reformat.pl fas a3m` → `hhmake -i A3M -o HHM -v 0` → `ffindex_build -s`
(HHM and A3M) → `cstranslate`; search `hhblits -i query -d DB -o out.hhr -n 2 -cpu 4 -v 2`. With a
caveat visible in the code: the A3Ms are built from **single FASTA sequences**, so every profile has
depth 1 and the "profile–profile" search is sequence–sequence in substance.

**Subdomain HMMs — not recovered.** `build_subdomain_hmms(2).sh` builds no HMMs; it is a SLURM
submitter. The actual per-domain HMM work lives in `filter_rt_completeness_v4_v2.py`, present locally
and also never audited.

### 5. Does anything materially change the current Stage 3A design?

**Yes, four things — all of which make 3A easier and better constrained, none of which revives a
historical conclusion.**

1. **The inclusion rule for the historical 25 is now known**: RCSB name match **AND**
   `taxonomy_lineage ∈ {Bacteria, Archaea}`, triage KEEP/REVIEW/DISCARD, resolution > 3.5 Å → REVIEW,
   dedup at 0.95 alignment-aware identity. This *explains* the set's composition — no non-LTR, LINE,
   R2 or telomerase, because those are eukaryotic — and exposes `5VBS` (Moloney MLV, a virus) as
   inconsistent with the stated rule. 3A can now state, rather than infer, why its inherited set looks
   the way it does.
2. **The audited boundary table did not use a regex at all.** The operative motif matcher is a
   **literal list of 20+ tetrads** including `YADN`. Separately, the same file carries a commented-out
   alternative class with **literature citations attached** (Zimmerly & Wu 2015; Kojima & Kanehisa
   2008; Simon & Zimmerly 2008) — the first sourced character class found anywhere in this project,
   and directly relevant to the killed claim that the project's class was the field's.
3. **There is a second boundary file the production run actually used**
   (`reference_boundaries_24_116.json`), and it is not the one the audit graded. 3A must not assume the
   audited 25-structure file is what was transferred onto predicted structures.
4. **The historical boundary-transfer engine is now readable** (`MAY_ANNOTATE_RT_DOMAINS`): boundaries
   were carried onto predicted structures by best-hit similarity transfer from a reference DB mixing
   predicted and experimental structures — the same fragile step the audit graded RED, applied at
   scale. 3A now has the concrete prior method to improve on rather than a rumour of one.

### 6. Does anything materially change Stage 3B?

**One item does. It is reported here and Stage 3B has not been altered.**

**`9Z6Y` — "Structure of the *elongating* EcDRT3 reverse transcriptase in complex with its non-coding
RNA", cryo-EM 2.6 Å, bound components `MG` and `POP` (pyrophosphate).**

Why it matters: the Stage 3B dossier's blocking gap is that **no bacterial-defence retron RT structure
in the population is in a catalytic state**. `9Z6Y` is the elongating counterpart of `9Z6Z` (the
*resting* EcDRT3 complex, which *is* in the population as `RG29`/`RG30` at chains A and H), and it
carries magnesium plus the pyrophosphate leaving group — a post-chemistry catalytic state.

Why it was missed: it was **curated but never downloaded**. The MAY `reference_structure_table1.tsv`
lists `9Z6Y`; the directory on disk holds `9Z6Z`. The audit recorded "`9Z6Y` — no such file" and
treated it as a misremembering. It is not: both are live entries, they are different states of the
same system, and the historical set differs from the intended one by this member.

**What this would change if acted on** — stated, not done: it is a candidate `HARD_PAIR` for a bacterial
defence RT in a catalytic state, which is exactly the evidence class Tier B lacks. It could move
`C30_20` (Drt3a) or the `9Z6Z` groups out of their current tiers and would change the Tier A/B
denominators and the "no catalytic-state retron structure" scope limit written into
`LAUNCHER_03B` §1 and §10.

**Nothing was done about it.** `9Z6Y` was not downloaded, not measured, not added to
`STRUCTURE_REGISTER.tsv`, and no Stage 3B artefact was edited. Acquiring it is an operator decision
under §9 of the launcher ("acquiring structures beyond the declared inclusion rule … stop and wait").

Two further items are worth the operator's attention but change nothing on their own: the `annotate`
pipeline's reference DB mixes predicted and experimental structures, which is a pattern Stage 3B
explicitly forbids and should not be inherited; and the HHblits depth-1 profile caveat bounds any
reuse of historical HHblits probabilities.

---

## What this cross-check did not do

No file was recomputed. No Stage 3B artefact was modified. Ibex was unreachable, so the MAY originals
remain unhashed and four named objects (`split_domain_annotation.sh`, `diagnose_find_yadd.py`,
`build_active_site_matrix.py`, `reference_boundaries_24_116.json`) are registered as absent rather than
as missing-and-searched-for-on-Ibex. `9Z6Y` was identified from RCSB metadata only.
