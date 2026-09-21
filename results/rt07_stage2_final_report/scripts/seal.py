#!/usr/bin/env python3
"""seal - write MANIFEST.tsv, INPUTS.tsv and (with --outputs) OUTPUTS.tsv for this bundle.

MANIFEST.tsv  every artefact this gate lands, the script that made it, its unit, its denominator.
INPUTS.tsv    every file outside the bundle that build.py or figures.py reads, hashed (BS-2).
OUTPUTS.tsv   every file in the bundle except itself, hashed (BS-11). Written LAST, after the
              README carries its final STATUS line.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import findings as F  # noqa: E402
import ledger as L  # noqa: E402

EXTRA_INPUTS = [
    F.G6T, F.UGS, F.UGN, F.G6B, F.ERR,
    "results/rt07_g7a_rt0_rt7_bridge/tables/g7a_state_to_residue.tsv",
    "results/rt07_g6_family_architecture/tables/g6_call_state_totals.tsv",
    "results/rt07_g4b_production_mapper/control/CROSSWALK_RT0_RT7.tsv",
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def inputs(root: Path) -> list[str]:
    ps = {v[0] for v in F.TABLE.values()} | set(EXTRA_INPUTS)
    ps |= {v[0] for v in F.DOC.values() if not v[0].startswith("git:")}
    ps |= {r[6] for r in L.REVIEWS if not r[6].startswith("git:")}
    ps |= {f"results/{b}/README.md" for b, _, _ in F.BUNDLES if (root / "results" / b / "README.md").exists()}
    return sorted(ps)


def manifest(out: Path) -> None:
    B, FG = "scripts/build.py", "scripts/figures.py"
    cmd_b, cmd_f = "see run.sh: build.py", "see run.sh: figures.py"
    na = "n/a - assembled document; every number is resolved from a landed table"
    rows = [
        ("report/STAGE2_TECHNICAL_REPORT.md", B, cmd_b, "document", na),
        ("report/THESIS_METHODS.md", B, cmd_b, "document", na),
        ("report/THESIS_RESULTS.md", B, cmd_b, "document", na),
        ("report/THESIS_DISCUSSION.md", B, cmd_b, "document", na),
        ("DELIVERABLES_INDEX.md", B, cmd_b, "document", na),
        ("tables/stage2_rt0_rt7_final.tsv", B, cmd_b, "historical label", "8 historical labels RT0-RT7"),
        ("tables/stage2_claim_evidence_matrix.tsv", B, cmd_b, "(claim, evidence value) link",
         "n/a - one lookup per row; no rate"),
        ("tables/stage2_review_ledger.tsv", B, cmd_b, "recorded independent review",
         "reviews recorded in docs/decisions and the g5 commit message"),
        ("tables/stage2_negative_results.tsv", B, cmd_b, "negative or null result", "n/a - one result per row"),
        ("tables/stage2_frozen_parameters.tsv", B, cmd_b, "frozen parameter", "n/a - one parameter per row"),
        ("tables/stage2_resolved_values.tsv", B, cmd_b, "resolved value", "n/a - one lookup per row; no rate"),
        ("tables/stage2_figure_plan.tsv", B, cmd_b, "figure", "n/a - one figure per row"),
        ("tables/stage2_bundle_index.tsv", B, cmd_b, "landed bundle", "Stage-2 bundles this report relies on"),
    ]
    units = {"F1_review_trajectory": ("recorded independent review", "reviews in tables/stage2_review_ledger.tsv"),
             "F2_validation": ("sequence / control class", "construction 219; UG25 28; controls 252 (carried)"),
             "F3_match_state_sensitivity": ("(convention, family)", "full consensus LENG per family (carried from g4a)"),
             "F4_catalogue_application": ("exact RT / state call", "catalogue, ELIGIBLE, and ELIGIBLE x 150 (carried from g5a/g5/g6)"),
             "F5_g6_concordance": ("g6 analysis", "13 analyses (carried from g6)"),
             "F6_rt0_rt7_final": ("historical label on LtrA", "8 historical labels; 150 anchor states (carried from g7a)")}
    for _, stem, *_ in L.FIGURES:
        u, d = units[stem]
        for ext in ("png", "svg"):
            rows.append((f"figures/{stem}.{ext}", FG, cmd_f, u, d))
        rows.append((f"tables/{stem}.tsv", FG, cmd_f, u, d))
    with (out / "MANIFEST.tsv").open("w", encoding="utf-8") as fh:
        fh.write("artifact\tscript\tcommand\tunit\tdenominator\n")
        for r in sorted(rows):
            fh.write("\t".join(r) + "\n")


PROVENANCE = """# PROVENANCE — rt07_stage2_final_report

Written by `scripts/seal.py --provenance`. The env.lock hash and the agreements pin are computed,
not typed.

```
env_lock_sha256: {env}
agreements: {agr}
seed: n/a — no random number generator is used; every step is a deterministic lookup or plot
models: claude-opus-5[1m]
source_of_record: {pin}
date: 2026-09-19
operator: Melissa Rios
scratch: ARIS_OUTPUT/rerun-rt07_stage2_final_report/
```

| field | value |
|---|---|
| gate id | `rt07_stage2_final_report` |
| track | `rt07` (Stage 2 — closed; reporting only) |
| branch | `rt07-stage2-final-report`, cut from `main` at the source-of-record commit |
| governing closure | `docs/decisions/2026-09-19_stage2_closed.md` |
| agreements pin | the `general/` submodule revision above |
| environment | `/home/borg/miniconda3/envs/retron_tradicional`, pinned by content via `env.lock` (`conda env export --no-builds`) |
| machine | borg, CPU only. No Ibex, no GPU, no job submitted. |
| models | `claude-opus-5[1m]` — package design, code and prose |

## What was read

Every input is listed with its sha256 in `INPUTS.tsv` ({n_in} files): landed tables of the
{n_b} Stage-2 bundles, the governing decision records, the g7a erratum table and the production
crosswalk. One value (the g5 application review score) is read from the message of commit
`6f4a7fe`. Landing commits are read with `git log` at the source-of-record commit, never typed.

## What was not done

No Stage-2 analysis was run or re-run. No frozen bundle, figure, table or decision record was
modified. No Stage-3 work was started. Nothing was pushed.

## Independence

This bundle has had **no adversarial pass**. It makes no new scientific claim. Every status and
interpretation it reports comes from records that were reviewed independently (see
`tables/stage2_review_ledger.tsv`). An independent review of the package's fidelity to those
records has not been done and would need to be vendor-disjoint from the model above.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--inputs", action="store_true", help="write INPUTS.tsv (landing only)")
    ap.add_argument("--outputs", action="store_true", help="write OUTPUTS.tsv (landing only, last)")
    ap.add_argument("--provenance", action="store_true", help="write PROVENANCE.md (landing only)")
    a = ap.parse_args()
    root, out = Path(a.root).resolve(), Path(a.out)
    manifest(out)
    if a.inputs:
        with (out / "INPUTS.tsv").open("w", encoding="utf-8") as fh:
            fh.write("path\tsha256\tbytes\tmtime\n")
            for rel in inputs(root):
                p = root / rel
                mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.stat().st_mtime))
                fh.write(f"{p}\t{sha(p)}\t{p.stat().st_size}\t{mt}\n")
    if a.provenance:
        import subprocess
        agr = subprocess.run(["git", "-C", str(root / "general"), "rev-parse", "HEAD"], check=True,
                             capture_output=True, text=True).stdout.strip()
        (out / "PROVENANCE.md").write_text(PROVENANCE.format(
            env=sha(out / "env.lock"), agr=agr, pin=F.PINNED_COMMIT, n_in=len(inputs(root)),
            n_b=len(F.BUNDLES)), encoding="utf-8")
    if a.outputs:
        files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "OUTPUTS.tsv"
                       and "__pycache__" not in p.parts)
        with (out / "OUTPUTS.tsv").open("w", encoding="utf-8") as fh:
            fh.write("path\tsha256\tbytes\n")
            for p in files:
                fh.write(f"{p.relative_to(out)}\t{sha(p)}\t{p.stat().st_size}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
