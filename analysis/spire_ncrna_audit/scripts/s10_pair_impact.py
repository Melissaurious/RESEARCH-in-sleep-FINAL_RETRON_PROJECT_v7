"""s10 — pair-population impact: components, not raw pairs. CALCULATED, NOT EXPLOITED.

Candidate classes (never merged):
  CM_WINDOW_RESCUE   pilot member with a + strand padlocdb.cm hit, E <= 1e-5, on the 300-nt
                     window (annotation-independent rescan; NOT de novo).
  DENOVO_WEAK        pilot de novo call (any arm, either rule) with covariation >= power,
                     cross-arm agreement, <50 % CDS overlap, and no strong CM hit.
Rules for DENOVO_WEAK are declared post hoc in BENCHMARK_RESULTS.md; nothing here is validated.
RT-relatedness component = RT50 cluster; ncRNA-relatedness component = blastn (E <= 1e-5)
connected component over existing oriented ncRNAs + candidate sequences.
"""
import subprocess
import duckdb
import networkx as nx
import numpy as np
import pandas as pd
from common import SCRATCH, TABLES, AUDIT, DERIVED, ENV

C = pd.read_csv(AUDIT / 'CANDIDATE_EVIDENCE.tsv', sep='\t')
CM = pd.read_csv(SCRATCH / 'pilot_cm/cm_hits.tsv', sep='\t')
mem = pd.read_csv(TABLES / 'SET_MEMBERS.tsv', sep='\t')
pm = mem[mem.cohort == 'PIL']
seqs = {}
for sid in pm.set_id.unique():
    name = None
    for line in open(SCRATCH / 'sets' / sid / 'input.fa'):
        name, seqs[(sid, name)] = (line[1:].strip(), None) if line.startswith('>') else (name, line.strip())

strong = (CM[(CM.cm_strand == '+') & (CM.cm_E <= 1e-5)].sort_values('cm_E')
            .groupby(['set_id', 'member_id']).head(1).merge(pm, on=['set_id', 'member_id']))
strong['cls'] = 'CM_WINDOW_RESCUE'
strong['f'], strong['t'] = strong.cm_rel_from, strong.cm_rel_to
strong['model'] = strong.cm_model
C['cm_strong'] = (C.cm_sub_hit_E <= 1e-5) & (C.cm_sub_hit_overlap_nt > 0)
dn = C[~C.cm_strong & C.independent_support.str.contains('covariation at/above power')
       & C.independent_support.str.contains('cross-arm') & (C.cds_overlap_frac < 0.5)]
dn = (dn.sort_values(['arm', 'rule']).groupby(['set_id', 'member_id']).head(1)
        .merge(pm[['set_id', 'member_id', 'rt50', 'rt90']], on=['set_id', 'member_id']))
dn['cls'], dn['f'], dn['t'], dn['model'] = 'DENOVO_WEAK', dn.cand_rel_from, dn.cand_rel_to, 'none'
cand = pd.concat([strong[['cls', 'set_id', 'member_id', 'physical_locus_key', 'rt_seq_hash', 'rt50', 'type_label',
                          'f', 't', 'model']],
                  dn[['cls', 'set_id', 'member_id', 'physical_locus_key', 'rt_seq_hash', 'rt50', 'type_label',
                      'f', 't', 'model']]], ignore_index=True)
cand['seq'] = [seqs[(r.set_id, r.member_id)][int(r.f) + 300: int(r.t) + 301] for r in cand.itertuples()]
cand['cid'] = [f'{r.cls}|{r.set_id}|{r.member_id}' for r in cand.itertuples()]

# ---- ncRNA-relatedness: candidates vs existing oriented ncRNAs ----------------------------------
d = SCRATCH / 'impact'
d.mkdir(exist_ok=True)
with open(d / 'cand.fa', 'w') as fh:
    fh.write(''.join(f'>{r.cid}\n{r.seq}\n' for r in cand.itertuples()))
blast = ENV / 'retron_tradicional/bin/blastn'
subprocess.run([str(blast), '-query', str(d / 'cand.fa'), '-db', str(SCRATCH / 'pubval/oriented'), '-evalue', '1e-5',
                '-outfmt', '6 qseqid sseqid pident length evalue', '-max_target_seqs', '1000', '-out',
                str(d / 'cand_vs_existing.tsv')], check=True)
subprocess.run([str(blast), '-query', str(d / 'cand.fa'), '-subject', str(d / 'cand.fa'), '-evalue', '1e-5',
                '-outfmt', '6 qseqid sseqid pident length evalue', '-out', str(d / 'cand_vs_cand.tsv')], check=True)
bx = pd.read_csv(d / 'cand_vs_existing.tsv', sep='\t', header=None, names=['q', 's', 'pid', 'len', 'e'])
bc = pd.read_csv(d / 'cand_vs_cand.tsv', sep='\t', header=None, names=['q', 's', 'pid', 'len', 'e'])
cand['matches_existing_ncrna'] = cand.cid.isin(set(bx.q))

# existing ncRNA components among existing sequences touched: approximate = existing hits group
M = duckdb.sql(f"""SELECT physical_locus_key, rt_seq_hash, type_label, nc_status, ref_detection_model
                   FROM read_parquet('{SCRATCH}/master/master_rt_system.parquet')""").df()
rt50 = {l.split('\t')[1].strip(): l.split('\t')[0] for l in open(SCRATCH / 's02/RT50_cluster.tsv')}
M['rt50'] = M.rt_seq_hash.map(rt50)
A3 = M[M.nc_status == 'A_T3']
A_rt50 = set(M[M.nc_status.isin(['A_T3', 'A_T2'])].rt50)
existing_rt_hash = set(M[M.nc_status.str.startswith('A_')].rt_seq_hash)

rows = []
for cls, g in cand.groupby('cls'):
    G = nx.Graph()
    G.add_nodes_from(g.cid)
    G.add_edges_from((a, b) for a, b in zip(bc.q, bc.s) if a in G and b in G)
    novel_nc = g[~g.matches_existing_ncrna]
    Gn = G.subgraph(novel_nc.cid)
    types = sorted(set(g.type_label))
    new_rt50 = set(g.rt50) - A_rt50
    neff_rows = []
    for t in types:
        before = A3[A3.type_label == t].rt50.nunique()
        after = len(set(A3[A3.type_label == t].rt50) | set(g[g.type_label == t].rt50))
        neff_rows.append(f'{t}:{before}->{after}')
    rows.append(dict(
        candidate_class=cls, scope='pilot (219 CM-negative members, 20 sets)', n_candidate_members=len(g),
        n_newly_paired_loci=g.physical_locus_key.nunique(),
        n_newly_paired_exact_RTs=g.rt_seq_hash.nunique(),
        n_exact_RTs_already_paired_elsewhere=len(set(g.rt_seq_hash) & existing_rt_hash),
        n_unique_ncRNA_seqs=g.seq.nunique(),
        n_retron_types=len(types), retron_types=';'.join(types),
        cm_models=';'.join(sorted(set(g.model))),
        n_rt_components_touched=g.rt50.nunique(),
        n_NEW_rt_components=len(new_rt50),
        n_candidates_matching_existing_ncRNA=int(g.matches_existing_ncrna.sum()),
        n_NEW_ncRNA_components=nx.number_connected_components(Gn) if len(novel_nc) else 0,
        within_type_rt_components_A_T3_before_to_after=' '.join(neff_rows),
        gains_TypeIIIA3_or_TypeIB1=bool(set(g.model) & {'TypeIIIA3', 'TypeIB1'}),
        infeasible_types_touched=';'.join(sorted(set(types) & {'VI', 'VII-A1', 'VII-A2', 'VIII', 'X', 'XI', 'XII'})),
        exploited='NO — calculated only'))

# ---- reference: current independent components for the two named models --------------------
for mdl in ['TypeIIIA3', 'TypeIB1']:
    sub = A3[A3.ref_detection_model == mdl]
    rows.append(dict(candidate_class=f'REFERENCE_current_{mdl}', scope='A_T3 loci, whole population',
                     n_newly_paired_loci=len(sub), n_newly_paired_exact_RTs=sub.rt_seq_hash.nunique(),
                     n_rt_components_touched=sub.rt50.nunique(), exploited='reference only'))

# ---- scale-up ceiling: B loci whose RT50 component has no CM-positive member --------------------
B = duckdb.sql(f"""SELECT rt_seq_hash, evidence_stratum, suitability FROM read_parquet('{SCRATCH}/master/master_rt_system.parquet')
                   WHERE nc_status = 'B_NO_CM_CALL' AND suitability = 'OK'""").df()
B['rt50'] = B.rt_seq_hash.map(rt50)
for st in ['S1_SYSTEM_CONTEXT_2TOOLS', 'S2_SYSTEM_CONTEXT_1TOOL', 'S3_FUSED_RT_RULE_ONLY', 'S5_SEQUENCE_ONLY']:
    b = B[B.evidence_stratum == st]
    rows.append(dict(candidate_class=f'CEILING_B_{st}', scope='all suitable B loci (upper bound if every one yielded)',
                     n_newly_paired_loci=len(b), n_newly_paired_exact_RTs=b.rt_seq_hash.nunique(),
                     n_rt_components_touched=b.rt50.nunique(), n_NEW_rt_components=len(set(b.rt50) - A_rt50),
                     exploited='NO — ceiling only'))
out = pd.DataFrame(rows)
out.to_csv(AUDIT / 'PAIR_POPULATION_IMPACT.tsv', sep='\t', index=False)
cand.drop(columns=['seq']).to_csv(TABLES / 'IMPACT_candidates.tsv', sep='\t', index=False)
print(out.T.to_string())
