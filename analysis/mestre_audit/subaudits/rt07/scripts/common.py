"""Shared helpers for the rt07 forensic inventory. Read-only against all sources."""
from __future__ import annotations

import csv
import gzip
import hashlib
import os
import re
from collections import defaultdict
from pathlib import Path

MS = Path("/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences")
PRED = Path("/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/"
            "Supp_material_T1_R1_systematic_prediction.csv")
GAPS = set("-.~")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def dir_manifest(path: Path) -> tuple[int, int, str]:
    rows = []
    tot = 0
    for dp, _dn, fn in os.walk(path):
        for f in fn:
            p = Path(dp) / f
            if p.is_symlink() or not p.is_file():
                continue
            tot += p.stat().st_size
            rows.append(f"{p.relative_to(path)}\t{sha256(p)}")
    rows.sort()
    return len(rows), tot, hashlib.sha256("\n".join(rows).encode()).hexdigest()


def opener(path: Path):
    return gzip.open(path, "rt") if str(path).endswith(".gz") else open(path, errors="replace")


def read_fasta(path: Path) -> list[tuple[str, str]]:
    out, name, buf = [], None, []
    with opener(path) as fh:
        for line in fh:
            line = line.rstrip("\r\n")
            if line.startswith(">"):
                if name is not None:
                    out.append((name, "".join(buf)))
                name, buf = line[1:].strip(), []
            elif name is not None:
                buf.append(line.strip())
    if name is not None:
        out.append((name, "".join(buf)))
    return out


def read_stockholm(path: Path) -> tuple[list[tuple[str, str]], str]:
    seqs: dict[str, list[str]] = defaultdict(list)
    order: list[str] = []
    rf: list[str] = []
    with opener(path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("#=GC RF"):
                rf.append(line.split()[2])
            elif not line or line.startswith("#") or line.startswith("//"):
                continue
            else:
                p = line.split()
                if len(p) == 2:
                    if p[0] not in seqs:
                        order.append(p[0])
                    seqs[p[0]].append(p[1])
    return [(k, "".join(seqs[k])) for k in order], "".join(rf)


def read_any(path: Path):
    s = str(path)
    if s.endswith(".sto") or s.endswith(".sto.gz") or s.endswith(".stk"):
        return read_stockholm(path)[0]
    return read_fasta(path)


def ungap(s: str) -> str:
    return "".join(c for c in s if c not in GAPS).upper()


def load_mestre():
    """terminal id -> dict(seq, header, rescued, accession_on_disk); plus published accession by node."""
    node_acc = {}
    with open(PRED, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            try:
                node_acc[int(r["Node"])] = (r["Accesion"] or "").strip()
            except (ValueError, KeyError):
                pass
    ref = {}
    for d in MS.glob("terminal_*"):
        f = d / "protein_aminoacid.fasta"
        if not f.exists() or f.stat().st_size == 0:
            continue
        recs = read_fasta(f)
        if not recs:
            continue
        h, s = recs[0]
        tid = int(d.name.split("_")[1])
        parts = h.split("|")
        ref[tid] = {"seq": s.upper().rstrip("*"), "header": h, "rescued": h.endswith("|rescued"),
                    "disk_acc": "|".join(parts[1:-1] if h.endswith("|rescued") else parts[1:]),
                    "pub_acc": node_acc.get(tid, "")}
    return ref, node_acc


TERM = re.compile(r"terminal_(\d+)")


def build_index(ref):
    by_seq = defaultdict(set)
    by_name = {}
    for t, r in ref.items():
        by_seq[r["seq"]].add(t)
        by_name[f"terminal_{t}"] = t
        for k in (r["disk_acc"], r["pub_acc"]):
            if k:
                by_name.setdefault(k, t)
    return by_seq, by_name


def resolve(name: str, by_name) -> int | None:
    m = TERM.match(name)
    if m:
        return int(m.group(1))
    first = name.split()[0]
    if first in by_name:
        return by_name[first]
    return None
