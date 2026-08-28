---
description: Summarize an Evidence Lab meeting and register the verified note in the canonical Notion meeting database
argument-hint: transcript, source page, or rough meeting notes
allowed-tools: ["Read", "Write", "Glob", "Grep", "Skill", "AskUserQuestion"]
---

# /evidence-lab-meeting-capture

The human entry point. The command does not restate the skill; it launches the skill with the right parameters and collects the result.

1. Load the `evidence-lab-meeting-capture:evidence-lab-meeting-capture` skill.
2. Confirm the meeting date, project, participants, and source only when the supplied material does not establish them.
3. Return the summary page URL, the source URL, and whether the stored record passed read-back verification.
