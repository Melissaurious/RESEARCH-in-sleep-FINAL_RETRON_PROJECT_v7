#!/usr/bin/env python3
"""Shared code for rt07_g3_prior_method_replication.

g3 audits prior work. The rule that shapes every function here: a prior number is evidence
of what a prior run produced, never an acceptance criterion for this one (launcher 5d). So
nothing in this module compares a new measurement against a prior value to decide whether
the new measurement is right; it computes the new measurement and records both.

Sequence identity is by sha256 of the ungapped, uppercased amino-acid string. That is the
only identifier that survives across projects: accessions, ids and file names were all
reassigned between project versions, and matching on them is how a seed member reappears in
a validation set without anyone noticing.
"""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[1]
PROJ = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7")
V4 = Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT")
G2 = PROJ / "results/rt07_g2_reference_reconstruction"
G1 = PROJ / "results/rt07_g1_history_and_definition"
ENV = Path("/home/borg/miniconda3/envs/retron_tradicional/bin")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def seq_hash(s: str) -> str:
    """The cross-project identity of a protein: hash of its residues, nothing else."""
    return hashlib.sha256(re.sub(r"[^A-Za-z]", "", s).upper().encode()).hexdigest()


def read_fasta(p: Path) -> dict[str, str]:
    out, name, buf = {}, None, []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(">"):
            if name:
                out[name] = "".join(buf)
            name, buf = line[1:].split()[0], []
        else:
            buf.append(line.strip())
    if name:
        out[name] = "".join(buf)
    return out


def fasta_hashes(p: Path) -> dict[str, str]:
    """id -> sequence hash, streamed so a 230 MB catalogue does not need to fit in memory."""
    out, name, buf = {}, None, []
    with p.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith(">"):
                if name:
                    out[name] = seq_hash("".join(buf))
                name, buf = line[1:].split()[0], []
            else:
                buf.append(line.strip())
    if name:
        out[name] = seq_hash("".join(buf))
    return out


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


def resolve(rel: str) -> Path:
    """Control tables may carry a path relative to the V4 tree or an absolute one.

    The prior work is spread across two project versions - the models that every prior
    number was computed on live in V3, while the tables live in V4 - so a single root would
    silently drop half the evidence.
    """
    p = Path(rel)
    return p if p.is_absolute() else V4 / rel


def control(name: str) -> list[dict[str, str]]:
    return read_tsv(BUNDLE / "control" / name)


def hmm_header(p: Path) -> dict[str, str]:
    """NAME / LENG / NSEQ etc. as the file itself declares them."""
    out = {}
    with p.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("HMM "):
                break
            m = re.match(r"^(\w+)\s+(.+?)\s*$", line)
            if m:
                out.setdefault(m.group(1), m.group(2))
    return out


def jaccard(a: tuple[int, int], b: tuple[int, int]) -> float:
    """Overlap of two closed residue intervals."""
    lo, hi = max(a[0], b[0]), min(a[1], b[1])
    inter = max(0, hi - lo + 1)
    union = (a[1] - a[0] + 1) + (b[1] - b[0] + 1) - inter
    return inter / union if union else 0.0


def g2_blocks() -> list[dict]:
    """The independently reconstructed g2 regions, in LtrA residue coordinates."""
    return [r for r in read_tsv(G2 / "tables/g2_ltra_mapping.tsv")]
