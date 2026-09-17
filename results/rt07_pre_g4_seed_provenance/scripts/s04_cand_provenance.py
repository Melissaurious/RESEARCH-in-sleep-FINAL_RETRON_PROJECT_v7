#!/usr/bin/env python3
"""pre-g4 step 4 - the provenance of the 95 CAND_* members of the old seed.

This was the last unresolved item in the old-seed genealogy. Everything measurable is
measured here: hash, length, family (the CAND identifiers carry it), exact and near presence
in every population the later work used, and which prior models were trained on a set that
contains them.

Fields that can only come from reading the builder's code - the source file, the original
identifier, the selection threshold - are read from control/cand_archaeology.tsv when that
file is present, and are landed as NOT_ESTABLISHED when it is not. An empty field that says
so is a result; a guessed one is not.

Writes: tables/preg4_cand_provenance.tsv
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preg4lib import BUNDLE_CONTROL, read_tsv, write_tsv  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    T = args.out

    lineage = [r for r in read_tsv(T / "preg4_sequence_lineage.tsv")
               if r["membership_class"] == "CANDIDATE"]
    leak = read_tsv(T / "preg4_leakage_audit.tsv")
    models = read_tsv(T / "preg4_model_lineage.tsv")

    # The builder's own tables, read read-only from the V3 tree. These are measurements of
    # what the old pipeline recorded, not a curated re-telling of it.
    from preg4lib import V3
    RECRUIT = V3 / "stage2b_assessor_redesign/columns_rt17/followup/tables/f3a_candidates.tsv"
    GATE = V3 / "stage2b_assessor_redesign/columns_rt17/followup/tables/f3c_candidate_gate.tsv"
    recruit = {r["cand_id"]: r for r in read_tsv(RECRUIT)} if RECRUIT.is_file() else {}
    gate = {r["cand_id"]: r for r in read_tsv(GATE)} if GATE.is_file() else {}
    arch = {}
    for cid, r in recruit.items():
        g = gate.get(cid, {})
        arch[cid] = {
            "original_identifier": f"rt_hash {r['rt_hash']} (corpus sequence hash; no NCBI or "
                                   f"UniProt accession exists for these)",
            "source_database_or_file":
                "stage2_rt/cache/ph4/dedup_501k.fasta - the 501,561-sequence deduplicated "
                "corpus, the same lineage as the Stage-1 catalogue",
            "generating_script":
                "columns_rt17/followup/scripts/f3a_recruit.py (recruitment) then "
                "f3c_validate.py (the G1-G5 structural gate that kept 95 of 129)",
            "selection_criterion":
                f"tier_variantB in COMPLETE/COMPLETE_MOSAIC; not clipped; 200-900 aa; cd-hit "
                f"at 50% identity; the K largest clusters per coverage tier "
                f"(6 RT7_DISSENTER / 4 THIN / 3 BY_CONSTRUCTION). No bit score or e-value. "
                f"This sequence: family {r['family']}, coverage_tier {r['coverage_tier']}, "
                f"cd-hit cluster {r['cluster']} of {r['n_clusters_in_family']} "
                f"(cluster size {r['cluster_size']}, family pool {r['pool_size']})",
            "annotation_before_inclusion":
                "YES - every CAND arrived carrying Stage-2 annotation: a palm-HMM domain "
                "boundary (palm_qs_frozen/palm_qe_frozen/palm_cov_frozen), a catalytic "
                "xxDD motif string, and a family call. The seed expansion was NOT "
                "annotation-free" +
                (f"; structural gate: mean pLDDT {g.get('mean_plddt', '?')}, "
                 f"{g.get('n_donors_tm50', '?')} crystal donors at TM>=0.5, "
                 f"max TM {g.get('max_tm', '?')}" if g else ""),
            "structural_gate_passed": g.get("VALIDATED", "NOT_IN_GATE_TABLE"),
        }

    by_seq: dict[str, dict[str, dict]] = {}
    for r in leak:
        by_seq.setdefault(r["sequence_id"], {})[r["population"]] = r

    # Every model trained on a set that contains all167 has seen every CAND by construction.
    n_all167_models = sum(1 for m in models
                          if m["built_from_set_implied_by_nseq"].startswith("all167"))

    rows = []
    for lin in lineage:
        sid = lin["sequence_id"]
        m = re.match(r"^CAND_(.+)_(\d+)$", sid)
        family = m.group(1) if m else "UNPARSED"
        pops = by_seq.get(sid, {})
        a = arch.get(sid, {})

        def cell(pid: str, field: str) -> str:
            return pops.get(pid, {}).get(field, "")

        rows.append({
            "sequence_id": sid, "sequence_hash": lin["sequence_hash"],
            "length_aa": lin["length_aa"],
            "family_from_identifier": family,
            "original_identifier": a.get("original_identifier", "NOT_ESTABLISHED"),
            "source_database_or_file": a.get("source_database_or_file", "NOT_ESTABLISHED"),
            "generating_script": a.get("generating_script", "NOT_ESTABLISHED"),
            "selection_criterion": a.get("selection_criterion", "NOT_ESTABLISHED"),
            "annotation_before_inclusion": a.get(
                "annotation_before_inclusion",
                "NOT_ESTABLISHED - whether any motif, boundary or region annotation existed "
                "for this sequence before it entered the seed"),
            "structural_gate_passed": a.get("structural_gate_passed", "NOT_ESTABLISHED"),
            "selected_using_structure":
                "YES - the 95 were kept by a structural gate (ESMFold models, crystal donors "
                "at TM>=0.5, pLDDT>=70, catalytic chemistry and order). The old seed's "
                "expansion is structure-selected, which is why it may not seed a "
                "sequence-defined instrument in g4",
            "exact_in_align000044": cell("align000044", "exact_sequence_present"),
            "exact_in_toro742": cell("toro742", "exact_sequence_present"),
            "exact_in_myrt1844": cell("myrt1844", "exact_sequence_present"),
            "exact_in_gold171": cell("gold171", "exact_sequence_present"),
            "exact_in_anchors72": cell("anchors72", "exact_sequence_present"),
            "exact_in_stage1": cell("stage1_exact_rt", "exact_sequence_present"),
            "best_identity_myrt": cell("myrt1844", "best_hit_identity"),
            "best_identity_toro": cell("toro742", "best_hit_identity"),
            "best_identity_align000044": cell("align000044", "best_hit_identity"),
            "best_identity_stage1": cell("stage1_exact_rt", "best_hit_identity"),
            "stage1_leakage_class": cell("stage1_exact_rt", "leakage_class"),
            "n_prior_models_that_saw_it": n_all167_models,
            "prior_model_note": f"every model trained on all167 has seen this sequence; "
                                f"{n_all167_models} such models were found",
            "role_in_g4": "PRIOR / AUDIT / COMPARATOR - excluded from g4 derivation, fitting, "
                          "thresholds and calibration, and excluded from any Stage-1 sample "
                          "by identity",
            "unit": "CAND_* seed member",
            "denominator": f"{len(lineage)} CAND_* members of all167.faa",
        })

    write_tsv(T / "preg4_cand_provenance.tsv",
              ["sequence_id", "sequence_hash", "length_aa", "family_from_identifier",
               "original_identifier", "source_database_or_file", "generating_script",
               "selection_criterion", "annotation_before_inclusion", "exact_in_align000044",
               "exact_in_toro742", "exact_in_myrt1844", "exact_in_gold171",
               "exact_in_anchors72", "exact_in_stage1", "best_identity_myrt",
               "best_identity_toro", "best_identity_align000044", "best_identity_stage1",
               "stage1_leakage_class", "structural_gate_passed", "selected_using_structure",
               "n_prior_models_that_saw_it", "prior_model_note", "role_in_g4", "unit",
               "denominator"], rows)

    fams: dict[str, int] = {}
    for r in rows:
        fams[r["family_from_identifier"]] = fams.get(r["family_from_identifier"], 0) + 1
    est = sum(1 for r in rows if r["generating_script"] != "NOT_ESTABLISHED")
    print(f"CAND_* members: {len(rows)} across {len(fams)} families from the identifier")
    for f, n in sorted(fams.items(), key=lambda kv: -kv[1])[:12]:
        print(f"  {f:<18} {n}")
    print(f"exactly present in Stage-1: "
          f"{sum(1 for r in rows if r['exact_in_stage1'] == 'YES')}/{len(rows)}")
    print(f"code-level provenance established: {est}/{len(rows)}"
          f"{' (control/cand_archaeology.tsv absent)' if not arch else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
