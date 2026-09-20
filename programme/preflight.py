#!/usr/bin/env python3
"""Preflight and consumption gates for the retron programme.

Non-scientific. Resolves and checks a task without executing it, and implements the
consumption gate that decides whether a downstream task may read an upstream artifact.

Usage:
    python3 programme/preflight.py <task-id>        # report one task
    python3 programme/preflight.py --all            # report every task on the board
    python3 programme/preflight.py --selftest       # failure-injection suite
"""
from __future__ import annotations
import csv, hashlib, json, os, subprocess, sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

SYN = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis")
PROGRAMME = SYN / "programme"
BOARD = PROGRAMME / "TASK_BOARD.tsv"
TASKS = PROGRAMME / "tasks"

# The four files that constitute the governance layer. governance_base is the commit at
# which ANY of these last changed. Stamping a launcher does not change them, so the base
# stays stable across launcher edits.
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


def git(*args: str, cwd: Path = SYN) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True).stdout.strip()


def governance_base() -> str:
    """Commit at which the governance layer last changed."""
    out = git("log", "-1", "--format=%h", "--", *GOVERNANCE_FILES)
    return out


def governance_fingerprint() -> str:
    """Content hash of the governance layer, independent of git."""
    h = hashlib.sha256()
    for rel in GOVERNANCE_FILES:
        p = SYN / rel
        h.update(rel.encode())
        h.update(p.read_bytes() if p.exists() else b"<MISSING>")
    return h.hexdigest()[:16]


def read_board() -> dict[str, dict]:
    with BOARD.open() as fh:
        return {r["task_id"]: r for r in csv.DictReader(fh, delimiter="\t")}


def read_front_matter(task_id: str) -> dict:
    p = TASKS / task_id / "TASK_LAUNCHER.md"
    if not p.exists():
        return {}
    txt = p.read_text()
    if not txt.startswith("---"):
        return {}
    block = txt.split("---", 2)[1]
    fm: dict = {}
    for line in block.splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    return fm


# --------------------------------------------------------------------------- gates

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

    fm = read_front_matter(task_id)
    pf.add("launcher_present", bool(fm), str(TASKS / task_id / "TASK_LAUNCHER.md"))
    if not fm:
        return pf

    pf.info.update({
        "launcher": str(TASKS / task_id / "TASK_LAUNCHER.md"),
        "worktree": fm.get("worktree", ""),
        "branch": fm.get("branch", ""),
        "output_directory": fm.get("output_directory", ""),
        "hard_dependencies": fm.get("hard_dependencies", "[]"),
        "populations_touched": fm.get("populations_touched", "[]"),
        "governance_base_recorded": fm.get("governance_base", ""),
        "governance_base_actual": base,
        "governance_fingerprint": governance_fingerprint(),
    })

    # governance base must match
    rec = fm.get("governance_base", "")
    pf.add("governance_base_current", rec == base,
           f"launcher records {rec or '<none>'}, governance layer is at {base}")

    # placeholders that must be resolved before execution
    body = (TASKS / task_id / "TASK_LAUNCHER.md").read_text()
    placeholders = [s for s in ("declared before running", "a floor declared", "TBC",
                                "not named", "<declare") if s in body]
    # a floor that is referenced but never given a value is a blocker
    unresolved = "floor declared before running" in body or "declared before running" in body
    pf.add("no_unresolved_criteria", not unresolved,
           "launcher refers to a criterion that is not stated in the launcher" if unresolved else "")

    # worktree present and descends from the governance base
    wt = Path(fm.get("worktree", ""))
    pf.add("worktree_exists", wt.is_dir(), str(wt))
    if wt.is_dir():
        head = git("rev-parse", "--short", "HEAD", cwd=wt)
        pf.info["worktree_head"] = head
        # Task worktrees are analysis-tier and are based on `main`; the governance layer is
        # index-tier and lives on project-synthesis. The two tiers are deliberately unmerged,
        # so a task worktree cannot descend from the governance commit without collapsing the
        # tier separation. Ancestry is therefore gated on the DECLARED base_commit, while
        # staleness of governance is gated separately and strictly by governance_base_current
        # plus the content fingerprint. A stale governance layer still cannot be used.
        declared = fm.get("base_commit", "")
        pf.info["base_commit_declared"] = declared
        anc = bool(declared) and subprocess.run(
            ["git", "merge-base", "--is-ancestor", declared, "HEAD"],
            cwd=wt, capture_output=True).returncode == 0
        pf.add("worktree_descends_from_declared_base", anc,
               f"worktree HEAD {head} does not descend from declared base {declared or '<none>'}"
               if not anc else f"{head} descends from {declared}")

    # output directory must be declared and inside the worktree
    outdir = fm.get("output_directory", "")
    pf.add("output_directory_declared", bool(outdir) and not outdir.startswith("/"), outdir)

    # hard dependencies must themselves be PASS
    deps = fm.get("hard_dependencies", "[]").strip("[]").replace('"', "").split(",")
    deps = [d.strip() for d in deps if d.strip()]
    for d in deps:
        drow = board.get(d)
        ok = bool(drow) and drow["state"] == "PASS"
        pf.add(f"dep_satisfied:{d}", ok, f"dependency state={drow['state'] if drow else 'missing'}")

    pf.launchable = all(c.ok for c in pf.checks)
    return pf


def consumption_gate(producer_state: str, scientific_outcome: str,
                     artifact: str, consumable_outputs: list[str]) -> tuple[bool, str]:
    """May a downstream task read `artifact`?

    Gates on TASK VALIDITY ONLY. A refuted hypothesis is a successful task.
    """
    if producer_state not in TERMINAL_VALID:
        return False, f"producer TASK_STATE={producer_state} is not PASS"
    if scientific_outcome not in SCIENTIFIC_OUTCOMES:
        return False, f"unknown SCIENTIFIC_OUTCOME={scientific_outcome}"
    if artifact not in consumable_outputs:
        return False, f"{artifact} is not on the producer's CONSUMABLE_OUTPUTS list"
    return True, f"allowed: TASK_STATE=PASS, SCIENTIFIC_OUTCOME={scientific_outcome}"


def write_guard(path: str, output_directory: str, worktree: str) -> tuple[bool, str]:
    """May a task write to `path`?"""
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


# --------------------------------------------------------------------------- cli

def render(pf: Preflight) -> str:
    lines = [f"=== PREFLIGHT · {pf.task_id} ===",
             f"  LAUNCHABLE: {'YES' if pf.launchable else 'NO'}"]
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
        from test_gates import run_suite  # noqa
        return run_suite()
    board = read_board()
    base = governance_base()
    if argv[0] == "--all":
        rows = []
        for tid, row in board.items():
            if not (TASKS / tid / "TASK_LAUNCHER.md").exists():
                continue
            pf = preflight(tid, board, base)
            print(render(pf)); print()
            rows.append({"task_id": tid, "state": row["state"],
                         "launchable": pf.launchable,
                         "failed_checks": ";".join(c.name for c in pf.checks if not c.ok)})
        out = PROGRAMME / "PREFLIGHT_STATUS.tsv"
        with out.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t")
            w.writeheader(); w.writerows(rows)
        print(f"wrote {out}")
        return 0
    print(render(preflight(argv[0], board, base)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
