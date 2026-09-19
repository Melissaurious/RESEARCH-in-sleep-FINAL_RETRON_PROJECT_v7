# Stage 3A — transfer readiness

**Not ready. Nothing to transfer.** No fingers/palm/thumb label was frozen, so the transfer-machinery
audit is carried forward unchanged from `analysis/prior_asset_audit/` and re-confirmed only where
this session touched a tool directly.

| tool | state after this session | condition before any reuse for transfer |
|---|---|---|
| **foldseek** | **PINNED and rerun**: `10.941cd33`, sha256 `ce5f08d8…`, 62×62 all-vs-all, command recorded | usable now; the unversioned build stays `DO-NOT-USE` |
| **FoldMason** | `4.dd3c235` installed; historical MSAs have logged version and command | usable as a tool; historical MSAs are input sets, not labels |
| **HHblits / HHsearch** | untouched this session | the historical database was built from **single-sequence A3Ms**; depth-1 profiles are **not** evolutionary profiles and their probabilities must not be read as profile–profile support. Any rebuild must document how genuine homologous alignments are constructed |
| **subdomain HMM construction** | untouched | `build_subdomain_hmms(2).sh` builds no HMMs — it is a SLURM submitter. The real per-domain HMM work is in `filter_rt_completeness_v4_v2.py`, which is present locally and was never audited |
| **`annotate_rt_domains_v5_.py`** | untouched | transfers boundaries by best-hit similarity from a reference DB that **mixes 164 predicted models with 7 crystal structures**. It must not inherit the old boundaries, and that mixing must not be reproduced |
| **mkdssp** | **BROKEN here**; replaced by a validated implementation | fix or keep the replacement, and carry its 0.701 strand recall as a stated limitation |
| **predicted structures** | untouched | out of scope until an experimental definition passes a validation gate; the 42 over-length truncations and the span→parent offsets remain open |
