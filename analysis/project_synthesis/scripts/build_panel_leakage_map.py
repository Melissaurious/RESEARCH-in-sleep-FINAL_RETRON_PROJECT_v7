#!/usr/bin/env python3
"""PANEL_LEAKAGE_MAP.tsv — exact-hash exposure map of the 175-element experimental panel
against every project population that a benchmark claim would depend on.

Read-only over all sources. Joins are EXACT SEQUENCE HASHES under the project's own rules:

  rt_seq_hash = sha256(upper(seq) with ONE trailing '*' removed)      dbchar_g2 g2lib.rt_seq_norm
  nc_seq_hash = sha256(upper(sequence_oriented))                       dbchar_g2 e01_extract.py:294

The panel's ncRNA is published as DNA in the paper's own orientation, which need not be the
corpus orientation, so BOTH the sequence and its reverse complement are hashed and either is
accepted as an exact match (which orientation matched is recorded).

Near-sequence exposure on the ncRNA side is NOT recomputed here: it is read from the SPIRE
audit's existing blastn of the same 175 published ncRNAs against rt_ncrna_oriented_v1
(pubval/pub_vs_oriented.tsv), under that audit's own filter (>=90% identity, >=80% of the
published length, plus strand).

Exposure classes (one per panel row, most-exposed wins):
  TRAIN_EXPOSED            an exact pair/RT/ncRNA of this element is in the X1/X2 train fold
  VAL_TEST_EXPOSED         ... in the val or test fold (X1 held-out; X2 cross-fits all folds)
  COMPONENT_HELD_OUT       present in PAIR-ELIG but its component is not in the split table
  CATALOGUE_ONLY           RT and/or ncRNA in the corpus, but not as a PAIR-ELIG pair
  SEQUENCE_NEAR_CORPUS     no exact hash match, but a >=90%/>=80% blastn ncRNA match exists
  FULLY_EXTERNAL           no exact match and no near match in any project population

NOTE ON X2: embed_x2 cross-fits over ALL 1,075 components / 30,924 pairs, so for X2 there is
no untouched fold. Any element exposed to any fold is X2-exposed. This is recorded per row.
"""
import csv
import gzip
import hashlib
import json
import os
import sys

V7 = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
EMB = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings"
SPIRE = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-spire-ncrna"
SYN = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis"

K = "/home/borg/RESEARCH-retron-db/results/stage1_mestre_replication_and_insights/inputs/support.csv"
FAA = os.path.join(V7, "data/derived/rt_exact_v1.faa")
PAIRS = os.path.join(V7, "data/derived/rt_ncrna_exact_pairs_v1.parquet")
ORIENTED = os.path.join(V7, "data/derived/rt_ncrna_oriented_v1.parquet")
CALLS = os.path.join(V7, "data/derived/rt_ncrna_calls_v1.parquet")
SPLIT = os.path.join(EMB, "results/embed_g2b_frozen_split/tables/split_assignment.tsv.gz")
PUBVAL = os.path.join(SPIRE, "ARIS_OUTPUT/spire_ncrna_audit/pubval/pub_vs_oriented.tsv")
MESTRE = os.path.join(SYN, "references/rt0_rt7/mestre_2020/Mestre_supplementary_material.csv")

COMP = str.maketrans("ACGTNRYKMSWBDHVacgtnrykmswbdhv", "TGCANYRMKSWVHDBtgcanyrmkswvhdb")


def rt_hash(seq):
    s = (seq or "").upper()
    s = s[:-1] if s.endswith("*") else s
    return hashlib.sha256(s.encode()).hexdigest() if s else ""


def nc_hash(seq):
    s = (seq or "").upper()
    return hashlib.sha256(s.encode()).hexdigest() if s else ""


def revcomp(seq):
    return (seq or "").translate(COMP)[::-1]


def main():
    import pandas as pd

    # ---- panel -------------------------------------------------------------
    panel = pd.read_csv(K, encoding="utf-8-sig")
    panel["tid"] = panel["terminal_id"].astype(str).str.split(".").str[0]

    # ---- project populations ----------------------------------------------
    catalogue = set()
    with open(FAA) as fh:
        for line in fh:
            if line[0] == ">":
                catalogue.add(line[1:].strip().split()[0])
    pairs = pd.read_parquet(PAIRS, columns=["rt_seq_hash", "nc_seq_hash"])
    pair_set = set(zip(pairs.rt_seq_hash, pairs.nc_seq_hash))
    pair_rt = set(pairs.rt_seq_hash)
    pair_nc = set(pairs.nc_seq_hash)
    oriented = pd.read_parquet(ORIENTED, columns=["nc_seq_hash", "detection_model"])
    nc_model = dict(zip(oriented.nc_seq_hash, oriented.detection_model))
    calls_nc = set()
    try:
        c = pd.read_parquet(CALLS, columns=["nc_seq_hash"])
        calls_nc = set(c.nc_seq_hash.dropna())
    except Exception as exc:                                    # column name may differ
        print("WARN calls parquet:", exc, file=sys.stderr)

    # ---- X1/X2 split -------------------------------------------------------
    fold_by_pair, fold_by_rt, fold_by_nc, comp_by_pair = {}, {}, {}, {}
    with gzip.open(SPLIT, "rt") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            key = (r["rt_seq_hash"], r["nc_seq_hash"])
            fold_by_pair[key] = r["fold"]
            comp_by_pair[key] = r["component_id"]
            fold_by_rt.setdefault(r["rt_seq_hash"], set()).add(r["fold"])
            fold_by_nc.setdefault(r["nc_seq_hash"], set()).add(r["fold"])

    # ---- existing blastn near-match (not recomputed) -----------------------
    near = {}
    if os.path.exists(PUBVAL):
        with open(PUBVAL) as fh:
            for line in fh:
                f = line.rstrip("\n").split("\t")
                if len(f) < 9:
                    continue
                q, s = f[0], f[1]
                try:
                    pid, alen, qlen = float(f[2]), float(f[3]), float(f[4])
                except ValueError:
                    continue
                if pid >= 90.0 and alen >= 0.8 * qlen and f[8] == "plus":
                    tid = q.split("_")[1] if q.startswith("terminal_") else q
                    d = near.setdefault(tid, {"n": 0, "best_pid": 0.0, "subjects": set()})
                    d["n"] += 1
                    d["best_pid"] = max(d["best_pid"], pid)
                    d["subjects"].add(s)

    # ---- Mestre reference --------------------------------------------------
    mestre = {}
    with open(MESTRE, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    h = list(rows[0].keys())
    for r in rows:
        node = (r[h[0]] or "").strip()
        if node:
            mestre[node] = (r[h[1]].strip(), r[h[5]].strip(), r[h[6]].strip())

    out = []
    for i, r in enumerate(panel.itertuples(), start=1):
        tid = r.tid
        rt_aa = str(getattr(r, "rt_protein_aa") or "")
        nc = str(getattr(r, "ncRNA_sequence") or "")
        rtdna = str(getattr(r, "RTDNA_sequence") or "")

        rth = rt_hash(rt_aa) if rt_aa and rt_aa != "nan" else ""
        nch_fwd = nc_hash(nc) if nc and nc != "nan" else ""
        nch_rev = nc_hash(revcomp(nc)) if nc and nc != "nan" else ""

        nc_match, nc_orient = "", ""
        for cand, lab in ((nch_fwd, "as_published"), (nch_rev, "reverse_complement")):
            if cand and (cand in pair_nc or cand in nc_model or cand in calls_nc):
                nc_match, nc_orient = cand, lab
                break

        rt_in_cat = bool(rth) and rth in catalogue
        rt_in_pair = bool(rth) and rth in pair_rt
        nc_in_pair = bool(nc_match) and nc_match in pair_nc
        pair_key = (rth, nc_match) if rth and nc_match else None
        pair_exact = bool(pair_key) and pair_key in pair_set

        folds = set()
        if pair_key and pair_key in fold_by_pair:
            folds.add(fold_by_pair[pair_key])
        folds |= fold_by_rt.get(rth, set())
        folds |= fold_by_nc.get(nc_match, set())
        comp = comp_by_pair.get(pair_key, "") if pair_key else ""

        nr = near.get(tid)
        if "train" in folds:
            cls = "TRAIN_EXPOSED"
        elif folds & {"val", "test"}:
            cls = "VAL_TEST_EXPOSED"
        elif pair_exact:
            cls = "COMPONENT_HELD_OUT"
        elif rt_in_cat or nc_match:
            cls = "CATALOGUE_ONLY"
        elif nr:
            cls = "SEQUENCE_NEAR_CORPUS"
        else:
            cls = "FULLY_EXTERNAL"

        clade, acc, name = mestre.get(tid, ("", "", ""))
        prod = str(getattr(r, "rtdna_production_xeco1") or "")
        out.append({
            "panel_id": "EXP-K%03d" % i,
            "mestre_terminal_id": "terminal_%s" % tid,
            "element_name": name or str(getattr(r, "potential_abbreviation") or ""),
            "mestre_accession": acc,
            "mestre_rt_clade": clade,
            "in_mestre_reference_set": "YES" if acc else "NO",
            "rt_aa_len": str(getattr(r, "rt_protein_aa_length") or ""),
            "rt_seq_hash": rth,
            "rt_in_exact_rt_catalogue_501561": "YES" if rt_in_cat else "NO",
            "rt_in_PAIR_ELIG": "YES" if rt_in_pair else "NO",
            "ncrna_len_nt": str(getattr(r, "ncRNA_length") or ""),
            "ncrna_hash_matched": nc_match,
            "ncrna_match_orientation": nc_orient,
            "ncrna_in_oriented_16458": "YES" if (nc_match and nc_match in nc_model) else "NO",
            "ncrna_in_PAIR_ELIG": "YES" if nc_in_pair else "NO",
            "ncrna_production_CM_model": nc_model.get(nc_match, ""),
            "exact_pair_in_PAIR_ELIG": "YES" if pair_exact else "NO",
            "embed_split_component_id": comp,
            "embed_folds_touched": ",".join(sorted(folds)) if folds else "",
            "x1_heldout_status": ("TEST_FOLD" if "test" in folds else
                                  ("VAL_FOLD" if "val" in folds else
                                   ("TRAIN_FOLD" if "train" in folds else "NOT_IN_SPLIT"))),
            "x2_status": ("CROSSFIT_EXPOSED_ALL_FOLDS_TRAINED" if folds else "NOT_IN_SPLIT"),
            "blastn_near_hits_ge90id_ge80len": str(nr["n"]) if nr else "0",
            "blastn_best_identity": ("%.2f" % nr["best_pid"]) if nr else "",
            "exposure_class": cls,
            "usable_as_external_benchmark": (
                "NO_TRAIN_EXPOSED" if cls == "TRAIN_EXPOSED" else
                "NO_VAL_TEST_EXPOSED" if cls == "VAL_TEST_EXPOSED" else
                "CONDITIONAL_COMPONENT_LEVEL_ONLY" if cls == "COMPONENT_HELD_OUT" else
                "CONDITIONAL_CORPUS_OVERLAP" if cls == "CATALOGUE_ONLY" else
                "CONDITIONAL_NEAR_SEQUENCE" if cls == "SEQUENCE_NEAR_CORPUS" else
                "YES_SUPPORTABLE_AS_EXTERNAL"),
            "rtdna_sequence_present": "YES" if len(rtdna) > 3 and rtdna != "nan" else "NO",
            "rtdna_len_nt": str(getattr(r, "RTDNA_length") or ""),
            "rtdna_production_xEco1": prod,
            "human_editing_xEco1": str(getattr(r, "human_editing_xeco1") or ""),
            "bacterial_editing_xEco1": str(getattr(r, "bacterial_editing_xeco1") or ""),
            "phage_editing_xEco1": str(getattr(r, "phage_editing_xeco1") or ""),
        })

    cols = list(out[0].keys())
    dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "PANEL_LEAKAGE_MAP.tsv")
    with open(dest, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    from collections import Counter
    summary = {
        "panel_rows": len(out),
        "exposure_class": dict(Counter(o["exposure_class"] for o in out)),
        "rt_in_catalogue": sum(o["rt_in_exact_rt_catalogue_501561"] == "YES" for o in out),
        "rt_in_PAIR_ELIG": sum(o["rt_in_PAIR_ELIG"] == "YES" for o in out),
        "ncrna_exact_in_corpus": sum(bool(o["ncrna_hash_matched"]) for o in out),
        "ncrna_in_PAIR_ELIG": sum(o["ncrna_in_PAIR_ELIG"] == "YES" for o in out),
        "exact_pair_in_PAIR_ELIG": sum(o["exact_pair_in_PAIR_ELIG"] == "YES" for o in out),
        "x1_test_fold": sum(o["x1_heldout_status"] == "TEST_FOLD" for o in out),
        "x1_val_fold": sum(o["x1_heldout_status"] == "VAL_FOLD" for o in out),
        "x1_train_fold": sum(o["x1_heldout_status"] == "TRAIN_FOLD" for o in out),
        "not_in_split": sum(o["x1_heldout_status"] == "NOT_IN_SPLIT" for o in out),
        "blastn_near_ge90_ge80": sum(o["blastn_near_hits_ge90id_ge80len"] != "0" for o in out),
        "in_mestre_reference_set": sum(o["in_mestre_reference_set"] == "YES" for o in out),
        "rtdna_sequence_present": sum(o["rtdna_sequence_present"] == "YES" for o in out),
    }
    print(json.dumps(summary, indent=2))
    with open(dest.replace(".tsv", "_SUMMARY.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print("wrote", dest)


if __name__ == "__main__":
    main()
