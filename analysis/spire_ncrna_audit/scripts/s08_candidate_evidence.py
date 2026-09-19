"""s08 — independent evidence for every pilot call (BENCHMARK_DESIGN §10). Post-freeze.

One row per (pilot member, arm, rule) with a call. Writes CANDIDATE_EVIDENCE.tsv and
CM_MISSED_PILOT.tsv (one row per pilot member, all arms/rules side by side).
"""
import subprocess
import duckdb
import numpy as np
import pandas as pd
from common import SCRATCH, TABLES, AUDIT, DERIVED, CMSEARCH, PADLOC_CM, RNAFOLD
from windows import _record, contig_to_rt_relative

E = pd.read_csv(TABLES / 'EVAL_member_level.tsv', sep='\t', low_memory=False)
mem = pd.read_csv(TABLES / 'SET_MEMBERS.tsv', sep='\t')
S = pd.read_csv(TABLES / 'EVAL_set_level.tsv', sep='\t')
PIL = E[(E.cohort == 'PIL') & E.rule.isin(['PRIMARY_SPIRE', 'SENS_ANY_COV'])].copy()
pm = mem[mem.cohort == 'PIL']

# ---- windows ---------------------------------------------------------------------------------
seqs = {}
for sid in pm.set_id.unique():
    name = None
    for line in open(SCRATCH / 'sets' / sid / 'input.fa'):
        if line.startswith('>'):
            name = line[1:].strip()
        else:
            seqs[(sid, name)] = line.strip()

# ---- Infernal padlocdb.cm at relaxed threshold on every pilot window ----------------------
cmd = SCRATCH / 'pilot_cm'
cmd.mkdir(exist_ok=True)
with open(cmd / 'pilot_windows.fa', 'w') as fh:
    for (sid, m), s in seqs.items():
        fh.write(f'>{sid}|{m}\n{s}\n')
subprocess.run([str(CMSEARCH), '--cpu', '8', '-E', '10', '--tblout', str(cmd / 'cm.tbl'), '-o', '/dev/null',
                str(PADLOC_CM), str(cmd / 'pilot_windows.fa')], check=True)
cm = []
for line in open(cmd / 'cm.tbl'):
    if line.startswith('#'):
        continue
    p = line.split()
    sid, m = p[0].split('|')
    a, b = int(p[7]), int(p[8])
    cm.append(dict(set_id=sid, member_id=m, cm_model=p[2], cm_strand=p[9], cm_E=float(p[15]),
                   cm_score=float(p[14]), cm_rel_from=-300 + min(a, b) - 1, cm_rel_to=-300 + max(a, b) - 1))
CM = pd.DataFrame(cm)
CM.to_csv(cmd / 'cm_hits.tsv', sep='\t', index=False)
best_cm = (CM[CM.cm_strand == '+'].sort_values('cm_E').groupby(['set_id', 'member_id']).head(1)
           if len(CM) else pd.DataFrame(columns=['set_id', 'member_id']))

# ---- annotated CDS in the member's record (contig coordinates -> RT-relative) ---------------
c = duckdb.connect()
keys = pm[['set_id', 'member_id', 'record_key', 'source_file', 'byte_offset', 'byte_len', 'rt_start', 'rt_end',
           'rt_strand']].copy()
cds_rows = []
for r in keys.itertuples():
    rec = _record(r.source_file, int(r.byte_offset), int(r.byte_len))
    for cd in rec['cds_annotations']:
        if cd.get('is_rt_gene'):
            continue
        a = contig_to_rt_relative(r.rt_start, r.rt_end, r.rt_strand, cd['start'])
        b = contig_to_rt_relative(r.rt_start, r.rt_end, r.rt_strand, cd['end'])
        lo, hi = min(a, b), max(a, b)
        if hi >= -300 and lo <= -1:
            cds_rows.append(dict(set_id=r.set_id, member_id=r.member_id, cds_rel_from=lo, cds_rel_to=hi,
                                 cds_same_strand=(cd['strand'] == r.rt_strand)))
CDS = pd.DataFrame(cds_rows)

# ---- homolog CM positions (RT50 cluster's A_T3 loci; revealed now, after freeze) -----------
M = duckdb.sql(f"""SELECT m.rt_seq_hash, m.rt_start, m.rt_end, m.rt_strand, m.ref_nc_start, m.ref_nc_end,
                   m.ref_detection_model FROM read_parquet('{SCRATCH}/master/master_rt_system.parquet') m
                   WHERE nc_status = 'A_T3'""").df()
rt50 = {l.split('\t')[1].strip(): l.split('\t')[0] for l in open(SCRATCH / 's02/RT50_cluster.tsv')}
M['rt50'] = M.rt_seq_hash.map(rt50)
a = np.where(M.rt_strand == '+', M.ref_nc_start - M.rt_start, M.rt_end - M.ref_nc_start)
b = np.where(M.rt_strand == '+', M.ref_nc_end - M.rt_start, M.rt_end - M.ref_nc_end)
M['hf'], M['ht'] = np.fmin(a, b), np.fmax(a, b)
H = M.groupby('rt50').agg(homolog_n_A_T3=('hf', 'size'), homolog_ref_from=('hf', 'median'),
                          homolog_ref_to=('ht', 'median'),
                          homolog_models=('ref_detection_model', lambda x: ';'.join(sorted(set(x))))).reset_index()


def rnafold(s):
    out = subprocess.run([str(RNAFOLD), '--noPS'], input=s, capture_output=True, text=True).stdout
    return float(out.strip().split('(')[-1].rstrip(')')) if '(' in out else None


def ov(a1, a2, b1, b2):
    return max(0, min(a2, b2) - max(a1, b1) + 1)


rows = []
calls = PIL[PIL.call == True]
spread = (calls.groupby(['set_id', 'arm', 'rule'])
               .agg(set_calls=('member_id', 'size'), sd_from=('pred_rel_from', 'std'), sd_to=('pred_rel_to', 'std'))
               .reset_index())
for r in calls.itertuples():
    f, t = int(r.pred_rel_from if r.rule == 'PRIMARY_SPIRE' else r.sens_rel_from), \
           int(r.pred_rel_to if r.rule == 'PRIMARY_SPIRE' else r.sens_rel_to)
    win = seqs[(r.set_id, r.member_id)]
    span = win[f + 300: t + 301]
    cds = CDS[(CDS.set_id == r.set_id) & (CDS.member_id == r.member_id)] if len(CDS) else CDS
    cds_ov = int(sum(ov(f, t, x.cds_rel_from, x.cds_rel_to) for x in cds.itertuples())) if len(cds) else 0
    bc = best_cm[(best_cm.set_id == r.set_id) & (best_cm.member_id == r.member_id)] if len(best_cm) else best_cm
    other = calls[(calls.set_id == r.set_id) & (calls.member_id == r.member_id) & (calls.rule == r.rule)
                  & (calls.arm != r.arm)]
    agree = sum(ov(f, t, int(o.pred_rel_from if r.rule == 'PRIMARY_SPIRE' else o.sens_rel_from),
                   int(o.pred_rel_to if r.rule == 'PRIMARY_SPIRE' else o.sens_rel_to)) > 0 for o in other.itertuples())
    rt50_id = pm[(pm.set_id == r.set_id) & (pm.member_id == r.member_id)].rt50.iloc[0]
    hh = H[H.rt50 == rt50_id]
    sp = spread[(spread.set_id == r.set_id) & (spread.arm == r.arm) & (spread.rule == r.rule)].iloc[0]
    row = dict(set_id=r.set_id, stratum=r.stratum, member_id=r.member_id, physical_locus_key=r.physical_locus_key,
               rt_seq_hash=r.rt_seq_hash, type_label=r.type_label, evidence_stratum=r.evidence_stratum,
               tax_phylum=r.tax_phylum, arm=r.arm, rule=r.rule,
               cand_rel_from=f, cand_rel_to=t, cand_len=t - f + 1, orientation='RT sense (by construction)',
               set_members=int(r.nseq_used), set_calls=int(sp.set_calls),
               pos_sd_5p=sp.sd_from, pos_sd_3p=sp.sd_to,
               n_sig_pairs=r.n_sig_pairs, min_sig_E=r.min_sig_E, expected_cov=r.expected_cov,
               observed_cov=r.observed_cov, obs_exp=r.obs_exp_ratio, low_power=r.low_power, avgid=r.avgid,
               n_supported_helices=r.n_supported_helices,
               cds_overlap_nt=cds_ov, cds_overlap_frac=cds_ov / (t - f + 1),
               cm_sub_hit_model=None if bc.empty else bc.cm_model.iloc[0],
               cm_sub_hit_E=None if bc.empty else bc.cm_E.iloc[0],
               cm_sub_hit_overlap_nt=0 if bc.empty else ov(f, t, int(bc.cm_rel_from.iloc[0]), int(bc.cm_rel_to.iloc[0])),
               rnafold_mfe=rnafold(span), rnafold_mfe_per_nt=(rnafold(span) or 0) / max(1, len(span)),
               n_other_arms_overlapping=agree,
               homolog_n_A_T3=None if hh.empty else int(hh.homolog_n_A_T3.iloc[0]),
               homolog_ref_rel=None if hh.empty else f'{hh.homolog_ref_from.iloc[0]:.0f}..{hh.homolog_ref_to.iloc[0]:.0f}',
               homolog_ref_overlap_nt=None if hh.empty else ov(f, t, int(hh.homolog_ref_from.iloc[0]), int(hh.homolog_ref_to.iloc[0])),
               homolog_models=None if hh.empty else hh.homolog_models.iloc[0])
    rows.append(row)
C = pd.DataFrame(rows)


def support(r):
    ev = []
    if r.n_other_arms_overlapping >= 1:
        ev.append('cross-arm')
    if r.cm_sub_hit_overlap_nt and r.cm_sub_hit_overlap_nt > 0:
        ev.append('sub-threshold CM')
    if r.homolog_ref_overlap_nt and r.homolog_ref_overlap_nt > 0:
        ev.append('homolog CM position')
    if r.cds_overlap_frac < 0.5:
        ev.append('mostly non-coding')
    if not r.low_power and r.obs_exp >= 1.0:
        ev.append('covariation at/above power')
    return ';'.join(ev)


C['independent_support'] = C.apply(support, axis=1)
C['n_support'] = C.independent_support.str.count(';') + (C.independent_support != '')
C['status'] = 'computational candidate (not validated)'
C.to_csv(AUDIT / 'CANDIDATE_EVIDENCE.tsv', sep='\t', index=False)

# ---- pilot member table: every member, every arm x rule ---------------------------------------
W = PIL.pivot_table(index=['set_id', 'stratum', 'member_id', 'physical_locus_key', 'type_label',
                           'evidence_stratum', 'tax_phylum'],
                    columns=['arm', 'rule'], values='category', aggfunc='first')
W.columns = [f'{a}__{r}' for a, r in W.columns]
W = W.reset_index()
W = W.merge(best_cm[['set_id', 'member_id', 'cm_model', 'cm_E', 'cm_rel_from', 'cm_rel_to']]
            if len(best_cm) else best_cm, on=['set_id', 'member_id'], how='left')
W = W.merge(S[(S.cohort == 'PIL') & (S.arm == 'A_SPIRE')][['set_id', 'avgid', 'expected_cov', 'observed_cov',
                                                            'n_sig', 'low_power']], on='set_id', how='left')
W.to_csv(AUDIT / 'CM_MISSED_PILOT.tsv', sep='\t', index=False)
print(C.groupby(['arm', 'rule']).agg(calls=('member_id', 'size'), loci=('physical_locus_key', 'nunique'),
                                    cross_arm=('n_other_arms_overlapping', lambda x: (x > 0).sum()),
                                    cm_sub=('cm_sub_hit_overlap_nt', lambda x: (x > 0).sum()),
                                    homolog=('homolog_ref_overlap_nt', lambda x: (x.fillna(0) > 0).sum()),
                                    noncoding=('cds_overlap_frac', lambda x: (x < 0.5).sum())).to_string())
print('pilot members with ANY relaxed CM hit (+ strand):', best_cm.shape[0], 'of', len(seqs))
print(best_cm.sort_values('cm_E').head(15).to_string())
