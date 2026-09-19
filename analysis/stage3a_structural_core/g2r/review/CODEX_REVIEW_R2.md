# Codex independent review — round 2 (amendment 1 @ 4aeb2181)

* Thread `01a0b9a6-a790-7ec0-9434-ca94a39aa69f`, read-only. No RT, benchmark or SS outcome existed or was shown.
* **Verdict: FIX_FIRST (B1–B8).** Response: `G2R_AMENDMENT_2.md`. Links are absolute paths as returned.

Verbatim:

---

No files were modified, and no prohibited source was opened. Commit `4aeb2181ee1a9a52834fce23a936dc6867f05848` exists and the reviewed files are unchanged from it.

The R1 response is substantial, but several executable defects remain blocking.

## F1–F7 status

| Fix | Status | Assessment |
|---|---|---|
| F1 — PDP instrument | **PARTIALLY RESOLVED** | The primary instrument is now correctly scoped as unmodified BioJava 7.1.4, defects are disclosed, complete source is supplied, and BJ-p4 cannot rescue the primary. However, a parser exception currently aborts the entire batch instead of counting that chain as an instrument failure. |
| F2 — mapping/preflight | **PARTIALLY RESOLVED** | RunPDP’s zero-based inclusive expansion, single-model/single-chain checks, exact residue keys, and canonical CA merge are correct. The CATH missing-endpoint fallback still mishandles insertion-code ordering. |
| F3 — provenance | **RESOLVED** | The method is no longer overclaimed as published-PDP-equivalent; split/merge exponents, contact enhancements, virtual Cβ, nonuniform sequence-separation filtering, provider effects, and validation interpretation are accurately disclosed. |
| F4 — anti-circularity | **RESOLVED**, with disclosed limitation | `5HHJ_A` is designated design-exposed, the historical SS exposure is candidly recorded, flag provenance is objective, and `g2r_units.py` actually subsets the register to the allowlisted columns. I found no forbidden-input route in the reviewed code. |
| F5 — CATH validation | **PARTIALLY RESOLVED** | Deterministic deduplication, shortfall handling, structural screening, discontinuous cases, Hungarian scoring, and failure accounting are implemented. E1 is mathematically wrong for one-domain discontinuous chains, and endpoint fallback is not insertion-code-safe. |
| F6 — SS validation | **PARTIALLY RESOLVED** | Route B exists, H is gated, coverage and undefined values are recorded, and route-A element construction is explicit. The pydssp route is not fully break-aware, and the concordance gate has cohort/coverage edge-case loopholes. |
| F7 — C4–C7/verdict | **PARTIALLY RESOLVED** | Most definitions are now executable and abstention is included in call-rate denominators. Remaining blockers are stage-verdict enforcement, pinned-alignment enforcement, and small but outcome-relevant sheet/hairpin rule divergences. |

## BLOCKING — must fix before running

### B1. A single PDP exception aborts the whole benchmark

[RunPDP.java:22](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis/stage3a_structural_core/g2r/scripts/RunPDP.java:22) catches exceptions only around the entire invocation. An exception from one chain—plausible given the disclosed `CutDomain` defect—stops all subsequent chains. [pdp_run.py:21](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis/stage3a_structural_core/g2r/scripts/pdp_run.py:21) then aborts instead of allowing that chain to count as failed validation.

Catch parser/output exceptions per input, emit `PARSER_FAIL`, produce no assignment for that chain, and let CATH scoring assign count failure and overlap zero.

### B2. E1 conflates discontinuity with multidomain structure

[cath_score.py:120](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis/stage3a_structural_core/g2r/scripts/cath_score.py:120) requires every chain containing a discontinuous CATH domain to be parsed into at least two PDP domains.

A discontinuous domain is one domain made of multiple segments. A correct parse of a one-domain/discontinuous chain can therefore have `n_pdp=1`, which E1 currently marks wrong. E1 must either be conditioned on discontinuous chains whose CATH count is at least two, or measure count agreement rather than universally requiring `n_pdp≥2`. This correction does not require changing its numerical bar.

### B3. CATH endpoint fallback ignores insertion-code order

When an endpoint is absent, [cath_score.py:59](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis/stage3a_structural_core/g2r/scripts/cath_score.py:59) and [line 65](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis/stage3a_structural_core/g2r/scripts/cath_score.py:65) compare only numeric sequence numbers.

For an absent boundary such as `100B`, this can select `100`, `100A`, or another insertion on the wrong side. The fallback must use a frozen total ordering over `(seqnum, insertion code)` consistent with the ordered coordinate list. Log and fail segments whose resolved start follows their resolved end.

### B4. The pydssp donor mask does not fully enforce chain breaks

[ss_routes.py:95](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis/stage3a_structural_core/g2r/scripts/ss_routes.py:95) removes incomplete-backbone residues and passes the remaining coordinates as one compact array. The mask disables donation only for the first residue after a break.

pydssp still computes:

- local-neighbor masks from compact-array offsets;
- 3/4/5-turn helices from compact-array diagonals;
- bridge neighborhoods from compact-array adjacency.

Consequently, later residues after a break can participate in turns spanning the missing residue or chain break, while residues across a break are also incorrectly treated as local sequence neighbors. Route B needs break-aware turn/bridge handling, not only hydrogen-donor masking.

### B5. SS-gate cohort and low-coverage failure are not fully controlled

[ss_concordance.py:34](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis/stage3a_structural_core/g2r/scripts/ss_concordance.py:34) accepts an arbitrary positional chain list. It does not reject omissions, duplicates, or a cohort different from the frozen 62 chains. That can change medians silently.

Additionally:

- `stats()` divides by zero if a chain has no common assignments.
- If many chains fail the 0.95 chain-coverage gate, population E/H medians can nevertheless pass because population reliability has no coverage or chain-gate requirement. Those chains then count as biological non-calls, potentially producing `FAIL` rather than `INSTRUMENT_LIMITED`.
- Both-all-positive assignments also produce undefined κ in code, contrary to the text saying undefined κ occurs only for concordant-empty chains.

The exact frozen cohort must be asserted, zero-common chains must fail safely, and the population instrument rule must address widespread coverage/chain-gate failure before results exist.

### B6. The implemented verdict ignores instrument failure

Although [g2r_units.py:61](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis/stage3a_structural_core/g2r/scripts/g2r_units.py:61) reads the population SS gate, [verdict()](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis/stage3a_structural_core/g2r/scripts/g2r_units.py:251) can return only `PASS`, `PARTIAL`, or `FAIL`. If the SS gate fails, the report therefore emits `FAIL`, contrary to Amendment §5’s `INSTRUMENT_LIMITED`.

The script also receives no CATH-gate result and cannot enforce C3r failure. Order-of-operations discipline is not enough because the report calls its output a verdict. Pass both gate statuses into the verdict implementation and explicitly emit `INSTRUMENT_LIMITED`.

### B7. The pinned Foldseek equivalence check does not enforce equivalence

[g2r_ava.py:24](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis/stage3a_structural_core/g2r/scripts/g2r_ava.py:24) only prints how many alignments match the pinned table. It still writes and permits downstream use of a differing result.

Require identical key sets, row counts, starts/ends, and alignment strings; abort on any mismatch. Otherwise C6/C7 can silently use a non-pinned alignment set.

### B8. Two C4/C4b decisions are not fully specified by the amendment

- [sheet_of()](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis/stage3a_structural_core/g2r/scripts/g2r_units.py:98) uses `Counter.most_common(1)`. Equal sheet-label counts are resolved by first occurrence, whereas the amendment specifies a majority but gives no tie rule.
- The hairpin bridge test at [g2r_units.py:119](/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis/stage3a_structural_core/g2r/scripts/g2r_units.py:119) checks only whether a residue in the earlier strand names a partner in the later strand. The amendment says a partner “of one” lies in the other, which is bidirectional.

Freeze a sheet-label tie rule and either check bridge pointers in both directions or amend the text to the narrower one-direction rule.

## NON-BLOCKING — record and proceed after B1–B8

- The complete BioJava source confirms that the initial segment is `[0, ca.length−1]`, split/merge precedes `ShortSegmentRemover`, and returned segments use inclusive atom-array indices. The rewritten mapping is consistent with that.
- `ShortSegmentRemover` removes a domain when total length is below 35 or every constituent segment is below 30. This behavior should be added to the method description, but it is pinned library behavior.
- The reported “PDP discontinuous domain” statistic can classify an otherwise contiguous returned atom-index segment as discontinuous when a canonical CA residue is `PDP_ABSENT`. It is secondary and should be labeled accordingly.
- C6 recurrence remains conditional on both chains having calls; absent Y calls are reported but excluded from recurrence. Because prevalence is separately tested with an all-chain denominator, this is now an explicit estimand rather than a hidden abstention path, though it may yield optimistic conditional recurrence.
- C7 would benefit from reporting shared-residue coverage. Its current exact common-universe calculation and minimum five-group rule are otherwise coherent.
- `--exposed 5HHJ_A` is optional at the command line. Archive the exact invocation or assert the frozen exposure set so accidental omission cannot alter the primary population.
- The BJ-p4 compiled classes and build command should be hashed and logged. This does not affect the primary-instrument verdict.
- Foldseek mapping in `g2r_units.py` correctly treats `qstart/tstart` as one-based and increments indices only on nongap characters. Adding end-position assertions would improve fault detection.
- No motif, catalytic, Stage 3B, historical-boundary, RT0–RT7, or lineage/family input is read by the reviewed analysis code.

OVERALL: FIX_FIRST (B1 per-chain PDP failure handling; B2 E1 definition; B3 insertion-aware CATH fallback; B4 break-aware pydssp; B5 SS cohort/coverage gate; B6 instrument-limited verdict; B7 pinned-alignment assertion; B8 sheet/hairpin tie rules).