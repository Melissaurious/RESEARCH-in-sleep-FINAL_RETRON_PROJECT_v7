#!/usr/bin/env python3
"""Deterministic executor for one frozen retron task.

No scientific decisions happen here. The worker verifies the frozen binding and input hashes,
executes the exact argv from TASK_EXECUTION.json, and validates the traceability contract.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from autonomy_state import (
    atomic_write,
    load_execution_spec,
    parse_task_report,
    sha256_file,
    verify_output_manifest,
)


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git(cwd: Path, *args: str, check: bool = True) -> str:
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout.strip()


def record(path: Path, data: dict) -> None:
    atomic_write(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


def validate_frozen_binding(spec: dict) -> tuple[Path, Path]:
    wt = Path(spec["worktree"]).resolve()
    if not wt.is_dir():
        raise RuntimeError(f"worktree missing: {wt}")
    head = git(wt, "rev-parse", "HEAD")
    if head != spec["freeze_commit"]:
        raise RuntimeError(f"freeze mismatch: HEAD={head}, expected={spec['freeze_commit']}")
    branch = git(wt, "rev-parse", "--abbrev-ref", "HEAD")
    if branch != spec["branch"]:
        raise RuntimeError(f"branch mismatch: {branch} != {spec['branch']}")
    dirty = git(wt, "status", "--porcelain")
    if dirty:
        raise RuntimeError("frozen task worktree is dirty before execution")

    for rel, expected in sorted(spec.get("frozen_files", {}).items()):
        p = (wt / rel).resolve()
        try:
            p.relative_to(wt)
        except ValueError:
            raise RuntimeError(f"frozen file escapes worktree: {rel}")
        if not p.is_file():
            raise RuntimeError(f"frozen file missing: {rel}")
        got = sha256_file(p)
        if got != expected:
            raise RuntimeError(f"frozen-file hash mismatch: {rel}: {got} != {expected}")

    for item in spec["inputs"]:
        p = Path(item["path"])
        expected = item.get("sha256", "")
        if not p.is_file():
            raise RuntimeError(f"input missing: {item.get('dataset_id', '?')} {p}")
        if expected:
            got = sha256_file(p)
            if got != expected:
                raise RuntimeError(
                    f"input hash mismatch: {item.get('dataset_id', '?')}: {got} != {expected}"
                )

    out = (wt / spec["output_directory"]).resolve()
    try:
        out.relative_to(wt)
    except ValueError:
        raise RuntimeError("output_directory escapes worktree")
    if out.exists() and any(out.iterdir()) and not spec["runtime"].get("resume_allowed", False):
        raise RuntimeError(f"output directory already non-empty: {out}")
    return wt, out


def run_local(spec: dict, runtime_record: Path) -> int:
    wt, out = validate_frozen_binding(spec)
    out.mkdir(parents=True, exist_ok=True)
    # The harness must NOT write into the task's declared output directory. A task that
    # enforces a closed output manifest correctly rejects files it did not declare, and
    # T-R2a failed exit 4 on exactly that ("undeclared output written: runner_logs/...")
    # after its science had already succeeded. Harness logs live beside the runtime record.
    logdir = runtime_record.parent / "runner_logs" / spec["task_id"]
    logdir.mkdir(parents=True, exist_ok=True)
    stdout_path = logdir / "stdout.log"
    stderr_path = logdir / "stderr.log"
    timeout = int(spec["runtime"].get("max_runtime_seconds", 0) or 0)

    env = os.environ.copy()
    env.update({str(k): str(v) for k, v in spec.get("environment", {}).items()})
    env["RETRON_TASK"] = spec["task_id"]
    env["RETRON_FREEZE_COMMIT"] = spec["freeze_commit"]

    started = utcnow()
    with stdout_path.open("ab") as outfh, stderr_path.open("ab") as errfh:
        proc = subprocess.Popen(
            spec["command"], cwd=wt, env=env, stdout=outfh, stderr=errfh,
            start_new_session=True,
        )
        status = {
            "schema_version": 1,
            "task_id": spec["task_id"],
            "backend": "local",
            "freeze_commit": spec["freeze_commit"],
            "worker_pid": os.getpid(),
            "analysis_pid": proc.pid,
            "analysis_pgid": os.getpgid(proc.pid),
            "started_at": started,
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
            "worker_state": "RUNNING",
        }
        record(runtime_record, status)
        try:
            rc = proc.wait(timeout=timeout if timeout > 0 else None)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            status.update({
                "worker_state": "STOP_RUNTIME",
                "finished_at": utcnow(),
                "exit_code": proc.returncode,
                "stop_reason": f"max_runtime_seconds={timeout} exceeded",
            })
            record(runtime_record, status)
            return 124

    status.update({"exit_code": rc, "finished_at": utcnow()})
    if rc != 0:
        status.update({"worker_state": "PROCESS_FAILED", "stop_reason": f"exit_code={rc}"})
        record(runtime_record, status)
        return rc or 1

    required = [out / "TASK_REPORT.md", out / "logs" / "run_log.json", out / "OUTPUT_MANIFEST.sha256"]
    missing = [str(p) for p in required if not p.is_file()]
    manifest_errors = [] if missing else verify_output_manifest(out)
    if missing or manifest_errors:
        status.update({
            "worker_state": "ARTIFACT_INVALID",
            "missing_required": missing,
            "manifest_errors": manifest_errors,
        })
        record(runtime_record, status)
        return 20

    try:
        task_state, scientific_outcome = parse_task_report(out / "TASK_REPORT.md")
    except Exception as exc:
        status.update({"worker_state": "ARTIFACT_INVALID", "report_error": str(exc)})
        record(runtime_record, status)
        return 21

    status.update({
        "worker_state": "COMPLETE",
        "task_state": task_state,
        "scientific_outcome": scientific_outcome,
        "task_report": str(out / "TASK_REPORT.md"),
        "output_manifest": str(out / "OUTPUT_MANIFEST.sha256"),
        "run_log": str(out / "logs" / "run_log.json"),
    })
    record(runtime_record, status)
    return 0


def remote_sha256(host: str, path: str) -> str:
    cmd = ["ssh", host, "sha256sum", path]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"remote sha256 failed for {path}: {p.stderr.strip()}")
    return p.stdout.split()[0]


def run_ibex(spec: dict, runtime_record: Path) -> int:
    """Minimal fail-closed Ibex adapter.

    It requires an explicitly predeclared remote worktree and submit script. Each staged input is
    copied and hash-checked remotely before sbatch. Current Wave 01 does not route a task here.
    """
    validate_frozen_binding(spec)
    ibex = spec.get("ibex") or {}
    for key in ("host", "remote_worktree", "submit_script", "remote_output_directory"):
        if not ibex.get(key):
            raise RuntimeError(f"ibex.{key} required")
    host = ibex["host"]
    remote_wt = ibex["remote_worktree"]

    # Stage only explicitly named immutable inputs. No directory guessing.
    for item in ibex.get("stage_inputs", []):
        src = Path(item["src"])
        dst = item["dst"]
        expected = item["sha256"]
        got = sha256_file(src)
        if got != expected:
            raise RuntimeError(f"local stage hash mismatch for {src}")
        subprocess.run(["ssh", host, "mkdir", "-p", str(Path(dst).parent)], check=True)
        subprocess.run(["rsync", "-a", str(src), f"{host}:{dst}"], check=True)
        rg = remote_sha256(host, dst)
        if rg != expected:
            raise RuntimeError(f"remote stage hash mismatch for {dst}: {rg} != {expected}")

    submit = subprocess.run(
        ["ssh", host, f"cd {remote_wt} && sbatch --parsable {ibex['submit_script']}"],
        capture_output=True, text=True,
    )
    if submit.returncode:
        raise RuntimeError(f"sbatch failed: {submit.stderr.strip()}")
    job_id = submit.stdout.strip().split(";")[0]
    status = {
        "schema_version": 1, "task_id": spec["task_id"], "backend": "ibex",
        "freeze_commit": spec["freeze_commit"], "worker_pid": os.getpid(),
        "slurm_job_id": job_id, "started_at": utcnow(), "worker_state": "RUNNING",
    }
    record(runtime_record, status)

    poll = int(ibex.get("poll_seconds", 30))
    while True:
        q = subprocess.run(
            ["ssh", host, f"squeue -h -j {job_id} -o %T"], capture_output=True, text=True
        )
        if q.returncode:
            status.update({"worker_state": "BLOCKED_BACKEND", "backend_error": q.stderr.strip()})
            record(runtime_record, status)
            return 30
        if not q.stdout.strip():
            break
        time.sleep(poll)

    a = subprocess.run(
        ["ssh", host, f"sacct -n -X -j {job_id} --format=State,ExitCode -P | head -1"],
        capture_output=True, text=True,
    )
    if a.returncode:
        status.update({"worker_state": "BLOCKED_BACKEND", "backend_error": a.stderr.strip()})
        record(runtime_record, status)
        return 31
    fields = a.stdout.strip().split("|")
    slurm_state = fields[0] if fields else "UNKNOWN"
    exit_code = fields[1] if len(fields) > 1 else "UNKNOWN"
    status.update({"slurm_state": slurm_state, "slurm_exit_code": exit_code, "finished_at": utcnow()})
    if not slurm_state.startswith("COMPLETED") or not exit_code.startswith("0:0"):
        status.update({"worker_state": "PROCESS_FAILED"})
        record(runtime_record, status)
        return 32

    local_out = Path(spec["worktree"]) / spec["output_directory"]
    local_out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["rsync", "-a", f"{host}:{ibex['remote_output_directory'].rstrip('/')}/", f"{local_out}/"],
        check=True,
    )
    missing = [p for p in [local_out / "TASK_REPORT.md", local_out / "logs/run_log.json",
                            local_out / "OUTPUT_MANIFEST.sha256"] if not p.is_file()]
    errors = [] if missing else verify_output_manifest(local_out)
    if missing or errors:
        status.update({"worker_state": "ARTIFACT_INVALID", "missing_required": [str(x) for x in missing],
                       "manifest_errors": errors})
        record(runtime_record, status)
        return 33
    task_state, outcome = parse_task_report(local_out / "TASK_REPORT.md")
    status.update({"worker_state": "COMPLETE", "task_state": task_state,
                   "scientific_outcome": outcome, "task_report": str(local_out / "TASK_REPORT.md")})
    record(runtime_record, status)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--runtime-record", required=True, type=Path)
    args = ap.parse_args()
    spec = load_execution_spec(args.spec)
    try:
        if spec["backend"] == "local":
            return run_local(spec, args.runtime_record)
        return run_ibex(spec, args.runtime_record)
    except Exception as exc:
        record(args.runtime_record, {
            "schema_version": 1,
            "task_id": spec.get("task_id", "UNKNOWN"),
            "worker_state": "REFUSED",
            "error": str(exc),
            "finished_at": utcnow(),
        })
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
