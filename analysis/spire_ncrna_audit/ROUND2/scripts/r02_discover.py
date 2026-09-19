"""r02 — blind discovery runner (DESIGN §4–5). Reads member FASTAs + record CDS annotation only.

usage: python r02_discover.py <jobs.tsv> <out_tag> [workers]
jobs.tsv columns: gid, fasta_key (e.g. W700_real, W500_ctrl_halfA), span
Writes SCRATCH/r2/runs/<gid>/<fasta_key>__S<span>/ and appends nothing in place: per-run motif features
are collected into SCRATCH/r2/<out_tag>_motifs.tsv and <out_tag>_spans.tsv.
"""
import os
import re
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / 'scripts'))
from common import SCRATCH, ENV, RSCAPE  # noqa: E402
from windows import _record, contig_to_rt_relative  # noqa: E402
from s04_run_sets import rscape_blocks, sig_pairs, one  # noqa: E402

BIN = ENV / 'retron_tradicional/bin'
SETS, RUNS = SCRATCH / 'r2/sets', SCRATCH / 'r2/runs'
WFROM = {'W700_real': -600, 'W700_ctrl': -1900, 'W500_real': -400, 'W500_ctrl': -1500}
MEM = pd.read_csv(HERE / 'tables/MEMBERS.tsv', sep='\t')
if (HERE / 'tables/NONRETRON_MEMBERS.tsv').exists():   # supplementary controls need their records too
    MEM = pd.concat([MEM, pd.read_csv(HERE / 'tables/NONRETRON_MEMBERS.tsv', sep='\t')], ignore_index=True)
ENVV = {**os.environ, 'PATH': f"{BIN}:{os.environ['PATH']}", 'CMfinder': str(ENV / 'retron_tradicional')}


@lru_cache(maxsize=None)
def coding_intervals(gid, member_id):
    """Non-RT CDS intervals and the RT-ORF interior (> +50) in RT-relative coordinates."""
    r = MEM[(MEM.gid == gid) & (MEM.member_id == member_id)].iloc[0]
    rec = _record(r.source_file, int(r.byte_offset), int(r.byte_len))
    iv = []
    for c in rec['cds_annotations']:
        if c.get('is_rt_gene'):
            continue
        a = contig_to_rt_relative(r.rt_start, r.rt_end, r.rt_strand, c['start'])
        b = contig_to_rt_relative(r.rt_start, r.rt_end, r.rt_strand, c['end'])
        iv.append((min(a, b), max(a, b)))
    iv.append((51, int(r.rt_end - r.rt_start)))
    return tuple(iv)


def coding_frac(gid, member_id, f, t):
    cov = np.zeros(t - f + 1, bool)
    for a, b in coding_intervals(gid, member_id):
        lo, hi = max(a, f), min(b, t)
        if lo <= hi:
            cov[lo - f: hi - f + 1] = True
    return float(cov.mean())


def run(job):
    gid, key, span = job
    base = key.split('_half')[0].replace('_lco', '')
    win_from = WFROM[base]
    fa = SETS / gid / f'{key}.fa'
    if not fa.exists():
        return [], [dict(gid=gid, key=key, span=span, status='NO_INPUT')]
    d = RUNS / gid / f'{key}__S{span}'
    d.mkdir(parents=True, exist_ok=True)
    n_in = sum(1 for l in open(fa) if l.startswith('>'))
    if not (d / 'motifs.txt').exists():
        (d / 'seq.fa').write_text(fa.read_text())
        with open(d / 'cmfinder.log', 'w') as fh:
            rc = subprocess.run(['cmfinder04.pl', '-maxspan1', str(span), '-maxspan2', str(span),
                                 '-motifList', 'motifs.txt', 'seq.fa'], cwd=d, stdout=fh, stderr=subprocess.STDOUT,
                                env=ENVV).returncode
        if rc != 0 or not (d / 'motifs.txt').exists():
            return [], [dict(gid=gid, key=key, span=span, status=f'CMFINDER_FAILED_rc{rc}', n_members=n_in)]
    motifs, spans = [], []
    for mf in [l.strip() for l in open(d / 'motifs.txt') if l.strip()]:
        sto = d / mf
        inst, scores, ss = {}, [], ''
        for line in open(sto):
            m = re.match(r'#=GS (\S+)\s+DE (\d+)\.\.(\d+)\s+([-\d.]+)', line)
            if m:
                inst[m[1]] = (win_from + int(m[2]) - 1, win_from + int(m[3]) - 1)
                scores.append(float(m[4]))
            elif line.startswith('#=GC SS_cons'):
                ss += line.split()[-1]
        if not inst:
            continue
        cen = [(a + b) / 2 for a, b in inst.values()]
        cf = [coding_frac(gid, k, a, b) for k, (a, b) in inst.items()]
        rs = d / f'{mf}.rs'
        rs.mkdir(exist_ok=True)
        out = d / f'{mf}.rs.out'
        if not out.exists():
            with open(out, 'w') as fh:
                subprocess.run([str(RSCAPE), '-E', '0.05', '--nofigures', '--outdir', str(rs), str(sto)],
                               stdout=fh, stderr=subprocess.STDOUT)
        hdr, blocks = rscape_blocks(out)
        b0 = blocks[0] if blocks else dict(expected=0.0, observed=0)
        nsig = len(sig_pairs(one(rs, '*.cov')))
        state = 'SUPPORTED' if nsig >= 2 else ('POWERED_ABSENT' if b0['expected'] >= 2 and nsig == 0 else 'UNDERPOWERED')
        motifs.append(dict(gid=gid, key=key, span=span, status='OK', motif=mf, n_members=n_in, n_inst=len(inst),
                           coverage=len(inst) / n_in, centre_median=float(np.median(cen)),
                           centre_sd=float(np.std(cen)) if len(cen) > 1 else np.nan,
                           inst_len_median=float(np.median([b - a + 1 for a, b in inst.values()])),
                           score_sum=float(sum(scores)), score_mean=float(np.mean(scores)),
                           coding_frac=float(np.mean(cf)), ss_bp=ss.count('<') + ss.count('('),
                           avgid=hdr.get('avgid'), n_sig=nsig, expected_cov=b0['expected'], cov_state=state))
        spans += [dict(gid=gid, key=key, span=span, motif=mf, member_id=k, rel_from=a, rel_to=b)
                  for k, (a, b) in inst.items()]
    if not motifs:
        motifs = [dict(gid=gid, key=key, span=span, status='NO_MOTIF', n_members=n_in)]
    return spans, motifs


if __name__ == '__main__':
    jobs = pd.read_csv(sys.argv[1], sep='\t')
    tag = sys.argv[2]
    with Pool(int(sys.argv[3]) if len(sys.argv) > 3 else 44) as p:
        res = p.map(run, list(zip(jobs.gid, jobs.fasta_key, jobs.span)), chunksize=1)
    S = pd.DataFrame([s for sp, _ in res for s in sp])
    Mo = pd.DataFrame([m for _, ms in res for m in ms])
    S.to_csv(SCRATCH / f'r2/{tag}_spans.tsv', sep='\t', index=False)
    Mo.to_csv(SCRATCH / f'r2/{tag}_motifs.tsv', sep='\t', index=False)
    print(Mo.groupby(['span', 'status']).size().to_string())
