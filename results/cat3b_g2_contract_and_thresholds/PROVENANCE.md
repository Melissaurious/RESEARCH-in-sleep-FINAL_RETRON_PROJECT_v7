# PROVENANCE — cat3b_g2

Thresholds derive from Tier A truth pairs only, by declared rounding rules recorded in
`tables/g2_frozen_parameters.tsv`. `DELTA_TIE` is declared a priori and is not outcome-derived.

The anti-circularity contract is enforced by executable code with a seeded-bad self-test
(`scripts/anticircularity_check.py --selftest`): the frozen detector is accepted, a deliberately
bad module referencing a family label and a Stage-2 state constant is rejected.

Tier B was not opened. `scripts/evaluate_tierA.py` asserts that no Tier B row enters the evaluation.

env_lock_sha256: 6711ca3943f06a07272d77cfae6af6fbf95b180bba25d663dc9d9b368131583f
seed: n/a — the detector is deterministic; no RNG is used anywhere in detector.py or evaluate_tierA.py
agreements: cff983144e2ad6fc01f648982fb61810dd77ddbe

