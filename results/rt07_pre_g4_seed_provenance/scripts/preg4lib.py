#!/usr/bin/env python3
"""Shared code for the pre-g4 seed-provenance audit.

Comparator populations are READ here for one purpose only: to measure how much of the old
seed reappears in them. That is a leakage measurement, not a definitional use, and it does
not make Toro, Mestre or myRT available to seed anything (launcher 5d). The distinction is
recorded on every table this bundle lands.
"""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

PROJ = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7")
BUNDLE_CONTROL = Path(__file__).resolve().parents[1] / "control"
V3 = Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT")
V4 = Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT")
ENV = Path("/home/borg/miniconda3/envs/retron_tradicional/bin")

# population id -> (path, kind, why it is in the audit)
POPULATIONS = {
    "align000044": (PROJ / "data/derived/rt07_external_assets/ALIGN_000044.aln", "clustal",
                    "the historical reconstruction substrate; overlap here would mean the "
                    "old seed and the new frame share sequences"),
    "toro742": (PROJ / "references/rt0_rt7/historical/toro_2014_Rt0-Rt7.FASTA", "fasta",
                "published comparator; read ONLY to measure overlap, never to define"),
    "myrt1844": (PROJ / "references/rt0_rt7/myrt/myRT-FastTree2.refpkg/RVT-ref.fst", "fasta",
                 "published comparator; read ONLY to measure overlap"),
    "gold171": (V4 / "D_instrument/cache/sets/gold175_uniq.faa", "fasta",
                "the retron literature challenge panel"),
    "anchors72": (V4 / "D_instrument/cache/sets/anchors72.faa", "fasta",
                  "the anchor set, which is inside the seed by construction"),
    "stage1_exact_rt": (PROJ / "data/derived/rt_exact_v1.faa", "fasta",
                        "the frozen Stage-1 catalogue g4 will sample from"),
}
IDENTITY_BINS = [1.0, 0.9, 0.7, 0.5, 0.3]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def seq_hash(s: str) -> str:
    return hashlib.sha256(re.sub(r"[^A-Za-z]", "", s).upper().encode()).hexdigest()


def read_fasta(p: Path) -> dict[str, str]:
    out, name, buf = {}, None, []
    with p.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith(">"):
                if name:
                    out[name] = "".join(buf)
                name, buf = line[1:].split()[0], []
            else:
                buf.append(line.strip())
    if name:
        out[name] = "".join(buf)
    return out


def read_clustal(p: Path) -> dict[str, str]:
    out: dict[str, list[str]] = {}
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        if not line.strip() or line.startswith(" "):
            continue
        parts = line.split()
        if len(parts) == 2:
            out.setdefault(parts[0], []).append(parts[1])
    return {k: "".join(v) for k, v in out.items()}


def load_population(pid: str) -> dict[str, str]:
    path, kind, _ = POPULATIONS[pid]
    raw = read_clustal(path) if kind == "clustal" else read_fasta(path)
    return {k: re.sub(r"[^A-Za-z]", "", v).upper() for k, v in raw.items()}


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
