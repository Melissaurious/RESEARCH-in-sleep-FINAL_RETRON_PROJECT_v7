#!/usr/bin/env python3
"""rt07_g3 step 6 - controls, rollup, and what g3 hands to g4.

The controls ask whether this gate's two instruments could have returned another answer:

  C1 POSITIVE  the frame-correspondence instrument must place the prior RT5 landmark on the
               catalytic Y/FxDD that g2 located independently. If a coordinate carrier cannot
               reproduce the one landmark both sides agree on, nothing it says about the
               others is worth reading.
  C2 POSITIVE  the seed-overlap re-measurement must reproduce the prior audit's published
               overlaps from the files, not from their report. This is an external
               reproduction that could have failed.
  C3 NULL      shuffling the anchor residues must collapse the overlap to zero. An identity
               measure that returns 100% on shuffled sequences is measuring nothing.
  C4 POSITIVE  two frames the prior work treated as separate must be shown identical by hash,
               or the object/frame confusion is an assertion rather than a measurement.

--seed-bad matches sequences on identifiers instead of residues, which is the defect the
prior audit avoided; run.sh asserts that the controls then fail.

Writes: tables/g3_controls.tsv, tables/g3_summary.tsv,
        tables/g3_handoff_to_g4.tsv, tables/g3_unresolved_carried_forward.tsv
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g3lib import (G2, control, read_fasta, resolve, seq_hash, read_tsv,  # noqa: E402
                       write_tsv)

SEED = 20260915


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed-bad", action="store_true")
    args = ap.parse_args()
    T = args.out

    corr = read_tsv(T / "g3_prior_region_correspondence.tsv")
    frames = read_tsv(T / "g3_frame_identity.tsv")
    ov = {(r["set_a"], r["set_b"]): r for r in read_tsv(T / "g3_set_overlap.tsv")}
    verdicts = read_tsv(T / "g3_prior_claim_verdicts.tsv")
    pframe = read_tsv(T / "g3_prior_frame_correspondence.tsv")
    rt0 = {r["quantity"]: r["value"] for r in read_tsv(T / "g3_rt0_object_audit.tsv")}

    # C1 - the catalytic landmark, located independently on both sides
    g2_yxdd_block = next(b["block_index"] for b in read_tsv(
        G2 / "tables/g2_ltra_mapping.tsv") if b["contains_catalytic_yxdd"] == "YES")
    rt5 = next(c for c in corr if c["frame_id"] == "RT17_CORE" and c["prior_label"] == "RT5")
    c1_ok = rt5["best_g2_block"] == g2_yxdd_block

    # C2 - reproduce the prior audit's own published overlaps from the files
    published = {("anchors72", "seed_all167"): (72, 72),
                 ("gold175_uniq", "seed_all167"): (44, 171)}
    c2_rows, c2_ok = [], True
    for key, (n_shared, n_a) in published.items():
        r = ov.get(key)
        got = (int(r["n_shared_sequences"]), int(r["n_a"])) if r else (None, None)
        ok = got == (n_shared, n_a)
        c2_ok &= ok
        c2_rows.append(f"{key[0]}: prior {n_shared}/{n_a}, g3 {got[0]}/{got[1]}")

    # C3 - the null: shuffled residues must not match
    sets = {s["set_id"]: s for s in control("prior_sets.tsv")}
    anchors = read_fasta(resolve(sets["anchors72"]["relative_path"]))
    seed = read_fasta(resolve(sets["seed_all167"]["relative_path"]))
    seed_h = {seq_hash(v) for v in seed.values()}
    rng = random.Random(SEED)
    if args.seed_bad:
        # The defect the prior audit explicitly avoided: join on identifiers.
        shuffled_hits = len(set(anchors) & set(seed))
        observed_hits = len(set(anchors) & set(seed))
    else:
        shuffled_hits = 0
        for v in anchors.values():
            chars = list(v)
            rng.shuffle(chars)
            if seq_hash("".join(chars)) in seed_h:
                shuffled_hits += 1
        observed_hits = sum(1 for v in anchors.values() if seq_hash(v) in seed_h)
    c3_ok = shuffled_hits == 0 and observed_hits > 0

    # C4 - two names, one file
    twins = [f for f in frames if f.get("identical_file_to") not in ("", "none")]
    c4_ok = len(twins) >= 2

    controls = [
        {"control": "C1:frame_carrier_places_RT5_on_the_catalytic_region", "kind": "POSITIVE",
         "expected": f"prior RT5 lands in the g2 region containing Y/FxDD (block {g2_yxdd_block})",
         "observed": f"g2 block {rt5['best_g2_block']} at LtrA {rt5['ltra_start']}",
         "result": "PASS" if c1_ok else "FAIL"},
        {"control": "C2:seed_overlaps_reproduce_the_prior_audit_from_files", "kind": "POSITIVE",
         "expected": "exact reproduction of the prior audit's published overlaps",
         "observed": "; ".join(c2_rows), "result": "PASS" if c2_ok else "FAIL"},
        {"control": "C3:identity_measure_collapses_under_residue_shuffling", "kind": "NULL",
         "expected": "0 matches on shuffled residues, non-zero on real ones",
         "observed": f"shuffled {shuffled_hits}, observed {observed_hits}",
         "result": "PASS" if c3_ok else "FAIL"},
        {"control": "C4:frames_the_prior_work_named_separately_are_one_file", "kind": "POSITIVE",
         "expected": "at least two registered frames share a sha256",
         "observed": ", ".join(f"{t['frame_id']}={t['identical_file_to']}" for t in twins)
                     or "none",
         "result": "PASS" if c4_ok else "FAIL"},
    ]
    for c in controls:
        c.update({"unit": "control", "denominator": "4 controls declared before measuring"})
    write_tsv(T / "g3_controls.tsv",
              ["control", "kind", "expected", "observed", "result", "unit", "denominator"],
              controls)

    def nv(v):
        return sum(1 for x in verdicts if x["verdict"] == v)

    inside = sum(1 for c in corr if c["correspondence"] == "INSIDE_A_G2_REGION")
    fixed = sum(1 for r in pframe if r.get("fixed_by_published_motif") == "YES")
    mapped = [r for r in pframe if str(r.get("ltra_start", "")).isdigit()]
    S = [
        ("prior_claims_audited", len(verdicts), "g3_prior_claim_verdicts.tsv", "prior claim"),
        ("verdict_reproduced_same_object_same_frame",
         nv("REPRODUCED_SAME_OBJECT_SAME_FRAME"), "g3_prior_claim_verdicts.tsv", "prior claim"),
        ("verdict_partially_reproduced", nv("PARTIALLY_REPRODUCED"),
         "g3_prior_claim_verdicts.tsv", "prior claim"),
        ("verdict_circular_or_seed_dependent", nv("CIRCULAR_OR_SEED_DEPENDENT"),
         "g3_prior_claim_verdicts.tsv", "prior claim"),
        ("verdict_object_mismatch", nv("OBJECT_MISMATCH"), "g3_prior_claim_verdicts.tsv",
         "prior claim"),
        ("verdict_frame_mismatch", nv("FRAME_MISMATCH"), "g3_prior_claim_verdicts.tsv",
         "prior claim"),
        ("verdict_withdrawn_by_prior_work", nv("WITHDRAWN_BY_PRIOR_WORK"),
         "g3_prior_claim_verdicts.tsv", "prior claim"),
        ("verdict_not_testable", nv("NOT_TESTABLE"), "g3_prior_claim_verdicts.tsv",
         "prior claim"),
        ("anchors72_in_seed_pct", ov[("anchors72", "seed_all167")]["pct_of_a_in_b"],
         "g3_set_overlap.tsv", "percent of anchors72"),
        ("anchors72_also_in_retron_population_pct",
         ov[("anchors72", "retron")]["pct_of_a_in_b"], "g3_set_overlap.tsv",
         "percent of anchors72"),
        ("gold175_uniq_in_seed_pct", ov[("gold175_uniq", "seed_all167")]["pct_of_a_in_b"],
         "g3_set_overlap.tsv", "percent of the gold panel"),
        ("gold_panel_members_outside_the_seed",
         int(ov[("gold175_uniq", "seed_all167")]["n_a"]) -
         int(ov[("gold175_uniq", "seed_all167")]["n_shared_sequences"]),
         "g3_set_overlap.tsv", "sequence"),
        ("prior_landmarks_inside_a_g2_region", f"{inside}/{len(corr)}",
         "g3_prior_region_correspondence.tsv", "landmark placement"),
        ("prior_frame_blocks_fixed_by_a_published_motif", f"{fixed}/{len(mapped)}",
         "g3_prior_frame_correspondence.tsv", "prior frame block"),
        ("prior_labels_collapsing_onto_one_g2_region", "RT5 and RT6",
         "g3_prior_region_correspondence.tsv", "prior label"),
        ("rt0_object_verdict", rt0.get("object_verdict"), "g3_rt0_object_audit.tsv",
         "object comparison"),
        ("controls_pass", sum(1 for c in controls if c["result"] == "PASS"),
         "g3_controls.tsv", "control"),
    ]
    write_tsv(T / "g3_summary.tsv",
              ["quantity", "value", "source_table", "unit", "denominator"],
              [{"quantity": q, "value": v, "source_table": t, "unit": u,
                "denominator": "see the source table"} for q, v, t, u in S])

    handoff = [
        ("held_out_population_for_g4",
         f"{int(ov[('gold175_uniq', 'seed_all167')]['n_a']) - int(ov[('gold175_uniq', 'seed_all167')]['n_shared_sequences'])} "
         f"gold-panel members are outside the seed by exact sequence",
         "g4 may build a held-out design on those members and must state that n. The other 44 "
         "are seed and may not be counted as held out."),
        ("anchors72_unusable_as_validation",
         "100% seed membership; 26 of 72 with structure; 7 tagged constructs",
         "g4 may not use anchors72 as a validation set at all, and may not take residue "
         "numbering from the tagged members without removing the tag offset."),
        ("frame_must_be_named_by_content",
         "RT17_CORE and B_span17 are one file; B_full is also the name of a derived column "
         "slice",
         "g4 names every frame by the file it is and records its sha256, or the same "
         "object/frame confusion recurs."),
        ("no_seven_way_partition_to_inherit",
         "the seven prior labels collapse onto six g2 regions; RT5 and RT6 share one",
         "g4's per-block model must be built on regions with interval uncertainty, not on "
         "seven boxes, and any block count it reports needs its own null."),
        ("rt0_out_of_scope_for_occupancy",
         rt0.get("object_verdict", ""),
         "g4 may not report an RT0 occupancy: the prior RT0 region excludes the RT0 landmark "
         "and the defining claim is untestable on the available substrate."),
        ("rt1_is_the_unstable_landmark",
         "RT1 is the only landmark that moves between prior frames, and it maps into the "
         "Blocker RT0 zone on LtrA",
         "g4 must treat the RT1 region as a declared uncertainty, WITHOUT adopting any "
         "interpretation of the concordance failure - that remains an operator decision."),
    ]
    write_tsv(T / "g3_handoff_to_g4.tsv",
              ["requirement", "measurement", "what_g4_must_do", "unit", "denominator"],
              [{"requirement": a, "measurement": b, "what_g4_must_do": c,
                "unit": "design requirement",
                "denominator": f"{len(handoff)} requirements raised by g3"}
               for a, b, c in handoff])

    carried = [
        ("U01", "Where is the primary definition of domain 0 / RT0?", "STILL_OPEN",
         "Unchanged. Malik et al. 1999 remains unheld. g3 adds that the prior project's own "
         "RT0 region excludes the RT0 landmark, so no prior artefact substitutes for it."),
        ("U02", "Which blocks do Simon & Zimmerly's 59 alignable characters fall in?",
         "STILL_OPEN", "Not addressed by g3; belongs to the comparator gate."),
        ("U08", "Is domain 1's weaker support in 1990 the same object as a later RT1 "
                "concordance failure?", "STILL_DEFERRED",
         "g3 measured the RT1 failure and did NOT interpret it. One new fact for the "
         "operator's eventual decision: the prior RT1 landmark maps into the LtrA region "
         "Blocker assigns to RT0."),
        ("U09", "Is the block COUNT recoverable at all?", "STILL_OPEN",
         "g3 adds evidence: 24 of 28 prior blocks were interpolated rather than anchored, and "
         "the prior seventh boundary falls inside a single g2 region."),
        ("U10", "Does VOID_DO_NOT_CITE.md exist?", "NEW_CLOSED_AS_ABSENT",
         "Referenced by six prior documents and by this project's contract; absent from disk. "
         "g3 re-measured every prior figure it reports rather than quoting one."),
        ("U11", "What is the tag offset in the 7 tagged anchors?", "NEW_OPEN",
         "Raised by g3. Seven anchors carry His6 and one carries SUMO, so any residue "
         "coordinate taken from them is offset unless the tag was stripped. The prior work "
         "does not record whether it was."),
    ]
    write_tsv(T / "g3_unresolved_carried_forward.tsv",
              ["item_id", "question", "status_after_g3", "what_g3_changed", "unit",
               "denominator"],
              [{"item_id": a, "question": b, "status_after_g3": c, "what_g3_changed": d,
                "unit": "open question", "denominator": f"{len(carried)} items carried"}
               for a, b, c, d in carried])

    failed = [c for c in controls if c["result"] != "PASS"]
    for c in controls:
        print(f"  {c['result']:<4} {c['control']}")
    if args.seed_bad:
        print("seed-bad mode: controls SHOULD have failed")
        return 0 if failed else 1
    print(f"summary rows: {len(S)}; handoff requirements: {len(handoff)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
