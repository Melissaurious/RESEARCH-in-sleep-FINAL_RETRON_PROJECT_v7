#!/usr/bin/env python3
"""Independent cross-model adversarial review of a TASK_LAUNCHER, to ARIS's gate.

⛔ THE EXECUTOR IS NEVER THE APPROVER.
    A preparation agent drafts a launcher; a DIFFERENT model family decides whether it may
    be frozen. This module is the second half of that split. It invents no policy: the gate
    below is copied from pinned ARIS `skills/auto-review-loop/SKILL.md`.

        POSITIVE_THRESHOLD: score >= 6/10 AND verdict in {"ready", "almost"}
                            -- BOTH must hold.
        verdict vocabulary: {"ready", "almost", "not ready"}
        MAX_ROUNDS = 4
        REVIEW_DOC  = review-stage/AUTO_REVIEW.md   (cumulative)
        BACKEND     = codex   (OpenAI family; Claude drafts, Codex judges)

    `general/agreements/WORKING_AGREEMENT.md` WA-A.5 forbids weakening any of this,
    substituting a same-family reviewer, or lowering the threshold to get a pass. A launcher
    that does not reach the gate within MAX_ROUNDS is PARKED, never frozen.

The loop is: review -> repair findings -> re-review. The repair step is performed by the
drafting agent, but it can only ever change the launcher; it can never declare the launcher
acceptable. Only a reviewer verdict does that.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_ROUNDS = 4
MIN_SCORE = 6
POSITIVE_VERDICTS = {"ready", "almost"}
VERDICTS = {"ready", "almost", "not ready"}
REVIEW_DOC = Path("review-stage/AUTO_REVIEW.md")
REVIEWER_BACKEND = "codex"

REVIEW_PROMPT = """You are an INDEPENDENT ADVERSARIAL REVIEWER for a computational biology
programme. You did NOT write this launcher and you are not its advocate. Your job is to find
what is wrong with it before any compute is spent.

Review the TASK_LAUNCHER below. Judge ONLY the scientific specification, not prose style.

Check, and say plainly when one is missing or vague:
1. Is the question falsifiable, and is the success/failure criterion declared IN ADVANCE?
2. Is the population named, with an explicit denominator and inference unit? Are records
   independent, and if not is that stated?
3. Are the endpoints explicit, and fixed before execution rather than chosen after seeing data?
4. Are there real blocking controls, including a POSITIVE control that would catch a broken
   instrument and a NEGATIVE control that would catch a spurious signal?
5. Is there an interpretation ceiling that forbids over-claiming?
6. Is there circularity -- does anything validate itself, or is a threshold fitted to its own
   result?
7. Is any protected or already-exhausted population spent without explicit authorisation?
8. Could the stated outputs fail to answer the stated question?

Respond with a SINGLE JSON object and nothing else:

{"score": <integer 0-10>,
 "verdict": "ready" | "almost" | "not ready",
 "summary": "<one sentence>",
 "findings": [{"severity": "blocking" | "major" | "minor",
               "issue": "<what is wrong>",
               "required_change": "<the specific change that fixes it>"}]}

Scoring: 0-5 = not ready. 6-7 = almost, usable after the listed changes. 8-10 = ready.
Be strict. A launcher with no negative control, or with a criterion that could be chosen after
seeing results, is NOT ready regardless of how well written it is.

--- TASK_LAUNCHER UNDER REVIEW ---
{launcher}
--- END ---
{context}
"""


def utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def codex_available() -> bool:
    return shutil.which("codex") is not None


def _extract_json(text: str) -> dict | None:
    """Pull the reviewer's JSON out of whatever framing the CLI wrapped it in."""
    for m in re.finditer(r"\{(?:[^{}]|\{[^{}]*\})*\}", text, re.S):
        chunk = m.group(0)
        if '"verdict"' in chunk and '"score"' in chunk:
            try:
                d = json.loads(chunk)
                if isinstance(d, dict) and "score" in d and "verdict" in d:
                    return d
            except json.JSONDecodeError:
                continue
    return None


def review_once(launcher_text: str, context: str = "", timeout: int = 900) -> dict:
    """One adversarial pass. Returns a normalised verdict dict."""
    if not codex_available():
        return {"score": 0, "verdict": "not ready", "summary": "reviewer unavailable",
                "findings": [], "error": "codex CLI not found", "reviewer_ran": False}
    prompt = REVIEW_PROMPT.replace("{launcher}", launcher_text).replace("{context}", context)
    try:
        r = subprocess.run(["codex", "exec", "--skip-git-repo-check", prompt],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"score": 0, "verdict": "not ready", "summary": "reviewer timed out",
                "findings": [], "error": f"timeout after {timeout}s", "reviewer_ran": False}
    out = (r.stdout or "") + "\n" + (r.stderr or "")
    d = _extract_json(out)
    if d is None:
        return {"score": 0, "verdict": "not ready", "summary": "unparseable reviewer output",
                "findings": [], "error": out.strip()[-600:], "reviewer_ran": False}
    verdict = str(d.get("verdict", "")).strip().lower()
    if verdict not in VERDICTS:
        verdict = "not ready"
    try:
        score = int(d.get("score", 0))
    except (TypeError, ValueError):
        score = 0
    findings = [f for f in (d.get("findings") or []) if isinstance(f, dict)]
    return {"score": max(0, min(10, score)), "verdict": verdict,
            "summary": str(d.get("summary", ""))[:400], "findings": findings,
            "reviewer_ran": True, "reviewer": f"{REVIEWER_BACKEND}:adversarial-launcher-review"}


def accepted(v: dict) -> bool:
    """ARIS's gate, unmodified: score >= 6 AND verdict in {ready, almost}. BOTH."""
    return bool(v.get("reviewer_ran")) and v.get("score", 0) >= MIN_SCORE \
        and v.get("verdict") in POSITIVE_VERDICTS


def log_round(repo: Path, task_id: str, rnd: int, v: dict) -> None:
    doc = repo / REVIEW_DOC
    doc.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"\n## {task_id} — round {rnd} — {utc()}\n",
             f"- reviewer: `{v.get('reviewer', REVIEWER_BACKEND)}`",
             f"- score: **{v.get('score')}/10** · verdict: **{v.get('verdict')}** · "
             f"gate (>=6 AND ready|almost): **{'PASS' if accepted(v) else 'FAIL'}**",
             f"- summary: {v.get('summary', '')}"]
    if v.get("error"):
        lines.append(f"- ⛔ reviewer error: `{str(v['error'])[:300]}`")
    for f in v.get("findings", []):
        lines.append(f"  - **{f.get('severity', '?')}** — {f.get('issue', '')} "
                     f"→ _required:_ {f.get('required_change', '')}")
    with doc.open("a") as fh:
        fh.write("\n".join(lines) + "\n")


def findings_brief(v: dict) -> str:
    out = []
    for f in v.get("findings", []):
        out.append(f"- [{f.get('severity','?')}] {f.get('issue','')}\n  REQUIRED: {f.get('required_change','')}")
    return "\n".join(out) or "(reviewer listed no specific findings; raise the specification quality)"


def main() -> int:
    ap = argparse.ArgumentParser(description="Adversarially review one TASK_LAUNCHER.md.")
    ap.add_argument("launcher", type=Path)
    ap.add_argument("--task-id", default="")
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--context", default="")
    ap.add_argument("--json-out", type=Path)
    a = ap.parse_args()
    tid = a.task_id or a.launcher.parent.name
    v = review_once(a.launcher.read_text(), a.context)
    log_round(a.repo, tid, a.round, v)
    if a.json_out:
        a.json_out.write_text(json.dumps(v, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"task_id": tid, "round": a.round, "score": v["score"],
                      "verdict": v["verdict"], "accepted": accepted(v),
                      "summary": v.get("summary", "")}, indent=2))
    return 0 if accepted(v) else 1


if __name__ == "__main__":
    sys.exit(main())
