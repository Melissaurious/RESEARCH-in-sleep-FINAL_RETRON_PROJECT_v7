# Table index

All paths repo-relative. `g2_*` tables are the frozen confirmatory result; `g2a_*` are the
descriptive atlas; `g0_*`/`g2_*` under the split bundles are population and split provenance.

## Confirmatory result — `results/embed_g2_frozen_baseline/tables/`

| table | content |
|---|---|
| `g2_test_ladder.tsv` | full test ladder: 6 models × 6 rungs, MRR (pre-registered and expected-tie conventions), component-level CIs, top-1/top-5, component counts |
| `g2_stop_rule.tsv` | paired per-component difference M-CCA − best trivial, per rung |
| `g2_stop_rule_corrected.tsv` | the same with the ≥30-component validity floor applied; the authoritative version |
| `g2_escalation_decision.json` | machine-readable escalation verdict (`g3_escalation_authorised: false`) |
| `g2_sensitivity.tsv` | near-duplicate-excluded population, per rung |
| `g2_strata.tsv` | T1–T4 descriptive MRR with component CIs |
| `g2_reverse.tsv` | ncRNA→RT retrieval |
| `g2_permutation.json` | rung 0F failure control: observed, null, p-value |
| `g2_validation_ladder.tsv` | validation-only baselines and selected-config ladder |
| `g2_cca_grid.tsv` | the 9-point grid and validation rung-1 MRR per configuration |
| `selected_config.json` | frozen k=32, α=0.01 and the selection rule |

## Descriptive atlas — `results/embed_g2c_atlas/tables/`

| table | content |
|---|---|
| `g2a_similarity_distributions.tsv` | observed pair vs three decoy classes: mean, sd, quantiles, Cohen's *d* |
| `g2a_neighbourhood.json` | top-k retrieval of the observed partner and type-sharing at k = 1/5/10/20, prevalence, 5.32× enrichment |
| `g2a_cca_dimensions.tsv` | per-dimension canonical correlation, cumulative share, η² of retron type, correlations with RT length / ncRNA length / GC |
| `g2a_type_encoding.tsv` | per-modality retron-type probe accuracy vs majority class |
| `g2a_pca_variance_rt.tsv`, `g2a_pca_variance_ncrna.tsv` | PCA explained-variance ratios (10 PCs) |
| `g2a_within_type_feasibility.tsv` | **21 retron types × feasibility criteria**, the audit behind §C |

## Split and population provenance

| table | content |
|---|---|
| `results/embed_g2b_frozen_split/SPLIT_MANIFEST.json` | the binding split definition: thresholds, coverage semantics, allocation, populations, n_eff, leakage, rationale |
| `results/embed_g2b_frozen_split/tables/split_assignment.tsv.gz` | all 30,924 pairs → component, fold, tier flags, near-duplicate flags |
| `results/embed_g2b_frozen_split/tables/split_components.tsv` | 1,075 components with fold and tier composition |
| `results/embed_g2b_frozen_split/tables/near_duplicate_stratum.tsv` | the frozen 3 RT + 263 ncRNA list |
| `results/embed_g2a_split_selection/tables/g2_decision_table.tsv` | the 12-combination threshold trade-off |
| `results/embed_g2a_split_selection/tables/g2_effective_units.tsv` | n_eff per fold per combination |
| `results/embed_g2a_split_selection/tables/g2_exact_leakage.tsv` | uncensored held-out-vs-training leakage |
| `results/embed_g2a_split_selection/tables/g2_fragment_bridge_options.tsv` | fragment-bridge pricing |
| `results/embed_g0_input_contract/tables/g0_views.tsv` | PAIR-ELIG vs T1–T4 population reconciliation |
| `results/embed_g1_representations/tables/g1_throughput.tsv` | per-shard throughput, VRAM, host RSS |
| `results/embed_g1_representations/tables/g1_hardware_comparison.tsv` | 4090 vs 1080 Ti vs A100, including the bf16 failure |

## Model / baseline summary

| id | scorer | fitted on | role |
|---|---|---|---|
| `B-pop` | ncRNA training frequency | train | ncRNA-only marginal |
| `B-len` | −\|len_nc − ridge(len_rt)\| | train | length |
| `B-gc` | −\|gc_nc − ridge(len_rt)\| | train | composition |
| `B-kmer` | cosine(ridge RT-dipeptide→ncRNA-4-mer, candidate) | train | strongest trivial |
| `B-model` | P(candidate type \| RT embedding) | train | RT-only marginal / label shortcut |
| `M-CCA` | cosine in shared CCA space, k=32 α=0.01 | train components only | cross-modal probe |
