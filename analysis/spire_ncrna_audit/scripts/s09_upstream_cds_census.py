"""s09 — how often is the RT-proximal upstream covered by an annotated non-RT CDS? (counts only)

Motivation (post-hoc, from the pilot): the corpus CM route searches intergenic regions only, so a
spurious small ORF over the msr/msd region hides a retron ncRNA from it. For each suitable locus's
representative record: max coverage of RT-relative −120…−1 by any non-RT CDS (either strand).
"""
import duckdb
from common import SCRATCH, DERIVED, TABLES

c = duckdb.connect()
c.execute('PRAGMA threads=24')
c.execute(f"""CREATE TABLE rep AS SELECT record_key, source_file, line_no, rt_start, rt_end, rt_strand, nc_status,
              evidence_stratum FROM read_parquet('{SCRATCH}/master/master_rt_system.parquet') m
              JOIN (SELECT record_key, line_no FROM read_parquet('{DERIVED}/rt_records_v1.parquet')) r USING (record_key)
              WHERE suitability = 'OK'""")
c.execute(f"""CREATE TABLE cov AS
  SELECT rep.record_key, max(greatest(0, least(-1, hi) - greatest(-120, lo) + 1)) AS cov_nt
  FROM rep JOIN (
      SELECT w.source_file, w.line_no, w.cds_start, w.cds_end FROM read_parquet('{DERIVED}/rt_window_cds_v1.parquet') w
      WHERE NOT w.is_rt_gene) w USING (source_file, line_no),
  LATERAL (SELECT CASE WHEN rep.rt_strand = '+' THEN w.cds_start - rep.rt_start ELSE rep.rt_end - w.cds_end END lo,
                  CASE WHEN rep.rt_strand = '+' THEN w.cds_end - rep.rt_start ELSE rep.rt_end - w.cds_start END hi)
  GROUP BY 1""")
out = c.execute("""
  SELECT CASE WHEN nc_status LIKE 'A_T%' AND nc_status IN ('A_T3','A_T2') THEN 'A_local (T2/T3)'
              WHEN nc_status = 'B_NO_CM_CALL' THEN 'B_no_current_ncRNA_call' ELSE 'A_other' END cohort,
         evidence_stratum, count(*) n_loci,
         sum((coalesce(cov_nt,0) >= 60)::int) n_upstream_half_covered_by_cds,
         round(avg((coalesce(cov_nt,0) >= 60)::int), 4) frac_upstream_half_covered_by_cds
  FROM rep LEFT JOIN cov USING (record_key) GROUP BY ALL ORDER BY ALL""").df()
out.to_csv(TABLES / 'SCALE_upstream_cds_cover.tsv', sep='\t', index=False)
print(out.to_string())
