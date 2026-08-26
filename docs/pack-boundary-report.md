# Pack-boundary evidence report

Generated deterministically by `python3 scripts/analyze_pack_boundaries.py`.
It measures the current catalog with R3 boundary status `implemented`.
Core capabilities are treated as the mandatory baseline and are not counted as over-installation.

## Summary

- Scenarios: **17**
- Missing required capability occurrences: **0**
- Over-installed optional-pack capability occurrences: **13**

## Scenario matrix

| Scenario | Selected packs | Missing required capabilities | Over-installed capabilities |
|---|---|---|---|
| `general-paper-lookup` | `evidence-lab-core` | — | — |
| `pdf-evidence-extraction` | `evidence-lab-core`, `document-evidence` | — | — |
| `structured-data-analysis` | `evidence-lab-core`, `structured-data-analysis` | — | — |
| `mathematical-model-review` | `evidence-lab-core`, `literature-publication`, `quantitative-sciences` | — | `academic-writing`, `literature-review`, `research-diagrams`, `scientific-visualization` |
| `full-cycle-quantitative-paper` | `evidence-lab-core`, `document-evidence`, `literature-publication`, `research-design`, `structured-data-analysis`, `quantitative-sciences`, `data-and-pdf`, `full-research-cycle` | — | — |
| `literature-review-only` | `evidence-lab-core`, `literature-publication` | — | `research-diagrams` |
| `full-cycle-pdf-only` | `evidence-lab-core`, `document-evidence`, `literature-publication`, `research-design`, `full-research-cycle` | — | — |
| `publication-preparation-only` | `evidence-lab-core`, `literature-publication` | — | — |
| `publication-monitoring-life-sciences` | `evidence-lab-core`, `publication-monitoring` | — | — |
| `publication-monitoring-physics` | `evidence-lab-core`, `publication-monitoring` | — | — |
| `systematic-review-life-sciences` | `evidence-lab-core`, `document-evidence`, `literature-publication`, `structured-data-analysis`, `quantitative-sciences`, `systematic-review` | — | `database-lookup`, `research-diagrams`, `scientific-visualization`, `statistical-power`, `uncertainty-and-units` |
| `systematic-review-social-sciences` | `evidence-lab-core`, `document-evidence`, `literature-publication`, `structured-data-analysis`, `systematic-review` | — | `database-lookup`, `exploratory-data-analysis`, `research-diagrams` |
| `qualitative-social-analysis` | `evidence-lab-core`, `qualitative-research` | — | — |
| `qualitative-humanities-analysis` | `evidence-lab-core`, `qualitative-research` | — | — |
| `research-images-engineering` | `evidence-lab-core`, `research-images` | — | — |
| `research-images-life-sciences` | `evidence-lab-core`, `research-images`, `life-sciences` | — | — |
| `life-science-study-design` | `evidence-lab-core`, `research-design`, `life-sciences` | — | — |

## Current pack coverage

- `evidence-lab-core`: selected by 17 scenario(s); mandatory baseline; exclusion is intentionally not applicable.
- `life-sciences`: selected by 2 scenario(s); negative scenarios include `general-paper-lookup`.
- `quantitative-sciences`: selected by 3 scenario(s); negative scenarios include `general-paper-lookup`.
- `data-and-pdf`: selected by 1 scenario(s); negative scenarios include `general-paper-lookup`.
- `document-evidence`: selected by 5 scenario(s); negative scenarios include `general-paper-lookup`.
- `full-research-cycle`: selected by 2 scenario(s); negative scenarios include `general-paper-lookup`.
- `literature-publication`: selected by 7 scenario(s); negative scenarios include `general-paper-lookup`.
- `publication-monitoring`: selected by 2 scenario(s); negative scenarios include `general-paper-lookup`.
- `qualitative-research`: selected by 2 scenario(s); negative scenarios include `general-paper-lookup`.
- `research-design`: selected by 3 scenario(s); negative scenarios include `general-paper-lookup`.
- `research-images`: selected by 2 scenario(s); negative scenarios include `general-paper-lookup`.
- `structured-data-analysis`: selected by 4 scenario(s); negative scenarios include `general-paper-lookup`.
- `systematic-review`: selected by 2 scenario(s); negative scenarios include `general-paper-lookup`.

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

### `research-design` — KEEP

Hypothesis generation and study design share one planning confirmation boundary and no longer force literature or publication tooling into focused design work.

Target boundary: Keep hypothesis generation and experimental design together as the focused research-planning workflow.

Evidence: `full-cycle-quantitative-paper`, `life-science-study-design`.

### `literature-publication` — KEEP

Literature synthesis, evidence-bounded writing, manuscript review, and editable diagrams share publication evidence and revision boundaries while excluding study design.

Target boundary: Keep the literature-to-publication procedures together and review further splits only from new over-installation evidence.

Evidence: `literature-review-only`, `publication-preparation-only`, `mathematical-model-review`.

### `document-evidence` — KEEP

Document conversion is independently triggered by PDF material and no longer brings database retrieval or exploratory dataset analysis into document-only work.

Target boundary: Keep deterministic document conversion as a focused material workflow with no structured-data dependency.

Evidence: `pdf-evidence-extraction`, `systematic-review-social-sciences`.

### `structured-data-analysis` — KEEP

Documented database retrieval and exploratory table analysis share structured-record provenance and data-quality checks without requiring document conversion.

Target boundary: Keep database retrieval and exploratory structured-data inspection together pending finer scenario evidence.

Evidence: `structured-data-analysis`, `full-cycle-quantitative-paper`.

## Prioritized additions

| Priority | Pack | Target capabilities | Lifecycle | Scenario evidence |
|---|---|---|---|---|
| P1 | `publication-monitoring` | `publication-monitoring` | `draft` | `publication-monitoring-life-sciences`, `publication-monitoring-physics` |
| P1 | `systematic-review` | `systematic-search`, `screening-and-deduplication` | `draft` | `systematic-review-life-sciences`, `systematic-review-social-sciences` |
| P1 | `qualitative-research` | `qualitative-analysis` | `draft` | `qualitative-social-analysis`, `qualitative-humanities-analysis` |
| P1 | `research-images` | `research-image-analysis` | `draft` | `research-images-engineering`, `research-images-life-sciences` |
| P2 | `life-sciences` | `life-science-protocols` | `draft` | `life-science-study-design`, `research-images-life-sciences` |

Each pack is tied to a repeatable workflow or material boundary across the listed scenarios, not merely to a discipline label.
Draft additions have passed repository behavior checks but still require representative research runs and independent review before `production`.
