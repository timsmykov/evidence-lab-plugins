# Evidence Lab Core — optional onboarding

The optional Evidence Lab personalization and foundation plugin. It runs the
short researcher onboarding and creates an explainable pack plan. Users who
want the complete skill library without onboarding should install the separate
`evidence-lab-research` plugin instead.

The host-neutral contract is `pack.json`. Claude Code and Codex manifests are generated from it and load the same `skills/` directory.

Numbered onboarding choices are normalized deterministically. Free-text answers
are treated as untrusted data and can only propose values from the reviewed
Selection Policy before deterministic validation. See the
[`evidence-lab-onboarding` procedure](skills/evidence-lab-onboarding/SKILL.md)
and its [free-text normalization contract](skills/evidence-lab-onboarding/references/normalization-contract.md).

## Skills

- `evidence-lab-onboarding` — profile and pack selection.
- `paper-lookup` — scholarly discovery and identifiers.
- `citation-management` — citation verification and formatting.
- `scientific-critical-thinking` — claim and evidence-quality audit.

Current status is `draft`; see `meta.json` for provenance and review state.
