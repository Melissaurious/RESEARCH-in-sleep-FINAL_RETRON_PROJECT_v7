"""r03 — DEV calibration (DESIGN §6). Reveals DEV references only. Never reads HELDOUT.

Outputs: tables/DEV_GRID_RESULTS.tsv (every combination), tables/DEV_CHOSEN.tsv,
tables/DEV_MEMBER_EVAL.tsv (chosen rule), tables/DEV_GROUP_EVAL.tsv.
"""
import itertools
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / 'scripts'))
sys.path.insert(0, str(HERE / 'scripts'))
from common import SCRATCH  # noqa: E402
from r_refs import member_refs, chance_iou50  # noqa: E402

T = HERE / 'tables'
WR = {'W700': (-600, 100), 'W500': (-400, 100)}
SPLIT = pd.read_csv(T / 'SPLIT_MANIFEST.tsv', sep='\t')
MEM = pd.read_csv(T / 'MEMBERS.tsv', sep='\t')
DEVG = SPLIT[(SPLIT.split == 'DEV') & SPLIT.evaluable].gid.tolist()
assert set(MEM[MEM.gid.isin(DEVG)].split) == {'DEV'}
MO = pd.read_csv(SCRATCH / 'r2/dev_grid_motifs.tsv', sep='\t')
SP = pd.read_csv(SCRATCH / 'r2/dev_grid_spans.tsv', sep='\t')
REF = member_refs(MEM[MEM.gid.isin(DEVG)])


from r_rule import candidate, passes  # noqa: E402  (single shared definition)


def correctness(gid, W, span, motif):
    wf, wt = WR[W]
    r = REF[(REF.gid == gid)]
    r = r[(r.ref_to >= wf) & (r.ref_from <= wt)]
    if r.empty:
        return np.nan
    s = SP[(SP.gid == gid) & (SP.key == f'{W}_real') & (SP.span == span) & (SP.motif == motif)]
    x = r.merge(s, on='member_id', how='left')
    hit = (np.fmin(x.rel_to, x.ref_to) - np.fmax(x.rel_from, x.ref_from) + 1).fillna(0) >= 1
    return float(hit.mean())


def has_ref(gid, W):
    wf, wt = WR[W]
    r = REF[REF.gid == gid]
    return bool(((r.ref_to >= wf) & (r.ref_from <= wt)).any())


HAS_REF = {(g, W): has_ref(g, W) for g in DEVG for W in WR}
GRID = dict(c=[0.5, 0.7], s=[30, 50], k=[0.3, 0.5], b=[0, 20, 40])
rows, cache_corr = [], {}
by_run = {kk: g for kk, g in MO.groupby(['gid', 'key', 'span'])}
for W, span, ranking in itertools.product(['W700', 'W500'], [100, 170, 260], ['R_A', 'R_B']):
    for c, s, k, b in itertools.product(*GRID.values()):
        n_ref = n_pass = n_corr = n_ctrl = n_grp = 0
        for gid in DEVG:
            n_grp += 1
            mr = candidate(by_run.get((gid, f'{W}_real', span), MO.iloc[:0]), ranking, k)
            mc = candidate(by_run.get((gid, f'{W}_ctrl', span), MO.iloc[:0]), ranking, k)
            pr, pc = passes(mr, c, s, k, b), passes(mc, c, s, k, b)
            n_ctrl += pc
            key = (gid, W, span, None if mr is None else mr.motif)
            if key not in cache_corr:
                cache_corr[key] = np.nan if mr is None else correctness(gid, W, span, mr.motif)
            cf = cache_corr[key]
            if HAS_REF[(gid, W)]:          # denominator depends only on the reference, never on the candidate
                n_ref += 1
                n_pass += pr
                n_corr += bool(pr and cf >= 0.5)
        rows.append(dict(W=W, span=span, ranking=ranking, c=c, s=s, k=k, b=b, dev_groups=n_grp,
                         groups_with_ref_in_window=n_ref, real_pass=n_pass / n_ref, correct_pass=n_corr / n_ref,
                         ctrl_pass=n_ctrl / n_grp, precision=n_corr / n_pass if n_pass else np.nan,
                         J=n_corr / n_ref - n_ctrl / n_grp))
R = pd.DataFrame(rows)
R.to_csv(T / 'DEV_GRID_RESULTS.tsv', sep='\t', index=False)

# ---- choose: max J with ctrl ≤ 0.05; ties (ΔJ ≤ 0.005) → looser constraints, then cheaper config ----
el = R[R.ctrl_pass <= 0.05].copy()
best = el.J.max()
tie = el[el.J >= best - 0.005].copy()
tie['looseness'] = (-tie.c) + tie.s / 100 + tie.k - tie.b / 100
tie['cost'] = tie.span / 100 + (tie.W == 'W700') * 0.5
ch = tie.sort_values(['looseness', 'cost'], ascending=[False, True]).iloc[0]
pd.DataFrame([ch]).to_csv(T / 'DEV_CHOSEN.tsv', sep='\t', index=False)

# ---- member- and group-level evaluation of the chosen rule on DEV ----
W, span, ranking = ch.W, int(ch.span), ch.ranking
wf, wt = WR[W]
mrows, grows = [], []
for gid in DEVG:
    for kind in ['real', 'ctrl']:
        m = candidate(by_run.get((gid, f'{W}_{kind}', span), MO.iloc[:0]), ranking, ch.k)
        p = passes(m, ch.c, ch.s, ch.k, ch.b)
        grows.append(dict(gid=gid, kind=kind, candidate=None if m is None else m.motif, passes=p,
                          coverage=None if m is None else m.coverage, centre_sd=None if m is None else m.centre_sd,
                          coding_frac=None if m is None else m.coding_frac, cov_state=None if m is None else m.cov_state,
                          correct_frac=cache_corr.get((gid, W, span, None if m is None else m.motif)) if kind == 'real' else None))
        if kind == 'real':
            s = SP[(SP.gid == gid) & (SP.key == f'{W}_real') & (SP.span == span) &
                   (SP.motif == (None if m is None else m.motif))] if p else SP.iloc[:0]
            x = REF[REF.gid == gid].merge(s[['member_id', 'rel_from', 'rel_to']], on='member_id', how='left')
            x['set_passes'] = p
            mrows.append(x)
G = pd.DataFrame(grows)
E = pd.concat(mrows, ignore_index=True)
E['in_window'] = (E.ref_to >= wf) & (E.ref_from <= wt)
E['call'] = E.rel_from.notna()
L = E.rel_to - E.rel_from + 1
ov = (np.fmin(E.rel_to, E.ref_to) - np.fmax(E.rel_from, E.ref_from) + 1).clip(lower=0)
E['IoU'] = (ov / (L + E.ref_len - ov)).where(E.call)
E['any_overlap'] = (ov >= 1) & E.call
E['err5'], E['err3'] = (E.rel_from - E.ref_from).where(E.call), (E.rel_to - E.ref_to).where(E.call)
E['both_ends_20'] = (E.err5.abs() <= 20) & (E.err3.abs() <= 20)
E['len_err'] = (L - E.ref_len).where(E.call)
E['chance_p'] = [chance_iou50(l, a, b, wf, wt) if c else np.nan for l, a, b, c in zip(L.fillna(0), E.ref_from, E.ref_to, E.call)]
E.to_csv(T / 'DEV_MEMBER_EVAL.tsv', sep='\t', index=False)
G.to_csv(T / 'DEV_GROUP_EVAL.tsv', sep='\t', index=False)

e = E[E.in_window]
summ = dict(rule=f"{W} span{span} {ranking} c{ch.c} s{ch.s} k{ch.k} b{ch.b}", J=ch.J, real_pass=ch.real_pass,
            ctrl_pass=ch.ctrl_pass, precision=ch.precision, abstention=1 - ch.real_pass,
            members_in_window=len(e), rediscovered_iou50=int((e.IoU >= 0.5).sum()),
            chance_expected=float(e.chance_p.sum()), any_overlap=int(e.any_overlap.sum()),
            both_ends_20=int((e.both_ends_20 & e.call).sum()))
pd.DataFrame([summ]).to_csv(T / 'DEV_CHOSEN_SUMMARY.tsv', sep='\t', index=False)
pd.set_option('display.width', 250)
print(R.sort_values('J', ascending=False).head(15).to_string())
print(pd.Series(summ).to_string())
print(R.groupby(['W', 'span', 'ranking']).J.max().to_string())
