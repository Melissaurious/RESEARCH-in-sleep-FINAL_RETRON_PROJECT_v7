# Retron / RT Project — Idea Inventory

> **Purpose:** Living brainstorming document for the core retron / bacterial reverse-transcriptase characterization project.  
> This is **not** a finalized methods plan. Ideas can be added, removed, merged, split, or reordered.  
> The goal is to capture what the project should eventually answer before individual analyses are converted into task launchers.

---

# 1. Overall idea

Build a deeply characterized and non-redundant database of bacterial reverse transcriptases, with special focus on retrons, and use it to understand:

- what defines a retron RT;
- how retron RTs differ from other bacterial RTs;
- how retron RTs are structured;
- how retron systems are organized genomically;
- whether the current retron classification remains valid at large scale;
- how RTs, ncRNAs, accessory proteins, and system architecture co-evolve;
- how much retron diversity remains unexplored;
- how to rapidly assess whether a newly discovered RT is biologically plausible and worth deeper analysis.

The outputs of this project should create the reference datasets and biological rules needed for later sub-projects.

---

# 2. Deep characterization of the created database

## Main ideas

- Deeply characterize the full integrated database.
- Decide what should count as a unique biological observation.
- Prepare clean datasets for downstream analyses.

## Things to define

### Unique RT

Possible definitions to consider:

- exact amino-acid sequence;
- exact sequence hash;
- clustered sequence;
- conserved-core identity;
- full-length identity.

### Unique system

Need to decide whether uniqueness is based on:

- RT sequence;
- genomic locus;
- RT + ncRNA;
- RT + ncRNA + accessory proteins;
- system architecture;
- genome / strain / assembly identity.

### Unique RT–ncRNA pair

Possible definitions:

- exact RT sequence + exact ncRNA sequence;
- clustered RT + clustered ncRNA;
- same biological locus;
- same operon architecture.

## Duplicate problems to address

- Same system appearing under different genome IDs.
- Same biological strain represented by multiple assemblies.
- Same RT sequence occurring in multiple records.
- Same locus recovered by multiple tools.
- Same system represented by multiple databases.
- Exact biological duplicates versus genuine repeated systems.

## Dataset characteristics to report

- Number of genomes.
- Number of RT-containing genomes.
- Number of total RT systems.
- Number of exact unique RT proteins.
- Number of clustered RT proteins.
- Number of retron RTs.
- Number of non-retron RTs.
- Number of high-confidence RT–ncRNA pairs.
- Number of unique RT–ncRNA pairs.
- Number of systems per genome.
- Number of multiple-system genomes.
- RT-family distribution.
- Retron-subtype distribution.
- Taxonomic distribution.
- Database/source distribution.
- Length distributions.
- Sequence-quality outliers.
- Contig-edge / incomplete-context cases.

## Geometry / organization of retron systems

Characterize:

- RT–ncRNA distance;
- upstream versus downstream ncRNA;
- same-strand versus opposite-strand elements;
- ncRNA overlapping CDS;
- intervening CDSs;
- RT/accessory-gene distance;
- number of genes in the local system;
- operon span;
- gene order;
- recurrent system architectures.

## Open questions

- What level of deduplication should be used for descriptive statistics?
- Should several parallel datasets be kept instead of choosing one definition?
- Which dataset becomes the frozen reference for downstream tasks?
- How should strain-level redundancy be handled?
- How should metagenomic and isolate records be treated?

---

# 3. RT0–RT7 characterization across bacterial RTs

## Main idea

Use the literature to define the conserved RT0–RT7 regions for bacterial reverse transcriptases and then characterize how those regions behave specifically in retron RTs.

## Questions

- What is the accepted definition of RT0–RT7?
- Which blocks are universally conserved?
- Which are family-specific?
- Which are frequently absent?
- Are some regions expanded or contracted in retron RTs?
- Are motif boundaries stable across families?
- Are some motifs useful for classification?
- Which regions are most useful for phylogeny?

## Things to report per RT family

- Presence / absence of RT0–RT7.
- Occupancy percentage.
- Start position.
- End position.
- Length.
- Normalized position within the protein.
- Inter-motif distances.
- Sequence conservation.
- Consensus sequence.
- Missing-block combinations.
- Insertions.
- Deletions.
- Truncation frequency.
- Core completeness.

## Retron-specific comparison

Compare:

- all bacterial RTs;
- retron RTs;
- major non-retron RT families.

Ask whether retron RTs show a distinct conserved architecture.

---

# 4. Palm / fingers / thumb domain detection

## Main idea

Define and detect the structural RT core across bacterial RTs.

## Questions

- How should fingers, palm, and thumb be defined?
- Which reference structures should be used?
- Can boundaries be transferred reliably across divergent RT families?
- Are some families missing or expanding canonical regions?
- What is the best automated method for large-scale detection?

## Possible evidence

- structural references;
- sequence alignment;
- profile HMMs;
- HHpred / HHblits;
- Foldseek;
- AlphaFold / predicted structures;
- conserved catalytic motifs.

## Things to report

- domain presence;
- domain boundaries;
- domain lengths;
- domain completeness;
- relative position;
- insertions and deletions;
- family-specific architectures;
- confidence of assignment.

---

# 5. YXDD catalytic motif analysis

## Main idea

Detect and characterize the catalytic YXDD motif and confirm its relationship to the RT palm.

## Questions

- Is YXDD present in all complete bacterial RTs?
- Is it always located in the palm?
- Which variants occur?
- Are variants family-specific?
- Are apparently missing motifs caused by:
  - sequence truncation;
  - annotation error;
  - genuine biological divergence?
- Can catalytic geometry rescue cases where the canonical sequence motif is weak?

## Possible measurements

- motif sequence;
- motif position;
- normalized motif position;
- motif-to-palm distance;
- number of candidate motifs;
- family-specific variants;
- structural location;
- catalytic-residue geometry.

---

# 6. Blind motif discovery per RT family

## Main idea

Perform motif discovery without imposing the known retron classification to identify features that distinguish retron RTs from other bacterial RTs.

## Main biological question

What sequence or structural features are present in retron RTs but absent or depleted in other RT families, and vice versa?

## Possible features

- short sequence motifs;
- gapped motifs;
- motif combinations;
- motif spacing;
- conserved insertions;
- conserved deletions;
- amino-acid composition;
- local sequence entropy;
- structural loops;
- catalytic-site environment;
- protein-language-model features.

## Comparison groups

Potentially compare retrons against:

- Group II intron RTs;
- DGR RTs;
- CRISPR-associated RTs;
- Abi-associated RTs;
- G2L;
- UG families;
- other bacterial RT families.

## Validation idea

Test whether discovered features discriminate:

- known retrons versus known non-retrons;
- unseen RT families;
- unseen retron clades;
- highly divergent candidate sequences.

Avoid relying only on random train/test splits.

Potential tests:

- leave-one-family-out;
- leave-one-clade-out;
- leave-one-genus-out;
- leave-one-phylum-out.

## Open question

Can a small number of interpretable features identify retron-like RTs without simply learning phylogeny?

---

# 7. Reproduce / challenge / refine Mestre et al. classification

## Main idea

Replicate the analyses underlying the current retron classification and determine which findings remain supported with the expanded dataset.

## Questions

- Are the original RT clades recovered?
- Are they stable with much larger sampling?
- Do some clades split?
- Do some merge?
- Are new groups present outside the existing framework?
- Do RT phylogeny, accessory architecture, and ncRNA family support the same classification?
- Does current classification reflect evolutionary lineage, system function, or both?

## Analyses to consider reproducing

- RT phylogeny;
- retron clade definition;
- neighboring CDS / accessory-protein classification;
- ncRNA family definition;
- covariance models;
- RT–ncRNA relationships;
- co-evolution;
- system architecture.

## ncRNA component

Potentially:

- rebuild retron ncRNA families de novo;
- reconstruct covariance models;
- compare against existing CMs;
- test false-negative regions;
- incorporate methods inspired by newer Toro work;
- examine clades where current CMs fail.

## Important principle

Do not assume the existing classification is wrong.

Possible outcomes:

- largely confirmed;
- confirmed with refinements;
- several unstable groups;
- need for additional clades;
- need for a multi-axis classification.

---

# 8. RT phylogeny

## Main idea

Construct a robust evolutionary representation of bacterial RTs, with special focus on retron RTs.

## Main question

Which part of the RT sequence or structure provides the most stable and biologically meaningful phylogeny?

## Sequence representations to compare

- full-length RT;
- full conserved RT core;
- palm only;
- fingers + palm;
- selected RT0–RT7 blocks;
- trimmed alignment;
- family-specific core.

## Structural possibilities

- full-structure tree;
- catalytic-core structure;
- Foldseek-based distances;
- structural alignment of palm/fingers;
- sequence–structure hybrid approaches.

## Scope possibilities

- one broad bacterial RT tree;
- retron-only tree;
- broad tree + retron-focused subtree;
- family-specific trees.

## Questions

- Does full-length sequence distort phylogeny because of fusions and insertions?
- Which clades are stable across methods?
- Which sequences move depending on representation?
- Do sequence-based and structure-based trees agree?
- Which tree is most useful for downstream co-evolution analysis?

## Model robustness

Potentially compare:

- alignment methods;
- trimming strategies;
- substitution models;
- sequence redundancy levels;
- taxonomic balancing.

---

# 9. Smart annotation of proteins neighboring the RT

## Main idea

Create an efficient and biologically consistent way to annotate proteins associated with retron RTs.

## First issue

Define what should count as the retron operon or retron-associated neighborhood.

## Features to account for

- same strand;
- distance to RT;
- distance between CDSs;
- gene overlap;
- intervening CDSs;
- orientation;
- recurrent synteny;
- ncRNA position;
- known validated system architectures.

## Annotation sources to consider

- HMM profiles;
- Pfam;
- InterPro;
- BLAST / MMseqs;
- HHpred;
- Foldseek;
- predicted structure;
- recurring gene-neighborhood evidence.

## Questions

- Which accessory proteins recur by RT clade?
- Which accessory proteins recur across multiple clades?
- Which "unknown" proteins form recurrent families?
- Are accessory proteins better predictors of system type than RT sequence?
- Are there lineage-specific replacements of effectors?
- Are certain architectures associated with specific ncRNA families?

## Possible output

A normalized system architecture representation, for example:

```text
ncRNA → RT → effector
ncRNA → effector → RT
RT–effector fusion
ncRNA → RT → unknown → effector
```

---

# 10. Protein fusion domains in retrons

## Main idea

Characterize RT fusion proteins in retrons and determine whether similar fusions exist in other bacterial RT families.

## Questions

- Which domains are fused to retron RTs?
- How often do fusions occur?
- N-terminal or C-terminal?
- Where are the fusion boundaries?
- Are fusion architectures clade-specific?
- Are particular fusions associated with:
  - ncRNA family;
  - accessory proteins;
  - taxonomy;
  - retron subtype;
  - function?
- Have similar fusions evolved independently multiple times?
- Are the same domains fused to non-retron RTs?

## Potential extension

Compare fusion architecture across all bacterial RT families to distinguish:

- retron-specific fusions;
- RT-family-specific fusions;
- broadly common RT fusion patterns.

---

# 11. Diversity and saturation

## Main idea

Determine whether the current database has sampled most retron diversity or whether substantial unexplored diversity remains.

## Possible saturation curves

- genomes sampled → unique RT sequences;
- genomes sampled → RT clusters;
- genomes sampled → retron RT clusters;
- genomes sampled → unique RT–ncRNA pairs;
- genomes sampled → ncRNA families;
- genomes sampled → accessory architectures;
- genomes sampled → fusion architectures;
- genomes sampled → retron subtypes.

## Stratify by

- phylum;
- class;
- genus;
- environment;
- database;
- isolate versus metagenome;
- assembly quality.

## Questions

- Is global RT diversity saturating?
- Is retron diversity saturating?
- Are ncRNAs less saturated than RT proteins?
- Are new system architectures still accumulating rapidly?
- Which taxa contribute most new diversity?
- Which taxa appear under-sampled?
- Does taxonomic oversampling create a false impression of saturation?

## Possible diversity metrics

- rarefaction;
- accumulation curves;
- Chao estimators;
- Hill numbers;
- Shannon diversity;
- singleton / doubleton counts.

---

# 12. RT–ncRNA co-evolution

## Main idea

Analyze co-evolution using the highest-confidence retron RT–ncRNA dataset.

## Main question

Do matched RT–ncRNA pairs share evolutionary information beyond what is explained by taxonomy or RT phylogeny?

## Dataset requirements

- high-confidence RT–ncRNA pairs;
- deduplicated systems;
- reliable ncRNA boundaries;
- reliable RT family/classification;
- phylogenetic information.

## Controls

- random mismatches;
- within-clade mismatches;
- within-genus mismatches;
- phylogenetically matched mismatches;
- taxonomy-only baseline.

## Possible analyses

- sequence distance correlation;
- structural distance correlation;
- Mantel tests;
- phylogeny-corrected correlation;
- paired versus mismatched classification;
- protein / RNA embeddings;
- contrastive learning.

## Questions

- Is co-evolution global or clade-specific?
- Which RT regions contribute most?
- Which ncRNA regions contribute most?
- Does the signal survive patristic correction?
- Does accessory architecture correlate with stronger or weaker RT–ncRNA coupling?

---

# 13. Fast but robust assessment of a novel RT

## Main idea

Create a rapid triage system for deciding whether a newly discovered RT protein is biologically plausible and worth deeper analysis.

Do not commit yet to a specific computational method.

## Possible checks

### Basic sequence integrity

- ambiguous amino acids;
- sequence length;
- low complexity;
- internal stop codons;
- obvious truncation;
- contig-edge status.

### RT evidence

- RT-family profile match;
- RT0–RT7 architecture;
- fingers / palm / thumb completeness;
- YXDD motif;
- catalytic geometry.

### Family-specific expectations

- expected length range;
- expected motif occupancy;
- expected domain architecture;
- expected insertions / deletions.

### Retron-specific evidence

- retron-enriched motifs;
- retron-like structural features;
- retron phylogenetic placement;
- retron embedding similarity.

### Genomic-context evidence

- nearby ncRNA;
- strand consistency;
- plausible RT–ncRNA distance;
- accessory proteins;
- plausible operon structure.

## Important idea

Avoid a strict binary filter that discards unusual biology.

Possible output classes:

- canonical RT;
- probable RT;
- canonical retron RT;
- probable retron RT;
- divergent / interesting candidate;
- fragmentary;
- inconsistent;
- likely false positive.

---

# 14. Annotation disagreement as a signal

## Idea

Treat disagreement among annotation methods as something worth analyzing rather than simply cleaning away.

Examples:

- MyRT family disagrees with phylogeny.
- PADLOC and DefenseFinder disagree.
- Sequence classification disagrees with structure.
- RT appears valid but no ncRNA is found.
- ncRNA is found but system architecture is unusual.
- YXDD is weak or absent despite convincing RT structure.
- Expected domains are absent in apparently complete proteins.

## Questions

- Which disagreements are technical?
- Which reflect classification limits?
- Which identify biological novelty?
- Are disagreements concentrated in particular RT families?

---

# 15. Classification stability

## Idea

Any retron classification or clustering result should be tested for stability.

## Perturbations to try

- exact deduplication;
- different sequence-clustering thresholds;
- taxonomic balancing;
- excluding fragments;
- different alignment methods;
- different RT regions;
- different phylogenetic models;
- sequence versus structure representations.

## Questions

- Which groups remain stable?
- Which groups collapse?
- Which groups split?
- Which sequences repeatedly change placement?
- Are unstable systems especially interesting?

---

# 16. Non-retron RT reference set

## Important missing piece

Build a deliberately designed reference set of non-retron bacterial RTs.

Without this, it is difficult to claim that a feature is specific to retrons.

## Potential use

- motif specificity;
- domain architecture;
- YXDD comparison;
- structural comparison;
- fusion-domain analysis;
- novelty detection;
- fast triage;
- classifier benchmarking.

## Candidate groups

- Group II intron RTs;
- DGR RTs;
- CRISPR-associated RTs;
- Abi-associated RTs;
- G2L;
- UG families;
- other MyRT families.

---

# 17. Novelty analysis

## Main idea

Novelty should not mean only low RT sequence identity.

A retron system can be novel in several independent ways.

## Possible novelty dimensions

- RT sequence novelty;
- RT structural novelty;
- ncRNA sequence novelty;
- ncRNA structural novelty;
- accessory-protein novelty;
- fusion-domain novelty;
- operon architecture novelty;
- unusual RT–ncRNA pairing.

## Possible output

A novelty profile per system rather than one single score.

Example:

```text
RT sequence novelty:
RT structure novelty:
ncRNA novelty:
accessory novelty:
fusion novelty:
architecture novelty:
```

This could eventually help prioritize experimental candidates.

---

# 18. Potential project-level outputs

## Reference datasets

- non-redundant RT dataset;
- high-confidence retron RT dataset;
- non-retron RT reference set;
- high-confidence RT–ncRNA pair dataset;
- fusion dataset;
- operon architecture dataset;
- discordant-system dataset;
- novelty candidate dataset.

## Biological outputs

- bacterial RT0–RT7 profile;
- retron-specific RT profile;
- fingers / palm / thumb architecture;
- catalytic motif atlas;
- retron-specific motif catalogue;
- robust RT phylogeny;
- evaluation of current retron classification;
- accessory-protein atlas;
- fusion-domain atlas;
- diversity / saturation analysis;
- RT–ncRNA co-evolution analysis;
- rapid RT/retron triage framework.

---

# 19. Possible downstream sub-projects unlocked

These should remain separate from the core characterization project unless needed directly.

- ncRNA boundary detection;
- retron ncRNA discovery;
- RT–ncRNA compatibility prediction;
- contrastive RT–ncRNA modeling;
- automated retron classification;
- novelty detection;
- experimental candidate prioritization;
- conditional RT/ncRNA design;
- retron database / web resource.

---

# 20. Rough dependency order

```text
1. Database characterization and deduplication
2. Frozen reference datasets
3. RT0–RT7 architecture
4. Palm / fingers / thumb + YXDD
5. Retron-specific motif discovery
6. Phylogeny
7. Reassessment of Mestre classification
8. Operon / neighboring protein annotation
9. Fusion-domain analysis
10. Diversity / saturation
11. RT–ncRNA co-evolution
12. Fast RT / retron triage
13. Downstream ML / design projects
```

This order can change as results come in.

---

# 21. Ideas parking lot

Add anything here before deciding whether it deserves a launcher.

- Compare sequence trees and structure trees.
- Build de novo retron ncRNA covariance models.
- Revisit Toro-style ncRNA family reconstruction.
- Detect orphan retron-like RTs with no ncRNA.
- Detect candidate ncRNAs around divergent RTs.
- Analyze taxonomic bias in current retron classifications.
- Compare accessory architecture versus RT phylogeny.
- Test whether ncRNA families are more or less diverse than RT clades.
- Analyze convergent acquisition of fusion domains.
- Analyze whether catalytic-site geometry is more conserved than motif sequence.
- Look for transitional systems between RT families.
- Quantify where existing retron HMMs fail.
- Quantify where existing retron covariance models fail.
- Identify families with unusually high structural diversity.
- Identify families with unusually high ncRNA diversity.
- Test whether accessory proteins evolve faster than RTs.
- Compare isolate and metagenomic retron diversity.
- Build a multidimensional experimental-prioritization score.
- Add any new idea here before deciding whether it becomes a formal task.

---

# 22. Candidate launcher list

These are only placeholders. They can be renamed, merged, or split.

```text
dbchar-g1-dedup
dbchar-g2-integrity
dbchar-g3-system-geometry

rtarch-g1-rt0-rt7
rtarch-g2-core-domains
rtarch-g3-yxdd

rtmotif-g1-blind-motifs

phylo-g1-representation
phylo-g2-retron-tree

mestre-g1-replication
mestre-g2-classification-stability

operon-g1-definition
operon-g2-accessory-annotation

fusion-g1-catalogue

diversity-g1-saturation

coevo-g1-rt-ncrna

triage-g1-novel-rt-filter
```

---

# 23. Open questions to refine later

- What is the primary unit of biological independence?
- Which datasets should be exact-deduplicated versus clustered?
- What is the best non-retron RT comparison set?
- How should RT0–RT7 be defined operationally?
- How should palm/fingers/thumb boundaries be assigned?
- Which RT representation should be used for phylogeny?
- Should the main tree include all RTs or retrons only?
- What constitutes a retron operon?
- Should accessory proteins define a separate classification axis?
- How should ncRNA families be reconstructed?
- How should phylogenetic dependence be controlled in co-evolution analysis?
- Which analyses need sealed labels to avoid circularity?
- Which tasks are descriptive versus hypothesis-testing?
- Which tasks need to be completed before others can begin?

---

# 24. Notes

Use this section freely.

```text
-
-
-
-
-
-
```
