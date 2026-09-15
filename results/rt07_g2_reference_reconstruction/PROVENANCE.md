gate: rt07_g2_reference_reconstruction
launcher: launchers/LAUNCHER_02_rt0_rt7_definition.md
scratch: ARIS_OUTPUT/02_rt0_rt7_definition
git_sha: 2e8d0a7
agreements: cff9831
env_lock_sha256: 9baa18b79c80c46bd536a8b6383b98fcfb7179e495a3747ed2bab35787254353
seed: 20260915 - the only RNG is the null models in s04_controls.py (200 replicates, seeded); everything else is deterministic
models: claude-opus-5[1m]
date: 2026-09-15
operator: Melissa Rios
compute: borg CPU, ~60 s wall, no GPU, no Ibex, no job submitted
network: none - ALIGN_000044 was acquired in rt07_g1 and is verified here against the hash recorded at retrieval; run.sh performs no network access
substrate: EMBL ALIGN_000044 (66 proteins, 1441 columns), from data/derived/rt07_external_assets
tools: MAFFT (FFT-NS-2, --retree 2 --maxiterate 0 --thread 1 --anysymbol) for the second alignment frame; python 3 from retron_tradicional
comparators_read: none - no Toro 2014, Mestre 2020, myRT, Toro 2026/SPIRE, prior HMM, prior boundary, anchors72 or gold175 asset was read, opened or hashed by this gate (launcher 5d); Blocker 2005 LtrA coordinates were used only as an external test
declared_before_scoring: control/reconstruction_parameters.tsv, control/historical_statements.tsv, control/lineage_rules.tsv
