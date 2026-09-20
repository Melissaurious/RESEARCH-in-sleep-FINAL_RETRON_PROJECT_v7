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
import shlex
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Acceptance boundary -- kept aligned with pinned ARIS tools/run_state.py.
#
# ARIS splits EXECUTION-COMPLETENESS from ACCEPTANCE: `set` may write only the
# executor statuses, and ONLY `accept` writes `accepted`, which requires a verdict
# id and a named reviewer. "A loop can DRIVE resume, it cannot ACQUIT a phase past
# itself."  This layer is a resource/process scheduler underneath that contract, so
# it must never turn an executor's own self-report into an acceptance.
#
# PASS therefore means INDEPENDENTLY ACCEPTED and is the only state that satisfies a
# hard scientific dependency.  A task the worker itself reports as having succeeded
# lands in COMPLETE_AWAITING_REVIEW -- the vocabulary this project's own
# EXECUTION_LEDGER already uses for executed-but-unreviewed tasks.
TERMINAL_VALID = {"PASS"}                         # accepted; satisfies a hard dependency
TERMINAL_EXECUTOR = {"COMPLETE_AWAITING_REVIEW"}  # executor self-report; NOT an acceptance
TERMINAL_INVALID = {"VOID", "STOP", "INCONCLUSIVE", "BLOCKED"}
TERMINAL = TERMINAL_VALID | TERMINAL_EXECUTOR | TERMINAL_INVALID
SCIENTIFIC_OUTCOMES = {
    "SUPPORTS_H1", "SUPPORTS_H0", "FALSIFIED", "BOUND", "DESCRIPTIVE", "NOT_APPLICABLE"
}


_BACKEND_ALIASES = {
    "workstation": "local", "local": "local", "borg": "local", "laptop": "local",
    "ibex": "ibex", "slurm": "ibex", "cluster": "ibex",
}


def normalise_prepare_result(d: dict) -> dict:
    """Accept the PREPARE_RESULT shapes a preparing agent actually writes.

    The contract asks for `command` as an argv list, `self_checks` as a list of
    {state: PASS}, and `backend` in {local, ibex}.  A preparing agent legitimately
    writes richer, equally unambiguous shapes -- `command` as {cwd, argv, ...},
    `self_checks` as {checks: [...], passed, failed, exit_code}, and `backend` as
    "workstation".  Rejecting those is a PARSER defect, not a scientific finding:
    iterating a dict yields its KEYS, so `x.get('state')` raised
    "'str' object has no attribute 'get'" and the task was wrongly BLOCKED_PREPARE.

    This normalises shape only.  It never invents a passing self-check, and it never
    relaxes what counts as a pass.
    """
    out = dict(d)

    cmd = out.get("command")
    if isinstance(cmd, dict):
        cmd = cmd.get("argv")
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    if not isinstance(cmd, list) or not cmd or not all(isinstance(x, str) for x in cmd):
        raise ValueError("PREPARE_RESULT.command must be an argv list, or a dict carrying one")
    out["command"] = cmd

    backend = str(out.get("backend", "")).strip().lower()
    if backend not in _BACKEND_ALIASES:
        raise ValueError(f"PREPARE_RESULT.backend={backend!r} is not a known backend")
    out["backend"] = _BACKEND_ALIASES[backend]

    out["self_checks"] = _normalise_self_checks(out.get("self_checks"))
    return out


def _normalise_self_checks(sc) -> list[dict]:
    """Flatten a self-check block to [{id, state}], failing closed on anything opaque."""
    if sc is None:
        return []
    if isinstance(sc, dict):
        items = sc.get("checks")
        if not isinstance(items, list):
            items = []
        rows = _normalise_self_checks(items)
        # Honour explicit counters when the block carries them: they must agree.
        failed, code = sc.get("failed"), sc.get("exit_code")
        if isinstance(failed, int) and failed > 0:
            rows.append({"id": "declared_failed_count", "state": f"FAIL({failed})"})
        if isinstance(code, int) and code != 0:
            rows.append({"id": "declared_exit_code", "state": f"FAIL({code})"})
        if not rows and not isinstance(failed, int):
            raise ValueError("PREPARE_RESULT.self_checks carries no checks and no failed count")
        return rows
    if not isinstance(sc, list):
        raise ValueError(f"PREPARE_RESULT.self_checks has unusable type {type(sc).__name__}")
    rows: list[dict] = []
    for x in sc:
        if isinstance(x, dict):
            state = x.get("state") or x.get("status") or x.get("result") or ""
            rows.append({"id": str(x.get("id") or x.get("name") or "?"), "state": str(state).upper()})
        else:
            # A bare string names a check but asserts no outcome -- never treat it as a pass.
            rows.append({"id": str(x), "state": "UNKNOWN"})
    return rows


def self_checks_all_pass(checks: list[dict]) -> bool:
    return bool(checks) and all(c.get("state") == "PASS" for c in checks)


def _controls_tables(out: Path) -> list[Path]:
    seen: dict[Path, None] = {}
    for pat in ("*controls*.tsv", "*gate*.tsv", "tables/*controls*.tsv", "tables/*gate*.tsv"):
        for p in out.glob(pat):
            if p.is_file():
                seen.setdefault(p.resolve(), None)
    return sorted(seen)


def validate_type_a_execution(spec: dict, wt: Path, out: Path) -> tuple[bool, list[dict]]:
    """Independent deterministic re-validation of a finished Type-A task.

    This is the separate verifier that ARIS run_state.py permits to write `accepted`
    ("a CROSS-MODEL reviewer (codex/gemini) OR a deterministic verifier").  It exists so
    an ordinary preregistered computation does NOT need a semantic reviewer merely to
    establish that it executed validly.

    It re-derives every check from disk.  It does NOT read, trust or consult the worker's
    own run record for any verdict -- the worker's statement of PASS is not evidence here.

    It establishes EXECUTION VALIDITY ONLY (Type A).  It makes no judgment about whether
    an interpretation is justified, whether a result supports a claim, or whether anything
    may enter thesis/paper language: those are Type-B and still require semantic review.
    """
    checks: list[dict] = []

    def add(name, ok, detail=""):
        checks.append({"check": name, "result": "PASS" if ok else "FAIL", "detail": str(detail)})
        return ok

    # 1 - frozen commit / launcher / implementation hashes, re-derived from the worktree.
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt, text=True,
                              capture_output=True, check=True).stdout.strip()
        branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=wt, text=True,
                                capture_output=True, check=True).stdout.strip()
        # Untracked files are EXPECTED: the run writes its outputs into the worktree.
        # What must not have moved is any TRACKED file, i.e. anything that was frozen.
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                               cwd=wt, text=True, capture_output=True, check=True).stdout.strip()
        add("freeze_commit", head == spec["freeze_commit"], f"{head} vs {spec['freeze_commit']}")
        add("freeze_branch", branch == spec["branch"], f"{branch} vs {spec['branch']}")
        add("no_tracked_file_modified_after_freeze", not dirty, dirty[:200] or "no tracked change")
    except Exception as exc:  # noqa: BLE001
        add("freeze_commit", False, exc)

    bad = []
    for rel, expected in sorted(spec.get("frozen_files", {}).items()):
        p = wt / rel
        if not p.is_file() or sha256_file(p) != expected:
            bad.append(rel)
    add("frozen_file_hashes", not bad and bool(spec.get("frozen_files")), bad or "all match")

    # The frozen set must actually cover the launcher, or "criteria unchanged" is unprovable.
    add("launcher_is_frozen",
        any(Path(r).name == "TASK_LAUNCHER.md" for r in spec.get("frozen_files", {})),
        "TASK_LAUNCHER.md must be hash-pinned in frozen_files")

    # 2 - exact input hashes.
    bad_in = []
    for item in spec.get("inputs", []):
        p = Path(item["path"])
        if not p.is_file() or (item.get("sha256") and sha256_file(p) != item["sha256"]):
            bad_in.append(item.get("dataset_id") or str(p))
    add("input_hashes", not bad_in, bad_in or "all match")

    # 3 / 4 / 5 - required artifacts, manifest, run log.
    report, runlog = out / "TASK_REPORT.md", out / "logs" / "run_log.json"
    manifest = out / "OUTPUT_MANIFEST.sha256"
    missing = [str(p.relative_to(out)) for p in (report, runlog, manifest) if not p.is_file()]
    add("required_outputs_present", not missing, missing or "present")

    if manifest.is_file():
        try:
            errs = verify_output_manifest(out)
            add("output_manifest_valid", not errs, errs[:5] or "verified")
        except Exception as exc:  # noqa: BLE001
            add("output_manifest_valid", False, exc)
    else:
        add("output_manifest_valid", False, "manifest missing")

    log_inputs: list[str] = []
    unverifiable: list[str] = []
    if runlog.is_file():
        try:
            data = json.loads(runlog.read_text())
            ok = isinstance(data, (dict, list)) and bool(data)
            if isinstance(data, dict):
                # A run log may record inputs as a list, or as {label: {...}} -- iterating a
                # dict yields its KEYS, which are labels, not paths. Compare only entries
                # that are actually paths; a label asserts nothing either way.
                raw = data.get("inputs") or []
                items = list(raw.values()) if isinstance(raw, dict) else raw
                for x in items:
                    p = x.get("path") if isinstance(x, dict) else x
                    p = str(p) if p is not None else ""
                    (log_inputs if ("/" in p or p.startswith("/")) else unverifiable).append(p)
            add("run_log_valid", ok, "parsed")
        except Exception as exc:  # noqa: BLE001
            add("run_log_valid", False, exc)
    else:
        add("run_log_valid", False, "run log missing")

    # 6 - TASK_REPORT schema.
    if report.is_file():
        try:
            parse_task_report(report)
            add("task_report_schema", True, "TASK_STATE + SCIENTIFIC_OUTCOME present and known")
        except Exception as exc:  # noqa: BLE001
            add("task_report_schema", False, exc)
    else:
        add("task_report_schema", False, "report missing")

    # 7 - blocking controls all PASS, read from the landed control tables themselves.
    tables = _controls_tables(out)
    failed_ctrl: list[str] = []
    n_ctrl = 0
    for t in tables:
        try:
            _, rows_ = read_tsv(t)
        except Exception:  # noqa: BLE001
            failed_ctrl.append(f"{t.name}:UNREADABLE")
            continue
        for r in rows_:
            res = (r.get("result") or r.get("state") or "").strip().upper()
            if not res:
                continue
            blocking = (r.get("blocking") or "YES").strip().upper()
            n_ctrl += 1
            if blocking in {"YES", "TRUE", "1"} and res != "PASS":
                failed_ctrl.append(f"{t.name}:{r.get('check') or r.get('name') or '?'}={res}")
    add("blocking_controls_pass", bool(tables) and n_ctrl > 0 and not failed_ctrl,
        failed_ctrl[:5] or f"{n_ctrl} blocking control rows PASS across {len(tables)} table(s)")

    # 8 - no forbidden input/population use: nothing read beyond the frozen declaration.
    declared = {str(Path(i["path"]).resolve()) for i in spec.get("inputs", [])}
    undeclared = [p for p in log_inputs if str(Path(p).resolve()) not in declared]
    detail = undeclared[:5] or (f"{len(log_inputs)} logged path(s) all declared"
                                + (f"; {len(unverifiable)} non-path label(s) not checkable" if unverifiable else ""))
    add("no_undeclared_inputs", not undeclared, detail)

    # 9 - preregistered endpoint: the frozen launcher still binds this output directory.
    try:
        fm = parse_front_matter(wt / "programme" / "tasks" / spec["task_id"] / "TASK_LAUNCHER.md")
        add("endpoint_unchanged",
            fm.get("output_directory", "").rstrip("/") == str(spec["output_directory"]).rstrip("/")
            and fm.get("frozen", "").lower() == "true",
            f"launcher output_directory={fm.get('output_directory')} frozen={fm.get('frozen')}")
    except Exception as exc:  # noqa: BLE001
        add("endpoint_unchanged", False, exc)

    return all(c["result"] == "PASS" for c in checks), checks


def acceptance_verdict(task_id: str, freeze_commit: str, checks: list[dict]) -> str:
    """Stable verdict id for a deterministic acceptance, derived from what was checked."""
    payload = json.dumps({"task_id": task_id, "freeze_commit": freeze_commit, "checks": checks},
                         sort_keys=True)
    return "det-" + sha256_text(payload)[:16]


def executor_terminal_state(self_reported: str) -> str:
    """Map a worker's self-reported task state onto a state the runner may write.

    A self-reported success is recorded as COMPLETE_AWAITING_REVIEW, never PASS:
    granting PASS is an acceptance and belongs to ARIS reviewer routing, which
    records who acquitted the task and under which verdict.  A self-reported
    FAILURE is kept verbatim -- no reviewer is needed to believe a task that says
    it failed, and downgrading it would hide a defect.
    """
    return "COMPLETE_AWAITING_REVIEW" if self_reported in TERMINAL_VALID else self_reported


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
