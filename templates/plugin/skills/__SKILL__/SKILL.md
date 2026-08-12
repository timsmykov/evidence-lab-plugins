---
name: __SKILL__
description:
  "REPLACE ME with 2-4 sentences a router can act on. State what the skill produces,
  then name the concrete phrasings that should load it — 'screen these abstracts',
  'build a PRISMA flow', 'проверь этот корпус на пропущенные ключевые работы'. Cover
  both English and Russian, since the team asks in both. Then name the near misses
  that must NOT load it. Write triggers, not marketing."
---

# __SKILL__

REPLACE ME: one paragraph on the job this skill does and the decision it supports.

## When it applies

- REPLACE ME: a concrete situation.

## When it does not apply

- REPLACE ME: the adjacent job that another skill or a human handles.

## Who does what

The model understands the request, searches and reasons. The repeatable artefact is produced by a deterministic script. If a step must return the same result on a rerun, it belongs in `scripts/`, not in prompt text.

| Step | Who runs it | Artefact |
|---|---|---|
| REPLACE ME | model / script / researcher | REPLACE ME |

## Procedure

1. REPLACE ME.
2. REPLACE ME.
3. REPLACE ME — the confirmation point: state exactly what the researcher has to approve before the work continues.

## Output format

REPLACE ME. Use `templates/report.md`.

## Quality gates

- Every claim traces to a source; what was not found is named as not found.
- Source coverage is shown explicitly, including access failures.
- Intermediate artefacts are kept, so the result can be rechecked rather than taken on trust.

## Boundaries

- REPLACE ME: what the skill does not guarantee (coverage of paywalled databases, legal assessment, authorship of conclusions).
