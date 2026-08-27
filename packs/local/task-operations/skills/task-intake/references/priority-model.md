# Universal baseline priority model

Use two stages: a readiness gate, then an additive rank. A high score never overrides a failed gate. If a project has an approved local model, keep it only when it preserves this invariant and produces a deterministic pull order.

## Semantic fields

Priority measures contribution to an authorized result:

- P0: without the task, a specific committed result cannot be delivered. Requires: "Without this task, [result] cannot be delivered because [reason]."
- P1: the result remains deliverable but loses a material layer of quality, completeness, safety, or usefulness.
- P2: optional improvement, exploration, polish, or work whose contribution is not yet validated.

Impact measures the consequence inside the task's work scope:

- 5: determines a committed delivery, release, client outcome, legal/safety gate, incident recovery, or central project result.
- 4: materially changes the quality or adoption of a major deliverable.
- 3: improves a meaningful workflow or removes recurring friction.
- 2: local improvement with limited downstream effect.
- 1: cosmetic, speculative, or easily deferred.

Urgency measures time-sensitive consequence, not emotional wording:

- 5: active incident, overdue verified commitment, or due within three days with a real consequence.
- 4: due within seven days or blocks work planned for the current cycle.
- 3: should land in the current cycle; delay has a visible but recoverable cost.
- 2: useful soon, with no current-cycle consequence.
- 1: no valid time pressure.

Size estimates one executable result: XS up to 30 minutes, S 30 minutes-2 hours, M 2-4 hours, L more than 4 hours. Split a card when it contains separately acceptable results, independently pullable work, or an outcome too broad to verify coherently; duration alone does not force an artificial split.

## Baseline score

For Ready tasks only:

```text
score = commitment gate
      + priority contribution
      + impact
      + urgency
      + active dependents unblocked
      + due-date pressure
      + small-size tie-breaker
      + in-progress continuity
```

Baseline weights:

- commitment gate: 100 or 0;
- priority: P0 60, P1 30, P2 0;
- impact: value x 10;
- urgency: value x 6;
- active dependents: 8 each, capped at 24;
- due: 20 when overdue or due in 0-1 days, 15 for 2-3 days, 10 for 4-7 days, 5 for 8-14 days, otherwise 0;
- size: XS 12, S 9, M 4, L 0;
- already in progress: 25.

The commitment gate is not an importance shortcut. Use it only when the source links the task directly to an approved milestone, delivery, release, incident, or equivalent result. A project may map a narrower local field such as `pilot_gate` to this neutral flag.

## Pull order

Place an existing In progress card before To Do work in the applicable pull queue, then sort by score descending. This lane rule enforces the work-in-progress limit; the continuity points remain visible in the score but are not the only protection against starting another task. Tie-break by earlier valid due date, smaller size, earlier creation, then title. Assign global ranks 10, 20, 30, and so on. Also assign ranks 10, 20, 30 within each owner.

- Shared unassigned queue: pull the smallest global rank.
- Capacity assigned by owner: each owner pulls the smallest owner rank.
- Keep at most one task in progress per executor unless the project explicitly documents another work-in-progress limit.

Blocked, Done, container, inactive-scope, and incomplete cards have no rank. Re-run ranking after intake, completion, dependency changes, priority changes, due-date changes, ownership changes, or scope activation changes.
