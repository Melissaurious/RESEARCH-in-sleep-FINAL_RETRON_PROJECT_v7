"""z01 — Z6 locus classes + RT homolog-group table (DESIGN §1–5). No reference coordinates read.

Outputs: ARIS_OUTPUT/spire_ncrna_audit/z6/z6_loci.parquet; tables/Z6_CHECKS.tsv, LOCUS_CLASSES.tsv,
GROUPS.tsv, GROUP_FLAGS_SUMMARY.tsv.
"""
import hashlib
import sys
from pathlib import Path
import duckdb
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from common import DERIVED, SCRATCH, DF_MULTI, DF_FUSED, PAD_MULTI, PAD_FUSED, PAD_NCDEP, HARMONISE  # noqa: E402

Z6 = Path('/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-dbchar-workbench/ARIS_OUTPUT/dbchar_workbench/tables/'
          'Z6_locus_matched_status.parquet')
Z6_COMMIT = '12ea561a5565aca29eeaacbfe8863dc244838fa3'
HERE = Path(__file__).resolve().parents[1]
T = HERE / 'tables'
OUT = SCRATCH / 'z6'
OUT.mkdir(parents=True, exist_ok=True)

c = duckdb.connect()
c.execute('PRAGMA threads=24')
c.execute(f"CREATE VIEW z AS SELECT * FROM read_parquet('{Z6}')")

# ---- the five frozen checks ------------------------------------------------------------------
chk = c.execute("""SELECT count(*) loci,
   sum((ncrna_status <> 'NO_NCRNA_CALL_IN_RETAINED_WINDOW')::int) AS n_matched,
   sum((ncrna_status = 'NO_NCRNA_CALL_IN_RETAINED_WINDOW')::int) AS n_unmatched,
   count(DISTINCT rt_seq_hash) exact_rt,
   count(DISTINCT rt_seq_hash) FILTER (WHERE ncrna_status <> 'NO_NCRNA_CALL_IN_RETAINED_WINDOW') exact_rt_matched
   FROM z""").df().T.reset_index()
chk.columns = ['check', 'observed']
chk['expected'] = [630741, 332769, 297972, 76381, 28838]
chk['reproduced'] = chk.observed == chk.expected
chk['z6_sha256'] = hashlib.sha256(Z6.read_bytes()).hexdigest()
chk['z6_commit'] = Z6_COMMIT
chk.to_csv(T / 'Z6_CHECKS.tsv', sep='\t', index=False)
assert chk.reproduced.all(), chk

# ---- tool evidence by locus (registered rt_tool_calls_v1) --------------------------------------
tools = c.execute(f"""SELECT locus_key,
   string_agg(DISTINCT nullif(subtypes_defensefinder,''), '|') df_labels,
   string_agg(DISTINCT nullif(subtypes_padloc,''), '|') padloc_labels
   FROM read_parquet('{DERIVED}/rt_tool_calls_v1.parquet')
   WHERE locus_key IN (SELECT locus_key FROM z) GROUP BY 1""").df()


def split(s):
    return set() if s is None or pd.isna(s) else {x for x in str(s).split('|') if x}


def stratum(df, pad):
    ctx = int(bool(df & DF_MULTI)) + int(bool(pad & PAD_MULTI))
    if ctx == 2:
        return 'S1'
    if ctx == 1:
        return 'S2'
    if (df & DF_FUSED) or (pad & PAD_FUSED):
        return 'S3'
    if pad & PAD_NCDEP:
        return 'S4'
    return 'S5'


def tlabel(df, pad):
    d = {HARMONISE[x] for x in df if x in HARMONISE}
    p = {HARMONISE[x] for x in pad if x in HARMONISE}
    if len(d) == 1:
        return next(iter(d))
    if not d and len(p) == 1:
        return next(iter(p))
    return 'AMBIGUOUS' if (len(d) > 1 or len(p) > 1) else 'UNLABELLED'


tools['_df'] = tools.df_labels.map(split)
tools['_pad'] = tools.padloc_labels.map(split)
tools['stratum'] = [stratum(a, b) for a, b in zip(tools._df, tools._pad)]
tools['type_label'] = [tlabel(a, b) for a, b in zip(tools._df, tools._pad)]
tools['padloc_xii'] = tools._pad.map(lambda s: 'retron_XII' in s)
tools = tools.drop(columns=['_df', '_pad'])
c.register('tools', tools)

# ---- homolog clusters ---------------------------------------------------------------------------
for tag in ['RT50', 'RT90']:
    c.execute(f"""CREATE TABLE {tag} AS SELECT column0 rep, column1 mem
                  FROM read_csv('{SCRATCH}/s02/{tag}_cluster.tsv', delim='\t', header=false)""")

L = c.execute(f"""
SELECT z.locus_key, z.physical_locus_key, z.record_key_any, z.rt_seq_hash, a.rep rt50, b.rep rt90,
       z.genome_id_norm, z.contig_norm, z.source_database, z.taxonomy_system, z.tax_domain, z.tax_species,
       r.tax_genus, r.tax_phylum, z.rt_start, z.rt_end, z.rt_strand, z.win_start, z.win_end,
       z.bp_available_upstream, z.any_window_clipped, z.rt_in_window, z.window_len_consistent,
       z.window_inverted, z.rt_seq_wellformed, z.rt_aa_len, z.ncrna_status, z.evidence_tier,
       z.detection_models, z.n_ncrna_calls,
       r.source_file, r.byte_offset, r.byte_len,
       coalesce(t.stratum, 'S5') stratum, coalesce(t.type_label, 'UNLABELLED') type_label,
       coalesce(t.padloc_xii, false) padloc_xii
FROM z LEFT JOIN RT50 a ON a.mem = z.rt_seq_hash LEFT JOIN RT90 b ON b.mem = z.rt_seq_hash
LEFT JOIN tools t USING (locus_key)
LEFT JOIN read_parquet('{DERIVED}/rt_records_v1.parquet') r ON r.record_key = z.record_key_any
""").df()


def ctx(r):
    if not (r.rt_in_window and r.window_len_consistent and not r.window_inverted and r.rt_seq_wellformed):
        return 'UNUSABLE_RT_OR_WINDOW'
    if r.bp_available_upstream >= 1000:
        return 'ADEQUATE'
    return 'LIMITED_LT200' if r.bp_available_upstream < 200 else 'LIMITED_200_1000'


L['context'] = [ctx(r) for r in L.itertuples()]
L['locus_class'] = 'UNMATCHED_' + L.context
m = L.ncrna_status != 'NO_NCRNA_CALL_IN_RETAINED_WINDOW'
L.loc[m & L.evidence_tier.isin(['T3_HIGH_CONFIDENCE', 'T2_ARCHITECTURE']), 'locus_class'] = 'MATCHED_LOCAL_' + L.context
L.loc[m & (L.evidence_tier == 'T1_OBSERVED'), 'locus_class'] = 'MATCHED_T1_' + L.context
L.to_parquet(OUT / 'z6_loci.parquet', index=False)

cls = (L.groupby(['locus_class', 'stratum']).agg(loci=('locus_key', 'size'), exact_rt=('rt_seq_hash', 'nunique'),
                                                rt90=('rt90', 'nunique'), rt50=('rt50', 'nunique'))
         .reset_index())
cls.to_csv(T / 'LOCUS_CLASSES.tsv', sep='\t', index=False)

# ---- group table --------------------------------------------------------------------------------
c.register('L', L)
G = c.execute("""
SELECT rt50,
  count(*) loci, count(DISTINCT rt_seq_hash) exact_rt, count(DISTINCT rt90) rt90,
  round(count(*) / count(DISTINCT rt90), 1) loci_per_rt90,
  count(DISTINCT genome_id_norm) genomes,
  count(DISTINCT taxonomy_system || ':' || tax_species) species, count(DISTINCT tax_genus) genera,
  count(DISTINCT tax_phylum) phyla, string_agg(DISTINCT source_database, '|') sources,
  string_agg(DISTINCT type_label, '|') type_labels,
  mode(type_label) type_label_modal,
  string_agg(DISTINCT detection_models, '|') cm_models,
  count(*) FILTER (WHERE locus_class LIKE 'MATCHED_LOCAL%') matched_local,
  count(*) FILTER (WHERE locus_class LIKE 'MATCHED_T1%') matched_t1,
  count(*) FILTER (WHERE locus_class = 'UNMATCHED_ADEQUATE') unmatched_adequate,
  count(*) FILTER (WHERE locus_class LIKE 'UNMATCHED_LIMITED%') unmatched_limited,
  count(*) FILTER (WHERE locus_class LIKE '%UNUSABLE%') unusable,
  count(DISTINCT rt90) FILTER (WHERE locus_class = 'MATCHED_LOCAL_ADEQUATE' AND stratum IN ('S1','S2','S3')) rt90_pos_pool,
  count(DISTINCT rt90) FILTER (WHERE locus_class = 'MATCHED_LOCAL_ADEQUATE' AND stratum IN ('S1','S2')) rt90_matched_s12,
  count(DISTINCT rt90) FILTER (WHERE locus_class = 'UNMATCHED_ADEQUATE' AND stratum IN ('S1','S2')) rt90_unmatched_s12,
  count(DISTINCT rt90) FILTER (WHERE locus_class = 'UNMATCHED_ADEQUATE' AND stratum = 'S3') rt90_unmatched_s3,
  count(DISTINCT rt90) FILTER (WHERE locus_class = 'UNMATCHED_ADEQUATE') rt90_unmatched_any,
  sum(padloc_xii::int) padloc_xii_loci
FROM L GROUP BY rt50""").df()
G['any_matched'] = (G.matched_local + G.matched_t1) > 0
G['POS_FEASIBLE'] = G.rt90_pos_pool >= 6
G['MIXED'] = (G.rt90_matched_s12 >= 4) & (G.rt90_unmatched_s12 >= 4)
G['DENOVO_FEASIBLE_S12'] = ~G.any_matched & (G.rt90_unmatched_s12 >= 6)
G['DENOVO_FEASIBLE_S3'] = ~G.any_matched & (G.rt90_unmatched_s3 >= 6)
G = G.sort_values('loci', ascending=False)
G.to_csv(T / 'GROUPS.tsv', sep='\t', index=False)

rows = []
for flag in ['POS_FEASIBLE', 'MIXED', 'DENOVO_FEASIBLE_S12', 'DENOVO_FEASIBLE_S3']:
    g = G[G[flag]]
    rows.append(dict(flag=flag, groups=len(g), loci=int(g.loci.sum()), exact_rt=int(g.exact_rt.sum()),
                     rt90=int(g.rt90.sum()), unmatched_adequate=int(g.unmatched_adequate.sum()),
                     matched_local=int(g.matched_local.sum()),
                     type_labels=';'.join(sorted(set('|'.join(g.type_labels.dropna()).split('|'))))))
rows.append(dict(flag='ALL_GROUPS', groups=len(G), loci=int(G.loci.sum()), exact_rt=int(G.exact_rt.sum()),
                 rt90=int(G.rt90.sum()), unmatched_adequate=int(G.unmatched_adequate.sum()),
                 matched_local=int(G.matched_local.sum())))
pd.DataFrame(rows).to_csv(T / 'GROUP_FLAGS_SUMMARY.tsv', sep='\t', index=False)
print(chk.to_string())
print(cls.groupby('locus_class')[['loci', 'exact_rt', 'rt90']].sum().to_string())
print(pd.DataFrame(rows).to_string())
