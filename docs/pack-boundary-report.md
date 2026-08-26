# Pack-boundary evidence report

Generated deterministically by `python3 scripts/analyze_pack_boundaries.py`.
It measures the current catalog before any proposed R3 split or addition.
Core capabilities are treated as the mandatory baseline and are not counted as over-installation.

## Summary

- Scenarios: **16**
- Missing required capability occurrences: **12**
- Over-installed optional-pack capability occurrences: **35**

## Scenario matrix

| Scenario | Selected packs | Missing required capabilities | Over-installed capabilities |
|---|---|---|---|
| `general-paper-lookup` | `evidence-lab-core` | — | — |
| `pdf-evidence-extraction` | `evidence-lab-core`, `data-and-pdf` | — | `database-lookup`, `exploratory-data-analysis` |
| `structured-data-analysis` | `evidence-lab-core`, `data-and-pdf` | — | `document-conversion` |
| `mathematical-model-review` | `evidence-lab-core`, `full-research-cycle`, `quantitative-sciences` | — | `academic-writing`, `hypothesis-generation`, `literature-review`, `research-diagrams`, `scientific-visualization`, `study-design` |
| `full-cycle-quantitative-paper` | `evidence-lab-core`, `data-and-pdf`, `full-research-cycle`, `quantitative-sciences` | — | — |
| `literature-review-only` | `evidence-lab-core`, `full-research-cycle` | — | `hypothesis-generation`, `research-diagrams`, `study-design` |
| `publication-preparation-only` | `evidence-lab-core`, `full-research-cycle` | — | `hypothesis-generation`, `study-design` |
| `publication-monitoring-life-sciences` | `evidence-lab-core` | `publication-monitoring` | — |
| `publication-monitoring-physics` | `evidence-lab-core`, `quantitative-sciences` | `publication-monitoring` | `scientific-visualization`, `statistical-analysis`, `statistical-power`, `uncertainty-and-units` |
| `systematic-review-life-sciences` | `evidence-lab-core`, `data-and-pdf`, `full-research-cycle`, `quantitative-sciences` | `screening-and-deduplication`, `systematic-search` | `database-lookup`, `hypothesis-generation`, `research-diagrams`, `scientific-visualization`, `statistical-power`, `study-design`, `uncertainty-and-units` |
| `systematic-review-social-sciences` | `evidence-lab-core`, `data-and-pdf`, `full-research-cycle` | `screening-and-deduplication`, `systematic-search` | `database-lookup`, `exploratory-data-analysis`, `hypothesis-generation`, `research-diagrams`, `study-design` |
| `qualitative-social-analysis` | `evidence-lab-core` | `qualitative-analysis` | — |
| `qualitative-humanities-analysis` | `evidence-lab-core` | `qualitative-analysis` | — |
| `research-images-engineering` | `evidence-lab-core`, `quantitative-sciences` | `research-image-analysis` | `statistical-analysis`, `statistical-power` |
| `research-images-life-sciences` | `evidence-lab-core` | `life-science-protocols`, `research-image-analysis` | — |
| `life-science-study-design` | `evidence-lab-core`, `full-research-cycle` | `life-science-protocols` | `academic-writing`, `peer-review`, `research-diagrams` |

## Current pack coverage

- `evidence-lab-core`: selected by 16 scenario(s); mandatory baseline; exclusion is intentionally not applicable.
- `quantitative-sciences`: selected by 5 scenario(s); negative scenarios include `general-paper-lookup`.
- `data-and-pdf`: selected by 5 scenario(s); negative scenarios include `general-paper-lookup`.
- `full-research-cycle`: selected by 7 scenario(s); negative scenarios include `general-paper-lookup`.

## Split or keep decisions

### `evidence-lab-core` — KEEP

The mandatory foundation is used by every scenario and its evidence, citation, critical-thinking, and onboarding responsibilities form one trust boundary.

Target boundary: Retain as the mandatory baseline and do not add domain or workflow procedures.

Evidence: `general-paper-lookup`, `publication-monitoring-life-sciences`, `qualitative-social-analysis`.

### `full-research-cycle` — SPLIT

The full-cycle route uses the complete pack, but literature-only and publication-only routes install hypothesis generation and study design without needing them.

Target boundary: Create research-design and literature-publication packs; retain the current ID only as a compatibility aggregate for full-cycle selection.

Evidence: `full-cycle-quantitative-paper`, `literature-review-only`, `publication-preparation-only`.

### `data-and-pdf` — SPLIT

PDF-only work installs database retrieval and exploratory analysis, while dataset-only work installs document conversion; the procedures have separate user triggers.

Target boundary: Create document-evidence and structured-data-analysis packs with the current ID retained only as a compatibility aggregate.

Evidence: `pdf-evidence-extraction`, `structured-data-analysis`, `systematic-review-social-sciences`.

### `quantitative-sciences` — KEEP

Statistics, power, units, uncertainty, and scientific visualization share assumptions and review checks; the main over-installation comes from broad domain selection, not the skill boundary.

Target boundary: Keep one quantitative pack but tighten selection when a domain alone is the only quantitative signal.

Evidence: `mathematical-model-review`, `full-cycle-quantitative-paper`, `publication-monitoring-physics`.

## Prioritized additions

| Priority | Proposed pack | Missing capabilities | Scenario evidence |
|---|---|---|---|
| P1 | `publication-monitoring` | `publication-monitoring` | `publication-monitoring-life-sciences`, `publication-monitoring-physics` |
| P1 | `systematic-review` | `systematic-search`, `screening-and-deduplication` | `systematic-review-life-sciences`, `systematic-review-social-sciences` |
| P1 | `qualitative-research` | `qualitative-analysis` | `qualitative-social-analysis`, `qualitative-humanities-analysis` |
| P1 | `research-images` | `research-image-analysis` | `research-images-engineering`, `research-images-life-sciences` |
| P2 | `life-sciences` | `life-science-protocols` | `life-science-study-design`, `research-images-life-sciences` |

Each proposal is tied to a repeatable workflow or material boundary across the listed scenarios, not merely to a discipline label.
All additions remain `planned`; representative behavior runs and independent review are required before `production`.
