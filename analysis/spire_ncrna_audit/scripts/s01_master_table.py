"""s01 — master RT-system table over the project's EXISTING retron population.

Unit: one physical locus (`physical_locus_key`) carrying >= 1 first-copy record whose
file_label = 'Retron' (dbchar_g2 population; SPIRE defines nothing here).

Every row gets three mutually explicit, independently derived fields:
  nc_status        A_T3 | A_T2 | A_T1 | A_NONCANON | B_NO_CM_CALL      (from rt_ncrna_pairs_v1)
  evidence_stratum S1..S5                                               (from rt_tool_calls_v1)
  suitability      OK | C_* reason                                      (method requirements)
plus the retained reference-ncRNA fields for A rows (EVALUATION ONLY — never an input to
prediction). Output: ARIS_OUTPUT/.../master/master_rt_system.parquet + summary TSVs.
"""
import hashlib
import duckdb
import pandas as pd
from common import (DERIVED, SCRATCH, TABLES, T1, T2, T3, T4_RECURRENCE, DF_MULTI, DF_FUSED,
                    PAD_MULTI, PAD_FUSED, PAD_NCDEP, HARMONISE, WINDOW_BP)

OUT = SCRATCH / 'master'
OUT.mkdir(parents=True, exist_ok=True)
c = duckdb.connect()
c.execute('PRAGMA threads=24')
for v in ['rt_records_v1', 'rt_tool_calls_v1', 'rt_ncrna_pairs_v1',
          'rt_ncrna_exact_pair_recurrence_v1', 'rt_ncrna_oriented_v1', 'rt_family_baseline_v1']:
    c.execute(f"CREATE VIEW {v} AS SELECT * FROM read_parquet('{DERIVED}/{v}.parquet')")

# ---- records: Retron, first copy ------------------------------------------------------------
c.execute("""
CREATE TABLE rec AS
SELECT r.record_key, r.physical_locus_key, r.locus_key, r.rt_system_id, r.rt_seq_hash,
       r.contig, r.rt_start, r.rt_end, r.rt_strand, r.rt_aa_len, r.win_start, r.win_end,
       r.true_start_clipped, r.clipped_end_flag, r.rt_at_window_edge, r.rt_in_window,
       r.bt_status, r.elig_geometry, r.elig_rt_coords, r.multilabel, r.n_ncrna,
       r.genome_id_norm, r.source_database, r.taxonomy_system, r.tax_phylum, r.tax_genus,
       r.tax_species, r.source_file, r.byte_offset, r.byte_len, r.window_dna_sha256,
       t.by_myRT, t.by_PADLOC, t.by_DefenseFinder, t.subtypes_defensefinder, t.subtypes_padloc
FROM rt_records_v1 r LEFT JOIN rt_tool_calls_v1 t USING (record_key)
WHERE r.file_label = 'Retron' AND r.is_first_copy
""")

# ---- best existing pair per locus (reference, evaluation only) ------------------------------
c.execute(f"""
CREATE TABLE pl AS
SELECT p.*, CASE WHEN {T3} THEN 3 WHEN {T2} THEN 2 WHEN {T1} THEN 1 ELSE 0 END AS tier_rank
FROM rt_ncrna_pairs_v1 p
WHERE p.file_label = 'Retron' AND p.record_key IN (SELECT record_key FROM rec)
""")
c.execute("""
CREATE TABLE best AS
SELECT * EXCLUDE (rn) FROM (
  SELECT pl.*, row_number() OVER (PARTITION BY physical_locus_key
         ORDER BY tier_rank DESC, evalue ASC, record_key, ncrna_idx) rn FROM pl) WHERE rn = 1
""")
c.execute("""
CREATE TABLE pl_agg AS
SELECT physical_locus_key, count(*) n_cm_placements, count(DISTINCT nc_seq_hash) n_cm_ncrna_seqs,
       count(DISTINCT detection_model) n_cm_models,
       count(DISTINCT record_key) n_records_with_cm_call
FROM pl GROUP BY 1
""")

# ---- per-locus tool evidence across all its Retron records ----------------------------------
tools = c.execute("""
SELECT physical_locus_key,
       bool_or(coalesce(by_myRT,false)) any_myRT, bool_or(coalesce(by_PADLOC,false)) any_PADLOC,
       bool_or(coalesce(by_DefenseFinder,false)) any_DF,
       string_agg(DISTINCT nullif(subtypes_defensefinder,''), '|') df_labels,
       string_agg(DISTINCT nullif(subtypes_padloc,''), '|') padloc_labels,
       count(*) n_records, count(DISTINCT genome_id_norm) n_genomes,
       bool_or(multilabel) any_multilabel, count(DISTINCT rt_seq_hash) n_rt_hashes,
       sum((n_ncrna > 0)::int) n_records_with_ncrna
FROM rec GROUP BY 1
""").df()


def split(s):
    return set() if s is None or pd.isna(s) else {x for x in str(s).split('|') if x}


def stratum(row):
    df, pad = split(row.df_labels), split(row.padloc_labels)
    ctx = int(bool(df & DF_MULTI)) + int(bool(pad & PAD_MULTI))
    if ctx == 2:
        return 'S1_SYSTEM_CONTEXT_2TOOLS'
    if ctx == 1:
        return 'S2_SYSTEM_CONTEXT_1TOOL'
    if (df & DF_FUSED) or (pad & PAD_FUSED):
        return 'S3_FUSED_RT_RULE_ONLY'
    if pad & PAD_NCDEP:
        return 'S4_PADLOC_NCRNA_DEPENDENT_RULE_ONLY'
    return 'S5_SEQUENCE_ONLY'


def type_label(row):
    """ncRNA-blind type label for homolog grouping: DefenseFinder first, then PADLOC protein
    rules. PADLOC Ec107-like/outgroup are excluded because their rule consumes the ncRNA."""
    df = {HARMONISE[x] for x in split(row.df_labels) if x in HARMONISE}
    pad = {HARMONISE[x] for x in split(row.padloc_labels) if x in HARMONISE}
    if len(df) == 1:
        lab, src = next(iter(df)), 'DefenseFinder'
    elif len(df) == 0 and len(pad) == 1:
        lab, src = next(iter(pad)), 'PADLOC'
    elif len(df) > 1 or len(pad) > 1:
        return 'AMBIGUOUS', 'multiple', True
    else:
        return 'UNLABELLED', 'none', False
    conflict = bool(df and pad and df != pad)
    return lab, src, conflict


tools['evidence_stratum'] = tools.apply(stratum, axis=1)
tl = tools.apply(type_label, axis=1, result_type='expand')
tools[['type_label', 'type_label_source', 'type_label_conflict']] = tl
c.register('tools_df', tools)

# ---- representative record: carrier of the best pair (A) else lowest record_key ------------
c.execute("""
CREATE TABLE rep AS
SELECT * EXCLUDE (rn) FROM (
  SELECT rec.*, row_number() OVER (PARTITION BY rec.physical_locus_key ORDER BY
         (rec.record_key = b.record_key) DESC NULLS LAST, rec.elig_geometry DESC,
         rec.record_key) rn
  FROM rec LEFT JOIN best b USING (physical_locus_key)) WHERE rn = 1
""")

m = c.execute(f"""
SELECT rep.*, t.* EXCLUDE (physical_locus_key), a.* EXCLUDE (physical_locus_key),
       b.record_key AS ref_record_key, b.ncrna_idx AS ref_ncrna_idx, b.nc_seq_hash AS ref_nc_seq_hash,
       b.nc_seq_len AS ref_nc_len, b.nc_start AS ref_nc_start, b.nc_end AS ref_nc_end,
       b.nc_strand AS ref_nc_strand, b.same_strand AS ref_same_strand, b.direction AS ref_direction,
       b.signed_distance_bp AS ref_signed_distance_bp, b.n_cds_between AS ref_n_cds_between,
       b.overlaps_rt_cds AS ref_overlaps_rt_cds, b.overlaps_any_cds AS ref_overlaps_any_cds,
       b.detection_model AS ref_detection_model, b.evalue AS ref_evalue, b.score AS ref_score,
       b.canonical AS ref_canonical, b.tier_rank AS ref_tier_rank, b.multiplicity_class AS ref_multiplicity,
       rc.recurrence_class AS ref_recurrence_class,
       fb.family_label, fb.completeness_class
FROM rep JOIN tools_df t USING (physical_locus_key)
LEFT JOIN pl_agg a USING (physical_locus_key)
LEFT JOIN best b USING (physical_locus_key)
LEFT JOIN rt_ncrna_exact_pair_recurrence_v1 rc
       ON rc.rt_seq_hash = b.rt_seq_hash AND rc.nc_seq_hash = b.nc_seq_hash
LEFT JOIN rt_family_baseline_v1 fb ON fb.rt_seq_hash = rep.rt_seq_hash
""").df()

m['nc_status'] = 'B_NO_CM_CALL'
has = m.ref_nc_seq_hash.notna()
m.loc[has, 'nc_status'] = m.loc[has, 'ref_tier_rank'].map(
    {3: 'A_T3', 2: 'A_T2', 1: 'A_T1', 0: 'A_NONCANON'})
m['ref_T4'] = (m.nc_status == 'A_T3') & m.ref_recurrence_class.isin(T4_RECURRENCE)
m['cm_call_inconsistent_across_records'] = has & (m.n_records_with_ncrna < m.n_records)

# ---- SPIRE-arm window: WINDOW_BP immediately 5' of the RT start codon, RT strand -------------
plus = m.rt_strand == '+'
m['up_start'] = m.rt_start.where(~plus, m.rt_start - WINDOW_BP)
m.loc[~plus, 'up_start'] = m.loc[~plus, 'rt_end'] + 1
m['up_end'] = (m.rt_start - 1).where(plus, m.rt_end + WINDOW_BP)
m['up_within_record_window'] = (m.up_start >= m.win_start) & (m.up_end <= m.win_end)


def suitability(r):
    if not r.elig_rt_coords or pd.isna(r.rt_start):
        return 'C_RT_COORDINATES_INVALID'
    if not r.rt_in_window:
        return 'C_RT_NOT_IN_WINDOW'
    if not r.up_within_record_window:
        return ('C_CONTIG_EDGE_TRUNCATED_UPSTREAM' if (r.true_start_clipped or r.clipped_end_flag)
                else 'C_UPSTREAM_OUTSIDE_RECORD_WINDOW')
    if r.any_multilabel or r.n_rt_hashes > 1:
        return 'C_AMBIGUOUS_RT_SYSTEM_IDENTITY'
    return 'OK'


m['suitability'] = m.apply(suitability, axis=1)


def ref_in_window(r):
    if pd.isna(r.ref_nc_start):
        return None
    ov = min(r.ref_nc_end, r.up_end) - max(r.ref_nc_start, r.up_start) + 1
    return max(0, ov) / (r.ref_nc_end - r.ref_nc_start + 1)


m['ref_frac_in_spire_window'] = m.apply(ref_in_window, axis=1)

m = m.sort_values('physical_locus_key').reset_index(drop=True)
path = OUT / 'master_rt_system.parquet'
m.to_parquet(path, index=False)
sha = hashlib.sha256(path.read_bytes()).hexdigest()
print(f'{len(m):,} loci -> {path}  sha256={sha}')

TABLES.mkdir(parents=True, exist_ok=True)
summ = (m.groupby(['nc_status', 'evidence_stratum', 'suitability'], dropna=False)
          .agg(n_physical_loci=('physical_locus_key', 'size'),
               n_exact_rt=('rt_seq_hash', 'nunique'))
          .reset_index())
summ.to_csv(TABLES / 'M1_master_status_by_stratum.tsv', sep='\t', index=False)
(m.groupby(['type_label', 'nc_status']).size().unstack(fill_value=0)
   .to_csv(TABLES / 'M2_type_label_by_nc_status.tsv', sep='\t'))
pd.DataFrame([{'file': str(path), 'rows': len(m), 'sha256': sha,
               'unit': 'physical locus with >=1 first-copy Retron record'}]).to_csv(
    TABLES / 'M0_master_manifest.tsv', sep='\t', index=False)
print(m.nc_status.value_counts().to_string())
print(m.evidence_stratum.value_counts().to_string())
print(m.suitability.value_counts().to_string())
