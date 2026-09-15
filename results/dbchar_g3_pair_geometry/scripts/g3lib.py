#!/usr/bin/env python3
"""g3lib - RT<->ncRNA geometry definitions.

Every convention that decides a number is declared here, before any data is read, because the
prior project's geometry carried two silent defects this file fixes by definition:

  * its `gap` was a coordinate difference, so abutting features read 1 and consumers binning at
    "<=100 bp" inherited an off-by-one. Here `gap_bp` is the NUMBER OF BASES STRICTLY BETWEEN
    the two intervals: abutting = 0, overlapping = 0 (with the overlap reported separately).
  * "upstream" was transcription-relative but the shipped distance columns were measured from
    the ncRNA start in contig frame. Here direction and signed distance are both
    transcription-relative to the RT strand, and the contig-frame values are kept beside them.

Nothing here filters: a pair that cannot support geometry gets `geometry_eligible = False` and a
reason, and stays in the table.
"""
from __future__ import annotations

# --- DECLARED before any data is read ------------------------------------------------
DIRECTION = ("upstream", "downstream", "overlapping", "undetermined")
# Distance bins, symmetric, edge-to-edge bases strictly between the two features.
DIST_BINS = (0, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000)
CDS_BINS = (0, 1, 2, 3, 5, 10, 20, 50)
# The canonical/high-confidence population: declared BEFORE the distributions are computed.
CANONICAL_RULE = ("record geometry-eligible (RT coordinates back-translation-verified and the "
                  "window self-consistent); the ncRNA interval wholly inside the window; ncRNA "
                  "strand present; the ncRNA not touching a window edge; and the call not a "
                  "duplicate of another call at the same locus")
# An Infernal `!` inclusion at the pipeline's own default is the corpus's own threshold; g3 does
# not re-threshold. E-value is carried and reported, never used to drop a call.
MULTIPLICITY_CLASS = ("single_call", "duplicate_call_same_sequence_and_coordinates",
                      "duplicate_call_same_sequence_other_coordinates", "distinct_sequences")


def overlap_len(a0: int, a1: int, b0: int, b1: int) -> int:
    """Bases shared by two closed intervals; 0 when they do not overlap."""
    return max(0, min(a1, b1) - max(a0, b0) + 1)


def gap_bp(rt0: int, rt1: int, nc0: int, nc1: int) -> int:
    """Bases strictly between two closed intervals. Abutting or overlapping -> 0."""
    if nc1 < rt0:
        return rt0 - nc1 - 1
    if rt1 < nc0:
        return nc0 - rt1 - 1
    return 0


def direction(rt0: int, rt1: int, rt_strand: str, nc0: int, nc1: int) -> str:
    """Transcription-relative placement of the ncRNA with respect to the RT gene."""
    if overlap_len(rt0, rt1, nc0, nc1) > 0:
        return "overlapping"
    if rt_strand not in ("+", "-"):
        return "undetermined"
    before = nc1 < rt0                      # lower coordinates than the RT
    return "upstream" if (before == (rt_strand == "+")) else "downstream"


def signed_distance(rt0: int, rt1: int, rt_strand: str, nc0: int, nc1: int):
    """Signed bases between: negative upstream, positive downstream, 0 when overlapping.

    None when the strand is missing - an unsigned magnitude would silently become a direction.
    """
    d = direction(rt0, rt1, rt_strand, nc0, nc1)
    if d == "overlapping":
        return 0
    if d == "undetermined":
        return None
    g = gap_bp(rt0, rt1, nc0, nc1)
    return -g if d == "upstream" else g


def bin_label(v: int, bins: tuple[int, ...]) -> str:
    """Half-open bins over a non-negative magnitude, with an explicit top bin."""
    if v is None:
        return "undetermined"
    a = abs(v)
    for i, b in enumerate(bins):
        if a <= b:
            return f"<={b}" if i == 0 else f"{bins[i - 1] + 1}-{b}"
    return f">{bins[-1]}"


def cds_between(rt0: int, rt1: int, nc0: int, nc1: int, cds: list[tuple[int, int]]) -> int:
    """CDS lying WHOLLY inside the gap between the two features (the RT CDS is excluded by the
    caller). Coordinate-based: it needs no gene-rank field and no upstream_gene_id convention."""
    lo, hi = (nc1 + 1, rt0 - 1) if nc1 < rt0 else (rt1 + 1, nc0 - 1)
    if hi < lo:
        return 0
    return sum(1 for s, e in cds if s >= lo and e <= hi)
