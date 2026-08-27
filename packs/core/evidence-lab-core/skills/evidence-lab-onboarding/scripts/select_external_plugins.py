#!/usr/bin/env python3
"""Create a deterministic, non-mutating Codex companion-plugin plan."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parent.parent
PACK_ROOT = HERE.parents[3] if HERE.parent.name == "scripts" and HERE.parent.parent.name == "evidence-lab-onboarding" else REPO_ROOT
DEFAULT_REGISTRY = PACK_ROOT / "catalog" / "external-plugin-candidates.json"
FIELDS = ("domains", "workflows", "materials", "stages", "methods")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def matches(profile: dict, signals: dict) -> bool:
    """Match when each declared signal field intersects the normalized profile."""
    return all(set(profile.get(field, [])) & set(values) for field, values in signals.items())


def select(profile: dict, registry: dict, host: str = "codex", requested_plugins: tuple[str, ...] = ()) -> dict:
    if host != "codex":
        return {"schema_version": 1, "host": host, "actions": [], "reason": "Codex directory plugins are not portable to this host."}
    requested = {value.casefold() for value in requested_plugins}
    actions = []
    for plugin in registry["plugins"]:
        if host not in plugin["hosts"] or not matches(profile, plugin["selection"]["signals"]):
            continue
        explicitly_requested = plugin["id"].casefold() in requested or plugin["display_name"].casefold() in requested
        if plugin["policy"] == "explicit-opt-in" and not explicitly_requested:
            continue
        if plugin["component_type"] in {"directory-app", "hybrid"}:
            action = "offer-connection" if plugin["policy"] == "candidate" else "withhold-pending-benchmark"
        elif plugin["policy"] == "approved-baseline" and plugin["selection"]["automatic"]:
            action = "install-after-confirmation"
        elif plugin["policy"] == "candidate":
            action = "recommend-after-validation"
        else:
            action = "offer-opt-in" if plugin["policy"] == "explicit-opt-in" else "withhold-pending-benchmark"
        actions.append({
            "plugin_id": plugin["id"],
            "display_name": plugin["display_name"],
            "action": action,
            "install_mode": plugin["install_mode"],
            "credential_mode": plugin["credential_mode"],
            "reason": plugin["rationale"],
        })
    return {"schema_version": 1, "host": host, "actions": actions}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--host", choices=("codex", "claude-code"), default="codex")
    parser.add_argument("--request", action="append", default=[], help="Explicit plugin ID or display name; may be repeated")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(select(load(args.profile), load(args.registry), args.host, tuple(args.request)), indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
