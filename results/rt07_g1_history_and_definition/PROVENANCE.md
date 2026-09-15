gate: rt07_g1_history_and_definition
launcher: launchers/LAUNCHER_02_rt0_rt7_definition.md
scratch: ARIS_OUTPUT/02_rt0_rt7_definition
git_sha: 2e8d0a7
agreements: cff9831
env_lock_sha256: 9baa18b79c80c46bd536a8b6383b98fcfb7179e495a3747ed2bab35787254353
seed: n/a - no RNG; the gate is deterministic text extraction, regex counting and quote verification
models: claude-opus-5[1m]
date: 2026-09-15
operator: Melissa Rios
compute: borg CPU, ~20 s wall, no GPU, no Ibex, no job submitted
network: one governed acquisition during this gate - EMBL-EBI (ftp.ebi.ac.uk, www.ebi.ac.uk) for ALIGN_000044, approved by launcher 9a and docs/decisions/2026-09-15_stage2_operator_decisions.md section A; recorded in tables/g1_acquisition_source_resolution.tsv; run.sh performs no network access
acquisition_destination: data/derived/rt07_external_assets (launcher 9c); references/rt0_rt7/ was not written to
tools: poppler pdftotext 22.02.0, pdfinfo, python 3 from the retron_tradicional environment, coreutils/grep for the second count
comparators_read: none - no Tier-2 asset was read, opened or hashed by this gate (launcher 5d)
