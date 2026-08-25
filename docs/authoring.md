# Authoring skills and plugins

## Start from a run, not from a text

A skill is written after the work has been done by hand at least once. The order is: do it → notice what repeats → write the procedure down → test it on a second case → package it. The reverse order produces plausible prose that falls apart on the first real task.

## The description is routing

The `description` in the frontmatter is read by a router, not by a person. It has to answer two things: what the skill produces, and on which phrasings to load it. Take real phrasings — the ones people actually use, including the clumsy ones. Name the neighbouring requests that must *not* load it.

Bad: "Helps you work with academic sources."
Good: "Builds a summary table over a set of documents. Loads on 'build a summary table', 'structure this collection', 'pull these files into one comparable table'. Does not load when new sources have to be found, or when a finished artefact needs checking."

Write routing phrasings in English. The verifier enforces English entrypoints; Russian-language guidance belongs in an explicitly named `*.ru.md` reference routed from the English `SKILL.md`.

## Split the model from the script

Ask of every step: must it return the same result on a rerun? If yes, it is `scripts/`. Citation formatting, deduplication, table assembly, template filling, diagram rendering — code. Understanding the request, searching, interpreting, deciding what matters — the model.

The script has to run standalone, without the agent: a reviewer must be able to rebuild the artefact without invoking a model.

## Put in a confirmation point

Every procedure contains a decision that belongs to the researcher, not the agent: the feature set, the inclusion criteria, the boundaries of the topic. Make that decision an explicit stop. Without it the model's hypothesis quietly becomes the result.

## Write the boundaries honestly

The "what it does not do" section matters more than the feature list. It is what stops the plugin being sold as a universal replacement for other tools, and it removes half the future complaints.

## Evals

At least eight cases, at least three of them negative. Take the negatives from neighbouring skills in the same plugin — that is where confusion is most likely. Vary the phrasing instead of the language: the same job asked as a request, as a problem, and by naming the artefact rather than the action.

One useful case type: a question *about* the method instead of a request to run it ("explain how a summary table differs from a comparison matrix" — must not load).

## What goes into references

`SKILL.md` holds what is always needed. `references/` holds what is rarely needed: the method rationale, standards, long examples, common failure modes. The agent should not read those by default, and `SKILL.md` should not grow to the size where people stop reading it whole.

## Provenance

Always filled in `meta.json`: whose practice, which run, which materials. This is not bureaucracy — six months on it is the only way to tell whether the procedure can be trusted and who to ask about it.
