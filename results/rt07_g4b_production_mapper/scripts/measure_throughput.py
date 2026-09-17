#!/usr/bin/env python3
"""Reproducible throughput measurement. ENGINEERING ONLY - no scientific claim.

    measure_throughput.py <work_dir> [out.tsv]

The independent packaging review noted that the landed throughput table's component
decomposition (alignment vs domain search) and its gzip ratio had no reproducible script
behind them, and that 2.2 + 11.9 did not add to the quoted 13.8 total because the numbers
came from different harnesses. This script produces every number in one run, on one
substrate, and writes the table itself, so the components and the total are commensurable
by construction.

Substrate: construction-family sequences only, materialised with the registered loader.
UG25 is never touched.
"""
import gzip
import os
import shutil
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
G4B = os.path.dirname(HERE)
ROOT = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
PY = "/home/borg/miniconda3/envs/retron_tradicional/bin/python3"

sys.path.insert(0, f"{G4B}/code")
sys.path.insert(0, f"{ROOT}/results/FINAL_PRE_UG25_VALIDATION_BUNDLE/code")

from rtmap import params as P          # noqa: E402
from rtmap.mapper import state_to_residue, domain_scores   # noqa: E402

FAMILIES = ("Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA")
N_PER_FAMILY = 120
STAGE1_N = 501561


def build_substrate(path):
    from loader import load_families
    e = load_families(FAMILIES)
    picked = []
    for fam in FAMILIES:
        for k in sorted(e[fam])[:N_PER_FAMILY]:
            picked.append((k, e[fam][k]))
    with open(path, "w") as f:
        for k, v in picked:
            f.write(f">{k}\n{v}\n")
    return dict(picked)


def main():
    w = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    os.makedirs(w, exist_ok=True)
    fa = f"{w}/throughput.faa"
    seqs = build_substrate(fa)
    n = len(seqs)
    lengths = [len(v) for v in seqs.values()]
    print(f"substrate: {n} sequences, mean length {statistics.mean(lengths):.1f} aa")

    # ---- component 1: batched alignment, one call over the whole substrate -------------
    t = time.perf_counter()
    state_to_residue(P.PROFILE_HMM, seqs, w, "align", pp_hi=P.PP_HI, pp_lo=P.PP_LO)
    t_align = time.perf_counter() - t

    # ---- component 2: per-sequence domain scoring, production protocol -----------------
    t = time.perf_counter()
    for i, sid in enumerate(sorted(seqs)):
        p = f"{w}/d{i:05d}.faa"
        with open(p, "w") as f:
            f.write(f">{sid}\n{seqs[sid]}\n")
        domain_scores(P.PROFILE_HMM, p, w, f"d{i:05d}")
    t_dom = time.perf_counter() - t

    # ---- end to end: the production runner, same substrate -----------------------------
    od = f"{w}/run"
    os.makedirs(od, exist_ok=True)
    t = time.perf_counter()
    r = subprocess.run([PY, "-B", f"{G4B}/code/rtmap/run_mapper.py", "--in", fa,
                        "--out", od, "--shard", "tp", "--work", f"{w}/runwork"],
                       capture_output=True, text=True,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    t_run = time.perf_counter() - t
    if r.returncode != 0:
        raise SystemExit(f"FAIL: runner returned {r.returncode}\n{r.stderr}")

    st = f"{od}/tp.states.tsv"
    sq = f"{od}/tp.sequences.tsv"
    n_state_rows = sum(1 for _ in open(st)) - 1
    b_states, b_seqs = os.path.getsize(st), os.path.getsize(sq)
    with open(st, "rb") as fi, gzip.open(f"{w}/states.gz", "wb") as fo:
        shutil.copyfileobj(fi, fo)
    gz = os.path.getsize(f"{w}/states.gz")
    ratio = b_states / gz

    per_seq_ms = 1000 * t_run / n
    rows = [
        ("n_sequences_timed", n, "sequences",
         f"{N_PER_FAMILY} per construction family, capped by family size"),
        ("mean_sequence_length", f"{statistics.mean(lengths):.1f}", "aa",
         "Stage-1 family medians run 253-1232 aa; see docs/G5_EXECUTION_PLAN.md"),
        ("wall_end_to_end", f"{t_run:.2f}", "s",
         "the production runner, one process, one core, default batching"),
        ("per_sequence_cost", f"{per_seq_ms:.1f}", "ms",
         "end-to-end wall / n; this is the number the g5 estimate uses"),
        ("component_alignment", f"{1000 * t_align / n:.1f}", "ms",
         "batched hmmalign over the whole substrate, in-process"),
        ("component_domain_search", f"{1000 * t_dom / n:.1f}", "ms",
         "per-sequence hmmsearch, production protocol, in-process"),
        ("component_sum", f"{1000 * (t_align + t_dom) / n:.1f}", "ms",
         "the two components add to LESS than the end-to-end cost; the remainder is "
         "process startup, I/O and row rendering, and is why the total - not the sum - is "
         "what the g5 estimate uses"),
        ("states_bytes_per_row", f"{b_states / n_state_rows:.1f}", "bytes",
         f"measured on {n_state_rows} emitted state rows"),
        ("sequences_bytes_per_row", f"{b_seqs / n:.1f}", "bytes",
         f"measured on {n} emitted sequence rows"),
        ("states_gzip_ratio", f"{ratio:.1f}", "x", "gzip -9 default, measured on this file"),
        ("projected_stage1_core_hours", f"{STAGE1_N * per_seq_ms / 1000 / 3600:.2f}",
         "core-hours", f"{STAGE1_N} x per_sequence_cost. NOT an upper bound: it is a "
         f"full-count extrapolation AT THIS SUBSTRATE'S RATE. Two effects push in opposite "
         f"directions - the eligible population is smaller than {STAGE1_N} (censused in g5 "
         f"step 1), but the Stage-1 length distribution is wider than this 477 aa substrate "
         f"(family medians 253-1232 aa) and hmmalign cost scales with length, so the "
         f"per-record cost can be higher"),
        ("projected_states_rows", f"{STAGE1_N * len(P.ANCHORS) / 1e6:.1f}", "million rows",
         f"{STAGE1_N} x {len(P.ANCHORS)} anchors"),
        ("projected_states_gb_raw",
         f"{STAGE1_N * len(P.ANCHORS) * b_states / n_state_rows / 1e9:.1f}", "GB", ""),
        ("projected_states_gb_gzip",
         f"{STAGE1_N * len(P.ANCHORS) * b_states / n_state_rows / ratio / 1e9:.2f}", "GB",
         "storage, not compute, is the binding constraint"),
        ("projected_sequences_mb", f"{STAGE1_N * b_seqs / n / 1e6:.0f}", "MB", ""),
    ]

    text = ("# MEASURED production throughput, produced by scripts/measure_throughput.py in a\n"
            "# SINGLE run on a SINGLE substrate, so components and total are commensurable.\n"
            "# Single core, one process, no parallelism. CPU only, no GPU, no Ibex.\n"
            "# Construction-family sequences only; UG25 is never touched.\n"
            "# Wall-clock numbers vary a few per cent between runs; they are measurements,\n"
            "# not frozen constants, and are NOT part of the instrument identifier.\n"
            "quantity\tvalue\tunit\tnote\n")
    text += "".join(f"{a}\t{b}\t{c}\t{d}\n" for a, b, c, d in rows)
    if out:
        with open(out, "w") as f:
            f.write(text)
        print(f"wrote {out}")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
