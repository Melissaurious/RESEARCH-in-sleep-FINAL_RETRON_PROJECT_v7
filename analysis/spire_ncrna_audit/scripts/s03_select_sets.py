"""s03 — prospective set selection (BENCHMARK_DESIGN.md §5–6). Reads no ref_* column.

Writes SCRATCH/sets/<set_id>/input.fa and tables/SET_MEMBERS.tsv, tables/SETS.tsv.
Cohorts POS (+POS_S5 descriptive), PIL, CTRL_DISTAL, CTRL_INTRAGENIC, CTRL_NONRETRON.
"""
import hashlib
import subprocess
from collections import Counter, defaultdict
import duckdb
import pandas as pd
from common import SCRATCH, TABLES, DERIVED, MMSEQS, WINDOW_BP, MAX_SET
from windows import window

SALT = 'spire-bench-v1|'
MIN_SET = 5
UP = (-WINDOW_BP, -1)
DISTAL = (-1500, -1201)
INTRA = (300, 599)
SETS = SCRATCH / 'sets'


def h(x):
    return hashlib.sha256((SALT + str(x)).encode()).hexdigest()


def load_clusters(path):
    d = {}
    for line in open(path):
        rep, mem = line.rstrip('\n').split('\t')
        d[mem] = rep
    return d


# Selection needs NO reference column: read only what set formation uses.
COLS = ['physical_locus_key', 'record_key', 'rt_system_id', 'rt_seq_hash', 'contig', 'rt_start',
        'rt_end', 'rt_strand', 'source_file', 'byte_offset', 'byte_len', 'tax_phylum',
        'taxonomy_system', 'tax_genus', 'source_database', 'nc_status', 'evidence_stratum',
        'suitability', 'type_label', 'type_label_source', 'type_label_conflict']
M = duckdb.sql(f"SELECT {', '.join(COLS)} FROM read_parquet('{SCRATCH}/master/master_rt_system.parquet')").df()
rt50 = load_clusters(SCRATCH / 's02/RT50_cluster.tsv')
rt90 = load_clusters(SCRATCH / 's02/RT90_cluster.tsv')
M['rt50'] = M.rt_seq_hash.map(rt50)
M['rt90'] = M.rt_seq_hash.map(rt90)
M['ord'] = M.physical_locus_key.map(h)


def build(pool, interval, max_n=MAX_SET):
    """Ordered pool -> list of (row, seq) with one locus per RT90 and no identical windows."""
    used90, seqs, out = set(), set(), []
    for _, r in pool.sort_values('ord').iterrows():
        if r.rt90 in used90:
            continue
        s = window(r, *interval)
        if s is None or s in seqs or set(s) - set('ACGT') == set(s):
            continue
        used90.add(r.rt90)
        seqs.add(s)
        out.append((r, s))
        if len(out) == max_n:
            break
    return out


members, sets = [], []


def emit(set_id, cohort, stratum, interval, picked, note=''):
    d = SETS / set_id
    d.mkdir(parents=True, exist_ok=True)
    with open(d / 'input.fa', 'w') as fh:
        for i, (r, s) in enumerate(picked):
            mid = f'm{i:02d}'
            fh.write(f'>{mid}\n{s}\n')
            members.append({'set_id': set_id, 'member_id': mid, 'cohort': cohort, 'stratum': stratum,
                            'win_from': interval[0], 'win_to': interval[1],
                            **{k: r[k] for k in COLS if k in r.index}, 'rt50': r.rt50, 'rt90': r.rt90})
    types = Counter(r.type_label for r, _ in picked)
    sets.append({'set_id': set_id, 'cohort': cohort, 'stratum': stratum, 'rt50': picked[0][0].rt50,
                 'n_members': len(picked), 'type_label': types.most_common(1)[0][0],
                 'n_type_labels': len(types), 'n_phyla': len({r.tax_phylum for r, _ in picked}),
                 'win_from': interval[0], 'win_to': interval[1], 'note': note})


def modal_type(df):
    return df.groupby('rt50').type_label.agg(lambda x: x.value_counts().index[0])


# ---------------- POS ----------------
OK = M.suitability == 'OK'
posA = M[OK & M.nc_status.isin(['A_T3', 'A_T2'])]
pos = posA[posA.evidence_stratum.isin(['S1_SYSTEM_CONTEXT_2TOOLS', 'S2_SYSTEM_CONTEXT_1TOOL',
                                       'S3_FUSED_RT_RULE_ONLY'])
           & ~posA.type_label_conflict.astype(bool)
           & ~posA.type_label.isin(['UNLABELLED', 'AMBIGUOUS'])]
mt = modal_type(pos)
pos_sets = []
for t in sorted(mt.unique(), key=h):
    clusters = sorted(mt[mt == t].index, key=h)
    k = 0
    for cl in clusters:
        picked = build(pos[pos.rt50 == cl], UP)
        if len(picked) >= MIN_SET:
            k += 1
            sid = f'POS_{t}_{k}'
            emit(sid, 'POS', 'S1-S3', UP, picked)
            pos_sets.append((sid, picked))
        if k == 3:
            break
s5 = posA[posA.evidence_stratum == 'S5_SEQUENCE_ONLY']
k = 0
for cl in sorted(s5.rt50.unique(), key=h):
    picked = build(s5[s5.rt50 == cl], UP)
    if len(picked) >= MIN_SET:
        k += 1
        emit(f'POS_S5_{k}', 'POS_S5', 'S5', UP, picked)
        pos_sets.append((f'POS_S5_{k}', picked))
    if k == 2:
        break

# ---------------- CONTROLS on POS members ----------------
for sid, picked in pos_sets:
    for tag, iv in [('CTRL_DISTAL', DISTAL), ('CTRL_INTRAGENIC', INTRA)]:
        sub = []
        for r, _ in picked:
            s = window(r, *iv)
            if s and s not in {x for _, x in sub}:
                sub.append((r, s))
        if len(sub) >= MIN_SET:
            emit(f'{tag}__{sid}', tag, 'S1-S3' if 'S5' not in sid else 'S5', iv, sub, note=sid)

# ---------------- PILOT ----------------
B = M[OK & (M.nc_status == 'B_NO_CM_CALL')]
has_cm = set(M[M.nc_status.isin(['A_T3', 'A_T2'])].rt50)
S12 = ['S1_SYSTEM_CONTEXT_2TOOLS', 'S2_SYSTEM_CONTEXT_1TOOL']
strata = {
    'PIL_S12_HOMOLOG_HAS_CM': B[B.evidence_stratum.isin(S12) & B.rt50.isin(has_cm)],
    'PIL_S12_ORPHAN': B[B.evidence_stratum.isin(S12) & ~B.rt50.isin(has_cm)],
    'PIL_S3_FUSED': B[B.evidence_stratum == 'S3_FUSED_RT_RULE_ONLY'],
    'PIL_S5_SEQONLY': B[B.evidence_stratum == 'S5_SEQUENCE_ONLY'],
}
for stratum, pool in strata.items():
    mtp = modal_type(pool)
    by_type = defaultdict(list)
    for cl in sorted(mtp.index, key=h):
        by_type[mtp[cl]].append(cl)
    order = sorted(by_type, key=h)
    k, exhausted = 0, False
    while k < 5 and not exhausted:
        exhausted = True
        for t in order:
            while by_type[t]:
                cl = by_type[t].pop(0)
                picked = build(pool[pool.rt50 == cl], UP)
                if len(picked) >= MIN_SET:
                    k += 1
                    emit(f'{stratum}_{k}', 'PIL', stratum, UP, picked)
                    exhausted = False
                    break
            if k == 5:
                break

# ---------------- NON-RETRON RT CONTROL ----------------
c = duckdb.connect()
nr = c.execute(f"""
  SELECT * EXCLUDE (rn) FROM (
    SELECT physical_locus_key, record_key, rt_system_id, rt_seq_hash, contig, rt_start, rt_end,
           rt_strand, source_file, byte_offset, byte_len, tax_phylum, taxonomy_system, tax_genus,
           source_database, file_label,
           row_number() OVER (PARTITION BY physical_locus_key ORDER BY record_key) rn
    FROM read_parquet('{DERIVED}/rt_records_v1.parquet')
    WHERE file_label IN ('RVT-AbiK', 'RVT-AbiP2') AND is_first_copy AND elig_rt_coords
          AND rt_in_window AND NOT multilabel) WHERE rn = 1""").df()
nrd = SCRATCH / 's03_nonretron'
nrd.mkdir(parents=True, exist_ok=True)
seqs = c.execute(f"""SELECT rt_seq_hash, rt_seq FROM read_parquet('{DERIVED}/rt_exact_v1.parquet')
                     WHERE rt_seq_hash IN (SELECT rt_seq_hash FROM nr)""").fetchall()
with open(nrd / 'rt.faa', 'w') as fh:
    fh.write(''.join(f'>{a}\n{b}\n' for a, b in seqs))
for idn, tag in [(0.5, 'RT50'), (0.9, 'RT90')]:
    subprocess.run([str(MMSEQS), 'easy-cluster', str(nrd / 'rt.faa'), str(nrd / tag), str(nrd / f'tmp{tag}'),
                    '--min-seq-id', str(idn), '-c', '0.8', '--cov-mode', '0', '--threads', '16', '-v', '1'],
                   check=True)
n50, n90 = load_clusters(nrd / 'RT50_cluster.tsv'), load_clusters(nrd / 'RT90_cluster.tsv')
nr['rt50'], nr['rt90'] = nr.rt_seq_hash.map(n50), nr.rt_seq_hash.map(n90)
nr['ord'] = nr.physical_locus_key.map(h)
nr['type_label'] = nr.file_label
for fam in ['RVT-AbiK', 'RVT-AbiP2']:
    pool, k = nr[nr.file_label == fam], 0
    for cl in sorted(pool.rt50.dropna().unique(), key=h):
        picked = build(pool[pool.rt50 == cl], UP)
        if len(picked) >= MIN_SET:
            k += 1
            emit(f'CTRL_NONRETRON_{fam}_{k}', 'CTRL_NONRETRON', fam, UP, picked)
        if k == 2:
            break

TABLES.mkdir(parents=True, exist_ok=True)
pd.DataFrame(members).to_csv(TABLES / 'SET_MEMBERS.tsv', sep='\t', index=False)
S = pd.DataFrame(sets)
S.to_csv(TABLES / 'SETS.tsv', sep='\t', index=False)
print(S.groupby('cohort').agg(n_sets=('set_id', 'size'), n_members=('n_members', 'sum')).to_string())
print(S[S.cohort.isin(['POS', 'PIL', 'POS_S5'])][['set_id', 'n_members', 'n_phyla']].to_string())
