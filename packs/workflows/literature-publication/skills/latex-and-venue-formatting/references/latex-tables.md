# Publication LaTeX tables

Use this reference for generating, repairing, fitting, or auditing a table.

## Data contract

Keep the original CSV, TSV, XLSX, JSON, or LaTeX source. Preserve visible values, decimals, percentages, uncertainty notation, units, row order, and labels unless the researcher explicitly requests a transformation. When generation is non-trivial, retain a normalized machine-readable snapshot and a manifest that records source identity, transformations, packages, and validation status.

Do not infer missing values, units, metric direction, comparison groups, or statistical significance. If a wrong highlight could change the scientific claim, leave values unhighlighted and request the rule.

## Fit ladder

Before shrinking text:

1. shorten headers using researcher-approved aliases and move definitions to notes;
2. group repeated headers;
3. use `tabularx` for text-heavy columns;
4. reduce `\tabcolsep` modestly;
5. use `table*` only when a readable one-column table is impossible;
6. split into meaningful panels;
7. use `adjustbox` with `max width=\linewidth`;
8. use `\resizebox` only as a disclosed last resort.

Avoid a result that technically fits but is unreadable. Do not add landscape mode or packages silently.

## Comparison and emphasis

- Compare values only within explicit compatible groups.
- Preserve standard deviations and confidence intervals; do not convert emphasis into a significance claim.
- Prefer bold for the best and underline for the second-best only when metric direction and comparison scope are explicit.
- For strict black-and-white venues, avoid color-dependent meaning.
- Add only packages actually required by the output and check that the official template permits them.

## Table gate

Before delivery verify source-value equality, header/group semantics, caption and note accuracy, package compatibility, column width, float placement, text references, accessibility, and rendered readability. A table failing data-integrity validation is not final even when it compiles.
