"""s03b — Amendment 2 control: CTRL_GII_HARD (group II intron RT loci, same set rules as s03).

The window −300…−1 of a group II intron RT ORF lies inside the intron's own structured RNA
(the ORF sits in domain IV), so real covariation is expected that is NOT a retron ncRNA.
Pool: first 5,000 eligible RVT-GII physical loci in hash order (bounded; the 1.6 M GII records
are not clustered). Writes tables/SETS_AMEND2.tsv and tables/SET_MEMBERS_AMEND2.tsv.
Standalone on purpose: importing s03 would re-execute the frozen selection.
"""
import hashlib
import subprocess
import duckdb
import pandas as pd
from common import SCRATCH, TABLES, DERIVED, MMSEQS, MAX_SET
from windows import window

SALT, MIN_SET, UP = 'spire-bench-v1|', 5, (-300, -1)


def h(x):
    return hashlib.sha256((SALT + str(x)).encode()).hexdigest()


def clusters(path):
    return {m: r for r, m in (l.rstrip('\n').split('\t') for l in open(path))}


c = duckdb.connect()
c.create_function('sha', h, ['VARCHAR'], 'VARCHAR')
g = c.execute(f"""
  SELECT * EXCLUDE (rn) FROM (
    SELECT physical_locus_key, record_key, rt_system_id, rt_seq_hash, contig, rt_start, rt_end,
           rt_strand, source_file, byte_offset, byte_len, tax_phylum, taxonomy_system, tax_genus,
           source_database, file_label,
           row_number() OVER (PARTITION BY physical_locus_key ORDER BY record_key) rn
    FROM read_parquet('{DERIVED}/rt_records_v1.parquet')
    WHERE file_label = 'RVT-GII' AND is_first_copy AND elig_rt_coords AND rt_in_window
          AND NOT multilabel) WHERE rn = 1""").df()
g['ord'] = g.physical_locus_key.map(h)
g = g.sort_values('ord').head(5000)
d = SCRATCH / 's03b_gii'
d.mkdir(parents=True, exist_ok=True)
c.register('gg', g[['rt_seq_hash']])
seqs = c.execute(f"""SELECT rt_seq_hash, rt_seq FROM read_parquet('{DERIVED}/rt_exact_v1.parquet')
                     WHERE rt_seq_hash IN (SELECT rt_seq_hash FROM gg)""").fetchall()
with open(d / 'rt.faa', 'w') as fh:
    fh.write(''.join(f'>{a}\n{b}\n' for a, b in seqs))
for idn, tag in [(0.5, 'RT50'), (0.9, 'RT90')]:
    subprocess.run([str(MMSEQS), 'easy-cluster', str(d / 'rt.faa'), str(d / tag), str(d / f'tmp{tag}'),
                    '--min-seq-id', str(idn), '-c', '0.8', '--cov-mode', '0', '--threads', '16', '-v', '1'],
                   check=True)
g['rt50'] = g.rt_seq_hash.map(clusters(d / 'RT50_cluster.tsv'))
g['rt90'] = g.rt_seq_hash.map(clusters(d / 'RT90_cluster.tsv'))

members, sets, k = [], [], 0
for cl in sorted(g.rt50.dropna().unique(), key=h):
    used, seen, picked = set(), set(), []
    for _, r in g[g.rt50 == cl].sort_values('ord').iterrows():
        if r.rt90 in used:
            continue
        s = window(r, *UP)
        if s is None or s in seen:
            continue
        used.add(r.rt90), seen.add(s), picked.append((r, s))
        if len(picked) == MAX_SET:
            break
    if len(picked) < MIN_SET:
        continue
    k += 1
    sid = f'CTRL_GII_HARD_{k}'
    (SCRATCH / 'sets' / sid).mkdir(parents=True, exist_ok=True)
    with open(SCRATCH / 'sets' / sid / 'input.fa', 'w') as fh:
        for i, (r, s) in enumerate(picked):
            fh.write(f'>m{i:02d}\n{s}\n')
            members.append({'set_id': sid, 'member_id': f'm{i:02d}', 'cohort': 'CTRL_GII_HARD',
                            'stratum': 'RVT-GII', 'win_from': -300, 'win_to': -1,
                            **{x: r[x] for x in ['physical_locus_key', 'record_key', 'rt_seq_hash', 'contig',
                                                 'rt_start', 'rt_end', 'rt_strand', 'tax_phylum', 'rt50', 'rt90']}})
    sets.append({'set_id': sid, 'cohort': 'CTRL_GII_HARD', 'stratum': 'RVT-GII', 'rt50': cl,
                 'n_members': len(picked), 'type_label': 'RVT-GII', 'n_type_labels': 1,
                 'n_phyla': len({r.tax_phylum for r, _ in picked}), 'win_from': -300, 'win_to': -1,
                 'note': 'Amendment 2'})
    if k == 3:
        break
pd.DataFrame(sets).to_csv(TABLES / 'SETS_AMEND2.tsv', sep='\t', index=False)
pd.DataFrame(members).to_csv(TABLES / 'SET_MEMBERS_AMEND2.tsv', sep='\t', index=False)
print(pd.DataFrame(sets)[['set_id', 'n_members', 'n_phyla']].to_string())
