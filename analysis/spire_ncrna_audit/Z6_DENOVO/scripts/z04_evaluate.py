"""z04 — set outcomes (DESIGN §8) and, AFTER the freeze check, reference reveal (§9).

Control pairing: for CMF the primary comparison is top motif vs control's top motif; a secondary
"any motif" variant is reported beside it. For MLOC/QINSI there is one region per set.
Outcome precedence when §8.1–3 fail: RUN_FAILED > NOT_LOCALISED > LOW_POWER > NO_COVARIATION.
MIXED set-level rediscovery = ≥ 50 % of matched members with ≥ 1 nt overlap.
"""
import hashlib
import sys
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from common import SCRATCH, DERIVED  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
T = HERE / 'tables'
RES, SPN = SCRATCH / 'z6/z6_set_arm_results.tsv', SCRATCH / 'z6/z6_member_spans.tsv'
frozen = set(pd.read_csv(T / 'PREDICTIONS_FROZEN.tsv', sep='\t').sha256)
for p in (RES, SPN):
    if hashlib.sha256(p.read_bytes()).hexdigest() not in frozen:
        sys.exit(f'REFUSING: {p} not in PREDICTIONS_FROZEN.tsv')

R = pd.read_csv(RES, sep='\t')
SP = pd.read_csv(SPN, sep='\t')
S = pd.read_csv(T / 'Z6_SETS.tsv', sep='\t')
MEM = pd.read_csv(T / 'Z6_SET_MEMBERS.tsv', sep='\t')
R = R.merge(S[['set_id', 'cohort']], on='set_id')


def reason(r):
    if str(r.get('status', '')).startswith('RUN_FAILED'):
        return 'RUN_FAILED'
    if r.get('status') == 'NO_MOTIF' or not (r.coverage >= 0.5 and r.centre_sd <= 50):
        return 'NOT_LOCALISED'
    if r.low_power == True:  # noqa: E712
        return 'LOW_POWER'
    if not (r.n_sig_pairs >= 2):
        return 'NO_COVARIATION'
    return 'PASSES_1_3'


R['reason'] = R.apply(reason, axis=1)
R['is_top'] = R.is_top.fillna(True)
rows = []
for (sid, arm), g in R[R.cohort != 'CTRL_DISTAL'].groupby(['set_id', 'arm']):
    top = g[g.is_top == True].iloc[0]  # noqa: E712
    c = R[(R.set_id == f'CTRL_{sid}') & (R.arm == arm)]
    ctop = c[c.is_top == True]  # noqa: E712
    ctrl_top_pass = bool(len(ctop)) and ctop.iloc[0].reason == 'PASSES_1_3'
    ctrl_any_pass = bool((c.reason == 'PASSES_1_3').any())
    out = top.reason if top.reason != 'PASSES_1_3' else ('SIGNAL_FAILS_CONTROL' if ctrl_top_pass else 'CANDIDATE')
    any_set = g[g.reason == 'PASSES_1_3']
    out_any = ('CANDIDATE' if (len(any_set) and not ctrl_any_pass) else
               ('SIGNAL_FAILS_CONTROL' if len(any_set) else top.reason))
    rows.append(dict(set_id=sid, cohort=top.cohort, arm=arm, motif=top.motif, outcome=out, outcome_any_motif=out_any,
                     n_members=top.n_members, n_with_span=top.n_with_span, coverage=top.coverage,
                     centre_sd=top.centre_sd, centre_median=top.centre_median, n_sig_pairs=top.n_sig_pairs,
                     expected_cov=top.expected_cov, observed_cov=top.observed_cov, avgid=top.avgid,
                     low_power=top.low_power, control_top_passes=ctrl_top_pass, control_any_passes=ctrl_any_pass,
                     control_reason=ctop.iloc[0].reason if len(ctop) else 'NO_CONTROL_SET'))
O = pd.DataFrame(rows)
O.to_csv(T / 'Z6_SET_OUTCOMES.tsv', sep='\t', index=False)

# ---------------- reveal (first read of reference coordinates) ----------------
c = duckdb.connect()
c.register('mem', MEM)
ref = c.execute(f"""SELECT * EXCLUDE (rn) FROM (
   SELECT m.set_id, m.member_id, p.nc_start, p.nc_end, p.nc_strand, p.detection_model, p.evalue, p.same_strand,
          p.rt_start prs, p.rt_end pre, p.rt_strand prt,
          row_number() OVER (PARTITION BY m.set_id, m.member_id ORDER BY
             (p.canonical AND p.same_strand AND p.direction <> 'downstream' AND p.n_cds_between = 0
              AND abs(p.signed_distance_bp) <= 200 AND p.evalue <= 1e-5) DESC, p.evalue) rn
   FROM mem m JOIN read_parquet('{DERIVED}/rt_ncrna_pairs_v1.parquet') p ON p.locus_key = m.locus_key
   WHERE m.locus_class LIKE 'MATCHED%' AND p.file_label = 'Retron') WHERE rn = 1""").df()
a = np.where(ref.prt == '+', ref.nc_start - ref.prs, ref.pre - ref.nc_start)
b = np.where(ref.prt == '+', ref.nc_end - ref.prs, ref.pre - ref.nc_end)
ref['ref_from'], ref['ref_to'] = np.fmin(a, b), np.fmax(a, b)
ref['ref_len'] = ref.ref_to - ref.ref_from + 1

top_motif = R[R.is_top == True][['set_id', 'arm', 'motif']]  # noqa: E712
spans = SP.merge(top_motif, on=['set_id', 'arm', 'motif'])
E = (MEM[['set_id', 'member_id', 'cohort', 'locus_key', 'rt_seq_hash', 'rt90', 'locus_class', 'stratum',
          'type_label', 'tax_genus']]
     .merge(pd.DataFrame({'arm': ['CMF', 'MLOC', 'QINSI']}), how='cross')
     .merge(spans[['set_id', 'arm', 'member_id', 'rel_from', 'rel_to']], on=['set_id', 'arm', 'member_id'], how='left')
     .merge(O[['set_id', 'arm', 'outcome']], on=['set_id', 'arm'], how='left')
     .merge(ref[['set_id', 'member_id', 'ref_from', 'ref_to', 'ref_len', 'detection_model', 'evalue', 'same_strand']],
            on=['set_id', 'member_id'], how='left'))
E = E[~E.cohort.eq('CTRL_DISTAL')]
E['call'] = E.rel_from.notna()
E['pred_len'] = E.rel_to - E.rel_from + 1
ov = (np.fmin(E.rel_to, E.ref_to) - np.fmax(E.rel_from, E.ref_from) + 1).clip(lower=0)
E['overlap_nt'] = ov.where(E.call & E.ref_from.notna())
E['IoU'] = (ov / (E.pred_len + E.ref_len - ov)).where(E.call & E.ref_from.notna())
E['Dice'] = (2 * ov / (E.pred_len + E.ref_len)).where(E.call & E.ref_from.notna())
E['err5'], E['err3'] = E.rel_from - E.ref_from, E.rel_to - E.ref_to
E['len_err'] = E.pred_len - E.ref_len
E['ref_contained'] = (E.rel_from <= E.ref_from) & (E.rel_to >= E.ref_to)
E['ref_frac_in_W'] = ((np.fmin(E.ref_to, 100) - np.fmax(E.ref_from, -600) + 1).clip(lower=0) / E.ref_len)


def chance(r):
    if not r.call or pd.isna(r.ref_from):
        return np.nan
    L = int(r.pred_len)
    st = np.arange(-600, 100 - L + 2)
    en = st + L - 1
    o = (np.minimum(en, r.ref_to) - np.maximum(st, r.ref_from) + 1).clip(min=0)
    return float((o / (L + r.ref_len - o) >= 0.5).mean())


E['chance_rediscovery_p'] = E.apply(chance, axis=1)
matched = E.locus_class.str.startswith('MATCHED')
E['category'] = np.select(
    [matched & E.ref_from.isna(), matched & (E.ref_frac_in_W == 0), matched & ~E.call, matched & (E.IoU >= 0.5),
     matched & (E.overlap_nt >= 1), matched, ~matched & E.call & (E.outcome == 'CANDIDATE'), ~matched & E.call],
    ['system unsuitable for this method', 'system unsuitable for this method', 'method abstention',
     'existing pair rediscovered', 'existing pair predicted with altered boundary', 'existing pair not rediscovered',
     'new candidate in previously ncRNA-unresolved system', 'span in unresolved system, set not a candidate'],
    default='method abstention')
E['level_region'] = E.call & (E.overlap_nt >= 1)
E['level_boundary'] = E.call & (E.IoU >= 0.5) & (E.err5.abs() <= 20) & (E.err3.abs() <= 20)
E.to_csv(T / 'Z6_MEMBER_EVAL.tsv', sep='\t', index=False)

# ---- summaries ----
m = E[matched]
summ = (m.groupby(['cohort', 'arm']).agg(
    matched_members=('call', 'size'), calls=('call', 'sum'), region=('level_region', 'mean'),
    boundary=('level_boundary', 'mean'),
    rediscovered=('category', lambda x: (x == 'existing pair rediscovered').sum()),
    altered=('category', lambda x: (x == 'existing pair predicted with altered boundary').sum()),
    not_rediscovered=('category', lambda x: (x == 'existing pair not rediscovered').sum()),
    abstention=('category', lambda x: (x == 'method abstention').sum()),
    unsuitable=('category', lambda x: (x == 'system unsuitable for this method').sum()),
    chance_expected_rediscovered=('chance_rediscovery_p', 'sum'),
    median_IoU=('IoU', 'median'), median_abs_err5=('err5', lambda x: x.abs().median()),
    median_abs_err3=('err3', lambda x: x.abs().median())).reset_index())
summ.to_csv(T / 'Z6_REDISCOVERY_SUMMARY.tsv', sep='\t', index=False)

mix = []
for (sid, arm), g in E[E.cohort == 'MIXED'].groupby(['set_id', 'arm']):
    gm, gu = g[g.locus_class.str.startswith('MATCHED')], g[g.locus_class.str.startswith('UNMATCHED')]
    red = (gm.overlap_nt >= 1).mean() if len(gm) else np.nan
    refc = ((gm.ref_from + gm.ref_to) / 2).median()
    uc = ((gu.rel_from + gu.rel_to) / 2)
    mix.append(dict(set_id=sid, arm=arm, outcome=g.outcome.iloc[0], matched=len(gm), unmatched=len(gu),
                    matched_region_hit_frac=red, set_rediscovers=red >= 0.5,
                    unmatched_with_span=int(gu.call.sum()),
                    unmatched_span_centre_offset_from_matched_ref_median=float((uc - refc).median()) if gu.call.any() else np.nan,
                    expansion_candidates=int(gu.call.sum()) if (red >= 0.5 and g.outcome.iloc[0] == 'CANDIDATE') else 0))
pd.DataFrame(mix).to_csv(T / 'Z6_MIXED_EXPANSION.tsv', sep='\t', index=False)
pd.set_option('display.width', 250)
print(O[['set_id', 'arm', 'outcome', 'outcome_any_motif', 'coverage', 'centre_sd', 'n_sig_pairs', 'expected_cov',
         'control_reason']].to_string())
print(summ.round(3).to_string())
print(pd.DataFrame(mix).to_string())
