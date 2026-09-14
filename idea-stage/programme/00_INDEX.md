# RETRON — STAGE DOCUMENTS

One document per stage. Each opens with **`## 0 · The point of this task`** — three to
six sentences, plain language, no hedging: what is unknown right now, and what changes
once the stage lands. Someone who reads only that section should be able to say why the
task is worth a day.

⚠️ **Status lines in these documents describe prior work in RETRON-DB V3/V4/V5.** Under
WA-I.3 all of it is `[UNVERIFIED]` in `research-wClaude-PART1_v2` until a row re-derives
it. `VOID_DO_NOT_CITE.md` has not been consulted; check it before quoting any figure.

## The operator's twelve

| # | file | title | status |
|---|---|---|---|
| 1 | `01_database_characterization.md` | Database characterization | 🟡 partly — active as `r01–r04` |
| 2 | `02_rt0_rt7_definition.md` | RT0-RT7 definition (general RT, focused on retron RTs) | 🟡 substantially **built**, foundation unverified |
| 3 | `03_blind_motif_discovery.md` | Blind discovery of motifs per RT family | 🟡 discovery holds; 3 derived claims failed |
| 4 | `04_palm_fingers_thumb_yxdd.md` | Detect/delimit palm/fingers/thumb domains and YXDD motifs | 🟡 partly — ⭐ ground truth already computed |
| 5 | `05_mestre_replication.md` | Replicate and learn limitations from Mestre work | 🟢 done |
| 6 | `06_tree_and_structural_route.md` | Construct a tree (sequence or structural?) | 🔴 closed negative — one route left |
| 7 | `07_neighbourhood_and_operon.md` | Annotate the neighbourhood of RTs + operon delimitation | 🟡 half closed, half untouched |
| 8 | `08_domain_fusions.md` | Analyse and characterize RT protein domain fusions | 🟡 a confound, never an object |
| 9 | `09_diversity_and_saturation.md` | Analyze diversity and saturation of the data | 🔴 blocked |
| 10 | `10_rt_ncrna_coevolution.md` | RT–ncRNA co-evolution | 🔴 the headline gap |
| 11 | `11_novel_rt_assessment.md` | Fast but robust assessment of a novel RT | 🟡 partly — the instrument exists |
| 12 | `12_annotation_disagreement.md` | Annotation disagreement as a signal (3 tools) | 🔴 barely started — ⭐ best stage |

## Proposed additions

| # | file | title | why |
|---|---|---|---|
| A | `A_delimitation.md` | Delimitation as a measurable property | the project's actual open problem |
| B | `B_object_register.md` | The object register | publishable with no computation |
| C | `C_positive_control.md` | Apparatus and positive control | the project currently has none |
| D | `D_relatedness_controls.md` | Relatedness and phylogenetic-signal controls | gates every co-variation claim |
| E | `E_detector_evaluation.md` | Detector evaluation protocol | our numbers are not comparable to the field's |
| F | `F_taxonomic_distribution.md` | Taxonomic and ecological distribution | smaller, still unwritten |
| G | `G_reproducibility_packaging.md` | Reproducibility packaging | a reviewer finds this in minutes |
| H | `H_classification_stability.md` | Classification stability | ⭐ from IDEAS §15 — every grouping moves when the knobs move |
| I | `I_non_retron_reference_set.md` | The non-retron RT reference set | ⭐⭐ from IDEAS §16 — "important missing piece", and it is |
| J | `J_novelty_profile.md` | Novelty as a profile, not a score | from IDEAS §17 |

## Source: `RETRON_RT_PROJECT_IDEAS.md`

The operator's living brainstorm (929 lines) sits in this directory. Stages H, I and J come
from it, and ten existing stage documents carry a final **"Refinements from
`RETRON_RT_PROJECT_IDEAS.md`"** section drawn from it:

| stage | ideas § | what it added |
|---|---|---|
| 1 | §2 | the uniqueness **ladder** (keep parallel datasets, don't choose); six duplicate classes; seven extra geometry axes; ⭐ the **frozen reference dataset** decision; isolate-vs-metagenome |
| 2 | §3 | the 14-column per-family report table; ⭐ **"missing-block combinations"** |
| 4 | §4, §5 | ⭐ the **palm/YXDD split** (4a boundaries · 4b motif · 4c the join); evidence-source table; "is geometry more conserved than motif sequence?" |
| 6 | §8 | ⭐ reframed as **"which representation?"** — 8 candidates, **5 never attempted** |
| 7 | §9 | ⭐ the **normalized architecture alphabet** (`ncRNA → RT → effector`), which links stages 7, 8, 1 and J |
| 8 | §10 | the retron-specific / family-specific / RT-general **three-way split**; convergence needs a tree we do not have |
| 9 | §11 | ⭐ **eight** saturation curves; Chao / Hill / singletons; isolate-vs-metagenome; "does oversampling fake saturation?" |
| 10 | §12 | ⭐ the five-rung **control ladder**; ⛔ **Mantel is rejected** — see below |
| 11 | §13 | ⭐⭐ the **eight graded output classes**, which respect the `A11` bound a binary filter cannot |
| 12 | §14 | ⭐ the **disagreement taxonomy** — 7 named types, 2 measurable today |
| E | §6 | ⭐ the **leave-one-family/clade/genus/phylum-out ladder** |

## ⛔ One correction to the ideas document

**§12 lists Mantel tests among the possible co-evolution analyses. Do not use them.**
`PE1` was re-specified for exactly this reason: a continuous relatedness covariate on a
distance matrix **is** a Mantel test, and **Harmon & Glor 2010** report inflated type-I
error for it, naming **Lapointe & Garland's PP** as the alternative. ⚠️ **Guillot &
Rousset 2013** argues the other side; the standing rule is **cite both or neither**. Use a
**PP-style block-constrained permutation** instead. Separately, **§7's Pagel's λ is not
executable** here (`E9`): binary-only, needs a resolved tree, and our labels are
multi-state.

## Dependency order — ideas §20 versus this set

The ideas document's rough order is sound and mostly agrees with
`/home/borg/RETRON_PROPOSED_STAGES_2026-09-10.md`. Four differences worth deciding:

1. ⭐ **It has no delimitation stage (A).** Boundary-drawing is the project's actual open
   problem and appears implicitly in its §4, §9 and §12.
2. ⭐ **It has no object register (B), positive control (C) or relatedness control (D).**
   D in particular gates its own §7, §12 and §14.
3. **It places the Mestre reassessment (§7) *after* phylogeny (§8).** Defensible, but
   `B4`/`B3` are already largely done and `C4` shows the reference lab published the same
   tree failure — so Mestre can inform the tree rather than wait on it.
4. ⭐ **It makes "frozen reference datasets" its own step (§20.2).** Adopted — folded into
   stage 1 §6 as an explicit operator decision.

## Parking-lot items (ideas §21) routed to stages

    orphan retron-like RTs with no ncRNA .............. 12 (the ~46% zero class), 10
    catalytic geometry vs motif conservation .......... 4 (⭐ testable with what exists)
    where existing retron HMMs / CMs fail ............. 12 (⭐ the publishable form)
    transitional systems between RT families .......... 12, H (the movers)
    accessory architecture vs RT phylogeny ............ 7, 6
    accessory proteins evolve faster than RTs? ........ 7
    convergent acquisition of fusion domains .......... 8 (⚠️ needs a tree)
    isolate vs metagenomic retron diversity ........... 9, F
    de novo retron ncRNA CMs / Toro-style rebuild ..... 5, 10
    sequence trees vs structure trees ................. 6
    families with unusual structural / ncRNA diversity  9, J
    multidimensional experimental prioritization ...... J (downstream, out of scope)

## Companion documents (outside this directory)

    /home/borg/RETRON_PROPOSED_STAGES_2026-09-10.md         order, gates, foreclosed list
    /home/borg/RETRON_IDEA_INVENTORY_2026-09-05.md          claims, experiments, evidence trail
    /home/borg/RETRON_STRUCTURAL_DATA_AND_METHODS_2026-09-09.md
    /home/borg/RETRON_STRUCTURES_AND_TOOLING_2026-09-09.md
    /home/borg/RETRON_STRUCTURE_ID_MAP_2026-09-09.tsv       9,965 structures, sha1-verified
