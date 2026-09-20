#!/usr/bin/env python3
"""
T-C1b · PF00078 envelope census over the full exact-RT catalogue.

FROZEN BEFORE EXECUTION (WORKING_RULES §6b). This file and its launcher are
committed together, before any run; the run records that commit SHA.

WHAT THIS IS
    A complete per-sequence census: for each of the 501,561 exact RTs, whether
    the registered PF00078 profile calls a domain, where it aligns, and the
    aligned subsequence.

WHAT THIS IS NOT
    ⚠️ It is NOT core extraction. A PF00078 envelope is where the profile
    aligns. An RT core is a structural/functional claim about boundaries. The
    output column is `envelope_seq`, never `core_seq`, and the rate is
    `pf00078_domain_call_fraction`, never "frame recovery rate" -- frame
    recovery is not demonstrated here.

CONTROLS run first, BLOCK, and use SEPARATE FIXTURE FILES. No control sequence
is ever appended to the primary FASTA (operator ruling 2026-09-20 §3).
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import argparse, hashlib, json, os, random, subprocess, time
from collections import Counter, defaultdict

HMM = "/home/borg/RESEARCH-retron-db/data/derived/frame_rvt_v1.hmm"
FAA = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_exact_v1.faa"
RECORDS = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_records_v1.parquet"
PANEL = {k: f"/home/borg/RESEARCH-retron-db/data/derived/panel_{k}_v1.faa"
         for k in ("truth", "derivation", "heldout")}

DOM_EVALUE = 1e-5
PANEL_MIN = 0.70
SHUF_MAX = 0.05
EXPECT_ROWS = 501561
SEED = 20260920


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def read_fasta(p):
    name, buf = None, []
    with open(p) as fh:
        for ln in fh:
            if ln.startswith(">"):
                if name:
                    yield name, "".join(buf)
                name, buf = ln[1:].strip().split()[0], []
            else:
                buf.append(ln.strip())
    if name:
        yield name, "".join(buf)


def write_fasta(p, recs):
    with open(p, "w") as fh:
        for n, s in recs:
            fh.write(f">{n}\n")
            for i in range(0, len(s), 60):
                fh.write(s[i:i + 60] + "\n")


def hmmsearch(faa, dom, threads):
    t0 = time.time()
    r = subprocess.run(["hmmsearch", "--cpu", str(threads), "--domtblout", dom,
                        "--domE", str(DOM_EVALUE), "-o", os.devnull, HMM, faa],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"hmmsearch rc={r.returncode}: {r.stderr[-400:]}")
    return round(time.time() - t0, 1)


def parse_dom(path):
    best = {}
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("#"):
                continue
            f = ln.split()
            if len(f) < 23:
                continue
            tgt, ev, sc, ef, et = f[0], float(f[12]), float(f[13]), int(f[19]), int(f[20])
            if tgt not in best or ev < best[tgt][2]:
                best[tgt] = (ef, et, ev, sc)
    return best


def tsv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\t".join(header) + "\n")
        for r in rows:
            fh.write("\t".join("" if v is None else str(v) for v in r) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--prerun-commit", required=True,
                    help="immutable SHA of the commit that froze this file")
    a = ap.parse_args()
    out = os.path.abspath(a.outdir)
    work = os.path.join(out, "work")
    os.makedirs(work, exist_ok=True)
    t0 = time.time()
    ctrl = []

    def add(c, t, b, e, o, s, d=""):
        ctrl.append([c, t, b, e, o, s, d])

    # ---- identity ------------------------------------------------------
    hashes, bad = {}, []
    for nm, p in [("frame_rvt_v1.hmm", HMM), ("rt_exact_v1.faa", FAA),
                  ("rt_records_v1.parquet", RECORDS)] + list(PANEL.items()):
        if not os.path.exists(p):
            bad.append(f"{nm} MISSING")
            continue
        hashes[nm] = sha256(p)
        side = p + ".sha256"
        if os.path.exists(side) and open(side).read().split()[0].strip() != hashes[nm]:
            bad.append(f"{nm} hash mismatch")
    add("C1b_POS_input_identity", "positive", "YES",
        "every input present and matching its recorded sha256 where one exists",
        "all match" if not bad else "; ".join(bad), "PASS" if not bad else "FAIL")

    # ---- control fixtures, SEPARATE FILES ------------------------------
    pan = []
    for k, p in PANEL.items():
        pan += [(f"{k}|{n}", s) for n, s in read_fasta(p)]
    pos_fa = os.path.join(work, "fixture_panel.faa")
    write_fasta(pos_fa, pan)
    rnd = random.Random(SEED)
    neg = []
    for n, s in pan:
        l = list(s)
        rnd.shuffle(l)
        neg.append((f"SHUF|{n}", "".join(l)))
    neg_fa = os.path.join(work, "fixture_shuffled.faa")
    write_fasta(neg_fa, neg)

    hmmsearch(pos_fa, os.path.join(work, "fixture_panel.dom"), a.threads)
    hp = parse_dom(os.path.join(work, "fixture_panel.dom"))
    rp = len(hp) / len(pan) if pan else 0.0
    add("C1b_POS_panel", "positive", "YES",
        f">= {PANEL_MIN:.0%} of {len(pan)} curated panel RTs carry a PF00078 domain "
        f"at domE<={DOM_EVALUE}",
        f"{len(hp)}/{len(pan)} = {rp:.6f}", "PASS" if rp >= PANEL_MIN else "FAIL",
        "fixture file is separate from the primary input")

    hmmsearch(neg_fa, os.path.join(work, "fixture_shuffled.dom"), a.threads)
    hn = parse_dom(os.path.join(work, "fixture_shuffled.dom"))
    rn = len(hn) / len(neg) if neg else 0.0
    add("C1b_NEG_shuffled", "negative", "YES",
        f"<= {SHUF_MAX:.0%} of the SAME sequences, residue-shuffled at identical length "
        f"and composition, call at domE<={DOM_EVALUE}",
        f"{len(hn)}/{len(neg)} = {rn:.6f}", "PASS" if rn <= SHUF_MAX else "FAIL",
        f"seed={SEED}")

    if [c for c in ctrl if c[2] == "YES" and c[5] != "PASS"]:
        tsv(os.path.join(out, "tables/C1b_controls.tsv"),
            ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], ctrl)
        print("BLOCKING CONTROL FAILURE — no primary table written"); print("TASK_STATE: VOID")
        return 2

    # ---- primary: EVERY sequence, hit or not ---------------------------
    dom = os.path.join(work, "primary.dom")
    if os.path.exists(dom):
        os.remove(dom)
    secs = hmmsearch(FAA, dom, a.threads)
    best = parse_dom(dom)

    import pyarrow.parquet as pq
    rec = pq.read_table(RECORDS, columns=[
        "rt_seq_hash", "type_set_norm", "multilabel", "rt_aa_len",
        "elig_exact_rt", "elig_rt_length", "elig_rt_completeness"]).to_pandas()
    rec = rec.drop_duplicates("rt_seq_hash").set_index("rt_seq_hash")
    fam = rec["type_set_norm"].to_dict()
    elig = rec["elig_exact_rt"].astype(str).to_dict()
    eligL = rec["elig_rt_length"].astype(str).to_dict()
    eligC = rec["elig_rt_completeness"].astype(str).to_dict()

    rows, n_seq = [], 0
    hit_by_fam, tot_by_fam = Counter(), Counter()
    lens_hit, lens_no = [], []
    strata = defaultdict(lambda: [0, 0])
    for name, s in read_fasta(FAA):
        n_seq += 1
        b = best.get(name)
        f = fam.get(name, "UNLABELLED") or "UNLABELLED"
        tot_by_fam[f] += 1
        if b:
            hit_by_fam[f] += 1
            lens_hit.append(len(s))
            rows.append([name, len(s), "HIT", b[0], b[1], b[1] - b[0] + 1,
                         f"{b[2]:.3g}", b[3], f, elig.get(name, ""),
                         s[b[0] - 1:b[1]]])
        else:
            lens_no.append(len(s))
            rows.append([name, len(s), "NO_HIT", None, None, None, None, None,
                         f, elig.get(name, ""), None])
        k = (elig.get(name, "?"), eligL.get(name, "?"), eligC.get(name, "?"))
        strata[k][0] += 1
        strata[k][1] += 1 if b else 0

    add("C1b_POS_completeness", "positive", "YES",
        f"exactly one output row per input sequence, {EXPECT_ROWS}",
        f"{len(rows)} rows for {n_seq} sequences",
        "PASS" if (len(rows) == n_seq == EXPECT_ROWS) else "FAIL",
        "no-hit records are PRESENT and flagged, not omitted")

    if [c for c in ctrl if c[2] == "YES" and c[5] != "PASS"]:
        tsv(os.path.join(out, "tables/C1b_controls.tsv"),
            ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], ctrl)
        print("BLOCKING CONTROL FAILURE — no primary table written"); print("TASK_STATE: VOID")
        return 2

    tsv(os.path.join(out, "tables/C1b_envelopes.tsv"),
        ["rt_id", "seq_len", "hit_state", "env_from", "env_to", "envelope_len",
         "dom_evalue", "score", "rt_family", "elig_exact_rt", "envelope_seq"], rows)

    famrows = []
    for f in sorted(tot_by_fam, key=lambda x: -tot_by_fam[x]):
        t_, h_ = tot_by_fam[f], hit_by_fam[f]
        famrows.append([f, t_, h_, t_ - h_, f"{h_/t_:.6f}", f"{(t_-h_)/t_:.6f}"])
    tsv(os.path.join(out, "tables/C1b_by_family.tsv"),
        ["rt_family", "n_sequences", "n_hit", "n_no_hit",
         "pf00078_domain_call_fraction", "no_hit_rate"], famrows)

    tsv(os.path.join(out, "tables/C1b_strata.tsv"),
        ["elig_exact_rt", "elig_rt_length", "elig_rt_completeness",
         "n_sequences", "n_hit", "pf00078_domain_call_fraction"],
        [[k[0], k[1], k[2], v[0], v[1], f"{v[1]/v[0]:.6f}"]
         for k, v in sorted(strata.items(), key=lambda kv: -kv[1][0])])

    def q(x, p):
        return sorted(x)[int(p * (len(x) - 1))] if x else None
    nh = n_seq - len(best)
    tsv(os.path.join(out, "tables/C1b_summary.tsv"),
        ["quantity", "value", "unit", "denominator"],
        [["n_sequences", n_seq, "exact RT sequences", n_seq],
         ["n_hit", len(best), "sequences", n_seq],
         ["n_no_hit", nh, "sequences", n_seq],
         ["pf00078_domain_call_fraction", f"{len(best)/n_seq:.6f}", "fraction", n_seq],
         ["no_hit_rate", f"{nh/n_seq:.6f}", "fraction", n_seq],
         ["n_rt_families", len(tot_by_fam), "families", len(tot_by_fam)],
         ["envelope_len_median", q([r[5] for r in rows if r[5]], 0.5), "residues", len(best)],
         ["hit_seq_len_median", q(lens_hit, 0.5), "residues", len(lens_hit)],
         ["no_hit_seq_len_median", q(lens_no, 0.5), "residues", len(lens_no)],
         ["panel_positive_rate", f"{rp:.6f}", "fraction", len(pan)],
         ["shuffled_call_rate", f"{rn:.6f}", "fraction", len(neg)]])
    tsv(os.path.join(out, "tables/C1b_controls.tsv"),
        ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], ctrl)

    log = {"task_state": "PASS", "prerun_commit": a.prerun_commit,
           "n_sequences": n_seq, "n_hit": len(best), "n_no_hit": nh,
           "pf00078_domain_call_fraction": len(best) / n_seq,
           "dom_evalue": DOM_EVALUE, "seed": SEED, "threads": a.threads,
           "primary_hmmsearch_seconds": secs, "input_sha256": hashes,
           "elapsed_s": round(time.time() - t0, 1), "blocking_failures": []}
    os.makedirs(os.path.join(out, "logs"), exist_ok=True)
    json.dump(log, open(os.path.join(out, "logs/run_log.json"), "w"), indent=2, sort_keys=True)
    print(json.dumps(log, indent=2, sort_keys=True))
    for c in ctrl:
        print(f"{c[5]:<7} {c[0]:<26} {c[4]}")
    print("TASK_STATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
