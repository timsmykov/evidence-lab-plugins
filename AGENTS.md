# Working in this repository

This is a marketplace of domain plugins for research work. A plugin bundles several skills from one subject area into an installable unit. You are most likely here to add a plugin, extend one, or review a change to one.

Read this file first. Read `docs/` only when this file points you there.

## Layout

| Path | What it is |
|---|---|
| `plugins/<name>/` | a plugin: `.claude-plugin/plugin.json`, `meta.json`, `skills/`, optional `commands/`, `agents/` |
| `plugins/<name>/skills/<skill>/` | `SKILL.md` plus optional `scripts/`, `templates/`, `references/`, and a required `evals/trigger_eval.json` |
| `templates/plugin/` | the scaffold; copy it via the script, never by hand |
| `schemas/` | JSON schemas the verifier enforces |
| `scripts/` | verifier, marketplace generator, scaffolder, portable export |
| `.claude-plugin/marketplace.json` | generated shop window — never edit it |

`plugins/example-domain` is a reference implementation. Study it; do not copy it and do not extend it with real work.

## Adding a plugin

```bash
python3 scripts/new_plugin.py <plugin-name> --skill <skill-name> --owner <owner> --reviewer <reviewer>
# write the real procedure, fill meta.json provenance, replace every eval case
python3 scripts/build_marketplace.py
git add -A && git commit          # commit before verifying: the version check diffs against origin/main
python3 scripts/verify_repo.py
```

Then open a pull request. Direct pushes to `main` are rejected; `verify` must be green.

## Rules the verifier enforces

Do not try to work around these. If a rule is genuinely wrong, narrow it in a separate reviewed change.

- **English only.** Cyrillic anywhere fails the build. A translation goes in a companion `*.ru.md` / `*.ru.json` file beside the English original, never inline.
- **Every skill needs `evals/trigger_eval.json`** with at least 8 cases and at least 3 negatives. Negatives come from neighbouring skills in the same plugin.
- **Descriptions are routing, not marketing.** At least 80 characters, naming the phrasings that load the skill and the near misses that must not.
- **`meta.json` lists every skill on disk**, and `provenance` names whose practice the procedure came from.
- **Version bumps are mandatory** when plugin content changes; update the plugin's `CHANGELOG.md` in the same commit.
- **No placeholders in `plugins/`.** `REPLACE ME` and `__SKILL__` left in a plugin fail the build.
- **No private data.** Tokens, IPs, private host paths, email addresses, client or student document contents, internal page links, bare UUIDs.
- **Production status** requires a reviewer different from the owner and a `provenance.reviewed_at` date.

## How to write a skill

The full guidance is in `docs/authoring.md`. The three things that matter most:

1. **Write it after doing the work by hand at least once.** A procedure derived from general reasoning rather than practice is the model paraphrasing itself, and it collapses on the first real task.
2. **Split the model from the script.** If a step must return the same result on a rerun — deduplication, table assembly, citation formatting, template filling — it belongs in `scripts/`, runnable standalone, not in prompt text.
3. **Put in a confirmation point.** Where the procedure picks criteria or boundaries, stop and let the researcher approve. Without it a model hypothesis silently becomes the result.

## What not to do

- Do not hand-edit `.claude-plugin/marketplace.json`; run `scripts/build_marketplace.py`.
- Do not delete or loosen a check in `scripts/verify_repo.py` to get CI green.
- Do not add a `shared/` skills directory — reuse is deliberately deferred until a real duplicate exists (see `docs/architecture.md`).
- Do not commit `dist/`; it is build output.
- Do not mark a plugin `production` because it looks finished. That status means it ran on a real task.
