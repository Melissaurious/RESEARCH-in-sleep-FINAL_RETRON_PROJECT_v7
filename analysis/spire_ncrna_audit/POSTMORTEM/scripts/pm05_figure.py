"""pm05 — motif centre (RT-relative) by RT class, passing groups only; data in figures/data/."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np, pandas as pd
from pathlib import Path
H = Path(__file__).resolve().parents[1]
I = pd.read_csv(H / 'tables/MOTIF_INSTANCES.tsv', sep='\t')
S = pd.read_csv(H / 'tables/SPECIFICITY_BY_CLASS.tsv', sep='\t').set_index('rt_class')
order = ['Retron'] + [c for c in S.sort_values('real_rate', ascending=False).index if c != 'Retron']
(H / 'figures/data').mkdir(parents=True, exist_ok=True)
I[['rt_class', 'gid', 'member_id', 'centre', 'rel_from', 'rel_to']].to_csv(H / 'figures/data/pmfig1_motif_centres.tsv', sep='\t', index=False)
fig, ax = plt.subplots(figsize=(8, 4.2), facecolor='#fcfcfb'); ax.set_facecolor('#fcfcfb')
ax.axvspan(-193, -24, color='#e4e3df', zorder=0, label='positional prior −193…−24')
ax.axvline(0, color='#52514e', lw=0.8); ax.text(2, len(order) - 0.4, 'RT start', fontsize=7, color='#52514e')
ax.axvspan(-20, -1, color='#eda100', alpha=.25, zorder=0, label='RBS region −20…−1')
rng = np.random.default_rng(1)
for i, c in enumerate(order):
    v = I[I.rt_class == c].centre
    ax.scatter(v, i + rng.normal(0, .08, len(v)), s=6, color='#2a78d6' if c == 'Retron' else '#8f8e89', alpha=.5, lw=0)
    ax.text(105, i, f"{int(S.loc[c,'real_pass'])}/{int(S.loc[c,'groups'])} groups pass", fontsize=7, va='center', color='#52514e')
ax.set_yticks(range(len(order)), order, fontsize=8); ax.invert_yaxis(); ax.set_xlim(-400, 100)
ax.set_xlabel('motif-instance centre, nt relative to RT start (window −400…+100)')
ax.set_title('Where the frozen CMfinder rule finds its motif, by RT class', loc='left', fontsize=9)
for s in ['top', 'right']: ax.spines[s].set_visible(False)
ax.legend(fontsize=7, frameon=False, loc='lower left')
fig.savefig(H / 'figures/pmfig1_motif_centre_by_class.png', dpi=200, bbox_inches='tight')
