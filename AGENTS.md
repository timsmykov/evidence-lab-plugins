# Working in this repository

This repository implements the Evidence Lab agent-first research stack. The product architecture and user flow are normative; do not reshape them around one host's current plugin format.

## Source of truth

- `packs/<layer>/<id>/pack.json` defines identity, version, layer, selection signals, dependencies, capabilities, and supported hosts.
- `skills/` contains the shared semantic implementation used by Claude Code and Codex.
- `meta.json` contains provenance, review state, risk, and the exact skill inventory.
- `.claude-plugin/`, `.codex-plugin/`, `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, and the Core catalog are generated. Never hand-edit them.
- The personal researcher profile and installation state do not belong in package source.

## Layers

Use `core`, `workflow`, `domain`, or `local`. A host is not a layer. Do not create separate Claude and Codex copies of a skill.

## Normal workflow

```bash
python3 scripts/new_pack.py <pack-name> --layer <core|workflow|domain|local> --skill <skill-name> --owner <owner> --reviewer <reviewer>
python3 scripts/build_adapters.py
python3 scripts/test_agent_first.py
python3 scripts/verify_repo.py
```

## Quality rules

- Every skill has at least eight routing cases and at least three negative near-misses.
- Deterministic outputs belong in scripts.
- Material research choices require a researcher confirmation point.
- `pack.json`, manifests, catalog, and actual skill directories must agree.
- Claude Code and Codex support is claimed only after native manifest validation and parity tests.
- Production requires a reviewer different from the owner, a review date, and a real run.
- Preserve provenance and third-party notices when moving or splitting content.
- Keep private paths, credentials, identifiers, and client material out of shared packs.
- Keep English entrypoints; route localized companions explicitly.

`packs/domains/example-domain` is a reference fixture, not a real capability pack.
