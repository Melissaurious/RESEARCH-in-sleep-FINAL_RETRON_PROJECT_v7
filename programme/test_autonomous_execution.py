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

from autonomy_state import ScheduleTask, choose_launchable, sha256_file  # noqa: E402
import task_worker  # noqa: E402
import wave_runner  # noqa: E402


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
