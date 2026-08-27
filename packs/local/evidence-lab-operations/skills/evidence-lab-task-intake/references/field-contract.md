# Evidence Lab task field contract

## Required for every executable task

| Field | Rule |
|---|---|
| Task | Action verb + object + useful context. |
| Status / Board column | `To Do`, `In progress`, or `Done`; blocked work uses the blocked board column and queue. |
| Queue | Use the board's canonical now, next, clarification, backlog, blocked, or complete option. It reflects execution state; it is not evidence of completion. |
| Owner | Exactly one person accountable for the result and acceptance. |
| Executors | People who perform the work. The list may differ from the owner. |
| Reviewer | Person who checks the acceptance criteria. For material work, prefer someone other than the owner. |
| Initiative | Relation to the active initiative that authorizes the work. Missing or inactive relation blocks Ready. |
| Product contour | One or more of Consulting, Methodology, Skill Pack, or Course, using the board's canonical option values. |
| Result | Observable artifact, decision, validated behavior, or delivered outcome. |
| Acceptance criteria | Specific checks that make completion decidable. |
| Source | Original request, meeting note, issue, specification, or other traceable evidence. |
| Priority | P0, P1, or P2 under the contribution test. |
| Impact | 1–5 under the impact rubric. |
| Urgency | 1–5 under the urgency rubric. |
| Size | XS, S, M, or L for the executable unit. |
| Dependencies | Only real linked prerequisites. Open dependencies block Ready. |

## Optional but important

- Due date: only when explicitly stated or supported by an external commitment.
- Start conditions: inputs, access, approval, or event required before execution.
- Artifact: link to the produced output.
- Cycle: delivery or review cycle used for reporting.
- Completion date: set when the task enters Done; never backfill by guessing.

## Role decision

The owner answers, "Who is accountable if the result is not accepted?" The executor answers, "Who performs the actions?" The reviewer answers, "Who independently decides whether the acceptance criteria were met?" If the answer to the first question is unknown, the task stays in clarification.

## Ready gate

Ready requires all required fields, an active initiative, a concrete next action, no blocker, zero open dependencies, and size XS–L. A result-sized container stays outside Ready and must expose at least one executable child.
