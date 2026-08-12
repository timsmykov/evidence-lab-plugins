# Getting into the catalogue

There is one path: propose → review → publish. No manual exceptions, because an exception to the process quickly becomes the process.

## 1. Propose

Open an issue answering five questions:

1. Which recurring piece of work does this cover, and how often does it come up?
2. Where does the procedure come from — whose practice, which run, which debrief?
3. What is the output, and how do you check that it came out right?
4. Which steps have to be deterministic?
5. What in the source material is private and must be stripped before publication?

A proposal that cannot answer question two is not reviewed. A skill derived from general reasoning rather than practice is the model paraphrasing itself.

## 2. Build

```bash
git checkout -b plugin/<name>
python3 scripts/new_plugin.py <name> --skill <skill> --owner <owner> --reviewer <reviewer>
```

Fill in `SKILL.md`, `meta.json` (especially `provenance`), the eval set and, where there are deterministic steps, `scripts/`. Before opening the pull request:

```bash
python3 scripts/build_marketplace.py
python3 scripts/verify_repo.py
```

## 3. Review

The reviewer named in `meta.json` takes the pull request; for `production` status they must not be the owner. They work through the [checklist](docs/review-checklist.md), and the thing they actually have to establish is whether the result reproduces on a real example — not whether the skill reads convincingly.

Attach the verifier output and one real run: the input, the artefact, and what came out wrong.

## 4. Publish

After merge the plugin appears in the shop window automatically — `marketplace.json` is rebuilt from `plugins/`. Status moves to `production` only once the plugin has done a real job at least once and `reviewed_at` is set in `meta.json`.

## What we do not take

- Work built for a single occasion that will not recur.
- Skills that cannot run without access to private infrastructure.
- Logs of completed work dressed up as a procedure.
- Anything carrying other people's personal data or the contents of client documents.
