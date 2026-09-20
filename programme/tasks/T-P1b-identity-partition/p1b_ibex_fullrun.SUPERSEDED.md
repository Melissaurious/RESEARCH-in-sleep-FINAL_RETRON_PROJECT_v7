# Superseded — the full run does not go to Ibex

An Ibex staging/submission script was drafted for the full 501,561-sequence run and then
**withdrawn before it was ever used**, because it could not have worked.

**The frozen implementation cannot run on Ibex.** `p1b_identity_partition.py` takes only
`--mode`, `--out`, `--fixtures` and `--threads`, and hardcodes six local absolute paths that do not
exist there: the catalogue, the exact-pair parquet, `g3_topology_components.tsv`, the family
baseline, the project root, and the local `mmseqs` binary.

Adding a path override would **edit a frozen artefact after its pilot validated it**, which
`WORKING_RULES` §6b exists to prevent.

**Use `p1b_fullrun.sh` instead** — it runs the frozen implementation locally, unmodified. Its header
records the reasoning, and `TASK_LAUNCHER.md`'s `preferred_backend: ibex (full)` is superseded by
it. That is an **execution-routing** change; no criterion, threshold, control or population is
touched.

If Ibex is ever genuinely required, the correct route is **a new task ID** whose implementation
takes path arguments, frozen and re-piloted on its own terms — not a patch to this one.
