"""Read RT-oriented genomic windows straight from the pinned raw corpus (byte-offset seek).

Coordinates: contig, 1-based inclusive; full_sequence[0] == actual_window.start
(verified on 59/59 random canonical placements: ncRNA and translated RT slices match).

RT-relative frame used everywhere in this audit:
  position p = distance from the RT start codon along the RT strand; the first nucleotide of
  the start codon is p = 0, the nucleotide immediately 5' of it is p = -1.
"""
import json
from functools import lru_cache
from common import RAW

_COMP = str.maketrans('ACGTNRYKMSWBDHVacgtnrykmswbdhv', 'TGCANYRMKSWVHDBtgcanyrmkswvhdb')


def revcomp(s):
    return s.translate(_COMP)[::-1]


@lru_cache(maxsize=4096)
def _record(source_file, byte_offset, byte_len):
    with open(RAW / source_file, 'rb') as fh:
        fh.seek(byte_offset)
        return json.loads(fh.read(byte_len))


def rt_relative_to_contig(rt_start, rt_end, rt_strand, p):
    """Contig coordinate of RT-relative position p."""
    return rt_start + p if rt_strand == '+' else rt_end - p


def contig_to_rt_relative(rt_start, rt_end, rt_strand, x):
    return x - rt_start if rt_strand == '+' else rt_end - x


def window(row, p_from, p_to):
    """RT-oriented sequence for RT-relative interval [p_from, p_to] (inclusive), or None if
    any part falls outside the record's stored window."""
    rec = _record(row['source_file'], int(row['byte_offset']), int(row['byte_len']))
    gc = rec['genomic_context']
    full, w0 = gc['full_sequence'], gc['actual_window']['start']
    a = rt_relative_to_contig(row['rt_start'], row['rt_end'], row['rt_strand'], p_from)
    b = rt_relative_to_contig(row['rt_start'], row['rt_end'], row['rt_strand'], p_to)
    lo, hi = min(a, b), max(a, b)
    if lo < w0 or hi - w0 + 1 > len(full):
        return None
    s = full[lo - w0: hi - w0 + 1].upper()
    return s if row['rt_strand'] == '+' else revcomp(s)
