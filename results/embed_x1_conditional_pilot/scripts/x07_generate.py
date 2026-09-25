#!/usr/bin/env python
"""embed_x1/x07 - generation analysis. DESCRIPTIVE ONLY. Run after likelihoods were frozen.

No claim of function. No ranking of generated RNA as biologically compatible. The only question
is whether RT conditioning changes the generated sequence distribution beyond generic and
type-level RNA grammar.
"""
from __future__ import annotations
import json, subprocess, sys
from collections import Counter
from pathlib import Path
import numpy as np, pandas as pd, torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x03_model import CondNcRNADecoder, PAD, BOS, EOS  # noqa: E402
from x04_train import load, SEED  # noqa: E402

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
INV = {3: "A", 4: "C", 5: "G", 6: "T", 7: "K", 8: "N", 9: "R", 10: "Y"}
N_RT, N_SAMP, TEMP, MAXLEN = 200, 4, 1.0, 400
RNAFOLD = "/home/borg/.local/bin/RNAfold"


@torch.no_grad()
def sample(model, arm, n, dev, type_id=None, rt_chunks=None, rt_mask=None, rng=None):
    tok = torch.full((n, 1), BOS, dtype=torch.long, device=dev)
    done = torch.zeros(n, dtype=torch.bool, device=dev)
    for _ in range(MAXLEN):
        b = {"tokens": torch.cat([tok, torch.full((n, 1), PAD, dtype=torch.long, device=dev)], 1)}
        if arm == "T": b["type_id"] = type_id
        if arm == "R": b["rt_chunks"], b["rt_mask"] = rt_chunks, rt_mask
        logits = model(b)["logits"][:, -1, :].float()
        logits[:, PAD] = -1e9; logits[:, BOS] = -1e9      # never emit pad or a second bos
        p = torch.softmax(logits / TEMP, -1)
        nxt = torch.multinomial(p, 1)
        nxt[done] = EOS
        tok = torch.cat([tok, nxt], 1)
        done |= (nxt.squeeze(1) == EOS)
        if bool(done.all()): break
    out = []
    for row in tok.cpu().numpy():
        s = []
        for t in row[1:]:
            if t == EOS: break
            s.append(INV.get(int(t), "N"))
        out.append("".join(s))
    return out


def kmer(seqs, k=3):
    c = Counter()
    for s in seqs:
        c.update(s[i:i+k] for i in range(len(s)-k+1))
    tot = sum(c.values()) or 1
    return {kk: v / tot for kk, v in c.items()}


def js(p, q):
    keys = set(p) | set(q)
    P = np.array([p.get(k, 0) for k in keys]); Q = np.array([q.get(k, 0) for k in keys])
    M = (P + Q) / 2
    def kl(a, b):
        m = a > 0
        return float((a[m] * np.log2(a[m] / np.maximum(b[m], 1e-12))).sum())
    return 0.5 * kl(P, M) + 0.5 * kl(Q, M)


def mfe(seqs):
    if not Path(RNAFOLD).exists() or not seqs: return None
    inp = "\n".join(seqs) + "\n"
    r = subprocess.run([RNAFOLD, "--noPS"], input=inp, capture_output=True, text=True)
    if r.returncode: return None
    vals = []
    for line in r.stdout.splitlines():
        if "(" in line and line.rstrip().endswith(")"):
            try: vals.append(float(line[line.rfind("(")+1:line.rfind(")")]))
            except ValueError: pass
    return vals or None


def main() -> int:
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    d, rt, rtm, rrow = load()
    te = np.where(d["fold"] == "test")[0]
    rng = np.random.default_rng(SEED)
    pick = rng.choice(te, size=min(N_RT, len(te)), replace=False)
    torch.manual_seed(SEED)

    train_nc = {d["nc_order"][r] for r in d["nc_row"][d["fold"] == "train"]}
    nc_seqs = {}
    for l in (TASK.parents[1] / "data/derived/rt_ncrna_oriented_v1.fna").read_text().splitlines():
        if l.startswith(">"): h = l[1:].split()[0]
        else: nc_seqs[h] = l.strip()
    train_seqs = {nc_seqs[h] for h in train_nc if h in nc_seqs}
    real_test = [nc_seqs[d["nc_hash"][i]] for i in te]

    gens, rows = {}, []
    for arm in ("U", "T", "R"):
        ck = torch.load(W / f"model_{arm}.pt", map_location=dev, weights_only=False)
        m = CondNcRNADecoder(arm).to(dev); m.load_state_dict(ck["state_dict"]); m.eval()
        allg, types = [], []
        for k in range(0, len(pick), 50):
            sel = pick[k:k+50]
            n = len(sel) * N_SAMP
            rep = np.repeat(sel, N_SAMP)
            kw = {}
            if arm == "T":
                kw["type_id"] = torch.from_numpy(d["type_id"][rep].astype(np.int64)).to(dev)
            if arm == "R":
                rows_ = np.array([rrow[h] for h in d["rt_hash"][rep]])
                kw["rt_chunks"] = torch.from_numpy(np.asarray(rt[rows_], np.float32)).to(dev)
                kw["rt_mask"] = torch.from_numpy(rtm[rows_]).to(dev)
            allg += sample(m, arm, n, dev, **kw)
            types += list(d["retron_type"][rep])
        gens[arm] = (allg, types)
        L = np.array([len(s) for s in allg])
        gc = np.array([(s.count("G") + s.count("C")) / max(len(s), 1) for s in allg])
        novel = sum(1 for s in allg if s not in train_seqs)
        f = mfe([s for s in allg if 10 < len(s) < 400][:400])
        rows.append(dict(arm=arm, n_samples=len(allg),
                         len_median=int(np.median(L)), len_p10=int(np.percentile(L, 10)),
                         len_p90=int(np.percentile(L, 90)), len_max=int(L.max()),
                         empty_or_degenerate=int((L < 10).sum()),
                         gc_mean=round(float(gc.mean()), 4), gc_sd=round(float(gc.std()), 4),
                         novel_vs_train=round(novel / len(allg), 4),
                         jsd_3mer_vs_real_test=round(js(kmer(allg), kmer(real_test)), 5),
                         mfe_median=round(float(np.median(f)), 2) if f else None,
                         mfe_n=len(f) if f else 0))
        print(f"  {arm}: n={len(allg)} len med {rows[-1]['len_median']} "
              f"GC {rows[-1]['gc_mean']:.3f} novel {rows[-1]['novel_vs_train']:.1%} "
              f"JSD(3-mer vs real) {rows[-1]['jsd_3mer_vs_real_test']:.5f} "
              f"MFE med {rows[-1]['mfe_median']}")

    L = np.array([len(s) for s in real_test])
    gc = np.array([(s.count("G")+s.count("C"))/max(len(s),1) for s in real_test])
    fr = mfe([s for s in real_test if 10 < len(s) < 400][:400])
    rows.append(dict(arm="REAL (test ncRNA)", n_samples=len(real_test),
                     len_median=int(np.median(L)), len_p10=int(np.percentile(L,10)),
                     len_p90=int(np.percentile(L,90)), len_max=int(L.max()),
                     empty_or_degenerate=0, gc_mean=round(float(gc.mean()),4),
                     gc_sd=round(float(gc.std()),4), novel_vs_train=None,
                     jsd_3mer_vs_real_test=0.0,
                     mfe_median=round(float(np.median(fr)),2) if fr else None,
                     mfe_n=len(fr) if fr else 0))
    print(f"  REAL: len med {rows[-1]['len_median']} GC {rows[-1]['gc_mean']:.3f} "
          f"MFE med {rows[-1]['mfe_median']}")

    # does R's output differ from T's beyond type-level grammar?
    cross = []
    for a, b in (("R", "T"), ("R", "U"), ("T", "U")):
        cross.append(dict(pair=f"{a} vs {b}",
                          jsd_3mer=round(js(kmer(gens[a][0]), kmer(gens[b][0])), 5)))
    print("  3-mer JSD between arms:", {c["pair"]: c["jsd_3mer"] for c in cross})

    pd.DataFrame(rows).to_csv(OUT / "x1_generation.tsv", sep="\t", index=False)
    pd.DataFrame(cross).to_csv(OUT / "x1_generation_between_arms.tsv", sep="\t", index=False)
    ex = {a: gens[a][0][:3] for a in ("U", "T", "R")}
    (OUT / "x1_generation_examples.json").write_text(json.dumps(
        dict(temperature=TEMP, n_rt=len(pick), n_per_rt=N_SAMP, examples=ex), indent=2) + "\n")
    print("\nwrote x1_generation.tsv, x1_generation_between_arms.tsv, x1_generation_examples.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
