"""pm01 — build the non-retron specificity panel (DESIGN §2). Reference-free; same member rules as Round 2."""
import hashlib
import subprocess
import sys
from pathlib import Path
import duckdb
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / 'scripts'))
from common import SCRATCH, DERIVED, MMSEQS  # noqa: E402
from windows import window  # noqa: E402

CLASSES = ['RVT-GII', 'RVT-DGRs', 'RVT-CRISPR', 'RVT-CRISPR-like', 'RVT-AbiK', 'RVT-AbiP2', 'RVT-AbiA',
           'RVT-UG2', 'RVT-UG3', 'RVT-UG5', 'RVT-UG8']
OUT = SCRATCH / 'pm'
SETS = SCRATCH / 'r2/sets'           # r02 reads sets from here; panel gids are prefixed PM_
h = lambda s, x: hashlib.sha256((s + str(x)).encode()).hexdigest()
c = duckdb.connect()
L = c.execute(f"""SELECT * EXCLUDE (rn) FROM (
    SELECT physical_locus_key, record_key, rt_seq_hash, rt_start, rt_end, rt_strand, source_file, byte_offset,
           byte_len, file_label, tax_phylum, row_number() OVER (PARTITION BY physical_locus_key ORDER BY record_key) rn
    FROM read_parquet('{DERIVED}/rt_records_v1.parquet')
    WHERE file_label IN ({','.join(repr(x) for x in CLASSES)}) AND is_first_copy AND elig_rt_coords AND rt_in_window
          AND NOT multilabel) WHERE rn = 1""").df()
L['o'] = L.physical_locus_key.map(lambda k: h('pm-panel|', k))
L = L.sort_values('o').groupby('file_label').head(6000)
OUT.mkdir(parents=True, exist_ok=True)
rows, members = [], []
for cls, sub in L.groupby('file_label'):
    d = OUT / cls
    d.mkdir(exist_ok=True)
    seqs = c.execute(f"""SELECT rt_seq_hash, rt_seq FROM read_parquet('{DERIVED}/rt_exact_v1.parquet')
                         WHERE rt_seq_hash IN (SELECT UNNEST(?::VARCHAR[]))""", [list(set(sub.rt_seq_hash))]).fetchall()
    (d / 'rt.faa').write_text(''.join(f'>{a}\n{b}\n' for a, b in seqs))
    cl = {}
    for idn, tag in [(0.5, 'RT50'), (0.9, 'RT90')]:
        subprocess.run([str(MMSEQS), 'easy-cluster', str(d / 'rt.faa'), str(d / tag), str(d / f'tmp{tag}'),
                        '--min-seq-id', str(idn), '-c', '0.8', '--cov-mode', '0', '--threads', '16', '-v', '1'], check=True)
        cl[tag] = {l.split('\t')[1].strip(): l.split('\t')[0] for l in open(d / f'{tag}_cluster.tsv')}
    sub = sub.assign(rt50=sub.rt_seq_hash.map(cl['RT50']), rt90=sub.rt_seq_hash.map(cl['RT90']))
    k = 0
    for g50 in sorted(sub.rt50.dropna().unique(), key=lambda x: h('pm-group|', x)):
        pick, used, seen = [], set(), set()
        for r in sub[sub.rt50 == g50].itertuples():
            if r.rt90 in used:
                continue
            dd = r._asdict()
            real, ctrl, far = window(dd, -400, 100), window(dd, -1500, -1001), window(dd, -1900, -1899)
            if real is None or ctrl is None or far is None or real in seen:
                continue
            used.add(r.rt90); seen.add(real); pick.append((r, real, ctrl))
            if len(pick) == 20:
                break
        if len(pick) < 6:
            continue
        k += 1
        gid = f'PM_{cls}_{k}'
        (SETS / gid).mkdir(parents=True, exist_ok=True)
        for key, idx in [('W500_real', 1), ('W500_ctrl', 2)]:
            (SETS / gid / f'{key}.fa').write_text(''.join(f'>m{i:02d}\n{p[idx]}\n' for i, p in enumerate(pick)))
        gc = sum(p[1].count('G') + p[1].count('C') for p in pick) / sum(len(p[1]) for p in pick)
        rows.append(dict(gid=gid, rt_class=cls, rt50=g50, n_members=len(pick), gc_real=gc,
                         n_phyla=len({p[0].tax_phylum for p in pick})))
        members += [dict(gid=gid, member_id=f'm{i:02d}', rt_class=cls, locus_key=p[0].physical_locus_key,
                         rt_seq_hash=p[0].rt_seq_hash, rt90=p[0].rt90, source_file=p[0].source_file,
                         byte_offset=p[0].byte_offset, byte_len=p[0].byte_len, rt_start=p[0].rt_start,
                         rt_end=p[0].rt_end, rt_strand=p[0].rt_strand) for i, p in enumerate(pick)]
        if k == 8:
            break
    if k == 0:
        rows.append(dict(gid=None, rt_class=cls, n_members=0, note='no homolog group with >= 6 RT90 members and context'))
T = HERE / 'tables'
pd.DataFrame(rows).to_csv(T / 'PANEL_GROUPS.tsv', sep='\t', index=False)
pd.DataFrame(members).to_csv(T / 'PANEL_MEMBERS.tsv', sep='\t', index=False)
jobs = [dict(gid=r['gid'], fasta_key=k, span=260) for r in rows if r.get('gid') for k in ['W500_real', 'W500_ctrl']]
pd.DataFrame(jobs).to_csv(T / 'JOBS_PANEL.tsv', sep='\t', index=False)
print(pd.DataFrame(rows).groupby('rt_class').agg(groups=('gid', 'count'), members=('n_members', 'sum')).to_string())
