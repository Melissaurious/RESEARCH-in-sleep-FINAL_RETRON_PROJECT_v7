#!/usr/bin/env python3
"""rt07_g3 step 3 - do the prior regions and the g2 regions describe the same thing?

A prior result says "the landmark is at match state 146". A g2 result says "a conserved
region runs from LtrA residue 126 to 166". Those are not comparable as numbers, and comparing
them by BLOCK LABEL would be worse: it would ask whether prior RT3 equals g2 block 3, which
presumes the seven-way partition g2 did not establish.

So the comparison is made on shared residues. The prior HMM is aligned to the g2 reference
proteins, which gives every prior match state a residue in each of them - including LtrA,
which both frames contain. Prior spans become LtrA intervals; g2 blocks already are LtrA
intervals; the correspondence is then Jaccard overlap, the same instrument g2 used to compare
its own two alignment frames.

This uses the prior HMM as a COORDINATE SYSTEM, not as a definition. No prior boundary is
adopted, and no g2 region is moved to fit one.

Writes: tables/g3_matchstate_to_ltra.tsv, tables/g3_prior_region_correspondence.tsv,
        tables/g3_frame_identity.tsv
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g3lib import (ENV, G2, control, g2_blocks, hmm_header, jaccard,  # noqa: E402
                       resolve, sha256_file, write_tsv)

LTRA = "L.l."


def match_state_map(sto: Path, seq_id: str) -> dict[int, int]:
    """match state -> residue number, for one sequence of an hmmalign result."""
    rows: dict[str, str] = {}
    for line in sto.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        p = line.split()
        if len(p) == 2:
            rows[p[0]] = rows.get(p[0], "") + p[1]
    aligned = rows.get(seq_id)
    if aligned is None:
        raise SystemExit(f"FATAL: {seq_id} absent from {sto}")
    res = state = 0
    out: dict[int, int] = {}
    for ch in aligned:
        if ch == "." or (ch.islower() and ch != "-"):
            if ch != ".":
                res += 1
            continue
        state += 1
        if ch != "-":
            res += 1
            out[state] = res
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    T, W = args.out, args.work
    W.mkdir(parents=True, exist_ok=True)

    refset = G2 / "reference/g2_reference_set.faa"
    frames = control("prior_frames.tsv")
    blocks = [(int(b["block_index"]), int(b["ltra_start_residue"]), int(b["ltra_end_residue"]),
               b["blocker_zone"], b["contains_catalytic_yxdd"])
              for b in g2_blocks()
              if b["ltra_start_residue"].isdigit() and b["ltra_end_residue"].isdigit()]

    identity, m2r_rows, corr = [], [], []
    maps: dict[str, dict[int, int]] = {}

    for f in frames:
        hmm = resolve(f["relative_path"])
        if not hmm.is_file():
            identity.append({"frame_id": f["frame_id"], "path": str(hmm),
                             "state": "MISSING", "declared_name_inside_file": "",
                             "leng": "", "nseq": "", "file_name_claims": f["name_claims"],
                             "name_matches_file": "NOT_TESTABLE", "sha256": "ABSENT",
                             "mapped_to_ltra_states": 0,
                             "unit": "prior frame", "denominator": "prior frames declared"})
            continue
        hdr = hmm_header(hmm)
        sto = W / f"{f['frame_id']}_vs_g2ref.sto"
        subprocess.run([str(ENV / "hmmalign"), "--amino", "-o", str(sto), str(hmm),
                        str(refset)], check=True, capture_output=True)
        m2r = match_state_map(sto, LTRA)
        maps[f["frame_id"]] = m2r
        identity.append({
            "frame_id": f["frame_id"], "path": str(hmm), "state": "ALIGNED",
            "declared_name_inside_file": hdr.get("NAME", ""),
            "leng": hdr.get("LENG", ""), "nseq": hdr.get("NSEQ", ""),
            "file_name_claims": f["name_claims"],
            # The finding is not whether the model matches what the control table says it
            # is - that would be circular - but whether the model's own NAME matches the
            # FILE it ships as. A number quoted on "RT17_CORE" is a number on B_span17.
            "file_stem": hmm.stem,
            "name_matches_file": ("YES" if hdr.get("NAME", "") == hmm.stem
                                  else f"NO - ships as {hmm.stem}.hmm but declares "
                                       f"NAME {hdr.get('NAME', '?')}"),
            "sha256": sha256_file(hmm),
            "mapped_to_ltra_states": len(m2r),
            "unit": "prior frame", "denominator": f"{len(frames)} prior frames declared"})
        for state, res in sorted(m2r.items()):
            m2r_rows.append({"frame_id": f["frame_id"], "match_state": state,
                             "ltra_residue": res, "unit": "HMM match state",
                             "frame": f["frame_id"],
                             "denominator": f"{hdr.get('LENG', '?')} match states in the model"})

    # Two frames that are the same bytes are one object under two names.
    by_sha: dict[str, list[str]] = {}
    for i in identity:
        if i["state"] == "ALIGNED":
            by_sha.setdefault(i["sha256"], []).append(i["frame_id"])
    for i in identity:
        twins = [x for x in by_sha.get(i.get("sha256", ""), []) if x != i["frame_id"]]
        i["identical_file_to"] = ",".join(twins) or "none"

    write_tsv(T / "g3_frame_identity.tsv",
              ["frame_id", "path", "state", "declared_name_inside_file", "file_stem",
               "leng", "nseq", "file_name_claims", "name_matches_file", "sha256",
               "identical_file_to", "mapped_to_ltra_states", "unit", "denominator"],
              identity)
    write_tsv(T / "g3_matchstate_to_ltra.tsv",
              ["frame_id", "match_state", "ltra_residue", "unit", "frame", "denominator"],
              m2r_rows)

    # ---------- prior regions -> LtrA -> correspondence with the g2 regions ----------
    for r in control("prior_regions.tsv"):
        m2r = maps.get(r["frame_id"])
        if not m2r:
            corr.append({**{k: r[k] for k in ("prior_region_id", "frame_id", "prior_label",
                                              "prior_coordinate_kind", "prior_start",
                                              "prior_end", "source_table")},
                         "ltra_start": "", "ltra_end": "",
                         "best_g2_block": "", "jaccard_on_ltra_residues": "",
                         "n_g2_blocks_overlapping": "", "correspondence": "NOT_TESTABLE",
                         "note": "the prior frame could not be aligned, so its coordinates "
                                 "cannot be carried onto a shared sequence",
                         "unit": "prior region", "denominator": "prior regions declared"})
            continue
        try:
            s, e = int(r["prior_start"]), int(r["prior_end"])
        except ValueError:
            continue

        def nearest(state: int, mode: str) -> int | None:
            if state in m2r:
                return m2r[state]
            cands = [k for k in m2r if (k <= state if mode == "s" else k >= state)]
            return m2r[max(cands)] if mode == "s" and cands else \
                   m2r[min(cands)] if cands else None

        ls, le = nearest(s, "s"), nearest(e, "e")
        if ls is None or le is None:
            corr.append({**{k: r[k] for k in ("prior_region_id", "frame_id", "prior_label",
                                              "prior_coordinate_kind", "prior_start",
                                              "prior_end", "source_table")},
                         "ltra_start": "", "ltra_end": "", "best_g2_block": "",
                         "jaccard_on_ltra_residues": "", "n_g2_blocks_overlapping": "",
                         "correspondence": "OUTSIDE_SHARED_SEQUENCE",
                         "note": "the prior span falls where LtrA has no residue in this model",
                         "unit": "prior region", "denominator": "prior regions declared"})
            continue
        best, best_j = None, 0.0
        overlapping = []
        for idx, bs, be, zone, yx in blocks:
            j = jaccard((ls, le), (bs, be))
            if j > best_j:
                best, best_j = (idx, bs, be, zone, yx), j
            if not (be < ls or bs > le):
                overlapping.append(idx)
        corr.append({
            **{k: r[k] for k in ("prior_region_id", "frame_id", "prior_label",
                                 "prior_coordinate_kind", "prior_start", "prior_end",
                                 "source_table")},
            "ltra_start": ls, "ltra_end": le,
            "best_g2_block": best[0] if best else "NONE",
            "jaccard_on_ltra_residues": f"{best_j:.3f}",
            "n_g2_blocks_overlapping": len(overlapping),
            # A prior landmark is a POINT, and Jaccard between a point and a 40-residue
            # region is small however well they agree. For a point the honest statistic is
            # containment: does the prior landmark fall inside an independently
            # reconstructed region, or in a gap between them?
            "correspondence": (
                ("INSIDE_A_G2_REGION" if overlapping else "IN_A_GAP_BETWEEN_G2_REGIONS")
                if ls == le else
                ("STRONG_POSITIONAL_MATCH" if best_j >= 0.5 else
                 "PARTIAL_POSITIONAL_MATCH" if best_j > 0 else
                 "NO_POSITIONAL_COUNTERPART")),
            "containment_or_jaccard": ("containment (the prior region is a single point)"
                                       if ls == le else "Jaccard over residues"),
            "note": r["note"],
            "unit": "prior region mapped onto shared LtrA residues",
            "frame": "LtrA residue coordinates",
            "denominator": f"{len(blocks)} independently reconstructed g2 regions"})

    write_tsv(T / "g3_prior_region_correspondence.tsv",
              ["prior_region_id", "frame_id", "prior_label", "prior_coordinate_kind",
               "prior_start", "prior_end", "ltra_start", "ltra_end", "best_g2_block",
               "jaccard_on_ltra_residues", "n_g2_blocks_overlapping", "correspondence",
               "containment_or_jaccard", "note", "source_table", "unit", "frame",
               "denominator"], corr)

    strong = sum(1 for c in corr if c["correspondence"] in
                 ("STRONG_POSITIONAL_MATCH", "INSIDE_A_G2_REGION"))
    print(f"frames aligned: {sum(1 for i in identity if i['state'] == 'ALIGNED')}/"
          f"{len(identity)}")
    for i in identity:
        if i["state"] == "ALIGNED" and i["name_matches_file"].startswith("NO"):
            print(f"  NAME MISMATCH: {i['path']} declares NAME={i['declared_name_inside_file']}")
    print(f"prior regions mapped: {len(corr)}; inside a g2 region: {strong}")
    by_res: dict[str, set] = {}
    for c in corr:
        by_res.setdefault(c["prior_label"], set()).add(c["ltra_start"])
    ident = sum(1 for v in by_res.values() if len(v) == 1)
    print(f"landmarks placing at the SAME LtrA residue in every frame: {ident}/{len(by_res)}"
          f" - the frames are coordinate systems over one landmark set, not independent "
          f"determinations")
    for c in corr:
        print(f"  {c['prior_region_id']:<18} {c['prior_label']:<10} -> LtrA "
              f"{c['ltra_start']}-{c['ltra_end']}  g2 block {c['best_g2_block']} "
              f"J={c['jaccard_on_ltra_residues']}  {c['correspondence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
