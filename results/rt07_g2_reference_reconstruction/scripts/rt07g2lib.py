#!/usr/bin/env python3
"""Shared code for rt07_g2_reference_reconstruction.

The substrate is ALIGN_000044 - the alignment Zimmerly 2001 adjusted its inherited
subdomain labels against - acquired and hash-verified in rt07_g1. Nothing here reads a
comparator: no Toro, no Mestre, no myRT, no SPIRE, no prior project boundary, HMM or anchor
set. Those belong to g3 and later gates, and a reconstruction that consulted them would
agree with them by construction.
"""
from __future__ import annotations

import csv
import hashlib
import re
from collections import OrderedDict
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[1]
PROJ = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7")
ACQUIRED = PROJ / "data/derived/rt07_external_assets"
G1 = PROJ / "results/rt07_g1_history_and_definition"

# Chemical similarity classes for the 'identical or chemically similar' reading of the
# criterion. Standard physico-chemical groupings; declared here, not tuned per column.
SIMILARITY_CLASSES = ["AGST", "ILMVF", "KRH", "DENQ", "CP", "WY"]
CLASS_OF = {aa: i for i, cls in enumerate(SIMILARITY_CLASSES) for aa in cls}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(p: Path) -> list[dict[str, str]]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(p: Path, cols: list[str], rows: list[dict]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(c, "")).replace("\t", " ").replace("\n", " ")
                               for c in cols) + "\n")


def control(name: str) -> list[dict[str, str]]:
    return read_tsv(BUNDLE / "control" / name)


def parse_clustal(p: Path) -> "OrderedDict[str, str]":
    """Parse the CLUSTAL W alignment as submitted. No reformatting, no trimming."""
    seqs: "OrderedDict[str, list[str]]" = OrderedDict()
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        if not line.strip() or line.startswith(" "):
            continue
        parts = line.split()
        if len(parts) != 2:
            continue
        seqs.setdefault(parts[0], []).append(parts[1])
    return OrderedDict((k, "".join(v)) for k, v in seqs.items())


def parse_descriptions(dat: Path) -> dict[str, str]:
    """abbreviation -> description, from the record's own SO lines."""
    out = {}
    for m in re.finditer(r"^SO\s+\d+\s+(\S+)\s+(\S+)\s+(.+?)\s*$",
                         dat.read_text(encoding="utf-8", errors="replace"), re.M):
        out[m.group(1)] = f"{m.group(3)} [{m.group(2)}]"
    return out


def assign_groups(desc: dict[str, str], rules: list[dict]) -> dict[str, tuple[str, str]]:
    """name -> (group, rule_id). First matching rule by declared priority wins."""
    ordered = sorted(rules, key=lambda r: int(r["priority"]))
    out = {}
    for name, d in desc.items():
        for r in ordered:
            if re.search(r["pattern"], d):
                out[name] = (r["group"], r["rule_id"])
                break
        else:
            out[name] = ("UNASSIGNED", "none")
    return out


def conserved_columns(seqs: dict[str, str], groups: dict[str, str], *,
                      threshold: float, min_groups: int, similarity: bool,
                      group_names: list[str]) -> list[dict]:
    """Apply the Xiong & Eickbush criterion, column by column.

    A group is satisfied at a column when more than `threshold` of THAT GROUP'S SEQUENCES
    (gaps included in the denominator) carry the group's modal residue - or, in the
    similarity reading, a residue from the modal residue's chemical class. A column is
    conserved when at least `min_groups` groups are satisfied.
    """
    names = list(seqs)
    ncol = len(next(iter(seqs.values())))
    members = {g: [n for n in names if groups.get(n) == g] for g in group_names}
    rows = []
    for c in range(ncol):
        sat, detail = 0, []
        for g in group_names:
            mem = members[g]
            if not mem:
                detail.append(f"{g}:no_members")
                continue
            counts: dict[str, int] = {}
            for n in mem:
                a = seqs[n][c]
                if a == "-":
                    continue
                key = str(CLASS_OF.get(a, -1)) if similarity else a
                counts[key] = counts.get(key, 0) + 1
            if not counts:
                detail.append(f"{g}:0.00")
                continue
            best = max(counts.values())
            frac = best / len(mem)
            if frac > threshold:
                sat += 1
            detail.append(f"{g}:{frac:.2f}")
        rows.append({"column": c + 1, "n_groups_satisfied": sat,
                     "conserved": sat >= min_groups, "per_group_fraction": "|".join(detail)})
    return rows


def blocks_from(columns: list[int], max_gap: int, min_size: int) -> list[tuple[int, int, int]]:
    """Merge conserved columns into blocks. Returns (start, end, n_conserved)."""
    if not columns:
        return []
    out, run = [], [columns[0]]
    for c in columns[1:]:
        if c - run[-1] - 1 <= max_gap:
            run.append(c)
        else:
            out.append(run)
            run = [c]
    out.append(run)
    return [(r[0], r[-1], len(r)) for r in out if len(r) >= min_size]


def col_to_residue(seq: str) -> dict[int, int]:
    """Alignment column (1-based) -> ungapped residue number for one sequence."""
    out, k = {}, 0
    for i, a in enumerate(seq, start=1):
        if a != "-":
            k += 1
            out[i] = k
    return out
