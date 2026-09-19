# PROVENANCE — m2a_reference_reconstruction

scratch_dir: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-mestre-audit/ARIS_OUTPUT/m2a
git_sha_at_assembly: e047fdcc46df6b376a98660e234cd5ccbf8e1962 (branch worktree-mestre-audit)
agreements: cff983144e2ad6fc01f648982fb61810dd77ddbe (general submodule pin)
env_lock_sha256: 9c6836194028fb2d2b363d39c842c944073555eac5272cf43ff49f536d1ebacd
env: /home/borg/miniconda3/envs/retron_tradicional (Ibex twin: /ibex/user/rioszemm/conda-environments/retron_tradicional, same IQ-TREE 3.1.3)
seed: 2026
seed_detail:
  - replicate splits: 2026*100 + rep (blocked); 2026*100 + rep + 5000 (random)
  - residue shuffles: 9000 + rep
  - control sampling (stratum X): 2026
  - Ibex IQ-TREE: -seed 2026
  - MMseqs2 / MAFFT: deterministic given their inputs (MMseqs2 cluster member ORDER varied between two runs; the counts did not)
date: 2026-09-19
operator: Melissa Rios
models: [claude-opus-5]
launcher: launchers/LAUNCHER_M2_historical_classification_expansion.md (rev-4, sha256 0bc716dc…491e at activation)
frozen_extractor: MCC-v3.1 — analysis/mestre_audit/scripts/m10_mcc_v3_freeze.py; params tables/MCC_V3_PARAMS.json
ibex_jobs:
  - 52098505 m2a_clean_tree_v3: CANCELLED after 00:28:31 on 12 CPUs (budget); checkpoint in /ibex/user/rioszemm/experiments/m2a/tree/
  - 52098506 m2a_au_test_v3: CANCELLED before start (dependency)
cpu_accounting_measured (user+sys, CPU-h):
  iqtree_fixed_topology_v3: 13.01    # /usr/bin/time: user 45988.22 s, sys 856.82 s
  iqtree_fixed_topology_v2: 8.41     # user 29676.93 s, sys 601.43 s
  raxml_full_reference_v3: 0.84      # user 3007.39 s
  replicate_v3_blocked_r01_first_run: 1.24
  replicates_24_xargs: 34.00         # user 122194.87 s, sys 206.31 s
  m2b_freeze: 1.30
  ibex_clean_tree_cancelled: 5.70    # 12 CPU x 28.5 min allocated
  total: 64.50                       # approved: 60 — overrun 4.5, disclosed in README §6
