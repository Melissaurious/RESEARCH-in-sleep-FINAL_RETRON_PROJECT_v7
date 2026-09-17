# ============================== SECTION A ==============================
md(r"""
---

# A. Corpus and redundancy

The unit ladder is the spine of every other number in this project. It exists because the
conversion between units is **not** a constant: the same corpus is 3.06 M records, 2.85 M loci
and 0.50 M distinct proteins, and the ratio between those depends on which database contributed
the rows.
""")

md(r"""
## A1 — The unit ladder: raw record → distinct → locus → physical locus → exact RT

* **Question.** By how much does each successive canonical unit collapse the corpus, and does
  the ladder recomputed from `data/derived/` reproduce the landed g2 ladder exactly?
* **Unit.** One row per rung; each rung is its own analytical unit (`V-REC`, `V-REC-DISTINCT`,
  `V-LOC`, `V-LOC-PHYS`, `V-RT`, `V-RT-TAXOCC`).
* **Denominator.** The 42 RT-anchored corpus files at their g1 sha256 — i.e. `POP-RT-FAM` +
  `POP-RT-MULTI`. The 298,482 ncRNA-anchor-only records are **not** in this table (Rule 1).
* **Data.** `rt_records_v1` → `record_key`, `is_first_copy`, `locus_key`, `physical_locus_key`,
  `rt_seq_hash`, `genome_id_norm`.
""")

code(r'''
funnel = cache("A1_unit_ladder", """
    SELECT 'raw_record'              AS unit, 1 AS rung, count(*)                                              AS n FROM rt_records
    UNION ALL SELECT 'distinct_raw_record', 2, count(*) FILTER (WHERE is_first_copy)                              FROM rt_records
    UNION ALL SELECT 'locus',               3, count(DISTINCT locus_key)                                          FROM rt_records
    UNION ALL SELECT 'physical_locus',      4, count(DISTINCT physical_locus_key)                                 FROM rt_records
    UNION ALL SELECT 'exact_rt',            5, count(DISTINCT rt_seq_hash)                                        FROM rt_records
    UNION ALL SELECT 'genome',              6, count(DISTINCT genome_id_norm)                                     FROM rt_records
    UNION ALL SELECT 'rt_taxonomic_occurrence', 7, count(DISTINCT (rt_seq_hash, genome_id_norm))                   FROM rt_records
    ORDER BY rung
""")
funnel["pct_of_raw"] = (100 * funnel["n"] / funnel.loc[funnel.unit == "raw_record", "n"].iloc[0]).round(2)
save(funnel, "A1_unit_ladder")
display(funnel[["unit", "n", "pct_of_raw"]])

print("\nagainst g7_resolved_values.tsv:")
for unit, key in [("raw_record", "records"), ("distinct_raw_record", "distinct_records"),
                  ("locus", "loci"), ("physical_locus", "phys_loci"),
                  ("exact_rt", "exact_rt"), ("genome", "genomes"),
                  ("rt_taxonomic_occurrence", "taxocc")]:
    check(unit, int(funnel.loc[funnel.unit == unit, "n"].iloc[0]), key)
''')

code(r'''
d = pd.read_csv(TABLES / "A1_unit_ladder.tsv", sep="\t").sort_values("rung")
lad = d[d.unit.isin(["raw_record", "distinct_raw_record", "locus", "physical_locus", "exact_rt"])]

fig, ax = plt.subplots(figsize=(7.2, 3.0))
y = np.arange(len(lad))[::-1]
ax.barh(y, lad["n"], color="#3b6ea5", height=0.62)
for yi, (u, n) in zip(y, lad[["unit", "n"]].itertuples(index=False)):
    ax.text(n * 1.02, yi, f"{n:,}", va="center", fontsize=8.5)
ax.set_yticks(y); ax.set_yticklabels(lad["unit"])
ax.set_xscale("log"); ax.set_xlim(1e5, 8e6)
ax.set_xlabel("count (log scale)")
ax.set_title("A1 — canonical unit ladder, RT-anchored corpus\n(ncRNA-anchor-only records excluded)",
             fontsize=9.5, loc="left")
savefig(fig, "A1_unit_ladder", pop=['REC-ALL']); plt.show()
''')

md(r"""
**Interpretation.** The ladder reproduces g2 exactly on every rung, which confirms the workbench
is reading the same canonical tables under the same keys. The collapse is severe and uneven:
3.06 M records carry only 501,561 distinct RT proteins, so **a record count is ~6× an exact-protein
count** — but that factor is an average over a heterogeneous corpus, not a conversion constant
(A2). `rt_taxonomic_occurrence` (2.74 M) sits *above* `locus` counts in informativeness for
taxonomic spread and *below* them for architecture; pick per question.

**Caveat.** `locus_key` is a coordinate interval on a contig *accession*, so two assembly versions
of the same contig are two loci. `physical_locus_key` normalises the `NZ_` spelling; the 371,628
RefSeq/GenBank twin collapses are all evidence-supported (identical window DNA, RT protein,
coordinates and strand), with zero disagreements.
""")

md(r"""
## A2 — Redundancy ratios, and why they are not a constant

* **Question.** How much redundancy does each source database contribute, and how far does the
  locus→exact-RT conversion factor move between them?
* **Unit.** Source database × each rung of the ladder.
* **Denominator.** Distinct raw records (`is_first_copy`) of that source database. **Population:
  full corpus, not `POP_RT`** — this cell characterises the corpus as mined.
  **A locus can appear under more than one source database (203,921 do), so the per-database
  columns do not sum to the corpus totals.**
* **Data.** `rt_records_v1` → `source_database`, `is_first_copy`, `locus_key`,
  `physical_locus_key`, `rt_seq_hash`, `genome_id_norm`.
""")

code(r'''
red = cache("A2_redundancy_by_database", """
    SELECT source_database,
           count(*)                                   AS n_records,
           count(DISTINCT locus_key)                  AS n_loci,
           count(DISTINCT physical_locus_key)         AS n_physical_loci,
           count(DISTINCT rt_seq_hash)                AS n_exact_rt,
           count(DISTINCT genome_id_norm)             AS n_genomes
    FROM rt_records WHERE is_first_copy
    GROUP BY 1 ORDER BY n_records DESC
""")
red["records_per_locus"]  = (red.n_records / red.n_loci).round(3)
red["loci_per_exact_rt"]  = (red.n_loci / red.n_exact_rt).round(2)
red["physical_loci_per_exact_rt"] = (red.n_physical_loci / red.n_exact_rt).round(2)
red["loci_per_genome"]    = (red.n_loci / red.n_genomes).round(3)
save(red, "A2_redundancy_by_database")
display(red)

print(f"\naccession-defined loci per exact RT: {red.loci_per_exact_rt.min():.2f} - {red.loci_per_exact_rt.max():.2f} "
      f"across source databases (~{red.loci_per_exact_rt.max()/red.loci_per_exact_rt.min():.1f}x spread).")
ident = (red.loci_per_exact_rt == red.physical_loci_per_exact_rt).all()
print(f"physical loci per exact RT is {'IDENTICAL' if ident else 'DIFFERENT'} within every database — "
      "the NZ_ twin collapse acts ACROSS databases (NCBI<->GTDB), never inside one, so the\n"
      "  per-database redundancy multiplier is unaffected by the choice of locus definition.")
print("corpus-wide ratios (distinct records / loci / physical loci per exact RT):")
f = pd.read_csv(TABLES / "A1_unit_ladder.tsv", sep="\t").set_index("unit")["n"]
for u in ["distinct_raw_record", "locus", "physical_locus"]:
    print(f"  {u:<22} {f[u] / f['exact_rt']:.3f} per exact RT")
''')

code(r'''
r = pd.read_csv(TABLES / "A2_redundancy_by_database.tsv", sep="\t").sort_values("loci_per_exact_rt")

fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.2))
ax = axes[0]
ax.barh(r.source_database, r.loci_per_exact_rt, color="#3b6ea5", height=0.62)
for i, v in enumerate(r.loci_per_exact_rt):
    ax.text(v + 0.06, i, f"{v:.2f}", va="center", fontsize=8)
ax.set_xlabel("loci per exact RT protein"); ax.set_xlim(0, r.loci_per_exact_rt.max() * 1.18)
ax.set_title("A2 — redundancy is database-dependent", fontsize=9.5, loc="left")

ax = axes[1]
ax.scatter(r.n_records, r.loci_per_exact_rt, s=42, color="#b5533b", zorder=3)
for _, row in r.iterrows():
    ax.annotate(row.source_database, (row.n_records, row.loci_per_exact_rt),
                textcoords="offset points", xytext=(5, 3), fontsize=7.5)
ax.set_xscale("log"); ax.set_xlabel("distinct records in that database (log)")
ax.set_ylabel("loci per exact RT")
ax.set_title("redundancy scales with sampling depth", fontsize=9.5, loc="left")
fig.tight_layout(); savefig(fig, "A2_redundancy_by_database", pop=['REC-ALL']); plt.show()
''')

md(r"""
**Interpretation.** The multiplier is **accession-defined loci per exact RT protein**, and within
a single source database it is numerically identical to *physical* loci per protein: the `NZ_`
twin collapse merges a RefSeq and a GenBank spelling of one contig, which by construction sit in
different databases. The locus-definition choice therefore changes corpus-wide totals but not the
per-database redundancy reported here. `loci_per_exact_rt` runs from **1.11** (`mgnify_soil`) to **5.49**
(`ncbi_bacteria`) — a ~5× spread, and it tracks how deeply the database was sampled rather than
anything about the RTs. This is the quantitative reason the project refuses a single
record↔protein conversion: an analysis reported on records is weighted by isolate-genome
sequencing effort, an analysis reported on exact RTs is not.

**Caveat.** These per-database columns overlap: 203,921 loci appear under more than one source
database, so column sums exceed the corpus totals in A1. The metagenomic databases (`mgnify_*`,
`gem`) look "less redundant" partly because near-identical MAG contigs receive different contig
accessions and therefore different `locus_key`s — low redundancy here is partly a naming effect.
""")

md(r"""
## A3 — Occurrence distribution per exact RT protein

* **Question.** How is genomic occurrence distributed across distinct RT proteins — is the corpus
  a few hyper-abundant sequences plus a long tail of singletons?
* **Unit.** Exact RT protein (`V-RT`, `rt_seq_hash`), 501,561 of them.
* **Denominator.** All exact RT proteins in `rt_exact_v1` (this **includes** the MULTI stratum;
  the family split is B).
* **Data.** `rt_exact_v1` → `rt_seq_hash`, `n_records`, `n_loci`, `n_physical_loci`, `n_genomes`.
  `rt_seq` is deliberately not selected.
""")

code(r'''
occ = cache("A3_occurrence_buckets", """
    WITH b AS (
      SELECT CASE WHEN n_genomes = 1 THEN '1'
                  WHEN n_genomes <= 10 THEN '2-10'
                  WHEN n_genomes <= 100 THEN '11-100'
                  WHEN n_genomes <= 1000 THEN '101-1000'
                  ELSE '>1000' END AS bucket,
             CASE WHEN n_genomes = 1 THEN 1 WHEN n_genomes <= 10 THEN 2
                  WHEN n_genomes <= 100 THEN 3 WHEN n_genomes <= 1000 THEN 4 ELSE 5 END AS ord,
             n_genomes, n_loci
      FROM rt_exact)
    SELECT bucket, ord, count(*) AS n_exact_rt, sum(n_genomes) AS n_taxocc, sum(n_loci) AS n_loci
    FROM b GROUP BY 1, 2 ORDER BY ord
""")
tot = occ.n_exact_rt.sum()
occ["pct_of_exact_rt"] = (100 * occ.n_exact_rt / tot).round(2)
occ["pct_of_taxocc"]   = (100 * occ.n_taxocc / occ.n_taxocc.sum()).round(2)
save(occ, "A3_occurrence_buckets")
display(occ[["bucket", "n_exact_rt", "pct_of_exact_rt", "n_taxocc", "pct_of_taxocc"]])

q = cache("A3_occurrence_quantiles", """
    SELECT 'n_genomes' AS measure, min(n_genomes) AS min,
           quantile_cont(n_genomes, 0.50) AS median, quantile_cont(n_genomes, 0.90) AS p90,
           quantile_cont(n_genomes, 0.99) AS p99, max(n_genomes) AS max, avg(n_genomes) AS mean
    FROM rt_exact
    UNION ALL SELECT 'n_loci', min(n_loci), quantile_cont(n_loci, 0.50), quantile_cont(n_loci, 0.90),
           quantile_cont(n_loci, 0.99), max(n_loci), avg(n_loci) FROM rt_exact
    UNION ALL SELECT 'n_records', min(n_records), quantile_cont(n_records, 0.50),
           quantile_cont(n_records, 0.90), quantile_cont(n_records, 0.99), max(n_records), avg(n_records)
    FROM rt_exact
""")
display(q.round(2))

top = cache("A3_top_recurrent_exact_rt", """
    SELECT rt_seq_hash, family_label_set, rt_aa_len, n_records, n_loci, n_physical_loci,
           n_genomes, n_source_databases
    FROM rt_exact ORDER BY n_genomes DESC LIMIT 20
""")
display(top.assign(rt_seq_hash=top.rt_seq_hash.str.slice(0, 12) + "…").head(10))
''')

code(r'''
o = pd.read_csv(TABLES / "A3_occurrence_buckets.tsv", sep="\t").sort_values("ord")
ccdf = cache("A3_occurrence_ccdf", """
    WITH t AS (SELECT n_genomes AS k, count(*) AS c FROM rt_exact GROUP BY 1)
    SELECT k, c, sum(c) OVER (ORDER BY k DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS n_at_least
    FROM t ORDER BY k
""")

fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.3))
ax = axes[0]
ax.bar(o.bucket, o.pct_of_exact_rt, color="#3b6ea5", width=0.62, label="% of exact RT proteins")
ax.bar(o.bucket, o.pct_of_taxocc, color="#b5533b", width=0.30, label="% of taxonomic occurrences")
ax.set_ylabel("percent"); ax.set_xlabel("genomes carrying that exact RT")
ax.legend(fontsize=8); ax.set_title("A3 — occurrence buckets", fontsize=9.5, loc="left")

ax = axes[1]
ax.plot(ccdf.k, ccdf.n_at_least, color="#3b6ea5", lw=1.4)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("genome occurrences k (log)"); ax.set_ylabel("# exact RTs with ≥ k (log)")
ax.set_title("heavy-tailed occurrence (CCDF)", fontsize=9.5, loc="left")
fig.tight_layout(); savefig(fig, "A3_occurrence_distribution", pop=['RT-BASE']); plt.show()
''')

md(r"""
**Interpretation.** **65.5 %** of exact RT proteins are seen in exactly one genome, while the
253 proteins found in >1,000 genomes account for a large share of all taxonomic occurrences. The
CCDF is close to straight on log–log over three decades, i.e. the corpus is heavy-tailed: any
statistic computed on records is dominated by a small number of hyper-sampled sequences, and the
same statistic computed on `V-RT` is dominated by singletons. Reporting both is the only honest
option.

**Caveat.** "Seen in one genome" is a statement about *this corpus at this sampling*, not about
rarity in nature. The singleton fraction is partly the metagenomic contribution, where every MAG
is its own genome id. The top of the table is the mirror image: hyper-abundant sequences are
concentrated in `ncbi_bacteria`, where the same organism is deposited thousands of times.
""")
