# Z6 de novo experiment — DESIGN (frozen before any outcome; hashes in `tables/FREEZE.tsv`)

Exploratory, not a gate. Supersedes the population of the first SPIRE benchmark (`../BENCHMARK_DESIGN.md`),
whose negative result on the released SPIRE rule stands and is **not** re-tested here.

## 0 · Question (operator, 2026-09-18)

> Among high-confidence retron loci for which the established ncRNA resource produced no call despite
> adequate genomic context, can comparative de novo RNA motif discovery identify reproducible structured
> RNA candidates associated with homologous RT groups?

First, as its positive control: can the same procedure localise a **hidden** known ncRNA in matched loci?

Not in scope: RT discovery or classification, PADLOC, rerunning production CMs, Mestre reproduction,
scaling SPIRE `07`.

## 1 · Canonical population

Z6 = `ARIS_OUTPUT/dbchar_workbench/tables/Z6_locus_matched_status.parquet` in the `dbchar-workbench`
worktree, produced at commit **`12ea561a5565aca29eeaacbfe8863dc244838fa3`**, sha256 `92dc8f2a…`.
All five checks reproduced here: 630,741 loci · 332,769 with a call · 297,972
`NO_NCRNA_CALL_IN_RETAINED_WINDOW` · 76,381 exact RTs · 28,838 exact RTs with a matched locus.
No population is reconstructed. Z6 is joined to registered tables only for: tool evidence
(`rt_tool_calls_v1`, by `locus_key`), taxonomy above species (`rt_records_v1`, by `record_key_any`),
and — **after predictions are frozen** — reference ncRNA coordinates (`rt_ncrna_pairs_v1`).

## 2 · Units (never merged)

| unit | key | use |
|---|---|---|
| locus | `locus_key` | genomic occurrence, context, match status |
| exact RT | `rt_seq_hash` | protein identity; repeated loci of one exact RT are **one** observation |
| RT homolog group | RT50 cluster (mmseqs ≥ 50 % id, ≥ 80 % cov; `../scripts/s02`) | comparative discovery unit |
| near-identical RT | RT90 cluster | de-duplication inside a group: **at most one locus per RT90** in any alignment |

## 3 · Context (declared per method)

Discovery window **W = RT-relative −600…+100** (700 nt, RT strand; position 0 = first base of the start
codon). It covers the matched-ncRNA positions (T2/T3 gap ≤ 200 bp; central 50 % of T3 references about −166…−32)
with margin; includes msr/msd that overlap the RT start; and leaves a background 3–5× the ncRNA length, so
*localisation* is a real test. The earlier 300-nt window made region overlap nearly automatic.

| context class | rule (Z6 fields) |
|---|---|
| `ADEQUATE` | `bp_available_upstream` ≥ 1000, `rt_in_window`, `window_len_consistent`, not `window_inverted`, `rt_seq_wellformed` |
| `LIMITED_LT200` / `LIMITED_200_1000` | `bp_available_upstream` < 200 / 200–999 — separate unresolved strata, never discovery evidence |

`any_window_clipped` is carried as a covariate, not a filter: W depends only on upstream availability.

## 4 · Locus classes

| class | rule |
|---|---|
| `MATCHED_LOCAL` | `evidence_tier` ∈ {T3, T2} (reference inside or at W) |
| `MATCHED_T1` | `T1_OBSERVED` — reference usually > 200 bp away; kept, not used as a rediscovery target |
| `UNMATCHED_ADEQUATE` | `NO_NCRNA_CALL_IN_RETAINED_WINDOW` and `ADEQUATE` |
| `UNMATCHED_LIMITED_*` | unmatched with limited context |

System evidence per locus (from each tool's rule file, see `../README.md`): S1 both tools with a
multi-gene rule · S2 one tool · S3 fused-RT rule only · **S4 PADLOC rule that needs the ncRNA —
excluded** · S5 sequence only. "High-confidence" = S1/S2. S3 is a separate stratum. PADLOC-labelled
XII (rule *prohibits* an ncRNA) is flagged.

## 5 · Homolog-group table (`tables/GROUPS.tsv`)

Per RT50 group: loci · exact RTs · RT90 clusters · genomes · species (within one taxonomy system) ·
genera · phyla · sources · matched-local / matched-T1 / unmatched-adequate / unmatched-limited loci
and the RT90 count behind each · CM models seen · type labels · redundancy (loci per RT90) · flags:

- `POS_FEASIBLE`: ≥ 6 RT90 among `MATCHED_LOCAL` + `ADEQUATE` + S1–S3 loci
- `MIXED`: ≥ 4 RT90 matched-local-adequate **and** ≥ 4 RT90 unmatched-adequate (S1/S2)
- `DENOVO_FEASIBLE`: no matched locus of any tier, ≥ 6 RT90 among unmatched-adequate S1/S2 (S3 separately)

## 6 · Bounded benchmark (selection by `sha256("z6-denovo-v1|"+key)` order; no outcome used)

| cohort | groups | members per set |
|---|---|---|
| `POS_BLIND` | ≤ 10 `POS_FEASIBLE` groups, at most one per type label, then one per dominant CM model until 10 | ≤ 16 matched-local adequate loci, one per RT90 |
| `MIXED` | ≤ 6 `MIXED` groups, round-robin over type labels | ≤ 8 matched + ≤ 8 unmatched adequate, one per RT90, **status hidden from every method** |
| `DENOVO_S12` | ≤ 5 `DENOVO_FEASIBLE` S1/S2 groups, round-robin over type labels | ≤ 16 unmatched adequate |
| `DENOVO_S3` | ≤ 3 such groups from S3 | ≤ 16 |
| `CTRL_DISTAL` | every set above | same loci, window −1900…−1201 (700 nt); loci lacking it dropped |

Identical windows are removed. A set needs ≥ 6 members.

## 7 · Methods (identical sets and windows; global parameters, nothing tuned per set)

| arm | discovery | structure / covariation |
|---|---|---|
| `CMF` | CMfinder 0.4.1.9 `cmfinder04.pl` defaults (local motif discovery); top-ranked motif = candidate, all motifs kept | R-scape `-E 0.05` and `--cacofold` on the motif alignment |
| `MLOC` | mLocARNA 2.0.1, SPIRE flags (global) | R-scape `--cacofold -E 0.05`; region = union of helices with ≥ 1 covarying pair |
| `QINSI` | MAFFT Q-INS-i 7.525 (`mafft-qinsi`) | as MLOC |

## 8 · Candidate rule (set level) — all must hold

1. **Localised:** a motif/region with a member span in ≥ 50 % of members.
2. **Positionally consistent:** SD of member-span centres (RT-relative) ≤ 50 nt.
3. **Covariation with power:** ≥ 2 significantly covarying pairs (E < 0.05) on the motif/region
   alignment, and expected covarying pairs ≥ 1 (not `LOW_POWER`).
4. **Survives the matched control:** the same arm on the set's `CTRL_DISTAL` windows does not pass 1–3.

Set-level outcome: `CANDIDATE` · `SIGNAL_FAILS_CONTROL` · `NOT_LOCALISED` · `NO_COVARIATION` ·
`LOW_POWER` · `RUN_FAILED`.

## 9 · Evaluation (references revealed after `tables/PREDICTIONS_FROZEN.tsv`)

Matched members of `POS_BLIND` and `MIXED`: best registered placement at that locus (T3 > T2, lowest E),
in RT-relative coordinates. Per member: overlap, IoU, Dice, 5′/3′ error, length error, reference
contained. Categories as before (`existing pair rediscovered` IoU ≥ 0.5 · `…altered boundary` ·
`…not rediscovered` · `method abstention` · `system unsuitable for this method`). Detection, region
and boundary levels are reported separately. Chance yardstick: same-length intervals placed
uniformly in W.

`MIXED` additionally: for sets whose candidate rediscovers the matched members' ncRNA, the unmatched
members' spans at the same alignment columns are **family-expansion candidates**
(`new candidate in previously ncRNA-unresolved system`), with their RT-relative offset from the
matched members' reference positions.

`DENOVO` candidates: CM-seeding test — `cmbuild` on the motif alignment (experimental, never merged
with production CMs), `cmsearch -T 20 --nohmmonly` on W and distal windows of up to 40 **held-out**
loci of the same group (one per RT90, not in the set). Report the held-out hit rate in W vs distal,
and positional agreement (hit centre within ±50 nt of the set median).

## 10 · Bounds

≤ 30 sets × 3 arms + controls, all local. No run over all unresolved loci, no production-CM
rescan, no scaling across groups.

## Amendment 1 — 2026-09-18, before any benchmark set was run (only one control set and a tool check had run)

1. **"Top-ranked CMfinder motif" made operational.** `cmfinder04.pl` writes no global ranking. Top motif =
   highest sum of member `#=GS … DE` scores; ties → more members. Every motif is still recorded, and
   "any motif passes §8" is reported beside "top motif passes".
2. **Tool positive control recorded.** On 12 registered TypeIIA3_proteo ncRNA sequences (tool check only,
   not benchmark windows) CMfinder returned 6 motifs; on `CTRL_POS_04_I-C` distal windows, 0 motifs
   (all EM runs: "failed to find acceptable structure prediction"). An empty CMfinder result is therefore
   an outcome, not a broken install.
3. **CMfinder defaults cap candidates at 100 nt** (`-M 100`), shorter than most retron ncRNAs. Kept, per the
   freeze. A CMfinder hit is judged at the *region* level; boundary metrics for CMF describe the motif
   (for example one stem-loop), not the whole ncRNA.
