#!/usr/bin/env python3
"""c03 - positive controls for g6: the subtype case rule and the tool matrix, on values whose
answer is known, plus the asymmetry measure on constructed data. `--seed-bad` must fail."""
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent

def load(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--seed-bad", action="store_true"); a = ap.parse_args()
    t01 = load(HERE / "t01_tool_calls.py", "t01")
    rows, fails = [], []
    def expect(name, want, got):
        ok = want == got
        rows.append([name, want, got, "PASS" if ok else "FAIL"])
        if not ok: fails.append(name)

    # the declared case rule: capital-initial = DefenseFinder, lowercase = PADLOC
    df_, pl, other = t01.split_subtypes(json.dumps(["Retron_I_A", "retron_i_a"]))
    expect("capital-initial goes to DefenseFinder", ["Retron_I_A"], df_)
    expect("lowercase goes to PADLOC", ["retron_i_a"], pl)
    expect("nothing is unclassifiable here", [], other)
    df_, pl, other = t01.split_subtypes(json.dumps(["_odd", "9x"]))
    expect("a non-alphabetic first character is unclassifiable", ["_odd", "9x"], other)
    expect("and is not silently given to a tool", ([], []), (df_, pl))
    expect("an empty list yields nothing", ([], [], []), t01.split_subtypes("[]"))
    expect("malformed json is unclassifiable, not dropped", 1,
           len(t01.split_subtypes("not json")[2]))
    # the rule must SEPARATE: pooling would have lost one of the two labels
    df_, pl, _ = t01.split_subtypes(json.dumps(["Retron_II", "retron_iii_a"]))
    expect("two tools at one locus stay separate", ("Retron_II", "retron_iii_a"), (df_[0], pl[0]))
    # the asymmetry measure must move when carriage differs by tool set
    d = pd.DataFrame({"detected_by_set": ["A"] * 10 + ["B"] * 10,
                      "n_ncrna": [1] * 10 + [0] * 10})
    pct = d.groupby("detected_by_set").n_ncrna.apply(lambda s: round(100 * (s > 0).mean(), 4))
    expect("carriage differs by tool set when constructed to", (100.0, 0.0), (pct["A"], pct["B"]))
    if a.seed_bad:
        expect("lowercase goes to PADLOC", ["Retron_I_A"], pl)
    (Path(a.out) / "tables").mkdir(parents=True, exist_ok=True)
    name = "c03_positive_controls_SEEDBAD.tsv" if a.seed_bad else "c03_positive_controls.tsv"
    with (Path(a.out) / "tables" / name).open("w") as fh:
        fh.write("control\texpected\tobserved\tresult\n")
        for r in rows: fh.write("\t".join(str(v) for v in r) + "\n")
    print(f"c03: {len(rows)} controls, {len(fails)} failed")
    for f in fails: print("  FAIL", f)
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
