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
  -> frozen 20-skill foundation + profile-specific additions
  -> reviewed selection plan
  -> Codex companion-plugin plan (Codex only)
  -> native host confirmation
  -> installation readback
```

Free text may help normalize a profile. It never becomes an executable package name or installation command.

The optional Codex companion-plugin plan is built from
`catalog/external-plugin-candidates.json`. It is a separate trust boundary:
portable Evidence Lab packs are selected first, then reviewed Codex-only
components are matched against the same normalized profile. Skills-only
plugins may become installable only after an Evidence Lab promotion gate.
Directory apps and hybrids always remain a visible connection step and require
post-connection readback. Claude Code receives no Codex directory actions.
Components marked `explicit-opt-in` stay out of the visible plan unless the
researcher names them or a future reviewed detector supplies the equivalent
explicit signal; a broad domain or `papers` answer is not enough.

Open-source skill examples discovered during capability research live in
`catalog/open-source-skill-candidates.json`. That registry contains immutable
upstream paths, license evidence, capability mappings, and promotion work. Its
entries are source-only (`bundled: false`): they do not enter generated
adapters, bootstrap selection, or release snapshots until a separate reviewed
import preserves attribution and passes representative Codex and Claude tests.

Selection Policy owns the allowed profile vocabulary, matching semantics, and
ordering contract. Reviewed rules in each `pack.json` select packs. The LLM may
suggest normalized values for free text, but it cannot select a pack directly.
`any` matches one value across declared fields, `all` requires a match in every
declared field, `contains_all` requires every listed value within a field, and
`none` excludes a match.

`catalog/foundation-core.json` is the canonical generated inventory of the
universal researcher foundation. It maps 21 implemented capabilities to 20
unique physical skill directories, records their owning packs, quality state,
and content hashes, and lists six planned gaps separately. Packs marked
`foundation: true` are installed for every validated profile. Profile rules
still explain which parts are immediately relevant and may add optional packs;
they cannot remove the foundation. A planned capability enters bootstrap only
after it has a reviewed physical skill and is regenerated into this index.

For an existing workspace, selection feeds a reconciliation plan instead of a clean-install plan. The plan hashes live installed readback, separates add/update/retain/remove-candidate groups, and keeps extras by default. Additions and updates share one approval; removal requires a second approval. The state records the old release ref and exact pre-change pack snapshot so a failed or interrupted run can be inspected and restored without claiming success before exact readback.

## Repository flow

```text
pack.json + shared skills + meta.json
  -> build_foundation_index.py + build_adapters.py
  -> Claude manifest and marketplace
  -> Codex manifest and marketplace
  -> Core runtime catalog
```

Generated artifacts are committed so repository marketplaces work directly, but CI rejects drift from `pack.json`.

## Current decomposition

- Evidence Lab Core: onboarding, selection, installation lifecycle, paper lookup, citations, critical thinking.
- Research Design and Literature Publication: focused study-design and manuscript workflows.
- Document Evidence and Structured Data Analysis: focused document conversion and dataset/database workflows.
- Quantitative Sciences and Life Sciences: discipline-specific methods and checks.
- Full Research Cycle and Data and PDF: compatibility aggregates that depend on the focused packs.
- Publication Monitoring, Systematic Review, Qualitative Research, and Research Images: reviewed draft additions awaiting representative real-task evidence.

Further splits or additions must be justified by tested user routes rather than by a desire to mirror a taxonomy.

## Invariants

- Shared skills are authored once.
- Every adapter exposes the same ID, version, description, author, license, and skill tree.
- Dependencies are resolved before a plan is shown.
- A changed profile, release ref, or installed snapshot invalidates an unexecuted reconcile plan.
- Reconciliation never removes an extra pack without a separate confirmation.
- Partial installation must not be recorded as ready.
- Every frozen foundation skill is owned by exactly one foundation pack and is
  present in both the canonical and Core runtime indexes with the same hash.
- A runtime is not supported until its adapter and representative behavior pass.
- Provenance, licensing, deterministic scripts, and negative routing evals survive every split.

## Deferred

Marketplace verification and application-specific graphical presentation remain distribution work. Hermes, ChatGPT-specific packaging, a graphical onboarding UI, silent installation, and runtime generation of new skills are outside the current Claude Code and Codex scope. The GitHub-first MVP already includes an app-first chat entrypoint, localized deterministic recommendations, explicit installation plans, state, readback, idempotent retry, and bounded rollback.
