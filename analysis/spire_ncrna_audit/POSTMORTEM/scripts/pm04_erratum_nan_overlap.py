"""pm04 — erratum: np.fmin/np.fmax ignore NaN, so a member WITHOUT a motif instance was scored as overlapping its
reference in (a) r03 DEV correctness (J, precision) and (b) r05 held-out 'correct' (G3). Recompute both correctly.
G1/G7 (IoU masked by call) and every Round-1 metric are unaffected. The Round-2 decision cannot change (G1, G7 fail)."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / 'scripts')); sys.path.insert(0, str(HERE.parent / 'ROUND2/scripts'))
from common import SCRATCH
from r_rule import candidate, passes
from r_refs import member_refs
R2 = HERE.parent / 'ROUND2'; T = R2 / 'tables'
RULE = json.loads((R2 / 'FROZEN_RULE.json').read_text()); a = (RULE['c'], RULE['s'], RULE['k'], RULE['b'])
S = pd.read_csv(T / 'SPLIT_MANIFEST.tsv', sep='\t'); M = pd.read_csv(T / 'MEMBERS.tsv', sep='\t')
MO = pd.concat([pd.read_csv(SCRATCH / f'r2/{t}_motifs.tsv', sep='\t') for t in ['dev_grid', 'heldout']])
SP = pd.concat([pd.read_csv(SCRATCH / f'r2/{t}_spans.tsv', sep='\t') for t in ['dev_grid', 'heldout']])
MO, SP = MO[MO.span == 260], SP[SP.span == 260]
runs = {k: g for k, g in MO.groupby(['gid', 'key'])}; E0 = MO.iloc[:0]
REF = member_refs(M[M.gid.isin(S[S.evaluable].gid)])
out = []
for split in ['DEV', 'HELDOUT']:
    rows = []
    for g in S[(S.split == split) & S.evaluable].itertuples():
        m = candidate(runs.get((g.gid, 'W500_real'), E0), RULE['ranking'], RULE['k']); p = passes(m, *a)
        r = REF[(REF.gid == g.gid) & (REF.ref_to >= -400) & (REF.ref_from <= 100)]
        s = SP[(SP.gid == g.gid) & (SP.key == 'W500_real') & (SP.motif == (m.motif if m is not None else None))]
        x = r.merge(s[['member_id', 'rel_from', 'rel_to']], on='member_id', how='left')
        ov = (np.minimum(x.rel_to, x.ref_to) - np.maximum(x.rel_from, x.ref_from) + 1)      # NaN-propagating
        buggy = (np.fmin(x.rel_to, x.ref_to) - np.fmax(x.rel_from, x.ref_from) + 1).fillna(0) >= 1
        fixed = ov.fillna(0) >= 1
        rows.append(dict(gid=g.gid, rule_pass=p, has_ref=len(r) > 0, correct_buggy=bool(p and len(r) and buggy.mean() >= .5),
                         correct_fixed=bool(p and len(r) and fixed.mean() >= .5)))
    D = pd.DataFrame(rows)
    rp = D[D.rule_pass]
    out.append(dict(split=split, groups=len(D), rule_pass=int(D.rule_pass.sum()),
                    precision_buggy=rp.correct_buggy.mean(), precision_fixed=rp.correct_fixed.mean(),
                    correct_fixed=int(rp.correct_fixed.sum())))
O = pd.DataFrame(out); O.to_csv(HERE / 'tables/ERRATUM_NAN_OVERLAP.tsv', sep='\t', index=False)
print(O.round(3).to_string())
