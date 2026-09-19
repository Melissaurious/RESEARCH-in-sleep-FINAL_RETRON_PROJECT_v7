"""s07 — scale-up census over the eligible A+B universe (counts only; no method is run).

Eligible homolog set (upper bound): RT50 cluster with >= 5 distinct RT90 clusters among
suitable loci of the cohort. The exact count also needs >= 5 distinct windows; that is checked
only on the benchmark (window extraction is not run catalogue-wide here).
"""
import duckdb
import pandas as pd
from common import SCRATCH, TABLES

c = duckdb.connect()
c.execute(f"CREATE VIEW m AS SELECT * FROM read_parquet('{SCRATCH}/master/master_rt_system.parquet')")
for tag in ['RT50', 'RT90']:
    c.execute(f"""CREATE TABLE {tag} AS SELECT column0 rep, column1 mem
                  FROM read_csv('{SCRATCH}/s02/{tag}_cluster.tsv', delim='\t', header=false)""")
c.execute("""CREATE TABLE mm AS SELECT m.*, a.rep rt50, b.rep rt90 FROM m
             LEFT JOIN RT50 a ON a.mem = m.rt_seq_hash LEFT JOIN RT90 b ON b.mem = m.rt_seq_hash""")
c.execute("""CREATE TABLE mm2 AS SELECT *, CASE
     WHEN nc_status IN ('A_T3','A_T2') THEN 'A_local (T2/T3)'
     WHEN nc_status = 'A_T1' THEN 'A_T1 (CM call beyond architecture rules)'
     WHEN nc_status = 'A_NONCANON' THEN 'A_noncanonical'
     ELSE 'B_no_current_ncRNA_call' END AS cohort FROM mm""")

pop = c.execute("""
  SELECT cohort, evidence_stratum, suitability, count(*) n_physical_loci,
         count(DISTINCT rt_seq_hash) n_exact_rt, count(DISTINCT rt50) n_rt50, count(DISTINCT rt90) n_rt90
  FROM mm2 GROUP BY ALL ORDER BY ALL""").df()
pop.to_csv(TABLES / 'SCALE_population_census.tsv', sep='\t', index=False)

sets = c.execute("""
  WITH s AS (SELECT cohort, CASE WHEN evidence_stratum LIKE 'S4%' THEN 'S4 (excluded: ncRNA-dependent)'
                                 ELSE evidence_stratum END stratum, rt50,
                    count(*) n_loci, count(DISTINCT rt90) n_rt90
             FROM mm2 WHERE suitability = 'OK' GROUP BY ALL)
  SELECT cohort, stratum,
         count(*) n_rt50_clusters,
         count(*) FILTER (WHERE n_rt90 >= 5) n_sets_eligible_ub,
         sum(n_loci) FILTER (WHERE n_rt90 >= 5) loci_in_eligible_sets,
         sum(n_loci) FILTER (WHERE n_rt90 < 5) loci_insufficient_homologs,
         sum(least(n_rt90, 40)) FILTER (WHERE n_rt90 >= 5) windows_if_one_set_per_cluster,
         sum(n_rt90) FILTER (WHERE n_rt90 >= 5) windows_if_all_rt90_reps
  FROM s GROUP BY ALL ORDER BY ALL""").df()
sets.to_csv(TABLES / 'SCALE_homolog_sets.tsv', sep='\t', index=False)
print(pop.groupby(['cohort', 'suitability']).n_physical_loci.sum().to_string())
print(sets.to_string())
