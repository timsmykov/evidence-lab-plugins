# Method: example-procedure

This file is loaded only when `SKILL.md` explicitly points at it. Keep here what is needed rarely: the method rationale, standards, contested points.

## Where the procedure comes from

Nowhere — this is a format exemplar. In a real plugin this slot holds specifics: whose practice, which debrief, which real run it was derived from. A skill without that provenance is somebody's guess dressed as a method.

## Why feature confirmation is its own step

The feature set determines what can appear in the result at all. If the model picks it and immediately extracts against it, an error in the choice becomes invisible: the table looks complete because it is complete with respect to the columns the model invented. Confirmation breaks that loop.

## Why table assembly is given to a script

Three reasons. Results become comparable across runs. A reviewer can rebuild the table without invoking the model. A formatting bug is fixed once in code instead of every time in a prompt.

## Common failure modes

- A gap is filled with a plausible value instead of `null`.
- Unreadable files quietly drop out of the reported coverage.
- Features are redefined mid-extraction, so half the table is built on one set and half on another.
