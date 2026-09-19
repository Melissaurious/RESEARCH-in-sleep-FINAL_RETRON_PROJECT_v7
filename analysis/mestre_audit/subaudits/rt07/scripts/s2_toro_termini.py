#!/usr/bin/env python3
"""s2 - Toro 2014 RT0-RT7 extraction alignment: per-sequence first/last non-gap column, by class.

Class comes from Table S1 ('RT phylogeny', 'RT class') joined to headers. The join re-uses the
V4 A1 join table (toro742_rt_class.tsv: key_type/key per header) but reads the class VALUES
directly from Table S1 by that key, and falls back to the V4 coarse_group for unjoined rows.
Also reports RT0-region (frame blocks 1-3, cols 68-182) occupancy per class and the match-state
ranges (toro742.hmm MAP) for RT0 blocks and the RT7 block / C-terminal end.
Read-only against sources.
"""
from __future__ import annotations

import csv
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import read_fasta  # noqa: E402

OUT = Path(__file__).resolve().parents[1]
H = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references/rt0_rt7/historical")
ALN = H / "toro_2014_Rt0-Rt7.FASTA"
S1 = H / "TableS1_Toro_2014.XLSX"
V4 = Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test")
CLS = V4 / "cache/toro742_rt_class.tsv"
HMM = V4 / "cache/frame/toro742.hmm"
FRAME = V4 / "tables/rt0_rt7_frame.tsv"
GAPS = set("-.")


def q(xs, ps=(0, 0.05, 0.25, 0.5, 0.75, 0.95, 1)):
    s = sorted(xs)
    return [s[min(len(s) - 1, int(round(p * (len(s) - 1))))] for p in ps]


def hmm_map(path):
    out, on = {}, False
    for line in open(path):
        if line.startswith("HMM "):
            on = True
            continue
        if on:
            p = line.split()
            if len(p) >= 22 and p[0].isdigit():
                out[int(p[0])] = int(p[21])
    return out


def main():
    seqs = read_fasta(ALN)
    width = {len(s) for _, s in seqs}
    assert len(width) == 1
    W = width.pop()
    s1 = pd.read_excel(S1, sheet_name="Hoja1")
    by = {}
    for _, r in s1.iterrows():
        for col in ("Patric Code (fid)", "GenBank GI"):
            v = r[col]
            if pd.notna(v):
                try:
                    by[str(int(v))] = r
                except (TypeError, ValueError):
                    by[str(v).strip()] = r
    cls = {r["header"]: r for r in csv.DictReader(open(CLS), delimiter="\t")}
    frame = list(csv.DictReader(open(FRAME), delimiter="\t"))
    rt0_cols = [c for b in frame if b["rt_interval"] == "RT0-RT1" for c in range(int(b["start_col"]), int(b["end_col"]) + 1)]
    rows = []
    for h, s in seqs:
        idx = [i + 1 for i, c in enumerate(s) if c not in GAPS]
        c = cls.get(h, {})
        tr = by.get(c.get("key", ""), None)
        phylo = str(tr["RT phylogeny"]).strip() if tr is not None else ""
        rtclass = str(tr["RT class"]).strip() if tr is not None else c.get("rt_class", "")
        rt0_occ = sum(1 for col in rt0_cols if s[col - 1] not in GAPS) / len(rt0_cols)
        b1 = sum(1 for col in range(68, 80) if s[col - 1] not in GAPS) / 12
        rows.append({"header": h.split()[0], "coarse_group": c.get("coarse_group", "UNASSIGNED"),
                     "tableS1_RT_phylogeny": phylo, "tableS1_RT_class": rtclass,
                     "first_col": idx[0], "last_col": idx[-1], "n_res": len(idx),
                     "rt0_blocks123_occ": round(rt0_occ, 3), "block1_occ": round(b1, 3)})
    with open(OUT / "toro2014_per_sequence_termini.tsv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    groups = defaultdict(list)
    for r in rows:
        groups[r["coarse_group"]].append(r)
        groups["ALL"].append(r)
    summ = []
    for g, rr in sorted(groups.items(), key=lambda x: -len(x[1])):
        f = q([r["first_col"] for r in rr])
        l = q([r["last_col"] for r in rr])
        n = q([r["n_res"] for r in rr])
        summ.append([g, len(rr)] + f + l + n + [
            round(st.mean(r["rt0_blocks123_occ"] for r in rr), 3),
            sum(1 for r in rr if r["first_col"] <= 79), sum(1 for r in rr if r["first_col"] > 182),
            sum(1 for r in rr if r["last_col"] >= 1297), sum(1 for r in rr if r["last_col"] >= 1305)])
    hdr = ["group", "n"] + [f"first_{p}" for p in ("min", "p05", "p25", "med", "p75", "p95", "max")] \
        + [f"last_{p}" for p in ("min", "p05", "p25", "med", "p75", "p95", "max")] \
        + [f"nres_{p}" for p in ("min", "p05", "p25", "med", "p75", "p95", "max")] \
        + ["mean_rt0_blocks1to3_occ", "n_first_le_col79(in_block1)", "n_first_after_col182(no_RT0_blocks)",
           "n_last_ge_1297(reach_RT7_block)", "n_last_ge_1305(past_RT7_block)"]
    with open(OUT / "toro2014_termini_summary.tsv", "w") as fh:
        fh.write(f"# alignment {ALN} ; {len(seqs)} seqs x {W} cols ; RT0-RT1 blocks cols {rt0_cols[0]}-{rt0_cols[-1]} (blocks 1-3)\n")
        fh.write("\t".join(hdr) + "\n")
        for r in summ:
            fh.write("\t".join(map(str, r)) + "\n")
    # column-level: distribution of first/last columns (mode concentration)
    from collections import Counter
    fc = Counter(r["first_col"] for r in rows)
    lc = Counter(r["last_col"] for r in rows)
    print("width", W, "n", len(seqs))
    print("top first cols", fc.most_common(8))
    print("top last cols", lc.most_common(8))
    for r in summ:
        print("\t".join(map(str, r)))
    # phylogeny values of retron rows
    ph = Counter((r["coarse_group"], r["tableS1_RT_phylogeny"]) for r in rows if r["coarse_group"] == "Retrons")
    print("retron rows by S1 'RT phylogeny':", ph.most_common())
    # HMM match states
    mp = hmm_map(HMM)
    col2k = {c: k for k, c in mp.items()}
    print("LENG", len(mp), "first state col", mp[1], "last state col", mp[len(mp)])
    with open(OUT / "toro742_hmm_blocks_to_match_states.tsv", "w") as fh:
        fh.write("block\tstart_col\tend_col\trt_interval\tretron_feature\tmatch_states\tfirst_state\tlast_state\n")
        for b in frame:
            ks = sorted(col2k[c] for c in range(int(b["start_col"]), int(b["end_col"]) + 1) if c in col2k)
            fh.write(f"{b['block']}\t{b['start_col']}\t{b['end_col']}\t{b['rt_interval']}\t{b['retron_feature']}\t{len(ks)}\t{ks[0] if ks else ''}\t{ks[-1] if ks else ''}\n")
        fh.write(f"#HMM\tLENG={len(mp)}\tstate1_col={mp[1]}\tstate{len(mp)}_col={mp[len(mp)]}\n")
        pre = [k for k, c in mp.items() if c < 68]
        post = [k for k, c in mp.items() if c > 1305]
        fh.write(f"#states_upstream_of_block1(col<68)\t{len(pre)}\n#states_downstream_of_block29(col>1305)\t{len(post)}\n")
    print("states before col68:", len([k for k, c in mp.items() if c < 68]),
          " after col1305:", len([k for k, c in mp.items() if c > 1305]))


if __name__ == "__main__":
    main()
