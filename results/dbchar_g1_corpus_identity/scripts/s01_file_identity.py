#!/usr/bin/env python3
"""s01 - file identity: every entry of the corpus root, byte-level, no JSON parser.

For each regular file: bytes, mtime, mode, sha256, newline count, whether the last byte
is a newline, CRLF count. Non-.jsonl entries are listed, not parsed. Also pins the
schema document(s) the gate compares records against.

Census (WA-D.2): every byte of every file is read. Timings go to stdout only.
"""
from __future__ import annotations

import argparse
import hashlib
import multiprocessing as mp
import os
import stat
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from g1lib import write_tsv  # noqa: E402

READ_BYTES = 64 << 20  # DECLARED: read block; newline/CRLF counts are block-boundary safe below


def scan(path_s: str) -> dict:
    p = Path(path_s)
    st = p.lstat()
    row = {"entry": p.name, "kind": "other", "bytes": st.st_size,
           "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "mode": stat.filemode(st.st_mode), "sha256": "", "n_newlines": "",
           "ends_with_newline": "", "n_crlf": "", "seconds": 0.0}
    if stat.S_ISLNK(st.st_mode):
        row["kind"] = "symlink"
        return row
    if stat.S_ISDIR(st.st_mode):
        row["kind"] = "dir"
        return row
    if not stat.S_ISREG(st.st_mode):
        return row
    row["kind"] = "file"
    t0 = time.time()
    h = hashlib.sha256()
    n_nl = n_crlf = 0
    prev_last = b""
    last = b""
    with p.open("rb") as fh:
        while True:
            b = fh.read(READ_BYTES)
            if not b:
                break
            h.update(b)
            n_nl += b.count(b"\n")
            n_crlf += b.count(b"\r\n")
            if prev_last == b"\r" and b[:1] == b"\n":
                n_crlf += 1
            prev_last = b[-1:]
            last = b[-1:]
    row.update(sha256=h.hexdigest(), n_newlines=n_nl,
               ends_with_newline=(last == b"\n") if st.st_size else "", n_crlf=n_crlf,
               seconds=round(time.time() - t0, 2))
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--schema", action="append", default=[], help="schema document(s) to pin")
    ap.add_argument("--out", required=True)
    ap.add_argument("--procs", type=int, default=16)
    a = ap.parse_args()
    out = Path(a.out) / "tables"
    out.mkdir(parents=True, exist_ok=True)

    root = Path(a.corpus)
    entries = sorted(str(root / n) for n in os.listdir(root))
    t0 = time.time()
    big_first = sorted(entries, key=lambda s: -Path(s).lstat().st_size)
    with mp.Pool(min(a.procs, len(entries))) as pool:
        rows = {r["entry"]: r for r in pool.imap_unordered(scan, big_first)}
    cols = ["entry", "kind", "jsonl", "bytes", "mtime_utc", "mode", "sha256",
            "n_newlines", "ends_with_newline", "n_crlf"]
    write_tsv(out / "s01_file_identity.tsv", cols,
              [[rows[k]["entry"], rows[k]["kind"], rows[k]["entry"].endswith(".jsonl")] +
               [rows[k][c] for c in cols[3:]] for k in sorted(rows)])
    files = [r for r in rows.values() if r["kind"] == "file" and r["entry"].endswith(".jsonl")]
    write_tsv(out / "s01_corpus_root.tsv", ["quantity", "value"], [
        ["corpus_root", str(root)],
        ["n_entries", len(rows)],
        ["n_regular_jsonl_files", len(files)],
        ["n_non_jsonl_or_non_regular_entries", len(rows) - len(files)],
        ["total_jsonl_bytes", sum(r["bytes"] for r in files)],
        ["total_jsonl_newlines", sum(r["n_newlines"] for r in files)],
        ["n_jsonl_files_not_ending_in_newline", sum(1 for r in files if r["ends_with_newline"] is False)],
        ["n_jsonl_files_writable_by_anyone", sum(1 for r in files if "w" in r["mode"])],
        ["total_crlf", sum(r["n_crlf"] for r in files)],
    ])

    srows = []
    for s in a.schema:
        r = scan(s)
        srows.append([s, r["bytes"], r["sha256"]])
    shas = {r[2] for r in srows}
    write_tsv(out / "s01_schema_identity.tsv", ["path", "bytes", "sha256", "identical_to_all_listed"],
              [r + [len(shas) == 1] for r in srows])

    for k in sorted(rows, key=lambda k: -rows[k]["bytes"]):
        print(f"  {k:48s} {rows[k]['bytes']:>14,d} B {rows[k]['seconds']:>7}s")
    print(f"s01 wall_seconds (stdout only): {time.time() - t0:.1f}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
