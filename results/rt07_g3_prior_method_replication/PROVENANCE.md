gate: rt07_g3_prior_method_replication
launcher: launchers/LAUNCHER_02_rt0_rt7_definition.md
scratch: ARIS_OUTPUT/02_rt0_rt7_definition
git_sha: 2e8d0a7
agreements: cff9831
env_lock_sha256: 9baa18b79c80c46bd536a8b6383b98fcfb7179e495a3747ed2bab35787254353
seed: 20260915 - used only by the residue-shuffling null in s06_controls_and_summary.py
models: claude-opus-5[1m]
date: 2026-09-15
operator: Melissa Rios
compute: borg CPU, ~90 s wall, no GPU, no Ibex, no job submitted
network: none
prior_trees_read: /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/{D_instrument,d_instrument_audit,rt0_rt7_domain_test*} and /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage2b_assessor_redesign - READ-ONLY; no prior file was written, moved or modified
tools: HMMER hmmalign/hmmsearch from retron_tradicional, python 3
comparators_read: none - Toro 2014, Mestre 2020, myRT and Toro 2026/SPIRE remain unread; the prior project's own Toro-derived artefacts were registered but not used to define anything, and the comparator arm belongs to g7
prior_numbers_as_criteria: none - every prior figure reported here was re-measured from the prior files, and no prior value is an acceptance criterion (launcher 5d)
deferred: the interpretation of the RT1 concordance failure remains an operator decision (launcher 9b); g3 measured it and did not interpret it
