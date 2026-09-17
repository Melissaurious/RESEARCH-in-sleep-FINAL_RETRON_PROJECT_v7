#!/usr/bin/env python3
"""Frozen production output schema `rtmap-schema-1.0`.

Three tables per shard, one provenance sidecar per run.

    states.tsv        one row per (sequence, frozen conserved state)  - 150 rows/sequence
    sequences.tsv     one row per sequence, summaries + catalytic block
    failures.tsv      one row per sequence that produced no state rows

Design rules that are NOT negotiable downstream:

  * The four per-state call states are NEVER collapsed to a binary present/absent.
    `DELETED_STATE` is a statement about the alignment path, not about the biology: the
    residue is absent FROM THE MATCH COLUMN, which is a different claim from "this protein
    lacks this region". g6 must not convert one into the other.

  * Only `MAPPED` is positive evidence. `AMBIGUOUS` and `UNSUPPORTED` are reported and are
    never counted toward callability. This is the frozen rule, carried verbatim.

  * The catalytic state (262) is NOT one of the 150 frozen anchors. Anchor callability and
    catalytic placement are separate measurements over different denominators and are never
    pooled. The schema keeps them in different column blocks for exactly that reason, and
    `n_states_total` counts anchors only.

  * `mapped_fraction` has denominator `n_states_total` (the anchors at or below the profile
    LENG), matching `pct_mapped` in the landed construction and UG25 tables.

  * Historical RT0-RT7 labels appear in NO column of these tables. They live in a separate
    crosswalk table (see crosswalk.py), joined on `state_id`, and are interpretation.
"""

SCHEMA_VERSION = "rtmap-schema-1.0"

# ---------------------------------------------------------------------------------------
# Per-state call states. Frozen in mapper.py; restated here only as the schema's enum.
# ---------------------------------------------------------------------------------------
CALL_STATES = (
    "MAPPED",         # residue in the match column, posterior >= PP_HI     (evidence)
    "AMBIGUOUS",      # residue in the match column, PP_LO <= post < PP_HI  (not evidence)
    "UNSUPPORTED",    # residue in the match column, posterior < PP_LO      (not evidence)
    "DELETED_STATE",  # match column is a gap on this sequence's path       (not evidence)
)

# Why a state carries the call it carries. Machine-readable, never free text.
STATE_REASON_CODES = {
    "OK_POSTERIOR_AT_OR_ABOVE_PP_HI": "MAPPED",
    "POSTERIOR_BETWEEN_PP_LO_AND_PP_HI": "AMBIGUOUS",
    "POSTERIOR_BELOW_PP_LO": "UNSUPPORTED",
    "POSTERIOR_UNAVAILABLE": "UNSUPPORTED",
    "MATCH_COLUMN_GAPPED": "DELETED_STATE",
}

# ---------------------------------------------------------------------------------------
# Sequence-level verdict, from the frozen `classify_sequence`. Unchanged wording.
# ---------------------------------------------------------------------------------------
SEQUENCE_VERDICTS = ("MAPPED", "ABSTAIN")
SEQUENCE_REASONS = ("OK", "NO_QUALIFYING_DOMAIN", "INSUFFICIENT_SUPPORTED_ANCHORS")

# ---------------------------------------------------------------------------------------
# Production inspectability status (launcher §7).
#
# This is a RELABELLING of the frozen (verdict, reason) pair, plus the frozen T1 threshold.
# It introduces NO new predicate: the map below is a bijection onto the frozen reason codes,
# and `MAPPABLE` / `PARTIAL_MAPPING` are split by T1, which is itself frozen. An earlier
# draft used an invented comparison (`n_ambiguous + n_unsupported > n_mapped`) to pick out
# AMBIGUOUS_MAPPING; the independent packaging review correctly called that a new
# classification rule, and it was removed. Nothing here is a scientific classification.
#
#   (MAPPED,  OK,                             frac >= T1) -> MAPPABLE
#   (MAPPED,  OK,                             frac <  T1) -> PARTIAL_MAPPING
#   (ABSTAIN, INSUFFICIENT_SUPPORTED_ANCHORS)             -> AMBIGUOUS_MAPPING
#   (ABSTAIN, NO_QUALIFYING_DOMAIN)                       -> NO_SUPPORTED_MAPPING
#
# NO_SUPPORTED_MAPPING IS NOT BIOLOGICAL ABSENCE. It says this instrument, under this
# profile and this match-state convention, found no qualifying domain. A protein can be
# a genuine RT and still land here - the construction families themselves run from median
# 95% (GII) to median 47% (Retrons) callability.
# ---------------------------------------------------------------------------------------
INSPECTABILITY_STATUS = {
    "MAPPABLE":
        "verdict MAPPED and mapped_fraction >= T1 (the frozen 5th-percentile construction "
        "floor). The sequence sits inside the callability range the instrument was "
        "calibrated on.",
    "PARTIAL_MAPPING":
        "verdict MAPPED (>= K_MIN supported anchors and a qualifying domain) but "
        "mapped_fraction < T1. Callable, below the construction floor. Retained, not "
        "filtered.",
    "AMBIGUOUS_MAPPING":
        "verdict ABSTAIN with the frozen reason INSUFFICIENT_SUPPORTED_ANCHORS: the "
        "sequence HAS a qualifying domain, so the instrument recognises it, but fewer than "
        "K_MIN anchors reached PP_HI. Support was the limiting factor, not recognition. "
        "Residues may well sit in those match columns with the model declining to commit "
        "to them - inspect the AMBIGUOUS and UNSUPPORTED counts and the per-state rows. "
        "This is not absence.",
    "NO_SUPPORTED_MAPPING":
        "verdict ABSTAIN with the frozen reason NO_QUALIFYING_DOMAIN: no domain was "
        "reported, or its bitscore was below S_MIN. NOT a biological absence claim; see "
        "the module docstring.",
    "INPUT_INVALID":
        "the record never reached the mapper: empty or short sequence, non-standard "
        "residue, duplicate identifier, unparseable FASTA. No scientific statement is made.",
    "TOOL_FAILURE":
        "hmmalign / hmmsearch failed, or an internal fail-closed assertion fired (LENG "
        "mismatch, PP-length mismatch, missing #=GC RF). No scientific statement is made.",
}

# The relabelling above, as data. `run_mapper.inspectability` is this map plus the T1 split
# and nothing else; the freeze tests assert the two agree on every frozen (verdict, reason).
STATUS_FROM_FROZEN_REASON = {
    ("ABSTAIN", "INSUFFICIENT_SUPPORTED_ANCHORS"): "AMBIGUOUS_MAPPING",
    ("ABSTAIN", "NO_QUALIFYING_DOMAIN"): "NO_SUPPORTED_MAPPING",
}

# The two statuses that are engineering facts, not measurements. They appear in
# failures.tsv and never in sequences.tsv.
NON_SCIENTIFIC_STATUS = ("INPUT_INVALID", "TOOL_FAILURE")

# ---------------------------------------------------------------------------------------
# Catalytic block. Frozen rule: evaluate CAT_STATE over the full state range; a MAPPED call
# whose residue starts the frozen dyad pattern is CATALYTIC_CONFIRMED.
#
# "Confirmed" means MOTIF CONCORDANCE AT A STATE. It is not independent residue truth, and
# the closure decision says so explicitly.
# ---------------------------------------------------------------------------------------
CAT_MOTIF_CLASSES = (
    "CATALYTIC_CONFIRMED",       # CAT_STATE MAPPED and residue begins [YF].DD
    "CATALYTIC_SUBSTITUTED",     # CAT_STATE MAPPED, residue does not begin [YF].DD
    "CATALYTIC_AMBIGUOUS",       # CAT_STATE AMBIGUOUS
    "CATALYTIC_UNSUPPORTED",     # CAT_STATE UNSUPPORTED
    "CATALYTIC_STATE_DELETED",   # CAT_STATE match column gapped
)

# ---------------------------------------------------------------------------------------
# Column orders. These ARE the schema; changing one is a schema-version change.
# ---------------------------------------------------------------------------------------
STATES_COLUMNS = (
    "rt_hash",                 # sha256 of the cleaned residue string - the join key
    "sequence_id",
    "mapper_version",
    "state_id",                # frozen conserved state (HMM match state), 1..LENG
    "anchor_index",            # 1..150, position of this state in the frozen anchor set
    "call_state",
    "sequence_residue_index",  # 1-based residue index, empty when DELETED_STATE
    "amino_acid",              # '-' when DELETED_STATE
    "posterior",               # lower bound of the HMMER PP band, empty when DELETED_STATE
    "support",                 # the per-state evidence weight: posterior, or 0.0 if none
    "reason_code",
)

SEQUENCES_COLUMNS = (
    "rt_hash",
    "sequence_id",
    "sequence_length",
    "mapper_version",
    "profile_version",
    "match_state_definition",
    "family_metadata",         # Stage-1 stratum label if supplied, else NOT_SUPPLIED
    # --- anchor block; denominator n_states_total ---
    "n_states_total",
    "n_mapped",
    "n_ambiguous",
    "n_unsupported",
    "n_deleted",
    "mapped_fraction",
    "verdict",
    "reason",
    "domain_bitscore",
    "domain_evalue",
    "inspectability_status",
    # --- catalytic block; SEPARATE denominator, never pooled with the anchor block ---
    "cat_state",
    "cat_call_state",
    "cat_residue_index",
    "cat_residue",
    "cat_motif_class",
    "cat_support",
    "cat_motif_window",        # the 4 residues from cat_residue_index, for inspection
    "n_dyad_motifs_in_sequence",
    # --- architecture, retained for g6; never a filter ---
    "n_insertion_runs",
    "total_inserted_residues",
    "max_insertion_run",
)

FAILURES_COLUMNS = (
    "rt_hash",
    "sequence_id",
    "sequence_length",
    "mapper_version",
    "inspectability_status",   # INPUT_INVALID or TOOL_FAILURE
    "reason_code",
    "detail",
)

PROVENANCE_COLUMNS = ("key", "value")

INPUT_INVALID_REASONS = (
    "EMPTY_SEQUENCE",
    "BELOW_MIN_LENGTH",
    "NON_STANDARD_RESIDUE",
    "DUPLICATE_SEQUENCE_ID",           # repeated identifier, identical sequence
    "DUPLICATE_SEQUENCE_ID_CONFLICT",  # repeated identifier, DIFFERENT sequences
    "UNPARSEABLE_RECORD",
)


def header(columns):
    return "\t".join(columns) + "\n"


def row(columns, d):
    """Render one record. Every column must be present - a missing key is a schema bug."""
    missing = [c for c in columns if c not in d]
    if missing:
        raise SystemExit(f"FAIL CLOSED: schema fields missing from record: {missing}")
    return "\t".join("" if d[c] is None else str(d[c]) for c in columns) + "\n"


if __name__ == "__main__":
    print(f"{SCHEMA_VERSION}")
    for name, cols in (("states", STATES_COLUMNS), ("sequences", SEQUENCES_COLUMNS),
                       ("failures", FAILURES_COLUMNS)):
        print(f"\n{name}.tsv ({len(cols)} columns)")
        for c in cols:
            print(f"  {c}")
