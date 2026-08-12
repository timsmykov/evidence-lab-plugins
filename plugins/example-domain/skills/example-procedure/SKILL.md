---
name: example-procedure
description:
  "Reference skill: turns a folder of source documents into a reviewed summary table
  with an explicit human confirmation step. Loads on requests like 'build a summary
  table from these documents', 'structure this collection', 'собери сводную таблицу
  по этим материалам'. Does NOT load for finding new sources, for checking a finished
  artefact (use example-checklist), or for questions about the method itself. Ships
  as a format example — it demonstrates the split between model reasoning and
  deterministic scripting, not a real research methodology."
---

# example-procedure

Shows the shape of a procedure skill: where the human decides, where the model reasons, and where a script runs. There is no subject-matter methodology here — a real plugin puts a procedure derived from someone's practice in this slot.

## When it applies

- There is a set of documents on hand and a structured summary over them is needed.
- The user is available to confirm an intermediate decision — the feature set the summary is built on.

## When it does not apply

- New sources have to be found rather than existing ones processed.
- The artefact already exists and needs checking — that is `example-checklist`.
- Someone is asking how the method works rather than asking for it to be run.

## Who does what

| Step | Who runs it | Artefact |
|---|---|---|
| 1. Inventory the input set | model | list of documents with type and size |
| 2. Propose features for the summary | model | draft feature set |
| 3. Confirm the features | researcher | approved set |
| 4. Extract values per feature | model | `extracted.json` |
| 5. Assemble the table | `scripts/build_table.py` | `summary.md` |
| 6. Review the result | `example-domain-critic` subagent | list of findings |

Step 5 is deliberately given to a script: sorting, column alignment and template substitution have to produce the same bytes on a rerun. Leave that to the model and the summary comes out slightly different every time, which makes two runs incomparable.

## Procedure

1. Read the input directory and inventory the documents. Files that could not be read go into a separate list — silently dropping them is not allowed.
2. Propose 4–7 features for the summary, with a short rationale for each.
3. **Confirmation point.** Show the feature set and wait for the researcher's decision. Do not proceed on silence: a model-chosen feature set is a hypothesis, not a result.
4. Extract values for the approved features into `extracted.json`; where a document has no value, write `null`, not a guess.
5. Run `python3 scripts/build_table.py extracted.json --out summary.md`.
6. Hand `summary.md` to the `example-domain-critic` subagent and attach its findings to the result.

## Output format

`summary.md` per `templates/report.md`: the table, explicit coverage (how many documents were processed, how many failed to read), and the list of gaps.

## Quality gates

- Every row traces to a specific document.
- Gaps are shown as gaps, not filled with plausible text.
- Features are approved by a human before extraction, not fitted to the result afterwards.
- Rerunning on the same `extracted.json` produces a byte-identical `summary.md`.

## Boundaries

- Does not assess the quality of the sources themselves.
- Does not replace the researcher's judgment about what counts as material.
