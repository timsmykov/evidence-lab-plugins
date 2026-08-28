# Changelog — Evidence Lab Core

## [0.15.1] — 2026-08-28

### Fixed
- The plan command can now write and print the canonical localized recommendation in the same deterministic operation, preventing a raw package list from replacing the user-facing plan.

## [0.15.0] — 2026-08-28

### Changed
- Language choice and all four onboarding questions now have a deterministic renderer whose output must be shown verbatim.
- Plan confirmation now fails closed unless the canonical localized recommendation heading is visible; raw package IDs are not an acceptable substitute.

## [0.14.0] — 2026-08-28

### Added
- Optional onboarding selection and localized plan copy for the Evidence Lab meeting-capture workflow.

## [0.13.0] — 2026-08-27

### Added
- An English-first language choice before onboarding, with deterministic English and Russian resolution and no LLM classification.

### Changed
- The setup contract now avoids redundant source dumps and duplicate host readback after a verified installation state.

## [0.12.1] — 2026-08-27

### Fixed
- Claude Code marketplace validation now recognizes the host's canonical `url` readback while continuing to reject a different repository.

## [0.12.0] — 2026-08-27

### Added
- A generated foundation index that pins all 20 physical researcher skills to owning packs, quality states, capability mappings, and content hashes.

### Changed
- Bootstrap now includes every declared foundation pack for every researcher profile while keeping unfinished capabilities and optional add-ons outside the base installation.

## [0.11.0] — 2026-08-27

### Added
- Mandatory host-neutral personal skill authoring with a plain-chat workflow, safe scaffolder, validator, quality checklist, and trigger boundary tests.
- Explicit skill-level quality states and a 27-capability foundation roadmap with visible implementation gaps.

## [0.10.0] — 2026-08-27

### Added
- Deterministic Codex companion-plugin planning from a reviewed, version-observed registry.
- Separate actions for skills-only candidates, explicit opt-ins, app connections, and benchmark-blocked components; Claude Code remains portable and receives no Codex directory actions.

## [0.9.0] — 2026-08-27

### Added
- App-first Codex and Claude Code entrypoints with a four-question chat contract.
- Deterministic English and Russian recommendation rendering before installation approval.

## [0.8.1] — 2026-08-27

### Changed
- Relicensed Evidence Lab-owned content under MIT while preserving bundled MIT notices.

## [0.8.0] — 2026-08-26

### Added
- Stable release-lock validation and immutable release identity in installation and reconciliation state.
- Exact release tag, source commit, and canonical lock digest checks before plan creation.
- Mandatory lock revalidation before lifecycle mutations, including the previous release lock before rollback or restore.

## [0.7.0] — 2026-08-26

### Added
- Deterministic reconciliation with exact add, update, retain, and removal-candidate diffs.
- Stale-plan rejection, pre-change snapshots, interrupted-run recovery, separately approved removal, and exact restore readback.

## [0.6.0] — 2026-08-26

### Changed
- Added an explicit pack-level license expression for generated host manifests.
- Added the focused `design-study` workflow option and exact all-value matching support for deterministic pack boundaries.

## [0.5.0] — 2026-08-26

### Added
- Deterministic option normalization and a schema-bounded validator for untrusted free-text classification candidates.
- Confidence gating, focused follow-up behavior, prompt-injection fixtures, and Russian/English semantic parity tests.

## [0.4.0] — 2026-08-26

### Changed
- Added Selection Policy v1 as the controlled vocabulary and matching contract.
- Replaced implicit broad matching with stable, explainable rule IDs.

## [0.3.0] — 2026-08-26

### Added
- GitHub-first bootstrap contract for clean Codex and Claude Code installations.
- Deterministic installation plans, explicit confirmation, atomic state writes, host readback, idempotent retries, and bounded rollback.
- Canonical English and Russian onboarding question catalogs.

## [0.2.0] — 2026-08-26

### Changed
- Reframed the package as the agent-first universal core for Claude Code and Codex.
- Moved workflow, data, and quantitative procedures into separately installable packs.

### Added
- Fast chat onboarding and deterministic pack selection.

## [0.1.0] — 2026-08-25

### Added
- Initial cross-disciplinary research skill collection, before its agent-first decomposition.
