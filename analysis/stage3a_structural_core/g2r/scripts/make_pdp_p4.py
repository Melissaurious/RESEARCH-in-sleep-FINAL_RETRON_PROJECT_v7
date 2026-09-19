#!/usr/bin/env python3
"""Build the SENSITIVITY-ONLY PDP variant "BJ-p4" (g2r amendment 1, F1).

Takes the BioJava 7.1.4 sources (sources jar sha1 0b9f0ffa413b3a0c1a7b5410b172eaa375dd43e6) and applies exactly
four index/typo corrections that have one unambiguous reading. Nothing else is changed; no constant is touched.
The primary instrument remains the unmodified 7.1.4 jar. Every edit asserts the original text first.

Usage: make_pdp_p4.py <biojava_src_root> <out_src_root>
"""
import sys, os

src, out = sys.argv[1], sys.argv[2]
PDP = "org/biojava/nbio/structure/domain/pdp"
EDITS = {
    "Cut.java": [
        (73, "size1t+=(dom.getSegmentAtPos(jseg).getFrom() - dom.getSegmentAtPos(jseg).getFrom() + 1);",
             "size1t+=(dom.getSegmentAtPos(jseg).getTo() - dom.getSegmentAtPos(jseg).getFrom() + 1);"),
        (82, "to2 = dom.getSegmentAtPos(kseg).getFrom();",
             "to2 = dom.getSegmentAtPos(kseg).getTo();"),
        (370, "if(size1>150) max_contacts[k] = 9*x*y;",
              "if(size1>150) max_contacts[nc] = 9*x*y;"),
    ],
    "CutDomain.java": [
        (133, "dom2.getSegmentAtPos(dom1.nseg).setTo(", "dom2.getSegmentAtPos(dom2.nseg).setTo("),
        (134, "dom2.getSegmentAtPos(dom1.nseg).setFrom(", "dom2.getSegmentAtPos(dom2.nseg).setFrom("),
    ],
}
os.makedirs(f"{out}/{PDP}", exist_ok=True)
for fn, edits in EDITS.items():
    lines = open(f"{src}/{PDP}/{fn}").read().split("\n")
    for ln, old, new in edits:
        assert old in lines[ln - 1], (fn, ln, lines[ln - 1])
        lines[ln - 1] = lines[ln - 1].replace(old, new)
        print(f"{fn}:{ln}  {old.strip()}  ->  {new.strip()}")
    open(f"{out}/{PDP}/{fn}", "w").write("\n".join(lines))
