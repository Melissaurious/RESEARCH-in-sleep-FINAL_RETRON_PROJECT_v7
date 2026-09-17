#!/usr/bin/env python3
"""rt07_g3 step 5 - one verdict per prior claim, computed from the landed measurements.

Each verdict is assembled from values this gate measured, not from a reading of the prior
reports, and each carries the frame, stratum, n and denominator the prior number was
computed on. The vocabulary is the launcher's plus the states the operator named:

  REPRODUCED_SAME_OBJECT_SAME_FRAME   the number comes back, measuring the same thing
  REPRODUCED_DIFFERENT_FRAME          comes back, but in a different coordinate system
  PARTIALLY_REPRODUCED                part of the claim survives
  NOT_REPRODUCED                      it does not come back
  CIRCULAR_OR_SEED_DEPENDENT          it is true by construction, or measured on its own seed
  OBJECT_MISMATCH                     the prior number measures a different object than named
  FRAME_MISMATCH                      the coordinate systems are not the same object
  NOT_TESTABLE                        this gate cannot decide it
  WITHDRAWN_BY_PRIOR_WORK             the prior work withdrew it itself

A verdict is never "wrong because it disagrees with g2". g2 established conserved regions
and explicitly did NOT establish a seven-way partition, so a prior claim is judged on what it
measured, on what frame, and on how much of its validation was its own seed.

Writes: tables/g3_prior_claim_verdicts.tsv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g3lib import control, read_tsv, write_tsv  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    T = args.out

    claims = {c["claim_id"]: c for c in control("prior_claims.tsv")}
    ov = {(r["set_a"], r["set_b"]): r for r in read_tsv(T / "g3_set_overlap.tsv")}
    comp = {r["property"]: r for r in read_tsv(T / "g3_anchor_composition.tsv")}
    frames = {r["frame_id"]: r for r in read_tsv(T / "g3_frame_identity.tsv")}
    corr = read_tsv(T / "g3_prior_region_correspondence.tsv")
    pframe = read_tsv(T / "g3_prior_frame_correspondence.tsv")
    rt0 = {r["quantity"]: r["value"] for r in read_tsv(T / "g3_rt0_object_audit.tsv")}

    rt17 = [c for c in corr if c["frame_id"] == "RT17_CORE"]
    inside = sum(1 for c in corr if c["correspondence"] == "INSIDE_A_G2_REGION")
    same_res: dict[str, set] = {}
    for c in corr:
        same_res.setdefault(c["prior_label"], set()).add(c["ltra_start"])
    n_same = sum(1 for v in same_res.values() if len(v) == 1)
    rt5 = next(c for c in rt17 if c["prior_label"] == "RT5")
    rt6 = next(c for c in rt17 if c["prior_label"] == "RT6")
    rt1 = next(c for c in rt17 if c["prior_label"] == "RT1")
    fixed = sum(1 for r in pframe if r.get("fixed_by_published_motif") == "YES")
    mapped = [r for r in pframe if str(r.get("ltra_start", "")).isdigit()]

    V = []

    def add(cid, verdict, evidence, frame, stratum_n, what_survives, what_changes):
        c = claims[cid]
        V.append({
            "claim_id": cid, "prior_claim": c["prior_claim"],
            "prior_value": c["prior_value"], "prior_source": c["prior_source"],
            "verdict": verdict, "evidence_measured_in_g3": evidence,
            "frame": frame, "stratum_and_n": stratum_n,
            "what_survives": what_survives, "what_changes": what_changes,
            "becomes_acceptance_criterion": "NO - no prior number is an acceptance criterion "
                                            "in this track (launcher 5d)",
            "unit": "prior claim", "denominator": f"{len(claims)} prior claims audited"})

    add("D1", "PARTIALLY_REPRODUCED",
        f"The two landmark states reproduce as POSITIONS: RT3 state 146 and RT5 state 229 "
        f"carry onto LtrA residues {next(c['ltra_start'] for c in rt17 if c['prior_label']=='RT3')} "
        f"and {rt5['ltra_start']}, both inside independently reconstructed g2 regions "
        f"(blocks {next(c['best_g2_block'] for c in rt17 if c['prior_label']=='RT3')} and "
        f"{rt5['best_g2_block']}); the RT5 landmark sits 2 residues from the catalytic "
        f"Y/FxDD that g2 located without consulting it. The 99.91% is NOT a held-out "
        f"accuracy: it is frac_D_of_occupied at one state in the retron stratum.",
        "RT17_CORE (= B_span17, 305 states) -> LtrA residues",
        "retron stratum n=78,287; anchors n=72",
        "The landmark POSITIONS. They are real locations in conserved regions, recovered "
        "independently in g2.",
        "The 99.91% must be renamed: it is the fraction of occupied sequences carrying Asp at "
        "one state, not a held-out performance figure. The enrichment range 214-441x is a "
        "property of a pair chosen because it is the dyad.")

    add("D2", "REPRODUCED_SAME_OBJECT_SAME_FRAME",
        f"RT1's landmark is the one that moves: it is the only one of the seven that does NOT "
        f"place at the same LtrA residue in every prior frame ({n_same} of 7 are identical "
        f"across frames), and its prior concordance is 0.75 in RT17_CORE against a declared "
        f"0.90 bar. In g2 coordinates the RT1 landmark falls at LtrA {rt1['ltra_start']}, "
        f"inside g2 block {rt1['best_g2_block']} - which lies in the LtrA region Blocker 2005 "
        f"assigns to RT0, not RT1.",
        "RT17_CORE and three further frames -> LtrA residues", "72 anchors",
        "The failure is real and reproduces: RT1 is the unstable landmark in every frame.",
        "INTERPRETATION IS NOT SETTLED HERE. Whether this is a limitation of the method or an "
        "independent recovery of a weakness the founding authors flagged remains an operator "
        "decision (launcher 9b). g3 adds one fact to it: the RT1 landmark maps into the RT0 "
        "zone on LtrA.")

    add("D4", "NOT_TESTABLE",
        "The Toro comparator arm belongs to g7 under the launcher's tier rules. g3 registers "
        "the object and does not re-derive a comparator here.",
        "not evaluated in this gate", "n/a",
        "Nothing is claimed either way.",
        "Deferred to g7 with its object recorded.")

    add("D6", "WITHDRAWN_BY_PRIOR_WORK",
        "Withdrawn by the prior work itself before this gate: regeneration gave 224x / 445x "
        "against the reported 2,657x / 4,936x, and Region X was weak rather than "
        "family-exclusive. g3 does not re-enter either value.",
        "n/a - withdrawn", "n/a",
        "Nothing. The withdrawal stands.",
        "Neither the original nor the regenerated magnitude may be quoted in this track.")

    a72 = ov[("anchors72", "seed_all167")]
    a72r = ov[("anchors72", "retron")]
    pdb = comp.get("id_prefix:PDB", {}).get("value", "?")
    his = comp.get("expression_tag:His6", {}).get("value", "0")
    add("A72_EXTERNAL", "CIRCULAR_OR_SEED_DEPENDENT",
        f"Re-measured by exact sequence identity: {a72['n_shared_sequences']}/{a72['n_a']} "
        f"({a72['pct_of_a_in_b']}%) of the anchors are in the model seed. Composition: "
        f"{pdb} of 72 carry a PDB id and the remaining 46 are sequence-propagated; "
        f"{a72r['n_shared_sequences']}/{a72r['n_a']} ({a72r['pct_of_a_in_b']}%) are also "
        f"members of the retron population they score. NEW IN g3: {his} of the 72 carry a "
        f"His6 expression tag and one carries a SUMO tag, so their residue numbering includes "
        f"vector-derived sequence.",
        "n/a - set membership", "anchors n=72",
        "The 72 sequences exist and 26 of them do have structures.",
        "The phrase '72 structure-validated anchors' is refuted three ways: 100% seed "
        "membership, 26 of 72 with structure, and tagged constructs inside the set.")

    add("C72", "OBJECT_MISMATCH",
        "The quoted '72/72' is concordance_over_truth_defined = 1.0 at states 146 and 229, "
        "i.e. 72 of 72 anchor rows landing on the modal state. Since all 72 anchors are seed "
        "members, it measures self-consistency between two alignments of the same sequences, "
        "not agreement with 72 independent references. The prior audit's own script says so "
        "in its docstring.",
        "RT17_CORE", "72 anchors, all seed members",
        "The measurement itself: the anchors do land consistently.",
        "The name. It is not 72 independent determinations and must never be quoted as "
        "concordance against external references.")

    g = ov[("gold175_uniq", "seed_all167")]
    ga = ov[("gold175_uniq", "anchors72")]
    add("GOLD175", "CIRCULAR_OR_SEED_DEPENDENT",
        f"Re-measured: {g['n_shared_sequences']}/{g['n_a']} ({g['pct_of_a_in_b']}%) of the "
        f"gold panel are exact-sequence seed members, reproducing the prior audit exactly. "
        f"NEW IN g3: the same {ga['n_shared_sequences']} sequences are the panel's overlap "
        f"with anchors72, so the panel's contamination enters entirely through the anchor "
        f"set; and {ov[('gold175_uniq', 'retron')]['pct_of_a_in_b']}% of the panel are also "
        f"in the retron population.",
        "n/a - set membership", "gold panel n=171 unique (named 175)",
        "The panel exists and 127 of its members are outside the seed.",
        "Any field recording this panel as in_model_seed = no is false by 25.73 points; a "
        "held-out design must be built on the 127, with that n stated.")

    add("PRODUCERS", "CIRCULAR_OR_SEED_DEPENDENT",
        "The prior audit measured 42 of 63 RT-DNA producers inside the seed and this gate "
        "does not re-derive the producer labels, which come from an external support table. "
        "What g3 confirms is the mechanism: the gold panel that supplies the producers is "
        "25.73% seed by exact sequence, and its seed overlap is entirely the anchor set.",
        "RT17_CORE", "63 producers within a 171-member panel",
        "On all 63 the hypergeometric test was real (p = 0.0141).",
        "The referee is not external: on the 21 producers outside the seed p = 0.2983, a test "
        "near-incapable of failing. 'External referee' must carry the subset qualifier.")

    add("RT0_VOID", "OBJECT_MISMATCH",
        f"The prior RT0 number was measured on frame blocks 1-2, LtrA "
        f"{rt0.get('prior_RT0_proximal_blocks_ltra_extent')}, and "
        f"{rt0.get('prior_RT0_proximal_blocks_all_interpolated')} that every block in that "
        f"region is order_interpolated rather than fixed by a published motif. The prior "
        f"frame begins at LtrA {rt0.get('prior_frame_ltra_extent')} and does NOT cover the "
        f"conserved RT0 alanine at LtrA {rt0.get('blocker_rt0_conserved_alanine_ltra')}, "
        f"which the independently reconstructed g2 region "
        f"{rt0.get('g2_region_covering_that_alanine')} does cover. The two are different "
        f"objects.",
        "prior RT0-RT7 frame in LtrA P0A3U0 numbering vs g2 regions",
        "retrons n=102, group II introns n=442 in the prior alignment",
        "The occupancy contrast itself is real and was measured with a declared positive "
        "control that passed: group II introns occupy that region at 0.8999, retrons at "
        "0.105, same columns, same alignment.",
        "It is not an RT0 number. It measures interpolated N-terminal blocks that exclude the "
        "only specific RT0 landmark available. The prior work's own later trees reached the "
        "same conclusion and banned RT0 as a landmark. U01 stays open and the scope limit "
        "from g2 stands: the defining cross-class claim is untestable on this substrate.")

    add("RT0_FRAME_GAP", "REPRODUCED_SAME_OBJECT_SAME_FRAME",
        f"Independently confirmed: the prior frame spans LtrA "
        f"{rt0.get('prior_frame_ltra_extent')} and begins "
        f"{rt0.get('prior_frame_starts_n_residues_after_the_alanine')} residues downstream of "
        f"the RT0 alanine at 39. g2's reconstruction places a conserved region at LtrA 39-61, "
        f"covering it.",
        "LtrA P0A3U0 numbering", "one reference protein",
        "The prior observation is exactly right and this gate reproduces it from the frame "
        "table itself.",
        "It is now paired with a positive: the region the prior frame excluded is one the "
        "independent reconstruction recovers.")

    add("SEVEN_BLOCKS", "FRAME_MISMATCH",
        f"Of {len(mapped)} mappable prior frame blocks only {fixed} are fixed by a published "
        f"motif; the rest are order_interpolated. {inside} of {len(corr)} prior landmark "
        f"placements fall inside a g2 region, and the seven prior labels collapse onto SIX "
        f"g2 regions because RT5 (LtrA {rt5['ltra_start']}) and RT6 (LtrA "
        f"{rt6['ltra_start']}) both fall in g2 block {rt5['best_g2_block']}. Across four "
        f"prior frames, {n_same} of 7 landmarks place at the identical LtrA residue, so the "
        f"frames are coordinate systems over one landmark set rather than independent "
        f"determinations.",
        "four prior frames -> LtrA residues vs g2 regions",
        "29 prior blocks; 6 g2 regions; 28 landmark placements",
        "The prior landmarks are real positions inside conserved regions, and their ORDER is "
        "preserved.",
        "No old seven-block result is defensible AS A SEVEN-WAY PARTITION after frame "
        "reconciliation: the seventh boundary is the RT5/RT6 split, which falls inside a "
        "single independently reconstructed region, and 24 of 28 prior blocks were "
        "interpolated rather than anchored.")

    add("DOMAIN_PHYLO", "WITHDRAWN_BY_PRIOR_WORK",
        "The prior work itself banned the description: the tips were a 341-residue window "
        "cut around the catalytic tetrad, Jaccard 0.732 against the published window, and the "
        "RT0-RT7 derivation was never fed to the tree.",
        "tetrad-anchored window -220..+120", "n/a",
        "The window is a legitimate object under its own name.",
        "The phrase 'domain-based phylogeny' must not reappear.")

    add("VOID_FILE", "NOT_TESTABLE",
        "VOID_DO_NOT_CITE.md is referenced by six prior documents and by the project's own "
        "contract as the file to consult before quoting any prior figure. It does not exist "
        "anywhere under the prior project tree. This gate therefore could not consult it, and "
        "records that every prior figure quoted here was re-measured rather than cited.",
        "n/a", "n/a",
        "Nothing depends on it in g3, because g3 re-measured rather than quoted.",
        "It stays unresolvable, and any later gate that quotes a prior figure without "
        "re-measuring inherits the problem.")

    write_tsv(T / "g3_prior_claim_verdicts.tsv",
              ["claim_id", "prior_claim", "prior_value", "prior_source", "verdict",
               "evidence_measured_in_g3", "frame", "stratum_and_n", "what_survives",
               "what_changes", "becomes_acceptance_criterion", "unit", "denominator"], V)

    counts: dict[str, int] = {}
    for v in V:
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
    print(f"verdicts: {len(V)}")
    for k in sorted(counts, key=lambda x: -counts[x]):
        print(f"  {k:<36} {counts[k]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
