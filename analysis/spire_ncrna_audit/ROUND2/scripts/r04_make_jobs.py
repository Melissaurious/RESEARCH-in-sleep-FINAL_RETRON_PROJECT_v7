"""r04 — build stability / held-out / supplementary-control jobs for the chosen configuration. Reference-blind.

usage: python r04_make_jobs.py dev_stability|heldout <W> <span>
  dev_stability : halves A/B + leave-cluster-out (LCO) of the W_real set, DEV testable groups
  heldout       : HELDOUT real + ctrl (all evaluable) + halves + LCO (testable) + non-retron supplementary groups
LCO = the W_real set minus every member of its most-populated RT70 cluster (only when that cluster has ≥ 2
members; otherwise LCO is NOT_APPLICABLE and recorded as such).
"""
import hashlib
import subprocess
import sys
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / 'scripts'))
from common import SCRATCH, DERIVED  # noqa: E402
from windows import window  # noqa: E402

T = HERE / 'tables'
SETS = SCRATCH / 'r2/sets'
mode, W, span = sys.argv[1], sys.argv[2], int(sys.argv[3])
SPLIT = pd.read_csv(T / 'SPLIT_MANIFEST.tsv', sep='\t')
MEM = pd.read_csv(T / 'MEMBERS.tsv', sep='\t')
split = 'DEV' if mode == 'dev_stability' else 'HELDOUT'
G = SPLIT[(SPLIT.split == split) & SPLIT.evaluable]
jobs, lco_rows, nr_members = [], [], []
for g in G.itertuples():
    if mode == 'heldout':
        jobs += [dict(gid=g.gid, fasta_key=f'{W}_real', span=span), dict(gid=g.gid, fasta_key=f'{W}_ctrl', span=span)]
    if not g.stability_testable:
        continue
    jobs += [dict(gid=g.gid, fasta_key=f'{W}_real_half{h}', span=span) for h in 'AB']
    m = MEM[MEM.gid == g.gid]
    top = m.rt70.value_counts()
    if top.iloc[0] >= 2:
        drop = set(m[m.rt70 == top.index[0]].member_id)
        seqs, name = {}, None
        for line in open(SETS / g.gid / f'{W}_real.fa'):
            if line.startswith('>'):
                name = line[1:].strip()
            else:
                seqs[name] = line.strip()
        with open(SETS / g.gid / f'{W}_real_lco.fa', 'w') as fh:
            for k, v in seqs.items():
                if k not in drop:
                    fh.write(f'>{k}\n{v}\n')
        jobs.append(dict(gid=g.gid, fasta_key=f'{W}_real_lco', span=span))
        lco_rows.append(dict(gid=g.gid, removed_rt70=top.index[0], removed_members=len(drop), remaining=len(seqs) - len(drop)))
    else:
        lco_rows.append(dict(gid=g.gid, removed_rt70=None, removed_members=0, remaining=len(m), note='NOT_APPLICABLE'))

if mode == 'heldout':
    # supplementary non-retron comparative controls (evaluation only)
    import duckdb
    WIN = {'W700': (-600, 100), 'W500': (-400, 100)}[W]
    c = duckdb.connect()
    nr = c.execute(f"""SELECT * EXCLUDE (rn) FROM (
        SELECT physical_locus_key, record_key, rt_seq_hash, rt_start, rt_end, rt_strand, source_file, byte_offset,
               byte_len, file_label, row_number() OVER (PARTITION BY physical_locus_key ORDER BY record_key) rn
        FROM read_parquet('{DERIVED}/rt_records_v1.parquet')
        WHERE file_label IN ('RVT-AbiK','RVT-AbiP2') AND is_first_copy AND elig_rt_coords AND rt_in_window
              AND NOT multilabel) WHERE rn = 1""").df()
    d = SCRATCH / 's03_nonretron'
    cl = lambda f: {l.split('\t')[1].strip(): l.split('\t')[0] for l in open(d / f)}
    nr['rt50'], nr['rt90'] = nr.rt_seq_hash.map(cl('RT50_cluster.tsv')), nr.rt_seq_hash.map(cl('RT90_cluster.tsv'))
    h = lambda x: hashlib.sha256(('r2-nonretron|' + str(x)).encode()).hexdigest()
    nr['o'] = nr.physical_locus_key.map(h)
    for fam in ['RVT-AbiK', 'RVT-AbiP2']:
        k = 0
        for g50 in sorted(nr[nr.file_label == fam].rt50.dropna().unique(), key=h):
            pick, used, seen = [], set(), set()
            for r in nr[nr.rt50 == g50].sort_values('o').itertuples():
                if r.rt90 in used:
                    continue
                s = window(r._asdict(), *WIN)
                if s is None or s in seen:
                    continue
                used.add(r.rt90); seen.add(s); pick.append((r, s))
                if len(pick) == 20:
                    break
            if len(pick) < 6:
                continue
            k += 1
            gid = f'NONRETRON_{fam}_{k}'
            (SETS / gid).mkdir(exist_ok=True)
            (SETS / gid / f'{W}_real.fa').write_text(''.join(f'>m{i:02d}\n{s}\n' for i, (_, s) in enumerate(pick)))
            nr_members += [dict(gid=gid, member_id=f'm{i:02d}', split='SUPPLEMENTARY_CONTROL', locus_key=r.physical_locus_key,
                                source_file=r.source_file, byte_offset=r.byte_offset, byte_len=r.byte_len,
                                rt_start=r.rt_start, rt_end=r.rt_end, rt_strand=r.rt_strand, file_label=r.file_label)
                           for i, (r, _) in enumerate(pick)]
            jobs.append(dict(gid=gid, fasta_key=f'{W}_real', span=span))
            if k == 2:
                break

if nr_members:
    pd.DataFrame(nr_members).to_csv(T / 'NONRETRON_MEMBERS.tsv', sep='\t', index=False)
J = pd.DataFrame(jobs)
J.to_csv(T / f'JOBS_{mode.upper()}.tsv', sep='\t', index=False)
pd.DataFrame(lco_rows).to_csv(T / f'LCO_{mode.upper()}.tsv', sep='\t', index=False)
print(J.fasta_key.str.replace(r'^W\d+_', '', regex=True).value_counts().to_string())
