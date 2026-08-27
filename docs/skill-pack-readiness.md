# Skill-pack readiness inventory

Generated deterministically by `python3 scripts/audit_skill_packs.py`.

## Summary

- Working packs: **13**; reference-only packs: **1**.
- Working skills: **25** — 21 research skills, 1 onboarding skill, 1 personal skill-authoring skill, and 2 compatibility routers.
- Lifecycle: **13 of 13 working packs are `draft`**.
- Trigger eval files present: **25 of 25**.
- Explicit quality states: **5 need substantive work**, **18 need representative testing**, **0 review-ready**, **0 production**, and **2 support-only**.

`draft` does not mean that the package is un-installable. It means scientific/content acceptance is incomplete even when repository, selection, release, and bootstrap checks pass.

## Foundation target

The bounded cross-disciplinary target contains **27 skills**: **6 planned**, **3 implemented but needing substantive work**, and **18 implemented but needing representative testing**.

This is the capability library from which deterministic onboarding selects a researcher's setup; it is not a requirement to install all 27 skills for every user. Personal skill authoring is mandatory through Core, while domain and workflow add-ons remain conditional.

| Priority | Foundation capability | Group | Current implementation | State |
|---|---|---|---|---|
| P0 | `personal-skill-authoring` | `workspace` | `personal-skill-authoring` | `implemented-needs-representative-testing` |
| P0 | `paper-lookup` | `sources` | `paper-lookup` | `implemented-needs-representative-testing` |
| P0 | `citation-management` | `sources` | `citation-management` | `implemented-needs-representative-testing` |
| P0 | `scientific-critical-thinking` | `reasoning` | `scientific-critical-thinking` | `implemented-needs-representative-testing` |
| P0 | `document-normalization` | `documents` | `markitdown` | `implemented-needs-representative-testing` |
| P0 | `evidence-extraction` | `documents` | — | `planned` |
| P0 | `literature-review` | `synthesis` | `literature-review` | `implemented-needs-representative-testing` |
| P0 | `systematic-review` | `synthesis` | `systematic-review` | `implemented-needs-substantive-work` |
| P0 | `hypothesis-generation` | `design` | `hypothesis-generation` | `implemented-needs-representative-testing` |
| P0 | `experimental-design` | `design` | `experimental-design` | `implemented-needs-representative-testing` |
| P1 | `preregistration` | `design` | `hypothesis-generation` | `implemented-needs-representative-testing` |
| P0 | `statistical-power` | `design` | `statistical-power` | `implemented-needs-representative-testing` |
| P1 | `database-lookup` | `data` | `database-lookup` | `implemented-needs-representative-testing` |
| P0 | `data-cleaning-and-provenance` | `data` | — | `planned` |
| P0 | `exploratory-data-analysis` | `data` | `exploratory-data-analysis` | `implemented-needs-representative-testing` |
| P0 | `statistical-analysis` | `analysis` | `statistical-analysis` | `implemented-needs-representative-testing` |
| P0 | `uncertainty-and-units` | `analysis` | `uncertainty-and-units` | `implemented-needs-representative-testing` |
| P0 | `qualitative-analysis` | `analysis` | `qualitative-analysis` | `implemented-needs-substantive-work` |
| P1 | `research-image-analysis` | `analysis` | `research-image-analysis` | `implemented-needs-substantive-work` |
| P0 | `scientific-visualization` | `communication` | `scientific-visualization` | `implemented-needs-representative-testing` |
| P1 | `research-diagrams` | `communication` | `markdown-mermaid-writing` | `implemented-needs-representative-testing` |
| P0 | `academic-writing` | `publication` | `writing-skill` | `implemented-needs-representative-testing` |
| P0 | `peer-review` | `publication` | `peer-review` | `implemented-needs-representative-testing` |
| P0 | `latex-and-venue-formatting` | `publication` | — | `planned` |
| P0 | `reproducible-computation` | `reproducibility` | — | `planned` |
| P1 | `research-data-management` | `reproducibility` | — | `planned` |
| P1 | `research-log-and-decision-trail` | `reproducibility` | — | `planned` |

## Packs, boundaries, and current status

| Pack | Layer | Version | Skills | Capabilities | Selection | Status |
|---|---|---:|---:|---|---|---|
| `evidence-lab-core` | `core` | `0.12.1` | 5 | `onboarding`, `pack-selection`, `companion-plugin-planning`, `installation-lifecycle`, `personal-skill-authoring`, `paper-lookup`, `citation-management`, `critical-thinking` | always | `draft` |
| `life-sciences` | `domain` | `0.1.2` | 1 | `life-science-protocols` | `life-science-planning`, `life-science-images` | `draft` |
| `quantitative-sciences` | `domain` | `0.4.0` | 4 | `statistical-analysis`, `statistical-power`, `uncertainty-and-units`, `scientific-visualization` | `quantitative-method` | `draft` |
| `data-and-pdf` | `workflow` | `1.0.2` | 1 | `data-and-pdf-compatibility` | `data-and-pdf-full-cycle-datasets`, `data-and-pdf-full-cycle-tables` | `draft` |
| `document-evidence` | `workflow` | `0.2.0` | 1 | `document-conversion` | `document-evidence-material` | `draft` |
| `full-research-cycle` | `workflow` | `1.0.2` | 1 | `full-research-cycle-compatibility` | `full-cycle-workflow` | `draft` |
| `literature-publication` | `workflow` | `0.2.0` | 4 | `literature-review`, `academic-writing`, `peer-review`, `research-diagrams` | `literature-publication-workflow`, `literature-publication-writing` | `draft` |
| `publication-monitoring` | `workflow` | `0.1.2` | 1 | `publication-monitoring` | `publication-monitoring-workflow` | `draft` |
| `qualitative-research` | `workflow` | `0.2.0` | 1 | `qualitative-analysis` | `qualitative-material` | `draft` |
| `research-design` | `workflow` | `0.2.0` | 2 | `hypothesis-generation`, `study-design` | `research-design-workflow` | `draft` |
| `research-images` | `workflow` | `0.2.0` | 1 | `research-image-analysis` | `research-image-material` | `draft` |
| `structured-data-analysis` | `workflow` | `0.2.0` | 2 | `database-lookup`, `exploratory-data-analysis` | `structured-data-material`, `structured-data-collection` | `draft` |
| `systematic-review` | `workflow` | `0.2.0` | 1 | `systematic-search`, `screening-and-deduplication` | `systematic-review-stage` | `draft` |

## Skills

| Pack | Skill | Role | SKILL.md lines | Scripts | References | Trigger eval | Quality status |
|---|---|---|---:|---:|---:|---|---|
| `evidence-lab-core` | `citation-management` | `research` | 328 | 8 | 10 | yes | `needs-representative-testing` |
| `evidence-lab-core` | `evidence-lab-onboarding` | `onboarding` | 125 | 4 | 1 | yes | `needs-representative-testing` |
| `evidence-lab-core` | `paper-lookup` | `research` | 262 | 5 | 11 | yes | `needs-representative-testing` |
| `evidence-lab-core` | `personal-skill-authoring` | `skill-authoring` | 102 | 2 | 1 | yes | `needs-representative-testing` |
| `evidence-lab-core` | `scientific-critical-thinking` | `research` | 165 | 0 | 7 | yes | `needs-representative-testing` |
| `life-sciences` | `life-science-protocols` | `research` | 20 | 1 | 0 | yes | `needs-substantive-work` |
| `quantitative-sciences` | `scientific-visualization` | `research` | 284 | 7 | 5 | yes | `needs-representative-testing` |
| `quantitative-sciences` | `statistical-analysis` | `research` | 450 | 1 | 5 | yes | `needs-representative-testing` |
| `quantitative-sciences` | `statistical-power` | `research` | 199 | 2 | 3 | yes | `needs-representative-testing` |
| `quantitative-sciences` | `uncertainty-and-units` | `research` | 383 | 7 | 6 | yes | `needs-representative-testing` |
| `data-and-pdf` | `data-and-pdf-router` | `compatibility-router` | 10 | 0 | 0 | yes | `support-only` |
| `document-evidence` | `markitdown` | `research` | 263 | 3 | 7 | yes | `needs-representative-testing` |
| `full-research-cycle` | `full-research-cycle-router` | `compatibility-router` | 10 | 0 | 0 | yes | `support-only` |
| `literature-publication` | `literature-review` | `research` | 187 | 3 | 5 | yes | `needs-representative-testing` |
| `literature-publication` | `markdown-mermaid-writing` | `research` | 278 | 0 | 2 | yes | `needs-representative-testing` |
| `literature-publication` | `peer-review` | `research` | 287 | 8 | 6 | yes | `needs-representative-testing` |
| `literature-publication` | `writing-skill` | `research` | 86 | 0 | 1 | yes | `needs-representative-testing` |
| `publication-monitoring` | `publication-monitoring` | `research` | 20 | 1 | 0 | yes | `needs-substantive-work` |
| `qualitative-research` | `qualitative-analysis` | `research` | 20 | 1 | 0 | yes | `needs-substantive-work` |
| `research-design` | `experimental-design` | `research` | 233 | 2 | 4 | yes | `needs-representative-testing` |
| `research-design` | `hypothesis-generation` | `research` | 263 | 8 | 10 | yes | `needs-representative-testing` |
| `research-images` | `research-image-analysis` | `research` | 20 | 1 | 0 | yes | `needs-substantive-work` |
| `structured-data-analysis` | `database-lookup` | `research` | 386 | 0 | 80 | yes | `needs-representative-testing` |
| `structured-data-analysis` | `exploratory-data-analysis` | `research` | 279 | 13 | 6 | yes | `needs-representative-testing` |
| `systematic-review` | `systematic-review` | `research` | 21 | 1 | 0 | yes | `needs-substantive-work` |

## Readiness interpretation

- **Mechanically ready:** both hosts can receive immutable pack versions; schemas, trigger evals, deterministic scenario selection, installation planning, and host readback are covered by repository tests.
- **Not yet production-accepted:** all working packs remain `draft`; representative real research runs and independent domain review are still required.
- **Highest content-development priority:** skills explicitly marked `needs-substantive-work`, currently life-science protocols, publication monitoring, qualitative analysis, research-image analysis, and systematic review. Their exact work items live in `meta.json`.
- **Host-independent skill creation:** `personal-skill-authoring` is part of mandatory Core. Native Codex or Claude authoring tools may accelerate it, but bootstrap does not assume that an optional host plugin is installed.
- **Compatibility only:** `data-and-pdf-router` and `full-research-cycle-router` carry no independent research method; their packs compose focused dependencies.

## Deterministic installation path

1. Chat answers are normalized to controlled profile values. Free text can propose values, but it cannot name install targets.
2. Stable rules in each `pack.json` select packs; Core is mandatory.
3. Dependencies are resolved and ordered by layer, then pack ID.
4. Bootstrap locks exact versions from the release snapshot and renders a plain-language plan.
5. Nothing is applied until confirmation; the host is read back afterward and state becomes `ready` only when exact versions match.
6. External Codex plugins use a separate reviewed registry because Claude cannot install Codex directory plugins and Codex apps may require an account connection.
