# Evidence Lab plugin architecture

This page explains how the user-facing plugin, canonical skill sources, optional onboarding, and host adapters relate. Start with [Getting started](getting-started.md) if you only want to install the library.

## Two independent user paths

### Direct library install

```text
GitHub marketplace
  -> evidence-lab-research
  -> 24 physical, byte-checked skill copies
  -> Codex or Claude Code loads them in a new task
```

This is the default path. It has no plugin dependencies and contains no onboarding, profile collection, companion-plugin selection, or automatic configuration.

### Optional personalized install

```text
chat onboarding
  -> normalized researcher profile
  -> deterministic selector
  -> reviewed focused-pack plan
  -> explicit confirmation
  -> installation and exact host readback
```

This path lives in `evidence-lab-core`. It is an optional installation module, not a dependency of `evidence-lab-research`.

## Core concepts

**Skill:** one repeatable procedure with its scripts, references, templates, and routing evals.

**Focused pack:** the canonical unit of skill ownership, versioning, provenance, review, and profile-based selection. A focused pack belongs to `core`, `workflow`, `domain`, or `local`.

**Distribution bundle:** an installation surface that mirrors canonical skills without becoming their source of truth. `evidence-lab-research` is the all-in-one distribution bundle.

**Researcher profile:** normalized domains, workflows, materials, stages, and methods used only by optional onboarding. It is user-owned state.

**Host adapter:** a generated Claude Code or Codex manifest exposing the same pack identity and skill tree.

## Canonical source and generated copies

```text
focused pack/pack.json + meta.json + skills/
              │
              ├── build_foundation_index.py -> capability and readiness index
              ├── build_adapters.py         -> host manifests and marketplaces
              └── build_research_bundle.py  -> all-in-one physical skill copies
```

Focused packs remain canonical. The all-in-one plugin contains physical copies because a clean Codex local-marketplace test showed that cross-plugin directory symlinks could install as empty directories. `build_research_bundle.py --check` compares paths, contents, and executable bits so generated copies cannot drift silently.

Generated artifacts are committed so GitHub marketplaces work directly. Repository verification rejects stale adapters, catalogues, indexes, or skill copies.

## Pack decomposition

| Pack | Responsibility |
|---|---|
| `evidence-lab-research` | One-install distribution of all 24 user-facing skills, without onboarding |
| `evidence-lab-core` | Optional onboarding, selection, installation lifecycle, and universal research foundations |
| `research-design` | Hypothesis generation and experimental design |
| `literature-publication` | Literature review, writing, peer review, diagrams, and LaTeX venue compliance |
| `document-evidence` | Document normalization |
| `structured-data-analysis` | Database retrieval and exploratory data analysis |
| `quantitative-sciences` | Statistical analysis, power, units, uncertainty, and scientific visualization |
| `life-sciences` | Life-science protocol and metadata checks |
| Focused workflow packs | Publication monitoring, systematic review, qualitative analysis, research-image analysis, and meeting capture |
| Compatibility packs | Legacy combined routes; not copied into the all-in-one library as user-facing skills |

The [skill catalogue](skills.md) links every user-facing skill to its canonical focused-pack source.

## Optional onboarding trust boundary

Free text may help normalize a researcher profile. It never becomes an executable package name or installation command. Selection rules in `pack.json` operate only on validated vocabulary and stable rule IDs.

The Codex companion-plugin plan is a second trust boundary. It is built from `catalog/external-plugin-candidates.json` only after portable Evidence Lab packs have been selected. Directory apps and hybrids remain visible connection steps, and every planned installation or activation requires exact readback. Claude Code receives no Codex directory actions.

For an existing workspace, onboarding builds a reconciliation plan rather than silently changing the installation. Additions and updates share one approval, extras are retained by default, and removal requires separate approval. A changed profile, release, or installed snapshot invalidates an unexecuted plan.

## Readiness model

Three different claims must not be collapsed:

1. **Installable:** the host receives the expected plugin files and discovers the skills.
2. **Mechanically verified:** schemas, generated artifacts, routing evals, and deterministic checks pass.
3. **Scientifically accepted:** representative real-task runs and independent review support the procedure's quality status.

The all-in-one plugin has passed the first two gates locally in Codex and Claude Code. Individual skills still carry their own review status; see [Skill-pack readiness](skill-pack-readiness.md).

## Release model

Each focused plugin uses SemVer. Public Evidence Lab distribution uses immutable `release-YYYY.MM.N` Git tags plus a generated `release-lock.json` GitHub Release asset. The lock binds the source commit, catalogue hash, and exact version, content hash, supported host, and license for each published pack.

A branch, fork, or untagged commit is source code, not a supported release. See [Release process](release-process.md).

## Invariants

- Every user-facing skill has exactly one canonical focused-pack owner.
- The all-in-one plugin has no dependencies and excludes onboarding and compatibility routers.
- Generated skill copies match their canonical sources byte for byte, including executable permissions.
- Claude Code and Codex adapters preserve pack identity, version, description, author, license, and component paths.
- Free-text onboarding cannot choose executable package identifiers.
- Reconciliation does not remove extras without separate confirmation.
- Partial installation is never recorded as ready.
- Planned capabilities are not presented as installed.
- A runtime is supported only after adapter, installed-copy, and representative behavior checks pass.
- Provenance, licensing, privacy, and negative routing evals survive every move or split.

## Related documentation

- [Getting started](getting-started.md)
- [Skill catalogue](skills.md)
- [Authoring skills and packs](authoring.md)
- [Review checklist](review-checklist.md)
- [Release process](release-process.md)
