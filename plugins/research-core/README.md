# research-core

The cross-disciplinary foundation of the Evidence Lab research stack. It covers repeatable work that most researchers need before a subject-specific plugin becomes useful: finding and managing sources, planning studies, inspecting data, analyzing evidence, communicating uncertainty, creating truthful figures, and writing from verified material.

## Who it is for

Researchers, students working under institutional rules, supervisors, research analysts, and consultants who need an auditable workflow rather than a universal autonomous scientist.

## What it gives you

| Skill | Output |
|---|---|
| `citation-management` | Verified and deduplicated citation metadata and BibTeX. |
| `database-lookup` | Reproducible, endpoint-pinned public database retrieval. |
| `experimental-design` | Study design, randomization, blocking, and DOE artefacts. |
| `exploratory-data-analysis` | Bounded data profile and quality diagnostics. |
| `hypothesis-generation` | Candidate hypotheses, rivals, predictions, and measurement plan. |
| `literature-review` | Search protocol, screening trail, evidence table, and synthesis. |
| `markdown-mermaid-writing` | Versionable Markdown documents and text diagrams. |
| `markitdown` | Normalized Markdown extracted from supported document formats. |
| `paper-lookup` | Deduplicated scholarly records and available full-text links. |
| `peer-review` | Evidence-bounded review draft and claim/method audit. |
| `scientific-critical-thinking` | Audit of claims, assumptions, bias, and evidence gaps. |
| `scientific-visualization` | Truthful publication-oriented figures and export QA. |
| `statistical-analysis` | Analysis plan, diagnostics, effect sizes, and bounded reporting. |
| `statistical-power` | Sample-size, power, sensitivity, and MDE calculations. |
| `uncertainty-and-units` | Unit checks, conversions, and uncertainty propagation. |
| `writing-skill` | Evidence-bounded Russian or English writing routed by genre. |

## What it does not do

It does not make scientific decisions for the researcher, write qualification work in place of its author, fabricate evidence, provide patient-specific or regulatory decisions, operate laboratory hardware, or install every domain package. `markitdown` provides lightweight general document normalization, but the plugin deliberately makes no choice yet between `liteparse`, Firecrawl, or another dedicated PDF extraction backend.

## Install

```
/plugin marketplace add timsmykov/evidence-lab-plugins
/plugin install research-core@evidence-lab-plugins
```

## Provenance

The initial procedures are adapted from K-Dense Scientific Agent Skills at a pinned commit and from the existing Evidence Lab bilingual writing workflow. Every imported skill remains a draft until it passes a real two-material run and independent review. See `meta.json` and `THIRD_PARTY_NOTICES.md`.
