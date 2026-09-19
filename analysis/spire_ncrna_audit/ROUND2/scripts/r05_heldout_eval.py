"""r05 — HELDOUT evaluation with the frozen rule and gate (DESIGN §7–9). Reveals HELDOUT references.

Refuses unless (a) FROZEN_RULE.json's sha256 is in tables/FREEZE.tsv and (b) the held-out motif/span outputs'
sha256 are in tables/PREDICTIONS_FROZEN.tsv.
Control pass = rule only (no stability requirement) — conservative for discrimination (G2).
"""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / 'scripts'))
sys.path.insert(0, str(HERE / 'scripts'))
from common import SCRATCH  # noqa: E402
from r_rule import candidate, passes, concordant  # noqa: E402

T = HERE / 'tables'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
FZ = set(pd.read_csv(T / 'FREEZE.tsv', sep='\t').sha256)
PF = set(pd.read_csv(T / 'PREDICTIONS_FROZEN.tsv', sep='\t').sha256)
RULE_P = HERE / 'FROZEN_RULE.json'
MO_P, SP_P = SCRATCH / 'r2/heldout_motifs.tsv', SCRATCH / 'r2/heldout_spans.tsv'
if sha(RULE_P) not in FZ:
    sys.exit('REFUSING: FROZEN_RULE.json not recorded in FREEZE.tsv')
for p in (MO_P, SP_P):
    if sha(p) not in PF:
        sys.exit(f'REFUSING: {p} not recorded in PREDICTIONS_FROZEN.tsv')
from r_refs import member_refs, chance_iou50  # noqa: E402  (reveal happens only after both checks)

RULE = json.loads(RULE_P.read_text())
W, span = RULE['W'], RULE['span']
wf, wt = {'W700': (-600, 100), 'W500': (-400, 100)}[W]
SPLIT = pd.read_csv(T / 'SPLIT_MANIFEST.tsv', sep='\t')
MEM = pd.read_csv(T / 'MEMBERS.tsv', sep='\t')
HG = SPLIT[(SPLIT.split == 'HELDOUT') & SPLIT.evaluable]
MO, SP = pd.read_csv(MO_P, sep='\t'), pd.read_csv(SP_P, sep='\t')
runs = {k: g for k, g in MO.groupby(['gid', 'key'])}
empty = MO.iloc[:0]
REF = member_refs(MEM[MEM.gid.isin(HG.gid)])

grows, mrows = [], []
for g in HG.itertuples():
    real = candidate(runs.get((g.gid, f'{W}_real'), empty), RULE['ranking'], RULE['k'])
    rule_pass = passes(real, RULE['c'], RULE['s'], RULE['k'], RULE['b'])
    ctrl = candidate(runs.get((g.gid, f'{W}_ctrl'), empty), RULE['ranking'], RULE['k'])
    ctrl_pass = passes(ctrl, RULE['c'], RULE['s'], RULE['k'], RULE['b'])
    stab = {}
    if g.stability_testable:
        for sub in ['halfA', 'halfB', 'lco']:
            key = f'{W}_real_{sub}'
            stab[sub] = concordant(real, runs[(g.gid, key)], RULE) if (g.gid, key) in runs else None
    halves_ok = bool(stab.get('halfA')) and bool(stab.get('halfB'))
    final = rule_pass and (halves_ok if g.stability_testable else True)
    # boundary dispersion across full + halves (candidate median start/end)
    ends = []
    for key in [f'{W}_real'] + ([f'{W}_real_halfA', f'{W}_real_halfB'] if g.stability_testable else []):
        m = candidate(runs.get((g.gid, key), empty), RULE['ranking'], RULE['k'])
        if m is not None:
            s = SP[(SP.gid == g.gid) & (SP.key == key) & (SP.motif == m.motif)]
            ends.append((s.rel_from.median(), s.rel_to.median()))
    r = REF[(REF.gid == g.gid)]
    r_in = r[(r.ref_to >= wf) & (r.ref_from <= wt)]
    s = SP[(SP.gid == g.gid) & (SP.key == f'{W}_real') & (SP.motif == (real.motif if real is not None else None))]
    x = r.merge(s[['member_id', 'rel_from', 'rel_to']], on='member_id', how='left')
    x['set_final_pass'] = final
    if not final:
        x[['rel_from', 'rel_to']] = np.nan
    mrows.append(x)
    hit = ((np.fmin(x.rel_to, x.ref_to) - np.fmax(x.rel_from, x.ref_from) + 1).fillna(0) >= 1)
    in_w = (x.ref_to >= wf) & (x.ref_from <= wt)
    grows.append(dict(gid=g.gid, type=g.type_modal, depth=g.pool_rt90, divergence=g.divergence_rt70_per_rt90,
                      deposition_loci=g.loci, exact_rt=g.pool_exact_rt, n_members=g.n_members,
                      testable=g.stability_testable, rule_pass=rule_pass, final_pass=final, ctrl_pass=ctrl_pass,
                      halfA=stab.get('halfA'), halfB=stab.get('halfB'), lco=stab.get('lco'),
                      boundary_sd_start=float(np.std([e[0] for e in ends])) if len(ends) > 1 else np.nan,
                      boundary_sd_end=float(np.std([e[1] for e in ends])) if len(ends) > 1 else np.nan,
                      coding_frac=None if real is None else real.coding_frac,
                      cov_state=None if real is None else real.cov_state,
                      has_ref_in_window=bool(len(r_in)), correct=bool(final and len(r_in) and hit[in_w].mean() >= 0.5),
                      ref_len_median=r.ref_len.median(), ref_dist_median=r.signed_distance_bp.abs().median(),
                      topology_modal=r.topology.mode().iloc[0] if len(r) else 'NA'))
GR = pd.DataFrame(grows)
E = pd.concat(mrows, ignore_index=True)
E['in_window'] = (E.ref_to >= wf) & (E.ref_from <= wt)
E['call'] = E.rel_from.notna()
L = E.rel_to - E.rel_from + 1
ov = (np.fmin(E.rel_to, E.ref_to) - np.fmax(E.rel_from, E.ref_from) + 1).clip(lower=0)
E['IoU'] = (ov / (L + E.ref_len - ov)).where(E.call)
E['any_overlap'] = (ov >= 1) & E.call
E['err5'], E['err3'] = (E.rel_from - E.ref_from).where(E.call), (E.rel_to - E.ref_to).where(E.call)
E['both_ends_20'] = E.call & (E.err5.abs() <= 20) & (E.err3.abs() <= 20)
E['len_err'] = (L - E.ref_len).where(E.call)
E['chance_p'] = [chance_iou50(l, a, b, wf, wt) if c else np.nan for l, a, b, c in zip(L.fillna(0), E.ref_from, E.ref_to, E.call)]
E.to_csv(T / 'HELDOUT_MEMBER_EVAL.tsv', sep='\t', index=False)
GR.to_csv(T / 'HELDOUT_GROUP_EVAL.tsv', sep='\t', index=False)

# ---- supplementary non-retron controls ----
nr = [dict(gid=gid, passes=passes(candidate(runs.get((gid, f'{W}_real'), empty), RULE['ranking'], RULE['k']),
                                  RULE['c'], RULE['s'], RULE['k'], RULE['b']))
      for gid in sorted({k[0] for k in runs if str(k[0]).startswith('NONRETRON_')})]
pd.DataFrame(nr).to_csv(T / 'HELDOUT_NONRETRON_CONTROLS.tsv', sep='\t', index=False)

# ---- gate ----
e = E[E.in_window]
obs = int((e.IoU >= 0.5).sum())
p_ = e.chance_p.dropna().values
rng = np.random.default_rng(20260919)
sim = (rng.random((20000, len(p_))) < p_).sum(1) if len(p_) else np.zeros(20000)
exp_ = float(p_.sum())
perm_p = float((np.sum(sim >= obs) + 1) / (len(sim) + 1))
n_ref_groups = int(GR.has_ref_in_window.sum())
real_rate = GR[GR.has_ref_in_window].final_pass.mean()
ctrl_rate = GR.ctrl_pass.mean()
passes_ = GR[GR.final_pass]
prec = passes_.correct.mean() if len(passes_) else np.nan
testable_pass = GR[GR.rule_pass & GR.testable]   # stability measured on rule passes (as on DEV), not on stability-filtered passes
stab_rate = ((testable_pass.halfA == True) & (testable_pass.halfB == True)).mean() if len(testable_pass) else np.nan  # noqa: E712
abst = 1 - real_rate
coding_art = (passes_.coding_frac > 0.5).mean() if len(passes_) else np.nan
G = RULE['gate']
checks = dict(
    G1_enrichment=dict(obs=obs, expected=exp_, ratio=obs / exp_ if exp_ else np.inf, perm_p=perm_p,
                       pass_=bool(exp_ > 0 and obs / exp_ >= G['G1_ratio'] and perm_p < G['G1_p'])),
    G2_discrimination=dict(real=real_rate, ctrl=ctrl_rate, diff=real_rate - ctrl_rate,
                           pass_=bool(real_rate - ctrl_rate >= G['G2_min_diff'] and ctrl_rate <= G['G2_max_ctrl'])),
    G3_precision=dict(precision=prec, n_pass=len(passes_), pass_=bool(len(passes_) and prec >= G['G3_min_precision'])),
    G4_stability=dict(rate=stab_rate, n_testable_pass=len(testable_pass),
                      pass_=bool(len(testable_pass) and stab_rate >= G['G4_min_stability'])),
    G5_abstention=dict(abstention=abst, pass_=bool(abst <= G['G5_max_abstention'])),
    G6_coding=dict(rate=coding_art, pass_=bool(len(passes_) and coding_art <= G['G6_max_coding'])))
p0f, p0t = G['G7_positional_prior']['P0_from'], G['G7_positional_prior']['P0_to']
L0 = p0t - p0f + 1
ov0 = (np.fmin(p0t, e.ref_to) - np.fmax(p0f, e.ref_from) + 1).clip(lower=0)
p0_iou50 = int((ov0 / (L0 + e.ref_len - ov0) >= 0.5).sum())
p0_ends20 = int(((abs(p0f - e.ref_from) <= 20) & (abs(p0t - e.ref_to) <= 20)).sum())
g7 = dict(method_iou50=obs, P0_iou50=p0_iou50, method_ends20=int(e.both_ends_20.sum()), P0_ends20=p0_ends20,
          pass_=bool(obs >= p0_iou50))
under = len(passes_) < G['min_passes_for_decision'] or n_ref_groups < 20


def decide(chk):
    ok = all(v['pass_'] for v in chk.values())
    return ('UNDERPOWERED/INCONCLUSIVE' if under and ok else 'ROUND2_PASS_SMALL_UNRESOLVED_PILOT' if ok
            else 'ROUND2_FAIL_STOP')


decision_g1_g6 = decide(checks)
checks['G7_positional_prior'] = g7
decision = decide(checks)
out = dict(rule=RULE, n_heldout_groups=len(HG), n_with_ref_in_window=n_ref_groups, checks=checks, decision=decision,
           decision_predeclared_G1_G6=decision_g1_g6,
           members_in_window=len(e), any_overlap=int(e.any_overlap.sum()), both_ends_20=int(e.both_ends_20.sum()),
           median_abs_err5=float(e.err5.abs().median()) if e.call.any() else None,
           median_abs_err3=float(e.err3.abs().median()) if e.call.any() else None,
           median_len_err=float(e.len_err.median()) if e.call.any() else None,
           nonretron_pass=f"{sum(x['passes'] for x in nr)}/{len(nr)}")
(T / 'HELDOUT_DECISION.json').write_text(json.dumps(out, indent=2, default=float))
print(json.dumps(out, indent=2, default=float))
