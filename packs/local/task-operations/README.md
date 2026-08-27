# Task Operations

Reusable operations pack for agents that receive work in chat and maintain a canonical task board. It combines atomic task intake, explicit accountability, readiness-first gating, deterministic ranking, and completion history without assuming a particular project, product, or workspace schema.

## What it provides

| Skill | Output |
|---|---|
| `task-intake` | Well-written task cards, verified role assignments, gate results, global rank, and per-owner rank. |

The completion contract keeps one canonical task record and exposes completed work through the workspace's archive view. The pack remains `reference` until it passes independent review and representative runs on more than one board implementation.

## What it does not do

It does not invent a roadmap, create work outside the named source, or replace human approval for unsupported P0 classification, deadlines, new active scopes, destructive deletion, or explicit accountability changes. It reads and preserves each project's canonical schema and values.

## Provenance

The procedure is derived from Hermes Task Intake and the later readiness-first correction to additive task ranking. Exact provenance is recorded in `meta.json`.
