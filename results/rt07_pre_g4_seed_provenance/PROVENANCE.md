gate: rt07_pre_g4_seed_provenance
launcher: launchers/LAUNCHER_02_rt0_rt7_definition.md
decision_record: docs/decisions/2026-09-16_stage2_g4_design_amendment.md
scratch: ARIS_OUTPUT/02_rt0_rt7_definition
git_sha: 2e8d0a7
agreements: cff9831
env_lock_sha256: 9baa18b79c80c46bd536a8b6383b98fcfb7179e495a3747ed2bab35787254353
seed: n/a - no RNG; mmseqs is deterministic at fixed parameters
models: claude-opus-5[1m]
date: 2026-09-16
operator: Melissa Rios
compute: borg CPU, ~60 s wall, no GPU, no Ibex, no job submitted
network: none
prior_trees_read: RETRON-DB_V3/ARIS_OUTPUT/stage2b_assessor_redesign and RETRON-DB_V4/ARIS_OUTPUT - READ-ONLY; no prior file was written, moved or modified
tools: mmseqs easy-search (-s 7.5, --max-seqs 300, -e 1e-3), python 3 from retron_tradicional
comparators_read: Toro 2014 and myRT were read ONLY to measure how much of the old seed reappears in them. No comparator defines, seeds, fits or thresholds anything here, and none is carried into g4 as truth (launcher 5d)
purpose: close the last old-seed provenance gap (CAND95) before g4, and measure leakage by identity rather than by exact duplicates alone
