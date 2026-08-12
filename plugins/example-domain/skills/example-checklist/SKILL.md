---
name: example-checklist
description:
  "Reference skill: checks a finished artefact against formal criteria before it goes
  to a supervisor or a client. Loads on 'review this artefact for gaps', 'what won't
  survive scrutiny here', 'check this table before I send it'. Does NOT load when
  the artefact still has to be produced (use example-procedure), when the ask is to
  rewrite the text rather than check it, or when someone wants a subjective opinion
  on quality. Ships as a format example: it shows why a plugin bundles several skills
  instead of shipping one."
---

# example-checklist

The second skill in the same domain. It exists to show why a plugin is needed at all: producing and checking are different procedures, but one subject area, one vocabulary and one set of templates.

## When it applies

- The artefact is finished and has to be checked against formal criteria before it is handed on.

## When it does not apply

- The artefact does not exist yet — start with `example-procedure`.
- The ask is to rewrite the text, not to find holes in it.
- Someone wants a subjective "is this good" verdict — this skill checks against criteria, not taste.

## Procedure

1. Read the artefact and reconstruct how it was built: what the inputs were, which features were used, what coverage is claimed.
2. Work through the criteria below and give a verdict on each, anchored to a place in the artefact.
3. Return findings ordered by severity. If there are none, say so plainly — do not manufacture findings for volume.

## Criteria

| Criterion | What to look for |
|---|---|
| Traceability | every claim reduces to a specific source |
| Honest coverage | what was left out and why; the unreachable is named as unreachable |
| Gaps | empty values are shown as empty, not filled with plausible text |
| Substitution | a model conclusion is not presented as a result derived from data |
| Reproducibility | the description is enough to repeat the run and get the same result |

## Quality gates

- Every finding points at a place in the artefact.
- Findings are not invented: "clean" is a valid verdict.
- Severity is differentiated: what would sink a defence and what is worth tidying do not go in one list.

## Boundaries

- Does not verify that the sources are factually correct — only that the artefact holds together internally.
