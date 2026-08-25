# Architecture

## The problem

What people work out stays inside their personal instances and never reaches the shared contour. Once user instances are isolated, today's workaround — opening someone's instance and reading their setup — disappears entirely. What is needed is an explicit mechanism: one format, versions, provenance, and a propose → review → publish process.

## Three levels, and why three

**Skill** — the atom: one repeatable procedure. It ports to another runtime because it is a `SKILL.md` plus the files next to it, with no external wiring.

**Plugin** — the domain bundle. It exists because research work does not decompose into isolated procedures: a systematic review is a search protocol, screening, PRISMA and an evidence table, sharing a vocabulary, templates and a reviewer. A client installs "the review plugin", not seven skills they are expected to assemble themselves. The plugin is the unit of installation and versioning.

**Marketplace** — the repository as a whole: shop window, gate, policy.

## Decisions

**The native Claude Code format, not our own.** The `.claude-plugin/plugin.json`, `skills/`, `commands/`, `agents/` layout is the one the official marketplace uses. The cost is somebody else's naming rules. The gain is that installation works out of the box (`/plugin marketplace add`), we ship no installer, and the format evolves without us.

**The shop window is generated, not written.** `marketplace.json` is rebuilt from `plugins/` by a script, and CI fails on drift. This is precisely where catalogues like this rot: the plugin lands, the window is forgotten, and after that nobody trusts either one.

**Registry metadata lives in `meta.json`.** Provenance, owner, reviewer, status, risk class are our fields, not Claude Code's. Putting them in `plugin.json` would put us in conflict with upstream the first time the schema tightens. The price is a second file per plugin.

**Evals live inside the skill.** The `{query, should_trigger}` format is taken from the official plugins. It is a routing test: which phrasings must load the skill and which must not. At least three negatives, because in a set of ten skills a false trigger breaks the session more visibly than a miss.

**Deterministic steps go into `scripts/`.** The model understands the request, searches and reasons; the repeatable artefact is produced by code. This is the principle from the 12 July product debrief: demanding byte-identical tables, citations and diagrams from a generative model is the wrong problem statement. The practical rule: if a step must return the same thing on a rerun, it belongs in code, not in a prompt.

**No shared skills yet.** There is deliberately no `shared/` directory. Claude Code requires a skill to sit physically inside the plugin, so reuse means a copy. Building a vendoring mechanism before the first real duplicate exists is premature. When that duplicate shows up, the copy will be made by a script that records source and version — not by hand.

**English entrypoints.** Skills, manifests, eval sets and repository docs are English so the registry stays portable and reads well to a routing agent. Localization, when it is genuinely needed, lives in an explicitly named file (`*.ru.md`, `*.ru.json`) routed from the English `SKILL.md`. Mixed-language entrypoints are rejected.

## What the gate enforces

Manifest schemas; names matching directories; completeness of `meta.json`; presence and composition of eval sets; description length and trigger wording; a reviewer distinct from the owner for production; a version bump when plugin content changes; unfilled scaffold placeholders; and the absence of private paths, addresses, tokens and identifiers.

The sanitization gate checks shared plugin material for private paths, addresses, tokens, internal identifiers, and misplaced localized prose before publication.

## Boundaries

This catalogue solves sharing inside the team. Delivering plugins into isolated user instances, versioning them client-side and rolling them back is separate work that depends on the memory-isolation task. It is not here, and it should not be.
