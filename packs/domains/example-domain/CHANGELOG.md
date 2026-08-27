# Changelog — example-domain

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow [SemVer](https://semver.org/).

MAJOR — the procedure changed such that earlier results are no longer reproducible.
MINOR — a skill, command or step was added.
PATCH — wording, templates, evals; the procedure is unchanged.

## [0.1.5] — 2026-08-27

### Changed
- Relicensed the reference fixture under MIT.

## [0.1.4] — 2026-08-26

### Changed
- Added an explicit pack-level license expression to the reference fixture.

## [0.1.3] — 2026-08-26

### Changed
- Updated the reference pack to the Selection Policy v1 rule contract.

## [0.1.2] — 2026-08-12

### Changed
- Removed the remaining Russian trigger phrases and eval queries. The registry is English-only; the verifier now fails on Cyrillic anywhere, and translations belong in a separate `*.ru.md` companion file.

## [0.1.1] — 2026-08-12

### Changed
- Translated to English in line with the registry's English-first policy. Trigger phrases in the skill descriptions and the eval sets keep their Russian queries — routing is tested in both languages.

## [0.1.0] — 2026-08-12

### Added
- Reference plugin structure: the `example-procedure` and `example-checklist` skills, the `/example-domain` command, a reviewer subagent, eval sets and a deterministic table builder.
