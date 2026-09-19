"""s05 — reveal reference ncRNAs AFTER predictions are frozen, and score (BENCHMARK_DESIGN §9).

usage: python s05_evaluate.py <predictions.tsv> [<predictions.tsv> ...]
Refuses to run unless every predictions file's sha256 is already in tables/PREDICTIONS_FROZEN.tsv.
Writes tables/EVAL_member_level.tsv (all cohorts, both rules, all arms) and tables/EVAL_set_level.tsv.
"""
import hashlib
import sys
import duckdb
import numpy as np
import pandas as pd
from common import SCRATCH, TABLES

RULES = {'PRIMARY_SPIRE': ('member_call', 'pred_rel_from', 'pred_rel_to'),
         'SENS_ANY_COV': ('sens_member_call', 'sens_rel_from', 'sens_rel_to'),
         'STRUCT_ONLY': (None, 'struct_rel_from', 'struct_rel_to')}

frozen = set(pd.read_csv(TABLES / 'PREDICTIONS_FROZEN.tsv', sep='\t').sha256)
preds = []
for p in sys.argv[1:]:
    sha = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    if sha not in frozen:
        sys.exit(f'REFUSING: {p} (sha256 {sha}) is not recorded in PREDICTIONS_FROZEN.tsv')
    preds.append(pd.read_csv(p, sep='\t'))
P = pd.concat(preds, ignore_index=True)
P = P[P.status == 'OK']

mem = pd.read_csv(TABLES / 'SET_MEMBERS.tsv', sep='\t')
if (TABLES / 'SET_MEMBERS_AMEND2.tsv').exists():
    mem = pd.concat([mem, pd.read_csv(TABLES / 'SET_MEMBERS_AMEND2.tsv', sep='\t')], ignore_index=True)

# ---- reveal: reference columns from the master table (first read of ref_* in the pipeline) ----
M = duckdb.sql(f"""SELECT physical_locus_key, nc_status, ref_nc_seq_hash, ref_nc_start, ref_nc_end,
       ref_nc_strand, ref_same_strand, ref_signed_distance_bp, ref_direction, ref_n_cds_between,
       ref_overlaps_rt_cds, ref_detection_model, ref_evalue, ref_score, ref_T4, ref_nc_len,
       ref_recurrence_class, rt_start AS m_rt_start, rt_end AS m_rt_end, rt_strand AS m_rt_strand
       FROM read_parquet('{SCRATCH}/master/master_rt_system.parquet')""").df()

# previously validated: our ncRNA matches one of 175 published characterised retron ncRNAs
b = pd.read_csv(SCRATCH / 'pubval/pub_vs_oriented.tsv', sep='\t', header=None,
                names='q s pid alen qlen slen e bits sstrand'.split())
pub = b[(b.pid >= 90) & (b.alen >= 0.8 * b.qlen) & (b.sstrand == 'plus')]
M['previously_validated'] = M.ref_nc_seq_hash.isin(set(pub.s))

X = P.merge(mem[['set_id', 'member_id', 'cohort', 'stratum', 'physical_locus_key', 'rt_seq_hash', 'rt50',
                 'tax_phylum', 'type_label', 'evidence_stratum', 'win_from', 'win_to']],
            on=['set_id', 'member_id'], how='left')
X = X.merge(M, on='physical_locus_key', how='left')


def rel(x, s, e, strand):
    return np.where(strand == '+', x - s, e - x)


a = rel(X.ref_nc_start, X.m_rt_start, X.m_rt_end, X.m_rt_strand)
bb = rel(X.ref_nc_end, X.m_rt_start, X.m_rt_end, X.m_rt_strand)
X['ref_rel_from'] = np.fmin(a, bb)
X['ref_rel_to'] = np.fmax(a, bb)
X['ref_len'] = X.ref_rel_to - X.ref_rel_from + 1
ov_w = (np.fmin(X.ref_rel_to, X.win_to) - np.fmax(X.ref_rel_from, X.win_from) + 1).clip(lower=0)
X['ref_frac_in_window'] = ov_w / X.ref_len

rows = []
for rule, (call_col, f, t) in RULES.items():
    Y = X.copy()
    Y['rule'] = rule
    call = Y[f].notna() if call_col is None else Y[call_col].fillna(False).astype(bool)
    Y['call'] = call
    pf, pt = Y[f], Y[t]
    Y['pred_len'] = pt - pf + 1
    ov = (np.fmin(pt, Y.ref_rel_to) - np.fmax(pf, Y.ref_rel_from) + 1).clip(lower=0)
    Y['overlap_nt'] = ov.where(call)
    uni = Y.pred_len + Y.ref_len - ov
    Y['IoU'] = (ov / uni).where(call)
    Y['Dice'] = (2 * ov / (Y.pred_len + Y.ref_len)).where(call)
    Y['err5'] = (pf - Y.ref_rel_from).where(call)        # + = prediction starts 3' of reference
    Y['err3'] = (pt - Y.ref_rel_to).where(call)
    Y['len_err'] = (Y.pred_len - Y.ref_len).where(call)
    Y['ref_contained'] = ((pf <= Y.ref_rel_from) & (pt >= Y.ref_rel_to)).where(call)
    Y['pred_contained'] = ((pf >= Y.ref_rel_from) & (pt <= Y.ref_rel_to)).where(call)
    Y['strand_correct'] = Y.ref_same_strand.where(call)
    has_ref = Y.ref_nc_start.notna()
    cat = np.select(
        [Y.cohort.isin(['PIL']) & call,
         Y.cohort.isin(['PIL']) & ~call,
         ~Y.cohort.isin(['POS', 'POS_S5', 'PIL']) & call,
         ~Y.cohort.isin(['POS', 'POS_S5', 'PIL']) & ~call,
         has_ref & (Y.ref_frac_in_window == 0),
         ~call,
         Y.IoU >= 0.5,
         Y.overlap_nt >= 1],
        ['new candidate in previously ncRNA-negative system',
         'method abstention',
         'control: call made',
         'control: no call',
         'system unsuitable for this method',
         'method abstention',
         'existing pair rediscovered',
         'existing pair predicted with altered boundary'],
        default='existing pair not rediscovered')
    Y['category'] = cat
    Y['level_detection'] = Y.set_signal if rule != 'SENS_ANY_COV' else (Y.n_sig_pairs >= 1)
    Y['level_region'] = (Y.overlap_nt >= 1) & call
    Y['level_boundary'] = (Y.IoU >= 0.5) & (Y.err5.abs() <= 20) & (Y.err3.abs() <= 20) & call
    rows.append(Y)
E = pd.concat(rows, ignore_index=True)

# ---- positional baseline P0 (A_T3, suitable, in no benchmark set) ----
allm = duckdb.sql(f"""SELECT physical_locus_key, rt_start, rt_end, rt_strand, ref_nc_start, ref_nc_end
    FROM read_parquet('{SCRATCH}/master/master_rt_system.parquet')
    WHERE nc_status = 'A_T3' AND suitability = 'OK'""").df()
allm = allm[~allm.physical_locus_key.isin(set(mem.physical_locus_key))]
r1 = rel(allm.ref_nc_start, allm.rt_start, allm.rt_end, allm.rt_strand)
r2 = rel(allm.ref_nc_end, allm.rt_start, allm.rt_end, allm.rt_strand)
p0_from, p0_to = float(np.median(np.fmin(r1, r2))), float(np.median(np.fmax(r1, r2)))
B0 = X[X.cohort.isin(['POS', 'POS_S5']) & (X.arm == 'A_SPIRE')].copy()
B0['arm'], B0['rule'], B0['call'] = 'P0_POSITIONAL_BASELINE', 'BASELINE', True
B0['pred_len'] = p0_to - p0_from + 1
ov = (np.fmin(p0_to, B0.ref_rel_to) - np.fmax(p0_from, B0.ref_rel_from) + 1).clip(lower=0)
B0['overlap_nt'], B0['IoU'] = ov, ov / (B0.pred_len + B0.ref_len - ov)
B0['Dice'] = 2 * ov / (B0.pred_len + B0.ref_len)
B0['err5'], B0['err3'] = p0_from - B0.ref_rel_from, p0_to - B0.ref_rel_to
B0['len_err'] = B0.pred_len - B0.ref_len
B0['category'] = np.where(B0.IoU >= 0.5, 'existing pair rediscovered',
                          np.where(ov >= 1, 'existing pair predicted with altered boundary',
                                   'existing pair not rediscovered'))
B0['level_region'] = ov >= 1
B0['level_boundary'] = (B0.IoU >= 0.5) & (B0.err5.abs() <= 20) & (B0.err3.abs() <= 20)
E = pd.concat([E, B0], ignore_index=True)
E['p0_interval'] = f'{p0_from:.0f}..{p0_to:.0f}'

keep = ['cohort', 'stratum', 'set_id', 'member_id', 'arm', 'rule', 'physical_locus_key', 'rt_seq_hash',
        'type_label', 'evidence_stratum', 'tax_phylum', 'nc_status', 'previously_validated',
        'ref_detection_model', 'ref_evalue', 'ref_T4', 'ref_signed_distance_bp', 'ref_len', 'ref_rel_from',
        'ref_rel_to', 'ref_frac_in_window', 'ref_overlaps_rt_cds', 'nseq_used', 'avgid', 'expected_cov',
        'observed_cov', 'obs_exp_ratio', 'n_sig_pairs', 'min_sig_E', 'n_supported_helices', 'set_signal',
        'low_power', 'verbatim_spire_parse_n_sig', 'call', 'abstain_reason', 'pred_rel_from', 'pred_rel_to',
        'sens_rel_from', 'sens_rel_to', 'struct_rel_from', 'struct_rel_to', 'pred_len', 'overlap_nt', 'IoU',
        'Dice', 'err5', 'err3', 'len_err', 'ref_contained', 'pred_contained', 'strand_correct',
        'level_detection', 'level_region', 'level_boundary', 'category', 'p0_interval']
E = E[[c for c in keep if c in E.columns]]
E.to_csv(TABLES / 'EVAL_member_level.tsv', sep='\t', index=False)

S = (X.groupby(['cohort', 'stratum', 'set_id', 'arm'])
       .agg(n=('member_id', 'size'), nseq_used=('nseq_used', 'first'), avgid=('avgid', 'first'),
            expected_cov=('expected_cov', 'first'), observed_cov=('observed_cov', 'first'),
            obs_exp=('obs_exp_ratio', 'first'), n_sig=('n_sig_pairs', 'first'),
            n_sup_helices=('n_supported_helices', 'first'), signal_primary=('set_signal', 'first'),
            low_power=('low_power', 'first'), verbatim_parse=('verbatim_spire_parse_n_sig', 'first'),
            region_col_lo=('region_col_lo', 'first'), region_col_hi=('region_col_hi', 'first'),
            member_calls_primary=('member_call', 'sum'), member_calls_sens=('sens_member_call', 'sum'))
       .reset_index())
S['signal_sens'] = S.n_sig >= 1
S.to_csv(TABLES / 'EVAL_set_level.tsv', sep='\t', index=False)
print(f'P0 baseline interval: {p0_from:.0f}..{p0_to:.0f} (n={len(allm):,} A_T3 loci outside benchmark)')
print(E[E.cohort.isin(['POS'])].groupby(['arm', 'rule']).category.value_counts().unstack(fill_value=0).to_string())
