# Autonomous Wave 01

This is an immutable operator-scope file, not a task-state database. `WAVE.tsv` is authorised at runtime by supplying its exact SHA-256 to `wave_runner.py --start`.

`T-P1b-identity-partition` is **monitor-only**. PID 810502 may not be signalled, restarted, modified or re-frozen. It reserves 6 of 8 local NVMe tokens while alive. This deliberately leaves room for two IO_LOW tasks while preventing IO_MEDIUM/IO_HIGH work from competing with it.

P1b exit is an escalation point under the current durable handoff. The runner does not auto-finalise P1b. `T-P1c` remains blocked until the authoritative board/report state becomes `PASS`.
