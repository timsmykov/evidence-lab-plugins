# Changelog — task-operations

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow [SemVer](https://semver.org/).

MAJOR — the procedure changed such that earlier results are no longer reproducible.
MINOR — a skill, command, or step was added.
PATCH — wording, templates, evals; the procedure is unchanged.

## [0.2.0] — 2026-08-27

### Changed
- Generalized the pack and `task-intake` skill for any project or shared task board.
- Replaced the project-specific gate with a neutral commitment gate while retaining local field mapping.
- Added deterministic global rank alongside per-owner rank.
- Made executor assignment and independent review part of the readiness contract.
