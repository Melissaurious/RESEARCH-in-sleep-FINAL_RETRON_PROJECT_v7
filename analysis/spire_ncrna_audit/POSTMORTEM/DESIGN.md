# SPIRE post-mortem — what conserved element does CMfinder detect? (declared before any post-mortem run)

`ROUND2_FAIL_STOP` is final (Round 2 commit `14f19ae20665f8db0a6db8f771e0247901c99af5`). This is a bounded,
**descriptive** analysis. It does not reopen discovery, seed or build CMs, or scale anything. Conservation is never
read as function.

Instrument: the **frozen Round-2 rule unchanged** (`../ROUND2/FROZEN_RULE.json`: CMfinder span 260, W500 −400…+100,
R_B ranking, coverage ≥ 0.5, centre SD ≤ 50, coding_frac ≤ 0.5, not `POWERED_ABSENT`). Cross-class comparisons use
**rule pass** (no half-split requirement), because non-retron panel groups get no halves; the retron reference rate is
recomputed the same way from the existing Round-2 runs (DEV + HELDOUT, no new retron runs).

## 1 · Motif characterisation (retron, existing Round-2 runs; DEV + HELDOUT real sets passing the rule)

Per member instance, RT-relative: start, end, centre, distance to RT start (0) and RT end; strand (= RT strand by
construction); non-RT CDS overlap; RT-ORF overlap (0…+100); overlap with the RT's Prodigal RBS region (−20…−1, and
whether the RT record carries an RBS motif); overlap with any registered ncRNA call in the record (all corpus ncRNA
annotations are production-CM calls); overlap with the locus's own reference ncRNA; instance length, consensus base
pairs, covariation state, set-level centre SD.

## 2 · Specificity panel (small, prospective)

RT classes (catalogue `file_label`): RVT-GII, RVT-DGRs, RVT-CRISPR, RVT-CRISPR-like, RVT-AbiK, RVT-AbiP2, RVT-AbiA,
RVT-UG2, RVT-UG3, RVT-UG5, RVT-UG8 (the four UG families with most exact RTs among those with > 30,000 loci).
Per class: first 6,000 eligible physical loci in `sha256("pm-panel|"+physical_locus_key)` order → RT50 / RT90
clustering of those exact RTs → homolog groups with ≥ 6 RT90 members that have ≥ 1,900 bp upstream → **≤ 8 groups
per class** in hash order, ≤ 20 members, one locus per RT90, no identical windows. The same member rules as the retron
sets (depth, redundancy control, window length, upstream availability). Each group gets its W500 real window and its
paired distal control (−1500…−1001). GC content per set is recorded and compared with the retron sets (matched by
report, not by resampling). Total ≤ 88 groups × 2 runs.

Reported: rule-pass rate by class, per independent homolog group, real vs distal, with the retron reference.

## 3 · Type III-A

For III-A groups (DEV + HELDOUT) whose real set passes the rule: motif position vs the reference ncRNA; overlap with
other registered ncRNA calls; CDS overlap and the identity (strand, position) of any overlapping gene; position in the
RBS / 5′-UTR region; **repeat test** — blastn of each motif instance against its own 20-kb record window
(> 1 hit at ≥ 85 % identity over ≥ 80 % of the instance = repeated in context). Outcome per group, one of:
`OTHER_ANNOTATED_NCRNA` · `LEADER_UTR_OR_RBS_REGION` · `NEIGHBOURING_CDS` · `REPEAT_ELEMENT` · `UNRESOLVED_CONSERVED_ELEMENT`.

## 4 · Positional baseline

HELDOUT, using DEV-derived priors only: (a) the global interval −193…−24; (b) per-type median intervals (DEV);
(c) the method; (d) how many method rediscoveries fall inside P0 anyway; (e) reference-position spread (SD of
start/end), overall and per type. Descriptive input for a future supervised boundary project; nothing is fitted
to HELDOUT.

## 5 · Closing label

One of `GENERAL_RT_NEIGHBOURHOOD_MOTIF` · `RETRON_ENRICHED_BUT_NOT_NCRNA_SPECIFIC` · `UNRESOLVED_CONSERVED_ELEMENT`
or another neutral label the evidence supports. Decision rule, declared now: retron rule-pass rate vs the pooled
panel rate over independent groups (two-sided Fisher). If not significantly different at 0.05 →
`GENERAL_RT_NEIGHBOURHOOD_MOTIF`. If retron is significantly higher but the motif rarely corresponds to the reference
ncRNA (§4) → `RETRON_ENRICHED_BUT_NOT_NCRNA_SPECIFIC`. Class-level heterogeneity is reported either way.
The 977-set provenance stays open; if it is found, the already-hashed Round-1 / Round-2 predictions are scored
without rerunning them.
