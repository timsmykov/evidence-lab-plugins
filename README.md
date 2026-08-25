# Evidence Lab Plugins

A marketplace of domain plugins for research work. A plugin is the installable unit: several skills from one subject area, plus the commands, subagents and routing checks that go with them.

The repository is private and scoped to sharing inside the team. Distribution into isolated client instances is separate work and deliberately out of scope here.

## Three levels

| Level | What it is | Where it lives |
|---|---|---|
| Skill | one repeatable procedure: `SKILL.md` plus `scripts/`, `templates/`, `references/`, `evals/` | `plugins/<plugin>/skills/<skill>/` |
| Plugin | a domain bundle of skills with a shared command and reviewer; the unit of installation and versioning | `plugins/<plugin>/` |
| Marketplace | the shop window and the quality gate | `.claude-plugin/marketplace.json` |

The format is native to Claude Code, so installation needs no installer of ours:

```
/plugin marketplace add timsmykov/evidence-lab-plugins
/plugin install <plugin>@evidence-lab-plugins
```

For non-Claude runtimes, export only plugins explicitly verified for that runtime:

```bash
python3 scripts/export_portable.py --runtime codex
```

## Language policy

English entrypoints, manifests, eval sets, documentation and commit messages are written in English, because the primary reader of a skill is a routing agent and the registry has to stay portable across runtimes.

The verifier enforces this: Cyrillic outside explicitly named `*.ru.md` / `*.ru.json` localization files fails the build. A localized reference is routed from an English `SKILL.md`; mixed-language entrypoints are not allowed.

## Quick start for a plugin author

```bash
python3 scripts/new_plugin.py systematic-review --skill screening --owner Tim --reviewer Misha
# fill in SKILL.md, the eval set and meta.json
python3 scripts/build_marketplace.py
python3 scripts/verify_repo.py
```

Then branch, pull request, review, merge. Direct pushes to `main` are rejected.

## What the gate enforces

`scripts/verify_repo.py` fails when: a plugin manifest breaks the schema; a name does not match its directory; a skill on disk is missing from `meta.json`; a skill has no `evals/trigger_eval.json` or fewer than three negative cases; a skill description is shorter than 80 characters; a production plugin has the same person as owner and reviewer; plugin content changed without a version bump; scaffold placeholders were left unfilled; private paths, addresses, tokens or identifiers leaked into a file.

`scripts/build_marketplace.py --check` fails when the shop window has drifted from `plugins/`.

## Repository map

| Path | Purpose |
|---|---|
| `plugins/` | the plugins; `example-domain` is the reference implementation and stays out of the shop window |
| `templates/plugin/` | scaffolding template |
| `schemas/` | schemas for `plugin.json`, `meta.json`, evals and the marketplace |
| `scripts/` | marketplace generator, verifier, scaffolder, portable export |
| `docs/` | architecture, authoring rules, review checklist, privacy, releases |

## Published plugins

| Plugin | Status | Purpose |
|---|---|---|
| [`research-core`](plugins/research-core/README.md) | draft | Cross-disciplinary source, design, analysis, review, visualization, and writing workflows. |

`example-domain` is a non-published reference fixture for authors and CI. It is intentionally kept because it proves the scaffold, deterministic-script, critic-agent, and portable-export paths without depending on a live plugin.

## Documentation

- [AGENTS.md](AGENTS.md) — the instruction an agent reads before touching this repository
- [Architecture and decisions](docs/architecture.md)
- [Authoring skills and plugins](docs/authoring.md)
- [Review checklist](docs/review-checklist.md)
- [Content privacy policy](docs/sanitization-policy.md)
- [Versions and releases](docs/release-process.md)
- [How to propose a plugin](CONTRIBUTING.md)
