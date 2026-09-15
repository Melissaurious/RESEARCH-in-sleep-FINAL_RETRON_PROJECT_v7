# Retro — dbchar_g4_family_baseline (2026-09-15)

Bundle: `results/dbchar_g4_family_baseline/` — REPRODUCIBLE, human_input_audit PENDING.
23 tables, 2 figures, rerun 116.8 s.

## What happened

- Per-family RT and ncRNA baselines on exact-sequence views (V-RT-SINGLE 493,956 · V-RT-MULTI
  7,593 · V-RT-CROSS 12). 36 of the prior project's 44 family length baselines reproduce exactly.
- The **MULTI basis was investigated from the underlying evidence**, as the operator required, not
  from the filename: every MULTI protein was scored against the myRT `RVT-All.hmm` library (45
  profiles). The best-scoring family is among the record's own labels for 99.91% of MULTI
  proteins, and the best-vs-second margin is a median **5.0 bits** against **81.7 bits** in a
  control whose best hit matches the known single label 98.10% of the time. MULTI is an
  **ambiguity stratum**, not mislabelling — and Stage 1 does not resolve it.
- The caveat is landed with the finding: MULTI proteins are also shorter, and bit score scales
  with length, so part of the tie may be a length effect.

## What went wrong

- **The profile→family regex failed** on `RVT-GII-I`, `RVT-GII-II` and `RVT-Retrons`, and the
  positive control read 33%. Replaced with an explicit *declared* mapping
  (`PROFILE_TO_FAMILY`, `PROFILE_PREFIX`) rather than a cleverer regex; the control then read
  98.1%. A pattern that infers a label from a name is a guess wearing a function's clothes.
- **The awk second count was silently corrupted**: `xargs -P` workers wrote to one pipe and
  interleaved *inside* lines longer than the 4 KB pipe buffer. The output looked like data. Fixed
  with per-worker output files. This is the failure mode that would not have announced itself.
- **A per-label count was off by 5** — the producing script applied the first-copy filter, the awk
  route counted all lines. The comparison table is now computed over all records on both sides.

## Proposal (not an amendment — WA-S.2)

**No parallel second-count route may write to a shared stream.** A `... | xargs -P N cmd >> out`
pattern is unsafe for any line that can exceed `PIPE_BUF` (4096 bytes on Linux), and the corruption
is silent and data-shaped. Second-count scripts should write one file per worker and concatenate.
- *Would have caught:* this gate's first awk route, whose interleaved output was read as real
  counts until the totals refused to reconcile.
- *Would wrongly reject:* a parallel route whose every output line is provably short — which is
  most of them, so the rule costs a concatenation step it does not strictly need.

## Carried into later gates

`PROFILE_TO_FAMILY` is the declared mapping any later HMM work must reuse or supersede by record;
the MULTI tie evidence is registered as `multi_hmm_evidence_v1.parquet`.
