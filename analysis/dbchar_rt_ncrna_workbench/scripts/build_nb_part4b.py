md(r"""
## D5 — Strand agreement, and what the opposite-strand placements actually are

* **Question.** What is the correct same-strand rate, and are the opposite-strand placements a
  scattered error tail or a structured population?
* **Unit.** Placement (`V-PAIR-PLACEMENT`), `CANONICAL`; MULTI additionally held out for the
  `POP_RT`-consistent figure.
* **Denominator.** 344,154 canonical placements (and 344,148 with MULTI removed). Sub-profiles use
  the 3,041 opposite-strand placements as their own denominator and say so.
* **Data.** `rt_ncrna_pairs_v1` → `same_strand`, `direction`, `signed_distance_bp`,
  `n_cds_between`, `true_start_clipped`, `rt_strand`, `detection_model`, `file_label`,
  `nc_seq_hash`, `rt_seq_hash`, `canonical`.

**Why this section exists.** The g7 REPORT.md prose states 99.8 % same-strand. That string is a
hard-coded literal in `dbchar_g7_stage1_report/scripts/findings.py:190` — every other number in
that sentence is a placeholder resolved from `g7_resolved_values.tsv`, and there is no
`same_strand` key in that registry. The gate table `g3_same_strand.tsv` says **99.12 %**. Rather
than restate the correct number, this section measures it under every relevant population and then
characterises the difference the two numbers are arguing about.
""")

code(r'''
# 1. the rate under every population, so the figure cannot be quoted without its denominator
rates = cache("D5_same_strand_by_population", f"""
    SELECT 'ALL placements' AS population, count(*) AS n,
           count(*) FILTER (WHERE same_strand) AS n_same,
           count(*) FILTER (WHERE NOT same_strand) AS n_opposite FROM rt_ncrna_pairs
    UNION ALL SELECT 'ELIGIBLE', count(*), count(*) FILTER (WHERE same_strand),
           count(*) FILTER (WHERE NOT same_strand) FROM rt_ncrna_pairs WHERE geometry_eligible
    UNION ALL SELECT 'CANONICAL', count(*), count(*) FILTER (WHERE same_strand),
           count(*) FILTER (WHERE NOT same_strand) FROM rt_ncrna_pairs WHERE canonical
    UNION ALL SELECT 'CANONICAL, MULTI held out (POP_RT-consistent)', count(*),
           count(*) FILTER (WHERE same_strand), count(*) FILTER (WHERE NOT same_strand)
           FROM rt_ncrna_pairs WHERE canonical AND file_label <> 'MULTI'
    UNION ALL SELECT 'CANONICAL, Retron only', count(*), count(*) FILTER (WHERE same_strand),
           count(*) FILTER (WHERE NOT same_strand) FROM rt_ncrna_pairs
           WHERE canonical AND file_label = 'Retron'
""")
rates["pct_same_strand"] = (100 * rates.n_same / rates.n).round(3)
save(rates, "D5_same_strand_by_population")
display(rates)

g3s = gate_table("dbchar_g3_pair_geometry", "g3_same_strand")
g3c = g3s[g3s.population == "CANONICAL"]
g3_pct = 100 * g3c.loc[g3c.same_strand == True, "n_placements"].sum() / g3c.n_placements.sum()
check("CANONICAL same-strand % (vs g3_same_strand.tsv)",
      float(rates.loc[rates.population == "CANONICAL", "pct_same_strand"].iloc[0]),
      expected=round(g3_pct, 3), tol=1e-3)

print('\n  provenance of the disputed figure:')
print('    g3_same_strand.tsv (gate table)          -> %.3f%%   REGISTERED, reproduced above' % g3_pct)
print('    g7 REPORT.md prose                       -> 99.8%     hard-coded literal, findings.py:190')
print('    g7_resolved_values.tsv                   -> %s' %
      ("absent — the quantity was never registered"
       if not (RESOLVED.key.str.contains("strand")).any() else "present"))
''')

code(r'''
# 2. are the 3,041 opposite-strand placements noise, or structured?
prof = cache("D5_opposite_strand_profile", """
    SELECT CASE WHEN same_strand THEN 'same strand' ELSE 'opposite strand' END AS stratum,
           count(*) AS n_placements,
           count(DISTINCT nc_seq_hash) AS n_exact_ncrna,
           count(DISTINCT rt_seq_hash) AS n_exact_rt,
           count(DISTINCT detection_model) AS n_models,
           quantile_cont(signed_distance_bp, 0.50) AS median_signed_bp,
           100.0 * count(*) FILTER (WHERE n_cds_between = 0) / count(*) AS pct_no_cds_between,
           100.0 * count(*) FILTER (WHERE true_start_clipped) / count(*) AS pct_true_start_clipped,
           100.0 * count(*) FILTER (WHERE rt_strand = '-') / count(*) AS pct_rt_on_minus_strand
    FROM rt_ncrna_pairs WHERE canonical GROUP BY 1
""")
display(prof.round(2))

comp = cache("D5_opposite_strand_composition", """
    SELECT 'detection_model' AS dimension, detection_model AS value, count(*) AS n
    FROM rt_ncrna_pairs WHERE canonical AND NOT same_strand GROUP BY 1, 2
    UNION ALL SELECT 'file_label', file_label, count(*)
    FROM rt_ncrna_pairs WHERE canonical AND NOT same_strand GROUP BY 1, 2
    UNION ALL SELECT 'direction', direction, count(*)
    FROM rt_ncrna_pairs WHERE canonical AND NOT same_strand GROUP BY 1, 2
    ORDER BY dimension, n DESC
""")
n_opp = int(comp[comp.dimension == "file_label"].n.sum())
comp["pct_of_opposite"] = (100 * comp.n / n_opp).round(2)
save(comp, "D5_opposite_strand_composition")
for dim in ["detection_model", "file_label", "direction"]:
    print(f"\n-- {dim} (denominator: {n_opp:,} opposite-strand canonical placements)")
    display(comp[comp.dimension == dim].head(6)[["value", "n", "pct_of_opposite"]])
''')

code(r'''
P = pd.read_csv(TABLES / "D5_same_strand_by_population.tsv", sep="\t")
C = pd.read_csv(TABLES / "D5_opposite_strand_composition.tsv", sep="\t")
PR = pd.read_csv(TABLES / "D5_opposite_strand_profile.tsv", sep="\t")

fig, axes = plt.subplots(1, 3, figsize=(13.4, 3.8))

ax = axes[0]
p = P.iloc[::-1]
ax.barh(np.arange(len(p)), p.pct_same_strand, color="#3b6ea5", height=0.6)
for i, v in enumerate(p.pct_same_strand):
    ax.text(v - 0.06, i, f"{v:.2f}%", va="center", ha="right", fontsize=8, color="white")
ax.axvline(99.8, color="#b5533b", lw=1.4, ls="--")
ax.text(99.8, len(p) - 0.35, ' g7 prose\n "99.8%"', color="#b5533b", fontsize=7.5, va="top")
ax.set_yticks(np.arange(len(p)))
ax.set_yticklabels([t.replace(", ", ",\n") for t in p.population], fontsize=7.5)
ax.set_xlim(98.5, 100.05); ax.set_xlabel("% same strand")
ax.set_title("D5 — same-strand rate by population", fontsize=9.5, loc="left")

ax = axes[1]
m = C[C.dimension == "detection_model"].sort_values("n").tail(8)
ax.barh(m.value, m.n, color="#b5533b", height=0.62)
for i, (v, n) in enumerate(zip(m.value, m.n)):
    ax.text(n + 30, i, f"{n:,}", va="center", fontsize=7.5)
ax.set_xlabel("opposite-strand placements")
ax.tick_params(axis="y", labelsize=7.5)
ax.set_title("one CM produces most of them", fontsize=9.5, loc="left")

ax = axes[2]
labels = ["median |distance| (bp)", "% no CDS between", "% contig-start clipped"]
same = PR[PR.stratum == "same strand"].iloc[0]
opp  = PR[PR.stratum == "opposite strand"].iloc[0]
vals_same = [abs(same.median_signed_bp), same.pct_no_cds_between, same.pct_true_start_clipped]
vals_opp  = [abs(opp.median_signed_bp),  opp.pct_no_cds_between,  opp.pct_true_start_clipped]
y = np.arange(len(labels)); h = 0.36
ax.barh(y + h/2, vals_same, height=h, color="#3b6ea5", label="same strand")
ax.barh(y - h/2, vals_opp,  height=h, color="#b5533b", label="opposite strand")
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=8)
ax.set_xscale("log"); ax.set_xlabel("value (log)"); ax.legend(fontsize=7.5)
ax.set_title("the two strata are different phenomena", fontsize=9.5, loc="left")

fig.tight_layout(); savefig(fig, "D5_strand_agreement", pop=['PL-CANON']); plt.show()
''')

md(r"""
**Interpretation.** The same-strand rate is **99.12 %** on canonical placements, and it barely moves
across populations (99.12 % on ALL, ELIGIBLE, CANONICAL, and with MULTI held out) — so the gap to
the prose's 99.8 % is not a denominator disagreement. The gate table is right and the report
sentence is an unregistered literal.

The more useful result is what the 3,041 opposite-strand placements *are*: **not an error tail**.
They are strongly structured —

* **2,571 of 3,041 (84.5 %) come from one covariance model, `TypeXIIIA_firmi`**, and 96 % sit at
  Retron loci;
* their median distance is **−4,750 bp** against −44 bp for same-strand placements;
* only **12.5 %** have no intervening CDS, against 95.1 % for same-strand placements;
* they collapse onto just **288 distinct ncRNA sequences** over 439 exact RTs, with one sequence
  alone accounting for 452 placements.

So the opposite-strand stratum is a distant, CDS-separated, single-CM population — architecturally
a *different thing* from the canonical adjacent retron arrangement, and the leading hypothesis is
TypeXIII CM matching at distance rather than an inverted retron. Rounding it away into "99.8 %
same strand" is precisely what loses it.

**Caveat.** This is a description, not an identification: nothing here shows what those 288
sequences are. Before any of them is read as biology, the CM cross-matching hypothesis has to be
excluded on the same evidence standard used for the 266 non-Retron candidates (section I) — and
the same-strand comparison bars above use a log axis precisely because the two strata differ by
two orders of magnitude on distance, which no linear panel would show honestly.
""")
