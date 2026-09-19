"""r03c — DEV final metrics for the chosen rule incl. stability; writes FROZEN_RULE.json (DEV only)."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / 'scripts')); sys.path.insert(0, str(HERE / 'scripts'))
from common import SCRATCH
from r_rule import candidate, passes, concordant
from r_refs import member_refs
T = HERE / 'tables'
RULE = dict(W='W500', span=260, ranking='R_B', c=0.5, s=50, k=0.5, b=0)
wf, wt = -400, 100
S = pd.read_csv(T / 'SPLIT_MANIFEST.tsv', sep='\t'); M = pd.read_csv(T / 'MEMBERS.tsv', sep='\t')
D = S[(S.split == 'DEV') & S.evaluable]
MO = pd.concat([pd.read_csv(SCRATCH / 'r2/dev_grid_motifs.tsv', sep='\t'), pd.read_csv(SCRATCH / 'r2/dev_stab_motifs.tsv', sep='\t')])
SP = pd.concat([pd.read_csv(SCRATCH / 'r2/dev_grid_spans.tsv', sep='\t'), pd.read_csv(SCRATCH / 'r2/dev_stab_spans.tsv', sep='\t')])
MO, SP = MO[MO.span == 260], SP[SP.span == 260]
runs = {k: g for k, g in MO.groupby(['gid', 'key'])}; E0 = MO.iloc[:0]
REF = member_refs(M[M.gid.isin(D.gid)])
rows = []
for g in D.itertuples():
    real = candidate(runs.get((g.gid, 'W500_real'), E0), 'R_B', .5); rp = passes(real, .5, 50, .5, 0)
    ctrl = candidate(runs.get((g.gid, 'W500_ctrl'), E0), 'R_B', .5); cp = passes(ctrl, .5, 50, .5, 0)
    st = {h: concordant(real, runs.get((g.gid, f'W500_real_{h}'), E0), RULE) for h in ['halfA', 'halfB', 'lco']} if g.stability_testable else {}
    final = rp and (st['halfA'] and st['halfB'] if g.stability_testable else True)
    r = REF[(REF.gid == g.gid) & (REF.ref_to >= wf) & (REF.ref_from <= wt)]
    s = SP[(SP.gid == g.gid) & (SP.key == 'W500_real') & (SP.motif == (real.motif if real is not None else None))]
    x = r.merge(s, on='member_id', how='left'); hit = ((np.fmin(x.rel_to, x.ref_to) - np.fmax(x.rel_from, x.ref_from) + 1).fillna(0) >= 1)
    rows.append(dict(gid=g.gid, testable=g.stability_testable, rule_pass=rp, final=final, ctrl=cp, has_ref=len(r) > 0,
                     correct=bool(final and len(r) and hit.mean() >= .5), halfA=st.get('halfA'), halfB=st.get('halfB'), lco=st.get('lco'),
                     coding=None if real is None else real.coding_frac))
G = pd.DataFrame(rows); G.to_csv(T / 'DEV_FINAL_GROUP_EVAL.tsv', sep='\t', index=False)
hr = G[G.has_ref]
real_rate, ctrl_rate = hr.final.mean(), G.ctrl.mean()
prec = G[G.final].correct.mean()
tp = G[G.rule_pass & G.testable]
stab = ((tp.halfA == True) & (tp.halfB == True)).mean()
lco = (tp.lco == True).mean()
abst = 1 - real_rate
coding = (G[G.final].coding > .5).mean()
dev = dict(real_final_pass=real_rate, ctrl_pass=ctrl_rate, diff=real_rate - ctrl_rate, precision=prec, stability=stab,
           lco_survival=lco, abstention=abst, coding_rate=coding, n_dev=len(G), n_testable_rule_pass=len(tp))
RULE.update(gate=dict(G1_ratio=3.0, G1_p=0.01, G2_min_diff=round(dev['diff'] * 0.5, 4), G2_max_ctrl=0.10,
                      G3_min_precision=round(max(0.6, prec - 0.15), 4), G4_min_stability=0.60,
                      G5_max_abstention=round(abst + 0.15, 4), G6_max_coding=0.10,
                      G7_positional_prior=dict(P0_from=-193, P0_to=-24, rule='method IoU>=0.5 count >= P0 count on same held-out in-window members'),
                      min_passes_for_decision=20),
            dev_metrics=dev, selected_by='Amendment 2', z6_commit='12ea561a5565aca29eeaacbfe8863dc244838fa3')
(HERE / 'FROZEN_RULE.json').write_text(json.dumps(RULE, indent=2, default=float))
print(json.dumps(RULE, indent=2, default=float))
