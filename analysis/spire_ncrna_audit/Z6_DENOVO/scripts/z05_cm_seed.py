"""z05 — CM-seeding test for candidates (DESIGN §9, last paragraph). Experimental CMs only; they
live in ARIS_OUTPUT/.../z6/seed/ and are never merged with, or written next to, production CMs.

For each (set, arm) with outcome CANDIDATE in a DENOVO or MIXED cohort:
  alignment = CMF top motif .sto, or the CaCoFold .sto sliced to the supported region (MLOC/QINSI);
  cmbuild → cmcalibrate (--cpu 8) → cmsearch -T 20 --nohmmonly on W and distal windows of up to 40
  held-out loci of the same RT50 group (one per RT90, not in any set, same locus class family).
Reports: held-out hit rate in W vs distal; share of W hits whose centre is within ±50 nt of the set median.
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from common import SCRATCH, ENV  # noqa: E402
from windows import window  # noqa: E402
from s04_run_sets import read_sto, one  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
T = HERE / 'tables'
BIN = ENV / 'retron_tradicional/bin'
SEED = SCRATCH / 'z6/seed'
W, DIST = (-600, 100), (-1900, -1201)
PAIRED = set('<>()[]{}')


def slice_sto(src, lo, hi, dst):
    seqs, ss = read_sto(src)
    ss = ss[lo - 1:hi]
    stack, keep = [], ['.'] * len(ss)
    pairs = {'<': '>', '(': ')', '[': ']', '{': '}'}
    for i, ch in enumerate(ss):
        if ch in pairs:
            stack.append((i, pairs[ch]))
        elif ch in pairs.values():
            if stack and stack[-1][1] == ch:
                j, _ = stack.pop()
                keep[j], keep[i] = '<', '>'
    with open(dst, 'w') as fh:
        fh.write('# STOCKHOLM 1.0\n\n')
        for k, v in seqs.items():
            fh.write(f'{k} {v[lo - 1:hi]}\n')
        fh.write(f"#=GC SS_cons {''.join(keep)}\n//\n")


O = pd.read_csv(T / 'Z6_SET_OUTCOMES.tsv', sep='\t')
cand = O[(O.outcome == 'CANDIDATE') & O.cohort.isin(['DENOVO_S12', 'DENOVO_S3', 'MIXED'])]
if cand.empty:
    pd.DataFrame(columns=['set_id', 'arm', 'note']).to_csv(T / 'Z6_CM_SEED.tsv', sep='\t', index=False)
    sys.exit('no CANDIDATE sets in DENOVO/MIXED cohorts — nothing to seed')

L = pd.read_parquet(SCRATCH / 'z6/z6_loci.parquet')
MEM = pd.read_csv(T / 'Z6_SET_MEMBERS.tsv', sep='\t')
used = set(MEM.locus_key)
SEED.mkdir(parents=True, exist_ok=True)
rows = []
for c in cand.itertuples():
    d = SCRATCH / 'z6/sets' / c.set_id
    w = SEED / f'{c.set_id}__{c.arm}'
    w.mkdir(exist_ok=True)
    if c.arm == 'CMF':
        sto = d / 'CMF' / c.motif
    else:
        res = pd.read_csv(SCRATCH / 'z6/z6_set_arm_results.tsv', sep='\t')
        src = Path(one(d / c.arm / 'caco', '*.cacofold.sto'))
        hel = open(one(d / c.arm / 'caco', '*.cacofold.helixcov')).read()
        rms = [(int(a), int(b)) for a, _, _, b, _, cov in
               re.findall(r'# RM (\d+)-(\d+) (\d+)-(\d+), nbp = (\d+) nbp_cov = (\d+)', hel) if int(cov) >= 1]
        lo, hi = min(x[0] for x in rms), max(x[1] for x in rms)
        sto = w / 'region.sto'
        slice_sto(src, lo, hi, sto)
    cm = w / 'seed.cm'
    subprocess.run([str(BIN / 'cmbuild'), '-F', str(cm), str(sto)], capture_output=True, check=True)
    subprocess.run([str(BIN / 'cmcalibrate'), '--cpu', '8', str(cm)], capture_output=True, check=True)
    # held-out loci of the same group, same cohort class, one per RT90, not in any set
    cls = 'UNMATCHED_ADEQUATE'
    pool = L[(L.rt50 == MEM[MEM.set_id == c.set_id].rt50.iloc[0]) & ~L.locus_key.isin(used)
             & L.locus_class.isin([cls, 'MATCHED_LOCAL_ADEQUATE'])]
    pool = pool.assign(o=pool.locus_key.map(lambda k: hashlib.sha256(('z6-seed|' + k).encode()).hexdigest()))
    pool = pool.sort_values('o').drop_duplicates('rt90').head(40)
    fw, fd = open(w / 'heldout_W.fa', 'w'), open(w / 'heldout_distal.fa', 'w')
    n_w = n_d = 0
    for r in pool.itertuples():
        s = window(r._asdict(), *W)
        q = window(r._asdict(), *DIST)
        if s:
            fw.write(f'>{r.locus_key}|{r.locus_class}\n{s}\n'); n_w += 1
        if q:
            fd.write(f'>{r.locus_key}|{r.locus_class}\n{q}\n'); n_d += 1
    fw.close(); fd.close()
    res_hits = {}
    for tag, fa, off in [('W', w / 'heldout_W.fa', W[0]), ('DIST', w / 'heldout_distal.fa', DIST[0])]:
        tbl = w / f'{tag}.tbl'
        subprocess.run([str(BIN / 'cmsearch'), '--nohmmonly', '-T', '20', '--toponly', '--tblout', str(tbl),
                        '-o', '/dev/null', str(cm), str(fa)], check=True)
        hits = {}
        for line in open(tbl):
            if line.startswith('#'):
                continue
            p = line.split()
            a, b = int(p[7]), int(p[8])
            hits.setdefault(p[0], (off + (a + b) / 2 - 1, float(p[14])))
        res_hits[tag] = hits
    med = c.centre_median
    wh = res_hits['W']
    rows.append(dict(set_id=c.set_id, arm=c.arm, cohort=c.cohort, heldout_W=n_w, heldout_distal=n_d,
                     hits_W=len(wh), hits_distal=len(res_hits['DIST']),
                     hit_rate_W=len(wh) / n_w if n_w else np.nan,
                     hit_rate_distal=len(res_hits['DIST']) / n_d if n_d else np.nan,
                     W_hits_within_50nt_of_set_median=sum(abs(x - med) <= 50 for x, _ in wh.values()),
                     heldout_matched_hit=sum('MATCHED' in k for k in wh),
                     heldout_unmatched_hit=sum('UNMATCHED' in k for k in wh),
                     note='experimental CM; not a production model'))
pd.DataFrame(rows).to_csv(T / 'Z6_CM_SEED.tsv', sep='\t', index=False)
print(pd.DataFrame(rows).to_string())
