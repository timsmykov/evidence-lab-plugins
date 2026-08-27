# Evidence Lab Operations

Internal pack for Evidence Lab agents that receive work in chat and maintain the canonical task board. It adapts the proven Hermes Task Intake structure to the current Evidence Lab schema and queue instead of carrying over the retired multiplicative Focus Score.

## What it provides

| Skill | Output |
|---|---|
| `evidence-lab-task-intake` | Atomic task cards, verified field assignments, gate results, and deterministic per-owner rank. |

The pack also defines the completion-to-archive contract: a Done task remains the same canonical database row and appears in the linked completed-task archive. Its `reference` status keeps this internal local pack out of the public researcher marketplace until independent review and representative board runs are complete.

## What it does not do

It does not manage personal LifeOS work, invent a product roadmap, or replace human approval for P0, unsupported deadlines, new active initiatives, deletion, or accountability changes. It is a local operations pack and is not selected for researcher installations by default.

## Provenance

The procedure is derived from the Hermes Task Intake page, the later Lean Focus v2 correction, and the live Evidence Lab board field contract. Exact source identifiers are recorded in `meta.json`.
