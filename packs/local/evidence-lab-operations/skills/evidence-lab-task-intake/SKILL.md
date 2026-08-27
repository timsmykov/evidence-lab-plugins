---
name: evidence-lab-task-intake
description: Convert one or more incoming Evidence Lab requests into atomic, well-written task cards with an accountable owner, executor, reviewer, active project or initiative, result, acceptance criteria, source, dependencies, and deterministic priority. Use when someone asks to create, add, record, triage, prioritize, reorder, complete, or archive Evidence Lab tasks. Do not use for merely explaining prioritization, managing another project's board, or inventing work that was not requested or found in a named source.
---

# Evidence Lab Task Intake

Turn raw requests into cards that another person can execute without reopening the original conversation. This skill adapts Hermes Task Intake: it retains atomic tasks, contextual descriptions, acceptance criteria, duplicate checks, and decomposition, while replacing the retired multiplicative Focus Score with Evidence Lab's gated additive queue.

## Required companions

Before drafting any title or prose, load `writing-skill`. Select one output language for the whole card. After drafting, apply the `humanizer` quality pass without changing facts, field values, or acceptance criteria. If either companion is unavailable, apply the rules in `references/language-and-writing.md` and report that fallback.

## Procedure

1. Read the target board schema, active initiatives, and existing task candidates before writing. Search for semantic duplicates inside the same initiative or product contour.
2. Split the request into atomic tasks. One card must produce one reviewable result. Treat work larger than `L` as a container and create executable children; a container never enters the execution queue.
3. Preserve intent. Extract the requested result, source, constraints, named people, deadline, and dependencies. Do not invent adjacent work. If a consequential field cannot be inferred safely, keep the card in the board's clarification queue rather than guessing.
4. Assign roles and relationships using `references/field-contract.md`. Distinguish the owner of the result from the person or people executing it. Link the active initiative and select the relevant product contour.
5. Write the title and body using `templates/task-card.md` and `references/language-and-writing.md`. The title is an action verb plus object and, when useful, context. The body leads with the result and contains only information needed to execute or verify the task.
6. Evaluate the execution gate. A task is Ready only when it has every required field, belongs to an active initiative, is not blocked, is not a container, and has no open dependencies. P0 additionally requires a concrete failure sentence.
7. Apply `references/priority-model.md`. For batches, serialize the normalized cards and run `scripts/rank_tasks.py`; use its score and per-owner rank rather than hand-sorting. Only Ready tasks receive a rank.
8. Write once through the canonical workspace connector. Re-fetch every created or updated card and verify title, language, roles, project relation, result, acceptance criteria, source, dependencies, readiness, and rank fields.
9. On completion, require an artifact or explicit result note, set completion date, change status and board column to Done, and verify the card appears in the completed-task archive view. Do not move or duplicate the database row.
10. Report created, updated, merged-as-duplicate, clarification-needed, completed, and archived counts. Include direct links and state any inferred field explicitly.

## Confirmation boundaries

Ask before silently approving a P0, a hard external deadline not present in the source, a new active initiative, deletion of a major task, or reassignment of accountability. Ordinary field normalization and deterministic re-ranking do not require confirmation.

## Quality gates

- One task, one result, one accountable owner.
- Owner, executor, and reviewer are not treated as synonyms.
- The card links to an active initiative and names its product contour.
- Result and acceptance criteria are observable; activity alone is not completion.
- Source and real dependencies are recorded; unsupported assumptions are visible.
- P0 has a failure sentence; urgency is based on consequence and time, not tone.
- Only executable cards receive an owner rank; the first Ready card is the next pull.
- Prose uses one language and has passed Writing Skill and Humanizer checks.
- Done cards retain their canonical identity and become visible through the archive view.

## Boundaries

- Do not treat `Priority score` as proof that a blocked or malformed card is executable.
- Do not create duplicates to represent archive history.
- Do not translate product names, identifiers, URLs, code, or canonical select values.
- Do not claim performance metrics that the board cannot derive from completion dates and stored fields.
