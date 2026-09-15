#!/usr/bin/env python3
"""g2lib - canonical-unit keys, RT back-translation and eligibility rules.

Shared by the extraction pass (e01) and the positive-control fixture (c04); the independent
second count (c03, shell) imports nothing from here.

Every rule that decides a count or an eligibility flag is a named constant or a function
declared here before any data is read (PLAN.md). Nothing filters a record: a record that
cannot support a measurement gets an eligibility flag and a reason, and stays in the table.
"""
from __future__ import annotations

import hashlib
import re

# --- DECLARED before any data is read ------------------------------------------------
NCRNA_FILE = "master_ncRNA-anchored_merged.jsonl"          # not part of the RT population
MULTI_FILE = "master_MULTI_merged_oriented.jsonl"
FILE_PREFIX, FILE_SUFFIX = "master_", "_merged_oriented.jsonl"
WINDOW_HALF = 10000            # mining pipeline's intended +/- window around anchor_center
START_CODONS = ("ATG", "GTG", "TTG", "ATT", "CTG")          # bacterial starts Prodigal may call
STOP_CODONS = ("TAA", "TAG", "TGA")
AA20 = "ACDEFGHIKLMNPQRSTVWY"
AA_EXTRA = "XBZJUO"            # ambiguity + Sec/Pyl; allowed but flagged
RT_HASH_NOTE = "sha256 of the uppercased amino-acid sequence with one trailing '*' removed"

# translation table 11 (bacterial), the reference frame check
_B = "TCAG"
_AA11 = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
CODON11 = {}
_i = 0
for _x in _B:
    for _y in _B:
        for _z in _B:
            CODON11[_x + _y + _z] = _AA11[_i]
            _i += 1
COMPLEMENT = str.maketrans("ACGTUacgtuNnRrYyKkMmSsWwBbVvDdHh", "TGCAAtgcaaNnYyRrMmKkSsWwVvBbHhDd")

BT_STATUS = (
    "exact",                    # translation == reported sequence
    "alt_start",                # differs only at position 1, reported M, DNA has an alt start codon
    "code4_tga_trp",            # remaining differences are all TGA translated '*' vs reported 'W'
    "internal_stop_masked",     # remaining differences are all stop codons vs reported 'U'
    "matches_opposite_strand",  # the declared strand fails but its reverse complement matches
    "mismatch",                 # anything else - NOT verified
    "not_testable_window_inverted",
    "not_testable_rt_outside_window",
    "not_testable_rt_partially_outside_window",
    "not_testable_window_length_inconsistent",
    "not_testable_bad_rt_interval",
)
BT_VERIFIED = ("exact", "alt_start", "code4_tga_trp", "internal_stop_masked")
# `matches_opposite_strand` is deliberately NOT verified: the sequence is recoverable but the
# strand as stored is wrong, which is exactly what geometry would get wrong downstream.

NO_RT_CDS_CLASS = (
    "has_rt_cds",
    "context_absent_window_inverted",
    "rt_outside_window",
    "rt_partially_outside_window",
    "no_prodigal_call_bt_verified_overlapping_cds",
    "no_prodigal_call_bt_verified_no_overlapping_cds",
    "no_prodigal_call_bt_mismatch",
    "no_prodigal_call_not_testable_other",
)


def file_label(name: str) -> str:
    if name == MULTI_FILE:
        return "MULTI"
    if name.startswith(FILE_PREFIX) and name.endswith(FILE_SUFFIX):
        return name[len(FILE_PREFIX):-len(FILE_SUFFIX)]
    return name


def rt_seq_norm(seq: str) -> str:
    """The exact-RT string: uppercased, one trailing stop removed. Nothing else is touched."""
    s = (seq or "").upper()
    return s[:-1] if s.endswith("*") else s


def rt_hash(seq: str) -> str:
    return hashlib.sha256(rt_seq_norm(seq).encode()).hexdigest()


def seq_wellformed(seq: str) -> tuple[bool, int, int]:
    """(well-formed, internal stops, non-standard residues) for the normalised sequence."""
    s = rt_seq_norm(seq)
    if not s:
        return False, 0, 0
    internal = s.count("*")
    nonstd = sum(1 for c in s if c not in AA20)
    ok = internal == 0 and all(c in AA20 + AA_EXTRA for c in s)
    return ok, internal, nonstd - internal


def translate11(nt: str) -> str:
    n = len(nt) - len(nt) % 3
    return "".join(CODON11.get(nt[i:i + 3].upper(), "X") for i in range(0, n, 3))


def revcomp(nt: str) -> str:
    return nt.translate(COMPLEMENT)[::-1]


def rt_dna(full_seq: str, win_start: int, start: int, end: int, strand: str) -> str:
    nt = full_seq[start - win_start:end - win_start + 1]
    return revcomp(nt) if strand == "-" else nt


def classify_bt(reported: str, dna: str, try_opposite: bool = True) -> tuple[str, int, str, str, int]:
    """Compare the reported protein with the window DNA translated in frame.

    Returns (status, n residue differences, first codon, last codon, internal DNA stops).
    The recoding classes exist because the corpus really contains them: TGA read as W
    (translation table 4) and internal stops written as 'U'. They are recorded as their own
    class, never silently folded into `exact` and never called a frame error.
    """
    prot = translate11(dna)
    rep = (reported or "").upper()
    first_codon = dna[:3].upper()
    last_codon = dna[-3:].upper() if len(dna) >= 3 else ""
    internal_stops = prot[:-1].count("*") if prot else 0
    if prot == rep:
        return "exact", 0, first_codon, last_codon, internal_stops
    diffs = [(i, prot[i] if i < len(prot) else "", rep[i] if i < len(rep) else "")
             for i in range(max(len(prot), len(rep)))
             if (prot[i] if i < len(prot) else "") != (rep[i] if i < len(rep) else "")]
    n = len(diffs)
    if len(prot) == len(rep):
        rest = [d for d in diffs if d[0] != 0]
        start_ok = diffs[0][0] == 0 and diffs[0][2] == "M" and first_codon in START_CODONS
        if not rest and start_ok:
            return "alt_start", n, first_codon, last_codon, internal_stops
        if rest and all(a == "*" and b == "W" for _, a, b in rest) and (start_ok or diffs[0][0] != 0):
            if all(dna[3 * i:3 * i + 3].upper() == "TGA" for i, _, _ in rest):
                return "code4_tga_trp", n, first_codon, last_codon, internal_stops
        if rest and all(a == "*" and b == "U" for _, a, b in rest) and (start_ok or diffs[0][0] != 0):
            if all(dna[3 * i:3 * i + 3].upper() in STOP_CODONS for i, _, _ in rest):
                return "internal_stop_masked", n, first_codon, last_codon, internal_stops
    # A declared strand that fails while its reverse complement matches is a strand
    # convention error, not a broken frame. Separating them is the point of the check:
    # both would otherwise land in `mismatch` and read as the same defect.
    if try_opposite:
        st, *_ = classify_bt(reported, revcomp(dna), try_opposite=False)
        if st in ("exact", "alt_start", "code4_tga_trp", "internal_stop_masked"):
            return "matches_opposite_strand", n, first_codon, last_codon, internal_stops
    return "mismatch", n, first_codon, last_codon, internal_stops


def contig_norm(contig: str) -> str:
    """RefSeq WGS contigs are the GenBank accession with an `NZ_` prefix; normalising the
    prefix is what lets the twin pair be SEEN. It is a key, not a merge: the twin flag and
    both spellings are retained, and collapsing is an explicit, reported decision."""
    return contig[3:] if contig.startswith("NZ_") else contig


_GEN = re.compile(r"^(?:RS_|GB_)?(GC[FA])_(\d+\.\d+)")


def genome_keys(genome_id: str) -> tuple[str, str]:
    """(genome_id with a GTDB RS_/GB_ prefix removed, assembly accession core or '')."""
    g = genome_id or ""
    base = g[3:] if g.startswith(("RS_", "GB_")) else g
    m = _GEN.match(g)
    return base, m.group(2) if m else ""


def locus_keys(contig: str, start: int, end: int, strand: str) -> tuple[str, str]:
    a = f"{contig}:{start}-{end}:{strand}"
    b = f"{contig_norm(contig)}:{start}-{end}:{strand}"
    return a, b


def eligibility(rec: dict) -> dict:
    """The declared eligibility rules. `rec` is the flat row built by e01.

    Each flag answers one question: can THIS record support THAT measurement? A False is
    paired with a reason, and the measurement reports how many records its rule removed.
    """
    seq_ok = rec["rt_seq_wellformed"]
    verified = rec["bt_status"] in BT_VERIFIED
    win_ok = rec["window_len_consistent"] and not rec["window_inverted"]
    out = {}
    out["elig_exact_rt"] = bool(seq_ok)
    out["elig_exact_rt_reason"] = "" if seq_ok else (
        "empty_rt_sequence" if rec["rt_aa_len"] == 0 else
        ("internal_stop_in_reported_sequence" if rec["rt_internal_stops"] else "non_amino_acid_characters"))
    coords = bool(seq_ok and rec["rt_interval_valid"] and verified)
    out["elig_rt_coords"] = coords
    out["elig_rt_coords_reason"] = "" if coords else (
        "rt_sequence_not_wellformed" if not seq_ok else
        ("bad_rt_interval" if not rec["rt_interval_valid"] else f"coords_unverified:{rec['bt_status']}"))
    geo = bool(coords and win_ok)
    out["elig_geometry"] = geo
    out["elig_geometry_reason"] = "" if geo else (
        out["elig_rt_coords_reason"] or ("window_inverted" if rec["window_inverted"]
                                         else "window_length_inconsistent"))
    out["elig_rt_length"] = bool(seq_ok)
    out["elig_rt_length_reason"] = out["elig_exact_rt_reason"]
    comp = bool(coords and (rec["rtcds_partial"] != "" or (rec["orf_start_codon_ok"] is not None)))
    out["elig_rt_completeness"] = comp
    out["elig_rt_completeness_reason"] = "" if comp else (
        out["elig_rt_coords_reason"] or "no_prodigal_partial_flag_and_no_verified_codons")
    return out
