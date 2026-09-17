# ============================== SECTION B ==============================
md(r"""
---

# B. RT-family landscape

Family composition is reported on **exact RT proteins**, not records: on records the landscape is
a picture of which organisms were sequenced most. `MULTI` is held out as its own stratum
throughout (Rule 2) and `V-RT-CROSS` — exact proteins seen under more than one family label in
single-family files — is reported separately rather than assigned anywhere.
""")

md(r"""
## B1 — Exact RT count and proportion by family

* **Question.** How is the distinct-protein diversity of the corpus distributed over RT families,
  and how different is that from the record-level distribution?
* **Unit.** Exact RT protein (`V-RT`), split into `V-RT-SINGLE` (493,956), `V-RT-MULTI` (7,593)
  and `V-RT-CROSS` (12).
* **Denominator.** `V-RT-SINGLE` exact RTs for family proportions. MULTI and CROSS are reported
  as their own rows and are **never** folded into a family.
* **Data.** `rt_family_baseline_v1` → `rt_seq_hash`, `family_label`, `view`, `rt_aa_len`;
  `rt_records_v1` → `file_label`, `is_first_copy` for the record-level comparison.
""")

code(r'''
views = cache("B1_views", "SELECT view, count(*) AS n_exact_rt FROM rt_family_baseline GROUP BY 1 ORDER BY 2 DESC")
display(views)
print("against g4:")
for v, k in [("V-RT-SINGLE", "v_single"), ("V-RT-MULTI", "v_multi"), ("V-RT-CROSS", "v_cross")]:
    check(v, int(views.loc[views.view == v, "n_exact_rt"].iloc[0]), k)

fam = cache("B1_family_composition", """
    WITH rt AS (
      SELECT family_label, count(*) AS n_exact_rt
      FROM rt_family_baseline WHERE view = 'V-RT-SINGLE' GROUP BY 1),
    rec AS (
      SELECT file_label AS family_label, count(*) AS n_records, count(DISTINCT locus_key) AS n_loci
      FROM rt_records WHERE is_first_copy AND file_label <> 'MULTI' GROUP BY 1)
    SELECT rt.family_label, rt.n_exact_rt, rec.n_records, rec.n_loci
    FROM rt JOIN rec USING (family_label) ORDER BY rt.n_exact_rt DESC
""")
fam["pct_of_exact_rt"] = (100 * fam.n_exact_rt / fam.n_exact_rt.sum()).round(3)
fam["pct_of_records"]  = (100 * fam.n_records  / fam.n_records.sum()).round(3)
fam["loci_per_exact_rt"] = (fam.n_loci / fam.n_exact_rt).round(2)
save(fam, "B1_family_composition")
print(f"\n{len(fam)} single-family labels; "
      f"top 3 = {fam.pct_of_exact_rt.head(3).sum():.1f}% of V-RT-SINGLE exact RTs "
      f"vs {fam.pct_of_records.head(3).sum():.1f}% of distinct records.")
display(fam.head(15))
''')

code(r'''
f = pd.read_csv(TABLES / "B1_family_composition.tsv", sep="\t").head(18).iloc[::-1]

fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.4), sharey=True)
y = np.arange(len(f))
ax = axes[0]
ax.barh(y, f.n_exact_rt, color="#3b6ea5", height=0.7)
ax.set_yticks(y); ax.set_yticklabels(f.family_label)
ax.set_xscale("log"); ax.set_xlabel("exact RT proteins (log)")
ax.set_title("B1 — V-RT-SINGLE exact RTs by family", fontsize=9.5, loc="left")

ax = axes[1]
h = 0.36
ax.barh(y + h/2, f.pct_of_exact_rt, height=h, color="#3b6ea5", label="% of exact RTs")
ax.barh(y - h/2, f.pct_of_records,  height=h, color="#b5533b", label="% of distinct records")
ax.set_xlabel("percent of its own denominator"); ax.legend(fontsize=8)
ax.set_title("protein-level vs record-level composition", fontsize=9.5, loc="left")
fig.tight_layout(); savefig(fig, "B1_family_composition", pop=['RT-BASE-1F']); plt.show()
''')

md(r"""
**Interpretation.** RVT-GII dominates distinct-protein diversity (~52 % of `V-RT-SINGLE`), with
Retron and RVT-DGRs next; the three together are ~83 % of exact RTs. The record-level bars differ
from the protein-level bars for every family, and the direction of the gap is informative:
families whose `% of records` exceeds `% of exact RTs` (see `loci_per_exact_rt` in the table)
are those concentrated in heavily redeposited isolate genomes.

**Caveat.** `family_label` here is the **corpus file the record came from** — a myRT-library
assignment, not an independent classification. A family's size is therefore partly the size and
sensitivity of its HMM. `MULTI` (7,593) and `V-RT-CROSS` (12) are excluded from these percentages
by construction; do not re-add them to reach 501,561.
""")

md(r"""
## B2 — RT length distribution by family

* **Question.** Do the major RT families occupy distinguishable protein-length regimes, and does
  the recomputed distribution match the landed g4 baseline?
* **Unit.** Exact RT protein (`V-RT-SINGLE`), one length per distinct sequence.
* **Denominator.** `V-RT-SINGLE` exact RTs of that family label. Families with n < 30 get no
  Tukey fences (the g4 rule) and are omitted from the plot.
* **Data.** `rt_family_baseline_v1` → `family_label`, `rt_aa_len`, `view`.
""")

code(r'''
lens = cache("B2_rt_length_by_family", """
    SELECT family_label, count(*) AS n_exact_rt,
           min(rt_aa_len) AS min,
           quantile_cont(rt_aa_len, 0.25) AS q25,
           quantile_cont(rt_aa_len, 0.50) AS median,
           quantile_cont(rt_aa_len, 0.75) AS q75,
           max(rt_aa_len) AS max,
           avg(rt_aa_len) AS mean
    FROM rt_family_baseline WHERE view = 'V-RT-SINGLE'
    GROUP BY 1 ORDER BY n_exact_rt DESC
""")
lens["iqr"] = lens.q75 - lens.q25
save(lens, "B2_rt_length_by_family")
display(lens.head(14).round(1))

print("\nagainst g4_rt_length_by_family:")
g4 = gate_table("dbchar_g4_family_baseline", "g4_rt_length_by_family")
m = lens.merge(g4[["family_label", "n_exact_rt", "median", "q25", "q75"]],
               on="family_label", suffixes=("", "_g4"))
bad = m[(m["median"] != m["median_g4"]) | (m.n_exact_rt != m.n_exact_rt_g4)]
print(f"  [{'MATCH' if bad.empty else ' DIFF'}] {len(m)} families compared on (n, median, q25, q75); "
      f"{len(bad)} disagree")
check("Retron median aa", float(lens.loc[lens.family_label == "Retron", "median"].iloc[0]), "retron_median_len")
check("RVT-GII median aa", float(lens.loc[lens.family_label == "RVT-GII", "median"].iloc[0]), "gii_median_len")

multi_len = Q("""SELECT count(*) AS n, quantile_cont(rt_aa_len, 0.50) AS median_aa_len
                 FROM rt_family_baseline WHERE view = 'V-RT-MULTI'""")
print(f"\nMULTI stratum (held out): n={int(multi_len.n[0]):,}, median {multi_len.median_aa_len[0]:.0f} aa")
''')

code(r'''
L = pd.read_csv(TABLES / "B2_rt_length_by_family.tsv", sep="\t")
L = L[L.n_exact_rt >= 30].head(14).iloc[::-1]

stats = [dict(label=f"{r.family_label}  (n={int(r.n_exact_rt):,})", med=r["median"],
              q1=r.q25, q3=r.q75,
              whislo=max(r["min"], r.q25 - 1.5 * (r.q75 - r.q25)),
              whishi=min(r["max"], r.q75 + 1.5 * (r.q75 - r.q25)), fliers=[])
         for _, r in L.iterrows()]

fig, ax = plt.subplots(figsize=(7.6, 5.0))
bp = ax.bxp(stats, vert=False, showfliers=False, patch_artist=True, widths=0.62)
for p in bp["boxes"]:
    p.set_facecolor("#3b6ea5"); p.set_alpha(0.75); p.set_edgecolor("#24425f")
for k in ("whiskers", "caps"):
    for p in bp[k]: p.set_color("#24425f")
for p in bp["medians"]: p.set_color("#f2c14e"); p.set_linewidth(1.8)
ax.set_xlabel("RT protein length (aa) — box = IQR, whiskers = Tukey 1.5×IQR clipped to observed range")
ax.set_title("B2 — RT length by family, V-RT-SINGLE exact proteins", fontsize=9.5, loc="left")
savefig(fig, "B2_rt_length_by_family", pop=['RT-BASE-1F']); plt.show()
''')

md(r"""
**Interpretation.** The families separate but overlap heavily: Retron sits at a median 342 aa,
RVT-GII at 407 aa, and several ungrouped families (RVT-UG5, RVT-UG8) are far longer — these are
the domain-fusion families. Length alone is not a classifier; the IQRs of the three largest
families all intersect.

**Caveat.** The extremes are real records, not outliers to be trimmed: maxima above 9,000 aa occur
in Retron and RVT-GII and are retained (`g4_rt_length_named_outliers.tsv`). Length is also
confounded by completeness — a partial call is short by construction — which is why B3 reports
completeness on the same denominator. `MULTI` proteins are *shorter* than single-family ones
(median 283 aa), and HMM score scales with length, so part of the MULTI label tie may be a length
effect (see G).
""")

md(r"""
## B3 — Completeness / partiality by family

* **Question.** How much of each family's protein-length distribution is carried by calls that are
  not complete ORFs?
* **Unit.** Exact RT protein (`V-RT-SINGLE`).
* **Denominator.** `V-RT-SINGLE` exact RTs of that family label.
* **Data.** `rt_family_baseline_v1` → `family_label`, `completeness_class`, `view`, `rt_aa_len`.
  `completeness_class` aggregates the Prodigal partial flags over all records of that exact
  sequence: **a missing flag is `no_completeness_evidence`, never `partial`** (g4 rule).
""")

code(r'''
comp = cache("B3_completeness_by_family", """
    SELECT family_label, completeness_class, count(*) AS n_exact_rt,
           quantile_cont(rt_aa_len, 0.50) AS median_aa_len
    FROM rt_family_baseline WHERE view = 'V-RT-SINGLE'
    GROUP BY 1, 2
""")
piv = comp.pivot_table(index="family_label", columns="completeness_class",
                       values="n_exact_rt", fill_value=0)
piv["n_family"] = piv.sum(axis=1)
pct = (100 * piv.drop(columns="n_family").div(piv.n_family, axis=0)).round(2)
pct["n_family"] = piv.n_family
pct = pct.sort_values("n_family", ascending=False)
display(pct.head(15))

overall = Q("""SELECT completeness_class, count(*) AS n FROM rt_family_baseline GROUP BY 1 ORDER BY 2 DESC""")
overall["pct_of_all_exact_rt"] = (100 * overall.n / overall.n.sum()).round(2)
print("\nover all 501,561 exact RTs (all views):"); display(overall)

print("\nagainst g4_completeness_by_family (n_exact_rt per family x class):")
g4c = gate_table("dbchar_g4_family_baseline", "g4_completeness_by_family")
mm = comp.merge(g4c[["family_label", "completeness_class", "n_exact_rt"]],
                on=["family_label", "completeness_class"], suffixes=("", "_g4"))
print(f"  [{'MATCH' if (mm.n_exact_rt == mm.n_exact_rt_g4).all() else ' DIFF'}] "
      f"{len(mm)} (family, class) cells compared")
''')

code(r'''
P = pd.read_csv(TABLES / "B3_completeness_by_family.tsv", sep="\t")
piv = P.pivot_table(index="family_label", columns="completeness_class", values="n_exact_rt", fill_value=0)
piv = piv.loc[piv.sum(axis=1).sort_values(ascending=False).index[:14]].iloc[::-1]
frac = 100 * piv.div(piv.sum(axis=1), axis=0)
order = [c for c in ["all_complete", "mixed_or_codon_evidence", "all_partial",
                     "no_completeness_evidence"] if c in frac.columns]
colors = {"all_complete": "#3b6ea5", "mixed_or_codon_evidence": "#7fa8cc",
          "all_partial": "#b5533b", "no_completeness_evidence": "#9a9a9a"}

fig, ax = plt.subplots(figsize=(7.8, 4.4))
left = np.zeros(len(frac))
for c in order:
    ax.barh(frac.index, frac[c], left=left, color=colors[c], label=c, height=0.7)
    left += frac[c].values
ax.set_xlim(0, 100); ax.set_xlabel("% of that family's V-RT-SINGLE exact RTs")
ax.legend(fontsize=8, ncol=2, loc="lower right", framealpha=0.9)
ax.set_title("B3 — completeness composition by family", fontsize=9.5, loc="left")
savefig(fig, "B3_completeness_by_family", pop=['RT-BASE-1F']); plt.show()
''')

md(r"""
**Interpretation.** Partiality is not evenly distributed: roughly a quarter of all exact RTs are
`all_partial`, but the fraction varies strongly by family, and the families with the most partial
calls are also the ones whose length medians sit lowest. Any family-level length comparison should
therefore be repeated on `all_complete` only before it is interpreted as a protein-architecture
difference.

**Caveat.** `completeness_class` describes the *calls*, not the organism: a partial flag usually
means the ORF ran into a contig end, which is an assembly property. `no_completeness_evidence`
(absent Prodigal flag) is deliberately its own class and must not be read as "complete".
""")
