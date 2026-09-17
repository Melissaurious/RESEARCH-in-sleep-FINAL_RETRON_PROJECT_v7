md(r"""
---

# F. Exact RT–ncRNA pairing topology and independent recurrence

Two distinct questions, deliberately separated: **is an observed association unambiguous** (does
this RT sequence go with exactly one ncRNA sequence and vice versa), and **is its recurrence
independent** (does it recur across genomes and species, or only as repeated database copies of a
single physical locus)? The first bears on dataset selection; only the second bears on any
co-evolutionary reading.
""")

md(r"""
## F0 — Which placement population the pair view is built on

The registered exact-pair view (`rt_ncrna_exact_pairs_v1`, **30,924** pairs) is derived from the
**ELIGIBLE** placement population (345,313), not the CANONICAL one (344,154). The difference is not
cosmetic, so it is measured rather than assumed.
""")

code(r'''
basis = cache("F0_pair_view_basis", """
    SELECT 'ALL placements' AS placement_population,
           count(DISTINCT (rt_seq_hash, nc_seq_hash)) AS n_exact_pairs,
           count(DISTINCT rt_seq_hash) AS n_exact_rt, count(DISTINCT nc_seq_hash) AS n_exact_ncrna
    FROM rt_ncrna_pairs
    UNION ALL SELECT 'ELIGIBLE', count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           count(DISTINCT rt_seq_hash), count(DISTINCT nc_seq_hash)
    FROM rt_ncrna_pairs WHERE geometry_eligible
    UNION ALL SELECT 'CANONICAL', count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           count(DISTINCT rt_seq_hash), count(DISTINCT nc_seq_hash)
    FROM rt_ncrna_pairs WHERE canonical
    UNION ALL SELECT 'rt_ncrna_exact_pairs_v1 (the registered view)', count(*),
           count(DISTINCT rt_seq_hash), count(DISTINCT nc_seq_hash) FROM rt_ncrna_exact_pairs
""", pop=["PAIR-ELIG", "PAIR-CANON"])
display(basis)
check("registered pair view size",
      int(basis.loc[basis.placement_population.str.startswith("rt_ncrna_exact_pairs"), "n_exact_pairs"].iloc[0]),
      "pairs")

orphan = Q("""SELECT count(*) AS n FROM rt_ncrna_exact_pairs e
              WHERE NOT EXISTS (SELECT 1 FROM rt_ncrna_pairs p
                                WHERE p.canonical AND p.rt_seq_hash = e.rt_seq_hash
                                  AND p.nc_seq_hash = e.nc_seq_hash)""")
print(f"""
  registered pair view (ELIGIBLE-based)  = PAIR-ELIG  .. {int(basis.loc[basis.placement_population == "ELIGIBLE", "n_exact_pairs"].iloc[0]):,}
  pairs from CANONICAL placements        = PAIR-CANON .. {int(basis.loc[basis.placement_population == "CANONICAL", "n_exact_pairs"].iloc[0]):,}
  difference .................................. {int(orphan.n[0])} pairs

  Those {int(orphan.n[0])} pairs are represented ONLY by placements that are geometry-eligible but were
  removed by placement de-duplication (the ATYPICAL population, 1,159 placements). They are real
  sequence pairs; they simply have no surviving canonical placement.
""")
''')

md(r"""
**Interpretation.** Section F uses the **registered 30,924-pair view** so that its numbers match the
landed g3 topology tables. Section D6, which compares geometry compositions, uses the
**canonical-derived 30,427 pairs**, because a geometry can only be attributed to a pair through a
placement that survived de-duplication. Both are correct for their purpose; **quoting one figure
while citing the other is not.** Any dataset row in section K states which basis it used.

## F1 — Partner-count distributions on both sides

* **Question.** How many partners does each side of the association have?
* **Unit.** Exact RT protein and exact ncRNA sequence, **within the exact-pair view**.
* **Denominator.** The side named in the measure, within the pair view — **29,192 exact RTs and
  16,458 exact ncRNAs**, not the 501,561 exact RTs of the corpus, since most carry no call at all.
* **Data.** `rt_ncrna_exact_pairs_v1` → `rt_seq_hash`, `nc_seq_hash`.
""")

code(r'''
deg = cache("F1_partner_degrees", """
    WITH rt AS (SELECT rt_seq_hash, count(DISTINCT nc_seq_hash) AS k FROM rt_ncrna_exact_pairs GROUP BY 1),
         nc AS (SELECT nc_seq_hash, count(DISTINCT rt_seq_hash) AS k FROM rt_ncrna_exact_pairs GROUP BY 1)
    SELECT 'exact RT -> n ncRNA partners' AS side, least(k, 10) AS k_capped, count(*) AS n FROM rt GROUP BY 1,2
    UNION ALL
    SELECT 'exact ncRNA -> n RT partners', least(k, 10), count(*) FROM nc GROUP BY 1,2
    ORDER BY side, k_capped
""")
for side in deg.side.unique():
    deg.loc[deg.side == side, "pct_of_side"] = (
        100 * deg.loc[deg.side == side, "n"] / deg.loc[deg.side == side, "n"].sum()).round(3)
save(deg, "F1_partner_degrees")
display(deg)

summ = cache("F1_topology_summary", """
    WITH rt AS (SELECT rt_seq_hash, count(DISTINCT nc_seq_hash) AS k FROM rt_ncrna_exact_pairs GROUP BY 1),
         nc AS (SELECT nc_seq_hash, count(DISTINCT rt_seq_hash) AS k FROM rt_ncrna_exact_pairs GROUP BY 1)
    SELECT 'exact RTs in the pair view' AS measure, count(*) AS n, NULL::DOUBLE AS pct FROM rt
    UNION ALL SELECT 'exact RTs with exactly one ncRNA partner', count(*) FILTER (WHERE k = 1),
           100.0 * count(*) FILTER (WHERE k = 1) / count(*) FROM rt
    UNION ALL SELECT 'exact RTs with more than one', count(*) FILTER (WHERE k > 1),
           100.0 * count(*) FILTER (WHERE k > 1) / count(*) FROM rt
    UNION ALL SELECT 'max ncRNA partners on one exact RT', max(k), NULL FROM rt
    UNION ALL SELECT 'exact ncRNAs in the pair view', count(*), NULL FROM nc
    UNION ALL SELECT 'exact ncRNAs with exactly one RT partner', count(*) FILTER (WHERE k = 1),
           100.0 * count(*) FILTER (WHERE k = 1) / count(*) FROM nc
    UNION ALL SELECT 'exact ncRNAs with more than one', count(*) FILTER (WHERE k > 1),
           100.0 * count(*) FILTER (WHERE k > 1) / count(*) FROM nc
    UNION ALL SELECT 'max RT partners on one exact ncRNA', max(k), NULL FROM nc
""")
display(summ.round(3))

print("\nagainst g3_topology_degrees:")
g3t = gate_table("dbchar_g3_pair_geometry", "g3_topology_degrees").set_index("measure")["n"]
for lab, key in [("exact RTs in the pair view", "exact_RTs_in_the_pair_view"),
                 ("exact RTs with exactly one ncRNA partner", "exact_RTs_paired_with_exactly_one_ncRNA_sequence"),
                 ("exact ncRNAs in the pair view", "exact_ncRNA_sequences_in_the_pair_view"),
                 ("exact ncRNAs with exactly one RT partner", "exact_ncRNA_sequences_paired_with_exactly_one_RT"),
                 ("max RT partners on one exact ncRNA", "max_exact_RTs_on_one_ncRNA_sequence")]:
    check(lab, int(summ.loc[summ.measure == lab, "n"].iloc[0]), expected=float(g3t[key]))
''')

md(r"""
## F2 — Component shapes: which associations are unambiguous

* **Question.** Treating exact RTs and exact ncRNAs as a bipartite graph, how many associations are
  cleanly one-to-one, and how much of the data sits in large entangled components?
* **Unit.** Connected component of the exact RT–ncRNA bipartite graph.
* **Denominator.** All 14,918 components.
* **Data.** `rt_ncrna_exact_pairs_v1`; cross-checked against `g3_topology_components.tsv`.
""")

code(r'''
comp = gate_table("dbchar_g3_pair_geometry", "g3_topology_components")
comp["pct_of_components"] = (100 * comp.n_components / comp.n_components.sum()).round(3)
comp["pct_of_exact_rt_in_view"] = (100 * comp.n_exact_rt / comp.n_exact_rt.sum()).round(3)
save(comp, "F2_component_shapes")
display(comp[["shape", "n_components", "pct_of_components", "n_exact_rt",
              "pct_of_exact_rt_in_view", "n_exact_ncrna",
              "max_rt_in_a_component", "max_ncrna_in_a_component"]])

check("1:1 components", int(comp.loc[comp.shape_ if False else comp["shape"] == "1:1", "n_components"].iloc[0]),
      "pairs_1to1")
one2one = int(comp.loc[comp["shape"] == "1:1", "n_components"].iloc[0])
print(f"\n{one2one:,} strictly 1:1 components: {100*one2one/comp.n_components.sum():.2f}% of components, "
      f"but only {100*one2one/comp.n_exact_rt.sum():.2f}% of the exact RTs in the pair view.")
print("The many:1 and many:many components hold few components but most of the RT sequences —\n"
      "ambiguity is concentrated, not spread.")
''')

md(r"""
## F3 — Recurrence: independent observation versus repeated database copies

* **Question.** When a pair recurs, what kind of repetition is it?
* **Unit.** Exact (RT, ncRNA) pair.
* **Denominator.** All 30,924 exact pairs.
* **Data.** `rt_ncrna_exact_pair_recurrence_v1` → `recurrence_class`, `n_placements`, `n_loci`,
  `n_physical_loci`, `n_genomes`, `n_species`, `n_databases`.
""")

code(r'''
rec = cache("F3_recurrence_classes", """
    SELECT recurrence_class, count(*) AS n_pairs,
           median(n_placements) AS median_placements, median(n_physical_loci) AS median_physical_loci,
           median(n_genomes) AS median_genomes, median(n_species) AS median_species
    FROM rt_ncrna_exact_pair_recurrence GROUP BY 1 ORDER BY n_pairs DESC
""")
rec["pct_of_pairs"] = (100 * rec.n_pairs / rec.n_pairs.sum()).round(3)
save(rec, "F3_recurrence_classes")
display(rec)

INDEPENDENT = ["multiple_species", "one_species_multiple_genomes", "one_genome_multiple_loci"]
ind = rec[rec.recurrence_class.isin(INDEPENDENT)].n_pairs.sum()
dbcopy = rec[rec.recurrence_class.str.contains("physical_locus")].n_pairs.sum()
once = rec[rec.recurrence_class == "single_placement"].n_pairs.sum()
tot = rec.n_pairs.sum()
print(f"""
  observed once .................................. {once:>6,}  ({100*once/tot:5.2f}%)
  recurs only as copies of ONE physical locus .... {dbcopy:>6,}  ({100*dbcopy/tot:5.2f}%)  <- database redundancy
  recurs across genomes or species ............... {ind:>6,}  ({100*ind/tot:5.2f}%)  <- independent observation
  ---------------------------------------------------------
  total exact pairs .............................. {tot:>6,}
""")

# cross-tabulate independence against how unambiguous the association is
cross = cache("F3_recurrence_x_ambiguity", """
    WITH deg AS (
      SELECT rt_seq_hash, nc_seq_hash,
             count(*) OVER (PARTITION BY rt_seq_hash) AS rt_partners,
             count(*) OVER (PARTITION BY nc_seq_hash) AS nc_partners
      FROM rt_ncrna_exact_pairs)
    SELECT r.recurrence_class,
           CASE WHEN d.rt_partners = 1 AND d.nc_partners = 1 THEN 'unambiguous (1:1)'
                ELSE 'ambiguous (>1 partner on a side)' END AS ambiguity,
           count(*) AS n_pairs
    FROM rt_ncrna_exact_pair_recurrence r
    JOIN deg d USING (rt_seq_hash, nc_seq_hash)
    GROUP BY 1, 2 ORDER BY n_pairs DESC
""")
piv = cross.pivot_table(index="recurrence_class", columns="ambiguity", values="n_pairs", fill_value=0)
piv["total"] = piv.sum(axis=1)
display(piv.sort_values("total", ascending=False))
''')

code(r'''
R = pd.read_csv(TABLES / "F3_recurrence_classes.tsv", sep="\t").sort_values("n_pairs")
Dg = pd.read_csv(TABLES / "F1_partner_degrees.tsv", sep="\t")
Cp = pd.read_csv(TABLES / "F2_component_shapes.tsv", sep="\t")

fig, axes = plt.subplots(1, 3, figsize=(13.4, 3.9))

ax = axes[0]
for side, color, off in [("exact RT -> n ncRNA partners", "#3b6ea5", -0.19),
                         ("exact ncRNA -> n RT partners", "#b5533b", 0.19)]:
    d = Dg[Dg.side == side]
    ax.bar(d.k_capped + off, d.pct_of_side, width=0.36, color=color, label=side.split(" -> ")[0])
ax.set_yscale("log"); ax.set_xlabel("partners (capped at 10)")
ax.set_ylabel("% of that side (log)"); ax.legend(fontsize=7.5)
ax.set_title("F1 — partner counts on both sides", fontsize=9.5, loc="left")

ax = axes[1]
y = np.arange(len(Cp)); h = 0.38
ax.barh(y + h/2, Cp.pct_of_components, height=h, color="#3b6ea5", label="% of components")
ax.barh(y - h/2, Cp.pct_of_exact_rt_in_view, height=h, color="#4a8a72", label="% of exact RTs")
ax.set_yticks(y); ax.set_yticklabels(Cp["shape"], fontsize=8.5)
ax.set_xlabel("percent"); ax.legend(fontsize=7.5)
ax.set_title("F2 — few components hold most sequences", fontsize=9.5, loc="left")

ax = axes[2]
colors = ["#b5533b" if "physical_locus" in c else
          ("#9aa7b1" if c == "single_placement" else "#4a8a72") for c in R.recurrence_class]
ax.barh(R.recurrence_class, R.pct_of_pairs, color=colors, height=0.66)
for i, (v, n) in enumerate(zip(R.pct_of_pairs, R.n_pairs)):
    ax.text(v + 0.7, i, f"{v:.1f}%  ({n:,})", va="center", fontsize=7.2)
ax.set_xlim(0, 55); ax.set_xlabel("% of 30,924 exact pairs")
ax.tick_params(axis="y", labelsize=7.2)
ax.set_title("F3 — recurrence: green = independent,\nred = database copies of one locus",
             fontsize=9.5, loc="left")

fig.tight_layout(); savefig(fig, "F_pairing_topology", pop=['PAIR-ELIG']); plt.show()
''')

md(r"""
**Interpretation.** The association is predominantly unambiguous *as observed*: **96.85 % of exact
RTs in the pair view have exactly one ncRNA partner** and **82.28 % of exact ncRNAs have exactly one
RT partner**. But ambiguity is concentrated rather than spread — the 1:1 components are 80.97 % of
components while holding only 41.38 % of the exact RTs in the view, and a single component reaches
706 RTs and 190 ncRNAs.

The recurrence split is the result that matters for any evolutionary reading. Of 30,924 exact
pairs, **38.82 % are seen once**, **30.32 % recur only as multiple database copies of a single
physical locus**, and only **30.86 % recur across distinct genomes or species**. Roughly **a third
of the apparent recurrence in this resource is database redundancy, not independent observation** —
and the cross-tabulation shows it is not evenly distributed across the ambiguity classes.

**Caveats.** (i) "Unambiguous" here means *unambiguous in this corpus under exact-sequence
identity*: a single amino-acid difference creates a new `rt_seq_hash` and therefore a new node, so
these degrees are an upper bound on distinctness and a lower bound on partner sharing. (ii) A 1:1
observed association **does not demonstrate orthogonality or cognate specificity** — it is a
selection criterion for a downstream dataset, not evidence of exclusive biological pairing.
(iii) Pair membership is inherited from placement geometry, which is detector-defined (§C, §E), so
the pair view inherits every scope limit of the covariance-model library.
""")
