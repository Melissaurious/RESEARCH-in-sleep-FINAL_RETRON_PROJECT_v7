# RT–ncRNA embedding track — reporting package

Closed 2026-09-18. Nothing here re-runs a model; every number is read from a frozen bundle.

| document | for |
|---|---|
| **`RT_NCRNA_EMBEDDING_REPORT.md`** | the full scientific report — question, data, split, models, results, interpretation, escalation decision, feasibility, OpenCRISPR precedent, future triggers |
| `RT_NCRNA_EMBEDDING_REPORT.tex` | thesis-ready LaTeX condensation of the same frozen numbers |
| **`SUPERVISOR_SUMMARY.md`** | 2–4 page summary for a supervision meeting, with split diagram, model schematic and next steps |
| `HISTORICAL_MODEL_ASSET_AUDIT.md` | prior embedding / contrastive / cross-attention work across all project trees, with paths, hashes and GREEN/AMBER/RED/DEAD-ROUTE classification |
| `FUTURE_MODELLING_DECISION_NOTE.md` | why contrastive escalation stopped, reopening triggers, standing requirements, and the engineering that already exists |
| `FIGURE_INDEX.md` | captions, plotting tables, scripts, descriptive vs inferential |
| `TABLE_INDEX.md` | every result table with its content |
| `figures/` | the five publication figures |

## Frozen artifacts this package reports on

| bundle | commit |
|---|---|
| `results/embed_g0_input_contract/` | `fe6e1a3` |
| `results/embed_g1_representations/` | `2c9127b` |
| `results/embed_g2a_split_selection/` | `4f7e441`, `fd5efc9` |
| `results/embed_g2b_frozen_split/` — **binding split** | `15e00b8` |
| `results/embed_g2_frozen_baseline/` — **confirmatory result** | `2c9127b` |
| `results/embed_g2c_atlas/` | `9154972` |
| `docs/decisions/2026-09-18_embed_g2_closure.md` | `9154972` |

Verify the split at any time: `bash results/embed_g2b_frozen_split/verify.sh`

## The result in three lines

Level 1 — shared RT–ncRNA organization at retron-type / system-class level: **evidence for**.
Level 2 — individual partner specificity within that organization: **not established**.
Binding constraint: **independent relatedness components (n_eff = 14.1)**, not model capacity.
