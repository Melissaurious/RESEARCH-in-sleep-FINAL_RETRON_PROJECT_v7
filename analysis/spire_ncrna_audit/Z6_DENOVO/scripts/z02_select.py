"""z02 — prospective selection of the bounded Z6 benchmark (DESIGN §6). Reads no reference coordinates.

Writes ARIS_OUTPUT/spire_ncrna_audit/z6/sets/<set_id>/input.fa (member ids hide match status) and
tables/Z6_SETS.tsv, tables/Z6_SET_MEMBERS.tsv.
"""
import hashlib
import sys
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from common import SCRATCH  # noqa: E402
from windows import window  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
T = HERE / 'tables'
W, DIST = (-600, 100), (-1900, -1201)
SALT, MIN_SET = 'z6-denovo-v1|', 6
SETS = SCRATCH / 'z6/sets'


def h(x):
    return hashlib.sha256((SALT + str(x)).encode()).hexdigest()


L = pd.read_parquet(SCRATCH / 'z6/z6_loci.parquet')
G = pd.read_csv(T / 'GROUPS.tsv', sep='\t')
L['ord'] = L.locus_key.map(h)
S12 = {'S1', 'S2'}
POS_POOL = L[(L.locus_class == 'MATCHED_LOCAL_ADEQUATE') & L.stratum.isin({'S1', 'S2', 'S3'})]
UNM_S12 = L[(L.locus_class == 'UNMATCHED_ADEQUATE') & L.stratum.isin(S12)]
UNM_S3 = L[(L.locus_class == 'UNMATCHED_ADEQUATE') & (L.stratum == 'S3')]
MAT_S12 = L[(L.locus_class == 'MATCHED_LOCAL_ADEQUATE') & L.stratum.isin(S12)]


def pick(pool, n, used90=None, seqs=None):
    used90 = set() if used90 is None else used90
    seqs = set() if seqs is None else seqs
    out = []
    for r in pool.sort_values('ord').itertuples():
        if r.rt90 in used90:
            continue
        s = window(r._asdict(), *W)
        if s is None or s in seqs:
            continue
        used90.add(r.rt90)
        seqs.add(s)
        out.append((r, s))
        if len(out) == n:
            break
    return out, used90, seqs


sets, members = [], []


def emit(sid, cohort, group, picked, note=''):
    d = SETS / sid
    d.mkdir(parents=True, exist_ok=True)
    order = sorted(picked, key=lambda x: h(sid + x[0].locus_key))   # shuffle: status not inferable from order
    with open(d / 'input.fa', 'w') as fh:
        for i, (r, s) in enumerate(order):
            fh.write(f'>m{i:02d}\n{s}\n')
            members.append(dict(set_id=sid, member_id=f'm{i:02d}', cohort=cohort, rt50=group,
                                locus_key=r.locus_key, physical_locus_key=r.physical_locus_key,
                                record_key_any=r.record_key_any, rt_seq_hash=r.rt_seq_hash, rt90=r.rt90,
                                locus_class=r.locus_class, stratum=r.stratum, type_label=r.type_label,
                                tax_genus=r.tax_genus, tax_phylum=r.tax_phylum, source_database=r.source_database,
                                genome_id_norm=r.genome_id_norm, any_window_clipped=r.any_window_clipped,
                                bp_available_upstream=r.bp_available_upstream, rt_start=r.rt_start,
                                rt_end=r.rt_end, rt_strand=r.rt_strand, source_file=r.source_file,
                                byte_offset=r.byte_offset, byte_len=r.byte_len, win_from=W[0], win_to=W[1]))
    g = G[G.rt50 == group].iloc[0]
    sets.append(dict(set_id=sid, cohort=cohort, rt50=group, n_members=len(picked),
                     n_matched=sum(r.locus_class.startswith('MATCHED') for r, _ in picked),
                     n_unmatched=sum(r.locus_class.startswith('UNMATCHED') for r, _ in picked),
                     type_label=Counter(r.type_label for r, _ in picked).most_common(1)[0][0],
                     n_genera=len({r.tax_genus for r, _ in picked}), n_phyla=len({r.tax_phylum for r, _ in picked}),
                     group_loci=g.loci, group_exact_rt=g.exact_rt, group_rt90=g.rt90, group_cm_models=g.cm_models,
                     note=note))


def modal(pool):
    return pool.groupby('rt50').type_label.agg(lambda x: x.value_counts().index[0])


# ---- POS_BLIND: one group per type label, then per dominant CM model, ≤ 10 ----------------------
pos_groups = G[G.POS_FEASIBLE].rt50
pp = POS_POOL[POS_POOL.rt50.isin(pos_groups)]
mt = modal(pp)
cmmod = pp.groupby('rt50').detection_models.agg(lambda x: x.value_counts().index[0])
chosen, seen_t, seen_m = [], set(), set()
for key, seen, lab in [('type', seen_t, mt), ('model', seen_m, cmmod)]:
    for g in sorted(mt.index, key=h):
        if len(chosen) == 10:
            break
        if g in chosen or lab[g] in seen:
            continue
        picked, _, _ = pick(pp[pp.rt50 == g], 16)
        if len(picked) >= MIN_SET:
            chosen.append(g)
            seen_t.add(mt[g]); seen_m.add(cmmod[g])
            emit(f'POS_{len(chosen):02d}_{mt[g]}', 'POS_BLIND', g, picked, note=f'dominant CM {cmmod[g]}')

# ---- MIXED: ≤ 6, round-robin over type labels -----------------------------------------------------
mix = G[G.MIXED].rt50


def round_robin(groups, labels, n, build, cohort, prefix):
    by = defaultdict(list)
    for g in sorted(groups, key=h):
        by[labels[g]].append(g)
    k = 0
    while k < n and any(by.values()):
        for t in sorted(by, key=h):
            while by[t]:
                g = by[t].pop(0)
                picked = build(g)
                if len(picked) >= MIN_SET:
                    k += 1
                    emit(f'{prefix}_{k:02d}_{t}', cohort, g, picked)
                    break
            if k == n:
                break


def build_mixed(g):
    a, used, seqs = pick(MAT_S12[MAT_S12.rt50 == g], 8)
    b, _, _ = pick(UNM_S12[UNM_S12.rt50 == g], 8, used, seqs)
    return a + b if (len(a) >= 3 and len(b) >= 3) else []


round_robin(mix, modal(L[L.rt50.isin(mix)]), 6, build_mixed, 'MIXED', 'MIX')
dn = G[G.DENOVO_FEASIBLE_S12].rt50
round_robin(dn, modal(UNM_S12[UNM_S12.rt50.isin(dn)]), 5,
            lambda g: pick(UNM_S12[UNM_S12.rt50 == g], 16)[0], 'DENOVO_S12', 'DN12')
dn3 = G[G.DENOVO_FEASIBLE_S3].rt50
round_robin(dn3, modal(UNM_S3[UNM_S3.rt50.isin(dn3)]), 3,
            lambda g: pick(UNM_S3[UNM_S3.rt50 == g], 16)[0], 'DENOVO_S3', 'DN3')

# ---- CTRL_DISTAL for every set ---------------------------------------------------------------------
M = pd.DataFrame(members)
for s in list(sets):
    sub = M[M.set_id == s['set_id']]
    ctrl, seen = [], set()
    for r in sub.itertuples():
        q = window(r._asdict(), *DIST)
        if q and q not in seen:
            seen.add(q)
            ctrl.append((r, q))
    if len(ctrl) >= MIN_SET:
        sid = f"CTRL_{s['set_id']}"
        (SETS / sid).mkdir(parents=True, exist_ok=True)
        with open(SETS / sid / 'input.fa', 'w') as fh:
            for r, q in ctrl:
                fh.write(f'>{r.member_id}\n{q}\n')
        sets.append(dict(set_id=sid, cohort='CTRL_DISTAL', rt50=s['rt50'], n_members=len(ctrl),
                         note=s['set_id']))
S = pd.DataFrame(sets)
S.to_csv(T / 'Z6_SETS.tsv', sep='\t', index=False)
M.to_csv(T / 'Z6_SET_MEMBERS.tsv', sep='\t', index=False)
print(S.to_string())
