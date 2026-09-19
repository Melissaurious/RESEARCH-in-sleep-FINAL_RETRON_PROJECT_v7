"""r06 — held-out failure analysis by stratum (post-evaluation; descriptive)."""
import numpy as np, pandas as pd
from pathlib import Path
T = Path(__file__).resolve().parents[1] / 'tables'
G = pd.read_csv(T / 'HELDOUT_GROUP_EVAL.tsv', sep='\t'); E = pd.read_csv(T / 'HELDOUT_MEMBER_EVAL.tsv', sep='\t')
e = E[E.in_window].copy()
p0f, p0t = -193, -24
ov0 = (np.fmin(p0t, e.ref_to) - np.fmax(p0f, e.ref_from) + 1).clip(lower=0)
e['P0_iou50'] = ov0 / ((p0t - p0f + 1) + e.ref_len - ov0) >= .5
e['m_iou50'] = e.IoU >= .5
e = e.merge(G[['gid', 'type', 'depth', 'divergence', 'deposition_loci']], on='gid')
bins = {'ref_len': ('ref_len', [0, 140, 170, 220, 1e9]), 'depth': ('depth', [0, 9, 19, 1e9]),
        'divergence': ('divergence', [0, .34, .67, 1.01]), 'deposition': ('deposition_loci', [0, 100, 1000, 1e9])}
rows = []
for name, (col, b) in bins.items():
    for lvl, g in e.groupby(pd.cut(e[col], b), observed=True):
        rows.append(dict(facet=name, level=str(lvl), members=len(g), groups=g.gid.nunique(), method_any=g.any_overlap.mean(),
                         method_iou50=g.m_iou50.mean(), P0_iou50=g.P0_iou50.mean(), method_ends20=g.both_ends_20.mean()))
for name in ['type', 'topology']:
    for lvl, g in e.groupby(name):
        rows.append(dict(facet=name, level=lvl, members=len(g), groups=g.gid.nunique(), method_any=g.any_overlap.mean(),
                         method_iou50=g.m_iou50.mean(), P0_iou50=g.P0_iou50.mean(), method_ends20=g.both_ends_20.mean()))
F = pd.DataFrame(rows); F.to_csv(T / 'HELDOUT_FAILURE_ANALYSIS.tsv', sep='\t', index=False)
gs = G.groupby('type').agg(groups=('gid', 'size'), final_pass=('final_pass', 'mean'), ctrl_pass=('ctrl_pass', 'mean'), correct=('correct', 'sum')).reset_index()
gs.to_csv(T / 'HELDOUT_GROUP_BY_TYPE.tsv', sep='\t', index=False)
st = G[G.rule_pass & G.testable]
stab = dict(testable_rule_pass=len(st), halves_concordant=int(((st.halfA == True) & (st.halfB == True)).sum()),
            lco_survival=int((st.lco == True).sum()), lco_testable=int(st.lco.notna().sum()),
            median_boundary_sd_start=float(st.boundary_sd_start.median()), median_boundary_sd_end=float(st.boundary_sd_end.median()))
pd.DataFrame([stab]).to_csv(T / 'HELDOUT_STABILITY.tsv', sep='\t', index=False)
pd.set_option('display.width', 220); print(F.round(3).to_string()); print(gs.to_string()); print(stab)
