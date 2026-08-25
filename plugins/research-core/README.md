# research-core

The cross-disciplinary foundation of the Evidence Lab research stack. It covers repeatable work that most researchers need before a subject-specific plugin becomes useful: finding and managing sources, planning studies, inspecting data, analyzing evidence, communicating uncertainty, creating truthful figures, and writing from verified material.

## Who it is for

Researchers, students working under institutional rules, supervisors, research analysts, and consultants who need an auditable workflow rather than a universal autonomous scientist.

## Choose by job

Start with the intended artefact, then load the smallest sufficient skill set. The [`/research-core`](commands/research-core.md) command can route a cross-stage request without loading the whole plugin.

### 1. Find and organize evidence

| Skill | Load when | Do not load when |
|---|---|---|
| [`paper-lookup`](skills/paper-lookup/SKILL.md) | You need papers, identifiers, citation graphs, or available full text. | You already have the corpus and need synthesis. |
| [`citation-management`](skills/citation-management/SKILL.md) | You need verified metadata, deduplication, BibTeX, or reference cleanup. | You need to decide which studies belong in a review. |
| [`literature-review`](skills/literature-review/SKILL.md) | You need a protocol, screening trail, evidence table, and synthesis. | You need only a bounded paper lookup. |
| [`database-lookup`](skills/database-lookup/SKILL.md) | You need reproducible retrieval from a named public database API. | The target source is scholarly literature rather than a data registry. |

### 2. Frame and design the study

| Skill | Load when | Do not load when |
|---|---|---|
| [`hypothesis-generation`](skills/hypothesis-generation/SKILL.md) | You need testable hypotheses, rivals, predictions, and operationalization. | You need to treat a hypothesis as an established result. |
| [`experimental-design`](skills/experimental-design/SKILL.md) | You need randomization, blocking, controls, or a DOE layout before collection. | The data already exist and need analysis. |
| [`statistical-power`](skills/statistical-power/SKILL.md) | You need sample size, power, sensitivity, or minimum detectable effect. | You need to choose the substantive research question. |

### 3. Inspect and analyze data

| Skill | Load when | Do not load when |
|---|---|---|
| [`exploratory-data-analysis`](skills/exploratory-data-analysis/SKILL.md) | You need a bounded data profile, missingness, leakage, or sensitivity diagnostics. | You need confirmatory claims before an analysis plan is approved. |
| [`statistical-analysis`](skills/statistical-analysis/SKILL.md) | You need a confirmed analysis plan, diagnostics, effect sizes, and reporting. | You need only a power calculation. |
| [`uncertainty-and-units`](skills/uncertainty-and-units/SKILL.md) | You need unit validation, conversions, uncertainty propagation, or result formatting. | You need a statistical model for observed data. |

### 4. Challenge and review claims

| Skill | Load when | Do not load when |
|---|---|---|
| [`scientific-critical-thinking`](skills/scientific-critical-thinking/SKILL.md) | You need a claim, bias, confounding, or evidence-quality audit. | You need a formal manuscript referee report. |
| [`peer-review`](skills/peer-review/SKILL.md) | You need an authorized structured review of a manuscript, protocol, or proposal. | You only need to understand one scientific claim. |

### 5. Prepare research outputs

| Skill | Load when | Do not load when |
|---|---|---|
| [`scientific-visualization`](skills/scientific-visualization/SKILL.md) | You need a data-derived figure, accessibility audit, or publication export. | You need a structural workflow diagram. |
| [`markdown-mermaid-writing`](skills/markdown-mermaid-writing/SKILL.md) | You need a versionable structural diagram or Markdown layout. | You need data-driven charts or general prose drafting. |
| [`writing-skill`](skills/writing-skill/SKILL.md) | You need to draft or revise evidence-bounded Russian or English prose, including academic writing. | You need literature discovery, citation validation, or methodological review. |
| [`markitdown`](skills/markitdown/SKILL.md) | You need lightweight normalization of a supported document into Markdown. | You need high-fidelity PDF extraction or a parser-backend decision. |

## What it does not do

It does not make scientific decisions for the researcher, write qualification work in place of its author, fabricate evidence, provide patient-specific or regulatory decisions, operate laboratory hardware, or install every domain package. `markitdown` provides lightweight general document normalization, but the plugin deliberately makes no choice yet between `liteparse`, Firecrawl, or another dedicated PDF extraction backend.

## Install

```
/plugin marketplace add timsmykov/evidence-lab-plugins
/plugin install research-core@evidence-lab-plugins
```

## Provenance

The initial procedures are adapted from K-Dense Scientific Agent Skills at a pinned commit and from the existing Evidence Lab bilingual writing workflow. Every imported skill remains a draft until it passes a real two-material run and independent review. See `meta.json` and `THIRD_PARTY_NOTICES.md`.

## Readiness

- **Current status:** `draft`.
- **Static gates:** repository schema, privacy, links, routing-eval structure, and Python syntax.
- **Before production:** run every skill on at least two representative materials, record the evidence, test declared portable runtimes, and obtain review from someone other than the owner.
- **Open architecture decision:** compare dedicated PDF extraction backends, including Firecrawl and `liteparse`; do not treat `markitdown` as that decision.
