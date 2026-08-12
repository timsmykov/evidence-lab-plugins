---
description: Reference entry point — run the example-domain procedure over a folder of documents
argument-hint: path to the directory of documents
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash", "Skill", "AskUserQuestion"]
---

# /example-domain

The human entry point. The command does not restate the skill; it launches the skill with the right parameters and collects the result.

1. If no path was passed as an argument, ask where the documents are.
2. Load the `example-domain:example-procedure` skill and run the procedure.
3. At the feature confirmation step, stop and ask the user via `AskUserQuestion`.
4. After `summary.md` is assembled, invoke the `example-domain-critic` subagent and attach its findings.
5. Return the path to `summary.md`, the coverage figures and the findings in one message.
