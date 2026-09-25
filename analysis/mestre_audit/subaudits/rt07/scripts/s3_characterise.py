#!/usr/bin/env python3
"""s3 - characterise each Mestre-bearing sequence asset against the on-disk Mestre proteins.

Per asset: sha256, bytes, mtime, n records, aligned width, n records resolving to a Mestre terminal
(by name, else by exact/substring sequence match), n clean vs rescued-substitute terminals,
full-length vs extract (ungapped record == protein / proper substring / neither), and for extracts
the start/end offsets (0-based start, exclusive end) relative to the protein and relative to the
first [YFWH].DD anchor. Writes asset_characterisation.tsv and per-asset offset summaries.
Read-only against sources.
"""
from __future__ import annotations

import csv
import datetime as dt
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import build_index, load_mestre, read_any, resolve, sha256, ungap  # noqa: E402

OUT = Path(__file__).resolve().parents[1]
ANCH = re.compile(r"[YFWH].DD")
V4 = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT"
V3 = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3"
PT = "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE"
RDB = "/home/borg/RESEARCH-retron-db"
ASSETS = [
    f"{V3}/ARIS_OUTPUT/mestre_scope_audit/cache/mestre_1928_proteins.faa",
    f"{V3}/ARIS_OUTPUT/mestre_scope_audit/cache/mestre_1926_vs_RT17CORE.sto",
    f"{V3}/ARIS_OUTPUT/_archive/stage3_phylogenetic_paper/cache/mestre_ref/mestre_reference_RTs.faa",
    f"{V4}/rt0_rt7_domain_test/cache/mestre_from_V3/mestre_1926_proteins.faa",
    f"{V4}/rt0_rt7_domain_test/cache/mestre_from_V3/mestre_1926_vs_RT17CORE.sto",
    f"{V4}/rt0_rt7_domain_test/cache/frame/mestre1926_in_toro_frame.sto",
    f"{V4}/rt0_rt7_domain_test/cache/nterm/mestre_nterm_ext.faa",
    f"{V4}/rt0_rt7_domain_test/cache/a9_ibex/nterm.faa",
    f"{V4}/rt0_rt7_domain_test/cache/nterm/clu_rep_seq.fasta",
    f"{V4}/rt0_rt7_domain_test/cache/frameR/frameR_seed.faa",
    f"{V4}/rt0_rt7_domain_test/cache/frameR/frameR.afa",
    f"{V4}/rt0_rt7_domain_test/cache/frameR/holdout.faa",
    f"{V4}/rt0_rt7_domain_test/cache/frameR/holdout_vs_FrameU.sto",
    f"{V4}/rt0_rt7_domain_test/cache/frameR/holdout_vs_FrameR.sto",
    f"{V4}/rt0_rt7_domain_test_v4_and_tree/cache/mestre_narrow.faa",
    f"{V4}/rt0_rt7_domain_test_v4_and_tree/cache/mestre_toro.faa",
    f"{V4}/rt0_rt7_domain_test_v4_and_tree/cache/mestre_ours.faa",
    f"{V4}/rt0_rt7_domain_test_v4_and_tree/cache/mestre_wide.faa",
    f"{V4}/rt0_rt7_domain_test_v4_and_tree/cache/mestre_tofold.faa",
    f"{V4}/rt0_rt7_domain_test_v4_and_paper/cache/mestre_clust/m.c9",
    f"{V4}/rt0_rt7_claim_ledger/cache/mestre_clusters/mestre.c90",
    f"{V4}/s5_admission/cache/mestre_ref.mafft.faa",
    f"{V4}/s5_admission/cache/mestre_ref.trim50.faa",
    f"{V4}/stage0_positioning/cache/refbuild/mestre_ref.faa",
    f"{V4}/stage0_positioning/cache/refbuild/mestre_ref.aln",
    f"{V4}/stage0_positioning/cache/refbuild/ref_gappyout.aln",
    f"{V4}/stage0_positioning/cache/refbuild/ref_automated1.aln",
    f"{V4}/stage0_positioning/cache/refbuild/sub200.aln",
    f"{RDB}/results/stage3_placement_toolkit/cache/reference_raw.faa",
    f"{RDB}/data/derived/reference_msa_v1.afa",
    f"{PT}/reference_RTs_raw.fasta",
    f"{PT}/reference_RTs_aligned.fasta",
    f"{PT}/PIPELINE_SEQUENCES/outfiles/reference_RTs_raw.fasta",
    f"{PT}/PIPELINE_SEQUENCES/outfiles/reference_RTs_aligned.fasta",
    f"{PT}/PIPELINE_SEQUENCES/outfiles/reference_RTs_hmmaligned.fasta",
    f"{PT}/PIPELINE_SEQUENCES/outfiles/reference_RTs_aligned_synced.fasta",
    f"{PT}/IBEX_TESTS/output_files_FINAL_V2_MARCH/reference_RTs_hmmaligned.fasta",
    f"{PT}/IBEX_TESTS/output_files_FINAL_V2_MARCH/reference_RTs_aligned.fasta",
    f"{V3}/MELISSA_SCRIPTS/custom_and_hmm_analysis/extract_domain_sequences_171/sequences/full_RT_all.fasta",
    f"{V3}/MELISSA_SCRIPTS/custom_and_hmm_analysis/extract_domain_sequences_171/sequences/palm_all.fasta",
]


def q(xs):
    if not xs:
        return ""
    s = sorted(xs)
    pick = lambda p: s[min(len(s) - 1, int(round(p * (len(s) - 1))))]  # noqa: E731
    return f"min={s[0]};p05={pick(.05)};med={pick(.5)};p95={pick(.95)};max={s[-1]}"


def main() -> None:
    ref, _ = load_mestre()
    by_seq, by_name = build_index(ref)
    anchor = {}
    for t, r in ref.items():
        m = ANCH.search(r["seq"])
        anchor[t] = m.start() if m else None
    rows = []
    for a in ASSETS:
        p = Path(a)
        if not p.exists():
            rows.append({"path": a, "note": "MISSING"})
            continue
        recs = read_any(p)
        widths = {len(s) for _, s in recs}
        aligned = len(widths) == 1 and any(c in s for _, s in recs[:50] for c in "-.")
        n = len(recs)
        term = Counter()
        kind = Counter()
        st_rel, en_rel, st_abs, en_tail = [], [], [], []
        unresolved = 0
        for h, s in recs:
            u = ungap(s).rstrip("*")
            t = resolve(h, by_name)
            if t is None and u in by_seq:
                t = sorted(by_seq[u])[0]
            if t is None or t not in ref:
                unresolved += 1
                continue
            term[t] += 1
            P = ref[t]["seq"]
            if u == P:
                kind["full"] += 1
            else:
                i = P.find(u)
                if i >= 0 and u:
                    kind["extract"] += 1
                    st_abs.append(i)
                    en_tail.append(len(P) - (i + len(u)))
                    if anchor[t] is not None:
                        st_rel.append(i - anchor[t])
                        en_rel.append(i + len(u) - 1 - anchor[t])
                else:
                    kind["other(not_substring;trimmed_cols_or_different_seq)"] += 1
        resc = sum(1 for t in term if ref[t]["rescued"])
        st = p.stat()
        rows.append({
            "path": a, "sha256": sha256(p), "bytes": st.st_size,
            "mtime": dt.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
            "n_records": n, "aligned_width": (widths.pop() if len(widths) == 1 else "unaligned/var"),
            "is_alignment": aligned, "n_mestre_records": sum(term.values()), "n_unique_terminals": len(term),
            "n_rescued_substitute_terminals": resc, "n_clean_terminals": len(term) - resc,
            "n_non_mestre_records": unresolved, "kind_counts": dict(kind),
            "extract_start_minus_anchor": q(st_rel), "extract_end_minus_anchor": q(en_rel),
            "extract_start_in_protein": q(st_abs), "residues_after_extract_end": q(en_tail),
            "missing_terminals_vs_1926": 1926 - len(term) if len(term) > 1500 else "",
        })
    keys = list(rows[0].keys())
    with open(OUT / "asset_characterisation.tsv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    for r in rows:
        print({k: r.get(k) for k in ("path", "n_records", "aligned_width", "n_unique_terminals",
                                     "n_rescued_substitute_terminals", "n_non_mestre_records", "kind_counts",
                                     "extract_start_minus_anchor", "extract_end_minus_anchor")})


if __name__ == "__main__":
    main()
