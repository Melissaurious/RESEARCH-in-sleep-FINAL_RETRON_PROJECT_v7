#!/usr/bin/env python3
"""Shared helpers for rt07_g1_history_and_definition.

Text normalisation lives here because every step depends on it being the same text.
A quote that verifies against one normalisation and fails against another is not a
verified quote, so the rule is written once: NFKC, ligatures expanded, every dash form
folded to '-', horizontal whitespace collapsed. Line breaks become single spaces so that
a sentence broken across a PDF column still matches the sentence as a human reads it.

Nothing here reads a comparator. g1's evidence set is the derivational primary literature
plus the acquired primary alignment (launcher 5d); Tier-2 assets may not seed it.
"""
from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[1]
PROJ = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7")
REGISTER = PROJ / "references/rt0_rt7/RESOURCE_REGISTER.tsv"
ACQUIRED = PROJ / "data/derived/rt07_external_assets"

LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi",
             "ﬄ": "ffl", "ﬅ": "st", "ﬆ": "st"}
DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−"), "-")
QUOTES = dict.fromkeys(map(ord, "‘’‛"), "'") | \
         dict.fromkeys(map(ord, "“”"), '"')


def normalise(s: str) -> str:
    """The one text normalisation this gate uses. See module docstring."""
    s = unicodedata.normalize("NFKC", s)
    for lig, rep in LIGATURES.items():
        s = s.replace(lig, rep)
    s = s.translate(DASHES).translate(QUOTES)
    return re.sub(r"\s+", " ", s).strip()


EMBL_LINE_CODE = re.compile(r"^(?:[A-Z]{2}|//)(?:\s{2,}|\s*$)", re.M)


def embl_prose(s: str) -> str:
    """Strip EMBL flat-file line-type codes (ID, AC, CC, XX, SO, //) from a record.

    The codes are line structure, not content: without stripping them, a sentence wrapped
    across two CC lines reads as '... a reverse CC transcriptase domain ...' and no quote
    of it can verify. This was caught by the alignment-annotation positive control, which
    read zero on a record that plainly names the domain it annotates.
    """
    return EMBL_LINE_CODE.sub("", s)


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
    """One writer, so every landed table has the same shape and byte layout."""
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(c, "")).replace("\t", " ").replace("\n", " ")
                               for c in cols) + "\n")


def register() -> dict[str, dict[str, str]]:
    return {r["asset_id"]: r for r in read_tsv(REGISTER)}


def multi(field: str) -> list[str]:
    """Pipe-separated region lists in the control tables."""
    return [x for x in (p.strip() for p in field.split("|")) if x]


def control(name: str) -> list[dict[str, str]]:
    return read_tsv(BUNDLE / "control" / name)
