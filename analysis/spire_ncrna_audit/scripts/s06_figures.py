"""s06 — figures + their plotting data (figures/*.png, figures/data/*.tsv).

Colours: reference palette slots 1-3 (validated all-pairs) for the three arms; gray for the
positional baseline. Text in ink colours only.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from common import TABLES, FIGS

FD = FIGS / 'data'
FD.mkdir(parents=True, exist_ok=True)
INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
ARMC = {'A_SPIRE': '#2a78d6', 'B_STRUCT_CACOFOLD': '#eb6834', 'B_SEQ_CACOFOLD': '#1baf7a',
        'P0_POSITIONAL_BASELINE': '#8f8e89'}
ARML = {'A_SPIRE': 'A · SPIRE (mLocARNA + R-scape)', 'B_STRUCT_CACOFOLD': 'B-struct · CaCoFold, same alignment',
        'B_SEQ_CACOFOLD': 'B-seq · MAFFT + CaCoFold', 'P0_POSITIONAL_BASELINE': 'P0 · fixed positional baseline'}
ARMS = list(ARMC)
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF,
                     'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6})

E = pd.read_csv(TABLES / 'EVAL_member_level.tsv', sep='\t', low_memory=False)
S = pd.read_csv(TABLES / 'EVAL_set_level.tsv', sep='\t')
POS = E[E.cohort == 'POS']
CATS = ['existing pair rediscovered', 'existing pair predicted with altered boundary',
        'existing pair not rediscovered', 'method abstention', 'system unsuitable for this method']
CATC = ['#2a78d6', '#8fb8ea', '#e34948', '#c9c8c2', '#eda100']


def save(fig, name, data):
    data.to_csv(FD / f'{name}.tsv', sep='\t', index=False)
    fig.savefig(FIGS / f'{name}.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


# 1 · outcome categories per arm × rule (POS)
rows = []
for rule in ['PRIMARY_SPIRE', 'SENS_ANY_COV', 'BASELINE']:
    for arm in ARMS:
        sub = POS[(POS.arm == arm) & (POS.rule == rule)]
        if len(sub):
            vc = sub.category.value_counts()
            rows.append({'rule': rule, 'arm': arm, 'n': len(sub), **{c: int(vc.get(c, 0)) for c in CATS}})
d1 = pd.DataFrame(rows)
fig, ax = plt.subplots(figsize=(8, 3.6))
labels = [f"{ARML[r.arm].split(' ·')[0]} · {r.rule}" for r in d1.itertuples()]
left = np.zeros(len(d1))
for c, col in zip(CATS, CATC):
    frac = d1[c] / d1.n
    ax.barh(range(len(d1)), frac, left=left, color=col, edgecolor=SURF, linewidth=1.5, label=c, height=0.7)
    left += frac
ax.set_yticks(range(len(d1)), labels)
ax.invert_yaxis()
ax.set_xlabel('share of positive-benchmark members (reference ncRNA known, blinded)')
ax.set_xlim(0, 1)
ax.grid(axis='y', visible=False)
ax.legend(ncol=2, fontsize=7.5, frameon=False, loc='upper center', bbox_to_anchor=(0.45, -0.18))
ax.set_title(f'Outcome per arm and rule — {POS.physical_locus_key.nunique()} loci, 27 homolog sets', loc='left', color=INK)
save(fig, 'fig1_outcomes_by_arm', d1)

# 2 · IoU and boundary errors for calls (SENS rule, where calls exist) + baseline
calls = POS[(POS.call == True) & POS.rule.isin(['SENS_ANY_COV', 'BASELINE'])]
d2 = calls[['arm', 'rule', 'IoU', 'err5', 'err3', 'len_err', 'physical_locus_key']]
fig, axs = plt.subplots(1, 3, figsize=(10, 3.2), sharey=True)
for ax, col, lab in zip(axs, ['IoU', 'err5', 'err3'], ['IoU', "5′ error (nt; + = 3′ of reference)", "3′ error (nt)"]):
    for i, arm in enumerate(ARMS):
        v = d2[d2.arm == arm][col].dropna()
        if len(v):
            ax.boxplot(v, positions=[i], vert=False, widths=0.55, showfliers=False,
                       medianprops=dict(color=INK), boxprops=dict(color=ARMC[arm]), whiskerprops=dict(color=ARMC[arm]),
                       capprops=dict(color=ARMC[arm]))
            ax.scatter(v, np.random.default_rng(1).normal(i, 0.07, len(v)), s=8, color=ARMC[arm], alpha=0.5, lw=0)
            ax.text(1.01, i, f'n={len(v)}', transform=ax.get_yaxis_transform(), fontsize=7, color=INK2, va='center')
    ax.set_xlabel(lab)
    if col != 'IoU':
        ax.axvline(0, color=INK2, lw=0.8)
        ax.set_xlim(-350, 350)
        off = int((d2[col].abs() > 350).sum())
        if off:
            ax.text(0.01, -0.28, f'{off} value(s) beyond ±350 nt not shown (reference outside window)',
                    transform=ax.transAxes, fontsize=6.5, color=INK2)
axs[0].set_yticks(range(len(ARMS)), [ARML[a].split(' ·')[0] for a in ARMS])
axs[0].set_title('Calls only (rule SENS_ANY_COV; P0 = baseline)', loc='left', color=INK)
save(fig, 'fig2_iou_boundary_error', d2)

# 3 · success by retron type, length, distance (region level, SENS rule)
sens = POS[POS.rule.isin(['SENS_ANY_COV', 'BASELINE'])].copy()
sens['len_bin'] = pd.cut(sens.ref_len, [0, 100, 150, 200, 1000], labels=['≤100', '101–150', '151–200', '>200'])
sens['dist_bin'] = pd.cut(sens.ref_signed_distance_bp.abs(), [-1, 20, 60, 120, 1e6],
                          labels=['0–20', '21–60', '61–120', '>120'])
fig, axs = plt.subplots(1, 3, figsize=(12, 3.4), sharey=True)
out = []
for ax, key, title in zip(axs, ['type_label', 'len_bin', 'dist_bin'],
                          ['retron type (tool label)', 'reference ncRNA length (nt)', '|RT–ncRNA gap| (bp)']):
    g = sens.groupby([key, 'arm'], observed=True).agg(n=('level_region', 'size'), region=('level_region', 'mean'),
                                                      boundary=('level_boundary', 'mean')).reset_index()
    g['facet'] = key
    out.append(g.rename(columns={key: 'level'}))
    levels = list(g[key].drop_duplicates())
    w = 0.8 / len(ARMS)
    for j, arm in enumerate(ARMS):
        gg = g[g.arm == arm].set_index(key).reindex(levels)
        ax.bar(np.arange(len(levels)) + (j - 1.5) * w, gg.region, width=w * 0.92, color=ARMC[arm],
               label=ARML[arm] if key == 'type_label' else None)
    ns = g.groupby(key, observed=True).n.max().reindex(levels)
    ax.set_xticks(range(len(levels)), [f'{l} (n={n})' for l, n in zip(levels, ns)], fontsize=7,
                  rotation=40, ha='right')
    ax.set_title(title, loc='left', color=INK, fontsize=9)
    ax.grid(axis='x', visible=False)
axs[0].set_ylabel('region hit rate (overlap ≥ 1 nt)')
axs[0].set_ylim(0, 1)
fig.legend(loc='upper center', ncol=4, frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, 1.07))
save(fig, 'fig3_success_by_type_length_distance', pd.concat(out))

# 4 · set-level signal: POS vs pilot vs controls, both rules
order = ['POS', 'POS_S5', 'PIL', 'CTRL_DISTAL', 'CTRL_INTRAGENIC', 'CTRL_NONRETRON', 'CTRL_GII_HARD']
g = (S[S.arm.isin(ARMS[:3])].groupby(['cohort', 'arm'])
       .agg(n_sets=('set_id', 'size'), primary=('signal_primary', 'mean'), sens=('signal_sens', 'mean'),
            low_power=('low_power', 'mean')).reset_index())
g = g[g.cohort.isin(order)]
fig, axs = plt.subplots(1, 2, figsize=(11, 3.4), sharey=True)
for ax, col, title in zip(axs, ['primary', 'sens'], ['SPIRE rule (≥1 cov. pair and obs/exp ≥ 1.1)',
                                                    'sensitivity rule (≥1 covarying pair)']):
    levels = [c for c in order if c in set(g.cohort)]
    w = 0.8 / 3
    for j, arm in enumerate(ARMS[:3]):
        gg = g[g.arm == arm].set_index('cohort').reindex(levels)
        ax.bar(np.arange(len(levels)) + (j - 1) * w, gg[col], width=w * 0.92, color=ARMC[arm],
               label=ARML[arm] if col == 'primary' else None)
    ns = g.groupby('cohort').n_sets.max().reindex(levels)
    SHORT = {'POS': 'POS', 'POS_S5': 'POS seq-only', 'PIL': 'pilot (CM-neg.)', 'CTRL_DISTAL': 'distal',
             'CTRL_INTRAGENIC': 'intragenic', 'CTRL_NONRETRON': 'non-retron RT', 'CTRL_GII_HARD': 'group II intron'}
    ax.set_xticks(range(len(levels)), [f'{SHORT[l]}\n({n} sets)' for l, n in zip(levels, ns)], fontsize=7,
                  rotation=30, ha='right')
    ax.set_title(title, loc='left', color=INK)
    ax.grid(axis='x', visible=False)
axs[0].set_ylabel('share of sets with signal')
axs[0].set_ylim(0, 1)
fig.legend(loc='upper center', ncol=3, frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, 1.07))
save(fig, 'fig4_set_signal_by_cohort', g)

# 5 · R-scape support: expected vs observed covarying pairs per set
d5 = S[S.arm.isin(ARMS[:3])][['cohort', 'set_id', 'arm', 'expected_cov', 'observed_cov', 'avgid', 'n']]
fig, axs = plt.subplots(1, 3, figsize=(12, 3.8), sharex=True, sharey=True)
mk = {'POS': 'o', 'POS_S5': 'v', 'PIL': 'D', 'CTRL_DISTAL': 'x', 'CTRL_INTRAGENIC': 'x',
      'CTRL_NONRETRON': '+', 'CTRL_GII_HARD': 's'}
cc = {'POS': '#2a78d6', 'POS_S5': '#2a78d6', 'PIL': '#1baf7a', 'CTRL_DISTAL': '#8f8e89',
      'CTRL_INTRAGENIC': '#52514e', 'CTRL_NONRETRON': '#eda100', 'CTRL_GII_HARD': '#e34948'}
for ax, arm in zip(axs, ARMS[:3]):
    sub = d5[d5.arm == arm]
    for c in order:
        q = sub[sub.cohort == c]
        if len(q):
            ax.scatter(q.expected_cov + 0.3, q.observed_cov + 0.3, marker=mk[c], s=22, color=cc[c], label=c,
                       lw=1 if mk[c] in 'x+' else 0.4, edgecolor=SURF if mk[c] not in 'x+' else None)
    lim = max(d5.expected_cov.max(), d5.observed_cov.max()) + 5
    ax.plot([0.3, lim], [0.3, lim], color=INK2, lw=0.8)
    ax.plot([0.3, lim], [0.33, 1.1 * lim], color=INK2, lw=0.8, ls=':')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_title(ARML[arm], loc='left', color=INK, fontsize=8.5)
    ax.set_xlabel('expected covarying pairs (power) + 0.3')
axs[0].set_ylabel('observed covarying pairs + 0.3')
axs[0].legend(fontsize=7, frameon=False, loc='upper left')
save(fig, 'fig5_rscape_support', d5)

# 6 · CM-positive vs CM-negative candidate yield (member call rate)
d6 = (E[E.cohort.isin(['POS', 'PIL']) & E.rule.isin(['PRIMARY_SPIRE', 'SENS_ANY_COV'])]
        .assign(group=lambda x: np.where(x.cohort == 'POS', 'POS (CM-positive)', x.stratum))
        .groupby(['group', 'arm', 'rule']).agg(n=('call', 'size'), call_rate=('call', 'mean')).reset_index())
fig, axs = plt.subplots(1, 2, figsize=(11, 3.4), sharey=True)
levels = ['POS (CM-positive)', 'PIL_S12_HOMOLOG_HAS_CM', 'PIL_S12_ORPHAN', 'PIL_S3_FUSED', 'PIL_S5_SEQONLY']
for ax, rule in zip(axs, ['PRIMARY_SPIRE', 'SENS_ANY_COV']):
    w = 0.8 / 3
    for j, arm in enumerate(ARMS[:3]):
        gg = d6[(d6.arm == arm) & (d6.rule == rule)].set_index('group').reindex(levels)
        ax.bar(np.arange(len(levels)) + (j - 1) * w, gg.call_rate, width=w * 0.92, color=ARMC[arm],
               label=ARML[arm] if rule == 'PRIMARY_SPIRE' else None)
    ns = d6[d6.rule == rule].groupby('group').n.max().reindex(levels)
    SH = {'POS (CM-positive)': 'POS, CM-positive', 'PIL_S12_HOMOLOG_HAS_CM': 'pilot S1/S2, homolog has CM',
          'PIL_S12_ORPHAN': 'pilot S1/S2, orphan', 'PIL_S3_FUSED': 'pilot S3 fused-RT', 'PIL_S5_SEQONLY': 'pilot S5 seq-only'}
    ax.set_xticks(range(len(levels)), [f"{SH[l]} (n={n})" for l, n in zip(levels, ns)], fontsize=7,
                  rotation=30, ha='right')
    ax.set_title(rule, loc='left', color=INK)
    ax.grid(axis='x', visible=False)
axs[0].set_ylabel('members with a predicted region')
axs[0].set_ylim(0, 1)
fig.legend(loc='upper center', ncol=3, frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, 1.07))
save(fig, 'fig6_cm_positive_vs_negative_yield', d6)
print('figures written')
