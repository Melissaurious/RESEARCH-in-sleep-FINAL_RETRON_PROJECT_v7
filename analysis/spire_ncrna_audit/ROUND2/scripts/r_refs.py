"""Reference reveal (imported ONLY by r03_dev_calibrate on DEV and r05_heldout_eval on HELDOUT after freeze).

Per member: best registered placement at its locus (T3-like first: canonical, same strand, not downstream,
no CDS between, ≤ 200 bp, E ≤ 1e-5; then lowest E), in RT-relative coordinates, with a topology label.
"""
import duckdb
import numpy as np
import pandas as pd
from common import DERIVED


def member_refs(members: pd.DataFrame) -> pd.DataFrame:
    c = duckdb.connect()
    c.register('m', members[['gid', 'member_id', 'locus_key']])
    r = c.execute(f"""SELECT * EXCLUDE (rn) FROM (
      SELECT m.gid, m.member_id, p.nc_start, p.nc_end, p.rt_start prs, p.rt_end pre, p.rt_strand prt, p.nc_seq_len,
             p.detection_model, p.evalue, p.signed_distance_bp, p.direction, p.overlaps_non_rt_cds, p.same_strand,
             row_number() OVER (PARTITION BY m.gid, m.member_id ORDER BY
                (p.canonical AND p.same_strand AND p.direction <> 'downstream' AND p.n_cds_between = 0
                 AND abs(p.signed_distance_bp) <= 200 AND p.evalue <= 1e-5) DESC, p.evalue) rn
      FROM m JOIN read_parquet('{DERIVED}/rt_ncrna_pairs_v1.parquet') p ON p.locus_key = m.locus_key
      WHERE p.file_label = 'Retron') WHERE rn = 1""").df()
    a = np.where(r.prt == '+', r.nc_start - r.prs, r.pre - r.nc_start)
    b = np.where(r.prt == '+', r.nc_end - r.prs, r.pre - r.nc_end)
    r['ref_from'], r['ref_to'] = np.fmin(a, b), np.fmax(a, b)
    r['ref_len'] = r.ref_to - r.ref_from + 1
    rtlen = r.pre - r.prs
    r['topology'] = np.select(
        [~r.same_strand.astype(bool), r.overlaps_non_rt_cds.astype(bool), r.ref_to < 0,
         (r.ref_from < 0) & (r.ref_to >= 0), (r.ref_from >= 0) & (r.ref_to <= rtlen), r.ref_from > rtlen],
        ['other_uncertain', 'overlapping_adjacent_CDS', 'upstream', 'overlaps_RT_start', 'intragenic_RT', 'downstream'],
        default='other_uncertain')
    return r[['gid', 'member_id', 'ref_from', 'ref_to', 'ref_len', 'detection_model', 'evalue',
              'signed_distance_bp', 'topology']]


def chance_iou50(L, ref_from, ref_to, wfrom, wto):
    """P(IoU ≥ 0.5) for a length-L interval placed uniformly inside [wfrom, wto]."""
    L = int(L)
    st = np.arange(wfrom, max(wfrom, wto - L + 1) + 1)
    en = st + L - 1
    o = (np.minimum(en, ref_to) - np.maximum(st, ref_from) + 1).clip(min=0)
    return float((o / (L + (ref_to - ref_from + 1) - o) >= 0.5).mean())
