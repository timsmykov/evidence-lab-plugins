# Open-source skills for the Evidence Lab foundation

Deep-research audit · 2026-08-27

## Executive conclusion

The current roadmap says **20 implemented + 7 planned = 27 foundation skills**. The audit does not support creating or importing seven separate new skills.

- **Preregistration is already implemented** inside `hypothesis-generation`: the skill timestamps planned decisions, distinguishes confirmatory and exploratory work, records deviations, ships a preregistration template, and includes a deterministic generator. The catalogue should record this as an existing capability, not a planned standalone skill.
- **One external skill is ready to take:** K-Dense `venue-templates`, under MIT and at the repository SHA already used by Evidence Lab.
- **Two sources are worth adapting:** Orchestra's passive research-manager schema for the research log, and compound-science's reproducible-pipeline method for a minimal run manifest. Neither should be copied unchanged.
- **Evidence extraction and data-cleaning provenance should extend current skills.** Evidence Lab already has document normalization, structured literature extraction, EDA diagnostics, transformation rationale, commands, seeds, and provenance. What is missing is a claim-linked evidence-card contract and a cross-workflow transformation ledger.
- **No clean `TAKE` candidate was found for universal RDM/DMP/FAIR.** The best substantive candidate has conflicting license declarations; other options are untested, dependency-heavy, or external-service integrations.

The likely result is **25–26 physical skills covering all 27 capabilities**, depending on whether evidence extraction and data lineage remain modes of current skills or become separate narrowly scoped skills.

## What was evaluated

The search targeted seven catalogue gaps:

1. evidence extraction from PDFs and other documents;
2. preregistration / pre-analysis plans;
3. data cleaning and provenance;
4. LaTeX and venue formatting;
5. reproducible computation;
6. research data management, DMP, and FAIR;
7. research log and decision trail.

Candidates were discovered broadly, then judged at the **exact skill directory and immutable commit**, not at repository level. Original upstreams were preferred; large aggregators were treated as indexes. The review covered license, maintenance, exact assets/scripts/references, tests, Codex/Claude portability, network and credential requirements, destructive behavior, and overlap with Evidence Lab.

`TAKE` means ready to vendor after normal review; `ADAPT` means useful upstream material requiring Evidence Lab boundaries and tests; `HOLD` means a blocking license or quality uncertainty; `REJECT` means it must not be incorporated.

## Capability decisions

| Capability | Current Evidence Lab coverage | Best external evidence | Verdict | Required action |
|---|---|---|---|---|
| Evidence extraction | MarkItDown preserves source/hash/page-or-section provenance; literature review performs structured extraction | Anthropic PDF is mature but proprietary; smaller evidence-card skills are unlicensed or untested | **No TAKE** | Add an original claim-linked evidence-card schema and tests around current skills |
| Preregistration | `hypothesis-generation` already ships a scaffold, generator, timestamps, exclusions, transformations, analysis decisions, and deviation handling | AER preregistration is strong but economics-specific | **Already covered** | Remove the duplicate planned slot; keep AER as a possible economics extension |
| Data cleaning + provenance | EDA already audits missingness and transformations and records commands, seeds, and provenance | Available candidates are prose-only or dependency-heavy | **No TAKE** | Add a narrow transformation ledger, not a second generic EDA skill |
| LaTeX + venue formatting | No dedicated skill | K-Dense `venue-templates`: MIT, templates, three bounded helpers, focused tests | **TAKE** | Vendor at pinned SHA, preserve license, add Evidence Lab evals |
| Reproducible computation | Distributed partial coverage, no universal rerun artifact | compound-science `reproducible-pipelines`: MIT, detailed references and repository tests | **ADAPT** | Extract a safe minimal run manifest; remove destructive cleanup patterns |
| RDM / DMP / FAIR | No complete universal skill | `dmp-builder` is substantive but declares MIT at root and CC-BY-4.0 in its skill | **HOLD** | Resolve licensing or author an original planning-only core from public standards |
| Research log | Several skills record provenance, but no durable universal event/decision schema | Orchestra `research-manager`: MIT, strong taxonomy and human/AI attribution | **ADAPT** | Keep only passive logging; add deterministic schema validation and tests |

## Shortlist audit

GitHub counts were read on 2026-08-27 and will drift; the SHAs below are the reproducible identity of the audited material.

### 1. K-Dense venue templates — TAKE

Repository snapshot: 35,004 stars, 3,377 forks, 45 contributors, 101 releases. Audited SHA: `36d8f13a1e754618794bf42f417884940077b4ae`.

The exact [`venue-templates` skill](https://github.com/K-Dense-AI/scientific-agent-skills/tree/36d8f13a1e754618794bf42f417884940077b4ae/skills/venue-templates) contains journal, conference, grant, and poster templates; references for multiple venue families; three local helpers for template query/customization/validation; and a focused test module. The repository is MIT-licensed. Static inspection found a bounded local Poppler subprocess, not shell execution or automatic network installation in this skill.

This is the only candidate that simultaneously clears the license, exact-skill substance, deterministic tooling, testing, maintenance, and scope-fit gates.

### 2. Orchestra research manager — ADAPT

Repository snapshot: 12,092 stars, 880 forks, 16 contributors, 10 releases. Audited SHA: `773a52944ba4747a18bd4ae9ade53fff041adcbc`.

The MIT-licensed [`research-manager`](https://github.com/Orchestra-Research/AI-Research-SKILLs/tree/773a52944ba4747a18bd4ae9ade53fff041adcbc/22-agent-native-research-artifact/research-manager) defines useful event and provenance taxonomies for decisions, experiments, claims, dead ends, pivots, and human/AI attribution. It has references but no exact-skill tests.

The parent repository also contains an autonomous research loop that directs the agent not to ask permission. That behavior conflicts with Evidence Lab's human-accountability model. Adapt only the passive post-task record schema; do not import the autonomous manager wholesale.

### 3. compound-science reproducible pipelines — ADAPT

Repository snapshot: 11 stars, 2 forks, one contributor, no releases. Audited SHA: `1ddb81fffbd95656322eed3577bee2080135d1af`.

The MIT-licensed [`reproducible-pipelines`](https://github.com/James-Traina/compound-science/tree/1ddb81fffbd95656322eed3577bee2080135d1af/skills/reproducible-pipelines) has unusually good exact content despite low adoption: Make/Snakemake/DVC patterns, pinned environments, seed handling, and replication-package references. The repository has 14 test files, though not all validate this exact skill.

It is framed for economics and quantitative social science, and its example Make target recursively deletes generated data/output directories. Evidence Lab should adapt the conceptual artifact contract—inputs, hashes, environment, command, seeds, outputs, and rerun verification—while replacing cleanup with bounded, recoverable behavior.

### 4. appautomaton arXiv writer — optional ADAPT

Repository snapshot: 416 stars, 37 forks, one contributor. Audited SHA: `349ce88a0797422911a4ce58ed335842e9b87e15`.

The MIT [`arxiv-paper-writer`](https://github.com/appautomaton/latex-arxiv-SKILL/tree/349ce88a0797422911a4ce58ed335842e9b87e15/.codex/skills/arxiv-paper-writer) includes templates, six workflow scripts, references, tests, and CI. It is an opinionated IEEE/arXiv/AI review-paper pipeline, not a universal LaTeX foundation. It may become an optional publication workflow after `venue-templates`, but should not replace it.

### 5. AER preregistration — domain ADAPT only

Repository snapshot: 44 stars, 9 forks, three contributors, two releases. Audited SHA: `85eae99fe5935c79c209f597a56c88899082a090`.

The MIT [`aer-preregistration`](https://github.com/brycewang-stanford/AER-Skills/tree/85eae99fe5935c79c209f597a56c88899082a090/skills/aer-preregistration) is substantive and ships a PAP template, but it is specific to AEA/economics/RCT conventions. Because the universal capability is already present in Evidence Lab, this belongs only in a future economics domain pack.

### 6. dmp-builder — HOLD

Repository snapshot: 2 stars, no forks, one contributor. Audited SHA: `d9061c1050f5fb31e9eaba4be0eb083b12c911f7`.

[`dmp-builder`](https://github.com/orazionelson/dmp-builder/tree/d9061c1050f5fb31e9eaba4be0eb083b12c911f7) has the best DMP/FAIR assets found, a Zenodo script, and four tests. However, the root file says MIT while `SKILL.md` declares CC-BY-4.0. That ambiguity blocks incorporation. Its focus is European funders/GDPR, and the deposit path uses a write-scoped Zenodo token. If licensing is clarified, adapt the planning core and keep deposit as explicit opt-in.

### 7. Popular but unusable candidates

- The official-looking [Anthropic PDF skill license](https://github.com/anthropics/skills/blob/3b3fad96af16a10759d930941b4520ba0c40edae/skills/pdf/LICENSE.txt) explicitly forbids retaining copies, reproduction, derivative works, and distribution. The 171,972-star repository is therefore **REJECT** for Evidence Lab vendoring.
- [`ndpvt-web/latex-document-skill`](https://github.com/ndpvt-web/latex-document-skill/tree/a1ebe264c7e51d20d89ea5b99ebee33ef1fca5de) has 725 stars, 27 scripts, tests, and CI, but no license was found. It is **HOLD** even though its implementation is impressive.
- [`wentorai/research-plugins`](https://github.com/wentorai/research-plugins/tree/bf44b3cd617fa94c8a1b254c5d1987142ca3d631) has 473 skills but only two repository test files. Its PDF, cleaning, LaTeX, and reproducibility entries are mostly long prose recipes with installation or Docker/cleanup commands. Use it for discovery, not direct promotion.
- [`awesome-rosetta-skills`](https://github.com/xjtulyc/awesome-rosetta-skills/tree/6cffda43d7cd6c07c563e2f2e24a88a615bcf003/skills/00-universal) has 169 skills, five scripts, no tests, and one contributor. Its universal RDM/reproducibility guides assume DVC, Docker, conda, and cloud plugins. **HOLD**.
- [`research-aware-engineering-skills/evidence-extractor`](https://github.com/GnohzZ/research-aware-engineering-skills/tree/17f37bfcfa577a8bb37c94b6837e4c151710d4da/skills/evidence-extractor) has an excellent evidence-card concept, but no license and no tests. **HOLD**; its text cannot be copied.

## Licensing and security rules for bootstrap

1. A root MIT license does not override a more specific license inside a skill. Missing license does not mean public domain; it means no permission to copy, modify, or distribute.
2. Repository stars cannot approve a skill. Promotion is per exact directory and pinned commit.
3. Imported scripts require local review for shell invocation, destructive cleanup, automatic installation, network calls, secrets, path traversal, unbounded input, and fail-open behavior.
4. Apps, MCP servers, cloud deposits, subscription products, and API-backed tools remain companion integrations. Bootstrap can recommend them after onboarding, but must not silently connect or install them as if they were ordinary local skills.
5. A portable `SKILL.md` does not make host-specific commands portable. Every promoted capability needs behavior tests in both Codex and Claude Code.

The baseline format should continue to follow the [Agent Skills specification](https://agentskills.io/specification), while Evidence Lab supplies stricter provenance, safety, and evaluation contracts.

## Recommended implementation order

1. Correct `catalog/foundation-skills.json`: map preregistration to the current `hypothesis-generation` skill.
2. Vendor K-Dense `venue-templates` at the audited SHA, preserve the MIT notice, run upstream tests, and add Evidence Lab trigger/behavior evals.
3. Define representative eval contracts before implementation for evidence cards, transformation ledger, reproducible run manifest, RDM/DMP, and research log.
4. Adapt Orchestra's passive event schema and compound-science's run-manifest method with explicit attribution and safe behavior.
5. Build the evidence-card and transformation-ledger pieces as original Evidence Lab glue around MarkItDown, literature review, and EDA.
6. Hold RDM vendoring until licensing is clear; if no source clears the gate, implement a small original planning-only skill from authoritative FAIR/DMP standards instead of copying a repository.
7. Promote only after Codex + Claude Code trigger, representative behavior, hostile-input, offline/default-dependency, and license-notice tests pass.

## Verification boundary

No external candidate code was executed and no skill was imported in this research task. Repositories were inspected statically at their audited HEADs; local Evidence Lab files were read directly. GitHub popularity and maintenance counts are a dated snapshot, while commit SHAs and linked source paths make the substantive findings reproducible.

The licensed examples selected for continued study are recorded in
[`catalog/open-source-skill-candidates.json`](../../catalog/open-source-skill-candidates.json).
Registry membership is not promotion: every entry remains source-only and
non-installable until its individual import requirements pass.
