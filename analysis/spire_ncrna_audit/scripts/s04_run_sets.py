"""s04 — run arms A / B-struct / B-seq on frozen sets and write BLIND predictions.

Arm A      : SPIRE 07_run_mlocarna_rscape.sh VERBATIM (unmodified file from the ZIP), with
             two PATH shims only: `rscape` -> bioconda `R-scape`, `python3` -> an env with numpy.
Arm B-struct: R-scape --cacofold on Arm A's mLocARNA alignment.
Arm B-seq  : MAFFT L-INS-i alignment -> R-scape --cacofold.
Parsing follows BENCHMARK_DESIGN.md §8. Reads no reference-ncRNA information.

usage: python s04_run_sets.py <cohort-regex> [workers]
"""
import os
import re
import subprocess
import sys
from multiprocessing import Pool
import pandas as pd
from common import SCRATCH, TABLES, ENV, MAFFT, RSCAPE

ZIP07 = SCRATCH / 'unpacked/spire_pipeline_scripts/07_run_mlocarna_rscape.sh'
SHIM = SCRATCH / 'smoke/shim'
ESL = ENV / 'retron_tradicional/bin/esl-reformat'
PATHENV = f"{SHIM}:{ENV}/locarna_test/bin:{ENV}/retron_tradicional/bin:{os.environ['PATH']}"
PAIRED = set('<>()[]{}') | set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')


def sh(cmd, log, cwd=None):
    with open(log, 'w') as fh:
        return subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, cwd=cwd,
                              env={**os.environ, 'PATH': PATHENV}).returncode


def read_sto(path):
    seqs, ss = {}, ''
    for line in open(path):
        if line.startswith('#=GC SS_cons'):
            ss += line.split()[-1]
        elif line.strip() and not line.startswith('#') and not line.startswith('//'):
            p = line.split()
            if len(p) == 2:
                seqs[p[0]] = seqs.get(p[0], '') + p[1]
    return seqs, ss


def rscape_blocks(stdout_path):
    """Per structure block in R-scape stdout: BPAIRS, expected, observed; plus header stats."""
    txt = open(stdout_path).read()
    msa = re.search(r'# MSA \S+ nseq (\d+) \((\d+)\) alen (\d+) \((\d+)\) avgid ([\d.]+)', txt)
    blocks = []
    for m in re.finditer(r'# BPAIRS (\d+)\n# avg substitutions per BP\s+([\d.]+)\n'
                         r'# BPAIRS expected to covary ([\d.]+) \+/- ([\d.]+)\n'
                         r'# BPAIRS observed to covary (\d+)', txt):
        blocks.append(dict(bpairs=int(m[1]), avg_subs=float(m[2]), expected=float(m[3]),
                           observed=int(m[5])))
    hdr = dict(nseq_used=int(msa[1]), alen_used=int(msa[3]), alen_input=int(msa[4]),
               avgid=float(msa[5])) if msa else {}
    return hdr, blocks


def sig_pairs(cov_path):
    out = []
    if not os.path.exists(cov_path):
        return out
    for line in open(cov_path):
        if line.startswith('#') or not line.strip():
            continue
        p = line.split()
        nums = [x for x in p if re.fullmatch(r'-?[\d.]+(e-?\d+)?', x)]
        # layout: [markers...] left right score E pvalue subs power
        if len(nums) < 7:
            continue          # e.g. the literal line "no significant pairs"
        left, right, e = int(nums[0]), int(nums[1]), float(nums[3])
        if e < 0.05:
            out.append((left, right, e))
    return out


def helices(helixcov_path):
    out = []
    if not os.path.exists(helixcov_path):
        return out
    for m in re.finditer(r'# RM (\d+)-(\d+) (\d+)-(\d+), nbp = (\d+) nbp_cov = (\d+)',
                         open(helixcov_path).read()):
        out.append(dict(lo=int(m[1]), hi=int(m[4]), nbp=int(m[5]), nbp_cov=int(m[6])))
    return out


def project(aln, lo, hi):
    """Ungapped 1-based window positions of a member inside alignment columns [lo, hi]."""
    k, pos = 0, []
    for col, ch in enumerate(aln, start=1):
        if ch not in '-.~':
            k += 1
            if lo <= col <= hi:
                pos.append(k)
    return (min(pos), max(pos)) if pos else (None, None)


def summarise(set_dir, arm, sto, stdout, cov, helixcov, block_idx, win_from, verbatim_log=None):
    rows = []
    if not os.path.exists(sto) or not os.path.exists(stdout):
        return [dict(arm=arm, status='RUN_FAILED')]
    seqs, ss = read_sto(sto)
    hdr, blocks = rscape_blocks(stdout)
    blk = blocks[block_idx] if len(blocks) > block_idx else dict(bpairs=0, expected=0.0, observed=0)
    sig = sig_pairs(cov)
    hel = helices(helixcov)
    sup = [x for x in hel if x['nbp_cov'] >= 1]
    ratio = blk['observed'] / blk['expected'] if blk['expected'] > 0 else (float('inf') if blk['observed'] else 0.0)
    signal = len(sig) >= 1 and ratio >= 1.1
    lo = min((x['lo'] for x in sup), default=None)
    hi = max((x['hi'] for x in sup), default=None)
    pc = [i for i, ch in enumerate(ss, start=1) if ch in PAIRED]
    slo, shi = (min(pc), max(pc)) if pc else (None, None)
    verb = None
    if verbatim_log and os.path.exists(verbatim_log):
        m = re.search(r'Significantly covarying BPs \(E<0.05\): (\d+)', open(verbatim_log).read())
        verb = int(m[1]) if m else None
    base = dict(arm=arm, status='OK', nseq_input=len(seqs), **hdr, ss_bpairs=blk['bpairs'],
                expected_cov=blk['expected'], observed_cov=blk['observed'], obs_exp_ratio=ratio,
                n_sig_pairs=len(sig), min_sig_E=min((e for *_, e in sig), default=None),
                n_helices=len(hel), n_supported_helices=len(sup),
                set_signal=signal, low_power=blk['expected'] < 1.0,
                region_col_lo=lo, region_col_hi=hi, struct_col_lo=slo, struct_col_hi=shi,
                verbatim_spire_parse_n_sig=verb)
    for mid, aln in sorted(seqs.items()):
        r = dict(base, member_id=mid)
        a, b = project(aln, lo, hi) if (signal and lo) else (None, None)
        sa, sb = project(aln, slo, shi) if slo else (None, None)
        xa, xb = project(aln, lo, hi) if (len(sig) >= 1 and lo) else (None, None)
        r.update(pred_rel_from=None if a is None else win_from + a - 1,
                 pred_rel_to=None if b is None else win_from + b - 1,
                 struct_rel_from=None if sa is None else win_from + sa - 1,
                 struct_rel_to=None if sb is None else win_from + sb - 1,
                 sens_rel_from=None if xa is None else win_from + xa - 1,
                 sens_rel_to=None if xb is None else win_from + xb - 1,
                 sens_member_call=xa is not None,
                 member_call=a is not None,
                 abstain_reason=None if a is not None else
                 ('NO_SET_SIGNAL' if not signal else 'MEMBER_NOT_IN_SUPPORTED_REGION'))
        rows.append(r)
    return rows


def one(d, pattern):
    hits = sorted(d.glob(pattern)) if d.exists() else []
    hits = [h for h in hits if '.sorted.' not in h.name and ('cacofold' in pattern or 'cacofold' not in h.name)]
    return str(hits[0]) if hits else str(d / ('MISSING_' + pattern.replace('*', '')))


def run_one(args):
    set_id, win_from = args
    d = SCRATCH / 'sets' / set_id
    fa = d / 'input.fa'
    rows = []
    # ---- Arm A: verbatim SPIRE 07
    if not (d / 'A/rscape').exists():
        sh(['bash', str(ZIP07), str(fa), str(d / 'A'), set_id, '4'], d / 'A.verbatim.log')
    stk = d / 'A/mlocarna/results/result.stk'
    # R-scape stdout for arm A is inside the verbatim log; re-run it quietly to a clean file
    if stk.exists() and not (d / 'A_rscape.out').exists():
        (d / 'A_rs').mkdir(exist_ok=True)
        sh([str(RSCAPE), '-E', '0.05', '--nofigures', '--outdir', str(d / 'A_rs'), str(stk)], d / 'A_rscape.out')
    rows += summarise(d, 'A_SPIRE', stk, d / 'A_rscape.out', one(d / 'A_rs', '*_1.cov'),
                      one(d / 'A_rs', '*_1.helixcov'), 0, win_from, verbatim_log=d / 'A.verbatim.log')
    # ---- Arm B-struct: CaCoFold on the same mLocARNA alignment
    if stk.exists() and not (d / 'Bstruct.out').exists():
        (d / 'Bstruct').mkdir(exist_ok=True)
        sh([str(RSCAPE), '--cacofold', '-E', '0.05', '--nofigures', '--outdir', str(d / 'Bstruct'), str(stk)],
           d / 'Bstruct.out')
    rows += summarise(d, 'B_STRUCT_CACOFOLD', one(d / 'Bstruct', '*.cacofold.sto'), d / 'Bstruct.out',
                      one(d / 'Bstruct', '*.cacofold.cov'), one(d / 'Bstruct', '*.cacofold.helixcov'), 1, win_from)
    # ---- Arm B-seq: MAFFT L-INS-i -> CaCoFold
    (d / 'Bseq').mkdir(exist_ok=True)
    afa, sto = d / 'Bseq/aln.afa', d / 'Bseq/aln.sto'
    if not sto.exists():
        with open(afa, 'w') as fh:
            subprocess.run([str(MAFFT), '--localpair', '--maxiterate', '1000', '--thread', '4', '--quiet',
                            str(fa)], stdout=fh, check=True)
        with open(sto, 'w') as fh:
            subprocess.run([str(ESL), '-u', 'stockholm', str(afa)], stdout=fh, check=True)
    if not (d / 'Bseq.out').exists():
        (d / 'Bseq/rs').mkdir(exist_ok=True)
        sh([str(RSCAPE), '--cacofold', '-E', '0.05', '--nofigures', '--outdir', str(d / 'Bseq/rs'), str(sto)],
           d / 'Bseq.out')
    rows += summarise(d, 'B_SEQ_CACOFOLD', one(d / 'Bseq/rs', '*.cacofold.sto'), d / 'Bseq.out',
                      one(d / 'Bseq/rs', '*.cacofold.cov'), one(d / 'Bseq/rs', '*.cacofold.helixcov'), 1, win_from)
    for r in rows:
        r['set_id'] = set_id
    return rows


if __name__ == '__main__':
    pat = re.compile(sys.argv[1])
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    S = pd.read_csv(TABLES / 'SETS.tsv', sep='\t')
    if (TABLES / 'SETS_AMEND2.tsv').exists():
        S = pd.concat([S, pd.read_csv(TABLES / 'SETS_AMEND2.tsv', sep='\t')], ignore_index=True)
    S = S[S.cohort.str.fullmatch(pat)]
    with Pool(workers) as p:
        res = p.map(run_one, list(zip(S.set_id, S.win_from)), chunksize=1)
    out = pd.DataFrame([r for rs in res for r in rs])
    tag = re.sub(r'\W+', '_', sys.argv[1]).strip('_')
    path = SCRATCH / f'predictions_{tag}.tsv'
    out.to_csv(path, sep='\t', index=False)
    print(f'{len(S)} sets, {len(out)} rows -> {path}')
    print(out.groupby('arm').status.value_counts().to_string())
