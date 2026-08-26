# Versions and releases

## The plugin is versioned, not the repository

Each plugin carries its own version in `.claude-plugin/plugin.json`, following SemVer:

- **MAJOR** — the procedure changed such that earlier results are no longer reproducible.
- **MINOR** — a skill, command or step was added.
- **PATCH** — wording, templates, evals; the procedure is unchanged.

CI diffs plugin content against `origin/main` and fails when files changed while the version stayed put. This guards against a quiet edit to a procedure, after which two runs can no longer be compared.

## Flow of a change

1. Branch `plugin/<name>` or `fix/<what>`.
2. Edits, version bump, entry in the plugin's `CHANGELOG.md`.
3. `python3 scripts/build_adapters.py` — both native manifests, marketplaces, and the Core catalog are rebuilt.
4. `python3 scripts/verify_repo.py` — the gate is green.
5. Pull request with the verifier output and a real run.
6. Review against the checklist, merge.

Claude Code and Codex have separate native adapter gates. `scripts/build_adapters.py` generates both manifests from `pack.json`, and `scripts/test_agent_first.py` checks their semantic parity. A host must be listed in `pack.json` and `meta.json` only after its native acceptance checks pass.

`main` is protected: direct pushes, force pushes and branch deletion are rejected.

## Statuses

`draft` — proposed, unverified. `review` — under review. `production` — reviewed and used on a real task; requires a reviewer distinct from the owner and a `reviewed_at` date. `reference` — a format exemplar, excluded from the shop window. `deprecated` — retired, kept in the repository for the record.

## Tags

Pack SemVer records which individual procedures changed. GitHub-first distribution
uses one immutable repository snapshot tag and a release lock containing every
pack version and content hash; bootstrap pins that snapshot, not a floating branch
or an arbitrary per-pack tag. The snapshot tooling is delivered in R5 of
`docs/github-first-execution-plan.md`. Until that gate exists and passes, a merged
pack version is not yet a public Evidence Lab distribution release.

## When the gate fails

Fix the cause. If a rule really is too broad, narrow it in a separate change with the reasoning in the pull request. Deleting a check to get CI green is not allowed: a gate that can be switched off the moment it is inconvenient is not a gate.
