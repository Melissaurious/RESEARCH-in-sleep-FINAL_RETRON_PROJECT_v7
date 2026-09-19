"""pm03 — post-mortem analyses (DESIGN §1–5). Descriptive; frozen rule unchanged."""
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / 'scripts')); sys.path.insert(0, str(HERE.parent / 'ROUND2/scripts'))
from common import SCRATCH, ENV  # noqa: E402
from windows import _record, contig_to_rt_relative, rt_relative_to_contig, revcomp  # noqa: E402
from r_rule import candidate, passes  # noqa: E402
from r_refs import member_refs  # noqa: E402

T, R2T = HERE / 'tables', HERE.parent / 'ROUND2/tables'
RULE = json.loads((HERE.parent / 'ROUND2/FROZEN_RULE.json').read_text())
args = (RULE['c'], RULE['s'], RULE['k'], RULE['b'])
SPLIT = pd.read_csv(R2T / 'SPLIT_MANIFEST.tsv', sep='\t'); MEM = pd.read_csv(R2T / 'MEMBERS.tsv', sep='\t')
PM = pd.read_csv(T / 'PANEL_MEMBERS.tsv', sep='\t'); PG = pd.read_csv(T / 'PANEL_GROUPS.tsv', sep='\t').dropna(subset=['gid'])
MO = pd.concat([pd.read_csv(SCRATCH / f'r2/{t}_motifs.tsv', sep='\t') for t in ['dev_grid', 'heldout', 'panel']])
SP = pd.concat([pd.read_csv(SCRATCH / f'r2/{t}_spans.tsv', sep='\t') for t in ['dev_grid', 'heldout', 'panel']])
MO, SP = MO[MO.span == 260], SP[SP.span == 260]
runs = {k: g for k, g in MO.groupby(['gid', 'key'])}
E0 = MO.iloc[:0]


def cand(gid, key):
    m = candidate(runs.get((gid, key), E0), RULE['ranking'], RULE['k'])
    return m, passes(m, *args)


# ---------------- §2 specificity: rule pass by class, real vs distal ----------------
rows = []
ret = SPLIT[SPLIT.evaluable]
for g in ret.itertuples():
    rows.append(dict(gid=g.gid, rt_class='Retron', split=g.split, real=cand(g.gid, 'W500_real')[1], ctrl=cand(g.gid, 'W500_ctrl')[1]))
for g in PG.itertuples():
    rows.append(dict(gid=g.gid, rt_class=g.rt_class, split='PANEL', real=cand(g.gid, 'W500_real')[1], ctrl=cand(g.gid, 'W500_ctrl')[1]))
SPEC = pd.DataFrame(rows)
cls = SPEC.groupby('rt_class').agg(groups=('gid', 'size'), real_pass=('real', 'sum'), ctrl_pass=('ctrl', 'sum')).reset_index()
cls['real_rate'], cls['ctrl_rate'] = cls.real_pass / cls.groups, cls.ctrl_pass / cls.groups
retr, pan = SPEC[SPEC.rt_class == 'Retron'], SPEC[SPEC.rt_class != 'Retron']
odds, p = fisher_exact([[retr.real.sum(), (~retr.real).sum()], [pan.real.sum(), (~pan.real).sum()]])
cls.to_csv(T / 'SPECIFICITY_BY_CLASS.tsv', sep='\t', index=False)
SPEC.to_csv(T / 'SPECIFICITY_BY_GROUP.tsv', sep='\t', index=False)
spec_test = dict(retron_real=f'{retr.real.sum()}/{len(retr)}', panel_real=f'{pan.real.sum()}/{len(pan)}',
                 retron_rate=retr.real.mean(), panel_rate=pan.real.mean(), odds_ratio=odds, fisher_p=p)
gc_pan = PG.groupby('rt_class').gc_real.median()

# ---------------- §1 characterisation of passing instances (retron + panel) ----------------
ALLM = pd.concat([MEM.assign(rt_class='Retron'), PM], ignore_index=True)
inst_rows = []
for g in SPEC[SPEC.real].itertuples():
    m, _ = cand(g.gid, 'W500_real')
    s = SP[(SP.gid == g.gid) & (SP.key == 'W500_real') & (SP.motif == m.motif)]
    for x in s.itertuples():
        mm = ALLM[(ALLM.gid == g.gid) & (ALLM.member_id == x.member_id)].iloc[0]
        rec = _record(mm.source_file, int(mm.byte_offset), int(mm.byte_len))
        rel = lambda v: contig_to_rt_relative(mm.rt_start, mm.rt_end, mm.rt_strand, v)
        f, t = int(x.rel_from), int(x.rel_to)
        cds_nt = 0
        rbs = None
        for cd in rec['cds_annotations']:
            a, b = sorted((rel(cd['start']), rel(cd['end'])))
            if cd.get('is_rt_gene'):
                rbs = (cd.get('prodigal_metadata') or {}).get('rbs_motif')
                continue
            cds_nt += max(0, min(b, t) - max(a, f) + 1)
        nc_hit = 0
        for nc in rec.get('ncrnas', []):
            a, b = sorted((rel(nc['start']), rel(nc['end'])))
            nc_hit += int(min(b, t) >= max(a, f))
        rtlen = int(mm.rt_end - mm.rt_start)
        inst_rows.append(dict(gid=g.gid, rt_class=g.rt_class, member_id=x.member_id, rel_from=f, rel_to=t, len=t - f + 1,
                              centre=(f + t) / 2, dist_to_rt_end=(f + t) / 2 - rtlen,
                              rt_orf_overlap_nt=max(0, t - max(f, 0) + 1) if t >= 0 else 0,
                              nonrt_cds_frac=cds_nt / (t - f + 1), overlaps_rbs_region=bool(t >= -20 and f <= -1),
                              rt_rbs_motif=rbs, overlaps_registered_ncrna=nc_hit > 0,
                              motif=m.motif, ss_bp=m.ss_bp, cov_state=m.cov_state, set_centre_sd=m.centre_sd))
INST = pd.DataFrame(inst_rows)
REF = member_refs(MEM[MEM.gid.isin(retr.gid)])
INST = INST.merge(REF[['gid', 'member_id', 'ref_from', 'ref_to', 'topology']], on=['gid', 'member_id'], how='left')
INST['overlaps_own_ref'] = ((np.minimum(INST.rel_to, INST.ref_to) - np.maximum(INST.rel_from, INST.ref_from) + 1) >= 1) & INST.ref_from.notna()  # NaN-safe (see pm04)
INST.to_csv(T / 'MOTIF_INSTANCES.tsv', sep='\t', index=False)
INST['is_retron'] = INST.rt_class == 'Retron'
char = INST.groupby('rt_class').agg(instances=('gid', 'size'), groups=('gid', 'nunique'),
                                    centre_median=('centre', 'median'), centre_iqr=('centre', lambda v: v.quantile(.75) - v.quantile(.25)),
                                    len_median=('len', 'median'), rt_orf_overlap=('rt_orf_overlap_nt', lambda v: (v > 0).mean()),
                                    nonrt_cds_frac=('nonrt_cds_frac', 'mean'), rbs_region=('overlaps_rbs_region', 'mean'),
                                    registered_ncrna=('overlaps_registered_ncrna', 'mean'),
                                    own_ref=('overlaps_own_ref', 'mean'), ss_bp_median=('ss_bp', 'median'),
                                    cov_supported=('cov_state', lambda v: (v == 'SUPPORTED').mean()),
                                    set_centre_sd_median=('set_centre_sd', 'median')).reset_index()
char['gc_real_median'] = char.rt_class.map(gc_pan)
char.to_csv(T / 'MOTIF_CHARACTERISATION_BY_CLASS.tsv', sep='\t', index=False)

# ---------------- §3 Type III-A dissection ----------------
BLASTN = ENV / 'retron_tradicional/bin/blastn'
tmp = SCRATCH / 'pm/iiia'; tmp.mkdir(parents=True, exist_ok=True)
iiia_g = set(SPLIT[SPLIT.type_modal == 'III-A'].gid)
I3 = INST[INST.gid.isin(iiia_g)].copy()
rep = []
for x in I3.itertuples():
    mm = MEM[(MEM.gid == x.gid) & (MEM.member_id == x.member_id)].iloc[0]
    rec = _record(mm.source_file, int(mm.byte_offset), int(mm.byte_len))
    full, w0 = rec['genomic_context']['full_sequence'].upper(), rec['genomic_context']['actual_window']['start']
    a, b = sorted((rt_relative_to_contig(mm.rt_start, mm.rt_end, mm.rt_strand, x.rel_from),
                   rt_relative_to_contig(mm.rt_start, mm.rt_end, mm.rt_strand, x.rel_to)))
    q = full[a - w0: b - w0 + 1]
    (tmp / 'q.fa').write_text(f'>q\n{q}\n'); (tmp / 's.fa').write_text(f'>s\n{full}\n')
    out = subprocess.run([str(BLASTN), '-query', str(tmp / 'q.fa'), '-subject', str(tmp / 's.fa'), '-outfmt', '6 pident length',
                          '-evalue', '1e-5', '-strand', 'both'], capture_output=True, text=True).stdout.split('\n')
    hits = [l.split('\t') for l in out if l]
    rep.append(sum(float(p_) >= 85 and int(L) >= 0.8 * len(q) for p_, L in hits))
I3['n_copies_in_record'] = rep


def i3class(r):
    if r.overlaps_own_ref:
        return 'THE_REFERENCE_NCRNA'
    if r.overlaps_registered_ncrna:
        return 'OTHER_ANNOTATED_NCRNA'
    if r.n_copies_in_record > 1:
        return 'REPEAT_ELEMENT'
    if r.nonrt_cds_frac >= 0.3:
        return 'NEIGHBOURING_CDS'
    if r.overlaps_rbs_region or (-60 <= r.centre <= 10):
        return 'LEADER_UTR_OR_RBS_REGION'
    return 'UNRESOLVED_CONSERVED_ELEMENT'


I3['class'] = I3.apply(i3class, axis=1)
I3['motif_minus_ref_centre'] = I3.centre - (I3.ref_from + I3.ref_to) / 2
I3.to_csv(T / 'IIIA_INSTANCES.tsv', sep='\t', index=False)
i3g = I3.groupby('gid').agg(instances=('member_id', 'size'), class_modal=('class', lambda v: v.value_counts().index[0]),
                            centre_median=('centre', 'median'), ref_topology=('topology', lambda v: v.value_counts().index[0]),
                            ref_from_median=('ref_from', 'median'), ref_to_median=('ref_to', 'median'),
                            offset_median=('motif_minus_ref_centre', 'median')).reset_index()
i3g.to_csv(T / 'IIIA_GROUPS.tsv', sep='\t', index=False)

# ---------------- §4 positional baseline (HELDOUT; DEV-derived priors) ----------------
DEVREF = member_refs(MEM[MEM.gid.isin(SPLIT[SPLIT.split == 'DEV'].gid)]).merge(SPLIT[['gid', 'type_modal']], on='gid')
DEVREF = DEVREF[(DEVREF.ref_to >= -400) & (DEVREF.ref_from <= 100)]
prior_t = DEVREF.groupby('type_modal').agg(pf=('ref_from', 'median'), pt=('ref_to', 'median')).reset_index()
HE = pd.read_csv(R2T / 'HELDOUT_MEMBER_EVAL.tsv', sep='\t')
HE = HE[HE.in_window].merge(SPLIT[['gid', 'type_modal']], on='gid').merge(prior_t, on='type_modal', how='left')


def iou(f, t, rf, rt):
    ov = (np.fmin(t, rt) - np.fmax(f, rf) + 1).clip(lower=0)
    return ov / ((t - f + 1) + (rt - rf + 1) - ov)


HE['P0_iou'] = iou(-193, -24, HE.ref_from, HE.ref_to)
HE['Ptype_iou'] = iou(HE.pf.fillna(-193), HE.pt.fillna(-24), HE.ref_from, HE.ref_to)
HE['method_vs_P0_iou'] = iou(HE.rel_from, HE.rel_to, -193, -24)
pos = dict(members=len(HE),
           method_iou50=int((HE.IoU >= .5).sum()), P0_iou50=int((HE.P0_iou >= .5).sum()),
           Ptype_iou50=int((HE.Ptype_iou >= .5).sum()),
           method_calls=int(HE.call.sum()),
           method_calls_mostly_inside_P0=int(((HE.rel_from >= -193) & (HE.rel_to <= -24)).sum()),
           method_hits_iou50_inside_P0=int(((HE.IoU >= .5) & (HE.rel_from >= -193 - 20) & (HE.rel_to <= -24 + 20)).sum()),
           ref_start_sd=float(HE.ref_from.std()), ref_end_sd=float(HE.ref_to.std()),
           ref_start_iqr=float(HE.ref_from.quantile(.75) - HE.ref_from.quantile(.25)),
           ref_end_iqr=float(HE.ref_to.quantile(.75) - HE.ref_to.quantile(.25)),
           ref_within_P0_pm20=float(((HE.ref_from >= -213) & (HE.ref_to <= -4)).mean()))
pt = HE.groupby('type_modal').agg(members=('gid', 'size'), method=('IoU', lambda v: (v >= .5).mean()),
                                  P0=('P0_iou', lambda v: (v >= .5).mean()), Ptype=('Ptype_iou', lambda v: (v >= .5).mean()),
                                  ref_start_sd=('ref_from', 'std'), ref_end_sd=('ref_to', 'std')).reset_index()
pt.to_csv(T / 'POSITIONAL_BY_TYPE.tsv', sep='\t', index=False)
prior_t.to_csv(T / 'POSITIONAL_PRIORS_DEV_BY_TYPE.tsv', sep='\t', index=False)

out = dict(specificity=spec_test, positional=pos,
           iiia_instance_classes=I3['class'].value_counts().to_dict(),
           iiia_group_classes=i3g.class_modal.value_counts().to_dict())
(T / 'POSTMORTEM_SUMMARY.json').write_text(json.dumps(out, indent=2, default=float))
pd.set_option('display.width', 250)
print(cls.round(3).to_string()); print(char.round(3).to_string()); print(json.dumps(out, indent=2, default=float))
print(i3g.to_string()); print(pt.round(3).to_string())
