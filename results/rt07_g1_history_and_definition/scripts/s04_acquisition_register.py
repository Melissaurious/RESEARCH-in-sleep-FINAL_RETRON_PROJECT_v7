#!/usr/bin/env python3
"""rt07_g1 step 4 - the acquisition and source-resolution register (launcher 7c, 9a, 9c).

`ALIGN_000044` was approved for governed acquisition during this gate. It was acquired.
This step is what turns downloaded bytes into evidence: it verifies the cached files
against the hashes recorded at retrieval, lands one register row per asset and per attempt
- including the attempts that FAILED, because a route that returned HTTP 200 carrying an
error string is the kind of thing that later gets mistaken for data - and measures what the
record actually contains rather than repeating what the paper says about it.

The register keeps the two states apart deliberately: ACQUIRED_VERIFIED means the bytes are
here and hash as recorded; USABLE_AS_EVIDENCE additionally means this row exists. A file in
the cache with no row is not evidence. If retrieval had failed, the row would read
MISSING_PRIMARY_ASSET and the gate would continue without a substitute.

This script does NOT re-download. Reproduction must not depend on a remote host still
answering, so rerunning verifies the cache; --acquire is the one-time fetch path and is not
called by run.sh.

Writes (under --out): g1_acquisition_source_resolution.tsv, g1_derived_registry.tsv,
                      g1_align000044_record_summary.tsv
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g1lib import (ACQUIRED, control, embl_prose, normalise, sha256,  # noqa: E402
                       write_tsv)


def record_summary(dat: Path) -> list[dict]:
    """Measure the alignment record. Every value here is read off the file."""
    # Line-code fields (ID, SO, RL) are read from the RAW record, because the code IS the
    # field marker; wrapped prose (the CC block) is read from the stripped rendering,
    # because there the code is what breaks the sentence. Using one text for both is how
    # the alignment summary silently read PARSE_FAILED the first time.
    raw = dat.read_text(encoding="utf-8", errors="replace")
    text = embl_prose(raw)
    head = re.search(r"^ID\s+(\S+);\s*(\w+);\s*(\d+)\s+symbols\s+\((\d+)\s+sequences\)",
                     raw, re.M)
    # Whitespace-collapsed, or a domain name wrapped across two lines is invisible to the
    # character class and the record reads as having one domain instead of three.
    dom = re.findall(r"a ([a-z ()/]+?) domain \(residues (\d+)-(\d+)\)", normalise(text))
    subdomain_hits = len(re.findall(r"\b(?:sub)?domains?\s+[0-7]\b|\bRT-?[0-7]\b",
                                    normalise(text), re.I))
    rows = [
        {"quantity": "accession", "value": head.group(1) if head else "PARSE_FAILED",
         "read_from": "ID line"},
        {"quantity": "molecule_type", "value": head.group(2) if head else "PARSE_FAILED",
         "read_from": "ID line"},
        {"quantity": "alignment_columns", "value": head.group(3) if head else "PARSE_FAILED",
         "read_from": "ID line"},
        {"quantity": "n_sequences", "value": head.group(4) if head else "PARSE_FAILED",
         "read_from": "ID line"},
        {"quantity": "n_sequence_rows_listed",
         "value": str(len(re.findall(r"^SO\s+\d+\s+", raw, re.M))), "read_from": "SO lines"},
        {"quantity": "submission_date",
         "value": (re.search(r"Submitted \((\d{2}-\w{3}-\d{4})\)", raw) or
                   re.search(r"(NOT_FOUND)", "NOT_FOUND")).group(1), "read_from": "RL line"},
        {"quantity": "alignment_method",
         "value": (re.search(r"ALIGNMENT METHOD:\s*(.+)", text) or
                   re.search(r"(PARSE_FAILED)", "PARSE_FAILED")).group(1).strip(),
         "read_from": "CC block"},
        {"quantity": "n_annotated_domains", "value": str(len(dom)), "read_from": "CC block"},
        {"quantity": "n_numbered_subdomain_annotations", "value": str(subdomain_hits),
         "read_from": "whole record; the detector that finds this is validated in step 2"},
    ]
    for name, start, end in dom:
        rows.append({"quantity": f"annotated_domain:{name.strip().replace(' ', '_')}",
                     "value": f"{start}-{end}", "read_from": "CC block"})
    for r in rows:
        r.update({"unit": "alignment record field",
                  "denominator": "n/a - single primary record, values read not derived",
                  "frame": "EMBL-Align flat file ALIGN_000044, as archived"})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--acquire", action="store_true",
                    help="one-time governed fetch; run.sh never uses this")
    args = ap.parse_args()

    assets = control("acquired_assets.tsv")
    attempts = control("acquisition_attempts.tsv")

    if args.acquire:
        import urllib.request
        ACQUIRED.mkdir(parents=True, exist_ok=True)
        for a in assets:
            dest = ACQUIRED / a["file_name"]
            if dest.is_file() and sha256(dest) == a["expected_sha256"]:
                continue
            urllib.request.urlretrieve(a["source_url"], dest)
        print(f"acquired {len(assets)} file(s) into {ACQUIRED}")

    register, problems = [], []
    for a in assets:
        p = ACQUIRED / a["file_name"]
        if not p.is_file():
            state, obs_sha, obs_bytes = "MISSING_PRIMARY_ASSET", "ABSENT", "0"
            problems.append(f"{a['file_name']}: absent from the governed cache")
        else:
            obs_sha, obs_bytes = sha256(p), str(p.stat().st_size)
            ok = (obs_sha == a["expected_sha256"] and obs_bytes == a["expected_bytes"])
            state = "ACQUIRED_VERIFIED" if ok else "ACQUIRED_HASH_MISMATCH"
            if not ok:
                problems.append(f"{a['file_name']}: hash or size differs from retrieval")
        register.append({
            "asset_id": a["asset_id"], "file_name": a["file_name"],
            "resolution_state": state,
            "usable_as_evidence": "YES" if state == "ACQUIRED_VERIFIED" else "NO",
            "cache_path": str(p.relative_to(p.parents[3])) if p.is_file() else "NOT_ACQUIRED",
            "source_url": a["source_url"], "archive_authority": a["archive_authority"],
            "retrieval_date_utc": a["retrieval_date_utc"],
            "archive_last_modified": a["archive_last_modified"],
            "access_conditions": a["access_conditions"], "licence_state": a["licence_state"],
            "bytes": obs_bytes, "sha256": obs_sha,
            "sha256_matches_retrieval": "YES" if obs_sha == a["expected_sha256"] else "NO",
            "acquired_by_attempt": a["acquired_by_attempt"],
            "written_into_references_package": "NO - references/rt0_rt7/ is read-only to "
                                               "this track (launcher 9c)",
            "unit": "externally acquired file",
            "denominator": f"{len(assets)} file(s) approved for governed acquisition",
        })

    for t in attempts:
        register.append({
            "asset_id": t["asset_id"], "file_name": f"attempt {t['attempt_id']}",
            "resolution_state": t["outcome"],
            "usable_as_evidence": "NO - attempt record, not an asset",
            "cache_path": "n/a", "source_url": t["endpoint"],
            "archive_authority": t["archive_authority"],
            "retrieval_date_utc": t["retrieval_date_utc"],
            "archive_last_modified": "n/a", "access_conditions": f"HTTP {t['http_code']}",
            "licence_state": "n/a", "bytes": t["bytes"], "sha256": "n/a",
            "sha256_matches_retrieval": "n/a", "acquired_by_attempt": t["attempt_id"],
            "written_into_references_package": "NO",
            "unit": "acquisition attempt",
            "denominator": f"{len(attempts)} attempts made or declined in this gate",
        })

    dat = ACQUIRED / "ALIGN_000044.dat"
    summary = record_summary(dat) if dat.is_file() else []

    derived = [{
        "dataset": f"data/derived/rt07_external_assets/{a['file_name']}",
        "bytes": r["bytes"], "sha256": r["sha256"],
        "rows": "n/a - flat file", "content_key": a["asset_id"],
        "content_digest_sha256": r["sha256"],
        "registered_by": "results/rt07_g1_history_and_definition",
        "unit": "acquired primary asset",
        "denominator": "assets landed in the governed acquisition cache by this gate",
    } for a, r in zip(assets, register) if r["resolution_state"] == "ACQUIRED_VERIFIED"]

    write_tsv(args.out / "g1_acquisition_source_resolution.tsv",
              ["asset_id", "file_name", "resolution_state", "usable_as_evidence",
               "cache_path", "source_url", "archive_authority", "retrieval_date_utc",
               "archive_last_modified", "access_conditions", "licence_state", "bytes",
               "sha256", "sha256_matches_retrieval", "acquired_by_attempt",
               "written_into_references_package", "unit", "denominator"], register)
    write_tsv(args.out / "g1_derived_registry.tsv",
              ["dataset", "bytes", "sha256", "rows", "content_key",
               "content_digest_sha256", "registered_by", "unit", "denominator"], derived)
    write_tsv(args.out / "g1_align000044_record_summary.tsv",
              ["quantity", "value", "read_from", "unit", "frame", "denominator"], summary)

    for p in problems:
        print(f"FAIL {p}", file=sys.stderr)
    print(f"register rows: {len(register)} "
          f"({len(assets)} asset(s), {len(attempts)} attempt(s))")
    print(f"acquired and verified: {sum(1 for r in register if r['resolution_state'] == 'ACQUIRED_VERIFIED')}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
