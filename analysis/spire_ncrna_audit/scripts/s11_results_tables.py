"""s11 — BENCHMARK_RESULTS.tsv (member level, positive cohorts) + summary tables.

Adds one post-hoc yardstick (labelled as such): for each call, the probability that an interval of the
same length placed uniformly at random inside the 300-nt window reaches IoU >= 0.5 with the reference
(chance rediscovery). Its mean over calls is the rediscovery rate expected from length alone.
"""
import numpy as np
import pandas as pd
from common import TABLES, AUDIT

E = pd.read_csv(TABLES / 'EVAL_member_level.tsv', sep='\t', low_memory=False)
P = E[E.cohort.isin(['POS', 'POS_S5'])].copy()


def chance(r):
    if not r.call or pd.isna(r.pred_len) or pd.isna(r.ref_rel_from):
        return np.nan
    L = int(r.pred_len)
    starts = np.arange(-300, -L + 1) if L <= 300 else np.array([-300])
    ends = starts + L - 1
    ov = (np.minimum(ends, r.ref_rel_to) - np.maximum(starts, r.ref_rel_from) + 1).clip(min=0)
    iou = ov / (L + r.ref_len - ov)
    return float((iou >= 0.5).mean())


P['chance_rediscovery_p'] = P.apply(chance, axis=1)
P.to_csv(AUDIT / 'BENCHMARK_RESULTS.tsv', sep='\t', index=False)

POS = P[P.cohort == 'POS']
g = (POS.groupby(['arm', 'rule'])
       .agg(n_members=('call', 'size'), n_calls=('call', 'sum'),
            detection=('level_detection', 'mean'), region=('level_region', 'mean'),
            boundary=('level_boundary', 'mean'),
            rediscovered=('category', lambda x: (x == 'existing pair rediscovered').sum()),
            altered=('category', lambda x: (x == 'existing pair predicted with altered boundary').sum()),
            not_rediscovered=('category', lambda x: (x == 'existing pair not rediscovered').sum()),
            abstention=('category', lambda x: (x == 'method abstention').sum()),
            unsuitable=('category', lambda x: (x == 'system unsuitable for this method').sum()),
            median_IoU_calls=('IoU', 'median'), median_Dice_calls=('Dice', 'median'),
            median_abs_err5=('err5', lambda x: x.abs().median()), median_abs_err3=('err3', lambda x: x.abs().median()),
            median_len_err=('len_err', 'median'), ref_contained=('ref_contained', 'mean'),
            strand_correct=('strand_correct', 'mean'),
            expected_rediscovered_by_chance=('chance_rediscovery_p', 'sum'))
       .reset_index())
g.to_csv(TABLES / 'BENCHMARK_SUMMARY.tsv', sep='\t', index=False)

# paired: A SENS vs P0 on the same members
a = POS[(POS.arm == 'A_SPIRE') & (POS.rule == 'SENS_ANY_COV')].set_index('physical_locus_key')
b = POS[POS.arm == 'P0_POSITIONAL_BASELINE'].set_index('physical_locus_key')
j = a[['IoU', 'call']].join(b[['IoU']], rsuffix='_P0')
j = j[j.call == True]
pair = pd.DataFrame([dict(comparison='A_SPIRE SENS_ANY_COV vs P0, members with an A call', n=len(j),
                          A_better=(j.IoU > j.IoU_P0).sum(), P0_better=(j.IoU < j.IoU_P0).sum(),
                          tie=(j.IoU == j.IoU_P0).sum(), median_IoU_A=j.IoU.median(), median_IoU_P0=j.IoU_P0.median())])
pair.to_csv(TABLES / 'BENCHMARK_paired_vs_P0.tsv', sep='\t', index=False)

# previously-validated subset
pv = (POS[POS.previously_validated == True].groupby(['arm', 'rule'])
         .agg(n=('call', 'size'), region=('level_region', 'mean'), boundary=('level_boundary', 'mean'),
              rediscovered=('category', lambda x: (x == 'existing pair rediscovered').sum())).reset_index())
pv.to_csv(TABLES / 'BENCHMARK_previously_validated_subset.tsv', sep='\t', index=False)

# by set
bs = (POS[POS.rule.isin(['PRIMARY_SPIRE', 'SENS_ANY_COV'])].groupby(['set_id', 'type_label', 'arm', 'rule'])
         .agg(n=('call', 'size'), avgid=('avgid', 'first'), expected=('expected_cov', 'first'),
              observed=('observed_cov', 'first'), signal=('set_signal', 'first'), calls=('call', 'sum'),
              region=('level_region', 'mean'), boundary=('level_boundary', 'mean'), median_IoU=('IoU', 'median'))
         .reset_index())
bs.to_csv(TABLES / 'BENCHMARK_by_set.tsv', sep='\t', index=False)
pd.set_option('display.width', 250)
print(g.round(3).to_string())
print(pair.to_string())
print(pv.round(3).to_string())
