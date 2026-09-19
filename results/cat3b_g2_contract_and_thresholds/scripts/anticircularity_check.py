#!/usr/bin/env python3
"""Anti-circularity checker — executable form of ANTICIRCULARITY_CONTRACT.tsv.

Refuses a detector module whose SOURCE references any forbidden input. Run with --selftest to
confirm the checker itself rejects a deliberately-bad module (a rule with no seeded-bad case has
not been validated).
"""
import re, sys, os
FORBIDDEN = {
 "motif regex":            r"\[YFWH\]|\[LIV\]|YADD|YXDD|YVDD|YIDD|YMDD|\bmotif\b",
 "RT0-RT7 / state coords": r"\bRT[0-7]\b|CAT_STATE|state_id|rtmap",
 "domain boundaries":      r"\bfingers\b|\bpalm\b|\bthumb\b|boundar",
 "family labels":          r"RVT-|\bretron\b|\bfamily\b|non-LTR|DRT\d",
 "Gate S":                 r"gateS|gate_s|GATE_S",
 "normalised position":    r"normali[sz]ed_position|rel_pos|frac_pos",
 "metal/ligand as input":  r"\bMG\b|\bMN\b|METAL_CAT|SUBSTRATE_NT|SUBSTRATE_NA|REACTION_PRODUCT|ligand",
 "truth leakage":          r"S_catalytic_asp|truth|TRUTH",
 "tier B leakage":         r"B_heldout|tier_b|TierB",
}
def check(path):
    src=open(path).read()
    src=re.sub(r'""".*?"""', "", src, flags=re.S)      # docstrings describe, they do not execute
    src=re.sub(r"#.*", "", src)
    bad=[]
    for name,pat in FORBIDDEN.items():
        m=re.search(pat, src)
        if m: bad.append(f"{name}: matched {m.group(0)!r}")
    return bad
def selftest():
    import tempfile
    good = os.path.join(os.path.dirname(os.path.abspath(__file__)), "detector.py")
    bad_src = "def predict(x):\n    if x.family == 'RVT-Retrons': return CAT_STATE\n    return None\n"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(bad_src); tmp=fh.name
    gb, bb = check(good), check(tmp)
    os.unlink(tmp)
    ok = (not gb) and len(bb) >= 2
    print(f"selftest: frozen detector clean = {not gb} ({gb}); seeded-bad module rejected = {len(bb)>=2} ({bb})")
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1
if __name__ == "__main__":
    if "--selftest" in sys.argv: sys.exit(selftest())
    t=sys.argv[1]; bad=check(t)
    print(("REJECT " + t + "\n  " + "\n  ".join(bad)) if bad else "ACCEPT " + t + " — no forbidden input referenced")
    sys.exit(1 if bad else 0)
