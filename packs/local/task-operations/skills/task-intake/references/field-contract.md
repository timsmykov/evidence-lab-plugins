# Universal task field contract

Map the target board's field names and option values to this neutral contract. Do not rename a live workspace field merely to match the contract.

## Required for every executable task

| Neutral field | Rule |
|---|---|
| `title` | Action verb + object + useful context. |
| `status` | Canonical workflow state such as To Do, In progress, Blocked, or Done. |
| `owner` | Exactly one person accountable for the result and acceptance. |
| `executors` | One or more people who perform the work. May include the owner. |
| `reviewer` | Person who checks the acceptance criteria. Material work should not be self-reviewed. |
| `scope` | Active project, initiative, area, objective, client, or other canonical work scope. |
| `result` | Observable artifact, decision, validated behavior, or delivered outcome. |
| `acceptance_criteria` | Specific checks that make completion decidable. |
| `source` | Original request, meeting note, issue, specification, or other traceable evidence. |
| `priority` | P0, P1, or P2 under the contribution test. |
| `impact` | 1-5 under the impact rubric. |
| `urgency` | 1-5 under the urgency rubric. |
| `size` | XS, S, M, or L for one executable result. |
| `dependencies` | Only real linked prerequisites. Any open prerequisite blocks Ready. |

## Optional but useful

- Due date: only when explicitly stated or supported by an external commitment.
- Commitment gate: only when the task directly gates an approved milestone, delivery, release, incident response, or equivalent committed result.
- Queue or lane: local workflow state such as now, next, clarification, backlog, blocked, or complete.
- Start conditions: inputs, access, approval, or event required before execution.
- Artifact: link to the produced output.
- Cycle or milestone: planning/reporting relation.
- Completion date: set when the task enters Done; never backfill by guessing.
- Priority rationale: short evidence for priority, impact, urgency, and any commitment gate.

## Role decision

- Owner: "Who is accountable if the result is not accepted?"
- Executor: "Who performs the work?"
- Reviewer: "Who decides whether the acceptance criteria were met?"

If the owner is unknown, keep the card in clarification. If the source names the owner and no separate executor is given, using the owner as executor is a safe normalization. For material work, select an independent reviewer from the known project roles; if none exists, record self-review as an explicit limitation.

## Ready gate

Ready requires all required fields, a concrete next action, no blocker, zero open dependencies, and a scope that is active when the workspace tracks scope lifecycle. A result-sized container remains outside Ready and must expose at least one executable child.

The deterministic script accepts `project`, `initiative`, `area`, or `scope` as the work-scope field. Local adapters may map different names before ranking.
