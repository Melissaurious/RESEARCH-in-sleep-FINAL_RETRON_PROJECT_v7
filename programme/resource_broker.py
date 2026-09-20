#!/usr/bin/env python3
"""Live resource broker: two execution pools, one admission decision.

WHY THIS EXISTS
    The scheduler had exactly one dimension -- NVME_TOKENS -- so Ibex was unreachable in
    practice: an Ibex-bound task would still have consumed local I/O tokens, and local
    capacity would have throttled cluster work. WAVE.tsv carried a `backend` column that
    nothing read, while PREPARE_RESULT silently decided the backend. That ambiguity is
    replaced here by ONE authoritative routing mechanism.

WHAT IT DOES NOT DO
    ⛔ It never touches science. Backend, thread count, memory, batching and retry shape are
    LOGISTICS. A frozen scientific endpoint is not a broker input and is never a broker
    output. The broker reads a task's DECLARED resource class; it does not interpret its
    question.

POOLS
    local : NVME_TOKENS (governed), plus live CPU / RAM / GPU headroom.
    ibex  : IBEX_SUBMISSIONS (governed concurrency budget), plus live reachability and
            queue depth. Staging still costs a local token, exactly as RESOURCE_LIMITS says.

STARVATION
    An IO_HIGH task needing the whole local budget cannot win a race against a stream of
    1-token jobs. `reserve_exclusive` ages such a task: once it has waited past a threshold
    the broker stops admitting new local work and drains, so the window opens. The same task
    may instead be routed to Ibex, which needs no local window at all.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

IBEX_HOST = os.environ.get("RETRON_IBEX_HOST", "rioszemm@ilogin.ibex.kaust.edu.sa")
IBEX_ENV = "/ibex/user/rioszemm/conda-environments/retron_tradicional"
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15"]

#: A task waiting this many scheduling cycles for an exclusive local window starts draining
#: the pool instead of losing every race to cheaper work.
EXCLUSIVE_AGE_CYCLES = 3
#: Probes are cached this long; a scheduling loop runs far faster than cluster state changes.
PROBE_TTL_SECONDS = 60


@dataclass
class LocalPool:
    nvme_capacity: int = 8
    nvme_used: int = 0
    cpu_threads: int = 44
    cpu_busy_threads: int = 0
    mem_available_gb: float = 0.0
    gpu_free: int = 0
    load1: float = 0.0

    @property
    def nvme_free(self) -> int:
        return max(0, self.nvme_capacity - self.nvme_used)


@dataclass
class IbexPool:
    reachable: bool = False
    capacity: int = 4
    submitted: int = 0
    idle_nodes: int = 0
    env_present: bool = False
    detail: str = ""

    @property
    def slots_free(self) -> int:
        return max(0, self.capacity - self.submitted) if self.reachable else 0


@dataclass
class Plan:
    task_id: str
    backend: str          # "local" | "ibex" | "defer"
    reason: str
    nvme_cost: int = 0
    ibex_cost: int = 0
    cpu_threads: int = 1
    memory_gb: int = 4
    array_size: int = 0
    drain: bool = False   # when True the broker is holding the local pool open for this task
    extra: dict = field(default_factory=dict)


def _run(cmd, timeout=40):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        class _R:
            returncode, stdout, stderr = 1, "", str(exc)
        return _R()


def probe_local(nvme_capacity: int, nvme_used: int, cpu_capacity: int = 44) -> LocalPool:
    """Live BORG capacity. Every field degrades to a safe default rather than raising."""
    p = LocalPool(nvme_capacity=nvme_capacity, nvme_used=nvme_used, cpu_threads=cpu_capacity)
    try:
        p.load1 = os.getloadavg()[0]
    except OSError:
        p.load1 = 0.0
    p.cpu_busy_threads = int(min(p.load1, cpu_capacity))
    try:
        meminfo = dict(
            (k.strip(), v) for k, v in
            (ln.split(":", 1) for ln in Path("/proc/meminfo").read_text().splitlines() if ":" in ln))
        p.mem_available_gb = int(meminfo.get("MemAvailable", "0 kB").split()[0]) / 1_048_576
    except Exception:  # noqa: BLE001
        p.mem_available_gb = 0.0
    if shutil.which("nvidia-smi"):
        r = _run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], 20)
        if r.returncode == 0:
            # A device under ~1 GiB is idle for our purposes.
            p.gpu_free = sum(1 for ln in r.stdout.split() if ln.strip().isdigit() and int(ln) < 1024)
    return p


def probe_ibex(capacity: int) -> IbexPool:
    """Live Ibex state. Unreachable is a normal answer, not an error."""
    pool = IbexPool(capacity=capacity)
    probe = ('echo "JOBS=$(squeue --me -h 2>/dev/null | wc -l)"; '
             'echo "IDLE=$(sinfo -h -p batch -t idle -o %D 2>/dev/null | paste -sd+ | bc 2>/dev/null)"; '
             f'echo "ENV=$(test -d {IBEX_ENV} && echo yes || echo no)"')
    r = _run(SSH + [IBEX_HOST, probe], timeout=45)
    if r.returncode != 0:
        pool.detail = (r.stderr or "unreachable").strip()[:160]
        return pool
    pool.reachable = True
    for line in r.stdout.splitlines():
        if line.startswith("JOBS="):
            pool.submitted = int(line[5:] or 0)
        elif line.startswith("IDLE="):
            pool.idle_nodes = int(line[5:] or 0) if (line[5:] or "").strip().isdigit() else 0
        elif line.startswith("ENV="):
            pool.env_present = line[4:].strip() == "yes"
    pool.detail = f"idle_nodes={pool.idle_nodes} submitted={pool.submitted} env={pool.env_present}"
    return pool


class Broker:
    """Holds pool state and makes one admission+routing decision per task."""

    def __init__(self, nvme_capacity=8, ibex_capacity=4, cpu_capacity=44, probe=True):
        self.nvme_capacity = nvme_capacity
        self.ibex_capacity = ibex_capacity
        self.cpu_capacity = cpu_capacity
        self._probe = probe
        self._ibex: IbexPool | None = None
        self._ibex_at = 0.0
        self.waiting: dict[str, int] = {}

    def ibex(self) -> IbexPool:
        # A pool already known (injected, or probed within the TTL) always wins; only an
        # unknown pool triggers a probe, and only when probing is enabled.
        if self._ibex is not None and (not self._probe or time.time() - self._ibex_at <= PROBE_TTL_SECONDS):
            return self._ibex
        if not self._probe:
            return IbexPool(capacity=self.ibex_capacity)
        now = time.time()
        if self._ibex is None or now - self._ibex_at > PROBE_TTL_SECONDS:
            self._ibex = probe_ibex(self.ibex_capacity)
            self._ibex_at = now
        return self._ibex

    def local(self, nvme_used: int) -> LocalPool:
        if not self._probe:
            return LocalPool(nvme_capacity=self.nvme_capacity, nvme_used=nvme_used,
                             cpu_threads=self.cpu_capacity, mem_available_gb=999, gpu_free=2)
        return probe_local(self.nvme_capacity, nvme_used, self.cpu_capacity)

    # -- routing ---------------------------------------------------------
    def plan(self, task_id: str, *, io_tokens: int, declared_backend: str = "auto",
             cpu_threads: int = 1, memory_gb: int = 4, gpu: bool = False,
             ibex_eligible: bool = True, nvme_used: int = 0,
             local_running: int = 0) -> Plan:
        """Choose a backend and shape for ONE task. Never consults its science."""
        local = self.local(nvme_used)
        want = (declared_backend or "auto").strip().lower()

        # An explicit, governed backend is honoured; only "auto" is brokered.
        if want == "ibex":
            ib = self.ibex()
            if ib.slots_free > 0 and ib.env_present:
                return Plan(task_id, "ibex", f"declared ibex; {ib.detail}", 1, 1, cpu_threads, memory_gb)
            self._age(task_id)
            return Plan(task_id, "defer", f"declared ibex but unavailable: {ib.detail or 'no slot'}")
        if want == "local":
            if io_tokens <= local.nvme_free:
                return Plan(task_id, "local", "declared local", io_tokens, 0, cpu_threads, memory_gb)
            return self._defer_or_drain(task_id, io_tokens, local, local_running, "declared local")

        # --- auto -------------------------------------------------------
        ib = self.ibex()
        ibex_ok = ibex_eligible and ib.slots_free > 0 and ib.env_present and ib.idle_nodes > 0
        gpu_blocked = gpu and local.gpu_free < 1
        cpu_free = local.cpu_threads - local.cpu_busy_threads
        local_ok = (io_tokens <= local.nvme_free
                    and not gpu_blocked
                    and local.mem_available_gb >= memory_gb
                    and cpu_free >= cpu_threads)

        # A whole-pool task goes to Ibex when it can, rather than draining BORG.
        if io_tokens >= self.nvme_capacity and ibex_ok:
            return Plan(task_id, "ibex", f"needs the whole local I/O budget; Ibex free ({ib.detail})",
                        1, 1, cpu_threads, memory_gb)
        if local_ok:
            self.waiting.pop(task_id, None)
            return Plan(task_id, "local", f"local headroom (nvme {local.nvme_free}/{local.nvme_capacity},"
                                          f" mem {local.mem_available_gb:.0f}G, load {local.load1:.1f})",
                        io_tokens, 0, cpu_threads, memory_gb)
        if ibex_ok:
            self.waiting.pop(task_id, None)
            return Plan(task_id, "ibex", f"local saturated; Ibex has capacity ({ib.detail})",
                        1, 1, cpu_threads, memory_gb)
        return self._defer_or_drain(task_id, io_tokens, local, local_running,
                                    f"local full and ibex unavailable ({ib.detail or 'unreachable'})")

    def _age(self, task_id: str) -> int:
        self.waiting[task_id] = self.waiting.get(task_id, 0) + 1
        return self.waiting[task_id]

    def _defer_or_drain(self, task_id, io_tokens, local, local_running, why) -> Plan:
        age = self._age(task_id)
        # Anti-starvation: a task that needs more than is ever free while small jobs keep
        # taking the pool gets a drain window rather than waiting forever.
        if io_tokens > local.nvme_free and age >= EXCLUSIVE_AGE_CYCLES:
            return Plan(task_id, "defer", f"{why}; DRAINING local pool for exclusive window "
                                          f"(waited {age} cycles, {local_running} running)",
                        drain=True)
        return Plan(task_id, "defer", f"{why}; waited {age}")

    def snapshot(self, nvme_used: int) -> dict:
        local, ib = self.local(nvme_used), self.ibex()
        return {
            "local": {"nvme_used": local.nvme_used, "nvme_capacity": local.nvme_capacity,
                      "nvme_free": local.nvme_free, "load1": round(local.load1, 2),
                      "mem_available_gb": round(local.mem_available_gb, 1),
                      "gpu_free": local.gpu_free, "cpu_threads": local.cpu_threads},
            "ibex": {"reachable": ib.reachable, "submitted": ib.submitted,
                     "capacity": ib.capacity, "slots_free": ib.slots_free,
                     "idle_nodes": ib.idle_nodes, "env_present": ib.env_present},
            "waiting": dict(self.waiting),
        }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Inspect live BORG and Ibex execution pools.")
    ap.add_argument("--nvme-capacity", type=int, default=8)
    ap.add_argument("--ibex-capacity", type=int, default=4)
    ap.add_argument("--nvme-used", type=int, default=0)
    ap.add_argument("--no-probe", action="store_true")
    a = ap.parse_args()
    b = Broker(a.nvme_capacity, a.ibex_capacity, probe=not a.no_probe)
    print(json.dumps(b.snapshot(a.nvme_used), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
