#!/usr/bin/env python3
"""Pre-freeze check that an implementation will actually produce its required artefacts.

WHY THIS EXISTS
    T-A23d ran its science to completion -- 19/19 controls PASS, TASK_STATE: PASS, five
    primary tables, a verified manifest and a run log -- and was still VOIDed as
    ARTIFACT_INVALID, because the frozen implementation contained ZERO references to
    TASK_REPORT.md. Nobody noticed until after the compute was spent.

    That is a machine-checkable defect. This module checks it BEFORE freeze, so an
    implementation that cannot satisfy the traceability contract never reaches execution.

WHAT IT CHECKS
    Statically, over the task's own frozen sources: does the code reference and write each
    required artefact? Plus, when the launcher declares primary tables, are those named too?

WHAT IT CANNOT CHECK
    That the artefact is CORRECT -- only that the implementation is capable of emitting it.
    A static check cannot prove a runtime path is taken. It is a floor, not a guarantee: the
    worker still verifies the artefacts actually exist after the run.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

#: Every task must emit these, per review-stage/TASK_PROTOCOL.md.
REQUIRED = ("TASK_REPORT.md", "OUTPUT_MANIFEST.sha256", "run_log.json")
#: TASK_REPORT.md must carry these machine-read lines, or parse_task_report refuses it.
REQUIRED_REPORT_FIELDS = ("TASK_STATE", "SCIENTIFIC_OUTCOME")


def _output_prefix(task_dir_name: str) -> str:
    """`T-A23d-primary-verification` -> `a23d_`; the prefix its own tables carry."""
    m = re.match(r"T-([A-Za-z0-9]+)", task_dir_name)
    return f"{m.group(1).lower()}_" if m else ""


def _sources(task_dir: Path) -> list[Path]:
    return sorted(p for p in task_dir.rglob("*.py")
                  if "__pycache__" not in p.parts and p.is_file())


def _writes_something(text: str) -> bool:
    """Does this file appear to write files at all?"""
    return bool(re.search(r"\.write_text\(|\bopen\(|\.to_csv\(|csv\.writer|\.write\(", text))


def check(task_dir: Path, launcher: Path | None = None) -> tuple[bool, list[dict]]:
    checks: list[dict] = []

    def add(name, ok, detail=""):
        checks.append({"check": name, "result": "PASS" if ok else "FAIL", "detail": str(detail)})
        return ok

    srcs = _sources(task_dir)
    add("implementation_present", bool(srcs), f"{len(srcs)} python file(s)")
    blob = "\n".join(p.read_text(errors="replace") for p in srcs) if srcs else ""

    for art in REQUIRED:
        named = art in blob
        add(f"emits:{art}", named,
            "referenced by the implementation" if named
            else f"NO source under {task_dir.name} mentions {art}; the run would be ARTIFACT_INVALID")

    # The report's machine-read fields must be produced, not just the filename mentioned.
    if "TASK_REPORT.md" in blob:
        for field in REQUIRED_REPORT_FIELDS:
            add(f"report_field:{field}", field in blob,
                "written by the implementation" if field in blob
                else f"TASK_REPORT.md is written but {field}: is never emitted; parse_task_report would refuse it")

    add("writes_files", _writes_something(blob), "implementation performs file writes")

    # Syntactic validity: a file that cannot compile cannot emit anything.
    bad = []
    for p in srcs:
        try:
            ast.parse(p.read_text(errors="replace"))
        except SyntaxError as exc:
            bad.append(f"{p.name}:{exc.lineno}")
    add("sources_parse", not bad, bad or "all sources parse")

    # Declared primary outputs, when the launcher names them.
    if launcher and launcher.is_file():
        ltext = launcher.read_text(errors="replace")
        # Only the task's OWN products count. A launcher also names its inputs and shared
        # reference files (GOVERNANCE_BASE.tsv, support.csv, ...), and demanding the
        # implementation "emit" an input is a false positive -- it made T-D1 fail this check
        # on a file it correctly only reads.
        prefix = _output_prefix(task_dir.name)
        declared = sorted(set(re.findall(r"\b([A-Za-z][\w\-]*\.(?:tsv|csv|parquet|json|png|svg|pdf))\b", ltext)))
        declared = [d for d in declared
                    if d not in REQUIRED and not d.startswith(("TASK_", "OUTPUT_", "PREPARE_"))
                    and prefix and d.lower().startswith(prefix)]
        missing = [d for d in declared if d not in blob]
        if declared:
            add("emits_declared_outputs", not missing,
                f"missing from implementation: {missing[:6]}" if missing
                else f"all {len(declared)} launcher-named output(s) referenced")
        controls = [d for d in declared if "control" in d.lower() or "gate" in d.lower()]
        if controls:
            add("emits_control_table", all(c in blob for c in controls), controls)

    return all(c["result"] == "PASS" for c in checks), checks


def main() -> int:
    ap = argparse.ArgumentParser(description="Check an implementation can emit its required artefacts.")
    ap.add_argument("task_dir", type=Path)
    ap.add_argument("--launcher", type=Path)
    ap.add_argument("--json-out", type=Path)
    a = ap.parse_args()
    launcher = a.launcher or (a.task_dir / "TASK_LAUNCHER.md")
    ok, checks = check(a.task_dir, launcher)
    for c in checks:
        print(f"{c['result']:4}  {c['check']:34}  {c['detail'][:100]}")
    print(f"\nverdict\t{'PASS' if ok else 'FAIL'}\t"
          f"{sum(1 for c in checks if c['result'] == 'PASS')}/{len(checks)}")
    if a.json_out:
        a.json_out.write_text(json.dumps({"ok": ok, "checks": checks}, indent=2, sort_keys=True) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
