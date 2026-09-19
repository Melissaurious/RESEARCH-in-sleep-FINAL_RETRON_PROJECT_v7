"""z06 — figures for the Z6 benchmark (+ plotting data under figures/data/)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
T, F = HERE / 'tables', HERE / 'figures'
(F / 'data').mkdir(parents=True, exist_ok=True)
INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
ARMC = {'CMF': '#2a78d6', 'MLOC': '#eb6834', 'QINSI': '#1baf7a'}
ARML = {'CMF': 'CMfinder\n(local motif)', 'MLOC': 'mLocARNA\n+ CaCoFold', 'QINSI': 'MAFFT Q-INS-i\n+ CaCoFold'}
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF,
                     'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6})


def save(fig, name, data):
    data.to_csv(F / 'data' / f'{name}.tsv', sep='\t', index=False)
    fig.savefig(F / f'{name}.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


# 1 · rediscovery of hidden references vs chance, per arm and cohort
S = pd.read_csv(T / 'Z6_REDISCOVERY_SUMMARY.tsv', sep='\t')
fig, axs = plt.subplots(1, 2, figsize=(10, 3.4), sharey=False)
for ax, coh in zip(axs, ['POS_BLIND', 'MIXED']):
    s = S[S.cohort == coh].set_index('arm').reindex(['CMF', 'MLOC', 'QINSI'])
    x = np.arange(3)
    ax.bar(x - 0.2, s.rediscovered, 0.38, color=[ARMC[a] for a in s.index], label='observed (IoU ≥ 0.5)')
    ax.bar(x + 0.2, s.chance_expected_rediscovered, 0.38, color='#c9c8c2', label='expected by chance')
    for i, (o, c) in enumerate(zip(s.rediscovered, s.chance_expected_rediscovered)):
        ax.text(i - 0.2, o + 0.5, f'{int(o)}', ha='center', fontsize=8, color=INK)
        ax.text(i + 0.2, c + 0.5, f'{c:.1f}', ha='center', fontsize=8, color=INK2)
    ax.set_xticks(x, [ARML[a] for a in s.index], fontsize=7.5)
    ax.set_title(f'{coh}: {int(s.matched_members.iloc[0])} hidden matched ncRNAs', loc='left', color=INK)
    ax.grid(axis='x', visible=False)
axs[0].set_ylabel('members rediscovered')
axs[0].legend(frameon=False, fontsize=7.5)
save(fig, 'zfig1_rediscovery_vs_chance', S)

# 2 · set outcome grid
O = pd.read_csv(T / 'Z6_SET_OUTCOMES.tsv', sep='\t')
cats = ['CANDIDATE', 'SIGNAL_FAILS_CONTROL', 'NO_COVARIATION', 'LOW_POWER', 'NOT_LOCALISED', 'RUN_FAILED']
cc = {'CANDIDATE': '#2a78d6', 'SIGNAL_FAILS_CONTROL': '#e34948', 'NO_COVARIATION': '#8fb8ea',
      'LOW_POWER': '#eda100', 'NOT_LOCALISED': '#c9c8c2', 'RUN_FAILED': '#52514e'}
sets = list(O.sort_values(['cohort', 'set_id']).set_id.unique())
fig, ax = plt.subplots(figsize=(5.2, 7.2))
for j, arm in enumerate(['CMF', 'MLOC', 'QINSI']):
    for i, sid in enumerate(sets):
        o = O[(O.set_id == sid) & (O.arm == arm)].outcome.iloc[0]
        ax.add_patch(plt.Rectangle((j, i), 0.94, 0.9, color=cc[o]))
ax.set_xlim(0, 3); ax.set_ylim(len(sets), 0)
ax.set_xticks([0.47, 1.47, 2.47], ['CMF', 'MLOC', 'QINSI'])
ax.set_yticks(np.arange(len(sets)) + 0.45, sets, fontsize=7)
ax.grid(False)
for sp in ax.spines.values():
    sp.set_visible(False)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=cc[c]) for c in cats], labels=cats, fontsize=7,
          frameon=False, loc='upper left', bbox_to_anchor=(1.02, 1))
ax.set_title('Set outcome (top motif / region) after the matched distal control', loc='left', color=INK, fontsize=9)
save(fig, 'zfig2_set_outcomes', O)

# 3 · how often each arm "passes" §8.1–3 on real vs distal-control windows
R = pd.read_csv('/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-spire-ncrna/ARIS_OUTPUT/spire_ncrna_audit/z6/z6_set_arm_results.tsv',
                sep='\t')
R['ctrl'] = R.set_id.str.startswith('CTRL_')
R['pass_top'] = R.passes_1to3.fillna(False).astype(bool) & R.is_top.fillna(True).astype(bool)
g = R.groupby(['arm', 'ctrl', 'set_id']).pass_top.any().reset_index().groupby(['arm', 'ctrl']).pass_top.agg(['sum', 'size']).reset_index()
g['rate'] = g['sum'] / g['size']
fig, ax = plt.subplots(figsize=(5.5, 3))
x = np.arange(3)
for k, (ctrl, lab, col) in enumerate([(False, 'benchmark windows (−600…+100)', None), (True, 'distal control (−1900…−1201)', '#c9c8c2')]):
    s = g[g.ctrl == ctrl].set_index('arm').reindex(['CMF', 'MLOC', 'QINSI'])
    ax.bar(x + (k - 0.5) * 0.38, s.rate, 0.36, color=col or [ARMC[a] for a in s.index], label=lab)
    for i, (n, t) in enumerate(zip(s['sum'], s['size'])):
        ax.text(i + (k - 0.5) * 0.38, s.rate.iloc[i] + 0.02, f'{int(n)}/{int(t)}', ha='center', fontsize=7.5, color=INK2)
ax.set_xticks(x, [ARML[a] for a in ['CMF', 'MLOC', 'QINSI']], fontsize=7.5)
ax.set_ylabel('sets passing §8.1–3 (top motif)')
ax.set_ylim(0, 1)
ax.legend(frameon=False, fontsize=7.5)
ax.grid(axis='x', visible=False)
save(fig, 'zfig3_pass_rate_real_vs_control', g)
print('ok')
