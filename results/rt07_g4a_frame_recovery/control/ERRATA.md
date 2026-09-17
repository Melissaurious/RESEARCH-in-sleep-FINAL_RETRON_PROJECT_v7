# g4a ERRATA — three errors made and corrected during execution

Recorded because each produced a plausible-looking result that would have been wrong, and
because two of them produced *negative* results that could easily have been reported as
findings. Absence is loud; wrongness is quiet.

## E1 · `hhsearch -d` failed silently and produced an EMPTY correspondence table

`scripts/g4a_pipeline.py` originally ran `hhsearch -i A.hhm -d B.hhm`. `-d` requires a prebuilt
ffindex database, so every call failed with
`could not open file 'Retrons.deriv.hhm_cs219.ffdata'`. The call used
`subprocess.run(...)` **without** `check=True`, so the failure was swallowed and the table landed
with 21 rows of empty scores.

**How it would have been misread:** as *no between-family correspondence* — the strongest possible
negative result of this entire task, and completely false.

**Fix:** `hhalign` is the correct pairwise profile-profile tool. All 42 ordered pairs align at
probability **74.2–100.0**.

## E2 · A reimplementation of `hhmake`'s match-state numbering produced a spurious negative

To test whether each family's catalytic dyad maps onto another family's, the first version
recomputed which MSA columns become HMM match states by reapplying the `-M 50` gap rule. That
numbering did not agree with `hhmake`'s, and the result was **0 of 42 pairs corresponding** —
i.e. *the catalytic aspartate dyad does not correspond across RT families*, which is
biologically implausible for the most conserved feature in all RTs.

Inspecting the raw alignment showed the dyads plainly aligned:

    Q Consensus (GII)      259  ~~~~~~~~~~~kvn~VRYADDFiiTG~Sk
    T Consensus (Retrons)  179  --------~~~g~tYTRYADDLTFSs~~~
                                              ^^^^  YADD on YADD

**Fix:** `scripts/g4a_dyad_check.py` reads the correspondence **directly from the alignment text**
and reimplements nothing. Result: **42 of 42 ordered pairs `DYAD_CORRESPONDS` at offset 0.**

**Rule adopted:** do not reimplement a tool's internal coordinate system in order to interrogate
its output. Read the output.

## E3 · The transitivity table inherited E2's broken mapping and was all zeros

`g4a_transitivity.tsv` initially reported **0.0% transitive consistency for every triple**, from
the same faulty match-state map.

**Fix:** recomputed in `scripts/g4a_intersection.py` from the aligned consensus strings, in
consensus-index coordinates. Result: **210 testable triples, mean 88.2% consistent within ±2
positions, 174 of 210 (83%) at or above 80%.**

## E4 · MAFFT `--thread 4` is non-deterministic — caught by the repaired harness

The repaired `verify.sh` detected drift on re-running: identical input, different alignment column
counts (Retrons 1237 → 1192; CRISPR 1424 → 1378). MUSCLE column counts were identical across
runs, so the non-determinism is MAFFT's parallel path, not the pipeline's.

**Conclusions were stable across the two runs** — dyad 42/42 both times, `pct_global` moved by at
most 2.3 points, minimum hhalign probability 75.2 vs 78.8 — but the tables were **not
byte-reproducible**.

**Fix:** MAFFT pinned to `--thread 1`. The bundle now reproduces byte-identically:
`verify.sh` → *"OK: every landed table reproduced byte-identically from registered inputs."*

**This is the defect the previous bundle's harness could not have found**, because it `tee`d the
reproduction over the expected output instead of diffing against it.

## What did not change

`g4a_family_selection.tsv` and `g4a_sequence_roles.tsv` reproduced identically at every stage —
cd-hit clustering and the cluster-holdout role assignment were deterministic throughout, so the
predeclared design was never at risk from any of the above.
