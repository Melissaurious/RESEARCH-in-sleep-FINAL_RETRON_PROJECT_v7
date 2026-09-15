gate: dbchar_g7b_stage1_extended_report
role: reporting layer over the landed Stage-1 gates g1-g7; NOT a measurement gate
scratch: ARIS_OUTPUT/01_database_characterization/dbchar_g7b_stage1_extended_report
git_sha: 5e74794
agreements: cff9831
env_lock_sha256: b1a63d8a7745c82c16cb88b871b51dbbe9c71cbd3bcd2cf10fb0219f14d2acbf
seed: 20260915 - used by c02 (the 5,000-placement sample), c03 (the constructed uni/bimodal
      samples) and the fig25 jitter; matplotlib's SVG id salt is pinned to the gate id in
      common.mpl_setup, without which the SVGs are not byte-reproducible
models: claude-opus-5[1m]
date: 2026-09-15
operator: Melissa Rios
supersedes: nothing. results/dbchar_g7_stage1_report remains the authoritative Stage-1 closeout
            and validation report; this bundle adds a scientific synthesis layer beside it and
            modifies nothing in g1-g7.
derived datasets produced: none. This bundle registers no new derived artifact; it reads the 14
            already registered in data/README.md.
declared data gap: two columns of the GTDB bacterial catalogue (accession, gtdb_taxonomy) plus
            checkm2_completeness are read for the section-11 prevalence denominator, because no
            landed Stage-1 table carries sampled genomes per taxon. That file is a registered
            Stage-1 metadata input, already hashed and joined by g5, and is hashed again here.
            Raw JSONL is never opened by this bundle.
context resources: PADLOC's 18 retron_*.yaml rule files and cm_meta.txt are read as CONTEXT, not
            as measurement, and are hashed in INPUTS.tsv.
