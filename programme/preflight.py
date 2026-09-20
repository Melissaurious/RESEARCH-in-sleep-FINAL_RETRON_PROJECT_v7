#!/usr/bin/env python3
"""Preflight and consumption gates for the retron programme.

Scientific design lives in TASK_LAUNCHER.md. This module checks readiness and integrity only.
TASK_BOARD.tsv is the authorisation/readiness authority; a frozen task worktree launcher supersedes
the mutable synthesis copy for execution checks.

Usage:
    python3 programme/preflight.py <task-id>
    python3 programme/preflight.py --execute <task-id>
    python3 programme/preflight.py --all
    python3 programme/preflight.py --selftest
"""
from __future__ import annotations
import csv, hashlib, json, os, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path

SYN = Path(__file__).resolve().parents[1]
PROGRAMME = SYN / "programme"
BOARD = PROGRAMME / "TASK_BOARD.tsv"
TASKS = PROGRAMME / "tasks"
CANONICAL = PROGRAMME / "CANONICAL_DATASETS.tsv"
EXECUTIONS = PROGRAMME / "executions"

GOVERNANCE_FILES = [
    "programme/PROGRAM_LAUNCHER.md",
    "programme/WORKING_RULES.md",
    "programme/templates/TASK_LAUNCHER_TEMPLATE.md",
    "review-stage/TASK_PROTOCOL.md",
]

LAUNCHABLE_STATES = {"AUTHORIZED"}
TERMINAL_VALID = {"PASS"}
TERMINAL_INVALID = {"VOID", "BLOCKED", "STOP", "INCONCLUSIVE"}
SCIENTIFIC_OUTCOMES = {
    "SUPPORTS_H1", "SUPPORTS_H0", "FALSIFIED", "BOUND", "DESCRIPTIVE", "NOT_APPLICABLE",
}
CONSUMABLE_DATASET_STATES = {"CANONICAL", "CANONICAL_WITH_LIMITATION"}


def git(*args: str, cwd: Path = SYN) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True).stdout.strip()


def governance_base() -> str:
    return git("log", "-1", "--format=%h", "--", *GOVERNANCE_FILES)


def governance_fingerprint() -> str:
    h = hashlib.sha256()
    for rel in GOVERNANCE_FILES:
        p = SYN / rel
        h.update(rel.encode())
        h.update(p.read_bytes() if p.exists() else b"<MISSING>")
    return h.hexdigest()[:16]


def read_board() -> dict[str, dict]:
    with BOARD.open() as fh:
        return {r["task_id"]: r for r in csv.DictReader(fh, delimiter="\t")}


def _parse_front_matter_file(p: Path) -> dict:
    if not p.exists():
        return {}
    txt = p.read_text()
    if not txt.startswith("---"):
        return {}
    block = txt.split("---", 2)[1]
    fm: dict = {}
    current = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1].isspace() and current:
            fm[current] = fm[current] + "\n" + raw.strip()
            continue
        if ":" not in raw:
            continue
        k, _, v = raw.partition(":")
        current = k.strip()
        fm[current] = v.strip()
    return fm


def default_worktree(task_id: str) -> Path:
    name = SYN.name
    base = name[:-len("-synthesis")] if name.endswith("-synthesis") else name
    return SYN.parent / f"{base}-{task_id}"


def launcher_path(task_id: str) -> Path:
    """For frozen execution, prefer the launcher physically inside the task worktree."""
    wt_candidate = default_worktree(task_id) / "programme" / "tasks" / task_id / "TASK_LAUNCHER.md"
    wfm = _parse_front_matter_file(wt_candidate)
    if wfm.get("frozen", "").lower() == "true":
        return wt_candidate
    central = TASKS / task_id / "TASK_LAUNCHER.md"
    cfm = _parse_front_matter_file(central)
    wt = Path(cfm.get("worktree", "")) if cfm.get("worktree") else None
    if wt:
        p = wt / "programme" / "tasks" / task_id / "TASK_LAUNCHER.md"
        pfm = _parse_front_matter_file(p)
        if pfm.get("frozen", "").lower() == "true":
            return p
    return central


def read_front_matter(task_id: str) -> dict:
    return _parse_front_matter_file(launcher_path(task_id))


def canonical_statuses() -> dict[str, str]:
    if not CANONICAL.exists():
        return {}
    with CANONICAL.open() as fh:
        return {r["dataset_id"]: r["status"] for r in csv.DictReader(fh, delimiter="\t")}


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


@dataclass
class Preflight:
    task_id: str
    launchable: bool = False
    checks: list[Check] = field(default_factory=list)
    info: dict = field(default_factory=dict)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append(Check(name, ok, detail))


def preflight(task_id: str, board: dict | None = None, base: str | None = None) -> Preflight:
    board = board if board is not None else read_board()
    base = base or governance_base()
    pf = Preflight(task_id)

    row = board.get(task_id)
    pf.add("on_board", row is not None, "" if row else "task id not in TASK_BOARD.tsv")
    if not row:
        return pf
    state = row["state"]
    pf.info["state"] = state
    pf.add("state_authorized", state in LAUNCHABLE_STATES, f"state={state}")

    lp = launcher_path(task_id)
    fm = _parse_front_matter_file(lp)
    pf.add("launcher_present", bool(fm), str(lp))
    if not fm:
        return pf
    pf.info.update({
        "launcher": str(lp),
        "worktree": fm.get("worktree", ""),
        "branch": fm.get("branch", ""),
        "output_directory": fm.get("output_directory", ""),
        "hard_dependencies": fm.get("hard_dependencies", "[]"),
        "populations_touched": fm.get("populations_touched", "[]"),
        "governance_base_recorded": fm.get("governance_base", ""),
        "governance_base_actual": base,
        "governance_fingerprint": governance_fingerprint(),
    })

    rec = fm.get("governance_base", "")
    pf.add("governance_base_current", rec == base,
           f"launcher records {rec or '<none>'}, governance layer is at {base}")

    body = lp.read_text()
    unresolved = any(s in body for s in (
        "floor declared before running", "declared before running", "<declare", "TBC"
    ))
    pf.add("no_unresolved_criteria", not unresolved,
           "launcher contains unresolved criterion placeholder" if unresolved else "")

    wt = Path(fm.get("worktree", "")) if fm.get("worktree") else default_worktree(task_id)
    pf.add("worktree_exists", wt.is_dir(), str(wt))
    if wt.is_dir():
        head = git("rev-parse", "--short", "HEAD", cwd=wt)
        pf.info["worktree_head"] = head
        declared = fm.get("base_commit", "")
        pf.info["base_commit_declared"] = declared
        anc = bool(declared) and subprocess.run(
            ["git", "merge-base", "--is-ancestor", declared, "HEAD"],
            cwd=wt, capture_output=True).returncode == 0
        pf.add("worktree_descends_from_declared_base", anc,
               f"worktree HEAD {head} does not descend from declared base {declared or '<none>'}"
               if not anc else f"{head} descends from {declared}")

    outdir = fm.get("output_directory", "")
    pf.add("output_directory_declared", bool(outdir) and not outdir.startswith("/") and ".." not in Path(outdir).parts, outdir)

    deps = fm.get("hard_dependencies", "[]").strip("[]").replace('"', "").split(",")
    deps = [d.strip() for d in deps if d.strip()]
    for d in deps:
        drow = board.get(d)
        ok = bool(drow) and drow["state"] == "PASS"
        pf.add(f"dep_satisfied:{d}", ok, f"dependency state={drow['state'] if drow else 'missing'}")

    pf.launchable = all(c.ok for c in pf.checks)
    return pf


def execution_preflight(task_id: str) -> Preflight:
    pf = preflight(task_id)
    if not pf.launchable:
        return pf
    specpath = EXECUTIONS / task_id / "TASK_EXECUTION.json"
    pf.add("execution_spec_present", specpath.is_file(), str(specpath))
    if not specpath.is_file():
        pf.launchable = False
        return pf
    try:
        spec = json.loads(specpath.read_text())
    except Exception as exc:
        pf.add("execution_spec_valid_json", False, str(exc))
        pf.launchable = False
        return pf
    required = {"task_id", "worktree", "branch", "freeze_commit", "command", "inputs", "output_directory", "backend"}
    missing = sorted(required - set(spec))
    pf.add("execution_spec_required_fields", not missing, f"missing={missing}" if missing else "")
    if missing:
        pf.launchable = False
        return pf
    pf.add("execution_spec_task_id", spec["task_id"] == task_id, spec["task_id"])
    wt = Path(spec["worktree"])
    if wt.is_dir():
        head = git("rev-parse", "HEAD", cwd=wt)
        pf.add("freeze_commit_exact", head == spec["freeze_commit"], f"HEAD={head} freeze={spec['freeze_commit']}")
        dirty = git("status", "--porcelain", cwd=wt)
        pf.add("frozen_worktree_clean", not dirty, dirty[:200])
    else:
        pf.add("freeze_commit_exact", False, "worktree missing")
        pf.add("frozen_worktree_clean", False, "worktree missing")

    statuses = canonical_statuses()
    for item in spec.get("inputs", []):
        p = Path(item.get("path", ""))
        expected = item.get("sha256", "")
        ds = item.get("dataset_id", "")
        ok = p.is_file()
        detail = str(p)
        if ok and expected:
            got = hashlib.sha256(p.read_bytes()).hexdigest()
            ok = got == expected
            detail = f"expected={expected[:12]} got={got[:12]}"
        pf.add(f"input_hash:{ds or p.name}", ok, detail)
        if ds in statuses:
            pf.add(f"canonical_status:{ds}", statuses[ds] in CONSUMABLE_DATASET_STATES, statuses[ds])
    pf.launchable = all(c.ok for c in pf.checks)
    return pf


def consumption_gate(producer_state: str, scientific_outcome: str,
                     artifact: str, consumable_outputs: list[str]) -> tuple[bool, str]:
    if producer_state not in TERMINAL_VALID:
        return False, f"producer TASK_STATE={producer_state} is not PASS"
    if scientific_outcome not in SCIENTIFIC_OUTCOMES:
        return False, f"unknown SCIENTIFIC_OUTCOME={scientific_outcome}"
    if artifact not in consumable_outputs:
        return False, f"{artifact} is not on the producer's CONSUMABLE_OUTPUTS list"
    return True, f"allowed: TASK_STATE=PASS, SCIENTIFIC_OUTCOME={scientific_outcome}"


def write_guard(path: str, output_directory: str, worktree: str) -> tuple[bool, str]:
    try:
        p = Path(path).resolve()
        allowed = (Path(worktree) / output_directory).resolve()
        p.relative_to(allowed)
        return True, "inside declared output directory"
    except Exception:
        return False, f"{path} is outside {worktree}/{output_directory}"


def hash_guard(path: str, expected_sha256: str) -> tuple[bool, str]:
    p = Path(path)
    if not p.exists():
        return False, "input missing"
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    return (got == expected_sha256), f"expected {expected_sha256[:12]} got {got[:12]}"


def criterion_guard(preregistered: str, at_report: str) -> tuple[bool, str]:
    return (preregistered == at_report), "criterion changed after preregistration" if preregistered != at_report else "unchanged"


def ordering_guard(prereg_ts: float, job_ts: float) -> tuple[bool, str]:
    return (prereg_ts < job_ts), f"preregistration {'precedes' if prereg_ts < job_ts else 'POST-DATES'} job submission"


def population_guard(claimed: set[str], already_consumed: set[str]) -> tuple[bool, str]:
    clash = claimed & already_consumed
    return (not clash), f"confirmatory population already consumed: {sorted(clash)}" if clash else "no collision"


def render(pf: Preflight) -> str:
    lines = [f"=== PREFLIGHT · {pf.task_id} ===", f"  LAUNCHABLE: {'YES' if pf.launchable else 'NO'}"]
    for k, v in pf.info.items():
        lines.append(f"  {k:<28} {v}")
    for c in pf.checks:
        mark = "ok  " if c.ok else "FAIL"
        lines.append(f"  [{mark}] {c.name}" + (f"  — {c.detail}" if c.detail else ""))
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--selftest":
        from test_gates import run_suite
        return run_suite()
    if argv[0] == "--execute":
        if len(argv) != 2:
            print("usage: preflight.py --execute <task-id>", file=sys.stderr)
            return 2
        p = execution_preflight(argv[1])
        print(render(p))
        return 0 if p.launchable else 1
    board = read_board()
    base = governance_base()
    if argv[0] == "--all":
        rows = []
        for tid in board:
            if not launcher_path(tid).exists():
                continue
            p = preflight(tid, board, base)
            print(render(p)); print()
            rows.append({"task_id": tid, "state": board[tid]["state"], "launchable": p.launchable,
                         "failed_checks": ";".join(c.name for c in p.checks if not c.ok)})
        out = PROGRAMME / "PREFLIGHT_STATUS.tsv"
        if rows:
            with out.open("w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t")
                w.writeheader(); w.writerows(rows)
            print(f"wrote {out}")
        return 0
    p = preflight(argv[0], board, base)
    print(render(p))
    return 0 if p.launchable else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
