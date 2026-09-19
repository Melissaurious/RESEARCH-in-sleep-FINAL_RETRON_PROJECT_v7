"""r01 — Round-2 group split (DEV / HELDOUT) and frozen member sets. Run once, then hash.

Split unit: RT50 homolog group; universe: the 173 POS_FEASIBLE groups of Z6_DENOVO/tables/GROUPS.tsv.
Allocation (declared before any Round-2 run):
  1. every group used in any Round-1 Z6 set is forced to DEV (its outcomes were seen);
  2. remaining groups are stratified by (modal type label × depth bin: 6–9 / 10–19 / ≥20 RT90);
  3. within a stratum, order by sha256("r2-split-v1|" + rt50); rank r → DEV if r % 5 in {0, 2}, else HELDOUT
     (≈ 40 % DEV; a 1-group stratum goes to DEV, a 2-group stratum splits 1/1).
Balance on RT divergence (RT70/RT90), deposition size, ncRNA length and RT–ncRNA distance is REPORTED,
not stratified. Reference-derived group summaries go to GROUP_REFSTATS_SEALED.tsv, which no discovery
script reads.

Members per group: MATCHED_LOCAL_ADEQUATE, stratum S1–S3, bp_available_upstream ≥ 1900 (so the real and the
distal-control windows exist for the SAME loci), one locus per RT90, ≤ 20, order sha256("r2-members-v1|"+locus_key).
Windows (RT-relative, RT strand): W700 = −600…+100, control −1900…−1201; W500 = −400…+100, control −1500…−1001.
Halves (stability): groups with ≥ 12 members → A = even hash ranks, B = odd.
"""
import hashlib
import sys
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / 'scripts'))
from common import SCRATCH, DERIVED  # noqa: E402
from windows import window  # noqa: E402

T = HERE / 'tables'
OUT = SCRATCH / 'r2/sets'
OUT.mkdir(parents=True, exist_ok=True)
Z6D = HERE.parent / 'Z6_DENOVO/tables'
WIN = {'W700': ((-600, 100), (-1900, -1201)), 'W500': ((-400, 100), (-1500, -1001))}


def h(salt, x):
    return hashlib.sha256((salt + str(x)).encode()).hexdigest()


G = pd.read_csv(Z6D / 'GROUPS.tsv', sep='\t')
G = G[G.POS_FEASIBLE].copy()
L = pd.read_parquet(SCRATCH / 'z6/z6_loci.parquet')
rt70 = {l.split('\t')[1].strip(): l.split('\t')[0] for l in open(SCRATCH / 's02/RT70_cluster.tsv')}
L['rt70'] = L.rt_seq_hash.map(rt70)
pool = L[L.rt50.isin(G.rt50) & (L.locus_class == 'MATCHED_LOCAL_ADEQUATE') & L.stratum.isin(['S1', 'S2', 'S3'])]

feat = pool.groupby('rt50').agg(pool_loci=('locus_key', 'size'), pool_exact_rt=('rt_seq_hash', 'nunique'),
                                pool_rt90=('rt90', 'nunique'), pool_rt70=('rt70', 'nunique'),
                                type_modal=('type_label', lambda x: x.value_counts().index[0])).reset_index()
feat['divergence_rt70_per_rt90'] = feat.pool_rt70 / feat.pool_rt90
feat['depth_bin'] = pd.cut(feat.pool_rt90, [0, 9, 19, 10 ** 6], labels=['6-9', '10-19', '>=20']).astype(str)
feat = feat.merge(G[['rt50', 'loci', 'exact_rt', 'rt90', 'genomes', 'genera', 'phyla']], on='rt50')

r1 = set(pd.read_csv(Z6D / 'Z6_SETS.tsv', sep='\t').rt50)
feat['round1_exposed'] = feat.rt50.isin(r1)
feat['split'] = None
feat.loc[feat.round1_exposed, 'split'] = 'DEV'
rest = feat[~feat.round1_exposed].copy()
rest['stratum'] = rest.type_modal + '|' + rest.depth_bin
for s, g in rest.groupby('stratum'):
    order = sorted(g.rt50, key=lambda x: h('r2-split-v1|', x))
    for r, gid in enumerate(order):
        feat.loc[feat.rt50 == gid, 'split'] = 'DEV' if r % 5 in (0, 2) else 'HELDOUT'
feat['stratum'] = feat.type_modal + '|' + feat.depth_bin

# ---- sealed reference summaries (balance reporting only) ----
c = duckdb.connect()
c.register('pool', pool[['locus_key', 'rt50']])
ref = c.execute(f"""
  SELECT pool.rt50, median(p.nc_seq_len) ref_len_median, median(abs(p.signed_distance_bp)) ref_dist_median,
         mode(CASE WHEN p.overlaps_rt_cds AND p.direction = 'overlapping' THEN 'intragenic_or_overlapping_RT'
                   WHEN p.direction = 'downstream' THEN 'downstream'
                   WHEN p.overlaps_non_rt_cds THEN 'overlapping_adjacent_CDS'
                   WHEN p.direction = 'upstream' THEN 'upstream' ELSE 'other_uncertain' END) topology_modal
  FROM pool JOIN read_parquet('{DERIVED}/rt_ncrna_pairs_v1.parquet') p USING (locus_key)
  WHERE p.canonical AND p.file_label = 'Retron' AND p.same_strand AND p.evalue <= 1e-5
  GROUP BY 1""").df()
ref.to_csv(T / 'GROUP_REFSTATS_SEALED.tsv', sep='\t', index=False)

# ---- member sets and FASTAs ----
members = []
for g in feat.itertuples():
    p = pool[(pool.rt50 == g.rt50) & (pool.bp_available_upstream >= 1900)].copy()
    p['o'] = p.locus_key.map(lambda k: h('r2-members-v1|', k))
    picked, used90, seen = [], set(), set()
    for r in p.sort_values('o').itertuples():
        if r.rt90 in used90:
            continue
        d = r._asdict()
        seqs = {}
        for w, (real, ctrl) in WIN.items():
            seqs[f'{w}_real'] = window(d, *real)
            seqs[f'{w}_ctrl'] = window(d, *ctrl)
        if any(v is None for v in seqs.values()) or seqs['W700_real'] in seen:
            continue
        used90.add(r.rt90)
        seen.add(seqs['W700_real'])
        picked.append((r, seqs))
        if len(picked) == 20:
            break
    gdir = OUT / g.rt50[:16]
    gdir.mkdir(exist_ok=True)
    for i, (r, seqs) in enumerate(picked):
        members.append(dict(rt50=g.rt50, gid=g.rt50[:16], split=g.split, member_id=f'm{i:02d}',
                            half=('A' if i % 2 == 0 else 'B') if len(picked) >= 12 else None,
                            locus_key=r.locus_key, rt_seq_hash=r.rt_seq_hash, rt90=r.rt90, rt70=r.rt70,
                            type_label=r.type_label, stratum=r.stratum, tax_genus=r.tax_genus, tax_phylum=r.tax_phylum,
                            source_database=r.source_database, rt_start=r.rt_start, rt_end=r.rt_end,
                            rt_strand=r.rt_strand, source_file=r.source_file, byte_offset=r.byte_offset,
                            byte_len=r.byte_len, bp_available_upstream=r.bp_available_upstream))
    for key in ['W700_real', 'W700_ctrl', 'W500_real', 'W500_ctrl']:
        with open(gdir / f'{key}.fa', 'w') as fh:
            for i, (r, seqs) in enumerate(picked):
                fh.write(f'>m{i:02d}\n{seqs[key]}\n')
        if len(picked) >= 12:
            for half in 'AB':
                with open(gdir / f'{key}_half{half}.fa', 'w') as fh:
                    for i, (r, seqs) in enumerate(picked):
                        if ('A' if i % 2 == 0 else 'B') == half:
                            fh.write(f'>m{i:02d}\n{seqs[key]}\n')
    feat.loc[feat.rt50 == g.rt50, 'n_members'] = len(picked)
M = pd.DataFrame(members)
feat['gid'] = feat.rt50.str[:16]
feat['stability_testable'] = feat.n_members >= 12
feat['evaluable'] = feat.n_members >= 6
feat.to_csv(T / 'SPLIT_MANIFEST.tsv', sep='\t', index=False)
M.to_csv(T / 'MEMBERS.tsv', sep='\t', index=False)

bal = feat.merge(ref, on='rt50', how='left')
rows = []
for col, bins in [('pool_rt90', [0, 9, 19, 1e9]), ('divergence_rt70_per_rt90', [0, .34, .67, 1.01]),
                  ('loci', [0, 100, 1000, 1e9]), ('ref_len_median', [0, 120, 180, 1e9]),
                  ('ref_dist_median', [-1, 20, 60, 1e9])]:
    b = pd.cut(bal[col], bins)
    t = pd.crosstab(b, bal.split)
    for idx, r in t.iterrows():
        rows.append(dict(feature=col, bin=str(idx), DEV=int(r.get('DEV', 0)), HELDOUT=int(r.get('HELDOUT', 0))))
for col in ['type_modal', 'topology_modal']:
    t = pd.crosstab(bal[col].fillna('NA'), bal.split)
    for idx, r in t.iterrows():
        rows.append(dict(feature=col, bin=str(idx), DEV=int(r.get('DEV', 0)), HELDOUT=int(r.get('HELDOUT', 0))))
pd.DataFrame(rows).to_csv(T / 'SPLIT_BALANCE.tsv', sep='\t', index=False)
print(feat.groupby('split').agg(groups=('rt50', 'size'), evaluable=('evaluable', 'sum'),
                                stability_testable=('stability_testable', 'sum'), members=('n_members', 'sum'),
                                round1=('round1_exposed', 'sum')).to_string())
print(pd.DataFrame(rows).to_string())
