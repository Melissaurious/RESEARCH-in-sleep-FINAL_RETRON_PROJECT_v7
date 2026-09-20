#!/usr/bin/env python3
"""Unit/failure-injection tests for the thin autonomous execution layer.

No project data is opened and no live process is touched.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from autonomy_state import (  # noqa: E402
    TERMINAL,
    TERMINAL_EXECUTOR,
    TERMINAL_INVALID,
    TERMINAL_VALID,
    ScheduleTask,
    choose_launchable,
    executor_terminal_state,
    sha256_file,
)
import task_worker  # noqa: E402
import wave_runner  # noqa: E402


class ArisAcceptanceBoundaryTests(unittest.TestCase):
    """The runner must not acquit a task past ARIS's acceptance gate.

    Pinned ARIS tools/run_state.py lets only `accept` write `accepted`, and only with a
    verdict id and a named reviewer. PASS is this project's accepted state, so a worker
    self-report may never produce it.
    """

    def test_self_reported_success_is_not_an_acceptance(self):
        self.assertEqual(executor_terminal_state("PASS"), "COMPLETE_AWAITING_REVIEW")
        self.assertNotIn("COMPLETE_AWAITING_REVIEW", TERMINAL_VALID)

    def test_self_reported_failure_is_kept_verbatim(self):
        for bad in sorted(TERMINAL_INVALID):
            self.assertEqual(executor_terminal_state(bad), bad)

    def test_awaiting_review_does_not_satisfy_a_hard_dependency(self):
        tasks = [ScheduleTask("descendant", "AUTHORIZED", 1, hard_dependencies=("producer",))]
        _, decisions = choose_launchable(
            tasks, {"producer": "COMPLETE_AWAITING_REVIEW"}, running_tokens=0, total_tokens=8)
        self.assertTrue(decisions["descendant"].startswith("WAIT_DEP"))

    def test_awaiting_review_does_satisfy_lane_ordering(self):
        """schedule_after is an I/O lane constraint, not a scientific dependency."""
        tasks = [ScheduleTask("second", "AUTHORIZED", 1, schedule_after=("first",))]
        selected, _ = choose_launchable(
            tasks, {"first": "COMPLETE_AWAITING_REVIEW"}, running_tokens=0, total_tokens=8)
        self.assertEqual(selected, ["second"])

    def test_awaiting_review_does_not_block_descendants(self):
        self.assertNotIn("COMPLETE_AWAITING_REVIEW", TERMINAL_INVALID)
        self.assertTrue(TERMINAL_EXECUTOR <= TERMINAL)

    def test_accept_is_reachable_only_from_the_deterministic_validator(self):
        """ARIS allows a DETERMINISTIC VERIFIER to accept -- but never a self-report."""
        src = (HERE / "wave_runner.py").read_text()
        self.assertEqual(src.count("aris('accept'"), 1)
        self.assertIn("def aris_accept", src)
        # the only caller is deterministic_accept(), after validate_type_a_execution()
        after = src.split("def deterministic_accept", 1)[1]
        self.assertIn("aris_accept(w,tid,vid,DET_REVIEWER)", after)
        self.assertIn("validate_type_a_execution", after)

    def test_deterministic_acceptance_requires_verdict_and_reviewer(self):
        src = (HERE / "wave_runner.py").read_text()
        self.assertIn("'--verdict-id',verdict_id,'--reviewer',reviewer", src)

    def test_spawn_clears_a_previous_attempts_runtime_record(self):
        """A stale record must never be read as the current attempt's outcome.

        A re-run of T-R2a was voided by a 20-minute-old record because launch_task.sh
        refused before the worker wrote a new one.
        """
        src = (HERE / "wave_runner.py").read_text()
        spawn = src.split("def spawn(", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("rec.unlink(missing_ok=True)", spawn)


class PrepareResultShapeTests(unittest.TestCase):
    """Regression for BLOCKED_PREPARE: 'str' object has no attribute 'get'.

    T-A23d wrote self_checks as a DICT. Iterating a dict yields its KEYS, so the old
    `x.get('state')` ran against a string and the prepared task was wrongly refused.
    """

    #: the exact shape T-A23d-primary-verification emitted
    A23D = {
        "schema_version": 1,
        "status": "READY_TO_FREEZE",
        "task_id": "T-A23d-primary-verification",
        "command": {"cwd": "/w", "argv": ["python", "a23d_resolve.py", "--outdir", "out"],
                    "network_egress_required": ["www.ebi.ac.uk"]},
        "inputs": [],
        "backend": "workstation",
        "resources": {"cpu_threads": 1, "memory_gb": 2, "io_tokens": 1},
        "runtime": {"max_runtime_seconds": 3600, "resume_allowed": False, "stop_note": ""},
        "self_checks": {
            "harness": "selfcheck_a23d.py", "passed": 24, "failed": 0, "exit_code": 0,
            "checks": [{"id": "SC01", "state": "PASS", "detail": "7 cases"},
                       {"id": "SC02", "state": "PASS", "detail": "regression"}],
        },
    }

    def test_dict_self_checks_no_longer_raises_str_has_no_get(self):
        d = wave_runner.normalise_prepare_result(json.loads(json.dumps(self.A23D)))
        self.assertTrue(wave_runner.self_checks_all_pass(d["self_checks"]))

    def test_nested_argv_and_backend_alias_are_normalised(self):
        d = wave_runner.normalise_prepare_result(json.loads(json.dumps(self.A23D)))
        self.assertEqual(d["command"][0], "python")
        self.assertEqual(d["backend"], "local")
        # and the result must satisfy the execution-spec contract downstream
        self.assertIsInstance(d["command"], list)

    def test_a_failing_self_check_is_still_refused(self):
        raw = json.loads(json.dumps(self.A23D))
        raw["self_checks"]["checks"][1]["state"] = "FAIL"
        d = wave_runner.normalise_prepare_result(raw)
        self.assertFalse(wave_runner.self_checks_all_pass(d["self_checks"]))

    def test_declared_failure_count_overrides_passing_rows(self):
        raw = json.loads(json.dumps(self.A23D))
        raw["self_checks"]["failed"] = 2
        d = wave_runner.normalise_prepare_result(raw)
        self.assertFalse(wave_runner.self_checks_all_pass(d["self_checks"]))

    def test_bare_string_checks_are_not_treated_as_passes(self):
        raw = json.loads(json.dumps(self.A23D))
        raw["self_checks"] = ["ran the fixtures", "looked fine"]
        d = wave_runner.normalise_prepare_result(raw)
        self.assertFalse(wave_runner.self_checks_all_pass(d["self_checks"]))

    def test_unknown_backend_is_refused(self):
        raw = json.loads(json.dumps(self.A23D))
        raw["backend"] = "someone_elses_gpu"
        with self.assertRaises(ValueError):
            wave_runner.normalise_prepare_result(raw)


class TypeAAcceptanceTests(unittest.TestCase):
    """A preregistered Type-A computation must self-clear on execution validity alone."""

    def _finished_task(self, root: Path, *, controls_pass=True, tamper_input=False):
        wt = root / "wt"
        (wt / "programme" / "tasks" / "T-SYN").mkdir(parents=True)
        (wt / "programme" / "tasks" / "T-SYN" / "TASK_LAUNCHER.md").write_text(
            "---\ntask_id: T-SYN\nautonomy_tier: A\nfrozen: true\n"
            "output_directory: analysis/t_syn/\n---\n# synthetic\n")
        out = wt / "analysis" / "t_syn"
        (out / "logs").mkdir(parents=True)
        (out / "TASK_REPORT.md").write_text(
            "TASK_STATE: PASS\nSCIENTIFIC_OUTCOME: DESCRIPTIVE\n")
        (out / "logs" / "run_log.json").write_text(json.dumps({"inputs": []}))
        (out / "result.tsv").write_text("value\n42\n")
        (out / "SYN_controls.tsv").write_text(
            "check\tblocking\tresult\nc1\tYES\t" + ("PASS" if controls_pass else "FAIL") + "\n")
        lines = []
        for rel in ("TASK_REPORT.md", "logs/run_log.json", "result.tsv", "SYN_controls.tsv"):
            lines.append(f"{sha256_file(out / rel)}  {rel}")
        (out / "OUTPUT_MANIFEST.sha256").write_text("\n".join(lines) + "\n")
        inp = root / "input.csv"
        inp.write_text("a,b\n1,2\n")
        inp_sha = sha256_file(inp)
        # Freeze ONLY the launcher, then leave the outputs untracked -- exactly how a real
        # run leaves its worktree. Acceptance must not mistake untracked output for tampering.
        subprocess.run(["git", "init", "-q", "-b", "task/T-SYN"], cwd=wt, check=True,
                       capture_output=True)
        subprocess.run(["git", "add", "programme"], cwd=wt, check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-q", "-m", "freeze"], cwd=wt, check=True, capture_output=True)
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt, text=True,
                              capture_output=True, check=True).stdout.strip()
        if tamper_input:
            inp.write_text("a,b\n9,9\n")
        spec = {
            "task_id": "T-SYN", "worktree": str(wt), "branch": "task/T-SYN",
            "freeze_commit": head, "output_directory": "analysis/t_syn",
            "inputs": [{"dataset_id": "SYN", "path": str(inp), "sha256": inp_sha}],
            "frozen_files": {"programme/tasks/T-SYN/TASK_LAUNCHER.md": sha256_file(
                wt / "programme" / "tasks" / "T-SYN" / "TASK_LAUNCHER.md")},
        }
        return spec, wt, out

    def test_valid_type_a_run_is_accepted_without_a_semantic_reviewer(self):
        with tempfile.TemporaryDirectory() as td:
            spec, wt, out = self._finished_task(Path(td))
            ok, checks = wave_runner.validate_type_a_execution(spec, wt, out)
            self.assertTrue(ok, [c for c in checks if c["result"] == "FAIL"])

    def test_failed_blocking_control_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            spec, wt, out = self._finished_task(Path(td), controls_pass=False)
            ok, checks = wave_runner.validate_type_a_execution(spec, wt, out)
            self.assertFalse(ok)
            self.assertIn("blocking_controls_pass",
                          [c["check"] for c in checks if c["result"] == "FAIL"])

    def test_input_hash_drift_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            spec, wt, out = self._finished_task(Path(td), tamper_input=True)
            ok, checks = wave_runner.validate_type_a_execution(spec, wt, out)
            self.assertFalse(ok)
            self.assertIn("input_hashes",
                          [c["check"] for c in checks if c["result"] == "FAIL"])

    def test_non_type_a_task_still_waits_for_semantic_review(self):
        with tempfile.TemporaryDirectory() as td:
            spec, wt, out = self._finished_task(Path(td))
            p = wt / "programme" / "tasks" / "T-SYN" / "TASK_LAUNCHER.md"
            p.write_text(p.read_text().replace("autonomy_tier: A", "autonomy_tier: B"))
            self.assertIsNone(wave_runner.deterministic_accept("T-SYN", spec, out, {}))


class SchedulerTests(unittest.TestCase):
    def test_two_lightweight_tasks_fit_beside_heavy_external_lane(self):
        tasks = [
            ScheduleTask("light-a", "AUTHORIZED", 1),
            ScheduleTask("light-b", "AUTHORIZED", 1),
            ScheduleTask("medium", "AUTHORIZED", 3),
        ]
        selected, decisions = choose_launchable(tasks, {}, running_tokens=6, total_tokens=8)
        self.assertEqual(selected, ["light-a", "light-b"])
        self.assertTrue(decisions["medium"].startswith("WAIT_RESOURCE"))

    def test_failed_task_blocks_only_hard_descendant(self):
        tasks = [
            ScheduleTask("descendant", "AUTHORIZED", 1, hard_dependencies=("producer",)),
            ScheduleTask("unrelated", "AUTHORIZED", 1),
        ]
        selected, decisions = choose_launchable(
            tasks, {"producer": "VOID"}, running_tokens=0, total_tokens=8
        )
        self.assertEqual(selected, ["unrelated"])
        self.assertTrue(decisions["descendant"].startswith("BLOCKED_DEPENDENCY"))

    def test_unfinished_dependency_waits(self):
        task = ScheduleTask("child", "AUTHORIZED", 1, hard_dependencies=("parent",))
        selected, decisions = choose_launchable([task], {"parent": "RUNNING"}, 0, 8)
        self.assertEqual(selected, [])
        self.assertTrue(decisions["child"].startswith("WAIT_DEP"))

    def test_schedule_after_is_ordering_not_scientific_dependency(self):
        task = ScheduleTask("second", "AUTHORIZED", 8, schedule_after=("first",))
        selected, _ = choose_launchable([task], {"first": "VOID"}, 0, 8)
        self.assertEqual(selected, ["second"])


class RunnerLaunchTests(unittest.TestCase):
    def test_spawn_uses_programme_path_without_shadowing(self):
        with tempfile.TemporaryDirectory() as td:
            wave = Path(td) / "wave" / "WAVE.tsv"
            wave.parent.mkdir(parents=True)
            spec = Path(td) / "TASK_EXECUTION.json"
            spec.write_text("{}\n")
            seen = {}
            class Dummy:
                pid = 4242
            old = wave_runner.subprocess.Popen
            def fake(cmd, **kwargs):
                seen["cmd"] = cmd
                return Dummy()
            wave_runner.subprocess.Popen = fake
            try:
                proc, rec = wave_runner.spawn("T-SYNTH", spec, wave)
            finally:
                wave_runner.subprocess.Popen = old
            self.assertEqual(proc.pid, 4242)
            self.assertEqual(seen["cmd"][0], "bash")
            self.assertTrue(str(seen["cmd"][1]).endswith("programme/launch_task.sh"))
            self.assertEqual(seen["cmd"][2:4], ["T-SYNTH", "--execute"])
            self.assertTrue(str(rec).endswith("runs/T-SYNTH.json"))


class WorkerIntegrityTests(unittest.TestCase):
    def _repo(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "autonomy@test.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Autonomy Test"], cwd=root, check=True)
        subprocess.run(["git", "checkout", "-q", "-b", "task/T-SYNTH"], cwd=root, check=True)
        taskdir = root / "programme/tasks/T-SYNTH"
        taskdir.mkdir(parents=True)
        out = root / "analysis/t_synth"
        input_path = root.parent / (root.name + "-input.txt")
        input_path.write_text("immutable input\n")
        script = taskdir / "run.py"
        script.write_text(textwrap.dedent(r'''
            from pathlib import Path
            import hashlib, json
            root = Path.cwd()
            out = root / "analysis/t_synth"
            (out / "logs").mkdir(parents=True, exist_ok=True)
            (out / "tables").mkdir(parents=True, exist_ok=True)
            (out / "tables/value.tsv").write_text("quantity\tvalue\nanswer\t42\n")
            (out / "logs/run_log.json").write_text(json.dumps({"test": True}) + "\n")
            (out / "TASK_REPORT.md").write_text(
                "# TASK REPORT — T-SYNTH\n\nTASK_STATE: PASS\nSCIENTIFIC_OUTCOME: DESCRIPTIVE\n"
            )
            files = ["tables/value.tsv", "logs/run_log.json", "TASK_REPORT.md"]
            lines = []
            for rel in files:
                b = (out / rel).read_bytes()
                lines.append(hashlib.sha256(b).hexdigest() + "  " + rel)
            (out / "OUTPUT_MANIFEST.sha256").write_text("\n".join(lines) + "\n")
        '''))
        launcher = taskdir / "TASK_LAUNCHER.md"
        launcher.write_text("---\ntask_id: T-SYNTH\nfrozen: true\n---\n")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "freeze"], cwd=root, check=True)
        freeze = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        frozen_files = {
            str(script.relative_to(root)): sha256_file(script),
            str(launcher.relative_to(root)): sha256_file(launcher),
        }
        spec = {
            "schema_version": 1,
            "task_id": "T-SYNTH",
            "worktree": str(root),
            "branch": "task/T-SYNTH",
            "freeze_commit": freeze,
            "command": [sys.executable, "programme/tasks/T-SYNTH/run.py"],
            "inputs": [{
                "dataset_id": "SYNTH",
                "path": str(input_path),
                "sha256": sha256_file(input_path),
            }],
            "output_directory": "analysis/t_synth/",
            "backend": "local",
            "resources": {"cpu_threads": 1, "memory_gb": 1, "io_tokens": 1},
            "runtime": {"max_runtime_seconds": 30, "resume_allowed": False, "stop_note": "test"},
            "frozen_files": frozen_files,
        }
        return td, root, input_path, script, spec

    def test_synthetic_pass_runs_and_validates(self):
        td, root, input_path, script, spec = self._repo()
        try:
            record = root.parent / (root.name + "-run.json")
            rc = task_worker.run_local(spec, record)
            self.assertEqual(rc, 0)
            data = json.loads(record.read_text())
            self.assertEqual(data["worker_state"], "COMPLETE")
            self.assertEqual(data["task_state"], "PASS")
        finally:
            td.cleanup()
            input_path.unlink(missing_ok=True)

    def test_frozen_hash_mismatch_refuses_before_command(self):
        td, root, input_path, script, spec = self._repo()
        try:
            script.write_text(script.read_text() + "\n# post-freeze mutation\n")
            marker = root / "analysis/t_synth/tables/value.tsv"
            record = root.parent / (root.name + "-run.json")
            with self.assertRaises(RuntimeError):
                task_worker.run_local(spec, record)
            self.assertFalse(marker.exists(), "primary command must not run after frozen-file mutation")
        finally:
            td.cleanup()
            input_path.unlink(missing_ok=True)

    def test_input_hash_mismatch_refuses_before_command(self):
        td, root, input_path, script, spec = self._repo()
        try:
            input_path.write_text("mutated input\n")
            marker = root / "analysis/t_synth/tables/value.tsv"
            record = root.parent / (root.name + "-run.json")
            with self.assertRaises(RuntimeError):
                task_worker.run_local(spec, record)
            self.assertFalse(marker.exists())
        finally:
            td.cleanup()
            input_path.unlink(missing_ok=True)


class BrokerPoolTests(unittest.TestCase):
    """BORG and Ibex are two pools, accounted separately, usable at the same time."""

    def _b(self, **kw):
        from resource_broker import Broker
        b = Broker(probe=False, **kw)
        return b

    def test_local_and_ibex_budgets_are_separate(self):
        from resource_broker import Broker, IbexPool
        b = Broker(nvme_capacity=8, ibex_capacity=4, probe=False)
        b._ibex = IbexPool(reachable=True, capacity=4, submitted=0, idle_nodes=10, env_present=True)
        b._ibex_at = 1e18
        # local saturated, ibex free -> the task still runs, on ibex
        p = b.plan("t", io_tokens=3, declared_backend="auto", nvme_used=8)
        self.assertEqual(p.backend, "ibex")
        self.assertEqual((p.nvme_cost, p.ibex_cost), (1, 1))

    def test_ibex_budget_is_enforced(self):
        from resource_broker import Broker, IbexPool
        b = Broker(nvme_capacity=8, ibex_capacity=4, probe=False)
        b._ibex = IbexPool(reachable=True, capacity=4, submitted=4, idle_nodes=10, env_present=True)
        b._ibex_at = 1e18
        p = b.plan("t", io_tokens=3, declared_backend="auto", nvme_used=8)
        self.assertEqual(p.backend, "defer")  # local full AND ibex budget exhausted

    def test_unreachable_ibex_is_a_normal_answer(self):
        from resource_broker import Broker, IbexPool
        b = Broker(probe=False)
        b._ibex = IbexPool(reachable=False); b._ibex_at = 1e18
        self.assertEqual(b.plan("t", io_tokens=1, nvme_used=0).backend, "local")

    def test_whole_pool_task_prefers_ibex_over_draining_borg(self):
        from resource_broker import Broker, IbexPool
        b = Broker(nvme_capacity=8, ibex_capacity=4, probe=False)
        b._ibex = IbexPool(reachable=True, capacity=4, submitted=0, idle_nodes=10, env_present=True)
        b._ibex_at = 1e18
        self.assertEqual(b.plan("m1b", io_tokens=8, nvme_used=2).backend, "ibex")

    def test_starvation_opens_an_exclusive_local_window(self):
        from resource_broker import Broker, IbexPool, EXCLUSIVE_AGE_CYCLES
        b = Broker(nvme_capacity=8, ibex_capacity=4, probe=False)
        b._ibex = IbexPool(reachable=False); b._ibex_at = 1e18   # no Ibex escape hatch
        p = None
        for _ in range(EXCLUSIVE_AGE_CYCLES):
            p = b.plan("m1b", io_tokens=8, nvme_used=7)
        self.assertEqual(p.backend, "defer")
        self.assertTrue(p.drain, "an aged whole-pool task must trigger a drain window")

    def test_terminal_tasks_release_their_resources(self):
        from resource_broker import Broker
        b = Broker(nvme_capacity=8, probe=False)
        self.assertEqual(b.plan("t", io_tokens=8, nvme_used=8).backend, "defer")
        self.assertEqual(b.plan("t", io_tokens=8, nvme_used=0).backend, "local")


class ReviewGateTests(unittest.TestCase):
    """ARIS's gate, unmodified: score >= 6 AND verdict in {ready, almost}."""

    def test_gate_requires_both_score_and_verdict(self):
        import launcher_review as lr
        self.assertTrue(lr.accepted({"score": 6, "verdict": "almost", "reviewer_ran": True}))
        self.assertTrue(lr.accepted({"score": 9, "verdict": "ready", "reviewer_ran": True}))
        self.assertFalse(lr.accepted({"score": 9, "verdict": "not ready", "reviewer_ran": True}))
        self.assertFalse(lr.accepted({"score": 5, "verdict": "ready", "reviewer_ran": True}))

    def test_a_reviewer_that_never_ran_is_never_a_pass(self):
        import launcher_review as lr
        self.assertFalse(lr.accepted({"score": 10, "verdict": "ready", "reviewer_ran": False}))

    def test_launcher_cannot_self_approve(self):
        """Only a reviewer verdict may freeze; the drafting agent has no such path."""
        src = (HERE / "wave_runner.py").read_text()
        body = src.split("for tid,(rproc,wt,d,rnd,jf,cost) in list(reviewing.items()):", 1)[1]
        self.assertIn("_lr.accepted(v)", body)
        freeze_calls = [ln for ln in src.splitlines() if "fr,sp=freeze(" in ln]
        self.assertTrue(freeze_calls, "freeze must exist")
        for ln in freeze_calls:  # every freeze site lives in the review-collection branch
            self.assertNotIn("prepare_finish", ln)

    def test_gate_constants_match_pinned_aris(self):
        import launcher_review as lr
        self.assertEqual((lr.MIN_SCORE, lr.MAX_ROUNDS), (6, 4))
        self.assertEqual(lr.POSITIVE_VERDICTS, {"ready", "almost"})


class ArtefactContractTests(unittest.TestCase):
    def _task(self, root: Path, body: str) -> Path:
        d = root / "T-XX-demo"; d.mkdir(parents=True)
        (d / "TASK_LAUNCHER.md").write_text("---\noutput_directory: out/\n---\nemits XX_primary.tsv and XX_controls.tsv\n")
        (d / "run.py").write_text(body)
        return d

    def test_missing_task_report_is_caught_before_freeze(self):
        import artefact_contract as ac
        with tempfile.TemporaryDirectory() as td:
            d = self._task(Path(td), "open('out/XX_primary.tsv','w');open('out/XX_controls.tsv','w')\n"
                                     "open('out/OUTPUT_MANIFEST.sha256','w');open('out/run_log.json','w')\n")
            ok, checks = ac.check(d, d / "TASK_LAUNCHER.md")
            self.assertFalse(ok)
            self.assertIn("emits:TASK_REPORT.md", [c["check"] for c in checks if c["result"] == "FAIL"])

    def test_complete_implementation_passes(self):
        import artefact_contract as ac
        with tempfile.TemporaryDirectory() as td:
            d = self._task(Path(td), "open('out/XX_primary.tsv','w');open('out/XX_controls.tsv','w')\n"
                                     "open('out/OUTPUT_MANIFEST.sha256','w');open('out/run_log.json','w')\n"
                                     "open('out/TASK_REPORT.md','w').write('TASK_STATE: PASS\\nSCIENTIFIC_OUTCOME: DESCRIPTIVE\\n')\n")
            ok, checks = ac.check(d, d / "TASK_LAUNCHER.md")
            self.assertTrue(ok, [c for c in checks if c["result"] == "FAIL"])

    def test_report_without_machine_fields_is_caught(self):
        import artefact_contract as ac
        with tempfile.TemporaryDirectory() as td:
            d = self._task(Path(td), "open('out/XX_primary.tsv','w');open('out/XX_controls.tsv','w')\n"
                                     "open('out/OUTPUT_MANIFEST.sha256','w');open('out/run_log.json','w')\n"
                                     "open('out/TASK_REPORT.md','w').write('# report')\n")
            ok, checks = ac.check(d, d / "TASK_LAUNCHER.md")
            self.assertFalse(ok)
            self.assertIn("report_field:TASK_STATE", [c["check"] for c in checks if c["result"] == "FAIL"])

    def test_an_input_file_is_not_demanded_as_an_output(self):
        """T-D1 failed this check on GOVERNANCE_BASE.tsv, which it only reads."""
        import artefact_contract as ac
        with tempfile.TemporaryDirectory() as td:
            d = self._task(Path(td), "open('out/XX_primary.tsv','w');open('out/XX_controls.tsv','w')\n"
                                     "open('out/OUTPUT_MANIFEST.sha256','w');open('out/run_log.json','w')\n"
                                     "open('out/TASK_REPORT.md','w').write('TASK_STATE: PASS\\nSCIENTIFIC_OUTCOME: BOUND\\n')\n")
            (d / "TASK_LAUNCHER.md").write_text(
                "---\noutput_directory: out/\n---\nreads GOVERNANCE_BASE.tsv and support.csv;"
                " emits XX_primary.tsv and XX_controls.tsv\n")
            ok, checks = ac.check(d, d / "TASK_LAUNCHER.md")
            self.assertTrue(ok, [c for c in checks if c["result"] == "FAIL"])


class TransientRetryTests(unittest.TestCase):
    """Mechanical failures retry; scientific failures never do."""

    def test_known_transient_signatures_are_recognised(self):
        import wave_runner as wr
        self.assertIn("specs_exist.sh did not pass", wr.TRANSIENT_SIGNATURES)
        self.assertTrue(any("slurm" in s.lower() or "sbatch" in s.lower() for s in wr.TRANSIENT_SIGNATURES))

    def test_a_failed_scientific_control_is_not_transient(self):
        import wave_runner as wr
        for bad in ("blocking controls did not all PASS", "control failure", "criterion not met"):
            self.assertFalse(any(sig in bad for sig in wr.TRANSIENT_SIGNATURES))

    def test_retry_only_when_no_run_record_exists(self):
        src = (HERE / "wave_runner.py").read_text()
        self.assertIn("sig=transient_reason(tid,w) if not rec.exists() else ''", src)
        self.assertIn("MAX_TRANSIENT_RETRIES", src)


class DurableStateTests(unittest.TestCase):
    """Restart recovery must come from disk, never from conversation or memory."""

    def test_status_is_reloaded_from_disk_at_start(self):
        src = (HERE / "wave_runner.py").read_text()
        self.assertIn("st=load_status(w)", src)

    def test_in_flight_sets_start_empty_so_restart_reconciles(self):
        src = (HERE / "wave_runner.py").read_text()
        self.assertIn("workers={}; preparing={}; reviewing={}; repairing={}", src)

    def test_loop_exit_waits_for_every_in_flight_stage(self):
        src = (HERE / "wave_runner.py").read_text()
        self.assertIn("if not workers and not preparing and not reviewing and not repairing:", src)



class AuthoringCostTests(unittest.TestCase):
    """Writing a launcher must not reserve the task's execution I/O budget.

    T-M1b, routed to Ibex and merely PREPARING, reserved all 8 LOCAL tokens and starved
    T-A23d -- head-of-line blocking reintroduced through the resource account.
    """

    def test_authoring_costs_one_token(self):
        import wave_runner as wr
        self.assertEqual(wr.AUTHORING_COST, 1)

    def test_prepare_reserves_authoring_cost_not_execution_budget(self):
        src = (HERE / "wave_runner.py").read_text()
        line = [l for l in src.splitlines() if "preparing[tid]=(proc,wt," in l][0]
        self.assertIn("AUTHORING_COST", line)
        self.assertNotIn("int(r['io_tokens'])", line)

    def test_execution_still_reserves_the_real_cost(self):
        src = (HERE / "wave_runner.py").read_text()
        line = [l for l in src.splitlines() if "workers[tid]=(p,rec," in l][0]
        self.assertIn("int(r['io_tokens'])", line)

if __name__ == "__main__":
    unittest.main(verbosity=2)
