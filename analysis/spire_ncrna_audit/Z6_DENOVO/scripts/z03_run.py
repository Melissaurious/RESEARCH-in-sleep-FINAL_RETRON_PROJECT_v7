"""z03 — run arms CMF / MLOC / QINSI on frozen Z6 sets (DESIGN §7–8). Reads no reference coordinates.

Per set × arm: member spans (RT-relative), coverage, positional SD, covariation, power. The
candidate rule's control clause (§8.4) is applied later in z04, pairing each set with its CTRL_ set.
usage: python z03_run.py [workers]
"""
import glob
import os
import re
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from common import SCRATCH, ENV, RSCAPE, MAFFT  # noqa: E402
from s04_run_sets import read_sto, rscape_blocks, sig_pairs, helices, project, one  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
T = HERE / 'tables'
SETS = SCRATCH / 'z6/sets'
BIN = ENV / 'retron_tradicional/bin'
PATHENV = f"{BIN}:{ENV}/locarna_test/bin:{os.environ['PATH']}"
MLOC_FLAGS = ['--stockholm', '--threads', '4', '--plfold-span', '400', '--min-prob', '0.03', '--indel', '-4',
              '--indel-open', '-400', '--max-diff', '100', '--max-diff-am', '-60', '--alifold-cons']


def sh(cmd, log, cwd=None):
    with open(log, 'w') as fh:
        return subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, cwd=cwd,
                              env={**os.environ, 'PATH': PATHENV, 'CMfinder': str(ENV / 'retron_tradicional')}).returncode


def rscape(sto, outdir, cacofold):
    outdir.mkdir(parents=True, exist_ok=True)
    tag = 'caco' if cacofold else 'rs'
    out = outdir.parent / f'{outdir.name}.{tag}.out'
    if not out.exists():
        sh([str(RSCAPE)] + (['--cacofold'] if cacofold else []) + ['-E', '0.05', '--nofigures', '--outdir', str(outdir),
                                                                 str(sto)], out)
    return out


def summary(spans, n_in, win_from):
    """spans: {member: (a, b)} in 1-based window coords."""
    rel = {m: (win_from + a - 1, win_from + b - 1) for m, (a, b) in spans.items()}
    centres = [(a + b) / 2 for a, b in rel.values()]
    return rel, dict(n_members=n_in, n_with_span=len(rel), coverage=len(rel) / n_in if n_in else 0,
                     centre_sd=float(np.std(centres)) if len(centres) > 1 else np.nan,
                     centre_median=float(np.median(centres)) if centres else np.nan)


def cov_stats(stdout, cov, block):
    hdr, blocks = rscape_blocks(stdout) if os.path.exists(stdout) else ({}, [])
    b = blocks[block] if len(blocks) > block else dict(bpairs=0, expected=0.0, observed=0)
    sig = sig_pairs(cov)
    return dict(avgid=hdr.get('avgid'), nseq_used=hdr.get('nseq_used'), bpairs=b['bpairs'],
                expected_cov=b['expected'], observed_cov=b['observed'], n_sig_pairs=len(sig),
                min_sig_E=min((e for *_, e in sig), default=None), low_power=b['expected'] < 1.0)


def passes(s):
    return (s['coverage'] >= 0.5 and (s['centre_sd'] <= 50 if not np.isnan(s['centre_sd']) else False)
            and s['n_sig_pairs'] >= 2 and not s['low_power'])


def arm_cmf(d, fa, n_in, win_from):
    w = d / 'CMF'
    w.mkdir(exist_ok=True)
    if not (w / 'motifs.txt').exists():
        (w / 'seq.fa').write_text(fa.read_text())
        sh(['cmfinder04.pl', '-motifList', 'motifs.txt', 'seq.fa'], w / 'cmfinder.log', cwd=w)
    rows, member_rows = [], []
    for mf in [l.strip() for l in open(w / 'motifs.txt') if l.strip()]:
        sto = w / mf
        spans, total = {}, 0.0
        for line in open(sto):
            m = re.match(r'#=GS (\S+)\s+DE (\d+)\.\.(\d+)\s+([-\d.]+)', line)
            if m:
                spans[m[1]] = (int(m[2]), int(m[3]))
                total += float(m[4])
        rel, s = summary(spans, n_in, win_from)
        out = rscape(sto, w / f'{mf}.rs', cacofold=False)
        cs = cov_stats(out, one(w / f'{mf}.rs', '*.cov'), 0)
        oc = rscape(sto, w / f'{mf}.caco', cacofold=True)
        cc = cov_stats(oc, one(w / f'{mf}.caco', '*.cacofold.cov'), 1)
        row = dict(arm='CMF', motif=mf, motif_score_sum=total, **s, **cs,
                   caco_n_sig_pairs=cc['n_sig_pairs'], caco_expected=cc['expected_cov'])
        row['passes_1to3'] = passes(row)
        rows.append(row)
        member_rows += [dict(arm='CMF', motif=mf, member_id=k, rel_from=a, rel_to=b) for k, (a, b) in rel.items()]
    if not rows:
        return [dict(arm='CMF', motif=None, n_members=n_in, n_with_span=0, coverage=0, passes_1to3=False,
                     status='NO_MOTIF')], []
    R = pd.DataFrame(rows).sort_values(['motif_score_sum', 'n_with_span'], ascending=False)
    R['is_top'] = [True] + [False] * (len(R) - 1)
    R['status'] = 'OK'
    return R.to_dict('records'), member_rows


def arm_align(d, fa, n_in, win_from, arm):
    w = d / arm
    w.mkdir(exist_ok=True)
    if arm == 'MLOC':
        sto = w / 'mloc/results/result.stk'
        if not sto.exists():
            sh(['mlocarna'] + MLOC_FLAGS + [str(fa), '--outdir', str(w / 'mloc')], w / 'mloc.log')
    else:
        sto = w / 'aln.sto'
        if not sto.exists():
            with open(w / 'aln.afa', 'w') as fh:
                subprocess.run([str(BIN / 'mafft-qinsi'), '--thread', '4', '--quiet', str(fa)], stdout=fh,
                               env={**os.environ, 'PATH': PATHENV})
            with open(sto, 'w') as fh:
                subprocess.run([str(BIN / 'esl-reformat'), '-u', 'stockholm', str(w / 'aln.afa')], stdout=fh)
    if not sto.exists() or sto.stat().st_size == 0:
        return [dict(arm=arm, status='RUN_FAILED', n_members=n_in, passes_1to3=False)], []
    oc = rscape(sto, w / 'caco', cacofold=True)
    cs = cov_stats(oc, one(w / 'caco', '*.cacofold.cov'), 1)
    hel = [x for x in helices(one(w / 'caco', '*.cacofold.helixcov')) if x['nbp_cov'] >= 1]
    seqs, _ = read_sto(sto)
    spans = {}
    if hel:
        lo, hi = min(x['lo'] for x in hel), max(x['hi'] for x in hel)
        for m, aln in seqs.items():
            a, b = project(aln, lo, hi)
            if a is not None:
                spans[m] = (a, b)
    rel, s = summary(spans, n_in, win_from)
    row = dict(arm=arm, motif='covarying-helix union', status='OK', n_supported_helices=len(hel), **s, **cs,
               is_top=True)
    row['passes_1to3'] = passes(row)
    return [row], [dict(arm=arm, motif=row['motif'], member_id=k, rel_from=a, rel_to=b) for k, (a, b) in rel.items()]


def run(args):
    set_id, win_from = args
    d = SETS / set_id
    fa = d / 'input.fa'
    n_in = sum(1 for l in open(fa) if l.startswith('>'))
    rows, members = [], []
    for fn in (lambda: arm_cmf(d, fa, n_in, win_from),
               lambda: arm_align(d, fa, n_in, win_from, 'MLOC'),
               lambda: arm_align(d, fa, n_in, win_from, 'QINSI')):
        try:
            r, m = fn()
        except Exception as e:  # recorded, never silently dropped
            r, m = [dict(arm='?', status=f'RUN_FAILED: {e!r}'[:200], passes_1to3=False)], []
        rows += r
        members += m
    for x in rows + members:
        x['set_id'] = set_id
    return rows, members


if __name__ == '__main__':
    S = pd.read_csv(T / 'Z6_SETS.tsv', sep='\t')
    wf = {'CTRL_DISTAL': -1900}
    jobs = [(s, wf.get(c, -600)) for s, c in zip(S.set_id, S.cohort)]
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 10) as p:
        res = p.map(run, jobs, chunksize=1)
    R = pd.DataFrame([r for rs, _ in res for r in rs])
    Mm = pd.DataFrame([m for _, ms in res for m in ms])
    R.to_csv(SCRATCH / 'z6/z6_set_arm_results.tsv', sep='\t', index=False)
    Mm.to_csv(SCRATCH / 'z6/z6_member_spans.tsv', sep='\t', index=False)
    print(R.groupby('arm').status.value_counts().to_string())
