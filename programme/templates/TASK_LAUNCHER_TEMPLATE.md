---
task_id:
stage_id:
title:
state: NOT_STARTED        # NOT_STARTED AUTHORIZED QUEUED RUNNING COMPUTE_COMPLETE VALIDATION_PENDING PASS FAIL STOP INCONCLUSIVE BLOCKED SUPERSEDED
autonomy_tier:            # A | B | C
compute_class:            # ZERO CPU_SMALL CPU_MEDIUM CPU_HIGH MEMORY_HIGH GPU_SMALL GPU_MEDIUM GPU_HIGH
preferred_backend:
fallback_backend:
worktree:
branch:
output_directory:
hard_dependencies: []
soft_dependencies: []
populations_touched: []   # and how: trained_on | tuned_against | inspected
iteration_budget: 1
claim_ids_touched: []
thesis_artifacts: []
---

# <task-id> · <title>

## Question
<one sentence, answerable>

## Hypothesis
<what is expected, and what the alternative is>

## Why existing evidence does not answer it
<including the registry lookup result: what prior work exists, and which of asset / bounded negative / unverified conclusion it is>

## Population and inferential unit
- population:
- inferential unit:
- **dependence structure:** <what makes units non-independent, and how variance accounts for it>
- effective n, expected:

## Inputs
| input | path | sha256 | role |

## Forbidden inputs
<what must not be used, and why — usually anti-circularity>

## Controls — these run FIRST and BLOCK
| control | type | what it must show | if it fails |
|---|---|---|---|
| | positive | | |
| | negative | | |
| | baseline | | |

## Reachability
<why the declared PASS outcome is attainable from this input population>

## Method
<software, version, parameters, seed policy>

## Endpoint and criterion
- primary endpoint:
- minimum detectable effect / decision threshold:
- **falsification criterion:**
- **death condition:** <what result closes this question permanently>

## Expected result patterns
| pattern | reading |

## Outputs
<declared files; the report lists their hashes>

## What this task may NOT conclude
<explicit>
