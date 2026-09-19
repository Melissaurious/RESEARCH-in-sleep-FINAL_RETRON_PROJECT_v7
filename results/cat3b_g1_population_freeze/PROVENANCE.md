# PROVENANCE — cat3b_g1

Inputs: 62 coordinate files (three historical caches plus `data/stage3b_external_structures/`,
the latter acquired with a logged, hashing RCSB fetcher). Every path and sha256 in `INPUTS.tsv`.

The 11 legacy-PDB entries (5HHK 5VBS 6MEC 7UIN 7V9X 7XJG 8FLI 8QBM 8UBD 9VHE 9X94) were re-fetched
as mmCIF and compared chain-by-chain against the legacy files: identical residue counts, identical
aspartate sets, identical hetero inventories. No format-driven data loss.

No network access is required to reproduce this gate; no RNG is used.
Frozen 2026-09-18T11:40:02Z.

env_lock_sha256: 6711ca3943f06a07272d77cfae6af6fbf95b180bba25d663dc9d9b368131583f
seed: n/a — deterministic scan, no RNG anywhere in scan.py or truth_schema.py
agreements: cff983144e2ad6fc01f648982fb61810dd77ddbe

