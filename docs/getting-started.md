# Getting started

This guide installs the complete Evidence Lab research library without onboarding. The result is one enabled plugin containing 24 skills.

## Before you start

You need either Codex with plugin support or Claude Code with plugin support, plus Git access to GitHub. Installation does not require an Evidence Lab account, a researcher profile, or a companion-plugin plan.

## Install in Codex

Add the Evidence Lab marketplace:

```bash
codex plugin marketplace add timsmykov/evidence-lab-plugins
```

Install the complete research library:

```bash
codex plugin add evidence-lab-research@evidence-lab-plugins
```

Confirm that the plugin is installed and enabled:

```bash
codex plugin list --json
```

Look for `evidence-lab-research@evidence-lab-plugins` with `installed: true` and `enabled: true`.

## Install in Claude Code

Add the Evidence Lab marketplace:

```bash
claude plugin marketplace add timsmykov/evidence-lab-plugins
```

Install the complete research library:

```bash
claude plugin install evidence-lab-research@evidence-lab-plugins
```

Confirm that the plugin is enabled and inspect its components:

```bash
claude plugin list --json
claude plugin details evidence-lab-research@evidence-lab-plugins
```

The component inventory should show 24 skills.

## Install from a local checkout

Use this path when reviewing an unreleased branch or developing the plugin locally. Replace `/path/to/evidence-lab-plugins` with the repository checkout.

### Codex

```bash
codex plugin marketplace add /path/to/evidence-lab-plugins
codex plugin add evidence-lab-research@evidence-lab-plugins
```

### Claude Code

```bash
claude plugin marketplace add /path/to/evidence-lab-plugins
claude plugin install evidence-lab-research@evidence-lab-plugins
```

For a supported research setup, prefer an immutable published Evidence Lab release rather than a floating development branch. The [release process](release-process.md) explains the release lock and version guarantees.

## Start your first task

Open a new Codex or Claude Code task after installation. Describe the research result rather than naming an internal pack:

```text
Find the most relevant papers on this question. Keep verified identifiers and source links, and tell me what could not be retrieved.
```

```text
I have interview transcripts. Help me define a codebook, preserve the coded excerpts, and record disagreements and negative cases.
```

```text
Review this dataset before analysis. Check missingness, possible leakage, outliers, and sensitivity to transformations.
```

If you already know the procedure you want, you can name it directly, for example: `Use statistical-power to justify the sample size for this design.`

Browse the [complete skill catalogue](skills.md) for task-to-skill guidance and expected outputs.

## What the direct install does not do

The `evidence-lab-research` plugin does not:

- ask onboarding or profile questions;
- select or install companion plugins;
- change existing plugins or standalone skills;
- create personal project instructions;
- claim that every included scientific method has completed acceptance.

The optional personalized flow is a separate module. Use [START.md](../START.md) only if you want Evidence Lab to recommend a smaller set of focused packs.

## Troubleshooting

### The plugin selector is not available

Update the marketplace and inspect its entries:

```bash
codex plugin marketplace upgrade evidence-lab-plugins
codex plugin list --json
```

For Claude Code:

```bash
claude plugin marketplace update evidence-lab-plugins
claude plugin list --available --json
```

If a published release predates the all-in-one plugin, install from a local checkout for review or wait for the next immutable release.

### The plugin is installed but the skills do not appear

Open a new task. Hosts load plugin components at task startup. Then re-run the plugin list or details command and confirm that the plugin is enabled.

### A skill reports a missing tool

Some procedures have optional or task-specific runtime requirements. For example, LaTeX validation can inspect sources without a compiler, but it must not claim a successful compilation until a supported TeX engine is present. Read the linked `SKILL.md` in the [catalogue](skills.md) for the exact boundary.

### I want fewer skills

Use the optional [personalized setup](../START.md). It builds a profile-selected plan and asks for confirmation before installing focused packs.

## Next steps

- [Choose a skill](skills.md)
- [Understand readiness labels](skills.md#readiness-at-a-glance)
- [Read the documentation map](README.md)
- [Review security and privacy boundaries](../SECURITY.md)
