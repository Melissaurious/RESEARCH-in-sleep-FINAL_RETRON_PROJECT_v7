# EXTERNAL WORKTREES AND SUBMODULES

Two things about this repository are easy to miss from a fresh clone, and both change what
you see on disk.

---

## 1 · `general/` is a git submodule

```
[submodule "general"]
    path = general
    url  = https://github.com/Melissaurious/RESEARCH-in-sleep-GENERAL_v3
```

`general/` is the **governance layer**: data-safety rules, evidence standards, provenance
requirements, reporting rules, compute policy, and the `bundle_valid.sh` BS-1..BS-11 standard
that every landed gate must pass. `CLAUDE.md` defers to it for every rule.

A plain `git clone` leaves it **empty**, and the project will appear to have no rules at all.

```bash
git clone --recurse-submodules <repo-url>
# or, in an existing clone:
git submodule update --init --recursive
```

It is pinned by revision. The pin is recorded in
`docs/decisions/2026-09-15_general_pin_cff9831.md`; moving it is an operator decision.

## 2 · There is a second worktree: `dbchar-workbench`

```
$ git worktree list
/home/borg/…_v7                    6f4a7fe [main]
/home/borg/…_v7-dbchar-workbench   7fa61b4 [dbchar-workbench]
```

| | |
|---|---|
| path | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-dbchar-workbench` |
| branch | `dbchar-workbench` |
| relationship | a **linked git worktree of this same repository** — its `.git` is a file pointing at `…_v7/.git/worktrees/…` |
| remote | the same `origin` |
| pushed? | **No. The branch is local only and is deliberately not pushed.** |
| unique commits | **zero** — `dbchar-workbench` is an *ancestor* of `main`, 5 commits behind, 0 ahead |

### What this means in practice

* It is **not** a second project and **not** a second repository. Cloning this repo gives you
  `main` and nothing about the workbench, which is why this file exists.
* Its *tracked* content is a strict subset of `main`'s history. Everything scientific it
  contains — `results/dbchar_g1…g7b` — is already on `main`.
* Its real, unique content lives in `ARIS_OUTPUT/dbchar_workbench/`, which is **gitignored**
  and therefore in no branch at all. See `docs/DBCHAR_WORKBENCH.md`.

### If you ever want it on GitHub

Do not `git init` inside it — that would break the worktree. Either push the branch as-is:

```bash
git push -u origin dbchar-workbench     # NOT done; the operator has kept it local
```

or, to make it a genuinely separate repository, detach it first:

```bash
git worktree remove /home/borg/…-dbchar-workbench     # after backing up ARIS_OUTPUT/
```

and start a fresh repository from a copy of its files. There is nothing to preserve from its
branch history that `main` does not already have.

## 3 · Directories that exist locally and in no branch

| path | size | state |
|---|---|---|
| `ARIS_OUTPUT/` | 23 GB | gitignored scratch (includes 12 GB of g5 shards) |
| `data/` | 2.2 GB | gitignored; `data/README.md` is the tracked register |
| `MELISSA_DATA/` | 1.8 GB | gitignored raw corpora |
| `…-dbchar-workbench/ARIS_OUTPUT/dbchar_workbench/` | 88 MB | gitignored, **and the only copy of the Stage-1 thesis-writing material** |

The last row is a real single-point-of-failure. A text-only snapshot of it is tracked at
`docs/dbchar_workbench_snapshot/`; the notebooks, figures and LaTeX are not.
