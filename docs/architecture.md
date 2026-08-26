# Agent-first architecture

## Normative direction

Evidence Lab is defined by its researcher experience and five product layers, not by Claude Code or Codex packaging. Host formats are adapters generated from one semantic source.

## Units

**Skill** is one repeatable procedure with its local scripts, references, assets, and routing evals.

**Pack** is the unit of selection, installation, versioning, provenance, and review. A pack belongs to `core`, `workflow`, `domain`, or `local`.

**Researcher profile** records normalized domains, workflows, materials, stages, and methods. It is user-owned state, not repository content.

**Selection plan** records exact pack IDs, versions, layers, and reasons before installation.

**Host adapter** exposes the same pack to Claude Code or Codex without changing its scientific meaning.

## Data flow

```text
chat onboarding
  -> normalized profile
  -> deterministic selector
  -> reviewed selection plan
  -> native host confirmation
  -> installation readback
```

Free text may help normalize a profile. It never becomes an executable package name or installation command.

## Repository flow

```text
pack.json + shared skills + meta.json
  -> build_adapters.py
  -> Claude manifest and marketplace
  -> Codex manifest and marketplace
  -> Core runtime catalog
```

Generated artifacts are committed so repository marketplaces work directly, but CI rejects drift from `pack.json`.

## Current decomposition

- Evidence Lab Core: onboarding, selection, paper lookup, citations, critical thinking.
- Full Research Cycle: hypotheses, design, literature review, writing, diagrams, peer review.
- Data and PDF: document conversion, public databases, exploratory analysis.
- Quantitative Sciences: statistics, power, uncertainty, units, scientific visualization.

This is the first real decomposition, not the final catalog. New packs must be justified by tested user routes rather than by a desire to fill the taxonomy.

## Invariants

- Shared skills are authored once.
- Every adapter exposes the same ID, version, description, author, license, and skill tree.
- Dependencies are resolved before a plan is shown.
- Partial installation must not be recorded as ready.
- A runtime is not supported until its adapter and representative behavior pass.
- Provenance, licensing, deterministic scripts, and negative routing evals survive every split.

## Deferred

Client-side installation transactions, rollback, and persisted installation readback are the next lifecycle layer. Hermes, ChatGPT-specific packaging, a graphical onboarding UI, silent installation, and runtime generation of new skills are outside the current Claude Code and Codex scope.
