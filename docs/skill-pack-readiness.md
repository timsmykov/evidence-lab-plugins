# Skill-pack readiness inventory

Generated deterministically by `python3 scripts/audit_skill_packs.py`.

## Summary

- Working packs: **13**; reference-only packs: **1**.
- Working skills: **24** — 21 research skills, 1 onboarding skill, and 2 compatibility routers.
- Lifecycle: **13 of 13 working packs are `draft`**.
- Trigger eval files present: **24 of 24**.
- Compact research skills needing deeper representative review: **5**.

`draft` does not mean that the package is un-installable. It means scientific/content acceptance is incomplete even when repository, selection, release, and bootstrap checks pass.

## Packs, boundaries, and current status

| Pack | Layer | Version | Skills | Capabilities | Selection | Status |
|---|---|---:|---:|---|---|---|
| `evidence-lab-core` | `core` | `0.10.0` | 4 | `onboarding`, `pack-selection`, `companion-plugin-planning`, `installation-lifecycle`, `paper-lookup`, `citation-management`, `critical-thinking` | always | `draft` |
| `life-sciences` | `domain` | `0.1.1` | 1 | `life-science-protocols` | `life-science-planning`, `life-science-images` | `draft` |
| `quantitative-sciences` | `domain` | `0.3.1` | 4 | `statistical-analysis`, `statistical-power`, `uncertainty-and-units`, `scientific-visualization` | `quantitative-method` | `draft` |
| `data-and-pdf` | `workflow` | `1.0.1` | 1 | `data-and-pdf-compatibility` | `data-and-pdf-full-cycle-datasets`, `data-and-pdf-full-cycle-tables` | `draft` |
| `document-evidence` | `workflow` | `0.1.1` | 1 | `document-conversion` | `document-evidence-material` | `draft` |
| `full-research-cycle` | `workflow` | `1.0.1` | 1 | `full-research-cycle-compatibility` | `full-cycle-workflow` | `draft` |
| `literature-publication` | `workflow` | `0.1.1` | 4 | `literature-review`, `academic-writing`, `peer-review`, `research-diagrams` | `literature-publication-workflow`, `literature-publication-writing` | `draft` |
| `publication-monitoring` | `workflow` | `0.1.1` | 1 | `publication-monitoring` | `publication-monitoring-workflow` | `draft` |
| `qualitative-research` | `workflow` | `0.1.1` | 1 | `qualitative-analysis` | `qualitative-material` | `draft` |
| `research-design` | `workflow` | `0.1.1` | 2 | `hypothesis-generation`, `study-design` | `research-design-workflow` | `draft` |
| `research-images` | `workflow` | `0.1.1` | 1 | `research-image-analysis` | `research-image-material` | `draft` |
| `structured-data-analysis` | `workflow` | `0.1.1` | 2 | `database-lookup`, `exploratory-data-analysis` | `structured-data-material`, `structured-data-collection` | `draft` |
| `systematic-review` | `workflow` | `0.1.1` | 1 | `systematic-search`, `screening-and-deduplication` | `systematic-review-stage` | `draft` |

## Skills

| Pack | Skill | Role | SKILL.md lines | Scripts | References | Trigger eval | Review signal |
|---|---|---|---:|---:|---:|---|---|
| `evidence-lab-core` | `citation-management` | `research` | 328 | 8 | 10 | yes | standard draft review |
| `evidence-lab-core` | `evidence-lab-onboarding` | `onboarding` | 125 | 4 | 1 | yes | standard draft review |
| `evidence-lab-core` | `paper-lookup` | `research` | 262 | 5 | 11 | yes | standard draft review |
| `evidence-lab-core` | `scientific-critical-thinking` | `research` | 165 | 0 | 7 | yes | standard draft review |
| `life-sciences` | `life-science-protocols` | `research` | 20 | 1 | 0 | yes | deeper representative review |
| `quantitative-sciences` | `scientific-visualization` | `research` | 284 | 7 | 5 | yes | standard draft review |
| `quantitative-sciences` | `statistical-analysis` | `research` | 450 | 1 | 5 | yes | standard draft review |
| `quantitative-sciences` | `statistical-power` | `research` | 199 | 2 | 3 | yes | standard draft review |
| `quantitative-sciences` | `uncertainty-and-units` | `research` | 383 | 7 | 6 | yes | standard draft review |
| `data-and-pdf` | `data-and-pdf-router` | `compatibility-router` | 10 | 0 | 0 | yes | standard draft review |
| `document-evidence` | `markitdown` | `research` | 263 | 3 | 7 | yes | standard draft review |
| `full-research-cycle` | `full-research-cycle-router` | `compatibility-router` | 10 | 0 | 0 | yes | standard draft review |
| `literature-publication` | `literature-review` | `research` | 187 | 3 | 5 | yes | standard draft review |
| `literature-publication` | `markdown-mermaid-writing` | `research` | 278 | 0 | 3 | yes | standard draft review |
| `literature-publication` | `peer-review` | `research` | 287 | 8 | 6 | yes | standard draft review |
| `literature-publication` | `writing-skill` | `research` | 86 | 0 | 4 | yes | standard draft review |
| `publication-monitoring` | `publication-monitoring` | `research` | 20 | 1 | 0 | yes | deeper representative review |
| `qualitative-research` | `qualitative-analysis` | `research` | 20 | 1 | 0 | yes | deeper representative review |
| `research-design` | `experimental-design` | `research` | 233 | 2 | 4 | yes | standard draft review |
| `research-design` | `hypothesis-generation` | `research` | 263 | 8 | 10 | yes | standard draft review |
| `research-images` | `research-image-analysis` | `research` | 20 | 1 | 0 | yes | deeper representative review |
| `structured-data-analysis` | `database-lookup` | `research` | 386 | 0 | 80 | yes | standard draft review |
| `structured-data-analysis` | `exploratory-data-analysis` | `research` | 279 | 13 | 6 | yes | standard draft review |
| `systematic-review` | `systematic-review` | `research` | 21 | 1 | 0 | yes | deeper representative review |

## Readiness interpretation

- **Mechanically ready:** both hosts can receive immutable pack versions; schemas, trigger evals, deterministic scenario selection, installation planning, and host readback are covered by repository tests.
- **Not yet production-accepted:** all working packs remain `draft`; representative real research runs and independent domain review are still required.
- **Highest content-review priority:** compact additions with little reference depth, currently life-science protocols, publication monitoring, qualitative analysis, research-image analysis, and systematic review.
- **Compatibility only:** `data-and-pdf-router` and `full-research-cycle-router` carry no independent research method; their packs compose focused dependencies.

## Deterministic installation path

1. Chat answers are normalized to controlled profile values. Free text can propose values, but it cannot name install targets.
2. Stable rules in each `pack.json` select packs; Core is mandatory.
3. Dependencies are resolved and ordered by layer, then pack ID.
4. Bootstrap locks exact versions from the release snapshot and renders a plain-language plan.
5. Nothing is applied until confirmation; the host is read back afterward and state becomes `ready` only when exact versions match.
6. External Codex plugins use a separate reviewed registry because Claude cannot install Codex directory plugins and Codex apps may require an account connection.
