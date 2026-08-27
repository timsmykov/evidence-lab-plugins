# Evidence Lab priority model

The queue uses two stages: execution gate, then additive rank. A high score never overrides a failed gate.

## Semantic fields

Priority measures contribution to the authorized result:

- P0: without the task, a specific committed result cannot be delivered. Requires the sentence: "Without this task, [result] cannot be delivered because [reason]."
- P1: the result remains deliverable but loses a material layer of quality, completeness, safety, or usefulness.
- P2: optional improvement, exploration, polish, or work whose contribution is not yet validated.

Impact measures the consequence for the active initiative:

- 5: determines a pilot, client, release, legal/safety gate, or central methodology result.
- 4: materially changes the quality or adoption of a major deliverable.
- 3: improves a meaningful workflow or removes recurring friction.
- 2: local improvement with limited downstream effect.
- 1: cosmetic, speculative, or easily deferred.

Urgency measures time-sensitive consequence, not emotional wording:

- 5: overdue or due within three days with a real consequence, or an active incident.
- 4: due within seven days or blocks work planned for the current cycle.
- 3: should land in the current cycle; delay has a visible but recoverable cost.
- 2: useful soon, with no current-cycle consequence.
- 1: no valid time pressure.

Size is AI-assisted elapsed effort for one executable unit: XS up to 30 minutes, S 30 minutes–2 hours, M 2–4 hours, L 4–8 hours. Larger work becomes a container with children.

## Deterministic score

For Ready tasks only:

```text
score = pilot gate
      + priority
      + impact
      + urgency
      + active dependents unblocked
      + due-date pressure
      + small-size tie-breaker
      + in-progress continuity
```

Weights match the current Evidence Lab board:

- pilot gate: 100 or 0;
- priority: P0 60, P1 30, P2 0;
- impact: value × 10;
- urgency: value × 6;
- active dependents: 8 each, capped at 24;
- due: 20 overdue or 0–1 days, 15 for 2–3 days, 10 for 4–7 days, 5 for 8–14 days, otherwise 0;
- size: XS 12, S 9, M 4, L 0;
- already in progress: 25.

The pilot flag is reserved for a task that directly gates an approved pilot criterion. "Important for the pilot someday" is not enough.

## Pull order

Within each owner, sort Ready cards by score descending. Tie-break by earlier valid due date, smaller size, earlier creation, then title. Assign ranks 10, 20, 30, and so on. The first card is the next pull; an owner may have only one card in progress. Blocked, Done, container, inactive-initiative, and incomplete cards have no owner rank.

Re-run ranking after intake, completion, dependency changes, priority changes, due-date changes, or initiative activation changes.
