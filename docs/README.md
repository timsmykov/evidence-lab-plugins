# Evidence Lab documentation

Use this page as the documentation home. Guides are grouped by what you are trying to accomplish, not by the repository directory that stores them.

## For researchers

| What you want to do | Read |
|---|---|
| Install all skills without onboarding | [Getting started](getting-started.md) |
| Find the right skill and expected output | [Skill catalogue](skills.md) |
| Understand which skills are mature or experimental | [Skill-pack readiness](skill-pack-readiness.md) |
| Use the optional profile-based installer | [Onboarding start](../START.md), [Russian start](../START.ru.md), and [bootstrap contract](../BOOTSTRAP.md) |
| Understand privacy and safe content boundaries | [Security](../SECURITY.md) and [sanitization policy](sanitization-policy.md) |

## For skill authors and reviewers

| What you want to do | Read |
|---|---|
| Understand a good skill's structure | [Skill and pack authoring](authoring.md) |
| Add a pack and run repository checks | [Contributing](../CONTRIBUTING.md) |
| Accept or reject a skill using evidence | [Review checklist](review-checklist.md) |
| Understand packs, bundles, adapters, and trust boundaries | [Architecture](architecture.md) |
| Version and publish a pack | [Release process](release-process.md) |
| Understand licensing and redistribution | [Licensing](../LICENSING.md), [third-party notices](../THIRD_PARTY_NOTICES.md), and [trademarks](../TRADEMARKS.md) |

## Technical reference

- [L0-L2 technical stack](l0-l2-technical-stack.md) and [Russian version](l0-l2-technical-stack.ru.md)
- [External plugin verification contract](external-plugin-verification.md)
- [GitHub-first execution plan](github-first-execution-plan.md)
- [Repository agent instructions](../AGENTS.md) and the [Claude Code instruction entrypoint](../CLAUDE.md)

## Audit and decision records

These pages preserve evidence and project history. New users normally do not need them to install or choose a skill.

- [Pack-boundary evidence report](pack-boundary-report.md)
- [OpenAI Codex plugin audit](openai-plugin-audit.md)
- [Open-source foundation skill audit](research/open-source-foundation-skill-audit-2026-08-27.md)
- [Onboarding experiment protocol](qa/onboarding-experiment-protocol.md)
- [20-scenario onboarding acceptance record](qa/onboarding-terra-20-2026-08-28.md)

## Source-of-truth map

| Question | Canonical source |
|---|---|
| What can a user install? | Marketplace manifests generated from each `pack.json` |
| Which skills are in the all-in-one plugin? | `packs/core/evidence-lab-research/meta.json` |
| What does each skill do for a user? | [Skill catalogue](skills.md), generated from `catalog/skill-docs.json` plus canonical pack metadata |
| Where is a skill maintained? | The focused pack linked from its row in the [catalogue](skills.md) |
| How ready is a skill? | Its canonical `meta.json`, summarized in [skill-pack readiness](skill-pack-readiness.md) |
| What version is supported? | The latest immutable GitHub release and its `release-lock.json` |

Return to the [project README](../README.md).
