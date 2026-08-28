---
name: task-intake
description: Convert incoming work into atomic, well-written task cards with accountable ownership, execution and review roles, project context, observable results, acceptance criteria, dependencies, readiness gates, and deterministic priority order. Use when someone asks to create, record, triage, assign, prioritize, reorder, complete, or archive tasks in any project or shared work queue. Do not use for explaining prioritization without changing tasks, product planning from scratch, or inventing work outside the named request or source.
---

# Task Intake

Turn raw requests into task cards that another person can execute without reopening the original conversation. Keep semantic judgment separate from deterministic ordering: first normalize and validate each card, then rank only executable work.

## Required companions

Before drafting task prose, load `writing-skill` and choose one output language for the whole card. After drafting, apply `humanizer` without changing facts, scope, roles, dates, field values, or acceptance criteria. If either skill is unavailable, use `references/language-and-writing.md` as the fallback and disclose that fallback.

## Procedure

1. Read the target board schema, active projects or work scopes, people, workflow states, and existing task candidates. Search for semantic duplicates in the same scope before writing.
2. Split the request into atomic tasks. One executable card produces one reviewable result. Use a container only when the outcome cannot be accepted as one result; containers never enter the execution queue.
3. Preserve intent. Extract the requested result, source, constraints, named people, deadline, and real dependencies. Do not invent adjacent work. Put consequential unknowns in clarification rather than guessing.
4. Assign fields using `references/field-contract.md`. Distinguish the accountable owner, the executor or executors, and the reviewer. Relate the card to the project, initiative, area, or other canonical work scope supported by the board.
5. Write the title and body with `templates/task-card.md` and `references/language-and-writing.md`. Lead with the result. Keep only the context needed to execute or verify the task.
6. Evaluate the readiness gate. A task is Ready only when the required fields are complete, its scope is active when scope lifecycle exists, it is not blocked or done, it is not a container, and it has no open dependencies. P0 additionally requires a concrete failure sentence.
7. Apply `references/priority-model.md`. Map local fields to the neutral input contract in `references/field-contract.md`. For a batch, run `scripts/rank_tasks.py`; use its score, global rank, and owner rank instead of hand-sorting. Only Ready tasks receive ranks.
8. Write once through the canonical workspace connector. Re-fetch every created or updated card and verify its language, roles, work scope, result, acceptance criteria, source, dependencies, readiness, score, and ranks.
9. On completion, require an artifact or explicit result note, set the completion date, change the canonical status to Done, and verify that the same record appears in the completed-task archive. Do not duplicate a task to archive it.
10. Report created, updated, merged-as-duplicate, clarification-needed, completed, and archived counts. Link the affected records and name any inferred field.

## Confirmation boundaries

Ask before approving P0 without source evidence, adding an unsupported hard deadline, creating a new active project or initiative, deleting a material task, or changing accountability from a person explicitly named by the user or source. Ordinary normalization, filling an executor who is already the named owner, independent-review correction, and deterministic re-ranking do not need confirmation.

## Quality gates

- One task, one observable result, one accountable owner.
- Owner, executor, and reviewer are separate roles even when one person legitimately holds more than one of them.
- Material work has a reviewer other than its owner unless the board records why self-review is unavoidable.
- The card belongs to a canonical work scope; inactive or missing required scope blocks Ready.
- Result and acceptance criteria make completion decidable; activity alone is not completion.
- Source and real dependencies are recorded; unsupported assumptions remain visible.
- P0 names the committed result that would fail and why.
- Urgency reflects time-sensitive consequence, not tone; a past date is verified before it creates overdue pressure.
- Only executable cards receive ranks. A shared queue pulls by global rank; owner-assigned queues pull by owner rank.
- Human-readable prose uses one language and passes Writing Skill and Humanizer checks.
- Done cards retain their canonical identity and completion evidence.

## Boundaries

- Prefer the target project's approved prioritization model when it is documented and passes the same readiness-first invariants. Use the baseline model only when no valid local model exists.
- A high score never makes a blocked, malformed, inactive-scope, or completed card executable.
- Do not invent deadlines, people, commitments, project relations, or dependencies to make a task Ready.
- Do not translate product names, identifiers, URLs, code, or canonical database option values.
- Do not claim throughput or performance metrics that the workspace cannot derive from stored completion evidence.
