---
description: Create, triage, assign, rank, complete, or archive project tasks.
argument-hint: Incoming tasks or the requested board operation.
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash", "Skill", "AskUserQuestion"]
---

# /task-operations

1. Load `task-operations:task-intake`.
2. Read the canonical board, people, and active work scopes before changing anything.
3. Apply Writing Skill in the request language, create or update the cards once, and verify them by readback.
4. Return links, gate results, global order, and per-owner order.
