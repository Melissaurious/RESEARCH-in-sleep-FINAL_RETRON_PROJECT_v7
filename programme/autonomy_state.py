#!/usr/bin/env python3
"""Small shared helpers for the autonomous execution layer.

This module is intentionally non-scientific. It only handles machine state, hashes,
TSV updates, task-report parsing, and scheduling predicates.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

TERMINAL_VALID = {"PASS"}
TERMINAL_INVALID = {"VOID", "STOP", "INCONCLUSIVE", "BLOCKED"}
TERMINAL = TERMINAL_VALID | TERMINAL_INVALID
SCIENTIFIC_OUTCOMES = {
    "SUPPORTS_H1", "SUPPORTS_H0", "FALSIFIED", "BOUND", "DESCRIPTIVE", "NOT_APPLICABLE"
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    os.close(fd)
    try:
        with open(tmp, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({k: "" if row.get(k) is None else str(row.get(k, "")) for k in fieldnames})
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def upsert_tsv(path: Path, key: str, row: dict[str, object], fieldnames: list[str] | None = None) -> None:
    if path.exists():
        fields, rows = read_tsv(path)
    else:
        fields, rows = (fieldnames or list(row), [])
    if fieldnames:
        fields = fieldnames
    found = False
    out: list[dict[str, object]] = []
    for old in rows:
        if old.get(key) == str(row.get(key, "")):
            merged = dict(old)
            merged.update(row)
            out.append(merged)
            found = True
        else:
            out.append(old)
    if not found:
        out.append(row)
    write_tsv(path, fields, out)


def parse_front_matter(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    block = text.split("---", 2)[1]
    result: dict[str, str] = {}
    current_key: str | None = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1].isspace() and current_key:
            result[current_key] = result[current_key] + "\n" + raw.strip()
            continue
        if ":" not in raw:
            continue
        key, _, value = raw.partition(":")
        current_key = key.strip()
        result[current_key] = value.strip()
    return result


REPORT_STATE_RE = re.compile(r"^TASK_STATE:\s*([A-Z_]+)\s*$", re.MULTILINE)
REPORT_OUTCOME_RE = re.compile(r"^SCIENTIFIC_OUTCOME:\s*([A-Z0-9_]+)\s*$", re.MULTILINE)


def parse_task_report(path: Path) -> tuple[str, str]:
    text = path.read_text()
    ms = REPORT_STATE_RE.search(text)
    mo = REPORT_OUTCOME_RE.search(text)
    if not ms:
        raise ValueError(f"TASK_STATE missing from {path}")
    state = ms.group(1)
    if state not in TERMINAL:
        raise ValueError(f"unknown TASK_STATE={state} in {path}")
    if not mo:
        raise ValueError(f"SCIENTIFIC_OUTCOME missing from {path}")
    outcome = mo.group(1)
    if outcome not in SCIENTIFIC_OUTCOMES:
        raise ValueError(f"unknown SCIENTIFIC_OUTCOME={outcome} in {path}")
    return state, outcome


def verify_output_manifest(output_dir: Path) -> list[str]:
    manifest = output_dir / "OUTPUT_MANIFEST.sha256"
    if not manifest.exists():
        raise FileNotFoundError(f"missing {manifest}")
    errors: list[str] = []
    for n, raw in enumerate(manifest.read_text().splitlines(), 1):
        if not raw.strip():
            continue
        parts = raw.split(None, 1)
        if len(parts) != 2:
            errors.append(f"line {n}: malformed")
            continue
        expected, rel = parts
        rel = rel.strip().lstrip("*")
        p = (output_dir / rel).resolve()
        try:
            p.relative_to(output_dir.resolve())
        except ValueError:
            errors.append(f"line {n}: path escapes output dir: {rel}")
            continue
        if not p.is_file():
            errors.append(f"line {n}: missing {rel}")
            continue
        got = sha256_file(p)
        if got != expected:
            errors.append(f"line {n}: sha mismatch {rel}: {got} != {expected}")
    return errors


def load_execution_spec(path: Path) -> dict:
    data = json.loads(path.read_text())
    required = {
        "schema_version", "task_id", "worktree", "branch", "freeze_commit", "command",
        "inputs", "output_directory", "backend", "resources", "runtime"
    }
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"execution spec missing fields: {missing}")
    if data["schema_version"] != 1:
        raise ValueError(f"unsupported schema_version={data['schema_version']}")
    if not isinstance(data["command"], list) or not data["command"]:
        raise ValueError("command must be a non-empty argv list")
    if data["backend"] not in {"local", "ibex"}:
        raise ValueError("backend must be local or ibex")
    out = data["output_directory"]
    if not out or str(out).startswith("/") or ".." in Path(out).parts:
        raise ValueError("output_directory must be a safe relative path")
    return data


@dataclass(frozen=True)
class ScheduleTask:
    task_id: str
    state: str
    io_tokens: int
    hard_dependencies: tuple[str, ...] = ()
    schedule_after: tuple[str, ...] = ()


def choose_launchable(
    tasks: list[ScheduleTask],
    task_states: dict[str, str],
    running_tokens: int,
    total_tokens: int,
) -> tuple[list[str], dict[str, str]]:
    """Pure deterministic scheduler used by the runner and tests.

    Hard dependencies require PASS. A terminal-invalid hard dependency blocks only its descendants.
    schedule_after is ordering only: predecessor must merely be terminal, so failure of an unrelated
    asset task does not poison the next serial lane item.
    """
    selected: list[str] = []
    decisions: dict[str, str] = {}
    available = total_tokens - running_tokens
    for task in sorted(tasks, key=lambda x: x.task_id):
        if task.state not in {"PENDING", "READY", "AUTHORIZED", "WAIT_DEP", "WAIT_RESOURCE"}:
            continue
        bad_dep = next((d for d in task.hard_dependencies if task_states.get(d) in TERMINAL_INVALID), None)
        if bad_dep:
            decisions[task.task_id] = f"BLOCKED_DEPENDENCY:{bad_dep}:{task_states.get(bad_dep)}"
            continue
        waiting_dep = next((d for d in task.hard_dependencies if task_states.get(d) != "PASS"), None)
        if waiting_dep:
            decisions[task.task_id] = f"WAIT_DEP:{waiting_dep}:{task_states.get(waiting_dep, 'UNKNOWN')}"
            continue
        waiting_order = next((d for d in task.schedule_after if task_states.get(d) not in TERMINAL), None)
        if waiting_order:
            decisions[task.task_id] = f"WAIT_ORDER:{waiting_order}:{task_states.get(waiting_order, 'UNKNOWN')}"
            continue
        if task.io_tokens > available:
            decisions[task.task_id] = f"WAIT_RESOURCE:need={task.io_tokens}:available={available}"
            continue
        selected.append(task.task_id)
        decisions[task.task_id] = "SELECTED"
        available -= task.io_tokens
    return selected, decisions
