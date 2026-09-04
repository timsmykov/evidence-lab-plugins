# Evidence Lab Research Skills

Evidence Lab is an open-source library of research procedures for Codex and Claude Code. Install one plugin, describe the research task in normal language, and let the host choose the relevant skill.

The library covers literature discovery, study design, data analysis, scientific writing, peer review, visualization, and reproducible research operations. It helps a researcher run a method and check the result; it does not replace subject expertise or make unsupported scientific decisions.

## Start here

| Your goal | Go to |
|---|---|
| Install the complete library | [Two-minute installation](docs/getting-started.md) |
| See every skill and what it produces | [Skill catalogue](docs/skills.md) |
| Choose a skill for a specific task | [Choose by outcome](docs/skills.md#choose-by-outcome) |
| Understand what is tested and what is still experimental | [Readiness inventory](docs/skill-pack-readiness.md) |
| Use the optional personalized setup | [Onboarding entrypoint](START.md) or [Russian entrypoint](START.ru.md) |
| Develop or review a skill | [Documentation home](docs/README.md) |

## Install all research skills

The direct installation path does not run onboarding, ask profile questions, or install companion plugins.

### Codex

```bash
codex plugin marketplace add timsmykov/evidence-lab-plugins
codex plugin add evidence-lab-research@evidence-lab-plugins
```

### Claude Code

```bash
claude plugin marketplace add timsmykov/evidence-lab-plugins
claude plugin install evidence-lab-research@evidence-lab-plugins
```

Open a new task after installation so the host loads the skills. For verification commands, local-checkout installation, and troubleshooting, use the [complete getting-started guide](docs/getting-started.md).

## What can I ask it to do?

You do not have to remember skill names. Start with the result you want:

```text
Find recent papers on this question and return verified identifiers and source links.
```

```text
Turn these observations into rival hypotheses and a study design I can review.
```

```text
Profile this dataset, show missingness and leakage risks, then propose an analysis plan.
```

```text
Check this manuscript against the journal's current LaTeX and submission requirements.
```

The [skill catalogue](docs/skills.md) lists all 24 installable skills, when to use each one, what it produces, its canonical source, and its current review status.

## How the package is organized

```text
install evidence-lab-research
        │
        ├── 24 research and skill-authoring procedures
        ├── scripts, references, templates, and evals used by those procedures
        └── no onboarding, profile collection, or automatic configuration
```

The all-in-one plugin contains generated, byte-checked copies for reliable installation. Focused packs remain the canonical sources used for review and maintenance. Optional onboarding lives separately in `evidence-lab-core` and is not a dependency of the research plugin.

Read [Architecture](docs/architecture.md) if you need the pack model, generated-file flow, trust boundaries, or release invariants.

## Current readiness

The package is mechanically installable in Codex and Claude Code, but the scientific procedures are still being accepted on real research tasks.

- 24 skills are available through the all-in-one plugin.
- 19 need a representative real-task run.
- 5 need substantive method work before acceptance.
- No skill is currently labelled `production`.

This distinction is intentional: successful installation is not evidence that a scientific procedure is mature. See the [readiness inventory](docs/skill-pack-readiness.md) for the exact status of every skill and pack.

## Optional personalized setup

Researchers who want a smaller profile-selected installation can use [START.md](START.md). The optional flow asks four questions, shows the complete installation plan, and requires confirmation before making changes.

The direct all-in-one installation above is the default for anyone who wants the whole library without that setup layer.

## Documentation

The [documentation home](docs/README.md) separates researcher guides, skill reference, contributor workflows, architecture, release policy, and historical audit evidence. You should not need to browse the repository tree to find the right page.

## Scope and license

This repository contains the distributable Evidence Lab skill and plugin product. The separate methodology repository, client deliverables, private data, personal overlays, consulting materials, and hosted services are outside this repository.

Evidence Lab-owned content is MIT-licensed. Bundled third-party components retain their MIT or Apache-2.0 notices. See [Licensing](LICENSING.md), [third-party notices](THIRD_PARTY_NOTICES.md), [security](SECURITY.md), and [trademarks](TRADEMARKS.md).
