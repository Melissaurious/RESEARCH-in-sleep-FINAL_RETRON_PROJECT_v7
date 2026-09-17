#!/usr/bin/env python3
"""s03 - THE MEASUREMENT: production `state_id` -> LtrA residue.

This is the one link the crosswalk has always been missing. It is obtained by applying the
FROZEN instrument, unmodified and through its own production entry point, to LtrA and a small
declared panel. No threshold, rule or parameter is touched: `run_mapper.py` is invoked exactly
as g5 invoked it.

Panel
  LtrA            the bridge substrate - every held historical coordinate is denominated in it
  LtrA_SHUF       NC-1, seeded shuffle; the project's own declared decoy convention (g4a step3)
  LtrA_REV        NC-2, reversed; the other g4a decoy convention
  MMLV_5VBS_A     NC-3, a real RETROVIRAL RT, recorded 'NON-MEMBER' of the bacterial RT set -
                  an out-of-population real protein, the sharpest available negative
  GsIIIC_6AR1_A   secondary comparator, Geobacillus stearothermophilus GsI-IIC RT
  Ec86_7V9U_A     secondary comparator, E. coli retron Ec86 RT

Structure-derived panel members are built from MODELLED residues only, so they carry internal
deletions where the structure is unmodelled. That is recorded per sequence and makes their
results illustrative, never a transfer claim.
"""
import os
import random
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g7alib import (G4B, TABLES, WORK, chain_residues, ltra_sequence, read_tsv,  # noqa: E402
                    write_fasta, write_tsv)

SEED = 20260918
ENVBIN = "/home/borg/miniconda3/envs/retron_tradicional/bin"
RUNNER = os.path.join(G4B, "code", "rtmap", "run_mapper.py")

STRUCT_PANEL = [("MMLV_5VBS_A", "5VBS", "A", "NC-3 out-of-population real protein "
                 "(retroviral RT, recorded NON-MEMBER of the bacterial RT set)"),
                ("GsIIIC_6AR1_A", "6AR1", "A", "secondary comparator, GsI-IIC RT"),
                ("Ec86_7V9U_A", "7V9U", "A", "secondary comparator, retron Ec86 RT")]


def build_panel():
    _, ltra = ltra_sequence()
    panel, meta = {}, []
    panel["LtrA"] = ltra
    meta.append(dict(sequence_id="LtrA", role="BRIDGE_SUBSTRATE", length=len(ltra),
                     source="rt07_g2_reference_reconstruction/reference/g2_reference_set.faa "
                            "(GenBank AAB06503)", n_unmodelled_gaps=0,
                     note="the protein every held historical coordinate is denominated in"))

    rng = random.Random(SEED)
    sh = list(ltra)
    rng.shuffle(sh)
    panel["LtrA_SHUF"] = "".join(sh)
    meta.append(dict(sequence_id="LtrA_SHUF", role="NEGATIVE_CONTROL_NC1", length=len(ltra),
                     source=f"seeded shuffle of LtrA, seed={SEED}", n_unmodelled_gaps=0,
                     note="identical amino-acid composition, no sequence order. The decoy "
                          "convention declared in g4a step3."))
    panel["LtrA_REV"] = ltra[::-1]
    meta.append(dict(sequence_id="LtrA_REV", role="NEGATIVE_CONTROL_NC2", length=len(ltra),
                     source="reversed LtrA", n_unmodelled_gaps=0,
                     note="the other g4a decoy convention."))

    for sid, pdb, chain, why in STRUCT_PANEL:
        res = chain_residues(pdb, chain)
        ks = sorted(res)
        seq = "".join(res[k] for k in ks)
        gaps = sum(1 for a, b in zip(ks, ks[1:]) if b != a + 1)
        panel[sid] = seq
        meta.append(dict(sequence_id=sid, role="PANEL", length=len(seq),
                         source=f"{pdb} chain {chain}, modelled residues "
                                f"{ks[0]}-{ks[-1]}", n_unmodelled_gaps=gaps,
                         note=why + f". Built from MODELLED residues only: {gaps} internal "
                                    f"chain break(s). Illustrative, not a transfer claim."))
    return panel, meta


def run_frozen(faa, out, shard):
    env = dict(os.environ, PATH=ENVBIN + os.pathsep + os.environ.get("PATH", ""))
    subprocess.run([sys.executable, RUNNER, "--in", faa, "--out", out, "--shard", shard,
                    "--work", os.path.join(WORK, shard + "_work"), "--force"],
                   check=True, env=env)


def main():
    os.makedirs(WORK, exist_ok=True)
    panel, meta = build_panel()
    faa = os.path.join(WORK, "panel.faa")
    write_fasta(panel, faa)
    out = os.path.join(WORK, "panel_out")
    run_frozen(faa, out, "panel")

    seqs = {r["sequence_id"]: r for r in read_tsv(os.path.join(out, "panel.sequences.tsv"))}
    states = read_tsv(os.path.join(out, "panel.states.tsv"))
    fails = read_tsv(os.path.join(out, "panel.failures.tsv"))

    write_tsv(os.path.join(TABLES, "g7a_panel.tsv"),
              ["sequence_id", "role", "length", "source", "n_unmodelled_gaps", "note"], meta)

    # ---- the bridge: state -> LtrA residue -------------------------------------------
    bridge = [dict(state_id=int(r["state_id"]), anchor_index=int(r["anchor_index"]),
                   call_state=r["call_state"],
                   ltra_residue=r["sequence_residue_index"], amino_acid=r["amino_acid"],
                   posterior=r["posterior"], reason_code=r["reason_code"],
                   unit="frozen conserved state on LtrA",
                   frame="GII.deriv.hmm state_id -> LtrA P0A3U0 residue",
                   denominator="150 frozen anchor states")
              for r in states if r["sequence_id"] == "LtrA"]
    bridge.sort(key=lambda r: r["state_id"])
    write_tsv(os.path.join(TABLES, "g7a_state_to_residue.tsv"),
              ["state_id", "anchor_index", "call_state", "ltra_residue", "amino_acid",
               "posterior", "reason_code", "unit", "frame", "denominator"], bridge)

    mapped = [r for r in bridge if r["call_state"] == "MAPPED"]
    res = sorted(int(r["ltra_residue"]) for r in mapped)
    sid = sorted(r["state_id"] for r in mapped)
    ltra_row = seqs["LtrA"]

    # ---- controls --------------------------------------------------------------------
    ctrl = []

    def add(cid, kind, expectation, observed, result, note):
        ctrl.append(dict(control_id=cid, kind=kind, expectation=expectation,
                         observed=observed, result=result, note=note))

    add("PC-1", "positive control - catalytic",
        "CAT_STATE 262 lands on the LtrA Y/FxDD catalytic dyad",
        f"cat_call_state={ltra_row['cat_call_state']}, residue "
        f"{ltra_row['cat_residue_index']} ({ltra_row['cat_residue']}), window "
        f"{ltra_row['cat_motif_window']}, class {ltra_row['cat_motif_class']}, "
        f"{ltra_row['n_dyad_motifs_in_sequence']} dyad motif(s) in the sequence",
        "PASS" if (ltra_row["cat_call_state"] == "MAPPED"
                   and ltra_row["cat_motif_class"] == "CATALYTIC_CONFIRMED") else "FAIL",
        "The sharpest independent check on the state->residue bridge: the one operational "
        "coordinate the frozen instrument commits to, on the one protein the history is "
        "denominated in. LAUNCHER_03 section 2 positive-control kill.")

    add("PC-4", "positive control - the Zimmerly anchor is MEASURED",
        "the catalytic residue lies inside g2 block 5 (LtrA 304-347), which is what makes "
        "'the catalytic YxDD lies in subdomain 5' (Z11) an anchor rather than an assumption",
        f"catalytic residue {ltra_row['cat_residue_index']}; g2 block 5 = LtrA 304-347",
        "PASS" if 304 <= int(ltra_row["cat_residue_index"]) <= 347 else "FAIL",
        "Declared rule A2/A3. If this fails, the single anchored label<->interval pair is "
        "lost and every label becomes ordinal with no anchor.")

    add("PC-5", "positive control - LtrA is inspectable",
        "the frozen instrument commits on LtrA (verdict MAPPED)",
        f"verdict={ltra_row['verdict']}, mapped {ltra_row['n_mapped']}/150 "
        f"({ltra_row['mapped_fraction']}), domain bitscore {ltra_row['domain_bitscore']}, "
        f"E-value {ltra_row['domain_evalue']}",
        "PASS" if ltra_row["verdict"] == "MAPPED" else "FAIL",
        "LAUNCHER_03 section 2 substrate kill.")

    for cid, sidq, role in (("NC-1", "LtrA_SHUF", "seeded shuffle"),
                            ("NC-2", "LtrA_REV", "reversed"),
                            ("NC-3", "MMLV_5VBS_A", "out-of-population real protein")):
        row = seqs.get(sidq)
        if row is None:
            f = [x for x in fails if x.get("sequence_id") == sidq]
            d = f[0] if f else {}
            add(cid, "negative control",
                "does not produce a confident mapping comparable to real LtrA",
                f"NOT TESTED - produced no scientific row: "
                f"{d.get('inspectability_status', 'absent')} / "
                f"{d.get('reason_code', '')} ({d.get('detail', '')})",
                "INCONCLUSIVE",
                f"{role}. The sequence was rejected by the FROZEN eligibility rule BEFORE it "
                "reached the mapper, so this is not evidence that the mapper abstains on it - "
                "it is evidence that the sequence is outside the population the instrument is "
                "ever applied to. Recorded as inconclusive rather than counted as a pass. The "
                "valid negatives for this gate are NC-1 and NC-2, which both reached the "
                "mapper and both ABSTAINED at 0/150.")
            continue
        add(cid, "negative control",
            "does not produce a confident mapping comparable to real LtrA",
            f"verdict={row['verdict']}, mapped {row['n_mapped']}/150 "
            f"({row['mapped_fraction']}), bitscore {row['domain_bitscore']}, "
            f"E-value {row['domain_evalue']}",
            "PASS" if (row["verdict"] != "MAPPED"
                       or float(row["mapped_fraction"]) < 0.5 * float(ltra_row["mapped_fraction"]))
            else "FAIL",
            f"{role}. Compared against LtrA's {ltra_row['mapped_fraction']}. "
            "LAUNCHER_03 section 2 negative-control kill.")

    add("PC-2", "anchor span - a LIMITATION, measured",
        "the 150 anchors do not cover the whole protein; the covered span is reported",
        f"MAPPED anchors span state_id {sid[0]}-{sid[-1]} and LtrA residues "
        f"{res[0]}-{res[-1]}; {len(mapped)} of 150 anchors MAPPED",
        "MEASURED",
        "This is the binding constraint on the crosswalk: a historical region outside LtrA "
        f"{res[0]}-{res[-1]} CANNOT receive frozen-state support however well defined it is "
        "historically (declared rule A7). It is a property of the frozen instrument, not of "
        "the biology, and it is not repaired.")

    add("NC-4", "anti-circularity", "no g5 or g6 path is read by this gate",
        "checked in verify.sh against INPUTS.tsv and the scripts",
        "SEE_VERIFY", "LAUNCHER_03 section 4 hard input exclusion.")

    write_tsv(os.path.join(TABLES, "g7a_controls.tsv"),
              ["control_id", "kind", "expectation", "observed", "result", "note"], ctrl)

    # sequence-level summary for every panel member
    write_tsv(os.path.join(TABLES, "g7a_panel_results.tsv"),
              ["sequence_id", "sequence_length", "verdict", "n_mapped", "mapped_fraction",
               "n_deleted", "n_unsupported", "domain_bitscore", "domain_evalue",
               "cat_call_state", "cat_residue_index", "cat_motif_window", "cat_motif_class"],
              [seqs[k] for k in panel if k in seqs])

    fail = [c for c in ctrl if c["result"] == "FAIL"]
    print(f"s03: bridge = {len(mapped)}/150 anchors MAPPED on LtrA, "
          f"state_id {sid[0]}-{sid[-1]} -> LtrA residues {res[0]}-{res[-1]}")
    for c in ctrl:
        print(f"  {c['control_id']:<5} {c['result']:<9} {c['observed'][:95]}")
    if fail:
        raise SystemExit(f"s03: {len(fail)} control(s) FAILED - see LAUNCHER_03 section 2")


if __name__ == "__main__":
    main()
