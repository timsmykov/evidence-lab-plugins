# example-domain

The reference implementation of a domain pack. It exists to show the whole shape: two skills, an entry command, a reviewer subagent, a deterministic script and eval sets. It carries no subject-matter value and never reaches either marketplace — `status: reference` keeps it out.

When you build a real pack, use the scaffolder rather than copying this directory: `python3 scripts/new_pack.py <name> --layer domain --skill <skill> --owner <owner> --reviewer <reviewer>`. Come back here to see what a filled-in result looks like.

## What is demonstrated here

| Element | File | Why |
|---|---|---|
| Pack contract | `pack.json` | Host-neutral identity, layer, selection metadata, dependencies, and runtimes |
| Host manifests | `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` | Generated native adapters |
| Registry metadata | `meta.json` | Provenance, owner, reviewer, status, risk class |
| Procedure skill | `skills/example-procedure/SKILL.md` | The split between model reasoning and a deterministic step |
| Deterministic part | `skills/example-procedure/scripts/build_table.py` | The repeatable artefact is built by code, not by a prompt |
| Checking skill | `skills/example-checklist/SKILL.md` | A second skill in the same domain — the reason a plugin exists at all |
| Routing | `skills/*/evals/trigger_eval.json` | What the skill must catch and what it must let pass |
| Command | `commands/example-domain.md` | The human entry point |
| Reviewer | `agents/example-domain-critic.md` | Fresh context, tasked with breaking the result rather than confirming it |

## What is not here

No real methodology, no sources, no subject-matter quality gates. All of that appears in real plugins and comes from someone's practice — see `provenance` in `meta.json`.
