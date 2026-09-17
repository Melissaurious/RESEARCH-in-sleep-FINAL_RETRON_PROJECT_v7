md(r"""
---

# L. Resolved questions from the thesis draft

Each subsection answers one `\todo` from the written report, with the query that answers it.
Where the answer is a decision rather than a measurement, that is said explicitly.
""")

code(r'''
# L1 — Why are 16,688 records "sequence only"? Metagenomic assembly, gene calling, or quality?
L1 = cache("L1_sequence_only_by_database", """
    WITH base AS (SELECT source_database, count(*) AS n_all FROM rt_records WHERE is_first_copy GROUP BY 1),
         rec  AS (SELECT r.source_database, v.representation_class, count(*) AS n
                  FROM rt_cds_recovery v JOIN rt_records r USING (record_key)
                  WHERE v.recovery_state = 'SEQUENCE_ONLY' GROUP BY 1, 2)
    SELECT rec.source_database, rec.representation_class, rec.n, base.n_all,
           round(100.0 * rec.n / base.n_all, 4) AS pct_of_that_database
    FROM rec JOIN base USING (source_database) ORDER BY rec.n DESC
""")
display(L1)
iso = L1[L1.source_database.str.startswith(("ncbi", "gtdb"))].n.sum()
print(f"\n  SEQUENCE_ONLY records from ISOLATE databases (ncbi_*, gtdb_*): {iso}")
print(f"  SEQUENCE_ONLY records from METAGENOMIC databases (mgnify_*, gem): {L1.n.sum() - iso:,}")
print("  -> the sequence-only category is ENTIRELY a metagenomic-assembly phenomenon.")

# L2 — which 12 proteins are cross-label?
L2 = cache("L2_cross_label_proteins", """
    SELECT e.rt_seq_hash, e.family_label_set, e.rt_aa_len, e.n_records, e.n_loci, e.n_genomes
    FROM rt_exact e JOIN rt_family_baseline f USING (rt_seq_hash)
    WHERE f.view = 'V-RT-CROSS' ORDER BY e.n_records DESC
""")
display(L2.assign(rt_seq_hash=L2.rt_seq_hash.str.slice(0, 12) + "…"))
print(f"  all {len(L2)} carry the SAME label pair: {sorted(set(L2.family_label_set))}")

# L3 — Prodigal partial flags
L3 = cache("L3_prodigal_partial_flags", """
    SELECT coalesce(nullif(rtcds_partial, ''), '(no RT CDS)') AS rtcds_partial,
           count(*) AS n_records,
           round(100.0 * count(*) / sum(count(*)) OVER (), 3) AS pct
    FROM rt_records WHERE is_first_copy GROUP BY 1 ORDER BY n_records DESC
""")
L3["meaning"] = L3.rtcds_partial.map({
    "00": "complete at both ends (a true ORF: start codon and stop codon both found)",
    "10": "5' end partial — the gene runs off the left edge of the contig",
    "01": "3' end partial — the gene runs off the right edge of the contig",
    "11": "partial at both ends — the contig is shorter than the gene",
    "(no RT CDS)": "no annotated RT CDS on the record (the g2b recovery population)"})
display(L3)
''')

md(r"""
**L1 — the sequence-only category is metagenomic assembly fragmentation.** All 16,688
`SEQUENCE_ONLY` records come from metagenome-derived databases (`mgnify_human_gut` 15,364,
`mgnify_marine` 766, `mgnify_soil` 533, `gem` 25) and **none** from isolate databases
(`ncbi_*`, `gtdb_*`). Within `mgnify_human_gut` they are **10.81 %** of records. The mechanism is
therefore short, fragmented MAG contigs on which the RT runs past the contig edge — not a gene-call
disagreement and not a genome-quality filter. The three representation classes (RT beyond the
contig, RT crossing a contig end, inverted window) are all consistent with that single cause.

**L2 — the 12 cross-label proteins are one family boundary, not scattered ambiguity.** Every one
carries the label set `RVT-CRISPR | RVT-CRISPR-like` — two adjacent labels in the myRT library. This
is a statement about where two profiles overlap, not about 12 unrelated confusions.

**L3 — Prodigal partial flags.** The two digits are the 5′ and 3′ ends of the called gene; `0` means
the end was found, `1` means the gene ran off the contig. `00` = complete (88.19 % of distinct
records), `10` = 5′ partial (4.79 %), `01` = 3′ partial (4.31 %), `11` = both (1.68 %). The empty
value (1.03 %) is the no-RT-CDS population. Partiality is an **assembly** property, which is why a
missing flag is classed `no_completeness_evidence` and never "complete".
""")

code(r'''
# L4 — is the opposite-strand TypeXIIIA_firmi group one genome re-sequenced, or independent?
L4 = cache("L4_opposite_strand_independence", """
    SELECT detection_model,
           CASE WHEN same_strand THEN 'same strand' ELSE 'opposite strand' END AS stratum,
           count(*) AS n_placements, count(DISTINCT physical_locus_key) AS n_physical_loci,
           count(DISTINCT genome_id_norm) AS n_genomes, count(DISTINCT tax_species) AS n_species,
           count(DISTINCT source_database) AS n_databases,
           count(DISTINCT nc_seq_hash) AS n_exact_ncrna, count(DISTINCT rt_seq_hash) AS n_exact_rt,
           quantile_cont(signed_distance_bp, 0.50) AS median_bp
    FROM rt_ncrna_pairs WHERE canonical AND detection_model = 'TypeXIIIA_firmi'
    GROUP BY 1, 2 ORDER BY n_placements DESC
""")
display(L4)

# L5 — geometry of the non-Retron candidates, in bp
L5 = cache("L5_nonretron_distance", """
    SELECT direction, count(*) AS n_placements,
           quantile_cont(signed_distance_bp, 0.50) AS median_signed_bp,
           quantile_cont(abs(signed_distance_bp), 0.50) AS median_abs_bp,
           avg(signed_distance_bp) AS mean_signed_bp,
           count(DISTINCT genome_id_norm) AS n_genomes, count(DISTINCT nc_seq_hash) AS n_exact_ncrna
    FROM rt_ncrna_pairs WHERE geometry_eligible AND file_label NOT IN ('Retron', 'MULTI')
    GROUP BY 1 ORDER BY n_placements DESC
""")
display(L5.round(1))
ret_med = Q("""SELECT quantile_cont(signed_distance_bp, 0.50) AS m FROM rt_ncrna_pairs
               WHERE canonical AND file_label = 'Retron' AND direction = 'upstream'""").m[0]
print(f"\n  Retron upstream median: {ret_med:.0f} bp")
print(f"  non-Retron upstream median: {L5.loc[L5.direction=='upstream','median_signed_bp'].iloc[0]:.0f} bp"
      f"  -> {abs(L5.loc[L5.direction=='upstream','median_signed_bp'].iloc[0]/ret_med):.0f}x further away.")
''')

md(r"""
**L4 — the opposite-strand group is not re-sequencing of one genome.** Its 2,571 placements span
**1,324 physical loci, 1,322 genomes, 67 species and 2 databases**, so the pattern recurs across
independent assemblies. More informative still, the *same* covariance model produces two completely
different geometries: 1,576 **same-strand** placements at a median of **+64 bp** across 292 species,
and 2,571 **opposite-strand** placements at a median of **−4,750 bp** across 67 species. One model,
two populations, disjoint in both distance and taxonomic range.

That rules out the simplest artefact (database redundancy) but does **not** establish biology. The
remaining hypotheses — the CM matching a second, unrelated element at distance; or a genuine distant
antisense arrangement in a restricted clade — are distinguishable only by inspecting what those 142
ncRNA sequences are, which this characterization does not do.

**L5 — the non-Retron candidates are not retron-like in architecture.** Their upstream placements
sit at a median of **−1,801 bp** and their downstream placements at **+4,281 bp**, against the
Retron upstream median of **−55 bp** — roughly **33× further away**. A retron-CM hit 1.8 kb from a
non-Retron RT does not resemble a retron locus. The reasonable reading is chance CM hits in the
genomic neighbourhood, and the burden of proof for "divergent retron" is not met by proximity alone.
""")

code(r'''
# L6 — why do some RTs have many ncRNA partners (max 176) and some ncRNAs many RTs (max 705)?
L6a = cache("L6_partner_multiplicity_source", """
    WITH multi AS (SELECT rt_seq_hash FROM rt_ncrna_exact_pairs
                   GROUP BY 1 HAVING count(DISTINCT nc_seq_hash) > 1)
    SELECT n_distinct_ncrna_seq_at_locus, count(*) AS n_placements
    FROM rt_ncrna_pairs WHERE canonical AND rt_seq_hash IN (SELECT rt_seq_hash FROM multi)
    GROUP BY 1 ORDER BY 1
""")
display(L6a)
print("  -> multi-partner RTs almost always carry ONE distinct ncRNA sequence AT EACH LOCUS.")
print("     The multiplicity comes from the same protein sitting at many loci, not from")
print("     several ncRNA matches being stored against one locus.\n")

L6b = cache("L6_partner_length_spread", """
    WITH multi AS (SELECT rt_seq_hash FROM rt_ncrna_exact_pairs
                   GROUP BY 1 HAVING count(DISTINCT nc_seq_hash) > 1),
         spread AS (SELECT p.rt_seq_hash,
                           max(b.nc_seq_len) - min(b.nc_seq_len) AS len_spread
                    FROM rt_ncrna_exact_pairs p JOIN multi USING (rt_seq_hash)
                    JOIN ncrna_family_baseline b USING (nc_seq_hash) GROUP BY 1)
    SELECT CASE WHEN len_spread <= 5 THEN 'a. <=5 nt  (boundary jitter)'
                WHEN len_spread <= 20 THEN 'b. 6-20 nt'
                WHEN len_spread <= 50 THEN 'c. 21-50 nt'
                ELSE 'd. >50 nt  (genuinely different RNAs)' END AS partner_length_spread,
           count(*) AS n_exact_rt FROM spread GROUP BY 1 ORDER BY 1
""")
L6b["pct"] = (100 * L6b.n_exact_rt / L6b.n_exact_rt.sum()).round(2)
save(L6b, "L6_partner_length_spread")
display(L6b)

L6c = cache("L6_top_degree_ncrna", """
    WITH t AS (SELECT nc_seq_hash FROM rt_ncrna_exact_pairs
               GROUP BY 1 ORDER BY count(DISTINCT rt_seq_hash) DESC LIMIT 1)
    SELECT count(DISTINCT p.rt_seq_hash) AS n_rt_partners,
           count(DISTINCT r.tax_species) AS n_species, count(DISTINCT r.genome_id_norm) AS n_genomes,
           min(e.rt_aa_len) AS min_rt_aa, quantile_cont(e.rt_aa_len, 0.50) AS median_rt_aa,
           max(e.rt_aa_len) AS max_rt_aa
    FROM rt_ncrna_exact_pairs p JOIN t USING (nc_seq_hash)
    JOIN rt_exact e ON e.rt_seq_hash = p.rt_seq_hash
    JOIN rt_ncrna_pairs r ON r.rt_seq_hash = p.rt_seq_hash AND r.nc_seq_hash = p.nc_seq_hash
""")
display(L6c)
''')

md(r"""
**L6 — both ends of the multiplicity have prosaic explanations, and neither is "multiple matches
stored per locus".**

*Why one RT has many ncRNA partners.* For RTs with more than one partner, essentially every
placement occurs at a locus carrying **exactly one** distinct ncRNA sequence (237,965 placements at
1-sequence loci versus 376 at 2–3-sequence loci). The multiplicity is therefore not several
competing CM matches recorded against one locus — it is **the same exact RT protein occurring at
many loci whose ncRNA calls differ slightly**. Confirming that: for **659 of the 921 multi-partner
RTs (71.6 %)** the partners' lengths span **≤ 5 nt**, i.e. they are boundary variants of one RNA.
Only 110 RTs (12 %) have partners differing by more than 50 nt and can be said to carry genuinely
different RNAs. The 176-partner extreme is a near-continuous length ladder from 68 to 223 nt with 57
sequences at exactly 158 nt — textbook CM hit-boundary jitter.

*Why one ncRNA has many RT partners.* The 705-partner extreme spans **25,748 genomes but only 17
species**, and its RT partners range from **58 to 1,254 aa** (median 585). So it is the combination
of a hyper-sequenced species group and **RT length/truncation variants** each hashing to a distinct
`rt_seq_hash`. Exact-sequence identity is a very fine equivalence: a single residue difference or a
partial call creates a new node.

**Consequence for dataset construction.** Exact-sequence identity over-counts distinctness on both
sides. Before multiplicity is interpreted — and before any train/test split — ncRNAs should be
collapsed by sequence clustering (or by trimming to a common CM-defined boundary) and RTs by
clustering at a stated identity threshold. Splitting on un-clustered exact hashes would place
boundary variants of the same RNA in both train and test.
""")

code(r'''
# L7 — the operator's proposed rule: same strand + immediately upstream, built cumulatively
L7 = cache("L7_dataset_rule_cascade", """
    WITH p AS (SELECT * FROM rt_ncrna_pairs WHERE canonical)
    SELECT 1 AS step, 'canonical placements' AS rule, count(*) AS n_placements,
           count(DISTINCT (rt_seq_hash, nc_seq_hash)) AS n_exact_pairs,
           count(DISTINCT rt_seq_hash) AS n_exact_rt, count(DISTINCT nc_seq_hash) AS n_exact_ncrna,
           count(DISTINCT physical_locus_key) AS n_physical_loci FROM p
    UNION ALL SELECT 2, '+ Retron family only', count(*), count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           count(DISTINCT rt_seq_hash), count(DISTINCT nc_seq_hash), count(DISTINCT physical_locus_key)
      FROM p WHERE file_label = 'Retron'
    UNION ALL SELECT 3, '+ same strand', count(*), count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           count(DISTINCT rt_seq_hash), count(DISTINCT nc_seq_hash), count(DISTINCT physical_locus_key)
      FROM p WHERE file_label = 'Retron' AND same_strand
    UNION ALL SELECT 4, '+ upstream', count(*), count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           count(DISTINCT rt_seq_hash), count(DISTINCT nc_seq_hash), count(DISTINCT physical_locus_key)
      FROM p WHERE file_label = 'Retron' AND same_strand AND direction = 'upstream'
    UNION ALL SELECT 5, '+ no CDS between', count(*), count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           count(DISTINCT rt_seq_hash), count(DISTINCT nc_seq_hash), count(DISTINCT physical_locus_key)
      FROM p WHERE file_label = 'Retron' AND same_strand AND direction = 'upstream' AND n_cds_between = 0
    UNION ALL SELECT 6, '+ within 200 bp', count(*), count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           count(DISTINCT rt_seq_hash), count(DISTINCT nc_seq_hash), count(DISTINCT physical_locus_key)
      FROM p WHERE file_label = 'Retron' AND same_strand AND direction = 'upstream'
        AND n_cds_between = 0 AND abs(signed_distance_bp) <= 200
    UNION ALL SELECT 7, '+ not contig-start-clipped', count(*), count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           count(DISTINCT rt_seq_hash), count(DISTINCT nc_seq_hash), count(DISTINCT physical_locus_key)
      FROM p WHERE file_label = 'Retron' AND same_strand AND direction = 'upstream'
        AND n_cds_between = 0 AND abs(signed_distance_bp) <= 200 AND NOT true_start_clipped
    ORDER BY step
""", pop="PAIR-CANON")
L7["pairs_retained_pct"] = (100 * L7.n_exact_pairs / L7.n_exact_pairs.iloc[0]).round(2)
save(L7, "L7_dataset_rule_cascade")
display(L7)
print("""
  WHICH FUNNEL IS THIS?  The workbench contains three reductions over PAIR-CANON. They are not
  versions of each other and their step counts must never be mixed:

    L7 (here)  cumulative; step 4 keeps ONLY '+ upstream'            -> 26,293 pairs
    N8         cumulative; step 4 keeps 'upstream OR overlapping'    -> 29,440 pairs
    K2         each criterion applied ALONE, never cumulatively      -> 26,805 for 'upstream only'

  N8 is the one the thesis chapter uses, because overlapping placements are retained as a
  flagged class (97.36% of them overlap only the RT gene itself). L7 is the operator's stricter
  exercise; K2 is a one-at-a-time sensitivity. Cite the one whose rule you actually applied.""")

L7b = cache("L7_rule_recurrence", """
    WITH sel AS (SELECT DISTINCT rt_seq_hash, nc_seq_hash FROM rt_ncrna_pairs
                 WHERE canonical AND file_label = 'Retron' AND same_strand
                   AND direction = 'upstream' AND n_cds_between = 0
                   AND abs(signed_distance_bp) <= 200)
    SELECT r.recurrence_class, count(*) AS n_pairs
    FROM sel JOIN rt_ncrna_exact_pair_recurrence r USING (rt_seq_hash, nc_seq_hash)
    GROUP BY 1 ORDER BY n_pairs DESC
""")
L7b["pct"] = (100 * L7b.n_pairs / L7b.n_pairs.sum()).round(2)
save(L7b, "L7_rule_recurrence")
display(L7b)
IND = ["multiple_species", "one_species_multiple_genomes", "one_genome_multiple_loci"]
print(f"\n  independently recurrent pairs within the rule: "
      f"{int(L7b[L7b.recurrence_class.isin(IND)].n_pairs.sum()):,} of {int(L7b.n_pairs.sum()):,}")
''')

code(r'''
C7 = pd.read_csv(TABLES / "L7_dataset_rule_cascade.tsv", sep="\t").sort_values("step")
S6 = pd.read_csv(TABLES / "L6_partner_length_spread.tsv", sep="\t")

fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.0))
ax = axes[0]
y = np.arange(len(C7))[::-1]
ax.barh(y, C7.n_exact_pairs, color="#3b6ea5", height=0.62)
for yi, (n, p) in zip(y, C7[["n_exact_pairs", "pairs_retained_pct"]].itertuples(index=False)):
    ax.text(n + 400, yi, f"{n:,}  ({p:.0f}%)", va="center", fontsize=8)
ax.set_yticks(y); ax.set_yticklabels(C7.rule, fontsize=8)
ax.set_xlim(0, 36000); ax.set_xlabel("exact RT–ncRNA pairs retained")
ax.set_title("L7 — candidate dataset rule, applied cumulatively", fontsize=9.5, loc="left")

ax = axes[1]
ax.bar(S6.partner_length_spread, S6.n_exact_rt,
       color=["#3b6ea5", "#7fa8cc", "#d9a441", "#b5533b"], width=0.62)
for x, (n, p) in enumerate(S6[["n_exact_rt", "pct"]].itertuples(index=False)):
    ax.text(x, n + 12, f"{n}\n({p:.0f}%)", ha="center", fontsize=8)
ax.set_ylabel("exact RTs with >1 ncRNA partner")
ax.set_xticks(range(len(S6)))
ax.set_xticklabels([s.split("  ")[0] for s in S6.partner_length_spread], fontsize=8)
ax.set_ylim(0, 780)
ax.set_title("L6 — most 'multiple partners' are\nlength variants of one RNA", fontsize=9.5, loc="left")
fig.tight_layout(); savefig(fig, "L_dataset_rule_and_multiplicity", pop=['PAIR-CANON']); plt.show()
''')

md(r"""
**L7 — the proposed rule, costed.** Applying *Retron → same strand → upstream → no intervening CDS
→ within 200 bp* cumulatively to canonical placements yields **190,028 placements, 22,526 exact
pairs, 21,610 exact RT proteins, 11,514 exact ncRNA sequences, 156,741 physical loci** — retaining
**74 %** of canonical exact pairs. The distance cut is the only step that removes a large share; the
strand and adjacency criteria are nearly free because the population already satisfies them.

Adding *not contig-start-clipped* is the consequential extra decision: it drops the dataset to
14,905 pairs, **removing a further 34 %**. That criterion is defensible — a clipped window cannot
show what lies beyond the contig edge — but it is a substantive reduction and should be a stated
choice, not a default.

Within the 22,526-pair rule, recurrence splits as **8,660 single-placement**, **6,686 database
copies of one physical locus**, and **7,180 independently recurrent** (3,761 across species, 3,399
across genomes of one species, 20 across loci of one genome).

**Recommendation.** Ship the dataset in **tiers** rather than as one thresholded set: a permissive
tier (the 22,526-pair rule), a strict tier (additionally unclipped, 14,905), and an
independence-filtered tier (additionally requiring cross-genome or cross-species recurrence). A
model or an experimental shortlist can then choose its own operating point, and the paper reports
all three rather than defending one threshold. **Covariance-model hit quality (`score`, `evalue`) is
still absent from every tier** and should be added before any tier is called "high-confidence".
""")
